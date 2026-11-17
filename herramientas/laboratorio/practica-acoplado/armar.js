/* Parcial de práctica «Flota Logística con acoplado»: lo que más se repite en los parciales de la cátedra, sobre el
   preenunciado de Flota. Una 6.ª columna entera con rango (como el 3K1 y el Recuperatorio 2) que, con valor mayor a 0,
   hace que el vehículo cueste distinto y tenga un tope propio (una subclase, como PRIORITARIO del 3K2 y ASEGURADO del
   Simulacro 4: un tope y un recargo «por cada»), un conteo por modalidad con «cantidades A/B» y el main del parcial.
   Uso: node herramientas/laboratorio/practica-acoplado/armar.js [carpeta de salida] [--pdf]   (el PDF necesita Playwright) */
const { armar } = require('../practica-comun.js');

// 26 filas con el encabezado nuevo: de cada tipo, los límites y una inválida por cada regla
const CSV = `patente,zona,velocidadPromedio,cargaToneladas,estado,acoplado
trk-0301,NORTE,76,11,EN_RUTA,0
trk-0302,NORTE,76,11,EN_RUTA,5
trk-0303,SUR,90,20,DEMORADO,20
trk-0304,SUR,91,20,EN_RUTA,10
trk-0305,CENTRO,100,15,EN_RUTA,0
trk-0306,CENTRO,60,10,EN_RUTA,21
trk-0307,NORTE,60,10,DEMORADO,-1
trk-0308,SUR,60,10,EN_RUTA,
trk-0309,NORTE,60,10,EN_RUTA,cinco
trk-0310,SUR,999,abc,EN_DEPOSITO,x
trk-0311,CENTRO,121,45,EN_RUTA,0
trk-0312,CENTRO,121,45,EN_RUTA,3
trk-0313,NORTE,128,43,EN_RUTA,0
trk-0314,SUR,85,46,DEMORADO,2
trk-0315,NORTE,10,-5,EN_RUTA,4
trk-0316,CENTRO,60,10,EN_RUTA
trk-0317,SUR,60,10,EN_RUTA,1,2

trk-0319,NORTE,70,25,PERDIDO,0
trk-0320,CENTRO,51,11,DEMORADO, 8
trk-0321,NORTE,92,12,EN_RUTA,0
trk-0322,SUR,80,20,EN_DEPOSITO,0
trk-0302,NORTE,60,10,DEMORADO,1
trk-0324,CENTRO,0,10,EN_RUTA,3
trk-0325,SUR,62,12,EN_RUTA,0
trk-0326,CENTRO, 72 , 12 , DEMORADO , 6
`;

