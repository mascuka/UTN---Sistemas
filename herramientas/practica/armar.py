"""Arma los JSON de la Práctica por partes de DAO (practica/dao-p1/) a partir de ej1.py ... ej5.py.

Cada ejN.py define E = ej(...) con el enunciado, los datos (CSV de datos/) y los pasos.
Uso (desde la raíz del repo):  python3 herramientas/practica/validar.py ej1 ej2 ej3 ej4 ej5  y después  python3 herramientas/practica/armar.py
"""
import json, os, sys, importlib
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
REPO = os.path.abspath(os.path.join(AQUI, '..', '..'))
DEST = os.path.join(REPO, 'practica', 'dao-p1')
os.makedirs(DEST, exist_ok=True)
indice = []
for k, nombre in enumerate(['ej1', 'ej2', 'ej3', 'ej4', 'ej5'], 1):
    E = importlib.import_module(nombre).E
    archivo = f'{k:02d}-{E["id"]}.json'
    with open(os.path.join(DEST, archivo), 'w', encoding='utf-8') as f:
        json.dump(E, f, ensure_ascii=False, separators=(',', ':'))
    indice.append(dict(id=E['id'], titulo=E['titulo'], origen=E['origen'], detalle=E['detalle'], pasos=len(E['pasos']), url=f'practica/dao-p1/{archivo}'))
    print(archivo, os.path.getsize(os.path.join(DEST, archivo)))
print(json.dumps(indice, ensure_ascii=False, indent=1))
