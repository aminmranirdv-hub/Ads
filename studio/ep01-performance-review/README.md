# Ep.1 — "The Performance Review" (Barnaby Purrkins)

**Final video:** `output/barnaby-ep01-performance-review.mp4`. Vertical 1080x1920, 30 fps, 34 s, H.264 + AAC.

The whole episode was made in code with no paid AI credits. The animation is drawn on an HTML canvas and rendered frame by frame with Playwright. The voice is espeak-ng with the MBROLA British voice, processed through sox. The music and sound effects are synthesized in NumPy, so all audio is original.

Rebuild it:
```bash
W=/tmp/ep01
python3 build/build_audio.py $W      # voice, SFX, music, timeline.json
node build/render.js $W              # frames
ffmpeg -framerate 30 -i $W/frames/f%05d.jpg -i $W/mix.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest out.mp4
```
Requirements: `apt-get install espeak-ng mbrola mbrola-en1 sox ffmpeg`, plus `numpy` and `playwright`.

## Concept
Barnaby gives the Landlord (his owner) a brutal annual performance review. He keeps his dignity right up until the "Ear Scratches" section, when he melts.

## Scene-by-scene script

| # | Time | Shot / camera | Action and expression | Dialogue / SFX |
|---|---|---|---|---|
| 1 HOOK | 0–2.7s | Close-up (1.75→1.95x slow push) | Judgmental half-lidded glare, unibrow in a V. Paw slides the review paper toward the camera. Red banner: "ANNUAL PERFORMANCE REVIEW" | SFX: paper slide, lamp click. **"Sit down. This won't take long."** |
| 2 | 2.7–7.7s | Wide (office, chart, Landlord's nervous tapping hands at the bottom) | Points at the "Treat Delivery Speed" chart. The last bar collapses; brow slams down; micro-shake | **"Treat delivery. Average response time: four seconds. Unacceptable."** |
| 3 | 7.7–13.5s | Medium on the pie chart → paper insert → face close-up | Air quotes with wiggling toes. Smash cut to a red NEEDS IMPROVEMENT stamp. Back to his face for a slow blink | **"Lap availability: forty percent. You were, quote, at work."** STAMP THUNK. **"Noted."** |
| 4 | 13.5–18.9s | Three timpani hits, each a snap zoom (1.6→2.0→2.7x), red tint, window flash | Wide trembling eyes, ears back, gasping mouth. "CLASSIFIED" bar | DUN · DUN · DUNNN + brass. **"The vacuum incident. We do not talk about the vacuum incident."** |
| 5 | 18.9–27s | Medium, then a slow push and Dutch tilt | Human arm reaches in. Panic: "No. Don't…" The scratch cuts him off mid-word. Eyes go ^ ^, blush, hearts, purr vibration, glasses slide, whole body melts sideways. Green stamps: EXCEEDS EXPECTATIONS ×2, EMPLOYEE OF THE YEAR | **"And finally… ear scratches."** **"No. Don't. Don't you dare. I am a professio—"** PURR + harp chimes. Dreamy: **"…exceeds expectations."** |
| 6 PUNCH | 27–31.8s | Whoosh-cut back upright, slow push to 2.05x | Fur tuft still messy. "Ahem." **Slow Glasses Push** into the lens. Final slow blink | **"Ahem. You're promoted. Same salary."** … **"Noted."** |
| End card | 31.8–34s | Title card | "PURRKINS & CO. Ep.1", "FOLLOW FOR EP.2: THE INTERN" | Brass button chord |

## AI video prompts (for a photoreal remake, if you later use a credit-based tool)
Start every prompt with the character reference from `studio/01-character-bible-and-scenarios.md`, then add:
1. *"…sits behind a dark walnut desk in a cozy home office at dusk, warm desk-lamp light, shallow depth of field, extreme close-up, glares judgmentally over his glasses and slides a paper toward the camera with one paw, 9:16 cinematic."*
2. *"…wide shot, easel chart of falling bar graph beside him, points at it with a paw, human hands nervously tapping on the near edge of the desk, photoreal."*
3. *"…medium shot, raises both front paws and does air quotes, deadpan face, pie chart in background."*
4. *"…extreme close-up of his eyes, pupils shrink in terror, ears flatten, red dramatic lighting, fast push-in zoom, trembling."*
5. *"…a human hand scratches behind his ears, he melts in bliss, eyes closed, glasses slide down his nose, body slowly tips sideways onto the desk, soft pink glow."*
6. *"…sits upright with messy fur on his head, slowly pushes his glasses up with one paw while staring straight into the lens, slow blink."*

**Editing:** use hard cuts on dialogue beats, whooshes on camera changes, zoom punches on every timpani hit, burned-in bold captions in the center safe zone with keywords in yellow, and cut the music completely for the vacuum beat.

## Social package
- **TikTok caption:** My cat gave me a performance review and I've never felt so unemployed 😭 #fyp
- **Instagram Reels caption:** He scheduled the meeting. He brought charts. He did NOT expect the ear scratches. 📋🐱 Rate your landlord 1–10 below 👇
- **YouTube Shorts title:** My Cat Gave Me a Performance Review (It Did Not Go Well)
- **Hashtags:** #talkingcat #catcomedy #funnycats #officehumor #catsoftiktok
- **Thumbnail:** Extreme close-up of Barnaby glaring over gold glasses, with a red "NEEDS IMPROVEMENT" stamp slanting across the corner. Text: "MY CAT FIRED ME?"
- **Engagement question:** "What score would YOUR cat give you? Be honest 👇"
