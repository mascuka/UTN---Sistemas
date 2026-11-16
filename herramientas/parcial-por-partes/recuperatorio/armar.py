#!/usr/bin/env python3
"""El recuperatorio por partes (Backend, Recuperatorio 1 · Flota Logística): practica/bk-recuperatorio/ejercicios.json.

El preenunciado no tiene tareas: el día del recuperatorio piden cambios. Acá van casos hipotéticos sobre el mismo
proyecto, con las mismas partes que El parcial por partes (0 Consigna, 1 CSV, 2 Dominio, 3 Polimorfismo, 4 Colector y
5 Main), para cubrir lo que tomaron en los parciales y simulacros:
  A · tipo de carga (5 → 6 columnas): GENERAL o REFRIGERADA; la refrigerada cuesta 300 USD más y lleva hasta 30 t.
  B · kilómetros, con el archivo nuevo separado por ';': el costo suma 1 USD cada 10 km (cambia para todos).
  C · estado MANTENIMIENTO (se descarta) y DEMORADO 15 % más caro (subclase según el estado).
  D · el gemelo del Parcial 3K1 (Cloud Center, el mismo preenunciado con otro tema): la facturación del flete en una
      6.ª columna reemplaza a los 2000 USD fijos, con un gancho que la subclase redefine.
  Más operaciones sueltas del colector (por estado, el de mayor costo, por patente, promedios, filtros) y el main.

Las soluciones completas de cada caso están en codigo/A, codigo/B y codigo/C; lo demás sale del proyecto real
(el ZIP del preenunciado, en material/backend-de-aplicaciones/p1/parcial/recuperatorio-1/). También escribe las pruebas
de cada ejercicio en ../pruebas/<id>/ (Prueba.java y base/), que corre herramientas/parcial-por-partes/validar.py.

Desde la raíz del repo:
  python3 herramientas/parcial-por-partes/recuperatorio/armar.py
  python3 herramientas/parcial-por-partes/validar.py
"""
import json, os, re, shutil, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, '..', '..', '..'))
ZIP = os.path.join(RAIZ, 'material', 'backend-de-aplicaciones', 'p1', 'parcial', 'recuperatorio-1', '01-preenunciado.zip')
PRUEBAS = os.path.join(AQUI, '..', 'pruebas')
SALIDA = os.path.join(RAIZ, 'practica', 'bk-recuperatorio', 'ejercicios.json')

with zipfile.ZipFile(ZIP) as z:
    ORIG = {os.path.basename(n): z.read(n).decode('utf-8').replace('\r\n', '\n') for n in z.namelist() if n.endswith('.java') and '/main/' in n}


def cod(caso, nombre):
    return open(os.path.join(AQUI, 'codigo', caso, nombre), encoding='utf-8').read()


def quitar(texto, *partes):
    for p in partes:
        assert p in texto, p[:60]
        texto = texto.replace(p, '')
    return texto


def cambiar(texto, *pares):
    for a, b in pares:
        assert texto.count(a) == 1, a[:60]
        texto = texto.replace(a, b)
    return texto


H5 = 'patente,zona,velocidadPromedio,cargaToneladas,estado'
HA = H5 + ',tipoCarga'
HB = 'patente;zona;velocidadPromedio;cargaToneladas;estado;kilometros'
STUB = lambda clase: f'package ar.edu.backend;\n\n// Archivo nuevo: escribí acá la clase {clase}.\n'

# ── Lo que cambia en cada caso (a partir de las soluciones completas)
A_RUTA, A_REF, A_PARSER, A_FLOTA, A_APP = (cod('A', n) for n in ('VehiculoRuta.java', 'VehiculoRefrigerado.java', 'ParserVehiculos.java', 'Flota.java', 'App.java'))
GET_TIPO = '\n    public String getTipoCarga() {\n        return "GENERAL";\n    }\n'
GET_TIPO_REF = '\n    @Override\n    public String getTipoCarga() {\n        return "REFRIGERADA";\n    }\n'
A_RUTA_SIN_TIPO, A_REF_SIN_TIPO = quitar(A_RUTA, GET_TIPO), quitar(A_REF, GET_TIPO_REF)
# Lo que ya está hecho antes de la subclase: desdeCampos acepta 5 o 6 campos (el tipo todavía no se mira)
A_RUTA_ANCHO = cambiar(ORIG['VehiculoRuta.java'], ('if (campos == null || campos.length != 5) {\n            throw new IllegalArgumentException("La fila debe tener exactamente cinco columnas");',
                                                   'if (campos == null || (campos.length != 5 && campos.length != 6)) {\n            throw new IllegalArgumentException("La fila debe tener cinco o seis columnas");'))
B_RUTA, B_PARSER, B_FLOTA = (cod('B', n) for n in ('VehiculoRuta.java', 'ParserVehiculos.java', 'Flota.java'))
C_RUTA, C_DEM, C_PARSER = (cod('C', n) for n in ('VehiculoRuta.java', 'VehiculoDemorado.java', 'ParserVehiculos.java'))
# D · el gemelo del Parcial 3K1 (Cloud Center): la facturación del flete viene en la 6.ª columna y reemplaza a los 2000 fijos
D_RUTA, D_FAC, D_PARSER, D_APP = (cod('D', n) for n in ('VehiculoRuta.java', 'VehiculoConFacturacion.java', 'ParserVehiculos.java', 'App.java'))
HD = H5 + ',facturacion'

# ── Operaciones nuevas del colector, sobre la Flota del preenunciado
IMPORTS = ['java.util.ArrayList', 'java.util.Collections', 'java.util.Comparator', 'java.util.LinkedHashMap', 'java.util.List',
           'java.util.Map', 'java.util.Optional', 'java.util.TreeMap', 'java.util.function.Predicate', 'java.util.stream.Collectors']
M_ESTADO = '''    public Map<String, Long> contarPorEstado() {
        return vehiculos.stream()
                .collect(Collectors.groupingBy(VehiculoRuta::getEstado, TreeMap::new, Collectors.counting()));
    }
'''
M_MAYOR = '''    public Optional<VehiculoRuta> getMayorCosto() {
        return vehiculos.stream()
                .max(Comparator.comparingInt(VehiculoRuta::getCostoDesgasteOperativo));
    }
'''
M_PATENTE = '''    public Map<String, Long> getViajesPorPatente() {
        return vehiculos.stream()
                .collect(Collectors.groupingBy(VehiculoRuta::getPatente, TreeMap::new, Collectors.counting()));
    }

    public List<String> getPatentesConMasDeUnViaje() {
        return getViajesPorPatente().entrySet().stream()
                .filter(entrada -> entrada.getValue() > 1)
                .map(Map.Entry::getKey)
                .toList();
    }
'''
M_VELOCIDAD = '''    public Map<String, Double> getVelocidadPromedioPorZona() {
        return vehiculos.stream()
                .collect(Collectors.groupingBy(VehiculoRuta::getZona, TreeMap::new,
                        Collectors.averagingInt(VehiculoRuta::getVelocidadPromedio)));
    }
'''
M_FILTROS = '''    public int getCostoDemorados() {
        return sumarCostoDesgasteOperativo(vehiculo -> "DEMORADO".equals(vehiculo.getEstado()));
    }

    public long contarConIndiceEntre(int minimo, int maximo) {
        return vehiculos.stream()
                .filter(vehiculo -> vehiculo.getIndiceDesgaste() >= minimo && vehiculo.getIndiceDesgaste() <= maximo)
                .count();
    }
'''
M_TIPO = '''    public Map<String, Long> contarPorTipoCarga() {
        return vehiculos.stream()
                .collect(Collectors.groupingBy(VehiculoRuta::getTipoCarga, TreeMap::new, Collectors.counting()));
    }
'''


def flota_con(*metodos, base=None):
    """La Flota del preenunciado con métodos nuevos (antes de getVehiculos) y los imports que usen"""
    t = base or ORIG['Flota.java']
    ancla = '    public List<VehiculoRuta> getVehiculos() {'
    t = t.replace(ancla, ''.join(m + '\n' for m in metodos) + ancla)
    usados = [i for i in IMPORTS if f'import {i};' in t or re.search(r'\b' + i.split('.')[-1] + r'\b', t.split('public final class')[1])]
    cab, cuerpo = t.split('public final class', 1)
    cab = re.sub(r'(import [\w.]+;\n)+', ''.join(f'import {i};\n' for i in usados), cab)
    return cab + 'public final class' + cuerpo


assert flota_con(M_TIPO) == A_FLOTA, 'la Flota del caso A tiene que salir igual'
assert flota_con(M_KM := B_FLOTA.split('    public long contarConIndiceDesgasteMenorA')[1].split('\n\n', 1)[1].split('    public List<VehiculoRuta> getVehiculos')[0].rstrip('\n') + '\n') == B_FLOTA

APP_LOGICA = '''package ar.edu.backend;

import java.io.IOException;
import java.nio.file.Path;

public class App {
    public static void main(String[] args) throws IOException {
        Path archivo = args.length == 0 ? Path.of("datos", "datos.csv") : Path.of(args[0]);
        ResultadoParseo resultado = new ParserVehiculos().parsear(archivo);
        Flota flota = new Flota(resultado.getVehiculos());

        int demorados = 0;
        VehiculoRuta masCaro = null;
        for (VehiculoRuta vehiculo : resultado.getVehiculos()) {
            if (vehiculo.getEstado().equals("DEMORADO")) {
                demorados++;
            }
            if (masCaro == null || vehiculo.getCostoDesgasteOperativo() > masCaro.getCostoDesgasteOperativo()) {
                masCaro = vehiculo;
            }
        }

        System.out.println(resultado.getResumenErrores());
        System.out.println("DEMORADO: " + demorados);
        System.out.println("Mayor costo: " + (masCaro == null ? "-" : masCaro.getPatente()));
        System.out.println(flota.panorama());
    }
}
'''
APP_DELEGA = '''package ar.edu.backend;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;

public class App {
    public static void main(String[] args) throws IOException {
        Path archivo = args.length == 0 ? Path.of("datos", "datos.csv") : Path.of(args[0]);
        ResultadoParseo resultado = new ParserVehiculos().parsear(archivo);
        Flota flota = new Flota(resultado.getVehiculos());
        Map<String, Long> porEstado = flota.contarPorEstado();

        System.out.println(resultado.getResumenErrores());
        System.out.println("DEMORADO: " + porEstado.getOrDefault("DEMORADO", 0L));
        System.out.println("Mayor costo: " + flota.getMayorCosto().map(VehiculoRuta::getPatente).orElse("-"));
        System.out.println(flota.panorama());
    }
}
'''


# ───────────────────────── Ayudas para escribir los ejercicios
def ch(regex, ok, error, archivo=None, tipo='contiene', flags=None, veces=None):
    k = dict(tipo=tipo, regex=regex, ok=ok, error=error)
    if archivo: k['archivo'] = archivo
    if flags: k['flags'] = flags
    if veces is not None: k['veces'] = veces
    return k


def arch(nombre, inicial, solucion=None, solo=False):
    a = dict(nombre=nombre, inicial=inicial, solucion=inicial if solo else solucion)
    if solo: a['soloLectura'] = True
    return a


def codigo(id, titulo, donde, consigna, archivos, checks, pasos, pistas, csv=None, csvNota=None, datos=None, prueba=None, base=None):
    e = dict(id=id, parte=int(id[1]), tema='Flota', titulo=titulo, tipo='codigo', proyecto='flo', donde=donde, consigna=consigna)
    if csv: e['csv'] = csv
    if csvNota: e['csvNota'] = csvNota
    if datos: e['datos'] = datos
    e.update(pasos=pasos, pistas=pistas, checks=checks, archivos=archivos)
    PRUEBA[id] = (prueba, base or {})
    return e


def clasif(id, titulo, consigna, cabecera, items, resumen, base=None):
    e = dict(id=id, parte=2, tema='Flota', titulo=titulo, tipo='clasificacion', proyecto='flo', consigna=consigna, cabecera=cabecera,
             opciones=['Procesada', 'Descartada', 'Inválida'], resumen=resumen, items=[dict(texto=t, respuesta=r, motivo=m) for t, r, m in items])
    PRUEBA[id] = (CLASIFICA, base or {})
    return e


def ubic(id, titulo, consigna, opciones, items, enunciado=None):
    e = dict(id=id, parte=int(id[1]), tema='' if id.startswith('r0') else 'Flota', titulo=titulo, tipo='ubicacion', consigna=consigna)
    if enunciado: e['enunciado'] = enunciado
    e.update(opciones=opciones, items=[dict(texto=t, respuesta=r, motivo=m) for t, r, m in items])
    return e


def tabla(cabecera, filas, nuevas=None, sep=','):
    t = dict(cabecera=cabecera, filas=filas, separador=sep)
    if nuevas: t['columnasNuevas'] = nuevas
    return t


