# Modern cartoon test: Pip & Pebble in 3D (0 credits)

A ~9-second test that uses each installed tool for a real job:

| Tool | Job |
|---|---|
| **Blender 4.0** (EEVEE, headless via Xvfb) | 3D Pip and Pebble, meadow, soft sun and fill lights, depth of field, animation, lip sync from the voice track (`build/scene_blender.py`) |
| **Kokoro-82M** | Natural character voices plus per-frame mouth data (`build/voices.py`) |
| **Remotion** (React) | Bouncy animated title card (`studio/engine/src/TitleCard.tsx`) |
| **MLT** (the engine behind Kdenlive) | Edit: title → scene with a luma wipe (`build/assemble.sh`) |
| **NumPy + sox** (Audacity-style audio work) | Original jingle, sound effects, ducking, final mix (`build/music_mix.py`) |

Pipeline: `voices.py` → `blender -b --python scene_blender.py -- <dir> all 12 EEVEE` (run under `xvfb-run`) → Remotion `TitleCard` → `music_mix.py <dir> 2.5` → `assemble.sh <dir> out.mp4`
