// usage: node render.js <workdir> [t1,t2,...]  -> renders frames (or stills) using Playwright
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2];
  const stills = process.argv[3] ? process.argv[3].split(',').map(Number) : null;
  const T = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.setContent(`<html><body style="margin:0;background:#000"><canvas id="c" width="1920" height="1080"></canvas></body></html>`);
  await page.evaluate((T) => { window.T = T; }, T);
  await page.addScriptTag({ content: fs.readFileSync(path.join(__dirname, 'scene.js'), 'utf8') });
  await page.evaluate(() => document.fonts.ready);
  const out = path.join(dir, stills ? 'stills' : 'frames'); fs.mkdirSync(out, { recursive: true });
  const times = stills || Array.from({ length: Math.ceil(T.end * T.fps) }, (_, i) => i / T.fps);
  for (let i = 0; i < times.length; i++) {
    const url = await page.evaluate((t) => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.92); }, times[i]);
    fs.writeFileSync(path.join(out, stills ? `t${times[i].toFixed(2)}.jpg` : `f${String(i).padStart(5, '0')}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
    if (!stills && i % 150 === 0) console.log('frame', i, '/', times.length);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
