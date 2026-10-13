from comun import *

P = "ar/edu/backend/"
FS, FI, FR, FP, FC, FA = P + "Servidor.java", P + "ServidorConIngresos.java", P + "ResultadoParseo.java", P + "ParserServidores.java", P + "Cloud.java", P + "App.java"
ORIG = {f: leer("proyectos", "cloud-center", f.split("/")[-1]) for f in (FS, FR, FP, FC, FA)}


def cambiar(texto, *pares):
    for a, b in pares:
        assert texto.count(a) == 1, a
        texto = texto.replace(a, b)
    return texto


# Paso 1: el estado, con un constructor nuevo (el viejo queda: lo usan los tests)
S1 = cambiar(ORIG[FS],
    ('''    private final int indiceCarga;
''', '''    private final int indiceCarga;
    private final String estado;
'''),
    ('''    public Servidor(String id, String region, int indiceCarga) {
''', '''    public Servidor(String id, String region, int indiceCarga) {
        this(id, region, indiceCarga, "SIN ESTADO");
    }

    public Servidor(String id, String region, int indiceCarga, String estado) {
'''),
    ('''        this.indiceCarga = indiceCarga;
    }''', '''        this.indiceCarga = indiceCarga;
        this.estado = estado;
    }'''),
    ('''        return new Servidor(tokens[0], tokens[1], indiceCarga);''', '''        return new Servidor(tokens[0], tokens[1], indiceCarga, tokens[4]);'''),
    ('''    public int getIndiceCarga() {
        return indiceCarga;
    }''', '''    public int getIndiceCarga() {
        return indiceCarga;
    }

    public String getEstado() {
        return estado;
    }'''))

# Paso 2: el gancho que la subclase va a redefinir
S2 = cambiar(S1,
    ('''    public int costoRiesgoOperativo() {
        int v = (INGRESO_PROMEDIO * this.indiceCarga) / 100;
        return v;
    }''', '''    /** El ingreso por hora para el costo. Una subclase lo puede redefinir. */
    protected int ingresoPorHora() {
        return INGRESO_PROMEDIO;
    }

    public int costoRiesgoOperativo() {
        return (this.ingresoPorHora() * this.indiceCarga) / 100;
    }'''))

CONINGRESOS = '''package ar.edu.backend;

public class ServidorConIngresos extends Servidor {
    private final int ingresos;

    public ServidorConIngresos(String id, String region, int indiceCarga, String estado, int ingresos) {
        super(id, region, indiceCarga, estado);
        if (ingresos < 1000 || ingresos >= 1900)
            throw new IllegalArgumentException("los ingresos estan fuera de rango");
        this.ingresos = ingresos;
    }

    public int getIngresos() {
        return ingresos;
    }

    @Override
    protected int ingresoPorHora() {
        return ingresos;
    }
}
'''
CONINGRESOS_INICIO = '''package ar.edu.backend;

public class ServidorConIngresos extends Servidor {
    // El dato nuevo: ingresos (private final)

    public ServidorConIngresos(String id, String region, int indiceCarga, String estado, int ingresos) {
        super(id, region, indiceCarga, estado);   // primero: la base valida lo de siempre
        // después: validá 1000 <= ingresos < 1900 y guardalos
    }

    // getIngresos() y la redefinición de ingresoPorHora()
}
'''

# Paso 4: la fábrica elige qué objeto crear
S4 = cambiar(S2,
    ('''        if (tokens.length != 5)
            throw new IllegalArgumentException("se esperan 5 columnas");''', '''        if (tokens.length != 5 && tokens.length != 6)
            throw new IllegalArgumentException("se esperan 5 o 6 columnas");'''),
    ('''        return new Servidor(tokens[0], tokens[1], indiceCarga, tokens[4]);''', '''        if (tokens.length == 6)
            return new ServidorConIngresos(tokens[0], tokens[1], indiceCarga, tokens[4], Integer.parseInt(tokens[5]));
        return new Servidor(tokens[0], tokens[1], indiceCarga, tokens[4]);'''))

