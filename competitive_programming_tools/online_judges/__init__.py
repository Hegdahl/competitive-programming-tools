'''
Provides classes containing
logic for submitting solutions
to specific online judges.
'''
from typing import Tuple, Type
from .online_judge import OnlineJudge
from .codeforces import Codeforces
from .kattis import Kattis

ONLINE_JUDGES: Tuple[Type[OnlineJudge], ...] = (Codeforces, Kattis,)
