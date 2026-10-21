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
    static Envio d(String bruto, String embalaje, String modalidad) { return Envio.desdeCampos(new String[] {"E", "Norte", bruto, embalaje, "LISTO", modalidad}); }
    public static void main(String[] a) throws Exception {
        Envio n = d("1200", "200", "NORMAL");
        igual(700, n.costo(), "normal de 1000 g"); igual(Envio.class, n.getClass(), "NORMAL crea un Envio");
        Envio p = d("1200", "200", "PRIORITARIO");
        igual(1100, p.costo(), "prioritario de 1000 g"); igual(true, p instanceof EnvioPrioritario, "PRIORITARIO crea la subclase");
        igual(1900, d("5200", "200", "PRIORITARIO").costo(), "prioritario de 5000 g");
        lanza(() -> d("5201", "200", "PRIORITARIO"), "prioritario de 5001 g");
        lanza(() -> d("1200", "200", ""), "modalidad vacía");
        lanza(() -> d("1200", "200", "URGENTE"), "modalidad desconocida");
        lanza(() -> d("1200", "200", "prioritario"), "en minúsculas");
        lanza(() -> d("0", "0", "PRIORITARIO"), "las validaciones de siempre");
        igual(700, Envio.desdeCampos(new String[] {"E", "N", "1200", "200", "LISTO"}).costo(), "formato viejo: normal");
        ResultadoParseo r = new ParserEnvios().leer(csv("id,zona,brutoGramos,embalajeGramos,estado,modalidad", "A,N,1200,200,LISTO,NORMAL", "B,N,1200,200,LISTO,PRIORITARIO", "C,S,5200,200,LISTO,PRIORITARIO"));
        CentralEnvios c = new CentralEnvios(r.getEnvios());
        igual(3700, c.total(), "el total, con el recargo"); igual(java.util.Map.of("N", 1800, "S", 1900), c.totalesPorZona(), "los totales por zona");
        igual(2, c.filtrar(e -> e.costo() > 1000).size(), "el filtro por costo");
        System.out.println("OK");
    }
}
