"""Shared helpers for the comedy-shorts pipeline (stdlib only)."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRAND_FILE = REPO / "brand" / "identity.json"

OUT_W, OUT_H, OUT_FPS = 1080, 1920, 30

# Rights statuses that allow a clip to be rendered for publication.
APPROVED_RIGHTS = {"owned", "licensed", "written_permission", "platform_licensed", "public_domain", "creative_commons_ok"}
# No licence on file: the channel owner has chosen to publish at their own copyright risk.
USER_ASSUMED_RIGHTS = {"user_assumed"}
# Statuses that allow internal drafts only (never publish).
DRAFT_ONLY_RIGHTS = {"pending", "fair_use_review"}


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die(f"{tool} not found on PATH")


def load_json(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_brand() -> dict:
    return load_json(BRAND_FILE)


_TS = re.compile(r"^(?:(\d+):)?(\d+):(\d+(?:[.,]\d+)?)$")


def parse_time(value) -> float:
    """Accept seconds (int/float/str) or [HH:]MM:SS(.mmm)."""
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    m = _TS.match(s)
    if m:
        h = int(m.group(1) or 0)
        return h * 3600 + int(m.group(2)) * 60 + float(m.group(3).replace(",", "."))
    return float(s)


def fmt_srt_time(t: float) -> str:
    t = max(0.0, t)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_ass_time(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def hex_to_ass(color: str, alpha: int = 0) -> str:
    """#RRGGBB -> &HAABBGGRR (ASS colour order)."""
    c = color.lstrip("#")
    r, g, b = c[0:2], c[2:4], c[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def parse_srt(path: str | Path) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8-sig")
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        idx = 0
        if "-->" not in lines[0]:
            idx = 1
        if idx >= len(lines) or "-->" not in lines[idx]:
            continue
        start, end = [x.strip().split(" ")[0] for x in lines[idx].split("-->")]
        cues.append({
            "start": parse_time(start),
            "end": parse_time(end),
            "text": "\n".join(lines[idx + 1:]),
        })
    return cues


def ffprobe(path: str | Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)


def filter_escape(path: str | Path) -> str:
    """Escape a file path for use inside an ffmpeg filtergraph argument."""
    s = str(path).replace("\\", "/")
    for ch in ("'", ":", ",", "[", "]", ";"):
        s = s.replace(ch, "\\" + ch)
    return s


def run(cmd: list[str], verbose: bool = False) -> None:
    if verbose:
        print("+ " + " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=not verbose, text=True)
    if proc.returncode != 0:
        if not verbose:
            print(proc.stderr[-4000:], file=sys.stderr)
        die(f"command failed ({proc.returncode}): {cmd[0]}")
