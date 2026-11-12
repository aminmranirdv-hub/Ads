#!/usr/bin/env python3
"""Transcribe footage into a source-timed, short-form-ready SRT (word-level timing).

Uses faster-whisper locally (pip install faster-whisper). Audio is decoded by
ffmpeg, so no PyAV is needed.

Usage:
  python3 tools/transcribe.py <footage> --lang fr [--start 3:19 --end 5:05] [--out subs.srt] [--model small]

  --lang  fr | en | ar   (Darija: use ar, then have a Darija speaker review it.
                          Whisper has no Darija model, so expect errors.)

Outputs subs.srt (cues of 1-2 short lines, <= ~3.2s, split at pauses) and
words.json (every word with start/end/probability), both timed against the
ORIGINAL footage, which is what make_short.py expects.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from common import fmt_srt_time, parse_time, require_ffmpeg

MAX_CHARS = 42      # per cue (rendered as up to 2 lines)
MAX_DUR = 3.2       # seconds per cue
GAP_SPLIT = 0.45    # a pause this long starts a new cue


def load_audio(path: str, start: float | None, end: float | None):
    import numpy as np
    cmd = ["ffmpeg", "-loglevel", "error"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}"]
    if end is not None:
        cmd += ["-to", f"{end:.3f}"]
    cmd += ["-i", path, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def group(words: list[dict]) -> list[dict]:
    cues, cur = [], []
    for w in words:
        if cur:
            text = " ".join(x["word"] for x in cur + [w])
            pause = w["start"] - cur[-1]["end"]
            ends_sentence = cur[-1]["word"].endswith((".", "?", "!", "…"))
            if (len(text) > MAX_CHARS or w["end"] - cur[0]["start"] > MAX_DUR or pause > GAP_SPLIT
                    or (ends_sentence and len(" ".join(x["word"] for x in cur)) > 12)):
                cues.append(cur)
                cur = []
        cur.append(w)
    if cur:
        cues.append(cur)
    out = []
    for c in cues:
        out.append({"start": c[0]["start"], "end": c[-1]["end"] + 0.15,
                    "text": " ".join(x["word"] for x in c).replace(" ,", ",").strip()})
    for a, b in zip(out, out[1:]):  # never overlap
        a["end"] = min(a["end"], b["start"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("footage")
    ap.add_argument("--lang", required=True)
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--out")
    ap.add_argument("--model", default="small", help="tiny|base|small|medium|large-v3 (bigger = better, slower)")
    args = ap.parse_args()
    require_ffmpeg()
    from faster_whisper import WhisperModel

    start = parse_time(args.start) if args.start else None
    end = parse_time(args.end) if args.end else None
    offset = start or 0.0
    audio = load_audio(args.footage, start, end)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio, language=args.lang, word_timestamps=True, vad_filter=True,
                                      condition_on_previous_text=False)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"word": w.word.strip(), "start": round(w.start + offset, 3),
                          "end": round(w.end + offset, 3), "p": round(w.probability, 3)})
    out = Path(args.out) if args.out else Path(args.footage).with_name("subs.srt")
    cues = group([w for w in words if w["word"]])
    out.write_text("\n".join(f"{i}\n{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}\n{c['text']}\n"
                             for i, c in enumerate(cues, 1)), encoding="utf-8")
    out.with_name("words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    low = [w for w in words if w["p"] < 0.5]
    print(f"wrote {out}: {len(cues)} cues, {len(words)} words ({len(low)} low-confidence words to check)")


if __name__ == "__main__":
    main()
