import asyncio
from typing import cast, Sequence, TextIO, Tuple

import click


async def execute_impl(executable: str,
                       argv: Sequence[str],
                       input_file: TextIO,
                       style_stderr: bool) -> Tuple[int, str]:
    output_chunks = []

    proc = await asyncio.create_subprocess_exec(
        executable, *argv,
        stdin=input_file,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    was_err = False

    async def process_stdout(stdout: asyncio.StreamReader) -> None:
        nonlocal was_err
        while (line := (await stdout.readline()).decode()):
            output_chunks.append(line)
            print(line, end='')
            was_err = False

    async def process_stderr(stderr: asyncio.StreamReader) -> None:
        nonlocal was_err
        while (line := (await stderr.readline()).decode()):
            if style_stderr:
                if was_err:
                    click.secho('       | ',
                                bold=True, fg='magenta', nl=False, err=True)
                else:
                    click.secho('STDERR | ',
                                bold=True, fg='magenta', nl=False, err=True)
            click.secho(line, nl=False, err=True)
            was_err = True

    await asyncio.gather(
            process_stdout(cast(asyncio.StreamReader, proc.stdout)),
            process_stderr(cast(asyncio.StreamReader, proc.stdin)),
    )

    return await proc.wait(), '.'.join(output_chunks)


def execute(executable: str,
            argv: Sequence[str],
            input_file: TextIO,
            style_stderr: bool) -> Tuple[int, str]:
    return asyncio.run(execute_impl(
        executable, argv, input_file, style_stderr))
