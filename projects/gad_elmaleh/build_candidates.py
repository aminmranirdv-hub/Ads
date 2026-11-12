#!/usr/bin/env python3
"""Source of truth for candidates.json (Gad Elmaleh, discovery round 1).

Every URL below was found on the rights holder's own YouTube channel, and
every timestamp/quote comes from that video's transcript (pulled 2026-11-12).
Timestamps are caption-block starts: refine by +/-3s on the actual footage.
Run: python3 build_candidates.py
"""
import json
from pathlib import Path

M = "Montreux Comedy (official festival channel)"
C = "The Late Show with Stephen Colbert (CBS official channel)"
Q = "ComediHa! (official festival channel)"
P = "La Relève Montreux Comedy (official secondary channel)"
MU, MT = "https://www.youtube.com/watch?v=kal9aFfyWOs", "Gad Elmaleh – Les petits mensonges du quotidien (Montreux Comedy Festival 2023)"
CU, CT = "https://www.youtube.com/watch?v=jLOKSJq4tRA", "Gad Elmaleh Performs Stand-up (The Late Show with Stephen Colbert, Dec 2016)"
QU, QT = "https://www.youtube.com/watch?v=Dyy-KRkdE2c", "Gad Elmaleh - Gala ComediHa! (Québec, 2018)"
PU, PT = "https://www.youtube.com/watch?v=OR-1TUobxk8", "Paul Mirabel & Gad Elmaleh – Conseils d'ami (Montreux Comedy Festival 2021)"
KEYS = ["attention", "comedy", "relatability", "surprise", "meme", "shortform"]


def c(i, src, url, title, tin, tout, cat, ctx, punch, why, meme, dur, sc, lang, note=""):
    return {
        "id": i, "comedian": "Gad Elmaleh", "language": lang,
        "source": {"title": title, "url": url, "channel": src, "official": True,
                   "timestamp_in": tin, "timestamp_out": tout,
                   "timestamp_precision": "caption-block start from the transcript; refine +/-3s on footage"},
        "category": cat, "context": ctx, "punchline": punch, "why_funny": why, "meme_idea": meme,
        "recommended_duration": dur, "context_preserved": True,
        "rights": {"status": "unknown",
                   "notes": ("Uploaded by the rights holder's channel. Publicly viewable does not mean reusable: "
                             "request a licence. " + note).strip()},
        "scores": dict(zip(KEYS, sc)),
    }


