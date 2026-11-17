# Parcial: Flota Logística con Pendiente del Tramo

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

- Formato original: `patente,zona,velocidadPromedio,cargaToneladas,estado`
- Formato del parcial: `patente,zona,velocidadPromedio,cargaToneladas,estado,pendientePromedio`

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

El CSV original debe seguir produciendo sus resultados de referencia: 60 filas leídas, 32 procesadas, 20 descartadas y 8 inválidas; costo total 31840, por zona SUR 8200, CENTRO 12440, NORTE 11200; 18 índices de desgaste menores a 55. Para el nuevo formato, verificar ambos límites de pendientePromedio y los ejemplos numéricos de esta consigna; no asumir que el índice o los agregados coinciden con los del archivo original.

El archivo de ejemplo combinado datos/datos-parcial.csv es corto: incluye 8 registros del archivo original (con sus casos testigo) y 14 líneas de prueba del nuevo formato, intercaladas bajo un único encabezado de seis columnas. Las filas originales de cinco campos conservan el cálculo anterior; las nuevas prueban ambos límites válidos de la pendiente, valores fuera de rango, un valor no numérico, índice fuera de rango, un índice que solo es válido con la fórmula nueva (trk-0112 contra trk-0005), descarte, estado desconocido, ancho incorrecto, línea vacía y un encabezado repetido.

El conjunto combinado debe producir 22 filas leídas, 9 procesadas, 2 descartadas y 11 inválidas; costo total 9340, por zona NORTE 3440, SUR 1360 y CENTRO 4540; 5 índices de desgaste menores a 55.

## Preparación y entrega

Usar el archivo combinado datos/datos-parcial.csv como entrada predeterminada. Incorporar o actualizar pruebas para cubrir los casos requeridos. Ejecutar:

    mvn test
    java -cp target/classes ar.edu.backend.App
    java -cp target/classes ar.edu.backend.App datos/datos.csv

Entregar el proyecto con pom.xml, src/ y datos/; excluir target/, .git/ y archivos del IDE. Incluir un texto breve DECISIONES.md (3–5 líneas) que indique cómo se resolvió la herencia y si quedó algo pendiente.