PRUEBA = {}
CABEZA = '''package ar.edu.backend;

import java.util.*;

public class Prueba {
    static java.nio.file.Path csv(String... lineas) throws Exception {
        java.nio.file.Path p = java.nio.file.Files.createTempFile("pp", ".csv");
        java.nio.file.Files.writeString(p, String.join("\\n", lineas) + "\\n");
        return p;
    }
    static ResultadoParseo leer(String... lineas) {
        try { return new ParserVehiculos().parsear(csv(lineas)); }
        catch (IllegalArgumentException e) { throw e; }
        catch (Exception e) { throw new RuntimeException(e); }
    }
    static VehiculoRuta v(String... campos) { return VehiculoRuta.desdeCampos(campos); }
    static void igual(Object esperado, Object real, String que) {
        if (!Objects.equals(esperado, real)) throw new AssertionError(que + ": se esperaba " + esperado + " y dio " + real);
    }
    static void lanza(Runnable r, String que) {
        try { r.run(); } catch (IllegalArgumentException e) { return; }
        throw new AssertionError(que + ": tenía que lanzar IllegalArgumentException");
    }
    static void anda(Runnable r, String que) {
        try { r.run(); } catch (RuntimeException e) { throw new AssertionError(que + ": no tenía que fallar y tiró " + e); }
    }
    static String salida(String... args) {
        java.io.PrintStream antes = System.out;
        java.io.ByteArrayOutputStream b = new java.io.ByteArrayOutputStream();
        System.setOut(new java.io.PrintStream(b, true));
        try { App.main(args); } catch (Exception e) { throw new RuntimeException(e); } finally { System.setOut(antes); }
        return b.toString();
    }
    static void contiene(String texto, String parte) {
        if (!texto.contains(parte)) throw new AssertionError("la salida no tiene \\"" + parte + "\\":\\n" + texto);
    }
    public static void main(String[] a) throws Exception {
'''
PIE = '''        System.out.println("OK");
    }
}
'''
CLASIFICA = '''        // Una fila por vez: así se sabe qué pasó con cada una
        String[] lineas = a[0].split("\\\\|", -1);
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < lineas.length; i++) {
            ResultadoParseo r = leer(lineas[0], lineas[i]);
            sb.append(r.getFilasDescartadas() == 1 ? "Descartada" : r.getFilasInvalidas() == 1 ? "Inválida" : "Procesada").append(i < lineas.length - 1 ? "," : "");
        }
        System.out.println(sb);
'''

# ───────────────────────── Las partes
ENUNCIADO_A = [
    'Columna nueva: `tipoCarga` (5 → 6), GENERAL o REFRIGERADA. En el formato viejo, todos son GENERAL. Cada fila, con el ancho de su cabecera.',
    'Exactamente GENERAL o REFRIGERADA, después de quitar espacios. Vacío o desconocido: la fila es inválida.',
    'REFRIGERADA: las mismas validaciones, como máximo 30 t (inclusive) y 300 USD más que una general con los mismos datos, una sola vez.',
    'Precedencia: ancho → descartar EN_DEPOSITO sin validar → validaciones.',
    'El costo total y por zona, con la regla nueva. Colector: un conteo por tipo de carga. Main: `datos-parcial.csv`, el resumen, los objetos, GENERAL / REFRIGERADA y el panorama.',
]
ENUNCIADO_B = [
    'El archivo nuevo viene separado por `;` y con una columna más, `kilometros` (5 → 6). La cabecera define el separador y el ancho.',
    '`kilometros`: entero de 0 a 5000 (inclusive). En el formato viejo, 0.',
    'El costo suma 1 USD cada 10 km (división entera): `2000 × índice / 100 + km / 10`.',
    'Colector: los kilómetros totales por zona y el vehículo con más kilómetros. Main: mostrarlos.',
]
ENUNCIADO_D = [
    'Es el mismo cambio del **Parcial 3K1 (Cloud Center)**, que tiene el mismo preenunciado con otro tema: allá la 6.ª columna eran los ingresos y reemplazaban a los 1000 USD fijos.',
    'Columna nueva: `facturacion` (5 → 6), lo que factura ese flete. En el formato viejo, los 2000 USD de siempre. Cada fila, con el ancho de su cabecera.',
    'EN_RUTA y DEMORADO del formato nuevo: la facturación es un entero de 2000 (inclusive) a 3800 (exclusive), después de quitar espacios. Fuera de rango: la fila es inválida.',
    'El costo usa la facturación de la fila: `facturacion × índice / 100`. El total, los filtros y los totales por zona, con la regla nueva.',
    'Colector: un conteo por estado. Main: `datos-parcial.csv`, el resumen, los objetos, EN_RUTA / DEMORADO y el panorama.',
]
ENUNCIADO_C = [
    'Estado nuevo MANTENIMIENTO: se descarta igual que EN_DEPOSITO, sin validar el resto.',
    'Un DEMORADO cuesta 15 % más: `costo × 115 / 100` (enteros).',
    'Colector: cuántos vehículos hay por estado, el costo total de los DEMORADO y las patentes con más de un viaje.',
    'Main: mostrarlo todo, sin cuentas en el main.',
]
OPC = ['Parser', 'Dominio', 'Colector', 'Main']
P0 = [
    ubic('r0.1', 'Caso A · Tipo de carga', 'Supongamos que el recuperatorio agrega `tipoCarga` (5 → 6 columnas): GENERAL o REFRIGERADA. Indicá en qué clase va cada cambio.', OPC, [
        ('Aceptar la cabecera con `tipoCarga` (5 y 6 columnas)', 'Parser', 'Estructura del archivo'),
        ('Una fila de 5 campos bajo la cabecera de 6 es inválida', 'Parser', 'El ancho lo decide la cabecera'),
        ('Descartar EN_DEPOSITO sin mirar el tipo de carga', 'Parser', 'Precedencia: ancho → descarte'),
        ('Que el tipo sea exactamente GENERAL o REFRIGERADA', 'Dominio', 'Validación del dato, en `desdeCampos`'),
        ('Una REFRIGERADA lleva como máximo 30 t', 'Dominio', 'Validación, en el constructor de la subclase'),
        ('La REFRIGERADA cuesta 300 USD más', 'Dominio', 'Subclase `VehiculoRefrigerado` con `@Override getCostoDesgasteOperativo()`'),
        ('Sacarle el `final` a `VehiculoRuta`', 'Dominio', '**Trampa:** una clase `final` no se puede heredar'),
        ('Que el costo total y por zona incluyan el recargo', 'Dominio', '**Trampa:** `Flota` no se toca; suma `getCostoDesgasteOperativo()`, que la subclase redefine'),
        ('Contar cuántos hay GENERAL y cuántos REFRIGERADA', 'Colector', '`groupingBy(VehiculoRuta::getTipoCarga, counting())`'),
        ('Usar `datos-parcial.csv` y mostrar las cantidades', 'Main', 'Solo imprime'),
    ], ENUNCIADO_A),
    ubic('r0.2', 'Caso B · Kilómetros con punto y coma', 'Supongamos que el archivo nuevo viene separado por `;` y con `kilometros` (5 → 6), y que el costo suma 1 USD cada 10 km. Indicá en qué clase va cada cambio.', OPC, [
        ('Reconocer la cabecera nueva separada por `;`', 'Parser', 'Estructura del archivo'),
        ('Partir cada fila con el separador de su cabecera', 'Parser', '`linea.split(separador, -1)`'),
        ('Una fila con comas bajo la cabecera con `;` es inválida', 'Parser', 'Partida por `;` queda 1 columna: falla el ancho'),
        ('Guardar los kilómetros y agregar su getter', 'Dominio', 'Atributo `final` + `getKilometros()`'),
        ('Los kilómetros van de 0 a 5000', 'Dominio', 'Validación, en el constructor'),
        ('En el formato viejo, 0 km', 'Dominio', '`desdeCampos`: valor por defecto si hay 5 campos'),
        ('El costo suma 1 USD cada 10 km', 'Dominio', 'Cambia para **todos**: se cambia `getCostoDesgasteOperativo()`, sin subclase'),
        ('Kilómetros totales por zona', 'Colector', '`groupingBy(getZona, summingInt(getKilometros))`'),
        ('El vehículo con más kilómetros', 'Colector', '`max(Comparator.comparingInt(...))`'),
        ('Mostrar los kilómetros por zona', 'Main', 'Solo imprime'),
    ], ENUNCIADO_B),
    ubic('r0.3', 'Caso C · MANTENIMIENTO y DEMORADO más caro', 'Supongamos que aparece el estado MANTENIMIENTO y que los DEMORADO pasan a costar 15 % más. Indicá en qué clase va cada cambio.', OPC, [
        ('Descartar MANTENIMIENTO igual que EN_DEPOSITO', 'Parser', 'Los descartes van antes de convertir'),
        ('Un MANTENIMIENTO con velocidad `abc` se descarta igual', 'Parser', '**Trampa:** el descarte no valida el resto'),
        ('Un DEMORADO cuesta 15 % más', 'Dominio', 'Subclase `VehiculoDemorado` con `@Override`'),
        ('Elegir qué clase crear según el estado', 'Dominio', '`desdeCampos`'),
        ('Que el costo por zona tenga el 15 %', 'Dominio', '**Trampa:** `Flota` suma el método redefinido; no se toca'),
        ('Cuántos vehículos hay por estado', 'Colector', '`groupingBy(getEstado, counting())`'),
        ('El costo total de los DEMORADO', 'Colector', '`sumarCostoDesgasteOperativo(v -> \"DEMORADO\".equals(v.getEstado()))`'),
        ('Las patentes con más de un viaje', 'Colector', 'Agrupar por patente y filtrar las de más de 1'),
        ('Mostrarlo todo sin `for` ni cuentas', 'Main', 'El main solo llama métodos'),
    ], ENUNCIADO_C),
    ubic('r0.4', 'Caso D · Facturación por flete (como el 3K1)', 'El caso más parecido a lo que ya tomaron: la facturación del flete viene en una 6.ª columna y reemplaza a los 2000 USD fijos. Indicá en qué clase va cada cambio.', OPC, [
        ('Aceptar la cabecera con `facturacion` (5 y 6 columnas)', 'Parser', 'Estructura del archivo'),
        ('Una fila de 5 campos bajo la cabecera de 6 es inválida', 'Parser', 'El ancho lo decide la cabecera'),
        ('Descartar EN_DEPOSITO sin mirar la facturación', 'Parser', 'Precedencia: ancho → descarte'),
        ('La facturación va de 2000 (inclusive) a 3800 (exclusive)', 'Dominio', 'Validación, en el constructor de la subclase'),
        ('En el formato viejo, 2000 USD por flete', 'Dominio', 'El gancho del padre devuelve 2000'),
        ('El costo usa la facturación de la fila', 'Dominio', 'Subclase que redefine el gancho (`@Override`)'),
        ('Que el total, los filtros y los totales por zona usen la facturación', 'Dominio', '**Trampa:** `Flota` no se toca; todo pasa por `getCostoDesgasteOperativo()`'),
        ('Contar cuántos hay EN_RUTA y cuántos DEMORADO', 'Colector', '`groupingBy(VehiculoRuta::getEstado, counting())`'),
        ('Usar `datos-parcial.csv` y mostrar EN_RUTA / DEMORADO', 'Main', 'Solo imprime, con `getOrDefault(..., 0L)`'),
    ], ENUNCIADO_D),
]

