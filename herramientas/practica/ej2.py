from comun import *
R = 'datos'
MANT = '''from abc import ABC, abstractmethod


class Mantenimiento(ABC):
    def __init__(self, fecha, operario, repuestos):
        self.fecha = fecha
        self.operario = operario
        self.repuestos = repuestos

    @abstractmethod
    def gasto_total(self):
        pass
'''
PREV = '''from mantenimiento import Mantenimiento


class Preventivo(Mantenimiento):
    def __init__(self, fecha, operario, repuestos, resultado, insumos):
        super().__init__(fecha, operario, repuestos)
        self.resultado = resultado      # 1 funciona, 2 revisión del fabricante, 3 rotura
        self.insumos = insumos

    def gasto_total(self):
        return self.repuestos + self.insumos
'''
CORR = '''from mantenimiento import Mantenimiento


class Correctivo(Mantenimiento):
    def __init__(self, fecha, operario, repuestos, horas_parada, tecnico):
        super().__init__(fecha, operario, repuestos)
        self.horas_parada = horas_parada
        self.tecnico = tecnico

    def gasto_total(self):
        return self.repuestos + self.tecnico
'''
M4 = '''from correctivo import Correctivo


class Maquina:
    def __init__(self):
        self.mantenimientos = []

    def agregar_mantenimiento(self, mantenimiento):
        self.mantenimientos.append(mantenimiento)

    def suma_gastos(self):
        return sum(m.gasto_total() for m in self.mantenimientos)
'''
M5 = M4 + '''
    def cantidad_mantenimientos_caros(self):
        cantidad = 0
        for m in self.mantenimientos:
            if m.gasto_total() > 10000:          # más de $10.000: el justo en 10.000 no cuenta
                cantidad += 1
        return cantidad
'''
M6 = M5 + '''
    def rotura_mas_larga(self):
        mayor = None
        for m in self.mantenimientos:
            if isinstance(m, Correctivo):
                if mayor is None or m.horas_parada > mayor.horas_parada:
                    mayor = m
        if mayor is None:
            return None
        return f"{mayor.fecha} {mayor.operario}"
'''
MAIN7 = '''from correctivo import Correctivo
from maquina import Maquina
from preventivo import Preventivo


def leer_mantenimientos(nombre_archivo, maquina):
    with open(nombre_archivo, encoding="utf-8") as archivo:
        for linea in archivo:                 # no tiene línea de títulos
            if not linea.strip():
                continue
            tipo, fecha, operario, repuestos, dato5, dato6 = linea.strip().split(",")
            if tipo == "1":
                m = Preventivo(fecha, operario, float(repuestos), int(dato5), float(dato6))
            else:
                m = Correctivo(fecha, operario, float(repuestos), int(dato5), float(dato6))
            maquina.agregar_mantenimiento(m)
'''
MAIN8 = MAIN7 + '''

def main():
    maquina = Maquina()
    leer_mantenimientos("mantenimientos.csv", maquina)
    print("Suma de gastos:", maquina.suma_gastos())
    print("Mantenimientos caros:", maquina.cantidad_mantenimientos_caros())
    print("Rotura más larga:", maquina.rotura_mas_larga())


if __name__ == "__main__":
    main()
'''
FIX = '''
P, C, Maquina = importar("preventivo", "Preventivo"), importar("correctivo", "Correctivo"), importar("maquina", "Maquina")
maq = Maquina()
maq.agregar_mantenimiento(P("1/1", "ANA", 5000, 2, 3000))
maq.agregar_mantenimiento(P("1/1", "BETO", 10000, 1, 1))
maq.agregar_mantenimiento(C("2/2", "CARI", 4000, 10, 8000))
maq.agregar_mantenimiento(C("3/3", "DIEGO", 1000, 20, 2000))
'''
E = ej('la-fabrica', 'La fábrica', 'Simulacro de la cátedra',
  'Mantenimientos preventivos y correctivos de una máquina. Una clase por archivo, como en la resolución de la cátedra.',
  [h('La fábrica'),
   pr('Una fábrica posee una máquina manufacturera a la que se le realizan diversos mantenimientos para garantizar su correcto funcionamiento.', 4),
   pr('Cada vez que se le realiza un mantenimiento se registra el nombre del operario que lo realiza, la fecha en que se efectuó y el importe que se gastó en repuestos.', 1),
   pr('Mantenimientos preventivos: periódicos, reemplazan insumos (lubricantes, repuestos de vida útil restringida) y verifican el funcionamiento. De ellos se registra el importe gastado en insumos y el resultado: 1 si la máquina funciona correctamente, 2 si se recomienda la revisión del servicio técnico y 3 si se detecta una rotura.', 2),
   pr('Mantenimientos correctivos: la máquina quedó impedida de funcionar y requiere la intervención. De ellos se registra la cantidad de horas de parada y el total abonado al técnico reparador.', 3),
   pr('Se necesita un programa que lea del archivo mantenimientos.csv la lista de todos los mantenimientos y los almacene en algún objeto (no en la función principal) que ofrezca los siguientes métodos:', 4, 7),
   li('1. Suma de gastos: total abonado por todo concepto en todos los mantenimientos registrados.', 1, 2, 3, 4),
   li('2. Cantidad de mantenimientos caros: total de mantenimientos de cualquier tipo que hayan tenido un gasto total de más de $10.000.', 5),
   li('3. Rotura más larga: la fecha y el nombre del operario del mantenimiento correctivo de mayor duración.', 6),
   pr('La función principal debe ingresar los datos desde el archivo de texto y finalizar luego de imprimir el resultado de la ejecución de los tres métodos anteriores.', 8),
   h('Estructura del archivo (sin línea de títulos)', 7),
   li('1. Tipo de mantenimiento: 1 para preventivo y 2 para correctivo', 7),
   li('2. Fecha: una cadena', 7), li('3. Operario: nombre del operario que realizó el mantenimiento', 7),
   li('4. Importe de repuestos: número de tipo float', 7),
   li('5. Si es un preventivo, resultado del mantenimiento (1, 2 o 3); si es un correctivo, cantidad de horas de parada', 7),
   li('6. Si es un preventivo, importe de los insumos; si es un correctivo, importe que cobró el técnico', 7),
   h('Contrato (para los tests)', 1, 2, 3, 4),
   li('Mantenimiento(fecha, operario, repuestos) · gasto_total()', 1),
   li('Preventivo(fecha, operario, repuestos, resultado, insumos) · gasto_total() = repuestos + insumos', 2),
   li('Correctivo(fecha, operario, repuestos, horas_parada, tecnico) · gasto_total() = repuestos + técnico', 3),
   li('Maquina() · agregar_mantenimiento(m), suma_gastos(), cantidad_mantenimientos_caros(), rotura_mas_larga()', 4, 5, 6)],
  {'mantenimientos.csv': leer(R, 'mantenimientos.csv')},
  [
  paso('La clase Mantenimiento', 'mantenimiento.py',
    ['Creá la clase abstracta Mantenimiento con fecha, operario y repuestos.',
     'gasto_total() es abstracto: cada tipo de mantenimiento suma algo distinto a los repuestos.'],
    ['Mantenimiento(fecha, operario, repuestos)', 'gasto_total()  → abstracto'],
    [('Mantenimiento es abstracta y gasto_total() también', '''
M = importar("mantenimiento", "Mantenimiento")
es_abstracta(M, "gasto_total")
lanza(TypeError, lambda: M("1/1", "ANA", 100), "Crear un Mantenimiento directamente")'''),
     ('El constructor guarda fecha, operario y repuestos', '''
M = importar("mantenimiento", "Mantenimiento")
m = concreta(M, ["gasto_total"], "1/1", "ANA", 5000)
atributo(m, "fecha", "1/1"); atributo(m, "operario", "ANA"); atributo(m, "repuestos", 5000)''')],
    {'mantenimiento.py': MANT},
    inicio={'mantenimiento.py': 'from abc import ABC, abstractmethod\n\n\nclass Mantenimiento(ABC):\n    # Completá el constructor y el método abstracto gasto_total\n    pass\n'},
    pistas=['class Mantenimiento(ABC): con def __init__(self, fecha, operario, repuestos):',
            'Arriba de def gasto_total(self): poné @abstractmethod y adentro pass.']),
  paso('El mantenimiento preventivo', 'preventivo.py',
    ['Preventivo hereda de Mantenimiento y agrega resultado e insumos.',
     'En el constructor, llamá primero a super().__init__(fecha, operario, repuestos).',
     'gasto_total() = repuestos + insumos.'],
    ['Preventivo(fecha, operario, repuestos, resultado, insumos)', 'gasto_total()  → repuestos + insumos'],
    [('Preventivo hereda de Mantenimiento', '''
M, P = importar("mantenimiento", "Mantenimiento"), importar("preventivo", "Preventivo")
hereda(P, M)'''),
     ('Guarda los datos propios y los de Mantenimiento', '''
P = importar("preventivo", "Preventivo")
m = P("1/1", "ANA", 5000, 2, 3000)
atributo(m, "fecha", "1/1"); atributo(m, "operario", "ANA"); atributo(m, "repuestos", 5000)
atributo(m, "resultado", 2); atributo(m, "insumos", 3000)'''),
     ('gasto_total(): $5.000 de repuestos + $3.000 de insumos = $8.000', '''
P = importar("preventivo", "Preventivo")
cerca(P("1/1", "ANA", 5000, 2, 3000).gasto_total(), 8000, "El gasto total del preventivo")''')],
    {'preventivo.py': PREV},
    inicio={'preventivo.py': 'from mantenimiento import Mantenimiento\n\n\nclass Preventivo(Mantenimiento):\n    # Completá: constructor (con super) y gasto_total\n    pass\n'},
    pistas=['def __init__(self, fecha, operario, repuestos, resultado, insumos): y la primera línea super().__init__(fecha, operario, repuestos)',
            'Después self.resultado = resultado y self.insumos = insumos.']),
  paso('El mantenimiento correctivo', 'correctivo.py',
    ['Correctivo hereda de Mantenimiento y agrega horas_parada y tecnico (lo que se le pagó).',
     'gasto_total() = repuestos + técnico.'],
    ['Correctivo(fecha, operario, repuestos, horas_parada, tecnico)', 'gasto_total()  → repuestos + técnico'],
    [('Correctivo hereda de Mantenimiento', '''
M, C = importar("mantenimiento", "Mantenimiento"), importar("correctivo", "Correctivo")
hereda(C, M)'''),
     ('Guarda horas_parada y tecnico', '''
C = importar("correctivo", "Correctivo")
m = C("2/2", "CARI", 4000, 10, 8000)
atributo(m, "operario", "CARI"); atributo(m, "horas_parada", 10); atributo(m, "tecnico", 8000)'''),
     ('gasto_total(): $4.000 + $8.000 = $12.000', '''
C = importar("correctivo", "Correctivo")
cerca(C("2/2", "CARI", 4000, 10, 8000).gasto_total(), 12000, "El gasto total del correctivo")'''),
     ('Sin técnico, el gasto son solo los repuestos', '''
C = importar("correctivo", "Correctivo")
cerca(C("2/2", "KIKA", 4000, 5, 0).gasto_total(), 4000, "El gasto con técnico en 0")''')],
    {'correctivo.py': CORR},
    inicio={'correctivo.py': 'from mantenimiento import Mantenimiento\n\n\nclass Correctivo(Mantenimiento):\n    # Completá: constructor (con super) y gasto_total\n    pass\n'},
    pistas=['Es igual que el preventivo, con horas_parada y tecnico en lugar de resultado e insumos.']),
  paso('La máquina y la suma de gastos', 'maquina.py',
    ['Maquina guarda los mantenimientos en una lista, self.mantenimientos.',
     'agregar_mantenimiento(m) agrega uno a la lista.',
     'suma_gastos() suma el gasto total de todos (cada uno sabe calcular el suyo).'],
    ['Maquina()', 'agregar_mantenimiento(mantenimiento)', 'suma_gastos()  → número'],
    [('La máquina empieza sin mantenimientos', '''
Maquina = importar("maquina", "Maquina")
m = Maquina(); atributo(m, "mantenimientos"); igual(len(m.mantenimientos), 0, "Al empezar")
cerca(m.suma_gastos(), 0, "La suma de gastos sin mantenimientos")'''),
     ('agregar_mantenimiento() los suma a la lista', FIX + 'igual(len(maq.mantenimientos), 4, "La cantidad después de agregar 4")'),
     ('suma_gastos(): 8.000 + 10.001 + 12.000 + 3.000 = 33.001', FIX + 'cerca(maq.suma_gastos(), 33001, "La suma de gastos")')],
    {'maquina.py': M4},
    inicio={'maquina.py': 'class Maquina:\n    # Completá: la lista de mantenimientos, agregar_mantenimiento y suma_gastos\n    pass\n'},
    pistas=['En el constructor: self.mantenimientos = []', 'return sum(m.gasto_total() for m in self.mantenimientos)']),
  paso('Los mantenimientos caros', 'maquina.py',
    ['Agregá cantidad_mantenimientos_caros(): cuántos tuvieron un gasto total de más de $10.000.',
     'Ojo: "más de" quiere decir que uno de exactamente $10.000 no cuenta.'],
    ['cantidad_mantenimientos_caros()  → entero'],
    [('Cuenta los de más de $10.000', FIX + 'igual(maq.cantidad_mantenimientos_caros(), 2, "Mantenimientos caros (10.001 y 12.000)")'),
     ('El justo en $10.000 no cuenta', '''
P, Maquina = importar("preventivo", "Preventivo"), importar("maquina", "Maquina")
maq = Maquina(); maq.agregar_mantenimiento(P("1/1", "EDITA", 10000, 1, 0))
igual(maq.cantidad_mantenimientos_caros(), 0, "Con uno de $10.000 justos")'''),
     ('Sin mantenimientos da 0', 'igual(importar("maquina", "Maquina")().cantidad_mantenimientos_caros(), 0, "Sin mantenimientos")')],
    {'maquina.py': M5},
    pistas=['Un contador: for m in self.mantenimientos: if m.gasto_total() > 10000: cantidad += 1']),
  paso('La rotura más larga', 'maquina.py',
    ['Agregá rotura_mas_larga(): del correctivo con más horas de parada, devolvé "fecha operario" (separados por un espacio).',
     'Solo cuentan los correctivos: para saber si un mantenimiento lo es, isinstance(m, Correctivo).',
     'Si no hay correctivos, devolvé None.'],
    ['rotura_mas_larga()  → "fecha operario", o None'],
    [('Devuelve la fecha y el operario del más largo', FIX + 'igual(maq.rotura_mas_larga(), "3/3 DIEGO", "La rotura más larga")'),
     ('No mira los preventivos', '''
P, C, Maquina = importar("preventivo", "Preventivo"), importar("correctivo", "Correctivo"), importar("maquina", "Maquina")
maq = Maquina(); maq.agregar_mantenimiento(P("1/1", "FEDE", 100, 1, 100)); maq.agregar_mantenimiento(C("2/2", "GABO", 100, 30, 100))
igual(maq.rotura_mas_larga(), "2/2 GABO", "Con un preventivo y un correctivo")'''),
     ('Elige el de más horas aunque no sea el último', '''
C, Maquina = importar("correctivo", "Correctivo"), importar("maquina", "Maquina")
maq = Maquina(); maq.agregar_mantenimiento(C("10/4", "HILDA", 1000, 7, 100)); maq.agregar_mantenimiento(C("9/3", "INES", 1000, 15, 100)); maq.agregar_mantenimiento(C("1/5", "JUAN", 1000, 3, 100))
igual(maq.rotura_mas_larga(), "9/3 INES", "La rotura más larga")'''),
     ('Sin correctivos devuelve None', '''
P, Maquina = importar("preventivo", "Preventivo"), importar("maquina", "Maquina")
maq = Maquina(); maq.agregar_mantenimiento(P("1/1", "JORGE", 100, 1, 100))
igual(maq.rotura_mas_larga(), None, "Sin correctivos")''')],
    {'maquina.py': M6},
    pistas=['Arriba del archivo: from correctivo import Correctivo',
            'Guardá el mayor en una variable que empieza en None y comparalo con m.horas_parada.',
            'Al final: return f"{mayor.fecha} {mayor.operario}"']),
  paso('Leer el CSV', 'main.py',
    ['En main.py escribí leer_mantenimientos(nombre_archivo, maquina): lee el archivo y agrega cada mantenimiento a la máquina.',
     'No tiene línea de títulos: cada línea es un mantenimiento. Separá los datos con split(",").',
     'El tipo (1 o 2) elige si es Preventivo o Correctivo; los datos 5 y 6 cambian de significado según el tipo.',
     'Convertí: repuestos e importes con float(); resultado y horas con int().'],
    ['leer_mantenimientos(nombre_archivo, maquina)'],
    [('Lee los 99 mantenimientos', '''
leer, Maquina = importar("main", "leer_mantenimientos"), importar("maquina", "Maquina")
maq = Maquina(); leer("mantenimientos.csv", maq)
igual(len(maq.mantenimientos), 99, "La cantidad de mantenimientos leídos")'''),
     ('La primera línea es un preventivo con sus datos convertidos', '''
leer, Maquina, P = importar("main", "leer_mantenimientos"), importar("maquina", "Maquina"), importar("preventivo", "Preventivo")
maq = Maquina(); leer("mantenimientos.csv", maq); m = maq.mantenimientos[0]
assert type(m) is P, "La primera línea (tipo 1) tiene que ser un Preventivo"
igual(m.fecha, "4/7", "La fecha"); igual(m.operario, "MARIA ROSARIO", "El operario")
cerca(m.repuestos, 15300, "Los repuestos"); igual(m.resultado, 2, "El resultado"); cerca(m.insumos, 4700, "Los insumos")'''),
     ('La segunda es un correctivo', '''
leer, Maquina, C = importar("main", "leer_mantenimientos"), importar("maquina", "Maquina"), importar("correctivo", "Correctivo")
maq = Maquina(); leer("mantenimientos.csv", maq); m = maq.mantenimientos[1]
assert type(m) is C, "La segunda línea (tipo 2) tiene que ser un Correctivo"
igual(m.horas_parada, 1, "Las horas de parada"); cerca(m.tecnico, 1400, "Lo del técnico")'''),
     ('Con todo el archivo, la suma de gastos da $3.023.600', '''
leer, Maquina = importar("main", "leer_mantenimientos"), importar("maquina", "Maquina")
maq = Maquina(); leer("mantenimientos.csv", maq)
cerca(maq.suma_gastos(), 3023600, "La suma de gastos")''')],
    {'main.py': MAIN7},
    inicio={'main.py': 'from correctivo import Correctivo\nfrom maquina import Maquina\nfrom preventivo import Preventivo\n\n\ndef leer_mantenimientos(nombre_archivo, maquina):\n    # Leé el archivo línea por línea y agregá cada mantenimiento\n    pass\n'},
    pistas=['with open(nombre_archivo, encoding="utf-8") as archivo: y for linea in archivo:',
            'tipo, fecha, operario, repuestos, dato5, dato6 = linea.strip().split(",")',
            'El tipo queda como texto: comparalo con "1" (con comillas) o convertilo con int().']),
  paso('El main', 'main.py',
    ['Escribí main(): crea la Maquina, lee mantenimientos.csv y muestra los tres resultados.',
     'Al final: if __name__ == "__main__": main()'],
    ['main()'],
    [('main() corre e imprime algo', 'assert correr_main().strip(), "main() no imprime nada"'),
     ('Muestra la suma de gastos', 'aparece(3023600.0, correr_main(), "la suma de gastos")'),
     ('Muestra los 88 mantenimientos caros', 'aparece(88, correr_main(), "la cantidad de mantenimientos caros")'),
     ('Muestra la rotura más larga', 'aparece("10/4 PILAR", correr_main(), "la rotura más larga")')],
    {'main.py': MAIN8}, ejecutar=['main', 'main'],
    pistas=['def main(): maquina = Maquina(); leer_mantenimientos("mantenimientos.csv", maquina) y después tres print.']),
  ])
