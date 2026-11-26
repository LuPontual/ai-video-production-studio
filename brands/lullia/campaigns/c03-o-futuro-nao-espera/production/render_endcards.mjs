import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);
const { chromium } = require('playwright'); import { pathToFileURL } from 'node:url'; import { resolve } from 'node:path';
const out = process.argv[2]; const b = await chromium.launch();
for (const [w, h, tag] of [[1920, 1080, '16x9'], [1080, 1920, '9x16']]) {
  const p = await b.newPage({ viewport: { width: w, height: h } }); const u = pathToFileURL(resolve(new URL('./endcard.html', import.meta.url).pathname)); u.search = `w=${w}&h=${h}`;
  await p.goto(u.href); await p.waitForFunction(() => window.__ready); await p.screenshot({ path: `${out}/endcard_${tag}.png` }); await p.close(); console.log('endcard', tag); }
await b.close();
