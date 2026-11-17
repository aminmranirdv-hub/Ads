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
- Keep the full payoff (up to 4:00) — never cut before the punchline.

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
