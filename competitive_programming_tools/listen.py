'''
Listen for information about problems
from the "Competitive Companion" extension.
'''

from datetime import datetime
import http.server
import json
import os
import threading
from typing import Any

import click

from .utils import warn
from .get import get as get_snippet


def format_name(s: str) -> str:

    # Codeforces style titles
    cf_parts = s.split('. ', 1)
    if (len(cf_parts) > 1 and
            1 <= len(cf_parts[0]) <= 3 and
            cf_parts[0][0].isalnum()):
        return cf_parts[0].upper()

    # AtCoder style titles
    ac_parts = s.split(' - ')
    if (len(ac_parts) > 1 and
            1 <= len(ac_parts[0]) <= 3 and
            ac_parts[0][0].isalnum()):
        return ac_parts[0]

    # Kattis style titles
    kattis_parts = s.split(' - ')
    if (len(kattis_parts) > 1 and
            kattis_parts[0].startswith('Problem ')):
        return kattis_parts[0][len('Problem '):]

    # Everything else
    return ''.join(
        c for c in s.strip().lower().replace(' ', '_')
        if c == '-' or c == '_' or c.isalnum()
    )


class ProblemLoader:
    def __init__(self, contest_directory: str):
        self.contest_directory = contest_directory

    def load_problem(self, data: Any) -> None:
        header = (
            '/**\n'
            f' * author:  {os.environ["USER"]}\n'
            f' * created: {datetime.now().strftime("%d.%m.%Y %H:%M")}\n'
            f' * problem: {data["name"]}\n'
            f' * url:     {data["url"]}\n'
            ' */\n'
        )

        filename = format_name(data['name'])

        if data['tests']:
            sample_dir = os.path.join(self.contest_directory, 'samples')
            if not os.path.exists(sample_dir):
                os.mkdir(sample_dir)

            for i, sample in enumerate(data['tests']):
                in_path = os.path.join(sample_dir, f'{filename}_{i+1:02d}.in')
                out_path = os.path.join(sample_dir, f'{filename}_{i+1:02d}.ans')

                if os.path.exists(in_path):
                    warn(click.style(repr(in_path), fg="yellow") +
                         ' already exists!')
                else:
                    with open(in_path, 'w') as file:
                        file.write(sample['input'])

                if os.path.exists(out_path):
                    warn(click.style(repr(out_path), fg="yellow") +
                         ' already exists!')
                else:
                    with open(out_path, 'w') as file:
                        file.write(sample['output'])

        sol_path = os.path.join(self.contest_directory, f'{filename}.cpp')

        if os.path.exists(sol_path):
            warn(click.style(repr(sol_path), fg="yellow") +
                 ' already exists!')
        else:
            with open(sol_path, 'w') as file:
                file.write(header + get_snippet('main', silent=True))

        click.echo(click.style(f'[{filename}]', fg='green') +
                   f' {data["timeLimit"]} ms / {data["memoryLimit"]} MB',
                   err=True)


def make_HTTPRequestHandler(problem_loader: ProblemLoader) -> Any:

    class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            content_len = int(self.headers.get('Content-Length'))

            data = json.loads(self.rfile.read(content_len))
            problem_loader.load_problem(data)

            self.send_response(200)
            self.end_headers()

        def log_message(self, *_: Any, **__: Any) -> None:
            pass

    return HTTPRequestHandler


@click.argument('directory', required=False,
                type=click.Path(file_okay=False, dir_okay=True))
@click.option('-p', '--port', type=click.IntRange(0, 65535), default=10042)
def listen(directory: str, port: int) -> None:
    '''
    Listen for information about problems
    from the "Competitive Companion" extension.
    '''

    if directory is None:
        directory = os.getcwd()

    if not os.path.exists(directory):
        os.mkdir(directory)

    if len(os.listdir(directory)):
        warn(f'Directory {click.style(repr(directory), fg="yellow")} '
             'is not empty!\n')

    click.echo('Listening for Competitive Companion on port '
               f'{click.style(port, fg="green")}', err=True)
    problem_loader = ProblemLoader(directory)
    httpd = http.server.ThreadingHTTPServer(
        ('', port),
        make_HTTPRequestHandler(problem_loader)
    )

    t = threading.Thread(target=lambda: httpd.serve_forever(1/20))
    t.start()

    # click.pause messes up line-breaks while paused
    # click.pause('Press any key to exit...\n', err = True)
    if os.name == 'nt':
        os.system('pause')
    else:
        os.system('read -n1 -r -p "Press any key to exit...\n" key')

    httpd.shutdown()
    t.join()
