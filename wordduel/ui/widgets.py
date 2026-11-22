"""Reusable cartoony widgets: bidi-aware labels, chunky 3D buttons, vector
icons, animated letter tiles, the board, keyboards, toggles and effects."""
import math
import random

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import (Color, Ellipse, Line, PopMatrix, PushMatrix, Rectangle, Rotate,
                           RoundedRectangle, Scale, Translate)
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, ColorProperty, ListProperty, NumericProperty,
                             ObjectProperty, OptionProperty, StringProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from ..core.bidi import has_rtl, visual_line
from . import theme


def _app():
    return App.get_running_app()


# ------------------------------------------------------------------ text ---

class RtlLabel(Label):
    """Label taking logical-order text in `rtext`.

    Hebrew is wrapped here (in reading order) and then each line converted to
    visual order, so multi-line Hebrew reads top-to-bottom correctly.
    `align` is start/center/end and flips automatically for RTL text.
    """
    rtext = StringProperty("")
    align = OptionProperty("center", options=["start", "center", "end"])
    wrap = BooleanProperty(False)   # True: height follows the text

    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", theme.FONT)
        super().__init__(**kwargs)
        self.valign = "middle"
        self._trigger = Clock.create_trigger(self._refresh, -1)
        self.bind(rtext=self._trigger, size=self._trigger, font_size=self._trigger,
                  font_name=self._trigger, align=self._trigger, wrap=self._trigger)
        self._trigger()

    def _refresh(self, *_):
        rtl = has_rtl(self.rtext)
        self.halign = {"start": "right" if rtl else "left", "center": "center",
                       "end": "left" if rtl else "right"}[self.align]
        width = max(self.width, 1)
        self.text_size = (width, None if self.wrap else self.height)
        if not rtl:
            self.text = self.rtext
            return
        measurer = CoreLabel(font_name=self.font_name, font_size=self.font_size)
        limit = width - dp(4)
        lines = []
        for para in self.rtext.split("\n"):
            line = ""
            for word in para.split(" "):
                cand = word if not line else f"{line} {word}"
                if not line or measurer.get_extents(cand)[0] <= limit:
                    line = cand
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
        self.text = "\n".join(visual_line(line) for line in lines)


# ----------------------------------------------------------------- icons ---

