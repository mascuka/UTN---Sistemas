# Lo que comparten los generadores de la Práctica de TPA (armar_p1.py, armar_p2.py, armar_p3.py).
# Los valores esperados (variables y respuestas) salen de correr cada solución en el Octave de verdad (octave-cli),
# con las funciones del profe; después validar.js comprueba que el Octave del navegador da lo mismo.
import json, os, re, subprocess, tempfile, textwrap, zipfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MAT = os.path.join(RAIZ, 'material', 'tecnologias-para-la-automatizacion')

def j(s):
    """Código escrito con sangría adentro del .py"""
    return textwrap.dedent(s).strip('\n') + '\n'

def ejemplo(archivo, origen, codigo, lenguaje='octave'):
    """Código de la explicación. Cada línea puede terminar en «n»: es del elemento n de "consta de"."""
    lineas, marcas = [], []
    for i, l in enumerate(j(codigo).rstrip('\n').split('\n'), 1):
        m = re.search(r'«(\d+)»\s*$', l)
        if m:
            g = int(m.group(1)); l = l[:m.start()].rstrip()
            if marcas and marcas[-1][0] == g and marcas[-1][2] == i - 1: marcas[-1][2] = i
            else: marcas.append([g, i, i])
        lineas.append(l)
    return {'archivo': archivo, 'origen': origen, 'codigo': '\n'.join(lineas), 'marcas': marcas, 'lenguaje': lenguaje}

def C(regex, ok, error, tipo='contiene', archivo=None):
    k = {'tipo': tipo, 'regex': regex, 'ok': ok, 'error': error}
    if archivo: k['archivo'] = archivo
    return k

def NO(regex, ok, error, archivo=None):
    return C(regex, ok, error, 'noContiene', archivo)

# ---------- Octave de verdad ----------
_carpetas = None
def _funciones():
    """Las funciones del profe (1º y 2º parcial) en una carpeta temporal, para el addpath"""
    global _carpetas
    if _carpetas: return _carpetas
    tmp = tempfile.mkdtemp(prefix='tpa-')
    for z in ['p1/funciones-octave-1er-parcial.zip', 'p2/funciones-octave-2do-parcial.zip']:
        with zipfile.ZipFile(os.path.join(MAT, z)) as f: f.extractall(tmp)
    # Sin pantalla, octave-cli no puede graficar: los gráficos no hacen nada (solo importan los números)
    mudas = os.path.join(tmp, 'sin-graficos')
    os.makedirs(mudas)
    for n in ['plot', 'plot3', 'figure', 'subplot', 'title', 'xlabel', 'ylabel', 'zlabel', 'grid', 'hold', 'axis', 'view',
              'legend', 'text', 'quiver3', 'line', 'Dibujar_Temporal', 'animar_trayectoria', 'DibujarEjes', 'dibujarOrigen',
              'dibujarSistemasDeEjesCoordenadosDeRobot', 'drawnow', 'pause']:
        open(os.path.join(mudas, n + '.m'), 'w').write(f'function varargout = {n}(varargin)\n  varargout = cell(1, nargout);\nend\n')
    _carpetas = [mudas, os.path.join(tmp, 'funciones-1er-parcial'), os.path.join(tmp, 'funciones-2do-parcial')]
    return _carpetas

def octave(codigo):
    """Corre un script en octave-cli y devuelve (salida, error)"""
    tmp = tempfile.mkdtemp(prefix='tpa-')
    f = os.path.join(tmp, 'script.m')
    open(f, 'w', encoding='utf-8').write(('1;\n' if re.search(r'\bfunction\b', codigo) else '') + codigo + '\n')
    path = "','".join(_funciones())
    r = subprocess.run(['octave-cli', '-q', '--no-window-system', '--eval', f"addpath('{path}'); source('{f}');"],
                       capture_output=True, text=True, timeout=120)
    return r.stdout, (r.stderr.strip() if r.returncode else '')