P1 = [
    codigo('r1.1', '5 → 6 columnas (`tipoCarga`)', '`ParserVehiculos.parsear` (mirá `VehiculoRuta`, que ya acepta 5 o 6 campos)',
           'El archivo nuevo trae una 6.ª columna, `tipoCarga`. El parser tiene que aceptar **las dos cabeceras** (la vieja de 5 y la nueva de 6) y cada fila tiene que tener el ancho de **su** cabecera: '
           'una fila de 5 bajo la cabecera de 6 es inválida, y al revés. Otra cabecera sigue tirando `IllegalArgumentException`. Un solo loop para los dos formatos; lo demás (descartar EN_DEPOSITO, registrar los errores) queda igual.',
           [arch('ParserVehiculos.java', ORIG['ParserVehiculos.java'], A_PARSER), arch('VehiculoRuta.java', A_RUTA, solo=True)],
           [ch(r'tipoCarga', 'La cabecera nueva', 'Falta la cabecera nueva, con `tipoCarga`', 'ParserVehiculos.java'),
            ch(r'campos\.length\s*!=\s*(?!5\b)\w+', 'El ancho lo decide la cabecera', 'Compará el largo con el ancho de la cabecera, no con 5 fijo', 'ParserVehiculos.java'),
            ch(r'campos\.length\s*!=\s*5\b', 'Sin el 5 fijo', 'Queda un `campos.length != 5`: las filas de 6 serían inválidas', 'ParserVehiculos.java', 'noContiene'),
            ch(r'=\s*6\s*;|\?\s*6\b|:\s*6\b', 'Ancho 6 para la cabecera nueva', 'Falta el ancho 6 para la cabecera nueva', 'ParserVehiculos.java'),
            ch(r'\bwhile\s*\(', 'Un solo loop', 'Usá un solo `while` para los dos formatos', 'ParserVehiculos.java', 'cuenta', veces=1),
            ch(r'throw\s+new\s+IllegalArgumentException', 'Otra cabecera sigue abortando', 'Con otra cabecera hay que tirar `IllegalArgumentException`', 'ParserVehiculos.java')],
           ['Una constante para la cabecera nueva: `ENCABEZADO + ",tipoCarga"`.', 'Después de leer la primera línea, decidí `columnas`: 5, 6, o la excepción.',
            'En el loop, `campos.length != columnas` en lugar de `!= 5`.', 'El mensaje del error puede decir cuántas columnas esperaba.'],
           ['`int columnas;` declarada antes del `if`: así el compilador sabe que siempre tiene valor.', 'No dupliques el `while`: es el mismo loop, solo cambia el número.',
            'El archivo vacío da `encabezado == null`: `ENCABEZADO.equals(encabezado)` no falla (al revés, sí).'],
           tabla(HA, ['trk-1,NORTE,60,10,EN_RUTA,GENERAL', 'trk-2,SUR,60,10,EN_RUTA,REFRIGERADA', 'trk-3,SUR,60,10,EN_RUTA', 'trk-4,SUR,999,-5,EN_DEPOSITO,X'], ['tipoCarga']),
           'trk-1 y trk-2 se procesan · trk-3 (5 campos) es **inválida** (línea 4) · trk-4 se **descarta**. Leídas 4 · procesadas 2 · descartadas 1 · inválidas 1.',
           prueba=f'''        ResultadoParseo r = leer("{HA}", "trk-1,NORTE,60,10,EN_RUTA,GENERAL", "trk-2,SUR,60,10,EN_RUTA,REFRIGERADA", "trk-3,SUR,60,10,EN_RUTA", "trk-4,SUR,999,-5,EN_DEPOSITO,X");
        igual(4, r.getFilasLeidas(), "leídas"); igual(2, r.getFilasProcesadas(), "procesadas"); igual(1, r.getFilasDescartadas(), "descartadas"); igual(1, r.getFilasInvalidas(), "inválidas");
        igual(4, r.getErrores().get(0).getNumeroLinea(), "la fila de 5 está en la línea 4");
        ResultadoParseo viejo = leer("{H5}", "trk-1,NORTE,60,10,EN_RUTA", "trk-2,NORTE,60,10,EN_RUTA,GENERAL");
        igual(1, viejo.getFilasProcesadas(), "formato viejo"); igual(1, viejo.getFilasInvalidas(), "6 campos bajo la cabecera de 5");
        lanza(() -> leer("otra,cabecera"), "otra cabecera");
''', base={'VehiculoRefrigerado.java': A_REF}),
    codigo('r1.2', 'Descartar también MANTENIMIENTO', '`ParserVehiculos.parsear`',
           'Aparece un estado nuevo, **MANTENIMIENTO**: esas filas se **descartan** igual que EN_DEPOSITO, sin validar el resto (velocidad, carga, zona) y sumando en las descartadas. '
           'El estado se compara después de quitar espacios y es sensible a mayúsculas.',
           [arch('ParserVehiculos.java', ORIG['ParserVehiculos.java'], C_PARSER)],
           [ch(r'"MANTENIMIENTO"', 'El estado nuevo', 'Falta descartar "MANTENIMIENTO"', 'ParserVehiculos.java'),
            ch(r'"EN_DEPOSITO"', 'EN_DEPOSITO se sigue descartando', 'No borres el descarte de EN_DEPOSITO', 'ParserVehiculos.java'),
            ch(r'"MANTENIMIENTO".*desdeCampos', 'Se descarta antes de convertir', 'El descarte va antes de `VehiculoRuta.desdeCampos`', 'ParserVehiculos.java', flags='s'),
            ch(r'filasDescartadas\s*\+\+', 'Suma en las descartadas', 'Las filas descartadas tienen que sumar en `filasDescartadas`', 'ParserVehiculos.java')],
           ['Una constante `Set.of("EN_DEPOSITO", "MANTENIMIENTO")`.', 'Cambiá el `if` por `ESTADOS_DESCARTADOS.contains(estado)`.',
            'El descarte sigue **antes** de `desdeCampos`: así no se valida nada de esas filas.'],
           ['También vale `"EN_DEPOSITO".equals(estado) || "MANTENIMIENTO".equals(estado)`.', 'No toques `VehiculoRuta`: un MANTENIMIENTO nunca llega a crear un vehículo.', 'Importá `java.util.Set`.'],
           tabla(H5, ['trk-1,NORTE,60,10,EN_RUTA', 'trk-2,SUR,abc,,MANTENIMIENTO', 'trk-3,SUR,999,-5,EN_DEPOSITO', 'trk-4,SUR,60,10,mantenimiento', 'trk-5,SUR,60,10, MANTENIMIENTO ']),
           'trk-1 se procesa · trk-2, trk-3 y trk-5 se **descartan** (trk-5 tiene espacios: con `trim()` vale) · trk-4 es **inválida**: en minúsculas no es MANTENIMIENTO. Leídas 5 · procesadas 1 · descartadas 3 · inválidas 1.',
           prueba=f'''        ResultadoParseo r = leer("{H5}", "trk-1,NORTE,60,10,EN_RUTA", "trk-2,SUR,abc,,MANTENIMIENTO", "trk-3,SUR,999,-5,EN_DEPOSITO", "trk-4,SUR,60,10,mantenimiento", "trk-5,SUR,60,10, MANTENIMIENTO ");
        igual(5, r.getFilasLeidas(), "leídas"); igual(1, r.getFilasProcesadas(), "procesadas"); igual(3, r.getFilasDescartadas(), "descartadas"); igual(1, r.getFilasInvalidas(), "inválidas");
        igual(5, r.getErrores().get(0).getNumeroLinea(), "la de minúsculas está en la línea 5");
'''),
    codigo('r1.3', 'Separador `;` y 6 columnas (`kilometros`)', '`ParserVehiculos.parsear` (mirá `VehiculoRuta`, que ya acepta 5 o 6 campos)',
           'El archivo nuevo viene separado por **punto y coma** y con una columna más: `' + HB + '`. La cabecera define **el separador y el ancho**: con la vieja, coma y 5; con la nueva, `;` y 6. '
           'Una fila que no respeta su cabecera es inválida. Otra cabecera sigue tirando `IllegalArgumentException`.',
           [arch('ParserVehiculos.java', ORIG['ParserVehiculos.java'], B_PARSER), arch('VehiculoRuta.java', B_RUTA, solo=True)],
           [ch(r'kilometros', 'La cabecera nueva', 'Falta la cabecera nueva, con `kilometros` y separada por `;`', 'ParserVehiculos.java'),
            ch(r'";"', 'El separador nuevo', 'Falta el separador `";"`', 'ParserVehiculos.java'),
            ch(r'split\s*\(\s*(?!")\w+\s*,\s*-1\s*\)', 'Parte con el separador de su cabecera', 'Usá `linea.split(separador, -1)` con el separador que corresponde', 'ParserVehiculos.java'),
            ch(r'campos\.length\s*!=\s*5\b', 'Sin el 5 fijo', 'Queda un `campos.length != 5`: las filas de 6 serían inválidas', 'ParserVehiculos.java', 'noContiene'),
            ch(r'\bwhile\s*\(', 'Un solo loop', 'Usá un solo `while` para los dos formatos', 'ParserVehiculos.java', 'cuenta', veces=1)],
           ['Dos variables antes del loop: `separador` y `columnas`.', 'Cabecera vieja: `","` y 5; nueva: `";"` y 6; si no, la excepción.', '`linea.split(separador, -1)`.', 'Compará el largo con `columnas`.'],
           ['`;` y `,` no son especiales en las expresiones regulares: `split(";", -1)` anda tal cual. Un `|` o un `.` sí lo son (habría que escribir `"\\\\|"`).',
            'El `-1` conserva los campos vacíos del final: `trk-1;NORTE;60;10;EN_RUTA;` tiene 6 campos, el último vacío.', 'Mirá en la otra pestaña cómo `desdeCampos` lee `campos[5]`.'],
           tabla(HB, ['trk-1;NORTE;60;10;EN_RUTA;300', 'trk-2;SUR;60;10;EN_RUTA;0', 'trk-3,SUR,60,10,EN_RUTA,300', 'trk-4;SUR;999;-5;EN_DEPOSITO;x'], ['kilometros'], ';'),
           'trk-1 (**830**) y trk-2 (**800**) se procesan · trk-3 viene con comas: partida por `;` queda **1** columna → **inválida** · trk-4 se descarta.',
           prueba=f'''        ResultadoParseo r = leer("{HB}", "trk-1;NORTE;60;10;EN_RUTA;300", "trk-2;SUR;60;10;EN_RUTA;0", "trk-3,SUR,60,10,EN_RUTA,300", "trk-4;SUR;999;-5;EN_DEPOSITO;x");
        igual(4, r.getFilasLeidas(), "leídas"); igual(2, r.getFilasProcesadas(), "procesadas"); igual(1, r.getFilasDescartadas(), "descartadas"); igual(1, r.getFilasInvalidas(), "inválidas");
        igual(1630, new Flota(r.getVehiculos()).getCostoTotalDesgasteOperativo(), "830 + 800");
        ResultadoParseo viejo = leer("{H5}", "trk-1,NORTE,60,10,EN_RUTA");
        igual(1, viejo.getFilasProcesadas(), "formato viejo, con comas"); igual(800, new Flota(viejo.getVehiculos()).getCostoTotalDesgasteOperativo(), "sin kilómetros");
        lanza(() -> leer("patente;zona"), "otra cabecera");
'''),
    codigo('r1.4', '5 → 6 columnas (`facturacion`, como el 3K1)', '`ParserVehiculos.parsear` (mirá `VehiculoRuta`, que ya acepta 5 o 6 campos)',
           'El parser del caso D, igual al del Parcial 3K1: el archivo nuevo trae una 6.ª columna, `facturacion`. Aceptá **las dos cabeceras** (la vieja de 5 y la nueva de 6); cada fila tiene que tener el ancho de **su** cabecera, '
           'ni filas de 5 bajo la de 6 ni al revés. Otra cabecera sigue tirando `IllegalArgumentException`. Un solo loop para los dos formatos.',
           [arch('ParserVehiculos.java', ORIG['ParserVehiculos.java'], D_PARSER), arch('VehiculoRuta.java', D_RUTA, solo=True)],
           [ch(r'facturacion', 'La cabecera nueva', 'Falta la cabecera nueva, con `facturacion`', 'ParserVehiculos.java'),
            ch(r'campos\.length\s*!=\s*(?!5\b)\w+', 'El ancho lo decide la cabecera', 'Compará el largo con el ancho de la cabecera, no con 5 fijo', 'ParserVehiculos.java'),
            ch(r'campos\.length\s*!=\s*5\b', 'Sin el 5 fijo', 'Queda un `campos.length != 5`: las filas de 6 serían inválidas', 'ParserVehiculos.java', 'noContiene'),
            ch(r'=\s*6\s*;|\?\s*6\b|:\s*6\b', 'Ancho 6 para la cabecera nueva', 'Falta el ancho 6 para la cabecera nueva', 'ParserVehiculos.java'),
            ch(r'\bwhile\s*\(', 'Un solo loop', 'Usá un solo `while` para los dos formatos', 'ParserVehiculos.java', 'cuenta', veces=1),
            ch(r'throw\s+new\s+IllegalArgumentException', 'Otra cabecera sigue abortando', 'Con otra cabecera hay que tirar `IllegalArgumentException`', 'ParserVehiculos.java')],
           ['Una constante para la cabecera nueva: `ENCABEZADO + ",facturacion"`.', 'Después de leer la primera línea, decidí `columnas`: 5, 6, o la excepción.',
            'En el loop, `campos.length != columnas` en lugar de `!= 5`.'],
           ['Es lo mismo que pidió el 3K1 con `ingresos`: «Integrar la lectura de ambas versiones del CSV sin duplicar el proceso de carga».', '`int columnas;` declarada antes del `if`.',
            'EN_DEPOSITO se sigue descartando después de mirar el ancho.'],
           tabla(HD, ['trk-1,NORTE,60,10,EN_RUTA,3000', 'trk-2,CENTRO,101,11,DEMORADO,2600', 'trk-3,SUR,60,10,EN_RUTA', 'trk-4,SUR,999,-5,EN_DEPOSITO,x'], ['facturacion']),
           'trk-1 (**1200**) y trk-2 (**1690**) se procesan · trk-3 (5 campos) es **inválida** · trk-4 se **descarta**. Leídas 4 · procesadas 2 · descartadas 1 · inválidas 1.',
           prueba=f'''        ResultadoParseo r = leer("{HD}", "trk-1,NORTE,60,10,EN_RUTA,3000", "trk-2,CENTRO,101,11,DEMORADO,2600", "trk-3,SUR,60,10,EN_RUTA", "trk-4,SUR,999,-5,EN_DEPOSITO,x");
        igual(4, r.getFilasLeidas(), "leídas"); igual(2, r.getFilasProcesadas(), "procesadas"); igual(1, r.getFilasDescartadas(), "descartadas"); igual(1, r.getFilasInvalidas(), "inválidas");
        igual(2890, new Flota(r.getVehiculos()).getCostoTotalDesgasteOperativo(), "1200 + 1690");
        ResultadoParseo viejo = leer("{H5}", "trk-1,NORTE,60,10,EN_RUTA", "trk-2,NORTE,60,10,EN_RUTA,3000");
        igual(1, viejo.getFilasProcesadas(), "formato viejo"); igual(1, viejo.getFilasInvalidas(), "6 campos bajo la cabecera de 5");
        lanza(() -> leer("otra,cabecera"), "otra cabecera");
''', base={'VehiculoConFacturacion.java': D_FAC}),
]

