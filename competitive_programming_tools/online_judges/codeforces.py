import asyncio
import os
import re

import aiohttp
from asyncspinner import Spinner
from bs4 import BeautifulSoup
import click

from ..utils import error, TMP_DIR

LOGIN_URL = 'https://codeforces.com/enter'
url_matcher = re.compile(r'^https://codeforces\.com/.*/problem/.*')

class Codeforces:
    format = 'SOURCE'

    @staticmethod
    def accepts_url(url: str):
        return url_matcher.match(url) is not None

    def __init__(self):
        with open(os.path.join(os.path.expanduser('~'), '.secret', 'cpt@codeforces')) as secret_file:
            self.username, self.password = (line.rstrip('\n') for line in secret_file.readlines())

    async def _post_form(self, session, url, form, **changes):
        inputs = {}
        for tag in form.find_all('input'):
            name = tag.attrs.get('name')
            if name is None:
                continue
            value = tag.attrs.get('value', '')
            inputs[name] = value
        inputs.update(changes)
        async with session.post(url, data=inputs) as response:
            return response.status, await response.text()

    def find_submission_error(self, html_text):
        soup = BeautifulSoup(html_text, features='html5lib')
        error_span = soup.find('span', class_='error')
        if error_span is not None:
            return error_span.text

    async def _update_submission_info(self, session, url, info):
        async with session.get(url) as response:
            assert response.status == 200
            soup = BeautifulSoup(await response.text(), features='html5lib')

        try:
            if 'id' not in info:
                    info['id'] = int((
                        soup.find(class_='view-source') or
                        soup.find(class_='hiddenSource')
                    ).text)

            row = soup.find('tr', {'data-submission-id': info['id']})

            verdict_wrapper = row.find(class_='submissionVerdictWrapper')
            if verdict_wrapper is None:
                verdict_cell = row.find('td', class_='status-verdict-cell')
            else:
                verdict_cell, = verdict_wrapper.children
                if 'verdict-waiting' not in verdict_cell.attrs['class']:
                    info['finished'] = True
            time_cell = row.find(class_='time-consumed-cell')
            memory_cell = row.find(class_='memory-consumed-cell')

            info['verdict'] = ' '.join(verdict_cell.text.strip().split())
            info['time'] = ' '.join(time_cell.text.strip().split())
            info['memory'] = ' '.join(memory_cell.text.strip().split())
        except Exception:
            path = os.path.join(TMP_DIR, 'dump.html')
            with open(path, 'w') as dump:
                dump.write(str(soup))
            error('Error during parsing of the html dumped here:')
            click.secho(path, fg='yellow')
            raise

    async def submit(self, url, solution, lang):
        async with aiohttp.ClientSession() as session:
            click.echo('Loggin in ... ', nl=False, err=True)
            async with session.get(LOGIN_URL) as response:
                assert response.status == 200
                soup = BeautifulSoup(await response.text(), features='html5lib')
            login_form = soup.find(id='enterForm')
            status, _ = await self._post_form(
                session, LOGIN_URL, login_form,
                handleOrEmail=self.username,
                password=self.password,
            )
            if status != 200:
                click.echo(err=True)
                error('Failed logging in.')
                return
            click.secho('ok!', fg='green', err=True)

            click.echo('Submitting ... ', nl=False, err=True)
            async with session.get(url) as response:
                assert response.status == 200
                soup = BeautifulSoup(await response.text(), features='html5lib')
            submit_form = soup.find(class_='table-form').parent
            status, submission_response = await self._post_form(
                session, url, submit_form,
                programTypeId=lang.cf_id,
                sourceFile=solution,
            )
            if status != 200:
                click.echo(err=True)
                error('Failed submitting')
                return

            if (submit_error := self.find_submission_error(submission_response)) is not None:
                click.echo(err=True)
                error(submit_error)
                return

            click.secho('ok!', fg='green', err=True)

            my_submissions_url = url.split('/problem/', 1)[0] + '/my'

            submission_info = {
                'finished': False,
            }
            async with Spinner() as spinner:
                while not submission_info['finished']:
                    await self._update_submission_info(session, my_submissions_url, submission_info)
                    verdict = submission_info['verdict']
                    verdict_color = 'red'
                    if not submission_info['finished']:
                        verdict_color = 'yellow'
                    elif (''.join(chr for chr in verdict.lower() if chr.isalpha())
                            in ('accepted', 'pretestspassed', 'happynewyear')):
                        verdict_color = 'green'
                    styled_verdict = click.style(
                        verdict,
                        fg=verdict_color, bold=True
                    )

                    time_used = submission_info['time']
                    memory_used = submission_info['memory']
                    resource_block = click.style(
                        f'[{time_used} / {memory_used}]',
                        fg='blue', bold=True,
                    )
                    info_str = f'{resource_block} {styled_verdict}'
                    spinner.message = info_str

                    if not submission_info['finished']:
                        await asyncio.sleep(1)
                click.echo(info_str, err=True)
