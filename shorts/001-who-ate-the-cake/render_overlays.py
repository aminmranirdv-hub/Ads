"""Render caption/overlay PNGs (1080x1920, transparent) for the Short.

Usage: python3 render_overlays.py <out_dir>
Each overlay is a full-frame transparent PNG so ffmpeg can overlay at 0:0.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
spec = json.loads((Path(__file__).parent / "overlays.json").read_text())


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def caption(text, y, size=78, fill="white", stroke="black", box=None, font=FONT_BLACK):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(font, size)
    lines = wrap(d, text, f, W - 140)
    lh = int(size * 1.18)
    total = lh * len(lines)
    top = y - total // 2
    if box:
        widest = max(d.textlength(l, font=f) for l in lines)
        pad = 34
        d.rounded_rectangle(
            [W / 2 - widest / 2 - pad, top - pad * 0.7, W / 2 + widest / 2 + pad, top + total + pad * 0.5],
            radius=28, fill=box,
        )
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f)
        d.text(((W - tw) / 2, top + i * lh), l, font=f, fill=fill,
               stroke_width=0 if box else max(4, size // 13), stroke_fill=stroke)
    return img


def stamp(text, sub):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_BLACK, 150)
    tw = d.textlength(text, font=f)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    cx, cy = W / 2, H * 0.45
    ld.rectangle([cx - tw / 2 - 40, cy - 110, cx + tw / 2 + 40, cy + 110], outline=(230, 30, 40, 255), width=16)
    ld.text((cx - tw / 2, cy - 92), text, font=f, fill=(230, 30, 40, 255))
    layer = layer.rotate(-8, center=(cx, cy), resample=Image.BICUBIC)
    img.alpha_composite(layer)
    if sub:
        img.alpha_composite(caption(sub, int(H * 0.66), size=64, fill="black", box=(255, 255, 255, 235), font=FONT_XB))
    return img


for item in spec:
    if item["kind"] == "stamp":
        im = stamp(item["text"], item.get("sub"))
    else:
        style = item.get("style", "sub")
        if style == "hook":
            im = caption(item["text"], 300, size=84, fill="black", box=(255, 222, 0, 245))
        elif style == "mid":
            im = caption(item["text"], 1050, size=96, fill="black", box=(255, 222, 0, 245))
        elif style == "label":
            im = caption(item["text"], 300, size=70, fill="white", box=(230, 30, 40, 240))
        else:
            im = caption(item["text"], 1440, size=74)
    im.save(out / f"{item['id']}.png")
    print("wrote", item["id"])
