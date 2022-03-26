from functools import partial

from typing import Protocol, Sequence


class CompileCommandGen(Protocol):
    def __call__(self, *, source_path: str, executable_path: str) -> str: ...


class Language:
    def __init__(self, *,
                 name: str,
                 suffixes: Sequence[str],
                 debug_levels: Sequence[str],
                 compile_format: str,
                 cf_id: int,
                 directly_runnable: bool = False):
        self.name = name
        self.suffixes = suffixes
        self.debug_levels = debug_levels
        self.compile_format = compile_format
        self.cf_id = cf_id
        self.directly_runnable = directly_runnable

    def get_compile_command_gen(self, *,
                                debug_level: int,
                                extra_flags: str) -> CompileCommandGen:
        return partial(
            self.compile_format.format,
            debug_level=self.debug_levels[debug_level],
            extra_flags=extra_flags,
        )
