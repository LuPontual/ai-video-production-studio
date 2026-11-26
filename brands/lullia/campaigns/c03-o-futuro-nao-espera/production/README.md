# Produção V4.3 — guia operacional (100% IA + pós local)

Fonte única: `spec.json` → `python3 build.py` valida e gera tudo abaixo. Nunca editar os gerados à mão.

| Arquivo | Conteúdo |
|---|---|
| `spec.json` | Filme, estilo por ato, 9 personagens, 11 cenários, 22 planos (tempo, lente, câmera, luz, ação, som, composições, geração), modelos com cotações verificadas |
| `build.py` | Validação (continuidade de tempo e figurino, fala vs. janelas, limites de prompt) + prompts + orçamento + bíblia |
| `BIBLE.md` | Bíblia de produção legível (personagens, cenários, decupagem, falas, orçamento) |
| `PROMPTS.md`, `prompts/shot_NN.json` | Prompt de keyframe (≤ 950 caracteres) + prompt de movimento + parâmetros do modelo por plano |
| `prompts/reference_assets.json` | 23 ativos de referência: fichas (Helena, Augusto, Ana × 4 vistas) + placas de 11 cenários |
| `budget.json` | Orçamento a partir das cotações do conector, com 3 estratégias de vertical |
| `endcard.html` | Cartela oficial (logo do site sem alteração, slogan institucional, CTA, pilares no 16:9) |
| `t1-helena/` | Teste de 1 imagem pronto para executar (prompt, custo, critérios) |

## Ordem de produção (cada etapa paga exige aprovação)
1. **T1-A** — 1 imagem de Helena (≤ 20 créditos) → `image_qa.py` + notas humanas.
2. **T1** — 23 referências (fichas + cenários) → aprovação de identidade e cenários.
3. **Keyframes** — 21 planos (+ verticais nativos conforme a estratégia escolhida) → aprovação plano a plano.
4. **T2** — 3 vídeos-piloto (planos 2, 14, 17) → valida movimento, realismo e a fala em ¾.
5. **Vídeo** — demais planos; salvar como `jobs/<job>/clips/shot_NN.mp4` e `shot_NN_9x16.mp4`.
6. **Pós (local, sem custo):** `studio/core/assemble.py` monta, gradua por ato (`config/luts`), compõe a interface real do ICEIA™ (`screen_insert.py`), queima legendas da marca (`captions.py`), mixa com ducking (`audio_mix.py`), exporta 16:9/9:16 e roda o QA (`qa.py`).
7. **Locução** recebida → `tools/whisper/.venv/bin/python studio/core/transcribe.py VO.wav --script ... --out-dir ...` → legendas sincronizadas → `assemble.py --voice VO.wav --srt captions.srt`.

## Ativos já prontos
- Interface real do ICEIA™: 12 telas a 2× (`jobs/20261126-lullia-c03-animatic/assets/iceia_v2/`), capturadas de cópia local do site, sem envio de dados (`../tools/capture_iceia_flow.mjs`).
- Cartelas 16:9 e 9:16; trilha provisória sintetizada; animatic de produção com o pipeline completo.

## Pendências de ativos
- **Executive Brief real** (plano 10): depende do servidor do site; pedir um Brief de exemplo à LULLIA. O pipeline não simula o backend.
- Locução (narradora + 2 vozes de fala) e trilha licenciada.
