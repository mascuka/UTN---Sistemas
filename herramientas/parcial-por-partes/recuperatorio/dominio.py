"""Más ejercicios de código para la parte 2 (Dominio) del recuperatorio por partes: todos arrancan del VehiculoRuta del
preenunciado tal cual y piden lo que más se repite en los parciales: una columna nueva (texto con valores fijos, entero
con rango, entero con valores permitidos, opcional por presencia), un estado nuevo válido y una validación nueva.
Las soluciones salen del VehiculoRuta original con cambios puntuales (cambiar(...) controla que cada cambio esté una vez)."""


def ejercicios(ORIG, codigo, arch, ch, tabla, cambiar, H5):
    R = ORIG['VehiculoRuta.java']
    CABEZA_CTOR = '''    public VehiculoRuta(
            String patente,
            String zona,
            int velocidadPromedio,
            int cargaToneladas,
            String estado,
            int indiceDesgaste) {
        this.patente = validarTexto(patente, "La patente no puede estar vacía");'''
    ANCHO5 = '''        if (campos == null || campos.length != 5) {
            throw new IllegalArgumentException("La fila debe tener exactamente cinco columnas");
        }'''
    ANCHO56 = '''        if (campos == null || (campos.length != 5 && campos.length != 6)) {
            throw new IllegalArgumentException("La fila debe tener cinco o seis columnas");
        }'''
    RETORNO = '''        int indiceDesgaste = calcularIndiceDesgaste(velocidadPromedio, cargaToneladas);

        return new VehiculoRuta(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste);'''
    ULTIMO_GETTER = '''    public int getIndiceDesgaste() {
        return indiceDesgaste;
    }
}'''

    def con_columna(T, N, defecto, validacion, lectura, costo=None, constante=None):
        """El VehiculoRuta del preenunciado con una columna nueva: atributo, el constructor viejo que delega con el valor
        del formato viejo, uno nuevo que la valida, desdeCampos con 5 o 6 campos y el getter."""
        G = 'get' + N[0].upper() + N[1:]
        s = cambiar(R,
                    ('    private final int indiceDesgaste;\n', f'    private final int indiceDesgaste;\n    private final {T} {N};\n'),
                    (CABEZA_CTOR, CABEZA_CTOR.replace('        this.patente = validarTexto(patente, "La patente no puede estar vacía");',
                                                      f'        this(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste, {defecto});\n    }}\n\n')
                     + CABEZA_CTOR.replace('            int indiceDesgaste) {', f'            int indiceDesgaste,\n            {T} {N}) {{')),
                    ('        this.velocidadPromedio = velocidadPromedio;\n', validacion + '        this.velocidadPromedio = velocidadPromedio;\n'),
                    ('        this.indiceDesgaste = indiceDesgaste;\n    }', f'        this.indiceDesgaste = indiceDesgaste;\n        this.{N} = {N};\n    }}'),
                    (ANCHO5, ANCHO56),
                    (RETORNO, RETORNO.replace('\n\n        return', '\n' + lectura + '\n        return').replace('indiceDesgaste);', f'indiceDesgaste, {N});')),
                    (ULTIMO_GETTER, ULTIMO_GETTER[:-1] + f'\n    public {T} {G}() {{\n        return {N};\n    }}\n}}'))
        if costo:
            s = cambiar(s, ('        return 2000 * indiceDesgaste / 100;', costo))
        if constante:
            s = cambiar(s, ('package ar.edu.backend;\n\n', 'package ar.edu.backend;\n\nimport java.util.Set;\n\n'),
                        ('public final class VehiculoRuta {\n', 'public final class VehiculoRuta {\n' + constante + '\n'))
        return s

    TIPO = con_columna('String', 'tipoCarga', '"GENERAL"',
                       '''        if (!"GENERAL".equals(tipoCarga) && !"REFRIGERADA".equals(tipoCarga)) {
            throw new IllegalArgumentException("Tipo de carga inválido: " + tipoCarga);
        }
''', '        String tipoCarga = campos.length == 6 ? limpiar(campos[5]) : "GENERAL";')
    FACT = con_columna('int', 'facturacion', '2000',
                       '''        if (facturacion < 2000 || facturacion >= 3800) {
            throw new IllegalArgumentException("La facturación debe ser de 2000 a menos de 3800");
        }
''', '        int facturacion = campos.length == 6 ? convertirEntero(campos[5], "facturación") : 2000;',
                       costo='        return facturacion * indiceDesgaste / 100;')
    DIAS = con_columna('int', 'diasCobertura', '0',
                       '''        if (!PLAZOS.contains(diasCobertura)) {
            throw new IllegalArgumentException("Plazo de cobertura inválido: " + diasCobertura);
        }
''', '        int diasCobertura = campos.length == 6 ? convertirEntero(campos[5], "días de cobertura") : 0;',
                       constante='    private static final Set<Integer> PLAZOS = Set.of(0, 30, 90, 180);\n')
    PEAJES = con_columna('int', 'peajes', '0',
                         '''        if (peajes < 0 || peajes > 10) {
            throw new IllegalArgumentException("Los peajes deben estar entre 0 y 10");
        }
''', '''        int peajes = 0;
        if (campos.length == 6 && !limpiar(campos[5]).isEmpty()) {
            peajes = convertirEntero(campos[5], "peajes");
            if (peajes < 1 || peajes > 10) {
                throw new IllegalArgumentException("Con valor, los peajes van de 1 a 10");
            }
        }''', costo='        return 2000 * indiceDesgaste / 100 + 50 * peajes;')
    TALLER = cambiar(R, ('package ar.edu.backend;\n\n', 'package ar.edu.backend;\n\nimport java.util.Set;\n\n'),
                     ('public final class VehiculoRuta {\n', 'public final class VehiculoRuta {\n    private static final Set<String> ESTADOS_VALIDOS = Set.of("EN_RUTA", "DEMORADO", "EN_TALLER");\n\n'),
                     ('if (!"EN_RUTA".equals(estado) && !"DEMORADO".equals(estado)) {', 'if (!ESTADOS_VALIDOS.contains(estado)) {'))
    CARGA = cambiar(R, ('''        if (cargaToneladas > 45) {
            throw new IllegalArgumentException("La carga no puede superar las 45 toneladas");''', '''        if (cargaToneladas < 0 || cargaToneladas > 45) {
            throw new IllegalArgumentException("La carga debe estar entre 0 y 45 toneladas");'''))

    V = 'VehiculoRuta.java'
    DELEGA = ('`this(...)` tiene que ser la **primera** línea del constructor viejo: no se puede validar nada antes.',)
    return [
        codigo('r2.7', '`tipoCarga` en `VehiculoRuta` (texto con valores fijos)', '`VehiculoRuta`: atributo, constructores, `desdeCampos` y el getter',
               'Agregá a `VehiculoRuta` el dato `tipoCarga` (texto): atributo `final` y getter. Solo admite **exactamente** GENERAL o REFRIGERADA, después de quitar espacios; '
               'otro valor, minúsculas o vacío → `IllegalArgumentException`. El constructor de siempre lo usan los tests: que **delegue** con `this(..., "GENERAL")`, porque en el formato viejo todos son GENERAL. '
               '`desdeCampos` acepta 5 o 6 campos y lee `campos[5]` solo si existe. El costo **no cambia** (el recargo de REFRIGERADA es la parte 3, con una subclase).',
               [arch(V, R, TIPO)],
               [ch(r'private\s+final\s+String\s+tipoCarga', 'El atributo', 'Falta `private final String tipoCarga;`', V),
                ch(r'String\s+getTipoCarga\s*\(\s*\)', 'El getter', 'Falta `public String getTipoCarga()`', V),
                ch(r'this\s*\([^;]*"GENERAL"\s*\)\s*;', 'El constructor viejo delega', 'El constructor viejo tiene que delegar: `this(..., "GENERAL");`', V),
                ch(r'"REFRIGERADA"', 'Valida los valores', 'Validá que sea GENERAL o REFRIGERADA', V),
                ch(r'campos\.length\s*==\s*6', 'Lee la columna solo si existe', 'Leé `campos[5]` solo si hay 6 campos', V)],
               ['`private final String tipoCarga;` y `getTipoCarga()`.',
                'Un constructor nuevo con `String tipoCarga` al final, que lo valida: `if (!"GENERAL".equals(tipoCarga) && !"REFRIGERADA".equals(tipoCarga)) throw …`.',
                'El viejo: `this(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste, "GENERAL");`',
                '`desdeCampos`: aceptá 5 o 6 y `String tipoCarga = campos.length == 6 ? limpiar(campos[5]) : "GENERAL";`, y pasáselo al constructor nuevo.'],
               ['Compará con `"GENERAL".equals(tipoCarga)` (el texto primero): así un `null` no rompe.', '`limpiar` ya hace el `trim()`: « GENERAL » queda GENERAL.', *DELEGA,
                'Con `import java.util.Set` también vale `Set.of("GENERAL", "REFRIGERADA").contains(tipoCarga)`.'],
               tabla(H5 + ',tipoCarga', ['trk-1,NORTE,60,10,EN_RUTA,REFRIGERADA', 'trk-2,NORTE,60,10,EN_RUTA, GENERAL ', 'trk-3,SUR,60,10,EN_RUTA,general', 'trk-4,SUR,60,10,EN_RUTA,'], ['tipoCarga']),
               'trk-1 → REFRIGERADA, cuesta **800** (todavía sin recargo) · trk-2 → GENERAL (con espacios vale) · trk-3 (`general`, en minúsculas) y trk-4 (vacío) → **excepción**.',
               datos='60 km/h y 10 t (índice 40): cuesta **800** con cualquier tipo · el formato viejo → GENERAL · REFRIGERADO, general o vacío → excepción.',
               prueba='''        VehiculoRuta x = v("trk-1", "NORTE", "60", "10", "EN_RUTA", "REFRIGERADA");
        igual("REFRIGERADA", x.getTipoCarga(), "el tipo"); igual(800, x.getCostoDesgasteOperativo(), "el costo no cambia");
        igual("GENERAL", v("trk-1", "NORTE", "60", "10", "EN_RUTA", " GENERAL ").getTipoCarga(), "con espacios");
        igual("GENERAL", v("trk-1", "NORTE", "60", "10", "EN_RUTA").getTipoCarga(), "formato viejo: GENERAL");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "REFRIGERADO"), "desconocido");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "general"), "en minúsculas");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", ""), "vacío");
        lanza(() -> v("trk-1", "NORTE", "60", "10"), "4 campos");
        igual("GENERAL", new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40).getTipoCarga(), "el constructor viejo delega con GENERAL");
        lanza(() -> new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, "OTRA"), "el constructor nuevo valida");
'''),
        codigo('r2.8', '`facturacion` en `VehiculoRuta` (rango, y reemplaza a los 2000)', '`VehiculoRuta`: atributo, constructores, `desdeCampos` y el costo',
               'El cambio del Parcial 3K1, todo en `VehiculoRuta` (sin subclase; en la parte 3 está con un gancho). Agregá el dato `facturacion` (entero): atributo `final` y getter. '
               'Admite valores **mayores o iguales a 2000 pero menores a 3800**; fuera de ese rango → `IllegalArgumentException`. En el formato viejo, **2000**: el constructor de siempre delega con `this(..., 2000)`. '
               '`desdeCampos` acepta 5 o 6 campos. Y el costo **toma el valor ingresado**: `facturacion × índice / 100`.',
               [arch(V, R, FACT)],
               [ch(r'private\s+final\s+int\s+facturacion', 'El atributo', 'Falta `private final int facturacion;`', V),
                ch(r'int\s+getFacturacion\s*\(\s*\)', 'El getter', 'Falta `public int getFacturacion()`', V),
                ch(r'this\s*\([^;]*,\s*2_?000\s*\)\s*;', 'El constructor viejo delega', 'El constructor viejo tiene que delegar: `this(..., 2000);`', V),
                ch(r'3_?800', 'Valida el rango', 'Validá que sea de 2000 a menos de 3800', V),
                ch(r'facturacion\s*\*\s*indiceDesgaste\s*/\s*100', 'El costo con la facturación', 'El costo es `facturacion * indiceDesgaste / 100`', V)],
               ['`private final int facturacion;` y `getFacturacion()`.', 'Constructor nuevo con `int facturacion`: `if (facturacion < 2000 || facturacion >= 3800) throw …`.',
                'El viejo: `this(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste, 2000);`',
                '`desdeCampos`: `int facturacion = campos.length == 6 ? convertirEntero(campos[5], "facturación") : 2000;`',
                '`getCostoDesgasteOperativo()`: `return facturacion * indiceDesgaste / 100;` (multiplicá primero: es división entera).'],
               ['«mayores iguales a 2000 pero menores a 3800»: 2000 vale, 3800 no.', *DELEGA, 'Con 2000 en el formato viejo, el costo de las filas viejas no cambia: los tests siguen pasando.'],
               tabla(H5 + ',facturacion', ['trk-1,NORTE,60,10,EN_RUTA,3000', 'trk-2,NORTE,60,10,EN_RUTA,2000', 'trk-3,SUR,60,10,EN_RUTA,3799', 'trk-4,SUR,60,10,EN_RUTA,3800', 'trk-5,SUR,60,10,EN_RUTA,1999'], ['facturacion']),
               'Índice 40: trk-1 → **1200** · trk-2 → **800** · trk-3 → **1519** (3799 × 40 / 100 = 1519,6 → 1519) · trk-4 (3800) y trk-5 (1999) → **excepción**.',
               datos='Índice 40 y facturación 3000 → **1200** · el formato viejo → 2000, **800** · 3800 o 1999 → excepción. Con índice 65 y 3000 → **1950** (el ejemplo del enunciado).',
               prueba='''        VehiculoRuta x = v("trk-1", "NORTE", "60", "10", "EN_RUTA", "3000");
        igual(3000, x.getFacturacion(), "la facturación"); igual(1200, x.getCostoDesgasteOperativo(), "3000 × 40 / 100");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "2000").getCostoDesgasteOperativo(), "2000 vale");
        igual(1519, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "3799").getCostoDesgasteOperativo(), "división entera");
        igual(1950, v("trk-1", "NORTE", "101", "11", "EN_RUTA", "3000").getCostoDesgasteOperativo(), "el ejemplo: índice 65");
        VehiculoRuta viejo = v("trk-1", "NORTE", "60", "10", "EN_RUTA");
        igual(2000, viejo.getFacturacion(), "formato viejo: 2000"); igual(800, viejo.getCostoDesgasteOperativo(), "formato viejo: el costo de siempre");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "3800"), "3800 no");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "1999"), "menos de 2000");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "mucho"), "no es entero");
        igual(2000, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40).getFacturacion(), "el constructor viejo delega con 2000");
        igual(1000, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, 2500).getCostoDesgasteOperativo(), "el constructor nuevo");
'''),
        codigo('r2.9', 'estado nuevo válido: EN_TALLER', '`VehiculoRuta`: la validación del estado',
               'Se incorpora el estado **EN_TALLER**: es válido y se procesa como los demás (con el mismo costo). Cambiá la validación del estado en el constructor para que acepte EN_RUTA, DEMORADO y EN_TALLER, '
               'con una constante `private static final Set<String> ESTADOS_VALIDOS = Set.of(...)`. El mensaje de error queda igual y se sigue distinguiendo mayúsculas. EN_DEPOSITO se sigue descartando en el parser: no lo agregues acá.',
               [arch(V, R, TALLER)],
               [ch(r'import\s+java\.util\.Set\s*;', 'Importa Set', 'Falta `import java.util.Set;`', V),
                ch(r'Set\.of\s*\([^)]*"EN_TALLER"', 'El estado nuevo, en el Set', 'Poné EN_TALLER en el `Set.of(...)`', V),
                ch(r'\.contains\s*\(\s*estado\s*\)', 'Valida con el Set', 'Validá con `ESTADOS_VALIDOS.contains(estado)`', V),
                ch(r'"EN_DEPOSITO"', 'EN_DEPOSITO no va acá', 'EN_DEPOSITO no es válido: se descarta en el parser antes de llegar acá', V, 'noContiene')],
               ['Arriba: `import java.util.Set;`', 'En la clase: `private static final Set<String> ESTADOS_VALIDOS = Set.of("EN_RUTA", "DEMORADO", "EN_TALLER");`',
                'En el constructor: `if (!ESTADOS_VALIDOS.contains(estado)) { throw new IllegalArgumentException("Estado de vehículo inválido: " + estado); }`'],
               ['Sin el Set también vale sumar `&& !"EN_TALLER".equals(estado)` al if; con muchos estados, el Set se lee mejor.', 'Un estado que se **descarta** (MANTENIMIENTO) va en el parser; uno **válido** va acá.',
                '`Set.of` no admite repetidos: si ponés dos veces el mismo, tira una excepción al cargar la clase.'],
               tabla(H5, ['trk-1,NORTE,60,10,EN_TALLER', 'trk-2,SUR,60,10,DEMORADO', 'trk-3,SUR,60,10,en_taller', 'trk-4,SUR,999,x,EN_DEPOSITO']),
               'trk-1 → **procesada** (EN_TALLER, 800) · trk-2 → procesada · trk-3 → **inválida** (minúsculas) · trk-4 → **descartada** (EN_DEPOSITO, sin validar).',
               datos='EN_TALLER con 60 km/h y 10 t → procesado, **800** · en_taller → inválido · EN_DEPOSITO → se sigue descartando.',
               prueba='''        igual("EN_TALLER", v("trk-1", "NORTE", "60", "10", "EN_TALLER").getEstado(), "EN_TALLER es válido");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_TALLER").getCostoDesgasteOperativo(), "el mismo costo");
        anda(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA"), "EN_RUTA sigue");
        anda(() -> v("trk-1", "NORTE", "60", "10", "DEMORADO"), "DEMORADO sigue");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "en_taller"), "en minúsculas");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "PERDIDO"), "desconocido");
        ResultadoParseo r = leer("''' + H5 + '''", "trk-1,NORTE,60,10,EN_TALLER", "trk-2,SUR,999,x,EN_DEPOSITO");
        igual(1, r.getFilasProcesadas(), "procesada"); igual(1, r.getFilasDescartadas(), "EN_DEPOSITO se sigue descartando");
'''),
        codigo('r2.10', 'validación nueva: la carga no puede ser negativa', '`VehiculoRuta`: la validación de la carga',
               'Hoy el preenunciado acepta cargas negativas (solo controla que no pase de 45). Nueva regla: la carga tiene que ser un entero **entre 0 y 45, inclusive**; una carga negativa hace inválida la fila. '
               'Cambiá la validación del constructor con el mensaje «La carga debe estar entre 0 y 45 toneladas». Los tests del preenunciado tienen que seguir pasando: fijate por qué las cargas de −5 del `datos.csv` no molestan.',
               [arch(V, R, CARGA)],
               [ch(r'cargaToneladas\s*<\s*0', 'Valida el mínimo', 'Falta rechazar la carga negativa: `cargaToneladas < 0`', V),
                ch(r'cargaToneladas\s*>\s*45', 'Sigue validando el máximo', 'No borres el tope de 45', V),
                ch(r'cargaToneladas\s*<=\s*0', 'Cero vale', 'Ojo: 0 toneladas es válido («entre 0 y 45, inclusive»): la condición es `< 0`', V, 'noContiene')],
               ['Cambiá `if (cargaToneladas > 45)` por `if (cargaToneladas < 0 || cargaToneladas > 45)`.', 'Y el mensaje: «La carga debe estar entre 0 y 45 toneladas».'],
               ['Las cargas de −5 del `datos.csv` están en filas EN_DEPOSITO: se descartan **antes** de validar, así que el resultado (32 / 20 / 8) no cambia.',
                'Con 0 toneladas y 60 km/h el índice es 36: vale y cuesta 720.'],
               tabla(H5, ['trk-1,NORTE,60,0,EN_RUTA', 'trk-2,NORTE,60,-1,EN_RUTA', 'trk-3,SUR,60,45,DEMORADO', 'trk-4,SUR,999,-5,EN_DEPOSITO']),
               'trk-1 → procesada (**720**) · trk-2 → **inválida** (−1) · trk-3 → procesada (el tope es inclusive) · trk-4 → **descartada**: la carga negativa no se llega a validar.',
               datos='0 t → vale (**720** con 60 km/h) · −1 t → inválida · 45 t → vale · 46 t → inválida · EN_DEPOSITO con −5 → se descarta igual.',
               prueba='''        igual(720, v("trk-1", "NORTE", "60", "0", "EN_RUTA").getCostoDesgasteOperativo(), "0 t vale");
        lanza(() -> v("trk-1", "NORTE", "60", "-1", "EN_RUTA"), "carga negativa");
        anda(() -> v("trk-1", "NORTE", "60", "45", "EN_RUTA"), "45 t vale");
        lanza(() -> v("trk-1", "NORTE", "60", "46", "EN_RUTA"), "más de 45");
        lanza(() -> new VehiculoRuta("trk-1", "NORTE", 10, -5, "EN_RUTA", 4), "el constructor valida");
        ResultadoParseo r = leer("''' + H5 + '''", "trk-4,SUR,999,-5,EN_DEPOSITO", "trk-5,SUR,10,-5,EN_RUTA");
        igual(1, r.getFilasDescartadas(), "EN_DEPOSITO no se valida"); igual(1, r.getFilasInvalidas(), "la negativa es inválida");
'''),
        codigo('r2.11', '`diasCobertura` en `VehiculoRuta` (valores permitidos: 0, 30, 90 o 180)', '`VehiculoRuta`: atributo, constructores, `desdeCampos` y el getter',
               'Como el Simulacro 4: agregá el dato `diasCobertura` (entero): atributo `final` y getter. Solo admite **0, 30, 90 o 180** (0 = sin seguro); cualquier otro valor, vacío o no numérico → `IllegalArgumentException`. '
               'Validalo con una constante `Set<Integer> PLAZOS = Set.of(0, 30, 90, 180)`. En el formato viejo, **0** (sin seguro): el constructor de siempre delega con `this(..., 0)`. '
               '`desdeCampos` acepta 5 o 6 campos. El costo **no cambia** acá (la prima de los asegurados es una subclase, parte 3).',
               [arch(V, R, DIAS)],
               [ch(r'private\s+final\s+int\s+diasCobertura', 'El atributo', 'Falta `private final int diasCobertura;`', V),
                ch(r'int\s+getDiasCobertura\s*\(\s*\)', 'El getter', 'Falta `public int getDiasCobertura()`', V),
                ch(r'Set\.of\s*\(\s*0\s*,\s*30\s*,\s*90\s*,\s*180\s*\)', 'Los plazos permitidos', 'Los plazos: `Set.of(0, 30, 90, 180)`', V),
                ch(r'import\s+java\.util\.Set\s*;', 'Importa Set', 'Falta `import java.util.Set;`', V),
                ch(r'this\s*\([^;]*,\s*0\s*\)\s*;', 'El constructor viejo delega', 'El constructor viejo tiene que delegar: `this(..., 0);`', V)],
               ['`import java.util.Set;` y `private static final Set<Integer> PLAZOS = Set.of(0, 30, 90, 180);`', '`private final int diasCobertura;` y `getDiasCobertura()`.',
                'Constructor nuevo con `int diasCobertura`: `if (!PLAZOS.contains(diasCobertura)) throw …`.', 'El viejo: `this(..., indiceDesgaste, 0);`',
                '`desdeCampos`: `int diasCobertura = campos.length == 6 ? convertirEntero(campos[5], "días de cobertura") : 0;`'],
               ['`Set<Integer>` (con mayúscula): los genéricos no aceptan `int`; el `contains(diasCobertura)` hace el autoboxing solo.',
                'Un rango («entre 0 y 180») no sirve: 45 estaría adentro y no es un plazo válido.', *DELEGA],
               tabla(H5 + ',diasCobertura', ['trk-1,NORTE,60,10,EN_RUTA,90', 'trk-2,NORTE,60,10,EN_RUTA,0', 'trk-3,SUR,60,10,EN_RUTA,45', 'trk-4,SUR,60,10,EN_RUTA,'], ['diasCobertura']),
               'trk-1 → 90 días · trk-2 → 0 (sin seguro) · trk-3 (45, no es un plazo) y trk-4 (vacío) → **excepción**. Todos cuestan **800** acá: la prima va en la parte 3.',
               datos='90 → vale · 0 → vale (sin seguro) · 45, −30, vacío o `x` → excepción · el formato viejo → 0 días.',
               prueba='''        igual(90, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "90").getDiasCobertura(), "90 días");
        igual(0, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "0").getDiasCobertura(), "0 vale");
        igual(180, v("trk-1", "NORTE", "60", "10", "EN_RUTA", " 180 ").getDiasCobertura(), "con espacios");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "30").getCostoDesgasteOperativo(), "el costo no cambia");
        igual(0, v("trk-1", "NORTE", "60", "10", "EN_RUTA").getDiasCobertura(), "formato viejo: 0");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "45"), "45 no es un plazo");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "-30"), "negativo");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", ""), "vacío");
        igual(0, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40).getDiasCobertura(), "el constructor viejo delega con 0");
        lanza(() -> new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, 60), "el constructor nuevo valida");
'''),
        codigo('r2.12', '`peajes` en `VehiculoRuta` (opcional: vacío = 0) y el costo', '`VehiculoRuta`: atributo, constructores, `desdeCampos` y el costo',
               'Como el Simulacro 3 («indicado por la presencia de un valor»): agregá el dato `peajes` (entero): atributo `final` y getter. Si el sexto campo **tiene valor**, es un entero de **1 a 10**; '
               'si viene **vacío**, o la fila es del formato viejo, son **0** peajes. El constructor de siempre delega con `this(..., 0)` y el nuevo valida de 0 a 10. '
               'El costo de todos suma **50 USD por cada peaje**: `2000 × índice / 100 + 50 × peajes`.',
               [arch(V, R, PEAJES)],
               [ch(r'private\s+final\s+int\s+peajes', 'El atributo', 'Falta `private final int peajes;`', V),
                ch(r'int\s+getPeajes\s*\(\s*\)', 'El getter', 'Falta `public int getPeajes()`', V),
                ch(r'isEmpty\s*\(\s*\)|isBlank\s*\(\s*\)|equals\s*\(\s*""\s*\)', 'Mira si el campo viene vacío', 'Si `campos[5]` viene vacío son 0 peajes: preguntá con `isEmpty()`', V),
                ch(r'50\s*\*\s*peajes|peajes\s*\*\s*50', 'El costo con los peajes', 'El costo suma `50 * peajes`', V),
                ch(r'this\s*\([^;]*,\s*0\s*\)\s*;', 'El constructor viejo delega', 'El constructor viejo tiene que delegar: `this(..., 0);`', V)],
               ['`private final int peajes;`, `getPeajes()` y el constructor viejo con `this(..., 0);`.', 'Constructor nuevo: `if (peajes < 0 || peajes > 10) throw …` (0 vale: es el «sin valor»).',
                '`desdeCampos`: `int peajes = 0;` y solo si `campos.length == 6 && !limpiar(campos[5]).isEmpty()` lo convertís y validás de 1 a 10.',
                'El costo: `return 2000 * indiceDesgaste / 100 + 50 * peajes;`'],
               ['Un 0 **escrito** en el CSV es un valor: tiene que ser de 1 a 10, así que es inválido. Solo el vacío cuenta como 0.',
                'Por eso el «de 1 a 10» va en `desdeCampos` (donde sabés si vino escrito) y el constructor acepta de 0 a 10.', '`limpiar(campos[5]).isEmpty()`: con espacios también cuenta como vacío.'],
               tabla(H5 + ',peajes', ['trk-1,NORTE,60,10,EN_RUTA,3', 'trk-2,NORTE,60,10,EN_RUTA,', 'trk-3,SUR,60,10,EN_RUTA,0', 'trk-4,SUR,60,10,EN_RUTA,11'], ['peajes']),
               'Índice 40: trk-1 → 3 peajes, **950** · trk-2 → vacío = 0, **800** · trk-3 (un 0 escrito) y trk-4 (11) → **excepción**.',
               datos='3 peajes → 800 + 150 = **950** · vacío → **800** · 10 → **1300** · 0 escrito, 11 o `x` → excepción · el formato viejo → 0 peajes.',
               prueba='''        VehiculoRuta x = v("trk-1", "NORTE", "60", "10", "EN_RUTA", "3");
        igual(3, x.getPeajes(), "3 peajes"); igual(950, x.getCostoDesgasteOperativo(), "800 + 150");
        igual(0, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "").getPeajes(), "vacío = 0");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "  ").getCostoDesgasteOperativo(), "con espacios también");
        igual(1300, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "10").getCostoDesgasteOperativo(), "10 vale");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_RUTA").getCostoDesgasteOperativo(), "formato viejo");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "0"), "un 0 escrito");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "11"), "más de 10");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "x"), "no es entero");
        igual(0, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40).getPeajes(), "el constructor viejo delega con 0");
        lanza(() -> new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, 11), "el constructor nuevo valida");
'''),
    ]
