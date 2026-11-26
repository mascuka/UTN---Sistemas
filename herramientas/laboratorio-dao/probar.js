/* Prueba del laboratorio de DAO con los parciales y simulacros del repo: abre cada ZIP como lo hace la página (el
   enunciado, los CSV y los tests, sin las soluciones que traen adentro), arma la solución y mira que cumpla las
   comprobaciones del test. Si hay python3 con pytest, además la corre de verdad (los tests y el main).
   Uso: node herramientas/laboratorio-dao/probar.js [--codigo] */
const fs = require('fs'), path = require('path'), os = require('os'), { spawnSync } = require('child_process');
const P = require('../laboratorio/proyecto.js'), D = require('./dao.js');
const DIR = path.join(__dirname, '../../material/desarrollo-de-aplicaciones-con-objetos/p1/parcial');
// lo que tiene que pasar con cada uno (los que todavía no resuelve quedan anotados como tales)
const ESPERADO = { '03-parcial-4k3-transporte-de-pasajeros.zip': 'todo', '04-simulacro-la-fabrica.zip': 'todo', '05-simulacro-hospital.zip': 'todo', '07-modelo-la-inmobiliaria.zip': 'todo', '08-modelo-el-supermercado.zip': 'todo' };
const conPytest = spawnSync('python3', ['-m', 'pytest', '--version'], { encoding: 'utf8' }).status === 0;
const deco = b => P.decodificar(b);
let mal = 0;
(async () => {
  for (const z of fs.readdirSync(DIR).filter(f => f.endsWith('.zip')).sort()) {
    const a = await P.leerZip(fs.readFileSync(path.join(DIR, z)));
    const sol = r => /soluci|resoluci|resuelt|propuesta|respuesta/i.test(r);
    const rutas = Object.keys(a).filter(r => !sol(r));
    const enun = rutas.filter(r => /\.(md|txt)$/i.test(r) && !/(^|\/)(LEEME|LICENSE)[^/]*$/i.test(r)).sort((x, y) => /enunciado|consigna|readme/i.test(y) - /enunciado|consigna|readme/i.test(x))[0];
    const csvs = {}, tests = {};
    for (const r of rutas) if (/\.csv$/i.test(r)) csvs[r.split('/').pop()] = deco(a[r]);
    for (const r of rutas) if (/(^|\/)test[^/]*\.py$/i.test(r)) tests[r.split('/').pop()] = deco(a[r]);
    const esperado = ESPERADO[z];
    if (!enun || !Object.keys(tests).length) { console.log(`· ${z}: ${!enun ? 'sin enunciado en texto (es un PDF)' : 'no trae tests'}${esperado ? ' ✗ y debía andar' : ''}`); if (esperado) mal++; continue; }
    let r;
    try { r = D.resolver({ enunciado: deco(a[enun]), csvs, tests }); } catch (e) { console.log(`✗ ${z}: el motor falló: ${e.message}`); mal++; continue; }
    const c = r.comprobacion, bien = c.total > 0 && c.ok === c.total;
    let py = '';
    if (conPytest) {
      const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'dao-'));
      // los CSV van en la carpeta que dice el enunciado (data/), si dice una
      const dCsv = path.join(dir, r.carpetaCsv || '.');
      fs.mkdirSync(dCsv, { recursive: true });
      for (const [n, t] of Object.entries({ ...r.archivos, ...tests })) fs.writeFileSync(path.join(dir, n), t);
      for (const [n, t] of Object.entries(csvs)) fs.writeFileSync(path.join(dCsv, n), t);
      const pt = spawnSync('python3', ['-m', 'pytest', '-q', '-p', 'no:cacheprovider'], { cwd: dir, encoding: 'utf8' });
      const mn = spawnSync('python3', [r.archivos['main.py'] ? 'main.py' : Object.keys(r.archivos)[0]], { cwd: dir, encoding: 'utf8' });
      py = ` · pytest: ${(pt.stdout.match(/\d+ (?:passed|failed)[^\n]*?(?= in )/g) || ['?']).pop()}${mn.status ? ' · el main falla' : ''}`;
      if (esperado && (pt.status || mn.status)) mal++;
      fs.rmSync(dir, { recursive: true, force: true });
    }
    if (esperado && !bien) mal++;
    console.log(`${bien ? '✓' : esperado ? '✗' : '·'} ${z}: cumple ${c.ok}/${c.total} comprobaciones del test${py}${!esperado ? ' (todavía no se resuelve solo)' : ''}`);
    if (process.argv.includes('--codigo')) for (const [n, t] of Object.entries(r.archivos)) console.log(`\n----- ${n}\n${t}`);
  }
  console.log(mal ? `\n${mal} problemas` : '\n✓ Los parciales que tiene que resolver, resueltos');
  process.exitCode = mal ? 1 : 0;
})();
