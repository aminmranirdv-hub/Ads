# Hook playbook (data-driven, updated 2026-11-16)

## What the numbers say (Instagram Reels, owner insights, 20 Reels, 69 followers)
| Reel | Views | Skip rate | Avg watched | Shares |
|---|---|---|---|---|
| **Jamel, César 2023 (Netflix / nounou), 2:12** | **54 994** | **16 %** | **54 %** | **247** |
| Booder Partie 2 (Mbappé arrives), 1:52 | 299 | 24 % | 49 % | 0 |
| P.E. prénom, 1:23 | 173 | 26 % | 24 % | 0 |
| Typical short (most others) | 150-270 | 34-39 % | 20-40 % | 0 |
| Guillermo Guizz, 1:36 | 205 | **51 %** | 17 % | 0 |
| Pierre Croce, 0:52 | 149 | 48 % | 22 % | 0 |
| Blanche Gardin, 2:00 | 183 | 46 % | 15 % | 0 |
TikTok: Jamel « ninjas » (César 2023) ~13k views in a day. Skip rate = % who swipe away in the first ~3 s: it is THE hook metric.

## Why the Jamel reel won (and the worst ones lost)
1. **Star face, big, in frame 1.** Jamel in medium close-up at 0:01. The worst (Guizz) opened on a wide shot where the comedian is a dot.
2. **First spoken line = stakes, not setup.** "Madame la ministre, le cinéma souffre." / "Un seul vœu ?" vs "C'est vraiment une caricature de…" / "Bon, il y a une étude qui a été réalisée…". Never open mid-sentence or on throat-clearing.
3. **Hook text promises a payoff with a twist + names the star.** "Jamel a trouvé LE coupable : la nounou 😂" / "Partie 2 : le vœu de Jamel… se réalise VRAIMENT 😱". Weak: generic questions ("Toi aussi tu prends ton téléphone aux toilettes ?", "Se battre pour son pays ?").
4. **Universal, shareable topic.** Netflix price, cinema, babysitter: everyone has an opinion → 247 shares. Shares push reach far more than likes.
5. **A famous moment** (César, Marrakech du Rire with Mbappé) beats an unknown gala set.
6. **Length is not the problem.** 2:12 kept 54 % watched. What kills is a weak first 3 seconds.

## Rules for every short (apply before rendering)
- **Pick bits that START strong**: choose the in-point on a line with stakes, a question, a provocation or a direct address. If the bit's natural start is setup, start later (first strong line) as long as the joke stays understandable.
- **Frame 1 = face.** If the source is a wide shot, set `"open_zoom": 1.3` in config.json (punch-in during the hook) and/or a tighter `pre_crop`. For a very wide shot, aim the punch-in at the comedian with `"open_zoom_cx"`/`"open_zoom_cy"` (0-1 of the output frame, e.g. 2.6× at cx 0.36 for Nawel) and end it before the next camera cut (`open_zoom_dur`). If the first segment opens on an audience shot, move its `in` to just before the first word.
- **Music/visual gags:** mark the range `[a, b, "raw"]` so pauses aren't tightened away (e.g. the raï-from-the-belly gag in Camille Lellouche's sketch).
- **Hook text formula** (max ~45 characters, 2 lines): `[Star name] + [promise/twist] + emoji`. Patterns that work:
  - "X a trouvé LE coupable : …"
  - "Le vœu de X… se réalise VRAIMENT"
  - "X explique pourquoi … (et c'est validé)"
  - "Attends la réponse de …" / "Personne n'était prêt pour la fin"
  - Name the famous guest if any (Mbappé, Jamel…).
  Avoid: vague "Toi aussi… ?" questions, topic labels, anything that spoils the punchline.
- **Prefer stars and famous moments**: Jamel, Gad, Booder, Malik Bentalha, Ilyès Djadel, Marrakech du Rire, César, big TV galas. Use lesser-known acts only with an exceptional first line.
- **Shareable topics first**: money, prices, family/parents, couples, everyday obsessions, France vs others.
- **Caption first line = the quote that makes people tag a friend**, then "Tague …" CTA (shares matter most).
- Length: 2:00 minimum, 2:00-3:00 target, up to 4:00 if the joke continues (owner, 2026-11-17) — never cut before the punchline. A strong hook in the first 3 s matters even more on long shorts.

## Re-check weekly
Pull `vidiq_instagram_owner_insights` mode reels (free) every few days, add rows above, and adjust. Look at skip rate first, then shares.

