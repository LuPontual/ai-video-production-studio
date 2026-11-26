# Workflow — Cinematic brand campaign (reusable)

Proven on LULLIA C02. Supports new scripts, audiences, offers and channels without touching the engine.

## 0. Inputs
- Brief (objective, audience, offer, channels) → `brands/<brand>/campaigns/<cNN-slug>/brief.md`
- Brand source of truth synced unmodified: `python3 brands/<brand>/tools/sync_brand_assets.py <site-repo>` (logo SVG, tokens, OFL fonts, with commit provenance)
- Positioning phrases copied from the brand's own site (never invented); offers only as published.

## 1. Creative approval (Phase A) — no spend
1. Three hooks (≤ 6 s, visual, credible) + recommended concept.
2. Narration script with planned timing (~2.4 words/s).
3. Storyboard: per scene → act, timing, camera, image, on-screen text, source (CG ✅ / AI insert / footage).
4. AI insert prompts (keyframe → image-to-video), cost per insert, tool route.
5. Audio strategy, conversion rationale, UTM plan.
→ **Gate: user approval** (`approvals: plan`).

## 2. Visual production — local, no spend
- Composition = `timeline.js` (single source of truth: scenes, VO, camera poses, world state, hook variants, aspect) + `index.html` (CG world + brand overlays).
- Variants via query: `?variant=H1&w=1080&h=1920` / `&w=1920&h=1080`.
- Iterate on stills: `node motion/html-renderer/render.mjs --comp … --query … --stills 1,5,10 --stills-dir out/`
- Full batch: `brands/<brand>/campaigns/<c>/render.sh v001 "H1 H2 H3" "1080x1920 1920x1080"` → render → temp score → mux → QA → review copy.

## 3. AI inserts — gated
- **Gate: `paid_call` approval** with budget (credits or USD) recorded in `job.yaml`.
- Keyframe (image model) → approve frame → image-to-video (Runway Gen-4.5 primary / Veo 3.1 Fast alt) via the connected Figma Weave or a provider API.
- Synthetic people only; no client logos; no legible UI text (UI text comes from motion design).
- Generate 9:16 and 16:9 separately. Store prompts, seeds, model ids and cost in `jobs/<job>/ai_log.jsonl`.

## 4. Audio
- VO delivered as dry WAV 48 kHz/24-bit (one take per line).
- Captions: `tools/whisper/.venv/bin/python studio/core/transcribe.py vo.wav --lang pt --script script.txt --out-dir jobs/<job>/work/`
  → re-time `timeline.js` scene boundaries to the real VO, regenerate captions from transcript.
- Licensed music (license proof stored in `rights.music_license`). Mix: VO priority, music ducked −10/−12 dB, master −14 LUFS / −1 dBTP (social), −16 LUFS (web/YouTube).

## 5. QA and delivery
- `python3 studio/core/qa.py out.mp4 --preset vertical_1080 --srt captions.srt --expected-duration D` (blocking: specs, loudness, black frames, caption timing/format/well-formedness).
- Human creative review against the 10-dimension rubric (score 1–10 with evidence, from the rendered file only).
- **Gate: `delivery` approval**, then **`publish`** approval per channel. UTM per hook × format.

## Versioning
- Code and creative docs in git; renders in `jobs/<job>/renders/vNNN/` (never overwritten; earlier previews preserved).
- Every render reproducible from: composition commit + brand asset commit + query string + tool versions.
