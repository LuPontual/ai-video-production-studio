# T1-A · Teste de 1 imagem cinematográfica de Helena (pronto para executar)

**Status:** preparado; **não executado**. Requer: plano Weave pago + sua aprovação explícita do custo cotado.

| Item | Valor |
|---|---|
| Plano do filme | 3 — close de Helena na sala do conselho, Ato I (luz fria) |
| Modelo | Runway Gen-4 Image via Figma Weave, 16:9, 1080p |
| Custo por execução | **10 créditos** (cotação verificada do conector, 26/11/2026) |
| Máximo do teste | **2 execuções = 20 créditos** |
| Prompt | `run_request.json` (842 caracteres; limite do modelo 1.000) |
| Referências | nenhuma — se aprovada, esta imagem vira a referência de identidade de Helena |

## Procedimento
1. Cotar (sem gasto) → mostrar custo → aprovação explícita → executar 1ª tentativa.
2. Avaliar: `python3 studio/core/image_qa.py helena_t1a.png --look cold --out scorecard.json` + notas humanas 1–9.
3. Só fazer a 2ª tentativa se a 1ª falhar em critério corrigível pelo prompt (registrar o ajuste).
4. Registrar custo, prompt, saída e notas em `jobs/20261126-lullia-c03-t1/audit.log`.

## Critérios de aprovação
**Técnicos (automáticos, `image_qa.py`):** lado maior ≥ 1920 px · nitidez (desvio do Laplaciano ≥ 6, limiar provisório a recalibrar) · altas luzes estouradas ≤ 1,5% · sombras esmagadas ≤ 8% · saturação média ≤ 0,45 · temperatura de meios-tons dentro do look "cold".

**Criativos (nota 1–5, júri: você + eu):**
1. Pele e olhos fotorrealistas (poros, brilho coerente, sem pele plástica)
2. Anatomia sem artefatos (dentes, orelhas, brincos, gola, mãos)
3. Luz motivada conforme o keyframe (key frio lateral, contraste ~4:1, sem "brilho de IA")
4. Ótica crível de 85 mm (compressão, bokeh natural)
5. Fidelidade a Helena (49 anos crível, brasileira, figurino A)
6. Cor dentro da paleta da cena
7. Sem texto ou logos
8. Composição utilizável como primeiro frame e recorte 9:16 seguro
9. Teste cego: passaria como still de um comercial de alto padrão

**Regra de decisão:** APROVA se técnico = pass, critérios 1–5 ≥ 4 e nenhum < 3. Se aprovar, o próximo passo é o restante do T1 (fichas de personagem e cenários, ~250 créditos), sob nova autorização.
