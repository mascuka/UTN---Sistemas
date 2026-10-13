from comun import *
from ej1 import S4 as SERVIDOR
from ej2 import RESULTADO, P4 as PARSER

FS = "ar/edu/backend/Servidor.java"
FR = "ar/edu/backend/ResultadoParseo.java"
FP = "ar/edu/backend/ParserServidores.java"
FC = "ar/edu/backend/Cloud.java"
FA = "ar/edu/backend/App.java"

CAB = '''package ar.edu.backend;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class Cloud {
    private final List<Servidor> servidores;
'''

INICIO = CAB + '''
    public Cloud(List<Servidor> servidores) {
        // Guardá una copia que no se pueda modificar
        this.servidores = servidores;
    }

    public List<Servidor> getServidores() {
        return servidores;
    }
}
'''

M1 = '''
    public Cloud(List<Servidor> servidores) {
        this.servidores = List.copyOf(servidores);
    }

    public List<Servidor> getServidores() {
        return servidores;
    }
'''
M2 = '''
    public int total() {
        return servidores.stream().mapToInt(Servidor::costoRiesgoOperativo).sum();
    }
'''
M3 = '''
    public List<Servidor> filtrar(Predicate<Servidor> criterio) {
        return servidores.stream().filter(criterio).toList();
    }
'''
M4 = '''
    public Map<String, Integer> totalesPorRegion() {
        return servidores.stream()
                .collect(Collectors.groupingBy(Servidor::getRegion, Collectors.summingInt(Servidor::costoRiesgoOperativo)));
    }
'''
M5 = '''
    public Map<String, Long> cantidadPorRegion() {
        return servidores.stream().collect(Collectors.groupingBy(Servidor::getRegion, Collectors.counting()));
    }

    public Map<String, Double> promedioPorRegion() {
        return servidores.stream()
                .collect(Collectors.groupingBy(Servidor::getRegion, Collectors.averagingInt(Servidor::costoRiesgoOperativo)));
    }
'''
M6 = '''
    public Optional<Servidor> masCaro() {
        return servidores.stream().max(Comparator.comparingInt(Servidor::costoRiesgoOperativo));
    }

    public List<Servidor> masCaros(int cantidad) {
        return servidores.stream()
                .sorted(Comparator.comparingInt(Servidor::costoRiesgoOperativo).reversed())
                .limit(cantidad)
                .toList();
    }
'''
M7 = '''
    public String panorama() {
        return "Total: %d | Por Region: %s | indice menores a 50: %d".formatted(
                total(), new TreeMap<>(totalesPorRegion()), filtrar(s -> s.getIndiceCarga() < 50).size());
    }
'''
C = lambda *ms: CAB + "".join(ms) + "}\n"

APP_INICIO = '''package ar.edu.backend;

import java.io.IOException;
import java.nio.file.Path;

public class App {
    public static void main(String[] args) throws IOException {
        // 1. El archivo: datos/datos.csv, o el que llegue en args[0]
        // 2. Leerlo con ParserServidores y armar el Cloud con los servidores
        // 3. Mostrar el informe, los descartes, los errores y el panorama
    }
}
'''
APP = '''package ar.edu.backend;

import java.io.IOException;
import java.nio.file.Path;

public class App {
    public static void main(String[] args) throws IOException {
        Path archivo = Path.of(args.length == 0 ? "datos/datos.csv" : args[0]);
        ResultadoParseo resultado = new ParserServidores().leer(archivo);
        Cloud colector = new Cloud(resultado.getServidores());

        System.out.println(resultado.informe());
        resultado.getDescartes().forEach(System.out::println);
        resultado.getErrores().forEach(System.out::println);
        System.out.println(colector.panorama());
    }
}
'''

# Tres servidores chicos para probar: costos 500, 590 y 100
TRES = '''List<Servidor> tres = List.of(new Servidor("a", "R1", 50), new Servidor("b", "R2", 59), new Servidor("c", "R1", 10));'''
REALES = '''List<Servidor> reales = new ParserServidores().leer(Path.of("datos/datos.csv")).getServidores();'''

