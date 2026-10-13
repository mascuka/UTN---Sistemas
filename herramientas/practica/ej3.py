from comun import *
R = 'datos'
INM = '''from abc import ABC, abstractmethod


class Inmueble(ABC):
    def __init__(self, codigo, propietario, superficie, alquiler_base):
        self.codigo = codigo
        self.propietario = propietario
        self.superficie = superficie
        self.alquiler_base = alquiler_base

    @abstractmethod
    def alquiler(self):
        pass
'''
CASA = '''from inmueble import Inmueble


class Casa(Inmueble):
    def __init__(self, codigo, propietario, superficie, alquiler_base, dormitorios, pileta):
        super().__init__(codigo, propietario, superficie, alquiler_base)
        self.dormitorios = dormitorios
        self.pileta = pileta

    def alquiler(self):
        importe = self.alquiler_base + self.dormitorios * 30000
        if self.pileta:
            importe += 100000
        return importe
'''
DEP = '''from inmueble import Inmueble


class Departamento(Inmueble):
    def __init__(self, codigo, propietario, superficie, alquiler_base, expensas, piso):
        super().__init__(codigo, propietario, superficie, alquiler_base)
        self.expensas = expensas
        self.piso = piso

    def alquiler(self):
        importe = self.alquiler_base + self.expensas
        if self.piso < 3:                     # piso inferior al tercero
            importe += 20000
        return importe
'''
I4 = '''from casa import Casa
from departamento import Departamento


class Inmobiliaria:
    def __init__(self):
        self.inmuebles = []

    def agregar(self, inmueble):
        self.inmuebles.append(inmueble)

    def suma_alquileres(self):
        return sum(i.alquiler() for i in self.inmuebles)
'''
I5 = I4 + '''
    def cantidad_casas_premium(self):
        cantidad = 0
        for i in self.inmuebles:
            if isinstance(i, Casa) and i.superficie > 150 and i.dormitorios > 2 and i.pileta:
                cantidad += 1
        return cantidad
'''
I6 = I5 + '''
    def propietario_alquiler_mas_bajo(self):
        menor = None
        for i in self.inmuebles:
            if isinstance(i, Departamento):
                if menor is None or i.alquiler() < menor.alquiler():
                    menor = i
        if menor is None:
            return None
        return menor.propietario
'''
MAIN7 = '''from casa import Casa
from departamento import Departamento
from inmobiliaria import Inmobiliaria


def leer_inmuebles(nombre_archivo, inmobiliaria):
    with open(nombre_archivo, encoding="utf-8") as archivo:
        for linea in archivo:                     # sin línea de títulos
            if not linea.strip():
                continue
            datos = linea.strip().split(",")
            tipo = datos[0]
            codigo = int(datos[1])
            propietario = datos[2]
            alquiler_base = float(datos[3])       # ojo: en el archivo el alquiler va antes que la superficie
            superficie = int(datos[4])
            if tipo == "1":
                inmueble = Casa(codigo, propietario, superficie, alquiler_base, int(datos[5]), datos[6] == "1")
            else:
                inmueble = Departamento(codigo, propietario, superficie, alquiler_base, float(datos[5]), int(datos[6]))
            inmobiliaria.agregar(inmueble)
'''
MAIN8 = MAIN7 + '''

def main():
    inmobiliaria = Inmobiliaria()
    leer_inmuebles("inmuebles.csv", inmobiliaria)
    print("Suma de alquileres:", inmobiliaria.suma_alquileres())
    print("Casas premium:", inmobiliaria.cantidad_casas_premium())
    print("Propietario del alquiler más bajo:", inmobiliaria.propietario_alquiler_mas_bajo())


if __name__ == "__main__":
    main()
'''
FIX = '''
Casa, Depto, Inmobiliaria = importar("casa", "Casa"), importar("departamento", "Departamento"), importar("inmobiliaria", "Inmobiliaria")
inm = Inmobiliaria()
inm.agregar(Casa(1, "ANA", 100, 200000, 3, False))
inm.agregar(Casa(2, "BETO", 160, 150000, 3, True))
inm.agregar(Depto(3, "CARI", 80, 300000, 50000, 5))
inm.agregar(Depto(4, "DIEGO", 70, 250000, 40000, 1))
'''
E = ej('la-inmobiliaria', 'La inmobiliaria', 'Modelo de parcial del repositorio',
  'Casas y departamentos en alquiler. Ojo con el orden de los datos en el archivo.',
  [h('La inmobiliaria'),
   pr('Una inmobiliaria de la ciudad administra una serie de inmuebles disponibles para ser alquilados.', 4),
   pr('De cada inmueble se conoce un código numérico, el nombre del propietario, la superficie de la construcción y el importe base del alquiler mensual.', 1),
   pr('El importe base es asignado por la inmobiliaria en función de las condiciones del mercado, pero el importe definitivo es calculado a partir del importe base y de las características particulares del inmueble.', 1, 2, 3),
   li('En el caso de las casas, al importe base se le adicionan $30.000 por cada dormitorio que posea y $100.000 si posee pileta de natación.', 2),
   li('Los departamentos ven incrementado su importe base en $20.000 si se encuentran en un piso inferior al tercero y se les incorpora el importe de las expensas.', 3),
   pr('Se necesita un programa que lea del archivo inmuebles.csv la lista de todos los inmuebles y los almacene en algún objeto (no en la función principal) que ofrezca los siguientes métodos:', 4, 7),
   li('1. Suma de alquileres: el total a recaudar en concepto de alquileres si todos los inmuebles se encuentran alquilados.', 4),
   li('2. Cantidad de casas premium: la cantidad de casas de más de 150 metros cuadrados, más de 2 dormitorios y que posean pileta.', 5),
   li('3. Propietario del alquiler más bajo: el nombre del propietario del departamento con el alquiler cuyo importe definitivo sea el más bajo.', 6),
   pr('La función principal debe ingresar los datos desde el archivo de texto y finalizar luego de imprimir el resultado de la ejecución de los tres métodos anteriores.', 8),
   h('Estructura del archivo (sin línea de títulos)', 7),
   li('1. Tipo de inmueble: 1 para casas y 2 para departamentos', 7),
   li('2. Código: número sin repetición que identifica cada inmueble', 7),
   li('3. Nombre del propietario', 7), li('4. Alquiler base: número de tipo float', 7),
   li('5. Superficie: número entero expresado en metros cuadrados', 7),
   li('6. Si es una casa, la cantidad de habitaciones; si es un departamento, el importe de las expensas', 7),
   li('7. Si es una casa, un 1 si tiene pileta y 0 si no tiene; si es un departamento, el piso, con 0 para planta baja', 7),
   h('Contrato (para los tests)', 1, 2, 3, 4),
   li('Inmueble(codigo, propietario, superficie, alquiler_base) · alquiler()', 1),
   li('Casa(codigo, propietario, superficie, alquiler_base, dormitorios, pileta) · pileta es booleano', 2),
   li('Departamento(codigo, propietario, superficie, alquiler_base, expensas, piso)', 3),
   li('Inmobiliaria() · agregar(inmueble), suma_alquileres(), cantidad_casas_premium(), propietario_alquiler_mas_bajo()', 4, 5, 6)],
  {'inmuebles.csv': leer(R, 'inmuebles.csv')},
  [
  paso('La clase Inmueble', 'inmueble.py',
    ['Creá la clase abstracta Inmueble con codigo, propietario, superficie y alquiler_base.',
     'alquiler() es abstracto: casas y departamentos lo calculan distinto.'],
    ['Inmueble(codigo, propietario, superficie, alquiler_base)', 'alquiler()  → abstracto'],
    [('Inmueble es abstracta y alquiler() también', '''
I = importar("inmueble", "Inmueble")
es_abstracta(I, "alquiler")
lanza(TypeError, lambda: I(1, "ANA", 100, 200000), "Crear un Inmueble directamente")'''),
     ('El constructor guarda los cuatro datos, en ese orden', '''
I = importar("inmueble", "Inmueble")
x = concreta(I, ["alquiler"], 1, "ANA", 100, 200000)
atributo(x, "codigo", 1); atributo(x, "propietario", "ANA"); atributo(x, "superficie", 100); atributo(x, "alquiler_base", 200000)''')],
    {'inmueble.py': INM},
    inicio={'inmueble.py': 'from abc import ABC, abstractmethod\n\n\nclass Inmueble(ABC):\n    # Completá el constructor y el método abstracto alquiler\n    pass\n'},
    pistas=['def __init__(self, codigo, propietario, superficie, alquiler_base): y un self.dato = dato por cada uno.']),
  paso('La casa', 'casa.py',
    ['Casa hereda de Inmueble y agrega dormitorios y pileta (True o False).',
     'alquiler() = alquiler base + $30.000 por dormitorio + $100.000 si tiene pileta.'],
    ['Casa(codigo, propietario, superficie, alquiler_base, dormitorios, pileta)', 'alquiler()  → número'],
    [('Casa hereda de Inmueble', 'hereda(importar("casa", "Casa"), importar("inmueble", "Inmueble"))'),
     ('Sin pileta: 200.000 + 3 × 30.000 = 290.000', '''
Casa = importar("casa", "Casa")
c = Casa(1, "ANA", 100, 200000, 3, False)
atributo(c, "dormitorios", 3); atributo(c, "pileta", False); atributo(c, "superficie", 100)
cerca(c.alquiler(), 290000, "El alquiler de la casa sin pileta")'''),
     ('Con pileta: 150.000 + 3 × 30.000 + 100.000 = 340.000', '''
Casa = importar("casa", "Casa")
cerca(Casa(2, "BETO", 160, 150000, 3, True).alquiler(), 340000, "El alquiler de la casa con pileta")''')],
    {'casa.py': CASA},
    inicio={'casa.py': 'from inmueble import Inmueble\n\n\nclass Casa(Inmueble):\n    # Completá: constructor (con super) y alquiler\n    pass\n'},
    pistas=['super().__init__(codigo, propietario, superficie, alquiler_base) y después los dos datos propios.',
            'importe = self.alquiler_base + self.dormitorios * 30000 y if self.pileta: importe += 100000']),
  paso('El departamento', 'departamento.py',
    ['Departamento hereda de Inmueble y agrega expensas y piso.',
     'alquiler() = alquiler base + expensas, + $20.000 si está en un piso inferior al tercero (0, 1 o 2).'],
    ['Departamento(codigo, propietario, superficie, alquiler_base, expensas, piso)', 'alquiler()  → número'],
    [('Departamento hereda de Inmueble', 'hereda(importar("departamento", "Departamento"), importar("inmueble", "Inmueble"))'),
     ('Piso 1: 250.000 + 20.000 + 40.000 = 310.000', '''
D = importar("departamento", "Departamento")
d = D(4, "DIEGO", 70, 250000, 40000, 1)
atributo(d, "expensas", 40000); atributo(d, "piso", 1)
cerca(d.alquiler(), 310000, "El alquiler en el piso 1")'''),
     ('Planta baja (piso 0) también suma los $20.000', '''
D = importar("departamento", "Departamento")
cerca(D(5, "EDITA", 60, 180000, 30000, 0).alquiler(), 230000, "El alquiler en planta baja")'''),
     ('Piso 3: ya no suma los $20.000', '''
D = importar("departamento", "Departamento")
cerca(D(6, "FEDE", 90, 220000, 35000, 3).alquiler(), 255000, "El alquiler en el piso 3")''')],
    {'departamento.py': DEP},
    inicio={'departamento.py': 'from inmueble import Inmueble\n\n\nclass Departamento(Inmueble):\n    # Completá: constructor (con super) y alquiler\n    pass\n'},
    pistas=['"Inferior al tercero" es piso < 3: el piso 3 ya no suma.']),
  paso('La inmobiliaria y la suma de alquileres', 'inmobiliaria.py',
    ['Inmobiliaria guarda los inmuebles en una lista, self.inmuebles.',
     'agregar(inmueble) agrega uno; suma_alquileres() suma el alquiler de todos.'],
    ['Inmobiliaria()', 'agregar(inmueble)', 'suma_alquileres()  → número'],
    [('Empieza vacía y la suma da 0', '''
Inm = importar("inmobiliaria", "Inmobiliaria")
x = Inm(); atributo(x, "inmuebles"); igual(len(x.inmuebles), 0, "Al empezar"); cerca(x.suma_alquileres(), 0, "La suma sin inmuebles")'''),
     ('agregar() los suma a la lista', FIX + 'igual(len(inm.inmuebles), 4, "La cantidad después de agregar 4")'),
     ('suma_alquileres(): 290.000 + 340.000 + 350.000 + 310.000', FIX + 'cerca(inm.suma_alquileres(), 1290000, "La suma de alquileres")')],
    {'inmobiliaria.py': I4},
    inicio={'inmobiliaria.py': 'from casa import Casa\nfrom departamento import Departamento\n\n\nclass Inmobiliaria:\n    # Completá: la lista, agregar y suma_alquileres\n    pass\n'},
    pistas=['return sum(i.alquiler() for i in self.inmuebles)']),
  paso('Las casas premium', 'inmobiliaria.py',
    ['Agregá cantidad_casas_premium(): casas de más de 150 m², más de 2 dormitorios y con pileta.',
     'Las tres condiciones a la vez, y solo casas (isinstance(i, Casa)).'],
    ['cantidad_casas_premium()  → entero'],
    [('Cuenta solo la casa de BETO', FIX + 'igual(inm.cantidad_casas_premium(), 1, "Casas premium")'),
     ('150 m² justos no alcanzan (tiene que ser más de 150)', '''
Casa, Inm = importar("casa", "Casa"), importar("inmobiliaria", "Inmobiliaria")
x = Inm(); x.agregar(Casa(1, "GABO", 150, 200000, 4, True)); x.agregar(Casa(2, "HUGO", 120, 200000, 3, True))
igual(x.cantidad_casas_premium(), 0, "Con 150 y 120 m²")'''),
     ('2 dormitorios no alcanzan, y sin pileta no cuenta', '''
Casa, Inm = importar("casa", "Casa"), importar("inmobiliaria", "Inmobiliaria")
x = Inm(); x.agregar(Casa(1, "INES", 200, 200000, 2, True)); x.agregar(Casa(2, "ANA", 180, 200000, 3, False))
igual(x.cantidad_casas_premium(), 0, "Con 2 dormitorios / sin pileta")'''),
     ('Un departamento grande no es una casa premium', '''
D, Inm = importar("departamento", "Departamento"), importar("inmobiliaria", "Inmobiliaria")
x = Inm(); x.agregar(D(1, "JORGE", 200, 200000, 30000, 1))
igual(x.cantidad_casas_premium(), 0, "Con solo un departamento")''')],
    {'inmobiliaria.py': I5},
    pistas=['if isinstance(i, Casa) and i.superficie > 150 and i.dormitorios > 2 and i.pileta:']),
  paso('El propietario del alquiler más bajo', 'inmobiliaria.py',
    ['Agregá propietario_alquiler_mas_bajo(): de los departamentos, el nombre del propietario del que tiene el alquiler más bajo.',
     'Solo departamentos: una casa más barata no cuenta. Si no hay departamentos, devolvé None.'],
    ['propietario_alquiler_mas_bajo()  → nombre, o None'],
    [('Es DIEGO (310.000)', FIX + 'igual(inm.propietario_alquiler_mas_bajo(), "DIEGO", "El propietario del alquiler más bajo")'),
     ('Solo mira los departamentos', '''
Casa, D, Inm = importar("casa", "Casa"), importar("departamento", "Departamento"), importar("inmobiliaria", "Inmobiliaria")
x = Inm(); x.agregar(Casa(1, "UNA CASA BARATA", 80, 50000, 1, False)); x.agregar(D(2, "EL DEPTO MAS CARO", 80, 900000, 100000, 3))
igual(x.propietario_alquiler_mas_bajo(), "EL DEPTO MAS CARO", "Con una casa barata y un depto")'''),
     ('Sin departamentos devuelve None', '''
Casa, Inm = importar("casa", "Casa"), importar("inmobiliaria", "Inmobiliaria")
x = Inm(); x.agregar(Casa(1, "KIKA", 100, 200000, 3, False))
igual(x.propietario_alquiler_mas_bajo(), None, "Sin departamentos")''')],
    {'inmobiliaria.py': I6},
    pistas=['Filtrá: deptos = [i for i in self.inmuebles if isinstance(i, Departamento)]',
            'Si la lista está vacía, None; si no, min(deptos, key=lambda d: d.alquiler()).propietario']),
  paso('Leer el CSV', 'main.py',
    ['En main.py escribí leer_inmuebles(nombre_archivo, inmobiliaria).',
     'No tiene títulos. Separá cada línea con split(",") y fijate el orden: el alquiler base viene ANTES que la superficie.',
     'Casa: el dato 6 son los dormitorios (int) y el 7 la pileta (1 → True, 0 → False). Departamento: expensas (float) y piso (int).'],
    ['leer_inmuebles(nombre_archivo, inmobiliaria)'],
    [('Lee los 200 inmuebles', '''
leer, Inm = importar("main", "leer_inmuebles"), importar("inmobiliaria", "Inmobiliaria")
x = Inm(); leer("inmuebles.csv", x); igual(len(x.inmuebles), 200, "La cantidad de inmuebles leídos")'''),
     ('La primera línea es una casa, con cada dato en su lugar', '''
leer, Inm, Casa = importar("main", "leer_inmuebles"), importar("inmobiliaria", "Inmobiliaria"), importar("casa", "Casa")
x = Inm(); leer("inmuebles.csv", x); c = x.inmuebles[0]
assert type(c) is Casa, "La primera línea (tipo 1) tiene que ser una Casa"
igual(c.codigo, 266, "El código"); igual(c.propietario, "PILAR CALVO", "El propietario")
cerca(c.superficie, 90, "La superficie (¿la cambiaste con el alquiler?)"); cerca(c.alquiler_base, 373000, "El alquiler base")
igual(c.dormitorios, 5, "Los dormitorios"); assert c.pileta in (False, 0), f"La pileta tenía que ser False y es {c.pileta!r}"'''),
     ('La segunda es un departamento', '''
leer, Inm, D = importar("main", "leer_inmuebles"), importar("inmobiliaria", "Inmobiliaria"), importar("departamento", "Departamento")
x = Inm(); leer("inmuebles.csv", x); d = x.inmuebles[1]
assert type(d) is D, "La segunda línea (tipo 2) tiene que ser un Departamento"
cerca(d.expensas, 18370, "Las expensas"); igual(d.piso, 3, "El piso")'''),
     ('La pileta queda como booleano (el "0" de texto sería verdadero)', '''
leer, Inm, Casa = importar("main", "leer_inmuebles"), importar("inmobiliaria", "Inmobiliaria"), importar("casa", "Casa")
x = Inm(); leer("inmuebles.csv", x)
assert all(c.pileta in (True, False) for c in x.inmuebles if isinstance(c, Casa)), "La pileta tiene que ser True o False: datos[6] == \\"1\\""'''),
     ('Con todo el archivo, la suma de alquileres da $78.832.240', '''
leer, Inm = importar("main", "leer_inmuebles"), importar("inmobiliaria", "Inmobiliaria")
x = Inm(); leer("inmuebles.csv", x); cerca(x.suma_alquileres(), 78832240, "La suma de alquileres")''')],
    {'main.py': MAIN7},
    inicio={'main.py': 'from casa import Casa\nfrom departamento import Departamento\nfrom inmobiliaria import Inmobiliaria\n\n\ndef leer_inmuebles(nombre_archivo, inmobiliaria):\n    # Leé el archivo línea por línea y agregá cada inmueble\n    pass\n'},
    pistas=['datos = linea.strip().split(",") y después datos[0] es el tipo, datos[1] el código…',
            'superficie = int(datos[4]) y alquiler_base = float(datos[3]): al constructor van en el orden del contrato.',
            'Para la pileta: datos[6] == "1" ya es True o False.']),
  paso('El main', 'main.py',
    ['Escribí main(): crea la Inmobiliaria, lee inmuebles.csv y muestra los tres resultados.'],
    ['main()'],
    [('main() corre e imprime algo', 'assert correr_main().strip(), "main() no imprime nada"'),
     ('Muestra la suma de alquileres', 'aparece(78832240.0, correr_main(), "la suma de alquileres")'),
     ('Muestra las 11 casas premium', 'aparece(11, correr_main(), "la cantidad de casas premium")'),
     ('Muestra el propietario del alquiler más bajo', 'aparece("MARIA JOSE ESTEBAN", correr_main(), "el propietario del alquiler más bajo")')],
    {'main.py': MAIN8}, ejecutar=['main', 'main']),
  ])
