'''Competitive programming tools'''
import os
import shutil
from tempfile import mkstemp
import click

DIRNAME = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

TMP_DIR = os.path.join('/tmp', 'competitive_programming_tools')
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)

def warn(s):
    click.echo(click.style('[WARNING]', fg = 'black', bg = 'yellow', bold = True),
               nl = False, err = True)
    click.echo(f' {s}', err = True)

def error(s):
    click.echo(click.style('[ERROR]', fg = 'black', bg = 'red', bold = True),
               nl = False, err = True)
    click.echo(f' {s}', err = True)

@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)

@main.command()
@click.pass_context
def flush(ctx):
    '''Clears temporary data stored by copetitive programming tools.'''
    shutil.rmtree(TMP_DIR)

from .get import get
from .listen import listen
from .run import run
from .mk import mk, mke

main.command()(get)
main.command()(listen)
main.command()(mk)
main.command()(mke)
main.command()(run)
