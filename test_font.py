import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.text import LabelBase

app_dir = os.path.dirname(os.path.abspath(__file__))
LabelBase.register(name='NotoHebrewBold', fn_regular=os.path.join(app_dir, 'NotoHebrewBold.ttf'))

class TestApp(App):
    def build(self):
        return Label(text='Hello World', font_name='NotoHebrewBold', font_size=48)

TestApp().run()