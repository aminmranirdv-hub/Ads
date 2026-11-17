# 9:16 versions of Ep.2 (TikTok / Reels / Shorts), composed from the finished 16:9 episode.
# usage: python3 build_vertical.py full|reel [preview_seconds...]
import os, sys, re, json, math, subprocess
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import build_episode as B
from script import LINES
W, H, FPS = 1080, 1920, B.FPS
MODE = sys.argv[1] if len(sys.argv) > 1 else "full"
SRC = f"{B.EP}/mrani-family-ep02-case-of-the-missing-cookie.mp4"
S = {}
for s in B.SHOTS:
    if s.get("key") == "s1a": S["s1"] = s["t0"]
    if s["kind"] == "title": S["title"] = s["t0"]
    if s.get("file") == "A_magnify": S["s2"] = s["t0"]
    if s.get("file") == "A_tablet_group": S["tab"] = s["t0"]
    if s["kind"] == "robot": S["robot"] = s["t0"]
    if s.get("file") == "A_outro" and s["start"] == 0: S["outro"] = s["t0"]
# reel: cold open, the crime scene, camera footage + twist, button gag + end card
PARTS = {"full": [(0.0, B.END)],
         "reel": [(0.0, S["title"]), (S["s1"], S["s2"]), (S["tab"], S["robot"]), (S["outro"], B.END)]}[MODE]
OUTLEN = sum(b - a for a, b in PARTS)
def src(t):
    for a, b in PARTS:
        if t < b - a: return a + t
        t -= b - a
    return PARTS[-1][1] - .01
VID_Y, VID_H = 470, 810
TEXT = {k: re.sub(r"\[[^\]]*\]\s*", "", txt).replace("...", "…") for k, spk, txt in LINES}
NAME = {"AZI": ("Aziza", (168, 107, 255)), "ABD": ("Abdel-Hamid", (255, 216, 77)), "AMI": ("Amir", (255, 138, 31)),
        "HIC": ("Hicham", (79, 195, 255)), "ALL": ("Everyone", (255, 255, 255))}
CAPS = []
for s in B.SHOTS:
    for k, off in s["lines"]:
        a = s["t0"] + off; CAPS.append((a - .1, a + B.line_len(k) + .25, B.SPK[k], TEXT[k]))

def wrap(d, text, f, maxw):
    rows, row = [], ""
    for w in text.split():
        t = (row + " " + w).strip()
        if row and f.getbbox(t, stroke_width=7)[2] > maxw: rows.append(row); row = w
        else: row = t
    return rows + [row]

def compose(im, T):
    bg = im.resize((int(H * 16 / 9), H)).crop((int((H * 16 / 9 - W) / 2), 0, int((H * 16 / 9 - W) / 2) + W, H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(28))).enhance(.62)
    canvas = bg.convert("RGBA")
    win = im.crop((240, 0, 1680, 1080)).resize((W, VID_H), Image.BICUBIC)
    mask = Image.new("L", win.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, VID_H - 1), 40, fill=255)
    canvas.paste(win, (0, VID_Y), mask); d = ImageDraw.Draw(canvas)
    lg = B.LOGO.resize((280, int(B.LOGO.height * 280 / B.LOGO.width))); canvas.alpha_composite(lg, ((W - lg.width) // 2, 60))
    f = B.font(92); t1 = "WHO ATE THE COOKIE?"; bw = f.getbbox(t1, stroke_width=9)[2]
    d.text(((W - bw) // 2, 300), t1, font=f, fill=(255, 216, 77), stroke_width=9, stroke_fill=B.NAVY)
    for a, b, spk, txt in CAPS:
        if a <= T < b:
            al = int(255 * min(1, (T - a) / .12, (b - T) / .12)); nm, col = NAME[spk]
            f2 = B.font(52); nb = f2.getbbox(nm)[2] + 50; x = (W - nb) // 2
            d.rounded_rectangle((x, 1330, x + nb, 1402), radius=36, fill=col + (al,)); d.text((x + 25, 1336), nm, font=f2, fill=B.NAVY + (al,))
            for sz in (76, 66, 58, 52):   # shrink long lines so the whole sentence fits in 4 rows
                f3 = B.font(sz); rows = wrap(d, txt, f3, W - 100)
                if len(rows) <= (3 if sz == 76 else 4): break
            for r, row in enumerate(rows):
                rw = f3.getbbox(row, stroke_width=7)[2]
                d.text(((W - rw) // 2, 1430 + r * int(sz * 1.28)), row, font=f3, fill=(255, 255, 255, al), stroke_width=7, stroke_fill=B.NAVY + (al,))
            break
    return canvas.convert("RGB")

def frames_of(a, b):
    """yield 16:9 frames for timeline-source interval [a, b)"""
    n = int(round((b - a) * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a:.4f}", "-i", SRC, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    for i in range(n):
        raw = p.stdout.read(1920 * 1080 * 3)
        if len(raw) < 1920 * 1080 * 3: break
        yield a + i / FPS, Image.frombytes("RGB", (1920, 1080), raw)
    p.stdout.close(); p.wait()

def chunk(args):
    k, a, b = args; out = f"{B.WORK}/v_{MODE}_{k}.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for T, im in frames_of(a, b): pr.stdin.write(compose(im, T).tobytes())
    pr.stdin.close(); pr.wait(); return out

def audio():
    o = f"{B.WORK}/v_mix_{MODE}.wav"; ins = []; fc = ""
    for j, (a, b) in enumerate(PARTS):
        fc += f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={b - a - .08}:d=0.08[p{j}];"
    fc += "".join(f"[p{j}]" for j in range(len(PARTS))) + f"concat=n={len(PARTS)}:v=0:a=1,afade=t=out:st={OUTLEN - .8}:d=0.8[o]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", SRC, "-filter_complex", fc, "-map", "[o]", o], check=True)
    return o

if __name__ == "__main__":
    if len(sys.argv) > 2:
        for x in sys.argv[2:]:
            T = src(float(x)); im = next(frames_of(T, T + 1 / FPS))[1]; compose(im, T).save(f"{B.WORK}/v_{MODE}_{x}.jpg", quality=85)
        sys.exit()
    # one job per part (reel) or four quarters (full)
    jobs = PARTS if MODE == "reel" else [(B.END * q / 4, B.END * (q + 1) / 4) for q in range(4)]
    jobs = [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in jobs]
    with Pool(4) as p: outs = p.map(chunk, [(k, a, b) for k, (a, b) in enumerate(jobs)])
    open(f"{B.WORK}/vlist_{MODE}.txt", "w").write("".join(f"file '{o}'\n" for o in outs))
    aud = audio(); os.makedirs(f"{B.EP}/social", exist_ok=True)
    final = f"{B.EP}/social/missing-cookie-{'full' if MODE == 'full' else 'reel'}-9x16.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{B.WORK}/vlist_{MODE}.txt", "-i", aud,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("done", final, round(OUTLEN, 1))
