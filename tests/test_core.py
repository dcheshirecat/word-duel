import datetime
import random

import pytest

from wordduel.core import bidi, challenge, words
from wordduel.core.rules import (ABSENT, CORRECT, PRESENT, hard_mode_violation, letter_states,
                                 normalize_word, pick_hint, score_guess)
from wordduel.core.storage import DailyProgress, Settings, Stats


# ------------------------------------------------------------------ rules ---

def test_score_basic():
    assert score_guess("crane", "crane") == [CORRECT] * 5
    assert score_guess("crane", "nacre") == [PRESENT, PRESENT, PRESENT, PRESENT, CORRECT]


def test_score_repeated_letters():
    # Only one E in the secret: second E is absent, not present.
    assert score_guess("water", "eerie") == [PRESENT, ABSENT, PRESENT, ABSENT, ABSENT]
    # Exact match takes priority over an earlier misplaced copy.
    assert score_guess("abbey", "babes") == [PRESENT, PRESENT, CORRECT, CORRECT, ABSENT]


def test_letter_states_keep_best():
    history = [("crane", score_guess("trace", "crane")), ("trace", [CORRECT] * 5)]
    assert letter_states(history)["c"] == CORRECT


def test_hard_mode():
    history = [("crane", score_guess("crisp", "crane"))]  # c,r green
    assert hard_mode_violation("crisp", history) is None
    assert hard_mode_violation("toast", history) == ("position", "c", 0)
    history = [("north", score_guess("crisp", "north"))]  # r yellow
    assert hard_mode_violation("stick", history) == ("contains", "r")


def test_hint_never_repeats_known():
    history = [("crane", score_guess("crisp", "crane"))]
    rng = random.Random(0)
    hints = {}
    for _ in range(3):
        i, letter = pick_hint("crisp", history, hints, rng)
        assert i not in (0, 1) and i not in hints and "crisp"[i] == letter
        hints[i] = letter
    assert pick_hint("crisp", history, hints, rng) is None


def test_hebrew_final_letters():
    assert normalize_word("שלומ", "he") == "שלום"
    assert normalize_word("םלש", "he") == "מלש"
    assert normalize_word("CRANE", "en") == "crane"


# ------------------------------------------------------------------ words ---

@pytest.mark.parametrize("lang", ["en", "he"])
@pytest.mark.parametrize("n", [4, 5, 6])
def test_answers_are_valid_and_unique(lang, n):
    ans = words.answers(lang, n)
    assert len(ans) > 1000
    for w in ans[:200]:
        assert len(w) == n and len(set(w)) == n and words.is_valid(w, lang)


def test_daily_is_stable_and_varies():
    a = words.daily_answer("en", 100)
    assert a == words.daily_answer("en", 100)
    assert len({words.daily_answer("en", i) for i in range(1, 31)}) == 30
    assert words.daily_number(datetime.date(2026, 1, 1)) == 1


def test_repeated_letter_guesses_allowed():
    assert words.is_valid("hello", "en")
    assert not words.is_valid("zzqxv", "en")


# ------------------------------------------------------------------- bidi ---

def test_bidi():
    assert bidi.visual("abc") == "abc"
    assert bidi.visual("שחקן 1") == "1 ןקחש"
    assert bidi.visual("חידה #42") == "42# הדיח"
    assert bidi.visual("קוד (AB12)") == "(AB12) דוק"


# ---------------------------------------------------------------- storage ---

def test_stats_and_streaks(tmp_path):
    s = Stats(str(tmp_path))
    s.record("daily", "en", True, 3, daily_number=10)
    s.record("daily", "en", True, 4, daily_number=11)
    assert s.get("daily", "en")["streak"] == 2
    s.record("daily", "en", True, 2, daily_number=13)  # skipped a day
    st = Stats(str(tmp_path)).get("daily", "en")      # reloaded from disk
    assert st["streak"] == 1 and st["best"] == 2 and st["dist"][:4] == [0, 1, 1, 1]
    assert s.current_streak("daily", "en", today_number=20) == 0


def test_settings_and_progress(tmp_path):
    st = Settings(str(tmp_path))
    st["hard_mode"] = True
    assert Settings(str(tmp_path))["hard_mode"] is True
    p = DailyProgress(str(tmp_path))
    p.store("en", 5, ["crane"], {"2": "a"}, False, False, True)
    assert DailyProgress(str(tmp_path)).load("en", 5)["guesses"] == ["crane"]
    assert p.load("en", 6) is None


# -------------------------------------------------------------- challenge ---

def test_challenge_roundtrip_all_words():
    for lang in ("en", "he"):
        for n in (4, 5, 6):
            for w in words.answers(lang, n)[::50]:
                code = challenge.encode(w, lang)
                assert len(code) == 10 and code.isdigit()
                assert challenge.decode(code) == (lang, w)


def test_challenge_hides_word_and_varies():
    a, b = challenge.encode("crane", "en"), challenge.encode("crank", "en")
    assert a[:6] != b[:6]          # similar words don't give similar codes


def test_challenge_catches_typos():
    code = challenge.encode("crane", "en")
    for i in range(10):
        wrong = code[:i] + str((int(code[i]) + 1) % 10) + code[i + 1:]
        with pytest.raises(challenge.ChallengeError):
            challenge.decode(wrong)
    with pytest.raises(challenge.ChallengeError):
        challenge.decode("123")


def test_challenge_hebrew_final_letters_and_paste():
    code = challenge.encode("שלומ", "he")
    assert challenge.decode(code) == ("he", "שלום")
    msg = f"Can you guess my word? Code: {challenge.format_code(code)} good luck"
    assert challenge.find_code(msg) == code


# ------------------------------------------------------------------ round ---

from wordduel.core.game import Round, share_text  # noqa: E402


def test_round_flow_and_errors():
    r = Round("crisp", "en", hard=True)
    for ch in "cra":
        r.type_letter(ch)
    assert r.submit() == ("error", "not_enough")
    for ch in "ne":
        r.type_letter(ch)
    assert r.submit()[0] == "ok"
    for ch in "toast":
        r.type_letter(ch)
    assert r.submit() == ("error", "hard_position", "c", 0)
    r.current = "crane"
    assert r.submit() == ("error", "already_guessed")
    r.current = "zzzzz"
    assert r.submit() == ("error", "not_valid")
    r.current = "crisp"
    assert r.submit()[0] == "ok" and r.won and r.done


def test_round_loses_after_six_and_hints_are_limited():
    r = Round("crisp", "en", max_hints=1)
    assert r.use_hint()[0] == "ok"
    assert r.use_hint() == ("error", "no_hints")
    for w in ["about", "other", "which", "their", "there", "would"]:
        r.current = w
        assert r.submit()[0] == "ok"
    assert r.done and not r.won


def test_round_replay_and_share():
    r = Round("crisp", "en", hard=True)
    r.replay(["crane", "crisp"], {"4": "p"})
    assert r.won and r.hints == {4: "p"}
    text = share_text("Word Duel", 7, r.history, r.won, 6, True, 1, "en")
    assert text.startswith("Word Duel #7 2/6* 💡") and text.endswith("🟩🟩🟩🟩🟩")
