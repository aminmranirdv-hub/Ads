"""Ep.2 audio: Kokoro neural voices (offline), synthesized music + SFX, timeline.json.
usage: python3 build_audio.py <outdir> <kokoro_dir>"""
import json, subprocess, sys, os
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__)); from script import SCRIPT, VOICES
OUT, KD = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
from kokoro_onnx import Kokoro
K = Kokoro(f"{KD}/model.onnx", f"{KD}/voices.npz")
SR, FPS = 48000, 24
rng = np.random.default_rng(5)
# extra action time (seconds) AFTER these lines
PAUSE = {"a2": 6, "h2": 3, "m2": 4, "a5": 1.5, "a7": 10, "b3": 13, "p5": 11, "b4": 3, "b6": 2.5, "m8": 1.5,
         "a8": 1.5, "m11": 13, "p6": 3, "h3": 8, "m12": 1, "b8": 1.5, "h4": 9, "m13": 2, "a10": 3}
def tts(key, spk, text):
    if spk == "ALL":
        parts = [tts(f"{key}_{s}", s, text) for s in ("PIP", "AZI", "AMI", "PEB", "HIC")]
        n = max(len(p) for p in parts); mix = np.zeros(n, np.float32)
        for p in parts: mix[:len(p)] += p
        return mix / np.max(np.abs(mix)) * 0.7
    v, sp, pc = VOICES[spk]; lang = "en-gb" if v.startswith("b") else "en-us"
    a, sr = K.create(text, voice=v, speed=sp, lang=lang)
    raw, fin = f"{OUT}/{key}_raw.wav", f"{OUT}/{key}.wav"
    sf.write(raw, a, sr)
    subprocess.run(["sox", raw, "-r", str(SR), "-c", "1", fin, "pitch", str(pc), "norm", "-3"], check=True, stderr=subprocess.DEVNULL)
    d, _ = sf.read(fin, dtype="float32"); idx = np.where(np.abs(d) > 0.01)[0]
    return d[max(0, idx[0] - 300): idx[-1] + 1200]

TITLE = 8.0
T = {"title": [0, TITLE]}; clips, spk_of, beat_of = {}, {}, {}
t = TITLE
for key, spk, text, gap, beat in SCRIPT:
    a = tts(key, spk, text); clips[key] = a; spk_of[key] = spk; beat_of[key] = beat
    t += gap; T[key] = [round(t, 3), round(t + len(a) / SR, 3)]; t = T[key][1] + PAUSE.get(key, 0)
T["end"] = round(t + 10, 3)
beats = {}
for key, _, _, _, beat in SCRIPT:
    beats.setdefault(beat, [T[key][0], T[key][1]]); beats[beat][1] = T[key][1] + PAUSE.get(key, 0)
T["beats"] = beats
N = int(T["end"] * SR)
voice = np.zeros(N, np.float32); spk_track = {s: np.zeros(N, np.float32) for s in list(VOICES) + ["ALL"]}
for k, a in clips.items():
    s = int(T[k][0] * SR); voice[s:s+len(a)] += a; spk_track[spk_of[k]][s:s+len(a)] += a

def tt(d): return np.arange(int(d * SR)) / SR
def add(buf, t0, a, g=1.0):
    s = int(t0 * SR); a = a[:max(0, N - s)]; buf[s:s+len(a)] += a * g
def lp(x, k):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += k * (x[i] - acc); y[i] = acc
    return y
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def chime(notes, t0, step=0.1, g=0.15):
    for i, f in enumerate(notes):
        s = tt(1.5); add(sfx, t0 + i*step, (np.sin(2*np.pi*f*s) + 0.4*np.sin(2*np.pi*3*f*s)*np.exp(-s*6)) * np.exp(-s*3), g)
def whoosh(d=0.5): n = noise(d); return lp(n, 0.06) * np.sin(np.linspace(0, np.pi, len(n)))**2
def boing(f0=300, d=0.35):
    s = tt(d); f = f0 * (1 + 1.2*np.exp(-s*9)*np.sin(2*np.pi*14*s)); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-s*7) * 0.4
def roar(d=1.0):
    s = tt(d); n = lp(noise(d), 0.08); f = 110 + 40*np.sin(2*np.pi*3*s)
    return (n * 3 + np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)) * 0.25) * np.sin(np.linspace(0, np.pi, len(s)))**0.5 * 0.35
def thud(): s = tt(0.4); return np.sin(2*np.pi*(90-60*s)*s) * np.exp(-s*12) * 0.8
def whistle(d=0.6): s = tt(d); return np.sin(2*np.pi*(2400 + 120*np.sin(2*np.pi*30*s))*s) * np.minimum(1, s/0.02) * np.exp(-s*1.5) * 0.18
def cheer(d=3.0):
    out = noise(d) * 0.0
    for i in range(40):
        st = rng.uniform(0, d - 0.5); s = tt(0.5); f = rng.uniform(300, 700)
        b = np.sin(2*np.pi*f*s*(1+0.3*s)) * np.sin(np.linspace(0, np.pi, len(s))) * 0.05
        j = int(st*SR); out[j:j+len(b)] += b[:len(out)-j]
    return out + lp(noise(d), 0.15) * 0.4 * np.sin(np.linspace(0, np.pi, int(d*SR)))
def footsteps(t0, t1, rate, f=160, g=0.3):
    x = t0
    while x < t1: s = tt(0.06); add(sfx, x, np.sin(2*np.pi*f*s) * np.exp(-s*60), g); x += 1 / rate
