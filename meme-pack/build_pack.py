"""Build an original, royalty-free meme overlay pack for Shorts.

Everything here is generated from scratch (text, shapes, synthesized audio),
so it is safe to use in monetized videos. Emoji art comes from Noto Color
Emoji (SIL Open Font License 1.1, commercial use allowed).

Usage: python3 build_pack.py   (writes into this folder)
"""
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent
STK = ROOT / "stickers"
EMO = ROOT / "emoji"
FRM = ROOT / "frames"
SFX = ROOT / "sfx"
for d in (STK, EMO, FRM, SFX):
    d.mkdir(parents=True, exist_ok=True)

BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H = 1080, 1920

RED = (230, 30, 40, 255)
YEL = (255, 222, 0, 255)
WHITE = (255, 255, 255, 255)
INK = (15, 15, 15, 255)


def trim(img, pad=24):
    box = img.getbbox()
    if not box:
        return img
    x0, y0, x1, y1 = box
    return img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))


def shadow(img, offset=10, blur=14, alpha=150):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    mask = img.split()[3].point(lambda a: min(alpha, a))
    sh.putalpha(mask)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (img.width + offset * 2 + blur * 2, img.height + offset * 2 + blur * 2), (0, 0, 0, 0))
    out.alpha_composite(sh, (blur + offset, blur + offset))
    out.alpha_composite(img, (blur, blur))
    return out


