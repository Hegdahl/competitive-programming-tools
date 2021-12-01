import click

class StdinOr(click.ParamType):
    name = 'auto-path'

    def __init__(self, inner, root = ''):
        self.inner = inner

    def convert(self, value, param, ctx):
        if value == '-':
            lines = []
            try:
                while 1: lines.append(input())
            except EOFError:
                pass
            value = '\n'.join(lines)+'\n'

        return self.inner.convert(value, param, ctx)
