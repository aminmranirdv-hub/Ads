"""Snack Squad Ep.1 audio: Kokoro voices, original score, Foley SFX, timeline.json. usage: build_audio.py <out> <kokoro_dir>"""
import json, subprocess, sys, os
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from script import SCRIPT, VOICES, PAUSE
OUT, KD = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
from kokoro_onnx import Kokoro
K = Kokoro(f"{KD}/model.onnx", f"{KD}/voices.npz"); SR, FPS = 48000, 24; rng = np.random.default_rng(9)
def tts(key, spk, text):
    if spk == "ALL":
        parts = [tts(f"{key}_{s}", s, text) for s in ("NIB", "BUB", "MOC")]
        n = max(len(p) for p in parts); mix = np.zeros(n, np.float32)
        for p in parts: mix[:len(p)] += p
        return mix / np.max(np.abs(mix)) * 0.75
    v, sp, pc = VOICES[spk]
    a, sr = K.create(text, voice=v, speed=sp, lang="en-us")
    raw, fin = f"{OUT}/{key}_raw.wav", f"{OUT}/{key}.wav"; sf.write(raw, a, sr)
    subprocess.run(["sox", raw, "-r", str(SR), "-c", "1", fin, "pitch", str(pc), "norm", "-3"], check=True, stderr=subprocess.DEVNULL)
    d, _ = sf.read(fin, dtype="float32"); i = np.where(np.abs(d) > 0.01)[0]
    return d[max(0, i[0] - 300): i[-1] + 1200]
TITLE_AT = None
T, clips, spk_of = {}, {}, {}
t = 0.4
for key, spk, text, gap, beat in SCRIPT:
    a = tts(key, spk, text); clips[key] = a; spk_of[key] = spk
    t += gap; T[key] = [round(t, 3), round(t + len(a) / SR, 3)]; t = T[key][1] + PAUSE.get(key, 0)
    if key == "n2": T["title"] = [round(T[key][1] + 0.6, 3), round(T[key][1] + 5.6, 3)]
T["end"] = round(t + 9.0, 3)
beats = {}
for key, _, _, _, beat in SCRIPT:
    beats.setdefault(beat, [T[key][0], T[key][1]]); beats[beat][1] = T[key][1] + PAUSE.get(key, 0)
T["beats"] = beats; N = int(T["end"] * SR)
voice = np.zeros(N, np.float32); tracks = {s: np.zeros(N, np.float32) for s in list(VOICES) + ["ALL"]}
for k, a in clips.items():
    s = int(T[k][0] * SR); voice[s:s+len(a)] += a; tracks[spk_of[k]][s:s+len(a)] += a

def tt(d): return np.arange(int(d * SR)) / SR
def add(b, t0, a, g=1.0): s = int(t0 * SR); a = a[:max(0, N - s)]; b[s:s+len(a)] += a * g
def lp(x, k):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += k * (x[i] - acc); y[i] = acc
    return y
def smooth(x, n): return np.convolve(x, np.ones(n) / n, "same")
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def tone(f, d, dec=6, h=4): s = tt(d); return sum(np.sin(2*np.pi*f*k*s) * .6**k for k in range(1, h+1)) * np.exp(-s*dec) * np.minimum(1, s/.004)
def bell(f, d=1.3): s = tt(d); return (np.sin(2*np.pi*f*s) + .3*np.sin(2*np.pi*2.76*f*s)*np.exp(-s*4)) * np.exp(-s*3)
def sweep(f0, f1, d, g=.3): s = tt(d); f = np.linspace(f0, f1, len(s)); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.sin(np.linspace(0, np.pi, len(s))) * g
def boing(f0=300, d=.35): s = tt(d); f = f0*(1+1.2*np.exp(-s*9)*np.sin(2*np.pi*14*s)); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-s*7)*.4
def whoosh(d=.5): return smooth(noise(d), 80) * np.sin(np.linspace(0, np.pi, int(d*SR)))**2 * 6
def thud(f=90): s = tt(.35); return np.sin(2*np.pi*(f-50*s)*s)*np.exp(-s*12)*.8
def splash(): d=.9; s=tt(d); n=noise(d); return (n - smooth(n, 6)) * np.exp(-s*4) * .5 + smooth(n, 40)*np.exp(-s*6)*3
def squeak(): return sweep(1800, 2600, .12, .25)
def tick(): s = tt(.03); return np.sin(2*np.pi*3000*s)*np.exp(-s*200)*.3
def click(): s = tt(.05); return (noise(.05) - smooth(noise(.05), 4)) * np.exp(-s*120) * .6
def gulp():
    a = thud(70) * .5; a[:int(.25*SR)] += sweep(400, 120, .25, .6); return a
