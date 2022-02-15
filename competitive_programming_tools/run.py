'''Executes a program from source.'''

CPP_DEBUG_LEVELS = (
    '-O2',

    '-O1 -g3 -DENABLE_DEBUG -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC',

    '-O0 -g3 -DENABLE_DEBUG -fsanitize=address -fsanitize=undefined -fno-sanitize-recover '
    '-fstack-protector -fsanitize-address-use-after-scope',

    '-O0 -g3 -DENABLE_DEBUG -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC '
    '-fsanitize=address -fsanitize=undefined -fno-sanitize-recover '
    '-fstack-protector -fsanitize-address-use-after-scope',
)

CPP_WARNINGS = (
    '-Wall -Wextra -Wshadow -Wformat=2 -Wfloat-equal -Wconversion '
    '-Wlogical-op -Wshift-overflow -Wduplicated-cond -Wcast-qual -Wcast-align '
    '-Wno-variadic-macros '
)

IO_TIMEOUT = 1/120

from hashlib import sha256
import os
import queue
import subprocess
import sys
import threading
import time

import click

from . import DIRNAME, TMP_DIR, error
from . import auto_check
from .auto_path import AutoPath

INCLUDE = os.path.join(DIRNAME, 'include')

def time_func(f):
    t0 = time.perf_counter()
    res = f()
    tf = time.perf_counter()
    return (tf-t0), res

class CompileError(Exception):
    def __init__(self, exit_code):
        self.exit_code = exit_code

def get_executable(*, source_path, command, force_recompile):
    '''
    Get the path to an executable corresponding to the source,
    by compiling, or using previously compiled executable.
    '''

    source_id = sha256(source_path.encode()).hexdigest()
    command_id = sha256(command.encode()).hexdigest()

    source_copy_path = os.path.join(TMP_DIR, '-'.join((source_id, command_id, 'SOURCE')))
    executable_path = os.path.join(TMP_DIR, '-'.join((source_id, command_id, 'EXECUTABLE')))

    old_content = ''

    if os.path.exists(source_copy_path):
        with open(source_copy_path, 'r') as file:
            old_content = ''.join(file)

    new_content = ''
    with open(source_path, 'r') as file:
        new_content = ''.join(file)

    if new_content != old_content:
        force_recompile = True
        with open(source_copy_path, 'w') as file:
            file.write(new_content)

    if force_recompile and os.path.exists(executable_path):
        os.remove(executable_path)

    if not os.path.exists(executable_path):
        click.echo(
            f'Compiling {click.style(repr(source_path), fg = "yellow")} ... ',
            err = True, nl = False
        )

        exit_code = os.system(f'{command} {source_path} -o {executable_path}')
        if exit_code:
            click.echo()
            raise CompileError(exit_code)

        click.secho('done!', fg = 'green', err = True)

    return executable_path

def read_ready_lines(q):
    lines = []
    try:
        lines.append(q.get(timeout = IO_TIMEOUT))
        while 1: lines.append(q.get(False))
    except queue.Empty:
        pass
    return lines

def interactive_subprocess(command, argv = ()):
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    exit_code = [None]

    process = subprocess.Popen(
        ' '.join((command, *argv)),
        shell = True,
        stdout = subprocess.PIPE,
        stdin = subprocess.PIPE,
        universal_newlines = True,
    )

    def write_loop(p, q):
        try:
            while 1:
                exit_code[0] = p.poll()
                if exit_code[0] is not None: break

                lines = read_ready_lines(q)
                if lines:
                    p.stdin.write(''.join(lines))
                    p.stdin.flush()

        except BrokenPipeError:
            error(f'Broken pipe when writing to {command!r}!')
            exit_code[0] = p.poll()

    def read_loop(p, q):
        try:
            while 1:
                exit_code[0] = p.poll()
                if exit_code[0] is not None: break
                line = p.stdout.readline()
                if line.strip():
                    q.put(line)
        except BrokenPipeError:
            error(f'Broken pipe when reading from {command!r}!')
            exit_code[0] = p.poll()

        for line in p.stdout:
            if line.strip():
                q.put(line)

    writer = threading.Thread(
        target = write_loop,
        args = (process, in_queue),
    )
    reader = threading.Thread(
        target = read_loop,
        args = (process, out_queue),
    )

    writer.start()
    reader.start()

    return in_queue, out_queue, writer, reader, exit_code

