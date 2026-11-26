# ADR-005 — AI Animation needs a GPU host

WanGP (Wan2GP, local Wan 2.x video models) and other open video models need an NVIDIA GPU; this container has none. Module 4 will run either on (a) the user's own GPU machine via Remote Control, (b) a rented cloud GPU, or (c) paid APIs. License and VRAM requirements of WanGP and the specific Wan checkpoints must be verified before adoption (not yet verified).
