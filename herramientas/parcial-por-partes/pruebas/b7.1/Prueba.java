package ar.edu.backend;

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
        java.nio.file.Path p = csv("id,region,porcentajeCPU,usoMemoria,estado", "srv-1,SA-EAST-1,63,9,ALERTA", "srv-2,US-WEST-2,20,19,ESTABLE", "srv-3,US-EAST-1,90,200,ALERTA");
        String s = salida(() -> { try { App.main(new String[] { p.toString() }); } catch (Exception e) { throw new RuntimeException(e); } });
        contiene(s, "Leídas: 3 | procesadas: 1 | descartadas: 1 | inválidas: 1 | objetos: 1");
        contiene(s, "Linea 3: ESTABLE"); contiene(s, "Linea 4: "); contiene(s, "Total: 460");
        igual(true, s.indexOf("Leídas") < s.indexOf("Linea 3") && s.indexOf("Linea 4") < s.indexOf("Total"), "el orden de la salida:\n" + s);
        System.out.println("OK");
    }
}
