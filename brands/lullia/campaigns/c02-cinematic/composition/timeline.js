// C02 "O ponto de maior impacto" — cinematic CG film. Single source of truth for timing, camera and world state.
// Query: ?variant=H1|H2|H3  &w=1080&h=1920 (default 9:16) or &w=1920&h=1080 (16:9).
// VO timings are PLANNED (~2.4 words/s, female PT-BR narration). Re-synced from Whisper word timestamps once the VO exists.
//
// Camera pose: { pos:[x,y,z], look:[x,y,z] } or cluster-relative { c:i|'center', off:[x,y,z] } or { c:i, frac:f }
//   (frac = point on the line origin->cluster, camera looks at the cluster). `cut:true` + `from` = editorial hard cut.
// State keys (interpolate from the previous scene's value to `state` over `ramp` = [start,end] fraction of the scene):
//   scatter, drift, broken, connect, flow, center, opp, oppPoint, loopHi, scan, order, pillars, dims, dimAll
(() => {
  const HOOKS = {
    H1: [{ id: "H1", dur: 5.6, act: "I", vo: "Sua empresa já usa inteligência artificial. A pergunta é: na direção certa?",
           from: { pos: [0, 1.2, 19], look: [0, 0, 0] }, to: { pos: [0, 1.0, 13.5], look: [0, 0, 0] },
           init: { scatter: 1, drift: 0 }, state: { drift: 1 }, ramp: [0.5, 0.8] }],
    H2: [{ id: "H2", dur: 5.8, act: "I", vo: "Cada área com a sua ferramenta de IA. E nenhuma conversando com a outra.",
           from: { pos: [-15, 1.8, 13], look: [-6.5, 0, 3] }, to: { pos: [12, 1.8, 12], look: [6, 0, 2] },
           init: { scatter: 0, broken: 1 }, state: { broken: 1 } }],
    H3: [{ id: "H3", dur: 6.0, act: "I", vo: "Se você tivesse que aplicar IA em um só ponto da sua empresa, saberia qual?",
           from: { c: 4, frac: 0.05 }, to: { c: 4, frac: 0.58 },
           init: { scatter: 0, oppPoint: 0 }, state: { oppPoint: 1 }, ramp: [0.62, 0.85] }]
  };
  const BODY = [
    // ACT II — the business reality
    { id: "B1a", dur: 4.2, act: "II", chapter: "ferramentas isoladas", vo: "Hoje, cada área testa a sua própria ferramenta.",
      to: { pos: [3, 3.6, 18.5], look: [0, 0, 0] }, state: { scatter: 0, drift: 0, broken: 1, oppPoint: 0 }, ramp: [0, 0.9] },
    { id: "B1b", dur: 3.0, act: "II", chapter: "dados retidos", vo: "Os dados ficam onde nasceram.", cut: true,
      from: { c: 1, off: [2.8, 1.3, 5.8] }, to: { c: 1, off: [1.6, 0.7, 3.9] }, state: { broken: 0 }, ramp: [0, 0.3] },
    { id: "B1c", dur: 2.6, act: "II", chapter: "retrabalho", vo: "O trabalho repetitivo continua.", cut: true,
      from: { c: 2, off: [-2.6, 1.1, 4.8] }, to: { c: 2, off: [-1.5, 0.6, 3.7] }, state: { loopHi: 1 }, ramp: [0, 0.25] },
    { id: "B1d", dur: 4.0, act: "II", chapter: "decisões sem informação", vo: "E decisões importantes seguem sem a informação que a empresa já tem.", cut: true,
      from: { pos: [0, 1.0, 6.4], look: [0, 0, 0] }, to: { pos: [0, 0.5, 3.7], look: [0, 0, 0] }, state: { loopHi: 0, center: 0.22 }, ramp: [0, 0.3] },
    // ACT III — the transformation
    { id: "B2a", dur: 4.6, act: "III", chapter: "conexão", vo: "A transformação começa quando a inteligência deixa de ser uma iniciativa isolada",
      to: { pos: [0, 7.5, 17], look: [0, 0, 0] }, state: { connect: 0.45, center: 0.45 }, ramp: [0.25, 1] },
    { id: "B2b", dur: 5.6, act: "III", vo: "e passa a conectar a forma como a empresa vende, atende, opera e decide.",
      to: { pos: [-9.5, 8, 12.5], look: [0, 0, 0] }, state: { connect: 1, flow: 1, center: 1 }, ramp: [0, 0.7] },
    { id: "B2c", dur: 4.2, act: "III", chapter: "prioridade", vo: "Com prioridade clara. E indicadores definidos desde o início.",
      to: { c: 4, frac: 0.25, lift: 2.6, side: 2.4 }, state: { scan: 1, opp: 1 }, ramp: [0.1, 0.8] },
    // ACT IV — LULLIA
    { id: "B3a", dur: 5.4, act: "IV", vo: "A LULLIA transforma inteligência, estratégia e experiências em impacto real para o negócio.",
      to: { pos: [0, 7, 36], look: [0, 0, 0] }, state: { scan: 0, order: 1, opp: 0.55 }, ramp: [0, 0.8] },
    { id: "B3b", dur: 4.0, act: "IV", vo: "AI Strategy. Business Transformation. Global Intelligence. B2B Experiences.",
      to: { pos: [0, 3.2, 31], look: [0, 0, 0] }, state: { pillars: 1 }, ramp: [0, 0.6] },
    // ACT V — conversion
    { id: "B4a", dur: 3.6, act: "V", vo: "Comece pelo ICEIA™, o diagnóstico estratégico da LULLIA.",
      to: { c: 4, frac: 0.3, lift: 2.4, side: 3.4 }, state: { pillars: 0, opp: 1, flow: 0.35 }, ramp: [0, 0.5] },
    { id: "B4b", dur: 4.6, act: "V", vo: "Ele mostra onde está a principal oportunidade de impacto da sua empresa.",
      to: { c: 4, frac: 0.38, lift: 2.0, side: 3.0 }, state: { dims: 1 }, ramp: [0.05, 0.4] },
    { id: "B4c", dur: 4.4, act: "V", vo: "Sem custo, em lullia.com.br.",
      to: { pos: [0, 5, 26], look: [0, 3.2, 0], focus: 2.6 }, state: { dims: 0, dimAll: 0.6, flow: 1 }, ramp: [0, 0.5] },
    { id: "B4d", dur: 2.6, act: "V", vo: "",
      to: { pos: [0, 4.6, 24.5], look: [0, 4.2, 0], focus: 2.6 }, state: { dimAll: 0.6 }, ramp: [0, 0.6] }
  ];

  const qs = typeof location !== "undefined" ? new URLSearchParams(location.search) : new URLSearchParams();
  const variant = HOOKS[qs.get("variant")] ? qs.get("variant") : "H1";
  const W = +(qs.get("w") || 1080), H = +(qs.get("h") || 1920);
  let t = 0;
  const scenes = [...HOOKS[variant], ...BODY].map(s => { const o = { ...s, start: +t.toFixed(3), end: +(t + s.dur).toFixed(3) }; t += s.dur; return o; });
  const at = id => scenes.find(s => s.id === id).start;

  window.TIMELINE = {
    id: `lullia-c02-${variant}-${W}x${H}`, variant, fps: 30, width: W, height: H, duration: +t.toFixed(3), scenes,
    tokens: {
      bg: "#0F1419", deep: "#0A0D10", fg: "#EFEAE0", muted: "#9B9B93", accent: "#A9834A", accentLight: "#DCC08A",
      line: "rgba(155,155,147,.18)", foil: "linear-gradient(135deg,#A88650 0%,#EBD3A2 38%,#C09C62 62%,#E3C894 100%)",
      fontDisplay: "'Bodoni Moda', Georgia, serif", fontText: "'Jost', sans-serif"
    },
    slogan: ["Inteligência que vira experiência.", "Experiência que vira resultado."],   // official, lullia-site
    hits: [0, at("B2a"), at("B3a"), +(at("B4a") + 0.3).toFixed(3), at("B4d")],
    pulse: [[at("B2a"), at("B3b") + 4.0]]
  };
})();
