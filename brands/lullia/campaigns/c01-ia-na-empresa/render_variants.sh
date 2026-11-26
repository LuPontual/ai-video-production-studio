#!/usr/bin/env bash
# Render C01 hook variants end to end: motion -> temp score -> mux -> QA -> review copy.
# Usage: render_variants.sh <version> [A B C]
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
VER=${1:?version e.g. v002}; shift; VARIANTS=${*:-A B C}
C=brands/lullia/campaigns/c01-ia-na-empresa
for V in $VARIANTS; do
  J=jobs/20261126-lullia-c01-hook$V; R=$J/renders/$VER; mkdir -p $J/work $R $J/qa
  echo "[$V] render"
  node motion/html-renderer/render.mjs --comp $C/composition/index.html --query variant=$V \
       --out $J/work/video_silent_$VER.mp4 --srt $R/captions_pt-BR_planned.srt --meta $R/timeline_meta.json | tail -1
  D=$(python3 -c "import json;print(json.load(open('$R/timeline_meta.json'))['duration'])")
  echo "[$V] score+mux ($D s)"
  $C/audio/make_temp_score.sh $J/work/temp_score_$VER.wav $R/timeline_meta.json
  $C/audio/mux_preview.sh $J/work/video_silent_$VER.mp4 $J/work/temp_score_$VER.wav $R/lullia_c01_hook${V}_preview_${VER}_9x16.mp4 $D
  echo "[$V] qa"
  python3 studio/core/qa.py $R/lullia_c01_hook${V}_preview_${VER}_9x16.mp4 --preset vertical_1080 \
       --srt $R/captions_pt-BR_planned.srt --expected-duration $D --out $J/qa/qa_report_$VER.json > /dev/null \
       && echo "[$V] QA PASS" || echo "[$V] QA FAIL"
  ffmpeg -hide_banner -loglevel error -y -i $R/lullia_c01_hook${V}_preview_${VER}_9x16.mp4 -c:v libx264 -preset slow -crf 27 \
       -maxrate 4M -bufsize 8M -c:a copy -movflags +faststart $R/lullia_c01_hook${V}_${VER}_review.mp4
  rm -f $J/work/video_silent_$VER.mp4
  echo "[$V] done"
done
