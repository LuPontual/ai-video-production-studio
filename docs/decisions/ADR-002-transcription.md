# ADR-002 — Transcription: Faster-Whisper

**Context.** No GPU. Need PT/EN/ES with word timestamps.
**Decision.** faster-whisper 1.2.x (MIT, CTranslate2 int8 on CPU). `small` for drafts, `large-v3(-turbo)` for finals if runtime is acceptable.
**Alternatives.** openai-whisper (needs torch, slower on CPU); cloud STT APIs (cost, private-content upload).
**Blocker.** Model weights are hosted on huggingface.co, which this environment blocks. Options: (a) approve the host in the network policy, (b) the user provides model files.
