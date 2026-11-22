from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from ..core import challenge, words
from ..core.game import Round, share_text
from ..core.rules import (MAX_ATTEMPTS, has_unique_letters, is_word_shaped, letter_states,
                          normalize_word)
from . import theme
from .platform_services import share
from .widgets import Tile, _text_texture


def app():
    return App.get_running_app()


def T(key, **params):
    return app().tr(key, **params)


def error_text(reason):
    kind = reason[0]
    if kind == "hard_position":
        return T("hard_position", n=reason[2] + 1, letter=reason[1].upper())
    if kind == "hard_contains":
        return T("hard_contains", letter=reason[1].upper())
    return T(kind)


def fmt_countdown(seconds):
    h, rem = divmod(max(seconds, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


class BaseScreen(Screen):
    def go_back(self):
        app().back()


# ------------------------------------------------------------------ logo ---

class Logo(Widget):
    """The title spelled in bouncing, colored tiles."""
    lang = StringProperty("en")

    WORDS = {"en": ["WORD", "DUEL"], "he": ["קרב", "מילים"]}
    STATES = ["correct", "present", "absent", "correct", "present"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tiles = []
        self.bind(lang=self.build, pos=self.layout, size=self.layout)
        Clock.schedule_once(self.build)
        Clock.schedule_interval(self.wave, 3.2)

    def build(self, *_):
        self.clear_widgets()
        self.tiles = []
        k = 0
        for word in self.WORDS[self.lang]:
            row = []
            for ch in word:
                t = Tile(letter=ch, state=self.STATES[k % len(self.STATES)])
                k += 1
                row.append(t)
                self.add_widget(t)
            self.tiles.append(row)
        self.layout()
        Clock.schedule_once(self.wave, 0.4)

    def layout(self, *_):
        if not self.tiles:
            return
        longest = max(len(r) for r in self.tiles)
        size = min(self.width / (longest * 1.12), self.height / (len(self.tiles) * 1.15), dp(64))
        gap = size * .12
        total_h = len(self.tiles) * size + (len(self.tiles) - 1) * gap
        rtl = self.lang == "he"
        for r, row in enumerate(self.tiles):
            total_w = len(row) * size + (len(row) - 1) * gap
            x0 = self.x + self.width / 2 - total_w / 2
            y = self.y + self.height / 2 + total_h / 2 - size - r * (size + gap)
            for c, t in enumerate(row):
                vc = len(row) - 1 - c if rtl else c
                t.size = (size, size)
                t.pos = (x0 + vc * (size + gap), y)

    def wave(self, *_):
        k = 0
        for row in self.tiles:
            for t in row:
                t.jump(delay=k * 0.07)
                k += 1


class DistChart(Widget):
    """Horizontal guess-distribution bars (single series, direct-labelled)."""
    dist = ListProperty([0] * MAX_ATTEMPTS)
    highlight = NumericProperty(0)
    last_label = StringProperty(str(MAX_ATTEMPTS))   # "6+" for endless Free Play

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw, dist=self.draw, highlight=self.draw,
                  last_label=self.draw)

    def draw(self, *_):
        self.canvas.clear()
        n = len(self.dist)
        if not n or self.width <= 0:
            return
        rtl = app().lang == "he"
        row_h = self.height / n
        bar_h = row_h * .68
        label_w = dp(24)
        track_w = self.width - label_w - dp(6)
        top = max(max(self.dist), 1)
        with self.canvas:
            for i, count in enumerate(self.dist):
                y = self.y + self.height - (i + 1) * row_h + (row_h - bar_h) / 2
                label = self.last_label if i == n - 1 else str(i + 1)
                num = _text_texture(label, dp(17), theme.INK, theme.FONT_BOLD)
                w = max(track_w * count / top, dp(30))
                if rtl:
                    lx = self.x + self.width - label_w / 2 - num.width / 2
                    bx = self.x + self.width - label_w - dp(6) - w
                else:
                    lx = self.x + label_w / 2 - num.width / 2
                    bx = self.x + label_w + dp(6)
                Color(1, 1, 1, 1)
                _blit(num, lx, y + (bar_h - num.height) / 2)
                Color(rgba=theme.MINT if i + 1 == self.highlight else theme.GRAPE)
                RoundedRectangle(pos=(bx, y), size=(w, bar_h), radius=[dp(8)])
                val = _text_texture(str(count), dp(15), theme.WHITE, theme.FONT_BOLD)
                vx = bx + dp(10) if rtl else bx + w - val.width - dp(10)
                Color(1, 1, 1, 1)
                _blit(val, vx, y + (bar_h - val.height) / 2)


def _blit(tex, x, y):
    Rectangle(texture=tex, pos=(x, y), size=tex.size)


# ------------------------------------------------------------------ home ---

class HomeScreen(BaseScreen):
    daily_sub = StringProperty("")
    solo_sub = StringProperty("")
    streak = NumericProperty(0)

    def on_pre_enter(self, *_):
        self.refresh()
        self._clock = Clock.schedule_interval(lambda dt: self.refresh(), 1)

    def on_leave(self, *_):
        if getattr(self, "_clock", None):
            self._clock.cancel()

    def on_enter(self, *_):
        if not app().settings["seen_rules"]:
            app().settings["seen_rules"] = True
            Clock.schedule_once(lambda dt: app().go("rules"), 0.4)

    def refresh(self):
        a = app()
        number = words.daily_number()
        saved = a.daily_progress.load(a.lang, number)
        if saved and saved.get("done"):
            self.daily_sub = T("daily_done", time=fmt_countdown(words.seconds_until_tomorrow()))
        else:
            self.daily_sub = T("daily_sub", n=number)
        self.streak = a.stats.current_streak("daily", a.lang, number)
        self.solo_sub = T("solo_sub", n=a.settings["word_length"])

    def on_kv_post(self, *_):
        app().bind(lang=lambda *_: self.refresh())

    def play(self, mode):
        a = app()
        if mode in ("daily", "solo"):
            a.go("game").start(mode)
        elif mode == "pass":
            a.pass_state = {"setter": 1, "score": [0, 0]}
            a.go("setter").start("pass")
        elif mode == "challenge":
            a.go("challenge_menu")


# ------------------------------------------------------------------ game ---

class GameScreen(BaseScreen):
    """Daily, Free Play, friend challenges and the guessing half of Pass & Play."""
    title = StringProperty("")
    subtitle = StringProperty("")
    hints_left = NumericProperty(0)
    show_hint = BooleanProperty(True)
    panel_up = BooleanProperty(False)

    # result panel content
    r_title = StringProperty("")
    r_sub = StringProperty("")
    r_extra = StringProperty("")
    r_primary = StringProperty("")
    r_can_share = BooleanProperty(False)
    r_stats = ListProperty([])

    def start(self, mode, secret=None, language=None, code=""):
        a = app()
        self.mode = mode
        self.lang = language or a.lang
        self.code = code
        self.busy = False
        self.number = None
        self.finished = False
        hard = bool(a.settings["hard_mode"])
        saved = None
        if mode == "daily":
            self.number = words.daily_number()
            secret = words.daily_answer(self.lang, self.number)
            saved = a.daily_progress.load(self.lang, self.number)
            if saved:
                hard = saved.get("hard", hard)
            self.title = T("daily")
            self.subtitle = f"#{self.number}"
        elif mode == "solo":
            secret = words.random_answer(self.lang, a.settings["word_length"])
            self.title = T("solo")
            self.subtitle = T("solo_sub", n=len(secret)).split(",")[0]
        elif mode == "challenge":
            self.title = T("challenge_play")
            self.subtitle = code
        else:
            guesser = 3 - a.pass_state["setter"]
            self.title = T("guesser", name=T(f"player_{guesser}"))
            p1, p2 = a.pass_state["score"]
            self.subtitle = f"{T('score')}  {p1} - {p2}"
        if hard:
            self.subtitle += "  ·  " + T("hard_badge")
        # Free Play is endless: unlimited guesses until the word is found.
        self.round = Round(secret, self.lang, hard=hard, max_hints=1 if mode == "daily" else 2,
                           max_attempts=None if mode == "solo" else MAX_ATTEMPTS)
        self.first = 0     # history index shown in the board's top row
        self.ids.board.reset(MAX_ATTEMPTS, self.round.length, self.lang == "he")
        self.ids.keyboard.language = self.lang
        self.ids.keyboard.set_states({})
        self.show_hint = True
        self._hide_panel(instant=True)
        if saved:
            self.round.replay(saved.get("guesses", []), saved.get("hints", {}))
            for r, (g, fb) in enumerate(self.round.history):
                self.ids.board.set_row(self.vrow(r), g, fb)
            self.ids.keyboard.set_states(letter_states(self.round.history))
            if self.round.done:
                Clock.schedule_once(lambda dt: self._finish(record=False), 0.5)
        self._refresh_typed()
        self.hints_left = self.round.hints_left

    # -- input
    def key_letter(self, letter):
        if self.busy or self.panel_up or not is_word_shaped(letter, self.lang):
            return
        if self.round.type_letter(letter):
            app().sfx("tap")
            app().buzz(8)
            self._refresh_typed()

    def key_delete(self):
        if self.busy or self.panel_up:
            return
        if self.round.backspace():
            app().sfx("delete")
            self._refresh_typed()

    def key_enter(self):
        if self.busy or self.panel_up or self.round.done:
            return
        result = self.round.submit()
        if result[0] == "error":
            app().toast(error_text(result[1:]))
            app().sfx("error")
            app().buzz(70)
            self.ids.board.shake_row(self.vrow(self.round.row))
            return
        _, guess, feedback = result
        row = self.round.row - 1
        self.busy = True
        self._save_daily()
        self.ids.board.reveal_row(self.vrow(row), guess, feedback,
                                  on_done=lambda: self._after_reveal(row))

    def _after_reveal(self, row):
        self.ids.keyboard.set_states(letter_states(self.round.history))
        if self.round.won:
            self.ids.board.celebrate_row(self.vrow(row))
            app().sfx("win")
            app().buzz(120)
            app().confetti.burst()
            Clock.schedule_once(lambda dt: self._finish(), 1.1)
        elif self.round.done:
            app().sfx("lose")
            app().buzz(200)
            Clock.schedule_once(lambda dt: self._finish(), 0.6)
        else:
            self.busy = False
            self._refresh_typed()

    # -- the board shows 6 rows; in endless Free Play older guesses scroll off
    def vrow(self, index):
        """Board row for a history index."""
        return index - self.first

    def _scroll_if_full(self):
        rows = self.ids.board.rows
        if self.round.done or self.vrow(self.round.row) < rows:
            return
        self.first = self.round.row - rows + 1
        board = self.ids.board
        for v in range(rows):
            i = self.first + v
            if i < len(self.round.history):
                board.set_row(v, *self.round.history[i])
            else:
                board.show_typed(v, "")

    def _refresh_typed(self):
        if not self.round.done:
            self._scroll_if_full()
            self.ids.board.show_typed(self.vrow(self.round.row), self.round.current,
                                      self.round.hints)

    def use_hint(self):
        if self.busy or self.panel_up:
            return
        res = self.round.use_hint()
        if res[0] == "error":
            app().toast(T(res[1]))
            app().sfx("error")
            return
        _, idx, letter = res
        app().sfx("hint")
        app().toast(T("hint_given", n=idx + 1, letter=letter.upper()), 2.6)
        self.hints_left = self.round.hints_left
        self._save_daily()
        self._refresh_typed()

    def _save_daily(self):
        if self.mode == "daily":
            r = self.round
            app().daily_progress.store(self.lang, self.number, r.guesses(),
                                       {str(k): v for k, v in r.hints.items()},
                                       r.done, r.won, r.hard)

    # -- end of round
    def _finish(self, record=True):
        if self.finished:
            return
        self.finished = True
        a = app()
        r = self.round
        attempts = len(r.history)
        self.r_title = T(f"win_{min(attempts, MAX_ATTEMPTS)}") if r.won else T("lose")
        self.r_sub = T("the_word_was", word=r.secret.upper())
        self.r_extra = ""
        self.r_can_share = self.mode in ("daily", "solo", "challenge")
        self.r_stats = []
        if self.mode in ("daily", "solo"):
            if record:
                s = a.stats.record(self.mode, self.lang, r.won, attempts,
                                   daily_number=self.number)
            else:
                s = a.stats.get(self.mode, self.lang)
            pct = round(100 * s["wins"] / s["played"]) if s["played"] else 0
            self.r_stats = [(str(s["played"]), T("played")), (f"{pct}", T("win_pct")),
                            (str(s["streak"]), T("streak")), (str(s["best"]), T("best"))]
        if self.mode == "daily":
            self.r_primary = T("menu")
            self._tick_countdown()
        elif self.mode == "solo":
            self.r_primary = T("play_again")
        elif self.mode == "challenge":
            self.r_primary = T("send_one_back")
        else:
            if record:
                guesser = 3 - a.pass_state["setter"]
                winner = guesser if r.won else a.pass_state["setter"]
                a.pass_state["score"][winner - 1] += 1
            p1, p2 = a.pass_state["score"]
            self.r_extra = f"{T('player_1')}  {p1} - {p2}  {T('player_2')}"
            self.r_primary = T("rematch")
        self._show_panel()

    def _tick_countdown(self, *_):
        if self.mode == "daily" and self.panel_up:
            self.r_extra = f"{T('next_daily')}  {fmt_countdown(words.seconds_until_tomorrow())}"
            Clock.schedule_once(self._tick_countdown, 1)

    def _show_panel(self):
        self.panel_up = True
        panel = self.ids.panel
        Animation.cancel_all(panel)
        Animation(y=self.y, d=.45, t="out_back").start(panel)

    def _hide_panel(self, instant=False):
        self.panel_up = False
        panel = self.ids.panel
        Animation.cancel_all(panel)
        if instant:
            panel.y = self.y - panel.height - dp(40)
        else:
            Animation(y=self.y - panel.height - dp(40), d=.25).start(panel)

    def primary_action(self):
        a = app()
        if self.mode == "daily":
            a.back()
        elif self.mode == "solo":
            self.start("solo")
        elif self.mode == "challenge":
            a.go("setter").start("challenge")
        else:
            a.pass_state["setter"] = 3 - a.pass_state["setter"]
            a.go("setter").start("pass")

    def do_share(self):
        r = self.round
        title = {"daily": T("daily"), "solo": T("solo")}.get(self.mode, T("challenge_play"))
        text = share_text(f"{T('share_title')} · {title}", self.number, r.history, r.won,
                          r.max_attempts, r.hard, len(r.hints), self.lang)
        if self.mode == "challenge":
            text = T("challenge_result_intro", code=self.code) + "\n" + text
        if not share(text, T("share")):
            app().toast(T("copied"))


# ---------------------------------------------------------- secret setter ---

class SetterScreen(BaseScreen):
    """Pick a secret word, for Pass & Play or for a friend challenge."""
    title = StringProperty("")
    peek = BooleanProperty(False)
    length = NumericProperty(5)

    def start(self, mode):
        a = app()
        self.mode = mode           # pass | challenge
        self.lang = a.lang
        self.length = a.settings["word_length"]
        self.word = ""
        self.peek = False
        if mode == "pass":
            self.title = T(f"player_{a.pass_state['setter']}")
        else:
            self.title = T("challenge_create")
        self.ids.board.reset(1, self.length, self.lang == "he")
        self.ids.keyboard.language = self.lang
        self.ids.keyboard.set_states({})
        self._show()

    def _show(self):
        shown = self.word if self.peek else "•" * len(self.word)
        self.ids.board.show_typed(0, shown)

    def toggle_peek(self):
        self.peek = not self.peek
        self._show()

    def key_letter(self, letter):
        if not is_word_shaped(letter, self.lang) or len(self.word) >= self.length:
            return
        self.word += letter
        app().sfx("tap")
        app().buzz(8)
        self._show()

    def key_delete(self):
        if self.word:
            self.word = self.word[:-1]
            app().sfx("delete")
            self._show()

    def key_enter(self):
        self.lock_in()

    def _reject(self, key):
        app().toast(T(key))
        app().sfx("error")
        app().buzz(70)
        self.ids.board.shake_row(0)

    def lock_in(self):
        word = normalize_word(self.word, self.lang)
        if len(word) < self.length:
            return self._reject("not_enough")
        if not has_unique_letters(word):
            return self._reject("repeat_letters")
        if not words.is_valid(word, self.lang, self.length):
            return self._reject("not_valid")
        app().sfx("pop")
        if self.mode == "pass":
            app().go("pass_phone").start(word)
        else:
            app().go("challenge_code").start(challenge.encode(word, self.lang))

    def go_back(self):
        app().back("challenge_menu" if self.mode == "challenge" else "home")


class PassPhoneScreen(BaseScreen):
    who = StringProperty("")

    def start(self, secret):
        self.secret = secret
        self.who = T(f"player_{3 - app().pass_state['setter']}")

    def ready(self):
        app().go("game").start("pass", secret=self.secret)


# ------------------------------------------------------------- challenges ---

class ChallengeMenuScreen(BaseScreen):
    def create(self):
        app().go("setter").start("challenge")

    def solve(self):
        app().go("solve").start()


class ChallengeCodeScreen(BaseScreen):
    """Shows the code for a challenge the player just made."""
    code = StringProperty("")
    pretty = StringProperty("")

    def start(self, code):
        self.code = code
        self.pretty = challenge.format_code(code)

    def share_code(self):
        if not share(T("challenge_message", code=self.pretty), T("share")):
            app().toast(T("copied"))

    def copy_code(self):
        Clipboard.copy(self.pretty)
        app().toast(T("copied"))

    def go_back(self):
        app().back("challenge_menu")


class SolveScreen(BaseScreen):
    """Type or paste a friend's code, then play their word."""
    code = StringProperty("")

    def start(self):
        self.code = ""

    def go_back(self):
        app().back("challenge_menu")

    def key_letter(self, ch):
        if ch.isdigit() and len(self.code) < challenge.CODE_LEN:
            self.code += ch
            app().sfx("tap")

    def key_delete(self):
        if self.code:
            self.code = self.code[:-1]
            app().sfx("delete")

    def key_enter(self):
        self.play()

    def paste(self):
        found = challenge.find_code(Clipboard.paste() or "")
        if found:
            self.code = found
            app().sfx("pop")
        else:
            app().toast(T("no_code_in_clipboard"))
            app().sfx("error")

    def play(self):
        try:
            lang, word = challenge.decode(self.code)
            if not words.is_valid(word, lang, len(word)):
                raise challenge.ChallengeError("code_invalid")
        except challenge.ChallengeError as e:
            app().toast(T(e.key), 2.5)
            app().sfx("error")
            app().buzz(70)
            return
        app().sfx("pop")
        app().go("game").start("challenge", secret=word, language=lang,
                               code=challenge.format_code(self.code))


# ------------------------------------------------------ stats / settings ---

class StatsScreen(BaseScreen):
    mode = StringProperty("daily")
    played = StringProperty("0")
    pct = StringProperty("0")
    streak = StringProperty("0")
    best = StringProperty("0")
    dist = ListProperty([0] * MAX_ATTEMPTS)
    last = NumericProperty(0)
    last_label = StringProperty(str(MAX_ATTEMPTS))
    empty = BooleanProperty(True)

    def on_pre_enter(self, *_):
        self.refresh()

    def on_mode(self, *_):
        self.refresh()

    def refresh(self):
        a = app()
        s = a.stats.get(self.mode, a.lang)
        self.played = str(s["played"])
        self.pct = str(round(100 * s["wins"] / s["played"]) if s["played"] else 0)
        today = words.daily_number() if self.mode == "daily" else None
        self.streak = str(a.stats.current_streak(self.mode, a.lang, today))
        self.best = str(s["best"])
        self.dist = list(s["dist"])
        self.last = min(s.get("last") or 0, MAX_ATTEMPTS)
        self.last_label = "6+" if self.mode == "solo" else str(MAX_ATTEMPTS)
        self.empty = s["played"] == 0


class SettingsScreen(BaseScreen):
    pass


class RulesScreen(BaseScreen):
    """No scrolling (see layout.kv), so shrink the text until the card fits."""
    fit = NumericProperty(1.0)

    def on_kv_post(self, *_):
        self._trigger_fit = Clock.create_trigger(self._fit, 0.05)
        self.ids.card.bind(height=self._trigger_fit)
        self.ids.area.bind(height=self._trigger_fit)
        app().bind(lang=lambda *_: self._refit())

    def on_pre_enter(self, *_):
        self._refit()

    def _refit(self):
        self.fit = 1.0
        self._trigger_fit()

    def _fit(self, *_):
        area, card = self.ids.area, self.ids.card
        if area.height > 10 and card.height > area.height and self.fit > 0.6:
            self.fit = max(0.6, self.fit * 0.94)


SCREENS = {
    "home": HomeScreen,
    "game": GameScreen,
    "setter": SetterScreen,
    "pass_phone": PassPhoneScreen,
    "challenge_menu": ChallengeMenuScreen,
    "challenge_code": ChallengeCodeScreen,
    "solve": SolveScreen,
    "stats": StatsScreen,
    "settings": SettingsScreen,
    "rules": RulesScreen,
}