class Icon(Widget):
    """Simple vector icons drawn with canvas instructions."""
    name = StringProperty("")
    color = ColorProperty([1, 1, 1, 1])
    mirror = BooleanProperty(False)
    max_size = NumericProperty(dp(30))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw, name=self.draw, color=self.draw,
                  mirror=self.draw, max_size=self.draw)

    def draw(self, *_):
        self.canvas.clear()
        s = min(self.width, self.height, self.max_size)
        if s <= 0 or not self.name:
            return
        cx, cy = self.x + self.width / 2, self.y + self.height / 2
        w = max(min(s * 0.09, dp(4.5)), 1.5)
        with self.canvas:
            PushMatrix()
            if self.mirror:
                Scale(x=-1, y=1, z=1, origin=(cx, cy))
            # Always opaque: wide translucent Lines use the stencil buffer
            # (see theme.TILE_EDGE). Fade icons with widget opacity instead.
            Color(rgba=list(self.color[:3]) + [1])
            getattr(self, "_" + self.name, self._missing)(cx, cy, s, w)
            PopMatrix()

    def _missing(self, cx, cy, s, w):
        Ellipse(pos=(cx - s * .2, cy - s * .2), size=(s * .4, s * .4))

    def _back(self, cx, cy, s, w):
        Line(points=[cx + s * .15, cy + s * .3, cx - s * .17, cy, cx + s * .15, cy - s * .3],
             width=w * 1.2, cap="round", joint="round")

    def _close(self, cx, cy, s, w):
        r = s * .28
        Line(points=[cx - r, cy - r, cx + r, cy + r], width=w, cap="round")
        Line(points=[cx - r, cy + r, cx + r, cy - r], width=w, cap="round")

    def _gear(self, cx, cy, s, w):
        for i in range(8):
            a = i * math.pi / 4
            Line(points=[cx + math.cos(a) * s * .2, cy + math.sin(a) * s * .2,
                         cx + math.cos(a) * s * .4, cy + math.sin(a) * s * .4],
                 width=w * 1.1, cap="round")
        Line(circle=(cx, cy, s * .24), width=w * 1.3)

    def _stats(self, cx, cy, s, w):
        bw = s * .18
        for i, h in enumerate((.4, .75, .55)):
            x = cx - s * .36 + i * s * .27
            RoundedRectangle(pos=(x, cy - s * .38), size=(bw, s * h), radius=[bw / 2])

    def _help(self, cx, cy, s, w):
        Line(circle=(cx, cy, s * .42), width=w)
        tex = _text_texture("?", s * .6, self.color, theme.FONT_BOLD)
        Rectangle(texture=tex, pos=(cx - tex.width / 2, cy - tex.height / 2), size=tex.size)

    def _bulb(self, cx, cy, s, w):
        Ellipse(pos=(cx - s * .27, cy - s * .08), size=(s * .54, s * .54))
        RoundedRectangle(pos=(cx - s * .13, cy - s * .3), size=(s * .26, s * .22), radius=[s * .04])
        RoundedRectangle(pos=(cx - s * .09, cy - s * .42), size=(s * .18, s * .09), radius=[s * .04])

    def _backspace(self, cx, cy, s, w):
        l, r, t, b = cx - s * .42, cx + s * .4, cy + s * .26, cy - s * .26
        Line(points=[l, cy, l + s * .2, t, r, t, r, b, l + s * .2, b], close=True,
             width=w * .9, joint="round")
        m, k = cx + s * .07, s * .11
        Line(points=[m - k, cy - k, m + k, cy + k], width=w * .9, cap="round")
        Line(points=[m - k, cy + k, m + k, cy - k], width=w * .9, cap="round")

    def _enter(self, cx, cy, s, w):
        Line(points=[cx - s * .3, cy, cx - s * .07, cy - s * .24, cx + s * .32, cy + s * .26],
             width=w * 1.2, cap="round", joint="round")

    def _share(self, cx, cy, s, w):
        pts = [(cx + s * .25, cy + s * .28), (cx - s * .25, cy), (cx + s * .25, cy - s * .28)]
        Line(points=[*pts[0], *pts[1], *pts[2]], width=w * .8)
        for x, y in pts:
            Ellipse(pos=(x - s * .12, y - s * .12), size=(s * .24, s * .24))

    def _calendar(self, cx, cy, s, w):
        Line(rounded_rectangle=(cx - s * .38, cy - s * .36, s * .76, s * .66, s * .1), width=w)
        Rectangle(pos=(cx - s * .38, cy + s * .08), size=(s * .76, s * .14))
        for dx in (-.18, .18):
            Line(points=[cx + dx * s, cy + s * .22, cx + dx * s, cy + s * .42], width=w, cap="round")
        Ellipse(pos=(cx - s * .1, cy - s * .24), size=(s * .2, s * .2))

    def _infinity(self, cx, cy, s, w):
        Line(ellipse=(cx - s * .42, cy - s * .17, s * .42, s * .34), width=w * 1.1)
        Line(ellipse=(cx, cy - s * .17, s * .42, s * .34), width=w * 1.1)

    def _people(self, cx, cy, s, w):
        for dx, k in ((-.17, 1), (.19, .85)):
            x = cx + dx * s
            r = s * .12 * k
            Ellipse(pos=(x - r, cy + s * .06), size=(2 * r, 2 * r))
            Ellipse(pos=(x - s * .2 * k, cy - s * .4), size=(s * .4 * k, s * .4 * k),
                    angle_start=-90, angle_end=90)

    def _globe(self, cx, cy, s, w):
        r = s * .4
        Line(circle=(cx, cy, r), width=w)
        Line(ellipse=(cx - r * .45, cy - r, r * .9, 2 * r), width=w * .8)
        Line(points=[cx - r, cy, cx + r, cy], width=w * .8)

    def _flame(self, cx, cy, s, w):
        Ellipse(pos=(cx - s * .25, cy - s * .38), size=(s * .5, s * .5))
        Line(points=[cx - s * .24, cy - s * .1, cx, cy + s * .42, cx + s * .24, cy - s * .1],
             width=w * 1.4, joint="round", cap="round")

    def _lock(self, cx, cy, s, w):
        RoundedRectangle(pos=(cx - s * .3, cy - s * .38), size=(s * .6, s * .45), radius=[s * .08])
        Line(ellipse=(cx - s * .18, cy - s * .05, s * .36, s * .45, -90, 90), width=w)

    def _eye(self, cx, cy, s, w):
        Line(ellipse=(cx - s * .42, cy - s * .22, s * .84, s * .44), width=w)
        Ellipse(pos=(cx - s * .12, cy - s * .12), size=(s * .24, s * .24))

    def _phone(self, cx, cy, s, w):
        Line(rounded_rectangle=(cx - s * .22, cy - s * .4, s * .44, s * .8, s * .08), width=w)
        Ellipse(pos=(cx - s * .04, cy - s * .33), size=(s * .08, s * .08))


