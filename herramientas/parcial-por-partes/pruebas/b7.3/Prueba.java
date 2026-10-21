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
    public static void main(String[] a) throws Exception {
        java.nio.file.Path p = csv("id;nombre;anio;min_jugadores;max_jugadores;duracion;rating;peso;categoria", "J1;Catan;1995;3;4;90;7.2;2.3;Estrategia", "J2;Dixit;2008;3;6;30;7.5;1.2;Familiar");
        String s = salida(() -> Main.main(new String[] { p.toString() }));
        contiene(s, "Panorama: 2 juegos"); contiene(s, String.format("Promedio de Rating: %.2f", 7.35)); contiene(s, "Juego más complejo: Catan (Peso: 2.3)");
        java.nio.file.Path v = csv("id;nombre;anio;min_jugadores;max_jugadores;duracion;rating;peso;categoria");
        String sv = salida(() -> Main.main(new String[] { v.toString() }));
        igual(false, sv.contains("Juego más complejo"), "sin juegos no se muestra el más complejo");
        System.out.println("OK");
    }
}
