from .c import C
from .cpp import CPP
from .py import PY
from .rs import RS

LANGUAGES = (C, CPP, PY, RS)

SUFF_TO_LANG = {
    suffix: language
    for language in LANGUAGES
    for suffix in language.suffixes
}
