# Vertical 9:16 versions of "Sparkle Smile!" for TikTok / Facebook Reels / YouTube Shorts.
# usage: python3 build_vertical.py full|reel [preview_seconds...]
import sys, os, math, subprocess, numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import build_video as B
W, H, FPS = 1080, 1920, B.FPS
MODE = sys.argv[1] if len(sys.argv) > 1 else "full"
# output-time -> song-time map. reel = intro+chorus, then bridge+final chorus, then Hicham's tag + end card
I = B.INTRO   # timeline time = intro + song time
PARTS = {"full": [(0.0, B.END)],
         "reel": [(0.0, I + B.REEL_CUT[0]), (I + B.REEL_CUT[1], B.END)]}[MODE]
OUTLEN = sum(b - a for a, b in PARTS)
def src(t):
    for a, b in PARTS:
        if t < b - a: return a + t
        t -= b - a
    return PARTS[-1][1] - .01
VID_Y, VID_H = 470, 810          # 4:3 window keeps ~75% of the width (all four siblings in group shots)

def base(ts):
    seg = next((e for e in B.EDL if e[0] <= ts < e[1]), B.EDL[-1]); t0, t1, name, off = seg; lt = ts - t0
    if name == "ENDCARD":
        return Image.open(f"{B.HERE}/stills/group_smile.png").convert("RGB").resize((1920, 1080), Image.LANCZOS), seg, lt
    fr = B.frames(name); n = len(fr); L = n / FPS; tc = off + lt; k = int(tc // L); within = tc - k * L
    if k % 2 == 1: within = L - 1 / FPS - within
    im = Image.fromarray(fr[min(n - 1, int(within * FPS))]); iw, ih = im.size
    cw = min(iw, ih * 16 / 9); ch = cw * 9 / 16
    im = im.resize((1920, 1080), Image.BICUBIC, box=((iw - cw) / 2, (ih - ch) / 2, (iw + cw) / 2, (ih + ch) / 2))
    return ImageEnhance.Color(im).enhance(1.12), seg, lt

def text_c(d, y, s, size, fill, sw=8, maxw=W - 80):
    f = B.font(size); bw = f.getbbox(s, stroke_width=sw)[2]
    if bw > maxw: f = B.font(int(size * maxw / bw)); bw = f.getbbox(s, stroke_width=sw)[2]
    d.text(((W - bw) // 2, y), s, font=f, fill=fill, stroke_width=sw, stroke_fill=B.NAVY)

def karaoke(d, ts):
    for a, b, words in B.LINES:
        if not (a - .15 <= ts < b): continue
        f = B.font(88); sp = 22; rows, row, rw = [], [], 0
        for w in words:   # wrap to 2 lines
            ww = f.getbbox(w[0], stroke_width=8)[2]
            if row and rw + ww > W - 100: rows.append(row); row, rw = [], 0
            row.append((w, ww)); rw += ww + sp
        rows.append(row)
        al = int(255 * min(1, (ts - a + .15) / .2, (b - ts) / .2))
        for ri, row in enumerate(rows):
            tot = sum(ww for _, ww in row) + sp * (len(row) - 1); x = (W - tot) // 2; y = 1375 + ri * 120
            for (w, ws, we), ww in row:
                cur = ws <= ts < we + .08; dy = -16 * math.sin(math.pi * min(1, (ts - ws) / .25)) if cur else 0
                col = (255, 216, 77) if ws <= ts else (255, 255, 255)
                d.text((x, y + dy), w, font=f, fill=col + (al,), stroke_width=8, stroke_fill=B.NAVY + (al,)); x += ww + sp
        break

def frame(i):
    t = i / FPS; T = src(t)
    if T < I: return intro_v(t, T)
    ts = T - I
    im, seg, lt = base(ts); t0, t1, name, off = seg
    bg = im.resize((W * 2, int(W * 2 * 1080 / 1920))).crop((W // 2, 0, W // 2 + W, int(W * 2 * 1080 / 1920)))
    bg = bg.resize((W, H)).filter(ImageFilter.GaussianBlur(28)); bg = ImageEnhance.Brightness(bg).enhance(.7)
    canvas = bg.convert("RGBA")
    win = im.crop((240, 0, 1680, 1080)).resize((W, VID_H), Image.BICUBIC)        # centre 4:3
    a = np.asarray(win, np.float32)
    if lt < .12 and t0 > 0 and name != "ENDCARD": a = a + (255 - a) * (1 - lt / .12) * .35
    win = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    mask = Image.new("L", win.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, VID_H - 1), 40, fill=255)
    canvas.paste(win, (0, VID_Y), mask); d = ImageDraw.Draw(canvas)
    lg = B.LOGO.resize((300, int(B.LOGO.height * 300 / B.LOGO.width))); canvas.alpha_composite(lg, ((W - lg.width) // 2, 60))
    if name == "ENDCARD":
        text_c(d, 1350, "SUBSCRIBE", 120, (255, 216, 77), 10)
        text_c(d, 1500, "for more M'Rani Family songs!", 64, (255, 255, 255), 7)
    else:
        text_c(d, 300, "SPARKLE SMILE!", 110, (255, 216, 77), 11)
        for tn, w in B.COUNT:
            if tn <= ts < tn + .9:
                p = (ts - tn) / .9; s = 1 + .5 * math.sin(math.pi * min(1, p * 2)) if p < .5 else 1.0
                num = str(B.NUMS.index(w) + 1); f = B.font(int(260 * s))
                bw = f.getbbox(num, stroke_width=14); al = int(255 * min(1, (1 - p) / .3))
                d.text(((W - (bw[2] - bw[0])) // 2, VID_Y + 200), num, font=f, fill=B.NUMCOL[w] + (al,), stroke_width=14, stroke_fill=B.NAVY + (al,))
        if ts < 150: karaoke(d, ts)
        if MODE == "reel" and t > OUTLEN - 9: text_c(d, 1295, "Full song on YouTube: M'Rani Family", 44, (255, 255, 255), 5)
    out = canvas.convert("RGB")
    if t < .3: out = Image.blend(Image.new("RGB", out.size), out, t / .3)
    if t > OUTLEN - .5: out = Image.blend(Image.new("RGB", out.size), out, max(0, (OUTLEN - t) / .5))
    return out

def compose(im):
    bg = im.resize((W * 2, int(W * 2 * 1080 / 1920))).crop((W // 2, 0, W // 2 + W, int(W * 2 * 1080 / 1920)))
    bg = ImageEnhance.Brightness(bg.resize((W, H)).filter(ImageFilter.GaussianBlur(28))).enhance(.7)
    canvas = bg.convert("RGBA"); win = im.crop((240, 0, 1680, 1080)).resize((W, VID_H), Image.BICUBIC)
    mask = Image.new("L", win.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, VID_H - 1), 40, fill=255)
    canvas.paste(win, (0, VID_Y), mask)
    lg = B.LOGO.resize((300, int(B.LOGO.height * 300 / B.LOGO.width))); canvas.alpha_composite(lg, ((W - lg.width) // 2, 60))
    return canvas

def intro_v(t, T):
    seg = next((e for e in B.INTRO_SEGS if e[0] <= T < e[1]), B.INTRO_SEGS[-1]); t0, t1, name, off, nm, tag, col = seg; lt = T - t0
    canvas = compose(B.intro_frame(T, text=False)); d = ImageDraw.Draw(canvas)
    text_c(d, 300, "MEET THE FAMILY!", 96, (255, 255, 255), 9)
    bounce = 1 + .12 * math.sin(math.pi * min(1, lt / .35)); al = int(255 * B.ease(lt / .25))
    f = B.font(int(150 * bounce)); bw = f.getbbox(nm, stroke_width=13)[2]
    if bw > W - 60: f = B.font(int(150 * bounce * (W - 60) / bw)); bw = f.getbbox(nm, stroke_width=13)[2]
    d.text(((W - bw) // 2, 1340), nm, font=f, fill=col + (al,), stroke_width=13, stroke_fill=B.NAVY + (al,))
    if lt > .25:
        f2 = B.font(62); tb = f2.getbbox(tag); pw = tb[2] - tb[0] + 60; x = (W - pw) // 2
        d.rounded_rectangle((x, 1540, x + pw, 1636), radius=48, fill=B.NAVY + (235,)); d.text((x + 30, 1550), tag, font=f2, fill="white")
    out = canvas.convert("RGB")
    if t < .3: out = Image.blend(Image.new("RGB", out.size), out, t / .3)
    return out

def chunk(args):
    k, a, b = args; o = f"{B.WORK}/v_{MODE}_{k}.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", o], stdin=subprocess.PIPE)
    for i in range(a, b): pr.stdin.write(frame(i).tobytes())
    pr.stdin.close(); pr.wait(); return o

def audio():
    mix = f"{B.WORK}/mix.wav"; o = f"{B.WORK}/mix_{MODE}.wav"
    if MODE == "full": return mix
    # song parts joined with short crossfades at phrase boundaries
    fc = ("[0:a]atrim=0:%s,asetpts=PTS-STARTPTS[a];[0:a]atrim=%s:%s,asetpts=PTS-STARTPTS[b];" % (I + B.REEL_CUT[0] + .2, I + B.REEL_CUT[1] - .2, B.END) +
          "[a][b]acrossfade=d=0.4:c1=tri:c2=tri,afade=t=out:st=%s:d=0.8[o]" % (OUTLEN - .8))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mix, "-filter_complex", fc, "-map", "[o]", o], check=True)
    return o

if __name__ == "__main__":
    if len(sys.argv) > 2:
        for s in sys.argv[2:]: frame(int(float(s) * FPS)).save(f"{B.WORK}/v_{MODE}_{s}.jpg", quality=85)
        sys.exit()
    aud = audio(); NF = int(OUTLEN * FPS); n = 4; cuts = [NF * k // n for k in range(n + 1)]
    with Pool(n) as p: outs = p.map(chunk, [(k, cuts[k], cuts[k + 1]) for k in range(n)])
    open(f"{B.WORK}/vlist_{MODE}.txt", "w").write("".join(f"file '{o}'\n" for o in outs))
    final = f"{B.HERE}/social/sparkle-smile-{'tiktok-full' if MODE == 'full' else 'reel'}-9x16.mp4"; os.makedirs(os.path.dirname(final), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{B.WORK}/vlist_{MODE}.txt", "-i", aud,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("done", final, round(OUTLEN, 1))
