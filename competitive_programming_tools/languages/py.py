from .language import Language

PY_DEBUG_LEVELS = (
    'pypy',
    'python',
)

PY = Language(
    name='Python',
    suffixes=('py',),
    debug_levels=(
        'pypy3',
        'python',
    ),
    compile_format=(
        'echo "#!/usr/bin/{debug_level}" '
        '| cat - {source_path} > {executable_path} '
        '&& chmod +x {executable_path}'
    )
)
