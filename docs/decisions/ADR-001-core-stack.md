# ADR-001 — Core stack: Python + uv + FFmpeg

**Context.** Container has Python 3.13, uv, Node 22 and FFmpeg 6.1 with every codec/filter the MVP needs; no GPU.
**Decision.** Orchestration, job model and media stages in Python (Pydantic + Typer). All media ops go through one FFmpeg wrapper that logs exact commands. Node is used only inside `motion/`.
**Alternatives.** Node-only (Remotion everywhere) — rejected: heavy for pure cutting/encoding and adds license exposure to the whole platform. MoviePy — rejected: slower, less control than raw FFmpeg.
**Consequences.** Two runtimes (Python + Node) with a narrow JSON-props boundary.