# ---------- text stickers ----------
def pill(text, fg, bg, size=110, rot=0, font=BLACK):
    f = ImageFont.truetype(font, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=f)
    pw, ph = int(size * 0.45), int(size * 0.28)
    img = Image.new("RGBA", (r - l + pw * 2, b - t + ph * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=int(size * 0.32), fill=bg)
    d.text((pw - l, ph - t), text, font=f, fill=fg)
    if rot:
        img = img.rotate(rot, expand=True, resample=Image.BICUBIC)
    return shadow(img)


def outline(text, fg=WHITE, stroke=INK, size=150, rot=0):
    f = ImageFont.truetype(BLACK, size)
    img = Image.new("RGBA", (W * 2, size * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((40, size // 2), text, font=f, fill=fg, stroke_width=max(6, size // 11), stroke_fill=stroke)
    img = trim(img)
    if rot:
        img = img.rotate(rot, expand=True, resample=Image.BICUBIC)
    return shadow(img, offset=6, blur=10)


def stamp(text, color=RED, size=170, rot=-10):
    f = ImageFont.truetype(BLACK, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=f)
    pad = int(size * 0.35)
    img = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(10, size // 11)
    d.rectangle([lw, lw, img.width - lw, img.height - lw], outline=color, width=lw)
    d.text((pad - l, pad - t), text, font=f, fill=color)
    # grunge: knock out random speckles so it reads like an ink stamp
    import random
    random.seed(text)
    a = img.split()[3]
    ad = ImageDraw.Draw(a)
    for _ in range(int(img.width * img.height / 3000)):
        x, y = random.randrange(img.width), random.randrange(img.height)
        rr = random.choice((1, 2, 2, 3))
        ad.ellipse([x - rr, y - rr, x + rr, y + rr], fill=0)
    img.putalpha(a)
    return img.rotate(rot, expand=True, resample=Image.BICUBIC)


TEXT_STICKERS = {
    # reaction / comedy
    "bruh": lambda: outline("BRUH", size=220, rot=4),
    "wait-for-it": lambda: pill("WAIT FOR IT…", INK, YEL),
    "plot-twist": lambda: pill("PLOT TWIST", WHITE, RED, rot=-4),
    "caught-in-4k": lambda: pill("CAUGHT IN 4K", WHITE, RED),
    "the-audacity": lambda: outline("THE AUDACITY", size=130, rot=-3),
    "not-me": lambda: pill("NOT ME 🙄".replace(" 🙄", ""), INK, WHITE),
    "oh-no": lambda: outline("OH NO.", fg=YEL, size=190, rot=-5),
    "nope": lambda: outline("NOPE", fg=RED, stroke=WHITE, size=220, rot=6),
    "suspect-1": lambda: pill("SUSPECT #1", WHITE, INK),
    "suspect-2": lambda: pill("SUSPECT #2", WHITE, INK),
    "meanwhile": lambda: pill("Meanwhile…", INK, WHITE, font=XB),
    "3-hours-later": lambda: pill("3 HOURS LATER", INK, YEL),
    "one-eternity-later": lambda: pill("ONE ETERNITY LATER", WHITE, (110, 60, 200, 255)),
    "zero-regrets": lambda: pill("0% REGRETS", INK, YEL, rot=3),
    "part-2": lambda: pill("PART 2?", WHITE, RED),
    "pov": lambda: pill("POV:", WHITE, INK),
    # pranks / challenges
    "challenge-accepted": lambda: pill("CHALLENGE ACCEPTED", INK, YEL),
    "impossible": lambda: outline("IMPOSSIBLE?", fg=YEL, size=150),
    "round-1": lambda: pill("ROUND 1", WHITE, (30, 110, 230, 255)),
    "winner": lambda: pill("WINNER 🏆".replace(" 🏆", ""), INK, YEL, rot=-4),
    "fail": lambda: stamp("FAIL", rot=8),
    "nailed-it": lambda: stamp("NAILED IT", color=(20, 160, 70, 255), size=140),
    # verdict stamps
    "guilty": lambda: stamp("GUILTY"),
    "case-closed": lambda: stamp("CASE CLOSED", size=130),
    "innocent": lambda: stamp("INNOCENT", color=(20, 160, 70, 255), size=150, rot=7),
    # transformations
    "before": lambda: pill("BEFORE", WHITE, INK),
    "after": lambda: pill("AFTER", INK, YEL),
    "day-1": lambda: pill("DAY 1", WHITE, INK),
    "satisfying": lambda: outline("SO SATISFYING", fg=WHITE, size=130),
    "rate-it": lambda: pill("RATE IT 1–10", INK, YEL),
    "worth-it": lambda: pill("WORTH IT?", WHITE, RED),
    # CTA
    "follow-for-more": lambda: pill("FOLLOW FOR MORE", WHITE, RED),
    "comment-below": lambda: pill("COMMENT YOUR VERDICT ↓", INK, WHITE, size=80),
    "wait-for-the-end": lambda: pill("WAIT FOR THE END", INK, YEL, size=90),
}

for name, fn in TEXT_STICKERS.items():
    fn().save(STK / f"{name}.png")


# ---------- graphic stickers ----------
def red_circle():
    img = Image.new("RGBA", (700, 560), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # hand-drawn feel: two slightly offset ellipses
    d.ellipse([30, 30, 670, 530], outline=RED, width=22)
    d.arc([18, 50, 660, 545], 200, 330, fill=RED, width=14)
    return img


def red_arrow():
    img = Image.new("RGBA", (620, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([(40, 150), (430, 150)], fill=RED, width=60)
    d.polygon([(400, 40), (590, 150), (400, 260)], fill=RED)
    return shadow(img, offset=6, blur=8)


def pixel_shades():
    # original 8-bit sunglasses, drawn on a grid
    grid = [
        "XXXXXXXXXXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXX",
        "..XWWXXXXXX....XWWXXXXXX..",
        "..XXWWXXXXX....XXWWXXXXX..",
        "...XXXXXXX......XXXXXXX...",
        "....XXXXX........XXXXX....",
    ]
    s = 30
    img = Image.new("RGBA", (len(grid[0]) * s, len(grid) * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == "X":
                d.rectangle([x * s, y * s, x * s + s - 1, y * s + s - 1], fill=INK)
            elif c == "W":
                d.rectangle([x * s, y * s, x * s + s - 1, y * s + s - 1], fill=WHITE)
    return img


def speed_lines():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H / 2
    import random
    random.seed(7)
    for i in range(120):
        a = i / 120 * 2 * math.pi + random.uniform(-0.02, 0.02)
        r0 = random.uniform(430, 620)
        r1 = 1500
        wdt = random.uniform(0.004, 0.012)
        pts = [
            (cx + r1 * math.cos(a - wdt), cy + r1 * math.sin(a - wdt)),
            (cx + r1 * math.cos(a + wdt), cy + r1 * math.sin(a + wdt)),
            (cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
        ]
        d.polygon(pts, fill=(255, 255, 255, 210))
    return img


def vignette():
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    d.ellipse([-200, 100, W + 200, H - 100], fill=255)
    img = img.filter(ImageFilter.GaussianBlur(160))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    out.putalpha(img.point(lambda v: int((255 - v) * 0.85)))
    return out


def rec_frame():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m, L, lw = 70, 120, 10
    for (x, y, dx, dy) in [(m, m + 80, 1, 1), (W - m, m + 80, -1, 1), (m, H - m - 80, 1, -1), (W - m, H - m - 80, -1, -1)]:
        d.line([(x, y), (x + dx * L, y)], fill=WHITE, width=lw)
        d.line([(x, y), (x, y + dy * L)], fill=WHITE, width=lw)
    d.ellipse([m + 30, m + 120, m + 80, m + 170], fill=RED)
    f = ImageFont.truetype(BLACK, 56)
    d.text((m + 100, m + 115), "REC", font=f, fill=WHITE)
    return img


def countdown(n):
    img = Image.new("RGBA", (520, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, 510, 510], fill=YEL, outline=INK, width=16)
    f = ImageFont.truetype(BLACK, 330)
    l, t, r, b = d.textbbox((0, 0), str(n), font=f)
    d.text(((520 - (r - l)) / 2 - l, (520 - (b - t)) / 2 - t), str(n), font=f, fill=INK)
    return shadow(img)


red_circle().save(STK / "red-circle.png")
red_arrow().save(STK / "red-arrow-right.png")
red_arrow().transpose(Image.FLIP_LEFT_RIGHT).save(STK / "red-arrow-left.png")
red_arrow().rotate(-90, expand=True).save(STK / "red-arrow-down.png")
pixel_shades().save(STK / "pixel-sunglasses.png")
for n in (3, 2, 1):
    countdown(n).save(STK / f"countdown-{n}.png")
speed_lines().save(FRM / "speed-lines-zoom.png")
vignette().save(FRM / "dramatic-vignette.png")
rec_frame().save(FRM / "camcorder-rec.png")


# ---------- caption templates (full 1080x1920) ----------
def top_bar_template():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 420], fill=WHITE)
    f = ImageFont.truetype(XB, 60)
    d.text((60, 170), "POV: your caption here", font=f, fill=INK)
    return img


def split_before_after():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, H // 2 - 6, W, H // 2 + 6], fill=WHITE)
    b = pill("BEFORE", WHITE, INK, size=70)
    a = pill("AFTER", INK, YEL, size=70)
    img.alpha_composite(b, (40, 60))
    img.alpha_composite(a, (40, H // 2 + 40))
    return img


top_bar_template().save(FRM / "pov-top-bar-template.png")
split_before_after().save(FRM / "before-after-split.png")


# ---------- emoji (Noto Color Emoji, OFL) ----------
EMOJIS = {
    "laughing": "😂", "skull": "💀", "sobbing": "😭", "eyes": "👀", "fire": "🔥",
    "flushed": "😳", "mind-blown": "🤯", "peeking": "🫣", "clown": "🤡", "hundred": "💯",
    "sparkles": "✨", "cake": "🎂", "dog": "🐶", "cat": "🐱", "trophy": "🏆",
    "warning": "⚠️", "check": "✅", "cross": "❌", "thinking": "🤔", "melting": "🫠",
}
ef = ImageFont.truetype(EMOJI_FONT, 109)
for name, ch in EMOJIS.items():
    img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((10, 10), ch, font=ef, embedded_color=True)
    img = trim(img, pad=4)
    s = 512 / max(img.size)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    img.save(EMO / f"{name}.png")


# ---------- synthesized SFX ----------
def ff(name, args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args,
                    "-ar", "48000", "-ac", "2", str(SFX / name)], check=True)


ff("boom-hit.wav", ["-f", "lavfi", "-i", "sine=f=50:d=1.4", "-f", "lavfi", "-i", "anoisesrc=d=0.08:c=brown:a=1",
                    "-filter_complex", "[0]afade=t=out:st=0.05:d=1.3,volume=5[a];[1]afade=t=out:d=0.08,volume=2[b];[a][b]amix=inputs=2:normalize=0,alimiter"])
ff("whoosh.wav", ["-f", "lavfi", "-i", "anoisesrc=d=0.5:c=pink:a=0.7",
                  "-af", "bandpass=f=1600:w=1500,afade=t=in:d=0.22,afade=t=out:st=0.22:d=0.28,volume=2"])
ff("pop.wav", ["-f", "lavfi", "-i", "sine=f=900:d=0.08", "-af", "asetrate=48000*1.0,afade=t=out:d=0.08,volume=2.5"])
ff("ding.wav", ["-f", "lavfi", "-i", "sine=f=1760:d=1.2", "-f", "lavfi", "-i", "sine=f=2637:d=1.2",
                "-filter_complex", "[0][1]amix=inputs=2,afade=t=out:st=0.02:d=1.15,volume=2"])
ff("error-buzzer.wav", ["-f", "lavfi", "-i", "sine=f=110:d=0.6", "-af", "acrusher=bits=4:mix=1,afade=t=out:st=0.45:d=0.15,volume=0.8"])
ff("dramatic-sting.wav", ["-f", "lavfi", "-i", "sine=f=98:d=0.35", "-f", "lavfi", "-i", "sine=f=92:d=0.35", "-f", "lavfi", "-i", "sine=f=73:d=1.2",
                          "-filter_complex", "[0]afade=t=out:st=0.2:d=0.15[a];[1]afade=t=out:st=0.2:d=0.15[b];[2]afade=t=out:st=0.3:d=0.9[c];[a][b][c]concat=n=3:v=0:a=1,volume=3"])
ff("stamp-thud.wav", ["-f", "lavfi", "-i", "sine=f=75:d=0.45", "-f", "lavfi", "-i", "anoisesrc=d=0.1:c=brown:a=1",
                      "-filter_complex", "[0]afade=t=out:st=0.02:d=0.43[a];[1]afade=t=out:d=0.1[b];[a][b]amix=inputs=2:normalize=0,volume=4,alimiter"])
ff("cartoon-boing.wav", ["-f", "lavfi", "-i", "aevalsrc='sin(2*PI*(180+120*sin(2*PI*9*t))*t)*exp(-3*t)':d=0.9:s=48000", "-af", "volume=0.9"])
ff("record-scratch.wav", ["-f", "lavfi", "-i", "aevalsrc='(random(0)*2-1)*0.6*sin(2*PI*14*t)*exp(-4*t)':d=0.5:s=48000",
                          "-af", "bandpass=f=1200:w=900,volume=3"])
ff("riser.wav", ["-f", "lavfi", "-i", "aevalsrc='sin(2*PI*(200*t+300*t*t))*0.5*(t/2.5)':d=2.5:s=48000",
                 "-af", "afade=t=out:st=2.4:d=0.1,volume=1.2"])
ff("camera-shutter.wav", ["-f", "lavfi", "-i", "anoisesrc=d=0.05:c=white:a=1", "-f", "lavfi", "-i", "anoisesrc=d=0.05:c=white:a=1",
                          "-filter_complex", "[0]highpass=f=2000,afade=t=out:d=0.05[a];[1]highpass=f=2500,afade=t=out:d=0.05,adelay=90|90[b];[a][b]amix=inputs=2:normalize=0,volume=2"])
ff("crickets.wav", ["-f", "lavfi", "-i", "aevalsrc='sin(2*PI*4500*t)*(gt(sin(2*PI*28*t),0.3))*(gt(sin(2*PI*1.3*t),0))*0.3':d=3:s=48000",
                    "-af", "afade=t=in:d=0.3,afade=t=out:st=2.6:d=0.4"])
ff("cash-register-ding.wav", ["-f", "lavfi", "-i", "sine=f=2093:d=0.9", "-f", "lavfi", "-i", "sine=f=3136:d=0.9",
                              "-filter_complex", "[1]adelay=90|90[b];[0][b]amix=inputs=2,afade=t=out:st=0.05:d=0.85,volume=2"])

print("done")
