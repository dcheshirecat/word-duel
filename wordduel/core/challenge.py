"""Friend challenges: a secret word packed into a 10-digit code.

No server involved. The word is encoded in the code itself, so a friend can
type or paste it and play whenever they like, fully offline.

Layout: 9 scrambled digits + 1 check digit.
  value = language_bit + 2 * (word as base-28 number, letters 1..27)
  6 letters max: 28**6 * 2 < 10**9, so it always fits in 9 digits.
The scramble is a fixed affine permutation of 0..10**9-1. It only stops the
word from being *readable* in the code; it is not encryption.
The check digit catches a mistyped or swapped digit.
"""
import re

from .rules import LENGTHS, has_unique_letters, normalize_word

ALPHABETS = {
    "en": "abcdefghijklmnopqrstuvwxyz",
    "he": "אבגדהוזחטיכךלמםנןסעפףצץקרשת",
}
LANG_BITS = {"en": 0, "he": 1}
BASE = 28
MOD = 10 ** 9
_A = 387_420_489          # 3**18: odd and not a multiple of 5, so invertible mod 10**9
_B = 271_828_182
_A_INV = pow(_A, -1, MOD)
CODE_LEN = 10


class ChallengeError(Exception):
    """.key is an i18n key."""

    def __init__(self, key):
        super().__init__(key)
        self.key = key


def _check_digit(digits):
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(digits))
    return str((10 - total % 10) % 10)


def encode(word, language):
    word = normalize_word(word, language)
    alphabet = ALPHABETS[language]
    if len(word) not in LENGTHS or any(c not in alphabet for c in word):
        raise ChallengeError("not_valid")
    number = 0
    for c in reversed(word):
        number = number * BASE + alphabet.index(c) + 1
    value = LANG_BITS[language] + 2 * number
    body = f"{(_A * value + _B) % MOD:09d}"
    return body + _check_digit(body)


def decode(code):
    """Return (language, word). Raises ChallengeError."""
    digits = re.sub(r"\D", "", code or "")
    if len(digits) != CODE_LEN or _check_digit(digits[:9]) != digits[9]:
        raise ChallengeError("code_invalid")
    value = (_A_INV * (int(digits[:9]) - _B)) % MOD
    language = "he" if value % 2 else "en"
    number = value // 2
    alphabet = ALPHABETS[language]
    letters = []
    while number:
        number, rem = divmod(number, BASE)
        if rem == 0 or rem > len(alphabet):
            raise ChallengeError("code_invalid")
        letters.append(alphabet[rem - 1])
    word = "".join(letters)
    if len(word) not in LENGTHS or not has_unique_letters(word):
        raise ChallengeError("code_invalid")
    return language, word


def format_code(code):
    """'1234567890' -> '123 456 7890' (easier to read aloud and type)."""
    return f"{code[:3]} {code[3:6]} {code[6:]}" if len(code) == CODE_LEN else code


def find_code(text):
    """Pull a challenge code out of pasted text (e.g. a whole chat message)."""
    for m in re.finditer(r"\d[\d \-]{8,20}\d", text or ""):
        digits = re.sub(r"\D", "", m.group())
        if len(digits) == CODE_LEN:
            return digits
    return None
