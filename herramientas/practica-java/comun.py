"""Ayudas para escribir los ejercicios de la Práctica por partes en Java (Backend).
Cada ejercicio (ej1.py, ej2.py…) define E = ej(...). validar.py los prueba con el JDK y armar.py los pasa a JSON."""
import os
AQUI = os.path.dirname(os.path.abspath(__file__))


def leer(*p):
    with open(os.path.join(AQUI, *p), encoding="utf-8", newline="") as f:
        return f.read()


def ej(id, titulo, origen, detalle, enunciado, datos, pasos, importar=(), grupo=None, tema=None):
    return dict(id=id, titulo=titulo, origen=origen, detalle=detalle, lenguaje="java", importar=list(importar),
                grupo=grupo, tema=tema, enunciado=enunciado, datos=datos, pasos=pasos)


def paso(titulo, archivo, hacer, contrato, checks, solucion, inicio=None, pistas=(), ejecutar=None, tambien=()):
    """archivo: donde se trabaja (ruta con paquete); solucion: {archivo: contenido} al terminar el paso.
    checks: [(descripción, código Java)]; el código va dentro de un lambda y usa Prueba.igual/lanza/…"""
    return dict(titulo=titulo, archivo=archivo, tambien=list(tambien), hacer=list(hacer), contrato=list(contrato),
                checks=[dict(d=d, c=c.strip("\n")) for d, c in checks], solucion=solucion, inicio=inicio or {},
                pistas=list(pistas), ejecutar=ejecutar)


def h(t, *p): return dict(k="h", t=t, p=list(p))
def pr(t, *p): return dict(k="p", t=t, p=list(p))
def li(t, *p): return dict(k="li", t=t, p=list(p))
def code(t, *p): return dict(k="code", t=t, p=list(p))
