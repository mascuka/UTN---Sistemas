/* Prueba de la solución de un parcial cualquiera. Para cada simulacro del repo cruza la consigna del parcial (el .md que
   viene en su ZIP), el CSV del parcial y el código del preenunciado:
   1) el análisis (guia.js) tiene que encontrar lo que pide el enunciado: el encabezado nuevo, cada columna con sus
      valores, los estados nuevos y la clase que conviene;
   2) la solución (resolver.js) tiene que compilar, correr con el CSV del parcial y dar los mismos números que la
      solución propuesta por la cátedra (las dos se corren con java.js, el mismo ejecutor de la página).
   Uso: node herramientas/laboratorio/probar-guia.js */
const fs = require('fs'), path = require('path');
const P = require('./proyecto.js'), G = require('./guia.js'), R = require('./resolver.js'), J = require('./java.js');
const PARCIAL = path.join(__dirname, '../../material/backend-de-aplicaciones/p1/parcial');
const CASOS = [
  { zip: 'simulacros/simulacro-1.zip', solucion: 'parcial-3k8/03-solucion-propuesta.zip', esperado: { columnas: { nivelMorosidad: 'NORMAL/EN_MORA' }, clases: [] } },
  { zip: 'simulacros/simulacro-2.zip', solucion: 'simulacros/simulacro-2/03-solucion-propuesta.zip', esperado: { columnas: { garantia: 'NO/SI', repuestos: 'int', modalidad: 'NORMAL/EXPRESS' }, estados: ['ENTREGADA'], clases: ['ReparacionExpress'], codigo: ['comun * 1.25'] } },
  { zip: 'simulacros/simulacro-3.zip', solucion: 'simulacros/simulacro-3/03-solucion-propuesta.zip', esperado: { columnas: { dificultad_cooperativa: 'int' }, clases: ['JuegoCooperativo'], codigo: ['tieneDificultadCooperativa && (dificultadCooperativa < 1 || dificultadCooperativa > 10)'] } },
  { zip: 'simulacros/simulacro-4.zip', solucion: 'simulacros/simulacro-4/03-solucion.zip', esperado: { columnas: { diasCobertura: '0/30/90/180' }, clases: ['ConsumoAsegurado'], codigo: ['200 * (diasCobertura / 30)', 'if (diasCobertura != 0)'] } },
];
let mal = 0;
(async () => {
  for (const caso of CASOS) {
    const a = await P.leerZip(fs.readFileSync(path.join(PARCIAL, caso.zip)));
    const p = P.elegir(a, caso.zip);
    const md = Object.keys(a).find(r => /02 - Enunciado\/.*consigna-parcial\.md$/.test(r)), csv = Object.keys(a).find(r => /02 - Enunciado\/.*datos-parcial\.csv$/.test(r));
    const errores = [];
    for (const conCsv of [true, false]) {
      const g = G.armar(p, P.decodificar(a[md]), conCsv ? P.decodificar(a[csv]) : null);
      const e = caso.esperado, de = conCsv ? '' : ' (sin CSV)';
      if (!g.pasos.some(x => x.clave === 'encabezado')) errores.push('no encontró el encabezado nuevo' + de);
      for (const [col, v] of Object.entries(e.columnas)) {
        const k = g.columnas.find(x => x.col === col);
        const da = k ? (k.valores.length ? k.valores.join('/') : k.tipo) : '—';
        if (da !== v) errores.push(`columna ${col}: esperaba ${v}, dio ${da}${de}`);
      }
      for (const w of e.estados || []) if (!g.pasos.some(x => x.clave === 'estado' && x.valor === w)) errores.push(`no pide aceptar el estado ${w}${de}`);
      for (const c of e.clases || []) if (!g.pasos.some(x => x.clave === 'clase' && x.valor === c)) errores.push(`no propone la clase ${c}${de}`);
      const todo = g.pasos.map(x => x.codigo || '').join('\n');
      for (const c of e.codigo || []) if (!todo.includes(c)) errores.push(`el código no trae «${c}»${de}`);
      for (const x of g.pasos) for (const l of x.lugares || []) if (!(l.archivo in p.fuentes) || !p.fuentes[l.archivo].split('\n')[l.linea - 1]) errores.push(`lugar inexistente ${l.archivo}:${l.linea}`);
    }
    // la solución: compila, corre y da los números de la de la cátedra
    const correr = fuentes => J.ejecutar({ fuentes: Object.fromEntries(Object.entries(fuentes).filter(([k]) => k.endsWith('.java'))), archivos: { 'datos/datos-parcial.csv': P.decodificar(a[csv]) }, args: ['datos/datos-parcial.csv'], idioma: 'es-AR' });
    const r = R.resolver(p, P.decodificar(a[md]), P.decodificar(a[csv]));
    for (const x of r.avisos) errores.push('aviso: ' + x);
    const yo = correr(r.fuentes);
    if (yo.noCompila || yo.error) errores.push('la solución no corre: ' + String(yo.error).split('\n')[0]);
    else if (caso.solucion) {
      const sa = await P.leerZip(fs.readFileSync(path.join(PARCIAL, caso.solucion))), sp = P.elegir(sa, 'solucion');
      const ella = correr(sp.fuentes);
      // las mismas filas inválidas y descartadas (los mensajes pueden decirlo con otras palabras) y los números del resumen
      const lineas = t => new Set((t.match(/^L[ií]nea \d+/gm) || []).map(x => x.replace(/\D/g, '')));
      const a1 = lineas(yo.salida), a2 = lineas(ella.salida);
      const distintas = [...a2].filter(x => !a1.has(x)).concat([...a1].filter(x => !a2.has(x)));
      if (distintas.length) errores.push(`filas inválidas o descartadas distintas de la solución de la cátedra: líneas ${distintas.slice(0, 8).join(', ')}`);
      const nums = t => (t.split('\n').filter(l => !/^L[ií]nea \d+/.test(l)).join(' ').match(/-?\d+(?:[.,]\d+)?/g) || []).map(x => Number(x.replace(',', '.')));
      const mios = nums(yo.salida);
      const faltan = [...new Set(nums(ella.salida))].filter(x => !mios.some(y => Math.abs(y - x) < 0.005));
      if (faltan.length) errores.push(`la salida no trae estos números de la solución de la cátedra: ${faltan.slice(0, 8).join(', ')}`);
    }
    if (!Object.keys(r.fuentes).some(k => r.fuentes[k] !== p.fuentes[k])) errores.push('la solución no cambió nada');
    mal += errores.length;
    console.log(`${errores.length ? '✗' : '✓'} ${p.nombre}${errores.length ? '\n    ' + errores.join('\n    ') : ''}`);
  }
  console.log(mal ? `\n${mal} problemas` : '\n✓ Encuentra lo que pide cada enunciado y la solución da los números de la cátedra');
  process.exitCode = mal ? 1 : 0;
})();
