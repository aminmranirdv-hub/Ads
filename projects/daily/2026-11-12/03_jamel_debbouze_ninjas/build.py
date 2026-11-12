#!/usr/bin/env python3
"""Jamel Debbouze, César 2023: « mettez des ninjas ». FR corrected, EN translation, edit spec.
Source window = YouTube 8:45-11:05 (source t=0 is 8:45)."""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "../../../../tools")
from common import fmt_srt_time, parse_srt  # noqa: E402
from make_short import build_timeline, total_duration  # noqa: E402

C = {
 10: ("Non. Autre proposition.", "No. Another proposal."),
 11: ("Qu'est-ce qui marche en ce moment au", "What's working right now at the"),
 12: ("cinéma ?", "movies?"),
 13: ("Avatar, Astérix, Top Gun.", "Avatar, Asterix, Top Gun."),
 14: ("Les cascades, les effets spéciaux.", "Stunts, special effects."),
 15: ("J'ai regardé nos films d'auteur :", "I looked at our art-house films:"),
 16: ("pas une cascade, pas un effet spécial.", "not one stunt, not one special effect."),
 17: ("C'est normal, ça ?", "Is that normal?"),
 18: ("Non mais sérieusement, vous voulez faire", "No, seriously, do you want to sell"),
 19: ("des entrées ou pas, franchement ?", "tickets or not?"),
 20: ("Il faut booster nos scénarios !", "We need to boost our scripts!"),
 21: ("Il faut être plus créatif !", "We need to be more creative!"),
 22: ("Je sais pas, moi, tu mets Anaïs", "I don't know, put Anaïs"),
 23: ("Demoustier dans un avion de chasse :", "Demoustier in a fighter jet:"),
 24: ("elle fait la même taille que Tom Cruise,", "she's the same height as Tom Cruise,"),
 25: ("c'est sûr, ça passe !", "it'll work for sure!"),
 26: ("Ou… ou…", "Or… or…"),
 27: ("on n'a qu'à inventer un Avatar à la", "we just invent a French-style"),
 28: ("française, tu vois ?", "Avatar, you know?"),
 29: ("C'est des hommes en bleu de…", "It's guys in blue…"),
 30: ("travail.", "overalls."),
 31: ("Et au lieu de se battre pour sauver la", "And instead of fighting to save"),
 32: ("nature, ils se battent pour sauver leur", "nature, they fight to save their"),
 33: ("retraite, eux, tu vois ?", "pensions, you see?"),
 34: ("On a les sujets, on les a.", "We've got the stories, we've got them."),
 35: ("On les a, les sujets.", "We've got the stories."),
 36: ("Il y a qu'à piocher.", "Just pick one."),
 37: ("Ça ne tient qu'à vous.", "It's up to you."),
 38: ("Attends, et si…", "Wait, what if…"),
 39: ("Et si on n'a pas le budget pour les", "What if we don't have the budget for"),
 40: ("Avatars ou pour des avions de chasse ?", "Avatars or fighter jets?"),
 41: ("Mais… des ninjas !", "Well… ninjas!"),
 42: ("Ça ne coûte pas cher, des ninjas.", "Ninjas are cheap."),
 43: ("Mais dès le scénario, faut les mettre, tu", "But you have to put them in the script,"),
 44: ("vois ? Parce que quand je lis, je suis", "you see? Because when I read, I'm"),
 45: ("désolé :", "sorry:"),
 46: ("« Vincent Lindon marche langoureusement", "\"Vincent Lindon walks languorously"),
 47: ("vers Juliette Binoche »,", "toward Juliette Binoche\","),
 48: ("à « langoureusement », on a vidé la salle.", "at \"languorously\", the theater's empty."),
 49: ("Si tu remplaces « langoureusement » par des", "If you replace \"languorously\" with"),
 50: ("ninjas, sur la vie de ma mère, c'est pas", "ninjas, I swear on my mother's life, it's not"),
 51: ("le même film.", "the same film."),
 52: ("T'imagines, Vincent Lindon, il marche comme", "Picture it: Vincent Lindon walks like"),
 53: ("ça, langoureusement, vers Juliette Binoche,", "this, languorously, toward Juliette Binoche,"),
 54: ("il se fait attaquer par des ninjas de part", "and gets attacked by ninjas from"),
 55: ("et d'autre.", "both sides."),
 56: ("Là, il se passe quelque chose, là, là, là,", "NOW something's happening, there, there,"),
 57: ("là, oui, là, on fait des entrées.", "yes, NOW we sell tickets."),
 64: ("Tu rajoutes des ninjas, Juliette, sur la", "Add ninjas, Juliette, I swear on"),
 65: ("vie de ma mère, on fait un malheur.", "my mother's life, it's a smash hit."),
}
RANGES = [(10, 57), (64, 65)]

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

segs = []
for a, b in RANGES:
    s0, e0 = cues[a - 1]["start"] - 0.25, cues[b - 1]["end"] + (1.2 if b in (57, 65) else 0.2)
    part = json.loads(subprocess.run(
        ["python3", "../../../../tools/tighten.py", "words.json", "--start", f"{s0:.2f}", "--end", f"{e0:.2f}",
         "--max-gap", "1.8", "--keep", "1.6", "--lead", "0.25"], capture_output=True, text=True, check=True).stdout.splitlines()[0])
    part[-1]["out"] = round(e0, 3)
    segs += part

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


_, salle = find("salle")
ninja1_s, _ = find("ninjas", 1)
_, retraite = find("retraite")
attack_s, _ = find("attaquer")
_, entrees = find("entrées", 2)
freeze_after(salle, 0.6)
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
    "framing": {"mode": "blur_fill", "raise_px": 140, "pre_crop": {"x0": 0.14, "x1": 0.86, "y0": 0.09, "y1": 1.0}},
    "highlight_words": ["cascade", "effet spécial", "entrées", "Tom Cruise", "retraite", "ninjas", "langoureusement", "vidé la salle"],
    "zooms": [{"at": round(ot(salle) - 1.4, 2), "dur": 2.2, "scale": 1.15}, {"at": round(ot(attack_s) - 0.3, 2), "dur": 2.4, "scale": 1.12}],
    "editorial_captions": [
        {"text": "Jamel a LA solution pour sauver le cinéma français", "start": 0.0, "end": 3.4},
        {"text": "Le plan est parfait", "start": round(ot(entrees) + 0.2, 2), "end": round(ot(entrees) + 2.8, 2)}],
    "overlays": [
        {"file": f"{A}/stickers/dramatic_realization/plot_twist.png", "start": ot(ninja1_s), "end": round(ot(ninja1_s) + 1.4, 2), "position": "upper_center", "width": 520}],
    "sfx": [
        {"file": f"{A}/sfx/boing.wav", "at": round(ot(retraite) + 0.05, 2), "gain_db": -13},
        {"file": f"{A}/sfx/crickets.wav", "at": round(ot(salle) + 0.05, 2), "gain_db": -15},
        {"file": f"{A}/sfx/whoosh.wav", "at": round(ot(attack_s), 2), "gain_db": -12},
        {"file": f"{A}/sfx/impact.wav", "at": round(ot(entrees) + 0.05, 2), "gain_db": -11}],
})
json.dump(spec, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(fr)} cues; {len(segs)} segments; duration {dur:.1f}s; salle@{ot(salle)}")
