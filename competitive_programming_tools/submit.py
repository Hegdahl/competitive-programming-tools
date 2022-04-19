'''
Provides `submit`.
'''

import asyncio
import re
from typing import cast, Type

import click

from .auto_path import AutoPath
from .expand import expand
from .languages import SUFF_TO_LANG
from .online_judges import ONLINE_JUDGES, OnlineJudge
from .utils import error

url_matcher = re.compile(r' \* url: *(https://.+)')


@click.argument('source', type=AutoPath())
def submit(source: str):
    '''
    Figure out where to submit a `source`,
    then submit it and show the result
    in the terminal.
    '''
    try:
        suf = source.rsplit('.', 1)[1]
        lang = SUFF_TO_LANG[suf]
    except (KeyError, IndexError):
        error('Could not detect language for file ' +
              click.style(repr(source), fg='yellow'))
        return

    with open(source, encoding='utf-8') as source_file:
        raw_content = source_file.read()
    url_match = url_matcher.search(raw_content)
    if url_match is None:
        error('Could not find the url of the problem.')
        click.secho('        Make sure there is a comment containing:',
                    err=True)
        click.secho('        * url: ', fg='blue', err=True, nl=False)
        click.secho('https://<the problem url>', fg='yellow', err=True)
        return
    url = url_match[1]

    for OnlineJudgeType in ONLINE_JUDGES:
        OnlineJudgeType = cast(Type[OnlineJudge], OnlineJudgeType)
        if OnlineJudgeType.accepts_url(url):
            if OnlineJudgeType.FORMAT == 'FILE':
                path_or_source = expand(source=source,
                                        tmp_file=True, is_cli=False)
            elif OnlineJudgeType.FORMAT == 'SOURCE':
                path_or_source = expand(source=source,
                                        tmp_file=False, is_cli=False)
            else:
                raise ValueError(
                    f'Unknown solution format: {OnlineJudgeType.FORMAT!r}'
                )

            assert path_or_source is not None
            asyncio.run(OnlineJudgeType().submit(url, path_or_source, lang))
            return

    error('Could not figure out which online judege ' +
          click.style(repr(url), fg='yellow') +
          ' belongs to.')