P2 = [
    codigo('r2.1', '`kilometros` en `VehiculoRuta`', '`VehiculoRuta`: atributo, constructores, `desdeCampos` y el costo',
           'Agregá el dato `kilometros` a `VehiculoRuta`: atributo `final`, getter y validación (entero de **0 a 5000**, inclusive). El constructor de siempre tiene que seguir andando (lo usan los tests): '
           'que **delegue** con `this(..., 0)` en uno nuevo que recibe los kilómetros. `desdeCampos` acepta 5 o 6 campos: con 6 lee `campos[5]`; con 5, 0 km. '
           'El costo suma **1 USD cada 10 km** (división entera): `2000 × índice / 100 + km / 10`.',
           [arch('VehiculoRuta.java', ORIG['VehiculoRuta.java'], B_RUTA)],
           [ch(r'private\s+final\s+int\s+kilometros', 'El atributo', 'Falta `private final int kilometros;`', 'VehiculoRuta.java'),
            ch(r'int\s+getKilometros\s*\(\s*\)', 'El getter', 'Falta `public int getKilometros()`', 'VehiculoRuta.java'),
            ch(r'this\s*\([^;]*,\s*0\s*\)\s*;', 'El constructor viejo delega', 'El constructor viejo tiene que delegar: `this(..., 0);`', 'VehiculoRuta.java'),
            ch(r'kilometros\s*<\s*0', 'Valida el mínimo', 'Validá que los kilómetros no sean negativos', 'VehiculoRuta.java'),
            ch(r'\b5_?000\b', 'Valida el máximo', 'Validá el tope de 5000 km', 'VehiculoRuta.java'),
            ch(r'campos\.length\s*==\s*6', 'Lee la columna solo si existe', 'Leé `campos[5]` solo si hay 6 campos', 'VehiculoRuta.java'),
            ch(r'kilometros\s*/\s*10', 'El costo con los kilómetros', 'El costo tiene que sumar `kilometros / 10`', 'VehiculoRuta.java')],
           ['`private final int kilometros;` y `getKilometros()`.', 'Un constructor nuevo con un parámetro más; validá `kilometros < 0 || kilometros > 5000`.',
            'El viejo: `this(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste, 0);`',
            '`desdeCampos`: aceptá 5 o 6 y `int kilometros = campos.length == 6 ? convertirEntero(campos[5], "kilómetros") : 0;`', '`getCostoDesgasteOperativo()`: sumale `kilometros / 10`.'],
           ['`this(...)` tiene que ser la **primera** línea del constructor viejo.', 'Con `convertirEntero` reutilizás el `trim()` y el mensaje de siempre.',
            'Leer `campos[5]` en una fila de 5 tira `ArrayIndexOutOfBoundsException`, que el parser no atrapa: preguntá el largo antes.',
            'El cálculo cambia para **todos**: no hace falta una subclase, se cambia el método.'],
           datos='60 km/h, 10 t (índice 40) y 300 km → 800 + 30 = **830** · con 99 km → **809** (99 / 10 = 9) · 5000 km → **1300** · 5001, -1, `mil` o vacío → excepción · formato viejo → 0 km, **800**.',
           prueba='''        VehiculoRuta x = v("trk-1", "NORTE", "60", "10", "EN_RUTA", "300");
        igual(300, x.getKilometros(), "los kilómetros"); igual(830, x.getCostoDesgasteOperativo(), "800 + 30");
        igual(809, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "99").getCostoDesgasteOperativo(), "99 km suman 9");
        igual(1300, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "5000").getCostoDesgasteOperativo(), "el tope es inclusive");
        VehiculoRuta viejo = v("trk-1", "NORTE", "60", "10", "EN_RUTA");
        igual(0, viejo.getKilometros(), "formato viejo: 0 km"); igual(800, viejo.getCostoDesgasteOperativo(), "formato viejo: el costo de siempre");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "5001"), "más de 5000");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "-1"), "negativo");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "mil"), "no es entero");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", ""), "vacío");
        lanza(() -> v("trk-1", "NORTE", "60", "10"), "4 campos");
        igual(0, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40).getKilometros(), "el constructor viejo delega con 0");
        igual(812, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, 120).getCostoDesgasteOperativo(), "el constructor nuevo");
        lanza(() -> new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, 6000), "el constructor valida");
'''),
    clasif('r2.2', 'clasificá las filas · las reglas de hoy', 'Con las reglas del preenunciado **tal como están**, indicá qué pasa con cada fila. Cabecera de **5 columnas**. '
           'Velocidad mayor a 0 y menor a 130; carga hasta 45 t; estado EN_RUTA o DEMORADO (EN_DEPOSITO se descarta); índice = `(int) (velocidad × 0.6 + carga × 0.4)`, entre 1 y 90. **Precedencia:** ancho → descarte → validaciones.', H5, [
        ('trk-0012,NORTE,76,11,EN_RUTA', 'Procesada', 'Caso testigo: índice 50 → cuesta 1000'),
        ('trk-0038,CENTRO,101,11,DEMORADO', 'Procesada', 'Caso testigo: índice 65 → 1300'),
        ('trk-0019,SUR,80,20,EN_DEPOSITO', 'Descartada', 'Caso testigo: EN_DEPOSITO'),
        ('trk-0008,SUR,999,-5,EN_DEPOSITO', 'Descartada', '**Trampa:** EN_DEPOSITO se descarta sin validar velocidad ni carga'),
        ('trk-0005,NORTE,128,43,EN_RUTA', 'Inválida', 'Caso testigo: velocidad y carga dentro del rango, pero el índice da 94'),
        ('trk-0080,SUR,121,45,EN_RUTA', 'Procesada', '**Trampa:** 72,6 + 18 = 90,6 y el `(int)` trunca → índice 90 (vale): cuesta 1800'),
        ('trk-0081,SUR,122,45,EN_RUTA', 'Inválida', '73,2 + 18 = 91,2 → 91: pasa de 90'),
        ('trk-0041,CENTRO,70,25,PERDIDO', 'Inválida', 'Caso testigo: estado desconocido'),
        ('trk-0002,CENTRO,85,50,DEMORADO', 'Inválida', 'Carga de 50 t: más de 45'),
        ('trk-0082,NORTE,10,-5,EN_RUTA', 'Procesada', '**Trampa:** la carga negativa no se valida (solo «no mayor a 45»): 6 − 2 = 4 → cuesta 80'),
        ('trk-0083,NORTE,1,-5,EN_RUTA', 'Inválida', '0,6 − 2 = −1,4 → −1: el índice tiene que ser al menos 1'),
        ('trk-0053,SUR,0,20,EN_RUTA', 'Inválida', 'Velocidad 0: tiene que ser mayor a 0'),
        ('trk-0084,SUR,130,10,EN_RUTA', 'Inválida', 'Velocidad 130: tiene que ser **menor** a 130'),
        ('trk-0021,NORTE,80,EN_RUTA', 'Inválida', '4 columnas'),
        ('trk-0085,NORTE,60,10,EN_DEPOSITO,EXTRA', 'Inválida', '**Trampa:** 6 columnas: el ancho se mira antes que el descarte'),
        ('trk-0046,,75,15,EN_RUTA', 'Inválida', 'Zona vacía'),
        ('trk-0086, CENTRO , 60 , 10 , DEMORADO ', 'Procesada', 'Los espacios se van con `trim()`: índice 40 → 800'),
        ('trk-0087,CENTRO,60,10,en_ruta', 'Inválida', 'El estado es sensible a mayúsculas'),
        ('trk-0088,NORTE,60.5,10,EN_RUTA', 'Inválida', '60.5 no es un entero'),
        ('trk-0012,NORTE,60,10,DEMORADO', 'Procesada', 'Patente repetida: no se exige unicidad, cada fila es un viaje'),
    ], 'Con estas filas: **leídas 20 · procesadas 7 · descartadas 2 · inválidas 11**. Con el CSV del preenunciado: 60 leídas, 32 procesadas, 20 descartadas y 8 inválidas.'),
    clasif('r2.3', 'clasificá las filas · tipo de carga', 'Con las reglas del **caso A**, indicá qué pasa con cada fila. Cabecera de **6 columnas**. Tipo: exactamente GENERAL o REFRIGERADA; REFRIGERADA: hasta 30 t y 300 USD más. '
           '**Precedencia:** ancho → descarte EN_DEPOSITO → validaciones.', HA, [
        ('trk-1,NORTE,60,10,EN_RUTA,GENERAL', 'Procesada', 'General: índice 40 → 800'),
        ('trk-2,SUR,60,10,EN_RUTA,REFRIGERADA', 'Procesada', 'Refrigerada: 800 + 300 = 1100'),
        ('trk-3,CENTRO,60,30,DEMORADO,REFRIGERADA', 'Procesada', '30 t: el tope de la refrigerada es inclusive (índice 48 → 960 + 300 = 1260)'),
        ('trk-4,CENTRO,60,31,DEMORADO,REFRIGERADA', 'Inválida', '31 t: pasa el tope de la refrigerada'),
        ('trk-5,NORTE,60,40,EN_RUTA,GENERAL', 'Procesada', 'General de 40 t: el tope de 30 es solo para las refrigeradas'),
        ('trk-6,NORTE,60,10,EN_RUTA,', 'Inválida', 'Tipo vacío'),
        ('trk-7,NORTE,60,10,EN_RUTA,CONGELADA', 'Inválida', 'Tipo desconocido'),
        ('trk-8,SUR,999,-5,EN_DEPOSITO,CONGELADA', 'Descartada', '**Trampa:** EN_DEPOSITO se descarta sin validar nada más'),
        ('trk-9,NORTE,60,10,EN_RUTA', 'Inválida', '5 campos bajo una cabecera de 6'),
        ('trk-10,SUR,60,10,EN_RUTA, REFRIGERADA ', 'Procesada', 'Los espacios se van: vale'),
        ('trk-11,SUR,60,10,EN_RUTA,refrigerada', 'Inválida', '«Exactamente» REFRIGERADA: en minúsculas no vale'),
        ('trk-12,NORTE,128,43,EN_RUTA,GENERAL', 'Inválida', 'Índice 94'),
        ('trk-13,SUR,60,10,PERDIDO,REFRIGERADA', 'Inválida', 'Estado desconocido'),
    ], 'Resumen esperado: **leídas 13 · procesadas 5 · descartadas 1 · inválidas 7**.', base={'ParserVehiculos.java': A_PARSER, 'VehiculoRuta.java': A_RUTA, 'VehiculoRefrigerado.java': A_REF}),
    clasif('r2.4', 'clasificá las filas · kilómetros con `;`', 'Con las reglas del **caso B**, indicá qué pasa con cada fila. Cabecera nueva, separada por **`;`** y de 6 columnas. '
           'Kilómetros: entero de 0 a 5000. **Precedencia:** ancho → descarte → validaciones.', HB, [
        ('trk-1;NORTE;60;10;EN_RUTA;300', 'Procesada', '800 + 30 = 830'),
        ('trk-2;SUR;60;10;EN_RUTA;0', 'Procesada', '0 km vale: 800'),
        ('trk-3;SUR;60;10;EN_RUTA;5000', 'Procesada', 'El tope es inclusive: 800 + 500 = 1300'),
        ('trk-4;SUR;60;10;EN_RUTA;5001', 'Inválida', 'Pasa los 5000 km'),
        ('trk-5;NORTE;60;10;EN_RUTA;-1', 'Inválida', 'Kilómetros negativos'),
        ('trk-6;NORTE;60;10;EN_RUTA;', 'Inválida', 'Kilómetros vacíos: no es un entero'),
        ('trk-7,NORTE,60,10,EN_RUTA,300', 'Inválida', '**Trampa:** viene con comas; partida por `;` queda 1 columna'),
        ('trk-8;SUR;999;-5;EN_DEPOSITO;abc', 'Descartada', 'EN_DEPOSITO se descarta sin validar'),
        ('trk-9;CENTRO;60;10;DEMORADO;99', 'Procesada', '99 / 10 = 9 (división entera): 809'),
        ('trk-10;CENTRO;60;10;DEMORADO', 'Inválida', '5 campos bajo una cabecera de 6'),
    ], 'Resumen esperado: **leídas 10 · procesadas 4 · descartadas 1 · inválidas 5**.', base={'ParserVehiculos.java': B_PARSER, 'VehiculoRuta.java': B_RUTA}),
    clasif('r2.5', 'clasificá las filas · MANTENIMIENTO', 'Con las reglas del **caso C**, indicá qué pasa con cada fila. Cabecera de 5 columnas. Se descartan EN_DEPOSITO y MANTENIMIENTO; un DEMORADO cuesta 15 % más. '
           '**Precedencia:** ancho → descarte → validaciones.', H5, [
        ('trk-1,NORTE,60,10,EN_RUTA', 'Procesada', 'Índice 40: 800'),
        ('trk-2,NORTE,60,10,DEMORADO', 'Procesada', '800 × 115 / 100 = 920'),
        ('trk-3,SUR,abc,,MANTENIMIENTO', 'Descartada', 'MANTENIMIENTO se descarta sin validar'),
        ('trk-4,SUR,60,10, MANTENIMIENTO ', 'Descartada', 'Con espacios también: `trim()`'),
        ('trk-5,SUR,60,10,Mantenimiento', 'Inválida', 'Sensible a mayúsculas: no es un estado conocido'),
        ('trk-6,SUR,60,10,MANTENIMIENTO,X', 'Inválida', '**Trampa:** 6 columnas: el ancho va antes que el descarte'),
        ('trk-7,CENTRO,101,11,DEMORADO', 'Procesada', 'Índice 65: 1300 × 115 / 100 = 1495'),
        ('trk-8,NORTE,85,50,DEMORADO', 'Inválida', 'Carga de 50 t'),
    ], 'Resumen esperado: **leídas 8 · procesadas 3 · descartadas 2 · inválidas 3**.', base={'ParserVehiculos.java': C_PARSER, 'VehiculoRuta.java': C_RUTA, 'VehiculoDemorado.java': C_DEM}),
    clasif('r2.6', 'clasificá las filas · facturación (como el 3K1)', 'Con las reglas del **caso D**, indicá qué pasa con cada fila. Cabecera de **6 columnas**. Facturación: entero de 2000 (inclusive) a 3800 (exclusive); '
           'el costo es `facturación × índice / 100`. **Precedencia:** ancho → descarte EN_DEPOSITO → validaciones.', HD, [
        ('trk-1,NORTE,60,10,EN_RUTA,2000', 'Procesada', 'El mínimo es inclusive: 2000 × 40 / 100 = 800'),
        ('trk-2,NORTE,60,10,EN_RUTA,3000', 'Procesada', '3000 × 40 / 100 = 1200'),
        ('trk-3,CENTRO,101,11,DEMORADO,2600', 'Procesada', 'Índice 65: 2600 × 65 / 100 = 1690'),
        ('trk-4,NORTE,60,10,EN_RUTA,3799', 'Procesada', '3799 × 40 / 100 = 1519 (división entera)'),
        ('trk-5,NORTE,60,10,EN_RUTA,3800', 'Inválida', 'El tope es **exclusive**: 3800 no entra'),
        ('trk-6,NORTE,60,10,EN_RUTA,1999', 'Inválida', 'Menos de 2000'),
        ('trk-7,NORTE,60,10,EN_RUTA, 2500 ', 'Procesada', 'Los espacios se van: 2500 × 40 / 100 = 1000'),
        ('trk-8,NORTE,60,10,EN_RUTA,', 'Inválida', 'Facturación vacía: no es un entero'),
        ('trk-9,SUR,999,-5,EN_DEPOSITO,abc', 'Descartada', '**Trampa:** EN_DEPOSITO se descarta sin validar nada más'),
        ('trk-10,SUR,60,10,EN_RUTA', 'Inválida', '5 campos bajo una cabecera de 6'),
        ('trk-11,SUR,128,43,DEMORADO,3000', 'Inválida', 'Índice 94: las validaciones de siempre siguen'),
        ('trk-12,SUR,60,10,PERDIDO,3000', 'Inválida', 'Estado desconocido'),
    ], 'Resumen esperado: **leídas 12 · procesadas 5 · descartadas 1 · inválidas 6**.', base={'ParserVehiculos.java': D_PARSER, 'VehiculoRuta.java': D_RUTA, 'VehiculoConFacturacion.java': D_FAC}),
]

