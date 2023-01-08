from .language import Language

WARNINGS = (
    '-Wall -Wextra -Wshadow -Wformat=2 -Wfloat-equal -Wconversion '
    '-Wlogical-op -Wshift-overflow -Wduplicated-cond -Wcast-qual -Wcast-align '
    '-Wno-variadic-macros '
)

SANITIZERS = (
    '-fsanitize=address -fsanitize=undefined -fno-sanitize-recover '
    '-fstack-protector -fsanitize-address-use-after-scope '
)

C = Language(
    name='C',
    suffixes=('c', 'h',),
    debug_levels=(
        '-O2',
        '-O1 -g3 -DENABLE_DEBUG ',
        '-O0 -g3 -DENABLE_DEBUG ' + SANITIZERS,
        '-O0 -ggdb -DENABLE_DEBUG ' + SANITIZERS,
    ),
    compile_format=(
        f'gcc -std=gnu2x {WARNINGS} '
        '{debug_level} {extra_flags} '
        '{source_path} -o {executable_path} '
    ),
    cf_id=73,
)
