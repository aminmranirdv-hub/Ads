#!/usr/bin/env python3
"""Corrected FR subtitles (checked against the burned-in captions of the official upload),
EN translation, tightened segments and punchline-timed effects for the Redouane short."""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "../../../../tools")
from common import fmt_srt_time, parse_srt  # noqa: E402
from make_short import build_timeline, total_duration  # noqa: E402

# cue number -> (french, english). "" french = drop the cue (not verifiable).
C = {
 1: ("Normalement, c'est le premier rang, mais", "Normally it's the front row, but"),
 2: ("là, aujourd'hui, spécialement, c'est", "today, specially, it's"),
 3: ("pas le premier rang.", "not the front row."),
 4: ("Vous êtes épargnés !", "You're spared!"),
 5: ("C'est le deuxième, troisième rang.", "It's the second, third row."),
 6: ("Contre-pied,", "Plot twist,"),
 7: ("contre-sens ! Non, non, non, j'ai eu une", "wrong way! No, no, no, I got some"),
 8: ("information juste avant !", "information just before!"),
 9: ("Y'a la meuf qui travaille ici, elle m'a", "The girl who works here told me…"),
 10: ("dit… « Il y a des gens de la SNCF… »", "\"There are people from the SNCF…\""),
 11: ("Elle m'a dit quoi ?", "She told me what?"),
 12: ("Elle m'a dit : « Il y a des fils de… »", "She said: \"There are sons of b…\""),
 13: ("J'ai fait : « Quoi ? »", "I went: \"What?\""),
 14: ("« Des contrôleurs ! Excuse-moi, j'ai fait un", "\"Ticket inspectors! Sorry, that was a"),
 15: ("lapsus ! »", "slip of the tongue!\""),
 16: ("J'ai un message pour vous ! Vraiment, ça", "I have a message for you! Really,"),
 17: ("fait plaisir que vous soyez là,", "it's great that you're here,"),
 18: ("mais niqu** vos mères !", "but screw you!"),
 19: ("Non, non,", "No, no,"),
 20: ("on veut partir en vacances, vous,", "we want to go on holiday, and you,"),
 21: ("vous partez en grève ? C'est quoi le truc ?", "you go on strike? What's the deal?"),
 22: ("", ""),
 23: ("Ça va partir en bagarre, ça va", "This is gonna turn into a fight, it's"),
 24: ("partir !", "gonna kick off!"),
 25: ("Ah, les contrôleurs, je peux pas, je peux", "Ticket inspectors… I can't, I"),
 26: ("pas. Pourquoi vous attendez qu'on", "can't. Why do you wait until we"),
 27: ("s'endorme pour venir ?", "fall asleep to show up?"),
 28: ("« Titres de transport » ? Pourquoi ?", "\"Tickets please\"? Why?"),
 29: ("Contrôlez dès le début, dès le début !", "Check us at the start, right at the start!"),
 30: ("T'as un mec, il te prend ton pass", "One guy takes your health"),
 31: ("sanitaire, il te scanne ton code, il te re-", "pass, scans your code, and then"),
 32: ("contrôle un deuxième coup !", "checks you a second time!"),
 33: ("Vous êtes dangereux !", "You people are dangerous!"),
 34: ("C'est quelle ligne que vous faites ?", "Which line do you work?"),
 35: ("Public : Saint-Lazare ! — Saint-Lazare ?", "Audience: Saint-Lazare! — Saint-Lazare?"),
 36: ("C'est quoi ? C'est que des…", "What's that? That's all…"),
 37: ("Public : Versailles, Nanterre,", "Audience: Versailles, Nanterre,"),
 38: ("RER A ! — Ouah, c'est dur, hein.", "RER A! — Wow, that's rough."),
 39: ("Vous êtes quoi ?", "What are you?"),
 40: ("Vous êtes les nouveaux contrôleurs,", "You're the new inspectors,"),
 41: ("là, qui mettent le…", "the ones who go…"),
 42: ("« Tac ! » quand ils rentrent ?", "\"Bam!\" when they walk in?"),
 43: ("Vous avez cru que vous étiez des Avengers ou", "Did you think you were the Avengers or"),
 44: ("quoi", "what"),
 45: ("? Ils ont raté le concours pour être flics", "? They failed the police exam"),
 46: ("! « Service RATP ! »", "! \"RATP Security!\""),
 47: ("« Police SNCF ! »", "\"SNCF Police!\""),
 48: ("Ils ont un pistolet en plastique !", "They've got a plastic gun!"),
 49: ("Ils interpellent que des clandos !", "They only ever arrest illegal immigrants!"),
 50: ("", ""),
 51: ("Ça va, ça se…", "Okay, okay…"),
 52: ("Ah moi, ça me régale, ça me régale.", "Me, I'm loving this, loving it."),
 53: ("Public : C'est la brigade, ça !", "Audience: That's the squad!"),
 54: ("Je te jure, j'ai vu la pub à la télé.", "I swear, I saw the ad on TV."),
 55: ("Regardez-moi cette pub !", "Look at this ad!"),
 56: ("Les mecs, ils rentrent.", "The guys walk in."),
 57: ("C'est vous, ça, la fameuse…", "That's you, the famous…"),
 58: ("Ils arrivent, ils rentrent.", "They show up, they walk in."),
 59: ("Genre, c'est des contrôleurs en civil.", "Like, they're plain-clothes inspectors."),
 60: ("Ils rentrent comme ça.", "They walk in like this."),
 61: ("C'est mon plus beau fou rire 2021 !", "Best laugh I've had all of 2021!"),
 62: ("Rentrez chez vous", "Go home"),
 63: ("et vous regardez cette pub !", "and watch that ad!"),
 64: ("Donc vous faites tout ça.", "So you do all this."),
 65: ("Qui vous a ramené ?", "Who brought you here?"),
 66: ("C'est vous, madame", "Was it you, madam"),
 67: ("? Vous faites quoi ?", "? What do you do?"),
 68: ("Vous aussi vous contrôlez les gens ?", "You check people's tickets too?"),
 69: ("Et ça va ? Ça se passe bien ?", "And how's it going? All good?"),
 70: ("", ""),
 71: ("", ""),
 72: ("Vous avez des primes si plus vous", "Do you get bonuses the more people"),
 73: ("attrapez des gens ou pas ?", "you catch, or not?"),
 74: ("Public : Non ! Bah c'est pour ça qu'on est là !", "Audience: No! Well, that's why we're here!"),
}

