'''Executes a program from source.'''

import os
import queue
import subprocess
import sys
import threading
from typing import (
    AnyStr, cast, IO, Optional, List,
    Sequence, TextIO, Tuple, TypeAlias
)

import click

from .auto_path import AutoPath
from .diff import diff_str
from .execute import execute
from .get_executable import CompileError, get_executable
from .languages import SUFF_TO_LANG
from .lenient_checker import LenientChecker
from .utils import error, warn, time_func

IO_TIMEOUT = 1/120


def read_ready_lines(q: queue.Queue) -> List[str]:
    lines = []
    try:
        lines.append(q.get(timeout=IO_TIMEOUT))
        while 1:
            lines.append(q.get(False))
    except queue.Empty:
        pass
    return lines


InteractiveSubprocess: TypeAlias = Tuple[
    queue.Queue, queue.Queue,
    threading.Thread, threading.Thread,
    List[Optional[int]]
]


def interactive_subprocess(command: str,
                           argv: Sequence[str] = (),
                           ) -> InteractiveSubprocess:
    in_queue: queue.Queue = queue.Queue()
    out_queue: queue.Queue = queue.Queue()
    exit_code: List[Optional[int]] = [None]

    process = subprocess.Popen(
        ' '.join((command, *argv)),
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        universal_newlines=True,
    )

    def write_loop(p: subprocess.Popen, stdin: TextIO, q: queue.Queue) -> None:
        try:
            while 1:
                exit_code[0] = p.poll()
                if exit_code[0] is not None:
                    break

                lines = read_ready_lines(q)
                if lines:
                    stdin.write(''.join(lines))
                    stdin.flush()

        except BrokenPipeError:
            error(f'Broken pipe when writing to {command!r}!')
            exit_code[0] = p.poll()

    def read_loop(p: subprocess.Popen, stdout: TextIO, q: queue.Queue) -> None:
        try:
            while 1:
                exit_code[0] = p.poll()
                if exit_code[0] is not None:
                    break
                line = stdout.readline()
                if line.strip():
                    q.put(line)

        except BrokenPipeError:
            error(f'Broken pipe when reading from {command!r}!')
            exit_code[0] = p.poll()

        for line in stdout:
            if line.strip():
                q.put(line)

    writer = threading.Thread(
        target=write_loop,
        args=(process, process.stdin, in_queue),
    )
    reader = threading.Thread(
        target=read_loop,
        args=(process, process.stdout, out_queue),
    )

    writer.start()
    reader.start()

    return in_queue, out_queue, writer, reader, exit_code


def interact(executable: str, interactor: str,
             argv: Sequence[str], sample_in: Sequence[str]) -> Tuple[int, int]:
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

    click.secho('[SAMPLE]', fg='yellow', bold=True, err=True)
    for line in sample_in:
        click.echo(line[:-1], err=True)
        interactor_in.put(line)

    def done() -> bool:
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

    click.secho('[INTERACTION]', fg='yellow', bold=True, err=True)
    while not done():
        lines = read_ready_lines(interactor_out)
        if lines:
            click.secho('[INTERACTOR] ',
                        bold=True, fg='magenta', nl=False, err=True)
            click.secho('| ' + '             | '.join(lines),
                        fg='yellow', err=True)
            for line in lines:
                executable_in.put(line)

        lines = read_ready_lines(executable_out)
        if lines:
            click.secho('[EXECUTABLE] ',
                        bold=True, fg='blue', nl=False, err=True)
            click.echo('| ' + '             | '.join(lines), err=True)
            for line in lines:
                interactor_in.put(line)

    if interactor_exit_code[0]:
        error(f'Interactor exited with code {interactor_exit_code[0]}')
    if executable_exit_code[0]:
        error(f'Executable exited with code {executable_exit_code[0]}')

    assert interactor_out.empty()
    assert executable_out.empty()

    i_exit = interactor_exit_code[0]
    e_exit = executable_exit_code[0]
    assert i_exit is not None
    assert e_exit is not None
    return i_exit, e_exit


def run_diagnostic(executable: str,
                   argv: Sequence[str],
                   input_file: IO[AnyStr]) -> None:
    proc = subprocess.Popen(
        ' '.join((
            'gdb -batch -ex "run" -ex "bt"',
            executable, *argv
        )),
        shell=True,
        stdin=input_file
    )
    proc.wait()


@click.argument('source', type=AutoPath())
@click.argument('argv', nargs=-1)
@click.option('-d', '--debug-level', type=click.IntRange(0), default=1,
              help=(
                  '\b\n'
                  'How paranoid should the debugging be?\n'
                  ' 0: As close to the average contest\n'
                  '    environment as possible.\n'
                  ' 1: Default balance between compilation\n'
                  '    speed and information.\n'
                  '>1: Higher levels may exist\n'
                  '    depending on language.\n\b\n'
              ))
@click.option('-fr', '--force-recompile', is_flag=True,
              help='If this flag is set, the program will'
                   'be recompiled even if unneccesary.')
@click.option('-e', '--extra-flags', default='')
@click.option('-T', '--testset', type=str)
@click.option('-i', '--interactor',
              type=click.Path(exists=True, dir_okay=False))
@click.option('--no-style-stderr', is_flag=True,
              help='Modify stderr to make it clearer which part it is')
