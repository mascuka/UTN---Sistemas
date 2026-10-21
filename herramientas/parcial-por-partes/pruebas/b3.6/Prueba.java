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
    static Envio d(String bruto, String embalaje) { return Envio.desdeCampos(new String[] {"E01", "Norte", bruto, embalaje, "LISTO"}); }
    public static void main(String[] a) {
        Envio e = d("1200", "200");
        igual(1000, e.getGramos(), "neto"); igual(700, e.costo(), "costo"); igual("Norte", e.getZona(), "zona");
        igual(30000, d("50000", "20000").getGramos(), "bruto 50000 y neto 30000");
        igual(1, d("1", "0").getGramos(), "bruto 1 sin embalaje");
        lanza(() -> Envio.desdeCampos(new String[] {"E01", "Norte", "1200", "200"}), "4 campos");
        lanza(() -> d("100", "100"), "embalaje igual al bruto");
        lanza(() -> d("1200", "-1"), "embalaje negativo");
        lanza(() -> d("0", "0"), "bruto 0");
        lanza(() -> d("50001", "30000"), "bruto 50001");
        lanza(() -> d("mil", "100"), "bruto que no es un número");
        lanza(() -> d("50000", "19999"), "neto 30001: lo frena el constructor");
        System.out.println("OK");
    }
}
