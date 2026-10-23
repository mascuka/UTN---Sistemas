# Arma el material del TPI resuelto por el grupo 1 (TP de TPA):
# - la guía técnica en PDF (desde tpi-grupo-1/guia-tecnica-tpi-4k3.md, con el diagrama dibujado acá) y
# - el ZIP con los dos sketches (los de practica/esp32/profe/, que ya tienen las claves tapadas) y la guía en .md.
# Necesita Chromium (el de Playwright), pymupdf y markdown (pip install markdown).
# Desde la raíz:  python3 herramientas/tpa-practica/guia_tpi.py
import html, os, re, shutil, subprocess, sys, tempfile, zipfile
import markdown, pymupdf

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
MD = os.path.join(AQUI, 'tpi-grupo-1', 'guia-tecnica-tpi-4k3.md')
DESTINO = os.path.join(RAIZ, 'material', 'tecnologias-para-la-automatizacion', 'tp-esp32')
PDF = os.path.join(DESTINO, '07-tpi-resuelto-grupo-1-guia-tecnica.pdf')
ZIP = os.path.join(DESTINO, 'tpi-resuelto-grupo-1.zip')
SKETCHES = ['sketch_envio_grupo_1.ino', 'sketch_lectura_grupo_1.ino']
CHROMIUM = next((c for c in (os.environ.get('CHROMIUM'), '/opt/pw-browsers/chromium', shutil.which('chromium')) if c and os.path.exists(c)), None)

def caja(x, y, w, h, texto, sub='', fuerte=False):
    fondo, borde = ('#e4f3f5', '#2d8992') if fuerte else ('#f7f7f5', '#b9b8b2')
    t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fondo}" stroke="{borde}"/>'
    cy = y + h / 2 + (-5 if sub else 4)
    t += f'<text x="{x + w / 2}" y="{cy}" text-anchor="middle" font-size="11.5" font-weight="{700 if fuerte else 600}">{html.escape(texto)}</text>'
    if sub: t += f'<text x="{x + w / 2}" y="{cy + 14}" text-anchor="middle" font-size="9.5" fill="#55544f">{html.escape(sub)}</text>'
    return t

def flecha(x1, y1, x2, y2, texto='', dx=0, dy=-5, punteada=False):
    trazo = ' stroke-dasharray="5 4"' if punteada else ''
    t = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#55544f" stroke-width="1.3" marker-end="url(#pta)"{trazo}/>'
    if texto: t += f'<text x="{(x1 + x2) / 2 + dx}" y="{(y1 + y2) / 2 + dy}" text-anchor="middle" font-size="9.5" fill="#2d2c29">{html.escape(texto)}</text>'
    return t

def diagrama():
    s = ['<svg viewBox="0 0 720 345" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, sans-serif">',
         '<defs><marker id="pta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#55544f"/></marker></defs>']
    # El sketch 1: entradas, la placa y las salidas
    for i, (a, b) in enumerate([('DHT22', 'GPIO 33'), ('Potenciómetro', 'GPIO 32'), ('Touch', 'GPIO 13 y 4')]):
        s.append(caja(10, 18 + i * 40, 150, 32, a, b)); s.append(flecha(160, 34 + i * 40, 230, 75))
    s.append(caja(230, 35, 200, 80, 'Sketch 1 · por USB', 'lee, controla, publica y ArduinoOTA', True))
    s.append(caja(540, 30, 170, 32, 'LEDs', 'integrado GPIO 2 · externo 23')); s.append(flecha(430, 65, 540, 46))
    s.append(caja(540, 80, 170, 32, 'Display OLED', 'I2C 0x3C · GPIO 21 / 22')); s.append(flecha(430, 90, 540, 96))
    # La nube y el IDE
    s.append(caja(540, 158, 170, 40, 'ThingSpeak', 'canal público, campos 1 a 6'))
    s.append(flecha(430, 108, 560, 158, '6 campos cada 16 s', dx=30, dy=-14))
    s.append(caja(10, 158, 150, 40, 'Arduino IDE', 'puerto de red ESP32_TPI4K3'))
    s.append(flecha(160, 170, 280, 115, 'ArduinoOTA: sube el sketch 2', dx=107, dy=0, punteada=True))
    # El sketch 2
    s.append(caja(10, 273, 150, 32, 'Pulsador', 'GPIO 19 · interrupción')); s.append(flecha(160, 289, 230, 289))
    s.append(caja(230, 255, 200, 70, 'Sketch 2 · por OTA', 'lee el canal y cuenta pulsaciones', True))
    s.append(flecha(610, 198, 430, 268, 'GET feeds/last.json cada 16 s', dx=95, dy=-6))
    s.append(caja(540, 273, 170, 32, 'Display OLED', '2 páginas de 3 campos')); s.append(flecha(430, 300, 540, 289))
    s.append('</svg>')
    return ''.join(s)

