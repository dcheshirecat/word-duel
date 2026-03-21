import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase

app_dir = os.path.dirname(os.path.abspath(__file__))
HEBREW_FONT = os.path.join(app_dir, "NotoHebrewBold.ttf")
LabelBase.register(name="NotoHebrewBold", fn_regular=HEBREW_FONT)

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical")
        
        # Test 1: hardcoded font in Label
        label1 = Label(
            text="שלום עולם",
            font_name=HEBREW_FONT,
            font_size=48
        )
        
        # Test 2: registered font name
        label2 = Label(
            text="שלום עולם",
            font_name="NotoHebrewBold",
            font_size=48
        )
        
        layout.add_widget(label1)
        layout.add_widget(label2)
        return layout

TestApp().run()