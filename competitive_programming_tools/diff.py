import difflib
import itertools

import click

def paint(s, color):
    return '\n'.join(click.style(line, bold = True, fg = 'black', bg = color) for line in s.split('\n'))

def style_block(s, t, op, i1, i2, j1, j2):
    if op == 'replace':
        return '\n'.join(a+b for a, b, in itertools.zip_longest(
            paint(s[i1:i2], 'red').split('\n'),
            paint(t[j1:j2], 'green').split('\n')
        ))
    if op == 'delete':
        return paint(s[i1:i2], 'red')
    if op == 'insert':
        return paint(t[j1:j2], 'green')
    if op == 'equal':
        return click.style(s[i1:i2])
    raise ValueError(f'{op!r} is not a valid opcode.')

def diff_str(s, t):
    matcher = difflib.SequenceMatcher(lambda c: c.isspace(), a=s, b=t)
    res = ''.join(style_block(s, t, *block) for block in matcher.get_opcodes())
    return res

@click.argument('file1', type = click.File())
@click.argument('file2', type = click.File())
def diff(file1, file2):
    click.echo(diff_str(''.join(file1), ''.join(file2)), nl = False)
