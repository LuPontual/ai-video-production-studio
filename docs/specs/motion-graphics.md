# Spec — Module 2: Motion Graphics

Status: draft. Target: Phase 6 (after Smart Editing MVP).

## Goal

Branded, reusable motion templates (kinetic typography, titles, lower thirds, end cards, animated captions, data callouts) rendered deterministically from props, and composited onto Smart Editing outputs or delivered standalone.

## Engine decision (pending spike — ADR-003)

| Criterion | Remotion 4.x | HyperFrames 0.9.x | FFmpeg drawtext/ASS only |
|---|---|---|---|
| Authoring | React/TSX | HTML + CSS + GSAP | filtergraphs / ASS tags |
| Maturity | High (years, large ecosystem) | Low (first release 2026-03, pre-1.0, rapid churn) | High |
| License | Remotion License: free ≤ 3 employees, paid above | Apache-2.0 | LGPL/GPL (system build) |
| Determinism | Frame-based, deterministic | Frame-seeked headless browser | Deterministic |
| Alpha output | ProRes 4444 / PNG seq / WebM VP9 | MOV / WebM (verify) | ASS overlay only |
| Claude-authoring fit | Good | Very good (plain HTML) | Limited |
| Runs here | Yes (Node 22 + Chrome present) | Yes (expected; verify) | Yes |

**Recommendation:** Remotion as primary engine *if* the producing entity qualifies for the free license (or buys a Company License); run a 1-day spike rendering the same two templates in HyperFrames. If HyperFrames matches quality and stability, it becomes the default for its licensing advantage. FFmpeg/ASS stays as the zero-dependency fallback for animated captions.

## Template contract

```
motion/templates/<template_id>/
  template.yaml    # id, description, props schema, duration rules, supported aspects, alpha: true|false
  <engine files>   # Composition.tsx (Remotion) or index.html (HyperFrames)
```

Props always include: `brand` (resolved tokens: colors, fonts, logo path), `aspect`, `fps`, `durationFrames`, plus template-specific fields. Templates must never embed brand values directly — only read tokens.

## Initial template set

1. `lower_third` — name + role, brand colors, in/out animation.
2. `title_card` — headline + subline, 3–5 s.
3. `kinetic_caption` — word-by-word captions driven by `transcript.cut.json`.
4. `end_card` — logo (official file only) + CTA text.

## Compositing

Overlays rendered with alpha (ProRes 4444 `.mov`) and composited by FFmpeg `overlay` in the Smart Editing `compose_export` stage, so one encoder pass produces the final file.
