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
    public static void main(String[] a) throws Exception {
        ResultadoParseo r = new ParserEnvios().leer(csv("id,zona,brutoGramos,embalajeGramos,estado,modalidad", "A,Norte,1200,200,LISTO,NORMAL", "B,Norte,1200,200,LISTO", "C,Sur,0,0,CANCELADO,URGENTE", "D,Sur,1000,0,LISTO,NORMAL,extra"));
        igual(4, r.getLeidas(), "leídas"); igual(1, r.getProcesadas(), "procesadas");
        igual(1, r.getDescartadas(), "descartadas (CANCELADO, sin validar)"); igual(2, r.getInvalidas(), "inválidas (5 y 7 campos)");
        ResultadoParseo v = new ParserEnvios().leer(csv("id,zona,brutoGramos,embalajeGramos,estado", "A,Norte,1200,200,LISTO", "B,Norte,1200,200,LISTO,NORMAL"));
        igual(1, v.getProcesadas(), "el formato viejo sigue andando"); igual(1, v.getInvalidas(), "6 campos bajo la cabecera de 5");
        try { new ParserEnvios().leer(csv("id,zona,peso", "A,N,1")); throw new AssertionError("una cabecera desconocida tenía que tirar IllegalArgumentException"); } catch (IllegalArgumentException e) { }
        System.out.println("OK");
    }
}