P3 = [
    codigo('r3.1', 'REFRIGERADA: 300 USD más y hasta 30 t', '`VehiculoRefrigerado.java` (archivo nuevo) y `VehiculoRuta`',
           'Si la 6.ª columna dice REFRIGERADA, el vehículo cuesta **300 USD más** que uno general con los mismos datos (una sola vez) y no puede llevar más de **30 t** (inclusive): validalo en el constructor de la subclase. '
           'GENERAL es el vehículo de siempre, y en el formato de 5 columnas todos son generales. Otro valor, o vacío: `IllegalArgumentException`. Usá polimorfismo: una subclase que redefine `getCostoDesgasteOperativo()`. '
           'Ya está hecho que `desdeCampos` acepte 5 o 6 campos.',
           [arch('VehiculoRuta.java', A_RUTA_ANCHO, A_RUTA_SIN_TIPO), arch('VehiculoRefrigerado.java', STUB('VehiculoRefrigerado'), A_REF_SIN_TIPO)],
           [ch(r'class\s+VehiculoRefrigerado\s+extends\s+VehiculoRuta\b', 'Subclase creada', 'Falta `class VehiculoRefrigerado extends VehiculoRuta`', 'VehiculoRefrigerado.java'),
            ch(r'\bfinal\s+class\s+VehiculoRuta\b', '`VehiculoRuta` se puede heredar', 'Sacale el `final` a `VehiculoRuta`: una clase `final` no se puede heredar', 'VehiculoRuta.java', 'noContiene'),
            ch(r'super\s*\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)', 'Llama al constructor del padre', 'El constructor empieza con `super(...)` y los seis datos', 'VehiculoRefrigerado.java'),
            ch(r'\b30\b', 'El tope de 30 t', 'Falta el tope: una refrigerada lleva como máximo 30 t', 'VehiculoRefrigerado.java'),
            ch(r'@Override\s*public\s+int\s+getCostoDesgasteOperativo', 'Redefine el costo', 'Redefiní `getCostoDesgasteOperativo()` con `@Override`', 'VehiculoRefrigerado.java'),
            ch(r'super\.getCostoDesgasteOperativo\s*\(\s*\)\s*\+', 'Reutiliza el costo de siempre', 'Usá `super.getCostoDesgasteOperativo() + 300`', 'VehiculoRefrigerado.java'),
            ch(r'\b300\b', 'El recargo de 300', 'Falta el recargo de 300 USD', 'VehiculoRefrigerado.java'),
            ch(r'"REFRIGERADA"', 'Lee el tipo', '`desdeCampos` tiene que mirar si el tipo es "REFRIGERADA"', 'VehiculoRuta.java'),
            ch(r'new\s+VehiculoRefrigerado\s*\(', 'Crea la subclase', '`desdeCampos` tiene que crear un `VehiculoRefrigerado`', 'VehiculoRuta.java'),
            ch(r'instanceof', 'Sin `instanceof`', 'Usá polimorfismo en lugar de `instanceof`', tipo='noContiene')],
           ['Sacale el `final` a `public final class VehiculoRuta`.', '`class VehiculoRefrigerado extends VehiculoRuta`, con un constructor que llame a `super(...)` con los seis datos y después valide `cargaToneladas > 30`.',
            '`@Override public int getCostoDesgasteOperativo()` → `super.getCostoDesgasteOperativo() + 300`.', 'En `desdeCampos`: el tipo es `limpiar(campos[5])` si hay 6 y `"GENERAL"` si hay 5.',
            'Un `switch` crea un `VehiculoRuta` o un `VehiculoRefrigerado`; el `default` tira la excepción.'],
           ['**Trampa del recuperatorio:** `VehiculoRuta` es `final`. Sin sacarlo, `extends VehiculoRuta` no compila.', 'Primero `super(...)`: así las validaciones de siempre (velocidad, carga ≤ 45, estado, índice) corren también para las refrigeradas.',
            'El índice lo calcula `desdeCampos` y se pasa igual a los dos constructores.', 'No hace falta tocar `Flota`: el total y los totales por zona suman `getCostoDesgasteOperativo()`.'],
           tabla(HA, ['A,NORTE,60,10,EN_RUTA,GENERAL', 'B,NORTE,60,10,EN_RUTA,REFRIGERADA', 'C,SUR,60,30,DEMORADO,REFRIGERADA', 'D,SUR,60,31,DEMORADO,REFRIGERADA'], ['tipoCarga']),
           'A → **800** · B → **1100** · C (30 t) → **1260** · D (31 t) es **inválida** (una general de 31 t sería válida).',
           prueba='''        VehiculoRuta g = v("A", "NORTE", "60", "10", "EN_RUTA", "GENERAL");
        igual(800, g.getCostoDesgasteOperativo(), "general"); igual(VehiculoRuta.class, g.getClass(), "GENERAL crea un VehiculoRuta");
        VehiculoRuta r = v("B", "NORTE", "60", "10", "EN_RUTA", "REFRIGERADA");
        igual(1100, r.getCostoDesgasteOperativo(), "refrigerada"); igual(true, r instanceof VehiculoRefrigerado, "REFRIGERADA crea la subclase");
        igual(1260, v("C", "SUR", "60", "30", "DEMORADO", "REFRIGERADA").getCostoDesgasteOperativo(), "refrigerada de 30 t");
        lanza(() -> v("D", "SUR", "60", "31", "DEMORADO", "REFRIGERADA"), "refrigerada de 31 t");
        anda(() -> v("E", "SUR", "60", "31", "DEMORADO", "GENERAL"), "general de 31 t");
        lanza(() -> v("F", "SUR", "60", "10", "EN_RUTA", ""), "tipo vacío");
        lanza(() -> v("F", "SUR", "60", "10", "EN_RUTA", "CONGELADA"), "tipo desconocido");
        lanza(() -> v("F", "SUR", "60", "10", "EN_RUTA", "refrigerada"), "en minúsculas");
        lanza(() -> v("F", "SUR", "0", "10", "EN_RUTA", "REFRIGERADA"), "las validaciones de siempre");
        igual(1100, v("G", "SUR", "60", "10", "EN_RUTA", " REFRIGERADA ").getCostoDesgasteOperativo(), "con espacios");
        igual(800, v("H", "SUR", "60", "10", "EN_RUTA").getCostoDesgasteOperativo(), "formato viejo: general");
        Flota f = new Flota(leer("''' + HA + '''", "A,NORTE,60,10,EN_RUTA,GENERAL", "B,NORTE,60,10,EN_RUTA,REFRIGERADA", "C,SUR,60,30,DEMORADO,REFRIGERADA").getVehiculos());
        igual(3160, f.getCostoTotalDesgasteOperativo(), "el total, con el recargo"); igual(1900, f.getCostoPorZona().get("NORTE"), "NORTE"); igual(1260, f.getCostoPorZona().get("SUR"), "SUR");
''', base={'ParserVehiculos.java': A_PARSER}),
    codigo('r3.2', 'DEMORADO: 15 % más caro', '`VehiculoDemorado.java` (archivo nuevo) y `VehiculoRuta.desdeCampos`',
           'Un vehículo en estado DEMORADO tiene un costo por desgaste operativo **15 % más alto**, en enteros: `costo × 115 / 100`. EN_RUTA sigue igual. '
           'Hacelo con una subclase `VehiculoDemorado` que redefine `getCostoDesgasteOperativo()`; `desdeCampos` decide qué clase crear según el estado.',
           [arch('VehiculoRuta.java', ORIG['VehiculoRuta.java'], C_RUTA), arch('VehiculoDemorado.java', STUB('VehiculoDemorado'), C_DEM)],
           [ch(r'class\s+VehiculoDemorado\s+extends\s+VehiculoRuta\b', 'Subclase creada', 'Falta `class VehiculoDemorado extends VehiculoRuta`', 'VehiculoDemorado.java'),
            ch(r'\bfinal\s+class\s+VehiculoRuta\b', '`VehiculoRuta` se puede heredar', 'Sacale el `final` a `VehiculoRuta`', 'VehiculoRuta.java', 'noContiene'),
            ch(r'super\s*\(', 'Llama al constructor del padre', 'El constructor empieza con `super(...)`', 'VehiculoDemorado.java'),
            ch(r'@Override\s*public\s+int\s+getCostoDesgasteOperativo', 'Redefine el costo', 'Redefiní `getCostoDesgasteOperativo()` con `@Override`', 'VehiculoDemorado.java'),
            ch(r'super\.getCostoDesgasteOperativo\s*\(\s*\)\s*\*', 'Reutiliza el costo de siempre', 'Multiplicá `super.getCostoDesgasteOperativo()`', 'VehiculoDemorado.java'),
            ch(r'\b115\b', 'El 15 % más', 'Falta el 115 (el 100 % más el 15 %)', 'VehiculoDemorado.java'),
            ch(r'\(\s*115\s*/\s*100\s*\)|1\.15', 'En enteros', '`* (115 / 100)` da `* 1` y `* 1.15` es un double: escribí `* 115 / 100`', 'VehiculoDemorado.java', 'noContiene'),
            ch(r'new\s+VehiculoDemorado\s*\(', 'Crea la subclase', '`desdeCampos` tiene que crear un `VehiculoDemorado` si el estado es DEMORADO', 'VehiculoRuta.java'),
            ch(r'instanceof', 'Sin `instanceof`', 'Usá polimorfismo en lugar de `instanceof`', tipo='noContiene')],
           ['Sacale el `final` a `VehiculoRuta`.', '`class VehiculoDemorado extends VehiculoRuta` con el constructor que llama a `super(...)`.',
            '`@Override` de `getCostoDesgasteOperativo()`: `super.getCostoDesgasteOperativo() * 115 / 100`.', 'En `desdeCampos`, si el estado es DEMORADO, `return new VehiculoDemorado(...)`; si no, el de siempre.'],
           ['Multiplicá **antes** de dividir: `* 115 / 100`. `* (115 / 100)` en enteros es `* 1`.', '`* 1.15` da un `double`: habría que castear y podés perder un peso por redondeo.',
            'El estado se sigue validando en el constructor de `VehiculoRuta` (EN_RUTA o DEMORADO).'],
           tabla(H5, ['A,NORTE,60,10,EN_RUTA', 'B,NORTE,60,10,DEMORADO', 'C,CENTRO,101,11,DEMORADO', 'D,SUR,51,11,DEMORADO']),
           'A → **800** · B → 800 × 115 / 100 = **920** · C (índice 65) → **1495** · D (índice 35) → 700 × 115 / 100 = **805**. Total **4020**.',
           prueba='''        VehiculoRuta x = v("A", "NORTE", "60", "10", "EN_RUTA");
        igual(800, x.getCostoDesgasteOperativo(), "EN_RUTA"); igual(VehiculoRuta.class, x.getClass(), "EN_RUTA crea un VehiculoRuta");
        VehiculoRuta b = v("B", "NORTE", "60", "10", "DEMORADO");
        igual(920, b.getCostoDesgasteOperativo(), "DEMORADO"); igual(true, b instanceof VehiculoDemorado, "DEMORADO crea la subclase");
        igual(1495, v("C", "CENTRO", "101", "11", "DEMORADO").getCostoDesgasteOperativo(), "índice 65");
        igual(805, v("D", "SUR", "51", "11", "DEMORADO").getCostoDesgasteOperativo(), "índice 35");
        lanza(() -> v("E", "SUR", "60", "10", "PERDIDO"), "estado desconocido");
        Flota f = new Flota(leer("''' + H5 + '''", "A,NORTE,60,10,EN_RUTA", "B,NORTE,60,10,DEMORADO", "C,CENTRO,101,11,DEMORADO", "D,SUR,51,11,DEMORADO").getVehiculos());
        igual(4020, f.getCostoTotalDesgasteOperativo(), "el total, con el 15 %"); igual(1720, f.getCostoPorZona().get("NORTE"), "NORTE");
'''),
    ubic('r3.3', '¿Subclase, cambiar el método, validación o colector?', 'Para cada pedido, ¿qué hace falta? Pensá si cambia un **cálculo para algunos** (subclase), un cálculo **para todos** (se cambia el método), una **regla** sobre el dato (validación) o algo **sobre todos los vehículos** (colector).',
         ['Subclase', 'Cambiar el método', 'Validación', 'Colector'], [
        ('Los REFRIGERADA cuestan 300 USD más', 'Subclase', 'Cambia el costo solo para algunos'),
        ('El costo de todos suma 1 USD cada 10 km', 'Cambiar el método', 'Cambia para todos: no hace falta una subclase'),
        ('Los DEMORADO cuestan 15 % más', 'Subclase', 'Cambia el costo según el estado'),
        ('La patente tiene que tener entre 6 y 10 caracteres', 'Validación', 'En el constructor'),
        ('La velocidad máxima pasa a ser 120 km/h para todos', 'Validación', 'Cambia el `if` del constructor'),
        ('Una REFRIGERADA lleva como máximo 30 t', 'Validación', 'En el constructor de la subclase'),
        ('El índice pasa a ser `velocidad × 0.5 + carga × 0.5`', 'Cambiar el método', 'Cambia `calcularIndiceDesgaste` para todos'),
        ('Los PELIGROSA duplican el costo', 'Subclase', 'Otro cálculo para algunos: `super.getCostoDesgasteOperativo() * 2`'),
        ('Cuántos vehículos hay por estado', 'Colector', 'Un conteo sobre todos'),
        ('El costo promedio por zona', 'Colector', '`groupingBy(getZona, averagingInt(...))`'),
    ]),
    codigo('r3.4', 'la facturación en el costo, con un gancho (como el 3K1)', '`VehiculoConFacturacion.java` (archivo nuevo) y `VehiculoRuta`',
           'Es el cambio del Parcial 3K1 llevado a Flota. En el formato nuevo, la 6.ª columna trae la **facturación** de ese flete, que reemplaza a los 2000 USD fijos: costo = `facturación × índice / 100`. '
           'La facturación es un entero de **2000 (inclusive) a 3800 (exclusive)**; fuera de rango, `IllegalArgumentException`. En el formato viejo, 2000 como siempre. '
           'Hacelo con un **gancho**: un método `protected` en `VehiculoRuta` que devuelve 2000 y que usa el costo; la subclase lo redefine con la facturación de la fila. Ya está hecho que `desdeCampos` acepte 5 o 6 campos.',
           [arch('VehiculoRuta.java', A_RUTA_ANCHO, D_RUTA), arch('VehiculoConFacturacion.java', STUB('VehiculoConFacturacion'), D_FAC)],
           [ch(r'class\s+VehiculoConFacturacion\s+extends\s+VehiculoRuta\b', 'Subclase creada', 'Falta `class VehiculoConFacturacion extends VehiculoRuta`', 'VehiculoConFacturacion.java'),
            ch(r'\bfinal\s+class\s+VehiculoRuta\b', '`VehiculoRuta` se puede heredar', 'Sacale el `final` a `VehiculoRuta`', 'VehiculoRuta.java', 'noContiene'),
            ch(r'int\s+\w+\s*\(\s*\)\s*\{\s*return\s+2_?000\s*;', 'El gancho con los 2000 de siempre', 'Agregá en `VehiculoRuta` un método que devuelva 2000 (el gancho)', 'VehiculoRuta.java'),
            ch(r'return\s+(this\.)?\w+\s*\(\s*\)\s*\*\s*(this\.)?indiceDesgaste\s*/\s*100', 'El costo usa el gancho', 'El costo tiene que ser `gancho() * indiceDesgaste / 100`, no `2000 * ...`', 'VehiculoRuta.java'),
            ch(r'@Override\s*(protected|public)\s+int\s+\w+\s*\(\s*\)', 'La subclase redefine el gancho', 'Redefiní el gancho con `@Override` en la subclase', 'VehiculoConFacturacion.java'),
            ch(r'\b3_?800\b', 'El tope de 3800', 'Falta el rango: menos de 3800', 'VehiculoConFacturacion.java'),
            ch(r'>=\s*3_?800|<\s*2_?000', 'Valida el rango', 'Validá `facturacion < 2000 || facturacion >= 3800`', 'VehiculoConFacturacion.java'),
            ch(r'new\s+VehiculoConFacturacion\s*\(', 'Crea la subclase', '`desdeCampos` tiene que crear un `VehiculoConFacturacion` cuando hay 6 campos', 'VehiculoRuta.java'),
            ch(r'campos\.length\s*==\s*6', 'Lee la columna solo si existe', 'Leé `campos[5]` solo si hay 6 campos', 'VehiculoRuta.java'),
            ch(r'instanceof', 'Sin `instanceof`', 'Usá polimorfismo en lugar de `instanceof`', tipo='noContiene')],
           ['Sacale el `final` a `VehiculoRuta`.', 'En `VehiculoRuta`: `protected int getFacturacionPorFlete() { return 2000; }` y el costo `getFacturacionPorFlete() * indiceDesgaste / 100`.',
            '`class VehiculoConFacturacion extends VehiculoRuta`, con un atributo `facturacion`; el constructor llama a `super(...)` y valida el rango.',
            '`@Override protected int getFacturacionPorFlete() { return facturacion; }`.', 'En `desdeCampos`: si hay 6 campos, `convertirEntero(campos[5], "facturación")` y `new VehiculoConFacturacion(...)`.'],
           ['Así resolvió la cátedra el 3K1 (`ingresoPorHora()` en `Servidor`, redefinido en `ServidorConIngresos`): la cuenta del costo queda en un solo lugar.',
            'También vale redefinir directamente `getCostoDesgasteOperativo()` en la subclase, pero el gancho evita repetir la cuenta.',
            'El rango: `facturacion < 2000 || facturacion >= 3800` → excepción (3800 queda **afuera**).', '`Flota` no cambia: suma `getCostoDesgasteOperativo()`.'],
           tabla(HD, ['A,NORTE,60,10,EN_RUTA,3000', 'B,CENTRO,101,11,DEMORADO,2600', 'C,SUR,60,10,EN_RUTA,3800', 'D,SUR,60,10,EN_RUTA'], ['facturacion']),
           'A → 3000 × 40 / 100 = **1200** · B → 2600 × 65 / 100 = **1690** · C (3800) es **inválida** · D (5 campos) es inválida bajo esta cabecera; en el formato viejo cuesta **800**.',
           prueba='''        VehiculoRuta x = v("A", "NORTE", "60", "10", "EN_RUTA", "3000");
        igual(1200, x.getCostoDesgasteOperativo(), "3000 × 40 / 100"); igual(true, x instanceof VehiculoConFacturacion, "6 campos crea la subclase");
        igual(1690, v("B", "CENTRO", "101", "11", "DEMORADO", "2600").getCostoDesgasteOperativo(), "2600 × 65 / 100");
        igual(800, v("C", "SUR", "60", "10", "EN_RUTA", "2000").getCostoDesgasteOperativo(), "el mínimo es inclusive");
        igual(1519, v("C", "SUR", "60", "10", "EN_RUTA", "3799").getCostoDesgasteOperativo(), "división entera");
        lanza(() -> v("C", "SUR", "60", "10", "EN_RUTA", "3800"), "el tope es exclusive");
        lanza(() -> v("C", "SUR", "60", "10", "EN_RUTA", "1999"), "menos de 2000");
        lanza(() -> v("C", "SUR", "60", "10", "EN_RUTA", ""), "vacía");
        lanza(() -> v("C", "SUR", "0", "10", "EN_RUTA", "3000"), "las validaciones de siempre");
        VehiculoRuta viejo = v("D", "SUR", "60", "10", "EN_RUTA");
        igual(800, viejo.getCostoDesgasteOperativo(), "formato viejo: 2000"); igual(VehiculoRuta.class, viejo.getClass(), "5 campos crea un VehiculoRuta");
        Flota f = new Flota(leer("''' + HD + '''", "A,NORTE,60,10,EN_RUTA,3000", "B,CENTRO,101,11,DEMORADO,2600", "C,SUR,60,10,EN_RUTA,3800").getVehiculos());
        igual(2890, f.getCostoTotalDesgasteOperativo(), "el total, con la facturación"); igual(1690, f.getCostoPorZona().get("CENTRO"), "CENTRO");
''', base={'ParserVehiculos.java': D_PARSER}),
]


