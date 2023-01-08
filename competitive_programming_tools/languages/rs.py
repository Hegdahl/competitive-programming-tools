from .language import Language

WARNINGS = (
    ''  # TODO
)

SANITIZERS = (
    ''  # TODO
)

DEBUG_MODE = (
    ''  # TODO
)

RS = Language(
    name='Rust',
    suffixes=('rs',),
    debug_levels=(
        '-C opt-level=3',
        '-C opt-level=1' + DEBUG_MODE,
        '-C opt-level=0' + SANITIZERS,
        '-C opt-level=0' + DEBUG_MODE + SANITIZERS,
    ),
    compile_format=(
        f'rustc {WARNINGS} '
        '{debug_level} {extra_flags} '
        '{source_path} -o {executable_path} '
    ),
    cf_id=75,
)
