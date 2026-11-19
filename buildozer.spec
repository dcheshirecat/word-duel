[app]
title = Word Duel
package.name = wordduel
package.domain = org.wordduel
source.dir = .
source.include_exts = py,kv,ttf,txt,wav,png
source.exclude_dirs = tools,tests,bin,.github,.buildozer,__pycache__
source.exclude_patterns = README.md,firestore.rules
version = 2.0.0
requirements = python3,kivy==2.3.1,certifi
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/assets/icon.png
android.permissions = INTERNET,VIBRATE
android.api = 35
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.window_softinput_mode = adjustResize
android.accept_sdk_license = True

[buildozer]
log_level = 2