# Paso 5: un solo parser; el encabezado dice cuántas columnas tiene cada fila
P5 = cambiar(ORIG[FP],
    ('''    private static final String CABECERA = "id,region,porcentajeCPU,usoMemoria,estado";''', '''    private static final String CABECERA = "id,region,porcentajeCPU,usoMemoria,estado";
    private static final String CABECERA_INGRESOS = CABECERA + ",ingresos";'''),
    ('''            if (!CABECERA.equals(lector.readLine()))
                throw new IllegalArgumentException("encabezado incorrecto");''', '''            String cabecera = lector.readLine();
            int columnas;
            if (CABECERA.equals(cabecera))
                columnas = 5;
            else if (CABECERA_INGRESOS.equals(cabecera))
                columnas = 6;
            else
                throw new IllegalArgumentException("encabezado incorrecto");'''),
    ('''                    if (tokens.length != 5)''', '''                    if (tokens.length != columnas)'''))

# Paso 6: el conteo por estado en el colector
C6 = cambiar(ORIG[FC],
    ('''    public String panorama() {''', '''    /** Cuántos servidores hay en cada estado. Vacío si no hay servidores. */
    public Map<String, Long> conteoPorEstado() {
        return this.servidores.stream()
                .collect(Collectors.groupingBy(Servidor::getEstado, TreeMap::new, Collectors.counting()));
    }

    public String panorama() {'''))

# Paso 7: el main del parcial
A7 = cambiar(ORIG[FA],
    ('''import java.nio.file.Path;''', '''import java.nio.file.Path;
import java.util.Map;'''),
    ('''        Path archivo = Path.of(args.length == 0 ? "datos/datos.csv" : args[0]);''', '''        Path archivo = Path.of(args.length == 0 ? "datos/datos-parcial.csv" : args[0]);'''),
    ('''        System.out.println(colector.panorama());''', '''        Map<String, Long> porEstado = colector.conteoPorEstado();
        System.out.println("ALERTA: %d | CRITICO: %d".formatted(
                porEstado.getOrDefault("ALERTA", 0L), porEstado.getOrDefault("CRITICO", 0L)));
        System.out.println(colector.panorama());'''))

NUEVO = "id,region,porcentajeCPU,usoMemoria,estado,ingresos"
VIEJO = "id,region,porcentajeCPU,usoMemoria,estado"

