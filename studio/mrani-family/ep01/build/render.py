# Renders ../output/work/timeline.json to 1080p24 MP4 (Ken Burns camera, FX, title overlays). Free, CPU only.
# usage: python3 render.py [preview_seconds...]   (no args = full render in 4 parallel chunks)
import json, os, sys, subprocess, math, numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); W, H = 1920, 1080
WORK = f"{HERE}/../output/work"; STILLS = f"{HERE}/../stills"; ART = f"{HERE}/../../channel-art"
TL = json.load(open(f"{WORK}/timeline.json")); FPS = TL["fps"]; NF = int(TL["end"] * FPS)
FONT = f"{ART}/fonts/lilita-one-latin-400-normal.woff"; FONT2 = f"{ART}/fonts/fredoka-latin-700-normal.woff"
NAVY = (27, 58, 143)
_img = {}
def still(name):
    if name not in _img:
        p = f"{STILLS}/title_ep01.jpg" if name == "TITLE" else f"{STILLS}/{name}.png"
        _img[name] = Image.open(p).convert("RGB")
    return _img[name]
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)

def label(txt, size, fill, stroke=NAVY, sw=8, font=FONT):
    f = ImageFont.truetype(font, size); b = f.getbbox(txt, stroke_width=sw)
    im = Image.new("RGBA", (b[2] - b[0] + 20, b[3] - b[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - b[0], 10 - b[1]), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke); return im
def pill(txt, size, fg=(255, 255, 255), bg=NAVY + (235,), pad=26, font=FONT2):
    f = ImageFont.truetype(font, size); b = f.getbbox(txt); w, h = b[2] - b[0] + 2 * pad, b[3] - b[1] + pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=bg); d.text((pad - b[0], pad // 2 - b[1]), txt, font=f, fill=fg); return im
def stack(*ims, gap=8):
    w = max(i.width for i in ims); h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); y = 0
    for i in ims: out.alpha_composite(i, ((w - i.width) // 2, y)); y += i.height + gap
    return out
_txt = {}
def overlay(tx):
    k = id(tx)
    if k not in _txt:
        kd = tx["kind"]
        if kd == "episode": im = stack(pill(tx["line1"], 44, bg=(255, 93, 143, 240)), label(tx["line2"], 88, (255, 216, 77)))
        elif kd == "name":
            im = Image.new("RGBA", (1100, 230), (0, 0, 0, 0)); n = label(tx["name"], 120, tx["color"])
            im.alpha_composite(n, (0, 0)); im.alpha_composite(pill(tx["tag"], 46), (16, n.height - 6))
        elif kd == "scene": im = pill(tx["label"], 46, bg=(255, 138, 31, 240))
        elif kd == "slowmo": im = label(tx["label"], 130, (255, 255, 255), sw=10)
        elif kd == "end":
            im = stack(label(tx["line1"], 96, (255, 216, 77)), pill("  SUBSCRIBE  ", 64, bg=(230, 33, 23, 250)), pill(tx["line2"], 44), gap=18)
        _txt[k] = im
    return _txt[k]

def frame(f):
    t = f / FPS
    sg = next((s for s in TL["segs"] if s["t0"] <= t < s["t1"]), TL["segs"][-1])
    d = sg["t1"] - sg["t0"]; p = ease((t - sg["t0"]) / d); lt = t - sg["t0"]
    im = still(sg["img"]); iw, ih = im.size
    lvl = TL["level"][f] if f < len(TL["level"]) else 0
    z = (sg["z0"] + (sg["z1"] - sg["z0"]) * p) * (1 + .006 * lvl)
    cx = sg["cx0"] + (sg["cx1"] - sg["cx0"]) * p; cy = sg["cy0"] + (sg["cy1"] - sg["cy0"]) * p
    bw = min(iw, ih * 16 / 9); cw = bw / z; ch = cw * 9 / 16
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw); y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    fx = sg["fx"]
    if "shake" in fx and lt < 1.2:
        a = 18 * (1 - lt / 1.2) * cw / W; x0 = min(max(x0 + math.sin(f * 2.7) * a, 0), iw - cw); y0 = min(max(y0 + math.cos(f * 3.1) * a, 0), ih - ch)
    fr = im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    a = np.asarray(fr, dtype=np.float32)
    if "redpulse" in fx: a = a * (1 - .06) + np.array([255, 40, 30]) * .06 * (0.5 + 0.5 * math.sin(t * 5))
    if "slowmo" in fx:
        g = a.mean(2, keepdims=True); a = a * .75 + g * .25; a[:, :, 2] += 10
        a[:110] = 0; a[-110:] = 0
    if "flash" in fx and lt < .3: a = a + (255 - a) * (1 - lt / .3)
    if "fadein" in fx and lt < .4: a = a * (lt / .4)
    if t > TL["end"] - .8: a = a * max(0, (TL["end"] - t) / .8)
    fr = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    for tx in TL["texts"]:
        if not (tx["t0"] <= t < tx["t1"]): continue
        o = overlay(tx); k = tx["kind"]; ti = t - tx["t0"]; to = tx["t1"] - t
        al = min(1, ti / .25, to / .25); sl = (1 - ease(ti / .35))
        if k == "episode": pos = ((W - o.width) // 2, int(H - o.height - 70 + 120 * sl))
        elif k == "name": pos = (int(70 - 600 * sl), H - o.height - 60)
        elif k == "scene": pos = (int(60 - 700 * sl), 60)
        elif k == "slowmo": pos = ((W - o.width) // 2 + int(6 * math.sin(t * 9)), H - o.height - 140)
        elif k == "end": pos = ((W - o.width) // 2, int(H - o.height - 90 + 100 * sl))
        if al < 1: o = o.copy(); o.putalpha(o.getchannel("A").point(lambda v: int(v * al)))
        fr.alpha_composite(o, (max(-o.width, pos[0]), pos[1]))
    return fr.convert("RGB")

def chunk(args):
    i, a, b = args; out = f"{WORK}/chunk{i}.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(a, b): pr.stdin.write(frame(f).tobytes())
    pr.stdin.close(); pr.wait(); return out

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for s in sys.argv[1:]: frame(int(float(s) * FPS)).save(f"{WORK}/preview_{s}.jpg", quality=88)
        sys.exit()
    n = 4; cuts = [NF * k // n for k in range(n + 1)]
    with Pool(n) as pool: outs = pool.map(chunk, [(k, cuts[k], cuts[k + 1]) for k in range(n)])
    open(f"{WORK}/list.txt", "w").write("".join(f"file '{o}'\n" for o in outs))
    final = f"{HERE}/../output/mrani-family-ep01-the-great-protocol-breakdown.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{WORK}/list.txt", "-i", f"{WORK}/mix.wav",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest", "-movflags", "+faststart", final], check=True)
    print("done", final)
