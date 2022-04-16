import asyncio
import os
import re

from asyncspinner import Spinner
import click
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.keys import Keys

from ..utils import error, warn, TMP_DIR

SUBMIT_URL = '{url}/submit'
url_matcher = re.compile(r'^https://(.+)\.kattis\.com/(w+/)*problems/.*')

class Kattis:
    format = 'FILE'

    @staticmethod
    def accepts_url(url: str):
        return url_matcher.match(url) is not None

    def __init__(self):
        with open(os.path.join(os.path.expanduser('~'), '.secret', 'cpt@kattis')) as secret_file:
            self.username, self.password = (line.rstrip('\n') for line in secret_file.readlines())
        options = webdriver.FirefoxOptions()
        options.headless = True
        self.browser = webdriver.Firefox(options=options)

    async def log_in_if_needed(self):
        click.echo('Loggin in ... ', nl=False, err=True)
        try:
            email_ele = self.browser.find_element_by_class_name('email')
            email_ele.click();
        except NoSuchElementException:
            pass

        try:
            user_ele = self.browser.find_element_by_id('user_input')
            user_ele.clear()
            user_ele.send_keys(self.username)
            pass_ele = self.browser.find_element_by_id('password_input')
            pass_ele.clear()
            pass_ele.send_keys(self.password)
            pass_ele.send_keys(Keys.RETURN)
        except NoSuchElementException:
            click.secho(err=True)
            warn('Could not log in. Hoping user is already logged in.')
            return
        click.secho('ok!', fg='green', err=True)

    async def submit(self, url, solution, lang):
        subdomain = url_matcher.match(url)[1]
        submit_url = SUBMIT_URL.format(url=url)
        self.browser.get(submit_url)

        await self.log_in_if_needed()

        click.echo('Submitting ... ', nl=False, err=True)
        for _ in range(600):
            try:
                try:
                    toggle_ele = self.browser.find_element_by_id('file-upload')
                    toggle_ele.click()
                except ElementNotInteractableException:
                    pass

                file_ele = self.browser.find_element_by_id('sub_files_input')
                file_ele.clear()
                file_ele.send_keys(solution)

                lang_ele = self.browser.find_element_by_id('s2id_autogen2')
                lang_ele.send_keys(lang.name + Keys.ENTER)

                submit_ele = self.browser.find_element_by_name('submit')
                submit_ele.click()

                break
            except NoSuchElementException as exc:
                await asyncio.sleep(0.1)
        click.secho('ok!', fg='green', err=True)

        async with Spinner() as spinner:
            for _ in range(600):
                try:
                    status_ele = self.browser.find_element_by_class_name('status')
                    status = status_ele.get_attribute('innerHTML')
                    status = status.rsplit('</i>', 1)[1]
                    status = status.rsplit('</span>', 1)[0]
                    color = 'red'
                    if status.lower() in ('new', 'compiling', 'judging'):
                        color = 'yellow'
                    elif status.lower() in ('accepted'):
                        color = 'green'
                    spinner.message = click.style(status, bold=True, fg=color)
                    await asyncio.sleep(0.1)

                    if color != 'yellow':
                        break
                except (NoSuchElementException, StaleElementReferenceException) as exc:
                    await asyncio.sleep(0.1)
        self.browser.close()

        click.secho(status, bold=True, fg=color, err=True)
