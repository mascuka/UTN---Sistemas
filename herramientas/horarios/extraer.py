# Arma horarios/2026.json con los horarios de cursado de los PDF de la carrera (uno por año).
# Uso, desde la raíz:  python3 herramientas/horarios/extraer.py horarios_1er.pdf horarios_2do.pdf ...
# Cada PDF trae una tabla por comisión, con el 1º y el 2º cuatrimestre lado a lado, módulos de 45 min
# y una casilla por día con la abreviatura de la materia. Sale, por cuatrimestre:
#   materia (número de la web, o "x:ABR" si la web no la tiene) → comisión → { t: turno, cc: contracuatrimestre, b: [[día, desde, hasta]] }
import json, re, sys
from collections import defaultdict
import pymupdf

# Abreviatura del horario → número de materia en la web (CARRERA.materias y CARRERA.electivas)
NUM = {
    'AMI': 1, 'Algebra': 2, 'AGA': 2, 'Fisica I': 3, 'Ingles': 4, 'LED': 5, 'AED': 6, 'ACO': 7, 'SPN': 8, 'Ing y Soc': 11,
    'AM2': 9, 'FISII': 10, 'Ingles II': 12, 'SSL': 13, 'PPR': 14, 'SOP': 15, 'ASI': 16, 'EST': 17,
    'ECO': 18, 'BDD': 19, 'DS': 20, 'COM': 21, 'CDD': 21, 'AN': 22, 'DSI': 23,
    'LEG': 24, 'ICS': 25, 'RED': 26, 'IOP': 27, 'SIM': 28, 'TPA': 29, 'TA': 29, 'ADSI': 30,
    'IAR': 31, 'IA': 31, 'CD': 32, 'SG': 33, 'GG': 34, 'SSI': 35, 'PROY': 36,
    'BDA': 201, 'GREEN': 202, 'Green': 202, 'GIP': 203, 'GMP': 204, 'Devops': 205, 'DevOps': 205, 'DAO': 206, 'CMD': 207,
    'DTB': 209, 'GEE': 212, 'CON': 213, 'ET': 214, 'DEC': 215, 'TSO': 216, 'SDS': 217, 'IAW': 218, 'SWL': 219,
}
# Electivas que están en los horarios pero no en el plan de la web (se guardan con su nombre)
EXTRAS = {'UIX': 'Experiencia e Interfaces de Usuario', 'HB': 'Habilidades Blandas', 'CDEV': 'Creatividad y Desarrollo de Entornos Virtuales'}
HORA = re.compile(r'^\d{1,2}:\d\d$')
TITULO = re.compile(r'(\d[A-Z]\d+[A-Z]?)\s*-\s*(?:\S+\s+año\s*-\s*)?(\d)\S*\s+(?:[Cc]ontra)?cuatrimestre\s*-\s*Turno\s*([A-Za-zñ]+)', re.S)
min_ = lambda t: int(t.split(':')[0]) * 60 + int(t.split(':')[1])
avisos = []

def claves(celda):
    """Las materias de una casilla: "GMP / GIP" son dos; "DSI Vega" es DSI. Lo que no se reconoce se descarta."""
    if not celda: return []
    # Algunas casillas traen restos de texto girado arriba ("C i\nRED"): vale la línea que se reconoce
    lineas = [re.sub(r'\s+', ' ', x).strip() for x in celda.split('\n') if x.strip()]
    buenas = [x for x in lineas if all(p in NUM or p in EXTRAS or p.split(' ')[0] in NUM for p in re.split(r'\s*/\s*', x) if p)]
    v = (buenas or lineas or [''])[0]
    if not v: return []
    sal = []
    for parte in re.split(r'\s*/\s*', v):
        if not parte: continue
        if parte in NUM: sal.append(NUM[parte]); continue
        if parte in EXTRAS: sal.append('x:' + parte); continue
        p1 = parte.split(' ')[0]
        if p1 in NUM and len(p1) >= 2: sal.append(NUM[p1]); continue
        avisos.append(v)
    return sal

def secciones(filas, i):
    """Dónde arranca cada mitad (1º y 2º cuatrimestre) de la tabla: columnas con dos horas seguidas en la primera fila de datos."""
    mejor = []
    for f in filas[i + 1:i + 7]:
        if any(v and 'cuatrimestre' in v for v in f): break
        ini = [j for j in range(len(f) - 1) if f[j] and f[j + 1] and HORA.match(f[j].strip()) and HORA.match(f[j + 1].strip())]
        if len(ini) > len(mejor): mejor = ini
    return mejor

