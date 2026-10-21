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
        // Los argumentos de "new Clase(...)": textos entre comillas, null o enteros
        static java.util.List<String> argumentos(String llamada) {
            java.util.regex.Matcher m = java.util.regex.Pattern.compile("\"([^\"]*)\"|null|-?\\d+").matcher(llamada.substring(llamada.indexOf('(')));
            java.util.List<String> xs = new java.util.ArrayList<>();
            while (m.find()) xs.add(m.group().equals("null") ? null : m.group(1) != null ? m.group(1) : m.group());
            return xs;
        }
    public static void main(String[] a) {
        String[] items = a[0].split("\\|", -1);
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < items.length; i++) {
            java.util.List<String> x = argumentos(items[i]);
            String r;
            try { new Consumo(x.get(0), x.get(1), Integer.parseInt(x.get(2)), Integer.parseInt(x.get(3))); r = "Se crea"; } catch (IllegalArgumentException e) { r = "Excepción"; }
            sb.append(r).append(i < items.length - 1 ? "," : "");
        }
        System.out.println(sb);
    }
}
