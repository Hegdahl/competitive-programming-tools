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
    '-Wlogical-op -Wshift-overflow -Wduplicated-cond -Wcast-qual -Wcast-align'
)

from hashlib import sha256
import os
import click

from .auto_path import AutoPath
from . import DIRNAME, TMP_DIR, error

INCLUDE = os.path.join(DIRNAME, 'include')

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
@click.pass_context
def run(ctx, source, debug_level, force_recompile, extra_flags):
    '''Executes a program from source.'''

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
        exit_code = os.system(executable) >> 8
        if exit_code:
            error(f'crashed ({exit_code})')
    except CompileError as exc:
        error('failed compiling.')
        return exc.exit_code
