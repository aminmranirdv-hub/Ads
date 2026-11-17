# M'RANI FAMILY Ep.2 "The Case of the Missing Cookie": 16:9 episode builder.
# usage: python3 build_episode.py            -> full render
#        python3 build_episode.py 12.5 40    -> preview stills at those seconds
import os, sys, math, subprocess, json
import numpy as np, soundfile as sf
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.dirname(HERE)
ART = f"{EP}/../channel-art"; WORK = f"{HERE}/work"; os.makedirs(WORK, exist_ok=True)
W, H, FPS, SR = 1920, 1080, 24, 48000
NAVY = (27, 58, 143); FONT = f"{ART}/fonts/lilita-one-latin-400-normal.woff"
CL, LS, ST, AU, VO = f"{HERE}/clips", f"{HERE}/ls_out", f"{EP}/stills", f"{HERE}/audio", f"{HERE}/vo"
SPK = {"s1a":"AZI","s1c":"AZI","s1h":"AZI","s1b":"AMI","s1d":"AMI","s1e":"ABD","s1g":"ABD","s1f":"HIC","s2e":"HIC","s3a":"ABD","s3b":"AZI",
       "s3c":"AMI","s3d":"HIC","s4a":"AMI","s4d":"ABD","s4b":"AZI","s4c":"AZI","s4e":"AZI","s5a":"HIC",
       "c1":"AZI","c2":"AZI","s2a":"AZI","s2b":"AMI","s2c":"ABD","s2d":"HIC","s2f":"AZI","s2g":"AMI","s2h":"ABD","s1i":"ALL","s5b":"ALL"}
PRE = 0.20   # silence before speech in every lip-sync clip
CROP = {"s4b", "s4c", "s4e"}   # lip-synced on an Aziza-only crop, pasted back over the full frame

def vo_path(k, spk=None): return f"{VO}/{k}_{spk or SPK[k]}.wav"
def adur(p): return sf.info(p).duration
def line_len(k): return max(adur(vo_path(k, s)) for s in ("AZI", "ABD", "AMI", "HIC")) if SPK[k] == "ALL" else adur(vo_path(k))

# ---------------------------------------------------------------- shot list
# kinds: clip (file, start, dur, speed), still (file, dur, motion), ls (line key), title, names, endcard
# each shot may carry lines [(key, offset)], sfx [(name, offset, gain)], trans ("cut"|"wipe"|"whip"|"flash")
def LSHOT(k, tail=0.30, **kw):
    d = PRE + line_len(k) + tail; p = f"{LS}/{k}.mp4"
    if os.path.exists(p): d = min(d, float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout) - 0.02)
    return dict(kind="ls", key=k, dur=d, lines=[(k, PRE)], **kw)
