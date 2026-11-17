/* Parcial de práctica «Flota Logística con pendiente del tramo»: el mismo cambio del Recuperatorio 2 (Red Eléctrica,
   temperatura ambiente) llevado a Flota. Escribe el enunciado (Markdown y PDF), un datos-parcial.csv corto y los números
   de referencia, que salen de la simulación del laboratorio (y se verifican con Java en probar.js).
   El Markdown y el ejemplo para el laboratorio (ejemplo.json) quedan acá; el PDF y el CSV, en el material del recuperatorio.
   Uso: node herramientas/laboratorio/practica-pendiente/armar.js [carpeta de salida] [--pdf]   (el PDF necesita Playwright) */
const fs = require('fs'), path = require('path');
const M = require('../motor.js');
const SALIDA = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : path.join(__dirname, '../../../material/backend-de-aplicaciones/p1/parcial/recuperatorio-1/practica-pendiente');
const ORIGINAL = fs.readFileSync(path.join(__dirname, 'datos-original.csv'), 'utf8');

// 8 filas del datos.csv del preenunciado (con sus casos testigo) y 14 del formato nuevo, intercaladas
const CSV = `patente,zona,velocidadPromedio,cargaToneladas,estado,pendientePromedio
trk-0101,NORTE,70,25,EN_RUTA,12
trk-0012,NORTE,76,11,EN_RUTA
trk-0102,SUR,60,10,DEMORADO,0
trk-0005,NORTE,128,43,EN_RUTA
trk-0112,NORTE,128,43,EN_RUTA,10
trk-0104,NORTE,80,20,EN_RUTA,31
trk-0019,SUR,80,20,EN_DEPOSITO
trk-0107,NORTE,999,abc,EN_DEPOSITO,x
trk-0103,CENTRO,90,30,EN_RUTA,30
trk-0038,CENTRO,101,11,DEMORADO
trk-0108,SUR,70,20,PERDIDO,10

trk-0001,SUR,51,11,DEMORADO
trk-0105,SUR,75,15,DEMORADO,-1
trk-0109,CENTRO,70,20,EN_RUTA,10,extra
trk-0041,CENTRO,70,25,PERDIDO
trk-0106,CENTRO,2,-5,EN_RUTA,0
patente,zona,velocidadPromedio,cargaToneladas,estado,pendientePromedio
trk-0004,CENTRO,92,12,EN_RUTA
trk-0110,NORTE,85,40,DEMORADO,diez
trk-0111,CENTRO, 64 , 18 , EN_RUTA , 25
trk-0009,NORTE,abc,20,EN_RUTA
`;

