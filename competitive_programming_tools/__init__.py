'''Competitive programming tools'''
import shutil
import click

from . import utils

from .expand import expand
from .diff import diff
from .get import get
from .listen import listen
from .run import run
from .mk import mk, mke


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    '''Entry point for all cpt commands.'''
    ctx.ensure_object(dict)


@main.command()
def flush() -> None:
    '''Clears temporary data stored by competitive programming tools.'''
    shutil.rmtree(utils.TMP_DIR)


main.command()(expand)
main.command()(diff)
main.command()(get)
main.command()(listen)
main.command()(mk)
main.command()(mke)
main.command()(run)
