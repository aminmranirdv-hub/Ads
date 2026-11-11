# M'RANI FAMILY Ep.1 - timeline + original score/SFX + mix.  Writes ../output/work/{timeline.json,mix.wav,ep01.srt}
import json, os, sys, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from script import SCRIPT, PAUSE
HERE = os.path.dirname(os.path.abspath(__file__)); VO = f"{HERE}/vo"; OUT = f"{HERE}/../output/work"; os.makedirs(OUT, exist_ok=True)
SR = 48000; rng = np.random.default_rng(7)

def load(key, spk):
    a, sr = sf.read(f"{VO}/{key}_{spk}.wav")
    if a.ndim > 1: a = a.mean(1)
    if sr != SR: a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    return a.astype(np.float32)

# ---------- shot library: still, focus x/y (0..1), zoom start/end ----------
SH = {
 "hook": ("scuffle", .5, .45, 1.05, 1.25), "hook2": ("hicham_hack", .45, .4, 1.15, 1.35),
 "s1_aziza_enters": ("wide_living", .5, .5, 1.0, 1.12), "s1_aziza_abd": ("aziza_stern", .4, .4, 1.05, 1.2),
 "s1_abd_chips": ("abd_chips", .45, .5, 1.05, 1.18), "s1_hicham_phone": ("hicham_phone", .5, .45, 1.0, 1.15),
 "s1_aziza_hicham": ("aziza_stern", .5, .38, 1.25, 1.1), "s1_hicham_shield": ("hicham_phone", .52, .4, 1.3, 1.45),
 "s1_aziza_hips": ("wide_living", .62, .45, 1.6, 1.8),
 "s2_goal": ("amir_goal", .55, .4, 1.25, 1.05), "s2_abd_unbothered": ("abd_chips", .4, .35, 1.4, 1.55),
 "s2_amir_arms": ("amir_arms", .45, .45, 1.0, 1.15), "s2_aziza_between": ("wide_living", .55, .5, 1.25, 1.1),
 "s2_aziza_forget": ("aziza_forget", .7, .4, 1.0, 1.3), "s2_amir_smirk": ("amir_arms", .3, .35, 1.6, 1.75),
 "s2_aziza_glare": ("aziza_stern", .42, .36, 1.4, 1.6),
 "s3_alert": ("alert", .5, .45, 1.0, 1.15), "s3_aziza_panic": ("aziza_panic", .5, .4, 1.0, 1.25),
 "s3_hicham_couch": ("hicham_hack", .5, .45, 1.0, 1.2), "s3_abd_sigh": ("abd_sigh", .55, .45, 1.05, 1.25),
 "s3_amir_bounce": ("amir_bounce", .45, .4, 1.1, 1.3), "s3_aziza_lunge": ("scuffle", .35, .45, 1.3, 1.6),
 "s4_lego_crash": ("lego_crash", .5, .5, 1.1, 1.3), "s4_aziza_sorry": ("aziza_sorry", .5, .4, 1.05, 1.3),
 "s4_amir_tough": ("amir_sad", .58, .4, 1.1, 1.35), "s4_hicham_brick": ("rebuild", .45, .45, 1.05, 1.25),
 "s4_abd_fix": ("abd_fix", .5, .5, 1.05, 1.2), "s4_aziza_lead": ("lego_done", .5, .4, 1.0, 1.15),
 "s5_innocent": ("innocent", .5, .5, 1.0, 1.1), "s5_aziza_camera": ("innocent", .2, .45, 1.9, 2.1),
 "s5_amir_lean": ("innocent", .6, .45, 2.0, 2.3), "s5_hicham_false": ("hicham_false", .5, .4, 1.1, 1.5),
}
segs, lines, events, music, texts = [], [], [], [], []
t = 0.0
def seg(img, d, cx, cy, z0, z1, fx=(), cx1=None, cy1=None):
    global t
    segs.append(dict(img=img, t0=round(t, 3), t1=round(t + d, 3), cx0=cx, cy0=cy, cx1=cx if cx1 is None else cx1,
                     cy1=cy if cy1 is None else cy1, z0=z0, z1=z1, fx=list(fx))); t += d
def sfx(name, at, g=1.0): events.append((name, at, g))
def mus(style, t0, t1, g=1.0, key="C", bpm=110): music.append((style, t0, t1, g, key, bpm))
def text(kind, t0, t1, **kw): texts.append(dict(kind=kind, t0=round(t0, 3), t1=round(t1, 3), **kw))