function enunciado(r0, r) {
  const zonas = r.porZona.map(([z, t]) => `${z} ${t}`);
  return `# Parcial: Flota Logística con Pendiente del Tramo

Tiempo orientativo: 50 minutos. Partir del proyecto 01-modelo-inicial y conservar sus comportamientos y pruebas existentes. El parcial extiende la lectura de telemetría incorporando la pendiente promedio del tramo que recorre cada vehículo.

Parcial de práctica: es hipotético, armado con el mismo cambio que el Recuperatorio 2 (Red Eléctrica, temperatura ambiente) sobre el preenunciado de Flota Logística.

## Ejecución

Requiere JDK 17, 21 o 25 y Maven 3.9.x. Desde la raíz del proyecto:

    mvn test
    java -cp target/classes ar.edu.backend.App datos/datos.csv
    java -cp target/classes ar.edu.backend.App datos/datos-parcial.csv

La primera ejecución de Maven puede requerir Internet. Luego, validar también con mvn -o test. La aplicación no requiere dependencias externas en ejecución.

## Formatos de entrada

Se deben admitir los dos encabezados exactos:

- Formato original: \`patente,zona,velocidadPromedio,cargaToneladas,estado\`
- Formato del parcial: \`patente,zona,velocidadPromedio,cargaToneladas,estado,pendientePromedio\`

Cada archivo contiene un único encabezado. Bajo el encabezado original, cada fila debe tener cinco campos y usa el formato anterior. Bajo el encabezado nuevo, se admiten filas de cinco campos (formato anterior) y de seis campos (formato nuevo); detectar el formato de cada fila por su ancho. No aceptar anchos distintos de cinco o seis, ni repetir un encabezado en medio del archivo. Reutilizar el flujo de lectura y clasificación; no duplicar el parser.

Los archivos son UTF-8. Cada registro ocupa una línea, con campos separados por coma y sin comas, comillas ni saltos de línea internos. Quitar espacios externos de cada campo. El uso de split(",", -1) conserva campos finales vacíos y es válido para este formato controlado.

No se exige unicidad de patentes. Cada fila válida cuenta como un viaje independiente. Las zonas distinguen mayúsculas y minúsculas.

## Nueva columna y jerarquía obligatoria

La columna pendientePromedio es un valor entero en porcentaje y admite valores entre 0 y 30, inclusive. Un valor fuera de ese rango invalida la fila.

La nueva columna debe implementarse mediante herencia desde la jerarquía existente. Se requiere una jerarquía equivalente a:

    VehiculoRuta
    └── VehiculoConPendiente

VehiculoRuta representa el formato original y conserva sus datos, invariantes y cálculo. Su método de fábrica desdeCampos(String[] campos) debe inspeccionar el ancho de la fila y crear un VehiculoRuta para cinco campos o un VehiculoConPendiente para seis campos. Toda decisión de tipo e instanciación ocurre en este método; el parser debe llamarlo y no crear directamente ninguna de las dos clases.

VehiculoConPendiente debe extender directamente a VehiculoRuta, agregar y exponer la pendiente promedio, y validar su rango. No agregar una clase intermedia que duplique a VehiculoRuta. El parser debe almacenar los resultados como VehiculoRuta para que filtros, sumas y agrupamientos trabajen polimórficamente con ambos formatos.

El formato original de cinco columnas conserva el cálculo anterior. Para el formato nuevo, VehiculoConPendiente calcula el índice de desgaste con la fórmula indicada abajo. La conversión textual, la validación del índice y la construcción del objeto deben quedar en la lógica de dominio cercana a la clase que representa el viaje. El constructor de VehiculoRuta recibe el indiceDesgaste calculado y conserva su invariante: con el formato original, un índice que no coincide con la fórmula original es inválido (lo verifica un test existente); con el formato nuevo, el índice tiene que coincidir con la fórmula ponderada.

## Validaciones, estados y cálculos

Se conservan todas las reglas del preparcial:

- patente y zona no pueden estar vacías.
- velocidadPromedio debe ser un entero mayor a 0 y menor a 130.
- cargaToneladas no puede ser mayor a 45.
- El índice de desgaste calculado debe estar entre 1 y 90, inclusive.
- EN_RUTA y DEMORADO se convierten en vehículos. Cualquier otro estado, excepto EN_DEPOSITO, es inválido.
- Se verifica primero el ancho de la fila. Si el ancho es correcto, EN_DEPOSITO se descarta sin validar los demás campos, incluida la pendiente promedio.
- Una fila vacía es inválida. Los errores de una fila no interrumpen la lectura de las restantes.

Para el formato original se mantiene:

    indiceDesgaste = (velocidadPromedio × 0.6) + (cargaToneladas × 0.4)

Para las filas del formato nuevo se usa la fórmula ponderada:

    indiceDesgaste = (velocidadPromedio × 0.50) + (cargaToneladas × 0.30) + (pendientePromedio × 0.20)

El índice se conserva como entero truncando la parte decimal hacia cero. Se valida el rango de 1 a 90 sobre ese entero. Por ejemplo, con velocidad promedio 70, carga 25 y pendiente 12, el índice nuevo es 44 (44.9 truncado); con el formato original y los mismos valores de velocidad y carga, es 52.

El costo por desgaste operativo no cambia: cada flete genera en promedio 2000 USD de facturación, y el costo es entero, sin redondeo:

    costoDesgasteOperativo = 2000 × indiceDesgaste / 100

En Java, calcularlo como 2000 * indiceDesgaste / 100, en ese orden, usando división entera. En el ejemplo anterior, los costos son 880 USD para el formato nuevo y 1040 USD para el original.

Un encabezado incorrecto debe abortar con IllegalArgumentException; los fallos de lectura deben propagar IOException. Los errores de filas inválidas registran el número físico de línea; el encabezado no cuenta como fila leída.

## Resultado requerido

1. Leer ambos formatos con el mismo flujo de clasificación y conservar la compatibilidad con el CSV original.
2. Implementar la nueva columna con la jerarquía de herencia requerida y aplicar sus invariantes.
3. Usar pendientePromedio en el índice de desgaste de las filas nuevas y conservar el cálculo anterior para las filas originales.
4. Mantener el tratamiento de EN_DEPOSITO, estados desconocidos, errores por fila y encabezados inválidos.
5. Hacer que Flota opere sobre VehiculoRuta e incluya los dos tipos en filtros, sumas y agrupamientos por zona.
6. Conservar copia defensiva de las colecciones y getters explícitos. No agregar Lombok ni dependencias de ejecución.
7. Actualizar App para que, sin argumentos, lea datos/datos-parcial.csv; si se pasa una ruta como argumento, debe usarla. Mostrar el resumen del parseo y el panorama.
8. Conservar y pasar los tests existentes. Agregar pruebas para ambos encabezados, límites de la pendiente, fórmulas, costos, ancho incorrecto y descartes. JUnit 5 es la única dependencia y se usa solo en tests.

El CSV original debe seguir produciendo sus resultados de referencia: ${r0.leidas} filas leídas, ${r0.procesadas} procesadas, ${r0.descartadas} descartadas y ${r0.invalidas} inválidas; costo total ${r0.total}, por zona ${r0.porZona.map(([z, t]) => `${z} ${t}`).join(', ')}; ${r0.menor55} índices de desgaste menores a 55. Para el nuevo formato, verificar ambos límites de pendientePromedio y los ejemplos numéricos de esta consigna; no asumir que el índice o los agregados coinciden con los del archivo original.

El archivo de ejemplo combinado datos/datos-parcial.csv es corto: incluye 8 registros del archivo original (con sus casos testigo) y 14 líneas de prueba del nuevo formato, intercaladas bajo un único encabezado de seis columnas. Las filas originales de cinco campos conservan el cálculo anterior; las nuevas prueban ambos límites válidos de la pendiente, valores fuera de rango, un valor no numérico, índice fuera de rango, un índice que solo es válido con la fórmula nueva (trk-0112 contra trk-0005), descarte, estado desconocido, ancho incorrecto, línea vacía y un encabezado repetido.

El conjunto combinado debe producir ${r.leidas} filas leídas, ${r.procesadas} procesadas, ${r.descartadas} descartadas y ${r.invalidas} inválidas; costo total ${r.total}, por zona ${zonas.slice(0, -1).join(', ')} y ${zonas[zonas.length - 1]}; ${r.menor55} índices de desgaste menores a 55.

## Preparación y entrega

Usar el archivo combinado datos/datos-parcial.csv como entrada predeterminada. Incorporar o actualizar pruebas para cubrir los casos requeridos. Ejecutar:

    mvn test
    java -cp target/classes ar.edu.backend.App
    java -cp target/classes ar.edu.backend.App datos/datos.csv

Entregar el proyecto con pom.xml, src/ y datos/; excluir target/, .git/ y archivos del IDE. Incluir un texto breve DECISIONES.md (3–5 líneas) que indique cómo se resolvió la herencia y si quedó algo pendiente.
`;
}