function enunciado(r0, r) {
  const zonas = r.porZona.map(([z, t]) => `${z} ${t}`), zonas0 = r0.porZona.map(([z, t]) => `${z} ${t}`);
  return `# Parcial práctico: viajes con acoplado

Tiempo orientativo: 45 minutos. Partir exactamente del proyecto preparcial. Se entregan este documento y datos-parcial.csv. Mantener los tests existentes.

El CSV del parcial es corto: contiene ${r.leidas} filas de datos más encabezado; es un conjunto distinto del preparcial de 60 filas. El volumen no agrega reglas ni tareas de programación.

Parcial de práctica: es hipotético, armado con lo que más se repite en los parciales y simulacros de la cátedra (3K1, 3K2, Simulacro 4 y Recuperatorio 2) sobre el preenunciado de Flota Logística.

La empresa incorpora vehículos que viajan con acoplado. Se necesita procesar vehículos con y sin acoplado en una misma colección y obtener sus costos correctos.

## Reglas nuevas

El nuevo encabezado es \`patente,zona,velocidadPromedio,cargaToneladas,estado,acoplado\`. Conservar también el formato original de cinco columnas: todos esos vehículos viajan sin acoplado. Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.

Para filas EN_RUTA o DEMORADO del nuevo formato, el sexto campo es un entero entre 0 y 20, inclusive, después de quitar espacios externos: el peso del acoplado. Un valor vacío, no numérico o fuera de ese rango hace inválida la fila.

- 0 conserva todas las reglas anteriores y su costo. Es un vehículo sin acoplado.
- Con un valor mayor a 0, el vehículo lleva acoplado: respeta las validaciones anteriores, su velocidad promedio no puede superar los 90 km/h y suma 40 USD por cada tonelada de acoplado sobre el costo de un vehículo sin acoplado con los mismos datos.
- Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar velocidad, carga ni acoplado. Las filas inválidas se registran y la carga continúa.

Ejemplos: un vehículo con índice 50 sin acoplado cuesta 1000; con 5 toneladas de acoplado, 1200; con acoplado a 91 km/h es inválido (a 90 km/h vale); con 21 toneladas de acoplado la fila es inválida.

## Resultado requerido

1. Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.
2. Hacer que \`getCostoDesgasteOperativo()\`, el costo total, los filtros por costo y los totales por zona reflejen la nueva regla.
3. Incorporar en el colector un conteo por modalidad. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío o conteos cero.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, cantidades SIN_ACOPLADO/CON_ACOPLADO, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes. Agregar tests propios para el acoplado (límites 0 y 20, tope de 90 km/h, recargo, conteo y ambos encabezados).

Se evalúa comportamiento observable, encapsulamiento y distribución de responsabilidades. Puede usar herencia, composición u otra solución razonable. Puede usar Streams o ciclos; no se exige una jerarquía ni una técnica determinada. No se evalúa el nombre concreto de una subclase.

El CSV original debe seguir produciendo sus resultados de referencia: ${r0.leidas} filas leídas, ${r0.procesadas} procesadas, ${r0.descartadas} descartadas y ${r0.invalidas} inválidas; costo total ${r0.total}, por zona ${zonas0.join(', ')}; ${r0.menor55} índices de desgaste menores a 55.

El archivo del parcial debe producir ${r.leidas} filas leídas, ${r.procesadas} procesadas, ${r.descartadas} descartadas y ${r.invalidas} inválidas; costo total ${r.total}, por zona ${zonas.slice(0, -1).join(', ')} y ${zonas[zonas.length - 1]}; ${r.menor55} índices de desgaste menores a 55.

## Preparación y entrega

Desde la raíz de su copia de 01-modelo-inicial, copiar datos-parcial.csv a datos/datos-parcial.csv y ajustar la ruta predeterminada del main.

    mvn test
    java -cp target/classes ar.edu.backend.App datos/datos-parcial.csv

Entregar un único ZIP del proyecto con pom.xml, src/ y datos/; excluir target/, .git/ y archivos del IDE. Incluir un texto breve DECISIONES.md (3–5 líneas) que indique la estrategia elegida y si quedó algo pendiente.

Distribución sugerida: 5 minutos de lectura, 25 de cambios, 10 de pruebas y 5 para revisar y empaquetar.
`;
}

armar({
  carpeta: __dirname, material: 'practica-acoplado', csv: CSV, enunciado,
  tituloPdf: 'Parcial de práctica · Flota Logística con acoplado',
  ejemplo: {
    id: 'j', titulo: 'Viajes con acoplado (con su CSV)', estilo: 'lo más probable: columna con rango, subclase con tope y recargo, conteo por modalidad',
    esperado: { columna: { nombre: 'acoplado', tipo: 'entero', rango: { min: 0, minIncl: true, max: 20, maxIncl: true }, defecto: 0 }, columnaEnSubclase: false,
      especiales: [{ clase: 'VehiculoConAcoplado', cuando: { op: 'mayor', valor: 0 }, ops: [{ op: 'sumaPorCada', n: 40, cada: 1 }], topes: [{ campo: 'velocidad', op: 'max', n: 90, incl: true }], etiqueta: 'CON_ACOPLADO' }],
      conteo: 'tipo', etiquetaBase: 'SIN_ACOPLADO' },
  },
});
