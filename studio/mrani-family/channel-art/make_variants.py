"""Logo/profile/banner variants B (Fredoka, sunny yellow) and C (Lilita One, sky blue + sibling faces)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(D); FD = f"{D}/fonts"
SIB = {"abdel": "#FFC93C", "amir": "#FF8A1F", "hicham": "#3D8BFF", "aziza": "#A86BFF"}
def logo(width, font, colors, outline="#2B1550", bounce=True, pill_fill="#FFFFFF", pill_text="#2B1550", word_size=230, fam_font=None):
    s = width / 1000; big = ImageFont.truetype(font, int(word_size * s)); small = ImageFont.truetype(fam_font or font, int(96 * s))
    word = "M’RANI"; t = ImageDraw.Draw(Image.new("RGBA", (9, 9)))
    ws = [t.textlength(c, font=big) for c in word]; gap = 6 * s; tw = sum(ws) + gap * 5
    H = int(470 * s); im = Image.new("RGBA", (width, H), (0, 0, 0, 0)); x = (width - tw) / 2; ci = 0
    for i, (c, w) in enumerate(zip(word, ws)):
        col = "#FFFFFF" if c == "’" else colors[ci % len(colors)]; ci += c != "’"
        L = Image.new("RGBA", (int(w + 80 * s), int(340 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.text((40 * s + 7 * s, 30 * s + 12 * s), c, font=big, fill=(30, 20, 60, 110))
        d.text((40 * s, 30 * s), c, font=big, fill=col, stroke_width=int(18 * s), stroke_fill=outline)
        d.text((40 * s, 30 * s), c, font=big, fill=col)
        hl = Image.new("RGBA", L.size, (0, 0, 0, 0)); ImageDraw.Draw(hl).text((40 * s, 30 * s), c, font=big, fill=(255, 255, 255, 70))
        hl = hl.crop((0, 0, L.width, int(L.height * .42))); L.alpha_composite(hl, (0, 0)) if False else None
        dy = (-14 if i % 2 else 10) * s if bounce else 0; rot = ([-6, 4, -3, 5, -4, 3][i]) if bounce else 0
        L = L.rotate(rot, resample=Image.BICUBIC); im.alpha_composite(L, (int(x - 40 * s), int(dy))); x += w + gap
    pw, ph = int(580 * s), int(132 * s); px, py = (width - pw) // 2, int(300 * s); d = ImageDraw.Draw(im)
    d.rounded_rectangle((px + 6 * s, py + 10 * s, px + pw + 6 * s, py + ph + 10 * s), radius=ph // 2, fill=(30, 20, 60, 120))
    d.rounded_rectangle((px, py, px + pw, py + ph), radius=ph // 2, fill=pill_fill, outline=outline, width=int(10 * s))
    d.text((width / 2, py + ph / 2 - 4 * s), "FAMILY", font=small, fill=pill_text, anchor="mm")
    return im
def rays(size, c1, c2, n=16):
    im = Image.new("RGBA", (size, size), c1); d = ImageDraw.Draw(im)
    for i in range(n):
        if i % 2: d.pieslice((-size, -size, size * 2, size * 2), i * 360 / n, (i + 1) * 360 / n, fill=c2)
    return im
def face(sheet, idx, size):
    im = Image.open(sheet).convert("RGB"); W, H = im.size; cw = W / 6
    c = im.crop((int(idx * cw + cw * .08), int(H * .70), int((idx + 1) * cw - cw * .08), int(H * .70 + cw * .84))).resize((size, size))
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size, size), fill=255); return c, m
FRED, LIL = f"{FD}/fredoka-latin-700-normal.woff", f"{FD}/lilita-one-latin-400-normal.woff"
group = Image.open(f"{ROOT}/team-group-shot-A.jpg").convert("RGB")
VAR = {
 "B": dict(font=FRED, colors=[SIB["abdel"], SIB["amir"], SIB["hicham"], SIB["aziza"]], outline="#2B1550", bg=("#FFD84D", "#FFC93C"), pill_fill="#2B1550", pill_text="#FFFFFF"),
 "C": dict(font=LIL, colors=["#FFD84D", SIB["amir"], "#FF5D8F", SIB["aziza"]], outline="#1B3A8F", bg=("#7FD3FF", "#5FC0F5"), pill_fill="#FFFFFF", pill_text="#1B3A8F"),
}
for name, v in VAR.items():
    mk = lambda w: logo(w, v["font"], v["colors"], v["outline"], True, v["pill_fill"], v["pill_text"])
    mk(1000).save(f"{D}/logo-{name}.png")
    # profile 800
    P = rays(800, *v["bg"]); d = ImageDraw.Draw(P)
    if name == "B":
        d.ellipse((30, 30, 770, 770), outline="#FFFFFF", width=18); P.alpha_composite(mk(720), (40, 175))
    else:
        faces = [("abdel-hamid", 4), ("amir", 0), ("hicham", 1), ("aziza", 1)]; pos = [(95, 70), (485, 70), (95, 470), (485, 470)]
        for (who, idx), (x, y) in zip(faces, pos):
            f, m = face(f"{ROOT}/characters/{who}/model-sheet-A.jpg", idx, 220)
            d.ellipse((x - 12, y - 12, x + 232, y + 232), fill="#FFFFFF"); P.paste(f, (x, y), m)
        P.alpha_composite(mk(640), (80, 215))
    P.convert("RGB").save(f"{D}/youtube-profile-800-{name}.jpg", quality=92)
    # banner 2560x1440, content in safe area (507..2053, 508..931)
    B = rays(2600, *v["bg"], n=28).crop((20, 580, 2580, 2020)); d = ImageDraw.Draw(B)
    for i, c in enumerate([SIB["abdel"], SIB["amir"], SIB["hicham"], SIB["aziza"]]):       # playful confetti dots
        for k in range(14):
            import random; random.seed(i * 50 + k); x, y = random.randint(0, 2560), random.randint(0, 1440); r = random.randint(10, 26)
            d.ellipse((x - r, y - r, x + r, y + r), fill=c if name == "C" else "#FFFFFF")
    card_h = 400; card = group.resize((int(card_h * group.width / group.height), card_h)); cw = card.width; cx, cy = 2053 - cw - 10, 520
    m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw, card_h), radius=40, fill=255)
    sh = Image.new("RGBA", (cw + 60, card_h + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((30, 30, cw + 30, card_h + 30), radius=40, fill=(0, 0, 0, 90))
    B.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (cx - 22, cy - 14)); B.paste(card, (cx, cy), m)
    d.rounded_rectangle((cx, cy, cx + cw, cy + card_h), radius=40, outline="#FFFFFF", width=10)
    B.alpha_composite(mk(700), (517, 470))
    tag = ImageFont.truetype(v["font"], 46); d.text((517 + 350, 890), "4 siblings · 4 kinds of genius · 1 team!", font=tag, fill="#FFFFFF", anchor="mm", stroke_width=6, stroke_fill=v["outline"])
    B.convert("RGB").save(f"{D}/youtube-banner-2560x1440-{name}.jpg", quality=92)
print("ok")
