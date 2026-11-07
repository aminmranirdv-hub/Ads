// Barnaby Purrkins — Ep.1 "The Performance Review" — procedural 2D renderer.
// Exposes window.renderFrame(t) drawing onto #c (1080x1920). Timeline in window.T.
(function () {
  const W = 1080, H = 1920;
  const c = document.getElementById('c');
  const ctx = c.getContext('2d');
  const T = window.T;

  // ---------- helpers ----------
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
  const backOut = (k) => { const s = 1.9; k = clamp(k) - 1; return k * k * ((s + 1) * k + s) + 1; };
  const within = (t, a, b) => t >= a && t < b;
  const hash = (n) => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); };
  const noise1 = (t) => { const i = Math.floor(t), f = t - i; const u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; };
  function mouthAt(t) { const i = Math.floor(t * T.fps); return T.mouth[i] || 0; }
  function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
  function ellipse(x, y, rx, ry, rot = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(0.1, rx), Math.max(0.1, ry), rot, 0, Math.PI * 2); }
  function text(str, x, y, size, color, opts = {}) {
    ctx.save();
    ctx.font = `${opts.weight || 900} ${size}px ${opts.font || 'Inter, "DejaVu Sans", sans-serif'}`;
    ctx.textAlign = opts.align || 'center'; ctx.textBaseline = 'middle';
    if (opts.stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = opts.stroke; ctx.strokeStyle = opts.strokeColor || '#000'; ctx.strokeText(str, x, y); }
    ctx.fillStyle = color; ctx.fillText(str, x, y);
    ctx.restore();
  }

  const FUR = '#f4e4c8', FUR_SH = '#e2c79f', GINGER = '#d8914a', GINGER_D = '#a85a24', LINE = '#7a5233';
  const EYE_R = '#7fe0b5'; // viewer-left = character's RIGHT eye = mint green
  const EYE_L = '#f0a530'; // viewer-right = character's LEFT eye = amber
  const GOLD = '#d9ac3c';

  // ---------- environment ----------
  function drawRoom(t, s) {
    // wall
    let g = ctx.createLinearGradient(0, 0, 0, 1300);
    g.addColorStop(0, '#3d2c24'); g.addColorStop(1, '#5e4434');
    ctx.fillStyle = g; ctx.fillRect(-400, -400, W + 800, 1700);
    // wainscot
    ctx.fillStyle = '#4a3428'; ctx.fillRect(-400, 1050, W + 800, 300);
    // window with blinds (right) - evening city
    ctx.save();
    rr(690, 230, 360, 430, 8); ctx.fillStyle = '#2b2018'; ctx.fill();
    rr(706, 246, 328, 398, 4); ctx.clip();
    g = ctx.createLinearGradient(0, 246, 0, 644); g.addColorStop(0, '#f6a66b'); g.addColorStop(0.6, '#c2607a'); g.addColorStop(1, '#4b2f5e');
    ctx.fillStyle = g; ctx.fillRect(706, 246, 328, 398);
    ctx.fillStyle = '#2a1b33';
    for (let i = 0; i < 9; i++) { const bx = 700 + i * 40, bh = 70 + hash(i + 3) * 160; ctx.fillRect(bx, 644 - bh, 34, bh); }
    ctx.fillStyle = 'rgba(255,220,140,0.8)';
    for (let i = 0; i < 40; i++) { const bx = 706 + hash(i) * 320, by = 520 + hash(i + 50) * 120; if (hash(i + 9) > 0.4) ctx.fillRect(bx, by, 5, 7); }
    if (s.flash) { ctx.fillStyle = `rgba(255,255,255,${s.flash})`; ctx.fillRect(706, 246, 328, 398); }
    ctx.fillStyle = 'rgba(240,225,200,0.92)';
    for (let y = 250; y < 640; y += 26) ctx.fillRect(706, y, 328, 13);
    ctx.restore();
    // framed photo "employee of the month"
    ctx.save(); ctx.translate(540, 150);
    rr(-120, -95, 240, 200, 6); ctx.fillStyle = '#c69b3c'; ctx.fill();
    rr(-104, -79, 208, 150, 3); ctx.fillStyle = '#e9dcc4'; ctx.fill();
    ellipse(0, -10, 46, 40); ctx.fillStyle = FUR; ctx.fill();
    ctx.fillStyle = GINGER_D; ctx.fillRect(-28, -32, 56, 7);
    ctx.beginPath(); ctx.moveTo(-44, -30); ctx.lineTo(-36, -62); ctx.lineTo(-18, -44); ctx.closePath(); ctx.fillStyle = FUR; ctx.fill();
    ctx.beginPath(); ctx.moveTo(44, -30); ctx.lineTo(36, -62); ctx.lineTo(18, -44); ctx.closePath(); ctx.fill();
    ctx.fillStyle = '#222'; ellipse(-15, -10, 4, 6); ctx.fill(); ellipse(15, -10, 4, 6); ctx.fill();
    text('EMPLOYEE OF THE MONTH', 0, 52, 15, '#5a3d22', { weight: 800 });
    text('(EVERY MONTH)', 0, 72, 12, '#8a6a46', { weight: 700 });
    ctx.restore();
    // board / easel (left)
    drawBoard(t, s);
    // lamp glow
    g = ctx.createRadialGradient(170, 1000, 20, 170, 1000, 700);
    g.addColorStop(0, 'rgba(255,200,120,0.35)'); g.addColorStop(1, 'rgba(255,200,120,0)');
    ctx.fillStyle = g; ctx.fillRect(-400, 300, 1300, 1300);
  }

  function drawBoard(t, s) {
    ctx.save(); ctx.translate(40, 260);
    ctx.strokeStyle = '#2c1d14'; ctx.lineWidth = 14; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(60, 400); ctx.lineTo(20, 820); ctx.moveTo(280, 400); ctx.lineTo(320, 820); ctx.stroke();
    rr(0, 0, 340, 420, 10); ctx.fillStyle = '#f5f1e8'; ctx.fill(); ctx.lineWidth = 10; ctx.strokeStyle = '#8b6440'; ctx.stroke();
    if (s.board === 'bars') {
      text('TREAT DELIVERY', 170, 44, 30, '#2a2a2a', { weight: 900 });
      text('SPEED (sec)', 170, 78, 22, '#666', { weight: 700 });
      const drop = s.barDrop || 0;
      const vals = [0.85, 0.7, 0.55, 0.25];
      const labels = ['Q1', 'Q2', 'Q3', 'NOW'];
      for (let i = 0; i < 4; i++) {
        let v = vals[i]; if (i === 3) v = lerp(0.25, 0.04, drop);
        const bh = v * 260, bx = 40 + i * 70;
        ctx.fillStyle = i === 3 ? '#e04848' : '#4a90d9';
        ctx.fillRect(bx, 370 - bh, 50, bh);
        text(labels[i], bx + 25, 395, 17, '#444', { weight: 800 });
      }
      ctx.strokeStyle = '#e04848'; ctx.lineWidth = 7; ctx.beginPath();
      ctx.moveTo(65, 370 - 0.85 * 260 - 18); ctx.lineTo(135, 370 - 0.7 * 260 - 18); ctx.lineTo(205, 370 - 0.55 * 260 - 18); ctx.lineTo(275, 370 - lerp(0.25, 0.04, drop) * 260 - 18); ctx.stroke();
    } else if (s.board === 'pie') {
      text('LAP', 170, 40, 30, '#2a2a2a'); text('AVAILABILITY', 170, 74, 26, '#2a2a2a');
      const cx = 170, cy = 245, r = 120, k = clamp(s.pieK ?? 1);
      ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fillStyle = '#ddd'; ctx.fill();
      ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * 0.4 * k); ctx.closePath(); ctx.fillStyle = '#e04848'; ctx.fill();
      text('40%', cx, cy, 44, '#fff', { stroke: 8, strokeColor: '#222' });
      text('"at work" 60%', cx, 395, 20, '#666', { weight: 800 });
    } else {
      text('AGENDA', 170, 50, 32, '#2a2a2a');
      ['1. Treats', '2. Laps', '3. [REDACTED]', '4. Ear scratches'].forEach((l, i) => text(l, 40, 120 + i * 62, 26, '#333', { align: 'left', weight: 700 }));
    }
    ctx.restore();
  }

  function drawDesk(t, s) {
    let g = ctx.createLinearGradient(0, 1240, 0, 1920);
    g.addColorStop(0, '#6d4126'); g.addColorStop(0.06, '#5a321c'); g.addColorStop(1, '#2e180c');
    ctx.fillStyle = g; ctx.fillRect(-400, 1240, W + 800, 900);
    ctx.fillStyle = '#8a5634'; ctx.fillRect(-400, 1236, W + 800, 14);
    // wood grain
    ctx.strokeStyle = 'rgba(0,0,0,0.12)'; ctx.lineWidth = 3;
    for (let i = 0; i < 12; i++) { ctx.beginPath(); const y = 1300 + i * 52; ctx.moveTo(-400, y); ctx.bezierCurveTo(200, y + 18, 700, y - 18, 1480, y + 6); ctx.stroke(); }
    // lamp
    ctx.save(); ctx.translate(150, 1240);
    ctx.fillStyle = '#1f3d2e'; ellipse(0, 0, 70, 16); ctx.fill();
    ctx.strokeStyle = '#b08a3a'; ctx.lineWidth = 10; ctx.beginPath(); ctx.moveTo(0, -5); ctx.lineTo(-10, -170); ctx.lineTo(40, -230); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-20, -210); ctx.lineTo(110, -260); ctx.lineTo(120, -200); ctx.lineTo(10, -175); ctx.closePath(); ctx.fillStyle = '#1f5a3e'; ctx.fill();
    ctx.restore();
    // mug
    ctx.save(); ctx.translate(880, 1250);
    rr(-55, -120, 110, 125, 14); ctx.fillStyle = '#fafafa'; ctx.fill();
    ctx.strokeStyle = '#fafafa'; ctx.lineWidth = 14; ctx.beginPath(); ctx.arc(60, -60, 26, -1.2, 1.2); ctx.stroke();
    text("WORLD'S", 0, -88, 18, '#c03030'); text('BEST', 0, -64, 22, '#c03030'); text('BOSS', 0, -38, 22, '#c03030');
    ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 5;
    for (let i = 0; i < 2; i++) { ctx.beginPath(); const ph = t * 2 + i * 2; ctx.moveTo(-15 + i * 30, -130); ctx.bezierCurveTo(-30 + i * 30 + Math.sin(ph) * 12, -170, 0 + i * 30 + Math.cos(ph) * 12, -200, -10 + i * 30, -240); ctx.stroke(); }
    ctx.restore();
    // review document on desk
    ctx.save(); ctx.translate(540, 1330); ctx.rotate(-0.03);
    rr(-150, -60, 300, 190, 4); ctx.fillStyle = '#fffdf6'; ctx.fill();
    text('PERFORMANCE REVIEW', 0, -35, 20, '#333');
    ctx.fillStyle = '#bbb'; for (let i = 0; i < 6; i++) ctx.fillRect(-120, -5 + i * 22, 240 - (i % 3) * 40, 6);
    ctx.restore();
    // nameplate
    ctx.save(); ctx.translate(540, 1560);
    ctx.fillStyle = '#2a1a10'; ctx.beginPath(); ctx.moveTo(-260, 70); ctx.lineTo(260, 70); ctx.lineTo(240, -70); ctx.lineTo(-240, -70); ctx.closePath(); ctx.fill();
    const gg = ctx.createLinearGradient(0, -55, 0, 55); gg.addColorStop(0, '#f3d27a'); gg.addColorStop(0.5, '#c99a32'); gg.addColorStop(1, '#f0cc6e');
    rr(-225, -55, 450, 110, 6); ctx.fillStyle = gg; ctx.fill();
    text('B. PURRKINS', 0, -16, 46, '#3a2608', { font: '"DejaVu Serif", serif', weight: 700 });
    text('HEAD OF HOUSEHOLD', 0, 30, 22, '#3a2608', { weight: 800 });
    ctx.restore();
  }

  // Landlord's nervous hands at the bottom of frame (we never see the face)
  function drawLandlordHands(t) {
    for (const side of [-1, 1]) {
      ctx.save(); ctx.translate(540 + side * 170, 1830 + Math.sin(t * 9 + side) * 4);
      ctx.fillStyle = '#4f6f9e'; rr(-90, 30, 180, 200, 30); ctx.fill();
      ctx.fillStyle = '#e8b896'; ellipse(0, 0, 80, 55); ctx.fill();
      for (let i = 0; i < 4; i++) {
        const tap = Math.max(0, Math.sin(t * 14 - i * 0.9 + side)) * 10;
        ellipse(-48 + i * 32, -48 - tap, 15, 26); ctx.fill();
      }
      ctx.restore();
    }
  }

  // ---------- the star ----------
  function drawCat(t, s) {
    const hx = 540, hy = 760;
    ctx.save();
    // whole-body tilt (melting) around desk pivot
    ctx.translate(540, 1250); ctx.rotate(s.tilt || 0); ctx.translate(-540, -1250);
    const vib = s.purr ? Math.sin(t * 150) * 2.2 * s.purr : 0;
    const tremble = s.tremble ? noise1(t * 40) * 6 * s.tremble : 0;
    ctx.translate(vib + tremble, (s.lean || 0) * -20);

    // tail
    ctx.save(); ctx.strokeStyle = FUR_SH; ctx.lineCap = 'round'; ctx.lineWidth = 46;
    const sw = Math.sin(t * 2.2) * 40;
    ctx.beginPath(); ctx.moveTo(760, 1200); ctx.bezierCurveTo(880, 1150, 900 + sw, 980, 860 + sw, 900); ctx.stroke();
    ctx.strokeStyle = GINGER; ctx.lineWidth = 48; ctx.beginPath(); ctx.moveTo(870 + sw * 0.95, 935); ctx.lineTo(860 + sw, 900); ctx.stroke();
    ctx.restore();

    // body
    let g = ctx.createRadialGradient(500, 1020, 40, 540, 1120, 300);
    g.addColorStop(0, '#fbf0dc'); g.addColorStop(1, FUR_SH);
    ellipse(540, 1130, 270, 250); ctx.fillStyle = g; ctx.fill();
    ctx.lineWidth = 5; ctx.strokeStyle = LINE; ctx.stroke();
    // chest fluff
    ctx.fillStyle = '#fffaf0'; ellipse(540, 1020, 120, 90); ctx.fill();
    // ginger ticking on body
    ctx.strokeStyle = 'rgba(216,145,74,0.45)'; ctx.lineWidth = 16; ctx.lineCap = 'round';
    for (const [x1, y1, x2, y2] of [[320, 1060, 360, 1110], [760, 1060, 720, 1110], [300, 1150, 345, 1185], [780, 1150, 735, 1185]]) { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); }
    // fanny pack strap + pack
    ctx.strokeStyle = '#7b5230'; ctx.lineWidth = 22; ctx.beginPath(); ctx.moveTo(355, 930); ctx.quadraticCurveTo(540, 1080, 720, 1210); ctx.stroke();
    ctx.save(); ctx.translate(615, 1135); ctx.rotate(0.55);
    rr(-80, -45, 160, 90, 24); ctx.fillStyle = '#b5824f'; ctx.fill(); ctx.strokeStyle = '#6e4724'; ctx.lineWidth = 5; ctx.stroke();
    ctx.strokeStyle = '#d8b07a'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-60, -12); ctx.lineTo(60, -12); ctx.stroke();
    ctx.fillStyle = GOLD; ellipse(50, -12, 7, 10); ctx.fill();
    ctx.restore();

    // arms + paws
    const pl = s.pawL || { x: 405, y: 1252 }, pr = s.pawR || { x: 675, y: 1252 };
    drawArm(395, 960, pl, s.quoteL, t);
    drawArm(685, 960, pr, s.quoteR, t);

    // ---- head ----
    ctx.save();
    ctx.translate(hx, hy); ctx.rotate(s.headRot || 0); ctx.translate(-hx, -hy);
    // ears (viewer-right = character's LEFT ear has the notch)
    drawEar(hx - 150, hy - 120, -1, false, s);
    drawEar(hx + 150, hy - 120, 1, true, s);
    g = ctx.createRadialGradient(hx - 60, hy - 80, 30, hx, hy, 260);
    g.addColorStop(0, '#fff6e6'); g.addColorStop(1, FUR_SH);
    ellipse(hx, hy, 235, 198); ctx.fillStyle = g; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = LINE; ctx.stroke();
    // cheek fluff
    ctx.fillStyle = FUR;
    for (const sd of [-1, 1]) { ctx.beginPath(); ctx.moveTo(hx + sd * 200, hy + 30); ctx.lineTo(hx + sd * 262, hy + 70); ctx.lineTo(hx + sd * 215, hy + 90); ctx.lineTo(hx + sd * 255, hy + 120); ctx.lineTo(hx + sd * 180, hy + 140); ctx.closePath(); ctx.fill(); }
    // forehead ticking stripes
    ctx.strokeStyle = 'rgba(216,145,74,0.55)'; ctx.lineWidth = 14;
    for (const dx of [-55, 0, 55]) { ctx.beginPath(); ctx.moveTo(hx + dx * 1.3, hy - 190); ctx.lineTo(hx + dx, hy - 140); ctx.stroke(); }
    // messy tuft after scratching
    if (s.tuft) { ctx.fillStyle = FUR; ctx.beginPath(); ctx.moveTo(hx - 30, hy - 192); ctx.lineTo(hx - 10, hy - 192 - 60 * s.tuft); ctx.lineTo(hx + 10, hy - 195); ctx.lineTo(hx + 35, hy - 195 - 45 * s.tuft); ctx.lineTo(hx + 45, hy - 190); ctx.fill(); }

    // blush
    if (s.blush) { ctx.fillStyle = `rgba(255,120,140,${0.55 * s.blush})`; ellipse(hx - 135, hy + 50, 50, 26); ctx.fill(); ellipse(hx + 135, hy + 50, 50, 26); ctx.fill(); }

    // eyes
    drawEye(hx - 88, hy - 25, EYE_R, s, -1, t);
    drawEye(hx + 88, hy - 25, EYE_L, s, 1, t);

    // unibrow: the signature judgmental stripe
    const ang = s.brow ?? 0.4; // >0 angry V, <0 worried
    const by = hy - 95 - (s.browLift || 0) * 25;
    ctx.strokeStyle = GINGER_D; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = 30;
    ctx.beginPath(); ctx.moveTo(hx - 150, by - ang * 30); ctx.quadraticCurveTo(hx - 75, by - 20 - ang * 8, hx, by + ang * 26); ctx.quadraticCurveTo(hx + 75, by - 20 - ang * 8, hx + 150, by - ang * 30); ctx.stroke();

    // muzzle
    ctx.fillStyle = '#fffaf2'; ellipse(hx - 42, hy + 72, 52, 40); ctx.fill(); ellipse(hx + 42, hy + 72, 52, 40); ctx.fill();
    ctx.fillStyle = 'rgba(120,80,50,0.5)';
    for (const [dx, dy] of [[-60, 65], [-40, 80], [-68, 88], [60, 65], [40, 80], [68, 88]]) { ellipse(hx + dx, hy + dy, 3.5, 3.5); ctx.fill(); }
    // mouth
    const m = s.mouth || 0;
    if (m > 0.05) {
      ctx.fillStyle = '#5a1e22'; ellipse(hx, hy + 102 + m * 18, 30 + m * 10, 6 + m * 34); ctx.fill();
      ctx.fillStyle = '#e07080'; ellipse(hx, hy + 112 + m * 34, 18 + m * 6, 4 + m * 12); ctx.fill();
    }
    ctx.strokeStyle = LINE; ctx.lineWidth = 5; ctx.lineCap = 'round';
    const smile = s.smile || 0;
    ctx.beginPath(); ctx.moveTo(hx, hy + 78); ctx.lineTo(hx, hy + 96);
    ctx.moveTo(hx, hy + 96); ctx.quadraticCurveTo(hx - 24, hy + 112 + smile * 14, hx - 50, hy + 96 - smile * 12);
    ctx.moveTo(hx, hy + 96); ctx.quadraticCurveTo(hx + 24, hy + 112 + smile * 14, hx + 50, hy + 96 - smile * 12);
    ctx.stroke();
    // nose
    ctx.fillStyle = '#e88a98'; ctx.beginPath(); ctx.moveTo(hx - 22, hy + 55); ctx.lineTo(hx + 22, hy + 55); ctx.lineTo(hx, hy + 80); ctx.closePath(); ctx.fill();
    // whiskers
    ctx.strokeStyle = 'rgba(255,255,255,0.95)'; ctx.lineWidth = 3.5;
    for (const sd of [-1, 1]) for (let i = 0; i < 3; i++) {
      const wy = hy + 70 + i * 16, wob = Math.sin(t * 3 + i) * 3;
      ctx.beginPath(); ctx.moveTo(hx + sd * 85, wy); ctx.quadraticCurveTo(hx + sd * 170, wy - 12 + i * 8 + wob, hx + sd * 265, wy - 20 + i * 18 + wob); ctx.stroke();
    }
    // glasses (gold half-moon, perched low)
    drawGlasses(hx, hy, s);
    ctx.restore(); // head
    ctx.restore(); // body
  }

  function drawEar(x, y, sd, notch, s) {
    const perk = (s.earsBack || 0);
    ctx.save(); ctx.translate(x, y); ctx.rotate(sd * (0.15 + perk * 0.6));
    ctx.beginPath(); ctx.moveTo(-sd * 70, 60); ctx.lineTo(-sd * 10, -110);
    if (notch) { ctx.lineTo(sd * 8, -82); ctx.lineTo(sd * 22, -96); }
    ctx.lineTo(sd * 75, 40); ctx.closePath();
    ctx.fillStyle = FUR_SH; ctx.fill(); ctx.strokeStyle = LINE; ctx.lineWidth = 5; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-sd * 40, 45); ctx.lineTo(-sd * 6, -62); ctx.lineTo(sd * 45, 35); ctx.closePath(); ctx.fillStyle = '#f2a9b4'; ctx.fill();
    ctx.restore();
  }

  function drawEye(x, y, col, s, sd, t) {
    const mode = s.eyes || 'normal';
    if (mode === 'happy') {
      ctx.strokeStyle = LINE; ctx.lineWidth = 9; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.arc(x, y + 12, 34, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke();
      return;
    }
    const big = mode === 'wide' ? 1.22 : 1;
    const rx = 46 * big, ry = 50 * big;
    ctx.save();
    ellipse(x, y, rx, ry); ctx.fillStyle = '#20140c'; ctx.fill();
    ellipse(x, y, rx - 5, ry - 5); const g = ctx.createRadialGradient(x, y + 10, 5, x, y, ry);
    g.addColorStop(0, '#fffbe0'); g.addColorStop(0.35, col); g.addColorStop(1, shade(col)); ctx.fillStyle = g; ctx.fill();
    const look = s.look || { x: 0, y: 0 };
    let pw = (s.pupil ?? 0.45) * 30, ph = 40 * big;
    if (mode === 'wide') { pw = 11; ph = 11; }
    ellipse(x + look.x * 12, y + look.y * 10, pw, ph); ctx.fillStyle = '#0c0805'; ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.95)'; ellipse(x - 14 + look.x * 8, y - 18, 11, 13); ctx.fill(); ellipse(x + 12, y + 14, 5, 5); ctx.fill();
    // lids
    let open = s.lid ?? 0.75;
    const blinkT = (s.blinkAt != null) ? s.blinkAt : -1;
    if (blinkT >= 0) open *= blinkT;
    else { const ph = (t + 0.3) % 3.7; if (ph < 0.12) open *= Math.abs(ph - 0.06) / 0.06; }
    if (mode === 'wide') open = 1;
    if (open < 1) {
      ctx.beginPath(); ellipse(x, y, rx + 3, ry + 3); ctx.clip();
      const lidY = y - ry - 4 + (2 * ry + 8) * (1 - open);
      const slant = (s.brow ?? 0.4) * 18 * sd;
      ctx.fillStyle = FUR_SH; ctx.beginPath();
      ctx.moveTo(x - rx - 10, y - ry - 10); ctx.lineTo(x + rx + 10, y - ry - 10);
      ctx.lineTo(x + rx + 10, lidY - slant); ctx.lineTo(x - rx - 10, lidY + slant); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = LINE; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(x - rx - 10, lidY + slant); ctx.lineTo(x + rx + 10, lidY - slant); ctx.stroke();
    }
    ctx.restore();
  }
  function shade(hex) { const n = parseInt(hex.slice(1), 16); const r = (n >> 16) * 0.55, g = ((n >> 8) & 255) * 0.55, b = (n & 255) * 0.55; return `rgb(${r | 0},${g | 0},${b | 0})`; }

  function drawGlasses(hx, hy, s) {
    ctx.save();
    const gy = hy + 5 + (s.glassesDrop || 0);
    ctx.translate(hx, gy); ctx.rotate(s.glassesRot || 0); ctx.translate(-hx, -gy);
    ctx.strokeStyle = GOLD; ctx.lineWidth = 7; ctx.fillStyle = 'rgba(220,240,255,0.18)';
    for (const sd of [-1, 1]) {
      const cx = hx + sd * 88;
      ctx.beginPath(); ctx.moveTo(cx - 60, gy); ctx.lineTo(cx + 60, gy); ctx.arc(cx, gy, 60, 0, Math.PI, false); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx + sd * 60, gy); ctx.lineTo(cx + sd * 125, gy - 45); ctx.stroke();
      ctx.save(); ctx.globalAlpha = 0.5; ctx.strokeStyle = '#fff'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(cx - 30, gy + 14); ctx.lineTo(cx - 12, gy + 36); ctx.stroke(); ctx.restore();
    }
    ctx.beginPath(); ctx.moveTo(hx - 28, gy); ctx.quadraticCurveTo(hx, gy - 14, hx + 28, gy); ctx.stroke();
    ctx.restore();
  }

  function drawArm(sx, sy, p, quote, t) {
    ctx.strokeStyle = LINE; ctx.lineCap = 'round'; ctx.lineWidth = 92;
    ctx.beginPath(); ctx.moveTo(sx, sy); ctx.quadraticCurveTo((sx + p.x) / 2, (sy + p.y) / 2 + 30, p.x, p.y); ctx.stroke();
    ctx.strokeStyle = FUR_SH; ctx.lineWidth = 82; ctx.stroke();
    ctx.fillStyle = '#fffaf0'; ellipse(p.x, p.y, 52, 40); ctx.fill(); ctx.strokeStyle = LINE; ctx.lineWidth = 4; ctx.stroke();
    if (quote) { // "air quote" toe wiggle
      const w = Math.sin(t * 22) * 10;
      ctx.fillStyle = '#fffaf0';
      for (const dx of [-16, 16]) { rr(p.x + dx - 11, p.y - 78 + (dx > 0 ? w : -w), 22, 50, 11); ctx.fill(); ctx.stroke(); }
    } else {
      ctx.strokeStyle = 'rgba(122,82,51,0.6)'; ctx.lineWidth = 3;
      for (const dx of [-17, 0, 17]) { ctx.beginPath(); ctx.moveTo(p.x + dx, p.y - 30); ctx.lineTo(p.x + dx, p.y - 12); ctx.stroke(); }
    }
  }

  function drawScratchHand(t, k, scratching) {
    // human arm from bottom-right reaching to the top of the head
    const tx = 560 + (scratching ? Math.sin(t * 26) * 28 : 0), ty = 545 + (scratching ? Math.cos(t * 26) * 10 : 0);
    const x = lerp(1250, tx, k), y = lerp(2050, ty, k);
    ctx.save();
    ctx.strokeStyle = '#4f6f9e'; ctx.lineCap = 'round'; ctx.lineWidth = 130;
    ctx.beginPath(); ctx.moveTo(x + 520, y + 950); ctx.quadraticCurveTo(x + 420, y + 300, x + 90, y + 90); ctx.stroke();
    ctx.translate(x, y); ctx.rotate(-0.75);
    ctx.fillStyle = '#e8b896'; ellipse(0, 40, 75, 95); ctx.fill();
    const curl = scratching ? (Math.sin(t * 26) * 0.5 + 0.5) * 14 : 0;
    for (let i = 0; i < 4; i++) { rr(-58 + i * 32, -70 + curl * (i % 2), 26, 90, 13); ctx.fill(); }
    rr(55, 10, 28, 70, 14); ctx.fill();
    ctx.restore();
  }

  // ---------- overlays ----------
  function caption(t) {
    for (const c of CAPS) {
      if (t >= c.a && t < c.b) {
        const k = backOut((t - c.a) / 0.12);
        ctx.save(); ctx.translate(540, 1395); ctx.scale(lerp(0.6, 1, k), lerp(0.6, 1, k));
        const words = c.text.split(' ');
        ctx.font = '900 76px Inter, sans-serif';
        const widths = words.map(w => ctx.measureText(w + ' ').width);
        let total = widths.reduce((a, b) => a + b, 0), x = -total / 2;
        words.forEach((w, i) => {
          const hl = HILITE.some(h => w.toUpperCase().includes(h));
          text(w, x + widths[i] / 2 - 10, 0, 76, hl ? '#ffd52e' : '#ffffff', { stroke: 16, strokeColor: '#111' });
          x += widths[i];
        });
        ctx.restore();
      }
    }
  }
  function stamp(t, t0, label, x, y, rot, col = '#d62828', size = 70) {
    if (t < t0) return;
    const k = clamp((t - t0) / 0.14);
    const sc = lerp(3, 1, k * k);
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sc, sc); ctx.globalAlpha = clamp(k * 1.5) * 0.92;
    ctx.font = `900 ${size}px Inter, sans-serif`;
    const lines = label.split('\n');
    const w = Math.max(...lines.map(l => ctx.measureText(l).width)) + 50, h = lines.length * size * 1.05 + 30;
    ctx.strokeStyle = col; ctx.lineWidth = 12; rr(-w / 2, -h / 2, w, h, 16); ctx.stroke();
    lines.forEach((l, i) => text(l, 0, -h / 2 + 15 + size * 0.55 + i * size * 1.05, size, col));
    ctx.restore();
  }
  function vignette(a, col = '0,0,0') {
    const g = ctx.createRadialGradient(540, 900, 300, 540, 960, 1250);
    g.addColorStop(0, `rgba(${col},0)`); g.addColorStop(1, `rgba(${col},${a})`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }

  // ---------- captions (words timed across each voice line) ----------
  const LINES = {
    L1: ['SIT DOWN.', "THIS WON'T", 'TAKE LONG.'],
    L2: ['TREAT DELIVERY.', 'AVERAGE RESPONSE', 'TIME: 4 SECONDS.', 'UNACCEPTABLE.'],
    L3: ['LAP AVAILABILITY:', '40 PERCENT.', 'YOU WERE', '"AT WORK."'],
    L4: ['NOTED.'],
    L5: ['THE VACUUM', 'INCIDENT.', "WE DON'T TALK", 'ABOUT IT.'],
    L6: ['AND FINALLY...', 'EAR SCRATCHES.'],
    L7: ["NO. DON'T.", "DON'T YOU DARE.", 'I AM A PROFESSIO—'],
    L8: ['exceeds', 'expectations...'],
    L9a: ['*AHEM*'],
    L9: ["YOU'RE PROMOTED.", 'SAME SALARY.'],
    L10: ['NOTED.'],
  };
  const HILITE = ['UNACCEPTABLE', '4', '40', '"AT', 'WORK."', 'NOTED', 'VACUUM', 'EAR', 'SCRATCHES', 'PROMOTED', 'SALARY', 'DARE', 'EXPECTATIONS'];
  const CAPS = [];
  for (const [k, chunks] of Object.entries(LINES)) {
    const [a, b] = T[k]; const tot = chunks.reduce((s, c) => s + c.length + 4, 0); let cur = a;
    chunks.forEach((c, i) => { const d = (b - a) * (c.length + 4) / tot; CAPS.push({ a: cur, b: i === chunks.length - 1 ? b + 0.25 : cur + d, text: c }); cur += d; });
  }

  // ---------- direction: per-time camera + performance ----------
  function direct(t) {
    const cam = { cx: 540, cy: 960, z: 1, rot: 0, shake: 0 };
    const s = { board: 'agenda', brow: 0.45, lid: 0.7, mouth: mouthAt(t), look: { x: 0, y: 0 } };
    const L = (k) => T[k];

    if (t < T.s2) { // S1 HOOK — close-up, paper slides to camera
      cam.cy = 830; cam.z = lerp(1.75, 1.95, ss(0, T.s2, t));
      s.brow = 0.7; s.lid = 0.62;
      const k = ss(0, 0.55, t);
      s.pawR = { x: lerp(675, 600, Math.sin(k * Math.PI)), y: lerp(1252, 1290, Math.sin(k * Math.PI)) };
    } else if (t < T.s3) { // S2 wide: the chart
      cam.z = lerp(1.0, 1.06, ss(T.s2, T.s3, t)); cam.cy = 980;
      s.board = 'bars';
      const [a, b] = L('L2'); const u = (t - a) / (b - a);
      s.barDrop = ss(0.72, 0.85, u);
      s.look = { x: -0.8, y: 0 };
      if (u > 0.05 && u < 0.7) { s.pawL = { x: lerp(405, 300, ss(0.05, 0.2, u)), y: lerp(1252, 900, ss(0.05, 0.2, u)) }; s.look = { x: -1, y: -0.3 }; }
      if (u >= 0.72) { s.brow = 0.95; s.lid = 0.5; s.look = { x: 0, y: 0 }; }
      if (u >= 0.72 && u < 0.8) cam.shake = 10;
    } else if (t < T.s4) { // S3 lap availability + air quotes + stamp + "Noted."
      cam.cx = 470; cam.cy = 820; cam.z = 1.35;
      s.board = 'pie'; s.pieK = ss(T.s3, T.s3 + 0.8, t);
      const [a, b] = L('L3'); const u = (t - a) / (b - a);
      if (u > 0.55 && t < T.stamp1) {
        const k = ss(0.55, 0.65, u);
        s.pawL = { x: lerp(405, 290, k), y: lerp(1252, 820, k) }; s.pawR = { x: lerp(675, 790, k), y: lerp(1252, 820, k) };
        s.quoteL = s.quoteR = k > 0.8; s.brow = 0.8; s.lid = 0.55;
      }
      if (t >= T.L4[0] - 0.3) { cam.cx = 540; cam.cy = 790; cam.z = 1.85; s.brow = 0.6; s.look = { x: 0, y: 0 };
        const [a4, b4] = L('L4'); const v = clamp((t - a4) / (b4 - a4 + 0.3));
        s.blinkAt = 1 - Math.sin(clamp(v) * Math.PI) * 0.95; }
    } else if (t < T.s5) { // S4 the vacuum incident
      const h = T.hits; let z = 1.35;
      if (t >= h[0]) z = 1.6; if (t >= h[1]) z = 2.0; if (t >= h[2]) z = 2.7;
      cam.z = z; cam.cy = lerp(900, 735, clamp((z - 1.35) / 1.35));
      cam.shake = (t - h[0] < 0.2 || (t >= h[1] && t - h[1] < 0.2) || (t >= h[2] && t - h[2] < 0.35)) ? 16 : 3;
      s.eyes = 'wide'; s.brow = -0.6; s.browLift = 1; s.tremble = 1; s.earsBack = 1; s.mouth = Math.max(s.mouth, t >= h[2] ? 0.75 : 0.3); s.flash = (t >= h[2] && t - h[2] < 0.15) ? 0.9 : 0;
      cam.z += Math.sin(t * 1.5) * 0.02;
    } else if (t < T.s6) { // S5 ear scratches → meltdown
      cam.cy = 860; cam.z = 1.4;
      const [a6] = L('L6');
      s.brow = 0.35; s.lid = 0.7;
      const reach = ss(T.L6[1] - 0.4, T.touch, t);
      s.handK = reach;
      if (t >= T.L7[0] && t < T.touch) { s.eyes = 'wide'; s.brow = -0.7; s.browLift = 1; s.lean = 1; s.earsBack = 0.7; s.tremble = 0.6; s.look = { x: 0.6, y: -0.6 };
        s.pawL = { x: 430, y: 1050 }; s.pawR = { x: 650, y: 1050 }; }
      if (t >= T.touch) {
        const k = ss(T.touch, T.touch + 2.6, t);
        s.eyes = 'happy'; s.brow = -0.35; s.blush = ss(T.touch, T.touch + 0.6, t); s.purr = 1; s.smile = 1; s.mouth = 0;
        s.glassesDrop = k * 55; s.glassesRot = k * 0.25; s.tilt = -0.42 * k; s.headRot = -0.25 * k; s.earsBack = -0.2;
        s.scratching = true; s.tuft = k; cam.z = lerp(1.4, 1.6, k); cam.rot = -0.04 * k;
        if (t >= T.L8[0]) s.mouth = mouthAt(t) * 0.4;
      }
    } else { // S6 recovery, Slow Glasses Push, "Noted."
      const [p0, p1] = T.push;
      s.tuft = 1; s.brow = 0.55; s.lid = 0.65;
      const k = ss(p0, p1, t);
      s.glassesDrop = lerp(40, 0, k); s.glassesRot = lerp(0.2, 0, k);
      cam.cy = lerp(860, 790, ss(T.s6, T.L10[0], t)); cam.z = lerp(1.45, 2.05, ss(T.s6, T.L10[1], t));
      if (t >= p0 - 0.2 && t < p1 + 0.25) { const e = ss(p0 - 0.2, p0 + 0.2, t) * (1 - ss(p1, p1 + 0.25, t)); s.pawR = { x: lerp(675, 600, e), y: lerp(1252, 790 + lerp(40, 0, k), e) }; }
      if (t >= T.L10[0] - 0.1) { const v = clamp((t - T.L10[0] + 0.1) / 0.9); s.blinkAt = 1 - Math.sin(v * Math.PI) * 0.95; s.brow = 0.7; }
    }
    return { cam, s };
  }

  window.renderFrame = function (t) {
    const { cam, s } = direct(t);
    ctx.save();
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
    const shx = cam.shake ? noise1(t * 60) * cam.shake : 0, shy = cam.shake ? noise1(t * 60 + 99) * cam.shake : 0;
    ctx.translate(W / 2 + shx, H / 2 + shy); ctx.scale(cam.z, cam.z); ctx.rotate(cam.rot); ctx.translate(-cam.cx, -cam.cy);
    drawRoom(t, s);
    drawCat(t, s);
    drawDesk(t, s);
    if (t >= T.s2 && t < T.s3) drawLandlordHands(t);
    if (s.handK > 0) drawScratchHand(t, s.handK, s.scratching);
    if (t >= T.touch && t < T.s6) { // floating hearts
      for (let i = 0; i < 8; i++) { const ph = ((t - T.touch) * 0.6 + i / 8) % 1; const hx = 540 + Math.sin(i * 2.3 + t * 2) * 260, hy = 700 - ph * 500;
        ctx.globalAlpha = Math.sin(ph * Math.PI); text('♥', hx, hy, 70, '#ff5d8f'); ctx.globalAlpha = 1; }
    }
    ctx.restore();

    // screen-space overlays
    if (t >= T.s4 && t < T.s5) { ctx.fillStyle = 'rgba(120,0,0,0.25)'; ctx.fillRect(0, 0, W, H); vignette(0.95); }
    else vignette(0.55);
    if (t >= T.touch && t < T.s6) { ctx.fillStyle = `rgba(255,160,200,${0.18 * ss(T.touch, T.touch + 0.8, t)})`; ctx.fillRect(0, 0, W, H); }

    if (t < T.s2) { // hook title + paper sliding toward the viewer
      const k = backOut((t - 0.1) / 0.35);
      if (t > 0.1) { ctx.save(); ctx.translate(540, 240); ctx.scale(k, k); rr(-430, -70, 860, 140, 18); ctx.fillStyle = '#d62828'; ctx.fill();
        text('ANNUAL PERFORMANCE REVIEW', 0, 0, 48, '#fff'); ctx.restore(); }
      const p = ss(0, 0.6, t);
      ctx.save(); ctx.translate(540, lerp(1350, 1700, p)); ctx.rotate(lerp(0.02, -0.08, p)); const sc = lerp(0.55, 1.25, p); ctx.scale(sc, sc);
      rr(-300, -190, 600, 380, 6); ctx.fillStyle = '#fffdf6'; ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 30; ctx.fill(); ctx.shadowBlur = 0;
      text('EMPLOYEE: THE LANDLORD', 0, -140, 32, '#222');
      ctx.fillStyle = '#bbb'; for (let i = 0; i < 5; i++) ctx.fillRect(-250, -90 + i * 40, 500 - (i % 2) * 120, 10);
      ctx.restore();
    }
    // stamp insert: NEEDS IMPROVEMENT
    if (t >= T.stamp1 - 0.2 && t < T.L4[0] - 0.3) {
      ctx.fillStyle = '#2e180c'; ctx.fillRect(0, 0, W, H);
      ctx.save(); ctx.translate(540, 960); ctx.rotate(-0.05);
      rr(-430, -620, 860, 1240, 10); ctx.fillStyle = '#fffdf6'; ctx.fill();
      text('PERFORMANCE REVIEW', 0, -540, 54, '#222');
      text('Employee: The Landlord', 0, -470, 36, '#555', { weight: 700 });
      const rows = [['Treat delivery', '✗'], ['Lap availability', '✗'], ['Vacuum incident', '✗✗✗'], ['Ear scratches', 'pending']];
      rows.forEach(([a, b], i) => { text(a, -370, -330 + i * 110, 44, '#333', { align: 'left', weight: 700 }); text(b, 370, -330 + i * 110, 44, '#c62828', { align: 'right' }); });
      ctx.restore();
      stamp(t, T.stamp1, 'NEEDS\nIMPROVEMENT', 540, 1150, -0.2, '#d62828', 84);
      if (t - T.stamp1 > 0 && t - T.stamp1 < 0.15) { ctx.fillStyle = 'rgba(0,0,0,0.15)'; ctx.fillRect(0, 0, W, H); }
    }
    if (t >= T.L5[0] && t < T.s5) { // redacted bar
      const k = ss(T.L5[0] + 0.2, T.L5[0] + 0.5, t);
      ctx.save(); ctx.translate(540, 300); ctx.rotate(-0.04);
      ctx.fillStyle = '#000'; ctx.fillRect(-460 * k, -70, 920 * k, 140);
      if (k > 0.9) text('CLASSIFIED', 0, 0, 80, '#e03030', { stroke: 4, strokeColor: '#000' });
      ctx.restore();
    }
    if (t >= T.touch && t < T.s6) {
      stamp(t, T.stamps[0], 'EXCEEDS\nEXPECTATIONS', 330, 360, -0.25, '#1fa34a', 64);
      stamp(t, T.stamps[1], 'EXCEEDS\nEXPECTATIONS', 760, 560, 0.2, '#1fa34a', 64);
      stamp(t, T.stamps[2], 'EMPLOYEE\nOF THE YEAR', 540, 1700, -0.08, '#1fa34a', 80);
    }
    if (t < T.endcard) caption(t);
    // end card
    if (t >= T.endcard) {
      const k = ss(T.endcard, T.endcard + 0.35, t);
      ctx.fillStyle = `rgba(20,12,8,${0.82 * k})`; ctx.fillRect(0, 0, W, H);
      const b = backOut((t - T.endcard) / 0.4);
      ctx.save(); ctx.translate(540, 760); ctx.scale(b, b);
      text('PURRKINS & CO.', 0, 0, 104, '#ffd52e', { stroke: 14, strokeColor: '#111', font: '"DejaVu Serif", serif', weight: 700 });
      text('Ep.1 — The Performance Review', 0, 110, 48, '#fff', { weight: 700 });
      ctx.restore();
      if (t > T.endcard + 0.5) {
        const b2 = backOut((t - T.endcard - 0.5) / 0.35);
        ctx.save(); ctx.translate(540, 1150); ctx.scale(b2, b2);
        rr(-380, -70, 760, 140, 70); ctx.fillStyle = '#d62828'; ctx.fill();
        text('FOLLOW FOR EP.2: THE INTERN', 0, 0, 44, '#fff'); ctx.restore();
        text('Rate YOUR landlord in the comments ↓', 540, 1330, 40, '#fff', { weight: 800 });
      }
    }
  };
})();