_tex_cache = {}


def _text_texture(text, size, color, font):
    key = (text, int(size), tuple(round(c, 3) for c in color), font)
    tex = _tex_cache.get(key)
    if tex is None:
        lbl = CoreLabel(text=text, font_size=max(int(size), 1), font_name=font, color=color)
        lbl.refresh()
        tex = lbl.texture
        if len(_tex_cache) > 600:
            _tex_cache.clear()
        _tex_cache[key] = tex
    return tex


# --------------------------------------------------------------- layouts ---

class MirrorMixin:
    """For horizontal BoxLayouts: lay out normally, then flip children
    right-to-left when `rtl` is set (Hebrew)."""
    rtl = BooleanProperty(False)

    def on_rtl(self, *_):
        self._trigger_layout()

    def do_layout(self, *args):
        super().do_layout(*args)
        if self.rtl and self.orientation == "horizontal":
            for child in self.children:
                child.x = self.x + (self.x + self.width) - (child.x + child.width)


class MirrorBox(MirrorMixin, BoxLayout):
    pass


# --------------------------------------------------------------- buttons ---

class ChunkyButton(ButtonBehavior, MirrorMixin, BoxLayout):
    """A rounded button with a darker '3D' bottom edge that squishes on press."""
    face = ColorProperty(theme.YELLOW)
    edge = ColorProperty(None, allownone=True)
    depth = NumericProperty(dp(6))
    radius = NumericProperty(dp(20))
    # Not called `press`: Kivy would treat on_press() as its change handler.
    squish = NumericProperty(0)
    sound = StringProperty("tap")
    pad_x = NumericProperty(dp(14))
    pad_y = NumericProperty(dp(6))

    def on_press(self):
        Animation.cancel_all(self, "squish")
        Animation(squish=1, d=0.05).start(self)
        app = _app()
        if app and self.sound:
            app.sfx(self.sound)

    def on_release(self):
        Animation.cancel_all(self, "squish")
        Animation(squish=0, d=0.3, t="out_back").start(self)


class IconButton(ButtonBehavior, Icon):
    """A bare icon that bounces when tapped."""
    scale = NumericProperty(1)

    def on_press(self):
        Animation.cancel_all(self, "scale")
        (Animation(scale=0.82, d=0.05) + Animation(scale=1, d=0.25, t="out_back")).start(self)
        app = _app()
        if app:
            app.sfx("tap")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self._scale = Scale(x=1, y=1, z=1)
        with self.canvas.after:
            PopMatrix()
        self.bind(scale=self._apply_scale, pos=self._apply_scale, size=self._apply_scale)

    def _apply_scale(self, *_):
        self._scale.origin = (self.x + self.width / 2, self.y + self.height / 2)
        self._scale.x = self._scale.y = self.scale


class Toggle(ButtonBehavior, Widget):
    active = BooleanProperty(False)
    knob = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw, knob=self.draw)
        self.knob = 1 if self.active else 0

    def on_active(self, *_):
        Animation(knob=1 if self.active else 0, d=0.25, t="out_back").start(self)

    def on_release(self):
        self.active = not self.active
        app = _app()
        if app:
            app.sfx("pop")

    def draw(self, *_):
        self.canvas.clear()
        h = min(self.height, dp(34))
        w = h * 1.75
        x = self.x + self.width - w
        y = self.y + self.height / 2 - h / 2
        on = theme.MINT
        off = [0.82, 0.79, 0.93, 1]
        k = max(0.0, min(1.0, self.knob))
        track = [off[i] + (on[i] - off[i]) * k for i in range(4)]
        with self.canvas:
            Color(rgba=theme.darker(track, .18))
            RoundedRectangle(pos=(x, y - dp(3)), size=(w, h), radius=[h / 2])
            Color(rgba=track)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[h / 2])
            kx = x + dp(3) + (w - h) * self.knob
            Color(rgba=[0, 0, 0, .15])
            Ellipse(pos=(kx, y + dp(1)), size=(h - dp(6), h - dp(6)))
            Color(rgba=[1, 1, 1, 1])
            Ellipse(pos=(kx, y + dp(3)), size=(h - dp(6), h - dp(6)))


