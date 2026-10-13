from comun import *

F = "ar/edu/backend/Servidor.java"

S1 = '''package ar.edu.backend;

public class Servidor {
    private final String id;
    private final String region;
    private final int indiceCarga;

    public Servidor(String id, String region, int indiceCarga) {
        this.id = id;
        this.region = region;
        this.indiceCarga = indiceCarga;
    }

    public String getId() {
        return id;
    }

    public String getRegion() {
        return region;
    }

    public int getIndiceCarga() {
        return indiceCarga;
    }
}
'''

S2 = S1.replace('''    public Servidor(String id, String region, int indiceCarga) {
        this.id = id;''', '''    public Servidor(String id, String region, int indiceCarga) {
        if (id == null || id.isBlank() || region == null || region.isBlank())
            throw new IllegalArgumentException("El id y la region son obligatorios");
        if (indiceCarga < 1 || indiceCarga > 70)
            throw new IllegalArgumentException("El indice de carga esta fuera del rango permitido");
        this.id = id;''')

S3 = S2.replace('''    public int getIndiceCarga() {
        return indiceCarga;
    }
}''', '''    public int getIndiceCarga() {
        return indiceCarga;
    }

    public int costoRiesgoOperativo() {
        return (1000 * indiceCarga) / 100;
    }
}''')

S4 = S3.replace('''    public String getId() {''', '''    public static Servidor desdeCampos(String[] tokens) {
        if (tokens.length != 5)
            throw new IllegalArgumentException("se esperan 5 columnas");
        int usoCpu = Integer.parseInt(tokens[2]);
        int usoMemoria = Integer.parseInt(tokens[3]);
        if (usoCpu < 1 || usoCpu > 100)
            throw new IllegalArgumentException("uso del cpu esta fuera de rango");
        if (usoMemoria < 1 || usoMemoria > 24576)
            throw new IllegalArgumentException("uso de memoria esta fuera de rango");
        int indiceCarga = (int) ((usoCpu * 0.7) + (usoMemoria * 0.3));
        return new Servidor(tokens[0], tokens[1], indiceCarga);
    }

    public String getId() {''')

INICIO = '''package ar.edu.backend;

public class Servidor {
    // Atributos: id, region e indiceCarga (private final)

    // Constructor: Servidor(String id, String region, int indiceCarga)

    // Getters: getId(), getRegion() y getIndiceCarga()
}
'''

