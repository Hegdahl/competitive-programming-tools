'''
Provides :py:func:`expand`.
'''
from typing import Optional, Set, Tuple

import click

from .auto_path import AutoPath
from .stdin_or import StdinOr



def get_inner_path(current_dir, line: str) -> Tuple[Optional[str], Optional[str]]:
    '''
    Find the path of an included file.
    Returns (path, filename).
    If the line is not an include or the
    file was not found in the environment
    variable `CPT_EXPAND_PATH`, return (None, None).
    '''
    import os

    local_match = local_include_matcher.match(line)
    if local_match:
        path = os.path.join(current_dir, local_match.group(1))
        if os.path.isfile(path):
            return path, local_match.group(1)

    match = include_matcher.match(line)
    if not match:
        return None, None

    for include_dir in os.environ['CPT_EXPAND_PATH'].split(':'):
        path = os.path.join(include_dir, match.group(2))
        if os.path.isfile(path):
            return path, match.group(2)
    return None, None


def should_skip(line: str, minify: bool, is_top_level: bool) -> bool:
    '''
    Determine whether to exclude a line from
    the expanded code to shorten it a bit.
    '''
    line = line.strip()
    if line == "#pragma once":
        return True
    if not is_top_level and minify and (line.startswith('//') or not line):
        return True
    return False


def expand_impl(path: str,
                already_included: Set[str],
                minify: bool,
                is_top_level: bool = True) -> str:
    '''
    Replace includes found in `CPT_EXPAND_PATH`
    with source code recursively
    and return the result as a string.

    Comments are removed unless the file top level.
    '''
    import os

    res = []
    with open(path, encoding='utf-8') as file:
        for line in file:
            if should_skip(line, minify, is_top_level):
                continue

            inner_path, inner_name = get_inner_path(os.path.dirname(path), line)

            if inner_path is None or inner_name is None:
                assert inner_path is None and inner_name is None
                res.append(line)
            elif inner_name not in already_included:
                already_included.add(inner_name)
                res.append(f'// <{inner_name}>\n')
                res.append(expand_impl(inner_path, already_included, False))
                res.append(f'// </{inner_name}>\n')
    return ''.join(res)


@click.argument('source', type=StdinOr(AutoPath()))
@click.option('--tmp-file', is_flag=True,
              help=('Put the result in a temporary file and'
                    'print the name of the temp file instead.'))
@click.option('--no-minify', is_flag=True,
              help=('Keep comments and empty lines in included files'))
def expand(source: str, tmp_file: bool, no_minify: bool, is_cli=True) -> Optional[str]:
    '''
    Replace cpt includes with source code (for submission to online judges)
    Specifically for C++.
    '''
    global include_matcher, local_include_matcher
    import re
    import os
    from .utils import TMP_DIR

    include_matcher = re.compile(r'^#include\s*(<|")(.*)(>|")$')
    local_include_matcher = re.compile(r'^#include\s*"(.*)"$')

    minify = not no_minify

    res = expand_impl(source, set(), minify)

    if tmp_file:
        out_path = os.path.join(TMP_DIR, os.path.basename(source))
        with open(out_path, 'w', encoding='utf-8') as file:
            file.write(res)
        res = out_path
    if is_cli:
        return print(res)
    else:
        return res
