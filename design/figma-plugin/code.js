/* ============================================================================
   ARABICA AURORA — Figma builder
   Membangun seluruh console (5 view, 1440x900) + token + komponen
   sebagai layer FIGMA NATIVE yang bisa diedit. Tanpa gambar tempel.
   ========================================================================== */

const COL = {
  field: '#0A0A0C', surface: '#141416', sunken: '#101012', raised: '#1C1C20',
  text: '#FFFFFF', sec: '#A8A8B3', muted: '#8A8A93', hair: '#5A5A63',
  accent: '#FF6B4A', accentSoft: '#2A1B16', action: '#C2410C',
  pos: '#4ADE80', danger: '#FF5C5C',
  defect: '#FDA4AF', longberry: '#FCD34D', peaberry: '#93C5FD', premium: '#6EE7B7',
  aA: '#2E8B7A', aB: '#3B3B8F', aC: '#E8552E'
};

const RAIL = 90, X0 = 122, W = 1286;

const SPEC = {
  kpiY: 96, kpiH: 149,
  gridY: 265, chartH: 387, chartW: 902, sideW: 360, sideH: 594, deckY: 676, deckH: 195
};

let F = { body: { family: 'Inter', style: 'Regular' }, medium: { family: 'Inter', style: 'Regular' }, semi: { family: 'Inter', style: 'Bold' }, bold: { family: 'Inter', style: 'Bold' }, mono: { family: 'Roboto Mono', style: 'Regular' }, monoBold: { family: 'Roboto Mono', style: 'Bold' } };
let styles = {};

/* ---------------------------------------------------------------- helpers */
function rgb(hex) {
  const h = hex.replace('#', '');
  return { r: parseInt(h.slice(0, 2), 16) / 255, g: parseInt(h.slice(2, 4), 16) / 255, b: parseInt(h.slice(4, 6), 16) / 255 };
}
function solid(hex, a) { return { type: 'SOLID', color: rgb(hex), opacity: a === undefined ? 1 : a }; }
function white(a) { return { type: 'SOLID', color: { r: 1, g: 1, b: 1 }, opacity: a }; }
function grad(a, b, vertical) {
  return {
    type: 'GRADIENT_LINEAR',
    gradientTransform: vertical ? [[0, 1, 0], [-1, 0, 1]] : [[1, 0, 0], [0, 1, 0]],
    gradientStops: [
      { position: 0, color: Object.assign(rgb(a), { a: 1 }) },
      { position: 1, color: Object.assign(rgb(b), { a: 1 }) }
    ]
  };
}
function shadow(y, blur, alpha) {
  return { type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: alpha }, offset: { x: 0, y: y }, radius: blur, spread: 0, visible: true, blendMode: 'NORMAL' };
}

function frame(parent, name, x, y, w, h, o) {
  o = o || {};
  const f = figma.createFrame();
  f.name = name;
  parent.appendChild(f);
  f.resize(w, h);
  f.x = x; f.y = y;
  f.fills = o.fill ? [o.fill].flat() : [];
  if (o.r !== undefined) f.cornerRadius = o.r;
  f.clipsContent = o.clip !== false;
  if (o.stroke) {
    f.strokes = [solid(o.stroke, o.strokeA === undefined ? 1 : o.strokeA)];
    f.strokeWeight = o.strokeW || 1;
    f.strokeAlign = 'INSIDE';
  }
  if (o.shadow) f.effects = [o.shadow];
  if (o.blur) f.effects = (f.effects || []).concat([{ type: 'LAYER_BLUR', radius: o.blur, visible: true }]);
  return f;
}

function rect(parent, name, x, y, w, h, fill, r) {
  const n = figma.createRectangle();
  n.name = name;
  parent.appendChild(n);
  n.resize(w, h);
  n.x = x; n.y = y;
  n.fills = fill ? [fill] : [];
  if (r) n.cornerRadius = r;
  return n;
}

function ell(parent, name, x, y, w, h, fill) {
  const n = figma.createEllipse();
  n.name = name;
  parent.appendChild(n);
  n.resize(w, h);
  n.x = x; n.y = y;
  n.fills = fill ? [fill] : [];
  return n;
}

/* text --------------------------------------------------------------- */
function tx(parent, name, chars, o) {
  o = o || {};
  const t = figma.createText();
  parent.appendChild(t);
  t.name = name;
  t.fontName = o.font || F.body;
  t.fontSize = o.size || 13;
  t.characters = String(chars);
  if (o.color) t.fills = [solid(o.color)];
  if (o.caps) t.textCase = 'UPPER';
  t.letterSpacing = { unit: 'PIXELS', value: o.ls === undefined ? 0 : o.ls };
  t.lineHeight = { unit: 'PIXELS', value: o.lh || Math.round((o.size || 13) * 1.45) };
  t.textAutoResize = 'HEIGHT';
  t.resize(o.w || 200, t.height);
  t.x = o.x || 0; t.y = o.y || 0;
  if (o.align) t.textAlignHorizontal = o.align;
  if (o.style) {
    try { t.textStyleId = o.style.id; } catch (e) { }
  }
  return t;
}

/* bootstrap ---------------------------------------------------------- */
async function boot() {
  const avail = await figma.listAvailableFontsAsync();
  const has = (fam, st) => avail.some(a => a.fontName.family === fam && a.fontName.style === st);
  const pick = (cands) => { for (const c of cands) if (has(c.family, c.style)) return c; return cands[cands.length - 1]; };

  const BODY = has('Plus Jakarta Sans', 'Regular') ? 'Plus Jakarta Sans' : 'Inter';
  const MONO = has('JetBrains Mono', 'Regular') ? 'JetBrains Mono' : 'Roboto Mono';

  F = {
    body: pick([{ family: BODY, style: 'Regular' }, { family: 'Inter', style: 'Regular' }]),
    medium: pick([{ family: BODY, style: 'Medium' }, { family: 'Inter', style: 'Medium' }, { family: 'Inter', style: 'Regular' }]),
    semi: pick([{ family: BODY, style: 'SemiBold' }, { family: 'Inter', style: 'Semi Bold' }, { family: 'Inter', style: 'Bold' }]),
    bold: pick([{ family: BODY, style: 'Bold' }, { family: 'Inter', style: 'Bold' }]),
    xbold: pick([{ family: BODY, style: 'ExtraBold' }, { family: 'Inter', style: 'Extra Bold' }, { family: 'Inter', style: 'Bold' }]),
    mono: pick([{ family: MONO, style: 'Regular' }, { family: 'Roboto Mono', style: 'Regular' }]),
    monoMed: pick([{ family: MONO, style: 'Medium' }, { family: 'Roboto Mono', style: 'Medium' }, { family: 'Roboto Mono', style: 'Regular' }]),
    monoBold: pick([{ family: MONO, style: 'Bold' }, { family: 'Roboto Mono', style: 'Bold' }])
  };

  const seen = new Set();
  for (const k in F) {
    const key = F[k].family + '|' + F[k].style;
    if (seen.has(key)) continue;
    seen.add(key);
    await figma.loadFontAsync(F[k]);
  }
}

/* variables ---------------------------------------------------------- */
function makeVariables() {
  let coll = figma.variables.getLocalVariableCollections().find(c => c.name === 'Arabica Aurora');
  if (!coll) coll = figma.variables.createVariableCollection('Arabica Aurora');
  const mode = coll.modes[0].modeId;
  coll.renameMode(mode, 'Dark');

  const defs = {
    'color/field': COL.field, 'color/surface': COL.surface, 'color/surface-sunken': COL.sunken,
    'color/surface-raised': COL.raised, 'color/text-primary': COL.text, 'color/text-secondary': COL.sec,
    'color/text-muted': COL.muted, 'color/hairline': COL.hair, 'color/accent': COL.accent,
    'color/action': COL.action, 'color/positive': COL.pos, 'color/danger': COL.danger,
    'class/defect': COL.defect, 'class/longberry': COL.longberry,
    'class/peaberry': COL.peaberry, 'class/premium': COL.premium,
    'aurora/teal': COL.aA, 'aurora/indigo': COL.aB, 'aurora/ember': COL.aC
  };
  const have = figma.variables.getLocalVariables().filter(v => v.variableCollectionId === coll.id).map(v => v.name);
  for (const name in defs) {
    if (have.indexOf(name) >= 0) continue;
    const v = figma.variables.createVariable(name, coll, 'COLOR');
    v.setValueForMode(mode, Object.assign(rgb(defs[name]), { a: 1 }));
  }
  return coll;
}

