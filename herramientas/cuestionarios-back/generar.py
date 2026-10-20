# Arma los PDF de los cuestionarios de Backend con el estilo de la revisión del campus:
# cabecera gris (pregunta, estado, puntaje), la pregunta en el recuadro azul con la tilde verde o la cruz roja,
# y abajo el recuadro beige con la respuesta correcta, el porqué y la corrección si estaba mal.
#
# Los datos están en preguntas.json (una entrada por cuestionario, con sus preguntas ya resueltas).
# Uso: python3 herramientas/cuestionarios-back/generar.py [--fuente CARPETA] [--solo 01,05]
#   --fuente: carpeta con open-sans-latin-{400,600,700}-normal.woff2 (de @fontsource/open-sans). Sin eso usa DejaVu Sans.
# Necesita Chromium (el de Playwright) y pymupdf. Escribe en material/backend-de-aplicaciones/cuestionarios/.
import argparse, html, json, os, shutil, subprocess, tempfile
import pymupdf

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESTINO = os.path.join(RAIZ, 'material', 'backend-de-aplicaciones', 'cuestionarios')
CHROMIUM = next((c for c in (os.environ.get('CHROMIUM'), '/opt/pw-browsers/chromium', shutil.which('chromium'), shutil.which('chromium-browser')) if c and os.path.exists(c)), None)
LETRAS = 'abcdefghij'

TILDE = '<svg class="ic ok" viewBox="0 0 16 16"><path d="M3 8.5l3.2 3.2L13 4.8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CRUZ = '<svg class="ic mal" viewBox="0 0 16 16"><path d="M4 4l8 8M12 4l-8 8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'
FALTA = '<span class="falta">' + TILDE + 'faltaba</span>'

CSS = """
@page { size: A4; margin: 14mm 15mm 14mm 15mm; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Open Sans', 'DejaVu Sans', sans-serif; font-size: 10pt; color: #1d2125; margin: 0; line-height: 1.4; }
h1 { font-size: 19pt; font-weight: 600; margin: 0 0 2pt; color: #1d2125; }
.sup { color: #6a737b; font-size: 9.5pt; margin-bottom: 8pt; }
table.res { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 9.6pt; }
table.res th { text-align: right; width: 30%; padding: 3pt 8pt; font-weight: 600; border-top: 1px solid #dee2e6; vertical-align: top; }
table.res td { padding: 3pt 8pt; border-top: 1px solid #dee2e6; }
table.res tr:last-child th, table.res tr:last-child td { border-bottom: 1px solid #dee2e6; }
.leyenda .ic { width: 11pt; height: 11pt; vertical-align: -2pt; }
h2 { font-size: 12.5pt; font-weight: 600; margin: 14pt 0 6pt; padding-bottom: 3pt; border-bottom: 2px solid #0f6cbf; color: #0f6cbf; break-after: avoid; }
.q { break-inside: avoid; margin-bottom: 10pt; }
.info { background: #dee2e6; border: 1px solid #ced4da; border-radius: 3pt; padding: 5pt 9pt; font-size: 8.4pt; color: #343a40; display: flex; justify-content: space-between; align-items: flex-start; }
.info .num { font-size: 8.4pt; }
.info .num b { font-size: 13pt; font-weight: 700; color: #1d2125; margin-left: 2pt; }
.info .est { margin-top: 1pt; }
.chip { font-size: 7.8pt; border-radius: 8pt; padding: 1pt 7pt; font-weight: 600; white-space: nowrap; }
.chip.tuyo { background: #0f6cbf; color: #fff; }
.chip.otro { background: #fff; color: #495057; border: 1px solid #adb5bd; }
.form { background: #def2f8; border: 1px solid #b8e0ee; border-radius: 3pt; padding: 7pt 11pt; margin-top: 5pt; color: #12404f; }
.en { margin-bottom: 5pt; }
pre { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.4pt; line-height: 1.4; background: #f4fafc; border: 1px solid #c9e6f0; border-radius: 3pt; padding: 5pt 8pt; margin: 4pt 0 6pt; white-space: pre-wrap; color: #1d2125; }
.sel { margin: 4pt 0 2pt; }
.op { display: flex; align-items: flex-start; gap: 6pt; padding: 1.6pt 0; }
.marca { flex: none; width: 10pt; height: 10pt; margin-top: 2.4pt; border: 1px solid #8f959e; background: #fff; position: relative; }
.marca.radio { border-radius: 50%; }
.marca.caja { border-radius: 2pt; }
.marca.si.radio::after { content: ''; position: absolute; left: 2.2pt; top: 2.2pt; width: 4.4pt; height: 4.4pt; border-radius: 50%; background: #6a737b; }
.marca.si.caja { background: #8f959e; border-color: #8f959e; }
.marca.si.caja::after { content: ''; position: absolute; left: 3.2pt; top: 0.6pt; width: 2.6pt; height: 5.6pt; border: solid #fff; border-width: 0 1.5pt 1.5pt 0; transform: rotate(45deg); }
.letra { flex: none; width: 13pt; }
.txt { flex: 1; }
.ic { width: 12pt; height: 12pt; vertical-align: -2.5pt; margin-left: 3pt; }
.ic.ok { color: #357a32; }
.ic.mal { color: #ca3120; }
.falta { color: #357a32; font-size: 8pt; font-weight: 600; white-space: nowrap; }
.falta .ic { width: 10pt; height: 10pt; vertical-align: -1.5pt; margin-right: 1pt; }
.out { background: #fcefdc; border: 1px solid #fbe3c0; border-radius: 3pt; padding: 6pt 11pt; margin-top: 5pt; color: #7d4a00; font-size: 9.5pt; }
.out p { margin: 0 0 3pt; }
.out p:last-child { margin-bottom: 0; }
.out .rc { color: #7d4a00; }
.out .pq { color: #4a3b26; }
.out .corr { color: #a52714; }
.out .ojo { color: #5b4a00; }
.out b { font-weight: 600; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.8pt; }
"""

