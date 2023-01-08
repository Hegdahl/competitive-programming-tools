'''
Provides functions for stress testing solutions.
'''

import asyncio
import random
import re
import time
from typing import cast, Awaitable, Callable, Optional, Sequence, Tuple

import click
import tqdm  # type: ignore

from .auto_path import AutoPath
from .execute import execute_interactive_impl
from .get_executable import get_executable
from .utils import error

range_matcher = re.compile(r'^\[(\d+)(\.\.\.?)(\d+)\]$')


def get_range(range_str: str) -> Optional[Callable[[], str]]:
    '''
    Converts a string in range format
    to a function returning a random
    integer in the range.
    '''
    match = range_matcher.match(range_str)
    if match is None:
        return None

    start = int(match[1])
    mid = match[2]
    stop = int(match[3])

    assert start <= stop

    if mid == '...':
        stop += 1

    return lambda: str(random.randint(start, stop))


class ProcessedArg:
    '''
    Given a cli argument,
    create a function `get`
    that returns a new cli
    argument that is potentially
    changed. For example [0...4]
    will return a function that returns
    a random integer between 0 and 4
    (converted to a string).
    '''
    def __init__(self, arg: str):
        self.get = (
            get_range(arg) or
            (lambda: arg)
        )


def search(func: Callable[[], Awaitable[None]],
           timeout: float,
           processes: int) -> None:
    '''
    Run :py:func:`func` until
    it it raises an exception,
    or for `timeout` seconds.
    '''
    start_time = time.time()

    async def loop() -> None:
        while time.time() - start_time < timeout:
            await func()

    with tqdm.tqdm(total=1000) as pbar:
        async def update_bar() -> None:
            last_prog = 0
            while last_prog < 1000:
                await asyncio.sleep(0.5)
                end_time = time.time()
                prog = int(1000*(end_time-start_time)/timeout)
                pbar.update(prog-last_prog)
                last_prog = prog

        async def run_all() -> None:
            await asyncio.gather(
                update_bar(),
                *(loop() for _ in range(processes)),
            )

        asyncio.run(run_all())

        pbar.update(1000)


async def silent_run(input_data: Optional[bytes],
                     solution: str,
                     interactor: Optional[str]) -> Tuple[bytes, int]:
    '''
    Run `solution` with `input_data` fed to stdin
    without any output forwarded to stdout.
    '''

    proc = await asyncio.create_subprocess_shell(
        solution,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    if interactor is None:
        stdout, _ = await proc.communicate(input_data)
        return stdout, await proc.wait()

    interactor_proc = await asyncio.create_subprocess_shell(
        interactor,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    interactor_proc.stdin.write(input_data)

    async def forward(src: asyncio.StreamReader,
                      dst: asyncio.StreamWriter):
        while (line_bytes := (await src.readline())):
            line = line_bytes.decode()
            dst.write(line_bytes)

    await asyncio.gather(
        forward(
            cast(asyncio.StreamReader, proc.stdout),
            cast(asyncio.StreamWriter, interactor_proc.stdin),
        ),
        forward(
            cast(asyncio.StreamReader, interactor_proc.stdout),
            cast(asyncio.StreamWriter, proc.stdin),
        )
    )

    return b'', (await proc.wait()) | (await interactor_proc.wait())




@click.argument('source', type=AutoPath())
@click.argument('pattern', nargs=-1)
@click.option('-d', '--debug-level', type=click.IntRange(0), default=0,
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
@click.option('-i', '--interactor', type=str)
@click.option('-e', '--extra-flags', default='')
@click.option('-ca', '--check-against', type=AutoPath())
@click.option('-t', '--timeout', default=10.0)
@click.option('-p', '--processes', default=4)
def stress(source: str,
           pattern: Sequence[str],
           debug_level: int,
           force_recompile: bool,
           interactor: Optional[str],
           extra_flags: str,
           check_against: Optional[str],
           timeout: float,
           processes: int,
           ) -> None:
    '''
    Run `source` repeatedly with input from
    generated by the pattern
    (which should expand to something runnable in the shell).
    Stops after `timeout` seconds, or when a test causing
    the solution to crash is found, or, if `check_against`
    is given, `check_against` returns a different answer
    from `source`.
    '''

    soln_exe = get_executable(
        source_path=source,
        debug_level=debug_level,
        force_recompile=force_recompile,
        extra_flags=extra_flags,
    )

    check_exe = get_executable(
        source_path=check_against,
        debug_level=debug_level,
        force_recompile=force_recompile,
        extra_flags=extra_flags,
    ) if check_against is not None else None

    processed_args = tuple(map(ProcessedArg, pattern))

    total_tests = 0

    class CountertestFound(Exception):
        '''
        Exception raised when a
        a countertest is found.
        '''

    async def run_single() -> None:
        nonlocal total_tests
        total_tests += 1
        test_gen_command = ' '.join(arg.get() for arg in processed_args)
        input_data, genr_exit_code = await silent_run(None, test_gen_command, None)

        if genr_exit_code:
            raise CountertestFound(
                'The command:',
                click.style(test_gen_command, bold=True, fg='red'),
                f'resulted in the generator crashing ({genr_exit_code=})',
            )

        out, soln_exit_code = await silent_run(input_data, soln_exe, interactor)
        if soln_exit_code:
            raise CountertestFound(
                'The command:',
                click.style(test_gen_command, bold=True, fg='red'),
                f'resulted in the solution crashing ({soln_exit_code=})',
            )

        if check_exe is not None:
            ans, check_exit_code = await silent_run(input_data, check_exe, interactor)
            if check_exit_code:
                raise CountertestFound(
                    'The command:',
                    click.style(test_gen_command, bold=True, fg='red'),
                    'resulted in the checked against'
                    f'code crashing ({check_exit_code=})',
                )

            if out != ans:
                raise CountertestFound(
                    'The command:',
                    click.style(test_gen_command, bold=True, fg='red'),
                    'resulted the solution getting a different answer',
                    'from the checked against code.',
                )

    try:
        search(run_single, timeout, processes)
    except CountertestFound as exc:
        print(*exc.args, sep='\n')
        return
    finally:
        print(f'Ran {total_tests} tests.')

    error('Could not find a counter test.')