cues = parse_srt("subs.srt")
fr, en = [], []
for i, c in enumerate(cues, 1):
    if i not in C or not C[i][0]:
        continue
    t = f"{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}"
    fr.append(f"{len(fr) + 1}\n{t}\n{C[i][0]}")
    en.append(f"{len(en) + 1}\n{t}\n{C[i][1]}")
Path("subs.fixed.srt").write_text("\n\n".join(fr) + "\n", encoding="utf-8")
Path("subs.en.srt").write_text("\n\n".join(en) + "\n", encoding="utf-8")

END = cues[73]["end"] + 1.2  # cue 74 + a beat of laughter; stop before the 2:55 exchange
segs = json.loads(subprocess.run(
    ["python3", "../../../../tools/tighten.py", "words.json", "--start", "0", "--end", f"{END:.2f}",
     "--max-gap", "1.8", "--keep", "1.6", "--lead", "0.3"], capture_output=True, text=True, check=True).stdout.splitlines()[0])
segs[-1]["out"] = round(END, 3)
words = json.load(open("words.json", encoding="utf-8"))
toks = [re.sub(r"[^\w'-]", "", w["word"].lower()) for w in words]


def find(tok, nth=1):
    k = 0
    for i, t in enumerate(toks):
        if t == tok:
            k += 1
            if k == nth:
                return words[i]["start"], words[i]["end"]
    raise SystemExit(f"not found {tok}")


def freeze_after(src, dur):
    for s in segs:
        if s["in"] <= src <= s["out"]:
            s["freeze"] = dur


_, lapsus = find("lapsus")
ctrl_s, _ = find("contrôleurs")
_, flics = find("flics")
_, plast = find("plastique")
_, avengers = find("avengers")
_, primes_q = find("pas", nth=sum(1 for t in toks[:[i for i, t in enumerate(toks) if t == "attrapez"][0]] if t == "pas") + 1)
freeze_after(lapsus, 0.7)
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
    "framing": {"mode": "blur_fill", "raise_px": 140, "pre_crop": {"x0": 0.17, "x1": 0.83, "y0": 0.02, "y1": 0.70}},
    "subtitles": "subs.fixed.srt",
    "translation": {"file": "subs.en.srt", "language": "en"},
    "highlight_words": ["contrôleurs", "lapsus", "vacances", "grève", "endorme", "Avengers", "flics", "plastique", "fou rire", "primes"],
    "zooms": [{"at": ot(ctrl_s) - 0.1, "dur": 2.6, "scale": 1.15}, {"at": ot(flics) - 0.8, "dur": 2.0, "scale": 1.12}],
    "editorial_captions": [
        {"text": "Il découvre que le 2e rang, c'est des contrôleurs", "start": 0.0, "end": 3.4},
        {"text": "Le contrôleur contrôlé", "start": ot(primes_q) + 0.3, "end": min(dur, ot(primes_q) + 3.0)}],
    "overlays": [
        {"file": f"{A}/stickers/shock/wait_what.png", "start": ot(ctrl_s), "end": ot(ctrl_s) + 1.5, "position": "upper_center", "width": 520},
        {"file": f"{A}/stickers/sarcasm/sure_buddy.png", "start": ot(avengers) + 0.1, "end": ot(avengers) + 1.5, "position": "upper_center", "width": 500},
        {"file": f"{A}/stickers/awkward_silence/awkward.png", "start": ot(primes_q) + 0.2, "end": ot(primes_q) + 1.6, "position": "lower_right", "width": 420}],
    "sfx": [
        {"file": f"{A}/sfx/record_scratch.wav", "at": ot(lapsus) + 0.05, "gain_db": -11},
        {"file": f"{A}/sfx/boing.wav", "at": ot(plast) + 0.05, "gain_db": -13},
        {"file": f"{A}/sfx/impact.wav", "at": ot(flics) + 0.05, "gain_db": -11}],
})
json.dump(spec, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(fr)} cues; {len(segs)} segments; duration {dur:.1f}s; lapsus@{ot(lapsus)} flics@{ot(flics)}")
