// Capture the real ICEIA™ flow from a LOCAL, unmodified copy of lullia-site, at 2x, with fictional answers.
// All non-localhost requests are aborted; /api/* is answered by a local stub, so nothing is sent anywhere.
// Usage: node capture_iceia_flow.mjs OUT_DIR [site_root_url=http://127.0.0.1:8765]
import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);
const { chromium } = require('playwright'); import fs from 'node:fs';
const out = process.argv[2], base = process.argv[3] || 'http://127.0.0.1:8765';
const fontsJs = fs.readFileSync('/home/user/lullia-site/js/brief-fonts.js', 'utf8');
const Fo = JSON.parse(fontsJs.slice(fontsJs.indexOf('{'), fontsJs.lastIndexOf('}') + 1));
const face = (fam, file, w, st) => `@font-face{font-family:"${fam}";src:url(data:font/ttf;base64,${Fo[file]}) format("truetype");font-weight:${w};font-style:${st}}`;
const css = [face('Bodoni Moda','BodoniModa-Regular.ttf',400,'normal'),face('Bodoni Moda','BodoniModa-Medium.ttf',500,'normal'),face('Bodoni Moda','BodoniModa-Italic.ttf',400,'italic'),
  face('Jost','Jost-Light.ttf',300,'normal'),face('Jost','Jost-Regular.ttf',400,'normal'),face('Jost','Jost-Medium.ttf',500,'normal')].join('');
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, acceptDownloads: true });
const p = await ctx.newPage();
const log = [];
await p.route('**/*', r => { const u = new URL(r.request().url());
  if (u.hostname !== '127.0.0.1') { log.push('blocked ' + u.hostname); return r.abort(); }
  if (u.pathname.startsWith('/api/')) { log.push('stubbed ' + u.pathname); return r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true, protocolo: 'DEMO-0000' }) }); }
  return r.continue(); });
await p.goto(base + '/#iceia', { waitUntil: 'domcontentloaded' }); await p.addStyleTag({ content: css }); await p.waitForTimeout(600);
await p.getByText('Iniciar meu ICEIA™').first().click(); await p.waitForTimeout(700);
let shot = 0; const snap = async tag => { shot++; await p.screenshot({ path: `${out}/${String(shot).padStart(2, '0')}_${tag}.png` }); };
await snap('inicio');
const fill = { 'ic-nome': 'Helena Prado', 'ic-empresa': 'Empresa Demonstração', 'ic-cargo': 'CEO', 'ic-email': 'helena@exemplo.com', 'ic-tel': '(11) 90000-0000', 'ic-site': 'exemplo.com' };
for (let step = 0; step < 40; step++) {
  // answer every visible, unanswered choice group inside the diagnostic panel
  await p.evaluate(() => {
    const root = document.getElementById('diag') || document;
    const vis = el => !!(el.offsetWidth || el.offsetHeight) && getComputedStyle(el).visibility !== 'hidden';
    const groups = new Map();
    root.querySelectorAll('input[type=radio],input[type=checkbox]').forEach(i => { if (!vis(i.closest('label') || i)) return; const k = i.name || 'g'; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(i); });
    groups.forEach(list => { if (!list.some(i => i.checked)) { const pick = list[Math.min(1, list.length - 1)]; (pick.closest('label') || pick).click(); } });
    const og = new Map();
    root.querySelectorAll('button.opt').forEach(bt => { if (!vis(bt)) return; const k = bt.dataset.g || bt.parentElement?.className || 'o'; if (!og.has(k)) og.set(k, []); og.get(k).push(bt); });
    og.forEach(list => { if (!list.some(bt => bt.getAttribute('aria-pressed') === 'true')) list[Math.min(1, list.length - 1)].click(); });
  });
  for (const [id, v] of Object.entries(fill)) { const el = p.locator('#' + id); if (await el.count() && await el.isVisible().catch(() => false) && !(await el.inputValue().catch(() => ''))) await el.fill(v).catch(() => {}); }
  { const sel = p.locator('#diag select:visible'); for (let i = 0; i < await sel.count(); i++) { const el = sel.nth(i); if (!(await el.inputValue().catch(() => 'x'))) await el.selectOption({ index: 1 }).catch(() => {}); } }
  for (const id of ['ic-lgpd', 'ic-agg']) { const el = p.locator('#' + id); if (await el.count() && await el.isVisible().catch(() => false)) await el.check().catch(() => {}); }
  const next = p.locator('#diag button:visible', { hasText: /Continuar|Próximo passo|Ver resultado|Ver meu resultado|Gerar|Concluir|Enviar|Acessar/i }).last();
  if (!(await next.count())) { await snap('sem_botao'); break; }
  await snap('passo');
  await next.click().catch(() => {}); await p.waitForTimeout(800);
  const body = await p.locator('#diag').innerText().catch(() => '');
  if (/Executive Brief|principal oportunidade/i.test(body) && /baixar|download|PDF/i.test(body)) { await snap('resultado'); await p.locator('#diag').screenshot({ path: `${out}/resultado_painel.png` }).catch(() => {}); break; }
}
// try the Brief download (generated client-side with jsPDF)
const dl = p.locator('#diag :is(button,a):visible', { hasText: /PDF|Baixar|Download|Executive Brief/i }).first();
if (await dl.count()) { const [d] = await Promise.all([p.waitForEvent('download', { timeout: 15000 }).catch(() => null), dl.click().catch(() => {})]);
  if (d) { await d.saveAs(`${out}/executive_brief_demo.pdf`); log.push('brief saved'); } else log.push('brief: no download event'); }
else log.push('brief: button not found');
fs.writeFileSync(`${out}/capture_log.json`, JSON.stringify({ shots: shot, log: [...new Set(log)] }, null, 2));
console.log(JSON.stringify({ shots: shot, log: [...new Set(log)] }));
await b.close();
