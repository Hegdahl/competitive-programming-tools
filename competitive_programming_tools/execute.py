import asyncio
from typing import cast, Optional, Sequence, TextIO, Tuple

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
            process_stderr(cast(asyncio.StreamReader, proc.stderr)),
    )

    return await proc.wait(), ''.join(output_chunks)


async def execute_interactive_impl(executable: str,
                                   interactor: str,
                                   argv: Sequence[str],
                                   sample_in: Sequence[str]
                                   ) -> Tuple[int, int]:

    exec_proc = await asyncio.create_subprocess_shell(
        executable,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        # stderr=asyncio.subprocess.PIPE,
    )

    inte_proc = await asyncio.create_subprocess_shell(
        ' '.join((interactor, *argv)),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        # stderr=asyncio.subprocess.PIPE,
    )

    last_begin_pre = ''

    async def forward(src: asyncio.StreamReader,
                      dst: asyncio.StreamWriter,
                      begin_pre: str,
                      continue_pre: str,
                      echo_color: Optional[str] = None) -> None:
        nonlocal last_begin_pre
        while (line_bytes := (await src.readline())):
            line = line_bytes.decode()
            if last_begin_pre == begin_pre:
                click.echo(continue_pre, nl=False, err=True)
            else:
                click.echo(begin_pre, nl=False, err=True)
                last_begin_pre = begin_pre
            click.secho(line, fg=echo_color, nl=False, err=True)
            dst.write(line_bytes)

    if sample_in:
        click.secho('[SAMPLE]', fg='yellow', bold=True, err=True)
    for line in sample_in:
        click.echo(line, nl=False, err=True)
        cast(asyncio.StreamWriter, inte_proc.stdin).write(line.encode())

    await asyncio.gather(
        forward(
            cast(asyncio.StreamReader, exec_proc.stdout),
            cast(asyncio.StreamWriter, inte_proc.stdin),
            click.style('\nEXECUTABLE | ', fg='blue', bold=True),
            click.style('           | ', fg='blue', bold=True),
        ),
        forward(
            cast(asyncio.StreamReader, inte_proc.stdout),
            cast(asyncio.StreamWriter, exec_proc.stdin),
            click.style('\nINTERACTOR | ', fg='magenta', bold=True),
            click.style('           | ', fg='magenta', bold=True),
            'yellow',
        ),
    )

    return await exec_proc.wait(), await inte_proc.wait()


def execute(executable: str,
            argv: Sequence[str],
            input_file: TextIO,
            style_stderr: bool) -> Tuple[int, str]:
    return asyncio.run(execute_impl(
        executable, argv, input_file, style_stderr))


def execute_interactive(executable: str,
                        interactor: str,
                        argv: Sequence[str],
                        sample_in: Sequence[str]) -> Tuple[int, int]:
    return asyncio.run(execute_interactive_impl(
        executable, interactor, argv, sample_in))
