"""Word Duel: entry point (Buildozer needs main.py at the project root)."""
from kivy.config import Config
from kivy.utils import platform

if platform not in ("android", "ios"):
    # Phone-shaped window when running on a desktop.
    Config.set("graphics", "width", "412")
    Config.set("graphics", "height", "880")

from wordduel.ui.app import WordDuelApp  # noqa: E402

if __name__ == "__main__":
    WordDuelApp().run()
