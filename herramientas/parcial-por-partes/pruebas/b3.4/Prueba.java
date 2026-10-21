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
    public static void main(String[] a) {
        JuegoMesa j = JuegoMesa.desdeCampos(" J2 ; Dixit ;2008;3;6;30;7.1;1.2; Familiar ".split(";", -1));
        igual("J2", j.getId(), "id"); igual("Dixit", j.getNombre(), "nombre con trim"); igual(2008, j.getAnio(), "año");
        igual(3, j.getMinJugadores(), "mínimo"); igual(6, j.getMaxJugadores(), "máximo"); igual(30, j.getDuracion(), "duración");
        cerca(7.1, j.getRating(), "rating"); cerca(1.2, j.getPeso(), "peso"); igual("Familiar", j.getCategoria(), "categoría");
        lanza(() -> JuegoMesa.desdeCampos("J1;Catan;1995;3;4;90;7.2;2.3".split(";", -1)), "8 campos");
        lanza(() -> JuegoMesa.desdeCampos("J1;Catan;mil;3;4;90;7.2;2.3;Estrategia".split(";", -1)), "año que no es número");
        System.out.println("OK");
    }
}
