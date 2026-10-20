package utnfc.backend.parcial;

import java.nio.file.Files;
import java.nio.file.Path;

public class Prueba {
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
        Path p = Files.createTempFile("pp", ".csv");
        Files.writeString(p, "id,rubro,importeCentavos,bonificacionCentavos,estado,diasCobertura\nC1,Electro,150000,50000,APROBADO,0\nC2,Electro,150000,50000,APROBADO,90\nC3,Electro,150000,50000,APROBADO,30\n");
        String s = salida(() -> { try { Main.main(new String[] { p.toString() }); } catch (Exception e) { throw new RuntimeException(e); } });
        contiene(s, "SIN_SEGURO: 1 | ASEGURADO: 2");
        contiene(s, "Total: 6800");
        System.out.println("OK");
    }
}