def cricket(t0, d):
    x = t0
    while x < t0 + d: add(sfx, x, sweep(4200, 4400, .05, .05)); add(sfx, x + .08, sweep(4200, 4400, .05, .05)); x += .9
def roll(t0, d, g=.15): add(sfx, t0, smooth(noise(d), 30) * 4 * (0.6 + 0.4*np.sin(np.linspace(0, d*20, int(d*SR)))), g)
def beepboop(t0): add(sfx, t0, tone(880, .12, 10, 2), .25); add(sfx, t0 + .15, tone(660, .15, 10, 2), .25)
def snore(t0, n=3):
    for i in range(n): add(sfx, t0 + i*1.6, smooth(noise(.9), 200) * 30 * np.sin(np.linspace(0, np.pi, int(.9*SR))) * (0.5 + 0.5*np.sin(2*np.pi*28*tt(.9))), .25)
def choir(t0, d=2.0):
    for f in (523, 659, 784): s = tt(d); add(sfx, t0, (np.sin(2*np.pi*f*s) + .3*np.sin(2*np.pi*2*f*s)) * np.sin(np.linspace(0, np.pi, len(s))) * (1 + .02*np.sin(2*np.pi*5*s)), .05)
def claps(t0, n=8):
    for i in range(n): add(sfx, t0 + i*.5, (noise(.06) - smooth(noise(.06), 3)) * np.exp(-tt(.06)*60), .5)

sfx = np.zeros(N, np.float32); B = beats
for i in range(int((T["n2"][1]) / 1.0)): add(sfx, 0.2 + i * 1.0, tick())                       # clock in the hook
add(sfx, T["n2"][1] + 0.1, tone(147, 1.2, 2, 6), .25); add(sfx, T["n2"][1] + 0.1, tone(185, 1.2, 2, 6), .2)   # sting
for i, f in enumerate([523, 659, 784, 1047]): add(sfx, T["title"][0] + .2 + i*.1, bell(f), .12)
add(sfx, B["team"][0] - 1.3, sweep(1200, 300, .6, .15)); add(sfx, B["team"][0] - .7, boing(260), 1)      # curtain slide + landing
roll(B["team"][0] - .2, 1.2); add(sfx, B["team"][0] + .9, boing(200), .9)
snore(B["mochi"][0] - .5, 3); add(sfx, T["m2"][0] + .4, bell(1319), .2)
add(sfx, B["plan"][0] - .3, smooth(noise(.6), 3) * .3)                                              # paper unroll
for i in range(4): add(sfx, T[f"c{i+1}"][0], thud(70), .35)
for k in range(6): add(sfx, B["floor"][0] + .4 + k*.6, tick(), .6)                                 # tiptoe
for k in range(5): add(sfx, T["n12"][0] + k*.25, squeak(), .8)
add(sfx, T["n12"][1] + .2, sweep(300, 900, 2.0, .12))                                              # spin whirr
roll(B["floor2"][0], 6); add(sfx, B["floor2"][0] + 2, whoosh(.6), .6); add(sfx, B["floor2"][0] + 3.5, whoosh(.6), .6)
for i in range(5): add(sfx, T[f"k{i+1}"][0], bell([523, 587, 659, 698, 784][i], .8), .15)
add(sfx, T["b7"][1] + 1, whoosh(.5), .5); add(sfx, T["n15"][0], thud(80), .4)
for i in range(4): beepboop(B["vacuum"][0] + i*.6)
add(sfx, B["chase"][0], smooth(noise(B["chase"][1] - B["chase"][0]), 400) * 10 * (1 + .3*np.sin(2*np.pi*3*tt(B["chase"][1] - B["chase"][0]))), .12)   # vacuum hum
roll(B["chase"][0], B["chase"][1] - B["chase"][0], .1)
add(sfx, B["chase2"][0] - .3, thud(60), .9); add(sfx, B["chase2"][0] + .3, tone(660, .3, 6, 2), .2); add(sfx, B["chase2"][0] + .6, tone(440, .5, 4, 2), .2)
add(sfx, T["m6"][0] - .2, thud(80), .5); add(sfx, T["b11"][0] - .2, splash(), .7)
for k in range(6): add(sfx, B["tower"][1] - 6 + k*1.0, sweep(180, 140, .4, .12))                  # wobble creaks
add(sfx, B["cookie"][0] - 1.2, sweep(2000, 3000, .3, .12)); choir(B["cookie"][0] - 1.0, 2.5)
add(sfx, T["m7"][1] + .1, whoosh(1.4), .9); add(sfx, T["m7"][1] + 1.8, gulp(), 1.0)
cricket(T["m7"][1] + 2.3, 3.0)
add(sfx, B["lights"][0] - .8, click(), 1.0)
for k in range(4): add(sfx, B["lights"][0] - .3 + k*.45, thud(140), .3)                           # slipper steps
for k in range(3): add(sfx, T["l4"][0] + k*1.6, smooth(noise(.3), 2) * .2)                        # treat crinkles
for i, f in enumerate([523, 659, 784]): add(sfx, T["p2"][1] + .1 + i*.1, bell(f), .12)
claps(B["party"][0], 16)
add(sfx, T["end"] - 7.5, sweep(500, 1200, .12, .3)); add(sfx, T["end"] - 7.3, click(), .4)          # burp bubble pop
for i, f in enumerate([523, 659, 784, 1047, 1319]): add(sfx, T["end"] - 6.5 + i*.1, bell(f), .12)

