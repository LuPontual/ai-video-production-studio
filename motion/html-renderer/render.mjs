#!/usr/bin/env node
// Deterministic HTML motion renderer (MotionRenderer adapter, "html" engine).
// Uses the pre-installed Playwright/Chromium and system FFmpeg — no extra dependencies.
//
// Contract: the composition page exposes window.__composition = { fps, width, height, duration, ready, seek(t), srt?() }.
// seek(t) must set the whole frame purely from t (no wall-clock animation).
//
// Usage:
//   node render.mjs --comp path/index.html --out video.mp4 [--srt out.srt] [--from 0] [--to <dur>] [--quality 92]
//   node render.mjs --comp path/index.html --stills 1.5,10,24 --stills-dir dir/
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => (v.startsWith('--') ? a.concat([[v.slice(2), arr[i + 1]?.startsWith('--') || arr[i + 1] === undefined ? true : arr[i + 1]]]) : a), []));
if (!args.comp) { console.error('missing --comp'); process.exit(2); }

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
await page.goto(pathToFileURL(resolve(args.comp)).href);
await page.waitForFunction(() => window.__composition);
await page.evaluate(() => window.__composition.ready);
const meta = await page.evaluate(() => { const c = window.__composition; return { fps: c.fps, width: c.width, height: c.height, duration: c.duration }; });
await page.setViewportSize({ width: meta.width, height: meta.height });
const stage = await page.$('#stage');

if (args.srt) writeFileSync(args.srt, await page.evaluate(() => window.__composition.srt()));

if (args.stills) {
  const dir = args['stills-dir'] || '.'; mkdirSync(dir, { recursive: true });
  for (const t of String(args.stills).split(',').map(Number)) {
    await page.evaluate(t => window.__composition.seek(t), t);
    await stage.screenshot({ path: join(dir, `still_${t.toFixed(2).padStart(6, '0')}.png`) });
  }
  await browser.close(); console.log('stills written to', dir); process.exit();
}

const from = Number(args.from ?? 0), to = Number(args.to ?? meta.duration);
const q = Number(args.quality ?? 92);
const n = Math.round((to - from) * meta.fps);
const ff = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(meta.fps), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(meta.fps), '-movflags', '+faststart', args.out],
  { stdio: ['pipe', 'inherit', 'inherit'] });
const write = buf => new Promise(res => ff.stdin.write(buf) ? res() : ff.stdin.once('drain', res));
const t0 = Date.now();
for (let i = 0; i < n; i++) {
  const t = from + i / meta.fps;
  await page.evaluate(t => window.__composition.seek(t), t);
  await write(await stage.screenshot({ type: 'jpeg', quality: q }));
  if (i % 150 === 0) console.log(`frame ${i}/${n} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
}
ff.stdin.end();
const code = await new Promise(res => ff.on('close', res));
await browser.close();
console.log(`rendered ${n} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s -> ${args.out} (ffmpeg exit ${code})`);
process.exit(code);