SHOTS = [
 # COLD OPEN
 dict(kind="still", file="jar_full", dur=4.4, motion="push", lines=[("c1", 0.35)]),
 dict(kind="still", file="jar_empty", dur=3.5, motion="shake", lines=[("c2", 0.15)], sfx=[("sting", 0.0, .8)], trans="flash"),
 # TITLE + MEET THE FAMILY
 dict(kind="title", dur=3.2, sfx=[("whoosh", 0.0, .7)], trans="wipe"),
 dict(kind="names", dur=8.0, trans="cut"),
 # SCENE 1: the crime scene
 LSHOT("s1a", trans="wipe", sfx=[("whoosh", 0.0, .5)]),
 LSHOT("s1b"), LSHOT("s1c", tail=.25), LSHOT("s1d", tail=.15),
 LSHOT("s1e", trans="whip", sfx=[("whoosh", 0.0, .7)]),
 LSHOT("s1f"),
 dict(kind="clip", file="A_gasp", start=0.0, dur=2.6),
 LSHOT("s1g"), LSHOT("s1h"),
 dict(kind="clip", file="A_gasp", start=3.75, dur=1.25, speed=0.8, lines=[("s1i", 0.05)]),
 # SCENE 2: the investigation montage
 dict(kind="clip", file="A_magnify", start=0.0, dur=4.2, lines=[("s2a", 0.6)], trans="wipe", sfx=[("whoosh", 0.0, .5)]),
 dict(kind="clip", file="A_dive", start=0.0, dur=5.0, lines=[("s2b", 0.25)], sfx=[("flump", 0.72, .9)], trans="whip"),
 dict(kind="clip", file="A_ruler", start=0.0, dur=4.6, lines=[("s2c", 0.45)], trans="whip"),
 dict(kind="clip", file="A_hack", start=0.0, dur=3.0, lines=[("s2d", 0.2)], sfx=[("beeps", 1.2, .5)], trans="whip"),
 LSHOT("s2e"),
 dict(kind="clip", file="A_tablet_group", start=0.0, dur=3.15, lines=[("s2f", 1.5)]),
 dict(kind="screen", file="A_screen", start=0.0, dur=5.2, lines=[("s2g", 0.9), ("s2h", 3.0)]),
 # SCENE 3: the twist
 dict(kind="clip", file="A_reveal", start=0.0, dur=5.0, sfx=[("sting", 0.0, .8)], trans="flash"),
 LSHOT("s3a"), LSHOT("s3b"),
 dict(kind="robot", dur=2.8, sfx=[("burp", 0.5, 1.0), ("beeps", 1.6, .4)]),
 LSHOT("s3c"), LSHOT("s3d", tail=.5),
 # SCENE 4: making it right
 dict(kind="clip", file="A_bake_wide", start=0.0, dur=5.0, trans="wipe", sfx=[("whoosh", 0.0, .5)]),
 dict(kind="clip", file="A_stir", start=0.0, dur=2.4),
 dict(kind="clip", file="A_egg", start=0.0, dur=2.9, sfx=[("egg", 0.45, .9)]),
 LSHOT("s4a", tail=.3),
 dict(kind="clip", file="A_timer", start=0.0, dur=3.6, sfx=[("beeps", 1.0, .5)]),
 LSHOT("s4b", tail=.35), LSHOT("s4c", tail=.35),
 LSHOT("s4d", tail=.4), LSHOT("s4e", tail=.4),
 dict(kind="still", file="cookies_tray", dur=3.0, motion="push", sfx=[("ding", 0.25, .9)], trans="flash"),
 # BUTTON GAG + OUTRO
 dict(kind="clip", file="A_outro", start=0.0, dur=2.6),
 LSHOT("s5a", tail=.45),
 dict(kind="clip", file="A_outro", start=2.6, dur=2.4, lines=[("s5b", 1.0)], sfx=[("zoom", 0.35, .9)]),
 dict(kind="endcard", dur=6.0, trans="wipe", sfx=[("whoosh", 0.0, .5)]),
]
T = 0.0
for s in SHOTS:
    s.setdefault("lines", []); s.setdefault("sfx", []); s.setdefault("trans", "cut"); s["t0"] = T; T += s["dur"]; s["t1"] = T
END = T
def tl(i): return SHOTS[i]["t0"]
IDX = {}   # scene markers for music
for i, s in enumerate(SHOTS):
    if s["kind"] == "title": IDX["title"] = s["t0"]
    if s.get("key") == "s1a": IDX["s1"] = s["t0"]
    if s.get("file") == "A_magnify": IDX["s2"] = s["t0"]
    if s["kind"] == "screen": IDX["screen"] = s["t0"]
    if s.get("file") == "A_reveal": IDX["s3"] = s["t0"]
    if s.get("file") == "A_bake_wide": IDX["s4"] = s["t0"]
    if s.get("file") == "A_outro" and s["start"] > 0: IDX["chase"] = s["t0"]
    if s["kind"] == "endcard": IDX["end"] = s["t0"]

