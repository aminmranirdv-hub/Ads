"""Pip & Pebble Ep.1 - all original audio: offline TTS voices, synthesized music + SFX, timeline.json."""
import json, subprocess, wave, sys, os
import numpy as np
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SR, FPS = 48000, 24
rng = np.random.default_rng(3)

VOICES = {  # speaker -> (espeak voice, speed, pitch, sox effects)
  "N":   ("mb-us1", 138, 55, ("reverb", "20", "bass", "2")),
  "PIP": ("mb-us1", 175, 95, ("pitch", "+380", "tempo", "1.02")),
  "PEB": ("mb-en1", 118, 60, ("pitch", "+520", "reverb", "8")),
}
def tts(name, spk, text):
    v, s, p, fx = VOICES[spk]
    raw, fin = f"{OUT}/{name}_raw.wav", f"{OUT}/{name}.wav"
    subprocess.run(["espeak-ng", "-v", v, "-s", str(s), "-p", str(p), "-w", raw, text], check=True)
    subprocess.run(["sox", raw, "-r", str(SR), "-c", "1", fin, *fx, "norm", "-3"], check=True, stderr=subprocess.DEVNULL)
    with wave.open(fin) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    idx = np.where(np.abs(a) > 0.02)[0]
    return a[max(0, idx[0] - 200): idx[-1] + 800]

SCRIPT = [  # (key, speaker, text, gap_before)
 ("n1", "N",   "In Sunny Meadow, lived Pip. The fastest bunny of all.", 0.3),
 ("p1", "PIP", "Look at my new shiny ball! It's all mine!", 0.3),
 ("b1", "PEB", "Hi Pip! Can I play too?", 0.9),
 ("p2", "PIP", "Hmm. You're too slow, Pebble. And it's MY ball.", 0.3),
 ("n2", "N",   "Pebble felt very sad.", 0.3),
 ("p3", "PIP", "Watch this! Super high bounce!", 0.6),
 ("p4", "PIP", "Oh no! My ball! I can't swim!", 2.6),
 ("b2", "PEB", "Don't worry, Pip. I can!", 0.4),
 ("n3", "N",   "Pebble was slow on land. But in the water, he was super fast!", 0.8),
 ("p5", "PIP", "Pebble, you saved my ball! I'm sorry I said you were slow.", 1.0),
 ("p6", "PIP", "Do you want to play with me?", 0.2),
 ("b3", "PEB", "Yes! Friends share!", 0.3),
 ("n4", "N",   "Everyone is good at something. And sharing makes playing even more fun!", 1.6),
 ("n5", "N",   "See you next time, friends!", 0.6),
]
TITLE = 4.0
T = {"title": [0, TITLE]}
clips = {}; spk_of = {}
t = TITLE
for key, spk, text, gap in SCRIPT:
    a = tts(key, spk, text); clips[key] = a; spk_of[key] = spk
    t += gap; T[key] = [round(t, 3), round(t + len(a) / SR, 3)]; t = T[key][1]
T["end"] = round(t + 3.0, 3)
# story beats
T["bounce"] = T["p3"][1] + 0.1          # ball goes high
T["splash"] = T["bounce"] + 1.6          # ball lands in pond
T["dive"] = T["b2"][1] + 0.2             # Pebble slides into water
T["back"] = T["n3"][1] - 0.3             # ball pushed back to shore
T["play"] = T["b3"][1] + 0.1
T["endcard"] = T["n4"][1] + 0.3
N = int(T["end"] * SR)
voice = np.zeros(N, np.float32); spk_track = {s: np.zeros(N, np.float32) for s in VOICES}
for k, a in clips.items():
    s = int(T[k][0] * SR); voice[s:s+len(a)] += a; spk_track[spk_of[k]][s:s+len(a)] += a

sfx = np.zeros(N, np.float32)
def tt(d): return np.arange(int(d * SR)) / SR
def add(buf, t0, a, g=1.0):
    s = int(t0 * SR); a = a[:max(0, N - s)]; buf[s:s+len(a)] += a * g
def lp(x, k):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += k * (x[i] - acc); y[i] = acc
    return y
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def boing(f0=300, d=0.35):
    s = tt(d); f = f0 * (1 + 1.2 * np.exp(-s * 9) * np.sin(2*np.pi*14*s)); ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph) * np.exp(-s * 7) * 0.4
def bounce(): s = tt(0.15); return np.sin(2*np.pi*(180-400*s)*s) * np.exp(-s*30) * 0.5
def splash():
    d = 1.2; s = tt(d); n = noise(d); return (n - lp(n, 0.3)) * np.exp(-s * 3.5) * 0.5 + lp(n, 0.05) * np.exp(-s*5) * 2
def bubbles(d=2.5):
    out = np.zeros(int(d*SR), np.float32)
    for i in range(int(d*12)):
        st = int(rng.uniform(0, d-0.1)*SR); s = tt(0.06); f = rng.uniform(500, 1100)
        b = np.sin(2*np.pi*(f + 3000*s)*s) * np.exp(-s*60) * 0.25; out[st:st+len(b)] += b[:len(out)-st]
    return out
