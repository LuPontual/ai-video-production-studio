# Implementation Roadmap

| Phase | Deliverable | Approval needed | Status |
|---|---|---|---|
| 1 — Environment audit | `docs/audits/2026-11-26-environment-audit.md` | — | Done |
| 2 — Architecture | `CLAUDE.md`, `docs/architecture.md`, specs, ADRs, repo skeleton | Review of this plan | Done (pending review) |
| 3 — Toolchain setup | `pyproject.toml` (uv), install faster-whisper + typer + pyyaml; model access (HF host or pre-staged model) | **Install + network change** | Next |
| 4 — Smart Editing MVP | `studio run` executes stages 1–11 on a sample clip → 9:16 with captions + QA report | Sample video from the user (rights confirmed) | — |
| 5 — Brand configuration | Real `brand.yaml` per brand with user-supplied logos/fonts/colors; caption styles per brand | Brand assets from the user | — |
| 6 — Motion Graphics | Remotion vs HyperFrames spike → 4 templates → overlay compositing | **npm install**; Remotion license check | — |
| 7 — Operations | multi-preset batch, Pipeline B (long-form → clips), delivery packages, cost reports, optional n8n/Metricool hand-off (publish gated) | Account connections | — |
| 8 — Ambient Video | seamless loops, 1–10 h renders, audio beds | Licensed loops/music | — |
| 9 — AI Animation | provider evaluation with real cost per second, character bible, GPU host decision (WanGP) | **Paid API / GPU host** | — |

## Recommended first production test (Phase 4)

A 60–120 s talking-head clip owned by the user (e.g. a SURF PONTUAL instruction tip or a PERSONAL BRAND insight), Portuguese speech:
1. Transcribe (pt) → remove pauses → 9:16 center-crop → burned-in captions → −14 LUFS → H.264 export.
2. Pass/fail on the QA report, then human review of pacing and caption readability.
Success metric: zero manual edits needed for a publishable draft; total processing < 2× clip duration on this machine.
