from typing import cast, Any, Callable, Dict, List, TypeAlias, Union
import re

ACCEPTABLE_PRECISION_ERROR = 1e-3

WarningSet: TypeAlias = Dict[str, Union[float]]
IgnoredPropertyChecker: TypeAlias = Callable[[str, str, WarningSet], bool]

check_float_format = re.compile(r'^\d+\.\d+$')
whitespace_chunk = re.compile(r'(\s+)')


class LenientChecker:
    IGNORE_PROPERTY: Dict[str, IgnoredPropertyChecker] = {}

    @classmethod
    def register_ignore(cls, name: str) -> Callable[[Any], Any]:
        def dec(f: IgnoredPropertyChecker) -> IgnoredPropertyChecker:
            cls.IGNORE_PROPERTY[name] = f
            return f
        return dec

    def __init__(self, participant_answer: str, judge_answer: str):
        self.accept = False
        self.ignored_properties = set()
        self.warnings: WarningSet = dict()

        p_tokens = cast(List[str], whitespace_chunk.split(participant_answer))
        j_tokens = cast(List[str], whitespace_chunk.split(judge_answer))

        if len(p_tokens) != len(j_tokens):
            self.ignored_properties.add('whitespace')
            p_tokens = cast(
                List[str], whitespace_chunk.split(participant_answer.strip()))
            j_tokens = cast(
                List[str], whitespace_chunk.split(judge_answer.strip()))

        if len(p_tokens) != len(j_tokens):
            return

        for p_token, j_token in zip(p_tokens, j_tokens):
            if p_token == j_token:
                continue

            for name, check in self.IGNORE_PROPERTY.items():
                if check(p_token, j_token, self.warnings):
                    self.ignored_properties.add(name)
                    break
            else:
                return

        self.accept = True


@LenientChecker.register_ignore('whitespace')
def ignore_whitespace(p_token: str,
                      j_token: str,
                      warnings: WarningSet) -> bool:
    return p_token.isspace() and j_token.isspace()


@LenientChecker.register_ignore('case')
def ignore_case(p_token: str, j_token: str, warnings: WarningSet) -> bool:
    return p_token.lower() == j_token.lower()


@LenientChecker.register_ignore('precision')
def ignore_precision(p_token: str, j_token: str, warnings: WarningSet) -> bool:
    if check_float_format.match(p_token) is None:
        return False
    if check_float_format.match(p_token) is None:
        return False

    p_val = float(p_token)
    j_val = float(j_token)

    error = abs(p_val-j_val) / max(1, j_val)
    if error > ACCEPTABLE_PRECISION_ERROR:
        return False

    if 'error' not in warnings or error > warnings['precision error']:
        warnings['precision error'] = error

    return True
