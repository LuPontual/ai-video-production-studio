# ADR-004 — Generative providers gated

All generative providers (Runway, Higgsfield, Kling, Veo, Luma, HeyGen render, ElevenLabs…) are declared in `config/providers.yaml` with `enabled: false`. The `GenVideoProvider` adapter refuses to call without an `approval_id` and a cost estimate under the job budget. Provider hosts are currently blocked by the network policy; enabling one requires (1) user approval, (2) a credential via the secret store, (3) a network host allowance. Pricing must be re-verified at decision time.