def _valor(txt):
    """Un valor de mat2str: número, true/false, texto entre comillas o matriz [a b;c d]"""
    t = txt.strip()
    if t in ('true', 'false'): return t == 'true'
    if t.startswith('"'): return t[1:-1]
    num = lambda x: float('nan') if x == 'NaN' else float('inf') if x == 'Inf' else float('-inf') if x == '-Inf' else float(x)
    if not t.startswith('['): return num(t)
    filas = [f.split() for f in t[1:-1].split(';')]
    return [[num(x) for x in f] for f in filas]

def valores(codigo, nombres=(), exprs=()):
    """Corre el código y devuelve el valor de cada variable y de cada expresión (con 17 cifras)"""
    extra = ''.join(f"\nprintf('@@v{i}=%s\\n', mat2str({n}, 17));" for i, n in enumerate(nombres))
    extra += ''.join(f"\nprintf('@@e{i}=%s\\n', mat2str({e}, 17));" for i, e in enumerate(exprs))
    sal, err = octave(codigo + '\n' + extra)
    if err: raise SystemExit(f'Octave dio un error:\n{err}\n--- código ---\n{codigo}')
    vs = dict(re.findall(r'^@@(\w+)=(.*)$', sal, re.M))
    return [_valor(vs[f'v{i}']) for i in range(len(nombres))], [_valor(vs[f'e{i}']) for i in range(len(exprs))], re.sub(r'^@@.*\n?', '', sal, flags=re.M)

def mostrar(v, dec=4):
    """Cómo se muestra una respuesta (como en el campus: con coma)"""
    if isinstance(v, bool): return 'Sí' if v else 'No'
    if isinstance(v, str): return v
    if abs(v - round(v)) < 1e-9: return str(int(round(v)))
    return f'{v:.{dec}f}'.rstrip('0').rstrip('.').replace('.', ',') if dec else str(v)

# ---------- Ejercicios ----------
def oct_ej(id, tema, titulo, consigna, inicial, solucion, vars=(), respuestas=(), pasos=(), pistas=(), checks=(),
           imagen=None, ocultar=None, datos=None, donde=None, archivo='mi_codigo.m', tolvars=1e-3, mensajes=None):
    """Un ejercicio de Octave: se escribe y se corre en el navegador.
    vars: nombres de variables que se comparan con lo que da la solución.
    respuestas: [{pregunta, expr (Octave, después de la solución), dec (decimales: 4), tol (10^-dec), unidad, motivo}]
    o con opciones: [{pregunta, opciones, valor, motivo}]"""
    nombres = list(vars)
    exprs = [r['expr'] for r in respuestas if 'expr' in r]
    vs, es, _ = valores(j(solucion), nombres, exprs)
    mensajes = mensajes or {}
    e = {'id': id, 'tema': tema, 'titulo': titulo, 'tipo': 'octave', 'consigna': consigna}
    if donde: e['donde'] = donde
    if imagen: e['imagen'] = imagen
    if datos: e['datos'] = datos
    if pasos: e['pasos'] = list(pasos)
    if pistas: e['pistas'] = list(pistas)
    e['archivos'] = [{'nombre': archivo, 'inicial': j(inicial), 'solucion': j(solucion)}]
    e['vars'] = []
    for n, v in zip(nombres, vs):
        x = {'nombre': n, 'valor': v, 'tol': tolvars}
        if n in mensajes: x['error'] = mensajes[n]
        e['vars'].append(x)
    if respuestas:
        e['respuestas'] = []
        k = 0
        for r in respuestas:
            x = {kk: vv for kk, vv in r.items() if kk not in ('expr', 'dec')}
            if 'expr' in r:
                x['valor'] = es[k]; k += 1
            if 'opciones' not in x: x.setdefault('tol', 10 ** -r['dec'] if 'dec' in r else 1e-3)
            x['mostrar'] = mostrar(x['valor'], r.get('dec', 4))
            e['respuestas'].append(x)
    if checks: e['checks'] = list(checks)
    if ocultar: e['ocultar'] = list(ocultar)
    return e

