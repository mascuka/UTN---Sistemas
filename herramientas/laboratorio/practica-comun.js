/* Lo común de los parciales de práctica (cada practica-xxx/armar.js): con el enunciado y el CSV escribe el Markdown y el
   ejemplo para el laboratorio (ejemplo.json) en la carpeta de la práctica, y el CSV y el PDF en el material del
   recuperatorio. Los números de referencia del enunciado salen de la simulación del laboratorio con las reglas que el
   mismo lector saca del enunciado (y probar.js los verifica). Con --pdf imprime el Markdown con Chromium, como los PDF de
   la cátedra, y le saca los metadatos con pymupdf. */
const fs = require('fs'), path = require('path');
const M = require('./motor.js');
const ORIGINAL = fs.readFileSync(path.join(__dirname, 'datos-preenunciado.csv'), 'utf8');
const CERO = { leidas: 0, procesadas: 0, descartadas: 0, invalidas: 0, total: 0, porZona: [['NORTE', 0]], menor55: 0 };

/* def: { carpeta (la de la práctica), material (nombre de la carpeta en el material), enunciado(r0, r) → Markdown,
          csv, ejemplo: { id, titulo, estilo, esperado }, tituloPdf } */
function armar(def) {
  const salida = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2]
    : path.join(__dirname, '../../material/backend-de-aplicaciones/p1/parcial/recuperatorio-1', def.material);
  const cfg = M.normalizar(M.leerEnunciado(def.enunciado(CERO, CERO)).cfg);
  const r0 = M.simular(ORIGINAL, cfg), r = M.simular(def.csv, cfg);
  if (r0.abortado || r.abortado) { console.error(r0.abortado || r.abortado, JSON.stringify(cfg.columna)); process.exit(1); }
  const md = def.enunciado(r0, r);
  fs.mkdirSync(salida, { recursive: true });
  fs.writeFileSync(path.join(def.carpeta, 'enunciado-parcial.md'), md);
  fs.writeFileSync(path.join(salida, 'datos-parcial.csv'), def.csv);
  fs.writeFileSync(path.join(def.carpeta, 'ejemplo.json'), JSON.stringify({ id: def.ejemplo.id, titulo: def.ejemplo.titulo, estilo: def.ejemplo.estilo, texto: md, csv: def.csv, esperado: def.ejemplo.esperado }, null, 1) + '\n');
  console.log('original:', r0.leidas, r0.procesadas, r0.descartadas, r0.invalidas, r0.total, '· del parcial:', r.leidas, r.procesadas, r.descartadas, r.invalidas, r.total, JSON.stringify(r.porZona), r.menor55);
  if (process.argv.includes('--pdf')) pdf(md, path.join(salida, 'enunciado-parcial.pdf'), def.tituloPdf);
  return { md, cfg, r0, r };
}

function pdf(md, archivo, titulo) {
  const { chromium } = require(process.env.PLAYWRIGHT || '/opt/node-tools/node_modules/playwright');
  const esc = t => t.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]);
  const enLinea = t => esc(t).replace(/`([^`]+)`/g, '<code>$1</code>');
  let html = '', lista = null, codigo = [];
  const cerrar = () => { if (lista) { html += `</${lista}>`; lista = null; } if (codigo.length) { html += `<pre>${esc(codigo.join('\n'))}</pre>`; codigo = []; } };
  for (const l of md.split('\n')) {
    if (/^ {4}/.test(l)) { if (lista) { html += `</${lista}>`; lista = null; } codigo.push(l.slice(4)); continue; }
    if (codigo.length && l.trim() === '') continue;
    if (codigo.length) { html += `<pre>${esc(codigo.join('\n'))}</pre>`; codigo = []; }
    let m;
    if ((m = l.match(/^(#+) (.*)/))) { cerrar(); html += `<h${m[1].length}>${enLinea(m[2])}</h${m[1].length}>`; }
    else if ((m = l.match(/^- (.*)/))) { if (lista !== 'ul') { cerrar(); html += '<ul>'; lista = 'ul'; } html += `<li>${enLinea(m[1])}</li>`; }
    else if ((m = l.match(/^\d+\. (.*)/))) { if (lista !== 'ol') { cerrar(); html += '<ol>'; lista = 'ol'; } html += `<li>${enLinea(m[1])}</li>`; }
    else if (l.trim()) { cerrar(); html += `<p>${enLinea(l)}</p>`; }
    else cerrar();
  }
  cerrar();
  (async () => {
    const b = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
    const pg = await b.newPage();
    await pg.setContent(`<!doctype html><html><head><meta charset="utf-8"><title>enunciado-parcial.md</title><style>
      body{font:10.5pt/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;color:#1f2328}
      h1{font-size:18pt;border-bottom:1px solid #d1d9e0;padding-bottom:6px;margin:0 0 10px} h2{font-size:13.5pt;border-bottom:1px solid #d1d9e0;padding-bottom:4px;margin:18px 0 8px}
      p{margin:0 0 8px} ul,ol{margin:0 0 8px 22px;padding:0} li{margin:2px 0}
      code{font:9pt ui-monospace,Menlo,Consolas,monospace;background:#eff1f3;border-radius:4px;padding:1px 4px}
      pre{font:9pt/1.45 ui-monospace,Menlo,Consolas,monospace;background:#f6f8fa;border-radius:6px;padding:9px 12px;margin:0 0 10px;white-space:pre-wrap}
    </style></head><body>${html}</body></html>`);
    await pg.pdf({ path: archivo, format: 'A4', margin: { top: '1.6cm', bottom: '1.6cm', left: '1.8cm', right: '1.8cm' }, displayHeaderFooter: true,
      headerTemplate: '<div style="font-size:8px;width:100%;padding:0 1.8cm;color:#555">enunciado-parcial.md<span style="float:right">2026-11-17</span></div>',
      footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#555"><span class="pageNumber"></span>/<span class="totalPages"></span></div>' });
    await b.close();
    require('child_process').execFileSync('python3', ['-I', '-c', `import sys, pymupdf
d = pymupdf.open(sys.argv[1])
d.set_metadata({'title': sys.argv[2], 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': ''})
d.del_xml_metadata()
d.save(sys.argv[1] + '.tmp', garbage=3, deflate=True)
`, archivo, titulo]);
    fs.renameSync(archivo + '.tmp', archivo);
    console.log('PDF:', path.relative(process.cwd(), archivo));
  })();
}

module.exports = { armar, M };
