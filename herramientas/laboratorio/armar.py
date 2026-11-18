"""Arma el laboratorio offline de Flota Logística: un solo HTML con todo adentro (motor, ejemplos, pdf.js y el proyecto
del preenunciado). Uso: python3 -I herramientas/laboratorio/armar.py  (desde la raíz del repo)."""
import datetime
import hashlib
import html as H
import json
import pathlib
import re
import unicodedata
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parents[2]
AQUI = RAIZ / 'herramientas' / 'laboratorio'
ZIP = RAIZ / 'material/backend-de-aplicaciones/p1/parcial/recuperatorio-1/01-preenunciado.zip'
SALIDA = RAIZ / 'material/backend-de-aplicaciones/p1/parcial/recuperatorio-1/laboratorio-flota.html'
PREFIJO = '01-modelo-inicial/'
CUESTIONARIOS = RAIZ / 'herramientas/cuestionarios-back/preguntas.json'
PARCIAL = RAIZ / 'quiz/backend-1er-parcial.json'


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


def plano(t):
    """Para comparar preguntas: sin etiquetas, sin tildes, en minúscula y solo letras y números."""
    t = re.sub(r'<[^>]*>', ' ', H.unescape(re.sub(r'<[^>]*>', ' ', t or '')))
    t = unicodedata.normalize('NFD', t.lower())
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in t if unicodedata.category(c) != 'Mn')).split())


def preguntas():
    """El banco del buscador: los cuestionarios 01 a 05 y todas las preguntas del 1.er parcial (las de la guía única:
    el parcial real, el proyecto, los simulacros, los apuntes y las de escribir). Todo en HTML; las repetidas, una vez."""
    banco, vistas = [], {}
    for c in json.loads(CUESTIONARIOS.read_text('utf-8'))['cuestionarios']:
        if c['n'] not in ('01', '02', '03', '04', '05'):
            continue
        for p in c['preguntas']:
            ex = H.escape(p.get('ex') or '')
            if p.get('ojo'):
                ex += ('<br>' if ex else '') + '<b>Ojo:</b> ' + H.escape(p['ojo'])
            banco.append({'f': [f"Cuestionario {c['n']} · {c['titulo']}"], 'en': H.escape(p['en']), 'code': '\n'.join(p.get('codigo') or []),
                          'tipo': 'vf' if p.get('vf') else 'varias' if p.get('varias') else 'una',
                          'op': [[H.escape(t), i in p['ok']] for i, t in enumerate(p['op'])], 'ex': ex})
    for s in json.loads(PARCIAL.read_text('utf-8'))['secciones']:
        for p in s['preguntas']:
            ex = p.get('ex') or ''
            if p.get('mal'):
                ex += ('<br>' if ex else '') + '<b>Ojo:</b> ' + p['mal']
            d = {'f': [p.get('fuente') or s['titulo']], 'en': p['en'], 'code': p.get('code') or '', 'tipo': p['tipo'], 'ex': ex}
            if p['tipo'] == 'modelo':
                d['modelo'] = p.get('modelo') or ''
            else:
                d['op'] = [[t, bool(v)] for t, v in p['op']]
            banco.append(d)
    unicas = []
    for d in banco:
        clave = plano(d['en']) + '|' + plano(d['code']) + '|' + '|'.join(sorted(plano(t) + ('+' if v else '-') for t, v in d.get('op', []))) + plano(d.get('modelo'))
        if clave in vistas:
            otra = vistas[clave]
            otra['f'] += [f for f in d['f'] if f not in otra['f']]
            continue
        vistas[clave] = d
        unicas.append(d)
    return unicas


def main():
    html = (AQUI / 'plantilla.html').read_text('utf-8')
    partes = {
        '/*@PDFJS@*/': (AQUI / 'vendor/pdfjs/pdf.min.js').read_text('utf-8'),
        '/*@WORKER@*/': (AQUI / 'vendor/pdfjs/pdf.worker.min.js').read_text('utf-8'),
        '/*@MOTOR@*/': (AQUI / 'motor.js').read_text('utf-8'),
        '/*@EJEMPLOS@*/': 'window.EJEMPLOS_EXTRA = [' + ','.join(f.read_text('utf-8').strip() for f in sorted(
                              AQUI.glob('practica-*/ejemplo.json'), key=lambda f: json.loads(f.read_text('utf-8'))['id'])) + '];\n'
                          + (AQUI / 'ejemplos.js').read_text('utf-8'),
        '/*@PROYECTO@*/': json.dumps(proyecto(), ensure_ascii=False),
        '/*@PREGUNTAS@*/': 'window.PREGUNTAS = ' + json.dumps(preguntas(), ensure_ascii=False) + ';',
    }
    for marca, texto in partes.items():
        assert html.count(marca) == 1, marca
        html = html.replace(marca, script(texto))
    # La versión: un resumen del contenido (cambia solo si cambia algo) y la fecha (hora de Argentina). El sitio enlaza
    # el archivo con ?v=versión, así el navegador no da una copia vieja guardada en la caché al abrirlo o descargarlo.
    version = hashlib.sha1(html.encode()).hexdigest()[:7]
    previa = SALIDA.read_text('utf-8') if SALIDA.exists() else ''
    m = re.search(r'Versión del (\d\d/\d\d/\d{4}) · ' + version, previa)
    fecha = m.group(1) if m else datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime('%d/%m/%Y')
    html = html.replace('@@FECHA@@', fecha).replace('@@VERSION@@', version)
    SALIDA.write_text(html, 'utf-8')
    indice = RAIZ / 'index.html'
    texto = indice.read_text('utf-8')
    nuevo = re.sub(r'(recuperatorio-1/laboratorio-flota\.html)(\?v=\w+)?"', r'\1?v=' + version + '"', texto)
    if nuevo != texto:
        indice.write_text(nuevo, 'utf-8')
    print(SALIDA.relative_to(RAIZ), f'{len(html.encode()) / 1024:.0f} KB', 'versión', version, fecha)


if __name__ == '__main__':
    main()