## Meta (Instagram/Facebook) distribution rules (owner goal 2026-11-16: every video toward 55k+)
No paid boost (no budget) and no way to "connect" to the algorithm directly: reach comes from the signals Meta's Reels ranking uses publicly: watch time, completion, **shares (sends)**, saves, comments, and the first-3-second hold. So:
1. **Series from winners.** When a reel outperforms (skip < 25 % or > 5k views), make « Partie 2 / 3 » from the SAME source within 1-3 days (e.g. more Jamel César 2023 bits), same hook style, caption "Partie 2 de [winner]". Allowed even if the comedian was used in the last 3 days.
2. **Hashtags: 3-5, specific** (comedian, show, topic), not 12 generic ones. Put keywords in the caption text for Instagram search: comedian full name + topic + "humour" + "stand-up".
3. **Caption line 1 = the share line** (the quote), line 2 = context, then a **question that invites comments** with two camps ("Team nounou ou team Netflix ? 👇") and a "Tague ton pote qui…" CTA. Shares + comments in the first hour decide distribution.
4. **First frame = face + hook text**, no black/wide/logo frame; the cover Meta picks is frame 1.
5. **Sound on, no silence**: start on speech, never on applause or walking.
6. **Post time**: strongest short at 18:00 or 21:00 Paris (peak evening scroll); keep 5 a day spread.
7. **Originality**: our own edit (zooms, captions, subtitles, translation) counts as transformation; never post the raw clip.
8. Re-check insights every 3 days and double down on what holds (skip rate, shares).

## Insights 2026-11-19 (vidiq_instagram_owner_insights, reels, free)
Followers **254** (69 on 2026-11-16). 30-day account views: 163k (mostly the Jamel nounou reel).
| Reel | Len | Views | Skip | Avg watched | Shares |
|---|---|---|---|---|---|
| Booder P2 (Mbappé génie) | 1:52 | 585 | 25.6% | 50% | 4 |
| Gad pompe à essence | 1:07 | 398 | 36% | 42% | 1 |
| Jarry Martine | 0:56 | 291 | 37.5% | 33% | 0 |
| Elie Semoun mensonges | 1:10 | 256 | 28.8% | 40% | 0 |
| Alban foot (18th, <1 day) | 2:00 | 161 | 45.6% | 21% | 1 |
| Gad couple (18th, <1 day) | 2:11 | 150 | 41% | 31% | 2 |
| Camille Lellouche enceinte | 3:18 | 94 | **20%** | 41% (81 s) | 1 |
| Nawel Rihanna | 3:23 | 57 | 37.8% | 30% | 0 |
| Jamel César P2 | 1:16 | 53 | 38.9% | 52% | 0 |
| Ilyès Lourdes (18th) | 3:01 | 17 | 27% | 35% | 0 |
| Jamel César P3 (18th) | 2:22 | 14 | 36% | 27% | 0 |
Read: the César series is fading (P2 53, P3 14) → pause it. Booder génie is the best follower of the Jamel winner → Booder Partie 3 (finale, 2026-11-19). Long 3-min reels hold viewers in absolute seconds (Camille 81 s) but % watched drops; keep 2:00-2:30 when possible and put the strongest laugh in the first 20 s.


Note 2026-11-19: owner overrides the 3-5 hashtag rule — add the fixed set from docs/DAILY.md (FIXED HASHTAGS) after the specific ones.

## Insights 2026-11-21 (IG, owner insights)
- 11-19 long reels (2:04-2:45): 144-170 views. 11-20 long reels (2:26-3:12): **6-13 views**. Avg watch time 26-56 s regardless of length → watched % 6-31 %.
- All +254 followers came 11-16/17 from the Jamel César reel. Nothing since.
- Shares: Caroline Vigneaux 4 (22 % skip, best), Gad couple 2, D'jal ambassade 1.
- Decision → docs/GROWTH.md: 35-75 s edits everywhere, 4/day, series for follows.

## IG daily check (account flagged 2026-11-21, flagged reels deleted 2026-11-21)
| Date | Followers | Non-follower reach 14 d | Recent reels views | Verdict |
|---|---|---|---|---|
| 2026-11-22 | 256 | 117,958 (flat) | Alban javelot 18, Djamil 19, older ones +1-5 | still restricted; wait |
| 2026-11-23 | 257 followers · reach 14 d: 118k non-followers / 136 followers (mostly pre-flag) · no new reels · still restricted |
