#!/usr/bin/env python3
"""Viral Clip Selection Engine: score, gate and rank candidate moments.

Input: a candidates JSON file (see templates/candidates.json).
Output: a ranked Markdown clipping report (stdout or --out).

Scoring (0-100):
  attention 20 | comedy 25 | relatability 15 | surprise 15 | meme 15 | shortform 10

Gates (a clip cannot be APPROVED regardless of score if any fails):
  - source.url and source.timestamp_in/out are filled in (never invented)
  - context_preserved is true (the joke stands without misleading cuts)
  - rights.status is an approved status
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import APPROVED_RIGHTS, DRAFT_ONLY_RIGHTS, USER_ASSUMED_RIGHTS, load_json

WEIGHTS = {"attention": 20, "comedy": 25, "relatability": 15, "surprise": 15, "meme": 15, "shortform": 10}
TIERS = [(85, "A - produce first"), (75, "B - produce"), (65, "C - backlog"), (0, "D - skip")]


def score(c: dict) -> tuple[int, list[str]]:
    problems, total = [], 0
    s = c.get("scores", {})
    for k, mx in WEIGHTS.items():
        v = s.get(k)
        if v is None:
            problems.append(f"missing score '{k}'")
            continue
        if not 0 <= v <= mx:
            problems.append(f"score '{k}'={v} outside 0-{mx}")
            v = max(0, min(mx, v))
        total += v
    return total, problems


def gates(c: dict) -> list[str]:
    fails = []
    src = c.get("source", {})
    for k in ("url", "timestamp_in", "timestamp_out"):
        if not str(src.get(k, "")).strip():
            fails.append(f"source.{k} not verified")
    if not c.get("context_preserved"):
        fails.append("context not confirmed preserved")
    st = c.get("rights", {}).get("status", "unknown")
    if st not in APPROVED_RIGHTS | USER_ASSUMED_RIGHTS:
        fails.append(f"rights '{st}'" + (" (draft only)" if st in DRAFT_ONLY_RIGHTS else ""))
    return fails


def tier(total: int) -> str:
    return next(name for floor, name in TIERS if total >= floor)


def md_cell(x) -> str:
    return str(x).replace("|", "\\|").replace("\n", " ")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidates")
    ap.add_argument("--out")
    args = ap.parse_args()
    data = load_json(args.candidates)
    rows = []
    for c in data["candidates"]:
        total, problems = score(c)
        g = gates(c)
        status = "APPROVED" if not g and not problems and total >= 75 else ("BLOCKED" if g else "HOLD")
        rows.append((total, c, problems, g, status))
    rows.sort(key=lambda r: r[0], reverse=True)

    L = [f"# Clipping report - {data.get('project', 'untitled')}", ""]
    L += ["| # | Score | Tier | Status | Comedian | Category | Punchline (short) | Duration | Rights |",
          "|---|---|---|---|---|---|---|---|---|"]
    for i, (total, c, _, _, status) in enumerate(rows, 1):
        L.append(f"| {i} | **{total}** | {tier(total)} | {status} | {md_cell(c.get('comedian', ''))} | "
                 f"{md_cell(c.get('category', ''))} | {md_cell(c.get('punchline', ''))[:60]} | "
                 f"{md_cell(c.get('recommended_duration', ''))} | {md_cell(c.get('rights', {}).get('status', 'unknown'))} |")
    L.append("")
    for i, (total, c, problems, g, status) in enumerate(rows, 1):
        src = c.get("source", {})
        s = c.get("scores", {})
        L += [f"## {i}. {c.get('id', '')} - {c.get('comedian', '')} ({total}/100, {status})", "",
              f"- **Source:** {src.get('title', '')} - {src.get('url') or '_URL not yet verified_'}",
              f"- **Original timestamp:** {src.get('timestamp_in') or '?'} -> {src.get('timestamp_out') or '?'}",
              f"- **Category:** {c.get('category', '')}",
              f"- **Context:** {c.get('context', '')}",
              f"- **Punchline:** {c.get('punchline', '')}",
              f"- **Why it's funny:** {c.get('why_funny', '')}",
              f"- **Meme integration:** {c.get('meme_idea', '')}",
              f"- **Recommended duration:** {c.get('recommended_duration', '')}",
              f"- **Rights:** {c.get('rights', {}).get('status', 'unknown')} - {c.get('rights', {}).get('notes', '')}",
              "- **Scores:** " + ", ".join(f"{k} {s.get(k, '?')}/{mx}" for k, mx in WEIGHTS.items())]
        if g:
            L.append("- **Gates failed:** " + "; ".join(g))
        if problems:
            L.append("- **Scoring issues:** " + "; ".join(problems))
        L.append("")
    text = "\n".join(L)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
