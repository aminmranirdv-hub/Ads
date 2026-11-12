#!/usr/bin/env bash
# Generates a synthetic 16:9 "stage" source clip (test pattern + tone bursts
# standing in for speech and laughter) so the pipeline can be tested without
# any third-party footage.
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -y -hide_banner -loglevel error \
  -f lavfi -i "testsrc2=size=1920x1080:rate=30:duration=30" \
  -f lavfi -i "aevalsrc='0.3*sin(2*PI*(180+40*sin(2*PI*3*t))*t)*gt(sin(2*PI*1.7*t),-0.3)+0.15*(2*random(0)-1)*between(mod(t,10),8,10)':s=48000:d=30" \
  -vf "drawtext=fontfile=$(fc-match 'Inter Black' -f '%{file}'):text='DEMO STAGE  %{pts\:hms}':fontsize=72:fontcolor=white:box=1:boxcolor=black@0.6:x=(w-tw)/2:y=h-160" \
  -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p -c:a aac -shortest source.mp4
echo "wrote $(pwd)/source.mp4"
