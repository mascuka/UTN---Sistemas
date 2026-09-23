# Página de la materia

## Estructura
- `index.html` → la página. El contenido se edita en el bloque `CURSO` al principio del `<script>`.
- `material/p1`, `material/p2`, `material/p3` → cada parcial, con subcarpetas `teorico/` y `practico/`.
- `material/actividades/` → trabajos prácticos y entregas.

## Agregar un PDF
1. Subilo a la carpeta que corresponde (ej: `material/p2/teorico/apunte.pdf`).
2. En `index.html`, dentro de `CURSO`, agregá una línea en `material`:
   `{ nombre: "Apunte", tipo: "PDF", url: "material/p2/teorico/apunte.pdf" }`

## Agregar un video
En `videos`, agregá:
`{ titulo: "Clase 4", url: "https://www.youtube.com/watch?v=XXXXXXXXXXX" }`

## Límites de GitHub
Hasta 100 MB por archivo. Conviene que el repositorio no pase de ~1 GB.