L = {k: (spk, txt, gap, shot) for k, spk, txt, gap, shot in SCRIPT}
order = [k for k, *_ in SCRIPT]
def say_block(keys, fx=()):
    """Place lines; consecutive lines sharing a shot become one segment."""
    global t
    i = 0
    while i < len(keys):
        shot = L[keys[i]][3]; j = i
        while j + 1 < len(keys) and L[keys[j + 1]][3] == shot: j += 1
        start = t; tt_ = t
        for k in keys[i:j + 1]:
            spk, txt, gap, _ = L[k]; a = load(k, spk); tt_ += gap
            lines.append(dict(key=k, spk=spk, text=txt, t0=round(tt_, 3), t1=round(tt_ + len(a) / SR, 3)))
            tt_ += len(a) / SR + PAUSE.get(k, 0.35)
        img, cx, cy, z0, z1 = SH[shot]
        t = start; seg(img, tt_ - start, cx, cy, z0, z1, fx); i = j + 1

def between(a, b): return order[order.index(a):order.index(b) + 1]

# ===== COLD OPEN =====
mus("tense", 0, 4.6, .9, "Am", 120)
t = 0; L["h1"] = (*L["h1"][:3], "hook"); L["h2"] = (*L["h2"][:3], "hook2")
say_block(["h1"], fx=["shake"]); sfx("whoosh", 0.05, .8); say_block(["h2"])
sfx("scratch", t - .9, .9)
# ===== TITLE + MEET THE FAMILY =====
T_title = t; sfx("swoosh_up", t, 1); seg("TITLE", 6.0, .5, .5, 1.0, 1.06, fx=["fadein"])
text("episode", T_title + 1.2, T_title + 6.0, line1="EPISODE 1", line2="The Great Protocol Breakdown")
for img, cx, cy, name, tag, col in [("aziza_stern", .4, .4, "AZIZA", "The Leader (who forgets)", "#A86BFF"),
                                    ("abd_chips", .45, .5, "ABDEL-HAMID", "The Lazy Genius", "#FFD84D"),
                                    ("amir_goal", .55, .4, "AMIR", "The Football Tactician", "#FF8A1F"),
                                    ("hicham_phone", .5, .45, "HICHAM", "The 4-Year-Old Hacker", "#4FC3FF")]:
    text("name", t + .25, t + 3.6, name=name, tag=tag, color=col); sfx("pop", t + .25, .8)
    seg(img, 3.8, cx, cy, 1.15, 1.3)
