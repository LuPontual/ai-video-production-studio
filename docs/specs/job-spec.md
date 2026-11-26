# Spec — Job Specification

Machine-readable schema: `schemas/job.schema.json`. Example: `jobs/_examples/smart-edit-sample/job.yaml`.

## Folder layout

```
jobs/<job_id>/
  job.yaml           # declarative spec (human-editable)
  state.json         # stage checkpoints (hashes, timings)
  audit.log          # JSONL: approvals, uploads, provider calls, deliveries
  cost.json          # per-stage time/CPU/bytes/provider cost
  work/              # intermediates (deletable)
  renders/v001/      # outputs, never overwritten
  qa/qa_report.json
  delivery/          # final package after approval
```

`job_id` format: `<yyyymmdd>-<brand_id>-<slug>` (e.g. `20261126-surf-pontual-paddle-tips`).

## Fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | see format above |
| `brand` | enum | `lullia` · `personal-brand` · `cozy-dreamy-night` · `surf-pontual` |
| `module` | enum | `smart_editing` · `motion_graphics` · `ambient_video` · `ai_animation` |
| `brief` | object | `objective`, `audience`, `language` (pt/en/es), `tone`, `notes` |
| `sources[]` | object | `path` (relative to `media/`), `sha256`, `role` (primary/broll/music/vo) |
| `rights` | object | `owner`, `license`, `people_consent` (bool/na), `music_license` |
| `outputs[]` | object | `preset` (from `config/export-presets.yaml`), `captions` (burn/sidecar/none), `languages[]` |
| `params` | object | module-specific overrides (silence threshold, caption style, reframe offset…) |
| `status` | enum | `draft → planned → approved → running → qa_passed/qa_failed → review → delivered` |
| `approvals[]` | object | `gate` (plan/paid_call/upload/delivery/publish), `by`, `at`, `note` |
| `budget` | object | `max_provider_cost_usd` (default 0) |
