import threading

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from ..core import online, words
from ..core.game import Round, share_text
from ..core.rules import (MAX_ATTEMPTS, decode_feedback, has_unique_letters, is_word_shaped,
                          letter_states, normalize_word)
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw, dist=self.draw, highlight=self.draw)

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
                num = _text_texture(str(i + 1), dp(17), theme.INK, theme.FONT_BOLD)
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
        elif mode == "online":
            a.go("online_menu")


# ------------------------------------------------------------------ game ---

class GameScreen(BaseScreen):
    """Daily, Free Play and the guessing half of Pass & Play."""
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

    def start(self, mode, secret=None):
        a = app()
        self.mode = mode
        self.lang = a.lang
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
        else:
            guesser = 3 - a.pass_state["setter"]
            self.title = T("guesser", name=T(f"player_{guesser}"))
            p1, p2 = a.pass_state["score"]
            self.subtitle = f"{T('score')}  {p1} - {p2}"
        if hard:
            self.subtitle += "  ·  " + T("hard_badge")
        self.round = Round(secret, self.lang, hard=hard, max_hints=1 if mode == "daily" else 2)
        self.ids.board.reset(MAX_ATTEMPTS, self.round.length, self.lang == "he")
        self.ids.keyboard.language = self.lang
        self.ids.keyboard.set_states({})
        self.show_hint = True
        self._hide_panel(instant=True)
        if saved:
            self.round.replay(saved.get("guesses", []), saved.get("hints", {}))
            for r, (g, fb) in enumerate(self.round.history):
                self.ids.board.set_row(r, g, fb)
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
            self.ids.board.shake_row(self.round.row)
            return
        _, guess, feedback = result
        row = self.round.row - 1
        self.busy = True
        self._save_daily()
        self.ids.board.reveal_row(row, guess, feedback, on_done=lambda: self._after_reveal(row))

    def _after_reveal(self, row):
        self.ids.keyboard.set_states(letter_states(self.round.history))
        if self.round.won:
            self.ids.board.celebrate_row(row)
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

    def _refresh_typed(self):
        if not self.round.done:
            self.ids.board.show_typed(self.round.row, self.round.current, self.round.hints)

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
        self.r_title = T(f"win_{attempts}") if r.won else T("lose")
        self.r_sub = T("the_word_was", word=r.secret.upper())
        self.r_extra = ""
        self.r_can_share = self.mode in ("daily", "solo")
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
        else:
            a.pass_state["setter"] = 3 - a.pass_state["setter"]
            a.go("setter").start("pass")

    def do_share(self):
        r = self.round
        title = T("daily") if self.mode == "daily" else T("solo")
        text = share_text(f"{T('share_title')} · {title}", self.number, r.history, r.won,
                          r.max_attempts, r.hard, len(r.hints), self.lang)
        if not share(text, T("share")):
            app().toast(T("copied"))


# ---------------------------------------------------------- secret setter ---

