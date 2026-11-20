"""Synthesize the small cartoony sound effects in assets/sounds/.

Run from the repo root:  python tools/make_sounds.py
"""
import math
import os
import struct
import wave

RATE = 22050
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sounds")


def tone(freq, dur, vol=0.5, shape="sine", slide=0.0, attack=0.005, release=0.06):
    n = int(RATE * dur)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / RATE
        f = freq + slide * t / dur
        phase += 2 * math.pi * f / RATE
        if shape == "square":
            s = 1.0 if math.sin(phase) > 0 else -1.0
            s *= 0.35
        elif shape == "tri":
            s = 2 / math.pi * math.asin(math.sin(phase))
        else:
            s = math.sin(phase) + 0.25 * math.sin(2 * phase)
        env = min(1.0, t / attack) * min(1.0, (dur - t) / release)
        out.append(s * vol * max(env, 0.0))
    return out


def mix(*parts):
    return [x for p in parts for x in p]


def silence(dur):
    return [0.0] * int(RATE * dur)


def save(name, samples):
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 32000)) for s in samples))


if __name__ == "__main__":
    save("tap.wav", tone(880, 0.04, 0.35, "tri", release=0.03))
    save("delete.wav", tone(500, 0.05, 0.3, "tri", slide=-150, release=0.03))
    save("flip.wav", tone(620, 0.07, 0.3, "sine", slide=260, release=0.05))
    save("error.wav", mix(tone(180, 0.09, 0.35, "square"), tone(150, 0.12, 0.35, "square")))
    save("hint.wav", mix(tone(1047, 0.07, 0.3), tone(1319, 0.07, 0.3), tone(1568, 0.14, 0.3)))
    save("win.wav", mix(*[tone(f, 0.11, 0.38) for f in (523, 659, 784)], tone(1047, 0.35, 0.4, release=0.25)))
    save("lose.wav", mix(tone(392, 0.18, 0.35, "tri"), tone(330, 0.18, 0.35, "tri"),
                         tone(262, 0.4, 0.35, "tri", slide=-30, release=0.3)))
    save("pop.wav", tone(300, 0.08, 0.4, "sine", slide=500, release=0.05))
    print("sounds written to", OUT)
