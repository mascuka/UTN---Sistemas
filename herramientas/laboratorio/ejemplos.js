/* Enunciados de práctica sobre Flota Logística, escritos como los de la cátedra (Parciales 3K1 y 3K2, Simulacros 1 a 4).
   Son hipotéticos: sirven para probar el lector y para practicar. Cada uno trae lo que el lector tiene que entender. */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica(raiz, true);
  else raiz.Ejemplos = fabrica(raiz, false);
}(typeof self !== 'undefined' ? self : this, function (raiz, enNode) {
  'use strict';
  const PIE = `
Resultado requerido
1. Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.
2. Hacer que getCostoDesgasteOperativo(), getCostoTotalDesgasteOperativo(), los filtros por costo y los totales por zona reflejen la nueva regla.
3. @CONTEO
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, @CANTIDADES total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes y los nuevos. Puede agregar tests propios.

Se evalúa comportamiento observable, encapsulamiento y distribución de responsabilidades. Puede usar herencia, composición u otra solución razonable. No se evalúa el nombre concreto de una subclase.

Preparación y entrega
Desde la raíz de su copia de 01-modelo-inicial, copiar tests-nuevos/ar a src/test/java/ar fusionando directorios. Copiar datos-parcial.csv a datos/datos-parcial.csv y ajustar la ruta predeterminada del main.
mvn test
java -cp target/classes ar.edu.backend.App datos/datos-parcial.csv
Entregar un único ZIP del proyecto con pom.xml, src/ y datos/; excluir target/, .git/ y archivos del IDE. Incluir un texto breve DECISIONES.md (3–5 líneas) que indique la estrategia elegida y si quedó algo pendiente.`;
  const CAB = `Tiempo orientativo: 45 minutos. Partir exactamente del proyecto preparcial. Se entregan este documento, datos-parcial.csv y la carpeta tests-nuevos. Mantener los tests existentes.
El CSV del parcial contiene 140 filas de datos más encabezado (141 líneas); es un conjunto distinto del preparcial de 60 filas. El volumen no agrega reglas ni tareas de programación.`;
  const pie = (conteo, cantidades) => PIE.replace('@CONTEO', conteo).replace('@CANTIDADES', cantidades ? cantidades + ', ' : '');

  const E = [
    {
      id: 'a', titulo: 'Caso A · Carga refrigerada', estilo: 'como el Parcial 3K2 (envíos prioritarios)',
      texto: `Parcial práctico: carga refrigerada
${CAB}
La empresa incorpora el transporte de carga REFRIGERADA. Se necesita procesar ambos tipos de carga en una misma colección y obtener sus costos correctos.

Reglas nuevas
El nuevo encabezado es patente,zona,velocidadPromedio,cargaToneladas,estado,tipoCarga. Conservar también el formato original de cinco columnas: todos sus vehículos llevan carga general. Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.
Para filas EN_RUTA o DEMORADO del nuevo formato, el sexto campo admite exactamente GENERAL o REFRIGERADA, después de quitar espacios externos. Un valor vacío o desconocido hace inválida la fila.
- GENERAL conserva todas las reglas anteriores y su costo.
- REFRIGERADA respeta las validaciones anteriores, admite como máximo 30 toneladas inclusive y cuesta 300 USD adicionales sobre el costo de una carga general del mismo índice. El recargo se aplica una sola vez por vehículo.
- Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar velocidad, carga ni tipo de carga. Las filas inválidas se registran y la carga continúa.
Ejemplos: un vehículo GENERAL con índice 50 cuesta 1000; uno REFRIGERADA con índice 50 cuesta 1300; uno REFRIGERADA con 31 toneladas es inválido.
${pie('Incorporar en el colector un conteo por tipo de carga. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío o conteos cero.', 'cantidades GENERAL/REFRIGERADA')}`,
      esperado: { columna: { nombre: 'tipoCarga', tipo: 'texto', valores: ['GENERAL', 'REFRIGERADA'], defecto: 'GENERAL', vacio: 'invalida' }, especiales: [{ clase: 'VehiculoRefrigerada', ops: [{ op: 'suma', n: 300 }], topes: [{ campo: 'carga', op: 'max', n: 30, incl: true }] }], conteo: 'columna', descartes: ['EN_DEPOSITO'] },
    },
    {
      id: 'b', titulo: 'Caso B · Kilómetros con punto y coma', estilo: 'como el Simulacro 3 (separador ;)',
      texto: `Parcial práctico: kilómetros recorridos
${CAB}
Logística empieza a registrar los kilómetros que recorrió cada vehículo y el nuevo archivo viene separado por punto y coma.

Reglas nuevas
El nuevo encabezado es patente;zona;velocidadPromedio;cargaToneladas;estado;kilometros . Conservar también el formato original de cinco columnas separadas por comas: todos sus vehículos tienen 0 kilómetros. Cada fila debe tener el ancho indicado por su encabezado.
Los kilómetros deben ser un entero entre 0 y 5000 inclusive, después de quitar espacios externos. Un valor vacío, no numérico o fuera de ese rango hace inválida la fila.
El costo por desgaste operativo de todos los vehículos suma 1 USD por cada 10 kilómetros recorridos (división entera).
Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar los demás campos.
${pie('Incorporar en el colector un conteo por zona.', '')}`,
      esperado: { separador: ';', columna: { nombre: 'kilometros', tipo: 'entero', rango: { min: 0, minIncl: true, max: 5000, maxIncl: true }, defecto: 0 }, extras: [{ op: 'sumaPorCada', n: 1, cada: 10 }], conteo: 'zona' },
    },
    {
      id: 'c', titulo: 'Caso C · Mantenimiento y demoras', estilo: 'como el Simulacro 2 (estados nuevos)',
      texto: `Parcial práctico: mantenimiento y demoras
${CAB}
Reglas nuevas
El archivo conserva el encabezado de cinco columnas.
MANTENIMIENTO indica que el vehículo está en el taller. Se descarta después de verificar el ancho de la fila, sin validar los demás campos operativos, igual que EN_DEPOSITO.
EN_RUTA conserva el comportamiento del preparcial.
Un vehículo DEMORADO respeta las validaciones anteriores y su costo por desgaste operativo es un 15 % más alto (en enteros, después de calcular el costo normal).
${pie('Incorporar en Flota el total de vehículos DEMORADO y un conteo por estado.', 'cantidades EN_RUTA/DEMORADO,')}`,
      esperado: { columna: null, descartes: ['EN_DEPOSITO', 'MANTENIMIENTO'], especiales: [{ clase: 'VehiculoDemorado', ops: [{ op: 'porcentaje', n: 15 }], topes: [] }], conteo: 'estado', totales: [{ campo: 'estado', valor: 'DEMORADO' }] },
    },
    {
      id: 'd', titulo: 'Caso D · Facturación por flete', estilo: 'el mismo cambio del Parcial 3K1 (ingresos)',
      texto: `Parcial práctico: facturación por flete
${CAB}
Administración incorpora para cada vehículo la facturación por flete que genera. Se necesita procesar el nuevo dato utilizando la misma colección y obtener sus costos y totales correctos.

Reglas nuevas
El nuevo encabezado es patente,zona,velocidadPromedio,cargaToneladas,estado,facturacion. Conservar también el formato original de cinco columnas: todos los vehículos en este punto tienen una facturación de 2000.
Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.
Para filas con el estado EN_RUTA o DEMORADO del nuevo formato, el sexto campo admite valores mayores iguales a 2000 pero menores a 3800, después de quitar los espacios externos. Un valor por fuera de ese rango hace inválida la fila.
Debe conservar toda validación que esté previamente cargada en el preenunciado. Usted debe modificar para que la facturación sea considerada al realizar el cálculo del costo por desgaste operativo, para que tome el valor ingresado, sin alterar la estructura de objetos del preparcial.
Ejemplos: un vehículo con un índice de desgaste de 65 y una facturación de 3000 USD tiene un costo por desgaste operativo de 1950 USD.
${pie('Incorporar en el colector un conteo por estado, que indique la cantidad de vehículos que se encuentran en cada estado procesado.', 'cantidades EN_RUTA/DEMORADO')}`,
      esperado: { columna: { nombre: 'facturacion', tipo: 'entero', rango: { min: 2000, minIncl: true, max: 3800, maxIncl: false }, defecto: 2000 }, baseDesdeColumna: true, especiales: [], conteo: 'estado' },
    },
    {
      id: 'e', titulo: 'Seguro de carga', estilo: 'como el Simulacro 4 (protección de compras)',
      texto: `Parcial práctico: seguro de carga
${CAB}
La empresa incorpora el seguro de la carga (cubre la mercadería ante robo o rotura durante el viaje). Se necesita procesar vehículos con y sin cobertura en una misma colección y obtener sus costos correctos.

Reglas nuevas
El nuevo encabezado es patente,zona,velocidadPromedio,cargaToneladas,estado,diasCobertura . Conservar también el formato original de cinco columnas: todos esos vehículos son sin seguro. Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.
Para filas EN_RUTA o DEMORADO del nuevo formato, el sexto campo es un entero (tras quitar espacios externos):
- 0 conserva todas las reglas anteriores y su costo. Es un vehículo sin seguro.
- 30, 90 o 180 son plazos de cobertura. El vehículo queda asegurado: respeta las validaciones anteriores, admite como máximo 40 toneladas inclusive y suma una prima de 200 USD por cada 30 días sobre el costo de un vehículo sin seguro. La prima se aplica una sola vez por vehículo.
- Un valor vacío, no numérico o un plazo distinto de 0/30/90/180 hace inválida la fila.
Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar velocidad, carga ni días de cobertura.
${pie('Incorporar en el colector un conteo por modalidad. Puede elegir el nombre y representación de esa operación. No se pide agrupar por plazo.', 'cantidades SIN_SEGURO/ASEGURADO')}`,
      esperado: { columna: { nombre: 'diasCobertura', tipo: 'entero', valores: [30, 90, 180, 0], defecto: 0 }, especiales: [{ clase: 'VehiculoConDiasCobertura', cuando: { op: 'mayor' }, ops: [{ op: 'sumaPorCada', n: 200, cada: 30 }], topes: [{ campo: 'carga', op: 'max', n: 40, incl: true }], etiqueta: 'ASEGURADO' }], conteo: 'tipo', etiquetaBase: 'SIN_SEGURO' },
    },
    {
      id: 'f', titulo: 'Prioridad con restricciones', estilo: 'como el Simulacro 1 (morosidad)',
      texto: `Parcial práctico: viajes urgentes
${CAB}
La empresa incorpora si el viaje es NORMAL o URGENTE. Se necesita procesar los viajes considerando la prioridad y obtener sus costos correctos.

Reglas Nuevas
El nuevo encabezado del archivo es patente,zona,velocidadPromedio,cargaToneladas,estado,prioridad . Se conserva el formato original de las cinco columnas: todos sus viajes son normales. Cada fila debe tener el ancho indicado en su encabezado, no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.
Para las filas con el estado EN_RUTA, el sexto campo puede admitir NORMAL o URGENTE; los vehículos DEMORADO solo admiten NORMAL. Después de quitar espacios externos, si un vehículo DEMORADO tiene un valor distinto a NORMAL, esa fila se considera inválida; también es inválida si el valor está vacío o es desconocido.
- NORMAL conserva todas las reglas anteriores y sus cálculos tal cual están definidos.
- URGENTE se considera válido solo si su velocidad supera los 60 km/h, y su costo es un 25 % más que el de un viaje normal.
- Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar velocidad ni prioridad.
${pie('Incorporar en Flota un conteo por prioridad.', 'cantidades NORMAL/URGENTE')}`,
      esperado: { columna: { nombre: 'prioridad', tipo: 'texto', valores: ['NORMAL', 'URGENTE'], defecto: 'NORMAL' }, restricciones: [{ estado: 'DEMORADO', valores: ['NORMAL'] }], especiales: [{ clase: 'VehiculoUrgente', ops: [{ op: 'porcentaje', n: 25 }], topes: [{ campo: 'velocidad', op: 'min', n: 60, incl: false }] }], conteo: 'columna' },
    },
    {
      id: 'g', titulo: 'Peajes (por presencia de un valor)', estilo: 'como el Simulacro 3 (juegos cooperativos)',
      texto: `Parcial práctico: peajes
${CAB}
Reglas nuevas
El nuevo encabezado es patente,zona,velocidadPromedio,cargaToneladas,estado,peajes . Conservar también el formato original de cinco columnas: todos sus vehículos son normales. Cada fila debe tener el ancho indicado por su encabezado.
Para vehículos con peajes (indicado por la presencia de un valor en la 6ta columna):
- La cantidad de peajes debe ser un entero entre 1 y 10. De lo contrario, la fila es inválida.
- El costo se calcula sumando 50 USD por cada peaje al costo por desgaste operativo normal.
${pie('Servicio: incorpore un método que cuente vehículos por tipo (normal/con peajes).', 'cantidades NORMAL/CON_PEAJES')}`,
      esperado: { columna: { nombre: 'peajes', tipo: 'entero', rango: { min: 1, minIncl: true, max: 10, maxIncl: true }, vacio: 'defecto', defecto: 0 }, especiales: [{ clase: 'VehiculoConPeajes', cuando: { op: 'presente' }, ops: [{ op: 'sumaPorCada', n: 50, cada: 1 }] }], conteo: 'tipo' },
    },
    {
      id: 'h', titulo: 'Estado nuevo EN_TALLER', estilo: 'sin columna nueva, como la primera parte del Simulacro 2',
      texto: `Parcial práctico: vehículos en el taller
${CAB}
Reglas nuevas
El archivo conserva el encabezado y las cinco columnas del preparcial.
Se incorpora el estado EN_TALLER: es un estado válido y debe incorporarse a la colección porque forma parte de la facturación.
Un vehículo EN_TALLER respeta las validaciones anteriores, admite como máximo 20 toneladas inclusive y su costo por desgaste operativo es el doble del normal.
EN_RUTA y DEMORADO conservan el comportamiento del preparcial. EN_DEPOSITO se sigue descartando sin validar.
${pie('Incorporar en el colector un conteo por estado.', 'cantidades EN_RUTA/DEMORADO/EN_TALLER')}`,
      esperado: { columna: null, estados: ['EN_RUTA', 'DEMORADO', 'EN_TALLER'], especiales: [{ clase: 'VehiculoEnTaller', ops: [{ op: 'multiplica', n: 2 }], topes: [{ campo: 'carga', op: 'max', n: 20, incl: true }] }], conteo: 'estado' },
    },
  ];
  // Los parciales de práctica con su propio CSV (practica-pendiente/ejemplo.json): en la página los mete armar.py
  let extra = [];
  if (enNode) { try { extra = [require('./practica-pendiente/ejemplo.json')]; } catch (e) { extra = []; } }
  else extra = (raiz && raiz.EJEMPLOS_EXTRA) || [];
  return E.concat(extra);
}));