E = ej(
    'bk-servidor', 'La clase Servidor', 'Preenunciado 3K1 · Cloud Center',
    'Atributos final, constructor con validaciones, el costo y la fábrica desdeCampos: la base de cualquier preenunciado.',
    [
        h('Cloud Center: la clase Servidor'),
        pr('El departamento de IT recibe un CSV con la telemetría de sus servidores. Cada servidor tiene un id, una región y un índice de carga. Los datos no cambian una vez creado el objeto.', 1),
        li('El id y la región son obligatorios: no pueden ser null ni estar vacíos.', 2),
        li('El índice de carga es un entero entre 1 y 70 (inclusive). El constructor recibe el índice ya calculado.', 1, 2),
        li('Si un dato no cumple, el constructor tira IllegalArgumentException con un mensaje que diga el motivo.', 2),
        pr('El costo del riesgo operativo supone un ingreso promedio de 1000 USD: costo = 1000 × índice / 100. Es un entero: no se usan decimales ni redondeos.', 3),
        pr('La fábrica desdeCampos recibe los campos de una fila del CSV, ya separados y sin espacios: id, region, porcentajeCPU, usoMemoria y estado.', 4),
        li('Tiene que haber exactamente 5 campos.', 4),
        li('El uso de CPU es un entero entre 1 y 100 y el de memoria, entre 1 y 24576.', 4),
        li('El índice de carga es (int) (cpu × 0,7 + memoria × 0,3). Si no queda entre 1 y 70, la fila es inválida: eso ya lo controla el constructor.', 4),
        code('srv-0044,US-WEST-2,67,13,ALERTA  →  índice (int) (46,9 + 3,9) = 50  →  costo 500', 3, 4),
    ],
    {},
    [
        paso('Atributos, constructor y getters', F,
             ['Declará los atributos id, region e indiceCarga como private final.',
              'Escribí el constructor Servidor(String id, String region, int indiceCarga) que los guarde.',
              'Agregá los getters getId(), getRegion() y getIndiceCarga().'],
             ['public Servidor(String id, String region, int indiceCarga)', 'public String getId()', 'public String getRegion()', 'public int getIndiceCarga()'],
             [('El constructor guarda los tres datos', '''
Servidor s = new Servidor("srv-0044", "US-WEST-2", 50);
Prueba.igual("srv-0044", s.getId(), "getId()");
Prueba.igual("US-WEST-2", s.getRegion(), "getRegion()");
Prueba.igual(50, s.getIndiceCarga(), "getIndiceCarga()");
'''),
              ('Cada objeto guarda sus propios datos', '''
Servidor a = new Servidor("a", "R1", 10);
Servidor b = new Servidor("b", "R2", 20);
Prueba.igual("a", a.getId(), "el id del primero");
Prueba.igual(20, b.getIndiceCarga(), "el índice del segundo");
''')],
             {F: S1}, inicio={F: INICIO},
             pistas=['Un atributo final se asigna una sola vez, en el constructor: this.id = id;',
                     'Los getters solo devuelven el atributo: public String getId() { return id; }']),
        paso('Las validaciones del constructor', F,
             ['Si id o region son null o están vacíos, tirá IllegalArgumentException.',
              'Si indiceCarga no está entre 1 y 70, tirá IllegalArgumentException.',
              'Validá antes de asignar: si un dato está mal, el objeto no se crea.'],
             ['throw new IllegalArgumentException("El id y la region son obligatorios")', '1 ≤ indiceCarga ≤ 70'],
             [('Un id null o vacío no se acepta', '''
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor(null, "R1", 10), "id null");
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor("   ", "R1", 10), "id con espacios");
'''),
              ('Una región null o vacía no se acepta', '''
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor("s1", null, 10), "región null");
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor("s1", "", 10), "región vacía");
'''),
              ('Un índice fuera de 1 a 70 no se acepta', '''
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor("s1", "R1", 0), "índice 0");
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor("s1", "R1", 71), "índice 71");
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor("s1", "R1", 1389), "índice 1389");
'''),
              ('Los límites 1 y 70 sí valen', '''
Prueba.noLanza(() -> new Servidor("s1", "R1", 1), "índice 1");
Prueba.noLanza(() -> new Servidor("s1", "R1", 70), "índice 70");
'''),
              ('El error trae un mensaje que explica el motivo', '''
try {
    new Servidor("", "R1", 10);
    Prueba.verdad(false, "tenía que tirar IllegalArgumentException");
} catch (IllegalArgumentException e) {
    Prueba.verdad(e.getMessage() != null && !e.getMessage().isBlank(), "la excepción no tiene mensaje: pasale un texto al crearla");
}
''')],
             {F: S2},
             pistas=['id == null || id.isBlank() cubre los dos casos: isBlank() también da true con "   ".',
                     'if (indiceCarga < 1 || indiceCarga > 70) throw new IllegalArgumentException("…");',
                     'Poné los if al principio del constructor, antes de los this.x = x.']),
        paso('El costo del riesgo operativo', F,
             ['Agregá costoRiesgoOperativo(): 1000 × índice / 100, en enteros.',
              'Multiplicá antes de dividir: con enteros, 1000 * indice / 100 no pierde nada.'],
             ['public int costoRiesgoOperativo()'],
             [('Con índice 50 el costo es 500', '''
Prueba.igual(500, new Servidor("srv-0044", "US-WEST-2", 50).costoRiesgoOperativo(), "costo con índice 50");
'''),
              ('Con índice 59 el costo es 590', '''
Prueba.igual(590, new Servidor("srv-0054", "SA-EAST-1", 59).costoRiesgoOperativo(), "costo con índice 59");
'''),
              ('En los límites: índice 1 da 10 e índice 70 da 700', '''
Prueba.igual(10, new Servidor("a", "R1", 1).costoRiesgoOperativo(), "costo con índice 1");
Prueba.igual(700, new Servidor("b", "R1", 70).costoRiesgoOperativo(), "costo con índice 70");
''')],
             {F: S3},
             pistas=['public int costoRiesgoOperativo() { return (1000 * indiceCarga) / 100; }']),
        paso('La fábrica desdeCampos', F,
             ['Escribí el método estático desdeCampos(String[] tokens), que crea un Servidor con los 5 campos de una fila.',
              'Controlá que haya 5 campos y convertí la CPU y la memoria con Integer.parseInt.',
              'Validá la CPU (1 a 100) y la memoria (1 a 24576) y calculá el índice: (int) (cpu * 0.7 + memoria * 0.3).',
              'Terminá con return new Servidor(…): el constructor controla que el índice quede entre 1 y 70.'],
             ['public static Servidor desdeCampos(String[] tokens)', 'tokens = { id, region, porcentajeCPU, usoMemoria, estado }'],
             [('srv-0044 queda con índice 50 y costo 500', '''
Servidor s = Servidor.desdeCampos(new String[] { "srv-0044", "US-WEST-2", "67", "13", "ALERTA" });
Prueba.igual("srv-0044", s.getId(), "getId()");
Prueba.igual("US-WEST-2", s.getRegion(), "getRegion()");
Prueba.igual(50, s.getIndiceCarga(), "índice de srv-0044");
Prueba.igual(500, s.costoRiesgoOperativo(), "costo de srv-0044");
'''),
              ('Se controla que haya 5 campos', '''
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "10", "10" }), "4 campos");
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "10", "10", "ALERTA", "1200" }), "6 campos");
'''),
              ('Una CPU fuera de 1 a 100 es inválida (srv-0006 tiene 114)', '''
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "srv-0006", "US-WEST-2", "114", "4", "ALERTA" }), "CPU 114");
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "0", "10", "ALERTA" }), "CPU 0");
'''),
              ('Una memoria fuera de 1 a 24576 es inválida', '''
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "10", "0", "ALERTA" }), "memoria 0");
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "10", "24577", "ALERTA" }), "memoria 24577");
'''),
              ('Si el índice da más de 70, también es inválida', '''
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "56", "4500", "CRITICO" }), "CPU 56 y memoria 4500 (índice 1389)");
'''),
              ('Un número mal escrito tira NumberFormatException', '''
Prueba.lanza(NumberFormatException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "abc", "10", "ALERTA" }), "CPU \\"abc\\"");
''')],
             {F: S4},
             pistas=['static: se llama con la clase, Servidor.desdeCampos(campos), sin crear un objeto antes.',
                     'int usoCpu = Integer.parseInt(tokens[2]); — si el texto no es un número, parseInt ya tira NumberFormatException.',
                     'El (int) va afuera del paréntesis: (int) ((usoCpu * 0.7) + (usoMemoria * 0.3)).']),
    ],
    importar=['ar.edu.backend'], grupo='basico', tema='clases')
