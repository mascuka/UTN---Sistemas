from comun import *
from ej1 import S4 as SERVIDOR

FS = "ar/edu/backend/Servidor.java"
FR = "ar/edu/backend/ResultadoParseo.java"
FP = "ar/edu/backend/ParserServidores.java"

RESULTADO = '''package ar.edu.backend;

import java.util.List;

public class ResultadoParseo {
    private final List<Servidor> servidores;
    private final int leidas;
    private final int descartadas;
    private final List<String> errores;
    private final List<String> descartes;

    public ResultadoParseo(List<Servidor> servidores, int leidas, int descartadas, List<String> errores,
            List<String> descartes) {
        this.servidores = List.copyOf(servidores);
        this.leidas = leidas;
        this.descartadas = descartadas;
        this.errores = List.copyOf(errores);
        this.descartes = List.copyOf(descartes);
    }

    public List<Servidor> getServidores() {
        return servidores;
    }

    public int getLeidas() {
        return leidas;
    }

    public int getDescartadas() {
        return descartadas;
    }

    public List<String> getErrores() {
        return errores;
    }

    public List<String> getDescartes() {
        return descartes;
    }

    public int getProcesadas() {
        return servidores.size();
    }

    public int getInvalidas() {
        return errores.size();
    }

    public String informe() {
        return "Leídas: %d | procesadas: %d | descartadas: %d | inválidas: %d | objetos: %d"
                .formatted(leidas, getProcesadas(), descartadas, getInvalidas(), servidores.size());
    }
}
'''

CABEZA = '''package ar.edu.backend;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ParserServidores {
    private static final String CABECERA = "id,region,porcentajeCPU,usoMemoria,estado";
'''

INICIO = CABEZA + '''
    /** Las líneas de datos del archivo, sin el encabezado. */
    public List<String> lineas(Path archivo) throws IOException {
        List<String> lineas = new ArrayList<>();
        // Abrí el archivo con Files.newBufferedReader, salteá el encabezado y guardá cada línea
        return lineas;
    }
}
'''

LINEAS1 = '''
    /** Las líneas de datos del archivo, sin el encabezado. */
    public List<String> lineas(Path archivo) throws IOException {
        List<String> lineas = new ArrayList<>();
        try (BufferedReader lector = Files.newBufferedReader(archivo, StandardCharsets.UTF_8)) {
            lector.readLine();   // el encabezado no es un dato
            String linea;
            while ((linea = lector.readLine()) != null) {
                lineas.add(linea);
            }
        }
        return lineas;
    }
'''
P1 = CABEZA + LINEAS1 + '}\n'

LINEAS2 = LINEAS1.replace('''            lector.readLine();   // el encabezado no es un dato''', '''            if (!CABECERA.equals(lector.readLine()))
                throw new IllegalArgumentException("encabezado incorrecto");''')
P2 = CABEZA + LINEAS2 + '}\n'

CAMPOS = '''
    /** Separa una línea en campos (conserva los vacíos del final) y les saca los espacios de afuera. */
    public static String[] campos(String linea) {
        return Arrays.stream(linea.split(",", -1)).map(String::strip).toArray(String[]::new);
    }
'''
P3 = CABEZA + LINEAS2 + CAMPOS + '}\n'

LEER = '''
    public ResultadoParseo leer(Path archivo) throws IOException {
        List<Servidor> servidores = new ArrayList<>();
        List<String> errores = new ArrayList<>();
        List<String> descartes = new ArrayList<>();
        int leidas = 0;
        for (String linea : lineas(archivo)) {
            leidas++;
            int numero = leidas + 1;   // la línea física: el encabezado es la 1
            try {
                String[] c = campos(linea);
                if (c.length != 5)
                    throw new IllegalArgumentException("cantidad de columnas incorrecta");
                if (c[4].equals("ESTABLE")) {
                    descartes.add("Linea " + numero + ": ESTABLE");
                    continue;
                }
                if (!c[4].equals("ALERTA") && !c[4].equals("CRITICO"))
                    throw new IllegalArgumentException("estado desconocido: " + c[4]);
                servidores.add(Servidor.desdeCampos(c));
            } catch (IllegalArgumentException ex) {
                errores.add("Linea " + numero + ": " + ex.getMessage());
            }
        }
        return new ResultadoParseo(servidores, leidas, descartes.size(), errores, descartes);
    }
'''
P4 = CABEZA + LINEAS2 + CAMPOS + LEER + '}\n'

