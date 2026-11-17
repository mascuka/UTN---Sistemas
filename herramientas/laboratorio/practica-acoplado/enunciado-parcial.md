# Parcial práctico: viajes con acoplado

Tiempo orientativo: 45 minutos. Partir exactamente del proyecto preparcial. Se entregan este documento y datos-parcial.csv. Mantener los tests existentes.

El CSV del parcial es corto: contiene 26 filas de datos más encabezado; es un conjunto distinto del preparcial de 60 filas. El volumen no agrega reglas ni tareas de programación.

Parcial de práctica: es hipotético, armado con lo que más se repite en los parciales y simulacros de la cátedra (3K1, 3K2, Simulacro 4 y Recuperatorio 2) sobre el preenunciado de Flota Logística.

La empresa incorpora vehículos que viajan con acoplado. Se necesita procesar vehículos con y sin acoplado en una misma colección y obtener sus costos correctos.

## Reglas nuevas

El nuevo encabezado es `patente,zona,velocidadPromedio,cargaToneladas,estado,acoplado`. Conservar también el formato original de cinco columnas: todos esos vehículos viajan sin acoplado. Cada fila debe tener el ancho indicado por su encabezado; no aceptar filas de cinco campos bajo un encabezado de seis, ni a la inversa.

Para filas EN_RUTA o DEMORADO del nuevo formato, el sexto campo es un entero entre 0 y 20, inclusive, después de quitar espacios externos: el peso del acoplado. Un valor vacío, no numérico o fuera de ese rango hace inválida la fila.

- 0 conserva todas las reglas anteriores y su costo. Es un vehículo sin acoplado.
- Con un valor mayor a 0, el vehículo lleva acoplado: respeta las validaciones anteriores, su velocidad promedio no puede superar los 90 km/h y suma 40 USD por cada tonelada de acoplado sobre el costo de un vehículo sin acoplado con los mismos datos.
- Conservar la precedencia del preparcial: verificar ancho y después descartar EN_DEPOSITO sin validar velocidad, carga ni acoplado. Las filas inválidas se registran y la carga continúa.

Ejemplos: un vehículo con índice 50 sin acoplado cuesta 1000; con 5 toneladas de acoplado, 1200; con acoplado a 91 km/h es inválido (a 90 km/h vale); con 21 toneladas de acoplado la fila es inválida.

## Resultado requerido

1. Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga.
2. Hacer que `getCostoDesgasteOperativo()`, el costo total, los filtros por costo y los totales por zona reflejen la nueva regla.
3. Incorporar en el colector un conteo por modalidad. Puede elegir el nombre y representación de esa operación; para una colección vacía debe dar un resultado vacío o conteos cero.
4. Hacer que el main use por defecto el archivo del parcial y muestre resumen, cantidad de objetos, cantidades SIN_ACOPLADO/CON_ACOPLADO, total y totales por zona. Seguir delegando cálculos.
5. Conservar el comportamiento anterior y pasar los tests existentes. Agregar tests propios para el acoplado (límites 0 y 20, tope de 90 km/h, recargo, conteo y ambos encabezados).

Se evalúa comportamiento observable, encapsulamiento y distribución de responsabilidades. Puede usar herencia, composición u otra solución razonable. Puede usar Streams o ciclos; no se exige una jerarquía ni una técnica determinada. No se evalúa el nombre concreto de una subclase.

El CSV original debe seguir produciendo sus resultados de referencia: 60 filas leídas, 32 procesadas, 20 descartadas y 8 inválidas; costo total 31840, por zona SUR 8200, CENTRO 12440, NORTE 11200; 18 índices de desgaste menores a 55.

El archivo del parcial debe producir 26 filas leídas, 11 procesadas, 2 descartadas y 13 inválidas; costo total 12700, por zona NORTE 4480, SUR 2880 y CENTRO 5340; 7 índices de desgaste menores a 55.

## Preparación y entrega

Desde la raíz de su copia de 01-modelo-inicial, copiar datos-parcial.csv a datos/datos-parcial.csv y ajustar la ruta predeterminada del main.

    mvn test
    java -cp target/classes ar.edu.backend.App datos/datos-parcial.csv

Entregar un único ZIP del proyecto con pom.xml, src/ y datos/; excluir target/, .git/ y archivos del IDE. Incluir un texto breve DECISIONES.md (3–5 líneas) que indique la estrategia elegida y si quedó algo pendiente.

Distribución sugerida: 5 minutos de lectura, 25 de cambios, 10 de pruebas y 5 para revisar y empaquetar.
