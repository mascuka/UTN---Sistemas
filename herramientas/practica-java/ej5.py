from comun import *
from ej4 import cambiar

P = "utnfc/backend/parcial/"
FC, FA, FR, FP, FL, FM = P + "Consumo.java", P + "ConsumoAsegurado.java", P + "ResultadoParseo.java", P + "ParserLiquidaciones.java", P + "LiquidadorTarjetas.java", P + "Main.java"
ORIG = {f: leer("proyectos", "tarjetas", f.split("/")[-1]) for f in (FC, FR, FP, FL, FM)}

C1 = cambiar(ORIG[FC],
    ('''    public int comision() { return centavos * 2 / 100; }''', '''    public String modalidad() { return "SIN_SEGURO"; }
    public int comision() { return centavos * 2 / 100; }'''))

ASEGURADO = '''package utnfc.backend.parcial;

public class ConsumoAsegurado extends Consumo {
    private final int diasCobertura;

    public ConsumoAsegurado(String id, String rubro, int importe, int bonificacion, int diasCobertura) {
        super(id, rubro, importe, bonificacion);
        if (diasCobertura != 30 && diasCobertura != 90 && diasCobertura != 180) {
            throw new IllegalArgumentException("plazo de cobertura inválido: " + diasCobertura);
        }
        if (getCentavos() > 500_000) {
            throw new IllegalArgumentException("asegurado supera 500000 centavos: " + getCentavos());
        }
        this.diasCobertura = diasCobertura;
    }

    public int getDiasCobertura() { return diasCobertura; }

    @Override public String modalidad() { return "ASEGURADO"; }

    @Override public int comision() { return super.comision() + 200 * (diasCobertura / 30); }
}
'''
ASEGURADO_INICIO = '''package utnfc.backend.parcial;

public class ConsumoAsegurado extends Consumo {
    // El dato nuevo: diasCobertura (private final)

    public ConsumoAsegurado(String id, String rubro, int importe, int bonificacion, int diasCobertura) {
        super(id, rubro, importe, bonificacion);   // primero: la base valida los montos
        // después: el plazo (30, 90 o 180) y el neto máximo (500000), y guardar los días
    }

    // getDiasCobertura(), modalidad() y comision() redefinidos
}
'''

C3 = cambiar(C1,
    ('''        if (c.length != 5) throw new IllegalArgumentException("se esperan 5 columnas");
        int importe = Integer.parseInt(c[2]);
        int bonificacion = Integer.parseInt(c[3]);
        return new Consumo(c[0], c[1], importe, bonificacion);''', '''        if (c.length != 5 && c.length != 6) throw new IllegalArgumentException("se esperan 5 o 6 columnas");
        int importe = Integer.parseInt(c[2]);
        int bonificacion = Integer.parseInt(c[3]);
        if (c.length == 5) return new Consumo(c[0], c[1], importe, bonificacion);
        int dias = Integer.parseInt(c[5]);
        if (dias == 0) return new Consumo(c[0], c[1], importe, bonificacion);
        return new ConsumoAsegurado(c[0], c[1], importe, bonificacion, dias);'''))

P4 = cambiar(ORIG[FP],
    ('''    private static final String CABECERA = "id,rubro,importeCentavos,bonificacionCentavos,estado";''', '''    private static final String CABECERA = "id,rubro,importeCentavos,bonificacionCentavos,estado";
    private static final String CABECERA_COBERTURA = CABECERA + ",diasCobertura";'''),
    ('''            if (!CABECERA.equals(reader.readLine())) {
                throw new IllegalArgumentException("encabezado incorrecto");
            }''', '''            String cabecera = reader.readLine();
            int columnas;
            if (CABECERA.equals(cabecera)) columnas = 5;
            else if (CABECERA_COBERTURA.equals(cabecera)) columnas = 6;
            else throw new IllegalArgumentException("encabezado incorrecto");'''),
    ('''                    if (c.length != 5) throw''', '''                    if (c.length != columnas) throw'''))

L5 = cambiar(ORIG[FL],
    ('''    public String panorama() {''', '''    /** Cuántos consumos hay de cada modalidad. Vacío si no hay consumos. */
    public Map<String, Long> conteoPorModalidad() {
        return consumos.stream().collect(Collectors.groupingBy(Consumo::modalidad, java.util.TreeMap::new, Collectors.counting()));
    }

    public String panorama() {'''))

