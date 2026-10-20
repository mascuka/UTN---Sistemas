# Revisa los ejercicios de "El parcial por partes" (practica/bk-parcial/ejercicios.json). Desde la raíz del repo:
#   python3 herramientas/parcial-por-partes/validar.py
# 1) Código: la solución pasa todas sus verificaciones y el código inicial no (las mismas reglas que la página:
#    sin comentarios, y un check sin "archivo" mira todos los archivos que se pueden editar).
# 2) Los que tienen "proyecto" (código real de un parcial): el inicial y la solución compilan con javac sobre ese
#    proyecto (sacado del ZIP del preenunciado), y pruebas/<id>/Prueba.java corre contra la solución e imprime OK.
#    pruebas/<id>/base/ son los archivos de otras partes que ese ejercicio da por hechos.
#    Los que tienen "compilar": "solo" se compilan solos (con los imports de java.util).
# 3) Clasificación con pruebas/<id>/: se corre la solución completa del parcial con esas filas y tiene que dar las
#    mismas respuestas.
# Necesita el JDK 21 (javac y java).
import json, os, re, shutil, subprocess, sys, tempfile, zipfile
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PRUEBAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pruebas')
PAR = os.path.join(RAIZ, 'material', 'backend-de-aplicaciones', 'p1', 'parcial')
PROYECTOS = {   # ZIP del preenunciado y la carpeta del proyecto adentro
    'cc': ('parcial-3k1/01-preenunciado.zip', '01-modelo-inicial'),
    'fin': ('simulacros/simulacro-1.zip', 'fintech'),
    'tal': ('simulacros/simulacro-2.zip', '01-modelo-inicial'),
    'jue': ('simulacros/simulacro-3.zip', '01-modelo-inicial'),
    'tar': ('simulacros/simulacro-4/01-preenunciado.zip', '01-preenunciado'),
}
IMPORTS = 'import java.util.*;\nimport java.util.function.*;\nimport java.util.stream.*;\n'

def sin_comentarios(c):
    out, i, en = [], 0, None
    while i < len(c):
        ch, dos = c[i], c[i:i + 2]
        if en:
            out.append(ch)
            if ch == '\\': out.append(c[i + 1:i + 2]); i += 2; continue
            if ch == en or ch == '\n': en = None
            i += 1; continue
        if ch in '"\'': en = ch; out.append(ch); i += 1; continue
        if dos == '//':
            while i < len(c) and c[i] != '\n': i += 1
            continue
        if dos == '/*':
            f = c.find('*/', i + 2); i = len(c) if f < 0 else f + 2; continue
        out.append(ch); i += 1
    return ''.join(out)

def verificar(archivos, checks, texto=False):
    res = []
    for k in checks:
        if k.get('archivo'): t = archivos.get(k['archivo'], '')
        else: t = '\n'.join(archivos.values())
        if not texto: t = sin_comentarios(t)
        if k['tipo'] == 'lineas':
            n = len([l for l in t.split('\n') if l.strip()]); ok = k['min'] <= n <= k['max']
        else:
            fl = (re.I if 'i' in k.get('flags', '') else 0) | (re.S if 's' in k.get('flags', '') else 0)
            n = len(re.findall(k['regex'], t, fl))
            ok = n == 0 if k['tipo'] == 'noContiene' else n == k['veces'] if k['tipo'] == 'cuenta' else n > 0
        res.append((ok, k['ok'] if ok else k['error']))
    return res

def proyecto(clave, tmp):
    z, carpeta = PROYECTOS[clave]
    with zipfile.ZipFile(os.path.join(PAR, z)) as f: f.extractall(tmp)
    for raiz, dirs, archivos in os.walk(tmp):
        if os.path.basename(raiz) == carpeta and os.path.isdir(os.path.join(raiz, 'src', 'main', 'java')):
            fuentes = os.path.join(raiz, 'src', 'main', 'java')
            for r, _, fs in os.walk(fuentes):
                if any(x.endswith('.java') for x in fs): return raiz, r
    raise SystemExit('No encontré el proyecto ' + clave)

