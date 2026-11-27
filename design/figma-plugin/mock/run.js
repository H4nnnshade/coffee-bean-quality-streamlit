/* Runs code.js against the mock Figma API to catch runtime errors */
const path = require('path');
const fs = require('fs');
const h = require('./harness.js');

const src = fs.readFileSync(path.join(__dirname, '..', 'code.js'), 'utf8');
const fn = new Function('figma', 'console', src + '\nreturn { run: (typeof main === "function" ? main : null) };');
fn(h.figma, console);

setTimeout(() => {
  const byType = {};
  for (const n of h.nodes) byType[n.type] = (byType[n.type] || 0) + 1;
  console.log('nodes total:', h.nodes.length);
  console.log('by type:', JSON.stringify(byType));
  console.log('variables:', h.variables.length, 'collections:', h.collections.length, 'textStyles:', h.textStyles.length);

  const pages = h.nodes.filter(n => n.type === 'PAGE');
  const top = h.nodes.filter(n => n.type === 'FRAME' && n.parent);
  console.log('pages:', pages.map(p => p.name));
  // top-level frames per page
  for (const p of pages) {
    console.log(' page', p.name, 'children:', p.children.length, p.children.slice(0, 8).map(c => c.name));
  }
  const bad = h.nodes.filter(n => n.type === 'FRAME' && (!isFinite(n.width) || !isFinite(n.height) || n.width <= 0 || n.height <= 0));
  console.log('bad frames:', bad.length, bad.slice(0, 5).map(b => b.name + ' ' + b.width + 'x' + b.height));
}, 600);
