// Pip & Pebble — Ep.1 "The Shiny Red Ball" — procedural 2D cartoon renderer (1920x1080).
(function () {
  const W = 1920, H = 1080, GROUND = 820, WATER = 905, SHORE = 1250;
  const ctx = document.getElementById('c').getContext('2d');
  const T = window.T;
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
  const backOut = (k) => { const s = 1.7; k = clamp(k) - 1; return k * k * ((s + 1) * k + s) + 1; };
  const hash = (n) => { const x = Math.sin(n * 91.7) * 43758.5453; return x - Math.floor(x); };
  const mouth = (spk, t) => (T['mouth_' + spk] || [])[Math.floor(t * T.fps)] || 0;
  const L = (k) => T[k];
  function ell(x, y, rx, ry, r = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(.1, rx), Math.max(.1, ry), r, 0, Math.PI * 2); }
  function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
  function text(s, x, y, size, col, o = {}) {
    ctx.save(); ctx.font = `${o.w || 800} ${size}px ${o.f || '"Baloo 2", Inter, "DejaVu Sans", sans-serif'}`;
    ctx.textAlign = o.a || 'center'; ctx.textBaseline = 'middle';
    if (o.stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = o.stroke; ctx.strokeStyle = o.sc || '#fff'; ctx.strokeText(s, x, y); }
    ctx.fillStyle = col; ctx.fillText(s, x, y); ctx.restore();
  }
  function heart(x, y, s, col) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = col; ctx.beginPath();
    ctx.moveTo(0, 12); ctx.bezierCurveTo(-26, -6, -14, -30, 0, -14); ctx.bezierCurveTo(14, -30, 26, -6, 0, 12); ctx.fill(); ctx.restore();
  }
  function star(x, y, r, col, rot = 0) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.fillStyle = col; ctx.beginPath();
    for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5 - Math.PI / 2, rad = i % 2 ? r * 0.45 : r; ctx.lineTo(Math.cos(a) * rad, Math.sin(a) * rad); }
    ctx.closePath(); ctx.fill(); ctx.restore();
  }

  // ---------------- world ----------------
  function groundY(x) { // meadow, then slope into the pond
    if (x < 1150) return GROUND + Math.sin(x / 260) * 6;
    if (x < 1330) return lerp(GROUND, WATER + 40, ss(1150, 1330, x));
    return WATER + 60;
  }
  function drawWorld(t, s) {
    let g = ctx.createLinearGradient(0, 0, 0, 800);
    g.addColorStop(0, s.sad ? '#9fb4c9' : '#7cc8f5'); g.addColorStop(1, s.sad ? '#d5dde6' : '#d8f1ff');
    ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, 1400);
    // sun with turning rays
    ctx.save(); ctx.translate(260, 170); ctx.rotate(t * 0.15);
    ctx.fillStyle = 'rgba(255,214,90,0.35)';
    for (let i = 0; i < 12; i++) { ctx.rotate(Math.PI / 6); ctx.beginPath(); ctx.moveTo(0, -95); ctx.lineTo(18, -150); ctx.lineTo(-18, -150); ctx.fill(); }
    ctx.restore();
    ell(260, 170, 85, 85); ctx.fillStyle = '#ffd84d'; ctx.fill();
    ell(235, 160, 9, 12); ctx.fillStyle = '#7a5200'; ctx.fill(); ell(285, 160, 9, 12); ctx.fill();
    ctx.strokeStyle = '#7a5200'; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(260, 185, 24, 0.2, Math.PI - 0.2); ctx.stroke();
    // clouds
    for (let i = 0; i < 4; i++) {
      const cx = ((i * 560 + t * (14 + i * 4)) % 2600) - 300, cy = 110 + (i % 2) * 90;
      ctx.fillStyle = 'rgba(255,255,255,0.95)';
      ell(cx, cy, 90, 42); ctx.fill(); ell(cx - 60, cy + 10, 60, 32); ctx.fill(); ell(cx + 65, cy + 12, 64, 30); ctx.fill(); ell(cx + 10, cy - 28, 55, 38); ctx.fill();
    }
    // far hills
    ctx.fillStyle = '#a5dc86'; ctx.beginPath(); ctx.moveTo(-300, 760);
    for (let x = -300; x <= 2300; x += 40) ctx.lineTo(x, 640 + Math.sin(x / 210) * 45 + Math.sin(x / 90) * 10);
    ctx.lineTo(2300, 1100); ctx.lineTo(-300, 1100); ctx.fill();
    ctx.fillStyle = '#8fd16f'; ctx.beginPath(); ctx.moveTo(-300, 780);
    for (let x = -300; x <= 2300; x += 40) ctx.lineTo(x, 715 + Math.sin(x / 150 + 1) * 30);
    ctx.lineTo(2300, 1100); ctx.lineTo(-300, 1100); ctx.fill();
    // tree
    ctx.fillStyle = '#8a5a3b'; rr(120, 520, 60, 310, 20); ctx.fill();
    ctx.fillStyle = '#4fae4f';
    for (const [x, y, r] of [[150, 470, 120], [70, 540, 90], [235, 540, 95], [150, 390, 90]]) { ell(x + Math.sin(t + x) * 3, y, r, r * 0.9); ctx.fill(); }
    ctx.fillStyle = '#e8473f'; for (const [x, y] of [[100, 470], [200, 430], [230, 560], [90, 580], [160, 520]]) { ell(x, y, 13, 13); ctx.fill(); }
    // pond (back part)
    g = ctx.createLinearGradient(0, WATER, 0, 1080); g.addColorStop(0, '#5ec6e8'); g.addColorStop(1, '#2f8fc2');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(1240, WATER); ctx.lineTo(2300, WATER); ctx.lineTo(2300, 1100); ctx.lineTo(1240, 1100); ctx.fill();
    // meadow ground with slope
    ctx.fillStyle = '#6cc04a'; ctx.beginPath(); ctx.moveTo(-300, 1100); ctx.lineTo(-300, groundY(-300));
    for (let x = -300; x <= 1400; x += 10) ctx.lineTo(x, groundY(x));
    ctx.lineTo(1400, 1100); ctx.fill();
    ctx.fillStyle = '#58a83a'; ctx.fillRect(-300, 880, 1450, 220);
    // grass tufts + flowers
    for (let i = 0; i < 40; i++) {
      const x = -250 + i * 37, y = groundY(x) + 4; if (x > 1180) continue;
      ctx.strokeStyle = '#3f8f2c'; ctx.lineWidth = 4; ctx.beginPath();
      ctx.moveTo(x, y); ctx.lineTo(x - 6, y - 16 - Math.sin(t * 2 + i) * 2); ctx.moveTo(x, y); ctx.lineTo(x + 6, y - 14); ctx.stroke();
    }
    const fc = ['#ff6fa8', '#ffd23f', '#ffffff', '#b07cff'];
    for (let i = 0; i < 16; i++) {
      const x = -200 + hash(i) * 1350, y = groundY(x) + 30 + hash(i + 7) * 50; if (x > 1150) continue;
      ctx.fillStyle = fc[i % 4]; for (let p = 0; p < 5; p++) { const a = p * 1.256 + t * 0.3; ell(x + Math.cos(a) * 9, y + Math.sin(a) * 9, 7, 7); ctx.fill(); }
      ell(x, y, 6, 6); ctx.fillStyle = '#ff9f1c'; ctx.fill();
    }
    // lily pads + reeds
    ctx.fillStyle = '#3fa34d';
    for (const [x, y] of [[1780, 930], [1880, 965], [1560, 1010]]) { ctx.beginPath(); ctx.ellipse(x, y, 42, 14, 0, 0.3, Math.PI * 2 - 0.1); ctx.lineTo(x, y); ctx.fill(); }
    ctx.strokeStyle = '#6b8f2c'; ctx.lineWidth = 7;
    for (let i = 0; i < 5; i++) { const x = 1880 + i * 14; ctx.beginPath(); ctx.moveTo(x, WATER + 10); ctx.quadraticCurveTo(x + Math.sin(t + i) * 8, WATER - 80, x - 4, WATER - 140 - i * 10); ctx.stroke(); }
  }
  function drawWaterFront(t) { // translucent water drawn OVER swimmers
    ctx.save(); ctx.beginPath(); ctx.moveTo(1240, WATER);
    for (let x = 1240; x <= 2300; x += 20) ctx.lineTo(x, WATER + Math.sin(x / 40 + t * 3) * 4);
    ctx.lineTo(2300, 1100); ctx.lineTo(1240, 1100); ctx.closePath();
    ctx.fillStyle = 'rgba(70,175,225,0.82)'; ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.7)'; ctx.lineWidth = 4;
    for (let i = 0; i < 6; i++) { const x = 1330 + i * 110 + Math.sin(t + i) * 20; ctx.beginPath(); ctx.moveTo(x, WATER + 25 + i % 2 * 30); ctx.lineTo(x + 50, WATER + 25 + i % 2 * 30); ctx.stroke(); }
    ctx.restore();
    // shore slope drawn again on top so the bank looks solid
    ctx.fillStyle = '#6cc04a'; ctx.beginPath(); ctx.moveTo(1140, 1100); ctx.lineTo(1140, groundY(1140));
    for (let x = 1140; x <= 1300; x += 8) ctx.lineTo(x, groundY(x)); ctx.lineTo(1250, 1100); ctx.fill();
  }

  // ---------------- characters ----------------
  // Pip the bunny. origin = feet center. o: {x,y,face,hop,mouth,mood,ears,hold,arms}
  function drawPip(o, t) {
    ctx.save(); ctx.translate(o.x, o.y - (o.hop || 0)); ctx.scale(o.face || 1, 1); ctx.scale(o.sc || 1, o.sc || 1);
    const sq = o.squash || 0; ctx.scale(1 + sq * 0.12, 1 - sq * 0.12);
    const OUT = '#6b4a3a', FUR = '#f7e6d4', BELLY = '#fffaf2';
    ctx.lineWidth = 5; ctx.strokeStyle = OUT;
    // tail
    ell(-58, -80, 24, 22); ctx.fillStyle = '#fff'; ctx.fill(); ctx.stroke();
    // feet
    ell(-28, -8, 30, 14); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke(); ell(30, -8, 30, 14); ctx.fill(); ctx.stroke();
    // body
    ell(0, -85, 58, 66); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke();
    ell(8, -78, 36, 44); ctx.fillStyle = BELLY; ctx.fill();
    // scarf
    ctx.fillStyle = '#3d8bff'; rr(-48, -150, 96, 26, 13); ctx.fill(); ctx.stroke();
    ctx.save(); ctx.translate(-30, -132); ctx.rotate(0.5 + Math.sin(t * 6) * 0.15); rr(-12, 0, 24, 46, 10); ctx.fill(); ctx.stroke(); ctx.restore();
    // ears
    const droop = o.ears || 0;
    for (const sd of [-1, 1]) {
      ctx.save(); ctx.translate(sd * 26, -250); ctx.rotate(sd * (0.12 + droop * 1.1) + Math.sin(t * 4 + sd) * 0.04);
      ell(0, -60, 22, 66); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke();
      ell(0, -56, 11, 50); ctx.fillStyle = '#ffb3c6'; ctx.fill(); ctx.restore();
    }
    // head
    ell(0, -205, 72, 64); ctx.fillStyle = FUR; ctx.fill(); ctx.stroke();
    // eyes
    const blink = ((t + 1.3) % 3.4) < 0.12;
    const happyEyes = o.mood === 'joy';
    for (const ex of [-4, 34]) {
      if (blink || happyEyes) { ctx.beginPath(); ctx.lineWidth = 6; ctx.arc(ex, -212, 13, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); ctx.lineWidth = 5; continue; }
      const look = o.look || 0, ly = o.lookY || 0;
      ell(ex, -212, 13, 18); ctx.fillStyle = '#2b1d16'; ctx.fill();
      ell(ex - 4 + look * 3, -219 + ly * 3, 5, 6); ctx.fillStyle = '#fff'; ctx.fill(); ell(ex + 4, -205, 2.5, 2.5); ctx.fill();
      if (o.mood === 'worry' || o.mood === 'sorry') { ctx.beginPath(); ctx.moveTo(ex - 14, -238 + (ex < 10 ? 6 : -2)); ctx.lineTo(ex + 14, -238 + (ex < 10 ? -2 : 6)); ctx.stroke(); }
      if (o.mood === 'proud') { ctx.beginPath(); ctx.moveTo(ex - 14, -236); ctx.lineTo(ex + 14, -240); ctx.stroke(); }
    }
    // cheeks + nose + mouth
    ctx.fillStyle = 'rgba(255,120,150,0.45)'; ell(-28, -185, 14, 9); ctx.fill(); ell(58, -185, 13, 9); ctx.fill();
    ctx.fillStyle = '#ff7f9e'; ell(18, -192, 9, 7); ctx.fill();
    const m = o.mouth || 0;
    if (m > 0.08) { ell(18, -170 + m * 3, 10 + m * 5, 3 + m * 12); ctx.fillStyle = '#7a2238'; ctx.fill(); ell(18, -166 + m * 7, 7, 3 + m * 4); ctx.fillStyle = '#ff8fa3'; ctx.fill(); }
    else { ctx.beginPath(); ctx.lineWidth = 4; if (o.mood === 'worry' || o.mood === 'sorry') ctx.arc(18, -164, 9, Math.PI * 1.15, Math.PI * 1.85); else ctx.arc(18, -178, 10, 0.25, Math.PI - 0.25); ctx.stroke(); }
    // arms (hold ball up / cross / normal)
    ctx.fillStyle = FUR; ctx.lineWidth = 5;
    const arms = o.arms || 'down';
    const armPos = arms === 'up' ? [[-38, -175], [42, -175]] : arms === 'out' ? [[-62, -110], [66, -110]] : [[-46, -78], [52, -78]];
    for (const [ax, ay] of armPos) { ell(ax, ay, 16, 20); ctx.fill(); ctx.stroke(); }
    ctx.restore();
  }

  // Pebble the turtle. origin = feet center.
  function drawPebble(o, t) {
    ctx.save(); ctx.translate(o.x, o.y - (o.bob || 0)); ctx.scale(o.face || 1, 1); ctx.scale(o.sc || 1, o.sc || 1);
    const OUT = '#2f5d2a'; ctx.lineWidth = 5; ctx.strokeStyle = OUT;
    const step = o.walk ? Math.sin(t * 7) : 0;
    // legs
    ctx.fillStyle = '#a8e08a';
    for (const [lx, ph] of [[-70, 1], [-25, -1], [35, 1], [75, -1]]) { ell(lx + step * ph * 6, -14 - Math.max(0, step * ph) * 6, 20, 16); ctx.fill(); ctx.stroke(); }
    // tail
    ctx.beginPath(); ctx.moveTo(-118, -40); ctx.lineTo(-140, -30); ctx.lineTo(-116, -24); ctx.closePath(); ctx.fill(); ctx.stroke();
    // shell
    ctx.beginPath(); ctx.ellipse(0, -40, 120, 92, 0, Math.PI, 0); ctx.closePath();
    let g = ctx.createRadialGradient(-30, -100, 10, 0, -50, 140); g.addColorStop(0, '#7fd36e'); g.addColorStop(1, '#3f9a3a');
    ctx.fillStyle = g; ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#9be38a';
    for (const [hx, hy, r] of [[0, -90, 26], [-55, -70, 20], [55, -70, 20], [-30, -112, 14], [30, -112, 14], [-85, -48, 13], [85, -48, 13]]) {
      ctx.beginPath(); for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; ctx.lineTo(hx + Math.cos(a) * r, hy + Math.sin(a) * r * 0.8); } ctx.closePath(); ctx.fill();
    }
    ctx.fillStyle = '#e6d27a'; rr(-122, -48, 244, 16, 8); ctx.fill(); ctx.stroke();
    // neck + head
    const hx = 128, hy = -70 - (o.headUp || 0) * 18;
    ctx.fillStyle = '#a8e08a'; ell(100, -55, 26, 22); ctx.fill();
    ell(hx, hy, 46, 42); ctx.fill(); ctx.stroke();
    // eyes
    const blink = ((t + 0.4) % 4.1) < 0.12;
    for (const ex of [hx - 6, hx + 22]) {
      if (blink || o.mood === 'joy') { ctx.beginPath(); ctx.lineWidth = 5; ctx.arc(ex, hy - 6, 10, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); continue; }
      ell(ex, hy - 8, 11, 14); ctx.fillStyle = '#fff'; ctx.fill(); ctx.stroke();
      const ly = o.mood === 'sad' ? 4 : 0;
      ell(ex + 3, hy - 6 + ly, 6, 8); ctx.fillStyle = '#1d140f'; ctx.fill(); ell(ex + 1, hy - 10 + ly, 2.5, 2.5); ctx.fillStyle = '#fff'; ctx.fill();
      if (o.mood === 'sad') { ctx.beginPath(); ctx.lineWidth = 4; ctx.moveTo(ex - 10, hy - 30 + (ex < hx ? 6 : 0)); ctx.lineTo(ex + 10, hy - 30 + (ex < hx ? 0 : 6)); ctx.stroke(); }
      if (o.mood === 'brave') { ctx.beginPath(); ctx.lineWidth = 4; ctx.moveTo(ex - 10, hy - 30 + (ex < hx ? -4 : 4)); ctx.lineTo(ex + 10, hy - 30 + (ex < hx ? 4 : -4)); ctx.stroke(); }
    }
    if (o.mood === 'sad' && o.tear) { const ty = hy + 6 + (t * 60 % 40); ctx.fillStyle = '#6ec6ff'; ell(hx + 30, ty, 6, 9); ctx.fill(); }
    ctx.fillStyle = 'rgba(255,130,150,0.5)'; ell(hx - 18, hy + 12, 9, 6); ctx.fill(); ell(hx + 36, hy + 12, 8, 6); ctx.fill();
    const m = o.mouth || 0; ctx.lineWidth = 4;
    if (m > 0.08) { ell(hx + 10, hy + 20, 8 + m * 4, 2 + m * 10); ctx.fillStyle = '#6b1f2e'; ctx.fill(); }
    else { ctx.beginPath(); if (o.mood === 'sad') ctx.arc(hx + 10, hy + 30, 9, Math.PI * 1.15, Math.PI * 1.85); else ctx.arc(hx + 10, hy + 14, 11, 0.3, Math.PI - 0.3); ctx.stroke(); }
    // little backpack strap (signature)
    ctx.restore();
  }

  function drawBall(b, t) {
    ctx.save(); ctx.translate(b.x, b.y); ctx.rotate(b.rot || 0);
    const g = ctx.createRadialGradient(-10, -12, 4, 0, 0, 34); g.addColorStop(0, '#ff7b6b'); g.addColorStop(1, '#d7261e');
    ell(0, 0, 32, 32); ctx.fillStyle = g; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = '#8a1a14'; ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.ellipse(0, 0, 32, 9, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#ffd23f'; star(0, 0, 8, '#ffd23f');
    ctx.restore();
    ell(b.x - 10, b.y - 14, 7, 5); ctx.fillStyle = 'rgba(255,255,255,0.7)'; ctx.fill();
    if (b.shine) for (let i = 0; i < 4; i++) star(b.x + Math.cos(t * 3 + i * 1.6) * 52, b.y + Math.sin(t * 3 + i * 1.6) * 52, 9, 'rgba(255,230,90,0.9)', t * 2);
  }

  // ---------------- direction ----------------
  function direct(t) {
    const cam = { cx: 960, cy: 540, z: 1 };
    const pip = { x: -200, y: GROUND, face: 1, mood: 'happy', mouth: mouth('PIP', t), arms: 'down' };
    const peb = { x: -300, y: GROUND, face: 1, mood: 'happy', mouth: mouth('PEB', t), show: false };
    const ball = { x: -200, y: GROUND - 32, rot: 0, show: false };
    const S = { sad: false, hearts: 0, splashAt: -1, diveAt: -1 };

    if (t < T.n1[0]) { // title: meadow, characters peek
      pip.x = 760; pip.mood = 'joy'; pip.hop = Math.abs(Math.sin(t * 5)) * 30; pip.arms = 'out';
      peb.show = true; peb.x = 1080; peb.face = -1; peb.mood = 'joy'; peb.bob = Math.abs(Math.sin(t * 3)) * 6;
      return { cam, pip, peb, ball, S };
    }
    if (t < T.b1[0] - 0.9) { // Pip hops in with ball, shows it off
      const k = ss(T.n1[0], T.n1[1], t);
      pip.x = lerp(-150, 620, k); pip.hop = k < 1 ? Math.abs(Math.sin(t * 7)) * 60 : 0;
      ball.show = true;
      if (t < T.p1[0]) { ball.x = pip.x + 60; ball.y = groundY(ball.x) - 32 - Math.abs(Math.sin(t * 7)) * 70; ball.rot = t * 8; cam.z = 1; }
      else { pip.mood = 'proud'; pip.arms = 'up'; ball.x = pip.x + 18; ball.y = GROUND - 300; ball.shine = true; cam.cx = 640; cam.cy = 560; cam.z = lerp(1, 1.55, ss(T.p1[0], T.p1[0] + 0.5, t)); }
      return { cam, pip, peb, ball, S };
    }
    if (t < T.p3[0] - 0.3) { // Pebble arrives, Pip refuses, Pebble sad
      pip.x = 620; ball.show = true; ball.x = 700; ball.y = GROUND - 32;
      peb.show = true; peb.x = lerp(-150, 330, ss(T.b1[0] - 0.9, T.b1[0] + 1.0, t)); peb.walk = t < T.b1[0] + 1.0;
      cam.cx = 500; cam.cy = 600; cam.z = 1.3;
      pip.face = -1; pip.look = 1;
      if (t >= T.p2[0]) { pip.face = 1; pip.mood = 'proud'; pip.arms = 'out'; ball.x = 700; }
      if (t >= T.n2[0]) { peb.mood = 'sad'; peb.tear = true; S.sad = true; cam.cx = lerp(500, 380, ss(T.n2[0], T.n2[0] + 1, t)); cam.z = lerp(1.3, 1.7, ss(T.n2[0], T.n2[0] + 1, t)); }
      return { cam, pip, peb, ball, S };
    }
    if (t < T.b2[0]) { // super high bounce → ball rolls into the pond
      peb.show = true; peb.x = 330; peb.mood = 'sad';
      pip.x = 620; ball.show = true;
      const b0 = T.bounce, sp = T.splash;
      if (t < b0) { // dribbling
        pip.mood = 'joy'; pip.arms = 'out'; const ph = Math.abs(Math.sin((t - T.p3[0]) * 6));
        ball.x = 700; ball.y = GROUND - 32 - ph * 120; pip.hop = ph * 12;
      } else if (t < sp) { // flight arc + bounces down the slope
        const k = (t - b0) / (sp - b0);
        const pts = [[700, GROUND - 32], [1000, 120], [1140, GROUND - 40], [1240, 820], [1310, 880], [1480, WATER]];
        const seg = Math.min(4, Math.floor(k * 5)), u = k * 5 - seg;
        const [x0, y0] = pts[seg], [x1, y1] = pts[seg + 1];
        const hgt = seg === 0 ? 0 : [0, 0, 90, 50, 30][seg];
        ball.x = lerp(x0, x1, u); ball.y = seg === 0 ? lerp(y0, y1, Math.sin(u * Math.PI / 2)) : lerp(y0, y1, u) - Math.sin(u * Math.PI) * hgt;
        if (seg === 0 && u > 0.5) ball.y = lerp(120, 120, 1);
        ball.rot = t * 14; pip.mood = 'worry'; pip.look = 1; pip.lookY = -1;
      } else { // floating away
        const k = t - sp; ball.x = 1480 + k * 45; ball.y = WATER + Math.sin(t * 3) * 5; ball.rot = Math.sin(t) * 0.3;
        S.splashAt = sp;
        pip.x = lerp(620, 1150, ss(sp, sp + 0.8, t)); pip.hop = t < sp + 0.8 ? Math.abs(Math.sin(t * 9)) * 40 : 0; pip.mood = 'worry'; pip.ears = 0.6; pip.arms = 'up';
      }
      if (t >= sp + 0.5) { cam.cx = 1300; cam.cy = 700; cam.z = 1.4; peb.show = false; }
      return { cam, pip, peb, ball, S };
    }
    if (t < T.p5[0] - 0.6) { // Pebble to the rescue
      pip.x = 1190; pip.mood = 'worry'; pip.ears = 0.5; ball.show = true;
      peb.show = true; cam.cx = 1300; cam.cy = 700; cam.z = 1.4;
      const fl = (t - T.splash);
      if (t < T.dive) { // Pebble arrives beside Pip, brave face
        peb.x = 930; peb.mood = 'brave'; peb.headUp = 1; ball.x = Math.min(1480 + fl * 45, 1700); ball.y = WATER + Math.sin(t * 3) * 5;
      } else { // slide, swim fast to ball, push it back
        S.diveAt = T.dive; cam.cx = lerp(1300, 1500, ss(T.dive, T.dive + 1, t)); cam.z = 1.25;
        const reach = T.dive + 1.8, back = T.back;
        const bx = Math.min(1480 + (T.dive - T.splash) * 45, 1700);
        if (t < T.dive + 0.5) { const u = ss(T.dive, T.dive + 0.5, t); peb.x = lerp(930, 1330, u); peb.y = groundY(peb.x) + u * 30; ball.x = bx; ball.y = WATER + Math.sin(t * 3) * 5; }
        else if (t < reach) { const u = ss(T.dive + 0.5, reach, t); peb.x = lerp(1330, bx - 150, u); peb.y = WATER + 55; peb.swim = true; ball.x = bx; ball.y = WATER + Math.sin(t * 3) * 5; }
        else { const u = ss(reach, back, t); peb.face = -1; peb.x = lerp(bx + 150, 1420, u); peb.y = WATER + 55; peb.swim = true; ball.x = peb.x - 175; ball.y = WATER - 2; ball.rot = -t * 6; }
        if (t >= back) { const u = ss(back, back + 0.7, t); peb.face = -1; peb.x = lerp(1420, 1340, u); peb.y = lerp(WATER + 55, groundY(1340), u); ball.x = lerp(1245, 1200, u); ball.y = groundY(ball.x) - 32; cam.cx = 1300; cam.z = 1.4; pip.mood = 'joy'; pip.ears = 0; pip.hop = Math.abs(Math.sin(t * 8)) * 25; }
        peb.mood = 'brave'; peb.walk = false;
      }
      return { cam, pip, peb, ball, S };
    }
    if (t < T.play) { // sorry + friendship
      cam.cx = 1180; cam.cy = 660; cam.z = 1.5;
      pip.x = 1010; peb.show = true; peb.x = 1360; peb.face = -1; ball.show = true; ball.x = 1150; ball.y = groundY(1150) - 32;
      pip.mood = t < T.p6[0] ? 'sorry' : 'happy'; pip.ears = t < T.p6[0] ? 0.8 : 0; pip.lookY = t < T.p6[0] ? 1 : 0;
      peb.mood = t >= T.b3[0] ? 'joy' : 'happy';
      if (t >= T.b3[0]) { S.hearts = ss(T.b3[0], T.b3[0] + 0.5, t); pip.mood = 'joy'; pip.hop = Math.abs(Math.sin(t * 6)) * 20; peb.bob = Math.abs(Math.sin(t * 6)) * 8; }
      return { cam, pip, peb, ball, S };
    }
    // playing together on the meadow + end card
    pip.x = 420; peb.show = true; peb.x = 900; peb.face = -1; ball.show = true;
    const ph = ((t - T.play) * 0.55) % 1, dir = Math.floor((t - T.play) * 0.55) % 2;
    const u = dir === 0 ? ph : 1 - ph;
    ball.x = lerp(500, 790, u); ball.y = GROUND - 32 - Math.sin(ph * Math.PI) * 150; ball.rot = t * 6;
    pip.mood = 'joy'; peb.mood = 'joy'; pip.arms = u < 0.15 ? 'out' : 'down'; pip.hop = Math.abs(Math.sin(t * 5)) * 18; peb.bob = Math.abs(Math.sin(t * 4)) * 6;
    S.hearts = 0.6; cam.cx = 700; cam.cy = 600; cam.z = 1.15;
    return { cam, pip, peb, ball, S };
  }

  // ---------------- captions ----------------
  const SPK = { N: { name: '', col: '#4a3b8f' }, PIP: { name: 'Pip', col: '#2f6fe0' }, PEB: { name: 'Pebble', col: '#2e8b3a' } };
  function caption(t) {
    for (const [k, spk, txt] of T.lines) {
      const [a, b] = T[k];
      if (t >= a - 0.05 && t < b + 0.3) {
        ctx.save(); let fs = 44; ctx.font = `800 ${fs}px "Baloo 2", Inter, sans-serif`;
        while (ctx.measureText(txt).width > 1560 && fs > 26) { fs -= 2; ctx.font = `800 ${fs}px "Baloo 2", Inter, sans-serif`; }
        const w = ctx.measureText(txt).width + 80;
        const k2 = backOut((t - a + 0.05) / 0.25);
        ctx.translate(960, 985); ctx.scale(k2, k2);
        rr(-w / 2, -42, w, 84, 42); ctx.fillStyle = 'rgba(255,255,255,0.93)'; ctx.fill();
        ctx.lineWidth = 6; ctx.strokeStyle = SPK[spk].col; ctx.stroke();
        text(txt, 0, 2, fs, SPK[spk].col);
        if (SPK[spk].name) { rr(-w / 2 + 20, -70, 150, 44, 22); ctx.fillStyle = SPK[spk].col; ctx.fill(); text(SPK[spk].name, -w / 2 + 95, -48, 28, '#fff'); }
        ctx.restore();
      }
    }
  }

  window.renderFrame = function (t) {
    const { cam, pip, peb, ball, S } = direct(t);
    ctx.save(); ctx.fillStyle = '#7cc8f5'; ctx.fillRect(0, 0, W, H);
    ctx.translate(W / 2, H / 2); ctx.scale(cam.z, cam.z); ctx.translate(-cam.cx, -cam.cy);
    drawWorld(t, S);
    if (peb.show) drawPebble(peb, t);
    drawPip(pip, t);
    if (ball.show) drawBall(ball, t);
    drawWaterFront(t);
    // splash bursts + swim bubbles
    for (const [at, x] of [[S.splashAt, 1480], [S.diveAt, 1330]]) {
      if (at > 0 && t - at < 0.9) { const k = (t - at) / 0.9; ctx.fillStyle = `rgba(255,255,255,${1 - k})`;
        for (let i = 0; i < 9; i++) { const a = Math.PI + i * Math.PI / 8; ell(x + Math.cos(a) * k * 120, WATER + Math.sin(a) * k * 110 + k * k * 120, 12 * (1 - k) + 4, 12 * (1 - k) + 4); ctx.fill(); } }
    }
    if (peb.swim) { ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = 5; for (let i = 0; i < 4; i++) { const d = -peb.face; ctx.beginPath(); ctx.moveTo(peb.x + d * (140 + i * 30), WATER + 10 + i * 12); ctx.lineTo(peb.x + d * (220 + i * 40), WATER + 10 + i * 12); ctx.stroke(); } }
    if (S.hearts > 0) for (let i = 0; i < 7; i++) { const p = ((t * 0.5 + i / 7) % 1); heart(lerp(pip.x, peb.x, i / 6) + Math.sin(t * 2 + i) * 30, GROUND - 260 - p * 260, (0.9 + 0.5 * Math.sin(i)) * S.hearts * (1 - p * 0.3), `rgba(255,${80 + i * 15},140,${(1 - p) * S.hearts})`); }
    ctx.restore();

    // title card
    if (t < T.n1[0]) {
      const k = backOut(t / 0.6), f = 1 - ss(T.n1[0] - 0.5, T.n1[0], t);
      ctx.save(); ctx.globalAlpha = f; ctx.translate(960, 330); ctx.scale(k, k);
      text('Pip & Pebble', 0, 0, 150, '#ff6f3c', { stroke: 22, sc: '#fff', w: 900 });
      ctx.restore();
      ctx.save(); ctx.globalAlpha = f * ss(0.6, 1.1, t);
      rr(560, 430, 800, 80, 40); ctx.fillStyle = '#3d8bff'; ctx.fill();
      text('Episode 1 · The Shiny Red Ball', 960, 472, 46, '#fff'); ctx.restore();
    }
    if (t >= T.n1[0]) caption(t);
    // end card
    if (t >= T.endcard) {
      const k = ss(T.endcard, T.endcard + 0.4, t);
      ctx.fillStyle = `rgba(255,248,230,${0.88 * k})`; ctx.fillRect(0, 0, W, H);
      const b = backOut((t - T.endcard) / 0.5);
      ctx.save(); ctx.translate(960, 300); ctx.scale(b, b);
      text("Today's Friendship Lesson", 0, -40, 64, '#ff6f3c', { stroke: 14 });
      heart(-470, 70, 2, '#ff5d8f'); heart(470, 70, 2, '#ff5d8f');
      text('Share with friends', 0, 50, 72, '#3d3d8f');
      text('& everyone is good at something!', 0, 140, 56, '#2e8b3a');
      ctx.restore();
      if (t > T.endcard + 0.6) { const b2 = backOut((t - T.endcard - 0.6) / 0.4); ctx.save(); ctx.translate(960, 640); ctx.scale(b2, b2);
        rr(-340, -55, 680, 110, 55); ctx.fillStyle = '#3d8bff'; ctx.fill(); text('See you next time!', 0, 2, 52, '#fff'); ctx.restore(); }
      drawPip({ x: 640, y: 1010, mood: 'joy', hop: Math.abs(Math.sin(t * 5)) * 25, arms: 'up', sc: 0.9, mouth: 0 }, t);
      drawPebble({ x: 1300, y: 1010, face: -1, mood: 'joy', bob: Math.abs(Math.sin(t * 5)) * 8, sc: 0.9, mouth: 0 }, t);
    }
  };
})();
