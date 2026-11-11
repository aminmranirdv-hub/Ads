"""Make variant C the official M'RANI FAMILY brand: profile (faces arc, no overlap), banner, logo, title card."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
ns = {"__file__": os.path.join(HERE, "make_variants.py")}
exec(open("make_variants.py").read().split("FRED, LIL =")[0], ns)
logo, rays, face, SIB = ns["logo"], ns["rays"], ns["face"], ns["SIB"]
LIL = "fonts/lilita-one-latin-400-normal.woff"; ROOT = ".."
mk = lambda w: logo(w, LIL, ["#FFD84D", SIB["amir"], "#FF5D8F", SIB["aziza"]], "#1B3A8F", True, "#FFFFFF", "#1B3A8F")
for a, b in [("youtube-profile-800.jpg", "youtube-profile-800-A.jpg"), ("youtube-banner-2560x1440.jpg", "youtube-banner-2560x1440-A.jpg"), ("title-card-1920x1080.jpg", "title-card-1920x1080-A.jpg"), ("logo.png", "logo-A.png")]:
    if os.path.exists(a) and not os.path.exists(b): os.replace(a, b)
P = rays(800, "#7FD3FF", "#5FC0F5"); d = ImageDraw.Draw(P); d.ellipse((22, 22, 778, 778), outline="#FFFFFF", width=16)
S = 140
for (who, idx), (x, y) in zip([("abdel-hamid", 4), ("amir", 0), ("hicham", 1), ("aziza", 1)], [(92, 210), (250, 112), (420, 112), (578, 210)]):
    f, m = face(f"{ROOT}/characters/{who}/model-sheet-A.jpg", idx, S)
    d.ellipse((x - 9, y - 9, x + S + 9, y + S + 9), fill="#FFFFFF"); P.paste(f, (x, y), m)
P.alpha_composite(mk(660), (70, 375)); P.convert("RGB").save("youtube-profile-800.jpg", quality=92)
Image.open("youtube-banner-2560x1440-C.jpg").save("youtube-banner-2560x1440.jpg", quality=92)
mk(1000).save("logo.png")
g = Image.open(f"{ROOT}/team-group-shot-A.jpg").convert("RGB")
Tc = g.resize((1920, int(1920 * g.height / g.width))).convert("RGBA"); Tc = Tc.crop((0, (Tc.height - 1080) // 2, 1920, (Tc.height - 1080) // 2 + 1080))
grad = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); gd = ImageDraw.Draw(grad)
for yy in range(380): gd.line((0, yy, 1920, yy), fill=(27, 58, 143, int(150 * (1 - yy / 380))))
Tc.alpha_composite(grad); Tc.alpha_composite(mk(600), (40, 20)); Tc.convert("RGB").save("title-card-1920x1080.jpg", quality=92)
print("ok")