const cfg = M.normalizar(M.leerEnunciado(enunciado({ leidas: 0, procesadas: 0, descartadas: 0, invalidas: 0, total: 0, porZona: [['NORTE', 0]], menor55: 0 }, { leidas: 0, procesadas: 0, descartadas: 0, invalidas: 0, total: 0, porZona: [['NORTE', 0]], menor55: 0 })).cfg);
const r0 = M.simular(ORIGINAL, cfg), r = M.simular(CSV, cfg);
if (r0.abortado || r.abortado) { console.error(r0.abortado || r.abortado, JSON.stringify(cfg.columna)); process.exit(1); }
const md = enunciado(r0, r);
fs.mkdirSync(SALIDA, { recursive: true });
fs.writeFileSync(path.join(__dirname, 'enunciado-parcial.md'), md);
fs.writeFileSync(path.join(SALIDA, 'datos-parcial.csv'), CSV);
fs.writeFileSync(path.join(__dirname, 'ejemplo.json'), JSON.stringify({
  id: 'i', titulo: 'Pendiente del tramo (con su CSV)', estilo: 'como el Recuperatorio 2 (Red Eléctrica): herencia por ancho y otra fórmula del índice',
  texto: md, csv: CSV,
  esperado: { columna: { nombre: 'pendientePromedio', tipo: 'entero', rango: { min: 0, minIncl: true, max: 30, maxIncl: true } }, anchoMixto: true, columnaEnSubclase: true, indiceNuevo: { v: 0.5, c: 0.3, x: 0.2 }, especiales: [{ clase: 'VehiculoConPendiente', ops: [], topes: [] }], conteo: null },
}, null, 1) + '\n');
module.exports = { md, CSV, cfg };
console.log('original:', r0.leidas, r0.procesadas, r0.descartadas, r0.invalidas, r0.total, '· combinado:', r.leidas, r.procesadas, r.descartadas, r.invalidas, r.total, JSON.stringify(r.porZona), r.menor55);

if (process.argv.includes('--pdf')) {
  // Como los de la cátedra: el Markdown impreso con Chrome, con el nombre del archivo y la fecha arriba y el número de página abajo
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
    const archivo = path.join(SALIDA, 'enunciado-parcial.pdf');
    await pg.pdf({ path: archivo, format: 'A4', margin: { top: '1.6cm', bottom: '1.6cm', left: '1.8cm', right: '1.8cm' }, displayHeaderFooter: true,
      headerTemplate: '<div style="font-size:8px;width:100%;padding:0 1.8cm;color:#555">enunciado-parcial.md<span style="float:right">2026-11-17</span></div>',
      footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#555"><span class="pageNumber"></span>/<span class="totalPages"></span></div>' });
    await b.close();
    // sin metadatos (con pymupdf), salvo el título
    require('child_process').execFileSync('python3', ['-I', '-c', `import sys, pymupdf as fitz
d = fitz.open(sys.argv[1])
d.set_metadata({'title': 'Parcial de práctica · Flota Logística con pendiente del tramo', 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': ''})
d.del_xml_metadata()
d.save(sys.argv[1] + '.tmp', garbage=3, deflate=True)
`, archivo]);
    fs.renameSync(archivo + '.tmp', archivo);
    console.log('PDF:', path.relative(process.cwd(), archivo));
  })();
}
