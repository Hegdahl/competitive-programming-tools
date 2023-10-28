'''
Provides :py:class:`StdinOr`.
'''
import click


class StdinOr(click.ParamType):
    '''
    If the input is '-' (without the quotes),
    replace the input with the content of stdin.
    '''
    name = 'auto-path'

    def __init__(self, inner):
        self.inner = inner

    def convert(self, value, param, ctx):
        if value == '-':
            lines = []
            try:
                while 1:
                    lines.append(input())
            except EOFError:
                pass
            value = '\n'.join(lines)+'\n'

        return self.inner.convert(value, param, ctx)
