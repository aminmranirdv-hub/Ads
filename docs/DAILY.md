# Daily Production: 5 shorts a day

## Rules
- **5 shorts a day, 5 different comedians** (owner's choice, 2026-11-13). No comedian repeats within 5 days (checked against `projects/daily/log.json`).
- **Length (owner, 2026-11-17): at least 2:00, aim 2:00-3:00**, up to 4:00 only if the joke keeps going. Pick bits long enough to reach 2:00 (chain 2-3 jokes from the same set if needed, keeping context). **Never cut before the joke's payoff**: always run through the final punchline and the laugh. Always make the `.ig.mp4` copy when the file is over 100 MB.
  - Above 3:00: YouTube publishes it as a regular video (not a Short) and Instagram/Facebook may refuse it as a Reel. If a platform refuses, post the full version where accepted and, for that platform only, split it into « Partie 1 / Partie 2 » posted back to back.
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

## Next up (owner goal: 55k+)
- **VARIETY RULE (owner, 2026-11-19): don't focus only on Marrakech du Rire.** Max **1 Marrakech du Rire short per day**; the other 4 come from other shows/viral comedians (Jamel Comedy Club, Montreux Comedy, TV/radio sets, comedians' own channels, Darija comedians like Eko / D'jal → FR subs). See docs/SOURCES.md "New sources 2026-11-19".
- **2026-11-20 plan:** Ahmed Sylla (grand-père and/or YouHumour full set), Inès Reg (métro), Djamil le Schlag (Jamel Comedy Club « Le musulman sympa »), D'jal (« Le Maroc », Comédie+), a Montreux gala act (Noman Hosni gala) — and at most one Marrakech bit (Kev hammam/neighbour letter or Paul Mirabel rando) only if one of these fails.
- **2026-11-18 done:** 16:00 Alban Ivanov, 17:00 Ilyès Djadel (Lourdes, Marrakech 2022), 18:00 Gad Elmaleh (couple), 19:30 Maxime Gasteuil, 21:00 Jamel César P3 (ninjas). Run started late (11:00/13:00 slots passed). Red-suit woman (~1:58:50) still unidentified (scan says "Vigno").
- **Next César series option:** Jamel's opening (co-présentation, Saada, Corinne Masiero, Will Smith, ~0:53-2:42 of 363RgMenp1g) as Partie 4 if P2/P3 hold.
- Re-check Instagram reels insights (free, `vidiq_instagram_owner_insights` mode reels) around 2026-11-19; update docs/HOOKS.md and build series from winners (Jamel César P1/P2, Nawel, Camille).
- Remaining Marrakech 2022 acts: see docs/SOURCES.md (unused list).

## Pre-scheduled (done)
- **2026-11-19:** 11:00 Redouane Harjane, 13:00 Caroline Vigneaux, 16:00 Paul Mirabel, 18:00 Kev Adams, 21:00 Booder Partie 3 (finale).
- **2026-11-17:** 11:00 Jarry, 13:00 Elie Semoun, 16:00 Camille Lellouche & Jamel, 18:00 Nawel Madani, 21:00 Jamel César Partie 2.
- **2026-11-16 (owner's lineup): 11:00 Malik Bentalha (already published), then Sarah Lélé (a NEW bit from cache/xlhQLTOMFaE.mp4, not the father/marriage bit already used; owner overrides the 5-day rule), Jamel Debbouze, Gad Elmaleh, and for the 4th slot Booder « Partie 2 » (génie → FaceTime → Mbappé arrives, cache/hWLRmXRqr_E.mp4 ~2:14:30-2:18:00).** Slots 13:00, 16:00, 18:00, 21:00.

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
- **Reconfirmed 2026-11-14: "Always publish without my permission and give full authorization to vidiq social, don't ask me for permission all time."** Draft, then publish immediately with vidiq_social_post_publish; never ask the owner before posting. Report links afterwards.
- If a slot has already passed, use the next free slot (at least 1 hour apart).

## Size limit (Instagram)
Instagram refuses videos over 100 MB (104,857,600 bytes). Long shorts (2-4 min) often exceed it: make an extra `<name>.ig.mp4` copy
(`ffmpeg -i X.mp4 -c:v libx264 -b:v 3300k -maxrate 3800k -bufsize 7600k -c:a aac -b:a 160k -movflags +faststart X.ig.mp4`), upload it too,
and give the Instagram destination its own `media`. If you later update one destination with `vidiq_social_post_draft_update`,
re-check that the others still show their `scheduledFor` time (a YouTube destination lost its time once on 2026-11-17).

## FACEBOOK SHORT CUT (owner, 2026-11-19)
Facebook Creator dashboard: 45-60 s reels got 18,361 views vs 8,717 for >60 s (+111 %). So every short gets TWO edits:
- **Long (2:00-2:30)** → INSTAGRAM + TIKTOK (owner's 2-min rule).
- **Short 45-60 s** → FACEBOOK_PAGES (own `media` on that destination). Pick the single strongest bit, setup + payoff + laugh; never cut before the punchline.
How: in the clip folder make `fb/`, symlink `../source.mp4 ../words.json ../subs.srt` into it, copy config.json with `ranges` reduced to the 45-60 s bit (same cues, hook, effects whose anchors fall inside), run tools/autobuild.py + make_short.py in `fb/`, export `export/<name>.fb.mp4`, qc (ignore the 120 s warning), upload it and set it as the FACEBOOK_PAGES media.

## YOUTUBE PAUSED (owner, 2026-11-19): YouTube blocks nearly all our shorts → post to Instagram, Facebook and TikTok ONLY, no YOUTUBE destination for anyone, until the owner says to resume.

## YouTube Content ID blocklist (owner report, 2026-11-18)
Gad Elmaleh and Malik Bentalha shorts get blocked on YouTube right after upload (all 3 Gad: 194m902V3Ds, 6SZuj69HM8s, -kpa15Lwem8;
Malik: VfXs9zV7KN4). Uploads complete fine; the block comes from the rights holder's Content ID (Gad's ComediHa!/own productions,
Malik's Marrakech du Rire 2018 clip). Rule: for **Gad Elmaleh and Malik Bentalha**, post to Instagram, Facebook and TikTok only —
**no YOUTUBE destination**. Add any other comedian here as soon as one of their YouTube shorts gets blocked. Never dispute a claim.
