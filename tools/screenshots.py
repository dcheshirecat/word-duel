"""Drive the app through its screens and save screenshots (dev tool).

    xvfb-run -s "-screen 0 412x880x24" python tools/screenshots.py OUT_DIR [en|he]

Uses a throwaway data dir so your real stats/settings are untouched.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "shots")
LANG = sys.argv[2] if len(sys.argv) > 2 else "en"
os.makedirs(OUT, exist_ok=True)

from kivy.config import Config  # noqa: E402
Config.set("graphics", "width", "412")
Config.set("graphics", "height", "880")

from kivy.clock import Clock  # noqa: E402
from kivy.core.window import Window  # noqa: E402

from wordduel.core import words  # noqa: E402
from wordduel.ui.app import WordDuelApp  # noqa: E402

DATA = tempfile.mkdtemp()
with open(os.path.join(DATA, "settings.json"), "w") as f:
    f.write('{"seen_rules": true, "language": "%s"}' % LANG)


class ShotApp(WordDuelApp):
    @property
    def user_data_dir(self):
        return DATA

    def build(self):
        root = super().build()
        self.settings["seen_rules"] = True
        self.set_language(LANG)
        return root


def run():
    app = ShotApp()
    steps = []

    def at(delay, fn):
        steps.append((delay, fn))

    def shot(name):
        def f():
            app.root.export_to_png(os.path.join(OUT, f"{LANG}_{name}.png"))
        return f

    def type_word(screen, word):
        for ch in word:
            screen.key_letter(ch)

    def setup():
        app.settings["seen_rules"] = True
        app.set_language(LANG)
        app.go("home")

    def daily_play():
        g = app.go("game")
        g.start("daily")
        secret = g.round.secret
        others = [w for w in words.answers(LANG, 5) if not set(w) & set(secret)][:1]
        near = [w for w in words.answers(LANG, 5) if w[0] == secret[0] and w != secret][:1]
        for w in others + near:
            type_word(g, w)
            g.key_enter()
            g.busy = False
        g._after_reveal(g.round.row - 1)

    def daily_win():
        g = app.sm.get_screen("game")
        g.use_hint()
        type_word(g, g.round.secret)
        g.key_enter()

    def typing():
        g = app.sm.get_screen("game")
        g.start("solo")
        type_word(g, g.round.secret[:3])

    def setter():
        s = app.go("setter")
        s.start("pass")
        type_word(s, words.answers(LANG, s.length)[10])

    def online_code():
        s = app.sm.get_screen("setter")
        s.start("online", code="482913", role="p2")
        s.online_mode = True
        s.code_status = app.tr("friend_joined")

    if len(sys.argv) > 3 and sys.argv[3] == "online":
        return online_scenario(app, at, shot, type_word, steps)

    at(0.5, setup)
    at(2.0, shot("home"))
    at(0.2, lambda: app.go("rules"))
    at(1.0, shot("rules"))
    at(0.2, daily_play)
    at(3.0, shot("game_progress"))
    at(0.2, daily_win)
    at(4.0, shot("game_won"))
    at(0.2, typing)
    at(1.0, shot("game_typing"))
    at(0.2, setter)
    at(1.0, shot("setter"))
    at(0.2, online_code)
    at(1.0, shot("online_setter"))
    at(0.2, lambda: app.go("pass_phone").start("xxxxx"))
    at(1.0, shot("pass_phone"))
    at(0.2, lambda: app.go("online_menu"))
    at(1.0, shot("online_menu"))
    at(0.2, lambda: (app.go("join").start(), [app.sm.get_screen("join").key_letter(c) for c in "4829"]))
    at(1.0, shot("join"))
    at(0.2, lambda: app.go("stats"))
    at(1.0, shot("stats"))
    at(0.2, lambda: app.go("settings"))
    at(1.0, shot("settings"))
    at(0.5, app.stop)

    t = 0
    for delay, fn in steps:
        t += delay
        Clock.schedule_once(lambda dt, f=fn: f(), t)
    app.run()


def online_scenario(app, at, shot, type_word, steps):
    """Full online duel against a bot, over an in-memory fake Firestore."""
    import threading
    import time

    from tests.fakes import FakeFirestore
    from wordduel.core import online

    fake = FakeFirestore()
    online.FirestoreTransport = lambda: fake
    online.POLL_SECONDS = 0.3
    me_word = words.answers(LANG, 5)[40]
    bot_word = words.answers(LANG, 5)[90]
    miss = next(w for w in words.answers(LANG, 5) if not set(w) & set(bot_word))
    bot_guesses = [w for w in words.answers(LANG, 5) if w != me_word][200:206]

    def bot():
        c = online.OnlineClient(fake)
        while not fake.docs:
            time.sleep(0.2)
        code = next(iter(fake.docs))
        c.join_game(code)
        time.sleep(1.0)
        c.commit_word(code, "p2", online.make_commitment(bot_word)[1])
        i = 0
        while True:
            time.sleep(0.4)
            snap = c.fetch(code)
            if snap["status"] == "finished":
                c.reveal(code, "p2", *_salted(snap, bot_word))
                return
            c.score_pending(code, "p2", bot_word)
            snap = c.fetch(code)
            if snap["turn"] == "p2" and len(snap["guesses_p2"]) == len(snap["feedback_p2"]):
                c.submit_guess(code, "p2", bot_guesses[i])
                i += 1

    commits = {}

    def _salted(snap, word):
        return commits["salt"], word

    real_commit = online.make_commitment

    def tracking_commit(word):
        salt, commit = real_commit(word)
        if word == bot_word:
            commits["salt"] = salt
        return salt, commit
    online.make_commitment = tracking_commit

    def start():
        app.settings["seen_rules"] = True
        app.go("online_menu")
        app.sm.get_screen("online_menu").create()
        threading.Thread(target=bot, daemon=True).start()

    def lock():
        s = app.sm.get_screen("setter")
        type_word(s, me_word)
        s.lock_in()

    def guess(w):
        def f():
            g = app.sm.get_screen("online_game")
            type_word(g, w)
            g.key_enter()
        return f

    at(0.5, start)
    at(1.5, shot("online_waiting"))
    at(1.5, shot("online_joined"))
    at(0.2, lock)
    at(2.0, guess(miss))
    at(4.0, shot("online_midgame"))
    at(0.1, guess(bot_word))
    at(6.0, shot("online_result"))
    at(0.5, app.stop)
    t = 0
    for delay, fn in steps:
        t += delay
        Clock.schedule_once(lambda dt, f=fn: f(), t)
    app.run()


if __name__ == "__main__":
    run()