/* text styles -------------------------------------------------------- */
function makeStyles() {
  const defs = {
    'Display/Metric': { font: F.monoBold, size: 26, lh: 30, ls: -0.5 },
    'Display/Verdict': { font: F.bold, size: 17, lh: 22, ls: -0.2 },
    'Heading/Section': { font: F.bold, size: 19, lh: 24, ls: -0.3 },
    'Heading/Card': { font: F.bold, size: 15.5, lh: 20, ls: -0.15 },
    'Label/Upper': { font: F.bold, size: 10.5, lh: 14, ls: 1.05 },
    'Body/Base': { font: F.body, size: 13, lh: 19, ls: 0 },
    'Body/Medium': { font: F.medium, size: 12.5, lh: 18, ls: 0 },
    'Caption': { font: F.body, size: 11.5, lh: 16, ls: 0 },
    'Numeric/MD': { font: F.monoMed, size: 12, lh: 16, ls: 0 },
    'Numeric/SM': { font: F.mono, size: 11, lh: 15, ls: 0 }
  };
  const existing = figma.getLocalTextStyles();
  for (const name in defs) {
    let st = existing.find(s => s.name === name);
    if (!st) st = figma.createTextStyle();
    st.name = name;
    const d = defs[name];
    st.fontName = d.font;
    st.fontSize = d.size;
    st.lineHeight = { unit: 'PIXELS', value: d.lh };
    st.letterSpacing = { unit: 'PIXELS', value: d.ls };
    styles[name] = st;
  }
}

/* icons -------------------------------------------------------------- */
const ICONS = {
  grid: '<rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/>',
  layers: '<path d="M3 7.5 12 3l9 4.5-9 4.5-9-4.5Z"/><path d="M3 12.2 12 16.7l9-4.5"/><path d="M3 16.9 12 21.4l9-4.5"/>',
  trend: '<path d="M4 17.5 9 11l4 3.5L20 6"/><path d="M15.5 6H20v4.5"/>',
  clock: '<circle cx="12" cy="12" r="8.4"/><path d="M12 7.6V12l3 1.9"/>',
  gear: '<circle cx="12" cy="12" r="3.1"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.2 5.2l2.1 2.1M16.7 16.7l2.1 2.1M18.8 5.2l-2.1 2.1M7.3 16.7l-2.1 2.1"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/>',
  download: '<path d="M12 3.8v11.4"/><path d="m7.4 10.9 4.6 4.6 4.6-4.6"/><path d="M4.4 19.6h15.2"/>',
  play: '<path d="M5 3.5 19.5 12 5 20.5Z"/>',
  star: '<path d="m12 3.6 2.6 5.4 5.9.8-4.3 4.1 1.1 5.9L12 17l-5.3 2.8 1.1-5.9-4.3-4.1 5.9-.8Z"/>',
  warn: '<path d="M10.3 4.3 2.9 17.1a2 2 0 0 0 1.7 3h14.8a2 2 0 0 0 1.7-3L13.7 4.3a2 2 0 0 0-3.4 0Z"/><path d="M12 9.2v4.4"/>',
  bean: '<ellipse cx="12" cy="12" rx="7.6" ry="10"/><path d="M12 2.9c-3.1 4.4-3.1 13.8 0 18.2"/>'
};

function icon(parent, name, x, y, size, color, weight) {
  const body = ICONS[name] || '';
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="none" stroke="' + color + '" stroke-width="' + (weight || 1.8) + '" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>';
  const n = figma.createNodeFromSvg(svg);
  n.name = 'icon/' + name;
  parent.appendChild(n);
  n.x = x; n.y = y;
  return n;
}

/* atoms -------------------------------------------------------------- */
function pillText(parent, x, y, label, fg, bg, w) {
  const p = frame(parent, 'pill/' + label, x, y, w || (label.length * 6.6 + 18), 22, { r: 999, fill: bg });
  tx(p, 'label', label, { font: F.monoMed, size: 11.5, color: fg, x: 9, y: 3.5, lh: 15 });
  return p;
}

function card(parent, name, x, y, w, h, r) {
  const c = frame(parent, name, x, y, w, h, {
    r: r || 20,
    fill: grad(COL.surface, COL.sunken, true),
    stroke: '#FFFFFF', strokeA: 0.07,
    shadow: shadow(20, 60, 0.5)
  });
  return c;
}

/* shell: rail + topbar ----------------------------------------------- */
function shell(page, title, frameName, xOffset) {
  const v = frame(page, frameName, xOffset, 0, 1440, 900, { fill: solid(COL.field), clip: true });

  // aurora field
  const aur = frame(v, 'Aurora Field', 0, -80, 1440, 560, {});
  aur.fills = [];
  const g1 = ell(aur, 'glow/teal', -120, -140, 820, 460, solid(COL.aA, 0.30));
  g1.effects = [{ type: 'LAYER_BLUR', radius: 90, visible: true }];
  const g2 = ell(aur, 'glow/indigo', 320, -220, 900, 520, solid(COL.aB, 0.32));
  g2.effects = [{ type: 'LAYER_BLUR', radius: 100, visible: true }];
  const g3 = ell(aur, 'glow/ember', 1120, -120, 640, 420, solid(COL.aC, 0.22));
  g3.effects = [{ type: 'LAYER_BLUR', radius: 90, visible: true }];

  // rail
  const rail = frame(v, 'Rail', 0, 0, RAIL, 900, { fill: solid(COL.surface), stroke: '#FFFFFF', strokeA: 0.06 });
  const mark = frame(rail, 'Brand Mark', 21, 22, 48, 48, { r: 14, fill: grad(COL.accent, COL.action, true) });
  icon(mark, 'bean', 11, 11, 26, '#FFFFFF', 1.9);

  const navIcons = ['grid', 'layers', 'trend', 'clock', 'gear'];
  navIcons.forEach((n, i) => {
    const active = i === 0;
    const y = 96 + i * 56;
    const b = frame(rail, 'rail/' + n, 22, y, 46, 46, { r: 12, fill: active ? solid(COL.accent, 0.14) : null, stroke: active ? COL.accent : null, strokeA: 0.34 });
    icon(b, n, 13, 13, 20, active ? COL.accent : COL.muted, 1.8);
  });
  const add = frame(rail, 'rail/add', 23, 480, 44, 44, { r: 12, fill: white(0.03), stroke: '#FFFFFF', strokeA: 0.14 });
  icon(add, 'plus', 13, 13, 18, COL.sec, 2);
  const av = frame(rail, 'avatar/AF', 26, 838, 38, 38, { r: 999, fill: grad('#2E8B7A', '#1F6F63', true) });
  tx(av, 'initials', 'AF', { font: F.bold, size: 12.5, color: '#FFFFFF', x: 12, y: 10, lh: 18 });

  // topbar
  tx(v, 'Title', title, { font: F.bold, size: 19, color: COL.text, x: X0, y: 20, ls: -0.3, lh: 24 });
  tx(v, 'Subtitle', 'Klasifikasi mutu biji kopi · Skenario 60:20:20', { font: F.medium, size: 11.5, color: COL.muted, x: X0, y: 46, lh: 16 });

  const search = frame(v, 'Search', 662, 27, 340, 44, { r: 12, fill: white(0.045), stroke: '#FFFFFF', strokeA: 0.07 });
  icon(search, 'search', 14, 14, 15, COL.muted, 2);
  tx(search, 'placeholder', 'Cari batch, arsip, atau SKU mutu…', { font: F.body, size: 13, color: COL.muted, x: 42, y: 13, w: 280, lh: 18 });

  const dp = frame(v, 'Date Pill', 1018, 31, 196, 36, { r: 999, fill: white(0.04), stroke: '#FFFFFF', strokeA: 0.07 });
  ell(dp, 'dot', 14, 15, 6, 6, solid(COL.pos));
  tx(dp, 'date', 'Jumat, 27 Nov 2026', { font: F.semi, size: 12, color: COL.sec, x: 27, y: 9, lh: 17 });

  const op = frame(v, 'Operator', 1234, 20, 174, 58, {});
  const opAv = frame(op, 'avatar', 0, 10, 38, 38, { r: 999, fill: grad('#2E8B7A', '#1F6F63', true) });
  tx(opAv, 'initials', 'AF', { font: F.bold, size: 12.5, color: '#FFFFFF', x: 12, y: 10, lh: 18 });
  tx(op, 'name', 'Agus Farhan', { font: F.semi, size: 13, color: COL.text, x: 48, y: 12, lh: 18 });
  tx(op, 'role', 'Quality Lead', { font: F.medium, size: 11.5, color: COL.muted, x: 48, y: 30, lh: 16 });

  return v;
}

