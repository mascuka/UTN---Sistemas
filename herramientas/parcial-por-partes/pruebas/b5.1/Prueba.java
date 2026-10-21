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
        java.util.List<Servidor> xs = new java.util.ArrayList<>(java.util.List.of(new Servidor("a", "SA", 50), new Servidor("b", "US", 30), new Servidor("c", "SA", 60)));
        Cloud c = new Cloud(xs);
        xs.clear();
        igual(1400, c.total(), "total (500 + 300 + 600), aunque afuera vacíen la lista");
        igual(1, c.filtrar(s -> s.getIndiceCarga() < 50).size(), "índice menor a 50");
        igual(java.util.List.of("a", "c"), c.filtrar(s -> s.getRegion().equals("SA")).stream().map(Servidor::getId).toList(), "los de SA");
        igual(0, new Cloud(java.util.List.of()).total(), "total sin servidores");
        System.out.println("OK");
    }
}
