/* Prueba del ejecutor de Java del navegador (java.js) contra Java de verdad. Para cada preenunciado del repo (los ZIP de
   material/backend-de-aplicaciones/p1/parcial): lo descomprime, compila y corre su main con javac/java, corre el mismo
   main con java.js y compara las salidas letra por letra. Además lo corre con CSV «rotos» al azar (filas cambiadas,
   campos vacíos, números raros) para que las dos implementaciones se crucen en los casos difíciles.
   Uso: node herramientas/laboratorio/probar-java.js [veces al azar por proyecto, 20 por defecto] [--detalle] */
const fs = require('fs'), path = require('path'), os = require('os'), zlib = require('zlib'), { execFileSync } = require('child_process');
const J = require('./java.js');

const RAIZ = path.join(__dirname, '../..');
const PARCIAL = path.join(RAIZ, 'material/backend-de-aplicaciones/p1/parcial');
const ZIPS = ['parcial-3k1/01-preenunciado.zip', 'parcial-3k2/01-preenunciado.zip', 'simulacros/simulacro-4/01-preenunciado.zip',
  'recuperatorio-1/01-preenunciado.zip', 'simulacros/simulacro-1.zip', 'simulacros/simulacro-2.zip', 'simulacros/simulacro-3.zip'];
// Las soluciones (con herencia, subclases y polimorfismo): se corren con el CSV del parcial si lo traen
const SOLUCIONES = ['parcial-3k1/03-solucion-propuesta.zip', 'parcial-3k2/03-solucion-propuesta.zip', 'parcial-3k8/03-solucion-propuesta.zip',
  'simulacros/simulacro-2/03-solucion-propuesta.zip', 'simulacros/simulacro-3/03-solucion-propuesta.zip', 'simulacros/simulacro-4/03-solucion.zip',
  'recuperatorio-1/practica-pendiente/solucion-propuesta.zip', 'recuperatorio-1/practica-acoplado/solucion-propuesta.zip'].filter(z => fs.existsSync(path.join(PARCIAL, z)));
const veces = Number(process.argv.find(a => /^\d+$/.test(a)) || 20), detalle = process.argv.includes('--detalle');

