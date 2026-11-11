"""M'RANI FAMILY channel art: logo, YouTube banner, profile picture, title card. usage: python3 make_art.py"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(D)
BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
COLORS = ["#FFC93C", "#FF8A1F", "#3D8BFF", "#7A4FD6", "#3FA34D", "#FF5D8F"]  # yellow(Abdel-Hamid) orange(Amir) blue(Hicham) purple(Aziza) green pink
def logo(width):
    """Returns RGBA logo image ~width px wide: colorful M'RANI + white FAMILY pill."""
    s = width / 1000
    big = ImageFont.truetype(BLACK, int(230 * s)); small = ImageFont.truetype(BLACK, int(92 * s))
    word = "M’RANI"
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    widths = [tmp.textlength(c, font=big) for c in word]; tw = sum(widths) + 8 * s * (len(word) - 1)
    H = int(430 * s); im = Image.new("RGBA", (width, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = (width - tw) / 2; y = int(20 * s); ci = 0
    for c, w in zip(word, widths):
        col = "#FFFFFF" if c == "’" else COLORS[ci % 4]; ci += c != "’"
        rot = Image.new("RGBA", (int(w + 60 * s), int(300 * s)), (0, 0, 0, 0)); rd = ImageDraw.Draw(rot)
        rd.text((30 * s + 8 * s, 18 * s), c, font=big, fill=(60, 30, 90, 120))                      # soft drop shadow
        rd.text((30 * s, 10 * s), c, font=big, fill=col, stroke_width=int(16 * s), stroke_fill="#2B1550")
        rot = rot.rotate([-4, 3, -2, 4, -3, 2][ci % 6], resample=Image.BICUBIC, expand=False)
        im.alpha_composite(rot, (int(x - 30 * s), y)); x += w + 8 * s
    pw, ph = int(560 * s), int(130 * s); px, py = (width - pw) // 2, int(285 * s)
    d.rounded_rectangle((px + 6 * s, py + 10 * s, px + pw + 6 * s, py + ph + 10 * s), radius=ph // 2, fill=(43, 21, 80, 140))
    d.rounded_rectangle((px, py, px + pw, py + ph), radius=ph // 2, fill="#FFFFFF", outline="#2B1550", width=int(10 * s))
    d.text((width / 2, py + ph / 2), "FAMILY", font=small, fill="#2B1550", anchor="mm")
    return im
group = Image.open(f"{ROOT}/team-group-shot-A.jpg").convert("RGB")
lg = logo(1000); lg.save(f"{D}/logo.png")

# --- YouTube banner 2560x1440 (safe area for all devices: centered 1546x423) ---
B = group.resize((2560, int(2560 * group.height / group.width))).crop((0, 0, 2560, 1440)) if group.height * 2560 / group.width >= 1440 else group.resize((int(1440 * group.width / group.height), 1440))
B = B.crop(((B.width - 2560) // 2, 0, (B.width - 2560) // 2 + 2560, 1440)).filter(ImageFilter.GaussianBlur(18))
B = ImageEnhance.Brightness(B).enhance(0.75).convert("RGBA")
ov = Image.new("RGBA", B.size, (43, 21, 80, 70)); B.alpha_composite(ov)
safe = (507, 508, 2053, 931)
card_h = 400; card = group.resize((int(card_h * group.width / group.height), card_h)); cw = card.width
cx, cy = safe[2] - cw - 10, safe[1] + 12
mask = Image.new("L", card.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw, card_h), radius=36, fill=255)
sh = Image.new("RGBA", (cw + 40, card_h + 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((20, 20, cw + 20, card_h + 20), radius=36, fill=(0, 0, 0, 120))
B.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (cx - 10, cy - 4))
B.paste(card, (cx, cy), mask); ImageDraw.Draw(B).rounded_rectangle((cx, cy, cx + cw, cy + card_h), radius=36, outline="#FFFFFF", width=8)
L = logo(720); B.alpha_composite(L, (safe[0] + 10, safe[1] + 10))
f = ImageFont.truetype(BLACK, 40); ImageDraw.Draw(B).text((safe[0] + 370, safe[1] + 355), "4 siblings · 4 kinds of genius · 1 team!", font=f, fill="#FFFFFF", anchor="mm", stroke_width=4, stroke_fill="#2B1550")
B.convert("RGB").save(f"{D}/youtube-banner-2560x1440.jpg", quality=92)

# --- profile picture 800x800 (shown as a small circle: logo badge reads best) ---
P = Image.new("RGBA", (800, 800), "#2B1550"); d = ImageDraw.Draw(P)
for i, c in enumerate(["#FFC93C", "#FF8A1F", "#3D8BFF", "#7A4FD6"]):
    d.pieslice((0, 0, 800, 800), i * 90 - 135, i * 90 - 45, fill=c)
d.ellipse((40, 40, 760, 760), fill="#2B1550")
P.alpha_composite(logo(700), (50, 230))
P.convert("RGB").save(f"{D}/youtube-profile-800.jpg", quality=92)

# --- episode title card 1920x1080 ---
Tc = group.resize((1920, int(1920 * group.height / group.width))).convert("RGBA")
Tc = Tc.crop((0, (Tc.height - 1080) // 2, 1920, (Tc.height - 1080) // 2 + 1080))
grad = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); gd = ImageDraw.Draw(grad)
for yy in range(0, 380): gd.line((0, yy, 1920, yy), fill=(43, 21, 80, int(170 * (1 - yy / 380))))
Tc.alpha_composite(grad); Tc.alpha_composite(logo(600), (40, 20))
Tc.convert("RGB").save(f"{D}/title-card-1920x1080.jpg", quality=92)
print("done")
