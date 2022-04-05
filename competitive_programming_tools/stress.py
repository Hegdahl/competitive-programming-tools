import asyncio
import os
import random
import re
import time
from typing import Awaitable, Callable, Optional, Sequence, Tuple

import click
import tqdm  # type: ignore

from .auto_path import AutoPath
from .get_executable import get_executable
from .utils import error

range_matcher = re.compile(r'^\[(\d+)(\.\.\.?)(\d+)\]$')


def get_range(s: str) -> Optional[Callable[[], str]]:
    match = range_matcher.match(s)
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
    def __init__(self, s: str):
        self.get = (
            get_range(s) or
            (lambda: s)
        )


def search(f: Callable[[], Awaitable[None]],
           timeout: float,
           processes: int) -> None:
    t0 = time.time()

    async def loop() -> None:
        while time.time() - t0 < timeout:
            await f()

    with tqdm.tqdm(total=1000) as pbar:
        async def update_bar() -> None:
            last_prog = 0
            while last_prog < 1000:
                await asyncio.sleep(0.5)
                t1 = time.time()
                prog = int(1000*(t1-t0)/timeout)
                pbar.update(prog-last_prog)
                last_prog = prog

        async def run_all() -> None:
            await asyncio.gather(
                update_bar(),
                *(loop() for _ in range(processes)),
            )

        asyncio.run(run_all())

        pbar.update(1000)


async def silent_run(input_data: Optional[str], solution: str) -> Tuple[bytes, int]:
    proc = await asyncio.create_subprocess_shell(
        solution,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    stdout, stderr = await proc.communicate(input_data)
    return stdout, await proc.wait()


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
@click.option('-e', '--extra-flags', default='')
@click.option('-ca', '--check-against', type=AutoPath())
@click.option('-t', '--timeout', default=10.0)
@click.option('-p', '--processes', default=4)
@click.pass_context
def stress(ctx: click.Context,
           source: str,
           pattern: Sequence[str],
           debug_level: int,
           force_recompile: bool,
           extra_flags: str,
           check_against: Optional[str],
           timeout: float,
           processes: int,
           ) -> None:

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
        pass

    async def run_single() -> None:
        nonlocal total_tests
        total_tests += 1
        test_gen_command = ' '.join(arg.get() for arg in processed_args)
        input_data, genr_exit_code = await silent_run(None, test_gen_command)

        if genr_exit_code:
            raise CountertestFound(
                'The command:',
                click.style(test_gen_command, bold=True, fg='red'),
                f'resulted in the generator crashing ({genr_exit_code=})',
            )

        out, soln_exit_code = await silent_run(input_data, soln_exe)
        if soln_exit_code:
            raise CountertestFound(
                'The command:',
                click.style(test_gen_command, bold=True, fg='red'),
                f'resulted in the solution crashing ({soln_exit_code=})',
            )

        if check_exe is not None:
            ans, check_exit_code = await silent_run(input_data, check_exe)
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