mus("party", T_title, t, 1.0, "C", 120)
# ===== SCENE 1 - command center =====
s1 = t; sfx("whoosh", t, .6); seg("wide_living", 3.2, .5, .5, 1.25, 1.0, fx=["fadein"])
text("scene", s1 + .3, s1 + 3.0, label="SCENE 1: THE COMMAND CENTER")
say_block(between("s1a", "s1i")); sfx("crunch", lines[-7]["t0"] - .4, .7)
mus("bouncy", s1, t, 1.0, "C", 104)
# ===== SCENE 2 - pitch invasion =====
s2 = t; sfx("kick", t + 1.2, 1); sfx("whoosh", t + 1.3, 1); sfx("crowd", t + 1.6, .6)
say_block(between("s2a", "s2n"))
sfx("thinking", next(l for l in lines if l["key"] == "s2j")["t0"] - .8, .8)
mus("chase", s2, s2 + 9, 1.0, "C", 140); mus("bouncy", s2 + 9, t, .9, "F", 108)
# ===== SCENE 3 - the crisis =====
s3 = t; sfx("alarm", t + .2, .55); sfx("siren", t + .4, .5)
say_block(between("s3a", "s3j"), fx=["redpulse"])
sfx("beeps", s3 + 6, .5); sfx("beeps", s3 + 14, .5)
mus("tense", s3, t, 1.0, "Am", 128)
# ===== SLOW-MOTION SCUFFLE (action, no dialogue) =====
sm = t; sfx("slowmo_in", t, 1)
seg("scuffle", 3.4, .3, .45, 1.55, 1.75, fx=["slowmo"]); seg("scuffle", 3.0, .75, .4, 1.8, 1.6, fx=["slowmo"])
seg("scuffle", 3.0, .52, .35, 1.7, 1.9, fx=["slowmo"]); seg("scuffle", 2.6, .5, .5, 1.25, 1.05, fx=["slowmo"])
text("slowmo", sm + .2, t, label="NOOOOOOO...")
sfx("slow_no", sm + .3, .9); mus("slowmo", sm, t, 1.0, "Am", 60)
cr = t; sfx("crash", t + .15, 1.1); seg("lego_crash", 3.4, .5, .5, 1.1, 1.35, fx=["shake", "flash"])
sfx("silence_ring", t, .35)
# ===== SCENE 4 - lego rescue =====
L["s4a"] = (L["s4a"][0], L["s4a"][1], 1.0, L["s4a"][3]); s4 = t
say_block(between("s4a", "s4f")); mus("warm", s4, t, 1.0, "C", 72)
# rebuild montage
mo = t; text("scene", mo + .2, mo + 2.6, label="OPERATION: REBUILD!")
seg("rebuild", 4.0, .5, .5, 1.0, 1.2); seg("rebuild", 3.2, .62, .4, 1.6, 1.4)
seg("lego_done", 3.6, .5, .3, 1.8, 1.3); seg("abd_fix", 3.2, .3, .5, 1.3, 1.5)
for k in range(14): sfx("click", mo + .5 + k * .95, .5)
sfx("ding", t - .4, .8)
L["s4g"] = (L["s4g"][0], L["s4g"][1], .3, L["s4g"][3])
say_block(between("s4g", "s4k")); mus("party", mo, mo + 14, 1.0, "C", 124); mus("bouncy", mo + 14, t, .9, "C", 104)
# clean-up montage (fast)
cu = t; text("scene", cu + .1, cu + 2.2, label="MOM IS 2 MINUTES AWAY!"); sfx("car", cu + .2, .7)
seg("lego_done", 2.0, .5, .5, 1.2, 1.0, fx=["fast"]); seg("wide_living", 2.2, .3, .6, 1.4, 1.6, fx=["fast"], cx1=.7)
seg("abd_chips", 1.8, .45, .5, 1.6, 1.3, fx=["fast"]); seg("wide_living", 2.0, .7, .5, 1.5, 1.2, fx=["fast"], cx1=.3)
for k in range(9): sfx("zip", cu + .4 + k * .85, .5)
mus("chase", cu, t, 1.0, "C", 160); sfx("door", t - .3, .9)
# ===== SCENE 5 - outro =====
s5 = t; sfx("ding", t + .3, .6)
say_block(between("s5a", "s5f")); sfx("blooper", t - 3.3, 1.1)
mus("party", s5, t - 3.6, .8, "C", 120)
# end card
ec = t; seg("TITLE", 9.0, .5, .5, 1.0, 1.04, fx=["fadein"])
text("end", ec + .3, ec + 9.0, line1="SUBSCRIBE for Episode 2!", line2="Next time: The Snack Robot")
mus("party", ec, t, 1.0, "C", 120); sfx("pop", ec + .5, .8)
END = round(t + .3, 3)

# ================= AUDIO =================
N = int(END * SR) + SR
voice = np.zeros(N, np.float32); fx_ = np.zeros(N, np.float32); score = np.zeros(N, np.float32)
def add(b, t0, a, g=1.0):
    s = int(t0 * SR)
    if s < 0: a = a[-s:]; s = 0
    a = a[:max(0, N - s)]; b[s:s + len(a)] += a * g
for l in lines: add(voice, l["t0"], load(l["key"], l["spk"]), 1.0)
def tt(d): return np.arange(int(d * SR)) / SR
def smooth(x, n): return np.convolve(x, np.ones(n) / n, "same")
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def tone(f, d, dec=6, h=4): s = tt(d); return sum(np.sin(2*np.pi*f*k*s) * .6**k for k in range(1, h+1)) * np.exp(-s*dec) * np.minimum(1, s/.004)
def bell(f, d=1.3): s = tt(d); return (np.sin(2*np.pi*f*s) + .3*np.sin(2*np.pi*2.76*f*s)*np.exp(-s*4)) * np.exp(-s*3)
def sweep(f0, f1, d, g=.3): s = tt(d); f = np.geomspace(f0, f1, len(s)); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.sin(np.linspace(0, np.pi, len(s))) * g
def whoosh(d=.5): return smooth(noise(d), 80) * np.sin(np.linspace(0, np.pi, int(d*SR)))**2 * 6
def thud(f=90, d=.35): s = tt(d); return np.sin(2*np.pi*(f-50*s)*s)*np.exp(-s*12)*.8
def click(): s = tt(.05); n = noise(.05); return (n - smooth(n, 4)) * np.exp(-s*120) * .6
def boing(f0=300, d=.45): s = tt(d); f = f0*(1+1.2*np.exp(-s*9)*np.sin(2*np.pi*14*s)); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-s*6)*.45
def P(*xs):
    n = max(len(x) for x in xs); return sum(np.pad(x, (0, n - len(x))) for x in xs)
