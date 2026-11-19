"""Settings, stats and daily progress, saved as JSON in the app data dir."""
import json
import os
import tempfile

from .rules import DEFAULT_LENGTH, MAX_ATTEMPTS


class JsonStore:
    def __init__(self, path, defaults):
        self.path = path
        self.data = json.loads(json.dumps(defaults))
        try:
            with open(path, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                self.data.update(loaded)
        except (OSError, ValueError):
            pass

    def save(self):
        folder = os.path.dirname(self.path) or "."
        os.makedirs(folder, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)


SETTINGS_DEFAULTS = {
    "language": "en",
    "word_length": DEFAULT_LENGTH,
    "hard_mode": False,
    "colorblind": False,
    "sound": True,
    "vibration": True,
    "seen_rules": False,
}


class Settings(JsonStore):
    def __init__(self, folder):
        super().__init__(os.path.join(folder, "settings.json"), SETTINGS_DEFAULTS)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()


def _empty_stats():
    return {"played": 0, "wins": 0, "streak": 0, "best": 0,
            "dist": [0] * MAX_ATTEMPTS, "last": None}


class Stats(JsonStore):
    """Stats per (mode, language). Modes: 'daily', 'solo'."""

    def __init__(self, folder):
        super().__init__(os.path.join(folder, "stats.json"), {})

    def get(self, mode, language):
        return self.data.get(f"{mode}_{language}") or _empty_stats()

    def record(self, mode, language, won, attempts, daily_number=None):
        s = self.get(mode, language)
        if mode == "daily" and daily_number is not None:
            # A streak only continues across consecutive days.
            if s.get("last_day") is not None and daily_number != s["last_day"] + 1:
                s["streak"] = 0
            s["last_day"] = daily_number
        s["played"] += 1
        if won:
            s["wins"] += 1
            s["streak"] += 1
            s["best"] = max(s["best"], s["streak"])
            s["dist"][attempts - 1] += 1
            s["last"] = attempts
        else:
            s["streak"] = 0
            s["last"] = None
        self.data[f"{mode}_{language}"] = s
        self.save()
        return s

    def current_streak(self, mode, language, today_number=None):
        """Daily streaks lapse if a day was skipped."""
        s = self.get(mode, language)
        if mode == "daily" and today_number is not None and s.get("last_day") is not None:
            if today_number - s["last_day"] > 1:
                return 0
        return s["streak"]


class DailyProgress(JsonStore):
    """Today's in-progress daily game, so leaving and coming back resumes it."""

    def __init__(self, folder):
        super().__init__(os.path.join(folder, "daily.json"), {})

    def load(self, language, number):
        entry = self.data.get(language)
        if entry and entry.get("number") == number:
            return entry
        return None

    def store(self, language, number, guesses, hints, done, won, hard):
        self.data[language] = {"number": number, "guesses": guesses, "hints": hints,
                               "done": done, "won": won, "hard": hard}
        self.save()
