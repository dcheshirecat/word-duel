"""Build the word lists shipped with the app.

Run from the repo root:  python tools/build_wordlists.py

Outputs (in words/):
  {lang}_{n}_valid.txt    every word accepted as a guess
  {lang}_{n}_answers.txt  common words with no repeated letters, used as
                          secret words for Free Play and the Daily word

Sources (tools/sources/, see README there):
  words_alpha.txt / words_he_full.txt   big dictionaries (validity)
  en_50k.txt / he_50k.txt               subtitle word frequencies (commonness)
  en_US.dic                             Hunspell dictionary; listing a word in
                                        lowercase rules out names, plurals and
                                        other inflected forms
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from wordduel.core.rules import normalize_word, is_word_shaped  # noqa: E402

SRC = os.path.join(ROOT, "tools", "sources")
OUT = os.path.join(ROOT, "words")
LENGTHS = (4, 5, 6)
ANSWER_CAP = {"en": 2500, "he": 2000}

# Words we never want as a secret, even if they are common.
BLOCK = {
    "en": set("""
        bitch whore slut pussy dicks penis vagina nigga nazis fucks shits sluty
        horny rapes raped rapist slave porno boobs titsy kills drugs
        spic kike dyke fags coon gook jizz cunt twat wank homos tits dick cock
        negro slaver nazi rape whores
        """.split()),
    "he": set("""
        זונה זין כוס שרמוטה מזדיין זיון
        """.split()),
}
HE_PREFIXES = "ושהבלכמ"


def read_lines(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def frequency_rank(name):
    ranks = {}
    for i, line in enumerate(read_lines(name)):
        word = line.split()[0].lower()
        ranks.setdefault(word, i)
    return ranks


def build(lang):
    if lang == "en":
        dictionary = {w.lower() for w in read_lines("words_alpha.txt")}
        hunspell = {line.split("/")[0] for line in read_lines("en_US.dic")[1:]}
        base_ok = {w for w in hunspell if w.isalpha() and w.islower()}
        ranks = frequency_rank("en_50k.txt")
    else:
        dictionary = {normalize_word(w, "he") for w in read_lines("words_he_full.txt")}
        base_ok = None
        ranks = {normalize_word(w, "he"): r for w, r in frequency_rank("he_50k.txt").items()}

    for n in LENGTHS:
        valid = {w for w in dictionary if len(w) == n and is_word_shaped(w, lang)}
        candidates = []
        for word, rank in sorted(ranks.items(), key=lambda kv: kv[1]):
            if len(word) != n or word not in valid or len(set(word)) != n:
                continue
            if word in BLOCK[lang]:
                continue
            if base_ok is not None and word not in base_ok:
                continue
            if lang == "he" and word[0] in HE_PREFIXES:
                # Skip "ה+בית"-style forms where the bare word is more common.
                stem_rank = ranks.get(word[1:])
                if stem_rank is not None and stem_rank < rank:
                    continue
            candidates.append(word)
        answers = sorted(candidates[: ANSWER_CAP[lang]])
        valid |= set(answers)
        write(f"{lang}_{n}_valid.txt", sorted(valid))
        write(f"{lang}_{n}_answers.txt", answers)
        print(f"{lang} {n}: {len(valid):>6} valid, {len(answers):>5} answers")


def write(name, words):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(words) + "\n")


if __name__ == "__main__":
    for language in ("en", "he"):
        build(language)
