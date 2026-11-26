# Spec — Module 1: Smart Editing

Status: draft for approval. Target: first working prototype (Phase 4).

## Goal

Turn one talking-head / speech-driven source clip into platform-ready edits with captions, clean audio and validated technical specs — with zero manual timeline work.

## MVP scope (Phase 4 acceptance)

Input: one local video (≤ 10 min, any common codec), brand id, target preset(s).
Output: `renders/v001/<preset>.mp4` + `captions.srt` + `captions.ass` + `qa_report.json`.

Must:
1. Probe the source and refuse unsupported inputs with a clear error.
2. Transcribe with word-level timestamps (Faster-Whisper, language auto or forced pt/en/es).
3. Remove silences longer than a threshold (default 0.6 s, keep 0.12 s padding) using `silencedetect` + transcript gaps.
4. Reframe to 9:16 (1080×1920) — v1: center crop with manual `x_offset` override; v2: face/subject tracking.
5. Generate captions: max 2 lines, max ~32 chars/line, 1–3 words per highlight group for short-form; style from brand tokens.
6. Audio master: high-pass 80 Hz, optional `afftdn` denoise, two-pass `loudnorm` to −14 LUFS / −1 dBTP.
7. Export H.264 High, yuv420p, 30 fps (or source fps if 24/25/30), AAC 48 kHz 192 kbps, `+faststart`.
8. Run QA and write `qa_report.json`; fail the job on any blocking check.

Not in MVP: highlight selection from long-form (Pipeline B), B-roll insertion, music, translation, motion overlays.

## Stages

| # | Stage | Tool | Output | Checkpoint key |
|---|---|---|---|---|
| 1 | `probe` | ffprobe | `probe.json` | source hash |
| 2 | `extract_audio` | ffmpeg → 16 kHz mono WAV | `audio.wav` | source hash |
| 3 | `transcribe` | Faster-Whisper | `transcript.json` (words, segments, language) | audio hash + model id |
| 4 | `plan_cuts` | silencedetect + transcript | `edl.json` (keep ranges) | transcript + params |
| 5 | `cut` | ffmpeg `trim/atrim + concat` (frame-accurate re-encode) | `cut.mp4` | edl hash |
| 6 | `retime_transcript` | map words through EDL | `transcript.cut.json` | edl + transcript |
| 7 | `reframe` | ffmpeg `crop,scale` | `reframed.mp4` | preset + offset |
| 8 | `captions` | generate SRT + ASS from words | `captions.{srt,ass}` | transcript + style |
| 9 | `audio_master` | ffmpeg loudnorm 2-pass | `audio_master.m4a` | cut hash |
| 10 | `compose_export` | ffmpeg `subtitles=` burn-in + mux | `<preset>.mp4` | all upstream |
| 11 | `qa` | ffprobe, ebur128, blackdetect, freezedetect | `qa_report.json` | export hash |
| 12 | `review` | human | approval in `job.yaml` | — |

## Transcription settings

- Default model: `small` (CPU int8) for drafts, `large-v3` or `large-v3-turbo` int8 for finals if runtime acceptable.
- `word_timestamps=True`, `vad_filter=True`.
- Requires model weights: either approve `huggingface.co` in the network policy, or pre-stage CTranslate2 model files into `models/` (git-ignored).

## Export presets (see `config/export-presets.yaml`)

`vertical_1080` 1080×1920 · `horizontal_1080` 1920×1080 · `square_1080` 1080×1080 · `portrait_4x5` 1080×1350 · `horizontal_2160` 3840×2160 (only if source ≥ 4K).

## QA checks (blocking unless noted)

- Container/codec/pix_fmt/resolution/fps match preset.
- Duration = sum(EDL keep ranges) ± 1 frame.
- Integrated loudness within ±1 LU of target; true peak ≤ −1 dBTP.
- No black segment > 0.5 s, no frozen segment > 2 s (warning only for intentional holds).
- Captions: no cue < 0.3 s or > 7 s, no overlap, all cues within video duration, text inside platform safe area.
- A/V sync: audio and video stream durations differ ≤ 1 frame.

## Performance expectations (to benchmark)

On 4 vCPU without GPU: transcription `small` int8 ≈ faster than real-time (assumption); 1080p x264 `medium` encode ≈ 1–2× real-time (assumption). Benchmarks recorded in Phase 4.
