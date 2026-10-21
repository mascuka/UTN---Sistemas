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
    public static void main(String[] a) {
        CentralEnvios c = new CentralEnvios(java.util.List.of(new Envio("A", "N", 1000), new EnvioPrioritario("B", "N", 1000), new EnvioPrioritario("C", "S", 5000)));
        igual(java.util.Map.of("NORMAL", 1L, "PRIORITARIO", 2L), c.conteoPorModalidad(), "conteo por modalidad");
        igual(true, new CentralEnvios(java.util.List.of()).conteoPorModalidad().isEmpty(), "sin envíos, vacío");
        igual(3700, c.total(), "el total no cambió");
        igual("NORMAL", new Envio("A", "N", 1).getModalidad(), "modalidad de un Envio");
        igual("PRIORITARIO", new EnvioPrioritario("A", "N", 1).getModalidad(), "modalidad de un EnvioPrioritario");
        System.out.println("OK");
    }
}
