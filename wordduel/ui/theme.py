"""Colors, fonts and sizes for the playful look."""
import os

from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex as hx

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, "assets")

FONT = "Fredoka"
FONT_BOLD = "FredokaBold"


def register_fonts():
    LabelBase.register(FONT, os.path.join(ASSETS, "fonts", "Fredoka-SemiBold.ttf"))
    LabelBase.register(FONT_BOLD, os.path.join(ASSETS, "fonts", "Fredoka-Bold.ttf"))


def darker(rgba, amount=0.22):
    r, g, b, a = rgba
    return [r * (1 - amount), g * (1 - amount), b * (1 - amount), a]


def lighter(rgba, amount=0.25):
    r, g, b, a = rgba
    return [r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount, a]


# Sunset-candy background gradient (top -> bottom)
BG_TOP = hx("#6C4CF1")
BG_MID = hx("#B44AD8")
BG_BOTTOM = hx("#FF7A9E")

WHITE = [1, 1, 1, 1]
INK = hx("#2C2058")          # main text on white
INK_SOFT = hx("#7C71AE")     # secondary text on white
CARD = hx("#FFFFFF")
CARD_SOFT = hx("#F3EEFF")
KEY = hx("#FFFFFF")
KEY_EDGE = hx("#C9BEF0")

# Mode button colors
YELLOW = hx("#FFC93C")
MINT = hx("#3EDBA0")
SKY = hx("#4CC3FF")
CORAL = hx("#FF6B6B")
GRAPE = hx("#8C6BFF")

PALETTES = {
    False: {"correct": hx("#38C976"), "present": hx("#FFBE2E"), "absent": hx("#8A84AD")},
    # High-contrast option (the classic colorblind-friendly orange / blue pair)
    True: {"correct": hx("#F5793A"), "present": hx("#5AB3F5"), "absent": hx("#8A84AD")},
}
