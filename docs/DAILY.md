# Daily Production: 3 shorts a day

## Rules
- **3 shorts a day, 3 different comedians.** No comedian repeats within 5 days (checked against `projects/daily/log.json`).
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