// Un ZIP mínimo (lo mismo que hace la página en el navegador)
function leerZip(buf) {
  const archivos = {};
  let fin = buf.length - 22;
  while (fin >= 0 && buf.readUInt32LE(fin) !== 0x06054b50) fin--;
  const n = buf.readUInt16LE(fin + 10);
  let p = buf.readUInt32LE(fin + 16);
  for (let i = 0; i < n; i++) {
    const metodo = buf.readUInt16LE(p + 10), comp = buf.readUInt32LE(p + 20), lnom = buf.readUInt16LE(p + 28), lext = buf.readUInt16LE(p + 30), lcom = buf.readUInt16LE(p + 32), off = buf.readUInt32LE(p + 42);
    const nombre = buf.slice(p + 46, p + 46 + lnom).toString('utf8');
    p += 46 + lnom + lext + lcom;
    if (nombre.endsWith('/')) continue;
    const ini = off + 30 + buf.readUInt16LE(off + 26) + buf.readUInt16LE(off + 28);
    const datos = buf.slice(ini, ini + comp);
    archivos[nombre] = metodo === 0 ? datos : zlib.inflateRawSync(datos);
  }
  return archivos;
}
// El proyecto del preenunciado dentro del ZIP: la carpeta del pom.xml que no es de un enunciado ni de una solución
function proyectoDe(archivos, solucion) {
  const poms = Object.keys(archivos).filter(n => /(^|\/)pom\.xml$/.test(n) && !/__MACOSX|\/target\//.test(n))
    .sort((a, b) => solucion ? a.length - b.length : (/enunciado|parcial|solucion/i.test(path.dirname(a).split('/').slice(1).join('/')) - /enunciado|parcial|solucion/i.test(path.dirname(b).split('/').slice(1).join('/'))) || a.length - b.length);
  const raiz = path.dirname(poms[0]) === '.' ? '' : path.dirname(poms[0]) + '/';
  const fuentes = {}, datos = {};
  for (const [n, b] of Object.entries(archivos)) {
    if (!n.startsWith(raiz) || /__MACOSX|\/target\//.test(n)) continue;
    const r = n.slice(raiz.length);
    if (/^src\/main\/.*\.java$/.test(r)) fuentes[r] = b.toString('utf8');
    else if (/\.(csv|txt)$/i.test(r)) datos[r] = b.toString('utf8');
  }
  return { raiz, fuentes, datos };
}

// CSV «rotos»: cambios al azar sobre el CSV del proyecto
function romper(csv, semilla) {
  let s = semilla;
  const azar = () => { s = (Math.imul(s, 1103515245) + 12345) >>> 0; return s / 4294967296; };
  const el = a => a[Math.floor(azar() * a.length)];
  const ls = csv.split('\n');
  const cuerpo = ls.slice(1).filter(l => l.trim());
  const RAROS = ['', ' ', '-1', '0', '2147483648', '1e3', '12.5', 'abc', ' 7 ', '+5', '00', '-0', '99999', '1,5', 'NULL', 'null', '\t3'];
  for (let i = 0; i < 12; i++) {
    const k = Math.floor(azar() * cuerpo.length), sep = cuerpo[k].includes(';') ? ';' : ',', cs = cuerpo[k].split(sep);
    const que = azar();
    if (que < 0.6) cs[Math.floor(azar() * cs.length)] = el(RAROS);
    else if (que < 0.7) cs.pop();
    else if (que < 0.8) cs.push(el(RAROS));
    else if (que < 0.9) { const j = Math.floor(azar() * cs.length), x = cuerpo[Math.floor(azar() * cuerpo.length)].split(sep)[j]; if (x !== undefined) cs[j] = x; }
    else { cuerpo.splice(k, 0, ''); continue; }
    cuerpo[k] = cs.join(sep);
  }
  return [ls[0]].concat(cuerpo).join('\n') + '\n';
}

function correrJava(dir, clase, args) {
  try { return execFileSync('java', ['-Dstdout.encoding=UTF-8', '-Duser.language=es', '-Duser.country=AR', '-cp', path.join(dir, 'cls'), clase, ...args], { cwd: dir, stdio: ['pipe', 'pipe', 'pipe'], input: '' }).toString(); }
  catch (x) { return x.stdout ? x.stdout.toString() : ''; }
}

let total = 0, fallas = 0, noSabe = 0;
for (const z of ZIPS.concat(SOLUCIONES)) {
  const archivos = leerZip(fs.readFileSync(path.join(PARCIAL, z)));
  const p = proyectoDe(archivos, SOLUCIONES.includes(z));
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pj-'));
  for (const [r, t] of Object.entries({ ...p.fuentes, ...p.datos })) { fs.mkdirSync(path.join(tmp, path.dirname(r)), { recursive: true }); fs.writeFileSync(path.join(tmp, r), t); }
  const fuentesAbs = Object.keys(p.fuentes).map(r => path.join(tmp, r));
  execFileSync('javac', ['-encoding', 'UTF-8', '-d', path.join(tmp, 'cls'), ...fuentesAbs], { stdio: 'pipe' });
  const main = Object.entries(p.fuentes).find(([, t]) => /static\s+void\s+main\s*\(/.test(t));
  const clase = ((main[1].match(/^\s*package\s+([\w.]+)\s*;/m) || [])[1] ? main[1].match(/^\s*package\s+([\w.]+)\s*;/m)[1] + '.' : '') + path.basename(main[0], '.java');
  const csvBase = Object.keys(p.datos).find(r => /datos\.csv$/.test(r)) || Object.keys(p.datos)[0];
  let malasProyecto = 0;
  const casos = [['el CSV del proyecto', []]];
  for (const r of Object.keys(p.datos)) if (r !== csvBase && /\.csv$/.test(r)) casos.push(['con ' + r, [r]]);
  for (let i = 0; i < veces; i++) casos.push(['CSV roto #' + i, ['datos/roto' + i + '.csv'], romper(p.datos[csvBase], 1000 + i * 7919 + ZIPS.indexOf(z))]);
  for (const [nombre, args, csv] of casos) {
    const datos = { ...p.datos };
    if (csv) { datos[args[0]] = csv; fs.mkdirSync(path.join(tmp, 'datos'), { recursive: true }); fs.writeFileSync(path.join(tmp, args[0]), csv); }
    const esperado = correrJava(tmp, clase, args);
    let r;
    try { r = J.ejecutar({ fuentes: p.fuentes, archivos: datos, args }); } catch (x) { r = { salida: '', error: 'EXCEPCIÓN JS: ' + x.stack.split('\n').slice(0, 3).join(' | ') }; }
    total++;
    if (r.noSoportado) noSabe++;
    if (r.salida !== esperado) {
      fallas++; malasProyecto++;
      if (malasProyecto <= (detalle ? 20 : 2)) {
        const a = esperado.split('\n'), b = r.salida.split('\n'), i = a.findIndex((x, k) => x !== b[k]);
        console.log(`  ✗ ${z} · ${nombre}: renglón ${i + 1}\n      java:    ${JSON.stringify(a[i])}\n      java.js: ${JSON.stringify(b[i])}${r.error ? '\n      error: ' + r.error.split('\n')[0] : ''}`);
      }
    }
  }
  console.log(`${malasProyecto ? '✗' : '✓'} ${z} (${clase}): ${casos.length - malasProyecto}/${casos.length} iguales a Java`);
  fs.rmSync(tmp, { recursive: true, force: true });
}
console.log(`\n${total} corridas: ${total - fallas} iguales a Java, ${fallas} distintas${noSabe ? ' (' + noSabe + ' con algo que el ejecutor no sabe)' : ''}`);
process.exitCode = fallas ? 1 : 0;
