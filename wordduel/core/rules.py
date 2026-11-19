"""Pure game rules: scoring, hard mode, hints. No Kivy imports."""
import random

MAX_ATTEMPTS = 6
DEFAULT_LENGTH = 5
LENGTHS = (4, 5, 6)
LANGUAGES = ("en", "he")

CORRECT = "correct"   # right letter, right spot
PRESENT = "present"   # right letter, wrong spot
ABSENT = "absent"     # not in the word
_RANK = {None: 0, ABSENT: 1, PRESENT: 2, CORRECT: 3}

# Compact one-letter codes, used for online play and share text.
CODE = {CORRECT: "G", PRESENT: "Y", ABSENT: "X"}
DECODE = {v: k for k, v in CODE.items()}

HE_LETTERS = set("אבגדהוזחטיכךלמםנןסעפףצץקרשת")
HE_FINALS = {"כ": "ך", "מ": "ם", "נ": "ן", "פ": "ף", "צ": "ץ"}
HE_UNFINALS = {v: k for k, v in HE_FINALS.items()}


def normalize_word(word, language):
    """Lowercase English; for Hebrew use final letter forms only at the end.

    Players can type מ at the end of a word and it counts as ם (and vice
    versa mid-word), which matches how Hebrew is actually written.
    """
    word = word.strip()
    if language != "he":
        return word.lower()
    chars = [HE_UNFINALS.get(c, c) for c in word]
    if chars:
        chars[-1] = HE_FINALS.get(chars[-1], chars[-1])
    return "".join(chars)


def is_word_shaped(word, language):
    if language == "he":
        return bool(word) and all(c in HE_LETTERS for c in word)
    return word.isascii() and word.isalpha()


def has_unique_letters(word):
    return len(set(word)) == len(word)


def score_guess(secret, guess):
    """Return a list of CORRECT / PRESENT / ABSENT, one per letter of guess.

    Repeated letters are handled the standard way: a letter is only marked
    PRESENT as many times as it still appears unmatched in the secret.
    """
    n = len(secret)
    if len(guess) != n:
        raise ValueError("guess and secret must be the same length")
    result = [ABSENT] * n
    remaining = {}
    for i in range(n):
        if guess[i] == secret[i]:
            result[i] = CORRECT
        else:
            remaining[secret[i]] = remaining.get(secret[i], 0) + 1
    for i in range(n):
        if result[i] != CORRECT and remaining.get(guess[i], 0) > 0:
            result[i] = PRESENT
            remaining[guess[i]] -= 1
    return result


def is_win(feedback):
    return bool(feedback) and all(f == CORRECT for f in feedback)


def encode_feedback(feedback):
    return "".join(CODE[f] for f in feedback)


def decode_feedback(text):
    return [DECODE[c] for c in text]


def letter_states(history):
    """Best-known state for every letter guessed so far: {letter: state}."""
    states = {}
    for guess, feedback in history:
        for letter, state in zip(guess, feedback):
            if _RANK[state] > _RANK[states.get(letter)]:
                states[letter] = state
    return states


def hard_mode_violation(guess, history):
    """Return None if guess respects all revealed clues, else a reason.

    Reasons are tuples so the UI can translate them:
      ("position", letter, index)  a green letter must stay in place
      ("contains", letter)         a yellow/green letter must be reused
    """
    for prev, feedback in history:
        for i, (letter, state) in enumerate(zip(prev, feedback)):
            if state == CORRECT and guess[i] != letter:
                return ("position", letter, i)
        needed = {}
        for letter, state in zip(prev, feedback):
            if state in (CORRECT, PRESENT):
                needed[letter] = needed.get(letter, 0) + 1
        for letter, count in needed.items():
            if guess.count(letter) < count:
                return ("contains", letter)
    return None


def known_positions(history):
    known = {}
    for guess, feedback in history:
        for i, (letter, state) in enumerate(zip(guess, feedback)):
            if state == CORRECT:
                known[i] = letter
    return known


def pick_hint(secret, history, hints, rng=random):
    """Pick a position the player has not solved yet. Returns (index, letter).

    `hints` is {index: letter} of hints already given. Returns None when every
    position is already known.
    """
    known = known_positions(history)
    known.update(hints)
    open_positions = [i for i in range(len(secret)) if i not in known]
    if not open_positions:
        return None
    i = rng.choice(open_positions)
    return i, secret[i]
