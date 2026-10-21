package ar.edu.backend.envios;

public class Prueba {
    static java.nio.file.Path csv(String... lineas) throws Exception {
        java.nio.file.Path p = java.nio.file.Files.createTempFile("pp", ".csv");
        java.nio.file.Files.writeString(p, String.join("\n", lineas) + "\n");
        return p;
    }
    static void igual(Object esperado, Object real, String que) {
        if (!java.util.Objects.equals(esperado, real)) throw new AssertionError(que + ": se esperaba " + esperado + " y dio " + real);
    }
    static void cerca(double esperado, double real, String que) {
        if (Math.abs(esperado - real) > 1e-6) throw new AssertionError(que + ": se esperaba " + esperado + " y dio " + real);
    }
    static void lanza(Runnable r, String que) {
        try { r.run(); } catch (IllegalArgumentException e) { return; }
        throw new AssertionError(que + ": tenía que lanzar IllegalArgumentException");
    }
    static void anda(Runnable r, String que) {
        try { r.run(); } catch (RuntimeException e) { throw new AssertionError(que + ": no tenía que fallar y tiró " + e); }
    }
    static String salida(Runnable r) {
        java.io.PrintStream antes = System.out;
        java.io.ByteArrayOutputStream b = new java.io.ByteArrayOutputStream();
        System.setOut(new java.io.PrintStream(b, true));
        try { r.run(); } finally { System.setOut(antes); }
        return b.toString();
    }
    static void contiene(String texto, String parte) {
        if (!texto.contains(parte)) throw new AssertionError("la salida no tiene \"" + parte + "\":\n" + texto);
    }
    public static void main(String[] a) throws Exception {
        java.nio.file.Path p = csv("id,zona,brutoGramos,embalajeGramos,estado", "E01,Norte,1200,200,LISTO", "E07,Norte,0,0,CANCELADO", "E09,Centro,100,100,LISTO");
        String s = salida(() -> { try { Main.main(new String[] { p.toString() }); } catch (Exception e) { throw new RuntimeException(e); } });
        contiene(s, "Leídas: 3 | procesadas: 1 | descartadas: 1 | inválidas: 1 | objetos: 1");
        contiene(s, "Línea 3: CANCELADO"); contiene(s, "Línea 4: "); contiene(s, "Total: 700");
        igual(true, s.indexOf("Leídas") < s.indexOf("Línea 3") && s.indexOf("Línea 4") < s.indexOf("Total"), "el orden de la salida:\n" + s);
        System.out.println("OK");
    }
}