# ---------------------------------------------------------------- helpers
_f = {}
def font(sz):
    if sz not in _f: _f[sz] = ImageFont.truetype(FONT, sz)
    return _f[sz]
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
LOGO = Image.open(f"{ART}/logo.png").convert("RGBA"); LOGO = LOGO.resize((200, int(LOGO.height * 200 / LOGO.width)), Image.LANCZOS)
_vc = {}
def video(path):
    if path not in _vc:
        if len(_vc) >= 3: _vc.pop(next(iter(_vc)))
        info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                               "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split(",")
        w, h = int(info[0]), int(info[1]); a, b = info[2].split("/"); fps = int(a) / int(b)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        _vc[path] = (np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3), fps)
    return _vc[path]
def vframe(path, t):
    fr, fps = video(path); return fr[min(len(fr) - 1, max(0, int(t * fps)))]
def cover(arr, zoom=1.0, cx=.5, cy=.5, dx=0, dy=0):
    im = Image.fromarray(arr) if isinstance(arr, np.ndarray) else arr; iw, ih = im.size
    cw = min(iw, ih * 16 / 9) / zoom; ch = cw * 9 / 16
    x0 = min(max(0, (iw - cw) * cx + dx), iw - cw); y0 = min(max(0, (ih - ch) * cy + dy), ih - ch)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
_si = {}
def still(name):
    if name not in _si:
        p = f"{ST}/{name}.png" if os.path.exists(f"{ST}/{name}.png") else f"{ST}/{name}.jpg"; _si[name] = Image.open(p).convert("RGB")
    return _si[name]
FEATHER = None
def ls_frame(k, t):
    fr = vframe(f"{LS}/{k}.mp4", t)
    if k not in CROP: return fr
    global FEATHER
    base = vframe(f"{HERE}/ls_in/{k}_full.mp4", t).copy()
    if FEATHER is None:
        x = np.arange(640); FEATHER = np.clip((610 - x) / 50, 0, 1)[None, :, None].astype(np.float32)
    base[:, :640] = (fr[:, :640] * FEATHER + base[:, :640] * (1 - FEATHER)).astype(np.uint8)
    return base

