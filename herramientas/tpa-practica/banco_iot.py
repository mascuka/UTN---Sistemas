# Arma el Banco de preguntas de IoT (3º parcial de TPA) desde el quiz: quiz/tpa-3er-parcial.json.
# Cada pregunta como en el campus (opciones con las correctas en verde, la respuesta como la muestra el campus y el porqué),
# agrupadas por tema. Las reales llevan "fuente" (Parcial / Recuperatorio / Simulacro IoT 2025 o 2026) y las de práctica,
# "practica". Las de armar el programa ("armar": objetivo, huecos y fichas de más) van con las líneas para arrastrar
# y el programa armado en verde.
# Necesita Chromium (el de Playwright) y pymupdf. Desde la raíz:  python3 herramientas/tpa-practica/banco_iot.py
import html, json, os, shutil, subprocess, tempfile
import pymupdf

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
QUIZ = os.path.join(RAIZ, 'quiz', 'tpa-3er-parcial.json')
PDF = os.path.join(RAIZ, 'material', 'tecnologias-para-la-automatizacion', 'p3-iot', '02-banco-de-preguntas-iot.pdf')
CHROMIUM = next((c for c in (os.environ.get('CHROMIUM'), '/opt/pw-browsers/chromium', shutil.which('chromium')) if c and os.path.exists(c)), None)
PIE = 'Tecnologías para la Automatización · Banco de preguntas IoT'
LETRAS = 'abcdefgh'
# La escala de notas que muestra el campus en la revisión del parcial
ESCALA = [(1, '0% a 29%', 'No aprobado'), (2, '30% a 49%', 'No aprobado'), (3, '50% a 54%', 'No aprobado'), (4, '55% a 57%', 'Aprobado'), (5, '58% a 59%', 'Aprobado'),
          (6, '60% a 68%', 'Aprobado'), (7, '69% a 77%', 'Aprobado'), (8, '78% a 86%', 'Aprobado'), (9, '87% a 95%', 'Aprobado'), (10, '96% a 100%', 'Aprobado')]

CSS = """
@page { size: A4; margin: 14mm 14mm 16mm; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: Inter, 'DejaVu Sans', sans-serif; font-size: 9.6pt; color: #1e293b; margin: 0; line-height: 1.45; }
.cab { background: linear-gradient(120deg, #1e3a5f, #0f766e); color: #fff; border-radius: 10pt; padding: 16pt 18pt 14pt; }
.cab small { display: block; font-size: 8pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; opacity: .85; }
.cab h1 { font-size: 22pt; font-weight: 800; margin: 4pt 0 3pt; }
.cab p { margin: 0 0 9pt; font-size: 10.5pt; opacity: .92; }
.chip { display: inline-block; font-size: 7.6pt; font-weight: 600; background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.3); border-radius: 9pt; padding: 2pt 8pt; margin-right: 4pt; }
.intro { background: #ccfbf1; border: 1px solid #99f6e4; border-radius: 8pt; padding: 9pt 12pt; margin: 10pt 0 6pt; }
.intro b.t { display: block; color: #115e59; font-size: 10pt; margin-bottom: 2pt; }
.intro p { margin: 0 0 4pt; }
.intro .tip { font-size: 8.2pt; color: #334155; margin: 0; }
.escala { break-inside: avoid; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8pt; padding: 8pt 12pt; margin: 6pt 0 10pt; }
.escala b.t { display: block; color: #1e3a5f; font-size: 10pt; margin-bottom: 3pt; }
.escala p { margin: 0 0 5pt; font-size: 9pt; }
.escala table { border-collapse: collapse; width: 100%; font-size: 8.4pt; text-align: center; }
.escala td, .escala th { border: 1px solid #cbd5e1; padding: 1.6pt 4pt; }
.escala th { background: #e2e8f0; font-weight: 700; }
.escala td.no { color: #b91c1c; } .escala td.si { color: #15803d; }
h2 { break-after: avoid; background: #1e3a5f; color: #fff; font-size: 11pt; font-weight: 700; border-radius: 6pt; padding: 5pt 10pt; margin: 12pt 0 8pt; }
.q { display: grid; grid-template-columns: 76pt 1fr; gap: 8pt; break-inside: avoid; margin-bottom: 9pt; }
.lado { border: 1px solid #e2e8f0; border-radius: 6pt; padding: 6pt 7pt; align-self: start; font-size: 7.8pt; color: #64748b; }
.lado b { display: block; color: #0f172a; font-size: 9.6pt; }
.lado .tipo { padding-bottom: 5pt; border-bottom: 1px solid #e2e8f0; margin-bottom: 5pt; }
.lado .real { color: #2563eb; }
.lado .prac { display: inline-block; background: #ede9fe; color: #6d28d9; font-weight: 700; border-radius: 6pt; padding: 1pt 6pt; }
.form { background: #e8f1f4; border-radius: 6pt; padding: 7pt 10pt 6pt; }
.en { font-size: 10.2pt; margin-bottom: 3pt; }
.sel { font-size: 7.8pt; color: #475569; margin-bottom: 3pt; }
.op { display: flex; gap: 5pt; padding: 2pt 5pt; border-radius: 4pt; font-size: 9.4pt; }
.op.ok { background: #d1fae5; }
.op .m { width: 11pt; flex: none; color: #64748b; }
.op.ok .m, .op .v { color: #15803d; }
.rc { background: #fdf0dc; border-radius: 6pt; padding: 6pt 10pt; margin-top: 5pt; font-size: 8.6pt; color: #7c4a03; }
.pq { background: #f0fdfa; border-left: 2.5pt solid #0f766e; border-radius: 0 6pt 6pt 0; padding: 6pt 10pt; margin-top: 5pt; font-size: 8.6pt; }
.pq b.t { color: #115e59; }
pre { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.2pt; line-height: 1.4; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 5pt; padding: 5pt 8pt; margin: 3pt 0 5pt; white-space: pre-wrap; }
.obj { margin: 0 0 5pt 14pt; padding: 0; font-size: 9pt; }
.fichas { margin: 2pt 0 6pt; }
.ficha { display: inline-block; font-family: 'DejaVu Sans Mono', monospace; font-size: 7.6pt; background: #fff; border: 1px solid #cbd5e1; border-radius: 4pt; padding: 1.5pt 5pt; margin: 0 3pt 3pt 0; }
.huecos { margin: 0; padding: 0; list-style: none; counter-reset: h; }
.huecos li { counter-increment: h; display: flex; gap: 6pt; align-items: center; margin-bottom: 2pt; }
.huecos li::before { content: counter(h); width: 12pt; text-align: right; font-size: 7pt; color: #64748b; }
.huecos span { flex: 1; font-family: 'DejaVu Sans Mono', monospace; font-size: 8pt; background: #d1fae5; border: 1px solid #86efac; border-radius: 4pt; padding: 1.5pt 6pt; }
"""