/* ============================ VIEW 1: DASHBOARD ====================== */
function kpiCard(parent, x, label, value, delta, up, sub, accentHex, spark, iconName) {
  const c = card(parent, 'KPI / ' + label, x, SPEC.kpiY, 306.5, SPEC.kpiH, 20);
  rect(c, 'accent bar', 0, 0, 306.5, 2, grad(accentHex, COL.surface, false), 0);
  tx(c, 'label', label, { font: F.bold, size: 10.5, color: COL.muted, x: 20, y: 18, caps: true, ls: 1.05, lh: 14 });
  const ico = frame(c, 'icon box', 258.5, 16, 28, 28, { r: 8, fill: white(0.05) });
  icon(ico, iconName, 7, 7, 14, COL.sec, 1.9);
  tx(c, 'value', value, { font: F.monoBold, size: 26, color: COL.text, x: 20, y: 43, ls: -0.6, lh: 30 });
  const dw = delta.length * 7 + 18;
  const d = frame(c, 'delta', 20 + (value.length * 15.6) + 10, 48, dw, 22, { r: 999, fill: up ? solid(COL.pos, 0.12) : solid(COL.danger, 0.12) });
  tx(d, 'delta text', delta, { font: F.monoMed, size: 11.5, color: up ? COL.pos : COL.danger, x: 9, y: 3.5, lh: 15 });
  tx(c, 'sub', sub, { font: F.medium, size: 11.5, color: COL.muted, x: 20, y: 112, lh: 16 });
  // sparkline
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="62" height="24" viewBox="0 0 62 24" fill="none"><path d="' + spark + '" stroke="' + accentHex + '" stroke-width="1.8" stroke-linecap="round"/></svg>';
  const sp = figma.createNodeFromSvg(svg);
  sp.name = 'sparkline';
  c.appendChild(sp);
  sp.x = 222; sp.y = 108;
  return c;
}

