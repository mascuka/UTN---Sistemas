package ar.edu.backend;

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
        Files.writeString(p, "id,region,porcentajeCPU,usoMemoria,estado,ingresos\ns1,norte,60,50,ALERTA,1300\ns2,sur,60,50,ESTABLE,1300\n");
        String s = salida(() -> { try { App.main(new String[] { p.toString() }); } catch (Exception e) { throw new RuntimeException(e); } });
        contiene(s, "ALERTA: 1 | CRITICO: 0");
        contiene(s, "Total:");
        System.out.println("OK");
    }
}