class Segmented(BoxLayout):
    """A row of pill buttons; `value` is the selected entry of `values`."""
    values = ListProperty([])
    labels = ListProperty([])
    value = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing = dp(6)
        self.bind(values=self._build, labels=self._build, value=self._style)
        Clock.schedule_once(self._build)

    def _build(self, *_):
        self.clear_widgets()
        self._buttons = []
        for v, text in zip(self.values, self.labels or [str(v) for v in self.values]):
            b = ChunkyButton(depth=dp(4), radius=dp(14), pad_x=dp(4), pad_y=dp(2), sound="pop")
            lbl = RtlLabel(rtext=text, font_name=theme.FONT_BOLD, font_size=dp(17))
            b.add_widget(lbl)
            b.bind(on_release=lambda _b, val=v: setattr(self, "value", val))
            b._lbl = lbl
            self._buttons.append((v, b))
            self.add_widget(b)
        self._style()

    def _style(self, *_):
        for v, b in getattr(self, "_buttons", []):
            sel = v == self.value
            b.face = theme.GRAPE if sel else theme.CARD_SOFT
            b._lbl.color = theme.WHITE if sel else theme.INK


# ----------------------------------------------------------------- tiles ---

class Tile(Widget):
    letter = StringProperty("")
    state = StringProperty("empty")   # empty | typed | correct | present | absent
    ghost = StringProperty("")
    flip = NumericProperty(1)
    scale = NumericProperty(1)
    dx = NumericProperty(0)
    dy = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw, letter=self.draw, state=self.draw,
                  ghost=self.draw, flip=self.draw, scale=self.draw, dx=self.draw, dy=self.draw)

    def colors(self):
        app = _app()
        pal = app.palette if app else theme.PALETTES[False]
        if self.state in pal:
            face = pal[self.state]
            return face, theme.darker(face, .25), theme.WHITE
        if self.state == "typed":
            return theme.WHITE, theme.KEY_EDGE, theme.INK
        return None, None, theme.INK

    def draw(self, *_):
        self.canvas.clear()
        w, h = self.size
        if w <= 0:
            return
        face, edge, ink = self.colors()
        depth = h * 0.08
        r = w * 0.18
        with self.canvas:
            PushMatrix()
            Translate(self.dx, self.dy)
            Scale(x=self.scale, y=self.scale * self.flip, z=1, origin=(self.x + w / 2, self.y + h / 2))
            if face is None:
                Color(rgba=[1, 1, 1, .18])
                RoundedRectangle(pos=self.pos, size=self.size, radius=[r])
                Color(rgba=theme.TILE_EDGE)
                Line(rounded_rectangle=(self.x + 1, self.y + 1, w - 2, h - 2, r), width=dp(1.4))
            else:
                Color(rgba=edge)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[r])
                Color(rgba=face)
                RoundedRectangle(pos=(self.x, self.y + depth), size=(w, h - depth), radius=[r])
                Color(rgba=[1, 1, 1, .22])
                RoundedRectangle(pos=(self.x + w * .12, self.y + h - h * .22), size=(w * .76, h * .1),
                                 radius=[h * .05])
            text = self.letter or self.ghost
            if text:
                color = ink if self.letter else [1, 1, 1, .55]
                tex = _text_texture(text.upper(), h * 0.52, color, theme.FONT_BOLD)
                Color(rgba=[1, 1, 1, 1])
                tx = self.x + w / 2 - tex.width / 2
                ty = self.y + depth / 2 + (h - tex.height) / 2
                Rectangle(texture=tex, pos=(tx, ty), size=tex.size)
            PopMatrix()

    # -- animations
    def pop(self):
        Animation.cancel_all(self, "scale")
        (Animation(scale=1.14, d=0.06) + Animation(scale=1, d=0.12, t="out_back")).start(self)

    def reveal(self, state, delay=0, sound=True, on_done=None):
        def start(_dt):
            def mid(*_):
                self.state = state
                if sound and _app():
                    _app().sfx("flip")
                a2 = Animation(flip=1, d=0.14, t="out_quad")
                if on_done:
                    a2.bind(on_complete=lambda *_: on_done())
                a2.start(self)
            a1 = Animation(flip=0, d=0.14, t="in_quad")
            a1.bind(on_complete=mid)
            a1.start(self)
        Clock.schedule_once(start, delay)

    def shake(self):
        a = Animation(dx=0, d=0)
        for x in (dp(9), -dp(9), dp(7), -dp(7), dp(3), 0):
            a += Animation(dx=x, d=0.045)
        a.start(self)

    def jump(self, delay=0):
        def go(_dt):
            (Animation(dy=dp(22), d=0.14, t="out_quad")
             + Animation(dy=0, d=0.45, t="out_bounce")).start(self)
        Clock.schedule_once(go, delay)


