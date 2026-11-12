# Production Playbook

The standard operating procedure for every clip. The goal isn't just to chop
sets into small pieces. Each short should be a complete little comedy
experience: a strong hook, intact timing, channel commentary that adds to
the joke, and a look people recognise as ours.

---

## 0. Hard rules (these can't be overridden)

1. **Never invent** source URLs, timestamps, view counts, quotes or audience reactions. If something hasn't been verified, the field stays empty and the scorer blocks the clip.
2. **Rights are recorded on every clip.** `make_short.py` exports when `rights.status` is approved, or when it's `user_assumed` (the channel owner has chosen to publish without a licence and accepts the copyright risk; see `docs/DAILY.md`). Anything else renders only as a watermarked `--draft`.
3. **The comedian's words are sacred.** No reordering of lines that changes meaning, no re-captioning that puts words in their mouth, no cutting a setup so a punchline means something else.
4. **Commentary looks like commentary.** Editorial captions use the boxed yellow `Editorial` style, never the subtitle style, so viewers can't mistake our jokes for the comedian's.
5. **No implied endorsement.** Comedian names and faces don't go in channel branding, avatars, banners or "official"-sounding titles.

---

## 1. Workflow

```
input (comedian / URL / footage library)
  -> 1. discovery        candidates.json (only verified sources)
  -> 2. scoring          tools/score.py -> clipping report, ranked
  -> 3. rights           request licence/permission; record evidence in edit.json
  -> 4. concept          edit.json: segments, zooms, captions, stickers, SFX
  -> 5. transcript       subs.srt, transcribed word for word, source-timed
  -> 6. render           tools/make_short.py  (--draft while pending)
  -> 7. QC               tools/qc.py + manual checklist
  -> 8. package          tools/thumbnail.py, tools/deliverables.py
  -> 9. publish + track  fill section 14 of deliverables.md at 24h and 7d
```

Project layout:

```
projects/<comedian>_<slug>/
  candidates.json     discovery + scores
  source.mp4          authorised footage (git-ignored)
  subs.srt            transcript, source-timed
  edit.json           the edit spec (see projects/_demo/edit.json)
  deliverables.md     generated
  export/             renders + thumbnail (git-ignored)
```

---

## 2. Discovery

Where authorised footage comes from, in order of preference:

