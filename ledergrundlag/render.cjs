// Renderer index.html frame-for-frame til MP4 (1920x1080, 30 fps).
// Brug:  node render.cjs [--in side.html] [output.mp4]
//        node render.cjs [--in side.html] --stills 3,12.5,40 [mappe]   (PNG-stillbilleder til gennemsyn)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const FPS = 30;
const args = process.argv.slice(2);
const inIdx = args.indexOf('--in');
const input = inIdx >= 0 ? args.splice(inIdx, 2)[1] : 'index.html';
const stillsIdx = args.indexOf('--stills');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('pageerror:', e.message));
  await page.goto('file://' + path.resolve(__dirname, input) + '?capture=1', { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });
  const total = await page.evaluate(() => window.TOTAL);

  if (stillsIdx >= 0) {
    const outDir = args[stillsIdx + 2] || __dirname;
    for (const t of args[stillsIdx + 1].split(',').map(Number)) {
      await page.evaluate(t => window.renderAt(t), t);
      await page.screenshot({ path: path.join(outDir, `still-${t}.png`) });
    }
    await browser.close();
    return;
  }

  const out = args[0] || path.join(__dirname, 'ledergrundlag.mp4');
  const frames = Math.ceil(total * FPS);
  console.log(`Renderer ${frames} frames (${total}s) -> ${out}`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < frames; f++) {
    await page.evaluate(t => window.renderAt(t), f / FPS);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 300 === 0) console.log(`${f}/${frames}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('Færdig:', out);
})();
