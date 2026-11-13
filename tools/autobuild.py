#!/usr/bin/env python3
"""Generic short builder: config.json (in the clip dir) -> subs.fixed.srt + translation SRT + edit.json.

config.json:
{
  "trans_lang": "en",                       # language of the translation track
  "cues": {"37": ["FR text", "EN text"], ...},   # transcript cue number -> [original, translation]; "" original drops it
  "ranges": [[37, 98]],                     # cue ranges kept (in order)
  "end_pad": 1.2,                           # seconds of laughter kept after each range
  "highlight_words": [...],
  "hook": "editorial caption shown 0-3.2s",
  "effects": [                              # anchored on transcript words (prefix match, nth occurrence)
     {"type": "zoom", "word": "merdologue", "nth": 1, "offset": -0.8, "dur": 2.2, "scale": 1.15},
     {"type": "sfx", "word": "...", "file": "impact", "gain": -10, "offset": 0.05},
     {"type": "sticker", "word": "...", "file": "confusion/huh", "pos": "upper_center", "width": 460, "dur": 1.4},
     {"type": "caption", "word": "...", "text": "...", "dur": 2.6},
     {"type": "freeze", "word": "...", "dur": 0.6}
  ],
  "publishing": {...}                       # merged into edit.json
}
Run from the clip directory: python3 ../../../../tools/autobuild.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from common import fmt_srt_time, parse_srt  # noqa: E402
from make_short import build_timeline, total_duration  # noqa: E402

A = "../../../../assets"
cfg = json.load(open("config.json", encoding="utf-8"))
cues = parse_srt("subs.srt")
C = {int(k): v for k, v in cfg["cues"].items()}
tl_lang = cfg.get("trans_lang", "en")

orig, trans = [], []
for i, c in enumerate(cues, 1):
    if i in C and C[i][0]:
        t = f"{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}"
        orig.append(f"{len(orig) + 1}\n{t}\n{C[i][0]}")
        trans.append(f"{len(trans) + 1}\n{t}\n{C[i][1]}")
Path("subs.fixed.srt").write_text("\n\n".join(orig) + "\n", encoding="utf-8")
Path(f"subs.{tl_lang}.srt").write_text("\n\n".join(trans) + "\n", encoding="utf-8")

segs = []
pad = float(cfg.get("end_pad", 1.2))
for a, b in cfg["ranges"]:
    s0, e0 = cues[a - 1]["start"] - 0.25, cues[b - 1]["end"] + pad
    out = subprocess.run(["python3", str(TOOLS / "tighten.py"), "words.json", "--start", f"{s0:.2f}", "--end", f"{e0:.2f}",
                          "--max-gap", "1.8", "--keep", "1.6", "--lead", "0.25"], capture_output=True, text=True, check=True)
    part = json.loads(out.stdout.splitlines()[0])
    part[-1]["out"] = round(e0, 3)
    segs += part

words = json.load(open("words.json", encoding="utf-8"))
toks = [re.sub(r"[^\w'-]", "", w["word"].lower()) for w in words]
kept = lambda t: any(s["in"] <= t <= s["out"] for s in segs)  # noqa: E731


def find(word, nth=1):
    word, k = word.lower(), 0
    for i, t in enumerate(toks):
        if t.startswith(word) and kept(words[i]["start"]):
            k += 1
            if k == nth:
                return words[i]["start"], words[i]["end"]
    raise SystemExit(f"word not found in kept ranges: {word} #{nth}")


for e in cfg.get("effects", []):
    if e["type"] == "freeze":
        _, end = find(e["word"], e.get("nth", 1))
        for s in segs:
            if s["in"] <= end <= s["out"]:
                s["freeze"] = e.get("dur", 0.6)
tl = build_timeline(segs)
dur = total_duration(tl)


def ot(src):
    for s in tl:
        if s["src_in"] <= src <= s["src_out"]:
            return round(s["out_start"] + src - s["src_in"], 2)
    return round(next(s["out_start"] for s in tl if s["src_in"] > src), 2)


zooms, sfx, overlays, captions = [], [], [], []
if cfg.get("hook"):
    captions.append({"text": cfg["hook"], "start": 0.0, "end": 3.2})
for e in cfg.get("effects", []):
    if e["type"] == "freeze":
        continue
    s, end = find(e["word"], e.get("nth", 1))
    at = ot(end) + e.get("offset", 0.05)
    if e["type"] == "zoom":
        zooms.append({"at": round(ot(s) + e.get("offset", -0.6), 2), "dur": e.get("dur", 2.2), "scale": e.get("scale", 1.15)})
    elif e["type"] == "sfx":
        sfx.append({"file": f"{A}/sfx/{e['file']}.wav", "at": round(at, 2), "gain_db": e.get("gain", -11)})
    elif e["type"] == "sticker":
        overlays.append({"file": f"{A}/stickers/{e['file']}.png", "start": round(at, 2), "end": round(at + e.get("dur", 1.4), 2),
                         "position": e.get("pos", "upper_center"), "width": e.get("width", 460)})
    elif e["type"] == "caption":
        captions.append({"text": e["text"], "start": round(at, 2), "end": round(min(dur, at + e.get("dur", 2.6)), 2)})

spec = json.load(open("edit.json", encoding="utf-8"))
spec.update({"segments": segs, "subtitles": "subs.fixed.srt", "translation": {"file": f"subs.{tl_lang}.srt", "language": tl_lang},
             "highlight_words": cfg.get("highlight_words", []), "zooms": zooms, "sfx": sfx, "overlays": overlays,
             "editorial_captions": captions})
if cfg.get("publishing"):
    spec["publishing"] = cfg["publishing"]
if cfg.get("context_note"):
    spec["context_note"] = cfg["context_note"]
json.dump(spec, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(orig)} cues; {len(segs)} segments; duration {dur:.1f}s")
