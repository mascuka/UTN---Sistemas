"""Genera la miniatura (primera página) de cada PDF de material/ en miniaturas/.

material/redes-de-datos/p2/teorico/apunte.pdf -> miniaturas/redes-de-datos/p2/teorico/apunte.jpg
Solo crea las que faltan o las de PDFs más nuevos que su miniatura, y borra las que ya no tienen PDF.
Uso (desde la raíz del repo):  pip install pymupdf  y  python3 herramientas/miniaturas.py
"""
import os
import pymupdf

ANCHO = 150      # px: se muestra a ~40 px, así queda nítida en pantallas de alta densidad
CALIDAD = 70

hechas = borradas = 0
validas = set()
for raiz, _, archivos in os.walk("material"):
    for a in sorted(archivos):
        if not a.lower().endswith(".pdf"):
            continue
        pdf = os.path.join(raiz, a)
        jpg = os.path.join("miniaturas", os.path.relpath(pdf, "material"))[:-4] + ".jpg"
        validas.add(jpg)
        if os.path.exists(jpg) and os.path.getmtime(jpg) >= os.path.getmtime(pdf):
            continue
        with pymupdf.open(pdf) as d:
            pag = d[0]
            pix = pag.get_pixmap(matrix=pymupdf.Matrix(ANCHO / pag.rect.width, ANCHO / pag.rect.width))
        os.makedirs(os.path.dirname(jpg), exist_ok=True)
        pix.save(jpg, jpg_quality=CALIDAD)
        hechas += 1
for raiz, _, archivos in os.walk("miniaturas"):
    for a in archivos:
        p = os.path.join(raiz, a)
        if p not in validas:
            os.remove(p)
            borradas += 1
print(f"Miniaturas nuevas: {hechas} · borradas: {borradas} · total: {len(validas)}")
