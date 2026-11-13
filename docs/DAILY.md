# Daily Production: 5 shorts a day

## Rules
- **5 shorts a day, 5 different comedians** (owner's choice, 2026-11-13). No comedian repeats within 5 days (checked against `projects/daily/log.json`).
- **Length:** 15s to **3:00** max. Use the long format only when the story needs it.
- **Subtitles are always bilingual:** original on top (white), translation underneath (yellow), plus the corner label "translation".

| performance language | translation shown |
|---|---|
| English (American / international) | French |
| French | English |
| Moroccan Darija | French |

- **Rights mode:** `user_assumed`. The channel owner decided to publish without licences and accepts the copyright risk (Content ID claims, strikes, takedowns). Always credit the comedian and link the original upload in the description.
- **Sources:** prefer the comedian's or the broadcaster's official upload (best quality, accurate credit).

## Pipeline per short
```
projects/daily/<date>/<nn>_<comedian>_<bit>/
  edit.json    segments, framing, captions, stickers, SFX, publishing (prepared in advance)
  script.md    bilingual draft from the official transcript
  source.mp4   the footage (dropped in by the channel owner)
```
1. `python3 tools/transcribe.py source.mp4 --lang <fr|en|ar> --start <first in> --end <last out>` writes `subs.srt` with word-level timing
2. Translate each cue into `subs.<fr|en>.srt` with the same timings (start from script.md)
3. Fill in the `__placeholder__` times in edit.json (zoom, sticker and SFX on the punchline words)
4. `python3 tools/make_short.py edit.json`, then `tools/qc.py`, `tools/thumbnail.py`, `tools/deliverables.py`

## Priority comedians (owner request, 2026-11-13)
- **Ilyès Djadel** (FR → EN; owner asked for 2026-11-14), **Sarah Lélé** (Belgian, FR → EN), **Booder** (FR → EN), and other acts from **Marrakech du Rire** (FR → EN; Darija → FR). Use them before the rotation below.

## Rotation (first 5 days)
| day | FR → EN | EN → FR | Darija → FR |
|---|---|---|---|
| 1 (2026-11-12) | Gad Elmaleh | Gabriel Iglesias | Rachid El Baz & Tarek Badir (StandUp Al Aoula) |
| 2 | Jamel Debbouze | Kevin Hart | another StandUp Al Aoula finalist |
| 3 | Redouane Bougheraba | Trevor Noah | Moroccan act from Marrakech du rire |
| 4 | Amine Radi | Dave Chappelle | (Darija) |
| 5 | Jamel Djadel (language to confirm) | Russell Peters / Chris Rock | (Darija) |

Then: Eddie Murphy, Bernie Mac, Katt Williams, Jim Carrey, and back to the top of the list.
If no usable Darija clip is found on a given day, fill the slot with another FR or EN comedian rather than ship a weak short.

## Publishing preference (set by the channel owner)
- **Always spread ("étale")**: the 5 daily shorts go out at **11:00, 13:00, 16:00, 18:00 and 21:00 Paris time** on Instagram @the_punchlinelab, the Facebook Page Thepunchlinelab and TikTok The_punchlinelab (public, comments on, Music Usage Confirmation accepted 2026-11-12).
- **Standing approval (owner, 2026-11-13): "NEXT time post without my ok".** Each daily run drafts and publishes all 5 shorts itself, then reports the links. Do not wait for an "ok".
- If a slot has already passed, use the next free slot (at least 1 hour apart).
