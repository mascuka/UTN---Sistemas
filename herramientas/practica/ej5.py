from comun import *
R = 'datos'
PAC = '''class Paciente:
    SINTOMAS = {1: "corazon", 2: "pulmon", 3: "otras"}

    def __init__(self, nombre, sintoma, habitual=False):
        if sintoma not in Paciente.SINTOMAS:
            raise ValueError("El síntoma tiene que ser 1, 2 o 3")
        self.nombre = nombre
        self.sintoma = sintoma
        self.habitual = habitual

    def __str__(self):
        return f"Paciente: {self.nombre} - Síntoma: {Paciente.SINTOMAS[self.sintoma]} - Habitual: {'sí' if self.habitual else 'no'}"
'''
AT2 = '''from abc import ABC, abstractmethod


class Atencion(ABC):
    TIPOS_DE_COBRO = {1: "efectivo", 2: "tarjeta de crédito"}

    def __init__(self, codigo, tipoDeCobro):
        if tipoDeCobro not in Atencion.TIPOS_DE_COBRO:
            raise ValueError("El tipo de cobro tiene que ser 1 o 2")
        self.codigo = codigo
        self.tipoDeCobro = tipoDeCobro

    @abstractmethod
    def importeACobrar(self):
        pass

    def __str__(self):
        return f"Atención {self.codigo} - Importe a cobrar: ${self.importeACobrar():.2f}"
'''
AT3 = AT2 + '''

class AtencionMedica(Atencion):
    def __init__(self, codigo, tipoDeCobro, paciente, importe):
        super().__init__(codigo, tipoDeCobro)
        self.paciente = paciente
        self.importe = importe            # el importe de la consulta

    def importeACobrar(self):
        valor = self.importe
        if self.paciente.habitual:
            valor = valor * 0.75          # 25 % de descuento
        if self.tipoDeCobro == 2:
            valor = valor * 1.20          # tarjeta: 20 % más
        else:
            valor = valor * 0.90          # efectivo: 10 % menos
        return valor

    def esPacienteHabitual(self):
        return self.paciente.habitual
'''
AT4 = AT3 + '''

class AtencionFarmacia(Atencion):
    def __init__(self, codigo, tipoDeCobro, importeTotal, descuento):
        super().__init__(codigo, tipoDeCobro)
        self.importeTotal = importeTotal  # lo de los medicamentos
        self.descuento = descuento        # el cupón: un monto fijo (0 si no hay)

    def importeACobrar(self):
        valor = self.importeTotal - self.descuento
        if self.tipoDeCobro == 2:
            valor = valor * 1.30          # tarjeta: 30 % más
        else:
            valor = valor * 0.95          # efectivo: 5 % menos
        return valor
'''
HOS5 = '''from atencion import AtencionMedica


class Hospital:
    def __init__(self, razonSocial):
        self.razonSocial = razonSocial
        self.atencionesRealizadas = []

    def addAtencion(self, atencion):
        self.atencionesRealizadas.append(atencion)

    def atencionesMedicas(self):
        return [a for a in self.atencionesRealizadas if isinstance(a, AtencionMedica)]

    def importe_total_atencion_consulta(self):
        return sum(a.importe for a in self.atencionesMedicas())
'''
HOS6 = HOS5 + '''
    def importe_promedio_atenciones(self, minimo, maximo):
        importes = [a.importeACobrar() for a in self.atencionesMedicas()
                    if minimo <= a.importeACobrar() <= maximo]
        if not importes:
            return 0
        return sum(importes) / len(importes)
'''
HOS7 = HOS6 + '''
    def codigo_primera_atencion_habitual(self):
        for a in self.atencionesMedicas():
            if a.esPacienteHabitual():
                return a.codigo
        return 0
'''
MAIN8 = '''import csv

from atencion import AtencionFarmacia, AtencionMedica
from hospital import Hospital
from paciente import Paciente


def leerCsv(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def aBooleano(texto):
    return texto.strip().lower() == "true"


def cargarPacientes(ruta="pacientes.csv"):
    """Los pacientes, guardados por el código de su atención médica."""
    pacientes = {}
    for fila in leerCsv(ruta):
        pacientes[int(fila["codigo_atencion"])] = Paciente(fila["nombre"], int(fila["sintoma"]), aBooleano(fila["habitual"]))
    return pacientes


def cargarAtencionesMedicas(pacientes, ruta="atenciones_medicas.csv"):
    atenciones = []
    for fila in leerCsv(ruta):
        codigo = int(fila["codigo"])
        atenciones.append(AtencionMedica(codigo, int(fila["tipo_cobro"]), pacientes[codigo], float(fila["importe_consulta"])))
    return atenciones
'''
MAIN9 = MAIN8 + '''

def cargarAtencionesFarmacia(ruta="atenciones_farmacia.csv"):
    return [AtencionFarmacia(int(f["codigo"]), int(f["tipo_cobro"]), float(f["importe_total"]), float(f["cupon_descuento"]))
            for f in leerCsv(ruta)]


def cargarHospital(razonSocial="Hospital San Roque"):
    hospital = Hospital(razonSocial)
    for atencion in cargarAtencionesMedicas(cargarPacientes()):
        hospital.addAtencion(atencion)
    for atencion in cargarAtencionesFarmacia():
        hospital.addAtencion(atencion)
    return hospital
'''
MAIN10 = MAIN9 + '''

def main():
    hospital = cargarHospital()
    print("Importe total de las consultas:", round(hospital.importe_total_atencion_consulta(), 2))
    print("Promedio entre $10.000 y $30.000:", round(hospital.importe_promedio_atenciones(10000, 30000), 2))
    print("Primera atención de un paciente habitual:", hospital.codigo_primera_atencion_habitual())


if __name__ == "__main__":
    main()
'''
MED = '''
P, AM = importar("paciente", "Paciente"), importar("atencion", "AtencionMedica")
def medica(codigo, importe, habitual=False, cobro=1):
    return AM(codigo, cobro, P(f"Paciente {codigo}", 3, habitual), importe)
'''
E = ej('hospital', 'Hospital', 'Simulacro de la cátedra · el más completo',
  'Atenciones médicas y de farmacia con su importe a cobrar. Tiene validaciones, un paciente adentro de cada atención y tres CSV.',
  [h('Hospital'),
   pr('Un hospital de nuestra ciudad necesita conocer cierta información respecto a los importes cobrados por las distintas atenciones que realiza, y requiere de un sistema orientado a objetos que le dé soporte a ello.'),
   pr('Del Hospital sólo interesa registrar la razón social y una colección con todas las atenciones realizadas.', 5),
   pr('Cada atención tiene los siguientes datos: un código numérico que identifica a cada atención y un valor numérico que representa el tipo de cobro (1: “efectivo”; 2: “tarjeta de crédito”). Las atenciones pueden ser médicas o de farmacia:', 2),
   pr('Una atención médica agrega los siguientes datos: el paciente atendido y el importe de la consulta.', 3),
   pr('Una atención de farmacia agrega los siguientes datos: el importe total de los medicamentos vendidos en dicha atención y un cupón de descuento que especifica el monto de descuento que se aplicaría sobre el importe total de los medicamentos; en caso que el cupón de descuento sea igual que 0, no se realizará ningún descuento; cabe aclarar que el cupón de descuento debe ser 0 o positivo.', 4),
   pr('Del paciente asociado a la atención médica se registran: su nombre, el síntoma que prevalece (1: “corazon”, 2: “pulmon”, 3: “otras”) y un valor booleano que representa si el paciente es habitual (true) o no (false) del hospital.', 1),
   pr('De cada clase de atención se debe calcular un importeACobrar en pesos, que representa lo que el hospital cobra al paciente por la atención brindada. Este cálculo dependerá del tipo de cobro de la atención y de la clase de atención brindada:', 2, 3, 4),
   pr('El importe total de las atenciones médicas se calcula a partir del importe de la consulta. En caso que el paciente sea “habitual” se le aplicará un descuento del 25 %. Por último, si el tipo de cobro es igual a 2 (“tarjeta de crédito”) se le incrementa al anterior importe un 20 % más; en caso que el cobro sea igual a 1 (“efectivo”) se le realiza un descuento del 10 % sobre el anterior importe.', 3),
   pr('El importe total de las atenciones de farmacia se calcula a partir del importe total de los medicamentos vendidos. Luego se le realiza el descuento del cupón de descuento cuyo importe está especificado. Por último, si el tipo de cobro es igual a 2 (“tarjeta de crédito”) se le incrementa al anterior importe un 30 % más; en caso que el cobro sea igual a 1 (“efectivo”) se le realiza un descuento del 5 % sobre el anterior importe.', 4),
   h('Con lo expuesto anteriormente, usted deberá implementar:'),
   li('Para las clases Atención, Médica, Farmacia y Paciente: su constructor, acceso y modificación y toString.', 1, 2, 3, 4),
   li('Para la clase Hospital: el método addAtencion que agrega una atención a la colección.', 5),
   li('Los métodos importeACobrar de las atenciones, que calculen y devuelvan el importe a cobrar según los criterios anteriores.', 3, 4),
   li('importe_total_atencion_consulta: la suma de los importes de las consultas de las atenciones médicas.', 5),
   li('importe_promedio_atenciones: el promedio de los importes a cobrar de las atenciones médicas cuyo importe a cobrar esté entre dos valores recibidos como parámetros.', 6),
   li('codigo_primera_atencion_habitual: el código de la primera atención médica registrada para un paciente habitual, o 0 si no existe ninguna.', 7),
   pr('Los valores de los objetos que deben ser instanciados se encuentran en los archivos pacientes.csv, atenciones_medicas.csv y atenciones_farmacia.csv (con línea de títulos).', 8, 9, 10)],
  {'pacientes.csv': leer(R, 'pacientes.csv'), 'atenciones_medicas.csv': leer(R, 'atenciones_medicas.csv'), 'atenciones_farmacia.csv': leer(R, 'atenciones_farmacia.csv')},
  [
  paso('El paciente', 'paciente.py',
    ['Paciente guarda nombre, sintoma (1, 2 o 3) y habitual (True o False; si no se pasa, False).',
     'Si el síntoma no es 1, 2 ni 3, el constructor lanza ValueError.',
     'str(paciente) muestra el nombre y el síntoma en palabras: corazon, pulmon u otras.'],
    ['Paciente(nombre, sintoma, habitual=False)', 'str(paciente)  → con el nombre y "corazon" / "pulmon" / "otras"'],
    [('Guarda los tres datos', '''
P = importar("paciente", "Paciente")
p = P("Ana Diaz", 1, True); atributo(p, "nombre", "Ana Diaz"); atributo(p, "sintoma", 1); atributo(p, "habitual", True)'''),
     ('Si no se dice, no es habitual', 'igual(importar("paciente", "Paciente")("Luis Perez", 3).habitual, False, "habitual sin pasarlo")'),
     ('Un síntoma fuera del enunciado lanza ValueError', '''
P = importar("paciente", "Paciente")
for s in (0, 4, "corazon"):
    lanza(ValueError, lambda: P("Ana Diaz", s), f"Paciente con síntoma {s!r}")'''),
     ('Los datos se pueden modificar', '''
P = importar("paciente", "Paciente")
p = P("Luis Perez", 2); p.nombre = "Marta Gomez"; p.habitual = True
igual(p.nombre, "Marta Gomez", "El nombre después de cambiarlo"); igual(p.habitual, True, "habitual después de cambiarlo")'''),
     ('str() muestra el nombre y el síntoma en palabras', '''
s = str(importar("paciente", "Paciente")("Ana Diaz", 1, True))
assert "Ana Diaz" in s, f"str() tiene que incluir el nombre y dio {s!r}"
assert "corazon" in s, f"str() tiene que decir \\"corazon\\" para el síntoma 1 y dio {s!r}"''')],
    {'paciente.py': PAC},
    inicio={'paciente.py': 'class Paciente:\n    # Completá: constructor con la validación del síntoma y __str__\n    pass\n'},
    pistas=['El valor por defecto va en la firma: def __init__(self, nombre, sintoma, habitual=False):',
            'Validación: if sintoma not in (1, 2, 3): raise ValueError("…")',
            'Un diccionario ayuda para el texto: SINTOMAS = {1: "corazon", 2: "pulmon", 3: "otras"}']),
  paso('La atención', 'atencion.py',
    ['Atencion es abstracta: guarda codigo y tipoDeCobro (1 efectivo, 2 tarjeta).',
     'Si el tipo de cobro no es 1 ni 2, lanza ValueError.',
     'importeACobrar() es abstracto; __str__ muestra el código y el importe a cobrar con dos decimales.'],
    ['Atencion(codigo, tipoDeCobro)', 'importeACobrar()  → abstracto'],
    [('Atencion es abstracta, con importeACobrar() abstracto', '''
A = importar("atencion", "Atencion")
es_abstracta(A, "importeACobrar"); lanza(TypeError, lambda: A(1, 1), "Crear una Atencion directamente")'''),
     ('Guarda código y tipo de cobro', '''
A = importar("atencion", "Atencion")
a = concreta(A, ["importeACobrar"], 7, 2); atributo(a, "codigo", 7); atributo(a, "tipoDeCobro", 2)'''),
     ('Un tipo de cobro que no es 1 ni 2 lanza ValueError', '''
A = importar("atencion", "Atencion")
for t in (0, 3, "efectivo"):
    lanza(ValueError, lambda: concreta(A, ["importeACobrar"], 1, t), f"Atención con tipo de cobro {t!r}")''')],
    {'atencion.py': AT2},
    inicio={'atencion.py': 'from abc import ABC, abstractmethod\n\n\nclass Atencion(ABC):\n    # Completá: constructor con la validación, importeACobrar abstracto y __str__\n    pass\n'},
    pistas=['if tipoDeCobro not in (1, 2): raise ValueError("…") antes de guardar.',
            'En __str__ podés llamar a self.importeACobrar(): cada subclase pone el suyo. Con :.2f queda con dos decimales.']),
  paso('La atención médica', 'atencion.py',
    ['En atencion.py, abajo de Atencion: AtencionMedica agrega el paciente (un objeto Paciente) y el importe de la consulta.',
     'importeACobrar(): si el paciente es habitual, 25 % de descuento; después, con tarjeta 20 % más y en efectivo 10 % menos.',
     'esPacienteHabitual() devuelve si su paciente es habitual.'],
    ['AtencionMedica(codigo, tipoDeCobro, paciente, importe)', 'importeACobrar()', 'esPacienteHabitual()  → True / False'],
    [('AtencionMedica es una Atencion', 'hereda(importar("atencion", "AtencionMedica"), importar("atencion", "Atencion"))'),
     ('Guarda el paciente y el importe', '''
P, AM = importar("paciente", "Paciente"), importar("atencion", "AtencionMedica")
p = P("Luis Perez", 2); a = AM(7, 1, p, 1000.0)
assert getattr(a, "paciente", None) is p, "La atención tiene que guardar el mismo objeto paciente (self.paciente = paciente)"
atributo(a, "importe", 1000.0); atributo(a, "codigo", 7)'''),
     ('No habitual: efectivo $900 y tarjeta $1.200', '''
P, AM = importar("paciente", "Paciente"), importar("atencion", "AtencionMedica")
p = P("Luis Perez", 2, False)
cerca(AM(1, 1, p, 1000.0).importeACobrar(), 900, "No habitual en efectivo"); cerca(AM(1, 2, p, 1000.0).importeACobrar(), 1200, "No habitual con tarjeta")'''),
     ('Habitual: primero el 25 %: efectivo $675 y tarjeta $900', '''
P, AM = importar("paciente", "Paciente"), importar("atencion", "AtencionMedica")
p = P("Ana Diaz", 1, True)
cerca(AM(1, 1, p, 1000.0).importeACobrar(), 675, "Habitual en efectivo"); cerca(AM(1, 2, p, 1000.0).importeACobrar(), 900, "Habitual con tarjeta")'''),
     ('esPacienteHabitual()', '''
P, AM = importar("paciente", "Paciente"), importar("atencion", "AtencionMedica")
igual(AM(1, 1, P("Ana", 1, True), 1.0).esPacienteHabitual(), True, "Con paciente habitual")
igual(AM(2, 1, P("Luis", 1, False), 1.0).esPacienteHabitual(), False, "Con paciente no habitual")'''),
     ('str() muestra el código y el importe a cobrar ($900.00)', '''
P, AM = importar("paciente", "Paciente"), importar("atencion", "AtencionMedica")
s = str(AM(1, 1, P("Luis Perez", 2), 1000.0)); assert "900.00" in s, f"str() tiene que mostrar 900.00 y dio {s!r}"''')],
    {'atencion.py': AT3},
    pistas=['valor = self.importe; if self.paciente.habitual: valor = valor * 0.75',
            'Después: if self.tipoDeCobro == 2: valor = valor * 1.2 y si no, valor = valor * 0.9']),
  paso('La atención de farmacia', 'atencion.py',
    ['AtencionFarmacia agrega importeTotal (los medicamentos) y descuento (el cupón, un monto fijo).',
     'importeACobrar(): al total se le resta el cupón; después, con tarjeta 30 % más y en efectivo 5 % menos.'],
    ['AtencionFarmacia(codigo, tipoDeCobro, importeTotal, descuento)', 'importeACobrar()'],
    [('AtencionFarmacia es una Atencion', 'hereda(importar("atencion", "AtencionFarmacia"), importar("atencion", "Atencion"))'),
     ('Guarda el total y el cupón', '''
AF = importar("atencion", "AtencionFarmacia")
a = AF(101, 2, 5000.0, 500.0); atributo(a, "importeTotal", 5000.0); atributo(a, "descuento", 500.0)'''),
     ('Cupón en 0: efectivo $950 y tarjeta $1.300', '''
AF = importar("atencion", "AtencionFarmacia")
cerca(AF(101, 1, 1000.0, 0.0).importeACobrar(), 950, "En efectivo sin cupón"); cerca(AF(101, 2, 1000.0, 0.0).importeACobrar(), 1300, "Con tarjeta sin cupón")'''),
     ('Con cupón de $200: efectivo $760 y tarjeta $1.040', '''
AF = importar("atencion", "AtencionFarmacia")
cerca(AF(101, 1, 1000.0, 200.0).importeACobrar(), 760, "En efectivo con cupón"); cerca(AF(101, 2, 1000.0, 200.0).importeACobrar(), 1040, "Con tarjeta con cupón")'''),
     ('str() muestra el código y el importe a cobrar', '''
s = str(importar("atencion", "AtencionFarmacia")(101, 1, 1000.0, 0.0))
assert "101" in s and "950.00" in s, f"str() tiene que mostrar 101 y 950.00 y dio {s!r}"''')],
    {'atencion.py': AT4},
    pistas=['El cupón se resta primero: valor = self.importeTotal - self.descuento',
            'El orden importa: (1000 − 200) × 0,95 = 760.']),
  paso('El hospital y el total de las consultas', 'hospital.py',
    ['Hospital guarda la razón social y la lista atencionesRealizadas, que empieza vacía.',
     'addAtencion(atencion) agrega una atención.',
     'importe_total_atencion_consulta(): la suma del importe de la consulta de las atenciones médicas (las de farmacia no).'],
    ['Hospital(razonSocial)', 'addAtencion(atencion)', 'importe_total_atencion_consulta()  → número'],
    [('Guarda la razón social y empieza sin atenciones', '''
H = importar("hospital", "Hospital")
h = H("Hospital San Roque"); atributo(h, "razonSocial", "Hospital San Roque"); atributo(h, "atencionesRealizadas")
igual(h.atencionesRealizadas, [], "Las atenciones al empezar")'''),
     ('addAtencion() las agrega en orden', MED + '''
H, AF = importar("hospital", "Hospital"), importar("atencion", "AtencionFarmacia")
h = H("X"); a, b = medica(1, 1000.0), AF(101, 1, 1000.0, 0.0); h.addAtencion(a); h.addAtencion(b)
assert h.atencionesRealizadas == [a, b], "atencionesRealizadas tiene que tener las dos, en el orden en que se agregaron"'''),
     ('Suma solo las consultas médicas: 1.000 + 2.500', MED + '''
H, AF = importar("hospital", "Hospital"), importar("atencion", "AtencionFarmacia")
h = H("X"); h.addAtencion(medica(1, 1000.0)); h.addAtencion(medica(2, 2500.0, habitual=True)); h.addAtencion(AF(101, 1, 9999.0, 0.0))
cerca(h.importe_total_atencion_consulta(), 3500, "El total de las consultas")'''),
     ('Sin atenciones, el total es 0', 'cerca(importar("hospital", "Hospital")("X").importe_total_atencion_consulta(), 0, "Sin atenciones")')],
    {'hospital.py': HOS5},
    inicio={'hospital.py': 'from atencion import AtencionMedica\n\n\nclass Hospital:\n    # Completá: constructor, addAtencion e importe_total_atencion_consulta\n    pass\n'},
    pistas=['Para quedarte solo con las médicas: isinstance(a, AtencionMedica).',
            'Ayuda tener un método que devuelva las médicas: [a for a in self.atencionesRealizadas if isinstance(a, AtencionMedica)]']),
  paso('El promedio entre dos valores', 'hospital.py',
    ['Agregá importe_promedio_atenciones(minimo, maximo): el promedio del importe a cobrar de las atenciones médicas cuyo importe a cobrar esté entre los dos valores (incluidos).',
     'Si ninguna está en el rango, devolvé 0 (sin dividir por cero).'],
    ['importe_promedio_atenciones(minimo, maximo)  → número'],
    [('Promedia solo las del rango: (900 + 1.800) / 2', MED + '''
H = importar("hospital", "Hospital")
h = H("X")
for c, i in ((1, 1000.0), (2, 2000.0), (3, 3000.0)): h.addAtencion(medica(c, i))
cerca(h.importe_promedio_atenciones(800.0, 2000.0), 1350, "El promedio entre 800 y 2.000")'''),
     ('No cuenta las de farmacia', MED + '''
H, AF = importar("hospital", "Hospital"), importar("atencion", "AtencionFarmacia")
h = H("X"); h.addAtencion(medica(1, 1000.0)); h.addAtencion(AF(101, 1, 1000.0, 0.0))
cerca(h.importe_promedio_atenciones(0.0, 10000.0), 900, "El promedio con una médica y una de farmacia")'''),
     ('Sin ninguna en el rango da 0', MED + '''
H = importar("hospital", "Hospital")
h = H("X"); h.addAtencion(medica(1, 1000.0))
cerca(h.importe_promedio_atenciones(5000.0, 9000.0), 0, "Sin coincidencias")''')],
    {'hospital.py': HOS6},
    pistas=['Primero juntá los importes: [a.importeACobrar() for a in medicas if minimo <= a.importeACobrar() <= maximo]',
            'if not importes: return 0 y si no, sum(importes) / len(importes)']),
  paso('La primera atención de un habitual', 'hospital.py',
    ['Agregá codigo_primera_atencion_habitual(): el código de la primera atención médica (en el orden en que se registraron) de un paciente habitual.',
     'Si no hay ninguna, devolvé 0.'],
    ['codigo_primera_atencion_habitual()  → código, o 0'],
    [('Devuelve la primera habitual (la 3)', MED + '''
H, AF = importar("hospital", "Hospital"), importar("atencion", "AtencionFarmacia")
h = H("X"); h.addAtencion(AF(101, 1, 1000.0, 0.0)); h.addAtencion(medica(2, 1000.0)); h.addAtencion(medica(3, 1000.0, True)); h.addAtencion(medica(4, 1000.0, True))
igual(h.codigo_primera_atencion_habitual(), 3, "El código de la primera habitual")'''),
     ('Sin habituales devuelve 0', MED + '''
H, AF = importar("hospital", "Hospital"), importar("atencion", "AtencionFarmacia")
h = H("X"); h.addAtencion(medica(1, 1000.0)); h.addAtencion(AF(101, 1, 1000.0, 0.0))
igual(h.codigo_primera_atencion_habitual(), 0, "Sin pacientes habituales")'''),
     ('Sin atenciones devuelve 0', 'igual(importar("hospital", "Hospital")("X").codigo_primera_atencion_habitual(), 0, "Sin atenciones")')],
    {'hospital.py': HOS7},
    pistas=['Recorré las médicas en orden y devolvé apenas encontrás una con esPacienteHabitual(); al final, return 0.']),
  paso('Leer pacientes y atenciones médicas', 'main.py',
    ['En main.py: aBooleano(texto) convierte "true" / "false" (en mayúsculas o minúsculas) a True / False.',
     'cargarPacientes(ruta="pacientes.csv") devuelve un diccionario: código de atención → Paciente.',
     'cargarAtencionesMedicas(pacientes, ruta="atenciones_medicas.csv") devuelve la lista de AtencionMedica, cada una con su paciente del diccionario.',
     'Los tres CSV tienen línea de títulos.'],
    ['aBooleano(texto)', 'cargarPacientes(ruta="pacientes.csv")  → {codigo: Paciente}', 'cargarAtencionesMedicas(pacientes, ruta="atenciones_medicas.csv")  → [AtencionMedica]'],
    [('aBooleano() entiende true y false', '''
aB = importar("main", "aBooleano")
igual(aB("true"), True, 'aBooleano("true")'); igual(aB("TRUE"), True, 'aBooleano("TRUE")'); igual(aB("false"), False, 'aBooleano("false")')'''),
     ('Carga los 30 pacientes, por código de atención', '''
cp, P = importar("main", "cargarPacientes"), importar("paciente", "Paciente")
pac = cp(); igual(len(pac), 30, "La cantidad de pacientes")
assert all(isinstance(k, int) for k in pac), "Las claves tienen que ser números (int), no texto"
assert all(isinstance(p, P) for p in pac.values()), "Los valores tienen que ser objetos Paciente"
igual(pac[1].nombre, "Ana Diaz", "El paciente de la atención 1"); igual(pac[1].habitual, True, "¿Es habitual?"); igual(pac[2].habitual, False, "El paciente 2 no es habitual")'''),
     ('Carga las 30 atenciones médicas, cada una con su paciente', '''
cp, cam, AM = importar("main", "cargarPacientes"), importar("main", "cargarAtencionesMedicas"), importar("atencion", "AtencionMedica")
pac = cp(); med = cam(pac); igual(len(med), 30, "La cantidad de atenciones médicas")
assert all(isinstance(a, AM) for a in med), "Tienen que ser objetos AtencionMedica"
assert all(a.paciente is pac[a.codigo] for a in med), "Cada atención tiene que tener el paciente con su mismo código"
cerca(med[0].importe, 17717.06, "El importe de la primera consulta")''')],
    {'main.py': MAIN8},
    inicio={'main.py': 'import csv\n\nfrom atencion import AtencionFarmacia, AtencionMedica\nfrom hospital import Hospital\nfrom paciente import Paciente\n\n\ndef aBooleano(texto):\n    pass\n\n\ndef cargarPacientes(ruta="pacientes.csv"):\n    pass\n\n\ndef cargarAtencionesMedicas(pacientes, ruta="atenciones_medicas.csv"):\n    pass\n'},
    pistas=['csv.DictReader(archivo) te da cada fila como diccionario: fila["nombre"], fila["sintoma"]…',
            'pacientes[int(fila["codigo_atencion"])] = Paciente(fila["nombre"], int(fila["sintoma"]), aBooleano(fila["habitual"]))',
            'Para la médica, el paciente sale del diccionario: pacientes[codigo].']),
  paso('Farmacia y el hospital completo', 'main.py',
    ['cargarAtencionesFarmacia(ruta="atenciones_farmacia.csv") devuelve la lista de AtencionFarmacia.',
     'cargarHospital(razonSocial="Hospital San Roque") crea el Hospital y le agrega las 30 médicas y las 30 de farmacia.'],
    ['cargarAtencionesFarmacia(ruta="atenciones_farmacia.csv")  → [AtencionFarmacia]', 'cargarHospital(razonSocial="Hospital San Roque")  → Hospital'],
    [('Carga las 30 atenciones de farmacia', '''
caf, AF = importar("main", "cargarAtencionesFarmacia"), importar("atencion", "AtencionFarmacia")
far = caf(); igual(len(far), 30, "La cantidad de atenciones de farmacia")
assert all(isinstance(a, AF) for a in far), "Tienen que ser objetos AtencionFarmacia"
cerca(far[1].descuento, 11187.13, "El cupón de la atención 102")'''),
     ('El hospital queda con las 60 atenciones', '''
h = importar("main", "cargarHospital")()
igual(len(h.atencionesRealizadas), 60, "La cantidad de atenciones del hospital")'''),
     ('El total de las consultas da $864.634,55', '''
h = importar("main", "cargarHospital")()
cerca(round(h.importe_total_atencion_consulta(), 2), 864634.55, "El total de las consultas")''')],
    {'main.py': MAIN9},
    pistas=['Una lista por comprensión: [AtencionFarmacia(int(f["codigo"]), …) for f in filas]',
            'cargarHospital: hospital = Hospital(razonSocial) y dos for con hospital.addAtencion(a).']),
  paso('El main', 'main.py',
    ['Escribí main(): carga el hospital e imprime el total de las consultas, el promedio de las atenciones médicas entre $10.000 y $30.000 y el código de la primera atención de un habitual.'],
    ['main()'],
    [('main() corre e imprime algo', 'assert correr_main().strip(), "main() no imprime nada"'),
     ('Muestra el total de las consultas', 'aparece(864634.55, correr_main(), "el total de las consultas")'),
     ('Muestra el promedio entre $10.000 y $30.000', 'aparece(21958.64, correr_main(), "el promedio entre $10.000 y $30.000")')],
    {'main.py': MAIN10}, ejecutar=['main', 'main']),
  ])
