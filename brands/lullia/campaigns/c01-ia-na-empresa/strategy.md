# Campanha C01 — "Todo mundo fala de IA. Poucos sabem o que fazer com ela dentro de uma empresa."

Status: **aguardando aprovação** · Marca: LULLIA · Objetivo: leads B2B qualificados para o **ICEIA™** (diagnóstico estratégico, sem custo).

## 0. Alinhamento com o site (verificado em LuPontual/lullia-site @ a642fd4)

| Elemento | Como está no site | Uso na campanha |
|---|---|---|
| Jornada | conteúdo → **ICEIA™** (sem custo) → **Opportunity Blueprint** (aprofundamento pago) → projeto nas 4 frentes | CTA único: ICEIA™. Blueprint não é citado no vídeo. |
| ICEIA™ | "diagnóstico estratégico proprietário da LULLIA para identificar onde uma empresa tem a maior oportunidade de impacto"; 5 dimensões: Inteligência de Decisão · Cliente & Receita · Experiência & Engajamento · Influência de Mercado · Adoção de IA & Transformação; entrega Executive Brief por e-mail | As 5 dimensões aparecem na cena S08, com os nomes exatos. |
| Público | "diretorias e áreas de marketing, comunicação, RH e comercial de médias e grandes empresas" | Público-alvo da distribuição |
| Slogan oficial | "Inteligência que vira experiência. Experiência que vira resultado." | **Divergência:** o roteiro usa "Intelligence. Strategy. Business Impact.", que não aparece no site → decisão pendente |
| Identidade | nero `#0F1419`, osso `#EFEAE0`, pedra `#9B9B93`, latão `#A9834A` + gradiente foil; Bodoni Moda + Jost; logo vetorial oficial | Aplicada sem alterações |
| Rastreamento | o formulário do ICEIA™ grava `utm_source/medium/campaign/content/term`, origem e referrer junto com o lead (Supabase); **não há** GA4, Meta Pixel ou LinkedIn Insight | A mensuração se apoia em UTMs |

**Não verificado:** se o funil está operando ponta a ponta em produção. O site é bloqueado pela rede desta sessão. → Antes de publicar, fazer um envio de teste do ICEIA™ com `utm_source=teste`.

## 1. Três hooks alternativos (primeiros 3 s)

| | Hook | Mecanismo | Visual de abertura |
|---|---|---|---|
| **A** (roteiro aprovado) | "Todo mundo fala de inteligência artificial. Poucos sabem o que fazer com ela dentro de uma empresa." | Contraste coletivo × minoria; posiciona a LULLIA na minoria | Nuvem de jargões de IA que se dissolve |
| **B** | "Sua empresa já usa IA. Mas ela já mudou algum resultado do negócio?" | Pergunta direta ao decisor; gera autoavaliação | Tela limpa; "resultado" em foil |
| **C** | "Usar IA para escrever e-mails não é estratégia de inteligência artificial." | Reenquadramento/provocação; separa ferramenta de estratégia | Chip "e-mails" riscado |

Mesmo corpo de vídeo para os três: só os 3–5 s iniciais mudam (teste A/B/C de retenção).

## 2. Roteiro flagship
Ver `script-timed.md`. Sem afirmações numéricas, sem estatísticas inventadas e sem promessas além das que o site faz.

## 3. Distribuição short-form

| Canal | Papel | Formato | Observação |
|---|---|---|---|
| LinkedIn — perfil da Luciana (founder) | **Principal.** Decisores B2B; voz de liderança | 9:16 nativo + texto de post | O link vai com UTM |
| LinkedIn — página LULLIA | Reforço institucional | 1:1 ou 4:5 | Repost com outro texto |
| Instagram Reels | Alcance secundário | 9:16 | Link na bio ou figurinha de link nos Stories |
| YouTube Shorts | Descoberta / busca | 9:16 | Link na descrição |
| TikTok | Opcional (baixa aderência B2B) | 9:16 | Só após resultado dos outros |

**Sequência sugerida (3 semanas):**
1. Semana 1: flagship com Hook A (53 s) no LinkedIn e no Instagram.
2. Semana 2: variantes B e C (mesmo corpo) e um corte de 20–25 s (S04→S12).
3. Semana 3: repete o hook vencedor em 4:5 para o feed, mais um carrossel estático derivado do storyboard.

Publicação: sempre com aprovação explícita (gate `publish`). Metricool está disponível para agendar, mas usar exige autorização.

## 4. Plano de mensuração

**Padrão de UTM** (capturado pelo formulário do ICEIA™, conforme verificado no código):
```
https://lullia.com.br/?utm_source={linkedin|instagram|youtube}&utm_medium={organic_social|paid_social}
  &utm_campaign=c01_ia_na_empresa&utm_content={hookA|hookB|hookC}_{53s|25s}_{9x16|4x5}#iceia
```

| Etapa do funil | Métrica | Fonte |
|---|---|---|
| Atenção | visualizações; retenção em 3 s (força do hook); taxa de conclusão | analytics nativo de cada rede |
| Interesse | cliques no link (CTR) | analytics nativo |
| Conversão | ICEIAs concluídos com `utm_campaign=c01_ia_na_empresa`, por `utm_content` | tabela de leads (Supabase) |
| Qualidade | % de leads de decisores (cargo e porte) | leitura dos leads |
| Receita | leads que avançam para o Opportunity Blueprint | CRM / acompanhamento manual |

**Lacuna:** sem analytics no site, quem clicou mas não concluiu o ICEIA™ fica invisível. Instalar analytics significaria alterar o site, o que está fora do escopo e depende da sua decisão.
**Leitura:** compare os hooks pela retenção em 3 s e pelos ICEIAs por 1.000 visualizações, não por curtidas.