def flota_ej(id, titulo, metodos, consigna, checks, pasos, pistas, datos, prueba, base_ruta=None, solo_ruta=None):
    archivos = [arch('Flota.java', ORIG['Flota.java'], flota_con(*metodos))]
    if solo_ruta: archivos.append(arch('VehiculoRuta.java', solo_ruta, solo=True))
    return codigo(id, titulo, '`Flota` (la operación nueva)', consigna, archivos, checks, pasos, pistas, datos=datos, prueba=prueba, base=base_ruta)


LISTA = '''        List<VehiculoRuta> l = List.of(v("a", "NORTE", "60", "10", "EN_RUTA"), v("b", "SUR", "60", "10", "DEMORADO"), v("c", "SUR", "70", "10", "DEMORADO"), v("a", "CENTRO", "101", "11", "EN_RUTA"));
        Flota f = new Flota(l), vacia = new Flota(List.of());
'''
P4 = [
    flota_ej('r4.1', 'cantidad de vehículos por estado', [M_ESTADO],
             'Es el conteo que pidió el Parcial 3K1 (caso D): agregá a `Flota` cuántos vehículos hay EN_RUTA y cuántos DEMORADO, ordenado por estado. Con la flota vacía, un mapa vacío (el 3K1 decía «un resultado vacío o conteos cero»). Nombre: `contarPorEstado()`.',
             [ch(r'Map<String,\s*Long>\s+contarPorEstado\s*\(\s*\)', 'El método nuevo', 'Falta `public Map<String, Long> contarPorEstado()`', 'Flota.java'),
              ch(r'groupingBy\s*\(\s*(VehiculoRuta::getEstado|\w+\s*->\s*\w+\.getEstado\s*\(\s*\))', 'Agrupa por estado', 'Agrupá por `VehiculoRuta::getEstado`', 'Flota.java'),
              ch(r'counting\s*\(\s*\)', 'Cuenta', 'Contá cada grupo con `Collectors.counting()`', 'Flota.java')],
             ['`vehiculos.stream().collect(...)`.', '`Collectors.groupingBy(VehiculoRuta::getEstado, TreeMap::new, Collectors.counting())`.'],
             ['`counting()` cuenta en `Long`: el mapa es `Map<String, Long>`.', 'Con `TreeMap::new` sale ordenado; sin él, también vale.', 'Importá `TreeMap` y `Collectors`.'],
             'a, a (EN_RUTA) · b, c (DEMORADO) → `{DEMORADO=2, EN_RUTA=2}` · vacía → `{}`. Con el CSV del preenunciado: `{DEMORADO=14, EN_RUTA=18}`.',
             LISTA + '''        igual(Map.of("DEMORADO", 2L, "EN_RUTA", 2L), f.contarPorEstado(), "por estado"); igual(Map.of(), vacia.contarPorEstado(), "vacía");
'''),
    codigo('r4.2', 'conteo por tipo de carga, en tres archivos', '`getTipoCarga()` en `VehiculoRuta` y `VehiculoRefrigerado`, y `Flota` (la operación nueva)',
           'Agregá a `Flota` un conteo por tipo de carga: cuántos GENERAL y cuántos REFRIGERADA (`contarPorTipoCarga()`); con la flota vacía, un mapa vacío. '
           'Para saber el tipo, agregá `getTipoCarga()` en `VehiculoRuta` (devuelve `"GENERAL"`) y redefinilo en `VehiculoRefrigerado` (devuelve `"REFRIGERADA"`). **Sin `instanceof`.**',
           [arch('VehiculoRuta.java', A_RUTA_SIN_TIPO, A_RUTA), arch('VehiculoRefrigerado.java', A_REF_SIN_TIPO, A_REF), arch('Flota.java', ORIG['Flota.java'], A_FLOTA)],
           [ch(r'String\s+getTipoCarga\s*\(\s*\)\s*\{\s*return\s+"GENERAL"', '`getTipoCarga()` en el padre', 'Agregá `getTipoCarga()` en `VehiculoRuta`, que devuelva "GENERAL"', 'VehiculoRuta.java'),
            ch(r'@Override\s*public\s+String\s+getTipoCarga', 'La subclase lo redefine', '`VehiculoRefrigerado` tiene que redefinir `getTipoCarga()` con `@Override`', 'VehiculoRefrigerado.java'),
            ch(r'"REFRIGERADA"', 'El tipo de la subclase', 'Falta el `getTipoCarga()` que devuelve "REFRIGERADA"', 'VehiculoRefrigerado.java'),
            ch(r'Map<String,\s*Long>\s+contarPorTipoCarga\s*\(\s*\)', 'El método nuevo', 'Falta `public Map<String, Long> contarPorTipoCarga()`', 'Flota.java'),
            ch(r'groupingBy\s*\(\s*VehiculoRuta::getTipoCarga', 'Agrupa por tipo', 'Agrupá por `VehiculoRuta::getTipoCarga`', 'Flota.java'),
            ch(r'counting\s*\(\s*\)', 'Cuenta', 'Contá con `Collectors.counting()`', 'Flota.java'),
            ch(r'instanceof', 'Sin `instanceof`', 'Usá el método redefinido, no `instanceof`', tipo='noContiene')],
           ['`public String getTipoCarga() { return "GENERAL"; }` en `VehiculoRuta`.', '`@Override public String getTipoCarga() { return "REFRIGERADA"; }` en `VehiculoRefrigerado`.',
            'En `Flota`: `groupingBy(VehiculoRuta::getTipoCarga, TreeMap::new, Collectors.counting())`.'],
           ['El tipo de vuelta es `Map<String, Long>`.', 'Por qué `getTipoCarga()` y no `instanceof`: si mañana aparece PELIGROSA, `Flota` no cambia.'],
           datos='GENERAL, REFRIGERADA, REFRIGERADA → `{GENERAL=1, REFRIGERADA=2}` · vacía → `{}`.',
           prueba='''        Flota f = new Flota(List.of(v("a", "N", "60", "10", "EN_RUTA", "GENERAL"), v("b", "N", "60", "10", "EN_RUTA", "REFRIGERADA"), v("c", "S", "60", "10", "DEMORADO", "REFRIGERADA")));
        igual(Map.of("GENERAL", 1L, "REFRIGERADA", 2L), f.contarPorTipoCarga(), "por tipo"); igual(Map.of(), new Flota(List.of()).contarPorTipoCarga(), "vacía");
        igual("GENERAL", v("a", "N", "60", "10", "EN_RUTA").getTipoCarga(), "formato viejo");
''', base={'ParserVehiculos.java': A_PARSER}),
    flota_ej('r4.3', 'el vehículo de mayor costo', [M_MAYOR],
             'Agregá a `Flota` el vehículo con el **mayor costo** por desgaste operativo: `getMayorCosto()`, que devuelve un `Optional<VehiculoRuta>` (vacío si la flota está vacía).',
             [ch(r'Optional<VehiculoRuta>\s+getMayorCosto\s*\(\s*\)', 'El método nuevo', 'Falta `public Optional<VehiculoRuta> getMayorCosto()`', 'Flota.java'),
              ch(r'\.max\s*\(', 'Usa max', 'Usá `.max(...)` del stream', 'Flota.java'),
              ch(r'Comparator\.comparingInt\s*\(\s*VehiculoRuta::getCostoDesgasteOperativo', 'Compara por el costo', 'Compará con `Comparator.comparingInt(VehiculoRuta::getCostoDesgasteOperativo)`', 'Flota.java')],
             ['`vehiculos.stream().max(Comparator.comparingInt(VehiculoRuta::getCostoDesgasteOperativo))`.', 'Devolvé el `Optional` tal cual.'],
             ['`max` ya devuelve un `Optional`: con la lista vacía, `Optional.empty()`.', 'Para la patente: `getMayorCosto().map(VehiculoRuta::getPatente).orElse("-")`.', 'Importá `Comparator` y `Optional`.'],
             'a (800), b (800), c (920), a (1300) → el de **1300** (patente a, CENTRO) · vacía → `Optional.empty()`. Con el CSV del preenunciado: **trk-0038** (1300).',
             LISTA + '''        igual(1300, f.getMayorCosto().get().getCostoDesgasteOperativo(), "el mayor"); igual("CENTRO", f.getMayorCosto().get().getZona(), "es el de CENTRO");
        igual(Optional.empty(), vacia.getMayorCosto(), "vacía");
'''),
    flota_ej('r4.4', 'viajes por patente y patentes repetidas', [M_PATENTE],
             'No se exige unicidad de patentes: cada fila es un viaje. Agregá a `Flota` cuántos viajes hizo cada patente (`getViajesPorPatente()`, ordenado) y la lista de patentes con **más de un viaje** (`getPatentesConMasDeUnViaje()`).',
             [ch(r'Map<String,\s*Long>\s+getViajesPorPatente\s*\(\s*\)', 'Viajes por patente', 'Falta `public Map<String, Long> getViajesPorPatente()`', 'Flota.java'),
              ch(r'groupingBy\s*\(\s*VehiculoRuta::getPatente', 'Agrupa por patente', 'Agrupá por `VehiculoRuta::getPatente`', 'Flota.java'),
              ch(r'List<String>\s+getPatentesConMasDeUnViaje\s*\(\s*\)', 'Las repetidas', 'Falta `public List<String> getPatentesConMasDeUnViaje()`', 'Flota.java'),
              ch(r'>\s*1\b', 'Más de un viaje', 'Filtrá las que tienen más de 1 viaje', 'Flota.java')],
             ['`groupingBy(VehiculoRuta::getPatente, TreeMap::new, Collectors.counting())`.', 'Para las repetidas: `entrySet().stream()`, `filter(e -> e.getValue() > 1)`, `map(Map.Entry::getKey)` y `toList()`.'],
             ['Reutilizá `getViajesPorPatente()` adentro de la otra.', '`toList()` (Java 16+) devuelve una lista que no se puede modificar.'],
             'a (2 viajes), b, c → `{a=2, b=1, c=1}` y `[a]`. Con el CSV del preenunciado no hay repetidas: `[]`.',
             LISTA + '''        igual(Map.of("a", 2L, "b", 1L, "c", 1L), f.getViajesPorPatente(), "viajes por patente"); igual(List.of("a"), f.getPatentesConMasDeUnViaje(), "las repetidas");
        igual(List.of(), vacia.getPatentesConMasDeUnViaje(), "vacía");
'''),
    flota_ej('r4.5', 'velocidad promedio por zona', [M_VELOCIDAD],
             'Agregá a `Flota` la **velocidad promedio** de cada zona (`getVelocidadPromedioPorZona()`), ordenada por zona. Con la flota vacía, un mapa vacío.',
             [ch(r'Map<String,\s*Double>\s+getVelocidadPromedioPorZona\s*\(\s*\)', 'El método nuevo', 'Falta `public Map<String, Double> getVelocidadPromedioPorZona()`', 'Flota.java'),
              ch(r'groupingBy\s*\(\s*VehiculoRuta::getZona', 'Agrupa por zona', 'Agrupá por `VehiculoRuta::getZona`', 'Flota.java'),
              ch(r'averagingInt\s*\(\s*VehiculoRuta::getVelocidadPromedio', 'Promedia la velocidad', 'Usá `Collectors.averagingInt(VehiculoRuta::getVelocidadPromedio)`', 'Flota.java')],
             ['`groupingBy(VehiculoRuta::getZona, TreeMap::new, Collectors.averagingInt(VehiculoRuta::getVelocidadPromedio))`.'],
             ['`averagingInt` devuelve `Double`: el mapa es `Map<String, Double>`.', 'Para sumar por zona sería `summingInt`; para contar, `counting()`.'],
             'NORTE (60) · SUR (60 y 70) · CENTRO (101) → `{CENTRO=101.0, NORTE=60.0, SUR=65.0}`. Con el CSV del preenunciado: CENTRO 78,83 · NORTE 77,09 · SUR 68,44.',
             LISTA + '''        igual(Map.of("CENTRO", 101.0, "NORTE", 60.0, "SUR", 65.0), f.getVelocidadPromedioPorZona(), "promedios"); igual(Map.of(), vacia.getVelocidadPromedioPorZona(), "vacía");
'''),
    flota_ej('r4.6', 'kilómetros por zona y el de más kilómetros', [M_KM],
             'Con el caso B (`kilometros` ya está en `VehiculoRuta`), agregá a `Flota` los **kilómetros totales por zona** (`getKilometrosPorZona()`, ordenado) y el vehículo con **más kilómetros** (`getConMasKilometros()`, un `Optional`).',
             [ch(r'Map<String,\s*Integer>\s+getKilometrosPorZona\s*\(\s*\)', 'Kilómetros por zona', 'Falta `public Map<String, Integer> getKilometrosPorZona()`', 'Flota.java'),
              ch(r'summingInt\s*\(\s*VehiculoRuta::getKilometros', 'Suma los kilómetros', 'Usá `Collectors.summingInt(VehiculoRuta::getKilometros)`', 'Flota.java'),
              ch(r'Optional<VehiculoRuta>\s+getConMasKilometros\s*\(\s*\)', 'El de más kilómetros', 'Falta `public Optional<VehiculoRuta> getConMasKilometros()`', 'Flota.java'),
              ch(r'comparingInt\s*\(\s*VehiculoRuta::getKilometros', 'Compara por kilómetros', 'Usá `max(Comparator.comparingInt(VehiculoRuta::getKilometros))`', 'Flota.java')],
             ['`groupingBy(VehiculoRuta::getZona, TreeMap::new, Collectors.summingInt(VehiculoRuta::getKilometros))`.', '`vehiculos.stream().max(Comparator.comparingInt(VehiculoRuta::getKilometros))`.'],
             ['`summingInt` da `Integer`; `counting` da `Long`.', 'Mirá en la otra pestaña el getter nuevo.'],
             'a (NORTE, 300 km) · b (SUR, 100) · c (SUR, 1200) → `{NORTE=300, SUR=1300}` y el de más km es **c**.',
             '''        Flota f = new Flota(List.of(v("a", "NORTE", "60", "10", "EN_RUTA", "300"), v("b", "SUR", "60", "10", "EN_RUTA", "100"), v("c", "SUR", "60", "10", "DEMORADO", "1200")));
        igual(Map.of("NORTE", 300, "SUR", 1300), f.getKilometrosPorZona(), "km por zona"); igual("c", f.getConMasKilometros().get().getPatente(), "el de más km");
        igual(Optional.empty(), new Flota(List.of()).getConMasKilometros(), "vacía");
''', solo_ruta=B_RUTA),
    flota_ej('r4.7', 'reusar el filtro: costo de los DEMORADO y conteo entre dos índices', [M_FILTROS],
             'Agregá a `Flota` el **costo total de los DEMORADO** (`getCostoDemorados()`), **reutilizando** `sumarCostoDesgasteOperativo` con un `Predicate`, y cuántos vehículos tienen el índice **entre dos valores, inclusive** (`contarConIndiceEntre(int minimo, int maximo)`).',
             [ch(r'int\s+getCostoDemorados\s*\(\s*\)', 'El costo de los DEMORADO', 'Falta `public int getCostoDemorados()`', 'Flota.java'),
              ch(r'sumarCostoDesgasteOperativo\s*\(\s*\w+\s*->[^;]*"DEMORADO"', 'Reutiliza el filtro', 'Llamá a `sumarCostoDesgasteOperativo(v -> ...)` en lugar de repetir el stream', 'Flota.java'),
              ch(r'"DEMORADO"', 'Filtra los DEMORADO', 'El `Predicate` tiene que mirar si el estado es "DEMORADO"', 'Flota.java'),
              ch(r'long\s+contarConIndiceEntre\s*\(\s*int\s+\w+\s*,\s*int\s+\w+\s*\)', 'El conteo entre dos índices', 'Falta `public long contarConIndiceEntre(int minimo, int maximo)`', 'Flota.java'),
              ch(r'>=\s*\w+.*<=\s*\w+|<=\s*\w+.*>=\s*\w+', 'Inclusive en los dos extremos', 'Usá `>=` y `<=`: el rango es inclusive', 'Flota.java')],
             ['`return sumarCostoDesgasteOperativo(vehiculo -> "DEMORADO".equals(vehiculo.getEstado()));`', '`filter(v -> v.getIndiceDesgaste() >= minimo && v.getIndiceDesgaste() <= maximo).count()`.'],
             ['`"DEMORADO".equals(...)` no falla si el estado fuera `null`.', '`count()` devuelve `long`.', 'Así se usa el `Predicate<VehiculoRuta>` del preenunciado: el filtro lo arma quien llama.'],
             'b (800) y c (920) son DEMORADO → **1720** · índices 40, 40, 46 y 65 → entre 40 y 46: **3** · entre 47 y 64: **0**. Con el CSV del preenunciado, los DEMORADO suman **13880**.',
             LISTA + '''        igual(1720, f.getCostoDemorados(), "costo de los DEMORADO"); igual(3L, f.contarConIndiceEntre(40, 46), "entre 40 y 46"); igual(0L, f.contarConIndiceEntre(47, 64), "entre 47 y 64");
        igual(0, vacia.getCostoDemorados(), "vacía");
'''),
]