function buildDashboard(page) {
  const v = shell(page, 'Quality Console', 'View 01 · Dashboard', 0);

  kpiCard(v, X0, 'Batch Terinspeksi', '1.284', '+18,2%', true, '30 hari terakhir', '#2E8B7A', 'M1 19 11 15.5 21 16.8 31 11 41 12.4 51 6.5 61 3.4', 'layers');
  kpiCard(v, X0 + 326.5, 'Akurasi Model', '96,8%', '+2,4%', true, 'EfficientNet-B0 + SVM', '#0071EF', 'M1 15 11 16.4 21 12 31 13.2 41 9 51 8.2 61 5', 'trend');
  kpiCard(v, X0 + 653, 'Mutu Premium', '82,4%', '+6,1%', true, '1.058 lot lolos grade 1', '#7047EB', 'M1 20 11 17 21 18 31 12.6 41 10 51 7.4 61 4.2', 'star');
  kpiCard(v, X0 + 979.5, 'Perlu Review', '3,2%', '−1,4%', false, '41 lot di bawah 55%', '#E8552E', 'M1 6 11 7.6 21 6.4 31 10.8 41 9.6 51 14 61 16.6', 'warn');

  /* --- chart card --- */
  const ch = card(v, 'Card / Statistik Inferensi', X0, SPEC.gridY, SPEC.chartW, SPEC.chartH, 24);
  tx(ch, 'title', 'Statistik Inferensi', { font: F.bold, size: 15.5, color: COL.text, x: 24, y: 20, ls: -0.15, lh: 20 });
  tx(ch, 'sub', 'Confidence per batch · model terpilih', { font: F.medium, size: 12, color: COL.muted, x: 24, y: 42, lh: 17 });

  const seg = frame(ch, 'Range Segmented', 700, 20, 178, 34, { r: 12, fill: white(0.045), stroke: '#FFFFFF', strokeA: 0.07 });
  ['1D', '1W', '1M', '1Y', 'MAX'].forEach((lbl, i) => {
    const on = lbl === '1M';
    const b = frame(seg, 'seg/' + lbl, 3 + i * 34.4, 3, 33, 28, { r: 9, fill: on ? solid(COL.accent, 0.18) : null });
    tx(b, 'l', lbl, { font: F.semi, size: 11, color: on ? COL.accent : COL.muted, x: 0, y: 7, w: 33, align: 'CENTER', lh: 15 });
  });

  tx(ch, 'headline', '96,8%', { font: F.monoBold, size: 27, color: COL.text, x: 24, y: 74, ls: -0.6, lh: 32 });
  const hd = frame(ch, 'head delta', 118, 82, 58, 22, { r: 999, fill: solid(COL.pos, 0.12) });
  tx(hd, 't', '+2,4%', { font: F.monoMed, size: 11.5, color: COL.pos, x: 9, y: 3.5, lh: 15 });
  tx(ch, 'head cap', '28 Okt – 27 Nov 2026', { font: F.medium, size: 12, color: COL.muted, x: 186, y: 85, lh: 17 });

  // plot
  const plot = frame(ch, 'Plot', 24, 112, 854, 216, {});
  // grid lines
  for (let i = 0; i <= 4; i++) {
    const yy = 20 + i * ((216 - 40) / 4);
    rect(plot, 'grid ' + i, 46, yy, 806, 1, white(i === 0 ? 0.12 : 0.07));
    tx(plot, 'ytick ' + i, Math.round(98 - i * 2.25) + '%', { font: F.mono, size: 10.5, color: COL.sec, x: 0, y: yy - 7, w: 38, align: 'RIGHT', lh: 14 });
  }
  const chartSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="806" height="176" viewBox="0 0 806 176" fill="none">' +
    '<defs><linearGradient id="ln" x1="0" y1="0" x2="806" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="#4ADE80"/><stop offset="0.42" stop-color="#FF4FA0"/><stop offset="1" stop-color="#FF7A45"/></linearGradient>' +
    '<linearGradient id="ar" x1="0" y1="0" x2="0" y2="176" gradientUnits="userSpaceOnUse"><stop stop-color="#FF4FA0" stop-opacity="0.34"/><stop offset="0.55" stop-color="#FF7A45" stop-opacity="0.1"/><stop offset="1" stop-color="#FF7A45" stop-opacity="0"/></linearGradient></defs>' +
    '<path d="M0 132 C30 126 60 120 90 116 C120 112 150 118 180 106 C210 94 240 96 270 88 C300 80 330 88 360 76 C390 64 420 70 450 62 C480 54 510 62 540 48 C570 34 600 44 630 34 C660 24 690 28 720 20 C750 12 780 14 806 8 L806 176 L0 176 Z" fill="url(#ar)"/>' +
    '<path d="M0 132 C30 126 60 120 90 116 C120 112 150 118 180 106 C210 94 240 96 270 88 C300 80 330 88 360 76 C390 64 420 70 450 62 C480 54 510 62 540 48 C570 34 600 44 630 34 C660 24 690 28 720 20 C750 12 780 14 806 8" stroke="url(#ln)" stroke-width="2.6" stroke-linecap="round"/>' +
    '<circle cx="806" cy="8" r="8" fill="#FF7A45" fill-opacity="0.16"/><circle cx="806" cy="8" r="3.6" fill="#FF7A45"/></svg>';
  const line = figma.createNodeFromSvg(chartSvg);
  line.name = 'area chart';
  ch.appendChild(line);
  line.x = 70; line.y = 132;
  rect(ch, 'threshold', 70, 208, 806, 1, white(0.22));
  tx(ch, 'threshold label', 'Ambang review 55%', { font: F.mono, size: 10.5, color: COL.sec, x: 700, y: 194, lh: 14 });
  ['28', '03', '09', '15', '21', '27'].forEach((d, i) => {
    tx(ch, 'xtick ' + d, d, { font: F.mono, size: 10.5, color: COL.sec, x: 62 + i * 155, y: 318, w: 40, lh: 14 });
  });

  rect(ch, 'footer rule', 24, 344, 854, 1, white(0.07));
  ell(ch, 'legend dot 1', 24, 360, 9, 9, grad('#FF4FA0', '#FF7A45', false));
  tx(ch, 'legend 1', 'Confidence rata-rata', { font: F.semi, size: 11.5, color: COL.sec, x: 39, y: 356, lh: 16 });
  ell(ch, 'legend dot 2', 206, 360, 9, 9, solid(COL.peaberry));
  tx(ch, 'legend 2', 'Batch diuji', { font: F.semi, size: 11.5, color: COL.sec, x: 221, y: 356, lh: 16 });
  tx(ch, 'legend 3', '--- Ambang review 55%', { font: F.mono, size: 11.5, color: COL.sec, x: 694, y: 356, lh: 16 });

  /* --- side card --- */
  const sc = card(v, 'Card / Hasil Klasifikasi', X0 + SPEC.chartW + 24, SPEC.gridY, SPEC.sideW, SPEC.sideH, 24);
  const thumb = frame(sc, 'Thumbnail', 19, 19, 56, 56, { r: 16, fill: grad('#2B1C0A', '#0B2318', true), stroke: '#FFFFFF', strokeA: 0.07 });
  icon(thumb, 'bean', 11, 11, 34, '#C98B57', 1.7);
  tx(sc, 'sample name', 'Arabica Gayo', { font: F.bold, size: 14, color: COL.text, x: 87, y: 24, ls: -0.2, lh: 19 });
  tx(sc, 'sample meta', 'Lot GJ-2291 · 224×224 px', { font: F.medium, size: 11.5, color: COL.muted, x: 87, y: 45, lh: 16 });
  pillText(sc, 285, 30, 'LIVE', COL.pos, solid(COL.pos, 0.12), 54);

  const vd = frame(sc, 'verdict', 19, 89, 322, 62, { r: 12, fill: white(0.03), stroke: '#FFFFFF', strokeA: 0.07 });
  tx(vd, 'label', 'Hasil klasifikasi', { font: F.bold, size: 10, color: COL.muted, x: 12, y: 10, caps: true, ls: 0.9, lh: 14 });
  tx(vd, 'verdict', 'ARABIKA PREMIUM', { font: F.bold, size: 17, color: COL.premium, x: 12, y: 28, ls: -0.2, lh: 22 });
  ell(vd, 'dot', 238, 36, 6, 6, solid(COL.premium));
  tx(vd, 'conf', '94,4%', { font: F.monoBold, size: 14, color: COL.text, x: 250, y: 31, lh: 18 });

  // donut
  const donut = frame(sc, 'Donut', 19, 165, 112, 112, {});
  ell(donut, 'track', 0, 0, 112, 112, white(0.07)).arcData = { startingAngle: 0, endingAngle: Math.PI * 2, innerRadius: 0.78 };
  const arc = ell(donut, 'arc premium', 0, 0, 112, 112, solid(COL.premium));
  arc.arcData = { startingAngle: -Math.PI / 2, endingAngle: -Math.PI / 2 + Math.PI * 2 * 0.944, innerRadius: 0.78 };
  tx(donut, 'val', '94,4%', { font: F.monoBold, size: 19, color: COL.text, x: 0, y: 38, w: 112, align: 'CENTER', lh: 24 });
  tx(donut, 'cap', 'PREMIUM', { font: F.semi, size: 9.5, color: COL.muted, x: 0, y: 60, w: 112, align: 'CENTER', ls: 0.6, lh: 13 });

  const legend = [['Premium', '94,4%', COL.premium], ['Longberry', '2,1%', COL.longberry], ['Peaberry', '1,7%', COL.peaberry], ['Defect', '1,8%', COL.defect]];
  legend.forEach((row, i) => {
    const y = 170 + i * 22;
    rect(sc, 'swatch ' + row[0], 147, y + 5, 8, 8, solid(row[2]), 2);
    tx(sc, 'cls ' + row[0], row[0], { font: F.semi, size: 11.5, color: COL.sec, x: 161, y: y, lh: 16 });
    tx(sc, 'val ' + row[0], row[1], { font: F.mono, size: 11, color: COL.text, x: 276, y: y, w: 65, align: 'RIGHT', lh: 16 });
  });

  const specRows = [['Backbone', 'EfficientNet-B0'], ['Latensi', '96,2 ms'], ['Fitur', '1280-D penultimate'], ['Split', '60:20:20']];
  specRows.forEach((row, i) => {
    const px = 19 + (i % 2) * 167, py = 288 + Math.floor(i / 2) * 46;
    const b = frame(sc, 'spec/' + row[0], px, py, 155, 40, { r: 8, fill: white(0.03), stroke: '#FFFFFF', strokeA: 0.07 });
    tx(b, 'k', row[0], { font: F.bold, size: 9.5, color: COL.muted, x: 9, y: 6, caps: true, ls: 0.7, lh: 13 });
    tx(b, 'v', row[1], { font: F.monoMed, size: 11.5, color: COL.text, x: 9, y: 20, w: 137, lh: 15 });
  });

  const bars = [['Defect', 1.8, COL.defect], ['Longberry', 2.1, COL.longberry], ['Peaberry', 1.7, COL.peaberry], ['Premium', 94.4, COL.premium]];
  bars.forEach((row, i) => {
    const y = 390 + i * 22;
    tx(sc, 'bar label ' + row[0], row[0], { font: F.semi, size: 11, color: COL.sec, x: 19, y: y, lh: 15 });
    rect(sc, 'track ' + row[0], 83, y + 4, 196, 6, white(0.07), 999);
    rect(sc, 'fill ' + row[0], 83, y + 4, Math.max(6, 196 * (row[1] / 100)), 6, solid(row[2]), 999);
    tx(sc, 'bar val ' + row[0], String(row[1]).replace('.', ',') + '%', { font: F.mono, size: 11, color: COL.text, x: 287, y: y, w: 54, align: 'RIGHT', lh: 15 });
  });

  const btn1 = frame(sc, 'Button / Jalankan Klasifikasi', 19, 528, 185, 44, { r: 12, fill: solid(COL.action), shadow: shadow(12, 30, 0.4) });
  icon(btn1, 'play', 44, 14, 15, '#FFFFFF', 2.1);
  tx(btn1, 'label', 'Jalankan Klasifikasi', { font: F.bold, size: 12.5, color: '#FFFFFF', x: 67, y: 12, lh: 18 });
  const btn2 = frame(sc, 'Button / Unduh', 214, 528, 127, 44, { r: 12, fill: white(0.04), stroke: '#FFFFFF', strokeA: 0.14 });
  icon(btn2, 'download', 30, 14, 15, COL.text, 2.1);
  tx(btn2, 'label', 'Unduh', { font: F.bold, size: 12.5, color: COL.text, x: 53, y: 12, lh: 18 });

  /* --- deck --- */
  const deck = card(v, 'Card / Kamus Mutu', X0, SPEC.deckY, SPEC.chartW, SPEC.deckH, 24);
  tx(deck, 'title', 'Kamus Mutu', { font: F.bold, size: 15.5, color: COL.text, x: 24, y: 17, ls: -0.15, lh: 20 });
  tx(deck, 'link', 'Lihat panduan lengkap →', { font: F.semi, size: 12, color: COL.accent, x: 700, y: 19, w: 178, align: 'RIGHT', lh: 17 });

  const kata = [
    ['Defect', 'Tidak layak · reject', 'Biji pecah, hitam, atau berjamur. Skor mutu di bawah ambang SCAA.', COL.defect],
    ['Longberry', 'Bentuk linear', 'Biji memanjang dengan alur tengah tajam. Ukuran tidak seragam.', COL.longberry],
    ['Peaberry', 'Biji bulat', 'Biji tunggal bulat tanpa belahan ganda. Densitas tinggi.', COL.peaberry],
    ['Premium', 'Grade 1 · specialty', 'Biji utuh seragam, warna konsisten, lolos sortir primer.', COL.premium]
  ];
  kata.forEach((k, i) => {
    const mx = 24 + i * 216.5;
    const mini = frame(deck, 'Mini / ' + k[0], mx, 48, 204.5, 111, { r: 16, fill: white(0.025), stroke: '#FFFFFF', strokeA: 0.07 });
    ell(mini, 'dot', 13, 15, 7, 7, solid(k[3]));
    tx(mini, 'title', k[0], { font: F.bold, size: 12.5, color: COL.text, x: 27, y: 11, ls: 0.1, lh: 17 });
    tx(mini, 'grade', k[1], { font: F.mono, size: 11, color: COL.sec, x: 13, y: 34, w: 178, lh: 15 });
    tx(mini, 'body', k[2], { font: F.body, size: 11.5, color: COL.muted, x: 13, y: 54, w: 178, lh: 17 });
  });

  return v;
}

