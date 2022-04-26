'''
Provides functions for creating files
with boilerplate for solutions.
'''
import os
import click

from .get import get as get_snippet

NO_EXIST = click.Path(file_okay=False, dir_okay=False)


@click.argument('path', type=NO_EXIST)
@click.pass_context
# pylint: disable=invalid-name
def mk(ctx: click.Context, path: str) -> str:
    '''Create a file containing snippets/main'''
    if not path.endswith('.cpp'):
        return mk(NO_EXIST.convert(f'{path}.cpp', None, ctx))

    with open(path, 'w', encoding='utf-8') as file:
        main_src = get_snippet('main', silent=True)
        assert main_src is not None
        file.write(main_src)

    return path


@click.argument('path', type=NO_EXIST)
def mke(path: str) -> None:
    '''Create a file containing snippets/main and open it in $EDITOR'''
    path = mk(path)
    os.system(f'$EDITOR {path}')
