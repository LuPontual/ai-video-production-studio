# ADR-003 — Motion engine (proposed)

**Options.** Remotion 4.x (mature, React, Remotion License: free ≤ 3 employees), HyperFrames 0.9.x (Apache-2.0, HTML/GSAP, heygen-com, pre-1.0 with fast churn), FFmpeg/ASS (fallback).
**Proposal.** Abstract behind `MotionRenderer`. Spike both on `lower_third` + `kinetic_caption`, compare visual quality, render time on 4 vCPU, alpha support and API stability. Default to Remotion if eligible for the free license; switch default to HyperFrames if it matches quality.
**Open question for the user.** Headcount of each producing entity (LULLIA etc.) to determine Remotion license tier.
