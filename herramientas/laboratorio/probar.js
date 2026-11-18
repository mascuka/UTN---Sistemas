/* Pruebas del laboratorio (Node, sin dependencias).
   node herramientas/laboratorio/probar.js                 → el lector con los enunciados de ejemplos.js (y cortados como un PDF)
   node herramientas/laboratorio/probar.js <proyecto> [n]  → además, n configuraciones al azar: el Java generado se compila
                                                            y se corre (javac) y tiene que imprimir lo mismo que la simulación.
   <proyecto> es la carpeta 01-modelo-inicial descomprimida (la de 01-preenunciado.zip).
   Para sumar un enunciado de práctica: agregalo en ejemplos.js con lo que el lector tiene que entender («esperado»). */
const fs = require('fs'), path = require('path'), os = require('os'), { execFileSync } = require('child_process');
const M = require('./motor.js'), E = require('./ejemplos.js');

function parecido(esp, real, ruta, errs) {
  if (esp === null || typeof esp !== 'object') { if (JSON.stringify(esp) !== JSON.stringify(real)) errs.push(`${ruta}: esperaba ${JSON.stringify(esp)} y leyó ${JSON.stringify(real)}`); return; }
  if (Array.isArray(esp)) { if (!Array.isArray(real) || real.length !== esp.length) { errs.push(`${ruta}: esperaba ${JSON.stringify(esp)} y leyó ${JSON.stringify(real)}`); return; } esp.forEach((x, i) => parecido(x, real[i], `${ruta}[${i}]`, errs)); return; }
  if (real == null) { errs.push(`${ruta}: esperaba ${JSON.stringify(esp)} y leyó null`); return; }
  for (const k of Object.keys(esp)) parecido(esp[k], real[k], ruta + '.' + k, errs);
}
const envolver = (t, w) => t.split('\n').map(l => { const out = []; let cur = ''; for (const p of l.split(' ')) { if ((cur + ' ' + p).length > w && cur) { out.push(cur); cur = p; } else cur = cur ? cur + ' ' + p : p; } out.push(cur); return out.join('\n'); }).join('\n');

let fallas = 0;
for (const e of E) {
  const r = M.leerEnunciado(e.texto), errs = [];
  parecido(e.esperado, r.cfg, 'cfg', errs);
  const base = JSON.stringify(r.cfg);
  for (const [nom, t] of [['renglones de 90', envolver(e.texto, 90)], ['renglones de 60', envolver(e.texto, 60)], ['viñetas de PDF', e.texto.replace(/^- /gm, ' ')], ['CRLF', e.texto.replace(/\n/g, '\r\n')]])
    if (JSON.stringify(M.leerEnunciado(t).cfg) !== base) errs.push('cambia con ' + nom);
  if (e.csv) {   // con su propio CSV: los números que da el enunciado tienen que salir
    const sim = M.simular(e.csv, M.normalizar(JSON.parse(JSON.stringify(r.cfg))));
    for (const x of M.referencias(e.texto).filter(x => x.leidas === sim.leidas)) {
      const vs = sim.filas.filter(f => f.vehiculo).map(f => f.vehiculo);
      const da = { leidas: sim.leidas, procesadas: sim.procesadas, descartadas: sim.descartadas, invalidas: sim.invalidas, total: sim.total, menores: vs.filter(v => v.indice < x.limite).length };
      for (const k of Object.keys(da)) if (x[k] != null && x[k] !== da[k]) errs.push(`el enunciado dice ${k} ${x[k]} y da ${da[k]}`);
    }
  }
  console.log((errs.length ? '✗ ' : '✓ ') + e.titulo); for (const x of errs) console.log('    ' + x);
  fallas += errs.length ? 1 : 0;
}

// «Flota.panorama() debe incluir esa última cantidad»: el panorama muestra los de índice menor a 55 (y nada más lo activa)
{
  const errs = [];
  for (const t of ['El conjunto debe dar 20 índices de desgaste menores a 55. Flota.panorama() debe incluir esa última cantidad en su salida.',
    'Mostrar el resumen del parseo y el panorama, que incluye costos por zona y la cantidad de vehículos con índice de desgaste menor a 55.'])
    if (!M.leerEnunciado(t).cfg.panoramaMenor) errs.push('no lo vio en: ' + t);
  for (const e of E) if (M.leerEnunciado(e.texto).cfg.panoramaMenor) errs.push('lo vio de más en: ' + e.titulo);
  console.log((errs.length ? '✗ ' : '✓ ') + 'El panorama con la cantidad menor a 55'); for (const x of errs) console.log('    ' + x);
  fallas += errs.length ? 1 : 0;
}

