#!/usr/bin/env python3
"""Write the per-clip deliverables sheet (Markdown) from an edit spec.

Covers: source reference, rights status, timestamps, editing timeline,
overlays, SFX, hooks, TikTok caption, YouTube Shorts title/description,
hashtags, and an empty post-publication performance table.

Usage: python3 tools/deliverables.py projects/<clip>/edit.json [--out deliverables.md]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import load_json, parse_time
from make_short import build_timeline, total_duration


def ts(x: float) -> str:
    m, s = divmod(x, 60)
    return f"{int(m):02d}:{s:05.2f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out")
    args = ap.parse_args()
    p = Path(args.spec)
    spec = load_json(p)
    tl = build_timeline(spec["segments"])
    pub = spec.get("publishing", {})
    src = spec.get("source", {})
    r = spec.get("rights", {})
    L = [f"# Deliverables - {spec.get('id')}", "",
         "## 1. Source reference",
         f"- Comedian: {spec.get('comedian', '')}",
         f"- Title: {src.get('title', '')}",
         f"- URL: {src.get('url') or '_not provided_'}",
         f"- Local file: `{src.get('file', '')}`", "",
         "## 2. Rights verification",
         f"- Status: **{r.get('status', 'unknown')}**",
         f"- Evidence: {r.get('evidence', '')}",
         f"- Notes: {r.get('notes', '')}", "",
         "## 3. Selected timestamps (source)",
         *[f"- {s['in']} -> {s['out']}" + (f" (+{s['freeze']}s freeze)" if s.get('freeze') else "") for s in spec["segments"]], "",
         "## 4. Editing timeline (output)",
         "| out time | event |", "|---|---|"]
    events = []
    for i, seg in enumerate(tl):
        events.append((seg["out_start"], f"Segment {i + 1}: source {seg['src_in']:.2f}-{seg['src_out']:.2f}s"))
        if seg["freeze"]:
            events.append((seg["out_start"] + seg["src_out"] - seg["src_in"], f"Freeze-frame {seg['freeze']}s"))
    for z in spec.get("zooms", []):
        events.append((parse_time(z["at"]), f"Punch-in zoom x{z.get('scale', 1.15)} for {z.get('dur', 1.5)}s"))
    for c in spec.get("editorial_captions", []):
        events.append((parse_time(c["start"]), f"Editorial caption: \"{c['text']}\""))
    for o in spec.get("overlays", []):
        events.append((parse_time(o["start"]), f"Sticker `{o['file']}` ({o.get('position', 'upper_center')})"))
    for f in spec.get("sfx", []):
        events.append((parse_time(f["at"]), f"SFX `{Path(f['file']).name}` {f.get('gain_db', -8)} dB"))
    for t, e in sorted(events):
        L.append(f"| {ts(t)} | {e} |")
    L += ["", f"Total duration: **{total_duration(tl):.2f}s**", "",
          "## 5-9. Files",
          f"- Final vertical video: `export/{spec.get('id')}.mp4`",
          f"- Subtitles: `{spec.get('subtitles', '')}` (language: {spec.get('language', '')})",
          f"- Thumbnail: `export/{spec.get('id')}.thumb.jpg`", "",
          "## 10. Alternative hooks",
          *[f"{i}. {h}" for i, h in enumerate(pub.get("hooks", []), 1)], "",
          "## 11. TikTok caption", pub.get("tiktok_caption", ""), "",
          "## 12. YouTube Shorts",
          f"- **Title:** {pub.get('youtube_title', '')}",
          f"- **Description:** {pub.get('youtube_description', '')}", "",
          "## 13. Hashtags", " ".join(pub.get("hashtags", [])), "",
          "## 14. Performance (fill in after publication)",
          "| platform | posted | views 24h | views 7d | avg watch % | likes | shares | saves | comments | notes |",
          "|---|---|---|---|---|---|---|---|---|---|",
          "| TikTok | | | | | | | | | |",
          "| YouTube Shorts | | | | | | | | | |",
          "| Instagram Reels | | | | | | | | | |", ""]
    out = Path(args.out) if args.out else p.parent / "deliverables.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
