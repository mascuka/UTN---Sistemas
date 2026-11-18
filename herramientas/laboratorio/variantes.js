/* Prueba de aguante del lector: cada enunciado que ya entiende bien (los de ejemplos.js y las prácticas, más los textos
   que se pasen como argumento) se reescribe de muchas formas que podrían aparecer en otro parcial o en otro PDF —cortes
   de renglón, guiones, comillas, rangos y fórmulas escritos distinto, sinónimos, encabezados y pies de página en el
   medio— y se compara lo que entiende con lo que entendía del original. No cambia nada: solo informa.
   Uso: node herramientas/laboratorio/variantes.js [texto1.txt …] [--detalle] */
const fs = require('fs');
const M = require('./motor.js'), E = require('./ejemplos.js');

// Lo que importa de la configuración (sin las frases de evidencia)
function clave(cfg) {
  const c = M.normalizar(JSON.parse(JSON.stringify(cfg)));
  return JSON.stringify({
    columna: c.columna && { nombre: c.columna.nombre, tipo: c.columna.tipo, valores: c.columna.valores, rango: c.columna.rango, vacio: c.columna.vacio, defecto: c.columna.defecto },
    separador: c.columna ? c.separador : ',', estados: c.estados, descartes: c.descartes, restricciones: c.restricciones,
    especiales: c.especiales.map(e => ({ cuando: e.cuando, ops: e.ops, topes: e.topes, clase: e.clase, etiqueta: e.etiqueta })),
    baseDesdeColumna: c.baseDesdeColumna, extras: c.extras, conteo: c.conteo, etiquetaBase: c.conteo === 'tipo' ? c.etiquetaBase : '',
    totales: c.totales, archivo: c.archivo, anchoMixto: c.anchoMixto, columnaEnSubclase: c.columnaEnSubclase, indiceNuevo: c.indiceNuevo,
    panoramaMenor: c.panoramaMenor,
  });
}
function diferencias(a, b) {
  const A = JSON.parse(a), B = JSON.parse(b);
  return Object.keys(A).filter(k => JSON.stringify(A[k]) !== JSON.stringify(B[k])).map(k => `${k}: ${JSON.stringify(A[k])} → ${JSON.stringify(B[k])}`);
}

// Un azar fijo, para que cada corrida dé lo mismo
let semilla = 1;
const azar = () => { semilla = (Math.imul(semilla, 1103515245) + 12345) >>> 0; return semilla / 4294967296; };

