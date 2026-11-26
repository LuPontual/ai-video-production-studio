# LULLIA · C01 "IA dentro da empresa"

| Arquivo | Conteúdo |
|---|---|
| `strategy.md` | Alinhamento com o site, 3 hooks, distribuição, plano de mensuração |
| `script-timed.md` | Roteiro final com marcação de tempo |
| `storyboard.md` | Storyboard de motion por cena |
| `production-options.md` | Opções de narração/trilha com custos e recomendação |
| `composition/` | Composição de motion (HTML determinístico) — `timeline.js` é a fonte de verdade de tempo |
| `audio/make_temp_score.sh` | Trilha provisória sintetizada (somente prévia) |
| `job.yaml` | Job de produção |

Render da prévia:
```bash
python3 brands/lullia/tools/sync_brand_assets.py /path/to/lullia-site     # assets oficiais, sem alteração
node motion/html-renderer/render.mjs --comp brands/lullia/campaigns/c01-ia-na-empresa/composition/index.html \
     --out jobs/20261126-lullia-c01-flagship/work/video_silent.mp4 --srt jobs/.../captions.srt
```
Saídas ficam em `jobs/20261126-lullia-c01-flagship/` (fora do git).