CSS = """
@page { size: A4; margin: 15mm 15mm 16mm; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 9.6pt; line-height: 1.45; color: #1f1e1c; }
h1 { font-size: 19pt; margin: 0 0 6pt; color: #1b5d64; }
h2 { font-size: 13.5pt; margin: 16pt 0 6pt; padding-bottom: 3pt; border-bottom: 1.5px solid #2d8992; color: #1b5d64; break-after: avoid; }
h3 { font-size: 11pt; margin: 12pt 0 4pt; break-after: avoid; }
h4 { font-size: 10pt; margin: 10pt 0 3pt; color: #46453f; break-after: avoid; }
p { margin: 0 0 6pt; }
ul, ol { margin: 0 0 7pt; padding-left: 18pt; }
li { margin-bottom: 2pt; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.4pt; background: #f1f0ec; border-radius: 3px; padding: 0 2px; }
pre { background: #1e2228; color: #e6e6e6; border-radius: 6px; padding: 7pt 9pt; font-size: 8.2pt; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 9pt; font-size: 8.4pt; break-inside: auto; }
tr { break-inside: avoid; }
th { background: #e4f3f5; text-align: left; }
th, td { border: 1px solid #d9d8d3; padding: 3pt 5pt; vertical-align: top; }
blockquote { margin: 6pt 0 9pt; padding: 6pt 9pt; background: #fbf3dc; border-left: 3px solid #d8b75e; }
blockquote p:last-child { margin: 0; }
.diagrama { margin: 6pt 0 10pt; break-inside: avoid; }
.diagrama svg { width: 100%; height: auto; }
.tarea { list-style: none; margin-left: -14pt; }
"""

def guia_html():
    t = open(MD, encoding='utf-8').read()
    t = t.replace('<!-- DIAGRAMA -->', f'<div class="diagrama">{diagrama()}</div>')
    cuerpo = markdown.markdown(t, extensions=['tables', 'fenced_code', 'sane_lists'])
    cuerpo = re.sub(r'<li>\[ \]\s*', '<li class="tarea">☐ ', cuerpo)
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{cuerpo}</body></html>'

def main():
    if not CHROMIUM: raise SystemExit('No encuentro Chromium (poné su ruta en la variable CHROMIUM).')
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, 'guia.html'); open(h, 'w', encoding='utf-8').write(guia_html())
        crudo = os.path.join(tmp, 'guia.pdf')
        subprocess.run([CHROMIUM, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--disable-background-networking',
                        '--no-first-run', f'--print-to-pdf={crudo}', 'file://' + h], check=True, capture_output=True)
        d = pymupdf.open(crudo)
        d.set_metadata({'title': 'TPI 4K3 · Guía técnica (grupo 1)', 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': ''})
        d.del_xml_metadata()
        d.save(PDF, garbage=4, deflate=True)
        print(os.path.relpath(PDF, RAIZ), len(d), 'páginas')
    # El ZIP: cada sketch en su carpeta (como lo abre el Arduino IDE) y la guía
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in SKETCHES:
            texto = open(os.path.join(RAIZ, 'practica', 'esp32', 'profe', n), encoding='utf-8').read()
            assert 'TU_' in texto and not re.search(r'API_KEY = "(?!TU_)[A-Z0-9]{8,}"', texto), n
            z.writestr(zipfile.ZipInfo(f'TPI resuelto grupo 1/{n[:-4]}/{n}', (2026, 10, 23, 12, 0, 0)), texto)
        z.writestr(zipfile.ZipInfo('TPI resuelto grupo 1/guia-tecnica-tpi-4k3.md', (2026, 10, 23, 12, 0, 0)), open(MD, encoding='utf-8').read())
    print(os.path.relpath(ZIP, RAIZ))

if __name__ == '__main__':
    main()
