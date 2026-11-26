# Opções de produção da versão final — custos e recomendação

Preços pesquisados em 26/11/2026, em fontes majoritariamente secundárias. **Confirmar na página oficial antes de contratar.** Nada foi contratado.

## 1. Narração PT-BR

| Opção | Custo estimado | Qualidade / risco | Requisitos técnicos |
|---|---|---|---|
| **A. Locutor(a) profissional humano(a)** — recomendada para o flagship | R$ 200–800 por vídeo curto (referências de mercado); varia com reputação, revisões e direitos de uso | Naturalidade e entonação; direitos de uso negociados por escrito | Entrega WAV 48 kHz/24-bit, seco (sem música); 2 takes |
| B. Voz da fundadora (Luciana) | R$ 0 | Máxima autenticidade B2B; depende do ambiente de gravação | Sala silenciosa, celular ou microfone USB a ~20 cm; o estúdio trata o áudio |
| C. TTS ElevenLabs | Creator ≈ US$ 22/mês (licença comercial nos planos pagos; o gratuito não permite uso comercial) | PT-BR bom, mas prosódia menos natural; não atende plenamente "voz natural" no flagship | Liberar host `api.elevenlabs.io` + chave via cofre de segredos |

## 2. Trilha licenciada

| Opção | Custo estimado | Observação de licença |
|---|---|---|
| **A. Epidemic Sound — plano Business** (recomendada) | ~US$ 30/mês no anual ou ~US$ 75/mês mensal (fontes divergem) | Cobre anúncios online; empresas acima de US$ 10 mi/ano devem usar Enterprise. Confirmar o enquadramento da LULLIA. |
| B. Artlist (Pro / Business) | Business sob consulta; tiers individuais conflitantes entre fontes | Exige o tier com licença comercial |
| C. Trilha original encomendada | sob orçamento | Exclusividade total |
| D. Trilha sintetizada pelo estúdio (a da prévia) | R$ 0 | Original, sem direitos de terceiros, mas **não tem qualidade de trilha final** |

## 3. Pós-produção no estúdio (custo de software R$ 0)

| Etapa | Ferramenta | Status |
|---|---|---|
| Motion graphics | Renderizador HTML determinístico (Chromium pré-instalado + FFmpeg) | **Operacional**: gerou a prévia |
| Sincronia de legendas com a voz real | Faster-Whisper (MIT, gratuito) | **Requer aprovação:** instalar o pacote e liberar `huggingface.co` para baixar o modelo |
| Mixagem | FFmpeg: filtro passa-altas, de-esser, compressão, ducking da trilha sob a voz, loudnorm −14 LUFS / −1 dBTP | Operacional |
| QA técnico | `studio/core/qa.py` | **Operacional** |

## 4. Recomendação e orçamento

| Item | Escolha | Custo |
|---|---|---|
| Narração | A (profissional) — ou B, se a fundadora preferir narrar | R$ 200–800 (ou R$ 0) |
| Trilha | Epidemic Sound Business, 1 mês | ~US$ 30–75 |
| Software / render | Stack local | R$ 0 |
| **Total estimado** | | **≈ R$ 400–1.300** |

## Fontes
- [ElevenLabs — preços oficiais](https://elevenlabs.io/pricing/api) · [eesel.ai — Creator vs Business](https://eesel.ai/blog/elevenlabs-pricing) · [bigvu — direitos comerciais](https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/)
- [Epidemic Sound — Business plan](https://www.epidemicsound.com/our-plans/business-plan/) · [Epidemic Sound — Help: Business Plan](https://help.epidemicsound.com/hc/en-us/articles/33405023521554-Business-Plan) · [lesfm — Epidemic Sound pricing 2026](https://lesfm.net/blog/epidemic-sound-pricing)
- [Artlist — planos](https://artlist.io/page/pricing) · [PricingSaaS — Artlist](https://pricingsaas.com/companies/artlist) · [Artyfile — comparação](https://artyfile.com/artlist-alternative)
- [Cronoshare — quanto custa locução](https://www.cronoshare.com.br/quanto-custa/locucao) · [Freelas em Crise — vídeo institucional](https://www.freelasemcrise.com.br/quanto-cobrar/video-institucional)
