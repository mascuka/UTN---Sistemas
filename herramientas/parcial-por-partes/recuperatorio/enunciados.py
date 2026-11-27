"""Los enunciados del recuperatorio por partes, escritos como los de la cátedra (Parciales 3K1 y 3K2, simulacros), y lo
que pide cada ejercicio, para pintarlo en la pestaña Enunciado. En el parcial no dicen «agregá getMayorCosto()»: dicen
«Incorporar en el colector…» y el nombre lo elegís vos. Por eso cada ejercicio muestra la frase como saldría en el examen.

DOCS: clave → {titulo, nota, texto}. El texto es Markdown simple: «# » título, «## » sección, «- » viñeta, «1. » lista
numerada, `código` y párrafos de una línea.
MARCAS: id del ejercicio → (clave del enunciado, [frases a pintar]). Cada frase tiene que estar tal cual en el texto
(armar.py lo controla) y no puede cortar un `código` por la mitad."""

CABEZA = """Tiempo orientativo: 45 minutos. Partir exactamente del proyecto preparcial. Se entregan este documento, datos-parcial.csv y la carpeta tests-nuevos. Mantener los tests existentes.
El CSV del parcial contiene 140 filas de datos más encabezado (141 líneas); es un conjunto distinto del preparcial de 60 filas. El volumen no agrega reglas ni tareas de programación."""

PIE = """Se evalúa comportamiento observable, encapsulamiento y distribución de responsabilidades. Puede usar herencia, composición u otra solución razonable. Puede usar Streams o ciclos; no se exige una jerarquía ni una técnica determinada. No se evalúa el nombre concreto de una subclase."""

NOTA = 'Hipotético: escrito con las frases que usa la cátedra en los Parciales 3K1 y 3K2 y en los simulacros. En el parcial no te dicen el nombre del método ni de la subclase: los elegís vos.'