/* ============================ VIEW 2: BATCH ========================== */
function buildBatch(page) {
  const v = shell(page, 'Batch & Arsip', 'View 02 · Batch', 1600);
  tx(v, 'head', 'Batch & Arsip', { font: F.bold, size: 19, color: COL.text, x: X0, y: 96, ls: -0.3, lh: 24 });
  tx(v, 'sub', '128 lot terdaftar · 1.284 citra terinspeksi', { font: F.medium, size: 12.5, color: COL.muted, x: X0, y: 123, lh: 17 });

  ['Semua', 'Premium', 'Longberry', 'Peaberry', 'Defect'].forEach((c, i) => {
    const on = i === 0;
    const w = c.length * 6.8 + 24;
    const chip = frame(v, 'chip/' + c, 806 + i * (w + 7), 104, w, 30, { r: 999, fill: on ? solid(COL.accent, 0.14) : white(0.035), stroke: on ? COL.accent : '#FFFFFF', strokeA: on ? 0.4 : 0.07 });
    tx(chip, 'l', c, { font: F.semi, size: 11.5, color: on ? COL.accent : COL.sec, x: 0, y: 7, w: w, align: 'CENTER', lh: 16 });
  });
  const nb = frame(v, 'Button / Batch baru', X0 + 1204, 100, 82, 38, { r: 12, fill: solid(COL.action) });
  tx(nb, 'l', 'Batch baru', { font: F.bold, size: 12, color: '#FFFFFF', x: 0, y: 10, w: 82, align: 'CENTER', lh: 17 });

  const tbl = card(v, 'Tabel Batch', X0, 156, W, 604, 24);
  const cols = [['Lot', 20, 150, 'LEFT'], ['Backbone', 190, 190, 'LEFT'], ['Hasil', 380, 150, 'LEFT'], ['Confidence', 560, 110, 'RIGHT'], ['Latensi', 690, 100, 'RIGHT'], ['Status', 810, 120, 'LEFT'], ['Waktu', 1050, 130, 'RIGHT']];
  cols.forEach(c => {
    tx(tbl, 'th ' + c[0], c[0], { font: F.bold, size: 10, color: COL.muted, x: c[1], y: 20, w: c[2], align: c[3], caps: true, ls: 1, lh: 14 });
  });
  rect(tbl, 'thead rule', 20, 42, W - 40, 1, white(0.08));

  const rows = [
    ['GJ-2291', 'EfficientNet-B0', 'Premium', '94,4%', '96,2 ms', 'ok', '27 Nov 16:40'],
    ['GJ-2290', 'EfficientNet-B0', 'Premium', '93,1%', '94,8 ms', 'ok', '27 Nov 16:12'],
    ['GJ-2289', 'MobileNetV3-Small', 'Longberry', '88,7%', '61,3 ms', 'ok', '27 Nov 15:58'],
    ['GJ-2288', 'EfficientNet-B0', 'Peaberry', '91,2%', '97,1 ms', 'ok', '27 Nov 15:31'],
    ['GJ-2287', 'ShuffleNetV2', 'Premium', '90,5%', '54,7 ms', 'ok', '27 Nov 15:02'],
    ['GJ-2286', 'EfficientNet-B0', 'Defect', '52,4%', '95,9 ms', 'warn', '27 Nov 14:44'],
    ['GJ-2285', 'MobileNetV3-Small', 'Premium', '92,8%', '60,2 ms', 'ok', '27 Nov 14:20'],
    ['GJ-2284', 'EfficientNet-B0', 'Longberry', '86,4%', '96,8 ms', 'ok', '27 Nov 13:55'],
    ['GJ-2283', 'ShuffleNetV2', 'Defect', '49,8%', '55,4 ms', 'bad', '27 Nov 13:31'],
    ['GJ-2282', 'EfficientNet-B0', 'Premium', '95,1%', '97,4 ms', 'ok', '27 Nov 13:08']
  ];
  const pillMap = { ok: ['Valid', COL.premium, 0.12], warn: ['Review', COL.longberry, 0.12], bad: ['Ditolak', COL.defect, 0.12] };
  rows.forEach((r, i) => {
    const y = 54 + i * 52;
    if (i % 2 === 0) rect(tbl, 'row bg ' + i, 12, y - 6, W - 24, 50, white(0.02), 10);
    tx(tbl, 'lot ' + i, r[0], { font: F.monoMed, size: 12.5, color: COL.text, x: 20, y: y + 4, w: 150, lh: 17 });
    tx(tbl, 'bb ' + i, r[1], { font: F.body, size: 12.5, color: COL.sec, x: 190, y: y + 4, w: 190, lh: 17 });
    tx(tbl, 'hasil ' + i, r[2], { font: F.semi, size: 12.5, color: COL.text, x: 380, y: y + 4, w: 150, lh: 17 });
    tx(tbl, 'conf ' + i, r[3], { font: F.mono, size: 12, color: COL.text, x: 560, y: y + 4, w: 110, align: 'RIGHT', lh: 17 });
    tx(tbl, 'lat ' + i, r[4], { font: F.mono, size: 12, color: COL.sec, x: 690, y: y + 4, w: 100, align: 'RIGHT', lh: 17 });
    const pm = pillMap[r[5]];
    const pl = frame(tbl, 'status ' + i, 810, y + 1, 74, 22, { r: 999, fill: solid(pm[1], pm[2]) });
    ell(pl, 'd', 9, 8, 5, 5, solid(pm[1]));
    tx(pl, 't', pm[0], { font: F.bold, size: 10.5, color: pm[1], x: 19, y: 4, lh: 14 });
    tx(tbl, 'waktu ' + i, r[6], { font: F.mono, size: 11.5, color: COL.muted, x: 1050, y: y + 4, w: 130, align: 'RIGHT', lh: 16 });
    rect(tbl, 'rule ' + i, 20, y + 44, W - 40, 1, white(0.045));
  });
  return v;
}

