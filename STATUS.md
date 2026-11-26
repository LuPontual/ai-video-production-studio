# Project status — AI Video Production Studio

Updated 2026-11-26 (autonomous work session). Branch: `claude/ai-video-production-studio-tmc1uv`.

## LULLIA film (C03, creative V4.3 approved)

| Area | State |
|---|---|
| Script, shot breakdown, characters, sets, cinematography | **Consolidated** in `brands/lullia/campaigns/c03-o-futuro-nao-espera/production/spec.json` (22 shots, 59.5 s, 38 spoken words); validated by `build.py` (0 errors, 0 warnings) |
| Prompts | **Ready** for 21 shots + 23 reference assets; every keyframe prompt ≤ 951 chars (Gen-4 Image limit 1,000) |
| Budget | From verified connector quotes: 12,660 credits (crop vertical, quality risk) · 19,840 (native 16:9 + 9:16) · **10,150 (native 9:16 first)** |
| Helena single-image test (T1-A) | **Ready to run**: prompt, 10 credits per run, cap 20, objective criteria + `image_qa.py` |
| Post-production pipeline | **Built and tested**: `assemble.py`, `grade.py` (4 act LUTs), `captions.py`, `audio_mix.py` (ducking calibrated 11.7 dB), `screen_insert.py`, `qa.py`, `image_qa.py`, `transcribe.py` |
| Animatic (pipeline proof) | 16:9 + 9:16 rendered end-to-end, technical QA pass (placeholders, not images) |
| Real ICEIA™ interface | 12 screens captured at 2× from a local copy of the site (no data sent) |
| Executive Brief (shot 10) | **Blocked**: needs the real server; request a sample Brief from LULLIA |
| Generation (images/video) | **Blocked**: Figma Weave workspace on free plan (MCP runs exhausted); needs paid plan + per-run approval |
| Voice / music | Pending (narration to be provided; licensed track to choose) |

## Earlier work (preserved)
C01 animatics v001/v002 (hooks A/B/C) · C02 CG film (direction rejected, kept as reference) · V4.0–V4.3 proposals.
