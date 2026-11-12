#!/usr/bin/env python3
"""Quality control for a rendered short.

Automated checks: resolution, fps, codecs, duration, loudness, true peak,
rights status and context note in the spec.
Manual checks: printed as a checklist the editor must tick before export.

Usage: python3 tools/qc.py projects/<clip>/edit.json projects/<clip>/export/<clip>.mp4
Exit code 1 if any automated check FAILS.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

from common import APPROVED_RIGHTS, USER_ASSUMED_RIGHTS, OUT_FPS, OUT_H, OUT_W, ffprobe, load_json

MANUAL = [
    "The joke is understandable without the surrounding set",
    "Original context is preserved; no cut changes what the comedian meant",
    "The punchline lands - no SFX or caption steps on it",
    "Subtitles match the audio word for word (spelling, names, timing)",
    "Translated subtitles are labelled as translation/adaptation where meaning was adapted",
    "Editorial captions are clearly the channel's commentary, never attributed to the comedian",
    "Meme overlays support the joke and don't cover faces",
    "All text sits inside the mobile safe zones",
    "Every asset (footage, stickers, SFX, music) has a recorded licence",
    "No comedian name/likeness is used in a way that implies endorsement",
]


def loudness(path: str) -> tuple[float | None, float | None]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    p = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary)
    return (float(i.group(1)) if i else None, float(p.group(1)) if p else None)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("video")
    args = ap.parse_args()
    spec = load_json(args.spec)
    info = ffprobe(args.video)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    results = []

    def check(name, ok, detail, warn=False):
        results.append(("PASS" if ok else ("WARN" if warn else "FAIL"), name, detail))

    check("video stream", v is not None, v["codec_name"] if v else "missing")
    if v:
        check("resolution 1080x1920", (v["width"], v["height"]) == (OUT_W, OUT_H), f"{v['width']}x{v['height']}")
        num, den = map(int, v["r_frame_rate"].split("/"))
        check(f"frame rate {OUT_FPS}", abs(num / den - OUT_FPS) < 0.5, f"{num / den:.2f}")
        check("H.264 / yuv420p", v["codec_name"] == "h264" and v.get("pix_fmt") == "yuv420p",
              f"{v['codec_name']} {v.get('pix_fmt')}")
    check("audio stream AAC", a is not None and a["codec_name"] == "aac", a["codec_name"] if a else "missing")
    check("duration <= 180s", dur <= 180.5, f"{dur:.2f}s")
    check("duration >= 10s", dur >= 10, f"{dur:.2f}s", warn=True)
    lufs, peak = loudness(args.video)
    check("loudness -14 LUFS (+/-2)", lufs is not None and abs(lufs + 14) <= 2, f"{lufs} LUFS", warn=True)
    check("true peak <= -1 dBFS", peak is not None and peak <= -0.9, f"{peak} dBFS", warn=True)
    st = spec.get("rights", {}).get("status", "unknown")
    if st in USER_ASSUMED_RIGHTS:
        check("rights", False, "user_assumed: no licence; copyright claims/strikes possible", warn=True)
    else:
        check("rights approved for publication", st in APPROVED_RIGHTS, st)
    check("context note present", bool(spec.get("context_note", "").strip()), "context_note")
    check("source reference present", bool(spec.get("source", {}).get("url", "").strip()), spec.get("source", {}).get("url", ""))

    width = max(len(r[1]) for r in results)
    print(f"QC report: {args.video}\n")
    for status, name, detail in results:
        print(f"  [{status}] {name.ljust(width)}  {detail}")
    print("\nManual checklist (editor must confirm):")
    for m in MANUAL:
        print(f"  [ ] {m}")
    fails = [r for r in results if r[0] == "FAIL"]
    print(f"\n{'FAILED' if fails else 'PASSED'}: {len(fails)} fail(s), {sum(r[0] == 'WARN' for r in results)} warning(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
