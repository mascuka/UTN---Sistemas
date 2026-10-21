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
        ResultadoProceso r = new ParserSolicitudes().procesar(csv("idCliente,tipoCliente,ingresosMensuales,totalDeudasActuales,estadoSolicitud",
                "CL1,PREMIUM,10000,2000,APROBADO", "CL2,BLACK,10000,2000,APROBADO", "CL3,BLACK", "CL4,PREMIUM,10000,2000,APROBADO,",
                "CL5,PREMIUM,500,0,APROBADO", "CL6,VIP,10000,2000,APROBADO", "CL7,REGULAR,abc,0,APROBADO", "CL8"));
        igual(8, r.getLeidas(), "leídas"); igual(1, r.getProcesadas(), "procesadas");
        igual(1, r.getDescartadas(), "descartadas"); igual(6, r.getInvalidas(), "inválidas");
        igual("Linea 3: BLACK", r.getDescartes().get(0), "el descarte");
        System.out.println("OK");
    }
}
