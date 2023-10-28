'''
Provides :py:class:`LenientChecker`
'''
import re

ACCEPTABLE_PRECISION_ERROR = 1e-3



class LenientChecker:
    '''
    Class for checkign whether two
    output files approximately match.
    '''
    IGNORE_PROPERTY = {}
    CHECK_FLOAT_FORMAT = None
    WHITESPACE_CHUNK = None

    @classmethod
    def register_ignore(cls, name):
        '''
        Add a function to the set of functions
        to compare tokens ignoring some property.
        '''
        def dec(func):
            cls.IGNORE_PROPERTY[name] = func
            return func
        return dec

    def __init__(self, participant_answer, judge_answer):
        import re
        if LenientChecker.CHECK_FLOAT_FORMAT is None:
            LenientChecker.CHECK_FLOAT_FORMAT = re.compile(r'^\d+\.\d+$')
            LenientChecker.WHITESPACE_CHUNK = re.compile(r'(\s+)')

        self.accept = False
        self.ignored_properties = set()
        self.warnings = dict()

        p_tokens = LenientChecker.WHITESPACE_CHUNK.split(participant_answer)
        j_tokens = LenientChecker.WHITESPACE_CHUNK.split(judge_answer)

        if len(p_tokens) != len(j_tokens):
            self.ignored_properties.add('whitespace')
            p_tokens = LenientChecker.WHITESPACE_CHUNK.split(participant_answer.strip())
            j_tokens = LenientChecker.WHITESPACE_CHUNK.split(judge_answer.strip())

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
def ignore_whitespace(p_token, j_token, _):
    '''
    Report tokens as equal if they are both whitespace.
    '''
    return p_token.isspace() and j_token.isspace()


@LenientChecker.register_ignore('case')
def ignore_case(p_token, j_token, _):
    '''
    Report tokens as equal if they are the
    same after ignoring letter case.
    '''
    return p_token.lower() == j_token.lower()


@LenientChecker.register_ignore('precision')
def ignore_precision(p_token, j_token, warnings):
    '''
    Report tokens as equal if both look like floating point numbers,
    and their absolute or relative error is less than
    :py:const:`ACCEPTABLE_PRECISION_ERROR`
    '''
    if LenientChecker.CHECK_FLOAT_FORMAT.match(p_token) is None:
        return False

    p_val = float(p_token)
    j_val = float(j_token)

    error = abs(p_val-j_val) / max(1, j_val)
    if error > ACCEPTABLE_PRECISION_ERROR:
        return False

    if 'error' not in warnings or error > warnings['precision error']:
        warnings['precision error'] = error

    return True