E = ej(
    'bk-parcial-3k1', 'Parcial 3K1 · Ingreso promedio por servidor', 'Parcial tomado · 3K1 · 19/09/2026',
    'El parcial real, de a pasos y con los mismos controles que mira el profe: el dato nuevo con herencia, los dos formatos, el conteo y el main.',
    [
        h('Parcial práctico: ingreso promedio por servidor'),
        pr('Partir exactamente del proyecto del preparcial (Cloud Center). El departamento de IT incorpora para cada servidor el ingreso promedio por hora que genera. Hay que procesar el dato nuevo con la misma colección y obtener los costos y totales correctos.', 3),
        h('Reglas nuevas'),
        li('El nuevo encabezado es id,region,porcentajeCPU,usoMemoria,estado,ingresos. El formato original de cinco columnas sigue valiendo: ahí todos los servidores tienen el ingreso de 1000.', 4, 5),
        li('Cada fila tiene que tener el ancho de su encabezado: no se aceptan filas de cinco campos con un encabezado de seis, ni al revés.', 5),
        li('Para ALERTA o CRITICO del formato nuevo, el sexto campo admite valores mayores o iguales a 1000 y menores a 1900, después de sacar los espacios de afuera. Un valor fuera de rango hace inválida la fila.', 3, 4),
        li('Se conservan todas las validaciones del preenunciado. El costo del riesgo operativo tiene que usar el ingreso de la fila, sin cambiar la estructura de objetos del preparcial.', 2, 3),
        code('srv-0054,SA-EAST-1,59,59,ALERTA,  1110  →  índice 59, ingreso 1110  →  costo 1110 × 59 / 100 = 654', 3, 4),
        h('Resultado requerido'),
        li('1. Leer las dos versiones del CSV sin duplicar el proceso de carga.', 4, 5),
        li('2. Que costoRiesgoOperativo(), total(), los filtros y los totales por región reflejen la regla nueva.', 2, 3, 6),
        li('3. Agregar en el colector un conteo por estado (vacío o en cero si no hay servidores).', 1, 6),
        li('4. Que el main use por defecto el archivo del parcial y muestre el resumen, la cantidad de objetos, las cantidades ALERTA y CRITICO, el total y los totales por región. Los cálculos siguen en las clases.', 7),
        li('5. Pasar los tests viejos y los nuevos: los constructores que ya existían no se tocan.', 1),
    ],
    {'datos/datos.csv': leer('datos', 'servidores.csv'), 'datos/datos-parcial.csv': leer('datos', 'servidores-parcial.csv')},
    [
        paso('El estado en Servidor (sin romper los tests)', FS,
             ['Para contar por estado, Servidor tiene que guardar el estado: agregá el atributo private final String estado y getEstado().',
              'Agregá un constructor nuevo de 4 parámetros (…, String estado) con las validaciones.',
              'No borres ni cambies el de 3 parámetros: lo usan los tests viejos. Que llame al nuevo con this(id, region, indiceCarga, "SIN ESTADO").',
              'En desdeCampos, creá el Servidor con el estado de la fila (tokens[4]).'],
             ['public Servidor(String id, String region, int indiceCarga)  ← queda', 'public Servidor(String id, String region, int indiceCarga, String estado)', 'public String getEstado()'],
             [('El constructor de 3 parámetros sigue andando', '''
Prueba.igual(400, new Servidor("srv-1", "R1", 40).costoRiesgoOperativo(), "costo con el constructor de 3 parámetros");
'''),
              ('El constructor de 4 parámetros guarda el estado', '''
Prueba.igual("ALERTA", new Servidor("srv-1", "R1", 40, "ALERTA").getEstado(), "getEstado()");
'''),
              ('desdeCampos guarda el estado de la fila', '''
Servidor s = Servidor.desdeCampos(new String[] { "srv-0044", "US-WEST-2", "67", "13", "CRITICO" });
Prueba.igual("CRITICO", s.getEstado(), "estado de srv-0044");
Prueba.igual(500, s.costoRiesgoOperativo(), "costo de srv-0044");
'''),
              ('Las validaciones también valen con el constructor nuevo', '''
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor("", "R1", 40, "ALERTA"), "id vacío");
Prueba.lanza(IllegalArgumentException.class, () -> new Servidor("srv-1", "R1", 80, "ALERTA"), "índice 80");
''')],
             {FS: S1}, inicio=dict(ORIG),
             pistas=['Sobrecarga: dos constructores con el mismo nombre y distintos parámetros. El de 3 queda así: public Servidor(String id, String region, int indiceCarga) { this(id, region, indiceCarga, "SIN ESTADO"); }',
                     'this(…) tiene que ser la primera línea del constructor.',
                     'Cambiar la firma del constructor viejo es el error que más puntos hace perder: los tests no compilan y no corre ninguno.']),
        paso('El gancho: ingresoPorHora()', FS,
             ['Agregá en Servidor un método protected int ingresoPorHora() que devuelva INGRESO_PROMEDIO (1000).',
              'Hacé que costoRiesgoOperativo() use ingresoPorHora() en lugar de la constante: (ingresoPorHora() * indiceCarga) / 100.',
              'Así el cálculo queda en un solo lugar y una subclase solo tiene que redefinir el ingreso.'],
             ['protected int ingresoPorHora()', 'public int costoRiesgoOperativo()  ← usa ingresoPorHora()'],
             [('El costo de siempre no cambia: índice 59 da 590', '''
Prueba.igual(590, new Servidor("srv-0054", "SA-EAST-1", 59, "ALERTA").costoRiesgoOperativo(), "costo con índice 59");
'''),
              ('costoRiesgoOperativo() usa ingresoPorHora() (una subclase lo puede redefinir)', '''
class Doble extends Servidor {
    Doble() { super("x", "R1", 50, "ALERTA"); }
    protected int ingresoPorHora() { return 2000; }
}
Prueba.igual(1000, new Doble().costoRiesgoOperativo(), "costo de una subclase que redefine ingresoPorHora() en 2000 (índice 50)");
''')],
             {FS: S2},
             pistas=['protected: lo ven la clase, sus subclases (aunque estén en otro paquete) y el paquete. private no se puede redefinir.',
                     'public int costoRiesgoOperativo() { return (this.ingresoPorHora() * this.indiceCarga) / 100; }']),
        paso('La subclase ServidorConIngresos', FI,
             ['Creá ServidorConIngresos extends Servidor con el atributo ingresos.',
              'El constructor recibe (id, region, indiceCarga, estado, ingresos): primero llama a super(…), que valida lo de siempre, y después valida 1000 ≤ ingresos < 1900.',
              'Redefiní ingresoPorHora() para que devuelva ingresos, y agregá getIngresos().'],
             ['public class ServidorConIngresos extends Servidor', 'public ServidorConIngresos(String id, String region, int indiceCarga, String estado, int ingresos)', 'protected int ingresoPorHora()  ← redefinido', 'public int getIngresos()'],
             [('Con índice 59 e ingresos 1110, el costo es 654', '''
Prueba.igual(654, new ServidorConIngresos("srv-0054", "SA-EAST-1", 59, "ALERTA", 1110).costoRiesgoOperativo(), "costo con índice 59 e ingresos 1110");
'''),
              ('Guarda los ingresos y el resto de los datos', '''
ServidorConIngresos s = new ServidorConIngresos("srv-0123", "US-WEST-2", 53, "ALERTA", 1253);
Prueba.igual(1253, s.getIngresos(), "getIngresos()");
Prueba.igual("US-WEST-2", s.getRegion(), "getRegion()");
Prueba.igual(664, s.costoRiesgoOperativo(), "costo con índice 53 e ingresos 1253");
'''),
              ('Los ingresos tienen que estar entre 1000 y 1899', '''
Prueba.lanza(IllegalArgumentException.class, () -> new ServidorConIngresos("s", "R1", 50, "ALERTA", 999), "ingresos 999");
Prueba.lanza(IllegalArgumentException.class, () -> new ServidorConIngresos("s", "R1", 50, "ALERTA", 1900), "ingresos 1900");
Prueba.noLanza(() -> new ServidorConIngresos("s", "R1", 50, "ALERTA", 1000), "ingresos 1000");
Prueba.noLanza(() -> new ServidorConIngresos("s", "R1", 50, "ALERTA", 1899), "ingresos 1899");
'''),
              ('Las validaciones de Servidor siguen valiendo', '''
Prueba.lanza(IllegalArgumentException.class, () -> new ServidorConIngresos("s", "R1", 80, "ALERTA", 1200), "índice 80");
'''),
              ('El colector la usa sin cambios: es un Servidor (polimorfismo)', '''
List<Servidor> l = List.of(new ServidorConIngresos("a", "R1", 59, "ALERTA", 1110), new Servidor("b", "R1", 40, "CRITICO"));
Prueba.igual(654 + 400, new Cloud(l).total(), "total() con un servidor de cada clase");
''')],
             {FI: CONINGRESOS}, inicio={FI: CONINGRESOS_INICIO},
             pistas=['super(id, region, indiceCarga, estado); tiene que ser la primera línea del constructor.',
                     'if (ingresos < 1000 || ingresos >= 1900) throw new IllegalArgumentException("…");',
                     '@Override protected int ingresoPorHora() { return ingresos; }  — el costo no se reescribe: ya lo calcula Servidor con el gancho.']),
        paso('desdeCampos: 5 o 6 campos', FS,
             ['desdeCampos ahora acepta 5 o 6 campos (cualquier otra cantidad sigue siendo un error).',
              'Con 6 campos, creá un ServidorConIngresos con Integer.parseInt(tokens[5]). Con 5, un Servidor como antes.',
              'Es la clave del parcial: si la fábrica no crea la subclase, el dato nuevo nunca se usa en el costo.'],
             ['public static Servidor desdeCampos(String[] tokens)  ← 5 o 6 campos'],
             [('Con 6 campos crea un ServidorConIngresos (costo 654)', '''
Servidor s = Servidor.desdeCampos(new String[] { "srv-0054", "SA-EAST-1", "59", "59", "ALERTA", "1110" });
Prueba.verdad(s instanceof ServidorConIngresos, "con 6 campos tiene que crear un ServidorConIngresos");
Prueba.igual(654, s.costoRiesgoOperativo(), "costo de srv-0054");
'''),
              ('Con 5 campos sigue creando un Servidor común', '''
Servidor s = Servidor.desdeCampos(new String[] { "srv-0054", "SA-EAST-1", "59", "59", "ALERTA" });
Prueba.verdad(!(s instanceof ServidorConIngresos), "con 5 campos tiene que ser un Servidor común");
Prueba.igual(590, s.costoRiesgoOperativo(), "costo de srv-0054 sin ingresos");
'''),
              ('Un sexto campo inválido no crea el servidor', '''
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "59", "59", "ALERTA", "999" }), "ingresos 999");
Prueba.lanza(NumberFormatException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "59", "59", "ALERTA", "" }), "ingresos vacío");
'''),
              ('Otra cantidad de campos sigue siendo un error', '''
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "59", "59" }), "4 campos");
Prueba.lanza(IllegalArgumentException.class, () -> Servidor.desdeCampos(new String[] { "s", "R1", "59", "59", "ALERTA", "1110", "x" }), "7 campos");
''')],
             {FS: S4},
             pistas=['if (tokens.length != 5 && tokens.length != 6) throw new IllegalArgumentException("se esperan 5 o 6 columnas");',
                     'if (tokens.length == 6) return new ServidorConIngresos(tokens[0], tokens[1], indiceCarga, tokens[4], Integer.parseInt(tokens[5]));',
                     'Las validaciones de CPU y memoria quedan antes: valen para los dos formatos.']),
        paso('Un solo parser para los dos formatos', FP,
             ['Leé el encabezado una vez: si es el viejo, cada fila tiene que tener 5 columnas; si es el nuevo (con ",ingresos"), 6. Si no es ninguno, IllegalArgumentException.',
              'Cambiá el control de cada fila para que compare con esa cantidad, no con 5.',
              'Todo lo demás queda igual: ESTABLE se descarta, el estado desconocido es inválido y desdeCampos crea el objeto.'],
             ['private static final String CABECERA_INGRESOS = CABECERA + ",ingresos";', 'tokens.length != columnas  ← la de su encabezado'],
             [('El archivo viejo sigue igual: 30 procesadas, 21 descartadas y 9 inválidas', '''
ResultadoParseo r = new ParserServidores().leer(Path.of("datos/datos.csv"));
Prueba.igual(30, r.getProcesadas(), "procesadas de datos.csv");
Prueba.igual(21, r.getDescartadas(), "descartadas de datos.csv");
Prueba.igual(9, r.getInvalidas(), "inválidas de datos.csv");
'''),
              ('El formato nuevo: 2 procesadas, 1 inválida y el primero cuesta 654', '''
Path p = Prueba.archivo("datos/nuevo.csv", "''' + NUEVO + '''\\nsrv-0054,SA-EAST-1,59,59,ALERTA,  1110\\nsrv-0027,SA-EAST-1,98,17934,CRITICO,   1679\\nsrv-0123,US-WEST-2,56,47,ALERTA,   1253\\n");
ResultadoParseo r = new ParserServidores().leer(p);
Prueba.igual(2, r.getProcesadas(), "procesadas");
Prueba.igual(1, r.getInvalidas(), "inválidas");
Prueba.igual(654, r.getServidores().get(0).costoRiesgoOperativo(), "costo de srv-0054");
'''),
              ('Cada fila tiene que tener el ancho de su encabezado', '''
Path p = Prueba.archivo("datos/mezcla6.csv", "''' + NUEVO + '''\\nsrv-1,R1,59,59,ALERTA\\nsrv-2,R1,59,59,ALERTA,1110\\n");
Prueba.igual(1, new ParserServidores().leer(p).getProcesadas(), "procesadas con encabezado de 6 (una fila tiene 5)");
Path q = Prueba.archivo("datos/mezcla5.csv", "''' + VIEJO + '''\\nsrv-1,R1,59,59,ALERTA,1110\\nsrv-2,R1,59,59,ALERTA\\n");
Prueba.igual(1, new ParserServidores().leer(q).getProcesadas(), "procesadas con encabezado de 5 (una fila tiene 6)");
'''),
              ('Un encabezado desconocido sigue cortando la lectura', '''
Path p = Prueba.archivo("datos/otro.csv", "id,region,cpu,memoria,estado,ingresos\\n");
Prueba.lanza(IllegalArgumentException.class, () -> new ParserServidores().leer(p), "encabezado desconocido");
'''),
              ('datos-parcial.csv: 140 leídas, 49 procesadas, 70 descartadas y 21 inválidas', '''
ResultadoParseo r = new ParserServidores().leer(Path.of("datos/datos-parcial.csv"));
Prueba.igual(140, r.getLeidas(), "leídas");
Prueba.igual(49, r.getProcesadas(), "procesadas");
Prueba.igual(70, r.getDescartadas(), "descartadas");
Prueba.igual(21, r.getInvalidas(), "inválidas");
''')],
             {FP: P5},
             pistas=['String cabecera = lector.readLine(); int columnas; if (CABECERA.equals(cabecera)) columnas = 5; else if (CABECERA_INGRESOS.equals(cabecera)) columnas = 6; else throw …',
                     'El "  1110 " con espacios no es problema: el parser ya hace strip() a cada campo antes de desdeCampos.',
                     'Una sola carga para los dos formatos: no copies el método leer.']),
        paso('Contar por estado en el colector', FC,
             ['Agregá en Cloud conteoPorEstado(): agrupá por getEstado con Collectors.counting().',
              'Usá TreeMap::new como segundo argumento de groupingBy para que salga ordenado.',
              'total(), filtrar() y totalesPorRegion() no se tocan: ya llaman a costoRiesgoOperativo() y el polimorfismo hace el resto.'],
             ['public Map<String, Long> conteoPorEstado()'],
             [('Cuenta por estado: ALERTA 2 y CRITICO 1', '''
List<Servidor> l = List.of(new Servidor("a", "R1", 10, "ALERTA"), new Servidor("b", "R1", 10, "CRITICO"), new Servidor("c", "R2", 10, "ALERTA"));
Prueba.igual(Map.of("ALERTA", 2L, "CRITICO", 1L), new Cloud(l).conteoPorEstado(), "conteoPorEstado()");
'''),
              ('Sin servidores, el conteo está vacío', '''
Prueba.verdad(new Cloud(List.of()).conteoPorEstado().isEmpty(), "con un Cloud vacío el conteo tiene que estar vacío");
'''),
              ('Con datos-parcial.csv: 49 en ALERTA (ningún CRITICO se procesa)', '''
List<Servidor> s = new ParserServidores().leer(Path.of("datos/datos-parcial.csv")).getServidores();
Prueba.igual(Map.of("ALERTA", 49L), new Cloud(s).conteoPorEstado(), "conteoPorEstado() con datos-parcial.csv");
'''),
              ('total() y totalesPorRegion() ya usan los ingresos, sin tocarlos', '''
Cloud c = new Cloud(new ParserServidores().leer(Path.of("datos/datos-parcial.csv")).getServidores());
Prueba.igual(35800, c.total(), "total() con datos-parcial.csv");
Prueba.igual(Map.of("SA-EAST-1", 12085, "US-EAST-1", 12712, "US-WEST-2", 11003), c.totalesPorRegion(), "totalesPorRegion() con datos-parcial.csv");
''')],
             {FC: C6},
             pistas=['this.servidores.stream().collect(Collectors.groupingBy(Servidor::getEstado, TreeMap::new, Collectors.counting()))',
                     'Para "ALERTA o CRITICO" en un filtro es ||: con && no se cumple nunca para un mismo servidor.']),
        paso('El main del parcial', FA,
             ['Por defecto, el main lee datos/datos-parcial.csv (si llega un argumento, usa ese archivo).',
              'Mostrá ALERTA y CRITICO por separado, aunque alguno dé 0: getOrDefault("CRITICO", 0L).',
              'Lo demás sigue igual: el informe, los descartes, los errores y el panorama. Los cálculos quedan en las clases.'],
             ['Path.of(args.length == 0 ? "datos/datos-parcial.csv" : args[0])', '"ALERTA: %d | CRITICO: %d"'],
             [('Por defecto lee datos/datos-parcial.csv', '''
String s = Prueba.salida(() -> App.main(new String[0]));
Prueba.contiene(s, "Leídas: 140 | procesadas: 49", "lo que muestra el main sin argumentos");
Prueba.contiene(s, "objetos: 49", "lo que muestra el main sin argumentos");
'''),
              ('Muestra ALERTA y CRITICO por separado (CRITICO en 0)', '''
String s = Prueba.salida(() -> App.main(new String[0]));
Prueba.contiene(s, "ALERTA: 49", "lo que muestra el main");
Prueba.contiene(s, "CRITICO: 0", "lo que muestra el main");
'''),
              ('Muestra el total y los totales por región', '''
String s = Prueba.salida(() -> App.main(new String[0]));
Prueba.contiene(s, "Total: 35800", "lo que muestra el main");
Prueba.contiene(s, "SA-EAST-1=12085", "lo que muestra el main");
'''),
              ('Con datos/datos.csv sigue mostrando lo de antes', '''
String s = Prueba.salida(() -> App.main(new String[] { "datos/datos.csv" }));
Prueba.contiene(s, "procesadas: 30", "lo que muestra el main con datos/datos.csv");
Prueba.contiene(s, "Total: 15170", "lo que muestra el main con datos/datos.csv");
''')],
             {FA: A7}, ejecutar={'entrada': FA, 'args': []},
             pistas=['Map<String, Long> porEstado = colector.conteoPorEstado();',
                     'System.out.println("ALERTA: %d | CRITICO: %d".formatted(porEstado.getOrDefault("ALERTA", 0L), porEstado.getOrDefault("CRITICO", 0L)));',
                     'Antes de entregar: el profe corre el main con los dos archivos. Probá con ▶ Ejecutar.']),
    ],
    importar=['ar.edu.backend'], grupo='parcial', tema='parcial')
