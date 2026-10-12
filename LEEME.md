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
- `#/` → inicio: el resumen del avance
- `#/nivel/3` → las materias de 3º Nivel (`#/nivel/0` es el Ingreso)
- `#/m26` → Redes de Datos
- `#/m26/p2` → 2º Parcial de Redes de Datos
- `#/m26/p2/teorico/videos` → videos del teórico

## Agregar una materia con contenido
Dentro de `MATERIAS`, copiá el bloque de la `26` y cambiale el número por el de la materia (el número está en `CARRERA.materias`). En la lista de su año, su fila muestra la etiqueta "Material" (y si es electiva, pasa a tener link).

## Barra de arriba
No hay columna al costado: la página usa todo el ancho. Arriba queda fija una barra con el logo y el avance (los dos llevan al inicio) y los años (Ingreso, 1º a 5º Nivel), que ocupan casi todo el ancho; cada año lleva a sus materias y queda marcado mientras estás en él o en una de sus materias. Adentro de una materia aparece una segunda fila, igual de ancha, con sus bloques (Inicio, parciales, TP, actividades). En el celular, adentro de una materia, esa fila reemplaza a los años (para volver está "Inicio" o "Atrás" en la barra de abajo).

## Inicio: resumen del avance
El inicio (`viewResumen`) no lista las materias: muestra el avance de la carrera (anillo con el %, materias, horas y créditos de electivas) y una tarjeta por año con sus materias como pastillas (en verde las aprobadas). Tocar la tarjeta lleva al año; tocar una pastilla, a la materia. Abajo van las notas del plan.
En la tarjeta de horas se marca la meta de `CARRERA.metaHoras` (32 hs, para pedir equivalencias): una rayita en la barra y un aviso con cuántas horas faltan, o en verde si ya se pasó. Para cambiar el número o el texto, se edita esa línea.

## Cada año
`#/nivel/N` (`viewNivel`) muestra solo las materias de ese año: las obligatorias y debajo las electivas, con los créditos mínimos que pide (`CREDITOS_NIVEL`). Cada materia es una fila redondeada, separada de las demás; las que tienen material cargado llevan la etiqueta "Material". Al final, botones para ir al año anterior o al siguiente. Al volver de una materia, la lista queda donde estaba, y el "Atrás" de una materia lleva a su año.
Cada materia lleva su abreviatura en una pastilla beige (`.abr`), igual que las correlativas; las correlativas ya aprobadas se ven en verde. Los colores del beige son `--beige` y `--beige-t` (con su versión para el modo oscuro).

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

El reproductor usa la API de YouTube (`youtube.com/iframe_api`): cuando termina un video arranca solo el siguiente de la lista, y la velocidad que se elige (por ejemplo 1.5) se mantiene en los videos siguientes y queda guardada en el navegador (`isi-yt-vel`). Tocar un video de la lista lo arranca. Si la API no carga, se ve el video común de YouTube, sin esas dos cosas.

En la compu, el botón "Modo cine" (o la tecla `t`) agranda el video a todo el ancho, sin pantalla completa, y pasa la lista abajo en una fila horizontal (con flechas y la rueda del mouse). Es solo CSS, así que el video no se corta; la elección queda guardada (`isi-yt-cine`). En el celular la lista ya va abajo y el botón no aparece.

Los archivos con `tipo: "ZIP"` o `tipo: "INO"` se descargan (botón "Descargar ↓") en vez de abrirse en otra pestaña.

## Niveles del material (esencial, para profundizar, extra)
Cada grupo de material puede llevar `nivel: "esencial"`, `"profundizar"` o `"extra"` (también un archivo suelto, para que vaya a otro nivel que su grupo). Si una lista usa niveles, se ordena por nivel con su color y lo extra queda plegado ("Ver N más"). Lo que no tiene nivel cuenta como esencial. Si ninguna parte de la lista tiene nivel, se ve como siempre.
`{ nivel: "profundizar", grupo: "Material del profe", archivos: [...] }`

## Tapas de los PDF y visor
Cada PDF del repo muestra su primera página en la lista y se abre en el visor de la página, en la compu y en el celular. El visor dibuja el PDF con PDF.js (se carga de cdnjs la primera vez que se abre un PDF), así no depende del navegador: antes, Chrome de Android los descargaba y los navegadores de WhatsApp o Instagram los dejaban en blanco. Tiene las páginas al costado (en pantallas anchas), zoom, buscar una palabra, descargar, la cruz para cerrar arriba a la derecha, y pasar al archivo anterior o siguiente de la misma página. En el celular ocupa toda la pantalla y el botón "atrás" lo cierra. Si PDF.js no carga, ofrece abrir o descargar el PDF. Ctrl/Cmd + clic sigue abriendo el PDF en otra pestaña.
Las tapas están en `miniaturas/` (misma ruta que en `material/`, en .jpg). Cuando subas PDFs nuevos, corré desde la raíz del repo:
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

## Bloques por evaluación
Los bloques de `parciales` son las evaluaciones de la materia, no las unidades de la cátedra. Por ejemplo, Desarrollo de Aplicaciones con Objetos (`206`) tiene dos:
- "1º Parcial", con Teórico, Práctico y "Parcial y simulacros".
- "TPI", con Teórico y Práctico.

Los temas de cada unidad van en el bloque de la evaluación donde se toman. Toda sección que se cargue lleva `material` y `videos`, aunque alguno quede vacío (`videos: []`).

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
