# Gad Elmaleh – Discovery Round 1

**Status:** 13 candidates found and scored → `clipping_report.md`. **0 can be produced yet**: every one is blocked on rights (`unknown`). Nothing has been downloaded or edited.

## How this was researched

- Searched YouTube and kept only uploads by the **rights holders' own channels** (festival or broadcaster).
- Pulled each video's transcript. Quotes and timestamps come from those transcripts, nothing invented. Timestamps are **caption-block starts**, so trim ±3s on the real footage.
- **Limitation:** I read the transcripts but didn't watch the videos. Laughter is only known where the captions mark `[Applaudissements]`, and facial expressions are unverified. The ComediHa! auto-captions are badly garbled, so those three candidates need re-transcribing from the audio. Scores are a first pass to re-check while watching.

## Authorised sources used

| Video | Channel | Length | Language | Candidates |
|---|---|---|---|---|
| [Les petits mensonges du quotidien](https://www.youtube.com/watch?v=kal9aFfyWOs) (MCF 2023) | Montreux Comedy | 8:39 | FR, human captions | 6 |
| [Gad Elmaleh Performs Stand-up](https://www.youtube.com/watch?v=jLOKSJq4tRA) (2016) | The Late Show with Stephen Colbert (CBS) | 5:43 | EN | 3 |
| [Gala ComediHa!](https://www.youtube.com/watch?v=Dyy-KRkdE2c) (Québec 2018) | ComediHa! | 9:22 | FR, auto captions | 3 |
| [Conseils d'ami, with Paul Mirabel](https://www.youtube.com/watch?v=OR-1TUobxk8) (MCF 2021) | La Relève Montreux Comedy | 7:28 | FR | 1 |

**For round 2:** the official *Marrakech du rire* channel has several Gad shorts with 1.4–1.7M views each (taxi in Morocco, "certificat de vie", passport, "fais attention", pony rides, his mother at his US show). They're already clipped, so ask the festival for the **full gala footage** instead. It's a great fit for the Darija/Arabic editions.

## Excluded

- **Fan re-uploads** of specials (e.g. the "IKEA", "La jalousie" and "Les maths" excerpts, and full uploads of *L'autre c'est moi*) by unaffiliated accounts. These aren't authorised sources, however many views they have.
- **"Team Gad Elmaleh"**: a fan news channel, not official.
- **Gad's official channel (@gadelmaleh / GadElmalehVEVO)**: music videos only, no stand-up.
- **Interviews and talk segments** (Fallon, Konbini, LEGEND, Drucker): not stand-up, and many are emotional rather than comic.
- **Context note:** in 2019 the CopyComic channel published videos comparing some of Gad's older bits to other comedians' material. Before picking any **older** bit, check it isn't one of those. All 13 candidates here come from 2016–2023 sets.

## Top 5 and the editing concepts

### 1. "Merci, la vie" – 89 · Montreux 3:37–4:28 · 35–45s
- **Hook (first 2s):** start on « Je scrolle sur Insta comme un c*n », the most intriguing line, without giving away the punchline.
- **Edit:** cut the 50-year-old preamble down to one line; keep the jet / Vuitton / « Merci, la vie » build in full. Punch in ×1.15 on « Jean-Jacques Lavie », hold a 0.6s freeze on the reaction, keep « 78 ans » and the plane tag.
- **Overlays:** an original mock Instagram card (« Merci, la vie. ✈️ ») during the setup; `impact` −8 dB just *after* « Lavie »; `dramatic_realization/il_a_compris` sticker on the tag.
- **Editorial captions:** « POV : tu lis les légendes Insta à 50 ans » → « Merci qui ? »
- **Hooks:** ① « Les légendes Instagram ne seront plus jamais pareilles » ② « Il a enfin trouvé qui est "la vie" » ③ « Attends de voir qui a payé le jet… »
- **Editions:** FR original · EN ("Thank you, life." → explain in the description that *Lavie* is a surname; translated subtitles keep « Jean-Jacques Lavie ») · Darija: adaptation note required, since the pun doesn't survive translation.

### 2. "Would be dope" – 89 · Late Show 4:23–5:26 · 35–45s · English
- **Hook:** « I've been texting some American girls… »
- **Edit:** this one barely needs cuts. Original chat bubbles for « I'm down / I'm in / would be dope » (his quoted words); punch in on « she's too young »; 0.8s freeze; `red_flag` sticker; `record_scratch` on « because you're depressed ».
- **Captions:** "POV: learning American slang at 45" → "The friend had to explain it…"
- **Editions:** EN original · FR subtitles · Darija (Latin) subtitles. This is the strongest cross-language candidate.

### 3. "Naaaan !" – 87 · Montreux 0:52–2:00 · 45–55s
- Animated phone screen reproducing the two texts he describes; « WAIT… WHAT?! » sticker on « Oh, mais vous n'êtes pas… ? »; caption « Elle savait. ELLE SAVAIT. »

### 4. "J'avoue / Askip" – 87 · Montreux 4:28–5:00 · 25–30s
- Slang "dictionary card" overlay (original); `boing` on « lessive ». The short length suits a Shorts/Reels loop.

### 5. "Arrondir à la pompe" – 86 · ComediHa! 0:47–1:53 · 40–50s
- Synced digital pump-counter overlay; `tension_tick` under the taps, `impact` on the overshoot. Re-transcribe from the audio first.

Quick win: **"Ah ! Moi oui"** (84, 15–20s) is the best pure one-liner for testing hooks.

## Rights: what to do next

All four sources belong to organisations that license festival footage. For each one, send the request template in `docs/RIGHTS.md`:

| Footage | Ask |
|---|---|
| Montreux Comedy Festival 2021 / 2023 | Montreux Comedy, via their official site / business contact |
| Gala ComediHa! 2018 | ComediHa! (Québec), via their official contact |
| The Late Show 2016 segment | CBS / Paramount licensing |
| Marrakech du rire galas (round 2) | The festival's production company, via the official channel's contact |

Copy Gad Elmaleh's management if possible (the performer's consent matters for the channel's reputation, even when the producer owns the footage). For the Mirabel duo, both performers are involved.

When a licence arrives: set `rights.status` to `licensed`, record the evidence, put the footage in `projects/gad_elmaleh/<clip>/source.mp4`, write `subs.srt` from the audio, copy `projects/_demo/edit.json` and fill in the concept above. Then render → QC → package.

Until then, if you want internal previews, set the clip to `pending` once a request has been sent and render with `--draft`, using footage you're allowed to hold.