def chime(notes, t0, step=0.1, g=0.18):
    for i, f in enumerate(notes):
        s = tt(1.5); add(sfx, t0 + i*step, (np.sin(2*np.pi*f*s) + 0.4*np.sin(2*np.pi*3*f*s)*np.exp(-s*6)) * np.exp(-s*3), g)
def whoosh(d=0.5):
    n = noise(d); return lp(n, 0.06) * np.sin(np.linspace(0, np.pi, len(n)))**2 * 1.2
def sadhorn(t0):
    for i, f in enumerate([392, 370, 349, 330]):
        s = tt(0.5 if i < 3 else 0.9); x = sum(np.sin(2*np.pi*f*h*s)/h for h in range(1,5))
        add(sfx, t0 + i*0.42, x * np.minimum(1, s/0.03) * np.exp(-s*2) * 0.08)

chime([523, 659, 784, 1047], 0.2, 0.12, 0.2)            # title sparkle
for k in range(5): add(sfx, T["n1"][0] + 0.2 + k*0.45, boing(280 + k*15), 0.8)  # Pip hops in
add(sfx, T["p1"][0] - 0.1, bounce())
sadhorn(T["n2"][0] + 0.1)
add(sfx, T["bounce"] - 0.15, boing(420, 0.5), 1.0)
add(sfx, T["bounce"] + 0.1, whoosh(1.2), 0.8)
for k, dt in enumerate([0.55, 0.95, 1.25]): add(sfx, T["bounce"] + dt, bounce(), 0.8 - k*0.2)
add(sfx, T["splash"], splash(), 1.0)
add(sfx, T["dive"], splash(), 0.7); add(sfx, T["dive"] + 0.3, bubbles(T["back"] - T["dive"]), 0.9)
add(sfx, T["back"], whoosh(0.4), 0.6)
chime([659, 784, 988, 1319], T["back"] + 0.2, 0.09, 0.18)
for k in range(4): add(sfx, T["play"] + 0.3 + k*0.8, bounce(), 0.6)
chime([523, 659, 784, 1047, 1319, 1568], T["endcard"], 0.1, 0.16)

# music: cheerful plucked "ukulele" + glockenspiel, original progression C-G-Am-F
music = np.zeros(N, np.float32)
def pluck(f, d=0.6):
    s = tt(d); x = sum(np.sin(2*np.pi*f*h*s) * (0.7**h) for h in range(1, 6))
    return x * np.exp(-s * 6) * np.minimum(1, s / 0.004)
bpm = 112; beat = 60 / bpm
prog = [[261.6, 329.6, 392], [196, 246.9, 293.7], [220, 261.6, 329.6], [174.6, 220, 261.6]]
sad_prog = [[220, 261.6, 329.6], [174.6, 220, 261.6]]
melody = [784, 659, 784, 880, 784, 659, 587, 523]
tb, bar = 0.0, 0
while tb < N / SR:
    sad = T["n2"][0] - 0.3 <= tb < T["p3"][0] - 0.3
    ch = (sad_prog if sad else prog)[bar % 2 if sad else bar % 4]
    for b in range(4):
        t0 = tb + b * beat
        for j, f in enumerate(ch): add(music, t0 + j * 0.018, pluck(f), 0.06 if not sad else 0.04)
        add(music, t0, pluck(ch[0] / 2, 0.8), 0.08)
        if not sad and b % 2 == 0:
            m = melody[(bar * 2 + b // 2) % len(melody)]
            s = tt(0.5); add(music, t0 + beat/2, np.sin(2*np.pi*m*s) * np.exp(-s*5), 0.05)
    tb += 4 * beat; bar += 1
env = np.ones(N, np.float32)
def zone(a, b, v): env[int(a*SR):int(b*SR)] = v
zone(T["splash"] - 0.2, T["dive"], 0.35)     # tension
env = lp(env, 0.0008)
duck = 1 - np.clip(lp(np.abs(voice), 0.0005) * 5, 0, 0.6)
music *= env * duck
mix = voice + sfx * 0.8 + music
mix /= np.max(np.abs(mix)) / 0.95
with wave.open(f"{OUT}/mix.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
nf = int(T["end"] * FPS) + 1; hop = SR // FPS
for s, tr in spk_track.items():
    m = np.array([np.sqrt(np.mean(tr[i*hop:(i+1)*hop]**2)) if i*hop < N else 0 for i in range(nf)])
    ref = np.percentile(m[m > 0.01], 90) if np.any(m > 0.01) else 1
    T["mouth_" + s] = [round(float(x), 3) for x in np.clip(m / ref, 0, 1)]
T["fps"] = FPS
T["lines"] = [[k, spk, txt] for k, spk, txt, _ in SCRIPT]
json.dump(T, open(f"{OUT}/timeline.json", "w"))
print({k: v for k, v in T.items() if not k.startswith("mouth") and k != "lines"})