P5 = [
    codigo('r5.1', 'el main del recuperatorio', '`App` → `main` (mirá `Flota`, que ya tiene `contarPorTipoCarga()`)',
           'El main del caso A: usar `datos/datos-parcial.csv` por defecto (y seguir aceptando un argumento) y mostrar el resumen de errores, la **cantidad de objetos**, las cantidades **GENERAL y REFRIGERADA** (en cero si no hay) y el panorama. '
           'El conteo ya está en `Flota.contarPorTipoCarga()` (parte 4). El main no calcula.',
           [arch('App.java', ORIG['App.java'], A_APP), arch('Flota.java', A_FLOTA, solo=True)],
           [ch(r'datos-parcial\.csv', 'El CSV del recuperatorio por defecto', 'La ruta por defecto tiene que ser `datos/datos-parcial.csv`', 'App.java'),
            ch(r'args\.length', 'Sigue aceptando un argumento', 'Seguí aceptando la ruta como argumento (`args`)', 'App.java'),
            ch(r'contarPorTipoCarga\s*\(', 'Usa el conteo del colector', 'Pedile el conteo a la flota: `flota.contarPorTipoCarga()`', 'App.java'),
            ch(r'getOrDefault\s*\(\s*"GENERAL"\s*,\s*0L?\s*\)', 'GENERAL, en cero si no hay', 'Mostrá GENERAL con `getOrDefault("GENERAL", 0L)`', 'App.java'),
            ch(r'getOrDefault\s*\(\s*"REFRIGERADA"\s*,\s*0L?\s*\)', 'REFRIGERADA, en cero si no hay', 'Mostrá REFRIGERADA con `getOrDefault("REFRIGERADA", 0L)`', 'App.java'),
            ch(r'getVehiculos\s*\(\s*\)\s*\.size\s*\(\s*\)', 'La cantidad de objetos', 'Mostrá cuántos objetos se crearon: `resultado.getVehiculos().size()`', 'App.java'),
            ch(r'\bfor\s*\(|\.stream\s*\(', 'El main no calcula', 'Sacá el `for` o el `stream` del main: eso va en `Flota`', 'App.java', 'noContiene')],
           ['Cambiá la ruta por defecto: `Path.of("datos", "datos-parcial.csv")`.', 'Guardá `flota.contarPorTipoCarga()` en un `Map<String, Long>`.',
            'Imprimí `"Objetos: " + resultado.getVehiculos().size()`.', 'Imprimí GENERAL y REFRIGERADA con `getOrDefault(..., 0L)`.', 'Dejá el resumen y el `panorama()`.'],
           ['`getOrDefault("REFRIGERADA", 0L)`: si en el archivo no hay ninguna, la clave no está y `get` daría `null`.', 'Importá `java.util.Map`.'],
           datos='Con 3 filas (GENERAL, REFRIGERADA, REFRIGERADA): `Objetos: 3` y `GENERAL: 1 | REFRIGERADA: 2`, y después el panorama con el total (con los recargos) y los totales por zona.',
           prueba='''        java.nio.file.Path p = csv("''' + HA + '''", "a,NORTE,60,10,EN_RUTA,GENERAL", "b,NORTE,60,10,EN_RUTA,REFRIGERADA", "c,SUR,60,30,DEMORADO,REFRIGERADA", "d,SUR,60,10,PERDIDO,GENERAL");
        String s = salida(p.toString());
        contiene(s, "Objetos: 3"); contiene(s, "GENERAL: 1"); contiene(s, "REFRIGERADA: 2"); contiene(s, "Costo total por desgaste operativo: 3160"); contiene(s, "Inválidas: 1");
''', base={'ParserVehiculos.java': A_PARSER, 'VehiculoRuta.java': A_RUTA, 'VehiculoRefrigerado.java': A_REF}),
    codigo('r5.2', 'sacar la lógica del main', '`App` y `Flota`',
           'Este main **calcula**: cuenta los DEMORADO y busca el de mayor costo con un `for`. Pasá esas cuentas a `Flota` (`contarPorEstado()` y `getMayorCosto()`, como en la parte 4) y que el main solo las llame e imprima lo mismo.',
           [arch('App.java', APP_LOGICA, APP_DELEGA), arch('Flota.java', ORIG['Flota.java'], flota_con(M_ESTADO, M_MAYOR))],
           [ch(r'\bfor\s*\(', 'Sin `for` en el main', 'El main no tiene que recorrer: el `for` va en `Flota`', 'App.java', 'noContiene'),
            ch(r'contarPorEstado\s*\(', 'Usa el conteo por estado', 'Llamá a `flota.contarPorEstado()`', 'App.java'),
            ch(r'getMayorCosto\s*\(', 'Usa el de mayor costo', 'Llamá a `flota.getMayorCosto()`', 'App.java'),
            ch(r'Map<String,\s*Long>\s+contarPorEstado\s*\(\s*\)', 'El conteo, en la Flota', 'Falta `public Map<String, Long> contarPorEstado()` en `Flota`', 'Flota.java'),
            ch(r'Optional<VehiculoRuta>\s+getMayorCosto\s*\(\s*\)', 'El mayor, en la Flota', 'Falta `public Optional<VehiculoRuta> getMayorCosto()` en `Flota`', 'Flota.java'),
            ch(r'orElse\s*\(|isPresent\s*\(|ifPresent', 'Contempla la flota vacía', 'El `Optional` puede estar vacío: usá `map(...).orElse("-")`', 'App.java')],
           ['En `Flota`: `contarPorEstado()` (groupingBy + counting) y `getMayorCosto()` (max + comparingInt).',
            'En el main: `flota.contarPorEstado().getOrDefault("DEMORADO", 0L)`.', '`flota.getMayorCosto().map(VehiculoRuta::getPatente).orElse("-")`.', 'Borrá el `for` y las variables auxiliares.'],
           ['Regla del parcial: si en el main hay un `for`, un `stream` o una cuenta, va en otra clase.', 'La salida tiene que ser la misma de antes.'],
           datos='Con el CSV del preenunciado: `DEMORADO: 14` y `Mayor costo: trk-0038`, más el resumen y el panorama de siempre.',
           prueba='''        java.nio.file.Path p = csv("''' + H5 + '''", "a,NORTE,60,10,EN_RUTA", "b,SUR,60,10,DEMORADO", "c,SUR,101,11,DEMORADO");
        String s = salida(p.toString());
        contiene(s, "DEMORADO: 2"); contiene(s, "Mayor costo: c"); contiene(s, "Costo total por desgaste operativo: 2900");
        igual(Optional.empty(), new Flota(List.of()).getMayorCosto(), "vacía");
'''),
    codigo('r5.3', 'el main (como el 3K1)', '`App` → `main` (mirá `Flota`, que ya tiene `contarPorEstado()`)',
           'El main del caso D, igual al que pidió el Parcial 3K1: usar `datos/datos-parcial.csv` por defecto (y seguir aceptando un argumento) y mostrar el resumen, la **cantidad de objetos**, las cantidades **EN_RUTA y DEMORADO** (en cero si no hay) y el panorama (el total y los totales por zona). '
           'El conteo ya está en `Flota.contarPorEstado()` (parte 4). El main no calcula.',
           [arch('App.java', ORIG['App.java'], D_APP), arch('Flota.java', flota_con(M_ESTADO), solo=True)],
           [ch(r'datos-parcial\.csv', 'El CSV del examen por defecto', 'La ruta por defecto tiene que ser `datos/datos-parcial.csv`', 'App.java'),
            ch(r'contarPorEstado\s*\(', 'Usa el conteo del colector', 'Pedile el conteo a la flota: `flota.contarPorEstado()`', 'App.java'),
            ch(r'getOrDefault\s*\(\s*"EN_RUTA"\s*,\s*0L?\s*\)', 'EN_RUTA, en cero si no hay', 'Mostrá EN_RUTA con `getOrDefault("EN_RUTA", 0L)`', 'App.java'),
            ch(r'getOrDefault\s*\(\s*"DEMORADO"\s*,\s*0L?\s*\)', 'DEMORADO, en cero si no hay', 'Mostrá DEMORADO con `getOrDefault("DEMORADO", 0L)`', 'App.java'),
            ch(r'getVehiculos\s*\(\s*\)\s*\.size\s*\(\s*\)', 'La cantidad de objetos', 'Mostrá cuántos objetos se crearon: `resultado.getVehiculos().size()`', 'App.java'),
            ch(r'\bfor\s*\(|\.stream\s*\(', 'El main no calcula', 'Sacá el `for` o el `stream` del main: eso va en `Flota`', 'App.java', 'noContiene')],
           ['Cambiá la ruta por defecto: `Path.of("datos", "datos-parcial.csv")`.', 'Guardá `flota.contarPorEstado()` en un `Map<String, Long>`.',
            'Imprimí `"Objetos: " + resultado.getVehiculos().size()`.', 'Imprimí EN_RUTA y DEMORADO con `getOrDefault(..., 0L)`.', 'Dejá el resumen y el `panorama()`.'],
           ['En el 3K1 eran ALERTA / CRITICO; acá, EN_RUTA / DEMORADO.', '`getOrDefault` evita el `null` si un estado no aparece.', 'Importá `java.util.Map`.'],
           datos='Con 3 filas (2 EN_RUTA, 1 DEMORADO, facturación 3000, 2600 y 2000): `Objetos: 3` y `EN_RUTA: 2 | DEMORADO: 1`, y el panorama con el total 3690.',
           prueba='''        java.nio.file.Path p = csv("''' + HD + '''", "a,NORTE,60,10,EN_RUTA,3000", "b,CENTRO,101,11,DEMORADO,2600", "c,SUR,60,10,EN_RUTA,2000", "d,SUR,60,10,EN_RUTA,3800");
        String s = salida(p.toString());
        contiene(s, "Objetos: 3"); contiene(s, "EN_RUTA: 2"); contiene(s, "DEMORADO: 1"); contiene(s, "Costo total por desgaste operativo: 3690"); contiene(s, "Inválidas: 1");
''', base={'ParserVehiculos.java': D_PARSER, 'VehiculoRuta.java': D_RUTA, 'VehiculoConFacturacion.java': D_FAC}),
]