def leer(pdfs):
    datos = {1: defaultdict(lambda: defaultdict(list)), 2: defaultdict(lambda: defaultdict(list))}
    info = {}
    for ruta in pdfs:
        for pag in pymupdf.open(ruta):
            for t in pag.find_tables().tables:
                filas = t.extract()
                i = 0
                while i < len(filas):
                    titulos = [m for v in filas[i] if v and 'cuatrimestre' in v for m in TITULO.finditer(v)]
                    if not titulos: i += 1; continue
                    ini = secciones(filas, i)
                    if len(ini) != len(titulos):
                        avisos.append(f'{ruta}: {len(titulos)} títulos y {len(ini)} tablas en {[m.group(0) for m in titulos]}'); i += 1; continue
                    sabado = any('Sabado' in (v or '') or 'Sábado' in (v or '') for v in filas[i] + (filas[i + 1] if i + 1 < len(filas) else []))
                    ndias = 6 if sabado else 5
                    j = i + 1
                    while j < len(filas) and not any(v and 'cuatrimestre' in v for v in filas[j]): j += 1
                    for m, c0 in zip(titulos, ini):
                        com, cuatri, turno = m.group(1), int(m.group(2)), m.group(3).capitalize()
                        cc = 'ontracuatrimestre' in m.string[m.end():m.end() + 30] or 'ontracuatrimestre' in m.group(0)
                        anterior = [None] * ndias
                        for f in filas[i + 1:j]:
                            a, b = (f[c0] or '').strip(), (f[c0 + 1] or '').strip()
                            if not (HORA.match(a) and HORA.match(b)):
                                # a veces la hora está solo en la otra mitad de la fila
                                otra = [(f[x].strip(), f[x + 1].strip()) for x in ini if x != c0 and f[x] and f[x + 1] and HORA.match(f[x].strip()) and HORA.match(f[x + 1].strip())]
                                if not otra: continue
                                a, b = otra[0]
                            largo = min_(b) - min_(a)
                            if largo < 30: anterior = [None] * ndias; continue   # recreo
                            for d in range(ndias):
                                k = c0 + 2 + d
                                v = f[k] if k < len(f) else ''
                                if v is None: v = anterior[d]          # casilla unida con la de arriba
                                anterior[d] = v
                                for clave in claves(v):
                                    datos[cuatri][clave][com].append([d, a, b])
                                    info[(cuatri, clave, com)] = (turno, cc)
                    i = j
    # Unir los módulos seguidos de cada día (con hasta 30 min de recreo en el medio)
    sal = {}
    for cuatri, mats in datos.items():
        sal[str(cuatri)] = {}
        for clave, coms in sorted(mats.items(), key=lambda x: str(x[0])):
            sal[str(cuatri)][str(clave)] = {}
            for com, mods in sorted(coms.items()):
                bloques = []
                for d, a, b in sorted(set(map(tuple, mods)), key=lambda x: (x[0], min_(x[1]))):
                    u = bloques[-1] if bloques else None
                    if u and u[0] == d and min_(a) - min_(u[2]) <= 30: u[2] = b if min_(b) > min_(u[2]) else u[2]
                    else: bloques.append([d, a, b])
                turno, cc = info[(cuatri, clave, com)]
                x = {'t': turno, 'b': bloques}
                if cc: x['cc'] = True
                sal[str(cuatri)][str(clave)][com] = x
    return sal

if __name__ == '__main__':
    pdfs = sys.argv[1:]
    if not pdfs: sys.exit(__doc__ or 'Pasá los PDF de horarios.')
    cuatris = leer(pdfs)
    salida = {'ciclo': 2026, 'extras': EXTRAS, 'cuatrimestres': cuatris}
    with open('horarios/2026.json', 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, separators=(',', ':'))
        f.write('\n')
    for c, ms in cuatris.items():
        print(f'{c}º cuatrimestre: {len(ms)} materias, {sum(len(x) for x in ms.values())} comisiones')
    if avisos: print('Sin reconocer:', sorted(set(avisos)))
