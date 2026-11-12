#!/usr/bin/env python3
"""Build edit.json for the 3-minute test: tightened segments + effects timed on punchline words."""
import json
import subprocess
import sys

sys.path.insert(0, "../../tools")
from make_short import build_timeline, total_duration  # noqa: E402

segs = json.loads(subprocess.run(["python3", "../../tools/tighten.py", "words.json", "--max-gap", "0.55", "--keep", "0.32"],
                                 capture_output=True, text=True, check=True).stdout.splitlines()[0])
words = json.load(open("words.json", encoding="utf-8"))
toks = [w["word"].lower().strip(".,!?«»:") for w in words]


def find(seq, nth=1):
    """(start, end) source time of the nth occurrence of a token sequence."""
    seq, k = [s.lower() for s in seq], 0
    for i in range(len(toks)):
        if toks[i:i + len(seq)] == seq:
            k += 1
            if k == nth:
                return words[i]["start"], words[i + len(seq) - 1]["end"]
    raise SystemExit(f"not found: {seq}")


def freeze_after(src_end, dur):
    for s in segs:
        if s["in"] <= src_end <= s["out"]:
            s["freeze"] = dur
            return


_, chat = find(["est", "mort"])
_, pouce3 = find(["pousse"], 3)
_, mere = find(["je", "suis", "ta", "mère"])
_, bruit = find(["faire", "du", "bruit"])
_, transf = find(["transformé"])
_, appeler = find(["'appeler"])
_, coince = find(["coincée"])
freeze_after(pouce3, 0.7)
freeze_after(mere, 0.8)
tl = build_timeline(segs)
dur = total_duration(tl)


def out_t(src):
    for s in tl:
        span = s["src_out"] - s["src_in"]
        if s["src_in"] <= src <= s["src_out"]:
            return round(s["out_start"] + src - s["src_in"], 2)
        if s["src_out"] < src and src - s["src_out"] < 0.05:
            return round(s["out_start"] + span, 2)
    return round(next(s["out_start"] for s in tl if s["src_in"] > src), 2)


S = "../../assets"
spec = {
    "id": "test_3min_groupe_whatsapp",
    "comedian": "PUNCHLINE LAB (original test bit, synthetic voice)",
    "language": "fr",
    "source": {"file": "source.mp4", "title": "Le groupe WhatsApp familial (original, written by the channel)",
               "url": "local://projects/_test_3min/source.mp4"},
    "rights": {"status": "owned", "evidence": "Script written by the channel; voice: Piper fr_FR-tom-medium (open source); visuals generated locally."},
    "context_note": "Full original bit; dead air trimmed with tools/tighten.py; freezes after the two biggest punchlines.",
    "segments": segs,
    "framing": {"mode": "blur_fill", "raise_px": 120},
    "subtitles": "subs.srt", "subtitles_timing": "source",
    "translation": {"file": "subs.en.srt", "language": "en"},
    "highlight_words": ["WhatsApp", "unie", "47", "paillettes", "bruit", "urgent", "huit minutes", "pouce", "mort",
                        "coincé", "mangé", "transformé", "silencieux", "ta mère", "wifi"],
    "zooms": [{"at": out_t(chat), "dur": 2.4, "scale": 1.18},
              {"at": round(out_t(mere) - 1.2, 2), "dur": 2.6, "scale": 1.15}],
    "editorial_captions": [
        {"text": "POV : le groupe WhatsApp de ta famille", "start": 0.0, "end": 3.2},
        {"text": "Papa a réagi : pouce", "start": out_t(pouce3), "end": round(out_t(pouce3) + 2.6, 2)},
        {"text": "Les mamans ont le wifi intégré", "start": round(out_t(mere) + 0.2, 2), "end": round(min(dur, out_t(mere) + 3.2), 2)}],
    "overlays": [
        {"file": f"{S}/stickers/awkward_silence/silence.png", "start": out_t(pouce3), "end": round(out_t(pouce3) + 1.4, 2), "position": "lower_right", "width": 360},
        {"file": f"{S}/stickers/family/every_mom.png", "start": round(out_t(mere) + 0.1, 2), "end": round(out_t(mere) + 1.6, 2), "position": "upper_center", "width": 560},
        {"file": f"{S}/stickers/dramatic_realization/plot_twist.png", "start": round(out_t(transf) + 0.1, 2), "end": round(out_t(transf) + 1.5, 2), "position": "upper_center", "width": 520}],
    "sfx": [
        {"file": f"{S}/sfx/pop.wav", "at": round(out_t(bruit) + 0.05, 2), "gain_db": -12},
        {"file": f"{S}/sfx/boing.wav", "at": round(out_t(appeler) + 0.1, 2), "gain_db": -12},
        {"file": f"{S}/sfx/crickets.wav", "at": round(out_t(pouce3) + 0.05, 2), "gain_db": -14},
        {"file": f"{S}/sfx/record_scratch.wav", "at": round(out_t(coince) + 0.05, 2), "gain_db": -12},
        {"file": f"{S}/sfx/dramatic_sting.wav", "at": round(out_t(transf) + 0.05, 2), "gain_db": -16},
        {"file": f"{S}/sfx/impact.wav", "at": round(out_t(mere) + 0.05, 2), "gain_db": -9}],
    "publishing": {
        "hooks": ["Le groupe WhatsApp familial a détruit ma famille", "Mon père répond à TOUT avec un pouce",
                  "Attends de voir comment elle a su…"],
        "tiktok_caption": "Le groupe « Famille unie » 😭 Tague celui qui envoie des roses qui tournent 🌹 #humour #whatsapp #famille",
        "youtube_title": "Le groupe WhatsApp familial 😂 (English subtitles)",
        "youtube_description": "Original stand-up bit by PUNCHLINE LAB (pipeline test, synthetic voice). English subtitles: translation by the channel.",
        "hashtags": ["#humour", "#standup", "#whatsapp", "#famille", "#shorts"]},
}
json.dump(spec, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"duration {dur:.1f}s, {len(segs)} segments; cat-died {out_t(chat)}s, 3rd thumbs-up {out_t(pouce3)}s, 'je suis ta mère' {out_t(mere)}s")
