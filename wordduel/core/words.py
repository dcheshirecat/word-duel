"""Word lists: lazy-loaded and cached (the old code re-read a 370k-line file
on every single guess)."""
import datetime
import os
import random

from .rules import DEFAULT_LENGTH, normalize_word

WORDS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "words",
)
DAILY_EPOCH = datetime.date(2026, 1, 1)
DAILY_LENGTH = DEFAULT_LENGTH

_cache = {}


def _load(language, length, kind):
    key = (language, length, kind)
    if key not in _cache:
        path = os.path.join(WORDS_DIR, f"{language}_{length}_{kind}.txt")
        with open(path, encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        _cache[key] = set(words) if kind == "valid" else words
    return _cache[key]


def answers(language, length=DEFAULT_LENGTH):
    return _load(language, length, "answers")


def is_valid(word, language, length=None):
    word = normalize_word(word, language)
    length = length or len(word)
    try:
        return word in _load(language, length, "valid")
    except FileNotFoundError:
        return False


def random_answer(language, length=DEFAULT_LENGTH, rng=random):
    return rng.choice(answers(language, length))


def daily_number(today=None):
    today = today or datetime.date.today()
    return (today - DAILY_EPOCH).days + 1


def daily_answer(language, number):
    """Same word for everyone on the same day. Order is a fixed shuffle so
    consecutive days are not alphabetical neighbours."""
    words = list(answers(language, DAILY_LENGTH))
    random.Random(f"wordduel-daily-{language}-v1").shuffle(words)
    return words[(number - 1) % len(words)]


def seconds_until_tomorrow(now=None):
    now = now or datetime.datetime.now()
    tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1),
                                         datetime.time())
    return int((tomorrow - now).total_seconds())
