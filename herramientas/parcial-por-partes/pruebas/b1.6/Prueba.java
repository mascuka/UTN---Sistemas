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
        igual(700, new Envio("E", "N", 1000).costo(), "1000 g");
        igual(900, new Envio("E", "N", 1001).costo(), "1001 g");
        igual(700, new Envio("E", "N", 1).costo(), "1 g");
        igual(900, new Envio("E", "N", 2000).costo(), "2000 g");
        igual(6500, new Envio("E", "N", 30000).costo(), "30000 g");
        Envio e = new Envio("E01", "Norte", 1000);
        igual("E01", e.getId(), "getId"); igual("Norte", e.getZona(), "getZona"); igual(1000, e.getGramos(), "getGramos");
        System.out.println("OK");
    }
}
