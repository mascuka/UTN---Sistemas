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
    public static void main(String[] a) {
        SolicitudCredito s = SolicitudCredito.desdeCampos(new String[] {"CL1", "PREMIUM", "10000", "2000", "APROBADO"});
        cerca(80, s.getScoreFinanciero(), "score"); cerca(56, s.getTasaInteresAnual(), "tasa");
        igual("APROBADO", s.getEstado(), "estado"); igual("PREMIUM", s.getTipoCliente(), "tipo");
        lanza(() -> SolicitudCredito.desdeCampos(new String[] {"CL1", "PREMIUM", "999", "0", "APROBADO"}), "ingresos 999");
        lanza(() -> SolicitudCredito.desdeCampos(new String[] {"CL1", "PREMIUM", "15001", "0", "APROBADO"}), "ingresos 15001");
        lanza(() -> SolicitudCredito.desdeCampos(new String[] {"CL1", "PREMIUM", "10000", "-1", "APROBADO"}), "deudas negativas");
        lanza(() -> SolicitudCredito.desdeCampos(new String[] {"CL1", "PREMIUM", "10000", "10000", "APROBADO"}), "deudas iguales a los ingresos");
        lanza(() -> SolicitudCredito.desdeCampos(new String[] {"CL1", "PREMIUM", "10000", "0"}), "4 campos");
        anda(() -> SolicitudCredito.desdeCampos(new String[] {"CL1", "PREMIUM", "1000", "0", "APROBADO"}), "ingresos 1000");
        System.out.println("OK");
    }
}