def interact(executable, interactor, argv, sample_in):
    '''Run the executable together with an interactor.'''
    (
        interactor_in, interactor_out,
        interactor_writer, interactor_reader,
        interactor_exit_code
    ) = interactive_subprocess(interactor, argv)

    (
        executable_in, executable_out,
        executable_writer, executable_reader,
        executable_exit_code
    ) = interactive_subprocess(executable)

    interactor_dead = False
    executable_dead = False

    click.secho('[SAMPLE]', fg = 'yellow', bold = True)
    for line in sample_in:
        click.echo(line[:-1])
        interactor_in.put(line)

    def done():
        nonlocal interactor_dead, executable_dead

        if interactor_exit_code[0] is not None and not interactor_dead:
            interactor_dead = True
            interactor_writer.join()
            interactor_reader.join()

        if executable_exit_code[0] is not None and not executable_dead:
            executable_dead = True
            executable_writer.join()
            executable_reader.join()

        if interactor_exit_code[0] is None:
            return False
        if executable_exit_code[0] is None:
            return False
        if not interactor_out.empty():
            return False
        if not executable_out.empty():
            return False

        return True

    click.secho('[INTERACTION]', fg = 'yellow', bold = True)
    while not done():
        lines = read_ready_lines(interactor_out)
        if lines:
            click.secho('[INTERACTOR] ', bold = True, fg = 'magenta', nl = False)
            click.secho('| ' + '             | '.join(lines), fg = 'yellow')
            for line in lines:
                executable_in.put(line)

        lines = read_ready_lines(executable_out)
        if lines:
            click.secho('[EXECUTABLE] ', bold = True, fg = 'blue', nl = False)
            click.echo('| ' + '             | '.join(lines))
            for line in lines:
                interactor_in.put(line)

    if interactor_exit_code[0]:
        error(f'Interactor exited with code {interactor_exit_code[0]}')
    if executable_exit_code[0]:
        error(f'Executable exited with code {executable_exit_code[0]}')

    assert interactor_out.empty()
    assert executable_out.empty()

    return (interactor_exit_code[0], executable_exit_code[0])

def execute(executable, argv, input_file):
    output_chunks = []

    proc = subprocess.Popen(
        [executable, *argv],
        stdin = input_file,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )

    while proc.poll() is None:
        out, err = proc.communicate()
        if err:
            lines = err.decode().split('\n')
            if not lines[-1]:
                lines.pop(-1)
            click.secho('STDERR | ', bold = True, fg = 'magenta', nl = False)
            click.secho(lines[0])
            for line in lines[1:]:
                click.secho('       | ', bold = True, fg = 'magenta', nl = False)
                click.secho(line)
        if out:
            output_chunks.append(out.decode())
            print(out.decode(), end='', flush = True)

    return proc.returncode, '.'.join(output_chunks)

@click.argument('source', type = AutoPath(['cpp']))
@click.argument('argv', nargs = -1)
@click.option('-d', '--debug-level', type = click.IntRange(0, 3), default = 1,
              help = (
                  '\b\n'
                  'How paranoid should the debugging be?\n'
                  ' 0: As close to the average contest\n'
                  '    environment as possible\n'
                  ' 1: Default balance between compilation\n'
                  '    speed and information\n'
                  ' 2: Enables sanitizers\n'
                  ' 3: EVERYTHING - last hope (before valgrind ig)\n\b\n'
              ))
@click.option('-fr', '--force-recompile', is_flag = True,
              help = 'If this flag is set, the program will be recompiled even if unneccesary.')
