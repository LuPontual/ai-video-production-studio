# Environment Audit — 2026-11-26

Phase 1. All items marked **Verified** were checked by command in this session. Items marked **Unverified** are assumptions.

## Hardware / OS (Verified)

| Item | Value |
|---|---|
| OS | Ubuntu 24.04.5 LTS, Linux 6.18, x86_64 |
| CPU | 4 vCPU, Intel Xeon @ 2.10 GHz |
| RAM | 15 GiB, no swap |
| GPU | **None** (no `nvidia-smi`, no `/dev/dri`) |
| Disk | ~60 GB available (per-session allowance) |
| Lifetime | Ephemeral cloud container — anything not pushed to git is lost |

## Software (Verified)

| Tool | Version | Notes |
|---|---|---|
| ffmpeg / ffprobe | 6.1.1 | encoders: libx264, libx265, libsvtav1, libvpx-vp9, prores_ks, aac, libopus; filters: subtitles/ass (libass), drawtext, loudnorm, silencedetect, zscale, libplacebo |
| Python | 3.13.18 | pip 24, **uv 0.11.32**; numpy 2.5, pydantic 2.13 present; no torch |
| Node | 22.23 | npm 10.9, pnpm 10.28, yarn 1.22, bun 1.4 |
| Docker | 29.9 | |
| Browser | Chrome for Testing 158 + Playwright Chromium | usable by Remotion / HyperFrames headless render |
| ImageMagick | 6.9 | |
| Fonts | 119 system fonts | brand fonts not installed |
| Missing | faster-whisper, openai-whisper, yt-dlp, Remotion, HyperFrames CLI, sox | |

## Network (Verified, via the environment proxy)

| Host | Result |
|---|---|
| pypi.org, registry.npmjs.org | reachable |
| huggingface.co | **blocked** → Faster-Whisper model download will fail |
| youtube.com | **blocked** → yt-dlp acquisition not possible here |
| api.runwayml.com | **blocked** → no generative provider reachable |

## Credentials (Verified, names only)

GitHub token present (repo-scoped). No API keys for Runway, Higgsfield, OpenAI, Replicate, fal, ElevenLabs, HeyGen or any media provider.

## Connected MCP services (Verified as listed; not exercised)

Adobe (Express, Firefly, video resize/quick cut, fonts), Canva, Figma, HyperFrames by HeyGen, Metricool (social scheduling), Google Drive, Notion, Gmail/Calendar.
Using any of them for private media counts as an **external upload** and needs approval. HyperFrames MCP `compose`/`render_video` are disabled for CLI agents by design; local authoring uses the `hyperframes` npm CLI.

## Package facts (Verified from registries)

| Package | Version | License |
|---|---|---|
| faster-whisper | 1.2.1 | MIT |
| ctranslate2 | 4.9.1 | MIT |
| openai-whisper | 20250625 | MIT |
| yt-dlp | 2026.11.23 | Unlicense |
| remotion | 4.0.547 | Remotion License — free for individuals and orgs ≤ 3 employees; Company License otherwise |
| hyperframes | 0.9.96 | Apache-2.0 — repo heygen-com/hyperframes; first published 2026-03, ~680 versions (very active, pre-1.0, API churn expected) |

## Unverified / to verify

- WanGP (deepbeepmeep/Wan2GP): license and current VRAM requirements not checked (GitHub page not fetched). Regardless, it needs an NVIDIA GPU — **not runnable here**.
- Faster-Whisper CPU speed on this machine (expected roughly real-time or better for `small`/`medium` int8 on 4 cores; to be benchmarked).
- Remotion render throughput on 4 vCPU (expected a few frames/s for 1080p).
- Pricing of Runway / Higgsfield / Kling / Veo APIs — must be checked at decision time; not assumed here.