class SetterScreen(BaseScreen):
    """Pick a secret word: Pass & Play and both sides of an Online Duel."""
    title = StringProperty("")
    code = StringProperty("")
    code_status = StringProperty("")
    peek = BooleanProperty(False)
    online_mode = BooleanProperty(False)
    working = BooleanProperty(False)
    length = NumericProperty(5)

    def start(self, mode, language=None, length=None, code="", role="p1"):
        a = app()
        self.mode = mode           # pass | online
        self.role = role
        self.lang = language or a.lang
        self.length = length or a.settings["word_length"]
        self.word = ""
        self.peek = False
        self.working = False
        self.online_mode = mode == "online"
        self.code = code
        self.code_status = ""
        self._stop_listen = None
        if mode == "pass":
            self.title = T(f"player_{a.pass_state['setter']}")
        else:
            self.title = T("online_title")
        self.ids.board.reset(1, self.length, self.lang == "he")
        self.ids.keyboard.language = self.lang
        self.ids.keyboard.set_states({})
        self._show()
        if self.online_mode and role == "p1" and not code:
            self.code_status = T("connecting")
            threading.Thread(target=self._create_game, daemon=True).start()
        elif self.online_mode and role == "p2":
            self.code_status = T("friend_joined")

    # -- online game creation
    def _create_game(self):
        try:
            code = online.OnlineClient().create_game(self.lang, self.length)
        except Exception:
            self._create_failed()
            return
        self._created(code)

    @mainthread
    def _create_failed(self):
        app().toast(T("net_error"), 3)
        app().back("online_menu")

    @mainthread
    def _created(self, code):
        if app().sm.current != "setter":
            return
        self.code = code
        self.code_status = T("waiting_friend")
        self._stop_listen = online.OnlineClient().listen(code, self._on_snap)

    def _on_snap(self, snap):
        if snap.get("joined_p2"):
            self._joined()

    @mainthread
    def _joined(self):
        if self.code_status != T("friend_joined"):
            self.code_status = T("friend_joined")
            app().sfx("pop")
            app().buzz(40)
        if self._stop_listen:
            self._stop_listen()
            self._stop_listen = None

    def share_code(self):
        text = f"{T('share_title')}: {T('join_game')} {self.code}"
        if not share(text, T("share")):
            app().toast(T("copied"))

    # -- typing
    def _show(self):
        shown = self.word if self.peek else "•" * len(self.word)
        self.ids.board.show_typed(0, shown)

    def toggle_peek(self):
        self.peek = not self.peek
        self._show()

    def key_letter(self, letter):
        if self.working or not is_word_shaped(letter, self.lang) or len(self.word) >= self.length:
            return
        self.word += letter
        app().sfx("tap")
        app().buzz(8)
        self._show()

    def key_delete(self):
        if self.word and not self.working:
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
        if self.working:
            return
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
            return
        if not self.code:
            app().toast(T("connecting"))
            return
        self.working = True
        salt, commit = online.make_commitment(word)
        threading.Thread(target=self._commit, args=(word, salt, commit), daemon=True).start()

    def _commit(self, word, salt, commit):
        try:
            online.OnlineClient().commit_word(self.code, self.role, commit)
        except Exception:
            self._commit_failed()
            return
        self._committed(word, salt)

    @mainthread
    def _commit_failed(self):
        self.working = False
        app().toast(T("net_error"), 3)

    @mainthread
    def _committed(self, word, salt):
        if self._stop_listen:
            self._stop_listen()
            self._stop_listen = None
        app().go("online_game").start(self.code, self.role, word, salt, self.lang, self.length)

    def go_back(self):
        if self._stop_listen:
            self._stop_listen()
            self._stop_listen = None
        if self.mode == "online" and self.code:
            code, role = self.code, self.role
            threading.Thread(target=lambda: _quiet(online.OnlineClient().forfeit, code, role),
                             daemon=True).start()
        app().back("online_menu" if self.mode == "online" else "home")


def _quiet(fn, *args):
    try:
        fn(*args)
    except Exception:
        pass


class PassPhoneScreen(BaseScreen):
    who = StringProperty("")

    def start(self, secret):
        self.secret = secret
        self.who = T(f"player_{3 - app().pass_state['setter']}")

    def ready(self):
        app().go("game").start("pass", secret=self.secret)


# ---------------------------------------------------------------- online ---

class OnlineMenuScreen(BaseScreen):
    def create(self):
        app().go("setter").start("online", role="p1")

    def join(self):
        app().go("join").start()


class JoinScreen(BaseScreen):
    code = StringProperty("")
    working = BooleanProperty(False)

    def start(self):
        self.code = ""
        self.working = False

    def go_back(self):
        app().back("online_menu")

    def key_letter(self, ch):
        if ch.isdigit() and len(self.code) < online.CODE_DIGITS and not self.working:
            self.code += ch
            app().sfx("tap")

    def key_delete(self):
        if self.code and not self.working:
            self.code = self.code[:-1]
            app().sfx("delete")

    def key_enter(self):
        self.join()

    def join(self):
        if self.working:
            return
        if len(self.code) != online.CODE_DIGITS:
            app().toast(T("enter_code"))
            app().sfx("error")
            return
        self.working = True
        code = self.code
        threading.Thread(target=self._join, args=(code,), daemon=True).start()

    def _join(self, code):
        try:
            snap = online.OnlineClient().join_game(code)
            self._joined(code, snap.get("language", "en"), snap.get("length", 5))
        except online.GameError as e:
            self._failed(e.key)
        except Exception:
            self._failed("net_error")

    @mainthread
    def _failed(self, key):
        self.working = False
        app().toast(T(key), 3)
        app().sfx("error")

    @mainthread
    def _joined(self, code, language, length):
        self.working = False
        app().go("setter").start("online", language=language, length=length, code=code, role="p2")