DOCS = {
    'R': dict(titulo='Recuperatorio · Tramo sin pavimentar', nota='El enunciado de verdad del recuperatorio (noviembre de 2026).', texto='# Parcial: Flota Logística con Tramo sin Pavimentar\nTiempo orientativo: 45 minutos. Partir del proyecto 01-modelo-inicial y conservar sus comportamientos y pruebas existentes.\nEl parcial extiende la telemetría de los vehículos incorporando el porcentaje del recorrido realizado por caminos sin pavimentar.\n## Formatos de entrada\nSe deben admitir los dos encabezados exactos:\n- Formato original: `patente,zona,velocidadPromedio,cargaToneladas,estado`\n- Formato del parcial: `patente,zona,velocidadPromedio,cargaToneladas,estado,porcentajeRutaSinPAvimentar`\nCada archivo contiene un único encabezado. Bajo el encabezado original, cada fila debe tener cinco campos y conserva el cálculo anterior. Bajo el encabezado nuevo, se admiten filas de cinco campos (formato original) y de seis campos (formato nuevo); detectar el formato de cada fila por su ancho. No aceptar anchos distintos de cinco o seis ni encabezados repetidos en medio del archivo. Reutilizar el flujo de lectura y clasificación; no duplicar el parser.\nLos archivos son UTF-8. Cada registro ocupa una línea, con campos separados por coma y sin comas, comillas ni saltos de línea internos. Quitar espacios externos de cada campo. El uso de `split(",", -1)` conserva campos finales vacíos y es válido para este formato controlado.\nNo se exige unicidad de patentes. Cada fila válida cuenta como un viaje independiente. Las zonas distinguen mayúsculas y minúsculas.\n## Nueva columna y jerarquía obligatoria\n`porcentajeRutaSinPAvimentar` es un porcentaje entero del recorrido realizado por caminos sin pavimentar y admite valores entre 0 y 100, inclusive. Un valor fuera de ese rango invalida la fila.\nLa nueva columna debe implementarse mediante herencia desde la jerarquía existente. Se requiere una jerarquía equivalente a `VehiculoRuta` → `VehiculoRutaConTramoSinPavimentar`.\n`VehiculoRuta` representa el formato original y conserva sus datos, invariantes y cálculo. Debe incluir un método de fábrica `desdeCampos(String[] campos)` que inspeccione el ancho de la fila y cree un `VehiculoRuta` para cinco campos o un `VehiculoRutaConTramoSinPavimentar` para seis campos. Toda decisión de tipo e instanciación ocurre en este método; el parser debe llamarlo y no crear directamente ninguna de las dos clases.\n`VehiculoRutaConTramoSinPavimentar` debe extender directamente a `VehiculoRuta`, agregar y exponer el porcentaje de recorrido sin pavimentar, y validar su rango. No agregar una clase intermedia que duplique a `VehiculoRuta`. El parser debe almacenar los resultados como `VehiculoRuta` para que filtros, sumas y agrupamientos trabajen polimórficamente con ambos formatos.\nEl formato original conserva el cálculo anterior. Para el formato nuevo, `VehiculoRutaConTramoSinPavimentar` calcula el índice de desgaste con la fórmula indicada abajo. La conversión textual, la validación del índice y la construcción del objeto deben quedar en la lógica de dominio cercana a la clase que representa la medición. El constructor de `VehiculoRuta` recibe el `indiceDesgaste` calculado; no debe recalcularlo.\n## Validaciones, estados y cálculos\nSe conservan todas las reglas del preparcial:\n- patente y zona no pueden estar vacías.\n- velocidadPromedio debe ser un entero mayor a 0 y menor a 130.\n- cargaToneladas no puede ser mayor a 45.\n- El índice de desgaste calculado debe estar entre 1 y 90, inclusive.\n- EN_RUTA y DEMORADO se convierten en vehículos. Cualquier otro estado, excepto EN_DEPOSITO, es inválido.\n- Se verifica primero el ancho de la fila. Si el ancho es correcto, EN_DEPOSITO se descarta sin validar los demás campos, incluido porcentajeRutaSinPAvimentar.\n- Una fila vacía es inválida. Los errores de una fila no interrumpen la lectura de las restantes.\nPara el formato original se mantiene: `indiceDesgaste = (velocidadPromedio × 0.6) + (cargaToneladas × 0.4)`\nPara las filas del formato nuevo se usa: `indiceDesgaste = (velocidadPromedio × 0.55) + (cargaToneladas × 0.30) + (porcentajeRutaSinPAvimentar × 0.15)`\nEl índice se conserva como entero truncando la parte decimal hacia cero. Por ejemplo, con velocidad 76, carga 11 y un 30 % de recorrido sin pavimentar, el índice nuevo es 49 (49.6 truncado); con el formato original y esos valores de velocidad y carga, es 50.\nEl costo por desgaste operativo no cambia: cada flete genera en promedio 2000 USD de facturación y el costo es entero, sin redondeo: `costoDesgasteOperativo = 2000 × indiceDesgaste / 100`. En Java, calcularlo como `2000 * indiceDesgaste / 100`, en ese orden, usando división entera.\nUn encabezado incorrecto debe abortar con `IllegalArgumentException`; los fallos de lectura deben propagar `IOException`. Los errores de filas inválidas registran el número físico de línea; el encabezado no cuenta como fila leída.\n## Resultado requerido\n1. Leer ambos formatos con el mismo flujo de clasificación y conservar la compatibilidad con el CSV original.\n2. Implementar la nueva columna con la jerarquía de herencia requerida y aplicar sus invariantes.\n3. Usar porcentajeRutaSinPAvimentar en el índice de las filas nuevas y conservar el cálculo anterior para las filas originales.\n4. Mantener el tratamiento de EN_DEPOSITO, estados desconocidos, errores por fila y encabezados inválidos.\n5. Hacer que Flota opere sobre VehiculoRuta e incluya ambos tipos en filtros, sumas y agrupamientos por zona.\n6. Conservar copia defensiva de las colecciones y getters explícitos. No agregar Lombok ni dependencias de ejecución.\n7. Actualizar App para que, sin argumentos, lea `datos/datos-parcial.csv`; si se pasa una ruta como argumento, debe usarla. Mostrar el resumen del parseo y el panorama, que incluye costos por zona y la cantidad de vehículos con índice de desgaste mayor o igual a un minimo.\n8. Conservar y pasar los tests existentes. Agregar pruebas para ambos encabezados, límites del porcentaje de recorrido sin pavimentar, fórmulas, costos, ancho incorrecto y descartes. JUnit 5 es la única dependencia y se usa solo en tests.\nEl CSV original debe seguir produciendo sus resultados de referencia: 60 filas leídas, 32 procesadas, 20 descartadas, 8 inválidas, costo total 31840 y 18 índices de desgaste menores a 55. Para las filas nuevas, verificar ambos límites de porcentajeRutaSinPAvimentar y los ejemplos numéricos de esta consigna; no asumir que sus agregados coinciden con los del archivo original.\nEl archivo de ejemplo combinado `datos/datos-parcial.csv` incluye los 60 registros del archivo original y 10 filas nuevas, bajo un único encabezado de seis columnas. Las filas originales de cinco campos conservan el cálculo anterior; las nuevas filas de seis campos prueban ambos límites válidos del porcentaje, valores fuera de rango, índice fuera de rango, depósito, estado desconocido, ancho incorrecto y línea vacía.\nEl conjunto combinado debe producir 70 filas leídas, 35 procesadas, 21 descartadas y 14 inválidas; costo total 34800, por zona NORTE 12180, CENTRO 13160 y SUR 9460; 20 índices de desgaste menores a 55. `Flota.panorama()` debe incluir esa última cantidad en su salida.\n## Preparación y entrega\nUsar el archivo combinado `datos/datos-parcial.csv` como entrada predeterminada. Incorporar o actualizar pruebas para cubrir los casos requeridos. Entregar el proyecto con pom.xml, src/ y datos/; excluir target/, .git/ y archivos del IDE. Incluir un texto breve DECISIONES.md (3–5 líneas) que indique cómo se resolvió la herencia y si quedó algo pendiente.'),

    'A': dict(titulo='Caso A · Carga refrigerada', nota=NOTA, texto=f"""# Parcial práctico: carga refrigerada
{CABEZA}
La empresa incorpora el transporte de carga REFRIGERADA. Se necesita procesar ambos tipos de carga en una misma colección y obtener sus costos correctos.
## Reglas nuevas
El nuevo encabezado es `patente,zona,velocidadPromedio,cargaToneladas,estado,tipoCarga`. Conservar también el formato original de cinco columnas: todos sus vehículos llevan carga GENERAL. Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.
Para filas EN_RUTA o DEMORADO del nuevo formato, el sexto campo admite exactamente GENERAL o REFRIGERADA, después de quitar espacios externos. Un valor vacío o desconocido hace inválida la fila.
- GENERAL conserva todas las reglas anteriores y su costo.
- REFRIGERADA respeta las validaciones anteriores, admite como máximo 30 toneladas inclusive y cuesta 300 USD adicionales sobre el costo de una carga general con los mismos datos. El recargo se aplica una sola vez por vehículo.
- Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar velocidad, carga ni tipo de carga. Las filas inválidas se registran y la carga continúa.
Ejemplos: un vehículo GENERAL con índice 50 cuesta 1000; uno REFRIGERADA con índice 50 cuesta 1300; uno REFRIGERADA con 31 toneladas es inválido.
## Resultado requerido
1. Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.
2. Hacer que `getCostoDesgasteOperativo()`, el costo total, los filtros por costo y los totales por zona reflejen la nueva regla.
3. Incorporar en el colector un conteo por tipo de carga. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío o conteos cero.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, cantidades GENERAL/REFRIGERADA, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes y los nuevos. Puede agregar tests propios.
{PIE}"""),

    'B': dict(titulo='Caso B · Kilómetros con punto y coma', nota=NOTA, texto=f"""# Parcial práctico: kilómetros recorridos
{CABEZA}
Logística empieza a registrar los kilómetros que recorrió cada vehículo, y el archivo nuevo viene separado por punto y coma.
## Reglas nuevas
El nuevo encabezado es `patente;zona;velocidadPromedio;cargaToneladas;estado;kilometros`. Conservar también el formato original de cinco columnas separadas por comas: todos sus vehículos tienen 0 kilómetros. El encabezado define el separador y el ancho de cada fila; una fila que no respeta su encabezado es inválida.
El sexto campo es un entero entre 0 y 5000, inclusive, después de quitar espacios externos. Un valor vacío, no numérico o fuera de ese rango hace inválida la fila.
El costo por desgaste operativo de todos los vehículos suma 1 USD por cada 10 kilómetros recorridos, con división entera: `2000 × índice / 100 + kilometros / 10`.
Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar los demás campos. Las filas inválidas se registran y la carga continúa.
Ejemplos: con índice 50 y 0 kilómetros, el costo es 1000; con índice 50 y 1234 kilómetros, 1123; 5001 kilómetros hace inválida la fila.
## Resultado requerido
1. Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.
2. Hacer que `getCostoDesgasteOperativo()`, el costo total, los filtros por costo y los totales por zona reflejen la nueva regla.
3. Incorporar en el colector el total de kilómetros por zona y el vehículo con más kilómetros recorridos. Puede elegir el nombre y representación de esas operaciones; para una colección vacía debe dar un resultado vacío.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, kilómetros por zona, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes y los nuevos. Puede agregar tests propios.
{PIE}"""),

    'C': dict(titulo='Caso C · Mantenimiento y demoras', nota=NOTA, texto=f"""# Parcial práctico: mantenimiento y demoras
{CABEZA}
El taller empieza a informar los vehículos que están en mantenimiento, y la empresa decide que el desgaste de los vehículos demorados cueste más.
## Reglas nuevas
El archivo conserva el encabezado y las cinco columnas del preparcial.
Se incorpora el estado MANTENIMIENTO: indica que el vehículo está en el taller. Se descarta después de verificar el ancho de la fila, sin validar los demás campos, igual que EN_DEPOSITO. El estado se compara después de quitar espacios externos y distingue mayúsculas.
- EN_RUTA conserva el comportamiento del preparcial.
- Un vehículo DEMORADO respeta las validaciones anteriores y su costo por desgaste operativo es un 15 % más alto que el normal, en enteros: `costo × 115 / 100`.
Ejemplos: un vehículo EN_RUTA con índice 40 cuesta 800; uno DEMORADO con índice 40 cuesta 920.
## Resultado requerido
1. Mantener la lectura del CSV con un solo proceso de carga y sumar MANTENIMIENTO a las filas descartadas.
2. Hacer que el costo, el total, los filtros y los totales por zona reflejen el recargo de los DEMORADO.
3. Incorporar en el colector la cantidad de vehículos por estado, el costo total de los vehículos DEMORADO reutilizando el filtro existente y las patentes con más de un viaje.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidades por estado, el costo de los DEMORADO, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes y los nuevos. Puede agregar tests propios.
{PIE}"""),

    'D': dict(titulo='Caso D · Facturación por flete (como el Parcial 3K1)', nota='Hipotético: es el enunciado del Parcial 3K1 (Cloud Center, «ingreso promedio por servidor») con las mismas frases, llevado a Flota. En el parcial no te dicen el nombre del método ni de la subclase: los elegís vos.', texto=f"""# Parcial práctico: facturación por flete
{CABEZA}
Administración incorpora para cada vehículo la facturación por flete que genera. Se necesita procesar el nuevo dato utilizando la misma colección y obtener sus costos y totales correctos.
## Reglas nuevas
El nuevo encabezado es `patente,zona,velocidadPromedio,cargaToneladas,estado,facturacion`. Conservar también el formato original de cinco columnas: todos los vehículos en este punto tienen una facturación de 2000.
Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.
Para filas con el estado EN_RUTA o DEMORADO del nuevo formato, el sexto campo admite valores mayores iguales a 2000 pero menores a 3800, después de quitar los espacios externos. Un valor por fuera de ese rango hace inválida la fila.
Debe conservar toda validación que esté previamente cargada en el preenunciado entregado. Usted debe modificar para que la facturación sea considerada al realizar el cálculo del costo por desgaste operativo, para que tome el valor ingresado, sin alterar la estructura de objetos del preparcial.
Ejemplos: un vehículo con un índice de desgaste de 65 y una facturación de 3000 USD tiene un costo por desgaste operativo de 1950 USD.
## Resultado requerido
1. Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.
2. Hacer que `getCostoDesgasteOperativo()`, el costo total, los filtros realizados y los totales por zona reflejen la nueva regla.
3. Incorporar en el colector un conteo por estado, que indique la cantidad de vehículos que se encuentran en cada estado procesado. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío o conteos cero.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, cantidades EN_RUTA/DEMORADO, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes y los nuevos. Puede agregar tests propios.
{PIE}"""),

    'E': dict(titulo='Caso E · Seguro de carga (como el Simulacro 4)', nota=NOTA, texto=f"""# Parcial práctico: seguro de carga
{CABEZA}
La empresa incorpora el seguro de la carga (cubre la mercadería ante robo o rotura durante el viaje). Se necesita procesar vehículos con y sin cobertura en una misma colección y obtener sus costos correctos.
## Reglas nuevas
El nuevo encabezado es `patente,zona,velocidadPromedio,cargaToneladas,estado,diasCobertura`. Conservar también el formato original de cinco columnas: todos esos vehículos son sin seguro. Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.
Para filas EN_RUTA o DEMORADO del nuevo formato, el sexto campo es un entero (tras quitar espacios externos):
- 0 conserva todas las reglas anteriores y su costo. Es un vehículo sin seguro.
- 30, 90 o 180 son plazos de cobertura. El vehículo queda asegurado: respeta las validaciones anteriores y suma una prima de 200 USD por cada 30 días sobre el costo de un vehículo sin seguro. La prima se aplica una sola vez por vehículo.
- Un valor vacío, no numérico o un plazo distinto de 0/30/90/180 hace inválida la fila.
Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar velocidad, carga ni días de cobertura.
## Resultado requerido
1. Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.
2. Hacer que `getCostoDesgasteOperativo()`, el costo total, los filtros por costo y los totales por zona reflejen la nueva regla.
3. Incorporar en el colector un conteo por modalidad. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío o conteos cero.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, cantidades SIN_SEGURO/ASEGURADO, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes y los nuevos. Puede agregar tests propios.
{PIE}"""),

    'F': dict(titulo='Caso F · Peajes (como el Simulacro 3)', nota=NOTA, texto=f"""# Parcial práctico: peajes
{CABEZA}
La empresa empieza a registrar los peajes que paga cada vehículo en el tramo.
## Reglas nuevas
El nuevo encabezado es `patente,zona,velocidadPromedio,cargaToneladas,estado,peajes`. Conservar también el formato original de cinco columnas: todos sus vehículos tienen 0 peajes. Cada fila debe tener el ancho indicado por su encabezado.
Para vehículos con peajes (indicado por la presencia de un valor en la 6ta columna), la cantidad de peajes debe ser un entero entre 1 y 10. De lo contrario, la fila es inválida. Un sexto campo vacío equivale a 0 peajes.
El costo por desgaste operativo de todos los vehículos suma 50 USD por cada peaje: `2000 × índice / 100 + 50 × peajes`.
Ejemplos: con índice 40 y 3 peajes, el costo es 950; con el sexto campo vacío, 800; con 11 peajes, la fila es inválida.
## Resultado requerido
1. Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.
2. Hacer que `getCostoDesgasteOperativo()`, el costo total, los filtros por costo y los totales por zona reflejen la nueva regla.
3. Incorporar en el colector el total de peajes por zona. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, peajes por zona, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes y los nuevos. Puede agregar tests propios.
{PIE}"""),

    'G': dict(titulo='Caso G · Vehículos en el taller', nota=NOTA, texto=f"""# Parcial práctico: vehículos en el taller
{CABEZA}
El taller empieza a informar los vehículos que están en reparación, y la empresa corrige una regla del contrato del archivo.
## Reglas nuevas
El archivo conserva el encabezado y las cinco columnas del preparcial.
Se incorpora el estado EN_TALLER: es un estado válido y debe incorporarse a la colección porque forma parte de la facturación. EN_RUTA y DEMORADO conservan el comportamiento del preparcial; EN_DEPOSITO se sigue descartando sin validar.
La carga en toneladas ya no admite valores negativos: debe ser un entero entre 0 y 45, inclusive. Una carga negativa hace inválida la fila.
Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar los demás campos. Las filas inválidas se registran y la carga continúa.
## Resultado requerido
1. Mantener la lectura del CSV con un solo proceso de carga.
2. Reflejar las nuevas reglas en la conversión de cada fila: los estados válidos y el rango de la carga.
3. Incorporar en el colector un conteo por estado, que indique la cantidad de vehículos en cada estado procesado, incluido EN_TALLER. Para una colección vacía debe dar un resultado vacío o conteos cero.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidades EN_RUTA/DEMORADO/EN_TALLER, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes y los nuevos. Puede agregar tests propios.
{PIE}"""),

    'P': dict(titulo='Preenunciado y operaciones nuevas', nota='Arriba, las reglas del preenunciado de Flota Logística (el texto de la cátedra). Abajo, un pedido hipotético escrito con las frases de los parciales: no te dan el nombre del método, lo elegís vos.', texto="""# Recuperatorio 1: Flota Logística
El departamento de operaciones de una empresa de transporte recibe un CSV con información referida a la telemetría de sus camiones en ruta. El programa carga los datos de los vehículos y calcula el costo asociado al desgaste operativo.
## Contrato del archivo
UTF-8, encabezado exacto `patente,zona,velocidadPromedio,cargaToneladas,estado`. Cada registro ocupa una línea con cinco campos separados por coma. Se quitan espacios externos de cada campo.
Cada fila tiene una patente y zona no vacíos, velocidad promedio en km/h y cantidad de carga en toneladas como valores enteros, y el estado en el que se encuentra el vehículo. No se exige unicidad de patentes; cada fila válida cuenta como un viaje independiente. Las zonas son textos sensibles a mayúsculas.
La velocidad promedio debe ser un valor mayor a 0 y menor a 130, y la carga no puede ser un valor mayor a 45 toneladas. El índice de desgaste que se debe calcular es un valor entre 1 y 90. Estos cálculos y validaciones quedan cerca del objeto, en `VehiculoRuta.desdeCampos` y su constructor.
El costo por desgaste operativo se calcula asumiendo que cada flete genera en promedio 2000 USD de facturación. No se usan números decimales ni redondeos monetarios, será un valor entero.
- Índice de desgaste: `indiceDesgaste = (velocidadPromedio × 0.6) + (cargaToneladas × 0.4)`
- Costo por desgaste operativo: `2000 × indiceDesgaste / 100`
## Flujo y errores
El parser verifica primero la cantidad de columnas. Con ancho correcto, EN_DEPOSITO se descarta sin validar los restantes datos. EN_RUTA y DEMORADO se intentan convertir; cualquier otro estado es inválido. Una línea vacía es inválida. No se interrumpe la carga por errores de una fila: se registra el número físico de línea y el motivo.
## Pedido hipotético · Resultado requerido
1. Incorporar en el colector una operación que devuelva el vehículo con mayor costo por desgaste operativo. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío.
2. No se exige unicidad de patentes: incorporar en el colector la cantidad de viajes de cada patente y las patentes que registran más de un viaje.
3. Incorporar en el colector la velocidad promedio de los vehículos de cada zona; para una colección vacía debe dar un resultado vacío.
4. Incorporar en el colector el costo total de los vehículos DEMORADO, reutilizando la operación de suma con filtro existente, y la cantidad de vehículos cuyo índice de desgaste está entre dos valores, inclusive.
5. Hacer que el main muestre la cantidad de vehículos por estado y el vehículo de mayor costo. Seguir delegando cálculos: el main no recorre la colección ni hace cuentas."""),
}