1. **Footage supplied with a licence**: from the comedian, their management, the producer or the distributor.
2. **Creator/clipping programmes**: some comedians and specials run official clipping or affiliate programmes with written terms. Save those terms as evidence.
3. **Official channels** (the comedian's own channel, the broadcaster's or the special's official channel). Being publicly *viewable* is **not** permission to reuse. Treat these as discovery sources, then request permission.
4. **Public domain / Creative Commons** recordings, after checking the licence actually allows commercial reuse and derivatives.

For each candidate, watch the full bit, not just the highlight. Write down:
- the exact `timestamp_in` / `timestamp_out` you watched,
- what the audience needs to know (the setup) for the punchline to land,
- the punchline as a word-for-word transcription,
- *why* it's funny (mechanism, see §3),
- whether a short cut keeps the meaning (`context_preserved`).

Don't pick a moment just because the room laughed. Laughter can come from earlier context, a callback or a visual we won't show.

---

## 3. Scoring (tools/score.py)

| criterion | max | ask yourself |
|---|---|---|
| Immediate attention | 20 | Does the first 1.5s give a reason to stay (face, conflict, odd claim)? |
| Comedy & punchline | 25 | Is the payoff strong *on its own*, without the rest of the set? |
| Relatability | 15 | Will viewers tag someone? (family, couples, work, school, migration) |
| Surprise | 15 | Is there real misdirection or escalation, or is it predictable? |
| Meme potential | 15 | Is there a natural spot for a freeze, sticker or caption that *adds* something? |
| Short-form fit | 10 | Does the bit fit in 15–60s without butchering the build-up? |

Tiers: **85+** produce first · **75–84** produce · **65–74** backlog · **<65** skip.
Status: `APPROVED` only when score ≥ 75 **and** every gate passes; `BLOCKED` when a gate fails (unverified source, context, rights); `HOLD` otherwise.

Comedy mechanisms to name in `why_funny`: misdirection, escalation, rule of three, act-out/character work, status reversal, callback, understatement, specificity, the cultural "we all know this" moment, and crowd-work reversal.

---

## 4. Editing standards

**Format:** 1080×1920, 30 fps, H.264 high/yuv420p, AAC 48 kHz 192 kbps, −14 LUFS, true peak ≤ −1 dBFS.

**Duration:**
- 15–20s: one strong joke
- 20–35s: setup + punchline
- 35–60s: full sequence (setup, escalation, tag)

**Cutting:**
- Cut dead air *between* thoughts, never *inside* a pause the comedian uses for timing. The beat before a punchline is part of the joke.
- Keep the laugh after the punchline for 0.5–1.0s, or hold a freeze-frame (`"freeze": 0.6`) on the reaction.
- Jump cuts should land on breaths or gestures so they feel natural.
- Open on the most intriguing line of the *setup*, not the punchline. Spoiling the payoff kills retention.

**Framing (`framing.mode`):**
- `blur_fill` (default): the whole 16:9 frame over a blurred fill, raised 120px so the subtitles sit below the face.
- `crop`: a tight 9:16 crop. Set `crop_x` (0–1) to follow the comedian. Use it when they don't move around much.
- `fit`: letterbox, as a last resort.

**Zooms:** one punch-in (×1.10–1.20) on the key expression or punchline, one more on the tag at most. Too many zooms tire the eye.

**Safe zones (1080×1920):** keep text out of the top 220px, bottom 480px and right 140px (platform UI). The defaults in `brand/identity.json` already respect this.

---

## 5. Memes and editorial commentary

Commentary sits *on top of* the joke. It never replaces it.

| technique | when | spec field |
|---|---|---|
| Editorial caption (boxed) | Hook in the first 3s; reaction after the punchline | `editorial_captions` |
| Reaction sticker | On the reaction beat, never on the punchline line itself | `overlays` |
| Freeze-frame | Hold the face after the punchline | `segments[].freeze` |
| Punch-in zoom | Key expression | `zooms` |
| SFX | See §6 | `sfx` |

Caption rules:
- Write it for *this* joke. Generic captions read as filler.
- Never put a caption in quotation marks or in subtitle style. Captions are our voice.
- Hook captions frame the situation ("POV: …", "When you…"). Reaction captions comment on the outcome.
- One caption on screen at a time, 2.5–3.5s each.

Caption starters live in `templates/caption_bank.md`. Sticker library: `assets/stickers/manifest.json` (original, organised by emotion; extend it in `tools/generate_stickers.py`).

Third-party meme images, GIFs and audio are **not** free to use just because they're popular. Use our original library, licensed stock, or properly licensed packs, and record the licence.

---

## 6. Sound design

Library: `assets/sfx/` (synthesised in house by `tools/generate_sfx.py`, so the channel owns all of it).

| moment | sound | typical gain |
|---|---|---|
| Building to the punchline | `riser`, `tension_tick` | −16 to −20 dB |
| Punchline / reveal | `impact` (+ `dramatic_sting` for big realisations) | −8 / −14 dB |
| "Wait, what?" stop | `record_scratch` | −10 dB |
| Silly beat | `boing` | −10 dB |
| Awkward silence | `crickets` | −12 dB |
| Sticker/caption pop | `pop` | −12 dB |
| Transitions | `whoosh` | −12 dB |

Rules: never put an SFX *over* the punchline word (place it right after). No more than 3–5 SFX per 30s. Audience laughter only ever comes from the authorised source, never added.

---

## 7. Subtitles

- Transcribe word for word from the audio into `subs.srt`, timed against the **source**. The renderer remaps the timing through every cut and freeze.
- Keep cues to 1–2 short lines (≤ 32 characters a line); break at natural pauses.
- `highlight_words`: 1–2 key words per cue (the twist word, the number, the name).
- Punctuation carries timing: "…" for a held pause, "?!" for disbelief.
- Uppercase is the default for Latin scripts; Arabic script stays in natural case with the Arabic font (`language: "ar"`).
- If a transcription service drafts the SRT, a person still checks every line against the audio.

---

## 8. Multilingual editions

See `docs/MULTILINGUAL.md`. In short: translate the *joke*, not the words. Mark adapted lines as translations, keep a 1:1 cue timing, and render one export per language (`subs.<lang>.srt`, `"language"` field).

---

## 9. Deliverables (per approved clip)

Generated by `tools/deliverables.py`: source reference · rights status · timestamps · editing timeline · final video · subtitles · overlays · SFX · thumbnail · 3 hooks · TikTok caption · YouTube Shorts title and description · hashtags · performance table (fill it in at 24h and 7d).

Hashtags: 3–5 per post. Mix broad (#comedy #standup), niche (#humourmarocain #darija #standupfr) and topic (#momlife). Don't use a comedian's name as a hashtag unless the clip is licensed and the credit is accurate.

Credit line in every description: `Comedian: <name> · Source: <special/show> · Used with permission / under licence`.

---

## 10. Performance review

After 7 days, compare clips on average watch %, the 3s hold rate and shares per 1k views. Feed the results back:
- a high hold rate with a low finish rate means the setup is too long, so tighten the middle;
- a low hold rate means the hook is weak, so test another of the three hooks on the next upload;
- a high share rate tells you which category or theme to look for more of in discovery.
