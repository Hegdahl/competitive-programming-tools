'''Given a the name of a snippet, print the content it to stdout.'''

import os
import click

from . import DIRNAME
from .auto_path import AutoPath

SNIPPETS = os.path.join(DIRNAME, 'snippets')

@click.argument('name', type=AutoPath(['cpp'], root = SNIPPETS))
def get(name, silent = False):
    '''Given a the name of a snippet, print the content it to stdout.'''
    if not name.endswith('.cpp'):  name += '.cpp'
    path = os.path.join(SNIPPETS, name)
    if os.path.exists(path):
        with open(path) as file:
            content = file.read()
            _, content = content.split('/*BEGIN_SNIPPET*/\n')
            content, _ = content.split('\n/*END_SNIPPET*/')
            if silent:
                return content
            else:
                print(content)
    else:
        click.secho(f'\nCould not find snippet {name!r}.', fg='red')
