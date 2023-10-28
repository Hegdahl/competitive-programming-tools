'''
Provides functions for executing
programs from source code and testing them.
'''
import click


async def execute_impl(executable,
                       argv,
                       input_file,
                       style_stderr):
    '''
    Run an executable with the given argv and input file,
    and return the exit code and standard output.
    '''
    import asyncio

    output_chunks = []

    proc = await asyncio.create_subprocess_shell(
        ' '.join((executable, *argv)),
        limit=128*1024**2,  # 128 MiB
        stdin=input_file,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    was_err = False

    async def process_stdout(stdout):
        nonlocal was_err
        while (line := (await stdout.readline()).decode()):
            output_chunks.append(line)
            print(line, end='')
            was_err = False

    async def process_stderr(stderr):
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
            process_stdout(proc.stdout),
            process_stderr(proc.stderr),
    )

    return await proc.wait(), ''.join(output_chunks)


async def execute_interactive_impl(executable,
                                   interactor,
                                   argv,
                                   sample_in,
                                   ):
    '''
    Run two executables communicating to each other
    through stdin and stdout.

    argv is given to `interactor`.

    `sample_in` is given to `interactor`'s stdin
    before the communication starts.
    '''
    import asyncio

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

    async def forward(src,
                      dst,
                      begin_pre,
                      continue_pre,
                      echo_color = None):
        nonlocal last_begin_pre
        while (line_bytes := (await src.readline())):
            line = line_bytes.decode()
            if last_begin_pre == begin_pre:
                click.echo(continue_pre, nl=False)
            else:
                click.echo(begin_pre, nl=False)
                last_begin_pre = begin_pre
            click.secho(line, fg=echo_color, nl=False)
            dst.write(line_bytes)

    if sample_in:
        click.secho('[SAMPLE]', fg='yellow', bold=True)
    for line in sample_in:
        click.echo(line, nl=False)
        inte_proc.stdin.write(line.encode())

    await asyncio.gather(
        forward(
            exec_proc.stdout,
            inte_proc.stdin,
            click.style('\nEXECUTABLE | ', fg='blue', bold=True),
            click.style('           | ', fg='blue', bold=True),
        ),
        forward(
            inte_proc.stdout,
            exec_proc.stdin,
            click.style('\nINTERACTOR | ', fg='magenta', bold=True),
            click.style('           | ', fg='magenta', bold=True),
            'yellow',
        ),
    )

    return await exec_proc.wait(), await inte_proc.wait()


def execute(executable, argv, input_file, style_stderr):
    '''
    Wrapper for :py:function:`execute_impl` to start it
    in an async context.
    '''
    import asyncio
    return asyncio.run(execute_impl(
        executable, argv, input_file, style_stderr))


def execute_interactive(executable, interactor, argv, sample_in):
    '''
    Wrapper for :py:func:`execute_interactive_impl` to start it
    in an async context.
    '''
    import asyncio
    return asyncio.run(execute_interactive_impl(
        executable, interactor, argv, sample_in))

