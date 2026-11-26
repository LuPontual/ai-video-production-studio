# studio/ — Python package (Phase 3+)

Planned layout:
```
studio/
  cli.py              # `studio new | plan | run | qa | status`
  jobs/               # Pydantic models, job store, checkpoints, audit, cost ledger
  core/               # ffmpeg wrapper, probe, audio, captions, reframe, export, qa
  adapters/           # transcriber, motion_renderer, gen_provider
  modules/
    smart_editing/    # Module 1 pipeline
    motion_graphics/  # Module 2 bridge to motion/
    ambient_video/    # Module 3
    ai_animation/     # Module 4
```
No code yet: dependencies require approval (see docs/roadmap.md, Phase 3).
