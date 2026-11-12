#!/usr/bin/env python3
"""Gad Elmaleh, « Merci, la vie »: FR corrected against Montreux Comedy's official captions, EN translation,
tightened segments and punchline-timed effects. Source window = YouTube 3:05-5:15 (source t=0 is 3:05)."""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "../../../../tools")
from common import fmt_srt_time, parse_srt  # noqa: E402
from make_short import build_timeline, total_duration  # noqa: E402

C = {
 4: ("On ment, les amis !", "We lie, my friends!"),
 5: ("À mon âge, je devrais arrêter. J'ai", "At my age, I should stop. I'm"),
 6: ("passé 50 balais. 50 balais,", "past 50. Fifty,"),
 7: ("c'est pas vieux, c'est pas jeune. 50", "it's not old, it's not young. 50"),
 8: ("ans. Ce soir,", "years old. Tonight,"),
 9: ("voilà,", "here we are,"),
 10: ("les filles de 25 ans dans la salle, elles", "the 25-year-old girls in the room"),
 11: ("me regardent. Elles se disent : « Ouah, il", "are looking at me, thinking: \"Wow, he"),
 12: ("pourrait être mon père !", "could be my dad!"),
 13: ("Et en même temps, ça passe. » C'est ça qui", "…but still, he'd do.\" That's what's"),
 14: ("est…", "so…"),
 15: ("Alors, comme tous les mecs de 50 ans, c'est", "So, like every 50-year-old guy, it's"),
 16: ("pathétique, je veux être avec des", "pathetic, I want to be with"),
 17: ("filles plus jeunes que moi. Et ça veut", "younger women. And it means"),
 18: ("rien dire, tu vois. Je scrolle sur Insta", "nothing, you know. I scroll Insta"),
 19: ("comme un c*n.", "like an idiot."),
 20: ("Je tombe sur des filles à moitié à poil", "I find half-naked girls"),
 21: ("qui citent des philosophes, j'ai jamais", "quoting philosophers, I never"),
 22: ("compris pourquoi.", "understood why."),
 23: ("Elles sont de dos, en string,", "From behind, in a thong,"),
 24: ("à Ibiza, et elles écrivent : « Si ton âme et ton", "in Ibiza, and they write: \"If your soul and your"),
 25: ("cœur regardent dans la même direction… »", "heart look in the same direction…\""),
 26: ("Ou alors, elle s'est prise en photo au", "Or she took a photo"),
 27: ("pied d'un jet privé sur le tarmac d'un", "next to a private jet on the tarmac of an"),
 28: ("aéroport. Elle a un sac Vuitton, des", "airport. Vuitton bag,"),
 29: ("chaussures à 3000,", "$3,000 shoes,"),
 30: ("et elle écrit : « Merci,", "and she writes: \"Thank you,"),
 31: ("la vie. »", "life.\""),
 32: ("La vie…", "\"Life\"…"),
 33: ("C'est la vie qui a payé tout ça, oui !", "Sure, \"Life\" paid for all that!"),
 34: ("Jean-Jacques Lavie, 78 ans.", "Jean-Jacques Lavie, age 78."),
 35: ("Il est dans l'avion, miskine, il", "He's on the plane, poor guy, he"),
 36: ("arrive même plus à bouger.", "can't even move anymore."),
 37: ("Non, c'est chaud.", "No, it's rough."),
 38: ("J'ai essayé. J'ai fait des dates avec des", "I tried. I went on dates with"),
 39: ("filles beaucoup plus jeunes que moi.", "much younger girls."),
 40: ("Même dans le langage, dans notre", "Even in the language, in how we"),
 41: ("communication, c'est pathétique. Elle", "communicate, it's pathetic. She"),
 42: ("essaye d'être, finalement, et de", "tries to be something, really, to"),
 43: ("correspondre à quelque chose, et ça va pas.", "fit in, and it doesn't work."),
 44: ("Et moi aussi. On était au resto, je lui", "Me neither. We're at a restaurant, I"),
 45: ("dis : « Ça te plaît, le resto ? » Elle m'a dit :", "ask: \"Do you like the place?\" She says:"),
 46: ("« J'avoue. »", "\"I confess.\""),
 47: ("Moi, j'ai plus de 50 ans. J'ai attendu", "I'm over 50. I waited"),
 48: ("qu'elle avoue un truc toute la soirée.", "all night for her to confess something."),
 49: ("Écoute-moi bien.", "Listen to me."),
 50: ("Elle a commencé une anecdote avec : « Askip… »", "She started a story with: \"Askip…\""),
 51: ("Je lui dis : « Chérie, j'ai 50 balais. « Askip »,", "I said: \"Honey, I'm 50. 'Askip'"),
 52: ("je vois de la lessive. Arrête ! »", "sounds like laundry detergent. Stop!\""),
 53: ("Du coup, je suis tout seul. Tu vois, je", "So now I'm all alone. You see, I'm"),
 54: ("suis seul.", "alone."),
 55: ("Mais j'aime bien être seul.", "But I like being alone."),
}

