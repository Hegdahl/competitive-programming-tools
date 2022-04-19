'''
Provides :py:class:`StdinOr`.
'''

from typing import Any, Optional

import click


class StdinOr(click.ParamType):
    '''
    If the input is '-' (without the quotes),
    replace the input with the content of stdin.
    '''
    name = 'auto-path'

    def __init__(self, inner: Any):
        self.inner = inner

    def convert(self,
                value: Any,
                param: Optional[click.Parameter],
                ctx: Optional[click.Context]) -> Any:
        if value == '-':
            lines = []
            try:
                while 1:
                    lines.append(input())
            except EOFError:
                pass
            value = '\n'.join(lines)+'\n'

        return self.inner.convert(value, param, ctx)
