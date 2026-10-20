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
    static double importe(String... c) { return Reparacion.desdeCampos(c).importe(); }
    public static void main(String[] a) throws Exception {
        igual(3840.0, importe("R1", "Ana", "celular", "Samsung", "2", "3", "ENTREGADA", "1000", "SI", "200", "NORMAL"), "con garantía");
        igual(4350.0, importe("R1", "Ana", "celular", "Samsung", "2", "3", "ABIERTA", "1000", "NO", "200", "NORMAL"), "sin garantía");
        igual(4150.0, importe("R1", "Ana", "celular", "Samsung", "2", "3", "LISTA", "1000"), "formato viejo");
        lanza(() -> importe("R1", "Ana", "celular", "Samsung", "2", "3", "LISTA", "1000", "", "200", "NORMAL"), "garantía vacía");
        lanza(() -> importe("R1", "Ana", "celular", "Samsung", "2", "3", "LISTA", "1000", "SI", "-1", "NORMAL"), "repuestos negativos");
        ResultadoParseo r = new ParserReparaciones().leer(csv("id,cliente,dispositivo,marca,prioridad,horas,estado,costoBase,garantia,repuestos,modalidad",
                "R1,Ana,celular,Samsung,2,3,ENTREGADA,1000,SI,200,NORMAL", "R2,Luis,tablet,Apple,1,1,CANCELADA,x,y,z,w", "R3,Eva,notebook,Lenovo,1,2,ABIERTA,500,QUIZAS,0,NORMAL"));
        igual(1, r.getReparaciones().size(), "procesadas"); igual(1, r.getDescartadas(), "descartadas"); igual(1, r.getInvalidas(), "inválidas");
        System.out.println("OK");
    }
}