E = ej(
    'bk-streams', 'Consultas con Streams: el colector Cloud', 'Preenunciado 3K1 · Cloud Center',
    'Copia defensiva, mapToInt, filter, groupingBy con summingInt, counting y averagingInt, max y sorted: todo lo que piden las preguntas del parcial.',
    [
        h('Cloud Center: el colector'),
        pr('Cloud guarda los servidores que se procesaron y responde las consultas. Recibe la lista en el constructor y se queda con una copia que no se puede modificar: si después alguien cambia la lista original, el colector no se entera.', 1),
        li('total(): la suma del costo del riesgo operativo de todos los servidores.', 2),
        li('filtrar(criterio): los servidores que cumplen un Predicate<Servidor> (por ejemplo, índice menor a 50).', 3),
        li('totalesPorRegion(): un Map con la suma de costos de cada región.', 4),
        li('cantidadPorRegion() y promedioPorRegion(): cuántos servidores hay en cada región y el costo promedio de cada una.', 5),
        li('masCaro() y masCaros(n): el servidor de mayor costo (puede no haber) y los n más caros, de mayor a menor.', 6),
        li('panorama(): "Total: %d | Por Region: %s | indice menores a 50: %d", con las regiones ordenadas (TreeMap).', 7),
        pr('El main lee datos/datos.csv (o el archivo que llegue como argumento) y muestra el informe, los descartes, los errores y el panorama. Panorama esperado: total 15170, por región SA-EAST-1 5400, US-EAST-1 6790 y US-WEST-2 2980, y 16 servidores con índice menor a 50.', 7),
    ],
    {'datos/datos.csv': leer('datos', 'servidores.csv')},
    [
        paso('El colector y la copia defensiva', FC,
             ['En el constructor, guardá List.copyOf(servidores) en lugar de la lista que llega.',
              'getServidores() devuelve esa copia: como es inmodificable, nadie puede agregar ni sacar servidores desde afuera.'],
             ['public Cloud(List<Servidor> servidores)', 'public List<Servidor> getServidores()'],
             [('Guarda los servidores', TRES + '''
Prueba.igual(3, new Cloud(tres).getServidores().size(), "cantidad de servidores");
'''),
              ('Si después cambia la lista original, el colector no se entera', '''
List<Servidor> lista = new ArrayList<>(List.of(new Servidor("a", "R1", 50), new Servidor("b", "R2", 59)));
Cloud c = new Cloud(lista);
lista.clear();
Prueba.igual(2, c.getServidores().size(), "servidores del Cloud después de vaciar la lista original");
'''),
              ('La lista que devuelve no se puede modificar', TRES + '''
Cloud c = new Cloud(tres);
Prueba.lanza(UnsupportedOperationException.class, () -> c.getServidores().add(new Servidor("d", "R3", 5)), "agregar a getServidores()");
''')],
             {FC: C(M1)}, inicio={FS: SERVIDOR, FR: RESULTADO, FP: PARSER, FC: INICIO},
             pistas=['this.servidores = List.copyOf(servidores);',
                     'List.copyOf hace una copia superficial (copia las referencias) e inmodificable: si alguien intenta un add, sale UnsupportedOperationException.']),
        paso('total(): sumar con mapToInt', FC,
             ['Recorré los servidores con stream(), convertí cada uno en su costo con mapToInt y sumalos con sum().'],
             ['public int total()'],
             [('Suma los costos: 500 + 590 + 100 = 1190', TRES + '''
Prueba.igual(1190, new Cloud(tres).total(), "total de los tres servidores");
'''),
              ('Sin servidores, el total es 0', '''
Prueba.igual(0, new Cloud(List.of()).total(), "total de un Cloud vacío");
'''),
              ('Con datos/datos.csv el total es 15170', REALES + '''
Prueba.igual(15170, new Cloud(reales).total(), "total con datos/datos.csv");
''')],
             {FC: C(M1, M2)},
             pistas=['servidores.stream().mapToInt(Servidor::costoRiesgoOperativo).sum()',
                     'mapToInt devuelve un IntStream: ahí ya tenés sum(), average() y max().']),
        paso('filtrar(): un Predicate', FC,
             ['filtrar recibe un Predicate<Servidor> (una condición) y devuelve los servidores que la cumplen.',
              'Usá filter(criterio) y terminá con toList().'],
             ['public List<Servidor> filtrar(Predicate<Servidor> criterio)'],
             [('Filtra por índice: 16 servidores con índice menor a 50', REALES + '''
Prueba.igual(16, new Cloud(reales).filtrar(s -> s.getIndiceCarga() < 50).size(), "servidores con índice menor a 50");
'''),
              ('Filtra por región: 13 servidores en US-EAST-1', REALES + '''
Prueba.igual(13, new Cloud(reales).filtrar(s -> s.getRegion().equals("US-EAST-1")).size(), "servidores de US-EAST-1");
'''),
              ('Devuelve los que cumplen, sin cambiar el colector', TRES + '''
Cloud c = new Cloud(tres);
List<Servidor> r1 = c.filtrar(s -> s.getRegion().equals("R1"));
Prueba.igual(2, r1.size(), "servidores de R1");
Prueba.igual("a", r1.get(0).getId(), "el primero de R1");
Prueba.igual(3, c.getServidores().size(), "el Cloud sigue con los tres");
''')],
             {FC: C(M1, M2, M3)},
             pistas=['return servidores.stream().filter(criterio).toList();',
                     'El Predicate se escribe al llamar: c.filtrar(s -> s.getIndiceCarga() < 50).']),
        paso('totalesPorRegion(): groupingBy y summingInt', FC,
             ['Agrupá por región con Collectors.groupingBy(Servidor::getRegion, …).',
              'Como segundo argumento, Collectors.summingInt(Servidor::costoRiesgoOperativo) suma el costo de cada grupo.'],
             ['public Map<String, Integer> totalesPorRegion()'],
             [('Suma por región: R1 = 600 y R2 = 590', TRES + '''
Prueba.igual(Map.of("R1", 600, "R2", 590), new Cloud(tres).totalesPorRegion(), "totales por región");
'''),
              ('Con datos/datos.csv: SA-EAST-1 5400, US-EAST-1 6790 y US-WEST-2 2980', REALES + '''
Prueba.igual(Map.of("SA-EAST-1", 5400, "US-EAST-1", 6790, "US-WEST-2", 2980), new Cloud(reales).totalesPorRegion(), "totales por región");
'''),
              ('Sin servidores, un mapa vacío', '''
Prueba.verdad(new Cloud(List.of()).totalesPorRegion().isEmpty(), "con un Cloud vacío tiene que dar un mapa vacío");
''')],
             {FC: C(M1, M2, M3, M4)},
             pistas=['servidores.stream().collect(Collectors.groupingBy(Servidor::getRegion, Collectors.summingInt(Servidor::costoRiesgoOperativo)))',
                     'groupingBy solo, sin el segundo argumento, daría Map<String, List<Servidor>>.']),
        paso('Contar y promediar por región', FC,
             ['cantidadPorRegion(): groupingBy con Collectors.counting() (da Long).',
              'promedioPorRegion(): groupingBy con Collectors.averagingInt(Servidor::costoRiesgoOperativo) (da Double).',
              'Es la pregunta del parcial: para el promedio de enteros, el colector justo es averagingInt.'],
             ['public Map<String, Long> cantidadPorRegion()', 'public Map<String, Double> promedioPorRegion()'],
             [('Cuenta por región: 11, 13 y 6', REALES + '''
Prueba.igual(Map.of("SA-EAST-1", 11L, "US-EAST-1", 13L, "US-WEST-2", 6L), new Cloud(reales).cantidadPorRegion(), "cantidad por región");
'''),
              ('Promedia por región: R1 = (500 + 100) / 2 = 300', TRES + '''
Map<String, Double> p = new Cloud(tres).promedioPorRegion();
Prueba.igual((Object) 300.0, p.get("R1"), "promedio de R1");
Prueba.igual((Object) 590.0, p.get("R2"), "promedio de R2");
'''),
              ('Con datos/datos.csv, US-EAST-1 promedia 522,3', REALES + '''
Prueba.igual((Object) (6790.0 / 13), new Cloud(reales).promedioPorRegion().get("US-EAST-1"), "promedio de US-EAST-1");
''')],
             {FC: C(M1, M2, M3, M4, M5)},
             pistas=['Collectors.groupingBy(Servidor::getRegion, Collectors.counting())',
                     'Collectors.groupingBy(Servidor::getRegion, Collectors.averagingInt(Servidor::costoRiesgoOperativo))',
                     'summarizingInt también trae el promedio, pero junto con cantidad, suma, mínimo y máximo: es más de lo que se pide.']),
        paso('El más caro y los primeros', FC,
             ['masCaro(): max(Comparator.comparingInt(Servidor::costoRiesgoOperativo)). Devuelve Optional: si no hay servidores, está vacío.',
              'masCaros(n): ordená de mayor a menor con sorted(…reversed()), quedate con limit(n) y terminá con toList().'],
             ['public Optional<Servidor> masCaro()', 'public List<Servidor> masCaros(int cantidad)'],
             [('El más caro de datos/datos.csv es srv-0023 (650)', REALES + '''
Optional<Servidor> m = new Cloud(reales).masCaro();
Prueba.verdad(m.isPresent(), "masCaro() vino vacío");
Prueba.igual("srv-0023", m.get().getId(), "el más caro");
'''),
              ('Sin servidores, masCaro() está vacío', '''
Prueba.verdad(new Cloud(List.of()).masCaro().isEmpty(), "con un Cloud vacío, masCaro() tiene que ser un Optional vacío");
'''),
              ('Los 3 más caros, de mayor a menor', REALES + '''
List<String> ids = new Cloud(reales).masCaros(3).stream().map(Servidor::getId).toList();
Prueba.igual(List.of("srv-0023", "srv-0049", "srv-0042"), ids, "los 3 más caros");
''')],
             {FC: C(M1, M2, M3, M4, M5, M6)},
             pistas=['servidores.stream().max(Comparator.comparingInt(Servidor::costoRiesgoOperativo))',
                     '.sorted(Comparator.comparingInt(Servidor::costoRiesgoOperativo).reversed()).limit(cantidad).toList()']),
        paso('panorama() y el main', FA,
             ['En Cloud, panorama() arma el texto con "Total: %d | Por Region: %s | indice menores a 50: %d".formatted(…). Las regiones van en un TreeMap para que salgan ordenadas.',
              'En App.main: el archivo es datos/datos.csv o args[0]. Leelo con ParserServidores, armá el Cloud y mostrá el informe, los descartes, los errores y el panorama.',
              'El main solo muestra: los cálculos siguen en las clases.'],
             ['public String panorama()', 'public static void main(String[] args) throws IOException'],
             [('panorama() con datos/datos.csv', REALES + '''
Prueba.igual("Total: 15170 | Por Region: {SA-EAST-1=5400, US-EAST-1=6790, US-WEST-2=2980} | indice menores a 50: 16", new Cloud(reales).panorama(), "panorama()");
'''),
              ('El main muestra el informe y el panorama', '''
String s = Prueba.salida(() -> App.main(new String[0]));
Prueba.contiene(s, "Leídas: 60 | procesadas: 30 | descartadas: 21 | inválidas: 9", "lo que muestra el main");
Prueba.contiene(s, "Total: 15170", "lo que muestra el main");
'''),
              ('El main también muestra los descartes y los errores', '''
String s = Prueba.salida(() -> App.main(new String[] { "datos/datos.csv" }));
Prueba.contiene(s, "Linea 14: ESTABLE", "lo que muestra el main");
Prueba.contiene(s, "Linea 35:", "lo que muestra el main");
''')],
             {FC: C(M1, M2, M3, M4, M5, M6, M7), FA: APP}, inicio={FA: APP_INICIO}, tambien=[FC],
             ejecutar={'entrada': FA, 'args': []},
             pistas=['Path archivo = Path.of(args.length == 0 ? "datos/datos.csv" : args[0]);',
                     'resultado.getDescartes().forEach(System.out::println); muestra cada descarte en su línea.',
                     'new TreeMap<>(totalesPorRegion()) ordena las regiones por nombre.']),
    ],
    importar=['ar.edu.backend'], grupo='basico', tema='streams')
