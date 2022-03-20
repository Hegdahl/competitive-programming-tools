import re
import os
from typing import Optional, Set, Tuple

import click

from .utils import TMP_DIR
from .languages.cpp import INCLUDE
from .auto_path import AutoPath
from .stdin_or import StdinOr

include_matcher = re.compile(r'^#include\s*(<|")(.*)(>|")$')
include_guard = re.compile(r'^#.*ATCODER_[A-Z_]*_HPP')


def get_inner_path(line: str) -> Tuple[Optional[str], Optional[str]]:
    match = include_matcher.match(line)
    if not match:
        return None, None
    path = os.path.join(INCLUDE, match.group(2))
    if not os.path.isfile(path):
        return None, None
    return path, match.group(2)


def should_skip(line: str, is_source: bool) -> bool:
    if include_guard.match(line):
        return True
    line = line.strip()
    if line == "#pragma once":
        return True
    if not is_source and (line.startswith('//') or not line):
        return True
    return False


def expand_impl(path: str,
                already_included: Set[str],
                is_source: bool = True) -> str:
    res = []
    with open(path) as file:
        for line in file:
            if should_skip(line, is_source):
                continue

            inner_path, inner_name = get_inner_path(line)

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
def expand(source: str, tmp_file: str) -> None:
    '''
    Replace cpt includes with source code (for submission to online judges)
    '''
    res = expand_impl(source, set())

    if tmp_file:
        out_path = os.path.join(TMP_DIR,
                                f'EXPANDED-{os.path.basename(source)}')
        with open(out_path, 'w') as file:
            file.write(res)
        print(out_path)
    else:
        print(res)
