"""One round of guessing a secret word. Pure logic, used by every local mode."""
import random

from . import words
from .rules import (MAX_ATTEMPTS, hard_mode_violation, is_win, normalize_word,
                    pick_hint, score_guess, CODE)


class Round:
    """max_attempts=None means unlimited guesses (Free Play)."""

    def __init__(self, secret, language, hard=False, max_hints=2,
                 max_attempts=MAX_ATTEMPTS, rng=None):
        self.secret = normalize_word(secret, language)
        self.language = language
        self.length = len(self.secret)
        self.hard = hard
        self.max_hints = max_hints
        self.max_attempts = max_attempts
        self.rng = rng or random.Random()
        self.history = []   # [(guess, feedback)]
        self.hints = {}     # {index: letter}
        self.current = ""
        self.won = False
        self.done = False

    # -- typing
    def type_letter(self, letter):
        if self.done or len(self.current) >= self.length:
            return False
        self.current += letter
        return True

    def backspace(self):
        if self.done or not self.current:
            return False
        self.current = self.current[:-1]
        return True

    @property
    def row(self):
        return len(self.history)

    # -- guessing
    def check(self, guess):
        """Return None if the guess is acceptable, else an error tuple."""
        if len(guess) < self.length:
            return ("not_enough",)
        if not words.is_valid(guess, self.language, self.length):
            return ("not_valid",)
        if any(g == guess for g, _ in self.history):
            return ("already_guessed",)
        if self.hard:
            v = hard_mode_violation(guess, self.history)
            if v and v[0] == "position":
                return ("hard_position", v[1], v[2])
            if v:
                return ("hard_contains", v[1])
        return None

    def submit(self):
        """Returns ("ok", guess, feedback) or ("error", ...reason)."""
        if self.done:
            return ("error", "done")
        guess = normalize_word(self.current, self.language)
        problem = self.check(guess)
        if problem:
            return ("error",) + problem
        feedback = score_guess(self.secret, guess)
        self.history.append((guess, feedback))
        self.current = ""
        if is_win(feedback):
            self.won = self.done = True
        elif self.max_attempts and len(self.history) >= self.max_attempts:
            self.done = True
        return ("ok", guess, feedback)

    # -- hints
    @property
    def hints_left(self):
        return self.max_hints - len(self.hints)

    def use_hint(self):
        """Returns ("ok", index, letter) or ("error", key)."""
        if self.done:
            return ("error", "done")
        if self.hints_left <= 0:
            return ("error", "no_hints")
        pick = pick_hint(self.secret, self.history, self.hints, self.rng)
        if pick is None:
            return ("error", "hint_none_needed")
        self.hints[pick[0]] = pick[1]
        return ("ok",) + pick

    # -- save / restore (daily)
    def replay(self, guesses, hints):
        for i, letter in hints.items():
            self.hints[int(i)] = letter
        for g in guesses:
            self.current = g
            hard, self.hard = self.hard, False   # rules were checked when typed
            self.submit()
            self.hard = hard
        self.current = ""

    def guesses(self):
        return [g for g, _ in self.history]


def share_text(title, number, history, won, max_attempts, hard, hints, language):
    score = str(len(history)) if won else "X"
    limit = max_attempts or "∞"
    head = f"{title} #{number} {score}/{limit}" if number else f"{title} {score}/{limit}"
    if hard:
        head += "*"
    if hints:
        head += " " + "💡" * hints
    emoji = {"G": "🟩", "Y": "🟨", "X": "⬜"}
    rows = []
    for _, fb in history:
        cells = [emoji[CODE[f]] for f in fb]
        if language == "he":
            cells.reverse()   # first letter sits on the right of the board
        rows.append("".join(cells))
    return head + "\n\n" + "\n".join(rows)
