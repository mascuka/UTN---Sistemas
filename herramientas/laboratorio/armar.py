"""Arma el laboratorio offline de Flota Logística: un solo HTML con todo adentro (motor, ejemplos, pdf.js y el proyecto
del preenunciado). Uso: python3 -I herramientas/laboratorio/armar.py  (desde la raíz del repo)."""
import json
import pathlib
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parents[2]
AQUI = RAIZ / 'herramientas' / 'laboratorio'
ZIP = RAIZ / 'material/backend-de-aplicaciones/p1/parcial/recuperatorio-1/01-preenunciado.zip'
SALIDA = RAIZ / 'material/backend-de-aplicaciones/p1/parcial/recuperatorio-1/laboratorio-flota.html'
PREFIJO = '01-modelo-inicial/'


def script(texto):
    """Lo que va dentro de <script>: que no cierre la etiqueta antes de tiempo."""
    return texto.replace('</script', '<\\/script').replace('<!--', '<\\!--')


def proyecto():
    archivos = {}
    with zipfile.ZipFile(ZIP) as z:
        for info in z.infolist():
            if info.is_dir() or not info.filename.startswith(PREFIJO):
                continue
            ruta = info.filename[len(PREFIJO):]
            archivos[ruta] = z.read(info).decode('utf-8').replace('\r\n', '\n')
    assert 'datos/datos.csv' in archivos and 'src/main/java/ar/edu/backend/VehiculoRuta.java' in archivos
    return dict(sorted(archivos.items()))


def main():
    html = (AQUI / 'plantilla.html').read_text('utf-8')
    partes = {
        '/*@PDFJS@*/': (AQUI / 'vendor/pdfjs/pdf.min.js').read_text('utf-8'),
        '/*@WORKER@*/': (AQUI / 'vendor/pdfjs/pdf.worker.min.js').read_text('utf-8'),
        '/*@MOTOR@*/': (AQUI / 'motor.js').read_text('utf-8'),
        '/*@EJEMPLOS@*/': 'window.EJEMPLOS_EXTRA = [' + (AQUI / 'practica-pendiente/ejemplo.json').read_text('utf-8').strip() + '];\n'
                          + (AQUI / 'ejemplos.js').read_text('utf-8'),
        '/*@PROYECTO@*/': json.dumps(proyecto(), ensure_ascii=False),
    }
    for marca, texto in partes.items():
        assert html.count(marca) == 1, marca
        html = html.replace(marca, script(texto))
    SALIDA.write_text(html, 'utf-8')
    print(SALIDA.relative_to(RAIZ), f'{len(html.encode()) / 1024:.0f} KB')


if __name__ == '__main__':
    main()