PARTES = [
    dict(n=0, id='r-ubicar', titulo='¿Dónde va cada cambio?', corto='Leer la consigna', pestana='Consigna',
         explicacion='El recuperatorio no trae tareas en el preenunciado: el día del examen piden cambios. Antes de escribir código, ubicá cada pedido: la forma del CSV va en el **Parser**; el dato nuevo, sus validaciones y cálculos, en el **dominio** (`VehiculoRuta`); conteos y totales, en el **colector** (`Flota`); mostrar, en el **Main** (`App`).',
         guia=[['Parser', 'La forma del archivo: las cabeceras, el ancho de cada fila, el separador, los descartes (EN_DEPOSITO y los que agreguen) y qué estados se aceptan.'],
               ['Dominio', 'El dato nuevo: `desdeCampos`, el constructor, el atributo y su getter, las validaciones y los cálculos. Si cambia un cálculo para algunos, una subclase (y ojo: `VehiculoRuta` es `final`).'],
               ['Colector', 'Lo que se calcula sobre todos: conteos, totales, promedios, máximos y agrupamientos (`groupingBy`), en `Flota`.'],
               ['Main', 'Solo mostrar: la ruta por defecto y qué se imprime, llamando métodos.']], ejercicios=P0),
    dict(n=1, id='r-formatos', titulo='Lectura de dos formatos (Parser)', corto='Lectura de dos formatos', pestana='CSV',
         explicacion='El parser reconoce dos cabeceras y la primera línea define cuántas columnas (y qué separador) tiene que tener **cada** fila. Un **solo loop** para los dos formatos. El orden es siempre: ancho → descarte → validaciones.', ejercicios=P1),
    dict(n=2, id='r-dominio', titulo='Columna nueva en el dominio', corto='Columna nueva en el dominio', pestana='Dominio',
         explicacion='Atributo + getter nuevos; constructor nuevo, con el viejo **delegando** con `this(...)`; `desdeCampos` acepta los dos anchos y lee la columna nueva **solo si existe**. Las validaciones nuevas van acá. Y practicá cómo se clasifica cada fila: el índice se trunca con `(int)` y la carga negativa no se valida.', ejercicios=P2),
    dict(n=3, id='r-polimorfismo', titulo='Cálculo distinto con polimorfismo', corto='Polimorfismo', pestana='Polimorfismo',
         explicacion='Cuando el dato nuevo cambia un **cálculo para algunos**, una subclase redefine el método (`@Override`) y reutiliza el del padre con `super`. `desdeCampos` decide qué clase crear. **En este preenunciado `VehiculoRuta` es `final`: hay que sacárselo.** `Flota` no cambia ni usa `instanceof`.', ejercicios=P3),
    dict(n=4, id='r-colector', titulo='Operación nueva en el colector', corto='Colector', pestana='Colector',
         explicacion='Conteos, totales, promedios y máximos con Streams en `Flota`: `groupingBy(..., counting())`, `summingInt`, `averagingInt`, `max(Comparator.comparingInt(...))` y el `sumarCostoDesgasteOperativo(Predicate)` que ya trae. Una flota vacía da un mapa vacío, 0 o `Optional.empty()`.', ejercicios=P4),
    dict(n=5, id='r-main', titulo='Main delegando', corto='Main', pestana='Main',
         explicacion='El CSV del examen por defecto; se imprime todo **llamando métodos**. Si en el main hay un `for`, un `stream` o una cuenta, eso va en otra clase.', ejercicios=P5),
]


CASOS = {
    'Caso A': ['r0.1', 'r1.1', 'r2.3', 'r3.1', 'r4.2', 'r5.1'],
    'Caso B': ['r0.2', 'r1.3', 'r2.1', 'r2.4', 'r4.6'],
    'Caso C': ['r0.3', 'r1.2', 'r2.5', 'r3.2'],
    'Caso D': ['r0.4', 'r1.4', 'r2.6', 'r3.4', 'r4.1', 'r5.3'],
    'Repaso': ['r3.3'],
}   # el resto trabaja sobre el preenunciado tal cual


def main():
    caso = {id: c for c, ids in CASOS.items() for id in ids}
    orden = {c: i for i, c in enumerate(['Preenunciado', 'Caso A', 'Caso B', 'Caso C', 'Caso D', 'Repaso'])}
    for p in PARTES:   # en cada parte, los casos en orden (A, B, C, D) y el repaso al final
        p['ejercicios'].sort(key=lambda e: orden[caso.get(e['id'], 'Preenunciado')])
    for p in PARTES:
        for e in p['ejercicios']:
            e['tema'] = caso.get(e['id'], 'Preenunciado')
    datos = dict(grupo='Recuperatorio · Flota Logística', partes=PARTES)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write('\n')
    # Las pruebas de cada ejercicio (las corre validar.py)
    for id, (cuerpo, base) in PRUEBA.items():
        d = os.path.join(PRUEBAS, id)
        if os.path.isdir(d): shutil.rmtree(d)
        os.makedirs(d)
        open(os.path.join(d, 'Prueba.java'), 'w', encoding='utf-8').write(CABEZA + cuerpo + ('    }\n}\n' if cuerpo is CLASIFICA else PIE))
        if base:
            os.makedirs(os.path.join(d, 'base'))
            for n, t in base.items(): open(os.path.join(d, 'base', n), 'w', encoding='utf-8').write(t)
    n = sum(len(p['ejercicios']) for p in PARTES)
    print(f'{len(PARTES)} partes y {n} ejercicios →', os.path.relpath(SALIDA, RAIZ), '·', len(PRUEBA), 'pruebas')


if __name__ == '__main__':
    main()
