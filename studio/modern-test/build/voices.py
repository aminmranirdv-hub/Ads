"""Kokoro voices + per-frame mouth envelopes for the Blender lip sync. usage: voices.py <out> <kokoro_dir>"""
import sys, json, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
OUT, KD = sys.argv[1], sys.argv[2]
K = Kokoro(f"{KD}/model.onnx", f"{KD}/voices.npz"); SR, FPS = 48000, 24
LINES = [("PIP", "af_sky", 1.05, 250, "Hi Pebble! Do you want to play ball with me?", 0.6),
         ("PEB", "am_puck", 0.9, 300, "Yes, please! Playing together is the best!", 0.5)]
t, clips, T = 0.0, [], {}
for spk, v, sp, pc, txt, gap in LINES:
    a, sr = K.create(txt, voice=v, speed=sp, lang="en-us"); sf.write(f"{OUT}/{spk}_raw.wav", a, sr)
    subprocess.run(["sox", f"{OUT}/{spk}_raw.wav", "-r", str(SR), "-c", "1", f"{OUT}/{spk}.wav", "pitch", str(pc), "norm", "-3"], check=True, stderr=subprocess.DEVNULL)
    d, _ = sf.read(f"{OUT}/{spk}.wav", dtype="float32"); i = np.where(np.abs(d) > 0.01)[0]; d = d[i[0]:i[-1] + 1000]
    t += gap; clips.append((spk, t, d)); T[spk] = [round(t, 3), round(t + len(d) / SR, 3)]; t += len(d) / SR
T["end"] = round(t + 1.6, 3); N = int(T["end"] * SR)
voice = np.zeros(N, np.float32); env = {}
for spk, t0, d in clips:
    s = int(t0 * SR); voice[s:s + len(d)] += d
    tr = np.zeros(N, np.float32); tr[s:s + len(d)] = d; hop = SR // FPS
    m = np.array([np.sqrt(np.mean(tr[k*hop:(k+1)*hop] ** 2)) for k in range(int(T["end"] * FPS))])
    env[spk] = [round(float(x), 3) for x in np.clip(m / (np.percentile(m[m > .01], 90) + 1e-6), 0, 1)]
sf.write(f"{OUT}/voices.wav", voice, SR, subtype="PCM_16")
json.dump({"T": T, "mouth": env, "fps": FPS}, open(f"{OUT}/lipsync.json", "w")); print(T)
