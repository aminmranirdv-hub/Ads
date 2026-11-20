#!/usr/bin/env python3
"""Make the 45-60 s Facebook cut of a clip: python3 tools/fbcut.py <clip_dir> <first_cue> <last_cue> [end_pad]
Creates <clip_dir>/fb/ with symlinks + config (ranges reduced, effects whose anchors fall outside dropped),
runs autobuild, and fixes asset paths so make_short can run from fb/."""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
clip = Path(sys.argv[1]).resolve(); a, b = int(sys.argv[2]), int(sys.argv[3])
pad = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
fb = clip / "fb"; (fb / "export").mkdir(parents=True, exist_ok=True)
for f in ("source.mp4", "words.json", "subs.srt"):
    p = fb / f
    if not p.exists(): p.symlink_to(Path("..") / f)
cfg = json.load(open(clip / "config.json")); cfg["ranges"] = [[a, b]]; cfg["end_pad"] = pad
spec = json.load(open(clip / "edit.json"))
for k in ("segments", "zooms", "sfx", "overlays", "editorial_captions"): spec.pop(k, None)
json.dump(spec, open(fb / "edit.json", "w"), ensure_ascii=False, indent=2)
for _ in range(30):
    json.dump(cfg, open(fb / "config.json", "w"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, str(ROOT / "tools/autobuild.py")], cwd=fb, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if r.returncode == 0 and "not found" not in out: print(out.strip().splitlines()[-1]); break
    bad = [l for l in out.splitlines() if "not found" in l]
    if not bad: print(out); sys.exit(1)
    w = bad[0].split(":")[-1].strip().split(" #")[0]
    n = len(cfg["effects"]); cfg["effects"] = [e for e in cfg["effects"] if e["word"].lower() != w.lower()]
    if len(cfg["effects"]) == n: print(out); sys.exit(1)
s = (fb / "edit.json").read_text(encoding="utf-8").replace('"../../../../assets', f'"{ROOT}/assets')
(fb / "edit.json").write_text(s, encoding="utf-8")
