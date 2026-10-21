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
    public static void main(String[] a) throws Exception {
        ResultadoParseo r = new ParserLiquidaciones().leer(csv("id,rubro,importeCentavos,bonificacionCentavos,estado",
                "C01,Alimentos,120000,20000,APROBADO", "C02,Viajes,100000,0,ANULADO", "C03,Hogar,100000,0,PENDIENTE",
                "C04,Hogar,100000,100000,APROBADO", "C05,Hogar,100000,0", " C06 , Combustible ,170000,20000, APROBADO"));
        igual(6, r.getLeidas(), "leídas"); igual(2, r.getProcesadas(), "procesadas");
        igual(1, r.getDescartadas(), "descartadas"); igual(3, r.getInvalidas(), "inválidas");
        igual(java.util.Map.of(3, "ANULADO"), r.getDescartes(), "descartes");
        igual(java.util.List.of(4, 5, 6), java.util.List.copyOf(r.getErrores().keySet()), "líneas con error");
        igual("Combustible", r.getConsumos().get(1).getRubro(), "rubro sin espacios");
        try { new ParserLiquidaciones().leer(csv("id,rubro", "x")); throw new AssertionError("cabecera incorrecta"); }
        catch (IllegalArgumentException e) { igual("encabezado incorrecto", e.getMessage(), "mensaje"); }
        System.out.println("OK");
    }
}
