ACCEPTABLE_PRECISION_ERROR = 1e-3

from enum import Enum, auto
import re

check_float_format = re.compile(r'^\d+\.\d+$')
whitespace_chunk = re.compile(r'(\s+)')

class LenientChecker:
    IGNORE_PROPERTY = {}

    @classmethod
    def register_ignore(cls, name):
        def dec(f):
            cls.IGNORE_PROPERTY[name] = f
            return f
        return dec

    def __init__(self, participant_answer, judge_answer):
        self.accept = False
        self.ignored_properties = set()
        self.warnings = dict()

        p_tokens = whitespace_chunk.split(participant_answer)
        j_tokens = whitespace_chunk.split(judge_answer)

        if len(p_tokens) != len(j_tokens):
            self.ignored_properties.add('whitespace')
            p_tokens = whitespace_chunk.split(participant_answer.strip())
            j_tokens = whitespace_chunk.split(judge_answer.strip())

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
def ignore_whitespace(p_token, j_token, warnings):
    return p_token.isspace() and j_token.isspace()

@LenientChecker.register_ignore('case')
def ignore_case(p_token, j_token, warnings):
    return p_token.lower() == j_token.lower()

@LenientChecker.register_ignore('precision')
def ignore_precision(p_token, j_token, warnings):
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
