import asyncio
import os
import re

import click

from .auto_path import AutoPath
from .expand import expand_impl
from .languages import SUFF_TO_LANG
from .online_judges import ONLINE_JUDGES
from .utils import error

url_matcher = re.compile(r' \* url: *(https://.+)')

@click.argument('source', type=AutoPath())
@click.pass_context
def submit(ctx: click.Context, source: str):
    try:
        suf = source.rsplit('.', 1)[1]
        lang = SUFF_TO_LANG[source.rsplit('.', 1)[1]]
    except (KeyError, IndexError):
        error('Could not detect language for file ' +
              click.style(repr(source), fg='yellow'))
        return

    content = expand_impl(source, set())
    url_match = url_matcher.search(content)
    if url_match is None:
        error('Could not find the url of the problem.')
        click.secho('        Make sure there is a comment containing:', err=True)
        click.secho('        * url: ', fg='blue', err=True, nl=False)
        click.secho('https://<the problem url>', fg='yellow', err=True)
        return
    url = url_match[1]

    for OnlineJudge in ONLINE_JUDGES:
        if OnlineJudge.accepts_url(url):
            oj = OnlineJudge()
            asyncio.run(oj.submit(url, content, lang))
            return

    error(f'Could not figure out which online judege ' +
            click.style(repr(url), fg='yellow') + 
            ' belongs to.')
