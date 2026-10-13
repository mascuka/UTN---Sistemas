"""Prueba cada ejercicio con el mismo corrector de la página (practica/corrector.py):
la solución de cada paso tiene que pasar todos los controles y el código de inicio tiene que fallar al menos uno.
Uso (desde la raíz del repo):  python3 herramientas/practica/validar.py ej1 ej2 ej3 ej4 ej5
"""
import os, sys, json, importlib
sys.dont_write_bytecode = True
import tempfile
AQUI = os.path.dirname(os.path.abspath(__file__))
os.environ["PRACTICA_DIR"] = os.path.join(tempfile.gettempdir(), "practica-validar")
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "..", "practica"))
import corrector as runner

def validar(E):
    ok = True
    acum = {}
    for k, p in enumerate(E["pasos"], 1):
        antes = dict(acum)
        for f, c in p["inicio"].items():
            antes.setdefault(f, c)
        acum.update(p["solucion"])
        bien = json.loads(runner.correr({**E["datos"], **acum}, p["checks"], p["ejecutar"]))
        mal = json.loads(runner.correr({**E["datos"], **antes}, p["checks"], False))
        fallan = [r for r in bien.get("res", []) if not r["ok"]]
        if "sintaxis" in bien or fallan:
            ok = False
            print(f"  ✗ paso {k} {p['titulo']}: la solución NO pasa:", bien.get("sintaxis") or fallan)
        n_mal = "sintaxis" in mal or sum(not r["ok"] for r in mal["res"])
        if not n_mal:
            ok = False
            print(f"  ✗ paso {k} {p['titulo']}: sin hacer nada ya pasa todo (los controles no sirven)")
        print(f"  {'✓' if not fallan else '✗'} paso {k}: {p['titulo']} · {len(p['checks'])} controles · sin hacer: {n_mal if n_mal is not True else 'sintaxis'} fallan" + (f"\n      salida: {bien['salida'][:300]!r}" if bien.get('salida') else ''))
    return ok

if __name__ == "__main__":
    tot = True
    for nombre in sys.argv[1:]:
        m = importlib.import_module(nombre)
        print("==", m.E["titulo"])
        tot &= validar(m.E)
    sys.exit(0 if tot else 1)
