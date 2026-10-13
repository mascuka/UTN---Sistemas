import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collection;
import java.util.Map;
import java.util.Objects;

/**
 * Ayuda para los controles de la Práctica por partes (Java). No lo escribe el alumno: se compila junto con
 * su código y Controles.java, que llama a control(k, () -> { ... }) por cada control del paso.
 * Cada control imprime una línea: "@@ok k", "@@mal k mensaje" o "@@error k excepción".
 */
public final class Prueba {
    private Prueba() { }

    public interface Bloque { void correr() throws Throwable; }

    public static final class Falla extends RuntimeException {
        public Falla(String mensaje) { super(mensaje); }
    }

    private static final PrintStream SALIDA = System.out;

    public static void control(int k, Bloque b) {
        String r;
        try {
            b.correr();
            r = "@@ok " + k;
        } catch (Falla f) {
            r = "@@mal " + k + " " + plano(f.getMessage());
        } catch (Throwable t) {
            r = "@@error " + k + " " + plano(describir(t));
        }
        System.setOut(SALIDA);
        SALIDA.println(r);
    }

    public static void fin() { SALIDA.println("@@fin"); }

    private static String plano(String s) { return s == null ? "" : s.replace("\r", "").replace("\n", " ⏎ "); }

    /** Nombre corto de la excepción (en el navegador a veces la clase no trae el nombre). */
    public static String nombre(Throwable t) {
        String n = null;
        try { n = t.getClass().getSimpleName(); } catch (Throwable e) { }
        if (n != null && !n.isEmpty()) return n;
        if (t instanceof NullPointerException) return "NullPointerException";
        if (t instanceof NumberFormatException) return "NumberFormatException";
        if (t instanceof IllegalArgumentException) return "IllegalArgumentException";
        if (t instanceof IllegalStateException) return "IllegalStateException";
        if (t instanceof ArrayIndexOutOfBoundsException) return "ArrayIndexOutOfBoundsException";
        if (t instanceof IndexOutOfBoundsException) return "IndexOutOfBoundsException";
        if (t instanceof ClassCastException) return "ClassCastException";
        if (t instanceof ArithmeticException) return "ArithmeticException";
        if (t instanceof UnsupportedOperationException) return "UnsupportedOperationException";
        if (t instanceof java.io.IOException) return "IOException";
        if (t instanceof RuntimeException) return "RuntimeException";
        if (t instanceof Error) return "Error";
        return "Exception";
    }

    public static String describir(Throwable t) {
        String m = t.getMessage();
        return m == null || m.isEmpty() ? nombre(t) : nombre(t) + ": " + m;
    }

    /* ---------- Comparaciones ---------- */

    public static void verdad(boolean condicion, String mensaje) {
        if (!condicion) throw new Falla(mensaje);
    }

    public static void igual(Object esperado, Object real, String que) {
        if (!iguales(esperado, real)) throw new Falla(que + ": tenía que dar " + mostrar(esperado) + " y dio " + mostrar(real));
    }

    public static void igual(long esperado, long real, String que) {
        if (esperado != real) throw new Falla(que + ": tenía que dar " + esperado + " y dio " + real);
    }

    public static void igual(double esperado, double real, String que) {
        if (!cerca(esperado, real)) throw new Falla(que + ": tenía que dar " + esperado + " y dio " + real);
    }

    public static void igual(boolean esperado, boolean real, String que) {
        if (esperado != real) throw new Falla(que + ": tenía que dar " + esperado + " y dio " + real);
    }

    private static boolean cerca(double a, double b) {
        if (Double.isNaN(a) || Double.isNaN(b)) return Double.isNaN(a) && Double.isNaN(b);
        return Math.abs(a - b) <= 1e-6 * Math.max(1, Math.max(Math.abs(a), Math.abs(b)));
    }

    private static boolean iguales(Object a, Object b) {
        if (a instanceof Number && b instanceof Number) {
            Number x = (Number) a, y = (Number) b;
            boolean decimal = x instanceof Double || x instanceof Float || y instanceof Double || y instanceof Float;
            return decimal ? cerca(x.doubleValue(), y.doubleValue()) : x.longValue() == y.longValue();
        }
        if (a instanceof Map && b instanceof Map) {
            Map<?, ?> m = (Map<?, ?>) a, n = (Map<?, ?>) b;
            if (m.size() != n.size()) return false;
            for (Map.Entry<?, ?> e : m.entrySet()) if (!n.containsKey(e.getKey()) || !iguales(e.getValue(), n.get(e.getKey()))) return false;
            return true;
        }
        return Objects.equals(a, b);
    }

    private static String mostrar(Object o) {
        if (o == null) return "null";
        if (o instanceof String) return "\"" + o + "\"";
        if (o instanceof Collection && ((Collection<?>) o).size() > 12) return ((Collection<?>) o).size() + " elementos";
        return String.valueOf(o);
    }

    public static void lanza(Class<? extends Throwable> tipo, Bloque b, String que) {
        try {
            b.correr();
        } catch (Throwable t) {
            if (tipo.isInstance(t)) return;
            throw new Falla(que + ": tenía que tirar " + tipo.getSimpleName() + " y tiró " + describir(t));
        }
        throw new Falla(que + ": tenía que tirar " + tipo.getSimpleName() + " y no tiró nada");
    }

    public static void noLanza(Bloque b, String que) {
        try {
            b.correr();
        } catch (Throwable t) {
            throw new Falla(que + ": no tenía que tirar nada y tiró " + describir(t));
        }
    }

    /** Lo que imprime el bloque con System.out (para revisar el main o un informe). */
    public static String salida(Bloque b) throws Throwable {
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        PrintStream antes = System.out;
        System.setOut(new PrintStream(buf, true));
        try {
            b.correr();
        } finally {
            System.out.flush();
            System.setOut(antes);
        }
        return buf.toString().replace("\r", "");
    }

    public static void contiene(String texto, String parte, String que) {
        if (texto == null || !texto.contains(parte)) throw new Falla(que + ": no aparece " + mostrar(parte) + (texto == null ? "" : " en " + mostrar(recortar(texto))));
    }

    private static String recortar(String s) {
        s = s.trim();
        return s.length() > 160 ? s.substring(0, 160) + "…" : s;
    }

    /** Crea (o pisa) un archivo de texto para la prueba, como el @TempDir de los tests del parcial. */
    public static Path archivo(String ruta, String contenido) throws Exception {
        Path p = Path.of(ruta);
        if (p.getParent() != null) Files.createDirectories(p.getParent());
        Files.writeString(p, contenido);
        return p;
    }
}
