#!/usr/bin/env bash
# Mux the rendered (silent) motion video with an audio bed into a social-ready preview MP4.
# Re-encodes video at a delivery bitrate (grain makes the intermediate very large).
set -euo pipefail
VIDEO=${1:?video_silent.mp4}; AUDIO=${2:?audio.wav}; OUT=${3:?out.mp4}; DUR=${4:-53}
ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" -i "$AUDIO" -t "$DUR" \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -profile:v high -preset slow -crf 20 -maxrate 14M -bufsize 28M -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$OUT"