@click.pass_context
def run(ctx: click.Context,
        source: str,
        argv: List[str],
        debug_level: int,
        force_recompile: bool,
        extra_flags: str,
        testset: Optional[str],
        interactor: Optional[str],
        no_style_stderr: bool) -> None:
    '''Executes a program from source.'''

    if testset is None:
        test_dir = os.path.join(os.path.dirname(source), 'samples')
        if os.path.isdir(test_dir):
            testset = os.path.join(
                test_dir,
                '.'.join(os.path.basename(source).split('.')[:-1])
            )
        else:
            testset = '-'

    suffix = source.rsplit('.')[-1]

    try:
        command = SUFF_TO_LANG[suffix].get_compile_command_gen(
            debug_level=debug_level,
            extra_flags=extra_flags,
        )
    except KeyError:
        ctx.fail(f'Unknown file suffix: {suffix!r}')

    try:

        executable = get_executable(
            source_path=source,
            command=command,
            force_recompile=force_recompile
        )

        if testset == '-':

            if interactor is not None:
                with open(0) as stdin:
                    interact(executable, interactor, argv, [*stdin])

            else:
                time_used, (returncode, output) = time_func(
                    lambda: execute(
                        executable, argv, sys.stdin,
                        not no_style_stderr
                    )
                )

                click.secho(f'{round(time_used * 1000)} ms',
                            fg='blue', err=True)

                if returncode:
                    error(f'crashed ({returncode})')

        else:

            test_dir = os.path.dirname(testset) or './'
            test_prefix = os.path.basename(testset)

            results = []

            for path in sorted(os.listdir(test_dir)):
                if not path.startswith(test_prefix):
                    continue
                if not path.endswith('.in'):
                    continue

                test_name = path[:-3]

                input_path = os.path.join(test_dir, f'{test_name}.in')
                output_path = os.path.join(test_dir, f'{test_name}.ans')

                click.secho(
                    'Running test ' +
                    click.style(repr(test_name), fg="yellow") +
                    ' ...',
                    err=True
                )

                if interactor is not None:
                    with open(input_path, 'r') as file:
                        input_data = ''.join(file)

                    time_used, exit_codes = time_func(
                        lambda: interact(
                            executable,
                            cast(str, interactor),
                            argv,
                            [f'{line}\n'
                             for line in input_data.split('\n')[:-1]]
                        )
                    )

                    interactor_exit_code, executable_exit_code = exit_codes

                    fail = (
                        interactor_exit_code != 0 or
                        executable_exit_code != 0
                    )

                    results.append([test_name, ['AC', 'RE'][fail], time_used])

                else:
                    with open(input_path) as file:
                        time_used, (returncode, output) = time_func(
                            lambda: execute(
                                executable, argv, file,
                                not no_style_stderr
                            )
                        )
                    results.append(
                        [test_name, click.style('??', fg='yellow'), time_used]
                    )

                    click.secho(f'{round(time_used * 1000)} ms',
                                fg='blue', err=True)

                    if returncode:
                        results[-1][1] = click.style('RE', 'red')
                        click.secho('[DIAGNOSTIC]',
                                    bold=True, fg='yellow', err=True)
                        with open(input_path) as file:
                            run_diagnostic(executable, argv, file)
                        click.echo(''.join((
                            click.style('Finished ', fg='red'),
                            click.style(repr(test_name), fg='yellow'),
                            click.style(f' with RE ({returncode})', fg='red'),
                        )), err=True)

                    elif os.path.exists(output_path):
                        results[-1][1] = click.style('AC', fg='green')

                        with open(output_path, 'r') as file:
                            answer = ''.join(file)

                        checker_result = LenientChecker(output, answer)

                        if not checker_result.accept:
                            click.secho('[DIFF]',
                                        bold=True, fg='yellow', err=True)
                            click.echo(diff_str(answer, output),
                                       err=True, nl=False)
                            results[-1][1] = click.style('WA', fg='red')
                            click.echo(''.join((
                                click.style('Finished ', fg='red'),
                                click.style(repr(test_name), fg='yellow'),
                                click.style(' with WA', fg='red'),
                            )), err=True)
                        elif checker_result.ignored_properties:
                            ignore_str = ', '.join(
                                checker_result.ignored_properties
                            )
                            click.echo(''.join((
                                click.style('Finished ', fg='green'),
                                click.style(repr(test_name), fg='yellow'),
                                click.style(f' with AC (ignored {ignore_str})',
                                            fg='green'),
                            )), err=True)

                            if checker_result.warnings:
                                results[-1][1] += click.style(
                                    ' (with warnings)', fg='yellow')

                            for name, err in checker_result.warnings.items():
                                warn(f'{name}: {err}')
                        else:
                            click.echo(''.join((
                                click.style('Finished ', fg='green'),
                                click.style(repr(test_name), fg='yellow'),
                                click.style(' with AC (exact)', fg='green'),
                            )), err=True)

            click.echo('\nSummary:', err=True)
            for name, verdict, time_used in results:
                click.echo(f'  [{name}] ', err=True, nl=False)
                click.secho(verdict, bold=True, err=True, nl=False)
                click.echo(f' {round(1000*time_used)} ms', err=True)
    except CompileError:
        error('failed compiling.')
        ctx.fail('')
