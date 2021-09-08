'''Competitive programming tools'''
import os
import shutil
from tempfile import mkstemp
import click

DIRNAME = os.path.realpath(os.path.dirname(__file__))

def path_fmt(path):
    return click.style(repr(path), fg='yellow') 

@click.group()
@click.option('-d', '--debug', is_flag=True, default=True)
@click.pass_context
def main(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

@main.command()
@click.option('-d', '--debug', is_flag=True, default=True)
@click.option('-t', '--time', is_flag=True)
@click.option('-T', '--test', type=int)
@click.option('-TT', '--test_all', is_flag=True)
@click.option('-s', '--sanitize', is_flag=True)
@click.option('-v', '--version')
@click.argument('source', type=click.Path())
@click.pass_context
def run(ctx, source, debug, time, test, test_all, version, sanitize):
    #print(test)
    #print(test_all)
    if not debug:
        ctx.obj['DEBUG'] = False

    def run_cpp(ctx, source, time):
        INCLUDE_PATH = os.path.join(os.path.dirname(DIRNAME), 'include')

        fd, out_path = mkstemp()
        os.close(fd)

        debug_txt = (
            '-DENABLE_DEBUG -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC '
            if ctx.obj['DEBUG'] else ''
        )

        sanitize_txt = (
            '-fsanitize=undefined '
            if sanitize else ''
        )

        warnings = (
            '-Wall -Wextra -pedantic -Wshadow -Wformat=2 -Wfloat-equal -Wconversion -Wlogical-op -Wshift-overflow '
            '-Wduplicated-cond -Wcast-qual -Wcast-align '
        )

        compile_cmd = (
            f'g++ -std=gnu++17 -O2 {warnings}{debug_txt}{sanitize_txt}'
            f'-I{INCLUDE_PATH} -o {out_path} {source}'
        )

        if version is not None:
            compile_cmd += f' -std={version}'

        if ctx.obj['DEBUG']:
            click.echo(f'Compiling {path_fmt(source)} '
                       f'to {path_fmt(out_path)}...', nl=False)
        if os.system(compile_cmd):
            click.secho('\nFailed compiling.', fg='red')
        else:
            if ctx.obj['DEBUG']:
                click.secho(' ok', fg='green')
            run_cmd = out_path
            if (time): run_cmd = 'time -f "%Us (%es)" '+run_cmd
            os.system(run_cmd)
            os.remove(out_path)

    def run_py(ctx, source, time):
        os.system(f'{"time " if time else ""}python {source}')

    if not os.path.exists(source):
        if (os.path.exists(source + '.cpp')):
            source += '.cpp'
        else:
            raise click.UsageError(
                f'File does not exist: {path_fmt(source)}')
    file_type = os.path.basename(source).rpartition('.')[-1]
    {
        'cpp': run_cpp,
        'py': run_py,
    }.get(
        file_type,
        lambda *args, **kwargs: click.secho(
            f'Unknown file type: {path_fmt(file_type)}', fg='red')
    )(ctx, source, time=time)

def mk_impl(ctx, name):
    def fallback(name):
        with open(name, 'w+'): pass
    def mkcpp(name):
        shutil.copy(os.path.join(DIRNAME, '..','templates', 'main.cpp'),
                    name)

    filename = os.path.basename(name)
    parts = filename.split('.')
    if len(parts) == 1:
        name += '.cpp'
        lang = 'cpp'
    else:
        lang = parts[-1]

    if (os.path.exists(name)):
        raise click.UsageError(f'File already exists: {path_fmt(name)}')
    
    {
        'cpp': mkcpp,
    }.get(lang, fallback)(name)
    return name

@main.command()
@click.argument('name', type=click.Path(exists=False))
@click.pass_context
def mk(ctx, name):
    mk_impl(ctx, name)

@main.command()
@click.argument('name', type=click.Path(exists=False))
@click.argument('count', type=click.INT)
@click.pass_context
def mks(ctx, name, count):
    os.mkdir(name)
    for i in range(count):
        mk_impl(ctx, os.path.join(name, chr(ord('A')+i)))

@main.command()
@click.argument('name', type=click.Path(exists=False))
@click.pass_context
def mke(ctx, name):
    os.system(f'$EDITOR {mk_impl(ctx, name)}')

@main.command()
@click.argument('name', type=click.Path())
@click.pass_context
def paste(ctx, name):
    i = 1
    while os.path.exists(f'{name}{i:0>2}.in'):
        i += 1
    path = f'{name}{i:0>2}.in'

    if ctx.obj['DEBUG']:
        click.secho(f'Pasting into file: {path_fmt(path)}')
        click.secho(f'Press Ctrl+D when finished.')

    s = '';
    while True:
        try:
            s += input()+'\n';
        except EOFError:
            break

    with open(path, 'w') as file: 
        file.write(s)
        if ctx.obj['DEBUG']:
            click.secho('ok', fg='green')

@main.command()
@click.argument('name', type=str)
@click.pass_context
def get(ctx, name):
    if not name.endswith('.cpp'):  name += '.cpp'
    path = os.path.join(DIRNAME, '..', 'snippets', name)
    if os.path.exists(path):
        with open(path) as file:
            content = file.read()
            _, content = content.split('/*BEGIN_SNIPPET*/\n')
            content, _ = content.split('/*END_SNIPPET*/')
            print(content)
    else:
        click.secho(f'\nCould not find snippet {name!r}.', fg='red')
