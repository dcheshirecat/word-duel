"""Word Duel: entry point (Buildozer needs main.py at the project root)."""
import traceback

from wordduel import crash

previous_crash = crash.install()   # before Kivy, so native crashes are recorded

from kivy.config import Config  # noqa: E402
from kivy.utils import platform  # noqa: E402

if platform not in ("android", "ios"):
    # Phone-shaped window when running on a desktop.
    Config.set("graphics", "width", "412")
    Config.set("graphics", "height", "880")


def show_startup_crash(report):
    """The app couldn't even start: run a bare app that just shows the error."""
    from kivy.app import App
    from kivy.uix.widget import Widget

    class CrashApp(App):
        title = "Word Duel"

        def build(self):
            return Widget()

        def on_start(self):
            crash.show_overlay("Word Duel couldn't start", report)

    CrashApp().run()


if __name__ == "__main__":
    try:
        crash.capture_logs()
        crash.install_kivy_handler()
        crash.install_long_press_share()
        from kivy.clock import Clock
        from wordduel.ui.app import WordDuelApp
        if previous_crash:
            crash.share_natively(previous_crash)
            Clock.schedule_once(lambda dt: crash.show_overlay(
                "Word Duel closed unexpectedly last time", previous_crash), 1.5)
        WordDuelApp().run()
    except Exception:
        report = traceback.format_exc()
        print(report)
        crash.save_report(report)
        show_startup_crash(report)