class Board(Widget):
    """rows x cols grid of tiles. Column 0 is the first letter; in RTL it is
    drawn on the right."""
    rows = NumericProperty(6)
    cols = NumericProperty(5)
    rtl = BooleanProperty(False)
    max_tile = NumericProperty(dp(66))
    gap_ratio = NumericProperty(0.12)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tiles = []
        self.bind(pos=self._layout, size=self._layout)
        self.reset(self.rows, self.cols, self.rtl)

    def reset(self, rows, cols, rtl):
        self.clear_widgets()
        self.rows, self.cols, self.rtl = rows, cols, rtl
        self.tiles = [[Tile() for _ in range(cols)] for _ in range(rows)]
        for row in self.tiles:
            for t in row:
                self.add_widget(t)
        self._layout()

    def _layout(self, *_):
        if not self.tiles:
            return
        g = self.gap_ratio
        size = min(self.width / (self.cols + (self.cols - 1) * g),
                   self.height / (self.rows + (self.rows - 1) * g), self.max_tile)
        gap = size * g
        total_w = self.cols * size + (self.cols - 1) * gap
        total_h = self.rows * size + (self.rows - 1) * gap
        x0 = self.x + self.width / 2 - total_w / 2
        y0 = self.y + self.height / 2 + total_h / 2 - size
        for r, row in enumerate(self.tiles):
            for c, t in enumerate(row):
                vc = self.cols - 1 - c if self.rtl else c
                t.size = (size, size)
                t.pos = (x0 + vc * (size + gap), y0 - r * (size + gap))

    def tile(self, r, c):
        return self.tiles[r][c]

    def show_typed(self, row, text, hints=None):
        if row >= self.rows:
            return
        hints = hints or {}
        for c, t in enumerate(self.tiles[row]):
            letter = text[c] if c < len(text) else ""
            if letter and letter != t.letter:
                t.pop()
            t.letter = letter
            t.state = "typed" if letter else "empty"
            t.ghost = "" if letter else hints.get(c, "")

    def set_row(self, row, guess, feedback):
        for c, t in enumerate(self.tiles[row]):
            t.letter, t.ghost, t.state, t.flip = guess[c], "", feedback[c], 1

    def reveal_row(self, row, guess, feedback, on_done=None, sound=True):
        for c, t in enumerate(self.tiles[row]):
            t.letter, t.ghost = guess[c], ""
            last = c == self.cols - 1
            t.reveal(feedback[c], delay=c * 0.22, sound=sound,
                     on_done=on_done if last else None)

    def shake_row(self, row):
        if row < self.rows:
            for t in self.tiles[row]:
                t.shake()

    def celebrate_row(self, row):
        for c, t in enumerate(self.tiles[row]):
            t.jump(delay=c * 0.09)

    def reveal_duration(self):
        return self.cols * 0.22 + 0.3


# -------------------------------------------------------------- keyboard ---

KEY_ROWS = {
    "en": ["QWERTYUIOP", "ASDFGHJKL", "<ZXCVBNM>"],
    # Standard Israeli layout; delete and enter where Hebrew phone keyboards put them.
    "he": ["קראטוןםפ<", "שדגכעיחלךף", ">זסבהנמצתץ"],
}


class Key(ChunkyButton):
    pass


