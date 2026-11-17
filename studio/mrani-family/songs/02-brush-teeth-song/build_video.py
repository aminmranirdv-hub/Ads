# "Sparkle Smile!" music video: animated clips cut to the song, karaoke lyrics, counting pops, end card.
# usage: python3 build_video.py [preview_seconds...]
import json, os, sys, math, subprocess, re, numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); W, H, FPS = 1920, 1080, 24
ART = f"{HERE}/../../channel-art"; WORK = f"{HERE}/work"; os.makedirs(WORK, exist_ok=True)
FONT = f"{ART}/fonts/lilita-one-latin-400-normal.woff"; NAVY = (27, 58, 143)
SONG = f"{HERE}/sparkle-smile-song-v1.mp3"; SONG_LEN = 150.0
EP1CLIPS = f"{HERE}/../../ep01/anim/clips"

# ---------- edit decision list (song seconds) ----------
EDL = [  # t0, t1, clip, start offset in clip (song seconds)
 (0.0, 5.2, "intro_hicham", 0), (5.2, 10.6, "ready", 0),
 (10.6, 15.6, "chorus_brush", 0), (15.6, 20.6, "chorus_dance", 0), (20.6, 25.0, "chorus_brush", 2.0), (25.0, 29.4, "chorus_dance", 1.0), (29.4, 31.8, "ready", 2.5),
 (31.8, 36.6, "aziza_paste", 0), (36.6, 41.4, "aziza_paste", 0.3), (41.4, 47.4, "aziza_paste", 1.9), (47.4, 53.6, "chorus_dance", 0),
 (53.6, 58.6, "amir_brush", 0), (58.6, 62.6, "chorus_brush", 3.0), (62.6, 66.7, "amir_brush", 0.3), (66.7, 73.0, "ready", 0.5), (73.0, 76.2, "ready", 1.5),
 (76.2, 81.2, "chorus_brush", 0), (81.2, 86.2, "chorus_dance", 0), (86.2, 90.0, "chorus_brush", 2.5), (90.0, 94.4, "chorus_dance", 1.0), (94.4, 97.5, "ready", 0),
 (97.5, 102.5, "abd_brush", 0), (102.5, 107.0, "abd_brush", 1.5),
 (107.0, 112.0, "hicham_tongue", 0), (112.0, 115.5, "hicham_tongue", 1.6), (115.5, 119.6, "intro_hicham", 2.4),
 (119.6, 124.6, "counting", 0), (124.6, 130.4, "counting", 0.5),
 (130.4, 135.4, "chorus_dance", 0), (135.4, 140.4, "chorus_brush", 0), (140.4, 145.4, "final_smile", 0), (145.4, 150.0, "chorus_dance", 1.5),
 (150.0, 151.9, "final_smile", 3.0), (151.9, 155.0, "intro_hicham", 2.8), (155.0, 161.0, "ENDCARD", 0),
]
SONG_END = 161.0
# ---------- character introduction (before the song) ----------
INTRO = 8.0
INTRO_SEGS = [(0.0, 2.0, "aziza_paste", 3.0, "AZIZA", "The Big Sister", (168, 107, 255)),
              (2.0, 4.0, "abd_brush", 3.4, "ABDEL-HAMID", "The Sleepy Genius", (255, 216, 77)),
              (4.0, 6.0, "amir_brush", 0.6, "AMIR", "The Football Star", (255, 138, 31)),
              (6.0, 8.0, "hicham_tongue", 3.4, "HICHAM", "The Sparkle Captain", (79, 195, 255))]
REEL_CUT = (31.6, 119.6)   # reel: intro + first chorus, then counting bridge -> end
END = SONG_END + INTRO
# ---------- karaoke lyrics from the word timings (with ASR fixes) ----------
FIX = {"up": "-a", "heat": "hee!"}
segs = json.load(open(f"{HERE}/song-transcript.json"))
LINES = []
for s in segs:
    words = []
    for w in s["words"]:
        t = w["w"].strip(); core = re.sub(r"[^\w']", "", t)
        if core in FIX: t = t.replace(core, FIX[core])
        words.append((t, w["s"], w["e"]))
    words = [(("Brush-a," if t.strip(",") == "Brush" and k + 1 < len(words) and words[k + 1][0].strip(",") == "-a" else t), a, b) for k, (t, a, b) in enumerate(words)]
    words = [w for w in words if w[0].strip(",") != "-a"]
    if s["text"].strip() == "Go!": words = [("GOAL!", a, b) for t, a, b in words]
    LINES.append((s["start"], s["end"] + .35, words))
