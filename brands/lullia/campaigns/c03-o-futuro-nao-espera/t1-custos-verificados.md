# T1 — custos verificados e recomendação (26/11/2026)

## Fatos verificados (sem gasto)
- Execução T1 bloqueada: workspace Weave no plano gratuito; 2 execuções gratuitas via conector já usadas em 23/11 (Nano Banana Pro, 11 créditos cada — relatório de uso do Weave). 0 créditos gastos hoje.
- Saldo atual: **não exposto pelo conector**; consultar em app.weavy.ai (Settings › Billing).
- Cotações exatas do conector (créditos Weave por execução):

| Modelo / configuração | Créditos | Por segundo |
|---|---|---|
| Runway Gen-4 Image, 1080p, com referência | 10 | — |
| Veo 3.1 imagem→vídeo **Standard**, 1080p, 6 s, sem áudio | **240** | 40 |
| Veo 3.1 imagem→vídeo Fast, 1080p, 6 s | 90 | 15 |
| Veo 3.1 Standard, **4K**, 6 s | 720 | 120 |
| Runway Gen-4.5, 5 s, 1280×720 | 70 | 14 |

Correção: estimativas anteriores usavam ~90 créditos por plano (modo Fast). A qualidade cinematográfica pede Veo 3.1 Standard (240).

## Não verificado (páginas oficiais bloqueadas pela rede desta sessão)
Preços dos planos Weave (fontes secundárias: Starter ~US$ 24/mês com 1.500 créditos; Professional 4.000 créditos, preço divergente US$ 45–60; recarga US$ 10/1.000 créditos no Starter e US$ 10/1.200 no Pro/Team; anual ~30% mais barato segundo uma única fonte). Confirmar em weave.figma.com/pricing antes de assinar.

## Orçamento do filme (21 planos gerados; cartela local)
Premissas: 3 tentativas por plano de vídeo; 2 por imagem; 42 imagens (fichas, cenários, keyframes 16:9 e 6 verticais); 6 planos com versão 9:16 própria.

| Cenário | Vídeo | Imagens | Total créditos | US$ via Weave* | US$ via APIs diretas** |
|---|---|---|---|---|---|
| A · Cinematográfico (Veo Standard em tudo) | 19.440 | 840 | **~20.300** | ~US$ 195–212 | ~US$ 200 |
| **B · Híbrido (Standard em 8 planos de rosto, Fast em 13 de apoio)** | ~12.240 | 840 | **~13.100** | **~US$ 136–140** | ~US$ 120 |
| C · Econômico (Fast em tudo) | 7.290 | 840 | ~8.100 | ~US$ 90 | ~US$ 75 |

\* Plano + recargas (secundário, não verificado). \*\* Veo via Google (US$ 0,40/s Standard, 0,12/s Fast) + Runway Gen-4 Image (US$ 0,08), fontes secundárias; exige contas, chaves e liberação de rede.
Checagem cruzada: 240 créditos ≈ US$ 2,40 por 6 s = US$ 0,40/s, igual ao preço Google do Veo Standard. Custo equivalente; o Weave dispensa chaves e mudanças de rede.

## Teste mínimo proposto: 1 imagem cinematográfica de Helena
- Plano 3 (close na sala do conselho, luz fria de janela, 85 mm). Runway Gen-4 Image 1080p.
- Custo máximo: **20 créditos** (2 tentativas × 10); opcional comparar com Nano Banana Pro (+11).
- Pré-requisito: plano Weave pago (o gratuito está esgotado via conector).

### Critérios objetivos de aprovação (nota 1–5; aprova se 1–5 ≥ 4 e nenhum < 3)
1. Pele e olhos fotorrealistas (poros, brilho nos olhos coerente, sem pele plástica)
2. Anatomia sem artefatos (dentes, orelhas, brincos, gola, mãos se visíveis)
3. Luz motivada conforme o keyframe: key frio lateral, contraste ~4:1, sem "brilho de IA"
4. Ótica crível de 85 mm (compressão, bokeh natural, transição de foco limpa)
5. Fidelidade ao briefing (49 anos crível, brasileira, blazer marinho, camisa osso, brincos latão)
6. Cor dentro da paleta da cena (aço/dessaturado, pretos nero, sem HDR ou saturação excessiva)
7. Resolução ≥ 1920 px no lado maior, sem artefatos de compressão, sem texto ou logos
8. Composição utilizável como primeiro frame de vídeo e com recorte 9:16 seguro
9. Teste cego: passaria como still de um comercial de alto padrão ao lado das referências de linguagem
