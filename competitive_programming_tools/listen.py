'''Listen for information about problems from the "Competitive Companion" extension.'''
import http.server
import json
import os
import threading
import click

from . import warn
from .get import get as get_snippet

def format_name(s):
    if len(s) > 3 and s[0].isalnum() and s[0].isupper() and s[1:3] == '. ':
        return s[0]

    return ''.join(
        c for c in s.strip().lower().replace(' ', '_')
        if c == '-' or c == '_' or c.isalnum()
    )

def load_problem(data):
    name = format_name(data['name'])

    if data['tests']:
        sample_dir = os.path.join(CONTEST_DIRECTORY, 'samples')
        if not os.path.exists(sample_dir):
            os.mkdir(sample_dir)

        for i, sample in enumerate(data['tests']):
            in_path = os.path.join(sample_dir, f'{name}_{i+1:02d}.in')
            out_path = os.path.join(sample_dir, f'{name}_{i+1:02d}.ans')

            if os.path.exists(in_path):
                warn(f'{click.style(repr(in_path), fg = "yellow")} already exists!')
            else:
                with open(in_path, 'w') as file:
                    file.write(sample['input'])

            if os.path.exists(out_path):
                warn(f'{click.style(repr(out_path), fg = "yellow")} already exists!')
            else:
                with open(out_path, 'w') as file:
                    file.write(sample['output'])

    sol_path = os.path.join(CONTEST_DIRECTORY, f'{name}.cpp')

    if os.path.exists(sol_path):
        warn(f'{click.style(repr(sol_path), fg = "yellow")} already exists!')
    else:
        with open(sol_path, 'w') as file:
            file.write(get_snippet('main', silent=True))

    click.echo(click.style(f'[{name}]', fg = 'green') +
               f' {data["timeLimit"]} ms / {data["memoryLimit"]} MB', err = True)

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))

        data = json.loads(self.rfile.read(content_len))
        load_problem(data)

        self.send_response(200)
        self.end_headers()

    def log_message(self, *_, **__):
        pass

@click.argument('directory', required = False,
                type = click.Path(file_okay = False, dir_okay = True))
@click.option('-p', '--port', type = click.IntRange(0, 65535), default = 10042)
def listen(directory, port):
    '''Listen for information about problems from the "Competitive Companion" extension.'''

    if directory is None:
        directory = os.getcwd()

    if not os.path.exists(directory):
        os.mkdir(directory)

    if len(os.listdir(directory)):
        warn(f'Directory {click.style(repr(directory), fg = "yellow")} is not empty!\n')

    global CONTEST_DIRECTORY
    CONTEST_DIRECTORY = directory

    click.echo('Listening for Competitive Companion on port '
               f'{click.style(port, fg = "green")}', err = True)
    httpd = http.server.ThreadingHTTPServer(('', port), HTTPRequestHandler)

    t = threading.Thread(target=lambda: httpd.serve_forever(1/20))
    t.start()

    # click.pause messes up line-breaks while paused
    #click.pause('Press any key to exit...\n', err = True)
    if os.name == 'nt':
        os.system('pause')
    else:
        os.system('read -n1 -r -p "Press any key to exit...\n" key')

    httpd.shutdown()
    t.join()
