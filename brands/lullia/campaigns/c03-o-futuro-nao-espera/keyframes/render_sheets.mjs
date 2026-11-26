import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);
const { chromium } = require('playwright'); import { pathToFileURL } from 'node:url'; import { resolve } from 'node:path';
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on('pageerror', e => console.error('page error', e.message));
for (const k of [1, 2, 3]) { const u = pathToFileURL(resolve('sheets.html')); u.search = `k=${k}`;
  await p.goto(u.href); await p.waitForFunction(() => window.__ready);
  await p.screenshot({ path: `keyframe-${k}.png` }); console.log('ok', k); }
await b.close();