# ---- score (original) ----
mus = np.zeros(N, np.float32)
def section(t0, t1, bpm, prog, style, gain):
    beat = 60 / bpm; x = t0; bar = 0
    while x < t1:
        ch = prog[bar % len(prog)]
        for b in range(4):
            tb = x + b * beat
            if tb >= t1: break
            if style == "sneak":
                add(mus, tb, tone(ch[0] / 2, .25, 14, 3), gain * 1.4)
                if b % 2 == 1: add(mus, tb, tone(ch[(b // 2) % 3] * 2, .18, 16, 3), gain)
            elif style == "chase":
                add(mus, tb, tone(ch[0] / 2, .2, 10, 4), gain * 1.3); add(mus, tb + beat/2, tone(ch[1], .15, 12, 3), gain)
                s = tt(.1); add(mus, tb, np.sin(2*np.pi*(60+80*np.exp(-s*30))*s)*np.exp(-s*14), gain * 3)
            elif style == "warm":
                for j, f in enumerate(ch): add(mus, tb + j*.02, tone(f, 1.0, 2.5, 3), gain * .7)
            elif style == "party":
                for j, f in enumerate(ch): add(mus, tb + j*.012, tone(f, .5, 6, 4), gain * .8)
                s = tt(.1); add(mus, tb, np.sin(2*np.pi*(55+70*np.exp(-s*30))*s)*np.exp(-s*14), gain * 3 if b % 2 == 0 else 0)
                add(mus, tb + beat/2, bell([784, 880, 1047, 880][b], .5), gain * .6)
        x += 4 * beat; bar += 1
Am = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7], [164.8, 207.7, 246.9]]
C = [[261.6, 329.6, 392], [196, 246.9, 293.7], [220, 261.6, 329.6], [174.6, 220, 261.6]]
section(T["title"][0], B["vacuum"][0], 96, Am, "sneak", .05)
section(B["vacuum"][0], B["chase2"][0], 150, Am, "chase", .05)
section(B["chase2"][0] + 1.5, T["m7"][0], 90, Am, "sneak", .045)
section(B["lights"][0] + .5, B["party"][0], 80, C, "warm", .05)
section(B["party"][0], T["end"], 120, C, "party", .055)
for i, f in enumerate([392, 494, 587, 784]): add(mus, T["title"][0] + i * .15, tone(f, 1.0, 3, 4), .08)
env = np.ones(N, np.float32)
env = smooth(env, 4800); duck = 1 - np.clip(smooth(np.abs(voice), 2400) * 5, 0, .6)
mus *= env * duck
mix = voice * 1.15 + sfx * .75 + mus
mix /= np.max(np.abs(mix)) / .95
sf.write(f"{OUT}/mix.wav", mix, SR, subtype="PCM_16")
nf = int(T["end"] * FPS) + 1; hop = SR // FPS
for s, tr in tracks.items():
    m = np.array([np.sqrt(np.mean(tr[i*hop:(i+1)*hop]**2)) if i*hop < N else 0 for i in range(nf)])
    ref = np.percentile(m[m > .01], 90) if np.any(m > .01) else 1
    T["mouth_" + s] = [round(float(x), 3) for x in np.clip(m / ref, 0, 1)]
T["fps"] = FPS; T["lines"] = [[k, spk, txt] for k, spk, txt, _, _ in SCRIPT]
json.dump(T, open(f"{OUT}/timeline.json", "w"))
print("END", T["end"]); print({b: [round(x, 1) for x in v] for b, v in beats.items()})
