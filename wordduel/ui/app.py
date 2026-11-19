import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import DictProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from ..core.i18n import tr
from ..core.storage import DailyProgress, Settings, Stats
from . import theme
from .platform_services import Sounds, vibrate
from .widgets import Background, Confetti, Toast

# Not named wordduel.kv on purpose: Kivy auto-loads "<appname>.kv", and we
# load it ourselves after registering fonts. Same name = loaded twice.
KV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout.kv")


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
        root.add_widget(Background())
        self.sm = ScreenManager(transition=SlideTransition(duration=0.28))
        for name, cls in screens.SCREENS.items():
            self.sm.add_widget(cls(name=name))
        root.add_widget(self.sm)
        self.confetti = Confetti()
        root.add_widget(self.confetti)
        self.toaster = Toast()
        root.add_widget(self.toaster)

        Window.clearcolor = theme.BG_TOP
        Window.bind(on_keyboard=self._on_keyboard, on_textinput=self._on_textinput)
        return root

    # -- helpers used from kv and screens
    def tr(self, key, _lang=None, **params):
        return tr(self.lang, key, **params)

    def go(self, name, direction="left"):
        if self.lang == "he":
            direction = {"left": "right", "right": "left"}.get(direction, direction)
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