class Keyboard(BoxLayout):
    __events__ = ("on_letter", "on_enter", "on_delete")
    language = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(7)
        self.keys = {}
        self.bind(language=lambda *_: self.build())
        Clock.schedule_once(lambda dt: self.build())

    def on_letter(self, letter):
        pass

    def on_enter(self):
        pass

    def on_delete(self):
        pass

    def build(self):
        self.clear_widgets()
        self.keys = {}
        rows = KEY_ROWS.get(self.language, KEY_ROWS["en"])
        units = [sum(1.5 if ch in "<>" else 1 for ch in row) for row in rows]
        widest = max(units)
        for row, u in zip(rows, units):
            line = BoxLayout(spacing=dp(5))
            pad = (widest - u) / 2
            if pad:
                line.add_widget(Widget(size_hint_x=pad))
            for ch in row:
                line.add_widget(self._make_key(ch))
            if pad:
                line.add_widget(Widget(size_hint_x=pad))
            self.add_widget(line)
        self.set_states({})

    def _make_key(self, ch):
        key = Key(depth=dp(5), radius=dp(10), pad_x=0, pad_y=0, sound="")
        if ch == "<":
            key.size_hint_x = 1.5
            key.face = theme.CORAL
            key.add_widget(Icon(name="backspace", color=theme.WHITE, mirror=self.language == "he"))
            key.bind(on_press=lambda *_: self.dispatch("on_delete"))
        elif ch == ">":
            key.size_hint_x = 1.5
            key.face = theme.MINT
            key.add_widget(Icon(name="enter", color=theme.WHITE))
            key.bind(on_press=lambda *_: self.dispatch("on_enter"))
        else:
            lbl = RtlLabel(rtext=ch, font_name=theme.FONT_BOLD, font_size=dp(21))
            key.add_widget(lbl)
            key._lbl = lbl
            letter = ch.lower()
            key.bind(on_press=lambda *_, l=letter: self.dispatch("on_letter", l))
            self.keys[letter] = key
        return key

    def set_states(self, states):
        app = _app()
        pal = app.palette if app else theme.PALETTES[False]
        for letter, key in self.keys.items():
            state = states.get(letter)
            if state in pal:
                key.face = pal[state]
                key._lbl.color = theme.WHITE
            else:
                key.face = theme.KEY
                key._lbl.color = theme.INK


