# Word Duel

A playful word-guessing game for Android, in English and Hebrew, built with Kivy.

![Word Duel in English](docs/screenshots/english.png)
![Word Duel in Hebrew](docs/screenshots/hebrew.png)

## Modes

- **Daily Word**: the same 5-letter puzzle for everyone each day. Progress is saved, streaks are tracked, and results can be shared as an emoji grid.
- **Free Play**: endless random words, 4, 5 or 6 letters long.
- **Pass & Play**: one player picks a secret word, the other guesses. Then swap, with a running score.
- **Challenge a Friend**: pick a secret word and get a 10-digit code. Send it any way you like; your friend enters (or pastes) it and solves your word whenever they want, then can share their result or send a challenge back. Works fully offline.

Also: hints (reveal a letter), hard mode, stats with guess distribution, a high-contrast color option, sound and vibration toggles, and full right-to-left support for Hebrew.

## Project layout

```
main.py                  entry point (Buildozer needs it at the root)
wordduel/core/           pure logic, no Kivy: rules, words, game round, challenge codes, storage, i18n, bidi
wordduel/ui/             Kivy app, screens, widgets, theme, layout.kv
words/                   generated word lists ({lang}_{n}_valid.txt / _answers.txt)
assets/                  fonts (Fredoka, OFL), sounds, icon
tools/                   word-list builder, sound generator, screenshot harness, sources
tests/                   unit tests for the core (pytest)
```

## Running locally

```
pip install kivy==2.3.1 pytest
python main.py           # opens a phone-sized window; your keyboard works too
python -m pytest tests   # core tests, no display needed
```

To regenerate data: `python tools/build_wordlists.py` and `python tools/make_sounds.py`.
For screenshots of every screen: `xvfb-run python tools/screenshots.py OUT_DIR en` (or `he`).

## Building the APK

Run the **Build Android APK** workflow from the GitHub Actions tab. It uses `buildozer.spec` from the repo and uploads the APK as an artifact. Tests run on every push.

## Hebrew text

Kivy draws text left to right only. All strings are stored in normal reading order (`wordduel/core/i18n.py`) and converted at draw time by `wordduel/core/bidi.py`, which also handles wrapping. Never pre-reverse strings.

## Challenge codes

A challenge code is the secret word itself, packed into 9 digits plus a check digit (`wordduel/core/challenge.py`). No server or account is needed, codes work across app versions, and a mistyped digit is caught. The digits are scrambled so the word can't be read off the code at a glance, but this is not encryption.

Never commit service-account keys; `.gitignore` blocks the usual file names.
