"""Sound, vibration and sharing, with graceful fallbacks off Android."""
import os

from kivy.core.audio import SoundLoader
from kivy.core.clipboard import Clipboard
from kivy.logger import Logger
from kivy.utils import platform

from .theme import ASSETS


class Sounds:
    def __init__(self):
        self._cache = {}

    def play(self, name):
        if name not in self._cache:
            path = os.path.join(ASSETS, "sounds", f"{name}.wav")
            self._cache[name] = SoundLoader.load(path) if os.path.exists(path) else None
        snd = self._cache[name]
        if snd:
            try:
                snd.stop()
                snd.play()
            except Exception as e:  # audio backends can be flaky; never crash a game
                Logger.warning(f"WordDuel: sound {name} failed: {e}")


def vibrate(ms=30):
    if platform != "android":
        return
    try:
        from jnius import autoclass
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        context = autoclass("android.content.Context")
        activity.getSystemService(context.VIBRATOR_SERVICE).vibrate(ms)
    except Exception as e:
        Logger.warning(f"WordDuel: vibrate failed: {e}")


def share(text, title="Share"):
    """Open the Android share sheet. Returns False if it fell back to the
    clipboard, so the caller can say "Copied!"."""
    if platform == "android":
        try:
            from jnius import autoclass, cast
            Intent = autoclass("android.content.Intent")
            String = autoclass("java.lang.String")
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.putExtra(Intent.EXTRA_TEXT, cast("java.lang.CharSequence", String(text)))
            intent.setType("text/plain")
            activity.startActivity(Intent.createChooser(intent, String(title)))
            return True
        except Exception as e:
            Logger.warning(f"WordDuel: share failed, using clipboard: {e}")
    Clipboard.copy(text)
    return False