def gen(name):
    if name == "whoosh": return whoosh(.6)
    if name == "swoosh_up": return P(whoosh(.8), sweep(300, 1400, .8, .15))
    if name == "pop": return P(sweep(400, 1200, .08, .4), click())
    if name == "scratch": n = noise(.5); s = tt(.5); return (n - smooth(n, 3)) * np.abs(np.sin(2*np.pi*7*s)) * .5 * np.exp(-s*3)
    if name == "crunch": return np.concatenate([(noise(.07) - smooth(noise(.07), 3)) * .5 * np.exp(-tt(.07)*30) for _ in range(6)])
    if name == "kick": return P(thud(120, .3) * 1.4, click())
    if name == "crowd": d = 2.5; return smooth(noise(d), 12) * np.sin(np.linspace(0, np.pi, int(d*SR))) * 2.5
    if name == "thinking": return np.concatenate([tone(f, .25, 8, 2) for f in [880, 988, 880, 988, 880]]) * .5
    if name == "alarm":
        return np.concatenate([np.sign(np.sin(2*np.pi*(660 if i % 2 == 0 else 880)*tt(.25))) * .12 for i in range(12)])
    if name == "siren": d = 5; s = tt(d); f = 700 + 250*np.sin(2*np.pi*.6*s); return np.sin(2*np.pi*np.cumsum(f)/SR) * .18 * np.minimum(1, (d - s))
    if name == "beeps": return np.concatenate([tone(f, .1, 10, 2) for f in [1320, 990, 1320, 1760]]) * .4
    if name == "slowmo_in": return P(sweep(900, 80, 1.6, .5), thud(60, 1.2))
    if name == "slow_no":
        d = 3.2; s = tt(d); f = 140 * (1 - .25 * s / d)
        v = sum(np.sin(2*np.pi*np.cumsum(f*k)/SR) * [1, .5, .35, .2, .12][k-1] for k in range(1, 6))
        return v * np.sin(np.linspace(0, np.pi, len(s))) * .35
    if name == "crash":
        b = thud(70, .8) * 1.5
        for k in range(60): o = int(rng.uniform(0, .9) * SR); c = click() * rng.uniform(.4, 1); b = np.pad(b, (0, max(0, o + len(c) - len(b)))); b[o:o+len(c)] += c
        return b
    if name == "silence_ring": return np.sin(2*np.pi*3100*tt(2.5)) * np.exp(-tt(2.5)*1.2) * .05
    if name == "click": return P(click() * .8, tone(2200, .04, 60, 1) * .2)
    if name == "ding": return bell(1318, 1.5) * .5 + bell(1760, 1.5) * .3
    if name == "car":   # two friendly horn toots
        h = np.concatenate([tone(392, .18, 4, 3), np.zeros(int(.06*SR)), tone(392, .35, 4, 3)]) * .35
        b = thud(50, 1.0) * .4; b = np.pad(b, (0, max(0, len(h) - len(b)))); b[:len(h)] += h; return b
    if name == "zip": return whoosh(.25) * .8
    if name == "door": return P(thud(80, .4), click() * .5)
    if name == "blooper":   # sad-trombone style descending 'wah wah' + boing
        out = [];
        for f, d in [(392, .4), (370, .4), (349, .4), (330, 1.1)]:
            s = tt(d); vib = 1 + .02*np.sin(2*np.pi*6*s) * (d > .5)
            out.append(sum(np.sin(2*np.pi*np.cumsum(np.full(len(s), f*k)*vib)/SR) * .6**k for k in range(1, 5)) * np.minimum(1, s/.03) * np.exp(-s*1.2) * .35)
        return np.concatenate([boing(260), np.concatenate(out)])
    raise KeyError(name)
for name, at, g in events: add(fx_, at, gen(name).astype(np.float32), g)

KEYS = {"C": [[261.6, 329.6, 392], [196, 246.9, 293.7], [220, 261.6, 329.6], [174.6, 220, 261.6]],
        "F": [[174.6, 220, 261.6], [261.6, 329.6, 392], [146.8, 174.6, 220], [196, 246.9, 293.7]],
        "Am": [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7], [164.8, 207.7, 246.9]]}