NUMS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
COUNT = [(x[1], x[0].strip(",.!").lower()) for l in LINES for x in l[2] if 121.9 < x[1] < 126.6 and x[0].strip(",.!").lower() in NUMS]
_PAL = [(255, 93, 143), (255, 138, 31), (255, 216, 77), (79, 195, 255), (168, 107, 255)]
NUMCOL = {n: _PAL[k % 5] for k, n in enumerate(NUMS)}

_cl = {}
MAXLEN = {"amir_brush": 3.4}   # frame-check: extra arms appear after 3.4 s in this clip
ALIAS = {"final_smile": "chorus_dance", "counting": "chorus_brush"}   # stand-in until the Kling 4.0 finale shot is ready
def frames(name):
    if not name.startswith("EP1:") and not os.path.exists(f"{HERE}/clips_k40/{name}.mp4") and name in ALIAS: name = ALIAS[name]
    if name not in _cl:
        if len(_cl) >= 4: _cl.pop(next(iter(_cl)))
        p = f"{EP1CLIPS}/{name[4:]}.mp4" if name.startswith("EP1:") else (f"{HERE}/clips_k40/{name}.mp4" if os.path.exists(f"{HERE}/clips_k40/{name}.mp4") else f"{HERE}/clips/{name}.mp4")
        w, h = [int(v) for v in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                               "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip().split(",")]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        _cl[name] = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)[:int(MAXLEN.get(name, 99) * FPS)]
    return _cl[name]
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
_f = {}
def font(sz):
    if sz not in _f: _f[sz] = ImageFont.truetype(FONT, sz)
    return _f[sz]
LOGO = Image.open(f"{ART}/logo.png").convert("RGBA"); LOGO = LOGO.resize((230, int(LOGO.height * 230 / LOGO.width)), Image.LANCZOS)
END_BG = None

def karaoke(d, t):
    for a, b, words in LINES:
        if not (a - .15 <= t < b): continue
        sz = 76; f = font(sz); sp = 22
        ws = [f.getbbox(w, stroke_width=8) for w, _, _ in words]; widths = [x[2] - x[0] for x in ws]
        total = sum(widths) + sp * (len(words) - 1)
        if total > W - 120: sz = int(sz * (W - 120) / total); f = font(sz); widths = [f.getbbox(w, stroke_width=8)[2] for w, _, _ in words]; total = sum(widths) + sp * (len(words) - 1)
        x = (W - total) // 2; y0 = H - 150
        al = min(1, (t - a + .15) / .2, (b - t) / .2)
        for (w, ws_, we), wd in zip(words, widths):
            on = ws_ <= t; cur = ws_ <= t < we + .08
            col = (255, 216, 77) if on else (255, 255, 255)
            dy = -14 * math.sin(math.pi * min(1, (t - ws_) / .25)) if cur else 0
            d.text((x, y0 + dy), w, font=f, fill=col + (int(255 * al),), stroke_width=8, stroke_fill=NAVY + (int(255 * al),))
            x += wd + sp
        break

def song_frame(t):
    seg = next((e for e in EDL if e[0] <= t < e[1]), EDL[-1]); t0, t1, name, off = seg; lt = t - t0
    if name == "ENDCARD":
        global END_BG
        if END_BG is None:
            END_BG = Image.open(f"{HERE}/stills/group_smile.png").convert("RGB").resize((W, H), Image.LANCZOS)
            END_BG = ImageEnhance.Brightness(END_BG).enhance(.75)
        img = END_BG.copy().convert("RGBA"); d = ImageDraw.Draw(img)
        s = ease(lt / .5); lg = LOGO.resize((int(LOGO.width * 2.4 * s) + 1, int(LOGO.height * 2.4 * s) + 1))
        img.alpha_composite(lg, ((W - lg.width) // 2, 140))
        if lt > .6:
            f = font(84); txt = "SUBSCRIBE for more songs!"; bw = f.getbbox(txt, stroke_width=8)[2]
            d.text(((W - bw) // 2, 640), txt, font=f, fill=(255, 216, 77), stroke_width=8, stroke_fill=NAVY)
        if lt > 1.0:
            f = font(60); txt = "Next song: Amir's Counting Football Song!"; bw = f.getbbox(txt, stroke_width=6)[2]
            d.text(((W - bw) // 2, 770), txt, font=f, fill="white", stroke_width=6, stroke_fill=NAVY)
        a = np.asarray(img.convert("RGB"), np.float32)
    else:
        fr = frames(name); n = len(fr); L = n / FPS
        tc = off + lt; k = int(tc // L); within = tc - k * L
        if k % 2 == 1: within = L - 1 / FPS - within                     # ping-pong for longer holds
        im = Image.fromarray(fr[min(n - 1, int(within * FPS))])
        iw, ih = im.size; z = 1.0 + .05 * ease(lt / max(1, t1 - t0))     # gentle push-in
        cw = min(iw, ih * 16 / 9) / z; ch = cw * 9 / 16
        x0 = (iw - cw) / 2; y0 = (ih - ch) / 2
        im = im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        im = ImageEnhance.Color(im).enhance(1.12)                            # brighter toddler look
        a = np.asarray(im, np.float32)
        if lt < .12 and t0 > 0: a = a + (255 - a) * (1 - lt / .12) * .35     # soft flash on each cut (beat feel)
    if t < .15: a = a + (255 - a) * (1 - t / .15) * .5
    if t > SONG_END - .6: a *= max(0, (SONG_END - t) / .6)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(img)
    if t < 150: img.alpha_composite(LOGO, (W - LOGO.width - 30, 24))
    if .8 < t < 5.0:   # song title
        s = ease((t - .8) / .4); al = min(1, (5.0 - t) / .3)
        f = font(int(130 * s) + 1); txt = "SPARKLE SMILE!"; bw = f.getbbox(txt, stroke_width=10)[2]
        d.text(((W - bw) // 2, 110), txt, font=f, fill=(255, 216, 77, int(255 * al)), stroke_width=10, stroke_fill=NAVY + (int(255 * al),))
        if s >= 1:
            f2 = font(54); t2 = "The M'Rani Family Brush Your Teeth Song"; bw = f2.getbbox(t2, stroke_width=6)[2]
            d.text(((W - bw) // 2, 270), t2, font=f2, fill=(255, 255, 255, int(255 * al)), stroke_width=6, stroke_fill=NAVY + (int(255 * al),))
    for tn, w in COUNT:   # big counting numbers
        if tn <= t < tn + .9:
            p = (t - tn) / .9; s = 1 + .5 * math.sin(math.pi * min(1, p * 2)) if p < .5 else 1.0
            num = str(NUMS.index(w) + 1); f = font(int(320 * s))
            bw = f.getbbox(num, stroke_width=14); al = int(255 * min(1, (1 - p) / .3))
            x = W // 2 - (bw[2] - bw[0]) // 2
            d.text((x, 300), num, font=f, fill=NUMCOL[w] + (al,), stroke_width=14, stroke_fill=NAVY + (al,))
    if t < 150: karaoke(d, t)
    return img.convert("RGB")

def intro_frame(t, text=True):
    seg = next((e for e in INTRO_SEGS if e[0] <= t < e[1]), INTRO_SEGS[-1]); t0, t1, name, off, nm, tag, col = seg; lt = t - t0
    fr = frames(name); n = len(fr); im = Image.fromarray(fr[min(n - 1, int((off + lt * .8) * FPS))]); iw, ih = im.size
    z = 1.06 + .06 * ease(lt / 2); cw = min(iw, ih * 16 / 9) / z; ch = cw * 9 / 16
    im = im.resize((W, H), Image.BICUBIC, box=((iw - cw) / 2, (ih - ch) / 2, (iw + cw) / 2, (ih + ch) / 2))
    a = np.asarray(ImageEnhance.Color(im).enhance(1.12), np.float32)
    if lt < .12: a = a + (255 - a) * (1 - lt / .12) * .45
    if t < .4: a *= t / .4
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(img)
    if not text: return img.convert("RGB")
    img.alpha_composite(LOGO, (W - LOGO.width - 30, 24))
    s = ease(lt / .35); bounce = 1 + .12 * math.sin(math.pi * min(1, lt / .35))
    f = font(int(170 * bounce)); bw = f.getbbox(nm, stroke_width=14)[2]; x = int(90 - 900 * (1 - s))
    d.text((x, 640), nm, font=f, fill=col, stroke_width=14, stroke_fill=NAVY)
    if lt > .25:
        f2 = font(66); tb = f2.getbbox(tag); pw = tb[2] - tb[0] + 60
        d.rounded_rectangle((x + 10, 850, x + 10 + pw, 950), radius=50, fill=NAVY + (235,))
        d.text((x + 40, 862), tag, font=f2, fill="white")
    return img.convert("RGB")

def frame(i):
    t = i / FPS
    return intro_frame(t) if t < INTRO else song_frame(t - INTRO)

def chunk(args):
    k, a, b = args; out = f"{WORK}/chunk{k}.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(a, b): pr.stdin.write(frame(i).tobytes())
    pr.stdin.close(); pr.wait(); return out

def audio():
    out = f"{WORK}/mix.wav"
    # song, ducked under two spoken lines; Abdel-Hamid at 88.0 s, Hicham at 149.2 s; boing at 151.6 s
    boing = f"{WORK}/boing.wav"
    sr = 48000; s = np.arange(int(.5 * sr)) / sr; f = 260 * (1 + 1.2 * np.exp(-s * 9) * np.sin(2 * np.pi * 14 * s))
    b = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-s * 6) * .5
    import soundfile as sf; sf.write(boing, b, sr)
    jingle = f"{WORK}/intro.wav"; N = int(INTRO * sr); j = np.zeros(N)
    def tone(fq, d, dec=5):
        tt = np.arange(int(d * sr)) / sr; return sum(np.sin(2 * np.pi * fq * k * tt) * .55 ** k for k in range(1, 4)) * np.exp(-tt * dec)
    beat = 60 / 112; notes = [523, 659, 784, 659, 587, 698, 880, 698, 523, 659, 784, 1047, 784, 659, 523, 392]
    for k in range(int(INTRO / (beat / 2))):
        st = int(k * beat / 2 * sr); x = tone(notes[k % len(notes)], .35, 9) * .18; j[st:st + len(x)] += x[:max(0, N - st)]
        if k % 2 == 0: x = tone([131, 98, 110, 87][(k // 8) % 4], .5, 6) * .25; j[st:st + len(x)] += x[:max(0, N - st)]
    for c in range(4):
        st = int(c * 2 * sr); tt = np.arange(int(1.2 * sr)) / sr; x = (np.sin(2 * np.pi * 1318 * tt) + .4 * np.sin(2 * np.pi * 1760 * tt)) * np.exp(-tt * 4) * .35
        j[st:st + len(x)] += x[:max(0, N - st)]
    j[-int(.3 * sr):] *= np.linspace(1, .3, int(.3 * sr)); sf.write(jingle, j.astype(np.float32), sr)
    D = int(INTRO * 1000)
    fc = ("[0:a]aresample=48000,adelay=%d|%d[song];"
          "[1:a]aresample=48000,adelay=%d|%d,volume=1.6[v1];[2:a]aresample=48000,adelay=%d|%d,volume=1.6[v2];"
          "[3:a]adelay=%d|%d,volume=0.8[b];[4:a]aresample=48000,volume=1.0[j];[song][v1][v2][b][j]amix=inputs=5:normalize=0,apad,atrim=0:%s,"
          "afade=t=out:st=%s:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11[out]" % (D, D, 150200 + D, 150200 + D, 152100 + D, 152100 + D, 154600 + D, 154600 + D, END, END - 1.2))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", SONG, "-i", f"{HERE}/vo/aziza_goodnight.mp3", "-i", f"{HERE}/vo/hicham_end.mp3",
                    "-i", boing, "-i", jingle, "-filter_complex", fc, "-map", "[out]", out], check=True)
    return out

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for s in sys.argv[1:]: frame(int(float(s) * FPS)).save(f"{WORK}/prev_{s}.jpg", quality=88)
        sys.exit()
    mix = audio(); NF = int(END * FPS); n = 4; cuts = [NF * k // n for k in range(n + 1)]
    with Pool(n) as p: outs = p.map(chunk, [(k, cuts[k], cuts[k + 1]) for k in range(n)])
    open(f"{WORK}/list.txt", "w").write("".join(f"file '{o}'\n" for o in outs))
    final = f"{HERE}/mrani-family-sparkle-smile-brush-teeth-song.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{WORK}/list.txt", "-i", mix,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    print("done", final)
