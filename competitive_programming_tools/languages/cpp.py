from ..utils import TMP_DIR
from .language import Language

WARNINGS = (
    '-Wall -Wextra -Wshadow -Wformat=2 -Wfloat-equal -Wconversion '
    '-Wlogical-op -Wshift-overflow -Wduplicated-cond -Wcast-qual -Wcast-align '
    '-Wno-variadic-macros -Wno-sign-conversion '
)

SANITIZERS = (
    '-fsanitize=address -fsanitize=undefined -fno-sanitize-recover '
    '-fstack-protector -fsanitize-address-use-after-scope '
)

GLIBCXX_DEBUG = '-D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC '

CPP = Language(
    name='C++',
    suffixes=('cpp', 'cxx', 'cc', 'hpp'),
    debug_levels=(
        '-O2 -g0',
        '-O1 -g0 -DENABLE_DEBUG ',
        '-O0 -g3 -DENABLE_DEBUG ' + SANITIZERS,
        '-O0 -g3 -DENABLE_DEBUG ' + GLIBCXX_DEBUG + SANITIZERS,
    ),
    compile_format=(
        f'g++ -std=gnu++2a {WARNINGS} '
        '{debug_level} {extra_flags} '
        '{source_path} -o {executable_path} '
    ),
    cf_id=73,
)
