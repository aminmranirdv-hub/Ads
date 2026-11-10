// Pip & Pebble — Ep.2 "Amir's Big Race" — procedural 2D cartoon renderer (1920x1080).
(function () {
  const W = 1920, H = 1080, GROUND = 820;
  const START = 800, TREE = 1750, BR0 = 2350, BR1 = 2850, FINISH = 4400;
  const MAIN = document.getElementById('c').getContext('2d'); let ctx = MAIN;
  const mk = () => { const c = document.createElement('canvas'); c.width = 1920; c.height = 1080; return c.getContext('2d'); };
  const LAYER = mk(), RIM = mk();
  const T = window.T, B = T.beats;
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
  const backOut = (k) => { const s = 1.7; k = clamp(k) - 1; return k * k * ((s + 1) * k + s) + 1; };
  const hash = (n) => { const x = Math.sin(n * 91.7) * 43758.5453; return x - Math.floor(x); };
  const mouth = (spk, t) => Math.max((T['mouth_' + spk] || [])[Math.floor(t * T.fps)] || 0, (T.mouth_ALL || [])[Math.floor(t * T.fps)] || 0);
  const at = (k, i = 0) => T[k][i];
  const inB = (b, t) => t >= B[b][0] - 0.4 && t < B[b][1];
  function ell(x, y, rx, ry, r = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(.1, rx), Math.max(.1, ry), r, 0, Math.PI * 2); }
  function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
  function text(s, x, y, size, col, o = {}) {
    ctx.save(); ctx.font = `${o.w || 800} ${size}px Inter, "DejaVu Sans", sans-serif`;
    ctx.textAlign = o.a || 'center'; ctx.textBaseline = 'middle';
    if (o.stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = o.stroke; ctx.strokeStyle = o.sc || '#fff'; ctx.strokeText(s, x, y); }
    ctx.fillStyle = col; ctx.fillText(s, x, y); ctx.restore();
  }
  function heart(x, y, s, col) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(0, 12); ctx.bezierCurveTo(-26, -6, -14, -30, 0, -14); ctx.bezierCurveTo(14, -30, 26, -6, 0, 12); ctx.fill(); ctx.restore(); }
  function star(x, y, r, col, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.fillStyle = col; ctx.beginPath(); for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5 - Math.PI / 2, rad = i % 2 ? r * .45 : r; ctx.lineTo(Math.cos(a) * rad, Math.sin(a) * rad); } ctx.closePath(); ctx.fill(); ctx.restore(); }
  function eyes(xs, y, o, t, size = 1) { // shared cartoon eyes
    const blink = ((t + (o.seed || 0)) % 3.7) < 0.12;
    for (const ex of xs) {
      if (blink || o.mood === 'joy') { ctx.beginPath(); ctx.lineWidth = 5; ctx.arc(ex, y + 2, 12 * size, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); ctx.lineWidth = 3.5; continue; }
      const big = o.mood === 'shock' ? 1.25 : 1;
      ell(ex, y, 13 * size * big, 17 * size * big); { const eg = ctx.createRadialGradient(ex, y + 6 * size, 2, ex, y, 17 * size * big); eg.addColorStop(0, '#5a3a2a'); eg.addColorStop(1, '#1a100c'); ctx.fillStyle = eg; } ctx.fill(); ell(ex + 5 * size, y + 7 * size, 3 * size, 3 * size); ctx.fillStyle = 'rgba(255,255,255,.8)'; ctx.fill();
      ell(ex - 4 * size + (o.look || 0) * 3, y - 6 * size + (o.lookY || 0) * 3, 5 * size, 6 * size); ctx.fillStyle = '#fff'; ctx.fill();
      if (o.mood === 'sad' || o.mood === 'worry' || o.mood === 'sorry') { ctx.beginPath(); const L = ex === xs[0]; ctx.moveTo(ex - 14 * size, y - 26 * size + (L ? 6 : -2)); ctx.lineTo(ex + 14 * size, y - 26 * size + (L ? -2 : 6)); ctx.stroke(); }
      if (o.mood === 'proud' || o.mood === 'brave') { ctx.beginPath(); const L = ex === xs[0]; ctx.moveTo(ex - 14 * size, y - 26 * size + (L ? -4 : 4)); ctx.lineTo(ex + 14 * size, y - 26 * size + (L ? 4 : -4)); ctx.stroke(); }
    }
  }
  function mouthShape(x, y, o, w = 10) {
    const m = o.mouth || 0; ctx.lineWidth = 4;
    if (m > 0.08) { ell(x, y + m * 4, w + m * 5, 3 + m * 12); ctx.fillStyle = '#7a2238'; ctx.fill(); ell(x, y + 4 + m * 8, w * .7, 2 + m * 4); ctx.fillStyle = '#ff8fa3'; ctx.fill(); }
    else { ctx.beginPath(); if (['sad', 'worry', 'sorry'].includes(o.mood)) ctx.arc(x, y + 8, w * .9, Math.PI * 1.15, Math.PI * 1.85); else ctx.arc(x, y - 6, w, 0.25, Math.PI - 0.25); ctx.stroke(); }
  }
  const legSwing = (o, t, ph = 0) => o.run ? Math.sin(t * 16 + ph) : (o.walk ? Math.sin(t * 7 + ph) * 0.6 : 0);

  // ---------------- world ----------------
  function groundY(x) { return GROUND + Math.sin(x / 260) * 5; }
  function drawWorld(t, cam, S) {
    const g = ctx.createLinearGradient(0, -200, 0, 800);
    g.addColorStop(0, S.sad ? '#9fb4c9' : '#7cc8f5'); g.addColorStop(1, S.sad ? '#d5dde6' : '#d8f1ff');
    const L = cam.cx - 1400, R = cam.cx + 1400;
    ctx.fillStyle = g; ctx.fillRect(L, -600, R - L, 1800);
    // parallax far layers (drawn relative to camera), softly blurred for depth
    ctx.filter = 'blur(3px)';
    ctx.save(); ctx.translate(cam.cx * 0.85, 0);
    { const gl = ctx.createRadialGradient(-700, 150, 40, -700, 150, 470); gl.addColorStop(0, 'rgba(255,240,180,.75)'); gl.addColorStop(1, 'rgba(255,240,180,0)'); ctx.fillStyle = gl; ctx.fillRect(-1180, -330, 960, 960); }
    ctx.save(); ctx.translate(-700, 150); ctx.rotate(t * .15); ctx.fillStyle = 'rgba(255,214,90,.35)';
    for (let i = 0; i < 12; i++) { ctx.rotate(Math.PI / 6); ctx.beginPath(); ctx.moveTo(0, -95); ctx.lineTo(18, -150); ctx.lineTo(-18, -150); ctx.fill(); }
    ctx.restore(); ell(-700, 150, 80, 80); ctx.fillStyle = '#ffd84d'; ctx.fill();
    ctx.restore();
    ctx.save(); ctx.translate(cam.cx * 0.6, 0);
    for (let i = 0; i < 6; i++) { const cx = ((i * 700 + t * 18) % 4200) - 2100 - cam.cx * 0.0, cy = 100 + (i % 2) * 90; ctx.fillStyle = 'rgba(255,255,255,.95)';
      ell(cx, cy, 90, 42); ctx.fill(); ell(cx - 60, cy + 10, 60, 32); ctx.fill(); ell(cx + 65, cy + 12, 64, 30); ctx.fill(); ell(cx + 10, cy - 28, 55, 38); ctx.fill(); }
    ctx.restore();
    ctx.save(); ctx.translate(cam.cx * 0.5, 0); const l2 = -cam.cx * 0.5 + L;
    ctx.fillStyle = '#a5dc86'; ctx.beginPath(); ctx.moveTo(l2 - 200, 1100);
    for (let x = l2 - 200; x <= l2 + 3200; x += 40) ctx.lineTo(x, 630 + Math.sin(x / 210) * 45 + Math.sin(x / 90) * 10);
    ctx.lineTo(l2 + 3200, 1100); ctx.fill(); ctx.restore();
    ctx.save(); ctx.translate(cam.cx * 0.25, 0); const l3 = -cam.cx * 0.25 + L;
    ctx.fillStyle = '#8fd16f'; ctx.beginPath(); ctx.moveTo(l3 - 200, 1100);
    for (let x = l3 - 200; x <= l3 + 3200; x += 40) ctx.lineTo(x, 712 + Math.sin(x / 150 + 1) * 30);
    ctx.lineTo(l3 + 3200, 1100); ctx.fill(); ctx.restore();
    ctx.filter = 'none';
    { const hz = ctx.createLinearGradient(0, 560, 0, 800); hz.addColorStop(0, 'rgba(230,245,255,0)'); hz.addColorStop(1, 'rgba(230,245,255,.25)'); ctx.fillStyle = hz; ctx.fillRect(L, 560, R - L, 260); }
    // ground
    ctx.fillStyle = '#6cc04a'; ctx.beginPath(); ctx.moveTo(L, 1300);
    for (let x = L; x <= R; x += 12) ctx.lineTo(x, (x > BR0 + 30 && x < BR1 - 30) ? 1300 : groundY(x));
    ctx.lineTo(R, 1300); ctx.fill();
    { const gg = ctx.createLinearGradient(0, 820, 0, 1200); gg.addColorStop(0, '#7fd05a'); gg.addColorStop(1, '#3f8f2c'); ctx.fillStyle = gg; ctx.fillRect(L, 870, BR0 + 30 - L, 430); ctx.fillRect(BR1 - 30, 870, R - BR1 + 30, 430);
      ctx.fillStyle = 'rgba(255,255,255,.05)'; for (let x = Math.floor(L / 160) * 160; x < R; x += 320) { if (x > BR0 - 160 && x < BR1) continue; ctx.beginPath(); ctx.moveTo(x, 870); ctx.lineTo(x + 160, 870); ctx.lineTo(x + 260, 1300); ctx.lineTo(x + 100, 1300); ctx.fill(); } }
    // stream under the bridge
    const sg = ctx.createLinearGradient(0, 860, 0, 1100); sg.addColorStop(0, '#5ec6e8'); sg.addColorStop(1, '#2f8fc2');
    ctx.fillStyle = sg; ctx.fillRect(BR0 + 30, 880, BR1 - BR0 - 60, 400);
    ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 4;
    for (let i = 0; i < 6; i++) { const x = BR0 + 60 + ((i * 90 + t * 60) % (BR1 - BR0 - 140)); ctx.beginPath(); ctx.moveTo(x, 930 + i % 3 * 40); ctx.lineTo(x + 40, 930 + i % 3 * 40); ctx.stroke(); }
    // grass + flowers
    for (let x = Math.floor(L / 37) * 37; x < R; x += 37) { if (x > BR0 && x < BR1) continue; const y = groundY(x) + 4; ctx.strokeStyle = '#3f8f2c'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 6, y - 16 - Math.sin(t * 2 + x) * 2); ctx.moveTo(x, y); ctx.lineTo(x + 6, y - 14); ctx.stroke(); }
    const fc = ['#ff6fa8', '#ffd23f', '#ffffff', '#b07cff'];
    for (let i = Math.floor(L / 90); i < R / 90; i++) { const x = i * 90 + hash(i) * 60; if (x > BR0 - 20 && x < BR1 + 20) continue; const y = groundY(x) + 30 + hash(i + 7) * 120;
      ctx.fillStyle = fc[Math.abs(i) % 4]; for (let p = 0; p < 5; p++) { const a = p * 1.256; ell(x + Math.cos(a) * 9, y + Math.sin(a) * 9, 7, 7); ctx.fill(); } ell(x, y, 6, 6); ctx.fillStyle = '#ff9f1c'; ctx.fill(); }
    // Abdelhamid's stump
    ctx.fillStyle = '#8a5a3b'; rr(420, 700, 160, 130, 18); ctx.fill(); ell(500, 700, 80, 22); ctx.fillStyle = '#c58b5e'; ctx.fill();
    // start line
    ctx.fillStyle = '#fff'; ctx.fillRect(START - 8, 790, 16, 120);
    for (const fx of [START - 260, START + 260]) { ctx.fillStyle = '#7a5a3a'; ctx.fillRect(fx - 6, 560, 12, 260); ctx.fillStyle = '#ff5d5d'; ctx.beginPath(); ctx.moveTo(fx + 6, 565); ctx.lineTo(fx + 90 + Math.sin(t * 5) * 8, 590); ctx.lineTo(fx + 6, 620); ctx.fill(); }
    text('START', START, 540, 46, '#ff6f3c', { stroke: 10 });
    // big apple tree
    ctx.fillStyle = '#8a5a3b'; rr(TREE - 40, 470, 80, 360, 26); ctx.fill(); ctx.fillStyle = '#4fae4f';
    for (const [x, y, r] of [[0, 420, 170], [-120, 500, 120], [125, 500, 125], [0, 300, 130]]) { ell(TREE + x + Math.sin(t + x) * 3, y, r, r * .9); ctx.fill(); }
    ctx.fillStyle = '#e8473f'; for (const [x, y] of [[-60, 420], [60, 380], [110, 520], [-130, 540], [10, 300], [-20, 470]]) { ell(TREE + x, y, 15, 15); ctx.fill(); }
    // bridge
    ctx.fillStyle = '#a0703f'; for (let x = BR0; x < BR1; x += 42) { rr(x, 812, 38, 22, 4); ctx.fill(); }
    ctx.strokeStyle = '#7a5530'; ctx.lineWidth = 10; ctx.beginPath(); ctx.moveTo(BR0, 760); ctx.quadraticCurveTo((BR0 + BR1) / 2, 720, BR1, 760); ctx.stroke();
    for (let x = BR0; x <= BR1; x += 125) { ctx.beginPath(); ctx.moveTo(x, 812); ctx.lineTo(x, 745); ctx.stroke(); }
    // finish line (built by Hicham)
    drawFinish(t, S);
  }
  function drawFinish(t, S) {
    const k = S.build ?? 1; if (k <= 0) return;
    const p0 = FINISH - 200, p1 = FINISH + 200, top = 560;
    ctx.fillStyle = '#7a5a3a'; for (const px of [p0, p1]) { const h = 260 * Math.min(1, k * 2); ctx.fillRect(px - 9, 820 - h, 18, h); ctx.fillStyle = '#4fae4f'; ell(px, 820 - h, 26, 18); ctx.fill(); ctx.fillStyle = '#7a5a3a'; }
    if (k > 0.5) text('FINISH', FINISH, 470, 54, '#3d8bff', { stroke: 10 });
    const rk = clamp((k - 0.5) * 2);
    if (S.ribbon === 'cut') { ctx.strokeStyle = '#e8262e'; ctx.lineWidth = 14; for (const [a, d] of [[p0, 1], [p1, -1]]) { ctx.beginPath(); ctx.moveTo(a, 600); ctx.quadraticCurveTo(a + d * 60, 700, a + d * 30 + Math.sin(t * 4) * 10, 760); ctx.stroke(); } }
    else if (S.ribbon !== 'gone' && rk > 0) { ctx.strokeStyle = '#e8262e'; ctx.lineWidth = 14; ctx.beginPath(); ctx.moveTo(p0, 600); ctx.quadraticCurveTo(FINISH, 630 + Math.sin(t * 3) * 6, lerp(p0, p1, rk), 600); ctx.stroke(); }
  }

  // ---------------- characters (origin = feet) ----------------
  function begin(o) { ctx.save(); ctx.translate(o.x, o.y - (o.hop || 0)); ctx.rotate(o.rot || 0); ctx.scale((o.face || 1) * (o.sc || 1), o.sc || 1); ctx.lineWidth = 3.5; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; }
  function drawPip(o, t) {
    begin(o); const OUT = '#c4977a', FUR = '#f7e6d4'; ctx.strokeStyle = OUT;
    if (o.ribbonBadge) { }
    ell(-58, -80, 24, 22); ctx.fillStyle = '#fff'; ctx.fill(); ctx.stroke();
    const sw = legSwing(o, t);
    ell(-28 + sw * 18, -8 - Math.max(0, sw) * 14, 30, 14); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke(); ell(30 - sw * 18, -8 - Math.max(0, -sw) * 14, 30, 14); ctx.fill(); ctx.stroke();
    ell(0, -85, 58, 66); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke(); ell(8, -78, 36, 44); ctx.fillStyle = '#fffaf2'; ctx.fill();
    ctx.fillStyle = '#3d8bff'; rr(-48, -150, 96, 26, 13); ctx.fill(); ctx.stroke();
    ctx.save(); ctx.translate(-30, -132); ctx.rotate(0.5 + Math.sin(t * 6) * .15 + (o.run ? 0.8 : 0)); rr(-12, 0, 24, 46, 10); ctx.fill(); ctx.stroke(); ctx.restore();
    const droop = o.ears || (o.run ? 0.5 : 0);
    for (const sd of [-1, 1]) { ctx.save(); ctx.translate(sd * 26, -250); ctx.rotate(sd * (0.12 + droop * 1.1) - (o.run ? 0.5 : 0) + Math.sin(t * 4 + sd) * .04); ell(0, -60, 22, 66); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke(); ell(0, -56, 11, 50); ctx.fillStyle = '#ffb3c6'; ctx.fill(); ctx.restore(); }
    ell(0, -205, 72, 64); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke();
    eyes([-4, 34], -212, o, t);
    ctx.fillStyle = 'rgba(255,120,150,.45)'; ell(-28, -185, 14, 9); ctx.fill(); ell(58, -185, 13, 9); ctx.fill();
    ctx.fillStyle = '#ff7f9e'; ell(18, -192, 9, 7); ctx.fill(); ctx.strokeStyle = OUT; mouthShape(18, -172, o);
    const arms = o.arms || 'down', ap = arms === 'up' ? [[-38, -175], [42, -175]] : arms === 'out' ? [[-62, -110], [66, -110]] : [[-46 - sw * 14, -78], [52 + sw * 14, -78]];
    ctx.fillStyle = FUR; ctx.lineWidth = 3.5; for (const [ax, ay] of ap) { ell(ax, ay, 16, 20); ctx.fill(); ctx.stroke(); }
    badge(o, 0, -120); ctx.restore();
  }
  function drawPebble(o, t) {
    begin(o); ctx.strokeStyle = '#4a9a44';
    if (o.flipped) { ctx.translate(0, -70); ctx.rotate(Math.PI); ctx.translate(0, 40); }
    const step = o.flipped ? Math.sin(t * 14) * 1.5 : legSwing(o, t);
    ctx.fillStyle = '#a8e08a';
    for (const [lx, ph] of [[-70, 1], [-25, -1], [35, 1], [75, -1]]) { ell(lx + step * ph * 6, -14 - Math.max(0, step * ph) * 6, 20, 16); ctx.fill(); ctx.stroke(); }
    ctx.beginPath(); ctx.moveTo(-118, -40); ctx.lineTo(-140, -30); ctx.lineTo(-116, -24); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(0, -40, 120, 92, 0, Math.PI, 0); ctx.closePath();
    const g = ctx.createRadialGradient(-30, -100, 10, 0, -50, 140); g.addColorStop(0, '#7fd36e'); g.addColorStop(1, '#3f9a3a'); ctx.fillStyle = g; ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#9be38a';
    for (const [hx, hy, r] of [[0, -90, 26], [-55, -70, 20], [55, -70, 20], [-30, -112, 14], [30, -112, 14]]) { ctx.beginPath(); for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; ctx.lineTo(hx + Math.cos(a) * r, hy + Math.sin(a) * r * .8); } ctx.closePath(); ctx.fill(); }
    ctx.fillStyle = '#e6d27a'; rr(-122, -48, 244, 16, 8); ctx.fill(); ctx.stroke();
    const hx = 128, hy = -70 - (o.headUp || 0) * 18;
    ctx.fillStyle = '#a8e08a'; ell(100, -55, 26, 22); ctx.fill(); ell(hx, hy, 46, 42); ctx.fill(); ctx.stroke();
    eyes([hx - 6, hx + 22], hy - 8, { ...o, seed: 0.4 }, t, 0.85);
    ctx.fillStyle = 'rgba(255,130,150,.5)'; ell(hx - 18, hy + 12, 9, 6); ctx.fill(); ell(hx + 36, hy + 12, 8, 6); ctx.fill();
    ctx.strokeStyle = '#4a9a44'; mouthShape(hx + 10, hy + 22, o, 9);
    badge(o, 0, -60); ctx.restore();
  }
  function drawAziza(o, t) { // giraffe
    begin(o); ctx.strokeStyle = '#c98a3a'; const Y = '#ffcf4a', SP = '#d9822b'; const sw = legSwing(o, t);
    ctx.fillStyle = Y;
    for (const [lx, ph] of [[-60, 1], [-30, -1], [40, 1], [70, -1]]) { ctx.save(); ctx.translate(lx, -230); ctx.rotate(sw * ph * 0.25); rr(-11, 0, 22, 225, 10); ctx.fill(); ctx.stroke(); ctx.fillStyle = '#c98a3a'; rr(-12, 210, 24, 20, 6); ctx.fill(); ctx.fillStyle = Y; ctx.restore(); }
    ell(5, -260, 110, 62); ctx.fill(); ctx.stroke();
    ctx.fillStyle = SP; for (const [sx, sy, r] of [[-50, -270, 18], [10, -250, 22], [60, -275, 16], [-15, -290, 12]]) { ell(sx, sy, r, r * .8); ctx.fill(); }
    // neck
    const lean = Math.sin(t * 1.2) * 0.04 + (o.neckBend || 0);
    ctx.save(); ctx.translate(70, -290); ctx.rotate(0.15 + lean);
    ctx.fillStyle = Y; rr(-24, -250, 48, 260, 22); ctx.fill(); ctx.stroke();
    ctx.fillStyle = SP; for (let i = 0; i < 4; i++) { ell(i % 2 ? 8 : -6, -40 - i * 52, 12, 10); ctx.fill(); }
    ctx.fillStyle = '#c4672a'; rr(-30, -240, 10, 200, 5); ctx.fill();
    // head
    ctx.translate(20, -270);
    ctx.fillStyle = '#c98a3a'; for (const hx of [-20, 12]) { rr(hx, -70, 10, 40, 5); ctx.fill(); ell(hx + 5, -72, 10, 10); ctx.fill(); }
    ctx.fillStyle = Y; ell(0, 0, 58, 46); ctx.fill(); ctx.stroke(); ell(38, 18, 34, 26); ctx.fillStyle = '#ffe08a'; ctx.fill(); ctx.stroke();
    ctx.fillStyle = Y; ctx.save(); ctx.translate(-48, -22); ctx.rotate(-0.6); ell(0, 0, 26, 12); ctx.fill(); ctx.stroke(); ctx.restore();
    for (let p = 0; p < 5; p++) { const a = p * 1.256; ctx.fillStyle = '#ff6fa8'; ell(-60 + Math.cos(a) * 9, -34 + Math.sin(a) * 9, 7, 7); ctx.fill(); } ell(-60, -34, 6, 6); ctx.fillStyle = '#fff'; ctx.fill();
    ctx.strokeStyle = '#8a5a2a'; eyes([-4, 24], -8, { ...o, seed: 1.7 }, t, 0.75);
    ctx.lineWidth = 3; for (const ex of [-4, 24]) for (let l = -1; l <= 1; l++) { ctx.beginPath(); ctx.moveTo(ex + l * 7, -22); ctx.lineTo(ex + l * 10, -30); ctx.stroke(); }
    ctx.fillStyle = 'rgba(255,120,150,.5)'; ell(-18, 14, 10, 6); ctx.fill();
    ctx.strokeStyle = '#c98a3a'; mouthShape(44, 30, o, 9);
    ctx.restore();
    // tail
    ctx.strokeStyle = '#c98a3a'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(-100, -280); ctx.quadraticCurveTo(-130, -230, -125 + Math.sin(t * 3) * 10, -190); ctx.stroke();
    badge(o, 0, -250); ctx.restore();
  }
  function drawAbdelhamid(o, t) { // owl
    begin(o); ctx.strokeStyle = '#8a6040'; const BR = '#9b6a43';
    const flap = o.fly ? Math.sin(t * 18) : 0;
    ctx.fillStyle = '#e8a33a'; ell(-22, -6, 14, 8); ctx.fill(); ell(22, -6, 14, 8); ctx.fill();
    ctx.fillStyle = BR;
    for (const sd of [-1, 1]) { ctx.save(); ctx.translate(sd * 62, -110); ctx.rotate(sd * (0.25 + flap * 0.9) + (o.point && sd === 1 ? -1.2 : 0)); ell(sd * 6, 30, 26, 58); ctx.fill(); ctx.stroke(); ctx.restore(); }
    ell(0, -105, 78, 98); ctx.fill(); ctx.stroke(); ell(0, -80, 52, 62); ctx.fillStyle = '#e9d2b0'; ctx.fill();
    ctx.strokeStyle = '#b89a72'; ctx.lineWidth = 3; for (let r = 0; r < 3; r++) for (let c = -1; c <= 1; c++) { ctx.beginPath(); ctx.arc(c * 22, -100 + r * 22, 8, 0.2, Math.PI - 0.2); ctx.stroke(); }
    ctx.lineWidth = 3.5; ctx.strokeStyle = '#8a6040';
    ctx.fillStyle = '#3f8f4f'; ctx.beginPath(); ctx.moveTo(-62, -120); ctx.lineTo(-30, -40); ctx.lineTo(-60, -40); ctx.closePath(); ctx.fill(); ctx.beginPath(); ctx.moveTo(62, -120); ctx.lineTo(30, -40); ctx.lineTo(60, -40); ctx.closePath(); ctx.fill();
    // head tufts
    ctx.fillStyle = BR; for (const sd of [-1, 1]) { ctx.beginPath(); ctx.moveTo(sd * 30, -190); ctx.lineTo(sd * 62, -230); ctx.lineTo(sd * 60, -180); ctx.closePath(); ctx.fill(); ctx.stroke(); }
    // eyes with round glasses
    for (const ex of [-28, 28]) { ell(ex, -160, 30, 30); ctx.fillStyle = '#fff6dc'; ctx.fill(); }
    eyes([-28, 28], -160, { ...o, seed: 2.2 }, t, 1.0);
    ctx.strokeStyle = '#c9a227'; ctx.lineWidth = 6; for (const ex of [-28, 28]) { ell(ex, -160, 33, 33); ctx.stroke(); } ctx.beginPath(); ctx.moveTo(-0, -165); ctx.lineTo(0, -165); ctx.stroke();
    ctx.fillStyle = '#e8a33a'; ctx.strokeStyle = '#8a6040'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-12, -132); ctx.lineTo(12, -132); ctx.lineTo(0, -108 + (o.mouth || 0) * -6); ctx.closePath(); ctx.fill(); ctx.stroke();
    if ((o.mouth || 0) > 0.1) { ctx.beginPath(); ctx.moveTo(-9, -126 + o.mouth * 8); ctx.lineTo(9, -126 + o.mouth * 8); ctx.lineTo(0, -110 + o.mouth * 6); ctx.closePath(); ctx.fillStyle = '#c9802a'; ctx.fill(); }
    ctx.restore();
  }
  function drawAmir(o, t) { // lion cub
    begin(o); ctx.strokeStyle = '#c4822a'; const F = '#f2b84b', MANE = '#c8741e'; const sw = legSwing(o, t);
    ctx.lineWidth = 9; ctx.beginPath(); ctx.moveTo(-60, -80); ctx.quadraticCurveTo(-120, -110 + Math.sin(t * 4) * 15, -125, -160); ctx.strokeStyle = F; ctx.stroke();
    ctx.lineWidth = 3.5; ctx.strokeStyle = '#c4822a'; ell(-125, -165, 16, 18); ctx.fillStyle = MANE; ctx.fill();
    ctx.fillStyle = F; for (const [lx, ph] of [[-40, 1], [-10, -1], [25, 1], [52, -1]]) { ell(lx + sw * ph * 14, -14 - Math.max(0, sw * ph) * 10, 18, 16); ctx.fill(); ctx.stroke(); }
    ell(0, -70, 70, 52); ctx.fill(); ctx.stroke(); ell(12, -60, 34, 28); ctx.fillStyle = '#ffe2a8'; ctx.fill();
    // mane
    const hx = 30, hy = -165; ctx.fillStyle = MANE;
    for (let i = 0; i < 14; i++) { const a = i / 14 * Math.PI * 2 + Math.sin(t * 3) * 0.03; ell(hx + Math.cos(a) * 82, hy + Math.sin(a) * 78, 34, 30); ctx.fill(); }
    ell(hx, hy, 82, 78); ctx.fill();
    ctx.fillStyle = F; for (const sd of [-1, 1]) { ell(hx + sd * 50, hy - 50, 18, 18); ctx.fill(); ctx.stroke(); }
    ell(hx, hy, 60, 56); ctx.fill(); ctx.stroke();
    // leaf crown
    ctx.fillStyle = '#4fae4f'; for (let i = -2; i <= 2; i++) { ctx.save(); ctx.translate(hx + i * 18, hy - 66); ctx.rotate(i * 0.25); ell(0, -14, 9, 20); ctx.fill(); ctx.restore(); }
    ctx.fillStyle = '#e8473f'; ell(hx, hy - 82, 7, 7); ctx.fill();
    ctx.strokeStyle = '#7a4a10'; eyes([hx - 22, hx + 22], hy - 8, { ...o, seed: 0.9 }, t, 0.9);
    ell(hx, hy + 20, 26, 18); ctx.fillStyle = '#ffe2a8'; ctx.fill();
    ctx.fillStyle = '#7a3a20'; ctx.beginPath(); ctx.moveTo(hx - 10, hy + 8); ctx.lineTo(hx + 10, hy + 8); ctx.lineTo(hx, hy + 18); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = '#c4822a'; mouthShape(hx, hy + 30, o, 9);
    ctx.fillStyle = 'rgba(255,120,120,.4)'; ell(hx - 36, hy + 14, 10, 6); ctx.fill(); ell(hx + 36, hy + 14, 10, 6); ctx.fill();
    if (o.roar) { ctx.strokeStyle = 'rgba(120,80,20,.6)'; ctx.lineWidth = 6; for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(hx + 40, hy + 25, 60 + i * 30 + (t * 120 % 30), -0.6, 0.6); ctx.stroke(); } }
    badge(o, 10, -60); ctx.restore();
  }
  function drawHicham(o, t) { // squirrel
    begin(o); ctx.strokeStyle = '#a5674a'; const F = '#c9774a', TAIL = '#b5653b';
    ctx.fillStyle = TAIL; ctx.beginPath(); ctx.moveTo(-30, -40);
    ctx.bezierCurveTo(-170, -40, -170 + Math.sin(t * 3) * 10, -260, -60, -270); ctx.bezierCurveTo(-10, -275, -40, -200, -80, -210);
    ctx.bezierCurveTo(-110, -200, -100, -90, -30, -80); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.strokeStyle = 'rgba(255,220,180,.5)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(-110, -90); ctx.quadraticCurveTo(-150, -180, -90, -245); ctx.stroke();
    ctx.strokeStyle = '#a5674a'; ctx.lineWidth = 3.5; const sw = legSwing(o, t);
    ctx.fillStyle = F; ell(-14 + sw * 10, -10, 22, 12); ctx.fill(); ctx.stroke(); ell(24 - sw * 10, -10, 22, 12); ctx.fill(); ctx.stroke();
    ell(4, -70, 44, 56); ctx.fill(); ctx.stroke(); ell(12, -64, 26, 36); ctx.fillStyle = '#ffe0c2'; ctx.fill();
    ctx.fillStyle = '#5a7fa8'; rr(-40, -48, 88, 16, 6); ctx.fill(); ctx.fillStyle = '#8a5a2b'; ell(36, -36, 10, 12); ctx.fill(); ell(-20, -36, 9, 11); ctx.fill();
    ctx.fillStyle = F; ell(14, -150, 50, 46); ctx.fill(); ctx.stroke();
    for (const sd of [-1, 1]) { ctx.beginPath(); ctx.moveTo(14 + sd * 22, -186); ctx.lineTo(14 + sd * 38, -222); ctx.lineTo(14 + sd * 44, -176); ctx.closePath(); ctx.fill(); ctx.stroke(); }
    ctx.strokeStyle = '#6a3a20'; eyes([0, 30], -156, { ...o, seed: 1.1 }, t, 0.78);
    ctx.fillStyle = '#6a3a20'; ell(36, -138, 6, 5); ctx.fill();
    ctx.fillStyle = '#fff'; rr(26, -126, 9, 10, 2); ctx.fill(); rr(36, -126, 9, 10, 2); ctx.fill();
    ctx.strokeStyle = '#a5674a'; mouthShape(34, -122, o, 7);
    // arm with hammer or scissors
    const hit = o.hammer ? Math.abs(Math.sin(t * 7)) : 0;
    ctx.save(); ctx.translate(40, -90); ctx.rotate(-0.4 - hit * 1.2);
    ctx.fillStyle = F; ell(16, 0, 18, 11); ctx.fill(); ctx.stroke();
    if (o.hammer) { ctx.fillStyle = '#8a5a2b'; rr(26, -50, 9, 60, 4); ctx.fill(); ctx.fillStyle = '#7d8691'; rr(12, -64, 38, 20, 4); ctx.fill(); ctx.stroke(); }
    if (o.scissors) { ctx.strokeStyle = '#7d8691'; ctx.lineWidth = 6; const sn = Math.sin(t * 14) * 0.3; ctx.beginPath(); ctx.moveTo(30, 0); ctx.lineTo(70, -10 - sn * 20); ctx.moveTo(30, 0); ctx.lineTo(70, 10 + sn * 20); ctx.stroke(); }
    ctx.restore();
    badge(o, 10, -60); ctx.restore();
  }
  function badge(o, x, y) { if (!o.badge) return; ctx.save(); ctx.translate(x, y); ctx.scale(o.face || 1, 1); ctx.fillStyle = '#e8262e'; ctx.beginPath(); ctx.moveTo(-10, 0); ctx.lineTo(-22, 34); ctx.lineTo(-6, 26); ctx.lineTo(0, 0); ctx.moveTo(10, 0); ctx.lineTo(22, 34); ctx.lineTo(6, 26); ctx.lineTo(0, 0); ctx.fill(); ell(0, 0, 16, 16); ctx.fill(); star(0, 0, 9, '#ffd23f'); ctx.restore(); }
  const DRAW = { PIP: drawPip, PEB: drawPebble, AZI: drawAziza, ABD: drawAbdelhamid, AMI: drawAmir, HIC: drawHicham };

  // ---------------- direction ----------------
  function C(spk, x, extra = {}) { return { spk, x, y: groundY(x), face: 1, mood: 'happy', ...(spk === 'AZI' ? { sc: 0.8 } : {}), ...extra }; }
  function direct(t) {
    const cam = { cx: 960, cy: 560, z: 1 }, S = { build: 1, ribbon: 'whole', sad: false, hearts: 0, bubble: 0 };
    let cast = [];
    const m = (spk) => mouth(spk, t);
    if (t < B.intro[0] - 0.3) { // title: everyone lined up waving
      cam.cx = 1100; cam.cy = 540; cam.z = 0.95; S.build = 0;
      cast = [C('AZI', 520, { mood: 'joy' }), C('ABD', 500, { y: 700, mood: 'joy', fly: false }), C('HIC', 820, { mood: 'joy', hop: Math.abs(Math.sin(t * 5)) * 30 }), C('PIP', 1050, { mood: 'joy', arms: 'up', hop: Math.abs(Math.sin(t * 5 + 1)) * 30 }),
        C('AMI', 1300, { mood: 'joy', hop: Math.abs(Math.sin(t * 5 + 2)) * 25 }), C('PEB', 1560, { face: -1, mood: 'joy' })];
      cast[0].x = 300; cast[0].y = groundY(300);
    } else if (inB('intro', t)) {
      S.build = 0; cam.cx = 560; cam.cy = 560; cam.z = lerp(1.15, 1.6, ss(B.intro[0], B.intro[0] + 4, t));
      cast = [C('ABD', 500, { y: 700, mouth: m('ABD'), point: t > at('a2') && t < at('a2', 1) })];
    } else if (inB('build', t)) { // Hicham builds the finish line
      cam.cx = FINISH; cam.cy = 600; cam.z = 1.3;
      S.build = ss(B.build[0], at('h2', 1) + 2.5, t);
      const hammer = t > at('h2', 1) - 0.2;
      cast = [C('HIC', FINISH - 120, { mouth: m('HIC'), mood: 'joy', hammer }), C('PIP', lerp(FINISH + 700, FINISH + 180, ss(at('p1') - 1, at('p1'), t)), { face: -1, mouth: m('PIP'), hop: t < at('p1') ? Math.abs(Math.sin(t * 8)) * 50 : 0, mood: t >= at('p2') ? 'proud' : 'joy', arms: t >= at('p2') ? 'out' : 'down' })];
    } else if (inB('amir', t)) { // Amir arrives with a roar
      cam.cx = 1050; cam.cy = 600; cam.z = 1.3;
      const ax = lerp(400, 820, ss(B.amir[0] - 1.2, B.amir[0] - 0.2, t));
      cast = [C('PIP', 1180, { face: -1, mouth: m('PIP'), mood: t >= at('p3') ? 'proud' : 'shock' }),
        C('AMI', ax, { mouth: m('AMI'), mood: 'proud', roar: t < at('m1', 1), hop: t < B.amir[0] ? Math.abs(Math.sin(t * 10)) * 60 : 0 })];
    } else if (inB('pebble', t)) {
      cam.cx = 1060; cam.cy = 560; cam.z = 1.05;
      cast = [C('AZI', 1500, { face: -1, mouth: m('AZI'), mood: inB('pebble', t) && t >= at('z1') && t < at('z2') ? 'worry' : 'happy', neckBend: t >= at('z2') ? 0.25 : 0 }),
        C('PIP', 1160, { face: -1, mouth: m('PIP') }), C('AMI', 820, { mouth: m('AMI'), mood: t < at('z1') ? 'proud' : 'sorry' }),
        C('PEB', lerp(150, 560, ss(B.pebble[0] - 1, at('b1'), t)), { mouth: m('PEB'), walk: t < at('b1'), mood: (t >= at('m3') && t < at('z2')) ? 'sad' : 'happy' })];
    } else if (inB('rules', t)) {
      cam.cx = 760; cam.cy = 560; cam.z = 1.1;
      cast = [C('ABD', 500, { y: 700, mouth: m('ABD'), point: true }), C('PEB', START - 160, { mouth: m('PEB') }), C('PIP', START + 120, { mouth: m('PIP') }),
        C('AMI', START + 330, { mouth: m('AMI'), mood: t >= at('m4') ? 'proud' : 'happy' }), C('AZI', 1450, { face: -1, mouth: m('AZI') })];
    } else if (t < B.go[0] - 0.4) { // countdown close-up on runners
      cam.cx = START + 100; cam.cy = 640; cam.z = lerp(1.4, 1.9, ss(B.countdown[0], B.go[0], t));
      cast = [C('PEB', START - 160, { mood: 'brave' }), C('PIP', START + 120, { mood: 'brave', run: false }), C('AMI', START + 330, { mood: 'brave' }), C('ABD', 500, { y: 700, mouth: m('ABD') })];
    } else if (inB('go', t)) { // GO!
      const k = ss(at('a7', 1), B.go[1], t);
      const px = lerp(START + 120, START + 1300, k), ax = lerp(START + 330, START + 1250, k);
      cam.cx = lerp(START + 150, px - 100, ss(at('a7', 1), at('a7', 1) + 2, t)); cam.cy = 580; cam.z = 1.1;
      cast = [C('ABD', 500, { y: 700, mouth: m('ABD'), mood: 'joy' }), C('PEB', lerp(START - 160, START + 40, k), { walk: t > at('a7', 1), mood: 'brave' }),
        C('PIP', px, { run: t > at('a7', 1), mood: 'joy' }), C('AMI', ax, { run: t > at('a7', 1), mood: 'proud' })];
    } else if (inB('run1', t)) {
      if (t < at('p4') - 0.4 || (t >= at('b3') - 0.4 && t < at('b3', 1) + 4)) { // Pebble plodding, Aziza cheering
        const k = (t - B.run1[0]); cam.cx = START + 350; cam.cy = 560; cam.z = 1.1;
        cast = [C('AZI', START + 700, { face: -1, mouth: m('AZI'), mood: 'joy', hop: t < at('z3', 1) ? Math.abs(Math.sin(t * 6)) * 20 : 0 }), C('PEB', START + 60 + k * 9, { walk: true, mouth: m('PEB'), mood: 'brave' })];
      } else { // Pip and Amir racing neck and neck
        const k = (t - B.run1[0]) / (B.run1[1] - B.run1[0]); const px = lerp(START + 1300, TREE - 300, k);
        cam.cx = px + 50; cam.cy = 600; cam.z = 1.25;
        cast = [C('PIP', px + Math.sin(t * 1.3) * 40, { run: true, mouth: m('PIP'), mood: 'joy' }), C('AMI', px - 160 + Math.sin(t * 1.1) * 60, { run: true, mouth: m('AMI'), mood: 'proud' })];
      }
    } else if (inB('run2', t)) { // Amir passes the apple tree first
      const k = (t - B.run2[0]) / (B.run2[1] - B.run2[0]); const ax = lerp(TREE - 300, TREE + 1500, k);
      cam.cx = Math.min(ax, TREE + 600); cam.cy = 600; cam.z = 1.15;
      cast = [C('AMI', ax, { run: true, mouth: m('AMI'), mood: 'joy' }), C('PIP', ax - 190 + Math.sin(t) * 30, { run: true, mouth: m('PIP'), mood: 'proud' })];
    } else if (inB('bridge', t) || inB('fall', t)) { // Pebble on the bridge, trips, flips
      cam.cx = BR0 + 250; cam.cy = 620; cam.z = 1.35;
      const flip = t >= at('b5') + 0.4;
      const px = flip ? BR0 + 230 : lerp(BR0 - 250, BR0 + 230, ss(B.bridge[0] - 0.4, at('b5') + 0.3, t));
      cast = [C('PEB', px, { y: 820, walk: !flip, flipped: flip, mouth: m('PEB'), mood: flip ? 'worry' : 'brave', rot: (t > at('b5') && !flip) ? Math.sin(t * 20) * 0.15 : 0 })];
      S.sad = flip;
    } else if (inB('choice', t)) { // Amir stops and thinks
      cam.cx = BR1 + 700; cam.cy = 600; cam.z = lerp(1.3, 1.6, ss(B.choice[0], B.choice[1], t));
      const stop = ss(B.choice[0] - 0.4, at('m7'), t);
      cast = [C('AMI', BR1 + lerp(500, 720, stop), { run: stop < 1, mouth: m('AMI'), mood: t < at('m8') ? 'shock' : 'worry', face: t >= at('m7', 1) ? -1 : 1, look: 1 })];
      S.sad = true; S.bubble = (t >= at('a8') - 0.3 && t < at('a8', 1) + 1) ? 1 : 0;
    } else if (inB('help', t)) { // Amir runs back and helps
      cam.cx = BR0 + 330; cam.cy = 620; cam.z = 1.3;
      const arrive = ss(B.help[0] - 0.4, at('m9', 1) + 0.6, t), pushed = t >= at('m10', 1) + 0.1;
      const walk = ss(at('m11', 1), B.help[1], t);
      const peb = C('PEB', BR0 + 230 + walk * 520, { y: 820, flipped: !pushed, mouth: m('PEB'), mood: pushed ? 'joy' : 'worry', walk: walk > 0 && walk < 1 });
      const ami = C('AMI', lerp(BR1 + 300, BR0 + 470, arrive) + walk * 520, { y: 820, face: walk > 0 ? 1 : -1, run: arrive < 1, walk: walk > 0 && walk < 1, mouth: m('AMI'), mood: pushed ? 'joy' : 'brave' });
      if (!pushed && t > at('m10')) ami.rot = Math.sin(t * 12) * 0.08;
      if (t >= at('m10', 1) + 0.1 && t < at('m10', 1) + 0.5) peb.hop = Math.sin((t - at('m10', 1)) * 8) * 60;
      cast = [peb, ami]; S.sad = !pushed; S.hearts = walk > 0 ? 0.5 : 0;
      if (walk > 0) cam.cx = BR0 + 330 + walk * 520;
    } else if (inB('finish', t)) { // Pip wins alone
      cam.cx = FINISH; cam.cy = 600; cam.z = 1.3;
      const cross = ss(B.finish[0] - 0.6, at('p6') - 0.1, t);
      S.ribbon = cross >= 1 ? 'cut' : 'whole';
      cast = [C('PIP', lerp(FINISH - 700, FINISH + 120, cross), { run: cross < 1, mouth: m('PIP'), mood: t >= at('p7') ? 'worry' : 'joy', arms: t < at('p7') && cross >= 1 ? 'up' : 'down', hop: cross >= 1 && t < at('p7') ? Math.abs(Math.sin(t * 7)) * 40 : 0, face: t >= at('p7') ? -1 : 1, look: t >= at('p7') ? Math.sin(t * 2) : 0 }),
        C('HIC', FINISH + 420, { face: -1, mood: 'joy' }), C('AZI', FINISH + 700, { face: -1, mood: 'happy' })];
    } else if (inB('together', t)) { // Amir and Pebble cross together
      cam.cx = FINISH - 150; cam.cy = 580; cam.z = 1.05; S.ribbon = 'cut';
      const k = ss(B.together[0], at('h3', 1) + 4, t);
      cast = [C('PIP', FINISH + 180, { face: -1, mood: 'shock' }), C('HIC', FINISH + 420, { face: -1, mouth: m('HIC'), mood: 'joy', hop: t > at('h3') ? Math.abs(Math.sin(t * 6)) * 30 : 0 }), C('AZI', FINISH + 700, { face: -1, mouth: m('AZI'), mood: 'joy' }),
        C('PEB', lerp(FINISH - 950, FINISH - 140, k), { walk: k < 1, mood: 'joy' }), C('AMI', lerp(FINISH - 760, FINISH + 40, k), { walk: k < 1, mood: 'joy' })];
      S.hearts = 0.5;
    } else if (inB('talk', t) || inB('ribbon', t)) {
      cam.cx = FINISH + 150; cam.cy = 560; cam.z = 1.1; S.ribbon = 'cut';
      const giving = ss(at('h4', 1), at('h4', 1) + 7, t);
      const scissors = t >= at('h4') && t < at('h4', 1) + 3;
      if (t > at('h4', 1) + 1) S.ribbon = 'gone';
      const got = (i) => giving > (i + 1) / 6;
      cast = [C('PEB', FINISH - 260, { mouth: m('PEB'), badge: got(0), mood: t >= at('p9') && t < at('b8') ? 'happy' : 'joy' }), C('AMI', FINISH + 20, { mouth: m('AMI'), badge: got(4), mood: 'happy' }),
        C('PIP', FINISH + 250, { face: -1, mouth: m('PIP'), badge: got(1), mood: (t >= at('p9') && t < at('b8', 1)) ? 'sorry' : (t >= at('p8') && t < at('p8', 1) ? 'shock' : 'happy'), ears: (t >= at('p9') && t < at('b8')) ? 0.8 : 0 }),
        C('HIC', FINISH + 470, { face: -1, mouth: m('HIC'), scissors, badge: got(2), mood: 'joy' }), C('AZI', FINISH + 720, { face: -1, mouth: m('AZI'), badge: got(3), neckBend: t >= at('z5') && t < at('z5', 1) + 1 ? -0.35 : 0 })];
      if (t >= at('z5')) { S.hearts = 0.7; }
    } else { // lesson + goodbye
      const fly = ss(B.lesson[0] - 0.4, B.lesson[0] + 1.6, t);
      cam.cx = FINISH + 200; cam.cy = 520; cam.z = 1.0; S.ribbon = 'gone';
      cast = [C('PEB', FINISH - 300, { badge: true, mood: 'joy', mouth: m('PEB') }), C('AMI', FINISH - 30, { badge: true, mood: 'joy', mouth: m('AMI'), hop: t > B.end[0] ? Math.abs(Math.sin(t * 6)) * 25 : 0 }),
        C('PIP', FINISH + 230, { badge: true, mood: 'joy', mouth: m('PIP'), arms: t > B.end[0] ? 'up' : 'down', hop: t > B.end[0] ? Math.abs(Math.sin(t * 6 + 1)) * 30 : 0 }),
        C('HIC', FINISH + 460, { face: -1, badge: true, mood: 'joy', mouth: m('HIC') }), C('AZI', FINISH + 760, { face: -1, badge: true, mood: 'joy', mouth: m('AZI') }),
        C('ABD', lerp(FINISH - 900, FINISH + 120, fly), { y: lerp(300, 560, fly), fly: fly < 1, mouth: m('ABD'), point: fly >= 1 })];
      S.hearts = t > B.end[0] ? 1 : 0.4;
    }
    return { cam, cast, S };
  }

  // ---------------- captions ----------------
  const SPK = { ABD: ['Abdelhamid', '#8a5a2b'], PIP: ['Pip', '#2f6fe0'], PEB: ['Pebble', '#2e8b3a'], AMI: ['Amir', '#d0711a'], AZI: ['Aziza', '#d63f8a'], HIC: ['Hicham', '#a0522d'], ALL: ['Everyone', '#7a4fd6'] };
  function caption(t) {
    for (const [k, spk, txt] of T.lines) {
      const [a, b] = T[k]; if (t < a - 0.05 || t >= b + 0.3) continue;
      ctx.save(); let fs = 44; ctx.font = `800 ${fs}px Inter, sans-serif`;
      while (ctx.measureText(txt).width > 1600 && fs > 26) { fs -= 2; ctx.font = `800 ${fs}px Inter, sans-serif`; }
      const w = ctx.measureText(txt).width + 80, k2 = backOut((t - a + 0.05) / 0.25), [name, col] = SPK[spk];
      ctx.translate(960, 990); ctx.scale(k2, k2);
      ctx.shadowColor = 'rgba(0,0,0,.18)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 6; rr(-w / 2, -42, w, 84, 42); ctx.fillStyle = 'rgba(255,255,255,.92)'; ctx.fill(); ctx.shadowColor = 'transparent'; ctx.fillStyle = col; rr(-w / 2, -42, 14, 84, 7); ctx.fill();
      text(txt, 0, 2, fs, col);
      ctx.font = '800 28px Inter, sans-serif'; const nw = ctx.measureText(name).width + 40;
      rr(-w / 2 + 20, -72, nw, 44, 22); ctx.fillStyle = col; ctx.fill(); text(name, -w / 2 + 20 + nw / 2, -50, 28, '#fff');
      ctx.restore();
    }
  }

  window.renderFrame = function (t) {
    const { cam, cast, S } = direct(t);
    ctx.save(); ctx.fillStyle = '#7cc8f5'; ctx.fillRect(0, 0, W, H);
    ctx.translate(W / 2, H / 2); ctx.scale(cam.z, cam.z); ctx.translate(-cam.cx, -cam.cy);
    drawWorld(t, cam, S);
    const order = ['AZI', 'ABD', 'HIC', 'PEB', 'AMI', 'PIP'];
    for (const o of cast) { if (o.fly || o.y < 780) continue; const sh = ctx.createRadialGradient(o.x, o.y + 4, 4, o.x, o.y + 4, 120 * (o.sc || 1)); sh.addColorStop(0, 'rgba(30,60,20,.35)'); sh.addColorStop(1, 'rgba(30,60,20,0)'); ctx.fillStyle = sh; ell(o.x, o.y + 4, 130 * (o.sc || 1), 26 * (o.sc || 1)); ctx.fill(); }
    const tf = MAIN.getTransform();
    ctx = LAYER; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); ctx.setTransform(tf);
    cast.sort((a, b) => order.indexOf(a.spk) - order.indexOf(b.spk)).forEach((o) => DRAW[o.spk](o, t));
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    // soft key light from the sun (top-left) and cool shade toward the ground
    ctx.globalCompositeOperation = 'source-atop';
    for (const o of cast) { const z = cam.z * (o.sc || 1), sx = (o.x - cam.cx) * cam.z + W / 2, sy = (o.y - cam.cy) * cam.z + H / 2;
      const hl = ctx.createRadialGradient(sx - 70 * z, sy - 230 * z, 10, sx - 40 * z, sy - 180 * z, 260 * z); hl.addColorStop(0, 'rgba(255,248,225,.30)'); hl.addColorStop(1, 'rgba(255,248,225,0)');
      ctx.fillStyle = hl; ctx.fillRect(sx - 400 * z, sy - 600 * z, 800 * z, 700 * z); }
    const gy = (GROUND - cam.cy) * cam.z + H / 2; let ao = ctx.createLinearGradient(0, gy - 140 * cam.z, 0, gy); ao.addColorStop(0, 'rgba(40,30,80,0)'); ao.addColorStop(1, 'rgba(40,30,80,.16)'); ctx.fillStyle = ao; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'source-over';
    // rim light: layer minus a shifted copy = thin glowing edge on the lit side
    RIM.globalCompositeOperation = 'source-over'; RIM.clearRect(0, 0, W, H); RIM.drawImage(LAYER.canvas, 0, 0);
    RIM.globalCompositeOperation = 'source-in'; RIM.fillStyle = 'rgba(255,250,225,.9)'; RIM.fillRect(0, 0, W, H);
    RIM.globalCompositeOperation = 'destination-out'; RIM.drawImage(LAYER.canvas, 5 * cam.z, 6 * cam.z);
    ctx = MAIN; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.shadowColor = 'rgba(20,30,60,.22)'; ctx.shadowBlur = 24; ctx.shadowOffsetX = 10; ctx.shadowOffsetY = 12;
    ctx.drawImage(LAYER.canvas, 0, 0); ctx.shadowColor = 'transparent';
    ctx.globalAlpha = .75; ctx.drawImage(RIM.canvas, 0, 0); ctx.restore();
    if (S.hearts > 0 && cast.length) { const xs = cast.map(c => c.x), x0 = Math.min(...xs), x1 = Math.max(...xs);
      for (let i = 0; i < 8; i++) { const p = ((t * .45 + i / 8) % 1); heart(lerp(x0, x1, i / 7) + Math.sin(t * 2 + i) * 30, GROUND - 330 - p * 260, (.8 + .4 * Math.sin(i)) * S.hearts, `rgba(255,${80 + i * 15},140,${(1 - p) * S.hearts})`); } }
    if (S.bubble) { const a = cast[0]; const bx = a.x - 260, by = 330; ctx.fillStyle = 'rgba(255,255,255,.95)';
      ell(a.x - 40, 560, 16, 16); ctx.fill(); ell(a.x - 90, 500, 26, 26); ctx.fill(); ell(bx, by, 190, 130); ctx.fill(); ctx.lineWidth = 3.5; ctx.strokeStyle = '#8a5a2b'; ctx.stroke();
      drawAbdelhamid({ x: bx, y: by + 110, sc: 0.85, mouth: mouth('ABD', t), point: true }, t); }
    ctx.restore();
    ctx.save(); ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = 'rgba(255,190,140,.16)'; ctx.fillRect(0, 0, W, H); ctx.restore(); ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.fillStyle = 'rgba(128,128,128,.0)'; ctx.restore();
    { const vg = ctx.createRadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1150); vg.addColorStop(0, 'rgba(60,30,10,0)'); vg.addColorStop(1, 'rgba(60,30,10,.16)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H); }

    if (t < B.intro[0] - 0.3) { // title card
      const k = backOut(t / 0.6), f = 1 - ss(B.intro[0] - 0.9, B.intro[0] - 0.3, t);
      ctx.save(); ctx.globalAlpha = f; ctx.translate(960, 230); ctx.scale(k, k); text('Pip & Pebble', 0, 0, 150, '#ff6f3c', { stroke: 22, w: 900 }); ctx.restore();
      ctx.save(); ctx.globalAlpha = f * ss(0.6, 1.1, t); rr(560, 330, 800, 80, 40); ctx.fillStyle = '#3d8bff'; ctx.fill(); text("Episode 2 · Amir's Big Race", 960, 372, 46, '#fff'); ctx.restore();
    } else caption(t);
    if (t >= at('a6') && t < B.go[0] + 1.2) { // countdown graphics
      const words = [['On your marks', at('a6')], ['Get set', at('a6') + (at('a6', 1) - at('a6')) * 0.55], ['GO!', at('a7')]];
      for (let i = words.length - 1; i >= 0; i--) { if (t >= words[i][1]) { const k = backOut((t - words[i][1]) / 0.3); ctx.save(); ctx.translate(960, 300); ctx.scale(k, k); text(words[i][0], 0, 0, i === 2 ? 180 : 110, i === 2 ? '#2e8b3a' : '#ff6f3c', { stroke: 18 }); ctx.restore(); break; } }
    }
    if (t >= T.end - 7) { // end card
      const k = ss(T.end - 7, T.end - 6.5, t);
      ctx.fillStyle = `rgba(255,248,230,${.9 * k})`; ctx.fillRect(0, 0, W, H);
      const b = backOut((t - T.end + 7) / 0.5); ctx.save(); ctx.translate(960, 300); ctx.scale(b, b);
      text("Today's Friendship Lesson", 0, -60, 64, '#ff6f3c', { stroke: 14 });
      heart(-520, 50, 2, '#ff5d8f'); heart(520, 50, 2, '#ff5d8f');
      text('Being kind is better', 0, 30, 76, '#3d3d8f'); text('than being first!', 0, 120, 76, '#2e8b3a'); ctx.restore();
      if (t > T.end - 6.3) { const b2 = backOut((t - T.end + 6.3) / 0.4); ctx.save(); ctx.translate(960, 600); ctx.scale(b2, b2); rr(-340, -55, 680, 110, 55); ctx.fillStyle = '#3d8bff'; ctx.fill(); text('See you next time!', 0, 2, 52, '#fff'); ctx.restore(); }
      const row = [['AZI', 300], ['ABD', 560], ['HIC', 800], ['PIP', 1030], ['AMI', 1270], ['PEB', 1560]];
      for (const [s, x] of row) DRAW[s]({ x, y: 1060, sc: s === 'AZI' ? 0.45 : 0.7, mood: 'joy', face: x > 1100 ? -1 : 1, hop: Math.abs(Math.sin(t * 5 + x)) * 20, badge: true }, t);
    }
  };
})();
