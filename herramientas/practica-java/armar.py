"""Arma los JSON de la Práctica por partes de Backend (practica/bk-p1/) a partir de ej1.py … ej5.py.
Uso (desde la raíz del repo): python3 herramientas/practica-java/validar.py ej1 ej2 ej3 ej4 ej5  y después  python3 herramientas/practica-java/armar.py"""
import importlib, json, os, sys
sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, AQUI)
DEST = os.path.join(REPO, 'practica', 'bk-p1')
os.makedirs(DEST, exist_ok=True)
indice = []
for k, nombre in enumerate(['ej1', 'ej2', 'ej3', 'ej4', 'ej5'], 1):
    E = importlib.import_module(nombre).E
    archivo = f'{k:02d}-{E["id"]}.json'
    with open(os.path.join(DEST, archivo), 'w', encoding='utf-8') as f:
        json.dump(E, f, ensure_ascii=False, separators=(',', ':'))
    indice.append(dict(id=E['id'], titulo=E['titulo'], origen=E['origen'], detalle=E['detalle'], pasos=len(E['pasos']),
                       grupo=E['grupo'], tema=E['tema'], url=f'practica/bk-p1/{archivo}'))
    print(archivo, os.path.getsize(os.path.join(DEST, archivo)))
for x in indice: print(json.dumps(x, ensure_ascii=False) + ',')