def kick(): s = tt(.12); return np.sin(2*np.pi*(55+80*np.exp(-s*30))*s)*np.exp(-s*14)
def hat(): s = tt(.04); n = noise(.04); return (n - smooth(n, 3)) * np.exp(-s*90) * .25
for style, t0, t1, g, key, bpm in music:
    prog = KEYS[key]; beat = 60 / bpm; x = t0; bar = 0; G = .05 * g
    if style == "slowmo":
        s = tt(t1 - t0); add(score, t0, (np.sin(2*np.pi*55*s) + .5*np.sin(2*np.pi*82.4*s)) * np.minimum(1, s/1.5) * G * 2)
    while x < t1 - .05 and style != "slowmo":
        ch = prog[bar % len(prog)]
        for b in range(4):
            tb = x + b * beat
            if tb >= t1 - .05: break
            if style == "bouncy":      # pizzicato comedy
                add(score, tb, tone(ch[0] / 2, .22, 12, 4), G * 1.5)
                add(score, tb + beat / 2, tone(ch[(b + 1) % 3], .12, 18, 3), G * .9)
                if b in (1, 3): add(score, tb, hat(), G * 2)
            elif style == "chase":
                add(score, tb, tone(ch[0] / 2, .2, 10, 4), G * 1.3); add(score, tb + beat / 2, tone(ch[1], .15, 12, 3), G)
                add(score, tb, kick(), G * 3); add(score, tb + beat / 2, hat(), G * 2)
            elif style == "tense":
                add(score, tb, tone(ch[0] / 2, .18, 14, 3), G * 1.4); add(score, tb + beat / 2, tone(ch[0] / 2, .18, 14, 3), G * 1.1)
                if b == 0: add(score, tb, tone(ch[2] * 2, .6, 5, 2), G * .6)
                add(score, tb + beat / 4, hat(), G * 1.5)
            elif style == "warm":
                for j, f in enumerate(ch): add(score, tb + j * .03, tone(f, 1.2, 2.2, 3), G * .6)
            elif style == "party":
                for j, f in enumerate(ch): add(score, tb + j * .012, tone(f, .5, 6, 4), G * .8)
                if b % 2 == 0: add(score, tb, kick(), G * 3)
                add(score, tb + beat / 2, bell([784, 880, 1047, 880][b], .5), G * .5); add(score, tb + beat / 2, hat(), G * 1.5)
        x += 4 * beat; bar += 1
for i, f in enumerate([392, 494, 587, 784]): add(score, T_title + i * .15, tone(f, 1.0, 3, 4), .09)   # title sting
duck = 1 - np.clip(smooth(np.abs(voice), 4800) * 6, 0, .65)
mix = voice * 1.2 + fx_ * .7 + score * duck
mix = mix[:int(END * SR)]; mix /= np.max(np.abs(mix)) / .95
sf.write(f"{OUT}/mix.wav", mix, SR, subtype="PCM_16")
# per-frame voice level (for subtle 'talking' camera pulse)
FPS = 24; hop = SR // FPS; nf = int(END * FPS)
lvl = np.array([np.sqrt(np.mean(voice[i*hop:(i+1)*hop]**2)) for i in range(nf)]); lvl = np.clip(lvl / (np.percentile(lvl[lvl > .01], 90) + 1e-6), 0, 1)
json.dump(dict(end=END, fps=FPS, segs=segs, texts=texts, lines=lines, level=[round(float(v), 3) for v in lvl]), open(f"{OUT}/timeline.json", "w"))
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
NAMES = {"AZI": "Aziza", "ABD": "Abdel-Hamid", "AMI": "Amir", "HIC": "Hicham"}
import re
with open(f"{OUT}/ep01.srt", "w") as f:
    for i, l in enumerate(lines, 1): f.write(f"{i}\n{ts(l['t0'])} --> {ts(l['t1'])}\n{re.sub(r'\[[^]]*\]\s*', '', l['text'])}\n\n")
print("END", END, "segments", len(segs), "lines", len(lines))
print("chapters:", {k: round(v, 1) for k, v in dict(title=T_title, s1=s1, s2=s2, s3=s3, scuffle=sm, s4=s4, rebuild=mo, cleanup=cu, s5=s5, end=ec).items()})
