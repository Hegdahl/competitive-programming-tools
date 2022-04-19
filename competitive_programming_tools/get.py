'''Given a the name of a snippet, print the content it to stdout.'''

import os
from typing import Optional

import click

from .utils import DIRNAME
from .auto_path import AutoPath
from .stdin_or import StdinOr

SNIPPETS = os.path.join(DIRNAME, 'snippets')


def list_snippets(ctx: click.Context,
                  _: click.Parameter,
                  value: bool) -> None:
    '''
    Print each filename in the snippet directory.
    '''
    if not value or ctx.resilient_parsing:
        return
    for name in os.listdir(SNIPPETS):
        print(name.rsplit('.')[0])
    ctx.exit()


@click.option('--list', is_flag=True, callback=list_snippets,
              expose_value=False, is_eager=True,
              help='List all available snippets and exit.')
@click.argument('name', type=StdinOr(AutoPath(root=SNIPPETS)))
def get(name: str, silent: bool = False) -> Optional[str]:
    '''Given a the name of a snippet, print the content it to stdout.'''

    if not name.endswith('.cpp'):
        name += '.cpp'
    path = os.path.join(SNIPPETS, name)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as file:
            content = file.read()
            _, content = content.split('/*BEGIN_SNIPPET*/\n')
            content, _ = content.split('/*END_SNIPPET*/')
            if silent:
                return content
            else:
                print(content)
                return None
    else:
        click.secho(f'\nCould not find snippet {name!r}.', fg='red')
        return None