_A_ENC = 'El nuevo encabezado es `patente,zona,velocidadPromedio,cargaToneladas,estado,tipoCarga`.'
_A_VIEJO = 'Conservar también el formato original de cinco columnas: todos sus vehículos llevan carga GENERAL.'
_ANCHO = 'Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.'
_INTEGRAR = 'Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.'
_A_SEXTO = 'Para filas EN_RUTA o DEMORADO del nuevo formato, el sexto campo admite exactamente GENERAL o REFRIGERADA, después de quitar espacios externos. Un valor vacío o desconocido hace inválida la fila.'
_A_REF = 'REFRIGERADA respeta las validaciones anteriores, admite como máximo 30 toneladas inclusive y cuesta 300 USD adicionales sobre el costo de una carga general con los mismos datos. El recargo se aplica una sola vez por vehículo.'
_A_GEN = 'GENERAL conserva todas las reglas anteriores y su costo.'
_A_PREC = 'Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar velocidad, carga ni tipo de carga.'
_A_CONTEO = 'Incorporar en el colector un conteo por tipo de carga. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío o conteos cero.'
_A_MAIN = 'Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, cantidades GENERAL/REFRIGERADA, total y totales por zona. Seguir delegando cálculos.'

_B_ENC = 'El nuevo encabezado es `patente;zona;velocidadPromedio;cargaToneladas;estado;kilometros`.'
_B_VIEJO = 'Conservar también el formato original de cinco columnas separadas por comas: todos sus vehículos tienen 0 kilómetros.'
_B_SEP = 'El encabezado define el separador y el ancho de cada fila; una fila que no respeta su encabezado es inválida.'
_B_SEXTO = 'El sexto campo es un entero entre 0 y 5000, inclusive, después de quitar espacios externos. Un valor vacío, no numérico o fuera de ese rango hace inválida la fila.'
_B_COSTO = 'El costo por desgaste operativo de todos los vehículos suma 1 USD por cada 10 kilómetros recorridos, con división entera: `2000 × índice / 100 + kilometros / 10`.'
_B_PREC = 'Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar los demás campos.'
_B_KM = 'Incorporar en el colector el total de kilómetros por zona y el vehículo con más kilómetros recorridos. Puede elegir el nombre y representación de esas operaciones; para una colección vacía debe dar un resultado vacío.'
_B_MAIN = 'Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, kilómetros por zona, total y totales por zona. Seguir delegando cálculos.'

