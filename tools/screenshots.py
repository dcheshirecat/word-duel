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

    def challenge_flow():
        s = app.go("setter")
        s.start("challenge")
        type_word(s, words.answers(LANG, s.length)[25])
        s.lock_in()

    def solve():
        from wordduel.core.challenge import encode
        code = encode(words.answers(LANG, 5)[60], LANG)
        sv = app.go("solve")
        sv.start()
        for c in code:
            sv.key_letter(c)

    def solve_play():
        sv = app.sm.get_screen("solve")
        sv.play()
        g = app.sm.get_screen("game")
        type_word(g, g.round.secret)
        g.key_enter()

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
    at(0.2, challenge_flow)
    at(1.0, shot("challenge_code"))
    at(0.2, lambda: app.go("pass_phone").start("xxxxx"))
    at(1.0, shot("pass_phone"))
    at(0.2, lambda: app.go("challenge_menu"))
    at(1.0, shot("challenge_menu"))
    at(0.2, solve)
    at(1.0, shot("solve"))
    at(0.2, solve_play)
    at(4.0, shot("challenge_won"))
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


if __name__ == "__main__":
    run()
