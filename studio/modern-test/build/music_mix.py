"""Original jingle + SFX + voices -> final mix. usage: music_mix.py <workdir> <scene_start_seconds>"""
import sys, json, numpy as np, soundfile as sf
W, OFF = sys.argv[1], float(sys.argv[2]); SR = 48000
LS = json.load(open(f"{W}/lipsync.json")); END = OFF + LS["T"]["end"]; N = int(END * SR)
rng = np.random.default_rng(2)
def tt(d): return np.arange(int(d * SR)) / SR
def add(b, t0, a, g=1.0): s = int(t0 * SR); a = a[:max(0, N - s)]; b[s:s+len(a)] += a * g
def pluck(f, d=0.7): s = tt(d); return sum(np.sin(2*np.pi*f*h*s) * .7**h for h in range(1, 6)) * np.exp(-s*5) * np.minimum(1, s/.004)
def bell(f, d=1.4): s = tt(d); return (np.sin(2*np.pi*f*s) + .3*np.sin(2*np.pi*2.76*f*s)*np.exp(-s*4)) * np.exp(-s*3)
mus = np.zeros(N, np.float32); beat = 60 / 116
prog = [[261.6, 329.6, 392], [220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7]]
mel = [523, 659, 784, 659, 698, 880, 784, 659, 587, 659, 523, 392]
t, bar = 0.0, 0
while t < END:
    ch = prog[bar % 4]
    for b in range(4):
        x = t + b * beat
        for j, f in enumerate(ch): add(mus, x + j * .012, pluck(f), .045)
        add(mus, x, pluck(ch[0] / 2, .9), .07)
        s = tt(.1); add(mus, x, np.sin(2*np.pi*(55 + 70*np.exp(-s*30))*s) * np.exp(-s*14), .18 if b % 2 == 0 else 0)
        add(mus, x + beat / 2, bell(mel[(bar * 4 + b) % len(mel)]), .035)
    t += 4 * beat; bar += 1
sfx = np.zeros(N, np.float32)
for i, f in enumerate([784, 988, 1175, 1568]): add(sfx, 0.25 + i * .09, bell(f), .12)
n = rng.standard_normal(int(.7 * SR)).astype(np.float32); y = np.convolve(n, np.ones(60) / 60, "same") * np.sin(np.linspace(0, np.pi, len(n)))**2
add(sfx, OFF - 0.45, y, 1.2)                                            # whoosh at the transition
for k in range(5):                                                       # soft hop boings
    s = tt(.3); f = 300 * (1 + 1.1*np.exp(-s*9)*np.sin(2*np.pi*13*s)); add(sfx, OFF + 0.35 + k * .75, np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-s*8) * .25)
add(sfx, OFF + LS["T"]["PEB"][1] - 0.2, rng.standard_normal(int(1.2*SR)).astype(np.float32) * 0, 1)
for i, f in enumerate([659, 784, 1047]): add(sfx, OFF + LS["T"]["PEB"][1] + 1.0 + i * .1, bell(f), .12)
v, _ = sf.read(f"{W}/voices.wav", dtype="float32"); voice = np.zeros(N, np.float32); add(voice, OFF, v)
env = np.convolve(np.abs(voice), np.ones(2400) / 2400, "same"); mus *= 1 - np.clip(env * 5, 0, .6)
fade = np.ones(N); fade[-int(1.2*SR):] = np.linspace(1, 0, int(1.2*SR)); mus *= fade
mix = voice * 1.1 + sfx * .8 + mus; mix /= np.max(np.abs(mix)) / .95
sf.write(f"{W}/final_mix.wav", mix, SR, subtype="PCM_16"); print("mix", round(END, 2), "s")
