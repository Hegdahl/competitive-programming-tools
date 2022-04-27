'''
General utilities.
'''

import os
import pathlib
import time
from typing import Any, Callable, Tuple

import click

DIRNAME = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
TMP_DIR = os.path.join(os.environ['TEMP'], 'competitive_programming_tools')


def ensure_dir(path):
    '''Create a directory at the path if it wasn't there.'''
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

ensure_dir(TMP_DIR)


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


def time_func(func: Callable[..., Any],
              *args: Any,
              **kwargs: Any) -> Tuple[float, Any]:
    '''
    Call `func` and meassure how long it takes to execute.
    Return (the time taken, the result of `func).
    '''
    start_time = time.perf_counter()
    res = func(*args, **kwargs)
    end_time = time.perf_counter()
    return (end_time-start_time), res
