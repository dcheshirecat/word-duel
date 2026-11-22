import os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import Metrics
from kivy.utils import platform
from kivy.properties import DictProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import NoTransition, ScreenManager

from ..core.i18n import tr
from ..core.storage import DailyProgress, Settings, Stats
from . import theme
from .platform_services import Sounds, vibrate
from .widgets import Background, Confetti, Toast

# Not named wordduel.kv on purpose: Kivy auto-loads "<appname>.kv", and we
# load it ourselves after registering fonts. Same name = loaded twice.
KV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout.kv")


def read_insets():
    """System bar / cutout insets as (left, top, right, bottom) in Kivy pixels.

    Android 15 draws apps edge to edge, under the status bar and navigation
    bar, so content has to keep clear of them itself.
    WORDDUEL_FAKE_INSETS="l,t,r,b" simulates them on a desktop.
    """
    fake = os.environ.get("WORDDUEL_FAKE_INSETS")
    if fake:
        return tuple(int(v) for v in fake.split(","))
    if platform != "android":
        return (0, 0, 0, 0)
    try:
        from jnius import autoclass
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        view = activity.getWindow().getDecorView()
        scale = Window.width / view.getWidth() if view.getWidth() else 1.0
        win_insets = view.getRootWindowInsets()
        if win_insets is not None:
            if autoclass("android.os.Build$VERSION").SDK_INT >= 30:
                Type = autoclass("android.view.WindowInsets$Type")
                i = win_insets.getInsets(Type.systemBars() | Type.displayCutout())
                raw = (i.left, i.top, i.right, i.bottom)
            else:
                raw = (win_insets.getSystemWindowInsetLeft(), win_insets.getSystemWindowInsetTop(),
                       win_insets.getSystemWindowInsetRight(), win_insets.getSystemWindowInsetBottom())
        else:
            res = activity.getResources()

            def dimen(name):
                rid = res.getIdentifier(name, "dimen", "android")
                return res.getDimensionPixelSize(rid) if rid else 0
            raw = (0, dimen("status_bar_height"), 0, dimen("navigation_bar_height"))
        return tuple(int(round(v * scale)) for v in raw)
    except Exception as e:
        Logger.warning(f"WordDuel: could not read insets: {e}")
        return (0, 0, 0, 0)


