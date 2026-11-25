"""Transcribe a clip (word timestamps) and write a 1fps contact sheet.

Usage: python3 tools/analyze_clip.py <clip.mp4> <sheet.jpg>
Needs: pip install faster-whisper
"""
import subprocess
import sys
import tempfile

import numpy as np
from faster_whisper import WhisperModel

clip, sheet = sys.argv[1], sys.argv[2]
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", clip,
                "-vf", "fps=1,scale=270:-1,tile=8x2", sheet], check=True)
with tempfile.NamedTemporaryFile(suffix=".f32") as f:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-ac", "1", "-ar", "16000",
                    "-f", "f32le", f.name], check=True)
    audio = np.fromfile(f.name, dtype=np.float32)
model = WhisperModel("base.en", device="cpu", compute_type="int8")
segs, _ = model.transcribe(audio, word_timestamps=True)
for s in segs:
    print(f"{s.start:5.2f}-{s.end:5.2f}: {s.text.strip()}  |",
          " ".join(f"{w.word.strip()}@{w.start:.2f}" for w in s.words))
