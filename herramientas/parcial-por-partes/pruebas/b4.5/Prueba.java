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
    public static void main(String[] a) {
        java.util.List<Servidor> xs = new java.util.ArrayList<>(java.util.List.of(new Servidor("s", "r", 10)));
        java.util.List<String> err = new java.util.ArrayList<>(java.util.List.of("Linea 3: x"));
        java.util.List<String> des = new java.util.ArrayList<>(java.util.List.of("Linea 4: ESTABLE"));
        ResultadoParseo r = new ResultadoParseo(xs, 3, 1, err, des);
        xs.add(new Servidor("t", "r", 10)); err.clear(); des.clear();
        igual(1, r.getServidores().size(), "copia de los servidores"); igual(1, r.getErrores().size(), "copia de los errores");
        igual(1, r.getDescartes().size(), "copia de los descartes");
        try { r.getServidores().clear(); throw new AssertionError("la lista de servidores se puede modificar"); }
        catch (UnsupportedOperationException e) { }
        igual(1, r.getProcesadas(), "procesadas"); igual(1, r.getInvalidas(), "inválidas");
        igual("Leídas: 3 | procesadas: 1 | descartadas: 1 | inválidas: 1 | objetos: 1", r.informe(), "informe");
        System.out.println("OK");
    }
}
