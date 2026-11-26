"""Arma el laboratorio de DAO: un solo HTML que funciona sin internet.

Mete en plantilla.html el lector de PDF (el mismo del laboratorio de Backend), el lector de ZIP (proyecto.js), y el
motor: python-lee.js (lee Python), test-lee.js (entiende el test de pytest) y dao.js (arma la solución). Escribe
material/desarrollo-de-aplicaciones-con-objetos/recuperatorio/laboratorio-dao.html, su archivo de versión al lado
y actualiza el ?v= del enlace en index.html.

Uso: python3 herramientas/laboratorio-dao/armar.py
"""
import datetime
import hashlib
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
JAVA = AQUI.parent / 'laboratorio'
SALIDA = RAIZ / 'material/desarrollo-de-aplicaciones-con-objetos/recuperatorio/laboratorio-dao.html'


def main():
    t = (AQUI / 'plantilla.html').read_text('utf-8')
    partes = {
        '/*@PDFJS@*/': (JAVA / 'vendor/pdfjs/pdf.min.js').read_text('utf-8'),
        '/*@WORKER@*/': (JAVA / 'vendor/pdfjs/pdf.worker.min.js').read_text('utf-8'),
        '/*@MOTOR@*/': '\n'.join((d / n).read_text('utf-8') for d, n in [(JAVA, 'proyecto.js'), (AQUI, 'python-lee.js'), (AQUI, 'test-lee.js'), (AQUI, 'dao.js')]),
    }
    for marca, texto in partes.items():
        # los scripts no pueden traer «</script>» adentro
        t = t.replace(marca, texto.replace('</script', '<\\/script'))
    version = hashlib.sha1(t.encode('utf-8')).hexdigest()[:7]
    t = t.replace('@@VERSION@@', version).replace('@@FECHA@@', datetime.date.today().strftime('%d/%m/%Y'))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(t, 'utf-8')
    (SALIDA.parent / 'laboratorio-dao-version.txt').write_text(version + '\n', 'utf-8')
    indice = RAIZ / 'index.html'
    texto = indice.read_text('utf-8')
    nuevo = re.sub(r'(recuperatorio/laboratorio-dao\.html)(\?v=\w+)?"', r'\1?v=' + version + '"', texto)
    if nuevo != texto:
        indice.write_text(nuevo, 'utf-8')
    print(f'{SALIDA.relative_to(RAIZ)} {len(t) // 1024} KB versión {version} {datetime.date.today():%d/%m/%Y}')


if __name__ == '__main__':
    main()
