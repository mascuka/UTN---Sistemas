"""Arma la solución propuesta de un parcial de práctica (practica-xxx): el proyecto del preenunciado con el Java (marcado) que
genera el laboratorio (motor.js) a partir de su enunciado, los tests de practica-xxx/tests/, los dos CSV y su DECISIONES.md.
Uso (desde la raíz del repo; necesita node):  python3 -I herramientas/laboratorio/practica-solucion.py practica-acoplado"""
import json
import pathlib
import subprocess
import sys
import zipfile

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
REC = RAIZ / 'material/backend-de-aplicaciones/p1/parcial/recuperatorio-1'
PREFIJO = '01-modelo-inicial/'
JAVA = 'src/main/java/ar/edu/backend/'

GENERAR = """
const fs = require('fs'), M = require(process.argv[1] + '/motor.js');
const orig = JSON.parse(fs.readFileSync(0, 'utf8'));
const cfg = M.normalizar(M.leerEnunciado(fs.readFileSync(process.argv[2], 'utf8')).cfg);
const gen = M.generar(cfg, orig);
for (const f of Object.keys(gen)) gen[f] = M.marcarCambios(orig[f], gen[f]);   // con «// NUEVO», «// MOD», «// ANTES»
process.stdout.write(JSON.stringify(gen));
"""


def main(carpeta):
    practica = AQUI / carpeta
    with zipfile.ZipFile(REC / '01-preenunciado.zip') as z:
        proyecto = {i.filename[len(PREFIJO):]: z.read(i).decode('utf-8').replace('\r\n', '\n')
                    for i in z.infolist() if not i.is_dir() and i.filename.startswith(PREFIJO)}
    originales = {r[len(JAVA):]: t for r, t in proyecto.items() if r.startswith(JAVA)}
    gen = json.loads(subprocess.run(['node', '-e', GENERAR, str(AQUI), str(practica / 'enunciado-parcial.md')],
                                    input=json.dumps(originales), capture_output=True, text=True, check=True).stdout)
    for nombre, texto in gen.items():
        proyecto[JAVA + nombre] = texto
    for test in sorted((practica / 'tests').glob('*.java')):
        proyecto['src/test/java/ar/edu/backend/' + test.name] = test.read_text('utf-8')
    proyecto['datos/datos-parcial.csv'] = (REC / carpeta / 'datos-parcial.csv').read_text('utf-8')
    proyecto['DECISIONES.md'] = (practica / 'DECISIONES.md').read_text('utf-8')
    destino = REC / carpeta / 'solucion-propuesta.zip'
    raiz = 'flota-' + carpeta.removeprefix('practica-') + '/'
    with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as z:
        for ruta in sorted(proyecto):
            info = zipfile.ZipInfo(raiz + ruta, date_time=(2026, 11, 17, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, proyecto[ruta])
    print(destino.relative_to(RAIZ), len(proyecto), 'archivos ·', ', '.join(sorted(gen)))


if __name__ == '__main__':
    main(sys.argv[1])
