package ar.edu.backend;

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
        ResultadoParseo r = new ParserServidores().leer(csv("id,region,porcentajeCPU,usoMemoria,estado",
                "srv-1,SA-EAST-1,63,9,ALERTA", "srv-2,US-WEST-2,20,19,ESTABLE", "srv-4,US-EAST-1,90,200,ALERTA",
                "srv-5,US-EAST-1,40,30,APAGADO", "srv-7,SA-EAST-1,40,30", "srv-3, US-WEST-2 ,50,58,CRITICO", "srv-11,SA-EAST-1,30,40,ALERTA,"));
        igual(7, r.getLeidas(), "leídas"); igual(2, r.getProcesadas(), "procesadas");
        igual(1, r.getDescartadas(), "descartadas"); igual(4, r.getInvalidas(), "inválidas");
        igual("Linea 3: ESTABLE", r.getDescartes().get(0), "el descarte");
        igual(true, r.getErrores().get(0).startsWith("Linea 4: "), "el primer error es la línea 4: " + r.getErrores());
        igual(true, r.getErrores().get(3).startsWith("Linea 8: "), "el último error es la línea 8: " + r.getErrores());
        igual("US-WEST-2", r.getServidores().get(1).getRegion(), "región sin espacios");
        try { new ParserServidores().leer(csv("id,region,cpu", "x")); throw new AssertionError("cabecera incorrecta"); }
        catch (IllegalArgumentException e) { }
        System.out.println("OK");
    }
}
