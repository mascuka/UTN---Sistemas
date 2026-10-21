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
        java.util.List<Envio> lista = new java.util.ArrayList<>(java.util.List.of(new Envio("A", "N", 1000), new Envio("B", "N", 1001), new Envio("C", "S", 1)));
        CentralEnvios c = new CentralEnvios(lista);
        lista.clear();
        igual(2300, c.total(), "total (y la copia defensiva)");
        igual(2, c.filtrar(e -> e.getGramos() <= 1000).size(), "filtrar");
        igual(true, c.filtrar(e -> e.getZona().equals("X")).isEmpty(), "filtrar sin resultados");
        contiene(c.panorama(), "hasta 1000 g: 2");
        try { c.filtrar(e -> true).clear(); throw new AssertionError("la lista de filtrar no tenía que poder modificarse"); } catch (UnsupportedOperationException e) { }
        igual(0, new CentralEnvios(java.util.List.of()).total(), "total sin envíos");
        System.out.println("OK");
    }
}