E = ej(
    'bk-csv', 'Leer el CSV de servidores', 'Preenunciado 3K1 · Cloud Center',
    'BufferedReader, el encabezado, split(",", -1) y cada fila clasificada: procesada, descartada o inválida, sin cortar la carga.',
    [
        h('Cloud Center: leer el archivo'),
        pr('El archivo datos/datos.csv está en UTF-8. La primera línea es el encabezado exacto id,region,porcentajeCPU,usoMemoria,estado y no cuenta como fila leída.', 1, 2),
        pr('Cada registro ocupa una línea con cinco campos separados por coma. No hay comillas ni comas adentro de un campo. Se sacan los espacios de afuera de cada campo. split(",", -1) conserva los campos vacíos del final.', 3),
        pr('Si el encabezado no es el esperado, la lectura se corta con IllegalArgumentException. Un error al leer el archivo sigue como IOException.', 2),
        h('Flujo y errores'),
        li('Primero se controla la cantidad de columnas.', 4),
        li('Con el ancho correcto, ESTABLE se descarta sin validar el resto de los datos.', 4),
        li('ALERTA y CRITICO se intentan convertir con Servidor.desdeCampos. Cualquier otro estado es inválido, y una línea vacía también.', 4),
        li('Un error en una fila no corta la carga: se anota el número físico de línea y el motivo ("Linea 7: …") y se sigue con la próxima.', 4),
        pr('Con el archivo del preenunciado: 60 leídas, 30 procesadas, 21 descartadas y 9 inválidas. Casos testigo: srv-0045 (línea 14, descarte por ESTABLE), srv-0006 (línea 7, CPU fuera de rango) y srv-0004 (línea 35, estado desconocido).', 4),
    ],
    {'datos/datos.csv': leer('datos', 'servidores.csv')},
    [
        paso('Abrir el archivo y saltear el encabezado', FP,
             ['Completá lineas(Path archivo): abrí el archivo con Files.newBufferedReader dentro de un try (…) para que se cierre solo.',
              'Leé la primera línea y no la guardes: es el encabezado.',
              'Recorré el resto con while ((linea = lector.readLine()) != null) y agregá cada una a la lista.'],
             ['public List<String> lineas(Path archivo) throws IOException'],
             [('datos/datos.csv tiene 60 filas de datos', '''
Prueba.igual(60, new ParserServidores().lineas(Path.of("datos/datos.csv")).size(), "filas de datos/datos.csv");
'''),
              ('La primera fila es la de srv-0032 (el encabezado no está)', '''
List<String> l = new ParserServidores().lineas(Path.of("datos/datos.csv"));
Prueba.verdad(!l.isEmpty(), "la lista quedó vacía");
Prueba.igual("srv-0032,SA-EAST-1,63,9,ALERTA", l.get(0), "la primera fila");
'''),
              ('Un archivo con solo el encabezado da 0 filas', '''
Path p = Prueba.archivo("datos/vacio.csv", "id,region,porcentajeCPU,usoMemoria,estado\\n");
Prueba.igual(0, new ParserServidores().lineas(p).size(), "filas de un archivo con solo el encabezado");
'''),
              ('Lee todas las filas de otro archivo', '''
Path p = Prueba.archivo("datos/dos.csv", "id,region,porcentajeCPU,usoMemoria,estado\\nsrv-1,R1,10,10,ALERTA\\nsrv-2,R2,20,20,CRITICO\\n");
List<String> l = new ParserServidores().lineas(p);
Prueba.igual(2, l.size(), "filas de un archivo de 2 filas");
Prueba.igual("srv-2,R2,20,20,CRITICO", l.get(1), "la segunda fila");
''')],
             {FP: P1}, inicio={FS: SERVIDOR, FR: RESULTADO, FP: INICIO},
             pistas=['try (BufferedReader lector = Files.newBufferedReader(archivo, StandardCharsets.UTF_8)) { … }',
                     'Un lector.readLine(); suelto, antes del while, se "come" el encabezado.',
                     'readLine() devuelve null cuando se termina el archivo: por eso el while compara con null.']),
        paso('Controlar el encabezado', FP,
             ['En lineas: si la primera línea no es exactamente CABECERA, tirá IllegalArgumentException("encabezado incorrecto").',
              'Un archivo vacío (readLine() da null) tampoco tiene el encabezado correcto.',
              'Compará con CABECERA.equals(…): así un null no rompe nada.'],
             ['throw new IllegalArgumentException("encabezado incorrecto")'],
             [('Un encabezado distinto corta la lectura', '''
Path p = Prueba.archivo("datos/otro.csv", "id,zona,cpu,memoria,estado\\nsrv-1,R1,10,10,ALERTA\\n");
Prueba.lanza(IllegalArgumentException.class, () -> new ParserServidores().lineas(p), "encabezado id,zona,cpu,memoria,estado");
'''),
              ('Tiene que ser exacto: con espacios tampoco vale', '''
Path p = Prueba.archivo("datos/espacios.csv", "id, region, porcentajeCPU, usoMemoria, estado\\n");
Prueba.lanza(IllegalArgumentException.class, () -> new ParserServidores().lineas(p), "encabezado con espacios");
'''),
              ('Un archivo vacío también es un error', '''
Path p = Prueba.archivo("datos/nada.csv", "");
Prueba.lanza(IllegalArgumentException.class, () -> new ParserServidores().lineas(p), "archivo vacío");
'''),
              ('Con el encabezado correcto sigue igual', '''
Prueba.igual(60, new ParserServidores().lineas(Path.of("datos/datos.csv")).size(), "filas de datos/datos.csv");
''')],
             {FP: P2},
             pistas=['if (!CABECERA.equals(lector.readLine())) throw new IllegalArgumentException("encabezado incorrecto");',
                     'CABECERA.equals(null) da false, así que el archivo vacío entra solo en el mismo if.']),
        paso('Separar los campos', FP,
             ['Escribí el método estático campos(String linea): separá con split(",", -1).',
              'Sacale los espacios de afuera a cada campo (strip).',
              'Con -1, "a,b," da 3 campos (el último vacío) en lugar de 2.'],
             ['public static String[] campos(String linea)'],
             [('Separa los 5 campos de una fila', '''
String[] c = ParserServidores.campos("srv-0044,US-WEST-2,67,13,ALERTA");
Prueba.igual(5, c.length, "cantidad de campos");
Prueba.igual("srv-0044", c[0], "el id");
Prueba.igual("ALERTA", c[4], "el estado");
'''),
              ('Saca los espacios de afuera de cada campo', '''
String[] c = ParserServidores.campos("  srv-1 , US-EAST-1 ,  10,20 ,ALERTA  ");
Prueba.igual("srv-1", c[0], "el id");
Prueba.igual("US-EAST-1", c[1], "la región");
Prueba.igual("10", c[2], "la CPU");
Prueba.igual("ALERTA", c[4], "el estado");
'''),
              ('Conserva los campos vacíos, también al final', '''
Prueba.igual(3, ParserServidores.campos("a,,b").length, "campos de \\"a,,b\\"");
Prueba.igual(3, ParserServidores.campos("a,b,").length, "campos de \\"a,b,\\" (el último vacío cuenta)");
Prueba.igual("", ParserServidores.campos("a,b,")[2], "el último campo de \\"a,b,\\"");
''')],
             {FP: P3},
             pistas=['String[] partes = linea.split(",", -1); y después un for que haga partes[i] = partes[i].strip();',
                     'Con Streams: Arrays.stream(linea.split(",", -1)).map(String::strip).toArray(String[]::new)']),
        paso('Clasificar cada fila', FP,
             ['Escribí leer(Path archivo): recorré lineas(archivo) y contá cada fila leída.',
              'El número físico de línea es leidas + 1 (el encabezado es la línea 1).',
              'Adentro de un try: separá con campos; si no hay 5, IllegalArgumentException. ESTABLE va a descartes ("Linea 14: ESTABLE") y sigue con continue. Si no es ALERTA ni CRITICO, IllegalArgumentException. Si no, Servidor.desdeCampos.',
              'En el catch (IllegalArgumentException ex) anotá "Linea N: " + ex.getMessage() y seguí: la carga no se corta.',
              'Devolvé new ResultadoParseo(servidores, leidas, descartes.size(), errores, descartes).'],
             ['public ResultadoParseo leer(Path archivo) throws IOException', 'ResultadoParseo(List<Servidor>, int leidas, int descartadas, List<String> errores, List<String> descartes)'],
             [('Con datos/datos.csv: 60 leídas, 30 procesadas, 21 descartadas y 9 inválidas', '''
ResultadoParseo r = new ParserServidores().leer(Path.of("datos/datos.csv"));
Prueba.igual(60, r.getLeidas(), "leídas");
Prueba.igual(30, r.getProcesadas(), "procesadas");
Prueba.igual(21, r.getDescartadas(), "descartadas");
Prueba.igual(9, r.getInvalidas(), "inválidas");
'''),
              ('srv-0045 (línea 14) se descarta por ESTABLE', '''
ResultadoParseo r = new ParserServidores().leer(Path.of("datos/datos.csv"));
Prueba.verdad(r.getDescartes().contains("Linea 14: ESTABLE"), "no aparece \\"Linea 14: ESTABLE\\" en los descartes: " + r.getDescartes().stream().limit(3).toList());
'''),
              ('srv-0006 (línea 7) y srv-0004 (línea 35) quedan como inválidas', '''
ResultadoParseo r = new ParserServidores().leer(Path.of("datos/datos.csv"));
Prueba.verdad(r.getErrores().stream().anyMatch(e -> e.startsWith("Linea 7:")), "no aparece la línea 7 en los errores: " + r.getErrores().stream().limit(3).toList());
Prueba.verdad(r.getErrores().stream().anyMatch(e -> e.startsWith("Linea 35:") && e.contains("MANTENIMIENTO")), "no aparece la línea 35 (estado MANTENIMIENTO) en los errores");
'''),
              ('Columnas de menos, una línea vacía o un número mal escrito no cortan la carga', '''
Path p = Prueba.archivo("datos/mezcla.csv", "id,region,porcentajeCPU,usoMemoria,estado\\nsrv-1,R1,67,13,ALERTA\\nsrv-2,R1,10,10\\n\\nsrv-3,R1,abc,10,CRITICO\\nsrv-4,R2,20,20,CRITICO\\n");
ResultadoParseo r = new ParserServidores().leer(p);
Prueba.igual(5, r.getLeidas(), "leídas");
Prueba.igual(2, r.getProcesadas(), "procesadas (srv-1 y srv-4)");
Prueba.igual(3, r.getInvalidas(), "inválidas (4 columnas, línea vacía y \\"abc\\")");
'''),
              ('El informe resume la carga', '''
ResultadoParseo r = new ParserServidores().leer(Path.of("datos/datos.csv"));
Prueba.igual("Leídas: 60 | procesadas: 30 | descartadas: 21 | inválidas: 9 | objetos: 30", r.informe(), "informe()");
''')],
             {FP: P4},
             pistas=['NumberFormatException es una IllegalArgumentException: el mismo catch atrapa el "abc".',
                     'continue salta a la próxima vuelta del for: así el ESTABLE no llega a desdeCampos.',
                     'Una línea vacía da un solo campo (""), así que cae en "cantidad de columnas incorrecta".']),
    ],
    importar=['ar.edu.backend'], grupo='basico', tema='csv')
