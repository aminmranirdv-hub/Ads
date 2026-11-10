# Pip & Pebble: kids' cartoon about friendship values

Original characters, all made in code for **0 credits**. The animation is drawn on an HTML canvas and rendered with Playwright. The voices use espeak-ng with MBROLA. The music and sound effects are synthesized in NumPy.

## Characters
- **Abdelhamid** (wise old owl, round glasses, green vest): the meadow's teacher and narrator. *"Hmm… let's think together."*
- **Aziza** (young giraffe, pink flower): kind and caring. Notices everyone's feelings. *"I see you, friend!"*
- **Amir** (lion cub, leaf crown): brave and loud. Learning that a real leader helps. *"Roar! Follow me!"*
- **Hicham** (squirrel, tool belt): inventor and builder. *"I've got an idea!"*
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

## Ep.2: "Amir's Big Race" (4:56, 16:9)
**Lesson:** being kind is better than being first.
**Voices:** Kokoro-82M neural voices (open-source, offline, free). Each character has its own voice and a slight pitch lift so they sound younger.

Beats: Abdelhamid introduces race day → Hicham builds the finish line → Amir roars in and boasts → Amir laughs at Pebble, Aziza defends him → rules ("how you run matters more than where you finish") → countdown and race → Amir passes the apple tree → Pebble trips on the bridge and is stuck on his back → Amir hears him, remembers Abdelhamid's words (thought bubble) and goes back → "One, two, three, push!" → Pip wins alone and wonders where everybody is → Amir and Pebble cross together → Pip says sorry → Hicham cuts the ribbon so everyone gets a piece → lesson and goodbye.

**YouTube title:** Pip & Pebble Ep.2: Amir's Big Race | Kindness Is Better Than Winning | Kids Cartoon
**Hashtags:** #kidscartoon #kindness #friendship #storiesforkids #pipandpebble
