import os
import click

from .get import get as get_snippet

NO_EXIST = click.Path(file_okay = False, dir_okay = False)

@click.argument('path', type = NO_EXIST)
@click.pass_context
def mk(ctx, path):
    '''Create a file containing snippets/main'''
    if not path.endswith('.cpp'):
        return mk(NO_EXIST.convert(f'{path}.cpp', None, ctx))

    with open(path, 'w') as file:
        file.write(get_snippet('main', silent = True))

    return path

@click.argument('path', type = NO_EXIST)
def mke(path):
    '''Create a file containing snippets/main and open it in $EDITOR'''
    path = mk(path)
    os.system(f'$EDITOR {path}')
