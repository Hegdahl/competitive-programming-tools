'''Executes a program from source.'''

CPP_DEBUG_LEVELS = (
    '-O2',

    '-O1 -g0 -DENABLE_DEBUG -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC',

    '-O0 -g3 -DENABLE_DEBUG -fsanitize=address -fsanitize=undefined -fno-sanitize-recover '
    '-fstack-protector -fsanitize-address-use-after-scope',

    '-O0 -g3 -DENABLE_DEBUG -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC '
    '-fsanitize=address -fsanitize=undefined -fno-sanitize-recover '
    '-fstack-protector -fsanitize-address-use-after-scope',
)

CPP_WARNINGS = (
    '-Wall -Wextra -pedantic -Wshadow -Wformat=2 -Wfloat-equal -Wconversion '
    '-Wlogical-op -Wshift-overflow -Wduplicated-cond -Wcast-qual -Wcast-align '
    '-Wno-variadic-macros '
)

from hashlib import sha256
import os
import subprocess
import click
import threading
import time
import queue

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

def interactive_subprocess(command):
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    exit_code = [None]

    process = subprocess.Popen(
        command,
        shell = True,
        stdout = subprocess.PIPE,
        stdin = subprocess.PIPE,
        universal_newlines = True,
    )

    def write_loop(p, q):
        try:
            while exit_code[0] is None:
                try:
                    line = q.get(timeout = 1/60)
                    p.stdin.write(line)
                    p.stdin.flush()
                except queue.Empty:
                    pass
                exit_code[0] = p.poll()

        except BrokenPipeError:
            error(f'Broken pipe when writing to {command!r}!')
            exit_code[0] = p.poll()

    def read_loop(p, q):
        try:
            while exit_code[0] is None:
                line = p.stdout.readline()
                if line.strip():
                    q.put(line)
                exit_code[0] = p.poll()
        except BrokenPipeError:
            error(f'Broken pipe when reading from {command!r}!')
            exit_code[0] = p.poll()

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

def interact(executable, interactor, sample_in):
    '''Run the executable together with an interactor.'''
    (
        interactor_in, interactor_out,
        interactor_writer, interactor_reader,
        interactor_exit_code
    ) = interactive_subprocess(interactor)

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
        try:
            line = interactor_out.get(timeout = 1/60)
            click.echo(click.style('[INTERACTOR]', bold = True, fg = 'magenta') + ' ' + repr(line))
            executable_in.put(line)
        except queue.Empty:
            pass

        try:
            line = executable_out.get(timeout = 1/60)
            click.echo(click.style('[EXECUTABLE]', bold = True, fg = 'blue') + ' ' + repr(line))
            interactor_in.put(line)
        except queue.Empty:
            pass

    if interactor_exit_code[0]:
        error(f'Interactor exited with code {interactor_exit_code[0]}')
    if executable_exit_code[0]:
        error(f'Executable exited with code {executable_exit_code[0]}')

    assert interactor_out.empty()
    assert executable_out.empty()

    return (interactor_exit_code[0], executable_exit_code[0])

@click.argument('source', type = AutoPath(['cpp']))
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
@click.option('-Ta', '--testset-auto', is_flag = True)
@click.option('-i', '--interactor', type = str)
@click.pass_context
def run(ctx, source, debug_level, force_recompile, extra_flags, testset, testset_auto, interactor):
    '''Executes a program from source.'''

    if testset_auto:
        if testset is not None:
            raise click.UsageError('Do not use --testset together with --testset-auto')
        testset = os.path.join(os.path.dirname(source),
                               'samples',
                               '.'.join(os.path.basename(source).split('.')[:-1]))

    lang = '.' + source.rsplit('.')[-1]

    GEN_COMMAND = {
        '.cpp': lambda: f'g++ -I{INCLUDE} {CPP_WARNINGS} {CPP_DEBUG_LEVELS[debug_level]} {extra_flags}',
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

        if testset is None:

            if interactor is not None:
                with open(0) as stdin:
                    interact(executable, interactor, [*stdin])

            else:
                time_used, completed = time_func(
                    lambda: subprocess.run(
                        executable,
                ))

                click.secho(f'{round(time_used * 1000)} ms', fg = 'blue', err = True)

                if completed.returncode:
                    error(f'crashed ({completed.returncode})')

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

                with open(input_path, 'r') as file:
                    input_data = ''.join(file)

                click.secho(
                    f'Running test {click.style(repr(test_name), fg = "yellow")} ...',
                    err = True
                )

                if interactor is not None:
                    time_used, (interactor_exit_code, executable_exit_code) = time_func(
                        lambda: interact(
                            executable,
                            interactor,
                            [f'{line}\n' for line in input_data.split('\n')[:-1]]
                        )
                    )

                    fail = interactor_exit_code != 0 or executable_exit_code != 0

                    results.append([test_name, ['AC', 'RE'][fail], time_used])

                else:
                    time_used, completed = time_func(
                        lambda: subprocess.run(
                            executable,
                            input = input_data.encode(),
                            capture_output = True,
                    ))
                    results.append([test_name, '??', time_used])

                    output = completed.stdout.decode()
                    print(output.rstrip('\n'))

                    if completed.stderr:
                        click.secho('STDERR:', fg = 'magenta')
                        click.echo(completed.stderr.decode(), err = True)

                    click.secho(f'{round(time_used * 1000)} ms', fg = 'blue', err = True)

                    if completed.returncode:
                        results[-1][1] = 'RE'
                        click.echo(''.join((
                            click.style('Finished ', fg = 'red'),
                            click.style(repr(test_name), fg = 'yellow'),
                            click.style(f' with RE ({completed.returncode})', fg = 'red'),
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
