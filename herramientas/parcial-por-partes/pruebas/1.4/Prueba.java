package ar.edu.backend;

import java.nio.file.Files;
import java.nio.file.Path;

public class Prueba {
    static Path csv(String... lineas) throws Exception {
        Path p = Files.createTempFile("pp", ".csv");
        Files.writeString(p, String.join("\n", lineas) + "\n");
        return p;
    }
    static void igual(Object esperado, Object real, String que) {
        if (!java.util.Objects.equals(esperado, real)) throw new AssertionError(que + ": se esperaba " + esperado + " y dio " + real);
    }
    static void lanza(Runnable r, String que) {
        try { r.run(); } catch (IllegalArgumentException e) { return; }
        throw new AssertionError(que + ": tenía que lanzar IllegalArgumentException");
    }
    public static void main(String[] a) throws Exception {
        ResultadoParseo r = new ParserServidores().leer(csv("id,region,porcentajeCPU,usoMemoria,estado,ingresos",
                "s1,norte,60,50,ALERTA,1300", "s2,sur,60,50,CRITICO", "s3,este,60,50,ESTABLE,1200"));
        igual(3, r.getLeidas(), "leídas (nuevo)"); igual(1, r.getProcesadas(), "procesadas (nuevo)");
        igual(1, r.getDescartadas(), "descartadas (nuevo)"); igual(1, r.getInvalidas(), "inválidas (nuevo)");
        ResultadoParseo v = new ParserServidores().leer(csv("id,region,porcentajeCPU,usoMemoria,estado",
                "s1,norte,60,50,ALERTA", "s2,sur,60,50,CRITICO,1300"));
        igual(1, v.getProcesadas(), "procesadas (viejo)"); igual(1, v.getInvalidas(), "inválidas (viejo)");
        try { new ParserServidores().leer(csv("id,region,cpu", "x")); throw new AssertionError("cabecera desconocida"); }
        catch (IllegalArgumentException e) { }
        System.out.println("OK");
    }
}
