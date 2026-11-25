"""Generic Shorts assembler for @waitfor.thetwist.

Usage: python3 tools/make_short.py shorts/<id>/spec.json

spec.json:
{
  "out": "final/short.mp4",                      # relative to the spec's folder
  "segments": [{"src": "raw/clip.mp4", "start": 0, "end": 15}],
  "freeze": {"src": "raw/clip.mp4", "t": 12.0, "dur": 2.0},   # optional end freeze
  "overlays": [                                   # times are OUTPUT seconds
    {"style": "hook|label|mid|sub|cta", "text": "...", "start": 0, "end": 2.5},
    {"style": "stamp", "text": "GUILTY", "sub": "Comment below", "start": 13, "end": 15},
    {"style": "sticker", "file": "meme-pack/stickers/bruh.png", "width": 600,
     "x": "center", "y": 260, "start": 5, "end": 7}
  ],
  "sfx": [{"file": "meme-pack/sfx/boom-hit.wav", "t": 0, "gain": 0.8}]
}
Sticker/sfx paths are relative to the repo root.
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
YEL, RED = (255, 222, 0, 245), (230, 30, 40, 240)


def wrap(d, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def caption(text, y, size, fill="white", box=None, font=BLACK):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(font, size)
    lines = wrap(d, text, f, W - 160)
    lh = int(size * 1.18)
    top = y - lh * len(lines) // 2
    if box:
        widest = max(d.textlength(l, font=f) for l in lines)
        pad = 34
        d.rounded_rectangle([W / 2 - widest / 2 - pad, top - pad * 0.7,
                             W / 2 + widest / 2 + pad, top + lh * len(lines) + pad * 0.5], radius=28, fill=box)
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f)
        d.text(((W - tw) / 2, top + i * lh), l, font=f, fill=fill,
               stroke_width=0 if box else max(4, size // 13), stroke_fill="black")
    return img


def stamp(text, sub):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    size = 150
    f = ImageFont.truetype(BLACK, size)
    while ld.textlength(text, font=f) > 760 and size > 60:   # keep the rotated stamp inside the frame
        size -= 6
        f = ImageFont.truetype(BLACK, size)
    tw = ld.textlength(text, font=f)
    cx, cy = W / 2, H * 0.45
    ld.rectangle([cx - tw / 2 - 40, cy - size * 0.73, cx + tw / 2 + 40, cy + size * 0.73],
                 outline=(230, 30, 40, 255), width=16)
    ld.text((cx - tw / 2, cy - size * 0.61), text, font=f, fill=(230, 30, 40, 255))
    img.alpha_composite(layer.rotate(-8, center=(cx, cy), resample=Image.BICUBIC))
    if sub:
        img.alpha_composite(caption(sub, int(H * 0.66), 64, fill="black", box=(255, 255, 255, 235), font=XB))
    return img


def render(item):
    st = item.get("style", "sub")
    if st == "hook":
        return caption(item["text"], 300, 84, fill="black", box=YEL)
    if st == "label":
        return caption(item["text"], 300, 70, box=RED)
    if st == "mid":
        return caption(item["text"], 1050, 96, fill="black", box=YEL)
    if st == "cta":
        return caption(item["text"], int(H * 0.66), 64, fill="black", box=(255, 255, 255, 235), font=XB)
    if st == "stamp":
        return stamp(item["text"], item.get("sub"))
    if st == "sticker":
        s = Image.open(REPO / item["file"]).convert("RGBA")
        wdt = item.get("width", 600)
        s = s.resize((wdt, round(s.height * wdt / s.width)), Image.LANCZOS)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        x = (W - s.width) // 2 if item.get("x", "center") == "center" else int(item["x"])
        img.alpha_composite(s, (x, int(item.get("y", 260))))
        return img
    return caption(item["text"], 1440, 74)


def main(spec_path):
    spec_path = Path(spec_path).resolve()
    base = spec_path.parent
    spec = json.loads(spec_path.read_text())
    tmp = base / "overlays"
    tmp.mkdir(exist_ok=True)

    inputs, fc, vlabels, alabels = [], [], [], []
    n = 0
    V = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
    total = 0.0
    for i, seg in enumerate(spec["segments"]):
        inputs += ["-i", str(base / seg["src"])]
        fc.append(f"[{n}:v]trim={seg['start']}:{seg['end']},setpts=PTS-STARTPTS,{V}[v{i}]")
        fc.append(f"[{n}:a]atrim={seg['start']}:{seg['end']},asetpts=PTS-STARTPTS,"
                  f"aformat=sample_rates=48000:channel_layouts=stereo[a{i}]")
        vlabels.append(f"[v{i}]"); alabels.append(f"[a{i}]")
        total += seg["end"] - seg["start"]
        n += 1
    fr = spec.get("freeze")
    if fr:
        png = tmp / "_freeze.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(fr["t"]), "-i", str(base / fr["src"]),
                        "-frames:v", "1", str(png)], check=True)
        d = fr.get("dur", 2.0)
        frames = int(d * 30)
        inputs += ["-loop", "1", "-t", str(d), "-i", str(png)]
        fc.append(f"[{n}:v]scale=2160:3840,zoompan=z='1+0.0025*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={frames}:s=1080x1920:fps=30,setsar=1,format=yuv420p,trim=0:{d}[vf]")
        fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{d}[af]")
        vlabels.append("[vf]"); alabels.append("[af]")
        total += d
        n += 1
    k = len(vlabels)
    fc.append(f"{''.join(vlabels)}concat=n={k}:v=1:a=0[base]")
    fc.append(f"{''.join(alabels)}concat=n={k}:v=0:a=1[dialog]")

    cur = "base"
    for i, item in enumerate(spec.get("overlays", [])):
        p = tmp / f"ov{i:02d}.png"
        render(item).save(p)
        inputs += ["-i", str(p)]
        fc.append(f"[{n}:v]format=rgba[o{i}]")
        fc.append(f"[{cur}][o{i}]overlay=0:0:enable='between(t,{item['start']},{item['end']})'[c{i}]")
        cur = f"c{i}"
        n += 1
    fc.append(f"[{cur}]null[vout]")

    labels = ["[dialog]"]
    for j, s in enumerate(spec.get("sfx", [])):
        inputs += ["-i", str(REPO / s["file"])]
        ms = int(s["t"] * 1000)
        fc.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={s.get('gain', 0.8)},"
                  f"adelay={ms}|{ms}[s{j}]")
        labels.append(f"[s{j}]")
        n += 1
    fc.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=first,"
              "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

    out = base / spec.get("out", "final/short.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc),
                    "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    print(f"wrote {out} ({total:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
