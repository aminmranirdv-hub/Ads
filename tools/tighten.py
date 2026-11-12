#!/usr/bin/env python3
"""Build jump-cut segments from words.json by shortening dead air.

Any silence longer than --max-gap between words is cut down to --keep
seconds (split evenly around the cut). Comedic pauses longer than
--protect are kept untouched, because the pause before a punchline is part of
the joke. Prints a JSON segments list for edit.json.

Usage: python3 tools/tighten.py words.json [--start 0 --end 999] [--max-gap 0.6 --keep 0.3 --protect 99]
"""
from __future__ import annotations

import argparse
import json

from common import parse_time


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("words")
    ap.add_argument("--start", default="0")
    ap.add_argument("--end", default="99999")
    ap.add_argument("--max-gap", type=float, default=0.6)
    ap.add_argument("--keep", type=float, default=0.3)
    ap.add_argument("--protect", type=float, default=99.0, help="gaps at least this long are comedic beats: never cut")
    ap.add_argument("--lead", type=float, default=0.15, help="padding before first / after last word")
    args = ap.parse_args()
    s0, e0 = parse_time(args.start), parse_time(args.end)
    words = [w for w in json.load(open(args.words, encoding="utf-8")) if w["start"] >= s0 and w["end"] <= e0]
    if not words:
        raise SystemExit("no words in range")
    segs, cur_in = [], max(0.0, words[0]["start"] - args.lead)
    for a, b in zip(words, words[1:]):
        gap = b["start"] - a["end"]
        if args.max_gap < gap < args.protect:
            half = args.keep / 2
            segs.append({"in": round(cur_in, 3), "out": round(a["end"] + half, 3)})
            cur_in = b["start"] - half
    segs.append({"in": round(cur_in, 3), "out": round(words[-1]["end"] + args.lead, 3)})
    total = sum(s["out"] - s["in"] for s in segs)
    print(json.dumps(segs))
    print(f"# {len(segs)} segments, {total:.1f}s (from {words[-1]['end'] - words[0]['start']:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
