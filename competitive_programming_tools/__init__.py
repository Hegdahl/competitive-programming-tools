'''Competitive programming tools'''
import os
import shutil
from tempfile import mkstemp
import click

DIRNAME = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

TMP_DIR = os.path.join('/tmp', 'competitive_programming_tools')
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)

@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)

@main.command()
@click.pass_context
def flush(ctx):
    '''Clears temporary data stored by copetitive programming tools.'''
    shutil.rmtree(TMP_DIR)

from .run import run
from .get import get

main.command()(run)
main.command()(get)
