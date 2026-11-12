"""Genera la miniatura (primera página) de cada PDF de material/ en miniaturas/.

material/redes-de-datos/p2/teorico/apunte.pdf -> miniaturas/redes-de-datos/p2/teorico/apunte.jpg
Solo crea las que faltan o las de PDFs más nuevos que su miniatura, y borra las que ya no tienen PDF.
Uso (desde la raíz del repo):  pip install pymupdf  y  python3 herramientas/miniaturas.py
Con --todas las vuelve a hacer todas (por ejemplo, después de cambiar cómo se hacen).

Para que no se vea como una hoja gris borrosa a ~40 px:
- se recorta el margen en blanco y se toma la parte de arriba de la hoja con la forma de la caja donde se muestra (38 × 50);
- en las hojas blancas (texto) se oscurece el texto, que a ese tamaño queda muy claro; las de color (diapositivas) quedan igual;
- se guarda a 240 px de ancho, nítida hasta en pantallas de alta densidad.
"""
import os
import sys
import pymupdf

ANCHO = 240         # px: se muestra a 30–46 px
CALIDAD = 82
PROP = 50 / 38      # alto / ancho de la caja de la lista
OSCURECER = 1.8     # gamma para las hojas de texto (1 = igual, más = más oscuro)


def zona(pag):
    """La parte de la hoja que va en la miniatura: el contenido sin el margen en blanco, desde arriba."""
    r = pag.rect
    area = r.width * r.height
    cajas = [pymupdf.Rect(b[:4]) for b in pag.get_text("blocks") if b[4].strip()]
    cajas += [pymupdf.Rect(i["bbox"]) for i in pag.get_image_info()]
    cajas += [d["rect"] for d in pag.get_drawings() if d["rect"].width * d["rect"].height < area * .85]
    cajas = [c & r for c in cajas]
    cajas = [c for c in cajas if c.width > .5 and c.height > .5]
    if not cajas:
        return r
    u = pymupdf.Rect(cajas[0])
    for c in cajas[1:]:
        u |= c
    pad = r.width * .035
    u = (u + (-pad, -pad, pad, pad)) & r
    if u.width < r.width * .6:      # poco contenido: que no quede demasiado de cerca
        cx, w = (u.x0 + u.x1) / 2, r.width * .6
        u = pymupdf.Rect(max(r.x0, cx - w / 2), u.y0, min(r.x1, cx + w / 2), u.y1)
    return pymupdf.Rect(u.x0, u.y0, u.x1, min(u.y1, u.y0 + u.width * PROP))


def miniatura(pdf, jpg):
    with pymupdf.open(pdf) as d:
        pag = d[0]
        z = zona(pag)
        esc = ANCHO / z.width
        pix = pag.get_pixmap(matrix=pymupdf.Matrix(esc, esc), clip=z, alpha=False)
    m = pix.samples
    claro = sum(m[::97]) / len(m[::97]) / 255      # brillo medio (una muestra cada 97 bytes alcanza)
    if claro > .86:
        pix.gamma_with(OSCURECER)
    os.makedirs(os.path.dirname(jpg), exist_ok=True)
    pix.save(jpg, jpg_quality=CALIDAD)


todas = "--todas" in sys.argv
hechas = borradas = 0
validas = set()
for raiz, _, archivos in os.walk("material"):
    for a in sorted(archivos):
        if not a.lower().endswith(".pdf"):
            continue
        pdf = os.path.join(raiz, a)
        jpg = os.path.join("miniaturas", os.path.relpath(pdf, "material"))[:-4] + ".jpg"
        validas.add(jpg)
        if not todas and os.path.exists(jpg) and os.path.getmtime(jpg) >= os.path.getmtime(pdf):
            continue
        miniatura(pdf, jpg)
        hechas += 1
for raiz, _, archivos in os.walk("miniaturas"):
    for a in archivos:
        p = os.path.join(raiz, a)
        if p not in validas:
            os.remove(p)
            borradas += 1
print(f"Miniaturas nuevas: {hechas} · borradas: {borradas} · total: {len(validas)}")
