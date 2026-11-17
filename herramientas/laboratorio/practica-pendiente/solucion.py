"""Arma la solución propuesta del parcial de práctica «pendiente del tramo»: el proyecto del preenunciado con el Java que
genera el laboratorio (motor.js), los tests nuevos de tests/, los dos CSV y DECISIONES.md.
Uso: python3 -I herramientas/laboratorio/practica-pendiente/solucion.py   (desde la raíz del repo; necesita node)"""
import json
import pathlib
import subprocess
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parents[3]
AQUI = pathlib.Path(__file__).resolve().parent
REC = RAIZ / 'material/backend-de-aplicaciones/p1/parcial/recuperatorio-1'
PREFIJO = '01-modelo-inicial/'
JAVA = 'src/main/java/ar/edu/backend/'
NOMBRE = 'flota-pendiente/'

DECISIONES = """# Decisiones

- Herencia por ancho: VehiculoRuta.desdeCampos es la fábrica; con cinco campos crea un VehiculoRuta y con seis un VehiculoConPendiente, que extiende directamente a VehiculoRuta (se le sacó el final), guarda pendientePromedio y valida su rango (0 a 30) después de super(...).
- El índice de las filas nuevas sale de VehiculoConPendiente.calcularIndiceDesgaste (0.50, 0.30 y 0.20, truncado). Se lo pasa a un constructor protegido de VehiculoRuta para que lo verifique; el constructor público sigue exigiendo la fórmula original, como pide el test existente.
- El parser acepta cinco o seis campos bajo el encabezado nuevo y solo cinco bajo el original, y conserva el orden: ancho, descarte de EN_DEPOSITO y recién después las validaciones. Todo se guarda como VehiculoRuta, así que Flota suma, filtra y agrupa los dos tipos sin cambios.
- El main lee datos/datos-parcial.csv por defecto. Tests nuevos en VehiculoConPendienteTest; pendiente: nada.
"""

GENERAR = """
const fs = require('fs'), M = require(process.argv[1] + '/motor.js');
const orig = JSON.parse(fs.readFileSync(0, 'utf8'));
const cfg = M.normalizar(M.leerEnunciado(fs.readFileSync(process.argv[1] + '/practica-pendiente/enunciado-parcial.md', 'utf8')).cfg);
process.stdout.write(JSON.stringify(M.generar(cfg, orig)));
"""


def main():
    with zipfile.ZipFile(REC / '01-preenunciado.zip') as z:
        proyecto = {i.filename[len(PREFIJO):]: z.read(i).decode('utf-8').replace('\r\n', '\n')
                    for i in z.infolist() if not i.is_dir() and i.filename.startswith(PREFIJO)}
    originales = {r[len(JAVA):]: t for r, t in proyecto.items() if r.startswith(JAVA)}
    gen = json.loads(subprocess.run(['node', '-e', GENERAR, str(AQUI.parent)], input=json.dumps(originales),
                                    capture_output=True, text=True, check=True).stdout)
    for nombre, texto in gen.items():
        proyecto[JAVA + nombre] = texto
    proyecto['src/test/java/ar/edu/backend/VehiculoConPendienteTest.java'] = (AQUI / 'tests/VehiculoConPendienteTest.java').read_text('utf-8')
    proyecto['datos/datos-parcial.csv'] = (REC / 'practica-pendiente/datos-parcial.csv').read_text('utf-8')
    proyecto['DECISIONES.md'] = DECISIONES
    destino = REC / 'practica-pendiente/solucion-propuesta.zip'
    with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as z:
        for ruta in sorted(proyecto):
            info = zipfile.ZipInfo(NOMBRE + ruta, date_time=(2026, 11, 17, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, proyecto[ruta])
    print(destino.relative_to(RAIZ), len(proyecto), 'archivos')


if __name__ == '__main__':
    main()
