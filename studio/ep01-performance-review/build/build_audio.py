"""Builds all original audio for Ep.1 (voice via espeak-ng+MBROLA, SFX/music synthesized) and timeline.json."""
import json, subprocess, wave, sys, os
import numpy as np

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SR = 48000
FPS = 30
rng = np.random.default_rng(7)

def tts(name, text, speed=162, pitch=32, sox_fx=("pitch", "-260", "bass", "6", "overdrive", "2", "reverb", "12")):
    raw = f"{OUT}/{name}_raw.wav"; fin = f"{OUT}/{name}.wav"
    subprocess.run(["espeak-ng", "-v", "mb-en1", "-s", str(speed), "-p", str(pitch), "-w", raw, text], check=True)
    subprocess.run(["sox", raw, "-r", str(SR), "-c", "1", fin, *sox_fx, "norm", "-3"], check=True)
    with wave.open(fin) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    # trim silence
    idx = np.where(np.abs(a) > 0.02)[0]
    return a[max(0, idx[0] - 200): idx[-1] + 800]

GRUFF = ("pitch", "-260", "bass", "6", "overdrive", "2", "reverb", "12")
lines = {
 "L1": tts("L1", "Sit down. This won't take long."),
 "L2": tts("L2", "Treat delivery. Average response time: four seconds. Unacceptable."),
 "L3": tts("L3", "Lap availability: forty percent. You were, quote, at work."),
 "L4": tts("L4", "Noted.", speed=115),
 "L5": tts("L5", "The vacuum incident. We do not talk about the vacuum incident.", speed=150, pitch=20),
 "L6": tts("L6", "And finally. Ear scratches.", speed=150),
 "L7": tts("L7", "No. Dont. Dont you dare. I am a professional", speed=215, pitch=70,
           sox_fx=("pitch", "+150", "reverb", "8")),
 "L8": tts("L8", "Exceeds expectations.", speed=110, pitch=45, sox_fx=("pitch", "-100", "reverb", "60", "tremolo", "6", "30")),
 "L9a": tts("L9a", "Ahem.", speed=130),
 "L9": tts("L9", "You're promoted. Same salary.", speed=155),
 "L10": tts("L10", "Noted.", speed=108),
}

# ---------- timeline ----------
T = {}
def place(key, t):
    T[key] = [round(t, 3), round(t + len(lines[key]) / SR, 3)]
    return T[key][1]

t = 0.0
T["s1"] = 0.0
e = place("L1", 0.35)
T["s2"] = e + 0.2
e = place("L2", T["s2"] + 0.25)
T["s3"] = e + 0.2
e = place("L3", T["s3"] + 0.2)
T["stamp1"] = e + 0.25
e = place("L4", T["stamp1"] + 0.6)
T["s4"] = e + 0.3
T["hits"] = [T["s4"], T["s4"] + 0.38, T["s4"] + 0.85]
e = place("L5", T["s4"] + 1.35)
T["s5"] = e + 0.3
e = place("L6", T["s5"] + 0.25)
e7 = place("L7", e + 0.15)
T["touch"] = round(e7 - 0.3, 3)
# cut off L7 at touch ("I am a professio—")
cut = int((T["touch"] - T["L7"][0]) * SR)
lines["L7"] = lines["L7"][:cut] * np.linspace(1, 0.6, cut)
T["L7"][1] = T["touch"]
T["stamps"] = [T["touch"] + 0.7, T["touch"] + 1.2, T["touch"] + 1.7]
e = place("L8", T["touch"] + 2.1)
T["s6"] = e + 0.55
e = place("L9a", T["s6"] + 0.35)
T["push"] = [T["L9a"][0], T["L9a"][0] + 0.9]
e = place("L9", e + 0.45)
e = place("L10", e + 0.55)
T["endcard"] = e + 0.4
T["end"] = T["endcard"] + 2.2
N = int(T["end"] * SR)

voice = np.zeros(N, np.float32)
for k, a in lines.items():
    s = int(T[k][0] * SR); voice[s:s + len(a)] += a[: N - s]

sfx = np.zeros(N, np.float32)
def add(buf, t, a, g=1.0):
    s = int(t * SR); a = a[: max(0, N - s)]; buf[s:s + len(a)] += a * g
def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, k):  # crude one-pole lowpass
    y = np.empty_like(x); acc = 0.0; a = k
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)

def paper(d=0.55):
    x = noise(d); x = x - lp(x, 0.15); env = np.sin(np.linspace(0, np.pi, len(x))) ** 0.7
    return x * env * 0.25
def thunk():
    s = tt(0.45); body = np.sin(2 * np.pi * (70 * s - 30 * s * s)) * np.exp(-s * 11)
    n = lp(noise(0.45), 0.25) * np.exp(-s * 40)
    return (body * 0.9 + n * 0.8)
def click():
    s = tt(0.04); return np.sin(2 * np.pi * 2500 * s) * np.exp(-s * 160) * 0.4
def whoosh(d=0.4):
    x = noise(d); y = lp(x, 0.08); env = np.sin(np.linspace(0, np.pi, len(x))) ** 2
    return y * env * 0.9
def pop():
    s = tt(0.12); return np.sin(2 * np.pi * (500 + 1800 * s) * s) * np.exp(-s * 35) * 0.35
