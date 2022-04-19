'''
Provides :py:class:`Kattis`.
'''

import asyncio
import os
import re

import aiohttp
from asyncspinner import Spinner
from bs4 import BeautifulSoup
import click

from .online_judge import OnlineJudge
from ..utils import error, TMP_DIR


class Kattis(OnlineJudge):
    '''
    Handles submitting solutions to https://*.kattis.com
    '''

    FORMAT = 'FILE'
    URL_PATTERN = r'^https://(.+)\.kattis\.com/(?:w+/)*problems/(.*)$'

    SUBMISSION_ID_PATTERN = r'^Submission received\. Submission ID: (\d+)\.$'
    TEST_NUMBER_PATTERN = r'Test case (\d+)/(\d+): (.+)'

    SUBMIT_URL = '{url}/submit'
    LOGIN_URL = 'https://{subdomain}.kattis.com/login'
    SUBMISSIONS_URL = (
        'https://{subdomain}.kattis.com'
        '/submissions/{submission_id}'
    )

    NOT_DONE_VERDICTS = ('new', 'compiling', 'running')
    ACCEPTED_VERDICTS = ('accepted',)

    def __init__(self):
        with open(os.path.join(os.path.expanduser('~'),
                               '.secret', 'cpt@kattis'),
                  encoding='utf-8') as secret_file:
            self.username, self.token = (
                line.rstrip('\n')
                for line in secret_file.readlines()
            )

    def _dump_error(self, body, message):
        path = os.path.join(TMP_DIR, 'dump.html')
        with open(path, 'w', encoding='utf-8') as dump:
            dump.write(str(body))
        error('html dumped here:')
        click.secho(path, fg='yellow')
        error(message)

    async def _log_in(self, session, subdomain):
        url = Kattis.LOGIN_URL.format(subdomain=subdomain)
        data = {
            'script': True,
            'user': self.username,
            'token': self.token,
        }
        async with session.post(url, data=data) as resp:
            if resp.status != 200:
                self._dump_error(
                    await resp.text(),
                    f'Failed logging in [{resp.status}].',
                )
                return False
            return True

    async def submit(self, url, solution, lang):
        '''
        Submit the `solution` Kattis,
        as a solution for the problem at the `url`.
        '''
        url_match = re.match(Kattis.URL_PATTERN, url)
        subdomain = url_match[1]
        problem_id = url_match[2]

        async with aiohttp.ClientSession(headers={
            'User-Agent': 'kattis-cli-submit',
        }) as session:
            if not await self._log_in(session, subdomain):
                return

            submit_url = Kattis.SUBMIT_URL.format(url=url)

            with open(solution, 'rb') as solution_file:
                data = aiohttp.FormData()
                data.add_field('script', 'true')
                data.add_field('submit', 'true')
                data.add_field('submit_ctr', '2')
                data.add_field('language', lang.name)
                data.add_field('problem', problem_id)
                data.add_field(
                    'sub_file[]',
                    solution_file,
                    filename=os.path.basename(solution),
                    content_type='application/octet-stream',
                )

                async with session.post(submit_url, data=data) as resp:
                    if resp.status != 200:
                        return self._dump_error(
                            await resp.text(),
                            f'Failed submitting [{resp.status}]'
                        )

                    resp_text = await resp.text()
                    id_match = re.match(
                        Kattis.SUBMISSION_ID_PATTERN,
                        resp_text,
                    )
                    if id_match is None:
                        return self._dump_error(
                            resp_text,
                            f'Failed submitting [{resp.status}]',
                        )

                    submission_id = id_match[1]

            if not await self._log_in(session, subdomain):
                return
            submission_url = Kattis.SUBMISSIONS_URL.format(
                subdomain=subdomain,
                submission_id=submission_id,
            )

            async with Spinner() as spinner:
                verdict = 'New'
                while verdict.lower() in Kattis.NOT_DONE_VERDICTS:
                    async with session.get(submission_url) as resp:
                        if resp.status != 200:
                            return self._dump_error(
                                await resp.text(),
                                'Failed checking submission status.',
                            )
                        soup = BeautifulSoup(
                            await resp.text(),
                            features='html5lib',
                        )

                    status_ele = soup.find(attrs={'data-type': 'status'})
                    if status_ele is None:
                        return self._dump_error(
                            soup,
                            'Failed finding status in HTML.',
                        )
                    verdict = status_ele.text

                    test_str = ''
                    try:
                        tests_ele = (soup
                                     .find(attrs={'data-type': 'testcases'})
                                     .find(class_='testcases')
                                     )

                        max_num = 0
                        max_den = 0

                        for test_ele in tests_ele.findChildren():
                            test_number_match = re.match(
                                Kattis.TEST_NUMBER_PATTERN,
                                test_ele.get('title', ''),
                            )
                            if test_number_match is None:
                                continue
                            num = int(test_number_match[1])
                            den = int(test_number_match[2])
                            test_verdict = test_number_match[3]

                            if (test_verdict.lower() in
                                    Kattis.ACCEPTED_VERDICTS):
                                max_num = max(num, max_num)
                            max_den = max(den, max_den)

                        if max_den:
                            test_str = f'{min(max_num+1, max_den)}/{max_den} '

                    except (AttributeError, TypeError) as exc:
                        try:
                            click.echo(f'test_ele: {test_ele!r}')
                        except NameError:
                            pass
                        click.echo(repr(exc), err=True)
                        self._dump_error(soup, 'Failed finding test cases')

                    time_str = ''
                    time_ele = soup.find(attrs={'data-type': 'cpu'})
                    if time_ele is not None:
                        time_text = time_ele.text
                        if time_text:
                            time_str = click.style(f'[{time_text}] ',
                                                   bold=True, fg='blue')

                    color = 'red'
                    if verdict.lower() in Kattis.NOT_DONE_VERDICTS:
                        color = 'yellow'
                    elif verdict.lower() in Kattis.ACCEPTED_VERDICTS:
                        color = 'green'

                    spinner.message = ''.join((
                        time_str,
                        test_str,
                        click.style(verdict, bold=True, fg=color),
                    ))

                    if verdict.lower() in Kattis.NOT_DONE_VERDICTS:
                        await asyncio.sleep(.5)
                click.secho(spinner.message)