"""Drive the real app with real touch events (dev tool).

    xvfb-run python tools/tap_test.py [en|he]

Unlike tools/screenshots.py, which calls screen methods directly, this taps
widgets the way a finger does, so touch handlers, button animations and
kv bindings all run. Any error the app reports is collected; exit code 1 if
there were any.
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
LANG = sys.argv[1] if len(sys.argv) > 1 else "en"

DATA = tempfile.mkdtemp()
with open(os.path.join(DATA, "settings.json"), "w") as f:
    json.dump({"language": LANG}, f)   # seen_rules stays False: first launch

from kivy.config import Config  # noqa: E402  (before anything opens the window)
Config.set("graphics", "width", "412")
Config.set("graphics", "height", "880")

from wordduel import crash  # noqa: E402

ERRORS = []
crash.share_natively = lambda report: None
crash.show_overlay = lambda title, report: ERRORS.append(report)
crash.install_kivy_handler()

from kivy.clock import Clock  # noqa: E402
from kivy.tests.common import UnitTestTouch  # noqa: E402

from wordduel.core import words  # noqa: E402
from wordduel.core.challenge import encode  # noqa: E402
from wordduel.ui import widgets  # noqa: E402
from wordduel.ui.app import WordDuelApp  # noqa: E402


class TapApp(WordDuelApp):
    @property
    def user_data_dir(self):
        return DATA


app = TapApp()
log = []


def screen():
    return app.sm.current_screen


def find(pred):
    for w in screen().walk(restrict=True):
        if pred(w) and w.get_root_window() is not None and w.opacity > 0 and w.width > 0:
            return w
    seen = [label_of(w) for w in screen().walk(restrict=True) if isinstance(w, widgets.ChunkyButton)]
    raise LookupError(f"no matching widget on {app.sm.current}; buttons: {seen}")


def label_of(w):
    return " ".join(c.rtext for c in w.walk(restrict=True) if isinstance(c, widgets.RtlLabel))


def tap(w, hold=0.08):
    """Press, hold like a real finger (so button animations actually run),
    then release."""
    x, y = w.to_window(*w.center)
    t = UnitTestTouch(x, y)
    t.touch_down()
    Clock.schedule_once(lambda dt: t.touch_up(), hold)


def tap_text(key, **params):
    text = app.tr(key, **params)
    tap(find(lambda w: isinstance(w, widgets.ChunkyButton) and text in label_of(w)))
    log.append(f"tap '{text}'")


def tap_icon(name):
    tap(find(lambda w: isinstance(w, widgets.IconButton) and w.name == name))
    log.append(f"tap icon {name}")


def tap_key(letter):
    kb = find(lambda w: isinstance(w, widgets.Keyboard))
    tap(kb.keys[letter])


def tap_special(icon):
    tap(find(lambda w: isinstance(w, widgets.Key) and any(
        isinstance(c, widgets.Icon) and c.name == icon for c in w.children)))


def typing_wrong(i):
    """Steps typing the i-th valid word that is not the current secret."""
    holder = {}

    def pick():
        secret = screen().round.secret
        tried = {g for g, _ in screen().round.history}
        holder["w"] = [w for w in words.answers(LANG, 5) if w != secret and w not in tried][i * 7]
    yield .1, pick
    for k in range(5):
        yield .15, (lambda k=k: tap_key(holder["w"][k]))


def typing(word):
    """Script steps that tap one key at a time."""
    for ch in word:
        yield .15, (lambda ch=ch: tap_key(ch))


def tap_digit(d):
    pad = find(lambda w: isinstance(w, widgets.Keypad))
    tap(next(k for k in pad.children if label_of(k) == d))


NONSENSE = {"en": "qxzjv", "he": "ץץקקק"}


def check(ok, message):
    assert ok, message


def expect(name):
    assert app.sm.current == name, f"expected {name}, on {app.sm.current}"


def script():
    w5 = words.answers(LANG, 5)
    yield 5.0, lambda: tap_text("got_it") if app.sm.current == "rules" else None
    yield .4, lambda: expect("home")
    yield .2, lambda: tap_text("rules")
    yield .4, lambda: tap_text("got_it")
    yield .4, lambda: expect("home")
    # Language switch by tapping the EN/עב pill
    other = "he" if LANG == "en" else "en"
    yield .3, lambda: tap(find(lambda w: isinstance(w, widgets.ChunkyButton)
                               and label_of(w) == ("עב" if other == "he" else "EN")))
    yield .5, lambda: check(app.lang == other, f"language after tap is {app.lang}")
    yield .3, lambda: tap(find(lambda w: isinstance(w, widgets.ChunkyButton)
                               and label_of(w) == ("עב" if LANG == "he" else "EN")))
    yield .5, lambda: check(app.lang == LANG, f"language after tap back is {app.lang}")
    # Free Play: nonsense word must be rejected
    yield .2, lambda: tap_text("solo")
    yield .5, lambda: expect("game")
    yield from typing(NONSENSE[LANG])
    yield .2, lambda: tap_special("enter")
    yield .8, lambda: check(screen().round.row == 0, f"nonsense guess accepted (row={screen().round.row})")
    yield from [(.15, lambda: tap_special("backspace"))] * 5
    yield from typing(w5[3][:2])
    yield .3, lambda: tap_special("enter")          # too short -> toast + shake
    yield .5, lambda: tap_special("backspace")
    yield .2, lambda: tap_special("backspace")
    yield from typing(w5[7])
    yield .2, lambda: tap_special("enter")
    yield 2.0, lambda: tap(find(lambda w: isinstance(w, widgets.ChunkyButton)
                                and any(isinstance(c, widgets.Icon) and c.name == "bulb"
                                        for c in w.children)))
    # Endless: 8 wrong guesses, still playing, board scrolled
    yield .5, lambda: None
    for i in range(8):
        yield from typing_wrong(i)
        yield .2, lambda: tap_special("enter")
        yield 2.2, lambda: None
    yield .2, lambda: check(screen().round.row >= 8 and not screen().round.done,
                            f"endless free play stopped at row {screen().round.row}")
    yield .1, lambda: check(screen().first == screen().round.row - 5,
                            f"board did not scroll (first={screen().first})")
    yield .5, lambda: tap_icon("back")
    yield .4, lambda: expect("home")
    # Daily: win it
    yield .2, lambda: tap_text("daily")
    yield .5, lambda: None
    yield from typing(screen().round.secret)
    yield .2, lambda: tap_special("enter")
    yield 6.0, lambda: tap_text("share")
    yield .4, lambda: tap_text("menu")
    yield .4, lambda: expect("home")
    # Pass & Play
    yield .2, lambda: tap_text("pass_play")
    yield .4, lambda: None
    yield from typing(w5[11])
    yield .2, lambda: tap_icon("eye")
    yield .2, lambda: tap_text("lock_in")
    yield .4, lambda: expect("pass_phone")
    yield .2, lambda: tap_text("im_ready", name=app.tr("player_2"))
    yield .4, lambda: None
    yield from typing(w5[11])
    yield .2, lambda: tap_special("enter")
    yield 6.0, lambda: tap_text("rematch")
    yield .4, lambda: expect("setter")
    yield .2, lambda: tap_icon("back")
    # Challenge: create, copy, solve
    yield .4, lambda: tap_text("challenge")
    yield .4, lambda: tap_text("challenge_create")
    yield .4, lambda: None
    yield from typing(w5[20])
    yield .2, lambda: tap_text("lock_in")
    yield .4, lambda: expect("challenge_code")
    yield .2, lambda: tap_text("copy_code")
    yield .2, lambda: tap_text("share_code")
    yield .2, lambda: tap_text("done")
    yield .4, lambda: tap_text("challenge")
    yield .4, lambda: tap_text("challenge_solve")
    code = encode(w5[30], LANG)
    for d in code:
        yield .15, (lambda d=d: tap_digit(d))
    yield .2, lambda: tap_text("play")
    yield .5, lambda: expect("game")
    yield .2, lambda: tap_icon("back")
    # Stats and settings
    yield .4, lambda: tap_icon("stats")
    yield .4, lambda: tap_text("solo")
    yield .3, lambda: tap_icon("back")
    yield .3, lambda: tap_icon("gear")
    yield .4, lambda: [tap(t) for t in screen().walk(restrict=True) if isinstance(t, widgets.Toggle)]
    yield .3, lambda: tap_icon("back")
    yield .4, lambda: expect("home")


def run():
    steps = script()

    # Each script entry is (wait this long, then do this).
    def step(_dt=None):
        try:
            delay, fn = next(steps)
        except StopIteration:
            Clock.schedule_once(lambda dt: app.stop(), 1)
            return
        Clock.schedule_once(lambda dt: run_one(fn), delay)

    def run_one(fn):
        try:
            fn()
        except Exception as e:  # a failed step is a test failure, not an app error
            log.append(f"STEP FAILED: {e!r}")
            app.stop()
            return
        step()

    step()
    app.run()
    print("\n".join(log[-12:]))
    failed = [x for x in log if x.startswith("STEP FAILED")]
    print(f"\n{len(log)} actions, {len(ERRORS)} app errors, {len(failed)} failed steps")
    for e in ERRORS[:3]:
        print("APP ERROR:\n" + e[:1500])
    sys.exit(1 if ERRORS or failed else 0)


if __name__ == "__main__":
    run()
