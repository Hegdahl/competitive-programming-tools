'''Executes a program from source.'''

import os
import subprocess
import sys
from typing import (
    AnyStr, cast, IO, Optional,
    List, Sequence, Tuple, Union
)

import click

from .auto_path import AutoPath
from .execute import execute, execute_interactive
from .get_executable import CompileError, get_executable
from .lenient_checker import LenientChecker
from .utils import error, warn, time_func


def run_interactive(executable: str,
                    interactor: str,
                    argv: Sequence[str],
                    input_path: Union[str, int, None],
                    test_name: str) -> Tuple[str, float]:
    '''
    Run two processes communicating with each other
    through stdin and stdout, and check that
    the return code of both is 0, and print
    information about the execution.

    Returns a verdict string and the number of seconds spent.
    '''
    if input_path is None:
        input_data = ''
    else:
        with open(input_path, 'r', encoding='utf-8') as file:
            input_data = ''.join(file)

    time_used, exit_codes = time_func(
        lambda: execute_interactive(
            executable,
            interactor,
            argv,
            [f'{line}\n'
             for line in input_data.split('\n')[:-1]],
        )
    )

    interactor_exit_code, executable_exit_code = exit_codes

    fail = (
        interactor_exit_code != 0 or
        executable_exit_code != 0
    )

    if fail:
        verdict_str = click.style('RE', fg='red')
    else:
        verdict_str = click.style('AC', fg='green')

    click.echo('Finished ', nl=False, err=True)
    if test_name:
        click.secho(f'{test_name!r} ', fg='yellow', nl=False, err=True)
    click.echo('with ', nl=False, err=True)
    click.secho(verdict_str, bold=True, err=True)
    if fail:
        error(f'crashed ({interactor_exit_code=}, {executable_exit_code=})')
    click.secho(f'{round(time_used * 1000)} ms',
                fg='blue', err=True)

    return verdict_str, time_used


def run_diagnostic(executable: str,
                   argv: Sequence[str],
                   input_file: IO[AnyStr]) -> None:
    '''
    Run the `executable` with `input_file`
    fed to stdin inside the gnu debugger.
    '''
    proc = subprocess.Popen(
        ' '.join((
            'gdb -batch -ex "run" -ex "bt"',
            executable, *argv
        )),
        shell=True,
        stdin=input_file
    )
    proc.wait()


def run_test(executable: str,
             interactor: Optional[str],
             argv: Sequence[str],
             no_style_stderr: bool,
             test_dir: str,
             test_name: str) -> Tuple[str, float]:
    '''
    Run `executable` with an input
    file and check if the output matches
    the corresponding ouput file.

    If an interactor is specified,
    run them communicating with each other
    instead of with the input file fed
    to the executable.
    In this case, feed the input file
    to the interactor instead and
    ignore any output file
    (the interactor should check that the output is correct).

    Returns a verdict string and the number of seconds used.
    '''
    input_path = os.path.join(test_dir, f'{test_name}.in')
    output_path = os.path.join(test_dir, f'{test_name}.ans')

    click.secho(
        'Running test ' +
        click.style(repr(test_name), fg="yellow") +
        ' ...',
        err=True
    )

    if interactor is not None:
        verdict_str, time_used = run_interactive(
            executable,
            cast(str, interactor),
            argv,
            input_path,
            test_name,
        )
        return verdict_str, time_used

    with open(input_path, encoding='utf-8') as file:
        time_used, (returncode, output) = time_func(
            lambda: execute(
                executable, argv, file,
                not no_style_stderr
            )
        )
    click.secho(f'{round(time_used * 1000)} ms',
                fg='blue', err=True)

    verdict_str = click.style('??', fg='yellow')

    if returncode:
        verdict_str = click.style('RE', 'red')
        click.secho('[DIAGNOSTIC]',
                    bold=True, fg='yellow', err=True)
        with open(input_path, encoding='utf-8') as file:
            run_diagnostic(executable, argv, file)
        click.echo(''.join((
            click.style('Finished ', fg='red'),
            click.style(repr(test_name), fg='yellow'),
            click.style(f' with RE ({returncode})', fg='red'),
        )), err=True)

    elif os.path.exists(output_path):
        verdict_str = click.style('AC', fg='green')

        with open(output_path, 'r', encoding='utf-8') as file:
            answer = ''.join(file)

        checker_result = LenientChecker(output, answer)

        if not checker_result.accept:
            click.secho('[DIFF]',
                        bold=True, fg='yellow', err=True)
            verdict_str = click.style('WA', fg='red')
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
                verdict_str += click.style(
                    ' (with warnings)', fg='yellow')

            for name, err in checker_result.warnings.items():
                warn(f'{name}: {err}')
        else:
            click.echo(''.join((
                click.style('Finished ', fg='green'),
                click.style(repr(test_name), fg='yellow'),
                click.style(' with AC (exact)', fg='green'),
            )), err=True)

    return verdict_str, time_used


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
              help='If this flag is set, the program will '
                   'be recompiled even if unneccesary.')
