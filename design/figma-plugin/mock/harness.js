/* Headless mock of the Figma plugin API — used to smoke-test code.js */
const nodes = [];
let idc = 0;
const push = n => { nodes.push(n); return n; };

class Base {
  constructor(type) {
    this.id = 'n' + (++idc);
    this.type = type;
    this.name = type;
    this.children = [];
    this.x = 0; this.y = 0; this.width = 100; this.height = 100;
    this.fills = []; this.strokes = []; this.effects = [];
    this._font = null; this.characters = '';
    this.parent = null;
  }
  appendChild(c) { this.children.push(c); c.parent = this; return c; }
  resize(w, h) {
    if (typeof w !== 'number' || typeof h !== 'number' || !isFinite(w) || !isFinite(h)) {
      throw new Error(`${this.type} "${this.name}".resize got ${w}x${h}`);
    }
    this.width = w; this.height = h;
  }
  set fontName(v) {
    if (!v || typeof v.family !== 'string' || typeof v.style !== 'string') {
      throw new Error(`fontName invalid on ${this.type} "${this.name}": ${JSON.stringify(v)}`);
    }
    this._font = v;
  }
  get fontName() { return this._font; }
  set fontNameSafe(v) { this.fontName = v; }
  scrollAndZoomIntoView() {}
  setValueForMode(m, v) { this.values = this.values || {}; this.values[m] = v; }
  renameMode(m, n) {
    if (typeof m !== 'string' || typeof n !== 'string') throw new Error('renameMode bad args: ' + m + ' / ' + n);
    this.modes = (this.modes || []).map(x => (x.modeId === m ? { modeId: m, name: n } : x));
  }
  remove() {
    if (this.parent) this.parent.children = this.parent.children.filter(c => c !== this);
    const i = nodes.indexOf(this);
    if (i >= 0) nodes.splice(i, 1);
    this.parent = null;
  }
  setRangeFontName() {}
  insertCharacters() {}
  setReactionsAsync() {}
}

const page = new Base('PAGE');
page.name = 'Page 1';
const root = new Base('DOCUMENT');
root.children = [page];

let collections = [];
let variables = [];
let textStyles = [];

const figma = {
  root,
  currentPage: page,
  viewport: { scrollAndZoomIntoView() {}, center: { x: 0, y: 0 }, zoom: 1 },
  notify(msg, opts) { if (/error/i.test(String(msg))) console.error('NOTIFY-ERROR:', msg); else console.log('notify:', msg); },
  closePlugin() { console.log('closePlugin called'); },

  createPage() { const p = new Base('PAGE'); push(p); return p; },
  createFrame() { return push(new Base('FRAME')); },
  createRectangle() { return push(new Base('RECTANGLE')); },
  createEllipse() { return push(new Base('ELLIPSE')); },
  createText() { return push(new Base('TEXT')); },
  createNodeFromSvg(svg) {
    if (typeof svg !== 'string' || !/^<svg/i.test(svg)) throw new Error('createNodeFromSvg: not svg: ' + String(svg).slice(0, 60));
    if (/undefined|NaN/.test(svg)) throw new Error('createNodeFromSvg: svg contains undefined/NaN: ' + svg.slice(0, 200));
    const n = new Base('FRAME');
    n.isSvg = true;
    return push(n);
  },
  createTextStyle() { const s = new Base('TEXTSTYLE'); textStyles.push(s); return s; },
  getLocalTextStyles() { return textStyles; },
  listAvailableFontsAsync() {
    const fams = ['Inter', 'Roboto Mono', 'Plus Jakarta Sans', 'JetBrains Mono'];
    const out = [];
    for (const f of fams) for (const s of ['Regular', 'Medium', 'Semi Bold', 'Bold']) out.push({ fontName: { family: f, style: s } });
    return Promise.resolve(out);
  },
  loadFontAsync(f) {
    if (!f || !f.family || !f.style) return Promise.reject(new Error('loadFontAsync bad font: ' + JSON.stringify(f)));
    const fams = ['Inter', 'Roboto Mono', 'Plus Jakarta Sans', 'JetBrains Mono'];
    if (!fams.includes(f.family)) return Promise.reject(new Error('font family missing: ' + f.family));
    if (!['Regular', 'Medium', 'Semi Bold', 'Bold'].includes(f.style)) return Promise.reject(new Error('font style missing: ' + f.style));
    return Promise.resolve();
  },
  loadAllPagesAsync() { return Promise.resolve(); },
  variables: {
    getLocalVariableCollections() { return collections; },
    createVariableCollection(name) {
      const c = {
        id: 'VariableCollectionId:' + (collections.length + 1) + ':2', name,
        modes: [{ modeId: 'm1', name: 'Mode 1' }],
        renameMode(m, n) {
          if (typeof n !== 'string') throw new Error('renameMode bad name: ' + n);
          this.modes = this.modes.map(x => (x.modeId === m ? { modeId: m, name: n } : x));
        }
      };
      collections.push(c);
      return c;
    },
    getLocalVariables() { return variables; },
    createVariable(name, coll, type) {
      const v = {
        id: 'VariableID:' + (variables.length + 1) + ':1', name, variableCollectionId: coll.id, resolvedType: type, values: {},
        setValueForMode(m, val) {
          if (typeof m !== 'string' || !val || typeof val.r !== 'number') throw new Error('setValueForMode bad: ' + JSON.stringify(val));
          this.values[m] = val;
        }
      };
      variables.push(v);
      return v;
    }
  }
};

global.figma = figma;
module.exports = { figma, nodes, collections, variables, textStyles, page, root };
