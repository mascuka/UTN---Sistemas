# Página de Ingeniería en Sistemas de Información

## Estructura
- `index.html` → la página. Todo el contenido se edita al principio del `<script>`:
  - `CARRERA` → el plan de estudios (página de inicio): materias por nivel, correlativas y electivas.
  - `MATERIAS` → el contenido de cada materia (parciales, material, videos, actividades), usando como clave el número de la materia (ej: `26` = Redes de Datos).
- `material/<materia>/<parcial>/<teorico|practico>/` → los PDF de cada materia (ej: `material/redes-de-datos/p2/teorico/apunte.pdf`).
- `material/<materia>/actividades/` → trabajos prácticos y entregas.

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

## Temas del parcial (introducción)
Cada parcial puede tener un campo `temas` (ver el 2º Parcial de Redes de Datos):
`temas: { titulo: "...", unidades: [ { titulo: "Unidad ...", contenidos: ["...", "..."] } ] }`
Se muestra abajo de las tarjetas de Teórico/Práctico. Si el parcial no lo tiene, no aparece nada.

## Secciones de un parcial a medida
Si un parcial no necesita las tres tarjetas, se puede limitar con `secciones` (ej.: Backend, 1º Parcial y TPI):
`secciones: ["teorico", "practico"]`

## Comisiones
Cada profesor es una fila con `comision`, `profesor`, `rol`, `asistencia` y `comentario`. El examen (`examen`) y la recomendación (`recomendada: true/false` y `motivo`) son de la comisión: se ponen una sola vez, en el primer profesor de esa comisión. `horario` también va en el primero.

## Parcial o TPI en una sola página
Con `secciones: []` el parcial no tiene tarjetas de Teórico/Práctico: su página muestra directamente las pestañas Material y Videos, con su propio `material` y `videos` (ver los TPI de Green Software, `202`).

## Condiciones de aprobación
Cada materia puede tener `condiciones` (ver Backend de Aplicaciones, `201`). Se muestra en la página de la materia, antes de las comisiones:
`condiciones: { directa: 6, regular: 4, aclaracion: "...", requisitos: [ { titulo: "Parcial", detalle: "6 o más" } ] }`
Si `regular` es `null`, aparece "No tiene" (electivas, que solo se aprueban de forma directa). La asistencia no va acá: se indica en la columna de cada profesor en las comisiones.

## Límites de GitHub
Hasta 100 MB por archivo. Conviene que el repositorio no pase de ~1 GB.