/* ============================ VIEW 3: MODEL ========================== */
function buildModel(page) {
  const v = shell(page, 'Performa Model', 'View 03 · Model', 3200);
  tx(v, 'head', 'Performa Model', { font: F.bold, size: 19, color: COL.text, x: X0, y: 96, ls: -0.3, lh: 24 });
  tx(v, 'sub', 'Skenario 60:20:20 · validasi silang 5-fold · CPU 2 thread', { font: F.medium, size: 12.5, color: COL.muted, x: X0, y: 123, lh: 17 });

  ['60:20:20', '70:15:15', '80:10:10'].forEach((c, i) => {
    const on = i === 0;
    const chip = frame(v, 'chip/' + c, 1082 + i * 106, 100, 100, 30, { r: 999, fill: on ? solid(COL.accent, 0.14) : white(0.035), stroke: on ? COL.accent : '#FFFFFF', strokeA: on ? 0.4 : 0.07 });
    tx(chip, 'l', c, { font: F.monoMed, size: 11.5, color: on ? COL.accent : COL.sec, x: 0, y: 7, w: 100, align: 'CENTER', lh: 16 });
  });

  const models = [
    ['EfficientNet-B0', 'BEST', '96,8%', '0,962', '1280', '#FF6B4A'],
    ['MobileNetV3-Small', 'RINGAN', '94,1%', '0,934', '576', '#0071EF'],
    ['ShuffleNetV2', 'TERCEPAT', '92,3%', '0,915', '1024', '#7047EB']
  ];
  models.forEach((m, i) => {
    const c = card(v, 'Model / ' + m[0], X0 + i * 434, 156, 418, 210, 20);
    rect(c, 'ring', 0, 0, 418, 2, solid(m[5]), 0);
    tx(c, 'name', m[0], { font: F.bold, size: 13, color: COL.text, x: 18, y: 18, ls: -0.15, lh: 18 });
    tx(c, 'tag', m[1], { font: F.bold, size: 9.5, color: COL.muted, x: 320, y: 20, w: 80, align: 'RIGHT', caps: true, ls: 1, lh: 14 });
    tx(c, 'acc', m[2], { font: F.monoBold, size: 27, color: COL.text, x: 18, y: 44, ls: -0.6, lh: 32 });
    tx(c, 'f1', 'Macro-F1', { font: F.medium, size: 11.5, color: COL.sec, x: 18, y: 92, lh: 16 });
    tx(c, 'f1v', m[3], { font: F.mono, size: 11.5, color: COL.text, x: 300, y: 92, w: 100, align: 'RIGHT', lh: 16 });
    tx(c, 'ft', 'Fitur penultimate', { font: F.medium, size: 11.5, color: COL.sec, x: 18, y: 114, lh: 16 });
    tx(c, 'ftv', m[4] + '-D', { font: F.mono, size: 11.5, color: COL.text, x: 300, y: 114, w: 100, align: 'RIGHT', lh: 16 });
    rect(c, 'trk', 18, 148, 382, 6, white(0.07), 999);
    rect(c, 'bar', 18, 148, 382 * (parseFloat(m[2].replace(',', '.')) / 100), 6, solid(m[5]), 999);
    tx(c, 'lat', 'Latensi rata-rata 96,2 ms', { font: F.mono, size: 10.5, color: COL.muted, x: 18, y: 166, lh: 15 });
  });

  const tbl = card(v, 'Tabel Skenario', X0, 390, W, 358, 24);
  tx(tbl, 'title', 'Perbandingan skenario', { font: F.bold, size: 14, color: COL.text, x: 22, y: 18, lh: 19 });
  tx(tbl, 'sub', 'Akurasi makro terhadap 4 kelas mutu', { font: F.medium, size: 11.5, color: COL.muted, x: 22, y: 38, lh: 16 });
  const cols = [['Skenario', 22, 200, 'LEFT'], ['Latih', 260, 100, 'RIGHT'], ['Val', 400, 100, 'RIGHT'], ['Uji', 540, 100, 'RIGHT'], ['Akurasi', 680, 120, 'RIGHT'], ['Macro-F1', 830, 120, 'RIGHT'], ['Status', 1000, 120, 'LEFT']];
  cols.forEach(c => tx(tbl, 'th ' + c[0], c[0], { font: F.bold, size: 10, color: COL.muted, x: c[1], y: 72, w: c[2], align: c[3], caps: true, ls: 1, lh: 14 }));
  rect(tbl, 'rule', 22, 96, W - 44, 1, white(0.08));
  const sk = [['60:20:20', '768', '256', '256', '96,8%', '0,962', 'Aktif', COL.premium],
  ['70:15:15', '896', '192', '192', '95,4%', '0,948', 'Cadangan', COL.peaberry],
  ['80:10:10', '1024', '128', '128', '94,2%', '0,936', 'Arsip', COL.longberry]];
  sk.forEach((r, i) => {
    const y = 106 + i * 54;
    tx(tbl, 'sk ' + i, r[0], { font: F.monoMed, size: 13, color: COL.text, x: 22, y: y + 6, w: 200, lh: 18 });
    [1, 2, 3, 4, 5].forEach(k => {
      tx(tbl, 'c' + i + k, r[k], { font: F.mono, size: 12, color: k === 4 || k === 5 ? COL.text : COL.sec, x: cols[k][1], y: y + 6, w: cols[k][2], align: 'RIGHT', lh: 17 });
    });
    const pl = frame(tbl, 'status ' + i, 1000, y + 3, 92, 22, { r: 999, fill: solid(r[7], 0.12) });
    ell(pl, 'd', 9, 8, 5, 5, solid(r[7]));
    tx(pl, 't', r[6], { font: F.bold, size: 10.5, color: r[7], x: 19, y: 4, lh: 14 });
    rect(tbl, 'rule ' + i, 22, y + 48, W - 44, 1, white(0.045));
  });
  return v;
}

