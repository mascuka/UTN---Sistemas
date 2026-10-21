package ar.edu.backend.juegos;

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
    static JuegoMesa j(String id, String nombre, int anio, int min, int max, double rating, double peso) {
        return new JuegoMesa(id, nombre, anio, min, max, 60, rating, peso, "Estrategia");
    }
    public static void main(String[] a) {
        anda(() -> j("J1", "Catan", 1995, 3, 4, 7.2, 2.3), "juego válido");
        anda(() -> j("J1", "Catan", 1900, 1, 1, 0, 1), "bordes de abajo");
        anda(() -> j("J1", "Catan", 2026, 1, 1, 10, 5), "bordes de arriba");
        lanza(() -> j(" ", "Catan", 1995, 3, 4, 7.2, 2.3), "id en blanco");
        lanza(() -> j("J1", null, 1995, 3, 4, 7.2, 2.3), "nombre null");
        lanza(() -> j("J1", "Catan", 1899, 3, 4, 7.2, 2.3), "año 1899");
        lanza(() -> j("J1", "Catan", 2027, 3, 4, 7.2, 2.3), "año 2027");
        lanza(() -> j("J1", "Catan", 1995, 0, 4, 7.2, 2.3), "mínimo 0");
        lanza(() -> j("J1", "Catan", 1995, 4, 3, 7.2, 2.3), "máximo menor al mínimo");
        lanza(() -> j("J1", "Catan", 1995, 3, 4, 10.5, 2.3), "rating 10.5");
        lanza(() -> j("J1", "Catan", 1995, 3, 4, 7.2, 0.9), "peso 0.9");
        lanza(() -> j("J1", "Catan", 1995, 3, 4, 7.2, 5.1), "peso 5.1");
        System.out.println("OK");
    }
}