def compilar(archivos_java, salida):
    r = subprocess.run(['javac', '-encoding', 'UTF-8', '-nowarn', '-d', salida, *archivos_java], capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()

def armar(ej, cual, prueba):
    """Copia el proyecto, pone los archivos del ejercicio (inicial o solución) y compila. Devuelve (ok, msg, salida, paquete)."""
    tmp = tempfile.mkdtemp(prefix='pp-')
    raiz, pkg = proyecto(ej['proyecto'], tmp)
    base = os.path.join(PRUEBAS, ej['id'], 'base')
    if os.path.isdir(base):
        for n in os.listdir(base): shutil.copy(os.path.join(base, n), os.path.join(pkg, n))
    for a in ej.get('archivos', []):
        texto = a['inicial'] if a.get('soloLectura') or cual == 'inicial' else a['solucion']
        open(os.path.join(pkg, a['nombre']), 'w', encoding='utf-8').write(texto)
    if prueba: shutil.copy(os.path.join(PRUEBAS, ej['id'], 'Prueba.java'), os.path.join(pkg, 'Prueba.java'))
    fuentes = [os.path.join(r, f) for r, _, fs in os.walk(os.path.join(raiz, 'src', 'main', 'java')) for f in fs if f.endswith('.java')]
    salida = os.path.join(tmp, 'clases')
    ok, msg = compilar(fuentes, salida)
    paquete = re.search(r'^package\s+([\w.]+);', open(fuentes[0], encoding='utf-8').read(), re.M).group(1)
    return ok, msg, salida, paquete

def correr(salida, paquete, *args):
    r = subprocess.run(['java', '-cp', salida, paquete + '.Prueba', *args], capture_output=True, text=True, timeout=60)
    err = '\n'.join(l for l in r.stderr.splitlines() if not l.startswith('Picked up JAVA_TOOL_OPTIONS'))
    return (r.stdout + err).strip()

def main():
    d = json.load(open(os.path.join(RAIZ, 'practica', 'bk-parcial', 'ejercicios.json'), encoding='utf-8'))
    mal = 0
    for p in d['partes']:
        for e in p['ejercicios']:
            notas = []
            if e['tipo'] == 'codigo':
                edit = [a for a in e['archivos'] if not a.get('soloLectura')]
                sol = {a['nombre']: a['solucion'] for a in edit}
                ini = {a['nombre']: a['inicial'] for a in edit}
                rs, ri = verificar(sol, e['checks']), verificar(ini, e['checks'])
                fallan = [m for ok, m in rs if not ok]
                if fallan: mal += 1; notas.append('✗ la solución no pasa: ' + ' | '.join(fallan))
                if all(ok for ok, _ in ri): mal += 1; notas.append('✗ el inicial pasa todo')
                notas.append(f'solución {len(rs) - len(fallan)}/{len(rs)} · inicial {sum(ok for ok, _ in ri)}/{len(ri)}')
                for k in e['checks']:
                    if k.get('archivo') and k['archivo'] not in sol:
                        mal += 1; notas.append('✗ check con un archivo que no se puede editar: ' + k['archivo'])
                if e.get('proyecto'):
                    hay = os.path.isfile(os.path.join(PRUEBAS, e['id'], 'Prueba.java'))
                    ok, msg, _, _ = armar(e, 'inicial', False)
                    if not ok: mal += 1; notas.append('✗ el inicial no compila:\n' + msg[:1500])
                    ok, msg, salida, paquete = armar(e, 'solucion', hay)
                    if not ok: mal += 1; notas.append('✗ la solución no compila:\n' + msg[:1500])
                    elif hay:
                        out = correr(salida, paquete)
                        if out.splitlines()[-1:] != ['OK']: mal += 1; notas.append('✗ la prueba falla:\n' + out[:1500])
                        else: notas.append('compila y la prueba da OK')
                    else: notas.append('compila')
                elif e.get('compilar') == 'solo':
                    for cual in ('inicial', 'solucion'):
                        tmp = tempfile.mkdtemp(prefix='pp-')
                        fs = []
                        for a in e['archivos']:
                            t = a['inicial'] if cual == 'inicial' or a.get('soloLectura') else a['solucion']
                            if 'import ' not in t and 'package ' not in t: t = IMPORTS + t
                            f = os.path.join(tmp, a['nombre']); open(f, 'w', encoding='utf-8').write(t); fs.append(f)
                        ok, msg = compilar(fs, os.path.join(tmp, 'clases'))
                        if not ok: mal += 1; notas.append(f'✗ {cual} no compila:\n' + msg[:1500])
                    notas.append('compila solo')
            elif e['tipo'] == 'texto':
                rs = verificar({'t': e['solucion']}, e['checks'], texto=True)
                if not all(ok for ok, _ in rs): mal += 1; notas.append('✗ el ejemplo no pasa')
            elif e['tipo'] == 'clasificacion' and os.path.isfile(os.path.join(PRUEBAS, e['id'], 'Prueba.java')):
                ok, msg, salida, paquete = armar({**e, 'archivos': []}, 'solucion', True)
                if not ok: mal += 1; notas.append('✗ no compila:\n' + msg[:1500])
                else:
                    out = correr(salida, paquete, '|'.join([e['cabecera'], *[i['texto'] for i in e['items']]]))
                    esperado = ','.join(i['respuesta'] for i in e['items'])
                    if out != esperado:
                        mal += 1; notas.append('✗ las respuestas no coinciden con el proyecto:\n  da       ' + out + '\n  esperado ' + esperado)
                    else: notas.append('las respuestas coinciden con la solución del parcial')
            if e['tipo'] in ('ubicacion', 'clasificacion'):
                for i in e['items']:
                    if i['respuesta'] not in e['opciones']: mal += 1; notas.append('✗ respuesta fuera de las opciones: ' + i['respuesta'])
            print(f"{e['id']:<4} {e['tipo']:<13} " + ' · '.join(notas))
    print('\n' + (f'{mal} PROBLEMAS' if mal else 'TODO BIEN'))
    sys.exit(1 if mal else 0)

if __name__ == '__main__':
    main()
