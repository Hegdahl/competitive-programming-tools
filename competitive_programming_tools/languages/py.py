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
    compile_format='{debug_level} {source_path}',
    cf_id=70,
    directly_runnable=True,
)