def cod_ej(id, tema, titulo, consigna, inicial, solucion, checks, respuestas=(), pasos=(), pistas=(), imagen=None, datos=None,
           donde=None, archivo='sketch.ino', lenguaje='cpp'):
    """Un ejercicio de código que no se corre (C++ de la ESP32): se verifica con los checks (expresiones regulares en el
    código sin comentarios) y, si tiene, las respuestas: [{pregunta, valor, dec, unidad, motivo}] u [{pregunta, opciones, valor}]"""
    e = {'id': id, 'tema': tema, 'titulo': titulo, 'tipo': 'codigo', 'lenguaje': lenguaje, 'consigna': consigna}
    if donde: e['donde'] = donde
    if imagen: e['imagen'] = imagen
    if datos: e['datos'] = datos
    if pasos: e['pasos'] = list(pasos)
    if pistas: e['pistas'] = list(pistas)
    e['archivos'] = [{'nombre': archivo, 'inicial': j(inicial), 'solucion': j(solucion)}]
    e['checks'] = list(checks)
    if respuestas:
        e['respuestas'] = []
        for r in respuestas:
            x = {kk: vv for kk, vv in r.items() if kk != 'dec'}
            if 'opciones' not in x: x.setdefault('tol', 10 ** -r['dec'] if 'dec' in r else 1e-3)
            x['mostrar'] = mostrar(x['valor'], r.get('dec', 4))
            e['respuestas'].append(x)
    return e

def resp_ej(id, tema, titulo, consigna, respuestas, imagen=None, codigo=None, calc=None, pistas=(), datos=None, lenguaje=None):
    """Un ejercicio solo de respuestas (números o una opción). Con calc, los valores salen de correr ese código en Octave:
    cada respuesta con 'expr'. codigo: {nombre, texto} para mirar al costado; si texto es '@salida', es lo que muestra calc."""
    e = {'id': id, 'tema': tema, 'titulo': titulo, 'tipo': 'respuestas', 'consigna': consigna}
    if lenguaje: e['lenguaje'] = lenguaje
    if imagen: e['imagen'] = imagen
    if datos: e['datos'] = datos
    if pistas: e['pistas'] = list(pistas)
    exprs = [r['expr'] for r in respuestas if 'expr' in r]
    salida = ''
    if calc:
        _, es, salida = valores(j(calc), (), exprs)
    k, out = 0, []
    for r in respuestas:
        x = {kk: vv for kk, vv in r.items() if kk not in ('expr', 'dec')}
        if 'expr' in r: x['valor'] = es[k]; k += 1
        if 'opciones' not in x: x.setdefault('tol', 10 ** -r['dec'] if 'dec' in r else 1e-3)
        x['mostrar'] = mostrar(x['valor'], r.get('dec', 4))
        out.append(x)
    e['respuestas'] = out
    if codigo:
        e['codigo'] = {'nombre': codigo['nombre'], 'texto': salida.strip('\n') if codigo['texto'] == '@salida' else j(codigo['texto']).rstrip('\n')}
    return e

def elegir_ej(id, tema, titulo, consigna, opciones, items, pregunta=None, tipo='ubicacion', imagen=None, resumen=None):
    """Una opción por fila (tipo ubicacion: el texto con formato; clasificacion: el texto como código)"""
    e = {'id': id, 'tema': tema, 'titulo': titulo, 'tipo': tipo, 'consigna': consigna, 'opciones': list(opciones),
         'items': [{'texto': t, 'respuesta': r, 'motivo': m} for t, r, m in items]}
    if pregunta: e['pregunta'] = pregunta
    if imagen: e['imagen'] = imagen
    if resumen: e['resumen'] = resumen
    for it in e['items']: assert it['respuesta'] in e['opciones'], it
    return e

def parte(n, id, titulo, pestana, explicacion, leccion, ejercicios):
    for k, e in enumerate(ejercicios, 1):
        e['parte'] = n
    return {'n': n, 'id': id, 'titulo': titulo, 'explicacion': explicacion, 'corto': pestana, 'pestana': pestana, 'leccion': leccion, 'ejercicios': ejercicios}

def guardar(destino, grupo, partes):
    d = {'grupo': grupo, 'partes': partes}
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    json.dump(d, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(destino.replace(RAIZ + '/', ''), '·', len(partes), 'partes,', sum(len(p['ejercicios']) for p in partes), 'ejercicios')
