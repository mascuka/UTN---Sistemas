from comun import *
R = 'datos'

S1 = '''from abc import ABC, abstractmethod


class Viaje(ABC):
    def __init__(self, codigo, conductor, destino, pasajeros, precio_base):
        self.codigo = codigo
        self.conductor = conductor
        self.destino = destino
        self.pasajeros = pasajeros
        self.precio_base = precio_base

    @abstractmethod
    def importe_recaudado(self):
        pass
'''
S2 = S1 + '''

class ViajeUrbano(Viaje):
    def importe_recaudado(self):
        return self.pasajeros * self.precio_base


class ViajeInterurbano(Viaje):
    def importe_recaudado(self):
        return self.pasajeros * self.precio_base * 1.10     # el mismo importe + 10 %
'''
S3 = S2 + '''

class Empresa:
    def __init__(self):
        self.viajes = []

    def agregar(self, viaje):
        self.viajes.append(viaje)

    def recaudacion_total(self):
        return sum(v.importe_recaudado() for v in self.viajes)
'''
S4 = S3 + '''
    def pasajeros_por_destino(self):
        conteo = {}
        for v in self.viajes:
            conteo[v.destino] = conteo.get(v.destino, 0) + v.pasajeros
        return conteo
'''
S5 = S4 + '''
    def viaje_con_mas_pasajeros(self):
        if not self.viajes:
            return None
        return max(self.viajes, key=lambda v: v.pasajeros)
'''
S6 = 'import csv\n' + S5 + '''

def leer_viajes(nombre_archivo, empresa):
    with open(nombre_archivo, encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):          # la primera línea son los títulos
            if fila["tipo"] == "1":
                clase = ViajeUrbano
            else:
                clase = ViajeInterurbano
            viaje = clase(int(fila["codigo"]), fila["conductor"], fila["destino"],
                          int(fila["pasajeros"]), float(fila["precio_base"]))
            empresa.agregar(viaje)
'''
S7 = S6 + '''

def main():
    empresa = Empresa()
    leer_viajes("viajes.csv", empresa)
    print("Recaudación total:", round(empresa.recaudacion_total(), 2))
    print("Pasajeros por destino:")
    for destino, cantidad in empresa.pasajeros_por_destino().items():
        print("  ", destino, cantidad)
    mayor = empresa.viaje_con_mas_pasajeros()
    print("Viaje con más pasajeros:", mayor.codigo, mayor.destino, mayor.pasajeros)


if __name__ == "__main__":
    main()
'''
F = 'solucion.py'
I = "from solucion import "
E = ej('transporte-4k3', 'Transporte de pasajeros', 'Parcial tomado · 4K3',
  'Viajes urbanos e interurbanos con su recaudación. Todo va en un solo archivo, solucion.py, como en el parcial.',
  [h('Ejercicio 6 · Transporte de pasajeros'),
   pr('Viaje urbano: pasajeros × precio base.', 2),
   pr('Viaje interurbano: mismo importe + 10 %.', 2),
   pr('Leer viajes.csv. El tipo solo determina qué objeto crear.', 6, 7),
   li('1. Importe mediante polimorfismo.', 1, 2),
   li('2. Recaudación total.', 3, 7),
   li('3. Pasajeros por destino.', 4, 7),
   li('4. Viaje con mayor cantidad de pasajeros.', 5, 7),
   pr('Formato: tipo, codigo, conductor, destino, pasajeros, precio_base. Tipo 1 = urbano; 2 = interurbano.', 6),
   h('El test que te dan (test_viajes.py)', 1, 2),
   code('from solucion import Viaje, ViajeUrbano, ViajeInterurbano\n\ndef test_urbano():\n    x = ViajeUrbano(1, "Ana", "Cordoba", 10, 2000)\n    assert isinstance(x, Viaje)\n    assert x.importe_recaudado() == pytest.approx(20000)\n\ndef test_interurbano():\n    x = ViajeInterurbano(2, "Juan", "Alta Gracia", 10, 2000)\n    assert isinstance(x, Viaje)\n    assert x.importe_recaudado() == pytest.approx(22000)', 1, 2)],
  {'viajes.csv': leer(R, 'viajes.csv')},
  [
  paso('La clase Viaje', F,
    ['Creá la clase abstracta Viaje (hereda de ABC).',
     'En el constructor guardá los cinco datos: codigo, conductor, destino, pasajeros y precio_base.',
     'Declará importe_recaudado() como método abstracto: cada tipo de viaje lo calcula distinto.'],
    ['Viaje(codigo, conductor, destino, pasajeros, precio_base)', 'importe_recaudado()  → abstracto'],
    [('Existe la clase Viaje', 'Viaje = importar("solucion", "Viaje")'),
     ('Viaje es abstracta y importe_recaudado() también', '''
Viaje = importar("solucion", "Viaje")
es_abstracta(Viaje, "importe_recaudado")
lanza(TypeError, lambda: Viaje(1, "Ana", "Cordoba", 10, 2000), "Crear un Viaje directamente (tiene que ser abstracta)")'''),
     ('El constructor guarda los cinco datos', '''
Viaje = importar("solucion", "Viaje")
v = concreta(Viaje, ["importe_recaudado"], 1, "Ana", "Cordoba", 10, 2000)
atributo(v, "codigo", 1); atributo(v, "conductor", "Ana"); atributo(v, "destino", "Cordoba")
atributo(v, "pasajeros", 10); atributo(v, "precio_base", 2000)''')],
    {F: S1},
    inicio={F: 'from abc import ABC, abstractmethod\n\n\nclass Viaje(ABC):\n    # Completá el constructor con los 5 datos y el método abstracto\n    pass\n'},
    pistas=['Para que sea abstracta: class Viaje(ABC): y arriba del método, @abstractmethod.',
            'El constructor: def __init__(self, codigo, conductor, destino, pasajeros, precio_base): y adentro self.codigo = codigo, y así con cada dato.',
            'El método abstracto no hace nada, solo se declara: def importe_recaudado(self): pass']),
  paso('Viaje urbano e interurbano', F,
    ['Agregá, abajo de Viaje, las clases ViajeUrbano y ViajeInterurbano, que heredan de Viaje.',
     'Urbano: el importe es pasajeros × precio base.',
     'Interurbano: el mismo importe + 10 %.',
     'Como no agregan datos, no necesitan constructor propio: usan el de Viaje.'],
    ['ViajeUrbano(codigo, conductor, destino, pasajeros, precio_base)', 'ViajeInterurbano(… los mismos datos)', 'importe_recaudado()  → número'],
    [('ViajeUrbano y ViajeInterurbano heredan de Viaje', '''
Viaje, U, I = importar("solucion", "Viaje", "ViajeUrbano", "ViajeInterurbano")
hereda(U, Viaje); hereda(I, Viaje)'''),
     ('Urbano: 10 pasajeros × $2.000 = $20.000', '''
U = importar("solucion", "ViajeUrbano")
cerca(U(1, "Ana", "Cordoba", 10, 2000).importe_recaudado(), 20000, "El importe del urbano")'''),
     ('Interurbano: lo mismo + 10 % = $22.000', '''
I = importar("solucion", "ViajeInterurbano")
cerca(I(2, "Juan", "Alta Gracia", 10, 2000).importe_recaudado(), 22000, "El importe del interurbano")''')],
    {F: S2},
    pistas=['class ViajeUrbano(Viaje): y adentro solo el método def importe_recaudado(self): return self.pasajeros * self.precio_base',
            'El interurbano es igual pero multiplicado por 1.10.']),
  paso('La empresa y la recaudación total', F,
    ['Creá la clase Empresa: guarda los viajes en una lista, self.viajes, que empieza vacía.',
     'agregar(viaje) suma un viaje a la lista.',
     'recaudacion_total() suma el importe de todos los viajes: cada viaje sabe calcular el suyo (polimorfismo).'],
    ['Empresa()', 'agregar(viaje)', 'recaudacion_total()  → número'],
    [('Empresa empieza con la lista de viajes vacía', '''
Empresa = importar("solucion", "Empresa")
e = Empresa(); atributo(e, "viajes"); igual(len(e.viajes), 0, "La cantidad de viajes al empezar")'''),
     ('agregar() suma el viaje a la lista', '''
Empresa, U = importar("solucion", "Empresa", "ViajeUrbano")
e = Empresa(); v = U(1, "Ana", "Cordoba", 10, 2000); e.agregar(v); e.agregar(U(2, "Bea", "Cordoba", 5, 1000))
igual(len(e.viajes), 2, "La cantidad de viajes después de agregar 2")
assert e.viajes[0] is v, "El primer viaje de la lista tiene que ser el que agregaste primero"'''),
     ('Sin viajes, la recaudación es 0', '''
Empresa = importar("solucion", "Empresa")
cerca(Empresa().recaudacion_total(), 0, "La recaudación sin viajes")'''),
     ('Con un urbano y un interurbano: 20.000 + 22.000', '''
Empresa, U, I = importar("solucion", "Empresa", "ViajeUrbano", "ViajeInterurbano")
e = Empresa(); e.agregar(U(1, "Ana", "Cordoba", 10, 2000)); e.agregar(I(2, "Juan", "Alta Gracia", 10, 2000))
cerca(e.recaudacion_total(), 42000, "La recaudación total")''')],
    {F: S3},
    pistas=['En el constructor: self.viajes = []', 'agregar: self.viajes.append(viaje)',
            'recaudacion_total: un acumulador en un for, o return sum(v.importe_recaudado() for v in self.viajes)']),
  paso('Pasajeros por destino', F,
    ['Agregá a Empresa el método pasajeros_por_destino().',
     'Devuelve un diccionario: cada destino con el total de pasajeros que viajaron ahí.',
     'Si un destino se repite, se suman sus pasajeros.'],
    ['pasajeros_por_destino()  → {destino: pasajeros}'],
    [('Suma los pasajeros de cada destino', '''
Empresa, U, I = importar("solucion", "Empresa", "ViajeUrbano", "ViajeInterurbano")
e = Empresa(); e.agregar(U(1, "A", "Cordoba", 10, 1)); e.agregar(I(2, "B", "Alta Gracia", 7, 1)); e.agregar(U(3, "C", "Cordoba", 5, 1))
igual(e.pasajeros_por_destino(), {"Cordoba": 15, "Alta Gracia": 7}, "Los pasajeros por destino")'''),
     ('Sin viajes devuelve un diccionario vacío', '''
Empresa = importar("solucion", "Empresa")
igual(Empresa().pasajeros_por_destino(), {}, "Sin viajes")''')],
    {F: S4},
    pistas=['Empezá con conteo = {} y recorré self.viajes.',
            'Para sumar sin que falle la primera vez: conteo[v.destino] = conteo.get(v.destino, 0) + v.pasajeros']),
  paso('El viaje con más pasajeros', F,
    ['Agregá a Empresa el método viaje_con_mas_pasajeros().',
     'Devuelve el viaje (el objeto entero) que llevó más pasajeros.',
     'Si no hay viajes, devuelve None.'],
    ['viaje_con_mas_pasajeros()  → un viaje, o None'],
    [('Devuelve el viaje con más pasajeros', '''
Empresa, U, I = importar("solucion", "Empresa", "ViajeUrbano", "ViajeInterurbano")
e = Empresa(); a = U(1, "A", "Cordoba", 10, 1); b = I(2, "B", "Rio Cuarto", 30, 1); c = U(3, "C", "Cordoba", 5, 1)
for v in (a, b, c): e.agregar(v)
r = e.viaje_con_mas_pasajeros()
assert r is b, f"Tenía que devolver el viaje 2 (30 pasajeros) y devolvió {r!r}"'''),
     ('Sin viajes devuelve None', '''
Empresa = importar("solucion", "Empresa")
igual(Empresa().viaje_con_mas_pasajeros(), None, "Sin viajes")''')],
    {F: S5},
    pistas=['max(self.viajes, key=lambda v: v.pasajeros) devuelve el objeto con más pasajeros.',
            'Antes, si la lista está vacía: if not self.viajes: return None']),
  paso('Leer el CSV', F,
    ['Escribí la función leer_viajes(nombre_archivo, empresa), afuera de las clases.',
     'Lee viajes.csv y agrega cada viaje a la empresa. La primera línea son los títulos.',
     'El tipo solo elige la clase: 1 = urbano, 2 = interurbano.',
     'Convertí los números: codigo y pasajeros con int(); precio_base con float().'],
    ['leer_viajes(nombre_archivo, empresa)'],
    [('Lee los 40 viajes del archivo', '''
Empresa, leer = importar("solucion", "Empresa", "leer_viajes")
e = Empresa(); leer("viajes.csv", e)
igual(len(e.viajes), 40, "La cantidad de viajes leídos")'''),
     ('El tipo elige la clase', '''
Empresa, leer, U, I = importar("solucion", "Empresa", "leer_viajes", "ViajeUrbano", "ViajeInterurbano")
e = Empresa(); leer("viajes.csv", e)
assert type(e.viajes[0]) is U, "El primer viaje (tipo 1) tiene que ser un ViajeUrbano"
assert type(e.viajes[1]) is I, "El segundo viaje (tipo 2) tiene que ser un ViajeInterurbano"'''),
     ('Los números quedan convertidos', '''
Empresa, leer = importar("solucion", "Empresa", "leer_viajes")
e = Empresa(); leer("viajes.csv", e); v = e.viajes[0]
igual(v.codigo, 6001, "El código del primer viaje"); igual(v.pasajeros, 12, "Los pasajeros del primer viaje")
cerca(v.precio_base, 1800, "El precio base del primer viaje")'''),
     ('Con todo el archivo, la recaudación da $3.510.745', '''
Empresa, leer = importar("solucion", "Empresa", "leer_viajes")
e = Empresa(); leer("viajes.csv", e)
cerca(e.recaudacion_total(), 3510745, "La recaudación total")''')],
    {F: S6},
    pistas=['Con import csv: for fila in csv.DictReader(archivo): y cada dato es fila["pasajeros"], fila["tipo"]…',
            'DictReader ya usa la primera línea como títulos, no hay que saltearla a mano.',
            'Todo lo que viene del archivo es texto: int(fila["pasajeros"]), float(fila["precio_base"]).']),
  paso('El main', F,
    ['Escribí main(): crea la Empresa, lee viajes.csv con leer_viajes e imprime los resultados.',
     'Imprimí la recaudación total, los pasajeros por destino y el viaje con más pasajeros (código y destino).',
     'Al final del archivo: if __name__ == "__main__": main()'],
    ['main()'],
    [('main() corre sin errores e imprime algo', '''
salida = correr_main("solucion")
assert salida.strip(), "main() no imprime nada"'''),
     ('Muestra la recaudación total', 'aparece(3510745.0, correr_main("solucion"), "la recaudación total")'),
     ('Muestra los pasajeros por destino', '''
s = correr_main("solucion")
aparece("Cordoba", s, "el destino Cordoba"); aparece(306, s, "los 306 pasajeros de Cordoba")'''),
     ('Muestra el viaje con más pasajeros (el 6026)', 'aparece("6026", correr_main("solucion"), "el código del viaje con más pasajeros")')],
    {F: S7}, ejecutar=['solucion', 'main'],
    pistas=['def main(): empresa = Empresa() y después leer_viajes("viajes.csv", empresa).',
            'Para el diccionario: for destino, cantidad in empresa.pasajeros_por_destino().items(): print(destino, cantidad)']),
  ])