def fuentes(carpeta):
    if not carpeta: return ''
    css = ''
    for peso in (400, 600, 700):
        f = os.path.join(carpeta, f'open-sans-latin-{peso}-normal.woff2')
        if os.path.exists(f):
            css += "@font-face { font-family: 'Open Sans'; font-weight: %d; src: url('file://%s') format('woff2'); }\n" % (peso, f)
    return css

def e(t): return html.escape(t, quote=False)

def coma(x): return f'{x:.2f}'.replace('.', ',')

def opcion(p, i, t):
    marcada, correcta = i in p['marcadas'], i in p['ok']
    tipo = 'caja' if p['varias'] else 'radio'
    icono = ''
    if marcada: icono = TILDE if correcta else CRUZ
    elif correcta and p['estado'] != 'Correcta': icono = ' ' + FALTA
    letra = '' if p['vf'] else f'<span class="letra">{LETRAS[i]}.</span>'
    return f'<div class="op"><span class="marca {tipo}{" si" if marcada else ""}"></span>{letra}<span class="txt">{e(t)}{icono}</span></div>'

def correcta(p):
    ok = p['ok']
    if p['vf']: return f"La respuesta correcta es «{e(p['op'][ok[0]])}»."
    partes = [f"{LETRAS[i]}. {e(p['op'][i].rstrip('.'))}" for i in ok]
    if len(ok) == 1: return 'La respuesta correcta es: <b>' + partes[0] + '</b>'
    return 'Las respuestas correctas son: <b>' + '</b> · <b>'.join(partes) + '</b>'

def pregunta(p, n, anio_intento):
    tuyo = p['origen'] == str(anio_intento)
    chip = f'<span class="chip tuyo">Tu intento {p["origen"]}</span>' if tuyo else f'<span class="chip otro">Cuestionario {p["origen"]}</span>'
    pts, mx = p['puntos']
    info = (f'<div class="info"><div><div class="num">Pregunta<b>{n}</b></div><div class="est">{p["estado"]}</div>'
            f'<div>Puntúa {coma(pts)} sobre {coma(mx)}</div></div>{chip}</div>')
    cuerpo = f'<div class="en">{e(p["en"])}</div>'
    if p.get('codigo'): cuerpo += '<pre>' + e('\n'.join(p['codigo'])) + '</pre>'
    cuerpo += '<div class="sel">' + ('Seleccione una o más de una:' if p['varias'] else 'Seleccione una:') + '</div>'
    cuerpo += ''.join(opcion(p, i, t) for i, t in enumerate(p['op']))
    out = f'<p class="rc">{correcta(p)}</p><p class="pq"><b>Por qué:</b> {e(p["ex"])}</p>'
    if p.get('corr'): out += f'<p class="corr"><b>Corrección:</b> {e(p["corr"])}</p>'
    if p.get('ojo'): out += f'<p class="ojo"><b>Ojo:</b> {e(p["ojo"])}</p>'
    return f'<div class="q">{info}<div class="form">{cuerpo}</div><div class="out">{out}</div></div>'

