# Pip & Pebble: kids' cartoon about friendship values

Original characters, all made in code for **0 credits**. The animation is drawn on an HTML canvas and rendered with Playwright. The voices use espeak-ng with MBROLA. The music and sound effects are synthesized in NumPy.

## Characters
- **Pip**: a small cream bunny with a blue scarf. The fastest in Sunny Meadow. Excited and sometimes selfish, but learns quickly.
- **Pebble**: a gentle green turtle. Slow on land, super fast in water. Kind and patient.

## Ep.1: "The Shiny Red Ball" (52s, 16:9, 1920x1080)
**Lesson:** share with friends, and everyone is good at something.
1. **Title card:** "Pip & Pebble, Episode 1."
2. Pip hops in: "Look at my new shiny ball! It's all mine!"
3. Pebble: "Hi Pip! Can I play too?" Pip: "You're too slow… it's MY ball." Pebble feels sad, and the sky turns grey.
4. Pip's "super high bounce" sends the ball down the hill into the pond. "Oh no! I can't swim!"
5. Pebble: "Don't worry, Pip. I can!" He dives in, swims super fast and pushes the ball back.
6. Pip: "You saved my ball! I'm sorry I said you were slow. Want to play with me?" Pebble: "Yes! Friends share!" Hearts appear.
7. They play catch together. End card: "Today's Friendship Lesson."

## Publishing notes
- YouTube: mark the video **"Made for kids"** (required by YouTube under COPPA).
- **Title:** Pip & Pebble Ep.1: The Shiny Red Ball | Sharing Is Caring | Kids Cartoon About Friendship
- **Description:** Pip the bunny learns that friends share and that everyone is good at something! A gentle cartoon for kids aged 2–7.
- **Hashtags:** #kidscartoon #friendship #sharingiscaring #storiesforkids #pipandpebble

Rebuild with `python3 ep01/build/build_audio.py <dir>`, then `node ep01/build/render.js <dir>`, then ffmpeg (same steps as `studio/ep01-performance-review/README.md`).
