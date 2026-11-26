#!/usr/bin/env bash
# C02 cinematic: render hook variants x aspect ratios -> temp score -> mux -> QA -> review copy.
# Usage: render.sh <version> "<variants>" "<sizes>"   e.g. render.sh v001 "H1 H2 H3" "1080x1920 1920x1080"
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
VER=${1:?version}; VARIANTS=${2:-H1 H2 H3}; SIZES=${3:-1080x1920}
C=brands/lullia/campaigns/c02-cinematic
for V in $VARIANTS; do for SZ in $SIZES; do
  Wd=${SZ%x*}; Ht=${SZ#*x}; TAG=$([ "$Ht" -gt "$Wd" ] && echo 9x16 || echo 16x9); PRESET=$([ "$TAG" = 9x16 ] && echo vertical_1080 || echo horizontal_1080)
  J=jobs/20261126-lullia-c02-$V; R=$J/renders/$VER; mkdir -p $J/work $R $J/qa
  echo "[$V $TAG] render"
  node motion/html-renderer/render.mjs --comp $C/composition/index.html --query "variant=$V&w=$Wd&h=$Ht" \
       --out $J/work/silent_${TAG}_$VER.mp4 --srt $R/captions_pt-BR_planned_$TAG.srt --meta $R/meta_$TAG.json | tail -1
  D=$(python3 -c "import json;print(json.load(open('$R/meta_$TAG.json'))['duration'])")
  $C/audio/make_temp_score.sh $J/work/temp_score_$VER.wav $R/meta_$TAG.json
  OUT=$R/lullia_c02_${V}_${VER}_${TAG}.mp4
  $C/audio/mux_preview.sh $J/work/silent_${TAG}_$VER.mp4 $J/work/temp_score_$VER.wav $OUT $D
  python3 studio/core/qa.py $OUT --preset $PRESET --srt $R/captions_pt-BR_planned_$TAG.srt --expected-duration $D --out $J/qa/qa_${VER}_$TAG.json > /dev/null \
    && echo "[$V $TAG] QA PASS" || echo "[$V $TAG] QA FAIL"
  ffmpeg -hide_banner -loglevel error -y -i $OUT -c:v libx264 -preset slow -crf 26 -maxrate 5M -bufsize 10M -c:a copy -movflags +faststart ${OUT%.mp4}_review.mp4
  rm -f $J/work/silent_${TAG}_$VER.mp4
  echo "[$V $TAG] done"
done; done