/* ============================ VIEW 4: RIWAYAT ======================== */
function buildRiwayat(page) {
  const v = shell(page, 'Riwayat Inferensi', 'View 04 · Riwayat', 4800);
  tx(v, 'head', 'Riwayat Inferensi', { font: F.bold, size: 19, color: COL.text, x: X0, y: 96, ls: -0.3, lh: 24 });
  tx(v, 'sub', 'Sesi hari ini · 47 inferensi · rata-rata 94,7 ms', { font: F.medium, size: 12.5, color: COL.muted, x: X0, y: 123, lh: 17 });

  const cardTbl = card(v, 'Timeline', X0, 156, W, 700, 24);
  const items = [
    ['16:40', 'GJ-2291 · Arabica Gayo', 'EfficientNet-B0 · 96,2 ms', '94,4%', 'Premium', COL.premium],
    ['16:12', 'GJ-2290 · Arabica Gayo', 'EfficientNet-B0 · 94,8 ms', '93,1%', 'Premium', COL.premium],
    ['15:58', 'GJ-2289 · Arabica Lintong', 'MobileNetV3 · 61,3 ms', '88,7%', 'Longberry', COL.longberry],
    ['15:31', 'GJ-2288 · Arabica Toraja', 'EfficientNet-B0 · 97,1 ms', '91,2%', 'Peaberry', COL.peaberry],
    ['15:02', 'GJ-2287 · Arabica Gayo', 'ShuffleNetV2 · 54,7 ms', '90,5%', 'Premium', COL.premium],
    ['14:44', 'GJ-2286 · Robusta Lampung', 'EfficientNet-B0 · 95,9 ms', '52,4%', 'Perlu review', COL.longberry],
    ['14:20', 'GJ-2285 · Arabica Kintamani', 'MobileNetV3 · 60,2 ms', '92,8%', 'Premium', COL.premium],
    ['13:55', 'GJ-2284 · Arabica Aceh', 'EfficientNet-B0 · 96,8 ms', '86,4%', 'Longberry', COL.longberry],
    ['13:31', 'GJ-2283 · Robusta Temanggung', 'ShuffleNetV2 · 55,4 ms', '49,8%', 'Ditolak', COL.defect]
  ];
  items.forEach((r, i) => {
    const y = 24 + i * 72;
    tx(cardTbl, 'time ' + i, r[0], { font: F.mono, size: 11, color: COL.muted, x: 26, y: y + 8, w: 60, lh: 15 });
    ell(cardTbl, 'node ' + i, 100, y + 9, 8, 8, solid(r[5]));
    tx(cardTbl, 'lot ' + i, r[1], { font: F.semi, size: 12.5, color: COL.text, x: 124, y: y + 2, w: 420, lh: 17 });
    tx(cardTbl, 'meta ' + i, r[2], { font: F.mono, size: 11, color: COL.muted, x: 124, y: y + 22, w: 420, lh: 15 });
    tx(cardTbl, 'conf ' + i, r[3], { font: F.monoMed, size: 12, color: COL.text, x: 600, y: y + 8, w: 90, align: 'RIGHT', lh: 17 });
    const pl = frame(cardTbl, 'verdict ' + i, 720, y + 4, 130, 24, { r: 999, fill: solid(r[5], 0.12) });
    tx(pl, 't', r[4], { font: F.bold, size: 10.5, color: r[5], x: 0, y: 5, w: 130, align: 'CENTER', lh: 14 });
    rect(cardTbl, 'rule ' + i, 26, y + 56, W - 52, 1, white(0.045));
  });

  const sum = card(v, 'Ringkasan', X0 + W - 360, 156, 360, 700, 24);
  tx(sum, 'h', 'Ringkasan Sesi', { font: F.bold, size: 15, color: COL.text, x: 20, y: 20, lh: 20 });
  const stats = [['Total inferensi', '47'], ['Rata-rata confidence', '94,7%'], ['Perlu review', '2'], ['Latensi p95', '112 ms'], ['Throughput', '10,4 / menit']];
  stats.forEach((s, i) => {
    const y = 56 + i * 54;
    tx(sum, 'k ' + i, s[0], { font: F.medium, size: 11.5, color: COL.sec, x: 20, y: y, lh: 16 });
    tx(sum, 'v ' + i, s[1], { font: F.monoBold, size: 15, color: COL.text, x: 200, y: y - 2, w: 140, align: 'RIGHT', lh: 20 });
    rect(sum, 'r ' + i, 20, y + 34, 320, 1, white(0.045));
  });
  tx(sum, 'note', 'Semua inferensi memakai artefak terverifikasi checksum.', { font: F.body, size: 11, color: COL.muted, x: 20, y: 340, w: 320, lh: 16 });
  return v;
}

/* ============================ VIEW 5: PENGATURAN ===================== */
function buildPengaturan(page) {
  const v = shell(page, 'Pengaturan', 'View 05 · Pengaturan', 6400);
  tx(v, 'head', 'Pengaturan', { font: F.bold, size: 19, color: COL.text, x: X0, y: 96, ls: -0.3, lh: 24 });
  tx(v, 'sub', 'Konfigurasi inferensi · berlaku untuk sesi berikutnya', { font: F.medium, size: 12.5, color: COL.muted, x: X0, y: 123, lh: 17 });

  const save = frame(v, 'Button / Simpan', X0 + 1204, 100, 82, 38, { r: 12, fill: solid(COL.action) });
  tx(save, 'l', 'Simpan', { font: F.bold, size: 12, color: '#FFFFFF', x: 0, y: 10, w: 82, align: 'CENTER', lh: 17 });
  const reset = frame(v, 'Button / Kembalikan', X0 + 1100, 100, 96, 38, { r: 12, fill: white(0.04), stroke: '#FFFFFF', strokeA: 0.14 });
  tx(reset, 'l', 'Kembalikan', { font: F.bold, size: 12, color: COL.text, x: 0, y: 10, w: 96, align: 'CENTER', lh: 17 });

  const form = card(v, 'Form Konfigurasi', X0, 156, 620, 470, 24);
  const fields = [
    ['Backbone default', 'EfficientNet-B0', 'Memberi fitur 1280-D penultimate, akurasi tertinggi.'],
    ['Skenario split', '60:20:20', 'Split 60:20:20 dipakai di skripsi. Artefak lain tersedia.'],
    ['Ambang review (%)', '55', 'Di bawah nilai ini hasil ditandai perlu review.'],
    ['Ukuran input (px)', '224 × 224', 'Normalisasi otomatis saat unggah.']
  ];
  fields.forEach((f, i) => {
    const x = 22 + (i % 2) * 300, y = 24 + Math.floor(i / 2) * 118;
    tx(form, 'label ' + i, f[0], { font: F.bold, size: 10, color: COL.muted, x: x, y: y, w: 270, caps: true, ls: 1, lh: 14 });
    const input = frame(form, 'input ' + i, x, y + 22, 270, 40, { r: 8, fill: white(0.045), stroke: '#FFFFFF', strokeA: 0.07 });
    tx(input, 'v', f[1], { font: F.monoMed, size: 12, color: COL.text, x: 11, y: 11, w: 200, lh: 17 });
    tx(form, 'hint ' + i, f[2], { font: F.body, size: 10.5, color: COL.muted, x: x, y: y + 70, w: 270, lh: 15 });
  });

  rect(form, 'rule', 22, 262, 576, 1, white(0.08));
  tx(form, 'switch head', 'Opsi inferensi', { font: F.bold, size: 12.5, color: COL.text, x: 22, y: 282, lh: 17 });
  const switches = [['Simpan riwayat inferensi', 'Mencatat lot, confidence, dan latensi per sesi.', true], ['Tolak gambar di luar spesifikasi', 'Gate ukuran, rasio, dan ekstensi sebelum inferensi.', true], ['Mode gelap', 'Tema Arabica Aurora aktif.', true]];
  switches.forEach((s, i) => {
    const y = 310 + i * 48;
    tx(form, 'sw t ' + i, s[0], { font: F.semi, size: 12.5, color: COL.text, x: 22, y: y, w: 400, lh: 17 });
    tx(form, 'sw s ' + i, s[1], { font: F.body, size: 11, color: COL.muted, x: 22, y: y + 18, w: 420, lh: 15 });
    const sw = frame(form, 'switch ' + i, 554, y + 4, 44, 24, { r: 999, fill: s[2] ? solid(COL.accent, 0.25) : white(0.07), stroke: s[2] ? COL.accent : '#FFFFFF', strokeA: s[2] ? 0.45 : 0.07 });
    ell(sw, 'knob', s[2] ? 22 : 3, 3, 18, 18, solid(s[2] ? COL.accent : COL.sec));
  });

  const note = frame(form, 'split note', 22, 466, 576, 0, {});
  note.remove();

  const info = card(v, 'Catatan Sistem', X0 + 644, 156, 642, 470, 24);
  tx(info, 'h', 'Artefak Terpasang', { font: F.bold, size: 15, color: COL.text, x: 24, y: 22, lh: 20 });
  tx(info, 'sub', '3 backbone × 3 skenario · checksum SHA-256 terverifikasi', { font: F.medium, size: 11.5, color: COL.muted, x: 24, y: 45, lh: 16 });
  const arts = [['MobileNetV3-Small', '60:20:20', '37,4 MB', 'Verified'], ['ShuffleNetV2', '60:20:20', '18,2 MB', 'Verified'], ['EfficientNet-B0', '60:20:20', '49,5 MB', 'Verified'], ['EfficientNet-B0', '70:15:15', '46,4 MB', 'Verified'], ['EfficientNet-B0', '80:10:10', '53,1 MB', 'Verified']];
  arts.forEach((a, i) => {
    const y = 78 + i * 46;
    tx(info, 'a ' + i, a[0], { font: F.semi, size: 12, color: COL.text, x: 24, y: y, w: 220, lh: 17 });
    tx(info, 'b ' + i, a[1], { font: F.mono, size: 11.5, color: COL.sec, x: 250, y: y + 1, w: 90, lh: 16 });
    tx(info, 'c ' + i, a[2], { font: F.mono, size: 11.5, color: COL.sec, x: 360, y: y + 1, w: 90, align: 'RIGHT', lh: 16 });
    const pl = frame(info, 'pl ' + i, 500, y - 2, 86, 22, { r: 999, fill: solid(COL.premium, 0.12) });
    tx(pl, 't', a[3], { font: F.bold, size: 10, color: COL.premium, x: 0, y: 4, w: 86, align: 'CENTER', lh: 14 });
    rect(info, 'r ' + i, 24, y + 34, 594, 1, white(0.045));
  });
  const warn = frame(info, 'warning', 24, 344, 594, 96, { r: 12, fill: solid(COL.longberry, 0.07), stroke: COL.longberry, strokeA: 0.24 });
  icon(warn, 'warn', 16, 16, 16, COL.longberry, 1.9);
  tx(warn, 'h', 'Model berjalan di CPU, 2 thread', { font: F.semi, size: 12, color: COL.text, x: 42, y: 14, w: 520, lh: 17 });
  tx(warn, 'b', 'Inferensi per citra ±95 ms. Untuk batch besar, jalankan bertahap agar RSS tetap stabil di bawah 512 MB.', { font: F.body, size: 11, color: COL.sec, x: 16, y: 40, w: 562, lh: 16 });

  return v;
}

