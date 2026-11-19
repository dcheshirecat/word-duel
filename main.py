"""Word Duel: entry point (Buildozer needs main.py at the project root)."""
import os
import traceback

from kivy.config import Config
from kivy.utils import platform

if platform not in ("android", "ios"):
    # Phone-shaped window when running on a desktop.
    Config.set("graphics", "width", "412")
    Config.set("graphics", "height", "880")


def show_crash(report):
    """Last resort: show the error on screen instead of silently closing,
    so a player can screenshot or copy it."""
    from kivy.app import App
    from kivy.core.clipboard import Clipboard
    from kivy.metrics import dp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.scrollview import ScrollView

    class CrashApp(App):
        title = "Word Duel"

        def build(self):
            box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
            box.add_widget(Label(text="Word Duel hit a problem.\nPlease send this to the developer:",
                                 size_hint_y=None, height=dp(60), halign="center"))
            scroll = ScrollView()
            msg = Label(text=report, size_hint_y=None, font_size=dp(11), halign="left", valign="top")
            msg.bind(width=lambda lbl, w: setattr(lbl, "text_size", (w, None)),
                     texture_size=lambda lbl, s: setattr(lbl, "height", s[1]))
            scroll.add_widget(msg)
            box.add_widget(scroll)
            copy = Button(text="Copy error", size_hint_y=None, height=dp(56))
            copy.bind(on_release=lambda *_: Clipboard.copy(report))
            box.add_widget(copy)
            return box

    CrashApp().run()


def save_report(report):
    try:
        with open(os.path.join(os.getcwd(), "last_crash.txt"), "w", encoding="utf-8") as f:
            f.write(report)
    except OSError:
        pass


if __name__ == "__main__":
    try:
        from wordduel.ui.app import WordDuelApp
        WordDuelApp().run()
    except Exception:
        report = traceback.format_exc()
        print(report)
        save_report(report)
        show_crash(report)
