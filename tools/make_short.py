#!/usr/bin/env python3
"""Render a vertical 1080x1920 comedy short from an edit spec (JSON).

What it does, in order:
  1. Cuts the source into the listed segments (jump cuts) with optional
     freeze-frame holds after a segment (e.g. hold on the reaction face).
  2. Frames 16:9 (or any) footage into 9:16: blurred-fill or cropped.
  3. Applies punch-in zooms at chosen moments on the output timeline.
  4. Overlays original reaction stickers.
  5. Burns animated subtitles (source-timed SRT is remapped through the cuts,
     key words highlighted) and boxed editorial captions that are visually
     distinct from the comedian's words.
  6. Mixes sound effects and normalises loudness to -14 LUFS.

Usage:
  python3 tools/make_short.py projects/<clip>/edit.json [--out out.mp4] [--draft] [-v]

The renderer refuses to make a publishable export unless the spec's
rights.status is an approved status. Use --draft for internal previews of
clips whose rights are still pending (output is watermarked DRAFT).
"""
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

from common import (APPROVED_RIGHTS, DRAFT_ONLY_RIGHTS, USER_ASSUMED_RIGHTS, OUT_FPS, OUT_H, OUT_W, die, filter_escape,
                    fmt_ass_time, hex_to_ass, load_brand, load_json, parse_srt, parse_time,
                    require_ffmpeg, run)

POSITIONS = {
    # (x, y) expressions for overlay of a sticker of size w x h, inside safe zones
    "top_left": ("80", "300"),
    "top_right": ("W-w-160", "300"),
    "center": ("(W-w)/2", "(H-h)/2"),
    "upper_center": ("(W-w)/2", "430"),
    "lower_left": ("80", "H-h-700"),
    "lower_right": ("W-w-160", "H-h-700"),
}


# ---------------------------------------------------------------- timeline
def build_timeline(segments: list[dict]) -> list[dict]:
    tl, cursor = [], 0.0
    for seg in segments:
        a, b = parse_time(seg["in"]), parse_time(seg["out"])
        if b <= a:
            die(f"segment out <= in: {seg}")
        freeze = float(seg.get("freeze", 0))
        tl.append({"src_in": a, "src_out": b, "out_start": cursor, "freeze": freeze})
        cursor += (b - a) + freeze
    return tl


def total_duration(tl: list[dict]) -> float:
    last = tl[-1]
    return last["out_start"] + (last["src_out"] - last["src_in"]) + last["freeze"]


def remap_cues(cues: list[dict], tl: list[dict]) -> list[dict]:
    """Map source-timed cues onto the edited output timeline."""
    out = []
    for cue in cues:
        for seg in tl:
            s, e = max(cue["start"], seg["src_in"]), min(cue["end"], seg["src_out"])
            if e - s <= 0.05:
                continue
            o_s = seg["out_start"] + (s - seg["src_in"])
            o_e = seg["out_start"] + (e - seg["src_in"])
            if cue["end"] >= seg["src_out"] - 0.01 and seg["freeze"]:
                o_e += seg["freeze"]  # keep the line on screen during the freeze-frame
            out.append({"start": o_s, "end": o_e, "text": cue["text"], "trans": cue.get("trans", "")})
    return out


def attach_translations(cues: list[dict], trans: list[dict]) -> list[dict]:
    """Give each original cue the translated cue it overlaps most (same source timing)."""
    for c in cues:
        best, best_ov = None, 0.0
        for t in trans:
            ov = min(c["end"], t["end"]) - max(c["start"], t["start"])
            if ov > best_ov:
                best, best_ov = t, ov
        c["trans"] = best["text"] if best else ""
    return cues


TRANSLATION_LABELS = {"fr": "Sous-titres FR : traduction", "en": "English subtitles: translation"}


# ---------------------------------------------------------------- subtitles
def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def highlight_words(text: str, words: list[str], hl_color: str, base_color: str) -> str:
    if not words:
        return text
    pattern = re.compile(r"(?<!\w)(" + "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True)) + r")(?!\w)",
                         re.IGNORECASE)
    return pattern.sub(lambda m: "{\\c" + hl_color + "}" + m.group(1) + "{\\c" + base_color + "}", text)


