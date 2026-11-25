"""Profile picture for the YouTube channel @waitfor.thetwist ("Wait For The Twist").

Original artwork: a looping "plot twist" arrow. Brand colours match the
video overlays (yellow #FFDE00, red #E61E28, ink #0F0F0F).
Renders at 4x then downsamples for smooth edges.

Usage: python3 build_brand.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
YEL = (255, 222, 0)
RED = (230, 30, 40)
INK = (15, 15, 15)
WHITE = (255, 255, 255)
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"

S = 4            # supersample factor
N = 800 * S      # YouTube recommends 800x800


def loop_points(cx, cy, scale, steps=900):
    """Loop-the-loop arrow path: in from the left, one full loop, out to the right."""
    r = 0.50            # loop radius (in path units; path spans about -1..1 horizontally)
    base = 0.42         # baseline height
    pts = []
    n1 = steps // 4
    for i in range(n1 + 1):                      # lead-in, gently curving up into the loop
        t = i / n1
        pts.append((-0.95 + 0.9 * t, base))
    n2 = steps // 2
    ccx, ccy = -0.05 + 0.10 * 0, base - r
    for i in range(1, n2 + 1):                   # full loop, counter-clockwise when viewed (going up)
        a = math.pi / 2 - 2 * math.pi * i / n2   # starts at bottom of circle (y down => +pi/2)
        drift = 0.26 * i / n2                    # small forward drift so the loop crosses itself
        pts.append((ccx + drift + r * math.cos(a) * -1, ccy + r * math.sin(a)))
    n3 = steps // 4
    x0, y0 = pts[-1]
    for i in range(1, n3 + 1):                   # exit to the right
        t = i / n3
        pts.append((x0 + (0.62 - x0) * t, y0))
    # tilt upward for energy, then centre the whole mark (incl. arrowhead room)
    tilt = math.radians(-14)
    pts = [(x * math.cos(tilt) - y * math.sin(tilt), x * math.sin(tilt) + y * math.cos(tilt)) for x, y in pts]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    mx, my = (min(xs) + max(xs) + 0.18) / 2, (min(ys) + max(ys)) / 2
    return [(cx + (x - mx) * scale / 2, cy + (y - my) * scale / 2) for x, y in pts]


def stroke(d, pts, width, fill):
    r = width / 2
    for x, y in pts[::2]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def arrowhead(d, pts, size, fill):
    (x0, y0), (x1, y1) = pts[-20], pts[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + math.cos(ang) * size * 0.9, y1 + math.sin(ang) * size * 0.9)
    back = (x1 - math.cos(ang) * size * 0.35, y1 - math.sin(ang) * size * 0.35)
    l = (back[0] + math.cos(ang + math.pi / 2) * size * 0.75, back[1] + math.sin(ang + math.pi / 2) * size * 0.75)
    rr = (back[0] + math.cos(ang - math.pi / 2) * size * 0.75, back[1] + math.sin(ang - math.pi / 2) * size * 0.75)
    d.polygon([tip, l, rr], fill=fill)


def twist_mark(d, cx, cy, scale, width, color, head_color=None):
    pts = loop_points(cx, cy, scale)
    stroke(d, pts[:-12], width, color)
    arrowhead(d, pts, width * 1.15, head_color or color)


def profile(bg, mark, head, ring=None, name="profile"):
    img = Image.new("RGB", (N, N), bg)
    d = ImageDraw.Draw(img)
    if ring:
        # thin inner ring inside the circular crop keeps the edge crisp on any theme
        m = int(N * 0.035)
        d.ellipse([m, m, N - m, N - m], outline=ring, width=int(N * 0.022))
    # shadow
    twist_mark(d, N / 2 + N * 0.012, N * 0.5 + N * 0.016, N * 0.62, N * 0.072, (0, 0, 0) if bg != INK else (60, 60, 60))
    twist_mark(d, N / 2, N * 0.5, N * 0.62, N * 0.072, mark, head)
    img = img.resize((800, 800), Image.LANCZOS)
    img.save(OUT / f"{name}.png")
    return img


def circle_preview(img, size):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, img.width - 1, img.height - 1], fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), m)
    return out.resize((size, size), Image.LANCZOS)


font = ImageFont.truetype(BLACK, 30)


# ---------------------------------------------------------------------------
# Typographic badge: "WAIT FOR THE / TWIST" with a red swoosh arrow.
# ---------------------------------------------------------------------------
def fit_font(d, text, path, max_w, start):
    size = start
    while size > 10:
        f = ImageFont.truetype(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(path, size)


def badge(bg, word, small, arrow, name):
    img = Image.new("RGB", (N, N), bg)
    d = ImageDraw.Draw(img)
    cx = N / 2
    # small line
    fs = fit_font(d, "WAIT FOR THE", BLACK, N * 0.52, int(N * 0.12))
    l, t, r, b = d.textbbox((0, 0), "WAIT FOR THE", font=fs)
    d.text((cx - (r - l) / 2 - l, N * 0.25 - t), "WAIT FOR THE", font=fs, fill=small)
    # main word (slight forward tilt)
    fb = fit_font(d, "TWIST", BLACK, N * 0.80, int(N * 0.40))
    l, t, r, b = d.textbbox((0, 0), "TWIST", font=fb)
    layer = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((cx - (r - l) / 2 - l, N * 0.38 - t), "TWIST", font=fb, fill=word + (255,))
    layer = layer.rotate(5, center=(cx, N * 0.48), resample=Image.BICUBIC)
    img.paste(layer, (0, 0), layer)
    # wavy "twist" arrow under the word (S-curve, NOT a smile swoosh)
    w = N * 0.048
    x0, x1, yc, amp = N * 0.24, N * 0.70, N * 0.70, N * 0.045
    pts = []
    for i in range(401):
        t = i / 400
        x = x0 + (x1 - x0) * t
        y = yc - amp * math.sin(t * 2 * math.pi * 1.5)
        pts.append((x, y))
    for x, y in pts:
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=arrow)
    (ax, ay), (bx, by) = pts[-12], pts[-1]
    ang = math.atan2(by - ay, bx - ax)
    size = w * 1.6
    tip = (bx + math.cos(ang) * size * 1.2, by + math.sin(ang) * size * 1.2)
    lft = (bx + math.cos(ang + math.pi / 2) * size, by + math.sin(ang + math.pi / 2) * size)
    rgt = (bx + math.cos(ang - math.pi / 2) * size, by + math.sin(ang - math.pi / 2) * size)
    d.polygon([tip, lft, rgt], fill=arrow)
    img = img.resize((800, 800), Image.LANCZOS)
    img.save(OUT / f"{name}.png")
    return img


badges = {
    "badge-yellow": badge(YEL, INK, INK, RED, "badge-yellow"),
    "badge-black": badge(INK, YEL, WHITE, RED, "badge-black"),
    "badge-red": badge(RED, WHITE, YEL, YEL, "badge-red"),
}
sheet = Image.new("RGB", (1500, 1220), (245, 245, 245))
sd = ImageDraw.Draw(sheet)
sd.rectangle([0, 610, 1500, 1220], fill=(15, 15, 15))
for row in range(2):
    for col, (nm, im) in enumerate(badges.items()):
        x0, y0 = 40 + col * 490, 30 + row * 610
        c4 = circle_preview(im, 400); sheet.paste(c4, (x0, y0), c4)
        c1 = circle_preview(im, 98); sheet.paste(c1, (x0, y0 + 430), c1)
        c0 = circle_preview(im, 48); sheet.paste(c0, (x0 + 120, y0 + 455), c0)
        sd.text((x0 + 190, y0 + 465), nm.replace("badge-", ""), font=font,
                fill=(15, 15, 15) if row == 0 else (245, 245, 245))
sheet.save(OUT / "badge-preview.jpg", quality=90)
print("badges done")

# main profile picture = yellow badge (stands out in both light and dark mode)
Image.open(OUT / "badge-yellow.png").save(OUT / "profile-picture.png")