@click.option('-e', '--extra-flags', default='',
              help='Pass extra arguments in the compilation.')
@click.option('-T', '--testset', type=str,
              help=('Select which tests to run. '
                    "Either the pattern 'some/directory/prefix' "
                    'to run all tests in the directory with a basename '
                    'starting with the prefix '
                    '(.in for input, .ans for correct output) '
                    "or '-' to use standard input instead of test files. "
                    "The default is 'samples/{source_filename_without_suffix}'"))
@click.option('-i', '--interactor', type=str,
              help=('Run the program against an interactor '
                    'instead of on input files. '
                    'The value should be something executable.'))
@click.option('--no-style-stderr', is_flag=True,
              help='Disable highlighting which part of output is stderr.')
def run(source: str,
        argv: List[str],
        debug_level: int,
        force_recompile: bool,
        extra_flags: str,
        testset: Optional[str],
        interactor: Optional[str],
        no_style_stderr: bool) -> None:
    '''Executes a program from source.'''

    if testset is None and interactor is None:
        test_dir = os.path.join(os.path.dirname(source), 'samples')
        if os.path.isdir(test_dir):
            testset = os.path.join(
                test_dir,
                '.'.join(os.path.basename(source).split('.')[:-1])
            )
        else:
            testset = '-'

    try:
        executable = get_executable(
            source_path=source,
            debug_level=debug_level,
            extra_flags=extra_flags,
            force_recompile=force_recompile
        )
    except CompileError:
        error('failed compiling.')
        return

    if testset is None:
        assert interactor
        run_interactive(executable, interactor, argv, None, '')
        return

    if testset == '-':
        if interactor is not None:
            run_interactive(executable, interactor, argv, 0, '')
            return

        time_used, (returncode, _) = time_func(
            lambda: execute(
                executable, argv, sys.stdin,
                not no_style_stderr
            )
        )

        click.secho(f'{round(time_used * 1000)} ms',
                    fg='blue', err=True)

        if returncode:
            error(f'crashed ({returncode})')
        return

    test_dir = os.path.dirname(testset) or './'
    test_prefix = os.path.basename(testset)

    results: List[Tuple[str, str, float]] = []

    for path in sorted(os.listdir(test_dir)):
        if not path.startswith(test_prefix):
            continue
        if not path.endswith('.in'):
            continue
        test_name = path[:-3]
        results.append((
            test_name,
            *run_test(executable, interactor, argv, no_style_stderr,
                      test_dir, test_name)
        ))

    click.echo('\nSummary:', err=True)
    for name, verdict, time_used in results:
        click.echo(f'  [{name}] ', err=True, nl=False)
        click.secho(verdict, bold=True, err=True, nl=False)
        click.echo(f' {round(1000*time_used)} ms', err=True)