_C_CINCO = 'El archivo conserva el encabezado y las cinco columnas del preparcial.'
_C_MANT = 'Se incorpora el estado MANTENIMIENTO: indica que el vehículo está en el taller. Se descarta después de verificar el ancho de la fila, sin validar los demás campos, igual que EN_DEPOSITO. El estado se compara después de quitar espacios externos y distingue mayúsculas.'
_C_RUTA = 'EN_RUTA conserva el comportamiento del preparcial.'
_C_DEM = 'Un vehículo DEMORADO respeta las validaciones anteriores y su costo por desgaste operativo es un 15 % más alto que el normal, en enteros: `costo × 115 / 100`.'
_C_LECTURA = 'Mantener la lectura del CSV con un solo proceso de carga y sumar MANTENIMIENTO a las filas descartadas.'
_C_COSTO = 'Hacer que el costo, el total, los filtros y los totales por zona reflejen el recargo de los DEMORADO.'
_C_COL = 'Incorporar en el colector la cantidad de vehículos por estado, el costo total de los vehículos DEMORADO reutilizando el filtro existente y las patentes con más de un viaje.'
_C_MAIN = 'Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidades por estado, el costo de los DEMORADO, total y totales por zona. Seguir delegando cálculos.'

_D_ENC = 'El nuevo encabezado es `patente,zona,velocidadPromedio,cargaToneladas,estado,facturacion`.'
_D_VIEJO = 'Conservar también el formato original de cinco columnas: todos los vehículos en este punto tienen una facturación de 2000.'
_D_SEXTO = 'Para filas con el estado EN_RUTA o DEMORADO del nuevo formato, el sexto campo admite valores mayores iguales a 2000 pero menores a 3800, después de quitar los espacios externos. Un valor por fuera de ese rango hace inválida la fila.'
_D_COSTO = 'Usted debe modificar para que la facturación sea considerada al realizar el cálculo del costo por desgaste operativo, para que tome el valor ingresado, sin alterar la estructura de objetos del preparcial.'
_D_REGLA = 'Hacer que `getCostoDesgasteOperativo()`, el costo total, los filtros realizados y los totales por zona reflejen la nueva regla.'
_D_CONTEO = 'Incorporar en el colector un conteo por estado, que indique la cantidad de vehículos que se encuentran en cada estado procesado. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío o conteos cero.'
_D_MAIN = 'Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, cantidades EN_RUTA/DEMORADO, total y totales por zona. Seguir delegando cálculos.'

