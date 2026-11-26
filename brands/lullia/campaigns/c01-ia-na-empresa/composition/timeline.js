// Single source of truth for the flagship video timing.
// Timings are PLANNED narration timings (~2.5 words/s, PT-BR). After the real voiceover is recorded,
// they are re-synced from the Whisper word timestamps of the VO (Smart Editing `transcribe` stage).
window.TIMELINE = {
  id: "lullia-c01-flagship",
  fps: 30,
  width: 1080,
  height: 1920,
  duration: 53.0,
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
  scenes: [
    { id: "S01", start: 0.0,  end: 3.0,  vo: "Todo mundo fala de inteligência artificial." },
    { id: "S02", start: 3.0,  end: 7.0,  vo: "Poucos sabem o que fazer com ela dentro de uma empresa." },
    { id: "S03", start: 7.0,  end: 13.4, vo: "Criar textos, apresentações e imagens é apenas uma pequena parte do que essa tecnologia pode oferecer." },
    { id: "S04", start: 13.4, end: 21.4, vo: "A verdadeira oportunidade está em transformar a maneira como as empresas vendem, atendem seus clientes, tomam decisões e crescem." },
    { id: "S05", start: 21.4, end: 24.6, vo: "Mas existe uma pergunta que quase ninguém faz:" },
    { id: "S06", start: 24.6, end: 27.0, vo: "Por onde começar?" },
    { id: "S07", start: 27.0, end: 30.4, vo: "A resposta não está em adotar mais ferramentas." },
    { id: "S08", start: 30.4, end: 35.8, vo: "Está em identificar onde a inteligência artificial pode gerar maior impacto no negócio." },
    { id: "S09", start: 35.8, end: 40.8, vo: "É exatamente essa a proposta do ICEIA™, o diagnóstico estratégico da LULLIA." },
    { id: "S10", start: 40.8, end: 45.4, vo: "Descubra onde estão as principais oportunidades de evolução da sua empresa." },
    { id: "S11", start: 45.4, end: 48.6, vo: "LULLIA — Intelligence. Strategy. Business Impact." },
    { id: "S12", start: 48.6, end: 53.0, vo: "Faça o ICEIA™ gratuitamente em lullia.com.br." }
  ],
  // Audio accents (seconds) used by the placeholder score and as edit points for the final mix.
  hits: [0.0, 24.6, 37.6, 48.6]
};
