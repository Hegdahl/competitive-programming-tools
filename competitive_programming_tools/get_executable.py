'''
Provides :py:func:`get_executable`.
'''

import click


class CompileError(Exception):
    '''
    Raised when some external compiler fails.
    '''
    def __init__(self, exit_code: int):
        super().__init__(self, f'Compiler exited with code {exit_code}.')
        self.exit_code = exit_code


def get_executable(*,
                   source_path: str,
                   debug_level: int,
                   extra_flags: str,
                   force_recompile: bool) -> str:
    '''
    Get the path to an executable corresponding to the source,
    by compiling, or using previously compiled executable.
    '''
    import os
    from hashlib import sha1

    from .languages import SUFF_TO_LANG
    from .utils import TMP_DIR, error

    suffix = source_path.rsplit('.', 1)[-1]

    try:
        lang = SUFF_TO_LANG[suffix]
    except KeyError as exc:
        error(f'Unknown file suffix: {suffix!r}')
        raise CompileError(1) from exc

    if lang.directly_runnable:
        return lang.get_compile_command_gen(
            debug_level=debug_level,
            extra_flags=extra_flags,
        )(source_path=source_path, executable_path='?')

    command = lang.get_compile_command_gen(
        debug_level=debug_level,
        extra_flags=extra_flags,
    )

    command_id_str = command(source_path=source_path, executable_path='?')

    source_id = sha1(source_path.encode()).hexdigest()[:16]
    command_id = sha1(command_id_str.encode()).hexdigest()[:16]

    source_copy_path = os.path.join(
        TMP_DIR,
        f'{source_id}-{command_id}.src',
    )
    executable_path = os.path.join(
        TMP_DIR,
        f'{source_id}-{command_id}.exe',
    )

    old_content = ''

    if os.path.exists(source_copy_path):
        with open(source_copy_path, 'r', encoding='utf-8') as file:
            old_content = ''.join(file)

    new_content = ''
    with open(source_path, 'r', encoding='utf-8') as file:
        new_content = ''.join(file)

    if new_content != old_content:
        force_recompile = True
        with open(source_copy_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

    if force_recompile and os.path.exists(executable_path):
        os.remove(executable_path)

    if not os.path.exists(executable_path):
        click.echo(
            f'Compiling {click.style(repr(source_path), fg="yellow")} ... ',
            err=True, nl=False
        )

        exit_code = os.system(
            command(source_path=source_path, executable_path=executable_path))
        if exit_code:
            click.echo(err=True)
            raise CompileError(exit_code)

        click.secho('done!', fg='green', err=True)

    return executable_path
