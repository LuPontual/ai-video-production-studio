# System Architecture

Version 0.1 — 2026-11-26. Status: proposed (Phase 2).

## 1. Principles

1. **Deterministic core, AI at the edges.** FFmpeg, Whisper and template renderers do the work; LLM planning and generative models are used only where they add measurable value.
2. **Everything is a job.** A job is a folder with a declarative `job.yaml`. Pipelines are pure functions of the job spec + source assets + pinned tool versions.
3. **Modules share one core.** The four production modules are thin compositions of shared stages.
4. **Human in the loop.** Approval checkpoints are first-class pipeline stages, not afterthoughts.
5. **Swappable engines.** Motion renderers, transcription backends and generative providers sit behind adapters.

## 2. Layers

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Interface      studio CLI (Typer)  ·  Claude Code session  ·  (later) web │
├──────────────────────────────────────────────────────────────────────────┤
│ Planning       brief parser · creative plan · script · storyboard         │  Claude-assisted,
│                (outputs editable YAML/Markdown, never renders directly)   │  human-approved
├──────────────────────────────────────────────────────────────────────────┤
│ Orchestration  job store · pipeline runner · checkpoints · retries ·      │
│                approvals · cost ledger · audit log                        │
├──────────────────────────────────────────────────────────────────────────┤
│ Modules        1 Smart Editing │ 2 Motion Graphics │ 3 Ambient │ 4 AI Anim │
├──────────────────────────────────────────────────────────────────────────┤
│ Core stages    probe · transcode · transcribe · cut · reframe · subtitle ·│
│                audio (denoise/loudnorm/duck) · compose · export · QA      │
├──────────────────────────────────────────────────────────────────────────┤
│ Adapters       FFmpeg │ FasterWhisper │ MotionRenderer (Remotion |        │
│                HyperFrames) │ GenVideoProvider (Runway | Kling | WanGP…)  │
├──────────────────────────────────────────────────────────────────────────┤
│ Storage        brands/ · media/ (originals, read-only) · jobs/ (outputs)  │
└──────────────────────────────────────────────────────────────────────────┘
```

## 3. Role → implementation mapping

| Role (master instructions) | Implementation | Deterministic? |
|---|---|---|
| Creative Strategy | Claude planning step → `plan.md` | No (human-approved) |
| Scriptwriting | Claude planning step → `script.md` / VO text | No (human-approved) |
| Storyboard | Claude → `storyboard.yaml` (shots, durations, assets) | No (human-approved) |
| Video Editing | `cut`, `silence`, `reframe`, `assemble` stages | Yes |
| Motion Design | `MotionRenderer` adapter + brand templates | Yes (templated) |
| Audio Production | `audio` stage (highpass, denoise, loudnorm, ducking) | Yes |
| Localization | `transcribe` + `subtitle` (+ optional LLM translation) | Mostly |
| Quality Assurance | `qa` stage → `qa_report.json` | Yes |
| Publishing Ops | `package` stage → delivery folder + metadata; publishing gated | Yes, gated |

## 4. Modules

### 4.1 Smart Editing (priority 1)
Source footage → probe → transcribe → silence/filler removal → (optional) highlight selection → reframe to target aspect → captions → audio master → export presets → QA.
Spec: `docs/specs/smart-editing.md`.

### 4.2 Motion Graphics (priority 2)
Template + brand tokens + data (text, timings from transcript) → MotionRenderer → alpha overlay (ProRes 4444 / PNG sequence) or full-frame MP4 → composited by FFmpeg.
Spec: `docs/specs/motion-graphics.md`.

### 4.3 Ambient Video (later)
Approved visual loops → seamless loop builder (crossfade/ping-pong) → long-form assembly via concat demuxer (stream copy where possible) → audio bed with loudness consistency → chapterized long render. CPU-friendly; long renders are disk-bound, not GPU-bound.

### 4.4 AI Animation (research)
Character bible + episode script → storyboard → per-shot generation through `GenVideoProvider` → edit in Smart Editing. Requires either a GPU host (WanGP / Wan 2.x, local) or paid APIs. Rights and consistency of original characters are tracked in `brands/<id>/characters/`.

## 5. Adapters

```python
class MotionRenderer(Protocol):
    def render(self, template: str, props: dict, out: Path, *, fps: int, size: tuple[int,int], alpha: bool) -> RenderResult: ...

class Transcriber(Protocol):
    def transcribe(self, audio: Path, *, language: str | None) -> Transcript: ...   # word-level timestamps

class GenVideoProvider(Protocol):
    def estimate_cost(self, request: GenRequest) -> Money: ...
    def generate(self, request: GenRequest, *, approval_id: str) -> GenResult: ...   # refuses without approval_id
```

## 6. Orchestration

- **Job store:** filesystem (`jobs/<job_id>/job.yaml`) in v1; SQLite index added when job count justifies it.
- **Runner:** sequential stage runner with per-stage checkpoint (`state.json` with input/output hashes). Re-running resumes from the first invalid stage.
- **Retries:** transient failures (I/O, provider 5xx) retried with exponential backoff, max 3; deterministic failures fail fast.
- **Queue:** not needed for v1 (single container). Designed so a queue (e.g. Redis/RQ, or n8n trigger) can feed `studio run <job>` later.
- **Cost ledger:** every stage records wall time, CPU time, output bytes and any provider cost into `cost.json`.
- **Audit log:** append-only `audit.log` (JSONL) for approvals, external uploads, provider calls and deliveries.

## 7. Security and rights

- Originals are never modified; outputs are versioned (`renders/v001`, `v002`…).
- Secrets via environment secret store or git-ignored `.env`; never logged (the ffmpeg/provider wrappers redact).
- External uploads (MCP connectors, provider APIs) require approval and are logged with destination and file hash.
- Each job carries a `rights` block (owner, license, people-consent) that QA checks for presence before delivery.
