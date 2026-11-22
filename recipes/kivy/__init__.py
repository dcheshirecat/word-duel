"""Kivy, built without `requests` and friends.

The stock python-for-android Kivy recipe pulls in requests, which pulls in
charset-normalizer. Since 3.5.0 that package ships Android wheels which
python-for-android's dependency resolver picks up but then cannot install,
so the APK build fails. Word Duel never downloads anything (Kivy only needs
requests for UrlRequest), so we simply leave those packages out.
"""
from os.path import join

from pythonforandroid.recipes.kivy import KivyRecipe


class OfflineKivyRecipe(KivyRecipe):
    python_depends = ["filetype"]

    def get_recipe_dir(self):
        # Keep using the stock recipe folder so its patch files are found.
        return join(self.ctx.root_dir, "recipes", "kivy")


recipe = OfflineKivyRecipe()