const NBSP = ' ';
const VARIANTES = {
  'renglones cortos (PDF)': t => t.split('\n').map(l => { let out = '', cur = ''; for (const p of l.split(' ')) { if ((cur + ' ' + p).length > 70 && cur) { out += cur + '\n'; cur = p; } else cur = cur ? cur + ' ' + p : p; } return out + cur; }).join('\n'),
  'todo en un renglón': t => t.replace(/\n+/g, ' '),
  'palabras cortadas con guion': t => t.replace(/\b([a-záéíóúñ]{5,})([a-záéíóúñ]{4,})\b/g, (m, a, b) => (azar() < 0.25 ? a + '-\n' + b : m)),
  'espacios duros (nbsp)': t => t.replace(/ /g, () => (azar() < 0.3 ? NBSP : ' ')),
  'comillas tipográficas': t => t.replace(/`([^`]+)`/g, '“$1”'),
  'sin acentos': t => t.normalize('NFD').replace(/[̀-ͯ]/g, ''),
  'viñetas •': t => t.replace(/^- /gm, '• ').replace(/^(\d+)\. /gm, '$1) '),
  'encabezado/pie de página en el medio': t => { const ls = t.split('\n'); const k = Math.floor(ls.length / 2); ls.splice(k, 0, 'enunciado_parcial.md', '2026-11-17', '1 / 3'); return ls.join('\n'); },
  'encabezado CSV con espacios': t => t.replace(/patente,zona,velocidadPromedio,cargaToneladas,estado((?:[,;|][A-Za-z]+)?)/g, (m, x) => 'patente, zona, velocidadPromedio, cargaToneladas, estado' + (x ? x[0] + ' ' + x.slice(1) : '')),
  'encabezado CSV partido': t => t.replace(/patente,zona,velocidadPromedio,cargaToneladas,estado([,;|][A-Za-z]+)/g, 'patente,zona,velocidadPromedio,cargaTonela\ndas,estado$1'),
  'rango «de X a Y»': t => t.replace(/entre (\d+) y (\d+),? inclusive/g, 'de $1 a $2 inclusive'),
  'rango «X–Y»': t => t.replace(/entre (\d+) y (\d+),? inclusive/g, 'en el rango $1–$2 (ambos inclusive)'),
  'rango «mínimo y máximo»': t => t.replace(/entre (\d+) y (\d+),? inclusive/g, 'con un mínimo de $1 y un máximo de $2'),
  'rango «no menor ni mayor»': t => t.replace(/entre (\d+) y (\d+),? inclusive/g, 'no menor a $1 ni mayor a $2'),
  'rango con símbolos': t => t.replace(/entre (\d+) y (\d+),? inclusive/g, '≥ $1 y ≤ $2'),
  'coma decimal en fórmulas': t => t.replace(/\b0\.(\d+)\b/g, '0,$1'),
  'asterisco en fórmulas': t => t.replace(/×/g, '*'),
  'miles con punto': t => t.replace(/\b(\d)(\d{3})\b(?! *[-–]? *\d{2}\b)/g, '$1.$2'),
  'sinónimo «acepta»': t => t.replace(/\badmite\b/g, 'acepta'),
  'sinónimo «puede tomar valores»': t => t.replace(/admite valores entre/g, 'puede tomar valores entre'),
  // segunda ronda: formas menos comunes
  'fórmula con el coeficiente adelante': t => t.replace(/\((\w+) × (0\.\d+)\)/g, '$2 × $1'),
  'fórmula sin paréntesis y con *': t => t.replace(/\((\w+) × (0\.\d+)\)/g, '$1 * $2'),
  'cabecera dicha de otra forma': t => t.replace(/El nuevo encabezado es/g, 'La nueva cabecera del CSV es').replace(/Formato del parcial:/g, 'Encabezado nuevo:'),
  'rango «desde X hasta Y»': t => t.replace(/entre (\d+) y (\d+),? inclusive/g, 'desde $1 hasta $2 inclusive'),
  'rango «ambos extremos incluidos»': t => t.replace(/entre (\d+) y (\d+),? inclusive/g, 'entre $1 y $2 (ambos extremos incluidos)'),
  'rango con %': t => t.replace(/entre (\d+) y (\d+),? inclusive/g, 'entre $1 % y $2 %, inclusive'),
  'moneda adelante (USD 40)': t => t.replace(/\b(\d+) USD\b/g, 'USD $1'),
  '«un número entero»': t => t.replace(/\bun entero\b/g, 'un número entero'),
  'títulos en mayúsculas': t => t.replace(/^(#+ )(.*)$/gm, (m, h, x) => h + x.toUpperCase()),
  'negritas de Markdown': t => t.replace(/\b(entre \d+ y \d+|EN_DEPOSITO|DEMORADO)\b/g, '**$1**'),
};
// combinadas: un PDF «sucio» de verdad y un profe que redacta todo distinto
const V = VARIANTES, juntas = (...ks) => t => ks.reduce((x, k) => V[k](x), t);
VARIANTES['PDF sucio (5 juntas)'] = juntas('comillas tipográficas', 'encabezado CSV partido', 'renglones cortos (PDF)', 'palabras cortadas con guion', 'encabezado/pie de página en el medio', 'espacios duros (nbsp)');
VARIANTES['otra redacción (6 juntas)'] = juntas('cabecera dicha de otra forma', 'rango «desde X hasta Y»', 'moneda adelante (USD 40)', '«un número entero»', 'fórmula con el coeficiente adelante', 'sinónimo «acepta»');
VARIANTES['todo junto'] = t => VARIANTES['PDF sucio (5 juntas)'](VARIANTES['otra redacción (6 juntas)'](V['sin acentos'](t)));

const textos = E.map(e => ({ titulo: e.titulo, texto: e.texto }));
for (const a of process.argv.slice(2)) if (!a.startsWith('--')) textos.push({ titulo: a.split('/').pop(), texto: fs.readFileSync(a, 'utf8') });
const detalle = process.argv.includes('--detalle');

const malas = {};
let total = 0, fallas = 0;
for (const x of textos) {
  const base = clave(M.leerEnunciado(x.texto).cfg);
  for (const [nom, f] of Object.entries(VARIANTES)) {
    const v = f(x.texto);
    if (v === x.texto) continue;                 // esa reescritura no aplica a este texto
    total++;
    const d = diferencias(base, clave(M.leerEnunciado(v).cfg));
    if (d.length) { fallas++; (malas[nom] = malas[nom] || []).push([x.titulo, d]); }
  }
}
console.log(`${textos.length} enunciados × ${Object.keys(VARIANTES).length} reescrituras: ${total} pruebas, ${fallas} cambian lo que entiende`);
for (const [nom, xs] of Object.entries(malas)) {
  console.log(`\n✗ ${nom}: ${xs.length}`);
  for (const [t, d] of detalle ? xs : xs.slice(0, 3)) console.log(`   · ${t}: ${d.join(' | ').slice(0, detalle ? 2000 : 260)}`);
}
process.exitCode = fallas ? 1 : 0;
