# Página de Ingeniería en Sistemas de Información

## Estructura
- `index.html` → la página. Todo el contenido se edita al principio del `<script>`:
  - `CARRERA` → el plan de estudios (página de inicio): materias por nivel, correlativas y electivas.
  - `MATERIAS` → el contenido de cada materia (parciales, material, videos, actividades), usando como clave el número de la materia (ej: `26` = Redes de Datos).
- `material/<materia>/<parcial>/<teorico|practico>/` → los PDF de cada materia (ej: `material/redes-de-datos/p2/teorico/apunte.pdf`).
- `material/<materia>/actividades/` → trabajos prácticos y entregas.
- `miniaturas/` → la tapa de cada PDF (se genera con `herramientas/miniaturas.py`).
- `quiz/` → las preguntas de cada quiz (JSON) y sus imágenes.

## Links
Cada página tiene su propio link, por ejemplo:
- `#/m26` → Redes de Datos
- `#/m26/p2` → 2º Parcial de Redes de Datos
- `#/m26/p2/teorico/videos` → videos del teórico

## Agregar una materia con contenido
Dentro de `MATERIAS`, copiá el bloque de la `26` y cambiale el número por el de la materia (el número está en `CARRERA.materias`). En el plan de estudios aparece marcada como "Con material".

## Agregar un PDF
1. Subilo a la carpeta que corresponde (ej: `material/redes-de-datos/p2/teorico/apunte.pdf`).
2. En `index.html`, dentro de la materia en `MATERIAS`, agregá una línea en `material`:
   `{ nombre: "Apunte", tipo: "PDF", url: "material/redes-de-datos/p2/teorico/apunte.pdf" }`

## Secciones de cada parcial
Cada parcial tiene tres secciones: `teorico`, `practico` y `parciales` (parciales de años anteriores). Todas se muestran aunque estén vacías; para cargar algo, agregá la sección en el parcial con `{ material: [...], videos: [...] }`.

## Agregar un video
En `videos`, agregá:
`{ url: "https://www.youtube.com/watch?v=XXXXXXXXXXX" }`
Sin `titulo`, el nombre se trae de YouTube (el video tiene que estar publicado u oculto, no en borrador) y, si todos empiezan con "Clase N", se ordenan por número. Si ponés `titulo: "..."`, se usa ese.

Opcionales en cada video: `bloque: "..."` agrupa la lista con un título por bloque (ver Backend, 1º Parcial), `detalle: "..."` se muestra debajo del video, y si el link tiene `&t=440s` el video arranca en ese segundo.

Los archivos con `tipo: "ZIP"` o `tipo: "INO"` se descargan (botón "Descargar ↓") en vez de abrirse en otra pestaña.

## Niveles del material (esencial, para profundizar, extra)
Cada grupo de material puede llevar `nivel: "esencial"`, `"profundizar"` o `"extra"` (también un archivo suelto, para que vaya a otro nivel que su grupo). Si una lista usa niveles, se ordena por nivel con su color y lo extra queda plegado ("Ver N más"). Lo que no tiene nivel cuenta como esencial. Si ninguna parte de la lista tiene nivel, se ve como siempre.
`{ nivel: "profundizar", grupo: "Material del profe", archivos: [...] }`

## Tapas de los PDF y visor
Cada PDF del repo muestra su primera página en la lista y, en la compu, se abre en un visor dentro de la página (con anterior/siguiente). En el celular se abre como siempre. Las tapas están en `miniaturas/` (misma ruta que en `material/`, en .jpg). Cuando subas PDFs nuevos, corré desde la raíz del repo:
`python3 herramientas/miniaturas.py` (necesita `pip install pymupdf`). Crea las que faltan y borra las que ya no tienen PDF. Si un PDF no tiene tapa, se ve el cartel "PDF" como antes.

## Quiz
Con `quiz: "quiz/archivo.json"` en el parcial aparece "Practicá → Quiz" (ruta `#/m201/p1/quiz`). El JSON tiene `titulo`, `descripcion` y `secciones: [ { titulo, preguntas: [...] } ]`. Cada pregunta: `tipo` (`una`, `varias`, `vf`, `num` o `modelo`), `en` (enunciado, acepta HTML), `op: [["texto", true/false], ...]` para las de opciones, `num` o `modelo` (la respuesta, para las que se resuelven y después se mira), y opcionales `ex` (por qué), `mal` (aviso, por ejemplo una clave del campus equivocada), `fuente`, `code`, `img` y `practica: true` (no salió en un parcial). Se elige la cantidad (10, 20 o todas) y los temas: cada sección del JSON es un tema. Las preguntas salen al azar y "Otras 10" trae las que todavía no salieron. No se guarda nada de quien lo hace.