class OnlineGameScreen(BaseScreen):
    status = StringProperty("")
    code = StringProperty("")
    panel_up = BooleanProperty(False)
    r_title = StringProperty("")
    r_sub = StringProperty("")
    r_extra = StringProperty("")
    snap = None
    client = None
    sending = False
    finished = False

    def start(self, code, role, word, salt, language, length):
        self.code, self.role, self.word, self.salt = code, role, word, salt
        self.lang, self.length = language, length
        self.client = online.OnlineClient()
        self.snap = None
        self.current = ""
        self.rendered = 0
        self.sending = False
        self.scoring = False
        self.revealing = False
        self.finished = False
        self._leave_armed = False
        self.ids.board.reset(MAX_ATTEMPTS, length, language == "he")
        self.ids.mini.reset(MAX_ATTEMPTS, length, language == "he")
        self.ids.keyboard.language = language
        self.ids.keyboard.set_states({})
        self.status = T("waiting_word")
        self._hide_panel(instant=True)
        self._stop = self.client.listen(code, self._on_snap, self._on_error)

    # -- network callbacks (background thread -> main thread)
    def _on_snap(self, snap):
        Clock.schedule_once(lambda dt: self._process(snap))

    def _on_error(self, _err):
        Clock.schedule_once(lambda dt: app().toast(T("net_retry")))

    def _bg(self, fn, *args, done=None):
        def run():
            try:
                fn(*args)
            except Exception:
                Clock.schedule_once(lambda dt: app().toast(T("net_retry")))
            finally:
                if done:
                    Clock.schedule_once(lambda dt: done())
        threading.Thread(target=run, daemon=True).start()

    def _process(self, snap):
        if getattr(self, "client", None) is None or snap.get("code") != self.code:
            return
        self.snap = snap
        me, opp = self.role, online.other(self.role)
        my_guesses = snap.get(f"guesses_{me}", [])
        my_fb = snap.get(f"feedback_{me}", [])
        their_guesses = snap.get(f"guesses_{opp}", [])
        their_fb = snap.get(f"feedback_{opp}", [])

        # Opponent's mini board: colors only.
        for i, fb in enumerate(their_fb[:MAX_ATTEMPTS]):
            self.ids.mini.set_row(i, [""] * self.length, decode_feedback(fb))

        # Reveal any newly scored rows of mine.
        history = [(g, decode_feedback(f)) for g, f in zip(my_guesses, my_fb)]
        for i in range(self.rendered, min(len(history), MAX_ATTEMPTS)):
            g, fb = history[i]
            self.ids.board.reveal_row(i, g, fb)
            self.current = ""
        if len(history) > self.rendered:
            self.rendered = len(history)
            delay = self.ids.board.reveal_duration()
            Clock.schedule_once(lambda dt: self.ids.keyboard.set_states(letter_states(history)), delay)

        status = snap.get("status")
        if status == "waiting":
            self.status = T("waiting_word")
        elif status == "playing":
            if len(their_guesses) > len(their_fb) and not self.scoring:
                self.scoring = True
                self._bg(self.client.score_pending, self.code, me, self.word,
                         done=lambda: setattr(self, "scoring", False))
            mine_pending = len(my_guesses) > len(my_fb)
            if mine_pending:
                self.status = T("scoring")
            elif snap.get("turn") == me:
                if self.status != T("your_turn"):
                    app().sfx("pop")
                    app().buzz(30)
                self.status = T("your_turn")
            else:
                self.status = T("their_turn")
            if not mine_pending and len(my_guesses) < MAX_ATTEMPTS:
                self.ids.board.show_typed(len(my_guesses), self.current)
        elif status == "finished":
            self._finished(snap)

    def _finished(self, snap):
        me = self.role
        if not snap.get(f"reveal_{me}") and not self.revealing:
            self.revealing = True
            self._bg(self.client.reveal, self.code, me, self.salt, self.word,
                     done=lambda: setattr(self, "revealing", False))
        winner = snap.get("winner")
        if snap.get("ended_by") == "forfeit" and winner == me:
            title = T("forfeit_win")
        elif winner == me:
            title = T("you_won")
        elif winner == "draw":
            title = T("draw")
        else:
            title = T("you_lost")
        word, honest = online.verify_opponent(snap, me)
        self.r_title = title
        self.r_sub = T("their_word", word=word.upper()) if word else T("no_reveal")
        self.r_extra = T("cheat_warning") if honest is False else ""
        self.status = title
        if not self.finished:
            self.finished = True
            delay = self.ids.board.reveal_duration()
            if winner == me:
                Clock.schedule_once(lambda dt: (app().sfx("win"), app().confetti.burst()), delay)
            else:
                Clock.schedule_once(lambda dt: app().sfx("lose"), delay)
            Clock.schedule_once(lambda dt: self._show_panel(), delay + 0.6)
        if word and snap.get(f"reveal_{me}"):
            self._stop_listening()

    # -- input
    def _can_type(self):
        s = self.snap
        if not s or s.get("status") != "playing" or s.get("turn") != self.role or self.sending:
            return False
        return len(s.get(f"guesses_{self.role}", [])) == len(s.get(f"feedback_{self.role}", []))

    def _row(self):
        return len(self.snap.get(f"guesses_{self.role}", [])) if self.snap else 0

    def key_letter(self, letter):
        if not self._can_type() or not is_word_shaped(letter, self.lang):
            return
        if len(self.current) < self.length:
            self.current += letter
            app().sfx("tap")
            app().buzz(8)
            self.ids.board.show_typed(self._row(), self.current)

    def key_delete(self):
        if self._can_type() and self.current:
            self.current = self.current[:-1]
            app().sfx("delete")
            self.ids.board.show_typed(self._row(), self.current)

    def key_enter(self):
        if not self._can_type():
            if self.snap and self.snap.get("status") == "playing":
                app().toast(self.status)
            return
        guess = normalize_word(self.current, self.lang)
        mine = self.snap.get(f"guesses_{self.role}", [])
        problem = None
        if len(guess) < self.length:
            problem = "not_enough"
        elif not words.is_valid(guess, self.lang, self.length):
            problem = "not_valid"
        elif guess in mine:
            problem = "already_guessed"
        if problem:
            app().toast(T(problem))
            app().sfx("error")
            app().buzz(70)
            self.ids.board.shake_row(self._row())
            return
        self.sending = True
        self.status = T("scoring")
        self._bg(self.client.submit_guess, self.code, self.role, guess,
                 done=lambda: setattr(self, "sending", False))

    # -- leaving
    def _stop_listening(self):
        if getattr(self, "_stop", None):
            self._stop()
            self._stop = None

    def go_back(self):
        if not self.finished and not self._leave_armed:
            self._leave_armed = True
            app().toast(T("leave_game") + "?")
            Clock.schedule_once(lambda dt: setattr(self, "_leave_armed", False), 2.5)
            return
        if not self.finished:
            self._bg(self.client.forfeit, self.code, self.role)
        self._stop_listening()
        self.client = None
        app().back()

    def _show_panel(self):
        self.panel_up = True
        Animation(y=self.y, d=.45, t="out_back").start(self.ids.panel)

    def _hide_panel(self, instant=False):
        self.panel_up = False
        panel = self.ids.panel
        Animation.cancel_all(panel)
        panel.y = self.y - panel.height - dp(40)

    def to_menu(self):
        self.finished = True
        self.go_back()


# ------------------------------------------------------ stats / settings ---

class StatsScreen(BaseScreen):
    mode = StringProperty("daily")
    played = StringProperty("0")
    pct = StringProperty("0")
    streak = StringProperty("0")
    best = StringProperty("0")
    dist = ListProperty([0] * MAX_ATTEMPTS)
    last = NumericProperty(0)
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
        self.last = s.get("last") or 0
        self.empty = s["played"] == 0


class SettingsScreen(BaseScreen):
    pass


class RulesScreen(BaseScreen):
    pass


SCREENS = {
    "home": HomeScreen,
    "game": GameScreen,
    "setter": SetterScreen,
    "pass_phone": PassPhoneScreen,
    "online_menu": OnlineMenuScreen,
    "join": JoinScreen,
    "online_game": OnlineGameScreen,
    "stats": StatsScreen,
    "settings": SettingsScreen,
    "rules": RulesScreen,
}
