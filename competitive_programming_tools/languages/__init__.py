from .cpp import CPP
from .py import PY

LANGUAGES = (CPP, PY)

SUFF_TO_LANG = {
    suffix: language
    for language in LANGUAGES
    for suffix in language.suffixes
}
