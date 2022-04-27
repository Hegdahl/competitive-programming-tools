import os
import shutil

import click
from requests import head

from .utils import TMP_DIR, ensure_dir
from .get_executable import get_executable
from .languages import CPP

@click.argument('header', type=str)
def mkpch(header):
    '''
    Create precompiled headers for each debug level.
    '''

    header_holder_path = os.path.join(TMP_DIR, 'header_holder.hpp')
    with open(header_holder_path, 'w', encoding='UTF-8') as header_holder:
        header_holder.write(f'#include <{header}>')

    pch_dir = os.path.join(TMP_DIR, 'pch')

    for debug_level in range(len(CPP.debug_levels)):
        dir = os.path.join(pch_dir, str(debug_level), os.path.dirname(header))
        ensure_dir(dir)

        path = os.path.join(dir, f'{os.path.basename(header)}.gch')
        if os.path.exists(path):
            os.remove(path)

        pch_path = get_executable(
            source_path=header_holder_path,
            debug_level=debug_level,
            extra_flags='',
            force_recompile=True,
        )
        shutil.move(pch_path, path)
