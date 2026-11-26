/* Prueba de la guía de un parcial cualquiera (guia.js): para cada simulacro del repo cruza la consigna del parcial
   (el .md que viene en su ZIP), el CSV del parcial y el código del preenunciado, y revisa que la guía encuentre lo que
   pide el enunciado: el encabezado nuevo, cada columna con sus valores, los estados nuevos y la clase que conviene.
   Uso: node herramientas/laboratorio/probar-guia.js */
const fs = require('fs'), path = require('path');
const P = require('./proyecto.js'), G = require('./guia.js');
const PARCIAL = path.join(__dirname, '../../material/backend-de-aplicaciones/p1/parcial');
const CASOS = [
  { zip: 'simulacros/simulacro-1.zip', esperado: { columnas: { nivelMorosidad: 'NORMAL/EN_MORA' }, clases: ['SolicitudCreditoEnMora'] } },
  { zip: 'simulacros/simulacro-2.zip', esperado: { columnas: { garantia: 'NO/SI', repuestos: 'int', modalidad: 'NORMAL/EXPRESS' }, estados: ['ENTREGADA'], clases: ['ReparacionExpress'], codigo: ['comun * 1.25'] } },
  { zip: 'simulacros/simulacro-3.zip', esperado: { columnas: { dificultad_cooperativa: 'int' }, clases: ['JuegoMesaCooperativo'], codigo: ['tieneDificultadCooperativa && (dificultadCooperativa < 1 || dificultadCooperativa > 10)'] } },
  { zip: 'simulacros/simulacro-4.zip', esperado: { columnas: { diasCobertura: '0/30/90/180' }, clases: ['ConsumoAsegurado'], codigo: ['200 * (diasCobertura / 30)', 'if (diasCobertura != 0)'] } },
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
    mal += errores.length;
    console.log(`${errores.length ? '✗' : '✓'} ${p.nombre}${errores.length ? '\n    ' + errores.join('\n    ') : ''}`);
  }
  console.log(mal ? `\n${mal} problemas en la guía` : '\n✓ La guía encuentra lo que pide cada enunciado');
  process.exitCode = mal ? 1 : 0;
})();