M6 = cambiar(ORIG[FM],
    ('''import java.nio.file.Path;''', '''import java.nio.file.Path;
import java.util.Map;'''),
    ('''        Path archivo = Path.of(args.length == 0 ? "datos/datos.csv" : args[0]);''', '''        Path archivo = Path.of(args.length == 0 ? "datos/datos-parcial.csv" : args[0]);'''),
    ('''        System.out.println(liquidador.panorama());''', '''        Map<String, Long> porModalidad = liquidador.conteoPorModalidad();
        System.out.println("SIN_SEGURO: %d | ASEGURADO: %d".formatted(
                porModalidad.getOrDefault("SIN_SEGURO", 0L), porModalidad.getOrDefault("ASEGURADO", 0L)));
        System.out.println(liquidador.panorama());'''))

NUEVO = "id,rubro,importeCentavos,bonificacionCentavos,estado,diasCobertura"
VIEJO = "id,rubro,importeCentavos,bonificacionCentavos,estado"

E = ej(
    'bk-simulacro-4', 'Simulacro 4 · Protección de compras', 'Simulacro · 3K7 · Tarjetas de crédito',
    'Otro dominio, el mismo esquema de parcial: el consumo asegurado con herencia, los dos formatos, el conteo por modalidad y el main.',
    [
        h('Parcial práctico: protección de compras'),
        pr('Partir exactamente del proyecto preparcial (liquidación de tarjetas). La liquidación incorpora la protección de compra: un seguro sobre lo que se compra. Hay que procesar consumos con y sin cobertura en una misma colección y obtener sus comisiones correctas.', 2),
        h('Reglas nuevas'),
        li('El nuevo encabezado es id,rubro,importeCentavos,bonificacionCentavos,estado,diasCobertura. El formato original de cinco columnas sigue valiendo: todos esos consumos son sin seguro. Cada fila tiene que tener el ancho de su encabezado.', 3, 4),
        li('En las filas APROBADO del formato nuevo, el sexto campo es un entero (sin los espacios de afuera). 0 es un consumo sin seguro, con las reglas y la comisión de siempre.', 3),
        li('30, 90 o 180 son plazos de cobertura: el consumo queda asegurado. Respeta las validaciones anteriores, admite como máximo 500000 centavos netos y suma una prima de 200 centavos por cada 30 días sobre la comisión de un consumo sin seguro.', 2),
        li('Un valor vacío, no numérico o un plazo distinto de 0, 30, 90 o 180 hace inválida la fila.', 2, 3),
        li('Se conserva el orden del preparcial: primero el ancho, después se descarta ANULADO sin validar montos ni días. Las filas inválidas se anotan y la carga sigue.', 4),
        code('Neto 100000 → comisión 2000 (sin seguro) · 2200 (30 días) · 2600 (90) · 3200 (180)\nNeto 500000 con 90 días → 10600 · neto 500001 con 90 días → inválido', 2),
        h('Resultado requerido'),
        li('1. Leer las dos versiones del CSV sin duplicar la carga. La construcción desde los campos queda en el dominio (desdeCampos).', 3, 4),
        li('2. Que comision(), getTotalLiquidacion(), los filtros y totalesPorRubro() reflejen la regla nueva.', 1, 2, 5),
        li('3. Agregar en el colector un conteo por modalidad (vacío o en cero si no hay consumos).', 1, 5),
        li('4. Que el main use por defecto el archivo del parcial y muestre el resumen, la cantidad de objetos, las cantidades SIN_SEGURO y ASEGURADO, el total y los totales por rubro.', 6),
    ],
    {'datos/datos.csv': leer('datos', 'consumos.csv'), 'datos/datos-parcial.csv': leer('datos', 'consumos-parcial.csv')},
    [
        paso('La modalidad en Consumo', FC,
             ['Agregá en Consumo el método modalidad(), que devuelve "SIN_SEGURO".',
              'Es el gancho: la subclase lo va a redefinir. Con él, el colector va a poder contar por modalidad.'],
             ['public String modalidad()'],
             [('Un consumo común es SIN_SEGURO', '''
Prueba.igual("SIN_SEGURO", new Consumo("C01", "Alimentos", 120000, 20000).modalidad(), "modalidad()");
'''),
              ('La comisión de siempre no cambia: neto 100000 → 2000', '''
Prueba.igual(2000, new Consumo("C01", "Alimentos", 120000, 20000).comision(), "comision() con neto 100000");
''')],
             {FC: C1}, inicio=dict(ORIG),
             pistas=['public String modalidad() { return "SIN_SEGURO"; }']),
        paso('La subclase ConsumoAsegurado', FA,
             ['Creá ConsumoAsegurado extends Consumo con el atributo diasCobertura.',
              'En el constructor, primero super(…) y después validá: el plazo tiene que ser 30, 90 o 180, y el neto (getCentavos()) como máximo 500000.',
              'Redefiní modalidad() ("ASEGURADO") y comision(): la de la base más 200 por cada 30 días.'],
             ['public ConsumoAsegurado(String id, String rubro, int importe, int bonificacion, int diasCobertura)', 'public String modalidad()  ← "ASEGURADO"', 'public int comision()  ← super.comision() + 200 * (diasCobertura / 30)'],
             [('La tabla del enunciado: neto 100000 con 30, 90 y 180 días', '''
Prueba.igual(2200, new ConsumoAsegurado("P1", "Alimentos", 120000, 20000, 30).comision(), "comisión con 30 días");
Prueba.igual(2600, new ConsumoAsegurado("P1", "Alimentos", 120000, 20000, 90).comision(), "comisión con 90 días");
Prueba.igual(3200, new ConsumoAsegurado("P1", "Alimentos", 120000, 20000, 180).comision(), "comisión con 180 días");
'''),
              ('Neto 500000 con 90 días vale 10600; con 500001, es inválido', '''
Prueba.igual(10600, new ConsumoAsegurado("P2", "Servicios", 500000, 0, 90).comision(), "comisión con neto 500000 y 90 días");
Prueba.lanza(IllegalArgumentException.class, () -> new ConsumoAsegurado("P3", "Servicios", 500001, 0, 90), "neto 500001");
'''),
              ('Solo valen los plazos de 30, 90 y 180 días', '''
Prueba.lanza(IllegalArgumentException.class, () -> new ConsumoAsegurado("P4", "Alimentos", 120000, 20000, 60), "60 días");
Prueba.lanza(IllegalArgumentException.class, () -> new ConsumoAsegurado("P4", "Alimentos", 120000, 20000, 0), "0 días (eso es un consumo sin seguro)");
Prueba.igual(90, new ConsumoAsegurado("P4", "Alimentos", 120000, 20000, 90).getDiasCobertura(), "getDiasCobertura()");
'''),
              ('Las validaciones de Consumo siguen valiendo', '''
Prueba.lanza(IllegalArgumentException.class, () -> new ConsumoAsegurado("P5", "Alimentos", 10000, 10000, 30), "bonificación igual al importe");
'''),
              ('Es ASEGURADO y el liquidador lo suma sin cambios (polimorfismo)', '''
Consumo a = new ConsumoAsegurado("P6", "Alimentos", 120000, 20000, 90);
Prueba.igual("ASEGURADO", a.modalidad(), "modalidad() del asegurado");
List<Consumo> l = List.of(a, new Consumo("C1", "Alimentos", 120000, 20000));
Prueba.igual(2600 + 2000, new LiquidadorTarjetas(l).getTotalLiquidacion(), "getTotalLiquidacion() con uno de cada clase");
''')],
             {FA: ASEGURADO}, inicio={FA: ASEGURADO_INICIO},
             pistas=['if (diasCobertura != 30 && diasCobertura != 90 && diasCobertura != 180) throw new IllegalArgumentException("…");',
                     'if (getCentavos() > 500_000) throw … — el neto ya lo calculó la base.',
                     '@Override public int comision() { return super.comision() + 200 * (diasCobertura / 30); }']),
        paso('desdeCampos: 5 o 6 campos', FC,
             ['desdeCampos acepta 5 o 6 campos. Con 5, un Consumo como antes.',
              'Con 6: convertí los días con Integer.parseInt(c[5]). Con 0, un Consumo sin seguro; si no, un ConsumoAsegurado (que valida el plazo).',
              'Si el sexto campo está vacío o no es un número, parseInt ya tira NumberFormatException y la fila queda inválida.'],
             ['public static Consumo desdeCampos(String[] c)  ← 5 o 6 campos'],
             [('Con 0 días es un consumo sin seguro', '''
Consumo c = Consumo.desdeCampos(new String[] { "P001", "Alimentos", "135000", "35000", "APROBADO", "0" });
Prueba.verdad(!(c instanceof ConsumoAsegurado), "con 0 días tiene que ser un Consumo común");
Prueba.igual(2000, c.comision(), "comisión con 0 días");
'''),
              ('Con 90 días es un ConsumoAsegurado', '''
Consumo c = Consumo.desdeCampos(new String[] { "P002", "Combustible", "142500", "42500", "APROBADO", "90" });
Prueba.verdad(c instanceof ConsumoAsegurado, "con 90 días tiene que crear un ConsumoAsegurado");
Prueba.igual(2600, c.comision(), "comisión con 90 días");
'''),
              ('Con 5 campos sigue creando un Consumo', '''
Consumo c = Consumo.desdeCampos(new String[] { "C01", "Alimentos", "120000", "20000", "APROBADO" });
Prueba.verdad(!(c instanceof ConsumoAsegurado), "con 5 campos tiene que ser un Consumo común");
'''),
              ('Un sexto campo vacío, con letras o con un plazo raro es inválido', '''
Prueba.lanza(NumberFormatException.class, () -> Consumo.desdeCampos(new String[] { "P", "Alimentos", "120000", "20000", "APROBADO", "" }), "días vacío");
Prueba.lanza(NumberFormatException.class, () -> Consumo.desdeCampos(new String[] { "P", "Alimentos", "120000", "20000", "APROBADO", "URGENTE" }), "días \\"URGENTE\\"");
Prueba.lanza(IllegalArgumentException.class, () -> Consumo.desdeCampos(new String[] { "P", "Alimentos", "120000", "20000", "APROBADO", "15" }), "15 días");
''')],
             {FC: C3},
             pistas=['if (c.length == 5) return new Consumo(c[0], c[1], importe, bonificacion);',
                     'int dias = Integer.parseInt(c[5]); if (dias == 0) return new Consumo(…); return new ConsumoAsegurado(…, dias);']),
        paso('Un solo parser para los dos formatos', FP,
             ['Leé el encabezado una vez y decidí cuántas columnas tiene cada fila: 5 con el viejo, 6 con el nuevo (",diasCobertura"). Si no es ninguno, IllegalArgumentException.',
              'Cada fila se controla contra esa cantidad.',
              'El orden queda igual: primero el ancho, después ANULADO se descarta sin mirar los días.'],
             ['private static final String CABECERA_COBERTURA = CABECERA + ",diasCobertura";'],
             [('El archivo viejo sigue igual: 39 procesadas, 6 descartadas y 15 inválidas', '''
ResultadoParseo r = new ParserLiquidaciones().leer(Path.of("datos/datos.csv"));
Prueba.igual(39, r.getProcesadas(), "procesadas de datos.csv");
Prueba.igual(6, r.getDescartadas(), "descartadas de datos.csv");
Prueba.igual(15, r.getInvalidas(), "inválidas de datos.csv");
'''),
              ('datos-parcial.csv: 140 leídas, 100 procesadas, 16 descartadas y 24 inválidas', '''
ResultadoParseo r = new ParserLiquidaciones().leer(Path.of("datos/datos-parcial.csv"));
Prueba.igual(140, r.getLeidas(), "leídas");
Prueba.igual(100, r.getProcesadas(), "procesadas");
Prueba.igual(16, r.getDescartadas(), "descartadas");
Prueba.igual(24, r.getInvalidas(), "inválidas");
'''),
              ('Cada fila tiene que tener el ancho de su encabezado', '''
Path p = Prueba.archivo("datos/mezcla6.csv", "''' + NUEVO + '''\\nP1,Alimentos,120000,20000,APROBADO\\nP2,Alimentos,120000,20000,APROBADO,30\\n");
Prueba.igual(1, new ParserLiquidaciones().leer(p).getProcesadas(), "procesadas con encabezado de 6 (una fila tiene 5)");
Path q = Prueba.archivo("datos/mezcla5.csv", "''' + VIEJO + '''\\nP1,Alimentos,120000,20000,APROBADO,30\\nP2,Alimentos,120000,20000,APROBADO\\n");
Prueba.igual(1, new ParserLiquidaciones().leer(q).getProcesadas(), "procesadas con encabezado de 5 (una fila tiene 6)");
'''),
              ('ANULADO se descarta sin mirar los días', '''
Path p = Prueba.archivo("datos/anulado.csv", "''' + NUEVO + '''\\nP1,Alimentos,120000,20000,ANULADO,abc\\n");
ResultadoParseo r = new ParserLiquidaciones().leer(p);
Prueba.igual(1, r.getDescartadas(), "descartadas");
Prueba.igual(0, r.getInvalidas(), "inválidas (un ANULADO con días \\"abc\\" se descarta, no es inválido)");
''')],
             {FP: P4},
             pistas=['String cabecera = reader.readLine(); y después if / else if / else para elegir 5, 6 o tirar la excepción.',
                     'if (c.length != columnas) throw new IllegalArgumentException("cantidad de columnas incorrecta");']),
        paso('Contar por modalidad', FL,
             ['Agregá en LiquidadorTarjetas conteoPorModalidad(): agrupá por Consumo::modalidad con Collectors.counting().',
              'getTotalLiquidacion(), los filtros y totalesPorRubro() no se tocan: ya usan comision() y el polimorfismo hace el resto.'],
             ['public Map<String, Long> conteoPorModalidad()'],
             [('Cuenta por modalidad', '''
List<Consumo> l = List.of(new ConsumoAsegurado("P1", "Alimentos", 120000, 20000, 30), new Consumo("C1", "Alimentos", 120000, 20000), new Consumo("C2", "Servicios", 60000, 10000));
Prueba.igual(Map.of("SIN_SEGURO", 2L, "ASEGURADO", 1L), new LiquidadorTarjetas(l).conteoPorModalidad(), "conteoPorModalidad()");
'''),
              ('Sin consumos, el conteo está vacío', '''
Prueba.verdad(new LiquidadorTarjetas(List.of()).conteoPorModalidad().isEmpty(), "sin consumos el conteo tiene que estar vacío");
'''),
              ('Con datos-parcial.csv: 55 sin seguro y 45 asegurados', '''
List<Consumo> c = new ParserLiquidaciones().leer(Path.of("datos/datos-parcial.csv")).getConsumos();
Prueba.igual(Map.of("SIN_SEGURO", 55L, "ASEGURADO", 45L), new LiquidadorTarjetas(c).conteoPorModalidad(), "conteoPorModalidad() con datos-parcial.csv");
'''),
              ('El total y los totales por rubro ya usan la regla nueva', '''
LiquidadorTarjetas t = new LiquidadorTarjetas(new ParserLiquidaciones().leer(Path.of("datos/datos-parcial.csv")).getConsumos());
Prueba.igual(1408456, t.getTotalLiquidacion(), "getTotalLiquidacion() con datos-parcial.csv");
Prueba.igual(Map.of("Alimentos", 475104, "Combustible", 436562, "Servicios", 496790), t.totalesPorRubro(), "totalesPorRubro() con datos-parcial.csv");
''')],
             {FL: L5},
             pistas=['consumos.stream().collect(Collectors.groupingBy(Consumo::modalidad, TreeMap::new, Collectors.counting()))']),
        paso('El main del parcial', FM,
             ['Por defecto, el main lee datos/datos-parcial.csv.',
              'Mostrá SIN_SEGURO y ASEGURADO por separado, aunque alguno dé 0 (getOrDefault).',
              'El resto queda igual: el resumen, los descartes, los errores y el panorama.'],
             ['Path.of(args.length == 0 ? "datos/datos-parcial.csv" : args[0])', '"SIN_SEGURO: %d | ASEGURADO: %d"'],
             [('Por defecto lee datos/datos-parcial.csv', '''
String s = Prueba.salida(() -> Main.main(new String[0]));
Prueba.contiene(s, "Leídas: 140 | procesadas: 100", "lo que muestra el main sin argumentos");
Prueba.contiene(s, "objetos: 100", "lo que muestra el main sin argumentos");
'''),
              ('Muestra SIN_SEGURO y ASEGURADO por separado', '''
String s = Prueba.salida(() -> Main.main(new String[0]));
Prueba.contiene(s, "SIN_SEGURO: 55", "lo que muestra el main");
Prueba.contiene(s, "ASEGURADO: 45", "lo que muestra el main");
'''),
              ('Con datos/datos.csv: 39 procesadas y ASEGURADO en 0', '''
String s = Prueba.salida(() -> Main.main(new String[] { "datos/datos.csv" }));
Prueba.contiene(s, "procesadas: 39", "lo que muestra el main con datos/datos.csv");
Prueba.contiene(s, "ASEGURADO: 0", "lo que muestra el main con datos/datos.csv");
''')],
             {FM: M6}, ejecutar={'entrada': FM, 'args': []},
             pistas=['Map<String, Long> porModalidad = liquidador.conteoPorModalidad();',
                     'porModalidad.getOrDefault("ASEGURADO", 0L) da 0 si no hay ninguno.']),
    ],
    importar=['utnfc.backend.parcial'], grupo='parcial', tema='parcial')
