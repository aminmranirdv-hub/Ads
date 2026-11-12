#!/usr/bin/env python3
"""Generate the channel's ORIGINAL reaction-sticker library (transparent PNGs).

Stickers are text badges in the channel's colours, organised by emotion
category. They are original designs, so they are safe to reuse on every
clip. Add new lines to LIBRARY and re-run.

Usage: python3 tools/generate_stickers.py [--out assets/stickers]
Requires Pillow.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import REPO, load_brand

# category -> list of (slug, text, language)
LIBRARY = {
    "confusion": [("huh", "HUH?", "en"), ("quoi", "QUOI ?!", "fr"), ("ach_hada", "ACH HADA?!", "darija")],
    "shock": [("wait_what", "WAIT... WHAT?!", "en"), ("nooon", "NOOON !", "fr")],
    "disbelief": [("no_way", "NO WAY.", "en"), ("serieux", "SÉRIEUX ?", "fr"), ("wach_bsah", "WACH BSSAH?", "darija")],
    "sarcasm": [("sure_buddy", "SURE, BUDDY.", "en"), ("bien_sur", "MAIS BIEN SÛR.", "fr")],
    "embarrassment": [("oof", "OOF.", "en"), ("la_honte", "LA HONTE.", "fr"), ("hchouma", "HCHOUMA!", "darija")],
    "unexpected_success": [("he_did_it", "HE ACTUALLY DID IT", "en"), ("valide", "VALIDÉ ✓", "fr")],
    "failure": [("it_failed", "IT DID NOT WORK.", "en"), ("rate", "RATÉ.", "fr")],
    "anger": [("calm_down", "CALM DOWN!", "en"), ("doucement", "DOUCEMENT !", "fr")],
    "awkward_silence": [("silence", "...", "en"), ("awkward", "AWKWARD.", "en")],
    "dramatic_realization": [("plot_twist", "PLOT TWIST", "en"), ("il_a_compris", "IL A COMPRIS.", "fr")],
    "relationship": [("red_flag", "RED FLAG", "en"), ("couple_goals", "COUPLE GOALS?", "en")],
    "family": [("every_mom", "EVERY MOM EVER", "en"), ("les_darons", "LES DARONS 😭", "fr"), ("mama_mghribiya", "MAMA MGHRIBIYA", "darija")],
}

PALETTES = ["highlight", "accent", "text"]


def font_path(family: str) -> str:
    return subprocess.run(["fc-match", family, "-f", "%{file}"], capture_output=True, text=True).stdout.strip()


def render(text: str, fill: str, out: Path, font_file: str, size: int = 120, tilt: float = -6) -> None:
    font = ImageFont.truetype(font_file, size)
    pad_x, pad_y, stroke = 60, 40, 10
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=font)
    w, h = r - l + 2 * pad_x, b - t + 2 * pad_y
    img = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # hard drop shadow, then badge
    d.rounded_rectangle([28, 28, w + 28, h + 28], radius=34, fill=(0, 0, 0, 200))
    d.rounded_rectangle([12, 12, w + 12, h + 12], radius=34, fill=fill, outline="#000000", width=stroke)
    text_color = "#111111" if fill.upper() != "#111111" else "#FFFFFF"
    d.text((12 + pad_x - l, 12 + pad_y - t), text, font=font, fill=text_color)
    img = img.rotate(tilt, expand=True, resample=Image.BICUBIC)
    img.save(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "assets" / "stickers"))
    args = ap.parse_args()
    brand = load_brand()
    font_file = font_path(brand["fonts"]["default"])
    fallback = font_path(brand["fonts"]["fallback"])
    out = Path(args.out)
    manifest = {}
    for ci, (cat, items) in enumerate(LIBRARY.items()):
        (out / cat).mkdir(parents=True, exist_ok=True)
        manifest[cat] = []
        for ii, (slug, text, lang) in enumerate(items):
            fill = brand["colors"][PALETTES[(ci + ii) % len(PALETTES)]]
            dst = out / cat / f"{slug}.png"
            # Inter has no emoji/Arabic glyphs; strip emoji rather than render tofu.
            clean = "".join(ch for ch in text if ord(ch) < 0x2000 or ch == "✓").strip()
            ff = font_file if all(ord(c) < 0x0250 for c in clean) else fallback
            render(clean, fill, dst, ff, tilt=-6 if ii % 2 == 0 else 5)
            manifest[cat].append({"file": f"{cat}/{slug}.png", "text": clean, "language": lang,
                                  "license": "original - channel owned"})
            print(f"wrote {dst}")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
