'''Competitive programming tools'''
import asyncio
import os

import shutil
import click

from . import utils

from .expand import expand
from .listen import listen
from .mkpch import mkpch
from .run import run
from .stress import stress
from .submit import submit

if os.name == 'nt':
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    '''
    Entry point for all cpt commands.

    Run `cpt COMMAND --help` for more
    info about the command.
    '''
    ctx.ensure_object(dict)


@main.command()
def flush() -> None:
    '''Clears temporary data stored by competitive programming tools.'''
    shutil.rmtree(utils.TMP_DIR)


main.command()(expand)
main.command()(listen)
main.command()(mkpch)
main.command()(run)
main.command()(stress)
main.command()(submit)
