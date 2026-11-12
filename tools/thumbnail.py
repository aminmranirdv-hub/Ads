#!/usr/bin/env python3
"""Build a 1080x1920 cover/thumbnail from a frame of the rendered short.

Usage: python3 tools/thumbnail.py <video> --at 7.4 --text "HE SAID WHAT?!" [--out cover.jpg]

Pass the CLEAN source footage (time = source time) so burned-in captions
don't end up under the thumbnail text; non-vertical frames are blur-filled.
Pick a frame with a strong facial expression. The text is the channel's
hook, not a quote, unless it is the comedian's exact words.
Requires Pillow.
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import OUT_H, OUT_W, load_brand, require_ffmpeg, run
from make_short import framing_filter


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--at", type=float, required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--out")
    ap.add_argument("--spec", help="edit.json: reuse its framing.pre_crop (e.g. to drop burned-in captions)")
    args = ap.parse_args()
    require_ffmpeg()
    brand = load_brand()
    pre = {}
    if args.spec:
        import json
        pc = json.load(open(args.spec, encoding="utf-8")).get("framing", {}).get("pre_crop")
        pre = {"pre_crop": pc} if pc else {}
    out = Path(args.out) if args.out else Path(args.video).with_suffix(".thumb.jpg")
    with tempfile.TemporaryDirectory() as td:
        frame = Path(td) / "f.png"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(args.at), "-i", args.video,
             "-frames:v", "1", "-filter_complex",
             f"[0:v]{framing_filter({'framing': {'mode': 'blur_fill', 'raise_px': 0, **pre}})}[o]", "-map", "[o]",
             str(frame)])
        img = Image.open(frame).convert("RGB")
    # darken the top for legibility
    grad = Image.new("L", (1, OUT_H))
    for y in range(OUT_H):
        grad.putpixel((0, y), int(170 * max(0, 1 - y / (OUT_H * 0.55))))
    shade = Image.new("RGB", (OUT_W, OUT_H), (0, 0, 0))
    img = Image.composite(shade, img, grad.resize((OUT_W, OUT_H)))
    d = ImageDraw.Draw(img)
    font_file = subprocess.run(["fc-match", brand["fonts"]["default"], "-f", "%{file}"],
                               capture_output=True, text=True).stdout.strip()
    font = ImageFont.truetype(font_file, 138)
    lines = textwrap.wrap(args.text.upper(), width=11)
    y = 330
    for i, line in enumerate(lines):
        color = brand["colors"]["highlight"] if i == len(lines) - 1 else brand["colors"]["text"]
        w = d.textlength(line, font=font)
        d.text(((OUT_W - w) / 2, y), line, font=font, fill=color, stroke_width=10, stroke_fill="#000000")
        y += 160
    d.rectangle([0, OUT_H - 24, OUT_W, OUT_H], fill=brand["colors"]["accent"])
    img.save(out, quality=92)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
