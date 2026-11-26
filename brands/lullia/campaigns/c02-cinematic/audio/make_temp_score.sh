#!/usr/bin/env bash
# TEMP SCORE — placeholder only (synthesized with FFmpeg, no third-party material).
# Marks pacing and hit points for the animatic. Replaced by licensed/original music in the final mix.
# Usage: make_temp_score.sh out.wav meta.json   (meta.json written by render.mjs --meta)
set -euo pipefail
OUT=${1:?output.wav}; META=${2:?meta.json}
IFS='|' read -r D HITS PULSE < <(python3 -c "
import json,sys; m=json.load(open('$META'))
print(m['duration'], ' '.join(str(h) for h in m['hits']), '+'.join(f'between(t,{a},{b})' for a,b in m['pulse']), sep='|')")
PAD="(0.18*sin(2*PI*110*t)+0.12*sin(2*PI*164.81*t)+0.10*sin(2*PI*220*t)+0.06*sin(2*PI*261.63*t)+0.05*sin(2*PI*329.63*t))*(0.75+0.25*sin(2*PI*0.08*t))"
PULSEX="0.10*sin(2*PI*440*t)*exp(-22*mod(t,0.6667))*(${PULSE})"
BOOM=""; for h in $HITS; do BOOM="${BOOM}+0.8*sin(2*PI*48*(t-$h))*exp(-2.6*(t-$h))*gte(t,$h)"; done
FADE=$(python3 -c "print($D-2)")
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "aevalsrc='${PAD}':s=48000:d=${D}" \
  -f lavfi -i "aevalsrc='${PULSEX}':s=48000:d=${D}" \
  -f lavfi -i "aevalsrc='0${BOOM}':s=48000:d=${D}" \
  -filter_complex "[0]lowpass=f=1600,aecho=0.8:0.6:120|240:0.3|0.2[p];[1]highpass=f=300,aecho=0.8:0.5:333:0.25[q];[2]lowpass=f=120[b];[p][q][b]amix=inputs=3:normalize=0,afade=t=in:d=0.3,afade=t=out:st=${FADE}:d=2,pan=stereo|c0=c0|c1=c0" \
  -ar 48000 -c:a pcm_s24le "$OUT.raw.wav"
M=$(ffmpeg -hide_banner -i "$OUT.raw.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$M" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -hide_banner -loglevel error -y -i "$OUT.raw.wav" -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" -c:a pcm_s24le "$OUT"
rm -f "$OUT.raw.wav"
