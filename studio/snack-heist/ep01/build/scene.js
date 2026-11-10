// The Snack Squad — Ep.1 "The Cookie Mission" — modern 2D renderer (1920x1080).
(function () {
  const W = 1920, H = 1080, FLOOR = 900;
  const CURTAIN = 420, SOFA0 = 900, SOFA1 = 1700, CUSHION = 1980, DOOR = 2500, CHAIRS = 3150, BEAM0 = 3700, BEAM1 = 4500, ISLAND = 4950, COUNTER = 5850, JAR = 5930, CTOP = 330;
  const MAIN = document.getElementById('c').getContext('2d'); let ctx = MAIN;
  const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c.getContext('2d'); };
  const LAYER = mk(), RIM = mk();
  const T = window.T, B = T.beats;
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
  const backOut = (k) => { const s = 1.7; k = clamp(k) - 1; return k * k * ((s + 1) * k + s) + 1; };
  const hash = (n) => { const x = Math.sin(n * 91.7) * 43758.5453; return x - Math.floor(x); };
  const fr = (t) => Math.floor(t * T.fps);
  const mouth = (spk, t) => Math.max((T['mouth_' + spk] || [])[fr(t)] || 0, (T.mouth_ALL || [])[fr(t)] || 0);
  const at = (k, i = 0) => T[k][i];
  const during = (k, t, pad = 0.3) => t >= T[k][0] - 0.1 && t < T[k][1] + pad;
  function ell(x, y, rx, ry, r = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(.1, rx), Math.max(.1, ry), r, 0, Math.PI * 2); }
  function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
  function text(s, x, y, size, col, o = {}) {
    ctx.save(); ctx.font = `${o.w || 900} ${size}px Inter, "DejaVu Sans", sans-serif`; ctx.textAlign = o.a || 'center'; ctx.textBaseline = 'middle';
    if (o.stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = o.stroke; ctx.strokeStyle = o.sc || '#fff'; ctx.strokeText(s, x, y); }
    ctx.fillStyle = col; ctx.fillText(s, x, y); ctx.restore();
  }
  function grad(x0, y0, x1, y1, stops) { const g = ctx.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => g.addColorStop(o, c)); return g; }
  function rgrad(x, y, r0, r1, stops) { const g = ctx.createRadialGradient(x, y, r0, x, y, r1); stops.forEach(([o, c]) => g.addColorStop(o, c)); return g; }
  function star(x, y, r, col, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.fillStyle = col; ctx.beginPath(); for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5 - Math.PI / 2, d = i % 2 ? r * .45 : r; ctx.lineTo(Math.cos(a) * d, Math.sin(a) * d); } ctx.closePath(); ctx.fill(); ctx.restore(); }
  function heart(x, y, s, col) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(0, 12); ctx.bezierCurveTo(-26, -6, -14, -30, 0, -14); ctx.bezierCurveTo(14, -30, 26, -6, 0, 12); ctx.fill(); ctx.restore(); }

  // shared glossy cartoon eyes. o.mood: happy|joy|shock|sad|worry|sleepy|sleep|squint|blank
  function eyes(xs, y, o, t, sz = 1, iris = null) {
    const blink = ((t + (o.seed || 0)) % 3.9) < 0.12;
    for (const ex of xs) {
      const L = ex === xs[0];
      if (o.mood === 'sleep' || o.mood === 'joy' || blink) { ctx.beginPath(); ctx.lineWidth = 4.5 * sz; ctx.arc(ex, y + (o.mood === 'sleep' ? -4 : 2) * sz, 11 * sz, o.mood === 'sleep' ? 0.15 : Math.PI * 1.1, o.mood === 'sleep' ? Math.PI - 0.15 : Math.PI * 1.9); ctx.stroke(); continue; }
      const big = o.mood === 'shock' ? 1.3 : 1;
      ell(ex, y, 12 * sz * big, 15 * sz * big); ctx.fillStyle = '#fff'; ctx.fill();
      const lx = (o.look || 0) * 4 * sz, ly = (o.lookY || 0) * 4 * sz;
      ell(ex + lx, y + ly + 1 * sz, 9 * sz * big, 11.5 * sz * big); ctx.fillStyle = iris ? rgrad(ex + lx, y + ly + 4 * sz, 1, 12 * sz, [[0, iris[0]], [1, iris[1]]]) : rgrad(ex + lx, y + ly + 4 * sz, 1, 12 * sz, [[0, '#5a3a2a'], [1, '#140c08']]); ctx.fill();
      if (iris) { ell(ex + lx, y + ly + 1 * sz, 4.5 * sz, 7 * sz); ctx.fillStyle = '#140c08'; ctx.fill(); }
      ell(ex + lx - 3.5 * sz, y + ly - 4 * sz, 4 * sz, 4.5 * sz); ctx.fillStyle = '#fff'; ctx.fill(); ell(ex + lx + 3 * sz, y + ly + 5 * sz, 1.8 * sz, 1.8 * sz); ctx.fill();
      if (o.mood === 'sleepy') { ctx.fillStyle = o.lid || '#9aa3ad'; ctx.beginPath(); ctx.rect(ex - 14 * sz, y - 18 * sz * big, 28 * sz, 15 * sz); ctx.fill(); ctx.beginPath(); ctx.lineWidth = 3 * sz; ctx.moveTo(ex - 13 * sz, y - 3 * sz); ctx.lineTo(ex + 13 * sz, y - 3 * sz); ctx.stroke(); }
      ctx.lineWidth = 3.5 * sz;
      if (['sad', 'worry'].includes(o.mood)) { ctx.beginPath(); ctx.moveTo(ex - 12 * sz, y - 22 * sz + (L ? 6 : -1) * sz); ctx.lineTo(ex + 12 * sz, y - 22 * sz + (L ? -1 : 6) * sz); ctx.stroke(); }
      if (o.mood === 'squint') { ctx.beginPath(); ctx.moveTo(ex - 12 * sz, y - 20 * sz + (L ? -4 : 4) * sz); ctx.lineTo(ex + 12 * sz, y - 20 * sz + (L ? 4 : -4) * sz); ctx.stroke(); }
    }
    if (o.tear) { ctx.fillStyle = 'rgba(120,200,255,.9)'; const ty = y + 12 * sz + (t * 50 % 30) * sz; ell(xs[1] + 10 * sz, ty, 4 * sz, 6 * sz); ctx.fill(); }
  }
  function mouthShape(x, y, o, w = 9) {
    const m = o.mouth || 0; ctx.lineWidth = 3.5;
    if (o.chew) { ell(x, y + 2, w * .8, 4 + Math.abs(Math.sin(o.chew * 14)) * 4); ctx.fillStyle = '#6b1f2e'; ctx.fill(); return; }
    if (m > 0.08) { ell(x, y + m * 4, w + m * 4, 2.5 + m * 10); ctx.fillStyle = '#6b1f2e'; ctx.fill(); ell(x, y + 3 + m * 7, w * .6, 1.5 + m * 3.5); ctx.fillStyle = '#ff8fa3'; ctx.fill(); }
    else if (o.mood === 'shock') { ell(x, y + 4, w * .55, w * .7); ctx.fillStyle = '#6b1f2e'; ctx.fill(); }
    else { ctx.beginPath(); if (['sad', 'worry'].includes(o.mood)) ctx.arc(x, y + 8, w * .8, Math.PI * 1.15, Math.PI * 1.85); else ctx.arc(x, y - 5, w * .9, 0.25, Math.PI - 0.25); ctx.stroke(); }
  }

  // ---------------- sets ----------------
  function lightsOn(t) { return ss(at('l1') - 0.9, at('l1') - 0.7, t); }
  function drawSets(t, cam) {
    const on = lightsOn(t), L = cam.cx - 1400 / cam.z, R = cam.cx + 1400 / cam.z;
    // ---- living room ----
    if (L < DOOR + 100) {
      ctx.fillStyle = grad(0, -400, 0, FLOOR, [[0, '#1d2650'], [1, '#2f3f78']]); ctx.fillRect(-1600, -800, DOOR + 1700, FLOOR + 800);
      // wallpaper dots
      ctx.fillStyle = 'rgba(255,255,255,.04)'; for (let x = -1600; x < DOOR; x += 90) for (let y = -700; y < FLOOR - 200; y += 90) { ell(x + (y / 90 % 2) * 45, y, 6, 6); ctx.fill(); }
      // window + moon
      ctx.fillStyle = '#0e1430'; rr(560, 120, 420, 470, 18); ctx.fill();
      ctx.save(); rr(580, 140, 380, 430, 10); ctx.clip();
      ctx.fillStyle = grad(0, 140, 0, 570, [[0, '#0b1d4a'], [1, '#2b4c8f']]); ctx.fillRect(580, 140, 380, 430);
      for (let i = 0; i < 30; i++) { ctx.globalAlpha = 0.5 + 0.5 * Math.sin(t * 2 + i); star(590 + hash(i) * 360, 150 + hash(i + 9) * 380, 3 + hash(i + 3) * 3, '#fff8d0'); } ctx.globalAlpha = 1;
      ctx.fillStyle = rgrad(840, 250, 10, 150, [[0, 'rgba(255,250,210,.5)'], [1, 'rgba(255,250,210,0)']]); ctx.fillRect(680, 100, 320, 320);
      ell(840, 250, 55, 55); ctx.fillStyle = '#fff6cf'; ctx.fill(); ell(822, 236, 10, 10); ctx.fillStyle = 'rgba(200,190,150,.4)'; ctx.fill(); ell(858, 268, 7, 7); ctx.fill();
      ctx.restore(); ctx.fillStyle = '#e8e2f0'; ctx.fillRect(764, 140, 12, 430); ctx.fillRect(580, 350, 380, 12);
      // moonlight pool on floor
      ctx.fillStyle = 'rgba(190,215,255,.10)'; ctx.beginPath(); ctx.moveTo(580, 590); ctx.lineTo(960, 590); ctx.lineTo(1250, FLOOR + 60); ctx.lineTo(700, FLOOR + 60); ctx.fill();
      // curtains
      for (const [cx, d] of [[CURTAIN, -1], [1110, 1]]) { ctx.fillStyle = grad(cx - 80, 0, cx + 80, 0, [[0, '#6a3fa0'], [.5, '#8a5cc8'], [1, '#5a3290']]);
        ctx.beginPath(); ctx.moveTo(cx - 70, 90); ctx.lineTo(cx + 70, 90); for (let y = 90; y <= FLOOR; y += 40) ctx.lineTo(cx + 70 + Math.sin(y / 60 + t) * 6, y); ctx.lineTo(cx - 70, FLOOR); ctx.closePath(); ctx.fill();
        ctx.strokeStyle = 'rgba(0,0,0,.12)'; ctx.lineWidth = 4; for (let k = -40; k <= 40; k += 40) { ctx.beginPath(); ctx.moveTo(cx + k, 95); ctx.lineTo(cx + k + 4, FLOOR); ctx.stroke(); } }
      ctx.fillStyle = '#c9a227'; rr(280, 78, 980, 16, 8); ctx.fill();
      // sofa
      ctx.fillStyle = '#3a6fb0'; rr(SOFA0, 560, SOFA1 - SOFA0, 240, 50); ctx.fill(); ctx.fillStyle = '#4a82c8'; rr(SOFA0 + 40, 680, SOFA1 - SOFA0 - 80, 150, 30); ctx.fill();
      ctx.fillStyle = '#2f5d98'; rr(SOFA0 - 30, 620, 110, 260, 45); ctx.fill(); rr(SOFA1 - 80, 620, 110, 260, 45); ctx.fill();
      ctx.fillStyle = '#ffcf4a'; ctx.save(); ctx.translate(SOFA0 + 220, 640); ctx.rotate(-0.15); rr(-70, -60, 140, 120, 30); ctx.fill(); ctx.restore();
      ctx.fillStyle = '#2a2a3a'; ctx.fillRect(SOFA0 + 30, 870, 26, 30); ctx.fillRect(SOFA1 - 56, 870, 26, 30);
      // floor lamp with warm glow
      ctx.fillStyle = '#3a3a4a'; ctx.fillRect(2240, 330, 12, 570); ell(2246, 895, 60, 12); ctx.fill();
      ctx.fillStyle = '#ffd88a'; ctx.beginPath(); ctx.moveTo(2190, 330); ctx.lineTo(2302, 330); ctx.lineTo(2280, 250); ctx.lineTo(2212, 250); ctx.fill();
      ctx.fillStyle = rgrad(2246, 360, 20, 700, [[0, 'rgba(255,200,120,.30)'], [1, 'rgba(255,200,120,0)']]); ctx.fillRect(1500, -300, 1500, 1300);
      // floor + rug
      ctx.fillStyle = grad(0, FLOOR, 0, FLOOR + 500, [[0, '#6b4a3a'], [1, '#3e2a20']]); ctx.fillRect(-1600, FLOOR, DOOR + 1700, 700);
      ctx.strokeStyle = 'rgba(0,0,0,.18)'; ctx.lineWidth = 3; for (let y = FLOOR + 30; y < FLOOR + 500; y += 50) { ctx.beginPath(); ctx.moveTo(-1600, y); ctx.lineTo(DOOR, y); ctx.stroke(); }
      ell(1300, FLOOR + 70, 650, 70); ctx.fillStyle = '#c0567a'; ctx.fill(); ell(1300, FLOOR + 70, 560, 52); ctx.fillStyle = '#d97a98'; ctx.fill();
      // Mochi's cushion
      ell(CUSHION, FLOOR - 10, 190, 50); ctx.fillStyle = '#e8a34a'; ctx.fill(); ell(CUSHION, FLOOR - 24, 165, 36); ctx.fillStyle = '#f6c06a'; ctx.fill();
    }
    // ---- doorway ----
    ctx.fillStyle = '#e8e2f0'; ctx.fillRect(DOOR - 30, 60, 40, FLOOR - 60); ctx.fillRect(DOOR + 190, 60, 40, FLOOR - 60); ctx.fillRect(DOOR - 30, 40, 260, 40);
    // ---- kitchen ----
    if (R > DOOR) {
      ctx.fillStyle = grad(0, -400, 0, FLOOR, [[0, '#173a4a'], [1, '#2a5a6e']]); ctx.fillRect(DOOR + 10, -800, 4500, FLOOR + 800);
      ctx.fillStyle = 'rgba(255,255,255,.05)'; for (let x = DOOR + 40; x < 6600; x += 70) for (let y = 380; y < FLOOR - 40; y += 70) { rr(x, y, 62, 62, 6); ctx.fill(); }
      // window with blinds
      ctx.fillStyle = '#0e1430'; rr(BEAM0 - 120, 110, 520, 420, 14); ctx.fill();
      ctx.save(); rr(BEAM0 - 105, 125, 490, 390, 8); ctx.clip(); ctx.fillStyle = grad(0, 125, 0, 515, [[0, '#0b1d4a'], [1, '#2b4c8f']]); ctx.fillRect(BEAM0 - 105, 125, 490, 390);
      ell(BEAM0 + 250, 230, 45, 45); ctx.fillStyle = '#fff6cf'; ctx.fill(); ctx.restore();
      ctx.fillStyle = 'rgba(235,230,215,.85)'; for (let y = 130; y < 515; y += 34) ctx.fillRect(BEAM0 - 105, y, 490, 16);
      // chairs
      for (const cx of [CHAIRS - 150, CHAIRS + 150]) { ctx.fillStyle = '#a0703f'; ctx.fillRect(cx - 70, 560, 14, 340); ctx.fillRect(cx + 56, 560, 14, 340); rr(cx - 80, 540, 160, 26, 8); ctx.fill(); ctx.fillRect(cx - 70, 300, 14, 250); ctx.fillRect(cx + 56, 300, 14, 250); rr(cx - 76, 300, 152, 60, 12); ctx.fill(); }
      ctx.fillStyle = '#7a5530'; ctx.fillRect(CHAIRS - 260, 470, 520, 30); ctx.fillRect(CHAIRS - 240, 500, 20, 400); ctx.fillRect(CHAIRS + 220, 500, 20, 400);
      // fridge
      ctx.fillStyle = grad(4500, 0, 4700, 0, [[0, '#dfe8ee'], [1, '#b8c8d2']]); rr(4420, 100, 330, 800, 24); ctx.fill(); ctx.fillStyle = '#9fb0bb'; ctx.fillRect(4430, 420, 310, 8); ctx.fillRect(4700, 200, 12, 160); ctx.fillRect(4700, 470, 12, 200);
      ctx.fillStyle = '#ff6fa8'; rr(4480, 500, 90, 70, 8); ctx.fill(); ctx.fillStyle = '#ffd23f'; star(4600, 250, 26, '#ffd23f');
      // island
      ctx.fillStyle = '#e8dcc6'; rr(ISLAND - 260, 560, 520, 340, 18); ctx.fill(); ctx.fillStyle = '#cdb99a'; rr(ISLAND - 300, 530, 600, 46, 14); ctx.fill();
      ctx.fillStyle = '#b89f7e'; for (const dx of [-160, 0, 160]) { rr(ISLAND + dx - 60, 620, 120, 230, 10); ctx.fill(); }
      // counter + cabinets + jar
      ctx.fillStyle = '#e8dcc6'; ctx.fillRect(COUNTER - 300, CTOP + 30, 1000, FLOOR - CTOP - 30); ctx.fillStyle = '#d0c0a4'; rr(COUNTER - 330, CTOP, 1060, 44, 10); ctx.fill();
      ctx.fillStyle = '#c9b48f'; for (const dx of [-250, 20, 290]) { rr(COUNTER + dx, CTOP + 90, 240, 460, 14); ctx.fill(); ctx.fillStyle = '#a08a68'; ell(COUNTER + dx + (dx < 0 ? 200 : 40), CTOP + 320, 8, 8); ctx.fill(); ctx.fillStyle = '#c9b48f'; }
      ctx.fillStyle = '#7a8a94'; ctx.fillRect(COUNTER - 300, FLOOR - 40, 1000, 40);
      // the cookie jar (lid state handled in scene)
      ctx.fillStyle = rgrad(JAR, CTOP - 70, 10, 200, [[0, `rgba(255,214,90,${.35 * (T._glow || 0)})`], [1, 'rgba(255,214,90,0)']]); ctx.fillRect(JAR - 220, CTOP - 290, 440, 440);
      ctx.fillStyle = 'rgba(200,235,255,.45)'; rr(JAR - 70, CTOP - 150, 140, 150, 26); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 4; ctx.stroke();
      ctx.fillStyle = 'rgba(255,255,255,.5)'; rr(JAR - 50, CTOP - 135, 14, 100, 7); ctx.fill();
      if (!T._cookieOut) { drawCookie(JAR, CTOP - 55, 0.9, 0); }
      ctx.save(); ctx.translate(JAR + (T._lid || 0) * 90, CTOP - 158 - (T._lid || 0) * 60); ctx.rotate((T._lid || 0) * 0.8); ctx.fillStyle = '#e8473f'; rr(-80, -14, 160, 28, 10); ctx.fill(); ell(0, -18, 18, 12); ctx.fill(); ctx.restore();
      text('COOKIES', JAR, CTOP - 92, 18, '#a0522d', { w: 800 });
      // vacuum dock
      ctx.fillStyle = '#3a3f48'; rr(5085, 830, 90, 70, 12); ctx.fill(); ell(5130, 845, 8, 8); ctx.fillStyle = '#5fe08a'; ctx.fill();
      // shiny tile floor with reflections
      ctx.fillStyle = grad(0, FLOOR, 0, FLOOR + 500, [[0, '#d8dfe6'], [1, '#9aa8b4']]); ctx.fillRect(DOOR + 10, FLOOR, 4500, 700);
      for (let x = DOOR + 10, i = 0; x < 6600; x += 120, i++) for (let y = FLOOR, j = 0; y < FLOOR + 600; y += 60, j++) if ((i + j) % 2) { ctx.fillStyle = 'rgba(80,100,120,.18)'; ctx.fillRect(x, y, 120, 60); }
      ctx.fillStyle = 'rgba(255,255,255,.12)'; for (let x = DOOR + 100; x < 6600; x += 400) { ctx.beginPath(); ctx.moveTo(x, FLOOR); ctx.lineTo(x + 60, FLOOR); ctx.lineTo(x + 140, FLOOR + 600); ctx.lineTo(x + 60, FLOOR + 600); ctx.fill(); }
    }
    // night tint / lights on
    T._night = 1 - on;
  }
  function drawMoonbeams(t, glowIdx) {
    for (let i = 0; i < 5; i++) {
      const x0 = BEAM0 - 80 + i * 100, x1 = BEAM0 + 120 + i * 190;
      const g = glowIdx >= i + 1 ? 0.36 : 0.16;
      ctx.fillStyle = `rgba(210,230,255,${g * (1 - lightsOn(t))})`; ctx.beginPath(); ctx.moveTo(x0, 140 + i * 0); ctx.lineTo(x0 + 60, 140); ctx.lineTo(x1 + 80, FLOOR + 40); ctx.lineTo(x1, FLOOR + 40); ctx.fill();
      ctx.fillStyle = `rgba(220,235,255,${(g + .08) * (1 - lightsOn(t))})`; ell(x1 + 40, FLOOR + 30, 70, 14); ctx.fill();
      if (glowIdx === i + 1) text(String(i + 1), x1 + 40, FLOOR - 70, 90, '#ffd23f', { stroke: 12, sc: '#1d2650' });
    }
  }
  function drawCookie(x, y, s, rot) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    ell(0, 0, 46, 44); ctx.fillStyle = rgrad(-10, -12, 4, 50, [[0, '#f3c27a'], [1, '#c98a3a']]); ctx.fill();
    ctx.fillStyle = '#a0682a'; for (const [a, b] of [[-18, -14], [14, -20], [22, 10], [-10, 16], [2, -2], [-26, 6]]) { ell(a, b, 6, 4, a); ctx.fill(); }
    ctx.fillStyle = 'rgba(255,240,200,.6)'; ell(-14, -18, 12, 6, -0.4); ctx.fill(); ctx.restore();
  }

  // ---------------- characters (origin = feet center) ----------------
  function begin(o) { ctx.save(); ctx.translate(o.x, o.y - (o.hop || 0)); ctx.rotate(o.rot || 0); const sq = o.squash || 0; ctx.scale((o.face || 1) * (o.sc || 1) * (1 + sq * .15), (o.sc || 1) * (1 - sq * .15)); ctx.lineWidth = 3.5; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; }
  function drawNibs(o, t) { // hamster
    begin(o); const OUT = '#c08a4a', FUR = '#f2c27b'; ctx.strokeStyle = OUT;
    const sw = o.run ? Math.sin(t * 18) : (o.walk ? Math.sin(t * 10) * .7 : 0);
    for (const [fx, ph] of [[-24, 1], [24, -1]]) { ell(fx + sw * ph * 10, -6 - Math.max(0, sw * ph) * 8, 20, 10); ctx.fillStyle = '#ffb3a7'; ctx.fill(); ctx.stroke(); }
    ell(0, -62, 56, 60); ctx.fillStyle = rgrad(-18, -84, 6, 80, [[0, '#ffd99a'], [1, FUR]]); ctx.fill(); ctx.stroke();
    ell(6, -44, 36, 38); ctx.fillStyle = '#fff5e6'; ctx.fill();
    ctx.fillStyle = '#ffd23f'; rr(-50, -38, 100, 14, 6); ctx.fill(); ctx.fillStyle = '#e8473f'; rr(14, -48, 10, 30, 3); ctx.fill();
    for (const sd of [-1, 1]) { ell(sd * 34, -116, 18, 18); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke(); ell(sd * 34, -116, 10, 10); ctx.fillStyle = '#ffb3c6'; ctx.fill(); }
    ell(-30, -72, 13, 9); ctx.fillStyle = 'rgba(255,130,150,.45)'; ctx.fill(); ell(46, -72, 12, 9); ctx.fill();
    if (o.mask !== false) { ctx.fillStyle = '#3d8bff'; rr(-48, -104 + (o.maskDrop || 0), 100, 30, 14); ctx.fill(); ctx.save(); ctx.translate(-48, -92 + (o.maskDrop || 0)); ctx.rotate(0.5 + Math.sin(t * 6) * .2); rr(-30, -6, 34, 12, 6); ctx.fill(); ctx.restore(); }
    ctx.strokeStyle = '#7a4a1a'; eyes([-6, 26], -90, { ...o, seed: .3 }, t, 0.95);
    ctx.fillStyle = '#ff7f9e'; ell(12, -76, 7, 5); ctx.fill();
    ctx.strokeStyle = '#7a4a1a'; mouthShape(12, -62, o, 8);
    ctx.strokeStyle = 'rgba(122,74,26,.5)'; ctx.lineWidth = 2; for (const sd of [-1, 1]) for (let k = 0; k < 2; k++) { ctx.beginPath(); ctx.moveTo(12 + sd * 12, -72 + k * 6); ctx.lineTo(12 + sd * 40, -76 + k * 10); ctx.stroke(); }
    ctx.lineWidth = 3.5; ctx.strokeStyle = OUT; const arm = o.arms || 'down';
    const ap = arm === 'up' ? [[-44, -112], [52, -112]] : arm === 'point' ? [[-40, -50], [66, -86]] : arm === 'out' ? [[-62, -70], [66, -70]] : arm === 'hold' ? [[-30, -120], [40, -120]] : [[-44 - sw * 8, -50], [48 + sw * 8, -50]];
    for (const [ax, ay] of ap) { ell(ax, ay, 12, 12); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke(); }
    if (o.crayon) { ctx.save(); ctx.translate(ap[1][0], ap[1][1]); ctx.rotate(-0.6); ctx.fillStyle = '#e8473f'; rr(-4, -34, 10, 34, 3); ctx.fill(); ctx.restore(); }
    if (o.holdCookie) drawCookie(4, -150, 0.85, Math.sin(t * 2) * .1);
    if (o.seeds) { ctx.fillStyle = '#5a4030'; for (let i = 0; i < 5; i++) { ell(-20 + i * 9, -122, 4, 6, .4); ctx.fill(); } }
    ctx.restore();
  }
  function drawBubbles(o, t) { // goldfish in a bowl on a skateboard
    begin(o); const wh = (o.roll || 0);
    // skateboard
    ctx.fillStyle = '#e8262e'; rr(-80, -34, 160, 18, 9); ctx.fill(); ctx.fillStyle = '#333'; for (const wx of [-50, 50]) { ell(wx, -10, 13, 13); ctx.fill(); ctx.save(); ctx.translate(wx, -10); ctx.rotate(wh); ctx.fillStyle = '#ddd'; ctx.fillRect(-2, -10, 4, 20); ctx.restore(); ctx.fillStyle = '#333'; }
    // bowl back + water
    const by = -112, slosh = (o.slosh || 0);
    ell(0, by, 82, 80); ctx.fillStyle = 'rgba(190,230,255,.28)'; ctx.fill();
    ctx.save(); ell(0, by, 80, 78); ctx.clip();
    ctx.fillStyle = 'rgba(80,170,230,.45)'; ctx.beginPath(); ctx.moveTo(-90, by - 40 + slosh * 20); for (let x = -90; x <= 90; x += 10) ctx.lineTo(x, by - 40 + slosh * (x / 90) * 22 + Math.sin(x / 15 + t * 4) * 3); ctx.lineTo(90, by + 90); ctx.lineTo(-90, by + 90); ctx.fill();
    ctx.fillStyle = '#d9c070'; ell(0, by + 70, 70, 16); ctx.fill(); ctx.fillStyle = '#3fae47'; for (const px of [-40, 30]) { ctx.beginPath(); ctx.moveTo(px, by + 62); ctx.quadraticCurveTo(px - 10 + Math.sin(t * 2 + px) * 8, by + 20, px + 4, by); ctx.lineTo(px + 8, by + 62); ctx.fill(); }
    // fish
    const fx = Math.sin(t * 1.5 + (o.seed || 0)) * 12 + (o.fishX || 0), fy = by + 6 + Math.sin(t * 2.3) * 6 + (o.fishY || 0), spin = o.spin || 0;
    ctx.save(); ctx.translate(fx, fy); ctx.scale(Math.cos(spin) || 0.01, 1);
    ctx.fillStyle = '#ff8a1f'; ctx.strokeStyle = '#d0601a'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(-26, 0); ctx.quadraticCurveTo(-56, -26 + Math.sin(t * 9) * 6, -60, -4); ctx.quadraticCurveTo(-56, 24 + Math.sin(t * 9) * 6, -26, 0); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(-56, -14); ctx.lineTo(-62, -6); ctx.lineTo(-56, 6); ctx.fill();
    ell(0, 0, 34, 24); ctx.fillStyle = rgrad(-6, -10, 3, 36, [[0, '#ffb35a'], [1, '#ff7a10']]); ctx.fill(); ctx.strokeStyle = '#d0601a'; ctx.stroke();
    ctx.fillStyle = '#ffd0a0'; ctx.beginPath(); ctx.moveTo(-6, -20); ctx.quadraticCurveTo(4, -40 + Math.sin(t * 6) * 4, 14, -20); ctx.fill();
    ctx.strokeStyle = '#7a3a10'; eyes([8, 26], -4, { ...o, seed: 1.2 }, t, 0.62);
    ctx.strokeStyle = '#7a3a10'; mouthShape(28, 10, o, 5);
    ctx.restore();
    // rising bubbles
    ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 2; for (let i = 0; i < 4; i++) { const p = (t * .6 + i / 4) % 1; ell(fx + 20 + Math.sin(t * 3 + i) * 5, fy - 20 - p * 60, 4 + i, 4 + i); ctx.stroke(); }
    ctx.restore(); ctx.restore();
    // glass front (highlights) drawn in bowl space again
    ctx.save(); ctx.translate(o.x, o.y - (o.hop || 0)); ctx.rotate(o.rot || 0); ctx.scale((o.face || 1) * (o.sc || 1), o.sc || 1);
    ctx.strokeStyle = 'rgba(255,255,255,.75)'; ctx.lineWidth = 4; ell(0, by, 82, 80); ctx.stroke();
    ctx.strokeStyle = 'rgba(255,255,255,.6)'; ctx.lineWidth = 7; ctx.beginPath(); ctx.arc(0, by, 66, Math.PI * 1.1, Math.PI * 1.45); ctx.stroke();
    ctx.fillStyle = 'rgba(220,245,255,.6)'; ell(0, by - 74, 52, 10); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.8)'; ctx.lineWidth = 3; ctx.stroke();
    if (o.splash) { ctx.fillStyle = 'rgba(160,220,255,.8)'; for (let i = 0; i < 7; i++) { const a = -Math.PI / 2 + (i - 3) * .35, d = o.splash * 70; ell(Math.cos(a) * d, by - 80 + Math.sin(a) * d + o.splash * o.splash * 40, 6, 8); ctx.fill(); } }
    ctx.restore();
  }
  function drawMochi(o, t) { // big grey cat: pose sit | loaf | run
    begin(o); const OUT = '#77808a', FUR = '#9aa3ad', WH = '#f4f6f8'; ctx.strokeStyle = OUT;
    const pose = o.pose || 'sit', sw = o.run ? Math.sin(t * 16) : (o.walk ? Math.sin(t * 7) * .6 : 0);
    if (pose === 'loaf') {
      ctx.lineWidth = 14; ctx.strokeStyle = FUR; ctx.beginPath(); ctx.moveTo(-120, -30); ctx.quadraticCurveTo(-190, -20, -170 + Math.sin(t) * 6, -80); ctx.stroke(); ctx.lineWidth = 3.5; ctx.strokeStyle = OUT;
      ell(-10, -70, 150, 74); ctx.fillStyle = rgrad(-40, -110, 10, 170, [[0, '#b4bcc5'], [1, FUR]]); ctx.fill(); ctx.stroke();
      ell(70, -40, 50, 30); ctx.fillStyle = WH; ctx.fill(); ell(60, -14, 32, 14); ctx.fill(); ell(110, -14, 32, 14); ctx.fill();
      ctx.save(); ctx.translate(110, -110); headMochi(o, t, FUR, WH, OUT); ctx.restore();
      if (o.mood === 'sleep') for (let i = 0; i < 3; i++) { const p = (t * .4 + i / 3) % 1; ctx.globalAlpha = Math.sin(p * Math.PI); text('z', 180 + p * 60, -200 - p * 120, 30 + i * 10, '#cfe0ff', { w: 800 }); ctx.globalAlpha = 1; }
      ctx.restore(); return;
    }
    const ry = pose === 'run' ? -150 : -150;
    ctx.lineWidth = 16; ctx.strokeStyle = FUR; ctx.beginPath(); ctx.moveTo(-80, -40); ctx.quadraticCurveTo(-170, -60, -150 + Math.sin(t * 2) * 15, -170); ctx.stroke();
    ctx.lineWidth = 3.5; ctx.strokeStyle = OUT;
    for (const [lx, ph] of [[-60, 1], [-20, -1], [40, 1], [80, -1]]) { ell(lx + sw * ph * 16, -16 - Math.max(0, sw * ph) * 10, 30, 18); ctx.fillStyle = WH; ctx.fill(); ctx.stroke(); }
    ell(0, ry + 60, 120, 120); ctx.fillStyle = rgrad(-40, ry, 10, 160, [[0, '#b4bcc5'], [1, FUR]]); ctx.fill(); ctx.stroke();
    ell(14, ry + 70, 64, 80); ctx.fillStyle = WH; ctx.fill();
    ctx.fillStyle = '#e8262e'; rr(-62, ry - 40, 140, 18, 8); ctx.fill(); ell(10, ry - 18, 12, 12); ctx.fillStyle = '#ffd23f'; ctx.fill();
    ctx.save(); ctx.translate(10, ry - 100); headMochi(o, t, FUR, WH, OUT); ctx.restore();
    ctx.restore();
  }
  function headMochi(o, t, FUR, WH, OUT) {
    ctx.strokeStyle = OUT; ctx.lineWidth = 3.5;
    for (const sd of [-1, 1]) { ctx.beginPath(); ctx.moveTo(sd * 30, -50); ctx.lineTo(sd * 70, -100); ctx.lineTo(sd * 80, -30); ctx.closePath(); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke(); ctx.beginPath(); ctx.moveTo(sd * 42, -54); ctx.lineTo(sd * 66, -84); ctx.lineTo(sd * 70, -44); ctx.closePath(); ctx.fillStyle = '#ffb3c6'; ctx.fill(); }
    ell(0, 0, 95, 80); ctx.fillStyle = rgrad(-30, -30, 6, 110, [[0, '#b8c0c9'], [1, FUR]]); ctx.fill(); ctx.stroke();
    ell(0, 30, 50, 34); ctx.fillStyle = WH; ctx.fill();
    ctx.strokeStyle = '#4a525a'; eyes([-32, 32], -6, { ...o, lid: FUR, seed: 2.1 }, t, 1.15, ['#b8f0c0', '#4fae6a']);
    ctx.fillStyle = '#ff9fb2'; ctx.beginPath(); ctx.moveTo(-9, 16); ctx.lineTo(9, 16); ctx.lineTo(0, 26); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = '#4a525a'; mouthShape(0, 38, o, 10);
    if (o.cheeks) { ell(-26, 38, 30, 24); ctx.fillStyle = FUR; ctx.fill(); ell(26, 38, 30, 24); ctx.fill(); }
    ctx.fillStyle = 'rgba(255,140,160,.4)'; ell(-56, 26, 14, 8); ctx.fill(); ell(56, 26, 14, 8); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,.85)'; ctx.lineWidth = 2.5; for (const sd of [-1, 1]) for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.moveTo(sd * 40, 28 + k * 6); ctx.lineTo(sd * 110, 18 + k * 12); ctx.stroke(); }
  }
  function drawLilyLegs(o, t) { // pink bunny slippers + pajama legs coming from above the frame
    for (const [dx, ph] of [[-70, 0], [70, Math.PI]]) {
      const lift = o.walk ? Math.max(0, Math.sin(t * 6 + ph)) * 30 : 0, x = o.x + dx + (o.walk ? Math.sin(t * 6 + ph) * 20 : 0);
      ctx.fillStyle = grad(x - 50, 0, x + 50, 0, [[0, '#f4a6c6'], [1, '#e888b0']]); rr(x - 48, -600, 96, o.y - 40 - lift + 600, 40); ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,.7)'; for (let y = -500; y < o.y - 80; y += 90) star(x + ((y / 90) % 2 ? -14 : 16), y, 10, 'rgba(255,255,255,.7)');
      ell(x + 20, o.y - 30 - lift, 80, 40); ctx.fillStyle = '#ffd3e3'; ctx.fill(); for (const ex of [x - 6, x + 30]) { ell(ex, o.y - 92 - lift, 14, 34, -.2); ctx.fillStyle = '#ffd3e3'; ctx.fill(); ell(ex, o.y - 92 - lift, 7, 22, -.2); ctx.fillStyle = '#ff9ec2'; ctx.fill(); }
      ell(x + 66, o.y - 36 - lift, 6, 6); ctx.fillStyle = '#ff6f9e'; ctx.fill(); ell(x + 40, o.y - 48 - lift, 4, 5); ctx.fillStyle = '#333'; ctx.fill();
    }
  }
  function drawLilyHand(x, y, item, t) {
    ctx.fillStyle = '#f4a6c6'; rr(x - 40, y - 700, 80, 640, 36); ctx.fill();
    ell(x, y - 40, 52, 44); ctx.fillStyle = '#f2c9a8'; ctx.fill(); for (let i = 0; i < 4; i++) { ell(x - 34 + i * 22, y - 2, 11, 18); ctx.fill(); }
    if (item === 'seeds') { ctx.fillStyle = '#5a4030'; for (let i = 0; i < 8; i++) { ell(x - 30 + (i % 4) * 18, y + 18 + Math.floor(i / 4) * 10, 5, 8, .5); ctx.fill(); } }
    if (item === 'flakes') { ctx.fillStyle = '#ff9f1c'; for (let i = 0; i < 10; i++) { const p = (t * 1.5 + i / 10) % 1; ctx.fillRect(x - 20 + hash(i) * 40, y + 10 + p * 120, 6, 4); } }
    if (item === 'biscuit') { ctx.fillStyle = '#c98a3a'; ctx.beginPath(); ctx.ellipse(x, y + 26, 34, 14, 0, 0, Math.PI * 2); ctx.fill(); ctx.beginPath(); ctx.moveTo(x + 30, y + 26); ctx.lineTo(x + 52, y + 12); ctx.lineTo(x + 52, y + 40); ctx.fill(); }
  }
  function drawLilySitting(o, t) { // full Lily for the finale
    ctx.save(); ctx.translate(o.x, o.y); const s = o.sc || 1; ctx.scale(s, s);
    ell(0, -60, 210, 70); ctx.fillStyle = '#f4a6c6'; ctx.fill();
    ctx.fillStyle = grad(-120, -420, 120, -60, [[0, '#f8b8d2'], [1, '#e888b0']]); rr(-120, -420, 240, 380, 100); ctx.fill();
    for (let i = 0; i < 6; i++) star(-70 + (i % 3) * 70, -360 + Math.floor(i / 3) * 120, 12, 'rgba(255,255,255,.7)');
    for (const sd of [-1, 1]) { ctx.fillStyle = '#f4a6c6'; ctx.save(); ctx.translate(sd * 110, -360); ctx.rotate(sd * (0.4 + Math.sin(t * 6) * (o.wave ? .5 : 0))); rr(-30, 0, 60, 200, 30); ctx.fill(); ell(0, 210, 34, 30); ctx.fillStyle = '#f2c9a8'; ctx.fill(); ctx.restore(); }
    ell(0, -540, 130, 125); ctx.fillStyle = '#f2c9a8'; ctx.fill();
    ctx.fillStyle = '#5a3825'; ctx.beginPath(); ctx.arc(0, -560, 132, Math.PI, 0); ctx.fill(); ell(-140, -600, 52, 52); ctx.fill(); ell(140, -600, 52, 52); ctx.fill();
    ctx.strokeStyle = '#3a2410'; eyes([-44, 44], -530, { mood: o.mood || 'happy', seed: 3 }, t, 1.3);
    ctx.fillStyle = 'rgba(255,120,150,.45)'; ell(-80, -490, 22, 12); ctx.fill(); ell(80, -490, 22, 12); ctx.fill();
    ctx.strokeStyle = '#7a3a2a'; mouthShape(0, -470, { mouth: o.mouth || 0, mood: 'happy' }, 18);
    ctx.restore();
  }
  function drawVacuum(o, t) {
    ctx.save(); ctx.translate(o.x, o.y); ctx.rotate(o.rot || 0);
    ell(0, -30, 110, 34); ctx.fillStyle = grad(0, -64, 0, 4, [[0, '#5a6270'], [1, '#2a2e36']]); ctx.fill();
    ell(0, -46, 90, 20); ctx.fillStyle = '#3a404a'; ctx.fill();
    const blink = o.awake ? (Math.sin(t * 10) > 0 ? 1 : 0.3) : 0.15; ell(40, -48, 14, 8); ctx.fillStyle = `rgba(80,180,255,${blink})`; ctx.fill();
    if (o.awake) { ctx.fillStyle = `rgba(80,180,255,${blink * .25})`; ell(40, -48, 60, 30); ctx.fill(); }
    ctx.fillStyle = '#222'; ell(-60, -6, 18, 8); ctx.fill(); ell(60, -6, 18, 8); ctx.fill();
    if (o.zzz) for (let i = 0; i < 3; i++) { const p = (t * .5 + i / 3) % 1; ctx.globalAlpha = Math.sin(p * Math.PI); text('z', 60 + p * 50, -100 - p * 100, 28 + i * 8, '#cfe0ff', { w: 800 }); ctx.globalAlpha = 1; }
    ctx.restore();
  }
  const DRAW = { NIB: drawNibs, BUB: drawBubbles, MOC: drawMochi };

  // ---------------- direction ----------------
  const NB = (x, e = {}) => ({ spk: 'NIB', x, y: FLOOR, face: 1, mood: 'happy', ...e });
  const BB = (x, e = {}) => ({ spk: 'BUB', x, y: FLOOR, face: 1, mood: 'happy', ...e });
  const MC = (x, e = {}) => ({ spk: 'MOC', x, y: FLOOR, face: 1, mood: 'sleepy', ...e });
  function direct(t) {
    const cam = { cx: 960, cy: 560, z: 1 }, S = { props: [], overlay: null, beamGlow: 0, lily: null };
    T._lid = 0; T._glow = 0; T._cookieOut = false;
    let cast = []; const m = (s) => mouth(s, t);
    const titleEnd = T.title[1];
    if (t < titleEnd) { // HOOK: ECU on Nibs, then title card overlay
      cam.cx = 1300; cam.cy = FLOOR - 92; cam.z = lerp(3.4, 2.2, ss(at('n2'), at('n2', 1) + .5, t));
      cast = [NB(1300, { mood: t < at('n2') ? 'squint' : 'happy', mouth: m('NIB'), look: .2 })];
      if (t >= T.title[0]) S.overlay = 'title';
    } else if (t < at('b1') - 0.2) { // Nibs slides down the curtain
      const k = ss(titleEnd, at('b1') - 0.9, t);
      cam.cx = 620; cam.cy = 560; cam.z = 1.25;
      cast = [NB(lerp(CURTAIN + 40, 560, ss(.8, 1, k)), { y: lerp(150, FLOOR, ss(0, .82, k)), arms: k < .82 ? 'up' : 'down', squash: (k > .82 && k < .9) ? .8 : 0, mood: 'joy' })];
    } else if (t < B.mochi[0] - 0.4) { // Bubbles rolls in, banter
      cam.cx = 700; cam.cy = 640; cam.z = 1.45;
      const k = ss(at('b1') - 1.4, at('b1') - 0.2, t);
      const bx = lerp(-250, 820, k), bonk = (t > at('b1') - .2 && t < at('b1') + .3);
      cast = [NB(560, { mouth: m('NIB'), mood: during('b3', t) || t > at('b3', 1) ? 'worry' : 'happy', arms: during('n3', t) ? 'out' : 'down', face: 1 }),
        BB(bx, { face: -1, roll: t * 8 * (k < 1 ? 1 : 0), mouth: m('BUB'), rot: bonk ? Math.sin(t * 40) * .08 : 0, mood: during('b3', t) ? 'blank' : 'joy', spin: during('b2', t) ? t * 12 : 0 })];
    } else if (t < B.plan[0] - 0.4) { // waking Mochi
      cam.cx = 1800; cam.cy = 700; cam.z = 1.5;
      const awake = t >= at('m2') - .1;
      cast = [MC(CUSHION + 30, { pose: awake ? 'sit' : 'loaf', face: -1, mood: awake ? 'shock' : (t >= at('m1') && t < at('m1', 1) + .6 ? 'sleepy' : 'sleep'), mouth: m('MOC'), y: FLOOR - 16, hop: awake ? Math.max(0, Math.sin((t - at('m2')) * 6)) * 30 * (t < at('m2') + .5 ? 1 : 0) : 0 }),
        NB(1640, { mouth: m('NIB'), arms: during('n4', t) ? 'up' : 'point', mood: 'happy' }), BB(1420, { mood: 'happy' })];
      if (awake) S.props.push(['sparkle', CUSHION + 20, FLOOR - 380]);
    } else if (t < B.chant[0] - 0.4) { // the crayon plan
      if (during('n7', t) || during('n8', t, .5)) { S.overlay = 'plan'; S.planStep = during('n8', t, .5) ? 1 + Math.min(2, Math.floor((t - at('n8')) / ((at('n8', 1) - at('n8')) / 3))) : 0; }
      cam.cx = 1300; cam.cy = 700; cam.z = 1.35;
      cast = [NB(1180, { mouth: m('NIB'), crayon: true, arms: 'point', mood: during('n9', t) ? 'squint' : 'happy' }), BB(1430, { face: -1, mouth: m('BUB'), mood: 'joy', spin: during('b5', t) ? t * 10 : 0 }),
        MC(1700, { face: -1, mouth: m('MOC'), mood: 'sleepy' })];
      S.props.push(['paper', 1300, FLOOR + 40]);
    } else if (t < B.floor[0] - 0.4) { // marching chant into the kitchen
      const k = ss(B.chant[0] - .4, B.floor[0] - .4, t), bounce = Math.abs(Math.sin(t * Math.PI * 96 / 60)) * 18;
      const x0 = lerp(1350, 2700, k);
      cam.cx = x0 + 150; cam.cy = 640; cam.z = 1.15;
      cast = [MC(x0 - 260, { walk: true, mood: 'sleepy', hop: bounce * .4, mouth: m('MOC') }), BB(x0 + 40, { roll: t * 6, mouth: m('BUB'), mood: 'joy', hop: bounce * .5 }), NB(x0 + 260, { walk: true, hop: bounce, mouth: m('NIB'), mood: 'joy' })];
      S.props.push(['notes', x0, 500]);
    } else if (t < B.floor2[0] - 0.4) { // Nibs slips and spins
      const slip = ss(at('n12'), at('n12', 1) + 6, t);
      const nx = t < at('n12') ? lerp(2800, 2980, ss(B.floor[0], at('n12'), t)) : lerp(2980, 3420, slip);
      cam.cx = Math.min(nx + 80, 3300); cam.cy = 720; cam.z = 1.6;
      cast = [NB(nx, { walk: t < at('n12'), mouth: m('NIB'), mood: t >= at('n12') ? 'shock' : 'squint', rot: t >= at('n12') ? (t - at('n12')) * 9 * (1 - slip) : 0, arms: t >= at('n12') ? 'up' : 'down' })];
      if (slip >= 1) cast[0].mood = 'blank';
    } else if (t < B.beams[0] - 0.4) { // Bubbles loops, Mochi strolls, "step one complete"
      cam.cx = 3200; cam.cy = 680; cam.z = 1.05;
      const u = (t - B.floor2[0]);
      const loop = ss(0, 7, u), ang = loop * Math.PI * 4;
      const bx = u < 7 ? CHAIRS + Math.sin(ang) * 260 : lerp(CHAIRS, 3600, ss(7, 9, u)), byOff = u < 7 ? Math.cos(ang) * 30 : 0;
      cast = [NB(3420, { mood: during('n13', t) ? 'blank' : 'happy', mouth: m('NIB'), face: -1, rot: during('n13', t) ? Math.sin(t * 6) * .1 : 0 }),
        BB(bx, { y: FLOOR + byOff, roll: t * 10, mouth: m('BUB'), mood: 'joy', face: Math.cos(ang) > 0 ? 1 : -1 }),
        MC(lerp(2700, 3700, ss(1, 14, u)), { walk: true, mood: (u > 6 && u < 8) ? 'joy' : 'sleepy', mouth: (u > 6 && u < 8) ? .9 : m('MOC') })];
      if (during('n13', t)) S.props.push(['dizzy', 3420, FLOOR - 150]);
    } else if (t < B.beams2[0] - 0.4) { // moonbeams: counting + limbo + somersault
      cam.cx = 4100; cam.cy = 640; cam.z = 1.05;
      let glow = 0; for (let i = 1; i <= 5; i++) if (during('k' + i, t, .6)) glow = i;
      S.beamGlow = glow; S.beams = true;
      const lim = ss(at('b7') - .2, at('b7', 1) + 4, t), som = ss(at('b7', 1) + 3, at('b7', 1) + 6, t);
      cast = [NB(lerp(3700, 4400, som), { mouth: m('NIB'), mood: 'joy', rot: som * Math.PI * 2, arms: during('n14', t) ? 'out' : 'down', lookY: 0, hop: Math.sin(som * Math.PI) * 120 }),
        BB(lerp(3560, 4500, lim), { roll: t * 6 * (lim > 0 && lim < 1 ? 1 : 0), mouth: m('BUB'), mood: 'joy', rot: (lim > 0 && lim < 1) ? -0.35 : 0 }),
        MC(3350, { mood: 'sleepy', mouth: m('MOC') })];
    } else if (t < B.vacuum[0] - 0.4) { // Mochi naps in a moonbeam; push
      S.beams = true; cam.cx = 4250; cam.cy = 700; cam.z = 1.25;
      const push = ss(at('n15'), at('b8', 1) + 2.5, t);
      cast = [MC(lerp(4250, 4650, push), { pose: t >= at('m4') + .8 ? 'loaf' : 'sit', mood: t >= at('m4') + .8 ? 'sleep' : 'joy', mouth: m('MOC'), y: FLOOR - 8, face: -1 }),
        NB(lerp(3980, 4320, push) , { arms: 'out', mouth: m('NIB'), mood: t >= at('n15') ? 'squint' : 'worry', rot: t >= at('n15') ? .2 : 0 }),
        BB(lerp(3780, 4120, push), { roll: push * 10, mouth: m('BUB'), mood: during('b8', t) ? 'blank' : 'squint' })];
    } else if (t < B.chase2[0] - 0.4) { // vacuum + chase (+ left/right choice)
      const chaseT = t - at('b10');
      if (t < at('b10')) { // vacuum wakes
        cam.cx = 4500; cam.cy = 760; cam.z = 1.3;
        cast = [NB(4100, { mood: 'shock', mouth: m('NIB'), arms: 'up' }), BB(3900, { mood: 'shock', mouth: m('BUB') }), MC(4350, { mood: 'shock', y: FLOOR - 8 })];
        S.vac = { x: 5250, y: FLOOR + 30, awake: true };
      } else if (t >= B.choose[0] - .2 && t < B.choose[1] - 2) { // Nibs asks the viewer
        cam.cx = 4300; cam.cy = FLOOR - 120; cam.z = 2.0;
        cast = [NB(4300, { mouth: m('NIB'), mood: 'happy', arms: t < at('n28') ? 'out' : 'point', look: 0 })];
        S.overlay = 'arrows'; S.arrowPick = t >= at('n28') ? 'right' : (t > at('n27', 1) ? 'blink' : null);
      } else { // circular chase around the island
        const ph = chaseT * 1.1, cx = ISLAND, r = 560;
        const pos = (o) => ({ x: cx + Math.cos(ph + o) * r, y: FLOOR + 40 + Math.sin(ph + o) * 50, face: -Math.sin(ph + o) > 0 ? 1 : -1, back: Math.sin(ph + o) < 0 });
        const pm = pos(0), pb = pos(-0.35), pv = pos(-1.0);
        cam.cx = ISLAND; cam.cy = 620; cam.z = 0.95;
        const mo = MC(pm.x, { y: pm.y, face: pm.face, run: true, pose: 'run', mood: t > at('m5') ? 'joy' : 'shock', mouth: m('MOC'), sc: pm.back ? .9 : 1 });
        cast = [mo, NB(pm.x + pm.face * 10, { y: pm.y - 270 * (pm.back ? .9 : 1), face: pm.face, arms: 'up', mood: 'joy', mouth: m('NIB'), sc: pm.back ? .9 : 1 }), BB(pb.x, { y: pb.y, face: pb.face, roll: t * 14, mood: 'shock', mouth: m('BUB'), sc: pb.back ? .9 : 1 })];
        S.vac = { x: pv.x, y: pv.y, awake: true, behind: pv.back };
        S.speed = true;
      }
    } else if (t < B.tower[0] - 0.4) { // vacuum bonks and sleeps; freeze; phew
      cam.cx = 5000; cam.cy = 700; cam.z = 1.1; const bonk = B.chase2[0] - .3;
      S.vac = { x: 5420 - 40 * ss(bonk, bonk + .4, t), y: FLOOR + 30, behind: true, awake: t < bonk + 1, zzz: t > bonk + 1.2, rot: (t > bonk && t < bonk + .4) ? Math.sin(t * 50) * .05 : 0 };
      cast = [MC(4700, { mood: t < at('n18') ? 'shock' : 'joy', y: FLOOR - 8 }), NB(4880, { mood: t < at('n18') ? 'shock' : 'joy', mouth: m('NIB'), arms: t < at('n18') ? 'up' : 'down' }), BB(4520, { mood: t < at('n18') ? 'shock' : 'joy' })];
      if (t > bonk && t < bonk + .25) cam.shake = 14;
    } else if (t < B.sneeze[0] - 0.4) { // building the tower, reaching the cookie
      S.vac = { x: 5130, y: FLOOR - 10, zzz: true, behind: true };
      const bowlUp = ss(at('b11') - 1.2, at('b11') - .1, t), climb = ss(at('b11', 1) + 1, at('b11', 1) + 4, t);
      const wob = (t > at('b11', 1) + 4) ? Math.sin(t * 3.2) * .07 : 0;
      const mx = COUNTER - 60, mTop = FLOOR - 340;
      cam.cx = COUNTER - 100; cam.z = 1.05; cam.cy = lerp(640, 520, ss(at('b11'), at('n20'), t));
      if (t < at('m6') - .4) { // size lesson: line up biggest, middle, smallest
        cam.cy = 640;
        cast = [MC(mx - 200, { mood: 'sleepy', mouth: m('MOC'), y: FLOOR - 8 }), BB(mx + 60, { mouth: m('BUB'), mood: 'joy' }), NB(mx + 260, { mouth: m('NIB'), mood: 'happy', arms: 'point' })];
        if (during('b15', t, 1.5) || during('n29', t, .2)) S.overlay = 'sizes';
      } else {
        const mo = MC(mx, { mood: 'squint', mouth: m('MOC'), y: FLOOR - 8, rot: wob * .4 });
        const bowlX = lerp(mx + 260, mx + 10, bowlUp), bowlY = lerp(FLOOR, mTop + 40, bowlUp) ;
        const bu = BB(bowlX + wob * 60, { mouth: m('BUB'), mood: bowlUp >= 1 ? 'joy' : 'worry', rot: wob * .8, splash: during('b11', t) ? ss(at('b11'), at('b11') + .5, t) : 0, slosh: wob * 6 });
        bu.y = bowlY;
        const nTopY = bowlY - 190, nx = lerp(mx + 300, bowlX + 10, climb);
        const nb = NB(nx + wob * 120, { y: lerp(FLOOR, nTopY, climb), mouth: m('NIB'), mood: 'squint', arms: climb >= 1 ? 'up' : 'down', rot: wob * 1.2, walk: climb > 0 && climb < 1 });
        const reach = ss(at('n20', 1) + 1, at('n20', 1) + 3, t);
        if (reach > 0) { nb.x += reach * 30; nb.y -= reach * 20; }
        T._lid = ss(at('n20', 1) + 2.5, at('n20', 1) + 3.3, t); T._glow = T._lid;
        if (t >= at('n21') - .6) { T._cookieOut = true; nb.holdCookie = true; nb.arms = 'hold'; nb.mood = 'joy'; }
        if (t >= at('b16')) bu.mood = 'shock';
        cast = [mo, bu, nb];
        if (t >= at('n20', 1) + 2.5) cam.cy = 420;
      }
    } else if (t < B.lights[0] - 1.0) { // sneeze, collapse, gulp, oops
      S.vac = { x: 5130, y: FLOOR - 10, zzz: true, behind: true }; T._lid = 1; T._cookieOut = true;
      const sn = at('m7', 1), fall = ss(sn, sn + 1.6, t), gulpT = sn + 1.8;
      const mx = COUNTER - 60, mTop = FLOOR - 340;
      cam.cx = COUNTER - 100; cam.cy = lerp(430, 640, ss(sn, sn + 1.2, t)); cam.z = 1.05;
      const pre = t < sn;
      const mo = MC(mx, { mood: pre ? (t > at('m7') + .8 ? 'shock' : 'squint') : (t < gulpT + .1 ? 'shock' : 'blank'), mouth: pre ? m('MOC') : (t < gulpT ? .9 : m('MOC')), y: FLOOR - 8, squash: (t > sn - .1 && t < sn + .2) ? -.6 : 0, cheeks: t > gulpT && t < gulpT + .5 });
      const bu = BB(lerp(mx + 10, mx + 320, fall), { y: lerp(mTop + 40, FLOOR, ss(0, 1, fall * 1.3)), rot: pre ? 0 : (fall < 1 ? fall * 2 : 0), mood: t > at('m8') ? 'sad' : 'shock', mouth: m('BUB'), tear: t > at('b12') });
      const nb = NB(lerp(mx + 20, mx - 300, fall), { y: lerp(mTop - 150, FLOOR, ss(0, 1, fall * 1.2)), rot: pre ? 0 : fall * 6 * (fall < 1 ? 1 : 0), mood: t > at('n22') ? 'sad' : 'shock', mouth: m('NIB'), maskDrop: t > at('n22') ? 18 : 0, arms: pre ? 'hold' : 'up', holdCookie: pre });
      cast = [mo, bu, nb];
      if (!pre && t < gulpT) { const k = clamp((t - sn) / (gulpT - sn)); S.props.push(['cookieFly', lerp(mx + 20, mx + 10, k), lerp(mTop - 300, mTop - 60, k * k) - Math.sin(k * Math.PI) * 200, k * 10]); }
      if (t > sn + 1.6 && t < at('m8')) S.silence = true;
      if (t > gulpT - .1 && t < gulpT + 1.5) cam.z = lerp(1.05, 1.5, ss(gulpT - .1, gulpT + .3, t)), cam.cy = FLOOR - 400;
      if (t >= at('m8') - .3) { cam.z = 1.25; cam.cy = 640; }
    } else if (t < B.party[0] - 0.4) { // lights on, Lily, treats, manners
      S.vac = { x: 5130, y: FLOOR - 10, behind: true }; T._lid = 1; T._cookieOut = true;
      cam.cx = COUNTER - 250; cam.cy = 640; cam.z = 1.15;
      const walkIn = ss(at('l1') - .8, at('l1') + .6, t);
      S.lily = { x: lerp(COUNTER + 600, COUNTER + 260, walkIn), y: FLOOR + 30, walk: walkIn < 1 };
      const caught = t < at('l3');
      const fed = (k) => t > at('l4') + k * 1.6;
      cast = [MC(COUNTER - 460, { mood: caught ? 'shock' : (fed(2) ? 'joy' : 'happy'), mouth: fed(2) && t < at('l5') ? 0 : m('MOC'), chew: fed(2) && t < at('l5') ? t : 0, y: FLOOR - 8 }),
        BB(COUNTER - 200, { mood: caught ? 'shock' : 'joy', mouth: m('BUB') }),
        NB(COUNTER - 40, { mood: caught ? 'shock' : (during('b13', t) ? 'joy' : 'happy'), mouth: m('NIB'), mask: t < at('n23'), seeds: fed(0) && t < at('l6'), arms: during('n23', t) ? 'up' : (fed(0) && t < at('l6') ? 'hold' : 'down'), face: -1 })];
      if (t >= at('l4') && t < at('l5')) { const k = Math.min(2, Math.floor((t - at('l4')) / 1.6)); S.hand = { x: [COUNTER - 40, COUNTER - 200, COUNTER - 460][k], item: ['seeds', 'flakes', 'biscuit'][k] }; }
      if (during('p1', t, .8)) S.overlay = 'please'; if (during('p2', t, .8)) S.overlay = 'thanks';
    } else { // dance party + goodbye + burp + end card
      S.vac = { x: 5130, y: FLOOR - 10, behind: true }; T._lid = 1; T._cookieOut = true;
      cam.cx = COUNTER - 250; cam.cy = 560; cam.z = 0.95;
      const dance = (p) => Math.abs(Math.sin(t * Math.PI * 2 + p)) * 30;
      S.lilySit = { x: COUNTER - 250, y: FLOOR + 10, mouth: m('ALL') * .6, wave: t > B.end[0], sc: .85, mood: 'joy' };
      const sleepy = t > T.end - 9;
      cast = [MC(COUNTER - 650, { pose: sleepy ? 'loaf' : 'sit', mood: sleepy ? 'sleep' : 'joy', hop: sleepy ? 0 : dance(0) * .5, mouth: m('MOC'), y: FLOOR - 8 }),
        BB(COUNTER + 100, { mood: 'joy', hop: dance(1), spin: t * 6, mouth: m('BUB'), face: -1 }), NB(COUNTER + 300, { mood: 'joy', hop: dance(2), arms: 'up', mask: false, mouth: m('NIB'), face: -1 })];
      S.confetti = !sleepy; if (t > T.end - 8 && t < T.end - 7.3) S.props.push(['burp', COUNTER - 520, FLOOR - 200, (t - (T.end - 8)) / .7]);
      if (sleepy) { cam.cx = lerp(COUNTER - 250, COUNTER - 560, ss(T.end - 9, T.end - 8, t)); cam.z = lerp(.95, 1.6, ss(T.end - 9, T.end - 8, t)); cam.cy = lerp(560, 760, ss(T.end - 9, T.end - 8, t)); }
    }
    return { cam, cast, S };
  }

  // ---------------- overlays ----------------
  function overlay(t, S) {
    if (S.overlay === 'title') {
      const k = ss(T.title[0], T.title[0] + .4, t) * (1 - ss(T.title[1] - .5, T.title[1], t));
      ctx.fillStyle = `rgba(14,20,48,${.85 * k})`; ctx.fillRect(0, 0, W, H);
      for (let i = 0; i < 40; i++) { ctx.globalAlpha = k * (.5 + .5 * Math.sin(t * 3 + i)); star(hash(i) * W, hash(i + 5) * H, 3 + hash(i + 2) * 4, '#fff8d0'); } ctx.globalAlpha = 1;
      const b = backOut((t - T.title[0]) / .6); ctx.save(); ctx.globalAlpha = k; ctx.translate(960, 420); ctx.scale(b, b);
      text('THE SNACK SQUAD', 0, 0, 140, '#ffd23f', { stroke: 20, sc: '#3d1d6a' }); ctx.restore();
      ctx.save(); ctx.globalAlpha = k * ss(T.title[0] + .6, T.title[0] + 1, t); rr(660, 540, 600, 80, 40); ctx.fillStyle = '#3d8bff'; ctx.fill(); text('The Cookie Mission', 960, 582, 46, '#fff'); ctx.restore();
      drawCookie(960, 720, 1.1 * b, t);
    }
    if (S.overlay === 'plan') { // crayon plan, full frame
      ctx.fillStyle = '#fdf8ec'; ctx.fillRect(140, 80, 1640, 860); ctx.strokeStyle = '#e8d8b8'; ctx.lineWidth = 3; for (let y = 140; y < 940; y += 50) { ctx.beginPath(); ctx.moveTo(160, y); ctx.lineTo(1760, y); ctx.stroke(); }
      ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      const wob = (x) => x + Math.sin(x * .05) * 3;
      ctx.strokeStyle = '#3d8bff'; ctx.beginPath(); ctx.moveTo(220, 820); for (let x = 220; x < 1700; x += 40) ctx.lineTo(x, wob(820)); ctx.stroke();
      ctx.strokeStyle = '#a0522d'; ctx.strokeRect(1320, 380, 360, 440); ctx.beginPath(); ctx.moveTo(1300, 380); ctx.lineTo(1700, 380); ctx.stroke();
      ctx.strokeStyle = '#e8473f'; ctx.beginPath(); ctx.arc(1520, 300, 60, 0, Math.PI * 2); ctx.stroke(); ctx.strokeStyle = '#c98a3a'; ctx.beginPath(); ctx.arc(1520, 310, 30, 0, Math.PI * 2); ctx.stroke();
      // stick team
      ctx.strokeStyle = '#555'; for (const [x, s] of [[300, 1.2], [420, .9], [520, .6]]) { ctx.beginPath(); ctx.arc(x, 700 - 60 * s, 30 * s, 0, Math.PI * 2); ctx.stroke(); ctx.beginPath(); ctx.moveTo(x, 730 - 60 * s); ctx.lineTo(x, 810); ctx.stroke(); }
      const steps = [[760, 760, '1', 'slippery floor', '#3fae47'], [1050, 620, '2', 'moonbeams', '#7a4fd6'], [1440, 520, '3', 'climb!', '#e8473f']];
      steps.forEach(([x, y, n, lab, col], i) => { const on = S.planStep >= i + 1; ctx.globalAlpha = on ? 1 : .35; ctx.strokeStyle = col;
        if (i === 0) { ctx.beginPath(); for (let k = 0; k < 4; k++) { ctx.moveTo(620 + k * 70, 800); ctx.lineTo(660 + k * 70, 770); } ctx.stroke(); }
        if (i === 1) { for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.moveTo(950 + k * 50, 450); ctx.lineTo(1000 + k * 60, 800); ctx.stroke(); } }
        if (i === 2) { ctx.beginPath(); ctx.moveTo(1330, 780); ctx.lineTo(1330, 420); ctx.stroke(); }
        ell(x, y - 120, 46, 46); ctx.fillStyle = col; ctx.fill(); text(n, x, y - 118, 56, '#fff'); text(lab, x, y - 50, 40, col, { w: 800 });
        if (on && S.planStep === i + 1) { ctx.globalAlpha = .5 + .5 * Math.sin(t * 8); star(x + 60, y - 170, 18, '#ffd23f', t); }
        ctx.globalAlpha = 1; });
      ctx.lineCap = 'butt';
    }
    if (S.overlay === 'arrows') {
      for (const [dir, x] of [['left', 330], ['right', 1590]]) {
        const pick = S.arrowPick === dir, dim = S.arrowPick === 'right' && dir === 'left';
        const pulse = S.arrowPick === 'blink' ? 1 + .08 * Math.sin(t * 8) : pick ? 1.2 : 1;
        ctx.save(); ctx.translate(x, 500); ctx.scale(pulse * (dir === 'left' ? -1 : 1), pulse); ctx.globalAlpha = dim ? .3 : 1;
        ctx.fillStyle = pick ? '#3fae47' : '#ffd23f'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 10;
        ctx.beginPath(); ctx.moveTo(-120, -50); ctx.lineTo(20, -50); ctx.lineTo(20, -110); ctx.lineTo(140, 0); ctx.lineTo(20, 110); ctx.lineTo(20, 50); ctx.lineTo(-120, 50); ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.restore();
        text(dir === 'left' ? 'LEFT' : 'RIGHT', x, 660, 56, dim ? 'rgba(255,255,255,.4)' : '#fff', { stroke: 10, sc: '#1d2650' });
      }
    }
    if (S.overlay === 'sizes') {
      const labs = [['BIGGEST', 520, '#e8473f', 70], ['MIDDLE', 960, '#3d8bff', 56], ['SMALLEST', 1400, '#3fae47', 44]];
      labs.forEach(([l, x, c, s], i) => { const k = backOut((t - at('n29') - i * 1.6) / .4); if (k <= 0) return; ctx.save(); ctx.translate(x, 160); ctx.scale(k, k); rr(-190, -50, 380, 100, 50); ctx.fillStyle = c; ctx.fill(); text(l, 0, 2, s, '#fff'); ctx.restore(); });
    }
    if (S.overlay === 'please' || S.overlay === 'thanks') {
      const k = backOut((t - at(S.overlay === 'please' ? 'p1' : 'p2')) / .4); ctx.save(); ctx.translate(960, 200); ctx.scale(k, k);
      rr(-330, -70, 660, 140, 70); ctx.fillStyle = S.overlay === 'please' ? '#ff6fa8' : '#3fae47'; ctx.fill(); text(S.overlay === 'please' ? 'Please!' : 'Thank you!', 0, 4, 80, '#fff');
      heart(-380, 0, 1.8, '#ff5d8f'); heart(380, 0, 1.8, '#ff5d8f'); ctx.restore();
    }
  }

  window.renderFrame = function (t) {
    const { cam, cast, S } = direct(t);
    ctx = MAIN; ctx.save(); ctx.fillStyle = '#1d2650'; ctx.fillRect(0, 0, W, H);
    const shx = cam.shake ? (Math.random() - .5) * cam.shake : 0;
    ctx.translate(W / 2 + shx, H / 2); ctx.scale(cam.z, cam.z); ctx.translate(-cam.cx, -cam.cy);
    drawSets(t, cam);
    if (S.beams) drawMoonbeams(t, S.beamGlow);
    for (const p of S.props) if (p[0] === 'paper') { ctx.save(); ctx.translate(p[1], p[2]); ctx.scale(1, .3); ctx.fillStyle = '#fdf8ec'; rr(-220, -160, 440, 320, 10); ctx.fill(); ctx.restore(); }
    if (S.vac && S.vac.behind) drawVacuum(S.vac, t);
    // contact shadows
    for (const o of cast) { const s = o.sc || 1, w = o.spk === 'MOC' ? 150 : o.spk === 'BUB' ? 90 : 60; ctx.fillStyle = rgrad(o.x, Math.min(o.y, FLOOR + 60) + 4, 3, w * s, [[0, 'rgba(10,10,30,.35)'], [1, 'rgba(10,10,30,0)']]); ell(o.x, Math.max(o.y, FLOOR - 10) + 4, w * s, 18 * s); ctx.fill(); }
    // characters on a lit layer
    const tf = MAIN.getTransform();
    ctx = LAYER; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); ctx.setTransform(tf);
    const order = { MOC: 0, BUB: 1, NIB: 2 };
    [...cast].sort((a, b) => (a.y - b.y) * .01 + order[a.spk] - order[b.spk]).forEach((o) => DRAW[o.spk](o, t));
    if (S.vac && !S.vac.behind) drawVacuum(S.vac, t);
    if (S.lily) drawLilyLegs(S.lily, t);
    if (S.lilySit) drawLilySitting(S.lilySit, t);
    if (S.hand) drawLilyHand(S.hand.x + 40, FLOOR - 260, S.hand.item, t);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalCompositeOperation = 'source-atop';
    const night = T._night ?? 1;
    for (const o of cast) { const z = cam.z * (o.sc || 1), sx = (o.x - cam.cx) * cam.z + W / 2, sy = (o.y - cam.cy) * cam.z + H / 2;
      ctx.fillStyle = rgrad(sx - 60 * z, sy - 220 * z, 8, sx > 0 ? 300 * z : 300, [[0, night > .5 ? 'rgba(200,220,255,.25)' : 'rgba(255,245,220,.30)'], [1, 'rgba(255,255,255,0)']]); ctx.fillRect(sx - 450 * z, sy - 700 * z, 900 * z, 800 * z); }
    if (night > 0) { ctx.fillStyle = `rgba(30,40,110,${.28 * night})`; ctx.fillRect(0, 0, W, H); }
    ctx.globalCompositeOperation = 'source-over';
    RIM.globalCompositeOperation = 'source-over'; RIM.clearRect(0, 0, W, H); RIM.drawImage(LAYER.canvas, 0, 0);
    RIM.globalCompositeOperation = 'source-in'; RIM.fillStyle = night > .5 ? 'rgba(200,225,255,.95)' : 'rgba(255,248,220,.9)'; RIM.fillRect(0, 0, W, H);
    RIM.globalCompositeOperation = 'destination-out'; RIM.drawImage(LAYER.canvas, -5 * cam.z, 5 * cam.z);
    ctx = MAIN; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.shadowColor = 'rgba(10,10,40,.25)'; ctx.shadowBlur = 22; ctx.shadowOffsetX = -8; ctx.shadowOffsetY = 10; ctx.drawImage(LAYER.canvas, 0, 0); ctx.shadowColor = 'transparent';
    ctx.globalAlpha = .7; ctx.drawImage(RIM.canvas, 0, 0); ctx.restore();
    // world-space FX on top
    for (const p of S.props) {
      if (p[0] === 'sparkle') for (let i = 0; i < 6; i++) star(p[1] + Math.cos(t * 4 + i) * 120, p[2] + Math.sin(t * 4 + i) * 60, 14, '#ffd23f', t * 3);
      if (p[0] === 'dizzy') for (let i = 0; i < 4; i++) star(p[1] + Math.cos(t * 6 + i * 1.57) * 60, p[2] + Math.sin(t * 6 + i * 1.57) * 18, 14, '#ffd23f', t * 4);
      if (p[0] === 'notes') for (let i = 0; i < 4; i++) { const q = (t * .5 + i / 4) % 1; ctx.globalAlpha = Math.sin(q * Math.PI); text('♪', p[1] - 300 + i * 200, p[2] - q * 150, 60, '#ffd23f', { w: 700 }); ctx.globalAlpha = 1; }
      if (p[0] === 'cookieFly') drawCookie(p[1], p[2], .9, p[3]);
      if (p[0] === 'burp') { const k = p[3]; ctx.strokeStyle = `rgba(255,255,255,${1 - k})`; ctx.lineWidth = 4; ell(p[1], p[2] - k * 60, 14 + k * 30, 14 + k * 30); ctx.stroke(); if (k > .85) for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; ell(p[1] + Math.cos(a) * 50, p[2] - 60 + Math.sin(a) * 50, 4, 4); ctx.fillStyle = '#fff'; ctx.fill(); } }
    }
    if (S.confetti) for (let i = 0; i < 60; i++) { const q = (t * .25 + hash(i)) % 1; ctx.fillStyle = ['#ff6fa8', '#ffd23f', '#3d8bff', '#3fae47', '#ff8a1f'][i % 5]; ctx.save(); ctx.translate(cam.cx - 1000 + hash(i + 3) * 2000, cam.cy - 700 + q * 1400); ctx.rotate(t * 3 + i); ctx.fillRect(-8, -4, 16, 8); ctx.restore(); }
    if (S.speed) { ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.lineWidth = 5; for (let i = 0; i < 10; i++) { const y = cam.cy - 400 + hash(i) * 800, x = cam.cx - 900 + ((t * 1800 + hash(i + 1) * 2000) % 1800); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 160, y); ctx.stroke(); } }
    ctx.restore();
    // grade: night blue or warm, vignette
    ctx.save(); ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = (T._night ?? 1) > .5 ? 'rgba(90,120,220,.25)' : 'rgba(255,190,140,.18)'; ctx.fillRect(0, 0, W, H); ctx.restore();
    ctx.fillStyle = rgrad(W / 2, H / 2, 480, 1150, [[0, 'rgba(10,10,40,0)'], [1, `rgba(10,10,40,${S.silence ? .5 : .3})`]]); ctx.fillRect(0, 0, W, H);
    overlay(t, S);
    // end card
    if (t >= T.end - 6.5) {
      const k = ss(T.end - 6.5, T.end - 6, t); ctx.fillStyle = `rgba(255,248,230,${.92 * k})`; ctx.fillRect(0, 0, W, H);
      const b = backOut((t - T.end + 6.5) / .5); ctx.save(); ctx.translate(960, 330); ctx.scale(b, b);
      text("Today's Lesson", 0, -90, 64, '#ff6f3c', { stroke: 14 }); heart(-560, 30, 2, '#ff5d8f'); heart(560, 30, 2, '#ff5d8f');
      text("It's better to ask", 0, 10, 84, '#3d3d8f'); text('than to sneak!', 0, 110, 84, '#3fae47'); ctx.restore();
      if (t > T.end - 5.8) { const b2 = backOut((t - T.end + 5.8) / .4); ctx.save(); ctx.translate(960, 640); ctx.scale(b2, b2); rr(-420, -55, 840, 110, 55); ctx.fillStyle = '#3d8bff'; ctx.fill(); text('See you next time, Snack Squad!', 0, 2, 46, '#fff'); ctx.restore(); }
      ctx.save(); ctx.translate(0, 0);
      drawMochi({ x: 620, y: 1040, sc: .55, mood: 'joy', pose: 'sit' }, t); drawBubbles({ x: 960, y: 1040, sc: .7, mood: 'joy', spin: t * 4 }, t); drawNibs({ x: 1280, y: 1040, sc: .9, mood: 'joy', arms: 'up', face: -1, hop: Math.abs(Math.sin(t * 5)) * 20 }, t);
      ctx.restore();
    }
  };
})();
