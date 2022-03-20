import os
from typing import cast, Callable, Optional, Sequence, Union

import click

from .languages import SUFF_TO_LANG


class AutoPath(click.ParamType):
    '''
    Tries finding a path by appending suffixes.
    '''

    name = 'auto-path'

    def __init__(self,
                 suffixes: Sequence[str] = tuple(SUFF_TO_LANG.keys()),
                 root: Union[str, os.PathLike[str]] = ''):
        self.suffixes = suffixes
        self.root = root

    def convert(self,
                value: str,
                param: Optional[click.Parameter],
                ctx: Optional[click.Context]) -> os.PathLike[str]:

        value = os.path.join(self.root, value.strip('\n'))

        attempts = (value, *(f'{value}.{suffix}' for suffix in self.suffixes))

        converter = cast(
            Callable[[str, Optional[click.Parameter], Optional[click.Context]],
                     os.PathLike[str]],
            click.Path(exists=True, dir_okay=False).convert,
        )

        messages = []

        for attempt in attempts:
            try:
                return converter(attempt, param, ctx)
            except click.BadParameter as exc:
                messages.append(exc.message)

        self.fail(
            '\n  Neither the path nor any of its concatenations with suffixes'
            f' {self.suffixes!r} are valid:\n    ' +
            '\n    '.join(messages)
        )
