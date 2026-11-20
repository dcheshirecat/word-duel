[app]
title = Word Duel
package.name = wordduel
package.domain = org.wordduel
source.dir = .
source.include_exts = py,kv,ttf,txt,wav,png
source.exclude_dirs = tools,tests,bin,recipes,.github,.buildozer,__pycache__
source.exclude_patterns = README.md
version = 2.0.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/assets/icon.png
android.permissions = VIBRATE
android.api = 35
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.window_softinput_mode = adjustResize
android.accept_sdk_license = True
# Local Kivy recipe without `requests` (see recipes/kivy/__init__.py)
p4a.local_recipes = ./recipes

[buildozer]
log_level = 2
