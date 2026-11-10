#!/usr/bin/env bash
# Assemble: Blender frames -> scene clip; MLT (Kdenlive's engine) joins title + scene with a luma wipe; mux the mix.
set -euo pipefail
W="$1"; OUT="$2"
ffmpeg -loglevel error -y -framerate 24 -i "$W/bl/f%04d.png" -c:v libx264 -crf 16 -pix_fmt yuv420p "$W/scene.mp4"
# title is 72 frames; a 12-frame luma wipe means the scene starts at frame 60 (2.5s) = music_mix.py offset
melt -silent "$W/title.mp4" "$W/scene.mp4" -mix 12 -mixer luma \
  -consumer avformat:"$W/assembled.mp4" vcodec=libx264 crf=18 an=1 r=24 width=1280 height=720 >/dev/null 2>&1
ffmpeg -loglevel error -y -i "$W/assembled.mp4" -i "$W/final_mix.wav" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