MARCAS = {
    # El recuperatorio de verdad (tramo sin pavimentar)
    'r1.5': ('R', ['Cada archivo contiene un único encabezado. Bajo el encabezado original, cada fila debe tener cinco campos y conserva el cálculo anterior.',
                   'Bajo el encabezado nuevo, se admiten filas de cinco campos (formato original) y de seis campos (formato nuevo); detectar el formato de cada fila por su ancho.',
                   'No aceptar anchos distintos de cinco o seis ni encabezados repetidos en medio del archivo. Reutilizar el flujo de lectura y clasificación; no duplicar el parser.',
                   'Se verifica primero el ancho de la fila. Si el ancho es correcto, EN_DEPOSITO se descarta sin validar los demás campos, incluido porcentajeRutaSinPAvimentar.']),
    'r2.13': ('R', ['`porcentajeRutaSinPAvimentar` es un porcentaje entero del recorrido realizado por caminos sin pavimentar y admite valores entre 0 y 100, inclusive. Un valor fuera de ese rango invalida la fila.',
                    'Debe incluir un método de fábrica `desdeCampos(String[] campos)` que inspeccione el ancho de la fila y cree un `VehiculoRuta` para cinco campos o un `VehiculoRutaConTramoSinPavimentar` para seis campos.',
                    '`VehiculoRutaConTramoSinPavimentar` debe extender directamente a `VehiculoRuta`, agregar y exponer el porcentaje de recorrido sin pavimentar, y validar su rango.']),
    'r3.5': ('R', ['El formato original conserva el cálculo anterior. Para el formato nuevo, `VehiculoRutaConTramoSinPavimentar` calcula el índice de desgaste con la fórmula indicada abajo.',
                   'El constructor de `VehiculoRuta` recibe el `indiceDesgaste` calculado; no debe recalcularlo.',
                   'Para las filas del formato nuevo se usa: `indiceDesgaste = (velocidadPromedio × 0.55) + (cargaToneladas × 0.30) + (porcentajeRutaSinPAvimentar × 0.15)`',
                   'Por ejemplo, con velocidad 76, carga 11 y un 30 % de recorrido sin pavimentar, el índice nuevo es 49 (49.6 truncado); con el formato original y esos valores de velocidad y carga, es 50.']),
    'r4.8': ('R', ['Hacer que Flota opere sobre VehiculoRuta e incluya ambos tipos en filtros, sumas y agrupamientos por zona.',
                   '20 índices de desgaste menores a 55. `Flota.panorama()` debe incluir esa última cantidad en su salida.']),
    'r5.4': ('R', ['Actualizar App para que, sin argumentos, lea `datos/datos-parcial.csv`; si se pasa una ruta como argumento, debe usarla.',
                   'Mostrar el resumen del parseo y el panorama, que incluye costos por zona y la cantidad de vehículos con índice de desgaste mayor o igual a un minimo.']),
    # Parte 0: dónde va cada cambio (todo lo que pide el caso)
    'r0.1': ('A', [_A_ENC, _A_VIEJO, _ANCHO, _A_SEXTO, _A_REF, _A_CONTEO, _A_MAIN]),
    'r0.2': ('B', [_B_ENC, _B_VIEJO, _B_SEP, _B_SEXTO, _B_COSTO, _B_KM, _B_MAIN]),
    'r0.3': ('C', [_C_MANT, _C_DEM, _C_COL, _C_MAIN]),
    'r0.4': ('D', [_D_ENC, _D_VIEJO, _ANCHO, _D_SEXTO, _D_COSTO, _D_CONTEO, _D_MAIN]),
    # Parte 1: el parser
    'r1.1': ('A', [_A_ENC, _A_VIEJO, _ANCHO, _INTEGRAR]),
    'r1.3': ('B', [_B_ENC, _B_VIEJO, _B_SEP, _INTEGRAR]),
    'r1.2': ('C', [_C_MANT, _C_LECTURA]),
    'r1.4': ('D', [_D_ENC, _D_VIEJO, _ANCHO, _INTEGRAR]),
    # Parte 2: el dominio y clasificar filas
    'r2.2': ('P', ['La velocidad promedio debe ser un valor mayor a 0 y menor a 130, y la carga no puede ser un valor mayor a 45 toneladas. El índice de desgaste que se debe calcular es un valor entre 1 y 90.',
                   'Índice de desgaste: `indiceDesgaste = (velocidadPromedio × 0.6) + (cargaToneladas × 0.4)`',
                   'El parser verifica primero la cantidad de columnas. Con ancho correcto, EN_DEPOSITO se descarta sin validar los restantes datos. EN_RUTA y DEMORADO se intentan convertir; cualquier otro estado es inválido. Una línea vacía es inválida.']),
    'r2.3': ('A', [_A_SEXTO, _A_REF, _A_PREC]),
    'r2.1': ('B', [_B_VIEJO, _B_SEXTO, _B_COSTO]),
    'r2.4': ('B', [_B_ENC, _B_SEXTO, _B_COSTO, _B_PREC]),
    'r2.5': ('C', [_C_CINCO, _C_MANT, _C_DEM]),
    'r2.6': ('D', [_ANCHO, _D_SEXTO, _D_COSTO]),
    'r2.7': ('A', [_A_ENC, _A_VIEJO, _A_SEXTO]),
    'r2.8': ('D', [_D_VIEJO, _D_SEXTO, _D_COSTO]),
    'r2.9': ('G', ['Se incorpora el estado EN_TALLER: es un estado válido y debe incorporarse a la colección porque forma parte de la facturación.',
                   'EN_DEPOSITO se sigue descartando sin validar.']),
    'r2.10': ('G', ['La carga en toneladas ya no admite valores negativos: debe ser un entero entre 0 y 45, inclusive. Una carga negativa hace inválida la fila.',
                    'Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar los demás campos.']),
    'r2.11': ('E', ['El nuevo encabezado es `patente,zona,velocidadPromedio,cargaToneladas,estado,diasCobertura`.',
                    'Conservar también el formato original de cinco columnas: todos esos vehículos son sin seguro.',
                    'Para filas EN_RUTA o DEMORADO del nuevo formato, el sexto campo es un entero (tras quitar espacios externos):',
                    'Un valor vacío, no numérico o un plazo distinto de 0/30/90/180 hace inválida la fila.']),
    'r2.12': ('F', ['Conservar también el formato original de cinco columnas: todos sus vehículos tienen 0 peajes.',
                    'Para vehículos con peajes (indicado por la presencia de un valor en la 6ta columna), la cantidad de peajes debe ser un entero entre 1 y 10. De lo contrario, la fila es inválida. Un sexto campo vacío equivale a 0 peajes.',
                    'El costo por desgaste operativo de todos los vehículos suma 50 USD por cada peaje: `2000 × índice / 100 + 50 × peajes`.']),
    # Parte 3: polimorfismo
    'r3.1': ('A', [_A_VIEJO, 'Un valor vacío o desconocido hace inválida la fila.', _A_GEN, _A_REF]),
    'r3.2': ('C', [_C_RUTA, _C_DEM, _C_COSTO]),
    'r3.4': ('D', [_D_VIEJO, _D_SEXTO, _D_COSTO, _D_REGLA]),
    # Parte 4: el colector
    'r4.3': ('P', ['Incorporar en el colector una operación que devuelva el vehículo con mayor costo por desgaste operativo. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío.']),
    'r4.4': ('P', ['No se exige unicidad de patentes; cada fila válida cuenta como un viaje independiente.',
                   'No se exige unicidad de patentes: incorporar en el colector la cantidad de viajes de cada patente y las patentes que registran más de un viaje.']),
    'r4.5': ('P', ['Incorporar en el colector la velocidad promedio de los vehículos de cada zona; para una colección vacía debe dar un resultado vacío.']),
    'r4.7': ('P', ['Incorporar en el colector el costo total de los vehículos DEMORADO, reutilizando la operación de suma con filtro existente, y la cantidad de vehículos cuyo índice de desgaste está entre dos valores, inclusive.']),
    'r4.2': ('A', [_A_CONTEO]),
    'r4.6': ('B', [_B_KM]),
    'r4.1': ('D', [_D_CONTEO]),
    # Parte 5: el main
    'r5.2': ('P', ['Hacer que el main muestre la cantidad de vehículos por estado y el vehículo de mayor costo. Seguir delegando cálculos: el main no recorre la colección ni hace cuentas.']),
    'r5.1': ('A', [_A_MAIN]),
    'r5.3': ('D', [_D_MAIN]),
}


def aplicar(datos):
    """Suma los enunciados al JSON y a cada ejercicio su enunciado y lo que hay que pintar (controla que esté tal cual)."""
    datos['enunciados'] = DOCS
    ejercicios = {e['id']: e for p in datos['partes'] for e in p['ejercicios']}
    for id, (doc, marcas) in MARCAS.items():
        if id not in ejercicios:   # un ejercicio que no se publica
            continue
        texto = DOCS[doc]['texto']
        for m in marcas:
            assert m in texto, (id, m[:60])
            assert m.count('`') % 2 == 0, (id, 'corta un `código`')
        ejercicios[id]['enunciadoDe'] = doc
        ejercicios[id]['marcas'] = marcas
    return datos