def text_c(d, y, s, size, fill, sw=10, maxw=W - 160, x=None):
    f = font(size); bw = f.getbbox(s, stroke_width=sw)[2]
    if bw > maxw: f = font(int(size * maxw / bw)); bw = f.getbbox(s, stroke_width=sw)[2]
    d.text(((W - bw) // 2 if x is None else x, y), s, font=f, fill=fill, stroke_width=sw, stroke_fill=NAVY[:3] + fill[3:] if len(fill) == 4 else NAVY)

NAMES = [("T_aziza_det", 2.9, "AZIZA", "The Detective", (168, 107, 255)),
         ("T_abd_bean", 0.5, "ABDEL-HAMID", "The Lazy Genius", (255, 216, 77)),
         ("T_amir_point", 0.2, "AMIR", "The Football Star", (255, 138, 31)),
         ("A_hack", 0.4, "HICHAM", "The Little Hacker", (79, 195, 255))]

# ---------------------------------------------------------------- shot renderers
def render(s, lt, text=True):
    k = s["kind"]
    if k == "clip":
        sp = s.get("speed", 1.0); im = cover(vframe(f"{CL}/{s['file']}.mp4", s["start"] + lt * sp), 1.03 + .03 * lt / s["dur"])
    elif k == "ls":
        im = cover(ls_frame(s["key"], lt), 1.02 + .04 * ease(lt / s["dur"]))
    elif k == "still":
        img = still(s["file"])
        if s["motion"] == "push": im = cover(img, 1.04 + .10 * ease(lt / s["dur"]))
        else:
            amp = 18 * math.exp(-lt * 3.5); im = cover(img, 1.14, dx=amp * math.sin(lt * 70), dy=amp * .6 * math.cos(lt * 55))
    elif k == "screen":   # baby-camera night footage on the tablet: grainy, dark, the thief stays a mystery
        a = cover(vframe(f"{CL}/{s['file']}.mp4", s["start"] + lt * .8), 1.08 + .12 * ease(lt / s["dur"]))
        g = ImageEnhance.Contrast(ImageEnhance.Brightness(a.convert("L").filter(ImageFilter.GaussianBlur(20))).enhance(.42)).enhance(.8)
        arr = np.asarray(g, np.float32); rng = np.random.default_rng(int(lt * 100))
        arr = arr + rng.normal(0, 14, arr.shape); arr[::4] *= .78
        rgb = np.stack([arr * .55, arr * 1.0, arr * .6], -1)
        yy, xx = np.mgrid[0:H, 0:W]; vig = 1 - .55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        im = Image.fromarray(np.clip(rgb * vig[..., None], 0, 255).astype(np.uint8)).convert("RGBA")
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow); bx = 820 + 60 * lt; by = 540
        for j, (ox, ph) in enumerate(((0, 0), (70, .5))):   # two little blinking lights on the mystery shadow
            on = .5 + .5 * math.sin((lt * 3 + ph) * 2 * math.pi)
            for r, al in ((34, 60), (18, 140), (8, 255)): dg.ellipse((bx + ox - r, by - r, bx + ox + r, by + r), fill=(200, 255, 200, int(al * on)))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3))); d = ImageDraw.Draw(im)
        if int(lt * 2) % 2 == 0: d.ellipse((290, 80, 330, 120), fill=(255, 40, 40)); d.text((350, 72), "REC", font=font(52), fill=(255, 255, 255))
        d.text((W - 660, H - 148), "BABY CAM 1", font=font(52), fill=(220, 255, 220))
        d.text((290, H - 148), "02:13 AM", font=font(60), fill=(220, 255, 220))
        im = im.convert("RGB")
    elif k == "robot":
        p = f"{CL}/A_robot.mp4"
        if os.path.exists(p): im = cover(vframe(p, lt * .9), 1.04)
        else:
            amp = 10 * math.exp(-max(0, lt - .5) * 4) if lt > .5 else 0
            im = cover(still("robot_bed"), 1.06 + .08 * ease(lt / s["dur"]), dx=amp * math.sin(lt * 60))
    elif k == "title":
        bg = cover(still("jar_empty"), 1.1 + .05 * lt / s["dur"]).filter(ImageFilter.GaussianBlur(14))
        im = ImageEnhance.Brightness(bg).enhance(.55).convert("RGBA"); d = ImageDraw.Draw(im)
        b = ease(lt / .4); bo = 1 + .14 * math.sin(math.pi * min(1, lt / .4))
        text_c(d, 300, "M'RANI FAMILY MYSTERY", 74, (255, 255, 255, int(255 * b)), 8)
        f = font(int(150 * bo)); txt = "THE CASE OF THE"; bw = f.getbbox(txt, stroke_width=12)[2]
        d.text(((W - bw) // 2, 410), txt, font=f, fill=(255, 216, 77, int(255 * b)), stroke_width=12, stroke_fill=NAVY + (int(255 * b),))
        if lt > .35:
            b2 = ease((lt - .35) / .35); bo2 = 1 + .16 * math.sin(math.pi * min(1, (lt - .35) / .35))
            f = font(int(190 * bo2)); txt = "MISSING COOKIE!"; bw = f.getbbox(txt, stroke_width=14)[2]
            d.text(((W - bw) // 2, 590), txt, font=f, fill=(255, 138, 31, int(255 * b2)), stroke_width=14, stroke_fill=NAVY + (int(255 * b2),))
        im = im.convert("RGB")
    elif k == "names":
        j = min(3, int(lt // 2)); clip, off, nm, tag, col = NAMES[j]; nt = lt - 2 * j
        im = cover(vframe(f"{CL}/{clip}.mp4", off + nt * (.3 if j == 0 else .7)), 1.06 + .06 * ease(nt / 2))
        a = np.asarray(ImageEnhance.Color(im).enhance(1.1), np.float32)
        if nt < .12: a = a + (255 - a) * (1 - nt / .12) * .45
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
        sc = ease(nt / .35); bo = 1 + .12 * math.sin(math.pi * min(1, nt / .35))
        f = font(int(170 * bo)); x = int(90 - 900 * (1 - sc))
        d.text((x, 640), nm, font=f, fill=col, stroke_width=14, stroke_fill=NAVY)
        if nt > .25:
            f2 = font(66); tb = f2.getbbox(tag); pw = tb[2] - tb[0] + 60
            d.rounded_rectangle((x + 10, 850, x + 10 + pw, 950), radius=50, fill=NAVY + (235,)); d.text((x + 40, 862), tag, font=f2, fill="white")
        text_c(d, 70, "MEET THE FAMILY!", 80, (255, 255, 255), 8)
        im = im.convert("RGB")
    elif k == "endcard":
        bg = cover(still("outro_group"), 1.05 + .04 * lt / s["dur"]).filter(ImageFilter.GaussianBlur(10))
        im = ImageEnhance.Brightness(bg).enhance(.6).convert("RGBA"); d = ImageDraw.Draw(im)
        b = ease(lt / .4); bo = 1 + .1 * math.sin(math.pi * min(1, lt / .4))
        lg = LOGO.resize((int(LOGO.width * 2.2 * (.6 + .4 * b)), int(LOGO.height * 2.2 * (.6 + .4 * b)))); im.alpha_composite(lg, ((W - lg.width) // 2, 70))
        text_c(d, 470, "SUBSCRIBE!", int(150 * bo), (255, 216, 77, int(255 * b)), 13)
        if lt > .6:
            b2 = ease((lt - .6) / .4)
            text_c(d, 700, "NEXT EPISODE:", 70, (255, 255, 255, int(255 * b2)), 8)
            text_c(d, 790, "Strange Noises at Midnight 👀".replace(" 👀", "..."), 110, (79, 195, 255, int(255 * b2)), 11)
        im = im.convert("RGB")
    if text and k not in ("title", "names", "endcard", "screen"):
        im = im.convert("RGBA"); im.alpha_composite(LOGO, (W - LOGO.width - 28, 22)); im = im.convert("RGB")
    return im

def frame(i):
    t = i / FPS
    si = next((j for j, s in enumerate(SHOTS) if s["t0"] <= t < s["t1"]), len(SHOTS) - 1); s = SHOTS[si]; lt = t - s["t0"]
    im = render(s, lt)
    tr = s["trans"]
    if si > 0 and tr != "cut":
        p = SHOTS[si - 1]; D = {"wipe": .55, "whip": .28, "flash": .25}[tr]
        if lt < D:
            x = lt / D
            if tr == "wipe":   # magnifying-glass iris: new shot opens inside a growing lens ring
                prev = render(p, p["dur"] - 1 / FPS); r = ease(x) * 1250
                mask = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(mask); dm.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=255)
                im = Image.composite(im, prev, mask); d = ImageDraw.Draw(im)
                if r > 20: d.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), outline=(255, 216, 77), width=26)
            elif tr == "whip":
                prev = render(p, p["dur"] - 1 / FPS); off = int(ease(x) * W)
                a = Image.new("RGB", (W, H)); a.paste(prev, (-off, 0)); a.paste(im, (W - off, 0))
                im = a.filter(ImageFilter.BoxBlur(int(40 * math.sin(math.pi * x)) + 1)) if .05 < x < .95 else a
            elif tr == "flash":
                a = np.asarray(im, np.float32); im = Image.fromarray(np.clip(a + (255 - a) * (1 - x) * .8, 0, 255).astype(np.uint8))
    if t < .4: im = Image.blend(Image.new("RGB", im.size), im, t / .4)
    if t > END - .6: im = Image.blend(Image.new("RGB", im.size), im, max(0, (END - t) / .6))
    return im

# ---------------------------------------------------------------- audio
def load(p, gain=1.0):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2) * gain
def place(buf, x, t):
    s = int(t * SR); e = min(len(buf), s + len(x)); buf[s:e] += x[:e - s]
def audio():
    N = int((END + 1) * SR); dia = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32); mus = np.zeros((N, 2), np.float32)
    talk = []
    for s in SHOTS:
        for k, off in s["lines"]:
            t = s["t0"] + off
            if SPK[k] == "ALL":   # four siblings shouting together, slightly staggered
                for j, spk in enumerate(("AZI", "ABD", "AMI", "HIC")): place(dia, load(vo_path(k, spk), .55), t + .018 * j)
            else: place(dia, load(vo_path(k), 1.0), t)
            talk.append((t, t + line_len(k)))
        for nm, off, g in s["sfx"]: place(fx, load(f"{AU}/sfx_{nm}.mp3", g * .7), s["t0"] + off)
    # music cues: (file, start, end, source offset, gain)
    CUES = [("m_warm", 0.0, IDX["title"] - 3.4, 6.0, .32),
            ("m_montage", IDX["title"], IDX["s1"], 0.0, .42),
            ("m_mystery", IDX["s1"], IDX["s2"], 0.0, .30),
            ("m_montage", IDX["s2"], IDX["screen"], 30.0, .36),
            ("m_mystery", IDX["screen"], IDX["s3"], 40.0, .26),
            ("m_mystery", IDX["s3"] + 1.2, IDX["s4"], 62.0, .26),
            ("m_warm", IDX["s4"], IDX["chase"], 20.0, .30),
            ("m_chase", IDX["chase"] - .1, END + .5, 28.0, .42)]
    for f, a, b, so, g in CUES:
        x = load(f"{AU}/{f}.mp3")[int(so * SR):int((so + b - a + .6) * SR)] * g
        n = len(x); fi = int(.35 * SR); fo = int(.6 * SR)
        env = np.ones(n, np.float32); env[:fi] = np.linspace(0, 1, fi); env[-fo:] = np.minimum(env[-fo:], np.linspace(1, 0, fo))
        place(mus, x * env[:, None], a)
    # duck music under dialogue
    duck = np.ones(N, np.float32)
    for a, b in talk: duck[max(0, int((a - .15) * SR)):int((b + .2) * SR)] = .42
    k = int(.12 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same")
    mix = dia * 1.0 + fx + mus * duck[:, None]
    tmp = f"{WORK}/ep_raw.wav"; sf.write(tmp, mix[:int(END * SR)], SR)
    out = f"{WORK}/ep_mix.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", f"afade=t=out:st={END - 1.0}:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), out], check=True)
    return out

def chunk(args):
    k, a, b = args; out = f"{WORK}/ep_chunk{k}.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(a, b): pr.stdin.write(frame(i).tobytes())
    pr.stdin.close(); pr.wait(); return out

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for x in sys.argv[1:]: frame(int(float(x) * FPS)).save(f"{WORK}/ep_prev_{x}.jpg", quality=85)
        print("END", round(END, 1)); sys.exit()
    json.dump([{k: v for k, v in s.items()} for s in SHOTS], open(f"{WORK}/edl.json", "w"), indent=1)
    mix = audio(); NF = int(END * FPS); n = 4
    # split at shot boundaries near the quarters so each worker decodes few clips
    bounds = [0] + [min((int(s["t0"] * FPS) for s in SHOTS), key=lambda f: abs(f - NF * q // n)) for q in range(1, n)] + [NF]
    with Pool(n) as p: outs = p.map(chunk, [(q, bounds[q], bounds[q + 1]) for q in range(n)])
    open(f"{WORK}/ep_list.txt", "w").write("".join(f"file '{o}'\n" for o in outs))
    final = f"{EP}/mrani-family-ep02-case-of-the-missing-cookie.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{WORK}/ep_list.txt", "-i", mix,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    print("done", final, round(END, 1))
