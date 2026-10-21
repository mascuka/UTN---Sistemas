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
        JuegoMesa c = new JuegoMesa("J1", "Catan", 1995, 7.2, 2.3);
        cerca(16.56, c.getPuntuacionAjustada(), "ajustada");
        JuegoMesa otro = new JuegoMesa(new String("J1"), "Otro nombre", 2000, 5, 1);
        igual(true, c.equals(otro), "mismo id"); igual(c.hashCode(), otro.hashCode(), "hashCode con el mismo id");
        igual(false, c.equals(new JuegoMesa("J2", "Catan", 1995, 7.2, 2.3)), "otro id");
        igual(false, c.equals(null), "con null"); igual(false, c.equals("J1"), "con otra clase");
        igual(String.format("%s (%d) - Rating: %.2f, Peso: %.2f, Ajustada: %.2f", "Catan", 1995, 7.2, 2.3, 7.2 * 2.3), c.toString(), "toString");
        igual(1, new java.util.HashSet<>(java.util.List.of(c, otro)).size(), "en un HashSet");
        System.out.println("OK");
    }
}
