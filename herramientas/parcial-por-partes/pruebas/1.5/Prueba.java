package utnfc.backend.parcial;

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
        ResultadoParseo r = new ParserLiquidaciones().leer(csv("id,rubro,importeCentavos,bonificacionCentavos,estado,diasCobertura",
                "C1,Electro,150000,50000,APROBADO,0", "C2,Hogar,80000,0,APROBADO", "C3,Hogar,abc,0,ANULADO,45"));
        igual(1, r.getProcesadas(), "procesadas (nuevo)"); igual(1, r.getInvalidas(), "inválidas (nuevo)"); igual(1, r.getDescartadas(), "descartadas (nuevo)");
        ResultadoParseo v = new ParserLiquidaciones().leer(csv("id,rubro,importeCentavos,bonificacionCentavos,estado",
                "C1,Electro,150000,50000,APROBADO", "C2,Hogar,80000,0,APROBADO,30"));
        igual(1, v.getProcesadas(), "procesadas (viejo)"); igual(1, v.getInvalidas(), "inválidas (viejo)");
        System.out.println("OK");
    }
}
