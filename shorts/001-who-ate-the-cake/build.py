"""Assemble Short #001 from the two generated clips.

Timeline (output seconds):
  0.0-14.5   clip A 0.0-14.5     interrogation -> side-eye -> kitten
  14.5-18.2  clip B 0.0-3.7      "Mochi... who did it?"
  18.2-28.3  clip B 4.9-15.0     (tilt shortened) pug reveal -> owner laughs
  28.3-30.3  freeze on the pug (clip B @10.5) with slow push-in + GUILTY stamp
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
OVL = HERE / "overlays"
SFX = HERE / "sfx"
PACK = HERE.parent.parent / "meme-pack"
OUT = HERE / "final"
OUT.mkdir(exist_ok=True)

subprocess.run(["python3", str(HERE / "render_overlays.py"), str(OVL)], check=True)
spec = json.loads((HERE / "overlays.json").read_text())

# freeze frame for the ending
freeze_png = OVL / "_freeze.png"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "10.5", "-i", str(RAW / "clipB.mp4"),
                "-frames:v", "1", str(freeze_png)], check=True)

inputs = ["-i", str(RAW / "clipA.mp4"), "-i", str(RAW / "clipB.mp4"),
          "-loop", "1", "-t", "2.0", "-i", str(freeze_png)]
n = 3
ov_idx = {}
for item in spec:
    inputs += ["-i", str(OVL / f"{item['id']}.png")]
    ov_idx[item["id"]] = n
    n += 1
regrets_idx = n
inputs += ["-i", str(PACK / "stickers" / "zero-regrets.png")]
n += 1
arrow_idx = n
inputs += ["-i", str(PACK / "stickers" / "red-arrow-down.png")]
n += 1
sfx_plan = [  # (file, output time, gain)
    (SFX / "boom.wav", 0.0, 0.9),
    (SFX / "whoosh.wav", 10.35, 0.8),
    (PACK / "sfx" / "pop.wav", 11.7, 0.6),
    (SFX / "dundun.wav", 17.4, 0.9),
    (PACK / "sfx" / "boom-hit.wav", 19.4, 0.8),
    (PACK / "sfx" / "pop.wav", 23.0, 0.6),
    (PACK / "sfx" / "record-scratch.wav", 28.25, 0.7),
    (PACK / "sfx" / "stamp-thud.wav", 28.45, 1.0),
]
sfx_idx = []
for f, t, g in sfx_plan:
    inputs += ["-i", str(f)]
    sfx_idx.append((n, t, g))
    n += 1

V = "scale=1080:1920,setsar=1,fps=30,format=yuv420p"
fc = [
    f"[0:v]trim=0:14.5,setpts=PTS-STARTPTS,{V}[va]",
    f"[1:v]trim=0:3.7,setpts=PTS-STARTPTS,{V}[vb1]",
    f"[1:v]trim=4.9:15.0,setpts=PTS-STARTPTS,{V}[vb2]",
    # slow push-in on the freeze frame
    f"[2:v]scale=2160:3840,zoompan=z='1+0.0025*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=60:s=1080x1920:fps=30,setsar=1,format=yuv420p,trim=0:2.0[vf]",
    "[va][vb1][vb2][vf]concat=n=4:v=1:a=0[base]",
    "[0:a]atrim=0:14.5,asetpts=PTS-STARTPTS[aa]",
    "[1:a]atrim=0:3.7,asetpts=PTS-STARTPTS[ab1]",
    "[1:a]atrim=4.9:15.0,asetpts=PTS-STARTPTS[ab2]",
    "anullsrc=r=48000:cl=stereo,atrim=0:2.0[af]",
]
# normalise audio formats before concat
for lab in ("aa", "ab1", "ab2", "af"):
    fc.append(f"[{lab}]aformat=sample_rates=48000:channel_layouts=stereo[{lab}n]")
fc.append("[aan][ab1n][ab2n][afn]concat=n=4:v=0:a=1[dialog]")

cur = "base"
for i, item in enumerate(spec):
    idx = ov_idx[item["id"]]
    nxt = f"v{i}"
    s, e = item["start"], item["end"]
    fc.append(f"[{idx}:v]format=rgba[o{i}]")
    fc.append(f"[{cur}][o{i}]overlay=0:0:enable='between(t,{s},{e})'[{nxt}]")
    cur = nxt
# 0% REGRETS sticker next to the pug
fc.append(f"[{regrets_idx}:v]format=rgba,scale=560:-1[reg]")
fc.append(f"[{cur}][reg]overlay=(W-w)/2:250:enable='between(t,23.0,25.8)'[vreg]")
# red arrow pointing UP at the pug during the reveal
fc.append(f"[{arrow_idx}:v]format=rgba,vflip,scale=-1:330[arr]")
fc.append(f"[vreg][arr]overlay=(W-w)/2:620:enable='between(t,19.4,21.0)'[vout]")

mix = ["[dialog]volume=1.0[d0]"]
labels = ["[d0]"]
for k, (idx, t, g) in enumerate(sfx_idx):
    ms = int(t * 1000)
    mix.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g},adelay={ms}|{ms}[s{k}]")
    labels.append(f"[s{k}]")
fc += mix
fc.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=first,"
          "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

out = OUT / "who-ate-the-cake_short.mp4"
cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc),
       "-map", "[vout]", "-map", "[aout]", "-t", "30.3",
       "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
subprocess.run(cmd, check=True)
print("wrote", out)
