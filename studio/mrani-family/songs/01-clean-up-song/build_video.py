# "Tidy Team!" music video: animated clips cut to the song, karaoke lyrics, counting pops, end card.
# usage: python3 build_video.py [preview_seconds...]
import json, os, sys, math, subprocess, re, numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); W, H, FPS = 1920, 1080, 24
ART = f"{HERE}/../../channel-art"; WORK = f"{HERE}/work"; os.makedirs(WORK, exist_ok=True)
FONT = f"{ART}/fonts/lilita-one-latin-400-normal.woff"; NAVY = (27, 58, 143)
SONG = f"{HERE}/tidy-team-song-v1.mp3"; SONG_LEN = 148.9
EP1CLIPS = f"{HERE}/../../ep01/anim/clips"

# ---------- edit decision list (song seconds) ----------
EDL = [  # t0, t1, clip, start offset in clip
 (0.0, 5.6, "intro_messy", 0), (5.6, 11.6, "ready", 0),
 (11.6, 16.6, "dance_a", 0), (16.6, 21.4, "dance_b", 0), (21.4, 25.4, "dance_a", 1.0), (25.4, 29.9, "dance_b", .5),
 (29.9, 34.4, "ready", 1.5),
 (34.4, 39.4, "aziza_books", 0), (39.4, 43.0, "dance_a", 2.0), (43.0, 48.2, "aziza_books", 2.5), (48.2, 52.6, "dance_b", 1.0),
 (52.6, 57.6, "amir_basket", 0), (57.6, 61.0, "dance_a", 3.0), (61.0, 66.0, "amir_basket", 0), (66.0, 74.0, "dance_b", 0),
 (74.0, 79.0, "abd_crumbs", 0), (79.0, 82.5, "dance_a", 1.5), (82.5, 87.6, "abd_crumbs", 0), (87.6, 91.0, "abd_crumbs", 2.5),
 (91.0, 95.0, "dance_b", 2.0),
 (95.0, 100.0, "hicham_blocks", 0), (100.0, 104.0, "dance_a", 0.5), (104.0, 108.6, "hicham_blocks", 0), (108.6, 112.3, "ready", 0),
 (112.3, 117.3, "highfive", 0), (117.3, 122.3, "counting", 0), (122.3, 128.5, "final_dance", 0),
 (128.5, 133.5, "dance_a", 0), (133.5, 138.5, "highfive", 0), (138.5, 143.5, "dance_b", 0), (143.5, 149.0, "final_dance", 0),
 (149.0, 152.4, "EP1:hicham_false", 0), (152.4, 158.4, "ENDCARD", 0),
]
END = 158.4
# ---------- karaoke lyrics from the word timings (with ASR fixes) ----------
FIX = {"hammer": "Amir", "grow": "go", "Tablets": "Tablet's"}
segs = json.load(open(f"{HERE}/song-transcript.json"))
LINES = []
for s in segs:
    words = []
    for w in s["words"]:
        t = w["w"].strip(); core = re.sub(r"[^\w']", "", t)
        if core in FIX: t = t.replace(core, FIX[core])
        words.append((t, w["s"], w["e"]))
    if s["text"].strip().startswith("Ball goes"): words = [(t if t.strip(",") != "go" else "GOAL!", a, b) for t, a, b in words]
    LINES.append((s["start"], s["end"] + .35, words))
COUNT = [(w[1], w[0]) for l in LINES if "count" in " ".join(x[0] for x in l[2]).lower() or "five" in " ".join(x[0] for x in l[2]).lower()
         for w in [(x[0].strip(",.!").lower(), x[1]) for x in l[2]] if w[0] in ("one", "two", "three", "four", "five")]
COUNT = [(t, w) for t, w in COUNT if 116 < t < 122]          # only the bridge count gets big numbers
NUMCOL = {"one": (255, 93, 143), "two": (255, 138, 31), "three": (255, 216, 77), "four": (79, 195, 255), "five": (168, 107, 255)}