def correctas(p):
    ok = [o for o, v in p['op'] if v]
    return f"La respuesta correcta es: {ok[0]}" if len(ok) == 1 else 'Las respuestas correctas son: ' + ', '.join(ok)

def pregunta(p, n):
    e = html.escape
    tipo = {'num': 'Respuesta numérica', 'varias': 'Varias respuestas', 'armar': 'Armar el programa'}.get(p['tipo'], 'Una respuesta')
    fuente = f'<span class="real">{e(p["fuente"])}</span>' if p.get('fuente') else '<span class="prac">De práctica</span>'
    cuerpo = f'<div class="en">{e(p["en"])}</div>'
    if p.get('code'): cuerpo += f'<pre>{e(p["code"])}</pre>'
    if p['tipo'] == 'num':
        rc = f'La respuesta correcta es: {e(str(p["num"]))}'
    elif p['tipo'] == 'armar':
        # Las líneas para arrastrar (en orden alfabético, como una bolsa) y el programa armado
        cuerpo += '<ul class="obj">' + ''.join(f'<li>{e(o)}</li>' for o in p['objetivo']) + '</ul>'
        cuerpo += '<div class="sel">Las líneas para arrastrar (sobran algunas):</div><div class="fichas">' + ''.join(f'<span class="ficha">{e(t)}</span>' for t in sorted(p['huecos'] + p['fichas'], key=str.lower)) + '</div>'
        cuerpo += '<div class="sel">Armado:</div><ol class="huecos">' + ''.join(f'<li><span>{e(t)}</span></li>' for t in p['huecos']) + '</ol>'
        rc = f'Cada uno de los {len(p["huecos"])} huecos vale lo mismo. Sobran: ' + ' · '.join(f'<code>{e(t)}</code>' for t in p['fichas'])
    else:
        varias = p['tipo'] == 'varias'
        cuerpo += f'<div class="sel">{"Seleccione una o más de una:" if varias else "Seleccione una:"}</div>'
        for i, (o, v) in enumerate(p['op']):
            marca = ('☑' if v else '☐') if varias else ('◉' if v else '○')
            cuerpo += f'<div class="op{" ok" if v else ""}"><span class="m">{marca}</span><span>{LETRAS[i]}. {e(o)}{" <span class=v>✓</span>" if v else ""}</span></div>'
        rc = e(correctas(p))
    # El porqué ya viene con su formato (<b>, <sup>…)
    return (f'<div class="q"><div class="lado"><b>Pregunta {n}</b><div class="tipo">{tipo}</div>{fuente}</div>'
            f'<div><div class="form">{cuerpo}</div><div class="rc">{rc}</div><div class="pq"><b class="t">Por qué:</b> {p["ex"]}</div></div></div>')

