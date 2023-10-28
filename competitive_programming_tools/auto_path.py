'''
Provides :py:class:`AutoPath`.
'''
import click

from .languages import SUFF_TO_LANG


class AutoPath(click.ParamType):
    '''
    Tries finding a path by appending suffixes.
    '''

    name = 'auto-path'

    def __init__(self,
                 suffixes = tuple(SUFF_TO_LANG.keys()),
                 root = ''):
        self.suffixes = suffixes
        self.root = root

    def convert(self, value, param, ctx):
        import os
        value = os.path.join(self.root, value.strip('\n'))

        attempts = (value, *(f'{value}.{suffix}' for suffix in self.suffixes))

        converter = click.Path(exists=True, dir_okay=False).convert

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