_cl = {}
def frames(name):
    if name not in _cl:
        if len(_cl) >= 4: _cl.pop(next(iter(_cl)))
        p = f"{EP1CLIPS}/{name[4:]}.mp4" if name.startswith("EP1:") else f"{HERE}/clips/{name}.mp4"
        w, h = [int(v) for v in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                               "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip().split(",")]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        _cl[name] = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
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

def frame(i):
    t = i / FPS
    seg = next((e for e in EDL if e[0] <= t < e[1]), EDL[-1]); t0, t1, name, off = seg; lt = t - t0
    if name == "ENDCARD":
        global END_BG
        if END_BG is None:
            END_BG = Image.open(f"{HERE}/stills/clean_highfive.png").convert("RGB").resize((W, H), Image.LANCZOS)
            END_BG = ImageEnhance.Brightness(END_BG).enhance(.75)
        img = END_BG.copy().convert("RGBA"); d = ImageDraw.Draw(img)
        s = ease(lt / .5); lg = LOGO.resize((int(LOGO.width * 2.4 * s) + 1, int(LOGO.height * 2.4 * s) + 1))
        img.alpha_composite(lg, ((W - lg.width) // 2, 140))
        if lt > .6:
            f = font(84); txt = "SUBSCRIBE for more songs!"; bw = f.getbbox(txt, stroke_width=8)[2]
            d.text(((W - bw) // 2, 640), txt, font=f, fill=(255, 216, 77), stroke_width=8, stroke_fill=NAVY)
        if lt > 1.0:
            f = font(60); txt = "Next song: Brush Your Teeth with Hicham!"; bw = f.getbbox(txt, stroke_width=6)[2]
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
    if t < .5: a *= t / .5
    if t > END - .6: a *= max(0, (END - t) / .6)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(img)
    if t < 149: img.alpha_composite(LOGO, (W - LOGO.width - 30, 24))
    if .8 < t < 5.0:   # song title
        s = ease((t - .8) / .4); al = min(1, (5.0 - t) / .3)
        f = font(int(130 * s) + 1); txt = "TIDY TEAM!"; bw = f.getbbox(txt, stroke_width=10)[2]
        d.text(((W - bw) // 2, 110), txt, font=f, fill=(255, 216, 77, int(255 * al)), stroke_width=10, stroke_fill=NAVY + (int(255 * al),))
        if s >= 1:
            f2 = font(54); t2 = "The M'Rani Family Clean Up Song"; bw = f2.getbbox(t2, stroke_width=6)[2]
            d.text(((W - bw) // 2, 270), t2, font=f2, fill=(255, 255, 255, int(255 * al)), stroke_width=6, stroke_fill=NAVY + (int(255 * al),))
    for tn, w in COUNT:   # big counting numbers
        if tn <= t < tn + .9:
            p = (t - tn) / .9; s = 1 + .5 * math.sin(math.pi * min(1, p * 2)) if p < .5 else 1.0
            num = str(["one", "two", "three", "four", "five"].index(w) + 1); f = font(int(300 * s))
            bw = f.getbbox(num, stroke_width=14); al = int(255 * min(1, (1 - p) / .3))
            x = W // 2 - 520 + 260 * (int(num) - 1) - (bw[2] - bw[0]) // 2
            d.text((x, 300), num, font=f, fill=NUMCOL[w] + (al,), stroke_width=14, stroke_fill=NAVY + (al,))
    if t < 149: karaoke(d, t)
    return img.convert("RGB")

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
    fc = ("[0:a]aresample=48000,volume='if(between(t,87.7,90.6),0.35,1)':eval=frame[song];"
          "[1:a]aresample=48000,adelay=88000|88000,volume=1.6[v1];[2:a]aresample=48000,adelay=149200|149200,volume=1.6[v2];"
          "[3:a]adelay=151600|151600,volume=0.8[b];[song][v1][v2][b]amix=inputs=4:normalize=0,apad,atrim=0:%s,"
          "afade=t=out:st=%s:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11[out]" % (END, END - 1.2))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", SONG, "-i", f"{HERE}/vo/abd_fun.mp3", "-i", f"{HERE}/vo/hicham_end.mp3",
                    "-i", boing, "-filter_complex", fc, "-map", "[out]", out], check=True)
    return out

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for s in sys.argv[1:]: frame(int(float(s) * FPS)).save(f"{WORK}/prev_{s}.jpg", quality=88)
        sys.exit()
    mix = audio(); NF = int(END * FPS); n = 4; cuts = [NF * k // n for k in range(n + 1)]
    with Pool(n) as p: outs = p.map(chunk, [(k, cuts[k], cuts[k + 1]) for k in range(n)])
    open(f"{WORK}/list.txt", "w").write("".join(f"file '{o}'\n" for o in outs))
    final = f"{HERE}/mrani-family-tidy-team-clean-up-song.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{WORK}/list.txt", "-i", mix,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    print("done", final)