def documento(q):
    todas = [p for s in q['secciones'] for p in s['preguntas']]
    reales = sum(1 for p in todas if p.get('fuente'))
    prac = len(todas) - reales
    escala = ''.join(f'<tr><td>{n}</td><td>{pc}</td><td class="{"si" if a == "Aprobado" else "no"}">{a}</td></tr>' for n, pc, a in ESCALA[:5])
    escala2 = ''.join(f'<tr><td>{n}</td><td>{pc}</td><td class="si">{a}</td></tr>' for n, pc, a in ESCALA[5:])
    h = f"""<div class="cab"><small>Tecnologías para la Automatización · 3º parcial IoT</small><h1>Banco de preguntas · IoT</h1>
      <p>Las preguntas de los parciales anteriores con la respuesta y por qué, más preguntas de práctica</p>
      <span class="chip">{reales} preguntas reales (2025 y 2026)</span><span class="chip">{prac} de práctica del apunte 2026</span><span class="chip">Formato del campus</span></div>
    <div class="intro"><b class="t">Cómo usar este banco</b>
      <p>Están <b>todas las preguntas que salieron</b> en los parciales, recuperatorios y simulacros de IoT de 2025 y 2026, sacadas de intentos reales del campus (cada una dice de dónde salió), y además preguntas <b>de práctica</b> armadas con el apunte 2026 y las clases, con el mismo formato. Las opciones correctas están en verde, abajo va la respuesta como la muestra el campus y una explicación corta. Están agrupadas por tema y sin repetir.</p>
      <p class="tip">Tip: tapá las opciones en verde y respondé primero; en el parcial casi todas tienen <b>más de una</b> respuesta correcta.</p></div>
    <div class="escala"><b class="t">Cómo se califica</b>
      <p>El parcial 2025 tuvo <b>10 preguntas de 10 puntos</b>, todas de casillas («una o más de una»), al azar de este banco. En el recuperatorio 2026 valen <b>8, 12 o 16</b>: las de «¿qué está mal en este código?» 12 y la de <b>armar el programa</b> (arrastrar cada línea a su hueco) 16, con cada hueco valiendo lo mismo. Cada correcta marcada suma una parte y <b>cada incorrecta marcada resta</b> (con una bien y una mal, por ejemplo, quedan 1,67 o 6,67 puntos según la pregunta): no marques de más. La nota sale de esta escala del campus:</p>
      <div style="display:flex;gap:8pt"><table><tr><th>Nota</th><th>Porcentaje</th><th>Calificación</th></tr>{escala}</table><table><tr><th>Nota</th><th>Porcentaje</th><th>Calificación</th></tr>{escala2}</table></div></div>"""
    n = 0
    for i, s in enumerate(q['secciones'], 1):
        h += f'<h2>{i} · {html.escape(s["titulo"])}</h2>'
        for p in s['preguntas']:
            n += 1
            h += pregunta(p, n)
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{h}</body></html>', n

def main():
    if not CHROMIUM: raise SystemExit('No encuentro Chromium (poné su ruta en la variable CHROMIUM).')
    q = json.load(open(QUIZ, encoding='utf-8'))
    doc, n = documento(q)
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, 'banco.html'); open(h, 'w', encoding='utf-8').write(doc)
        crudo = os.path.join(tmp, 'banco.pdf')
        subprocess.run([CHROMIUM, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--disable-background-networking',
                        '--no-first-run', f'--print-to-pdf={crudo}', 'file://' + h], check=True, capture_output=True)
        d = pymupdf.open(crudo)
        # El pie de cada página: el nombre y el número
        for i, pag in enumerate(d):
            r = pag.rect
            pag.insert_text((40, r.height - 22), PIE, fontsize=6.5, color=(.39, .45, .55))
            t = f'{i + 1} / {len(d)}'
            pag.insert_text((r.width - 40 - pymupdf.get_text_length(t, fontsize=6.5), r.height - 22), t, fontsize=6.5, color=(.39, .45, .55))
        d.set_metadata({'title': 'Banco de preguntas · IoT', 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': ''})
        d.del_xml_metadata()
        d.save(PDF, garbage=4, deflate=True)
        print(os.path.relpath(PDF, RAIZ), len(d), 'páginas,', n, 'preguntas')

if __name__ == '__main__':
    main()