## Herramientas y explicaciones
Con `herramientas: ["csv", "streams"]` en el parcial aparecen en "Practicá y entendé" (ruta `#/m201/p1/h/csv`). Hay:
- `csv`: cómo se lee un CSV en Java. Las formas del apunte 11 (Scanner, BufferedReader, Files.lines, CSVReader, CSVReaderHeaderAware y CsvToBean) con un cuadro de qué hace cada una y, para cada forma, un paso a paso con dibujo y el código resaltado.
- `streams`: Streams y Collectors, con un stream recorrido paso a paso y cada operación sola (filter, map, sorted, limit, terminales y groupingBy).
- `rotaciones` (rotaciones y traslaciones, TPA), `robot2r` (robot 2R directa e inversa, TPA) y `subredes` (subredes y VLSM, Redes).
Están en `HERRAMIENTAS`, en el código de la página.

## Temas del parcial (introducción)
Cada parcial puede tener un campo `temas` (ver el 2º Parcial de Redes de Datos):
`temas: { titulo: "...", unidades: [ { titulo: "Unidad ...", contenidos: ["...", "..."] } ] }`
Se muestra abajo de las tarjetas de Teórico/Práctico. Si el parcial no lo tiene, no aparece nada.

## Secciones de un parcial a medida
Si un parcial no necesita las tres tarjetas, se puede limitar con `secciones`:
`secciones: ["teorico", "practico"]`

Además de `teorico`, `practico` y `parciales` hay dos secciones más: `parcial` (simulacros, parciales tomados y guía para prepararlo) y `tpi` (enunciado del TPI y sus guías). Su contenido va en el parcial con la misma clave, igual que las otras. Con `nombres` se le cambia el título a una sección de ese parcial (ver Backend, `201`: el 1º Parcial tiene Teórico y "1º Parcial", y el TPI tiene Teórico y "TPI"):
`secciones: ["teorico", "parcial"], nombres: { parcial: "1º Parcial" }`

## Comisiones
Cada profesor es una fila con `comision`, `profesor`, `rol` y `asistencia`. El comentario (`comentario`), el examen (`examen`) y la recomendación (`recomendada: true/false` y `motivo`) son de la comisión: se ponen una sola vez, en el primer profesor de esa comisión. `horario` también va en el primero.

## Parcial o TPI en una sola página
Con `secciones: []` el parcial no tiene tarjetas de Teórico/Práctico: su página muestra directamente las pestañas Material y Videos, con su propio `material` y `videos` (ver los TPI de Green Software, `202`). Si además tiene `temas`, se muestran debajo del material (ver Tecnologías para la Automatización, `29`).

## Condiciones de aprobación
Cada materia puede tener `condiciones` (ver Backend de Aplicaciones, `201`). Se muestra arriba de todo en la página de la materia:
`condiciones: { directa: 6, regular: 4, aclaracion: "...", requisitos: [ { titulo: "Parcial", corto: "Parcial ≥ 6", detalle: "6 o más" } ] }`
Se ve en una sola línea ("Para aprobar: Directa con 6 · Parcial ≥ 6…", con `corto`) y al tocarla se despliega el detalle. Si `regular` es `null`, aparece "Sin regularidad" (electivas, que solo se aprueban de forma directa). La asistencia no va acá: se indica en la columna de cada profesor en las comisiones.

## Descargar toda la materia (ZIP)
En la página de cada materia aparece el botón "Descargar todo (ZIP)" si tiene archivos propios (`material/...`). El ZIP se arma en el navegador, sin copias en el repo: una carpeta por parcial y sección (Teórico, Práctico…), y adentro una por grupo y parte, numeradas en el orden de la página. Los archivos se llaman como en la página ("01 - Nombre.pdf"). Los videos no van, y los links externos (Drive, webs) quedan en un `Enlaces.txt` dentro de su carpeta.

## Límites de GitHub
Hasta 100 MB por archivo. Conviene que el repositorio no pase de ~1 GB.
