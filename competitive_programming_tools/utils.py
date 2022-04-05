import os
import time
from typing import Any, Callable, Tuple

import click

DIRNAME = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
TMP_DIR = os.path.join(os.environ['TEMP'], 'competitive_programming_tools')
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)


def warn(message: str) -> None:
    '''Print a message to stderr styled as a warning.'''
    click.echo(click.style('[WARNING]', fg='black', bg='yellow', bold=True),
               nl=False, err=True)
    click.echo(f' {message}', err=True)


def error(message: str) -> None:
    '''Print a message to stderr styled as an error.'''
    click.echo(click.style('[ERROR]', fg='black', bg='red', bold=True),
               nl=False, err=True)
    click.echo(f' {message}', err=True)


def time_func(f: Callable[..., Any],
              *args: Any,
              **kwargs: Any) -> Tuple[float, Any]:
    t0 = time.perf_counter()
    res = f(*args, **kwargs)
    tf = time.perf_counter()
    return (tf-t0), res