def snip(): s = tt(0.12); return (noise(0.12) - lp(noise(0.12), 0.5)) * np.exp(-s*40) * 0.5

sfx = np.zeros(N, np.float32)
chime([523, 659, 784, 1047, 1319], 0.3, 0.12, 0.18)
add(sfx, T["h1"][0] - 0.6, whoosh(0.5), 0.6)
for i in range(6): add(sfx, T["h2"][1] + 0.2 + i*0.45, thud(), 0.35)    # hammering the finish line
add(sfx, T["m1"][0] - 1.0, roar(1.0), 1.0)
for b in ("a6",): add(sfx, T[b][1] + 0.1, boing(500, 0.2), 0.4)
add(sfx, T["a7"][0], whistle(0.8), 1.0)
add(sfx, T["a7"][1] + 0.1, whoosh(0.8), 0.9)
footsteps(T["a7"][1], T["b3"][1] + 13, 7, 200, 0.18)                     # fast runners
footsteps(T["b3"][0], T["b3"][1] + 13, 1.5, 120, 0.3)                    # Pebble plods
add(sfx, T["z3"][0] - 0.2, cheer(2.5), 0.7)
add(sfx, T["b5"][0] + 0.2, thud(), 1.0); add(sfx, T["b5"][0] + 0.5, thud(), 0.7)
add(sfx, T["m9"][0] - 0.3, whoosh(0.6), 0.8)
add(sfx, T["m10"][1] + 0.1, boing(260, 0.5), 0.9)
chime([659, 784, 988], T["m10"][1] + 0.4, 0.1, 0.15)
footsteps(T["m11"][1], T["m11"][1] + 13, 2, 140, 0.25)
add(sfx, T["p6"][0] - 0.4, snip(), 1.0); add(sfx, T["p6"][0] - 0.3, cheer(2.0), 0.5)
add(sfx, T["h3"][0], cheer(4.0), 0.9); chime([523, 659, 784, 1047], T["h3"][0] + 0.5, 0.12, 0.15)
for i in range(5): add(sfx, T["h4"][1] + 0.5 + i*0.6, snip(), 0.8)
chime([784, 988, 1175, 1568], T["h4"][1] + 3.6, 0.1, 0.15)
add(sfx, T["all"][0], cheer(3.0), 0.6); chime([523, 659, 784, 1047, 1319, 1568], T["all"][1] + 0.2, 0.1, 0.16)

# music: original cheerful theme; faster "race" groove during the race; gentle during the fall/choice
music = np.zeros(N, np.float32)
def pluck(f, d=0.6):
    s = tt(d); x = sum(np.sin(2*np.pi*f*h*s) * (0.7**h) for h in range(1, 6)); return x * np.exp(-s*6) * np.minimum(1, s/0.004)
prog = [[261.6, 329.6, 392], [196, 246.9, 293.7], [220, 261.6, 329.6], [174.6, 220, 261.6]]
soft = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7], [196, 246.9, 293.7]]
mel = [784, 659, 784, 880, 784, 659, 587, 523, 587, 659, 523, 392]
race0, race1 = T["a7"][0], T["b4"][0]; sad0, sad1 = T["b5"][0], T["m9"][0]
tb, bar = 0.0, 0
while tb < N / SR:
    racing, sad = race0 <= tb < race1, sad0 <= tb < sad1
    bpm = 150 if racing else (84 if sad else 112); beat = 60 / bpm
    ch = (soft if sad else prog)[bar % 4]
    for b in range(4):
        t0 = tb + b * beat
        for j, f in enumerate(ch): add(music, t0 + j*0.015, pluck(f), 0.035 if sad else 0.05)
        add(music, t0, pluck(ch[0] / 2, 0.8), 0.07)
        if racing:
            s = tt(0.12); add(music, t0, np.sin(2*np.pi*(60+80*np.exp(-s*30))*s) * np.exp(-s*14), 0.35)
            add(music, t0 + beat/2, (noise(0.04) - lp(noise(0.04), 0.5)) * np.exp(-tt(0.04)*90), 0.12)
        if not sad and b % 2 == 0:
            m = mel[(bar*2 + b//2) % len(mel)]; s = tt(0.45); add(music, t0 + beat/2, np.sin(2*np.pi*m*s) * np.exp(-s*5), 0.045)
    tb += 4 * beat; bar += 1
env = lp(np.ones(N, np.float32), 0.001)
duck = 1 - np.clip(lp(np.abs(voice), 0.0005) * 5, 0, 0.65)
music *= env * duck
mix = voice * 1.1 + sfx * 0.7 + music
mix /= np.max(np.abs(mix)) / 0.95
sf.write(f"{OUT}/mix.wav", mix, SR, subtype="PCM_16")
nf = int(T["end"] * FPS) + 1; hop = SR // FPS
for s, tr in spk_track.items():
    m = np.array([np.sqrt(np.mean(tr[i*hop:(i+1)*hop]**2)) if i*hop < N else 0 for i in range(nf)])
    ref = np.percentile(m[m > 0.01], 90) if np.any(m > 0.01) else 1
    T["mouth_" + s] = [round(float(x), 3) for x in np.clip(m / ref, 0, 1)]
T["fps"] = FPS
T["lines"] = [[k, spk, txt] for k, spk, txt, _, _ in SCRIPT]
json.dump(T, open(f"{OUT}/timeline.json", "w"))
print("END", T["end"]); print({b: [round(x, 1) for x in v] for b, v in beats.items()})
