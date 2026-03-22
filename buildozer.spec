
[app]
title = The Word Game
package.name = thewordgame
package.domain = org.thewordgame
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,ttf,json
source.include_patterns = *.ttf,*.png,*.kv,*.json,*.txt
version = 1.3.7
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 34
android.minapi = 26
android.sdk = 34
android.ndk = 25b
android.archs = arm64-v8a
icon.filename = %(source.dir)s/icon.png
android.window_softinput_mode = adjustResize
p4a.branch = master

[buildozer]
log_level = 2