CANDS = [
    c("gad_lavie", M, MU, MT, "3:37", "4:28", "social media / dating at 50",
      "He's 50, scrolls Instagram, and sees half-naked girls quoting philosophers. One poses next to a private jet with a Vuitton bag and writes « Merci, la vie. »",
      "« La vie… C'est la vie qui a payé tout ça, oui ! Jean-Jacques Lavie, 78 ans. »",
      "Wordplay misdirection: 'la vie' (life) turns into a sugar daddy's surname, and the specific age makes the picture land. The tag (he can't even move on the plane) extends it.",
      "Mock Instagram post (original graphic) for « Merci, la vie. »; freeze + impact on « Jean-Jacques Lavie »; editorial caption « Merci qui ? »",
      "35-60s", [17, 23, 13, 14, 14, 8], "fr"),
    c("gad_naaan", M, MU, MT, "0:52", "2:00", "celebrity encounter / texting",
      "On a train, the woman next to him texts « Devine à côté de qui je suis assise : Gad Elmaleh » (misspelled) and her friend replies « Naaaan ! ». He reads it all over her shoulder.",
      "Ten minutes later: « Oh, mais vous n'êtes pas… ? » — « T'es sérieuse ? J'ai les preuves. J'ai le ‹ Naaaan › ! »",
      "Dramatic irony: the audience saw the texts with him, so her fake 'aren't you…?' is a lie we can prove. Plus the act-out of 'Naaaan'.",
      "Animated chat bubbles recreating the texts he quotes (original graphic); 'WAIT… WHAT?!' sticker on her question.",
      "35-60s", [17, 22, 13, 13, 15, 7], "fr"),
    c("gad_askip", M, MU, MT, "4:28", "5:00", "generation gap / dating",
      "Dating much younger women: at a restaurant he asks if she likes it, and she answers « J'avoue. »",
      "« J'ai attendu qu'elle avoue un truc toute la soirée… ‹ Askip ›, je vois de la lessive. Arrête ! »",
      "A 50-year-old taking youth slang literally ('j'avoue' = I confess; 'askip' sounds like a detergent ad). Two quick hits, very shareable across generations.",
      "Slang 'dictionary card' overlay (j'avoue = carrément, askip = à ce qu'il paraît); boing on « lessive ».",
      "20-35s", [16, 21, 15, 12, 13, 10], "fr"),
    c("gad_marie", M, MU, MT, "5:00", "5:40", "flirting / reversal",
      "In Morocco, a woman comes up to him at the hotel: « Gad, dommage que vous soyez marié. » He says: « Ben moi, je ne suis pas marié. »",
      "« Elle me dit : ‹ Ah ! Moi oui. › »",
      "A clean three-line reversal; the pause before « Moi oui » is the joke. An ideal 15–20s one-liner.",
      "Crickets SFX + 'AWKWARD.' sticker after the reveal; caption « Elle avait un plan ».",
      "15-20s", [15, 21, 12, 16, 11, 10], "fr"),
    c("gad_laisse", M, MU, MT, "2:30", "3:19", "observational / parenting",
      "In Paris, a man walks his child on a retractable leash. 200 m later, another man is pushing a stroller with a dog inside.",
      "« J'ai craqué. Je lui ai dit : ‹ Monsieur, il y a un monsieur là-bas avec son fils. Il faut parler. › »",
      "Escalation into a role swap (child as dog, dog as child) and an absurd matchmaking solution; strong act-out of the leash.",
      "Split-screen icons child/dog; record scratch on the stroller reveal.",
      "35-60s", [16, 19, 13, 14, 14, 8], "fr"),
    c("gad_tattoo", M, MU, MT, "7:37", "8:15", "self-deprecation / regional",
      "He wants Sophie Marceau's name tattooed. The advice he gets: do your first tattoo somewhere you don't care about.",
      "« Du coup, je vais le faire… à Annemasse. »",
      "The body-part expectation flips into a place name. It lands hardest with a Swiss/Geneva audience (Annemasse is a French border town), and it needs the Marceau setup.",
      "Map-pin graphic on Annemasse for viewers who aren't local.",
      "20-35s", [14, 19, 8, 14, 9, 9], "fr",
      "Regional reference: needs an on-screen explainer outside Switzerland/eastern France."),
    c("gad_down", C, CU, CT, "4:23", "5:26", "dating / language barrier",
      "Single in New York, texting American girls. She says 'I'm down', and he thinks she's depressed. Then 'I'm in'.",
      "« She said ‹ would be dope ›… my American friend said: it means she's too young. »",
      "A non-native taking slang literally, then a twist where the explanation itself is the punchline (the age gap).",
      "Text-message bubbles; 'RED FLAG' sticker on the final line; EN original + FR / Darija subtitle editions.",
      "35-60s", [17, 22, 14, 14, 14, 8], "en"),
    c("gad_encore", C, CU, CT, "3:16", "4:23", "culture clash / show business",
      "He explains the encore ritual: everyone pretends. The comedian hides, and the crowd pretends to want him back.",
      "« Finished my show, walked off the stage. I came back, they were gone. »",
      "A long build on mutual hypocrisy pays off with a four-word picture of an empty room. A great freeze-frame point.",
      "Freeze on his face + crickets; caption 'New York doesn't do encores'.",
      "35-60s", [15, 22, 11, 15, 13, 7], "en"),
    c("gad_jfk", C, CU, CT, "0:32", "2:21", "accent / immigrant life",
      "A NYC cab driver can't understand 'JFK' in his accent; the 'meet me halfway' riff; the driver keeps correcting him.",
      "« Sir, we are both immigrants… you maybe got the J right, but you said ‹ airpoot ›. Touché. »",
      "A relatable accent struggle with a status reversal at the end. Long (~110s), so it needs tightening without cutting the KFC / iPhone-tower builds.",
      "Captions showing the mispronunciations and corrections; highlight 'touché'.",
      "35-60s", [15, 19, 14, 11, 12, 5], "en",
      "Accent humour about another immigrant: keep the full 'we are both immigrants' framing; never cut it down to the accent alone."),
    c("gad_essence", Q, QU, QT, "0:47", "1:53", "observational / everyday obsession",
      "'We're all the same': at the gas station, you absolutely have to round off the amount on the pump.",
      "Tiny trigger taps, overshooting to 20,02, then going all the way to the next round number (auto-captions garbled; transcribe from the audio).",
      "A universal micro-obsession plus a physical act-out of the pump nozzle; suspense built out of numbers.",
      "Digital pump-counter overlay synced to his numbers; tension_tick + impact on the overshoot.",
      "35-60s", [18, 20, 15, 11, 14, 8], "fr",
      "Auto-captions are garbled: transcribe the punchline wording from the audio before the score is final."),
    c("gad_bruits", Q, QU, QT, "3:01", "3:48", "couples / gender",
      "The 'féminin ou masculin ?' game with the audience: hearing noises at night.",
      "« Il y a aucun homme au monde qui a déjà dit à sa femme à 4 heures du matin : ‹ Chérie, je crois qu'il y a des gens dans la salle de bain. › »",
      "The interactive format ('feminine or masculine?') invites comments and gets couples tagging each other.",
      "Poll-style caption « Féminin ou masculin ? », with the answer revealed on his line.",
      "20-35s", [16, 19, 15, 11, 13, 9], "fr",
      "Wording from auto-captions; verify on the audio."),
    c("gad_petition", Q, QU, QT, "5:09", "6:14", "provocation / misunderstanding",
      "He says he doesn't like animals, and a woman in Montreal got angry. That afternoon in Québec, a girl with a petition asks: « Avez-vous deux minutes pour la défense des animaux ? »",
      "« J'ai dit : ouais, ils sont où ? »",
      "He hears 'defending against animals' and gets ready to fight. Short and sharp once it's set up.",
      "Freeze + 'HUH?' sticker; caption « Il a mal compris… ou pas ».",
      "20-35s", [15, 20, 11, 14, 12, 8], "fr",
      "Wording from garbled auto-captions; verify on the audio."),
    c("gad_protestants", P, PU, PT, "5:43", "6:20", "religion / wordplay",
      "Duo set with Paul Mirabel; a riff on Switzerland as protestant land.",
      "« Les protestants, c'est des catholiques qui se sont mis à leur compte… et ont fait un vrai succès en tant qu'auto-entrepreneurs. »",
      "Business framing of a religious schism. Sharp, but it needs the duo context and it's religion-adjacent.",
      "Keep it minimal: caption « Cours d'histoire express ».",
      "20-35s", [13, 20, 8, 14, 9, 8], "fr",
      "Religion topic: high context sensitivity; the duo dynamic with Paul Mirabel needs explaining. A second performer's rights are also involved."),
]

out = Path(__file__).with_name("candidates.json")
out.write_text(json.dumps({"project": "Gad Elmaleh – discovery round 1 (official / rights-holder uploads only)",
                           "candidates": CANDS}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out} ({len(CANDS)} candidates)")
