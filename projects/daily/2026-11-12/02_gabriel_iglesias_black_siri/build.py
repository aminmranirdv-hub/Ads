#!/usr/bin/env python3
"""Gabriel Iglesias, « Black Siri »: EN transcript + FR translation, story trimmed to <3:00.
Source window = YouTube 0:45-5:00 (source t=0 is 0:45). Burned-in captions are cropped out."""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "../../../../tools")
from common import fmt_srt_time, parse_srt  # noqa: E402
from make_short import build_timeline, total_duration  # noqa: E402

C = {
 4: ("After, you know,", "Après, tu vois,"),
 5: ("season one of Stand-Up Revolution, we went on", "la saison 1 de Stand-Up Revolution, on est partis"),
 6: ("tour for a while, we went all over the US,", "en tournée un moment, partout aux États-Unis,"),
 7: ("and as a gift to all my buddies that were", "et en cadeau à tous mes potes"),
 8: ("on the tour with me, I gave everybody an", "de la tournée, j'ai offert à chacun un"),
 9: ("iPhone 4S. Yeah.", "iPhone 4S. Ouais."),
 10: ("We're good. Martin was so excited because it", "On est sympas. Martin était trop content parce qu'il"),
 11: ("had this feature, it still has this feature,", "avait cette fonction, il l'a toujours,"),
 12: ("called Siri, where you hit the button and", "qui s'appelle Siri : tu appuies sur le bouton,"),
 13: ("you can talk to the phone and it'll help you", "tu parles au téléphone et il t'aide,"),
 14: ("out. Like, if you say: \"Oh, call John,\"", "genre si tu dis : « Appelle John »,"),
 15: ("it's like, you know, ding ding, \"Calling", "il fait, ding ding, « J'appelle"),
 16: ("John.\" You know, it's really, really,", "John. » C'est vraiment, vraiment,"),
 17: ("really cool. But Martin, you see how he", "vraiment cool. Mais Martin, vous voyez comment il"),
 18: ("is? You know, he messes with the phone.", "est ? Il fait l'idiot avec le téléphone."),
 19: ("He's like: ding ding, \"Siri, tell me", "Il fait : ding ding, « Siri, dis-moi"),
 20: ("something dirty.\"", "un truc cochon. »"),
 21: ("And the phone takes everything literally, so", "Et le téléphone prend tout au pied de la lettre,"),
 22: ("it's like: ding, \"Would you like me to", "alors il répond : ding, « Voulez-vous que je"),
 23: ("locate a car wash?\"", "trouve une station de lavage ? »"),
 29: ("We had a really good time that night", "On a passé une super soirée"),
 30: ("doing the show, and the people invited us", "pendant le spectacle, et les gens nous ont invités"),
 31: ("to hang out, and we had a bunch of drinks.", "à sortir, et on a bu pas mal de verres."),
 37: ("…and I'm walking in, okay, and he's gone.", "…je rentre à l'hôtel, et il est KO."),
 38: ("He is just… ugh. And somebody's helping the", "Il est complètement… Et quelqu'un aide le"),
 39: ("man. I'm like: \"Who are you?\"", "gars. Je fais : « Vous êtes qui ? »"),
 40: ("\"I don't know, but he fell.\"", "« Je sais pas, mais il est tombé. »"),
 42: ("He doesn't even take off his clothes.", "Il n'enlève même pas ses vêtements."),
 43: ("He gets into the bed with everything on,", "Il se couche tout habillé,"),
 44: ("including his shoes.", "chaussures comprises."),
 45: ("So the next morning, you guys,", "Alors le lendemain matin,"),
 46: ("Martin comes over to my side of the room", "Martin vient de mon côté de la chambre"),
 47: ("and he's like:", "et il fait :"),
 48: ("\"Bro…", "« Frérot…"),
 49: ("are you okay?\"", "ça va ? »"),
 50: ("\"Bro, I peed on myself.\"", "« Frérot, je me suis fait pipi dessus. »"),
 51: ("And my response was actually: \"Again?\"", "Et ma réponse a été : « Encore ? »"),
 62: ("He goes: \"Bro, you don't understand.", "Il me fait : « Frérot, tu comprends pas."),
 63: ("My phone was in my pocket.\"", "Mon téléphone était dans ma poche. »"),
 64: ("I go: \"No…\"", "Je fais : « Non… »"),
 65: ("\"Yeah. I drowned Siri.\"", "« Si. J'ai noyé Siri. »"),
 72: ("So we take a nice little trip to the mall,", "Alors on fait un petit tour au centre commercial,"),
 73: ("and we found an Apple Store, and we get to", "on trouve un Apple Store, et à"),
 74: ("the front, there's a girl there with a", "l'entrée, il y a une fille avec un"),
 75: ("clipboard, they're always trying to…", "porte-bloc, elles essaient toujours de…"),
 76: ("\"How can I help you?\"", "« Je peux vous aider ? »"),
 77: ("\"Well, we wanna see about replacing my", "« On voudrait remplacer le téléphone"),
 78: ("friend's phone.\"", "de mon ami. »"),
 79: ("\"Did he lose it?\"", "« Il l'a perdu ? »"),
 80: ("I go: \"No, actually, it got damaged.\"", "Je fais : « Non, il est abîmé. »"),
 81: ("\"Oh, what's wrong with the phone?\"", "« Ah, qu'est-ce qu'il a, le téléphone ? »"),
 82: ("I go: \"It kind of got wet.\"", "Je fais : « Il a un peu pris l'eau. »"),
 83: ("And then she looks at Martin…", "Et là, elle regarde Martin…"),
 84: ("\"Oh, did someone drop it in the sink?\"", "« Oh, quelqu'un l'a fait tomber dans l'évier ? »"),
 85: ("Like: \"No… not exactly.\"", "Genre : « Non… pas exactement. »"),
 86: ("And she's like: \"Oh, he dropped it in the", "Et elle fait : « Oh, il l'a fait tomber dans les"),
 87: ("toilet?\" I go: \"He wishes.\"", "toilettes ? » Je fais : « Il aimerait bien. »"),
 88: ("She goes: \"Well, we have a few in stock.", "Elle dit : « Bon, on en a quelques-uns en stock."),
 89: ("Would you like a black iPhone, or would you", "Vous voulez un iPhone noir ou"),
 90: ("like a white iPhone?\"", "un iPhone blanc ? »"),
 91: ("I said: \"Well, you know, Martin and I have", "J'ai dit : « Martin et moi, on a"),
 92: ("the same color iPhone.\"", "la même couleur d'iPhone. »"),
 93: ("I said: \"We both have a white one.\"", "« On a tous les deux un blanc. »"),
 94: ("So I says:", "Alors je dis :"),
 95: ("\"Just so we don't have the confusion of", "« Pour qu'on arrête de"),
 96: ("always grabbing each other's phones,\" I", "se tromper de téléphone, »"),
 97: ("said, \"Martin, would you mind getting a", "j'ai dit, « Martin, ça te dérange de prendre"),
 98: ("black iPhone?\"", "un iPhone noir ? »"),
 99: ("He goes: \"Yeah, but… does the black iPhone", "Il fait : « Ouais, mais… est-ce que l'iPhone noir"),
 100: ("have Siri?\"", "a Siri ? »"),
 101: ("And I'm like: what kind of a question is", "Et moi : c'est quoi cette question ?"),
 102: ("that? Why wouldn't the black iPhone have", "Pourquoi l'iPhone noir n'aurait pas"),
 103: ("Siri, right?", "Siri, hein ?"),
 104: ("And then I started thinking… can you", "Et puis je me suis mis à penser… vous"),
 105: ("imagine if a black iPhone was really", "imaginez si l'iPhone noir était vraiment"),
 106: ("a BLACK iPhone?", "un iPhone NOIR ?"),
 107: ("You know, Martin gets in the car:", "Martin monte dans la voiture :"),
 108: ("\"Siri, what's the temperature outside?\"", "« Siri, quelle température fait-il dehors ? »"),
 109: ("\"Why don't you stick your head out the", "« T'as qu'à passer la tête par la"),
 110: ("window?\"", "fenêtre ! »"),
 111: ("\"Siri, talk dirty to me.\" \"You better not pee", "« Siri, parle-moi cochon. » « T'as intérêt à pas"),
 112: ("on me.\"", "me faire pipi dessus. »"),
 113: ("Okay… I like that white iPhone.", "Bon… je préfère l'iPhone blanc."),
}
RANGES = [(4, 23), (29, 31), (37, 51), (62, 65), (72, 113)]