/* ============================ COMPONENT SHEET ======================== */
function buildTokens(page) {
  const sheet = frame(page, 'Token & Komponen', 8100, 0, 1440, 900, { fill: solid(COL.field) });
  tx(sheet, 'h', 'Arabica Aurora · Token & Komponen', { font: F.bold, size: 22, color: COL.text, x: 48, y: 40, ls: -0.4, lh: 28 });
  tx(sheet, 's', 'Sumber normatif: DESIGN.md · 28 warna · 11 skala tipografi · 13 komponen', { font: F.medium, size: 12.5, color: COL.muted, x: 48, y: 72, lh: 17 });

  const swatches = [
    ['field', COL.field], ['surface', COL.surface], ['sunken', COL.sunken], ['raised', COL.raised],
    ['text', COL.text], ['secondary', COL.sec], ['muted', COL.muted], ['hairline', COL.hair],
    ['accent', COL.accent], ['action', COL.action], ['positive', COL.pos], ['danger', COL.danger],
    ['defect', COL.defect], ['longberry', COL.longberry], ['peaberry', COL.peaberry], ['premium', COL.premium],
    ['aurora/teal', COL.aA], ['aurora/indigo', COL.aB], ['aurora/ember', COL.aC]
  ];
  swatches.forEach((s, i) => {
    const x = 48 + (i % 7) * 192, y = 112 + Math.floor(i / 7) * 92;
    const box = frame(sheet, 'swatch/' + s[0], x, y, 176, 56, { r: 12, fill: solid(s[1]), stroke: '#FFFFFF', strokeA: 0.12 });
    tx(sheet, 'sw name ' + i, s[0], { font: F.semi, size: 11.5, color: COL.text, x: x, y: y + 62, lh: 16 });
    tx(sheet, 'sw hex ' + i, s[1].toUpperCase(), { font: F.mono, size: 10.5, color: COL.muted, x: x, y: y + 78, lh: 14 });
  });

  const typeY = 412;
  const samples = [['Display/Metric', '1.284', F.monoBold, 26], ['Heading/Card', 'Statistik Inferensi', F.bold, 15.5], ['Body/Base', 'Klasifikasi mutu biji kopi · Skenario 60:20:20', F.body, 13], ['Label/Upper', 'Batch Terinspeksi', F.bold, 10.5]];
  samples.forEach((s, i) => {
    const y = typeY + i * 52;
    tx(sheet, 'ts name ' + i, s[0], { font: F.mono, size: 10, color: COL.muted, x: 48, y: y + 6, w: 160, lh: 14 });
    tx(sheet, 'ts sample ' + i, i === 3 ? s[1].toUpperCase() : s[1], { font: s[2], size: s[3], color: COL.text, x: 220, y: y, ls: i === 3 ? 1 : 0, lh: s[3] + 6 });
  });

  const compY = 620;
  tx(sheet, 'ch', 'Komponen', { font: F.bold, size: 15, color: COL.text, x: 48, y: compY - 34, lh: 20 });

  const b1 = frame(sheet, 'Button / Primary', 48, compY, 190, 44, { r: 12, fill: solid(COL.action) });
  tx(b1, 'l', 'Jalankan Klasifikasi', { font: F.bold, size: 12.5, color: '#FFFFFF', x: 0, y: 12, w: 190, align: 'CENTER', lh: 18 });
  const b2 = frame(sheet, 'Button / Ghost', 254, compY, 120, 44, { r: 12, fill: white(0.04), stroke: '#FFFFFF', strokeA: 0.14 });
  tx(b2, 'l', 'Unduh', { font: F.bold, size: 12.5, color: COL.text, x: 0, y: 12, w: 120, align: 'CENTER', lh: 18 });

  ['Semua', 'Premium', 'Defect'].forEach((c, i) => {
    const on = i === 0;
    const w = c.length * 6.8 + 24;
    const chip = frame(sheet, 'Chip/' + c, 400 + i * (w + 8), compY + 7, w, 30, { r: 999, fill: on ? solid(COL.accent, 0.14) : white(0.035), stroke: on ? COL.accent : '#FFFFFF', strokeA: on ? 0.4 : 0.07 });
    tx(chip, 'l', c, { font: F.semi, size: 11.5, color: on ? COL.accent : COL.sec, x: 0, y: 7, w: w, align: 'CENTER', lh: 16 });
  });

  ['Valid', 'Review', 'Ditolak'].forEach((c, i) => {
    const cols = [COL.premium, COL.longberry, COL.defect];
    const pl = frame(sheet, 'Pill/' + c, 700 + i * 100, compY + 11, 86, 22, { r: 999, fill: solid(cols[i], 0.12) });
    ell(pl, 'd', 9, 8, 5, 5, solid(cols[i]));
    tx(pl, 't', c, { font: F.bold, size: 10.5, color: cols[i], x: 19, y: 4, lh: 14 });
  });

  tx(sheet, 'foot', 'Dibangun oleh plugin Arabica Aurora Builder · semua layer native, tanpa raster.', { font: F.body, size: 11, color: COL.muted, x: 48, y: 856, lh: 16 });
  return sheet;
}

/* ============================ MAIN =================================== */
(async () => {
  try {
    await figma.loadAllPagesAsync();
    await boot();

    let page = figma.root.children.find(p => p.name === 'Arabica Aurora');
    if (!page) { page = figma.createPage(); page.name = 'Arabica Aurora'; }
    figma.currentPage = page;
    for (const c of [...page.children]) c.remove();

    makeVariables();
    makeStyles();

    buildDashboard(page);
    buildBatch(page);
    buildModel(page);
    buildRiwayat(page);
    buildPengaturan(page);
    buildTokens(page);

    figma.viewport.scrollAndZoomIntoView(page.children.slice(0, 1));
    figma.notify('Arabica Aurora selesai: 6 frame, 5 view + token sheet', { timeout: 6000 });
    figma.closePlugin();
  } catch (e) {
    figma.notify('Builder error: ' + e.message, { error: true, timeout: 12000 });
    console.error(e);
    figma.closePlugin();
  }
})();