class Keypad(GridLayout):
    """Digits for entering a game code."""
    __events__ = ("on_letter", "on_delete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3
        self.spacing = dp(8)
        for ch in "123456789<0":
            key = Key(depth=dp(5), radius=dp(14), pad_x=0, pad_y=0, sound="")
            if ch == "<":
                key.face = theme.CORAL
                key.add_widget(Icon(name="backspace", color=theme.WHITE))
                key.bind(on_press=lambda *_: self.dispatch("on_delete"))
            else:
                key.face = theme.WHITE
                key.add_widget(RtlLabel(rtext=ch, font_name=theme.FONT_BOLD, font_size=dp(28),
                                        color=theme.INK))
                key.bind(on_press=lambda *_, d=ch: self.dispatch("on_letter", d))
            self.add_widget(key)

    def on_letter(self, letter):
        pass

    def on_delete(self):
        pass


# ------------------------------------------------------------ background ---

def _lerp_stops(stops, t):
    seg = min(int(t * (len(stops) - 1)), len(stops) - 2)
    local = t * (len(stops) - 1) - seg
    a, b = stops[seg], stops[seg + 1]
    return [a[k] + (b[k] - a[k]) * local for k in range(4)]


class Background(Widget):
    """Candy gradient with slowly drifting translucent bubbles.

    The gradient is drawn as thin colored strips rather than a texture, so it
    survives Android dropping and rebuilding the GL context. It is only
    rebuilt when the size changes; each frame just moves the bubbles.
    """
    STRIPS = 48

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rnd = random.Random(7)
        self.blobs = [dict(x=rnd.random(), y=rnd.random(), r=rnd.uniform(.08, .26),
                           sp=rnd.uniform(.15, .4), ph=rnd.uniform(0, 6.28),
                           a=rnd.uniform(.05, .12)) for _ in range(9)]
        self.t = 0.0
        stops = [theme.BG_BOTTOM, theme.BG_MID, theme.BG_TOP]
        self.strips = []
        with self.canvas.before:
            for i in range(self.STRIPS):
                Color(rgba=_lerp_stops(stops, (i + .5) / self.STRIPS))
                self.strips.append(Rectangle())
        self.ellipses = []
        with self.canvas:
            for b in self.blobs:
                Color(1, 1, 1, b["a"])
                self.ellipses.append(Ellipse())
        self.bind(pos=self.layout, size=self.layout)
        Clock.schedule_interval(self.tick, 1 / 30)

    def layout(self, *_):
        h = self.height / self.STRIPS
        for i, rect in enumerate(self.strips):
            rect.pos = (self.x, self.y + i * h)
            rect.size = (self.width, h + 1)
        self.move_bubbles()

    def tick(self, dt):
        self.t += dt
        self.move_bubbles()

    def move_bubbles(self):
        w, h = self.size
        for b, e in zip(self.blobs, self.ellipses):
            r = b["r"] * w
            x = self.x + b["x"] * w + math.sin(self.t * b["sp"] + b["ph"]) * w * .06
            y = self.y + ((b["y"] + self.t * b["sp"] * .012) % 1.2 - .1) * h
            e.pos = (x - r, y - r)
            e.size = (2 * r, 2 * r)


class Confetti(Widget):
    """Burst of falling paper bits. Doesn't block touches."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parts = []
        self.ev = None

    def on_touch_down(self, touch):
        return False

    def burst(self, n=90):
        rnd = random.Random()
        cols = [theme.YELLOW, theme.MINT, theme.SKY, theme.CORAL, theme.GRAPE, theme.WHITE]
        w, h = self.size
        self.parts = [dict(x=self.x + w * rnd.uniform(.1, .9), y=self.top + rnd.uniform(0, h * .3),
                           vx=rnd.uniform(-1, 1) * dp(60), vy=-rnd.uniform(.4, 1) * dp(260),
                           rot=rnd.uniform(0, 360), vr=rnd.uniform(-400, 400),
                           sz=dp(rnd.uniform(6, 12)), c=rnd.choice(cols),
                           wob=rnd.uniform(0, 6.28)) for _ in range(n)]
        if self.ev is None:
            self.ev = Clock.schedule_interval(self.tick, 1 / 60)

    def tick(self, dt):
        alive = []
        for p in self.parts:
            p["wob"] += dt * 5
            p["x"] += (p["vx"] + math.sin(p["wob"]) * dp(40)) * dt
            p["y"] += p["vy"] * dt
            p["rot"] += p["vr"] * dt
            if p["y"] > self.y - dp(20):
                alive.append(p)
        self.parts = alive
        self.canvas.clear()
        with self.canvas:
            for p in self.parts:
                Color(rgba=p["c"])
                PushMatrix()
                Rotate(angle=p["rot"], origin=(p["x"], p["y"]))
                Rectangle(pos=(p["x"] - p["sz"] / 2, p["y"] - p["sz"] / 4),
                          size=(p["sz"], p["sz"] / 2))
                PopMatrix()
        if not self.parts and self.ev is not None:
            self.ev.cancel()
            self.ev = None


class Toast(BoxLayout):
    """A pill message that pops in and fades out."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.size_hint = (None, None)
        self.padding = [dp(18), dp(10)]
        self.label = RtlLabel(font_name=theme.FONT_BOLD, font_size=dp(18), color=theme.WHITE)
        self.add_widget(self.label)
        self._ev = None
        with self.canvas.before:
            self._c = Color(rgba=theme.INK)
            self._r = RoundedRectangle(radius=[dp(18)])
        self.bind(pos=self._bg, size=self._bg)

    def _bg(self, *_):
        self._r.pos, self._r.size = self.pos, self.size

    def on_touch_down(self, touch):
        return False

    def show(self, text, duration=1.8):
        self.label.rtext = text
        lbl = CoreLabel(text=text, font_name=theme.FONT_BOLD, font_size=dp(18))
        width = min(lbl.get_extents(text)[0] + dp(48), (self.parent.width if self.parent else 400) - dp(32))
        self.size = (width, dp(46))
        if self.parent:
            self.center_x = self.parent.center_x
            self.top = self.parent.top - dp(84)
        Animation.cancel_all(self)
        self.opacity = 0
        self.label.font_size = dp(14)
        Animation(opacity=1, d=.12).start(self)
        Animation(font_size=dp(18), d=.25, t="out_back").start(self.label)
        if self._ev:
            self._ev.cancel()
        self._ev = Clock.schedule_once(lambda dt: Animation(opacity=0, d=.3).start(self), duration)