const proyecto = process.argv[2];
if (proyecto) {
  const SRC = path.join(proyecto, 'src/main/java/ar/edu/backend'), originales = {};
  for (const f of fs.readdirSync(SRC)) originales[f] = fs.readFileSync(path.join(SRC, f), 'utf8').replace(/\r\n/g, '\n');
  const datos = fs.readFileSync(path.join(proyecto, 'datos/datos.csv'), 'utf8');
  let semilla = 12345;
  const azar = () => { semilla = (Math.imul(semilla, 1103515245) + 12345) >>> 0; return semilla / 4294967296; };
  const el = a => a[Math.floor(azar() * a.length)], si = p => azar() < p;
  const cfgs = [M.configBase()].concat(E.map(e => M.leerEnunciado(e.texto).cfg));
  for (let k = 0; k < Number(process.argv[3] || 20); k++) {
    const c = M.configBase(); c.archivo = 'datos-parcial.csv';
    if (si(0.2)) c.estados.push('EN_TALLER');
    if (si(0.3)) c.descartes.push('MANTENIMIENTO');
    if (si(0.8)) {
      c.separador = el([',', ';', '|']);
      c.columna = si(0.5)
        ? { nombre: 'tipoCarga', tipo: 'texto', valores: ['GENERAL', 'REFRIGERADA', 'PELIGROSA'], rango: null, vacio: si(0.2) ? 'defecto' : 'invalida', defecto: 'GENERAL' }
        : { nombre: 'kilometros', tipo: 'entero', valores: si(0.3) ? [0, 30, 90] : [], rango: { min: el([null, 0, 1]), minIncl: si(0.6), max: el([null, 10, 5000]), maxIncl: si(0.5) }, vacio: si(0.25) ? 'defecto' : 'invalida', defecto: 0 };
      if (si(0.3)) c.restricciones.push({ estado: 'DEMORADO', valores: [c.columna.tipo === 'texto' ? 'GENERAL' : 0] });
      if (c.columna.tipo === 'entero' && si(0.3)) c.baseDesdeColumna = true;
      const cuando = c.columna.tipo === 'texto' ? { campo: 'columna', op: 'igual', valor: el(['REFRIGERADA', 'PELIGROSA']) } : el([{ campo: 'columna', op: 'mayor', valor: 0 }, { campo: 'columna', op: 'presente', valor: '' }, { campo: 'estado', op: 'igual', valor: 'DEMORADO' }]);
      c.especiales.push({ cuando, ops: [el([{ op: 'suma', n: 300 }, { op: 'porcentaje', n: 25 }, { op: 'multiplica', n: 2 }, ...(c.columna.tipo === 'entero' ? [{ op: 'sumaPorCada', n: 200, cada: 30 }] : [])])], topes: si(0.6) ? [{ campo: el(['carga', 'velocidad', 'indice']), op: el(['max', 'min']), n: el([30, 60]), incl: si(0.5) }] : [], clase: '', etiqueta: '' });
    }
    if (c.columna && si(0.4)) c.anchoMixto = true;
    if (c.columna && si(0.4)) {   // la columna en la subclase de las filas de seis campos, a veces con otra fórmula del índice
      c.columnaEnSubclase = true; c.baseDesdeColumna = c.columna.tipo === 'entero' && si(0.4);
      c.especiales = [{ cuando: { campo: 'columna', op: 'ancho', valor: '' }, ops: si(0.5) ? [el([{ op: 'suma', n: 300 }, { op: 'porcentaje', n: 10 }])] : [], topes: si(0.4) ? [{ campo: 'carga', op: 'max', n: 30, incl: true }] : [], clase: '', etiqueta: '' }];
      if (c.columna.tipo === 'entero') { c.columna.rango = c.baseDesdeColumna ? { min: 2000, minIncl: true, max: 3800, maxIncl: false } : { min: 0, minIncl: true, max: el([30, 60]), maxIncl: true }; c.columna.defecto = c.baseDesdeColumna ? 2000 : 0; c.columna.valores = []; if (si(0.7)) c.indiceNuevo = el([{ v: 0.5, c: 0.3, x: 0.2 }, { v: 0.55, c: 0.3, x: 0.15 }]); }
      if (c.conteo === 'columna') c.conteo = 'tipo';
    }
    if (si(0.3)) c.extras.push({ op: 'suma', n: 50 });
    c.conteo = el([null, 'estado', 'zona', c.columna && !c.columnaEnSubclase ? 'columna' : null, c.especiales.length ? 'tipo' : null]);
    if (si(0.4)) c.totales.push({ campo: 'estado', valor: 'DEMORADO' });
    if (si(0.3)) c.panoramaMenor = true;
    cfgs.push(M.normalizar(c));
  }
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'lab-'));
  cfgs.forEach((cfg, k) => {
    const dir = path.join(tmp, 'c' + k), cls = path.join(dir, 'cls'); fs.mkdirSync(cls, { recursive: true });
    const todos = Object.assign({}, originales), gen = M.generar(cfg, originales);
    // una vez con las marcas y otra sin ningún comentario (la vista simple): las dos tienen que compilar y dar lo mismo
    for (const [f, t] of Object.entries(gen)) todos[f] = k % 2 ? M.sinComentarios(M.marcarCambios(originales[f], t)) : M.marcarCambios(originales[f], t);
    for (const [f, t] of Object.entries(todos)) fs.writeFileSync(path.join(dir, f), t);
    let mal = '';
    try { execFileSync('javac', ['-encoding', 'UTF-8', '-d', cls, ...Object.keys(todos).map(f => path.join(dir, f))], { stdio: 'pipe' }); }
    catch (x) { mal = 'no compila: ' + x.stderr.toString().split('\n')[0]; }
    for (const [i, csv] of [datos, M.csvDePrueba(cfg, k + 1), M.csvDePrueba(cfg, k + 50, 60)].entries()) {
      if (mal) break;
      const f = path.join(dir, 'd' + i + '.csv'); fs.writeFileSync(f, csv);
      const sim = M.simular(csv, cfg);
      let java;
      try { java = execFileSync('java', ['-Dstdout.encoding=UTF-8', '-cp', cls, 'ar.edu.backend.App', f], { stdio: ['pipe', 'pipe', 'pipe'] }).toString().replace(/\n$/, ''); }
      catch (x) { java = null; }
      if (sim.abortado ? java !== null : java !== sim.salida) mal = 'CSV ' + i + ': la salida de Java no coincide con la simulación';
    }
    if (mal) { fallas++; console.log(`✗ configuración ${k}: ${mal}`); }
  });
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(`${cfgs.length} configuraciones compiladas y corridas con Java`);
}
console.log(fallas ? `${fallas} con problemas` : 'TODO BIEN');
process.exit(fallas ? 1 : 0);