class WordDuelApp(App):
    title = "Word Duel"
    icon = os.path.join(theme.ASSETS, "icon.png")
    lang = StringProperty("en")
    palette = DictProperty(theme.PALETTES[False])

    # -- setup
    def build(self):
        theme.register_fonts()
        self.settings = Settings(self.user_data_dir)
        self.stats = Stats(self.user_data_dir)
        self.daily_progress = DailyProgress(self.user_data_dir)
        self.sounds = Sounds()
        self.pass_state = {"setter": 1, "score": [0, 0]}
        self.lang = self.settings["language"]
        self.palette = theme.PALETTES[bool(self.settings["colorblind"])]

        from . import screens  # noqa: F401  (registers screen classes for kv)
        Builder.load_file(KV)

        root = FloatLayout()
        root.add_widget(Background())          # full screen, behind the system bars
        # Everything interactive lives in the "safe" area, clear of the status
        # bar / camera cutout at the top and the navigation bar at the bottom.
        self.safe = FloatLayout(size_hint=(None, None))
        root.add_widget(self.safe)
        # Instant screen switches: rules out transition rendering issues on phones.
        self.sm = ScreenManager(transition=NoTransition(), pos_hint={"x": 0, "y": 0})
        for name, cls in screens.SCREENS.items():
            self.sm.add_widget(cls(name=name))
        self.safe.add_widget(self.sm)
        self.confetti = Confetti()
        root.add_widget(self.confetti)
        self.toaster = Toast()
        self.safe.add_widget(self.toaster)
        self.insets = (0, 0, 0, 0)             # left, top, right, bottom (pixels)
        root.bind(pos=self._layout_safe, size=self._layout_safe)
        self._update_insets()

        Window.clearcolor = theme.BG_TOP
        Logger.info(f"WordDuel: built, window {Window.size}, density {Metrics.density}")
        self.sm.bind(current=self._log_screen)
        Clock.schedule_interval(self._check_gl, 0)
        Clock.schedule_interval(self._check_window_size, 0.5)
        Clock.schedule_once(lambda dt: self._log_screen(self.sm, self.sm.current), 1)
        Window.bind(on_resize=lambda _w, w, h: Logger.info(f"WordDuel: window resized {w}x{h}"))
        Window.bind(on_keyboard=self._on_keyboard, on_textinput=self._on_textinput)
        return root

    # -- helpers used from kv and screens
    def tr(self, key, _lang=None, **params):
        return tr(self.lang, key, **params)

    def go(self, name, direction="left"):
        if self.lang == "he":
            direction = {"left": "right", "right": "left"}.get(direction, direction)
        if hasattr(self.sm.transition, "direction"):
            self.sm.transition.direction = direction
        self.sm.current = name
        return self.sm.get_screen(name)

    def back(self, name="home"):
        return self.go(name, "right")

    def toast(self, text, duration=1.8):
        self.toaster.show(text, duration)

    def sfx(self, name):
        if self.settings["sound"] and name:
            self.sounds.play(name)

    def buzz(self, ms=25):
        if self.settings["vibration"]:
            vibrate(ms)

    def set_language(self, lang):
        if lang and lang != self.lang:
            self.settings["language"] = lang
            self.lang = lang

    def set_setting(self, key, value):
        if self.settings[key] == value:
            return
        self.settings[key] = value
        if key == "colorblind":
            self.palette = theme.PALETTES[bool(value)]

    # -- diagnostics (shared via press-and-hold, see wordduel/crash.py)
    _gl_errors = 0

    def _check_gl(self, _dt):
        from kivy.graphics.opengl import glGetError
        err = glGetError()
        while err and self._gl_errors < 40:
            self._gl_errors += 1
            Logger.warning(f"WordDuel: GL error 0x{err:04x} on screen {self.sm.current}")
            err = glGetError()

    def _log_screen(self, _sm, name):
        Logger.info(f"WordDuel: screen -> {name}")

        def detail(_dt):
            scr = self.sm.current_screen
            Logger.info(f"WordDuel: {scr.name} pos={tuple(map(int, scr.pos))} "
                        f"size={tuple(map(int, scr.size))} opacity={scr.opacity} "
                        f"in_sm={scr.parent is self.sm} sm={tuple(map(int, self.sm.size))} "
                        f"window={Window.size}")
        Clock.schedule_once(detail, 0.5)

    def on_pause(self):
        Logger.info("WordDuel: on_pause")
        return True

    def on_resume(self):
        Logger.info("WordDuel: on_resume")
        Clock.schedule_once(self._check_window_size, 0.2)
        Clock.schedule_once(self._check_window_size, 1.0)

    # -- safe area (system bars / camera cutout)
    def _layout_safe(self, *_):
        root = self.root or self.safe.parent
        if root is None:
            return
        left, top, right, bottom = self.insets
        self.safe.pos = (root.x + left, root.y + bottom)
        self.safe.size = (max(root.width - left - right, 1), max(root.height - top - bottom, 1))

    def _update_insets(self):
        insets = read_insets()
        if insets != self.insets:
            Logger.info(f"WordDuel: safe-area insets (l, t, r, b) = {insets}")
            self.insets = insets
            self._layout_safe()

    def _check_window_size(self, _dt=None):
        self._update_insets()
        """Re-sync Kivy with the real drawing surface.

        Seen on a phone: after a while the surface grew but Kivy never got a
        resize event, so the app drew into the bottom-left ~83% of the screen
        while touches were mapped to the full screen (taps hit the wrong
        widgets). If the sizes disagree, apply the resize Kivy missed.
        """
        try:
            surface = tuple(int(v) for v in Window._win._get_gl_size())
            sdl_size = tuple(int(v) for v in Window._win.window_size)
        except Exception:
            return
        current = tuple(int(v) for v in Window.size)
        target = surface if platform == "android" else sdl_size
        if min(target) <= 0 or target == current:
            return
        Logger.warning(f"WordDuel: window out of sync: kivy {current}, sdl {sdl_size}, "
                       f"surface {surface}; resizing to {target}")
        Window._size = target
        Window._do_resize(0)
        Window.canvas.ask_update()

    # -- hardware / desktop keys
    def _current(self):
        return self.sm.current_screen

    def _on_keyboard(self, _win, key, _scancode, _codepoint, _mods):
        screen = self._current()
        if key == 27:  # Android back button / Esc
            if self.sm.current == "home":
                return False
            screen.go_back()
            return True
        if key in (8, 127) and hasattr(screen, "key_delete"):
            screen.key_delete()
            return True
        if key in (13, 271) and hasattr(screen, "key_enter"):
            screen.key_enter()
            return True
        return False

    def _on_textinput(self, _win, text):
        screen = self._current()
        if hasattr(screen, "key_letter"):
            for ch in text.lower():
                if ch.isalpha() or ch.isdigit():
                    screen.key_letter(ch)
