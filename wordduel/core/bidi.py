"""Minimal right-to-left display support.

Kivy draws text strictly left-to-right and has no bidi algorithm, so Hebrew
must be handed to it in *visual* order. The old code stored every Hebrew
string pre-reversed, which made translations unreadable. Now all strings are
kept in normal (logical) order and converted here, right before drawing.

Handles one line at a time: Hebrew runs are reversed, embedded runs of
Latin letters / digits (e.g. "שחקן 1", game codes, "#42") keep their order,
and brackets are mirrored. Line wrapping is done by the caller *before*
conversion (see widgets.RtlLabel) so that wrapped lines read top-to-bottom.
"""
import re

_RTL = re.compile(r"[֐-׿יִ-ﭏ]")
_LTR_RUN = re.compile(r"[A-Za-z0-9]+(?:[.,:/%\-][A-Za-z0-9]+)*")
_MIRROR = str.maketrans("()[]{}<>", ")(][}{><")


def has_rtl(text):
    return bool(_RTL.search(text or ""))


def visual_line(line):
    if not has_rtl(line):
        return line
    parts = []
    pos = 0
    for m in _LTR_RUN.finditer(line):
        if m.start() > pos:
            parts.append(line[pos:m.start()][::-1].translate(_MIRROR))
        parts.append(m.group())
        pos = m.end()
    if pos < len(line):
        parts.append(line[pos:][::-1].translate(_MIRROR))
    return "".join(reversed(parts))


def visual(text):
    return "\n".join(visual_line(line) for line in (text or "").split("\n"))
