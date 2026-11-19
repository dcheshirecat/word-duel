[app]
title = Word Duel
package.name = wordduel
package.domain = org.wordduel
source.dir = .
source.include_exts = py,kv,ttf,txt,wav,png
source.exclude_dirs = tools,tests,bin,.github,.buildozer,__pycache__
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
# Pin python-for-android to a stable release. Its master branch currently
# fails to install Android-only wheels (e.g. charset-normalizer) pulled in
# through Kivy's dependencies.
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
