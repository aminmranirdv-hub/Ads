# Comedy Shorts Studio

A repeatable pipeline for turning **authorised** stand-up footage into
mobile-first, meme-enhanced 9:16 shorts for TikTok, YouTube Shorts and
Instagram Reels. It covers discovery, scoring, rights gating, editing,
subtitles, sound design, QC and the publishing package.

Channel identity: **PUNCHLINE LAB** (`brand/identity.json`): white/yellow
subtitles, a boxed yellow style for channel commentary, and a pink accent.

## Quick start

```bash
# requirements: ffmpeg (with libass), Python 3.10+, Pillow
python3 tools/generate_sfx.py          # original SFX library  -> assets/sfx/
python3 tools/generate_stickers.py     # original sticker library -> assets/stickers/

# end-to-end demo on synthetic footage
bash projects/_demo/make_source.sh
cd tools
python3 score.py        ../projects/_demo/candidates.json
python3 make_short.py   ../projects/_demo/edit.json
python3 qc.py           ../projects/_demo/edit.json ../projects/_demo/export/demo_mama_6am.mp4
python3 thumbnail.py    ../projects/_demo/source.mp4 --at 16.2 --text "She called at 6 A.M. for THIS" \
                        --out ../projects/_demo/export/demo_mama_6am.thumb.jpg
python3 deliverables.py ../projects/_demo/edit.json
```

## Tools

| tool | what it does |
|---|---|
| `tools/score.py` | Scores candidates on the 100-point rubric, applies the gates (verified source, context, rights), ranks them and writes the clipping report |
| `tools/make_short.py` | Renders a 1080×1920 short from `edit.json`: jump cuts, freeze-frames, blur-fill/crop framing, punch-in zooms, stickers, animated subtitles remapped through the cuts, editorial captions, SFX mix, −14 LUFS. **Refuses to export without approved rights** (`--draft` gives a watermarked preview) |
| `tools/qc.py` | Automated spec/loudness/rights checks plus the manual QC checklist |
| `tools/thumbnail.py` | 9:16 cover from a clean source frame with the hook text |
| `tools/deliverables.py` | Deliverables sheet: source, rights, timeline, hooks, captions, titles, hashtags, performance table |
| `tools/generate_sfx.py` | Synthesises 9 original SFX (impact, boing, riser, record scratch, sting, whoosh, pop, crickets, tick) |
| `tools/generate_stickers.py` | Generates original reaction stickers in 12 emotion categories (EN/FR/Darija) |

## Docs

- `docs/PLAYBOOK.md`: the full SOP (workflow, scoring, editing, memes, audio, subtitles, deliverables, review)
- `docs/RIGHTS.md`: rights statuses, evidence, permission request template
- `docs/MULTILINGUAL.md`: FR / EN / Darija / Arabic adaptation rules
- `docs/COMEDIAN_REFERENCE.md`: technique study of the reference comedians (analysis, not imitation)
- `templates/`: candidates template and caption bank

## Starting a real clip

1. `mkdir projects/<comedian>_<slug>` and copy `templates/candidates.json` into it.
2. Fill in candidates **only from footage you watched**; run `score.py`.
3. Secure the rights; record the evidence in `edit.json` → `rights`.
4. Put the authorised footage in as `source.mp4` (git-ignored), transcribe `subs.srt`, write `edit.json` (copy the demo).
5. Render → QC → thumbnail → deliverables → publish → fill in the performance table.