@click.option('-e', '--extra-flags', default = '')
@click.option('-T', '--testset', type = str)
@click.option('-i', '--interactor', type = str)
@click.pass_context
def run(ctx, source, argv, debug_level, force_recompile, extra_flags, testset, interactor):
    '''Executes a program from source.'''

    if testset is None:
        test_dir = os.path.join(os.path.dirname(source), 'samples')
        if os.path.isdir(test_dir):
            testset = os.path.join(test_dir, '.'.join(os.path.basename(source).split('.')[:-1]))
        else:
            testset = '-'

    lang = '.' + source.rsplit('.')[-1]

    GEN_COMMAND = {
        '.cpp': lambda: 'g++ -std=gnu++20 '
        f'-I{INCLUDE} {CPP_WARNINGS} {CPP_DEBUG_LEVELS[debug_level]} {extra_flags}',
    }

    try:
        command = GEN_COMMAND[lang]()
    except KeyError:
        ctx.fail(f'Unknown language {lang!r}')

    try:

        executable = get_executable(
            source_path=os.path.abspath(source),
            command=command,
            force_recompile=force_recompile
        )

        if testset == '-':

            if interactor is not None:
                with open(0) as stdin:
                    interact(executable, interactor, argv, [*stdin])

            else:
                time_used, (returncode, output) = time_func(lambda: execute(executable, argv, sys.stdin))

                click.secho(f'{round(time_used * 1000)} ms', fg = 'blue', err = True)

                if returncode:
                    error(f'crashed ({returncode})')

        else:

            test_dir = os.path.dirname(testset) or './'
            test_prefix = os.path.basename(testset)

            results = []

            for path in sorted(os.listdir(test_dir)):
                if not path.startswith(test_prefix): continue
                if not path.endswith('.in'): continue

                test_name = path[:-3]

                input_path = os.path.join(test_dir, f'{test_name}.in')
                output_path = os.path.join(test_dir, f'{test_name}.ans')

                click.secho(
                    f'Running test {click.style(repr(test_name), fg = "yellow")} ...',
                    err = True
                )

                if interactor is not None:
                    with open(input_path, 'r') as file:
                        input_data = ''.join(file)

                    time_used, (interactor_exit_code, executable_exit_code) = time_func(
                        lambda: interact(
                            executable,
                            interactor,
                            argv,
                            [f'{line}\n' for line in input_data.split('\n')[:-1]]
                        )
                    )

                    fail = interactor_exit_code != 0 or executable_exit_code != 0

                    results.append([test_name, ['AC', 'RE'][fail], time_used])

                else:
                    with open(input_path) as file:
                        time_used, (returncode, output) = time_func(
                            lambda: execute(executable, argv, file)
                        )
                    results.append([test_name, '??', time_used])

                    click.secho(f'{round(time_used * 1000)} ms', fg = 'blue', err = True)

                    if returncode:
                        results[-1][1] = 'RE'
                        click.echo(''.join((
                            click.style('Finished ', fg = 'red'),
                            click.style(repr(test_name), fg = 'yellow'),
                            click.style(f' with RE ({returncode})', fg = 'red'),
                        )), err = True)

                    elif os.path.exists(output_path):

                        with open(output_path, 'r') as file:
                            answer = ''.join(file)

                        results[-1][1] = 'AC'

                        if answer == output:
                            click.echo(''.join((
                                click.style('Finished ', fg = 'green'),
                                click.style(repr(test_name), fg = 'yellow'),
                                click.style(' with AC (exact)', fg = 'green'),
                            )), err = True)
                        elif answer.strip().split() == output.strip().split():
                            click.echo(''.join((
                                click.style('Finished ', fg = 'green'),
                                click.style(repr(test_name), fg = 'yellow'),
                                click.style(' with AC (up to whitespace)', fg = 'green'),
                            )), err = True)
                        else:
                            results[-1][1] = 'WA'
                            click.echo(''.join((
                                click.style('Finished ', fg = 'red'),
                                click.style(repr(test_name), fg = 'yellow'),
                                click.style(' with WA', fg = 'red'),
                        )), err = True)

            click.echo('\nSummary:', err = True)
            for name, verdict, time_used in results:

                color = 'red'
                if verdict == 'AC':
                    color = 'green'
                elif verdict == '??':
                    color = 'yellow'

                click.echo(f'  [{name}] ', err = True, nl = False)
                click.secho(verdict, fg = color, bold = True, err = True, nl = False)
                click.echo(f' {round(1000*time_used)} ms', err = True)

    except CompileError as exc:
        error('failed compiling.')
        return exc.exit_code
