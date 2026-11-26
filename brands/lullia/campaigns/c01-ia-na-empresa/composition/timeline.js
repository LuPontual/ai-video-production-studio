// Single source of truth for the C01 timing. Three hook variants (A/B/C) share one body.
// Select the variant with the page query string: index.html?variant=B  (default A).
// Timings are PLANNED narration timings (~2.5 words/s, PT-BR). After the real voiceover is recorded,
// they are re-synced from the Whisper word timestamps of the VO (Smart Editing `transcribe` stage).
(() => {
  const HOOKS = {
    A: [
      { id: "S01", dur: 3.0, vo: "Todo mundo fala de inteligência artificial." },
      { id: "S02", dur: 4.0, vo: "Poucos sabem o que fazer com ela dentro de uma empresa." }
    ],
    B: [
      { id: "B01", dur: 2.4, vo: "Sua empresa já usa IA." },
      { id: "B02", dur: 4.2, vo: "Mas ela já mudou algum resultado do negócio?" }
    ],
    C: [
      { id: "C01", dur: 5.0, vo: "Usar IA para escrever e-mails não é estratégia de inteligência artificial." }
    ]
  };
  const BODY = [
    { id: "S03", dur: 6.4, vo: "Criar textos, apresentações e imagens é apenas uma pequena parte do que essa tecnologia pode oferecer." },
    { id: "S04", dur: 8.0, vo: "A verdadeira oportunidade está em transformar a maneira como as empresas vendem, atendem seus clientes, tomam decisões e crescem." },
    { id: "S05", dur: 3.2, vo: "Mas existe uma pergunta que quase ninguém faz:" },
    { id: "S06", dur: 2.4, vo: "Por onde começar?" },
    { id: "S07", dur: 3.4, vo: "A resposta não está em adotar mais ferramentas." },
    { id: "S08", dur: 5.4, vo: "Está em identificar onde a inteligência artificial pode gerar maior impacto no negócio." },
    { id: "S09", dur: 5.0, vo: "É exatamente essa a proposta do ICEIA™, o diagnóstico estratégico da LULLIA." },
    { id: "S10", dur: 4.6, vo: "Descubra onde estão as principais oportunidades de evolução da sua empresa." },
    { id: "S11", dur: 3.2, vo: "LULLIA — Intelligence. Strategy. Business Impact." },
    { id: "S12", dur: 4.4, vo: "Faça o ICEIA™ gratuitamente em lullia.com.br." }
  ];
  const q = (typeof location !== "undefined" && new URLSearchParams(location.search).get("variant")) || "A";
  const variant = HOOKS[q] ? q : "A";
  let t = 0;
  const scenes = [...HOOKS[variant], ...BODY].map(s => { const o = { ...s, start: +t.toFixed(3), end: +(t + s.dur).toFixed(3) }; t += s.dur; return o; });
  const at = id => scenes.find(s => s.id === id).start;

  window.TIMELINE = {
    id: `lullia-c01-hook${variant}`,
    variant,
    fps: 30,
    width: 1080,
    height: 1920,
    duration: +t.toFixed(3),
    // Official LULLIA tokens — from brands/lullia/assets-generated (synced from LuPontual/lullia-site).
    tokens: {
      bg: "#0F1419",        // --nero
      bg2: "#151C23",       // --nero-2
      deep: "#0A0D10",      // --black
      fg: "#EFEAE0",        // --osso
      muted: "#9B9B93",     // --pedra
      accent: "#A9834A",    // --latao
      accentLight: "#DCC08A", // --latao-l
      line: "rgba(155,155,147,.18)", // --line-n
      foil: "linear-gradient(135deg,#A88650 0%,#EBD3A2 38%,#C09C62 62%,#E3C894 100%)", // --foil
      fontDisplay: "'Bodoni Moda', Georgia, serif",
      fontText: "'Jost', sans-serif"
    },
    scenes,
    // Grid dims during the "question" beat (S05–S06).
    quiet: [at("S05"), at("S07")],
    // Audio accents and pulse ranges (seconds) for the temp score and the final mix.
    hits: [0.0, at("S06"), +(at("S09") + 1.8).toFixed(3), at("S12")],
    pulse: [[at("S03"), at("S05")], [at("S08"), at("S11") + 3.2]]
  };
})();
