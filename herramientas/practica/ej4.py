from comun import *
R = 'datos'
SUC1 = '''from abc import ABC, abstractmethod


class Sucursal(ABC):
    def __init__(self, numero, superficie, facturacion):
        self.numero = numero
        self.superficie = superficie
        self.facturacion = facturacion

    @abstractmethod
    def resultado_comercial(self):
        pass

    @abstractmethod
    def es_rentable(self):
        pass

    @abstractmethod
    def tipo(self):
        pass

    def indice_rentabilidad(self):
        return self.resultado_comercial() / self.superficie
'''
SUC7 = SUC1 + '''
    def __str__(self):
        return f"{self.numero} {self.tipo()}"
'''
HIPER = '''from sucursal import Sucursal


class Hiper(Sucursal):
    def __init__(self, numero, superficie, facturacion, alquileres):
        super().__init__(numero, superficie, facturacion)
        self.alquileres = alquileres          # lo que cobra por los boxes

    def resultado_comercial(self):
        return self.facturacion + self.alquileres

    def es_rentable(self):
        return self.indice_rentabilidad() > 50

    def tipo(self):
        return 1
'''
SUPER = '''from sucursal import Sucursal


class Super(Sucursal):
    def __init__(self, numero, superficie, facturacion, mayorista):
        super().__init__(numero, superficie, facturacion)
        self.mayorista = mayorista

    def resultado_comercial(self):
        return self.facturacion

    def es_rentable(self):
        if self.mayorista:
            return self.indice_rentabilidad() > 45
        return self.indice_rentabilidad() > 40

    def tipo(self):
        return 2
'''
MINI = '''from sucursal import Sucursal


class Mini(Sucursal):
    def __init__(self, numero, superficie, facturacion, alquiler):
        super().__init__(numero, superficie, facturacion)
        self.alquiler = alquiler              # lo que paga al consorcio

    def resultado_comercial(self):
        return self.facturacion - self.alquiler

    def es_rentable(self):
        return self.indice_rentabilidad() > 35

    def tipo(self):
        return 3
'''
EMP5 = '''class Empresa:
    def __init__(self):
        self.sucursales = []

    def agregar_sucursal(self, sucursal):
        self.sucursales.append(sucursal)

    def suma_ganancia(self):
        return sum(s.resultado_comercial() for s in self.sucursales)
'''
EMP6 = EMP5 + '''
    def cantidad_no_rentables(self):
        return len([s for s in self.sucursales if not s.es_rentable()])
'''
EMP7 = EMP6 + '''
    def local_mas_rentable(self):
        if not self.sucursales:
            return None
        return max(self.sucursales, key=lambda s: s.indice_rentabilidad())
'''
MAIN8 = '''from empresa import Empresa
from hiper import Hiper
from mini import Mini
from super import Super


def leer_sucursales(nombre_archivo, empresa):
    with open(nombre_archivo, encoding="utf-8") as archivo:
        for linea in archivo:                   # sin línea de títulos
            if not linea.strip():
                continue
            tipo, numero, superficie, facturacion, extra = linea.strip().split(",")
            numero, superficie, facturacion = int(numero), int(superficie), float(facturacion)
            if tipo == "1":
                sucursal = Hiper(numero, superficie, facturacion, float(extra))
            elif tipo == "2":
                sucursal = Super(numero, superficie, facturacion, extra == "1")
            else:
                sucursal = Mini(numero, superficie, facturacion, float(extra))
            empresa.agregar_sucursal(sucursal)
'''
MAIN9 = MAIN8 + '''

def main():
    empresa = Empresa()
    leer_sucursales("sucursales.csv", empresa)
    print("Suma de ganancia:", empresa.suma_ganancia())
    print("Locales no rentables:", empresa.cantidad_no_rentables())
    print("Local más rentable (número y tipo):", empresa.local_mas_rentable())


if __name__ == "__main__":
    main()
'''
FIX = '''
H, S, M, Empresa = importar("hiper", "Hiper"), importar("super", "Super"), importar("mini", "Mini"), importar("empresa", "Empresa")
emp = Empresa()
for s in (H(1, 1000, 50000, 30000), H(2, 1000, 20000, 20000), S(3, 1000, 45000, False), S(4, 1000, 44000, False),
          S(5, 1000, 46000, True), S(6, 1000, 45000, True), M(7, 1000, 50000, 10000), M(8, 1000, 40000, 5000)):
    emp.agregar_sucursal(s)
'''
E = ej('el-supermercado', 'El supermercado', 'Modelo de parcial del repositorio',
  'Sucursales hiper, super y mini con su resultado y su rentabilidad. Tres subclases y un índice que depende del tipo.',
  [h('El supermercado'),
   pr('Una cadena de supermercados posee varias sucursales con diferentes características, agrupadas en tres formatos diferentes.', 5),
   li('Hipermercados: además del punto de venta, poseen boxes que cede a comerciantes pequeños a cambio de un alquiler mensual.', 2),
   li('Supermercados tradicionales: en edificaciones propias; algunos tienen un formato más orientado a la venta mayorista.', 3),
   li('Mini: en locales que alquila en plantas bajas de edificios de viviendas, abonando un alquiler mensual al consorcio.', 4),
   pr('De cada sucursal el supermercado registra la superficie en metros cuadrados del salón de ventas y el total facturado en el último mes. Adicionalmente existen dos cálculos relevantes: el resultado comercial y el índice de rentabilidad.', 1),
   pr('El resultado comercial de cada sucursal tipo supermercado es equivalente a la facturación. En los locales de hipermercados se suma el total ganado en concepto de alquileres; en los de modalidad Mini se resta el alquiler abonado al edificio.', 2, 3, 4),
   pr('El índice de rentabilidad es el cociente entre el resultado comercial y la superficie. Un local de hipermercado es rentable si su índice es mayor a 50; uno Mini si es mayor a 35. Los locales tradicionales son rentables si su índice es mayor a 40, pero los mayoristas deben tener un índice mayor a 45.', 1, 2, 3, 4),
   pr('Se necesita un programa que lea del archivo sucursales.csv la lista de todas las sucursales y las almacene en algún objeto (no en la función principal) que ofrezca los siguientes métodos:', 5, 8),
   li('1. Suma de ganancia: total del resultado comercial de todas las sucursales.', 5),
   li('2. Cantidad de locales no rentables: cantidad de sucursales cuyo índice de rentabilidad sea menor al exigido.', 6),
   li('3. Local más rentable: número y tipo de la sucursal cuyo índice de rentabilidad sea el mayor de todos.', 7),
   pr('La función principal debe ingresar los datos desde el archivo de texto y finalizar luego de imprimir el resultado de la ejecución de los tres métodos anteriores.', 9),
   h('Estructura del archivo (sin línea de títulos)', 8),
   li('1. Tipo de sucursal: 1 para hiper, 2 para super y 3 para mini', 8),
   li('2. Número: número sin repetición que identifica cada sucursal', 8),
   li('3. Superficie: número entero con la superficie en metros cuadrados', 8),
   li('4. Facturación: número float, expresada en miles de pesos', 8),
   li('5. Si es hiper, el importe ganado por alquileres; si es super, un 1 si es mayorista y 0 si no; si es Mini, el importe pagado por el alquiler', 8),
   h('Contrato (para los tests)', 1, 2, 3, 4, 5),
   li('Sucursal(numero, superficie, facturacion) · resultado_comercial(), es_rentable(), tipo()', 1),
   li('Hiper(numero, superficie, facturacion, alquileres) · tipo() = 1', 2),
   li('Super(numero, superficie, facturacion, mayorista) · tipo() = 2', 3),
   li('Mini(numero, superficie, facturacion, alquiler) · tipo() = 3', 4),
   li('Empresa() · agregar_sucursal(s), suma_ganancia(), cantidad_no_rentables(), local_mas_rentable()', 5, 6, 7),
   li('str(local) es "número tipo", por ejemplo "1 1"', 7)],
  {'sucursales.csv': leer(R, 'sucursales.csv')},
  [
  paso('La clase Sucursal', 'sucursal.py',
    ['Creá la clase abstracta Sucursal con numero, superficie y facturacion.',
     'resultado_comercial(), es_rentable() y tipo() son abstractos: cada formato los resuelve distinto.',
     'indice_rentabilidad() sí se escribe acá, porque es igual para todas: resultado comercial / superficie.'],
    ['Sucursal(numero, superficie, facturacion)', 'resultado_comercial(), es_rentable(), tipo()  → abstractos', 'indice_rentabilidad()  → resultado / superficie'],
    [('Sucursal es abstracta, con sus tres métodos abstractos', '''
S = importar("sucursal", "Sucursal")
es_abstracta(S, "resultado_comercial", "es_rentable", "tipo")
lanza(TypeError, lambda: S(1, 1000, 50000), "Crear una Sucursal directamente")'''),
     ('El constructor guarda número, superficie y facturación', '''
S = importar("sucursal", "Sucursal")
x = concreta(S, ["resultado_comercial", "es_rentable", "tipo"], 1, 1000, 50000)
atributo(x, "numero", 1); atributo(x, "superficie", 1000); atributo(x, "facturacion", 50000)'''),
     ('indice_rentabilidad() = resultado comercial / superficie', '''
S = importar("sucursal", "Sucursal")
Prueba = type("Prueba", (S,), {"resultado_comercial": lambda self: 80000, "es_rentable": lambda self: True, "tipo": lambda self: 1})
x = Prueba(1, 1000, 50000)
assert hasattr(x, "indice_rentabilidad"), "Falta el método indice_rentabilidad() en Sucursal"
cerca(x.indice_rentabilidad(), 80, "El índice con resultado 80.000 y 1.000 m²")''')],
    {'sucursal.py': SUC1},
    inicio={'sucursal.py': 'from abc import ABC, abstractmethod\n\n\nclass Sucursal(ABC):\n    # Completá: constructor, los 3 métodos abstractos e indice_rentabilidad\n    pass\n'},
    pistas=['Tres métodos con @abstractmethod y pass adentro.',
            'def indice_rentabilidad(self): return self.resultado_comercial() / self.superficie (llama al de cada subclase).']),
  paso('El hipermercado', 'hiper.py',
    ['Hiper agrega los alquileres que cobra por los boxes.',
     'resultado comercial = facturación + alquileres; es rentable si su índice es mayor a 50; tipo() devuelve 1.'],
    ['Hiper(numero, superficie, facturacion, alquileres)', 'tipo()  → 1'],
    [('Hiper hereda de Sucursal', 'hereda(importar("hiper", "Hiper"), importar("sucursal", "Sucursal"))'),
     ('Resultado: 50.000 + 30.000 = 80.000', 'cerca(importar("hiper", "Hiper")(1, 1000, 50000, 30000).resultado_comercial(), 80000, "El resultado del hiper")'),
     ('Rentable solo si el índice es mayor a 50', '''
H = importar("hiper", "Hiper")
igual(H(1, 1000, 50000, 30000).es_rentable(), True, "Con índice 80")
igual(H(2, 1000, 20000, 20000).es_rentable(), False, "Con índice 40")
igual(H(3, 1000, 30000, 20000).es_rentable(), False, "Con índice 50 justo")'''),
     ('tipo() devuelve 1', 'igual(importar("hiper", "Hiper")(1, 1000, 50000, 30000).tipo(), 1, "El tipo del hiper")')],
    {'hiper.py': HIPER},
    inicio={'hiper.py': 'from sucursal import Sucursal\n\n\nclass Hiper(Sucursal):\n    # Completá: constructor (con super), resultado_comercial, es_rentable y tipo\n    pass\n'},
    pistas=['es_rentable: return self.indice_rentabilidad() > 50 (ya lo tenés en Sucursal).']),
  paso('El supermercado tradicional', 'super.py',
    ['Super agrega si es mayorista (True o False).',
     'Su resultado comercial es la facturación.',
     'Es rentable si su índice es mayor a 40; si es mayorista, mayor a 45. tipo() devuelve 2.'],
    ['Super(numero, superficie, facturacion, mayorista)', 'tipo()  → 2'],
    [('Super hereda de Sucursal', 'hereda(importar("super", "Super"), importar("sucursal", "Sucursal"))'),
     ('El resultado es la facturación', 'cerca(importar("super", "Super")(3, 1000, 45000, False).resultado_comercial(), 45000, "El resultado del super")'),
     ('Tradicional: rentable con índice mayor a 40', '''
S = importar("super", "Super")
igual(S(1, 1000, 41000, False).es_rentable(), True, "Tradicional con índice 41"); igual(S(2, 1000, 40000, False).es_rentable(), False, "Tradicional con 40")'''),
     ('Mayorista: rentable con índice mayor a 45', '''
S = importar("super", "Super")
igual(S(1, 1000, 46000, True).es_rentable(), True, "Mayorista con 46"); igual(S(2, 1000, 45000, True).es_rentable(), False, "Mayorista con 45")'''),
     ('tipo() devuelve 2', 'igual(importar("super", "Super")(3, 1000, 45000, False).tipo(), 2, "El tipo del super")')],
    {'super.py': SUPER},
    inicio={'super.py': 'from sucursal import Sucursal\n\n\nclass Super(Sucursal):\n    # Completá: constructor (con super), resultado_comercial, es_rentable y tipo\n    pass\n'},
    pistas=['if self.mayorista: return self.indice_rentabilidad() > 45 y si no, > 40.']),
  paso('El mini', 'mini.py',
    ['Mini agrega el alquiler que paga al consorcio.',
     'resultado comercial = facturación − alquiler; rentable si su índice es mayor a 35; tipo() devuelve 3.'],
    ['Mini(numero, superficie, facturacion, alquiler)', 'tipo()  → 3'],
    [('Mini hereda de Sucursal', 'hereda(importar("mini", "Mini"), importar("sucursal", "Sucursal"))'),
     ('Resultado: 50.000 − 10.000 = 40.000', 'cerca(importar("mini", "Mini")(7, 1000, 50000, 10000).resultado_comercial(), 40000, "El resultado del mini")'),
     ('Rentable solo con índice mayor a 35', '''
M = importar("mini", "Mini")
igual(M(1, 1000, 50000, 10000).es_rentable(), True, "Con índice 40"); igual(M(2, 1000, 40000, 5000).es_rentable(), False, "Con índice 35")'''),
     ('tipo() devuelve 3', 'igual(importar("mini", "Mini")(7, 1000, 50000, 10000).tipo(), 3, "El tipo del mini")')],
    {'mini.py': MINI},
    inicio={'mini.py': 'from sucursal import Sucursal\n\n\nclass Mini(Sucursal):\n    # Completá: constructor (con super), resultado_comercial, es_rentable y tipo\n    pass\n'}),
  paso('La empresa y la suma de ganancia', 'empresa.py',
    ['Empresa guarda las sucursales en una lista, self.sucursales.',
     'agregar_sucursal(s) agrega una; suma_ganancia() suma el resultado comercial de todas.'],
    ['Empresa()', 'agregar_sucursal(sucursal)', 'suma_ganancia()  → número'],
    [('Empieza vacía y la ganancia da 0', '''
Empresa = importar("empresa", "Empresa")
e = Empresa(); atributo(e, "sucursales"); igual(len(e.sucursales), 0, "Al empezar"); cerca(e.suma_ganancia(), 0, "Sin sucursales")'''),
     ('agregar_sucursal() las suma a la lista', FIX + 'igual(len(emp.sucursales), 8, "La cantidad después de agregar 8")'),
     ('suma_ganancia() de las 8 sucursales da 375.000', FIX + 'cerca(emp.suma_ganancia(), 375000, "La suma de ganancia")')],
    {'empresa.py': EMP5},
    inicio={'empresa.py': 'class Empresa:\n    # Completá: la lista, agregar_sucursal y suma_ganancia\n    pass\n'},
    pistas=['return sum(s.resultado_comercial() for s in self.sucursales)']),
  paso('Los locales no rentables', 'empresa.py',
    ['Agregá cantidad_no_rentables(): cuántas sucursales no son rentables.',
     'Cada sucursal ya sabe si es rentable: usá es_rentable() (polimorfismo, sin preguntar el tipo).'],
    ['cantidad_no_rentables()  → entero'],
    [('Hay 3 no rentables: el hiper 2, el super 6 y el mini 8', FIX + 'igual(emp.cantidad_no_rentables(), 3, "Locales no rentables")'),
     ('Sin sucursales da 0', 'igual(importar("empresa", "Empresa")().cantidad_no_rentables(), 0, "Sin sucursales")')],
    {'empresa.py': EMP6},
    pistas=['len([s for s in self.sucursales if not s.es_rentable()])']),
  paso('El local más rentable', 'empresa.py',
    ['Agregá local_mas_rentable(): la sucursal con el mayor índice de rentabilidad (o None si no hay).',
     'El enunciado pide el número y el tipo: agregá en sucursal.py el __str__ que devuelve "número tipo", por ejemplo "1 1".',
     'Este paso usa dos archivos: empresa.py y sucursal.py.'],
    ['local_mas_rentable()  → la sucursal, o None', 'str(sucursal)  → "numero tipo"'],
    [('Es el hiper 1 (índice 80)', FIX + '''
local = emp.local_mas_rentable()
assert local is not None, "Devolvió None"
igual(local.numero, 1, "El número del local más rentable"); igual(local.tipo(), 1, "Su tipo")'''),
     ('str() del local da "número tipo"', FIX + 'igual(str(emp.local_mas_rentable()), "1 1", "str() del local más rentable (en sucursal.py)")'),
     ('Con una sola sucursal, es esa', '''
S, Empresa = importar("super", "Super"), importar("empresa", "Empresa")
e = Empresa(); e.agregar_sucursal(S(15, 100, 40000, False))
igual(e.local_mas_rentable().numero, 15, "Con una sola sucursal"); igual(str(e.local_mas_rentable()), "15 2", "Su str()")'''),
     ('Sin sucursales devuelve None', 'igual(importar("empresa", "Empresa")().local_mas_rentable(), None, "Sin sucursales")')],
    {'empresa.py': EMP7, 'sucursal.py': SUC7}, tambien=['sucursal.py'],
    pistas=['max(self.sucursales, key=lambda s: s.indice_rentabilidad())',
            'En Sucursal: def __str__(self): return f"{self.numero} {self.tipo()}"']),
  paso('Leer el CSV', 'main.py',
    ['En main.py escribí leer_sucursales(nombre_archivo, empresa). No tiene títulos.',
     'Cada línea: tipo, número, superficie, facturación y un dato extra que depende del tipo.',
     'Hiper: el extra son los alquileres (float). Super: un 1 si es mayorista (→ True). Mini: el alquiler (float).'],
    ['leer_sucursales(nombre_archivo, empresa)'],
    [('Lee las 199 sucursales', '''
leer, Empresa = importar("main", "leer_sucursales"), importar("empresa", "Empresa")
e = Empresa(); leer("sucursales.csv", e); igual(len(e.sucursales), 199, "La cantidad de sucursales leídas")'''),
     ('La primera es un hiper con sus datos convertidos', '''
leer, Empresa, H = importar("main", "leer_sucursales"), importar("empresa", "Empresa"), importar("hiper", "Hiper")
e = Empresa(); leer("sucursales.csv", e); s = e.sucursales[0]
assert type(s) is H, "La primera línea (tipo 1) tiene que ser un Hiper"
igual(s.numero, 135, "El número"); igual(s.superficie, 1740, "La superficie")
cerca(s.facturacion, 53200, "La facturación"); cerca(s.alquileres, 238400, "Los alquileres")'''),
     ('El mayorista queda como True o False', '''
leer, Empresa, S = importar("main", "leer_sucursales"), importar("empresa", "Empresa"), importar("super", "Super")
e = Empresa(); leer("sucursales.csv", e)
sups = [s for s in e.sucursales if isinstance(s, S)]
assert sups, "No se creó ningún Super: ¿el tipo 2 crea un Super?"
assert all(s.mayorista in (True, False) for s in sups), "mayorista tiene que ser True o False: extra == \\"1\\""
assert any(s.mayorista for s in sups) and not all(s.mayorista for s in sups), "Tiene que haber supers mayoristas y tradicionales"'''),
     ('Con todo el archivo, la ganancia da −5.602.000', '''
leer, Empresa = importar("main", "leer_sucursales"), importar("empresa", "Empresa")
e = Empresa(); leer("sucursales.csv", e); cerca(e.suma_ganancia(), -5602000, "La suma de ganancia")''')],
    {'main.py': MAIN8},
    inicio={'main.py': 'from empresa import Empresa\nfrom hiper import Hiper\nfrom mini import Mini\nfrom super import Super\n\n\ndef leer_sucursales(nombre_archivo, empresa):\n    # Leé el archivo línea por línea y agregá cada sucursal\n    pass\n'},
    pistas=['tipo, numero, superficie, facturacion, extra = linea.strip().split(",")',
            'Para el super: extra == "1" ya es True o False (el "0" de texto sería verdadero si hacés bool(extra)).']),
  paso('El main', 'main.py',
    ['Escribí main(): crea la Empresa, lee sucursales.csv y muestra la ganancia, los no rentables y el local más rentable.'],
    ['main()'],
    [('main() corre e imprime algo', 'assert correr_main().strip(), "main() no imprime nada"'),
     ('Muestra la suma de ganancia', 'aparece(-5602000.0, correr_main(), "la suma de ganancia")'),
     ('Muestra los 112 locales no rentables', 'aparece(112, correr_main(), "la cantidad de locales no rentables")'),
     ('Muestra el local más rentable (159, tipo 1)', 'aparece("159", correr_main(), "el número del local más rentable")')],
    {'main.py': MAIN9}, ejecutar=['main', 'main']),
  ])
