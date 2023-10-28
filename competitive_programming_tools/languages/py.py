from .language import Language

PY_DEBUG_LEVELS = (
    'pypy3',
    'python',
    'python',
    'python',
)

PY = Language(
    name='Python',
    suffixes=('py',),
    debug_levels=PY_DEBUG_LEVELS,
    compile_format='{debug_level} {source_path}',
    cf_id=70,
    directly_runnable=True,
)
