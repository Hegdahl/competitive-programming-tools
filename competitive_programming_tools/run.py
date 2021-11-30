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
import subprocess
import click
from time import perf_counter

from .auto_path import AutoPath
from . import DIRNAME, TMP_DIR, error

INCLUDE = os.path.join(DIRNAME, 'include')

def time(f):
    t0 = perf_counter()
    res = f()
    tf = perf_counter()
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
@click.pass_context
def run(ctx, source, debug_level, force_recompile, extra_flags, testset, testset_auto):
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
            time_used, completed = time(
                lambda: subprocess.run(
                    executable,
            ))

            click.secho(f'{round(time_used * 1000)} ms', fg = 'blue', err = True)

            if completed.returncode:
                error(f'crashed ({returncode})')

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

                time_used, completed = time(
                    lambda: subprocess.run(
                        executable,
                        input = input_data.encode(),
                        capture_output = True,
                ))
                results.append([test_name, '??', time_used])

                output = completed.stdout.decode()
                print(output.rstrip('\n'))

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
