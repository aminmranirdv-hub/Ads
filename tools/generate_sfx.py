#!/usr/bin/env python3
"""Synthesize the channel's ORIGINAL sound-effect library with ffmpeg.

Every sound here is generated mathematically from scratch, so the channel
owns it outright: no licence questions, no Content ID claims.

Usage: python3 tools/generate_sfx.py [--out assets/sfx]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import REPO, require_ffmpeg, run

SR = 48000
N = "(2*random(0)-1)"  # white noise sample

SOUNDS = {
    # name: (duration_s, expression, extra audio filters, description)
    "impact": (1.2,
               f"0.9*sin(2*PI*55*t)*exp(-5*t)+0.6*sin(2*PI*110*t)*exp(-9*t)+0.5*{N}*exp(-28*t)",
               "lowpass=f=2500", "Low punch-line hit / boom"),
    "boing": (0.9,
              "0.8*sin(2*PI*(180*t+6*sin(2*PI*11*t)))*exp(-3.5*t)",
              "", "Cartoon spring for silly moments"),
    "riser": (2.0,
              f"(t/2)*(0.5*sin(2*PI*(120*t+220*t*t))+0.35*{N})",
              "highpass=f=300,lowpass=f=9000", "Suspense build before a punchline"),
    "record_scratch": (0.55,
                       f"(0.6*sin(2*PI*(400*t-30*cos(2*PI*9*t)))+0.6*{N})*exp(-3*t)*(0.5+0.5*sin(2*PI*18*t))",
                       "bandpass=f=1400:width_type=h:w=1800,volume=8dB", "Scratch for 'wait, WHAT?' stops"),
    "dramatic_sting": (2.6,
                       "(0.35*(sin(2*PI*110*t)+sin(2*PI*130.8*t)+sin(2*PI*164.8*t)+0.5*sin(2*PI*55*t)))"
                       "*(lt(t,0.25)*exp(-6*t)+between(t,0.35,0.6)*exp(-6*(t-0.35))+gte(t,0.7)*exp(-1.6*(t-0.7)))",
                       "lowpass=f=3000", "Three-hit 'dun dun DUNN' realization"),
    "whoosh": (0.7,
               f"{N}*sin(PI*t/0.7)*sin(PI*t/0.7)",
               "bandpass=f=1800:width_type=h:w=2500,volume=6dB", "Transition / zoom whoosh"),
    "pop": (0.12,
            "0.8*sin(2*PI*(900*t+3000*t*t))*exp(-35*t)",
            "", "Caption / sticker pop-in"),
    "crickets": (2.4,
                 "0.25*sin(2*PI*4600*t)*gt(sin(2*PI*28*t),0)*lt(mod(t,0.8),0.22)",
                 "", "Awkward silence"),
    "tension_tick": (2.0,
                     "0.7*sin(2*PI*1800*t)*exp(-80*mod(t,0.5))",
                     "", "Clock tick for a dramatic pause"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "assets" / "sfx"))
    args = ap.parse_args()
    require_ffmpeg()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    index = ["# Original SFX library (synthesized, channel-owned)", "",
             "| file | duration | use |", "|---|---|---|"]
    for name, (dur, expr, filt, desc) in SOUNDS.items():
        af = "afade=t=out:st={:.3f}:d=0.05".format(max(0, dur - 0.05))
        if filt:
            af = filt + "," + af
        af += ",alimiter=limit=0.9,pan=stereo|c0=c0|c1=c0"
        dst = out / f"{name}.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "lavfi", "-i", f"aevalsrc='{expr}':s={SR}:d={dur}",
             "-af", af, "-c:a", "pcm_s16le", str(dst)])
        index.append(f"| `{name}.wav` | {dur:.2f}s | {desc} |")
        print(f"wrote {dst}")
    (out / "README.md").write_text("\n".join(index) + "\n\nRegenerate with `python3 tools/generate_sfx.py`.\n",
                                   encoding="utf-8")


if __name__ == "__main__":
    main()