def build_ass(spec: dict, brand: dict, cues: list[dict], path: Path, draft: bool) -> None:
    colors, sub, ed = brand["colors"], brand["subtitle"], brand["editorial"]
    lang = spec.get("language", "fr")
    font = brand["fonts"].get(lang, brand["fonts"]["default"])
    ed_font = brand["fonts"].get(lang, brand["fonts"]["default"])
    white, black = hex_to_ass(colors["text"]), hex_to_ass(colors["outline"])
    hl = hex_to_ass(colors["highlight"])
    box, box_text = hex_to_ass(colors["editorial_box"]), hex_to_ass(colors["editorial_text"])
    uppercase = sub.get("uppercase", True) and lang not in ("ar", "darija_ar")
    pop = int(sub.get("pop_in_ms", 90))

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {OUT_W}
PlayResY: {OUT_H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{font},{sub['size']},{white},{white},{black},&H96000000,-1,0,0,0,100,100,0,0,1,{sub['outline']},{sub['shadow']},2,{sub['margin_left']},{sub['margin_right']},{sub['margin_bottom']},1
Style: Trans,{brand['fonts'].get('translation', brand['fonts']['default'])},{brand['subtitle'].get('translation_size', 54)},{hl},{hl},{black},&H96000000,-1,0,0,0,100,100,0,0,1,5,2,2,{sub['margin_left']},{sub['margin_right']},{sub['margin_bottom']},1
Style: Editorial,{ed_font},{ed['size']},{box_text},{box_text},{box},{box},-1,0,0,0,100,100,0,0,3,14,0,8,90,150,{ed['margin_top']},1
Style: Mark,{brand['fonts']['fallback']},34,&H60FFFFFF,&H60FFFFFF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,1,{brand['safe_zone_px']['left'] + 30},0,{brand['safe_zone_px']['bottom'] - 10},1
Style: Draft,{brand['fonts']['fallback']},120,&HA00000FF,&HA00000FF,&H80000000,&H00000000,-1,0,0,0,100,100,0,-30,1,3,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    words = spec.get("highlight_words", [])
    for c in cues:
        text = ass_escape(c["text"].upper() if uppercase else c["text"])
        text = highlight_words(text, [w.upper() if uppercase else w for w in words], hl, white)
        anim = f"{{\\fscx82\\fscy82\\t(0,{pop},\\fscx100\\fscy100)}}"
        if c.get("trans"):
            text += "\\N{\\rTrans}" + ass_escape(c["trans"])
        lines.append(f"Dialogue: 1,{fmt_ass_time(c['start'])},{fmt_ass_time(c['end'])},Sub,,0,0,0,,{anim}{text}")

    for cap in spec.get("editorial_captions", []):
        txt = ass_escape(cap["text"])
        anim = "{\\fad(120,120)}"
        lines.append(f"Dialogue: 2,{fmt_ass_time(parse_time(cap['start']))},{fmt_ass_time(parse_time(cap['end']))},"
                     f"Editorial,,0,0,0,,{anim}{txt}")

    end = fmt_ass_time(spec["_duration"])
    mark = brand.get("watermark", "")
    tl = spec.get("translation", {}).get("language")
    if tl in TRANSLATION_LABELS:
        mark = (mark + "  ·  " if mark else "") + TRANSLATION_LABELS[tl]
    if mark:
        lines.append(f"Dialogue: 0,0:00:00.00,{end},Mark,,0,0,0,,{ass_escape(mark)}")
    if draft:
        lines.append(f"Dialogue: 3,0:00:00.00,{end},Draft,,0,0,0,,DRAFT - NOT FOR PUBLICATION")
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- video
def framing_filter(spec: dict) -> str:
    mode = spec.get("framing", {}).get("mode", "blur_fill")
    if mode == "blur_fill":
        return (f"split[bgsrc][fgsrc];"
                f"[bgsrc]scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,crop={OUT_W}:{OUT_H},"
                f"gblur=sigma=40,eq=brightness=-0.12:saturation=1.1[bg];"
                f"[fgsrc]scale={OUT_W}:-2[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2-{int(spec.get('framing', {}).get('raise_px', 120))}")
    if mode == "crop":
        x = float(spec.get("framing", {}).get("crop_x", 0.5))  # 0 = left edge, 1 = right edge
        return (f"scale=-2:{OUT_H},crop={OUT_W}:{OUT_H}:(iw-{OUT_W})*{x}:0")
    if mode == "fit":
        return (f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=decrease,"
                f"pad={OUT_W}:{OUT_H}:(ow-iw)/2:(oh-ih)/2:color=black")
    die(f"unknown framing mode {mode}")
    return ""


def zoom_filter(zooms: list[dict]) -> str | None:
    if not zooms:
        return None
    terms = []
    for z in zooms:
        a = parse_time(z["at"])
        b = a + float(z.get("dur", 1.5))
        s = float(z.get("scale", 1.15))
        e = float(z.get("ease", 0.12))
        terms.append(f"({s - 1:.4f})*min(1\\,(it-{a:.3f})/{e:.3f})*between(it\\,{a:.3f}\\,{b:.3f})")
    zexpr = "1+" + "+".join(terms)
    # Upscale first so the zoompan crop doesn't jitter on sub-pixel moves.
    return (f"scale={OUT_W * 2}:{OUT_H * 2},"
            f"zoompan=z='{zexpr}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={OUT_W}x{OUT_H}:fps={OUT_FPS}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out")
    ap.add_argument("--draft", action="store_true", help="internal preview; allowed while rights are pending")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    require_ffmpeg()
    spec_path = Path(args.spec).resolve()
    base = spec_path.parent
    spec = load_json(spec_path)
    brand = load_brand()
    if "\"__" in open(spec_path, encoding="utf-8").read():
        die("edit.json still has __placeholder__ values (zoom/sticker/SFX times). Set them from the transcript first.")

    status = spec.get("rights", {}).get("status", "unknown")
    if status in USER_ASSUMED_RIGHTS:
        print("NOTE: rights status 'user_assumed': no licence on file; the channel owner accepts the copyright risk.")
    elif status not in APPROVED_RIGHTS:
        if args.draft and status in DRAFT_ONLY_RIGHTS | APPROVED_RIGHTS:
            print(f"NOTE: rights status '{status}' -> rendering watermarked internal DRAFT only.")
        elif args.draft:
            die(f"rights status '{status}' does not allow even a draft. Set rights.status to 'pending' once a request is in progress.")
        else:
            die(f"rights status '{status}' is not approved for publication ({sorted(APPROVED_RIGHTS)}). "
                f"Use --draft for an internal preview.")
    draft = args.draft or status not in APPROVED_RIGHTS | USER_ASSUMED_RIGHTS

    src = (base / spec["source"]["file"]).resolve()
    if not src.exists():
        die(f"source footage not found: {src}")

    tl = build_timeline(spec["segments"])
    spec["_duration"] = total_duration(tl)
    out = Path(args.out).resolve() if args.out else base / "export" / f"{spec.get('id', 'short')}{'_DRAFT' if draft else ''}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cues = []
        if spec.get("subtitles"):
            raw = parse_srt(base / spec["subtitles"])
            if spec.get("translation", {}).get("file"):
                raw = attach_translations(raw, parse_srt(base / spec["translation"]["file"]))
            cues = raw if spec.get("subtitles_timing", "source") == "output" else remap_cues(raw, tl)
        ass_path = td / "subs.ass"
        build_ass(spec, brand, cues, ass_path, draft)

        # 1. segments: cut each one to a near-lossless intermediate, then join them.
        #    (A single trim/concat graph buffers every branch and runs out of memory
        #    with dozens of jump cuts.)
        listing = []
        for i, seg in enumerate(tl):
            part = td / f"seg{i:03d}.mkv"
            vf = f"fps={OUT_FPS},setsar=1"
            af = "aresample=48000,aformat=channel_layouts=stereo"
            if seg["freeze"]:
                vf += f",tpad=stop_mode=clone:stop_duration={seg['freeze']:.3f}"
                af += f",apad=pad_dur={seg['freeze']:.3f}"
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-ss", f"{seg['src_in']:.3f}", "-to", f"{seg['src_out']:.3f}", "-i", str(src),
                 "-vf", vf, "-af", af, "-t", f"{seg['src_out'] - seg['src_in'] + seg['freeze']:.3f}",
                 "-c:v", "libx264", "-preset", "ultrafast", "-crf", "10", "-pix_fmt", "yuv420p",
                 "-c:a", "pcm_s16le", str(part)])
            listing.append(f"file '{part}'")
        (td / "parts.txt").write_text("\n".join(listing) + "\n")
        joined = td / "joined.mkv"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(td / "parts.txt"), "-c", "copy", str(joined)])

        inputs = ["-i", str(joined)]
        fc = ["[0:v]setpts=PTS-STARTPTS[vc]", "[0:a]asetpts=PTS-STARTPTS[ac]"]
        # 2. framing
        fc.append(f"[vc]{framing_filter(spec)}[vf]")
        last = "vf"
        # 3. zooms
        zf = zoom_filter(spec.get("zooms", []))
        if zf:
            fc.append(f"[{last}]{zf}[vz]")
            last = "vz"
        # 4. sticker overlays
        idx = 1
        for k, ov in enumerate(spec.get("overlays", [])):
            inputs += ["-loop", "1", "-i", str((base / ov["file"]).resolve()) if not Path(ov["file"]).is_absolute() else ov["file"]]
            s, e = parse_time(ov["start"]), parse_time(ov["end"])
            w = int(ov.get("width", 420))
            x, y = POSITIONS.get(ov.get("position", "upper_center"), POSITIONS["upper_center"])
            fc.append(f"[{idx}:v]scale={w}:-1,format=rgba,fade=in:st={s:.3f}:d=0.12:alpha=1[ov{k}]")
            fc.append(f"[{last}][ov{k}]overlay={x}:{y}:enable='between(t\\,{s:.3f}\\,{e:.3f})':shortest=1[vo{k}]")
            last = f"vo{k}"
            idx += 1
        # 5. subtitles + captions
        fc.append(f"[{last}]ass='{filter_escape(ass_path)}',format=yuv420p[vout]")

        # 6. audio: SFX + loudness
        sfx_labels = []
        for k, fx in enumerate(spec.get("sfx", [])):
            f = (base / fx["file"]).resolve() if not Path(fx["file"]).is_absolute() else Path(fx["file"])
            inputs += ["-i", str(f)]
            ms = int(parse_time(fx["at"]) * 1000)
            fc.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
                      f"volume={float(fx.get('gain_db', -8))}dB,adelay={ms}|{ms}[sfx{k}]")
            sfx_labels.append(f"[sfx{k}]")
            idx += 1
        duck = float(spec.get("dialogue_gain_db", 0))
        fc.append(f"[ac]volume={duck}dB[dlg]")
        if sfx_labels:
            fc.append(f"[dlg]{''.join(sfx_labels)}amix=inputs={1 + len(sfx_labels)}:duration=first:normalize=0[mix]")
            mix = "mix"
        else:
            mix = "dlg"
        fc.append(f"[{mix}]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
               "-filter_complex", ";".join(fc),
               "-map", "[vout]", "-map", "[aout]",
               "-t", f"{spec['_duration']:.3f}",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
               "-r", str(OUT_FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-movflags", "+faststart", str(out)]
        if args.verbose:
            print("filter_complex:\n  " + ";\n  ".join(fc))
        run(cmd, args.verbose)

    print(f"Rendered {out}  ({spec['_duration']:.2f}s, {OUT_W}x{OUT_H}, {'DRAFT' if draft else 'publishable'})")


if __name__ == "__main__":
    main()