def timpani(f=55, d=1.2, g=1.0):
    s = tt(d); x = np.sin(2 * np.pi * f * s) + 0.5 * np.sin(2 * np.pi * f * 1.5 * s)
    return (x * np.exp(-s * 3.2) + lp(noise(d), 0.1) * np.exp(-s * 25) * 2) * 0.5 * g
def brass(freqs, d, g=0.25):
    s = tt(d); x = np.zeros_like(s)
    for f in freqs:
        for h in range(1, 7): x += np.sin(2 * np.pi * f * h * s) / h
    env = np.minimum(1, s / 0.05) * np.exp(-s * 1.2)
    return x * env * g
def purr(d):
    s = tt(d); n = lp(noise(d), 0.02) * 6
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 24 * s) ** 2
    hum = np.sin(2 * np.pi * 48 * s) * 0.3
    env = np.minimum(1, s / 0.3) * np.minimum(1, (d - s) / 0.4)
    return (n * am + hum * am) * env * 0.5
def chime_arp(t0, notes, step=0.09, g=0.18):
    for i, f in enumerate(notes):
        s = tt(1.4); add(sfx, t0 + i * step, (np.sin(2*np.pi*f*s) + 0.3*np.sin(2*np.pi*2*f*s)) * np.exp(-s*3), g)

add(sfx, 0.0, paper(), 1.0)
add(sfx, 0.05, click(), 1.0)
add(sfx, T["s2"] - 0.15, whoosh(0.35), 0.5)
add(sfx, T["s3"] - 0.15, whoosh(0.35), 0.5)
add(sfx, T["stamp1"] - 0.2, whoosh(0.2), 0.4)
add(sfx, T["stamp1"], thunk(), 1.0)
for i, h in enumerate(T["hits"]):
    add(sfx, h, timpani(55 if i < 2 else 41, 1.6, 1 + 0.4 * i))
add(sfx, T["hits"][2], brass([73.4, 87.3, 103.8], 2.2), 1.0)
add(sfx, T["s5"] - 0.15, whoosh(0.35), 0.5)
add(sfx, T["touch"], purr(T["s6"] - T["touch"] - 0.1), 1.0)
chime_arp(T["touch"] + 0.05, [523, 659, 784, 1047, 1319, 1568], 0.08, 0.15)
for s_ in T["stamps"]:
    add(sfx, s_, thunk(), 0.8); add(sfx, s_ - 0.03, pop(), 0.6)
add(sfx, T["s6"] - 0.05, whoosh(0.25), 0.8)
add(sfx, T["s6"], pop(), 0.8)
add(sfx, T["L10"][0] - 0.1, click(), 0.6)
add(sfx, T["endcard"], brass([261.6, 329.6, 392], 1.8, 0.12), 1.0)
add(sfx, T["endcard"], pop(), 0.8)

# ---------- music bed: original lo-fi "corporate" loop ----------
music = np.zeros(N, np.float32)
bpm = 92; beat = 60 / bpm
chords = [[261.6, 329.6, 392, 493.9], [220, 261.6, 329.6, 392], [174.6, 220, 261.6, 329.6], [196, 246.9, 293.7, 329.6]]
def epiano(f, d):
    s = tt(d); return (np.sin(2*np.pi*f*s) + 0.25*np.sin(2*np.pi*2*f*s)*np.exp(-s*4)) * np.exp(-s*1.5)
bar = 0
tb = 0.0
while tb < N / SR:
    ch = chords[bar % 4]
    for b in range(4):
        tbeat = tb + b * beat
        if b in (0, 2):
            for f in ch: add(music, tbeat, epiano(f, beat * 2), 0.05)
            add(music, tbeat, epiano(ch[0] / 2, beat * 2), 0.07)
        s = tt(0.25); add(music, tbeat, np.sin(2*np.pi*(55+60*np.exp(-s*30))*s)*np.exp(-s*12), 0.25 if b in (0,2) else 0.0)
        add(music, tbeat + beat / 2, (noise(0.05) - lp(noise(0.05), 0.5)) * np.exp(-tt(0.05) * 80), 0.05)
    tb += 4 * beat; bar += 1
# mute music during vacuum sting & purr dream, end card button
env = np.ones(N, np.float32)
def zone(a, b, val):
    s, e = int(a * SR), int(b * SR); env[s:e] = val
zone(T["s4"], T["s5"], 0.0)
zone(T["touch"], T["s6"], 0.15)
zone(T["endcard"], T["end"], 0.0)
env = lp(env, 0.0008)
# duck under voice
venv = lp(np.abs(voice), 0.0005)
duck = 1 - np.clip(venv * 6, 0, 0.55)
music *= env * duck

mix = voice * 1.0 + sfx * 0.8 + music * 0.9
mix /= max(1e-6, np.max(np.abs(mix))) / 0.95
with wave.open(f"{OUT}/mix.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

# mouth envelope per frame from voice track
nf = int(T["end"] * FPS) + 1
hop = SR // FPS
mouth = []
for i in range(nf):
    seg = voice[i * hop:(i + 1) * hop]
    mouth.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
m = np.array(mouth); m = np.clip(m / (np.percentile(m[m > 0.01], 90) + 1e-6), 0, 1)
T["mouth"] = [round(float(x), 3) for x in m]
T["fps"] = FPS
json.dump(T, open(f"{OUT}/timeline.json", "w"))
print({k: v for k, v in T.items() if k != "mouth"})
