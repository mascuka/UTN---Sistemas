package utnfc.backend.parcial;

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
        lanza(() -> new Consumo("", "A", 100, 0), "id vacío");
        lanza(() -> new Consumo("C", null, 100, 0), "rubro null");
        lanza(() -> new Consumo("C", "A", 0, 0), "importe 0");
        lanza(() -> new Consumo("C", "A", 5_000_001, 3_000_000), "importe 5.000.001");
        lanza(() -> new Consumo("C", "A", 100, -1), "bonificación negativa");
        lanza(() -> new Consumo("C", "A", 100, 100), "bonificación igual al importe");
        lanza(() -> new Consumo("C", "A", 4_000_000, 500_000), "neto 3.500.000");
        anda(() -> new Consumo("C", "A", 5_000_000, 2_000_000), "neto justo 3.000.000");
        Consumo c = new Consumo(" C1 ", " Viajes ", 100, 0);
        igual("C1", c.getId(), "id con strip"); igual("Viajes", c.getRubro(), "rubro con strip");
        System.out.println("OK");
    }
}