cues = parse_srt("subs.srt")
fr, en = [], []
for i, c in enumerate(cues, 1):
    if i not in C:
        continue
    t = f"{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}"
    en.append(f"{len(en) + 1}\n{t}\n{C[i][0]}")
    fr.append(f"{len(fr) + 1}\n{t}\n{C[i][1]}")
Path("subs.fixed.srt").write_text("\n\n".join(en) + "\n", encoding="utf-8")
Path("subs.fr.srt").write_text("\n\n".join(fr) + "\n", encoding="utf-8")

segs = []
for a, b in RANGES:
    s0, e0 = cues[a - 1]["start"] - 0.25, cues[b - 1]["end"] + (1.4 if b in (23, 51, 65, 87, 113) else 0.2)
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
        if t == tok:
            k += 1
            if k == nth:
                return words[i]["start"], words[i]["end"]
    raise SystemExit(f"not found {tok}")


def freeze_after(src, dur):
    for s in segs:
        if s["in"] <= src <= s["out"]:
            s["freeze"] = dur


_, wash = find("wash")
_, again = find("again")
_, drowned = find("drowned")
q_s, _ = find("does", 1)
_, window = find("window")
_, peeme = find("me", sum(1 for t in toks[:len(toks) - 3] if t == "me"))
freeze_after(window, 0.7)
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
    "framing": {"mode": "blur_fill", "raise_px": 140, "pre_crop": {"x0": 0.12, "x1": 0.88, "y0": 0.0, "y1": 0.76}},
    "subtitles": "subs.fixed.srt",
    "translation": {"file": "subs.fr.srt", "language": "fr"},
    "highlight_words": ["Siri", "car wash", "shoes", "peed", "Again", "drowned", "toilet", "black iPhone", "window", "pee"],
    "zooms": [{"at": ot(drowned) - 0.9, "dur": 2.0, "scale": 1.12}, {"at": ot(window) - 1.3, "dur": 2.6, "scale": 1.18}],
    "editorial_captions": [
        {"text": "N'offrez jamais un iPhone à ce pote", "start": 0.0, "end": 3.2},
        {"text": "Siri n'a rien demandé", "start": ot(drowned) + 0.3, "end": ot(drowned) + 2.8}],
    "overlays": [
        {"file": f"{A}/stickers/shock/wait_what.png", "start": ot(q_s), "end": ot(q_s) + 1.6, "position": "lower_right", "width": 460},
        {"file": f"{A}/stickers/embarrassment/oof.png", "start": ot(again) + 0.1, "end": ot(again) + 1.4, "position": "upper_center", "width": 420}],
    "sfx": [
        {"file": f"{A}/sfx/pop.wav", "at": ot(wash) + 0.05, "gain_db": -12},
        {"file": f"{A}/sfx/record_scratch.wav", "at": ot(again) + 0.05, "gain_db": -12},
        {"file": f"{A}/sfx/dramatic_sting.wav", "at": ot(drowned) + 0.05, "gain_db": -16},
        {"file": f"{A}/sfx/impact.wav", "at": ot(window) + 0.05, "gain_db": -9}],
})
for z in spec["zooms"]:
    z["at"] = round(z["at"], 2)
json.dump(spec, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(en)} cues; {len(segs)} segments; duration {dur:.1f}s; window@{ot(window)}")
