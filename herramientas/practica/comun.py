import os
AQUI = os.path.dirname(os.path.abspath(__file__))
def leer(*p):
    """Lee un archivo de datos (los CSV de cada ejercicio están en datos/)."""
    with open(os.path.join(AQUI, *p), encoding='utf-8', newline='') as f:
        return f.read()
def ej(id, titulo, origen, detalle, enunciado, datos, pasos):
    return dict(id=id, titulo=titulo, origen=origen, detalle=detalle, enunciado=enunciado, datos=datos, pasos=pasos)
def paso(titulo, archivo, hacer, contrato, checks, solucion, inicio=None, pistas=(), ejecutar=None, tambien=()):
    """archivo: el archivo en el que se trabaja; solucion: {archivo: contenido} al terminar el paso."""
    return dict(titulo=titulo, archivo=archivo, tambien=list(tambien), hacer=list(hacer), contrato=list(contrato),
                checks=[dict(d=d, c=c.strip("\n")) for d, c in checks], solucion=solucion, inicio=inicio or {},
                pistas=list(pistas), ejecutar=ejecutar)
def h(t, *p): return dict(k='h', t=t, p=list(p))
def pr(t, *p): return dict(k='p', t=t, p=list(p))
def li(t, *p): return dict(k='li', t=t, p=list(p))
def code(t, *p): return dict(k='code', t=t, p=list(p))