def documento(c, css_fuentes):
    ps = c['preguntas']
    anio = c['intento']['anio'] if c['intento'] else None
    grupos = []
    for origen in [str(anio)] if anio else []:
        grupos.append((f'Tu intento {origen}', [p for p in ps if p['origen'] == origen]))
    otros = sorted({p['origen'] for p in ps if p['origen'] != str(anio)})
    for o in otros:
        grupos.append((f'Preguntas del cuestionario {o}', [p for p in ps if p['origen'] == o]))
    filas = [('Preguntas', f'{len(ps)}, sin repetir')]
    if anio:
        mias = grupos[0][1]
        filas.append((f'Tu intento {anio}', f"{len(mias)} preguntas · {c['intento']['nota']} · {sum(1 for p in mias if p['estado'] != 'Correcta')} con corrección"))
    for titulo, g in grupos[1 if anio else 0:]:
        filas.append((titulo.replace('Preguntas del cuestionario', 'Sumadas de'), f'{len(g)} preguntas'))
    filas.append(('Cómo leerlo', f'<span class="leyenda">{TILDE} bien marcada · {CRUZ} mal marcada · <span class="falta">{TILDE}faltaba</span> la que había que marcar</span>'))
    tabla = ''.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k, v in filas)
    cuerpo, n = '', 0
    for titulo, g in grupos:
        cuerpo += f'<h2>{e(titulo)}</h2>'
        for p in g:
            n += 1
            cuerpo += pregunta(p, n, anio)
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Cuestionario {c["n"]} · {e(c["titulo"])}</title>'
            f'<style>{css_fuentes}{CSS}</style></head><body>'
            f'<div class="sup">Backend de Aplicaciones · Cuestionario {c["n"]}</div><h1>{e(c["titulo"])}</h1>'
            f'<table class="res">{tabla}</table>{cuerpo}</body></html>')

def imprimir(html_path, pdf_path):
    subprocess.run([CHROMIUM, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    '--disable-background-networking', '--disable-component-update', '--no-first-run',
                    f'--print-to-pdf={pdf_path}', 'file://' + html_path], check=True, capture_output=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fuente')
    ap.add_argument('--solo')
    ap.add_argument('--html', help='dejar también el HTML en esta carpeta, para revisarlo')
    ap.add_argument('--salida', default=DESTINO, help='carpeta donde quedan los PDF')
    a = ap.parse_args()
    if not CHROMIUM: raise SystemExit('No encuentro Chromium (poné su ruta en la variable CHROMIUM).')
    datos = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preguntas.json')))
    solo = set(a.solo.split(',')) if a.solo else None
    css_f = fuentes(os.path.abspath(a.fuente) if a.fuente else None)
    with tempfile.TemporaryDirectory() as tmp:
        for c in datos['cuestionarios']:
            if solo and c['n'] not in solo: continue
            h = os.path.join(tmp, c['n'] + '.html')
            open(h, 'w').write(documento(c, css_f))
            if a.html: shutil.copy(h, os.path.join(a.html, c['n'] + '.html'))
            crudo = os.path.join(tmp, c['n'] + '.pdf')
            imprimir(h, crudo)
            d = pymupdf.open(crudo)
            d.set_metadata({'title': f"Cuestionario {c['n']} · {c['titulo']}", 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': ''})
            d.del_xml_metadata()
            salida = os.path.join(a.salida, c['archivo'])
            d.save(salida, garbage=4, deflate=True)
            print(c['archivo'], len(d), 'páginas,', len(c['preguntas']), 'preguntas')

if __name__ == '__main__':
    main()
