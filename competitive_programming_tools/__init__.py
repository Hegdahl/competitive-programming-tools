'''Competitive programming tools'''
import shutil
import click

from . import utils

from .diff import diff
from .expand import expand
from .get import get
from .listen import listen
from .mk import mk, mke
from .run import run
from .stress import stress
from .submit import submit


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    '''Entry point for all cpt commands.'''
    ctx.ensure_object(dict)


@main.command()
def flush() -> None:
    '''Clears temporary data stored by competitive programming tools.'''
    shutil.rmtree(utils.TMP_DIR)


main.command()(diff)
main.command()(expand)
main.command()(get)
main.command()(listen)
main.command()(mk)
main.command()(mke)
main.command()(run)
main.command()(stress)
main.command()(submit)
