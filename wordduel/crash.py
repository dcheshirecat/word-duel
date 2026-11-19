"""Crash diagnostics for builds running on phones, where there is no console.

* Python errors raised inside the Kivy event loop are caught, saved and shown
  in an overlay with a Copy button, and the app keeps running.
* Hard crashes (the process dies, e.g. in native code) are recorded by
  faulthandler; the report is shown the next time the app starts.
"""
import faulthandler
import os
import platform
import sys
import traceback

_REPORT = "last_error.txt"
_FAULT = "last_fault.txt"
_fault_file = None


def _storage_dir():
    for candidate in (os.environ.get("ANDROID_PRIVATE"), os.getcwd(),
                      os.path.expanduser("~")):
        if candidate and os.access(candidate, os.W_OK):
            return candidate
    return None


def _path(name):
    folder = _storage_dir()
    return os.path.join(folder, name) if folder else None


def _header():
    from kivy import __version__ as kivy_version
    from kivy.utils import platform as kivy_platform
    return (f"Word Duel | {kivy_platform} | Python {platform.python_version()} "
            f"| Kivy {kivy_version}\n\n")


def save_report(text):
    path = _path(_REPORT)
    if path:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        except OSError:
            pass


def install():
    """Call as early as possible. Returns a report left by a previous hard
    crash, or None."""
    global _fault_file
    previous = None
    path = _path(_FAULT)
    if path:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                previous = f.read().strip() or None
        except OSError:
            pass
        try:
            _fault_file = open(path, "w", encoding="utf-8")
            faulthandler.enable(_fault_file, all_threads=True)
        except OSError:
            _fault_file = None
    return previous


def install_kivy_handler():
    from kivy.base import ExceptionHandler, ExceptionManager

    class ShowAndContinue(ExceptionHandler):
        def __init__(self):
            self.shown = 0

        def handle_exception(self, exc):
            report = _header() + "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__))
            print(report, file=sys.stderr)
            save_report(report)
            if self.shown < 3:       # don't bury the screen in overlays
                self.shown += 1
                try:
                    show_overlay("Word Duel hit an error", report)
                except Exception:
                    return ExceptionManager.RAISE
            return ExceptionManager.PASS

    ExceptionManager.add_handler(ShowAndContinue())


def show_overlay(title, report):
    """A plain panel on top of everything (default font, no app widgets, so it
    still works if the app's own UI is what broke)."""
    from kivy.core.clipboard import Clipboard
    from kivy.core.window import Window
    from kivy.graphics import Color, Rectangle
    from kivy.metrics import dp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.scrollview import ScrollView

    panel = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(8))
    with panel.canvas.before:
        Color(0.08, 0.06, 0.16, 0.97)
        bg = Rectangle()
    panel.bind(pos=lambda w, v: setattr(bg, "pos", v), size=lambda w, v: setattr(bg, "size", v))

    panel.add_widget(Label(text=f"{title}\nPlease copy this and send it to the developer.",
                           size_hint_y=None, height=dp(56), halign="center"))
    scroll = ScrollView()
    msg = Label(text=report, size_hint_y=None, font_size=dp(11), halign="left", valign="top")
    msg.bind(width=lambda lbl, w: setattr(lbl, "text_size", (w, None)),
             texture_size=lambda lbl, s: setattr(lbl, "height", s[1]))
    scroll.add_widget(msg)
    panel.add_widget(scroll)

    row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
    copy = Button(text="Copy error")
    copy.bind(on_release=lambda *_: (Clipboard.copy(report), setattr(copy, "text", "Copied!")))
    close = Button(text="Close")
    close.bind(on_release=lambda *_: Window.remove_widget(panel))
    row.add_widget(copy)
    row.add_widget(close)
    panel.add_widget(row)
    Window.add_widget(panel)
