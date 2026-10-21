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
    static JuegoMesa j(String id, int min, int max, double rating, double peso) {
        return new JuegoMesa(id, "Juego " + id, 2000, min, max, 60, rating, peso, "Estrategia");
    }
    public static void main(String[] a) {
        ServicioJuegos s = new ServicioJuegos(java.util.List.of(j("J1", 2, 4, 8, 2.5), j("J2", 1, 2, 6, 3.9), j("J3", 3, 6, 7, 1.2)));
        cerca(7.0, s.calcularPromedioRating(), "promedio");
        igual("J2", s.obtenerMasComplejo().get().getId(), "más complejo");
        igual(java.util.List.of("J1", "J2"), s.filtrarPorJugadores(2).stream().map(JuegoMesa::getId).toList(), "para 2 jugadores");
        igual(java.util.List.of("J3"), s.filtrarPorJugadores(6).stream().map(JuegoMesa::getId).toList(), "para 6 (borde)");
        cerca(0.0, new ServicioJuegos(java.util.List.of()).calcularPromedioRating(), "promedio sin juegos");
        System.out.println("OK");
    }
}