cues = parse_srt("subs.srt")
fr, en = [], []
for i, c in enumerate(cues, 1):
    if i not in C:
        continue
    t = f"{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}"
    fr.append(f"{len(fr) + 1}\n{t}\n{C[i][0]}")
    en.append(f"{len(en) + 1}\n{t}\n{C[i][1]}")
Path("subs.fixed.srt").write_text("\n\n".join(fr) + "\n", encoding="utf-8")
Path("subs.en.srt").write_text("\n\n".join(en) + "\n", encoding="utf-8")

START, END = cues[3]["start"] - 0.3, cues[54]["end"] + 1.0
segs = json.loads(subprocess.run(
    ["python3", "../../../../tools/tighten.py", "words.json", "--start", f"{START:.2f}", "--end", f"{END:.2f}",
     "--max-gap", "1.8", "--keep", "1.6", "--lead", "0.3"], capture_output=True, text=True, check=True).stdout.splitlines()[0])
segs[-1]["out"] = round(END, 3)
words = json.load(open("words.json", encoding="utf-8"))
toks = [re.sub(r"[^\w'-]", "", w["word"].lower()) for w in words]


def find(tok, nth=1):
    k = 0
    for i, t in enumerate(toks):
        if t.startswith(tok):
            k += 1
            if k == nth:
                return words[i]["start"], words[i]["end"]
    raise SystemExit(f"not found {tok}")


def freeze_after(src, dur):
    for s in segs:
        if s["in"] <= src <= s["out"]:
            s["freeze"] = dur


lavie_s, _ = find("lavi")
ans78_s, ans78 = find("78")
_, lessive = find("lessive")
_, avoue = find("'avoue")
insta_s, _ = find("insta")
freeze_after(ans78 + 0.4, 0.6)
tl = build_timeline(segs)


def ot(src):
    for s in tl:
        if s["src_in"] <= src <= s["src_out"]:
            return round(s["out_start"] + src - s["src_in"], 2)
    return round(next(s["out_start"] for s in tl if s["src_in"] > src), 2)


dur = total_duration(tl)
A = "../../../../assets"
spec = json.load(open("edit.json", encoding="utf-8"))
spec.update({
    "segments": segs,
    "framing": {"mode": "blur_fill", "raise_px": 140, "pre_crop": {"x0": 0.2, "x1": 0.8, "y0": 0.0, "y1": 0.94}},
    "subtitles": "subs.fixed.srt",
    "translation": {"file": "subs.en.srt", "language": "en"},
    "highlight_words": ["50 balais", "Insta", "philosophes", "Merci", "Lavie", "78 ans", "J'avoue", "avoue", "Askip", "lessive"],
    "zooms": [{"at": ot(lavie_s) - 0.2, "dur": 2.6, "scale": 1.18}, {"at": ot(lessive) - 1.2, "dur": 2.0, "scale": 1.12}],
    "editorial_captions": [
        {"text": "POV : tu lis les légendes Insta à 50 ans", "start": 0.0, "end": 3.2},
        {"text": "Merci qui ?", "start": ot(ans78) + 0.2, "end": ot(ans78) + 2.6}],
    "overlays": [
        {"file": f"{A}/stickers/dramatic_realization/il_a_compris.png", "start": ot(ans78) + 0.1, "end": ot(ans78) + 1.6, "position": "upper_center", "width": 520},
        {"file": f"{A}/stickers/confusion/quoi.png", "start": ot(avoue) + 0.1, "end": ot(avoue) + 1.4, "position": "lower_right", "width": 380}],
    "sfx": [
        {"file": f"{A}/sfx/impact.wav", "at": ot(ans78) + 0.05, "gain_db": -10},
        {"file": f"{A}/sfx/record_scratch.wav", "at": ot(avoue) + 0.05, "gain_db": -12},
        {"file": f"{A}/sfx/boing.wav", "at": ot(lessive) + 0.05, "gain_db": -13}],
})
for z in spec["zooms"]:
    z["at"] = round(z["at"], 2)
json.dump(spec, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(fr)} cues; {len(segs)} segments; duration {dur:.1f}s; lavie@{ot(lavie_s)}")
