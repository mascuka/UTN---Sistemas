package ar.edu.backend;

import java.util.List;

public class Prueba {
    static void igual(Object esperado, Object real, String que) {
        if (!java.util.Objects.equals(esperado, real)) throw new AssertionError(que + ": se esperaba " + esperado + " y dio " + real);
    }
    static void lanza(Runnable r, String que) {
        try { r.run(); } catch (IllegalArgumentException e) { return; }
        throw new AssertionError(que + ": tenía que lanzar IllegalArgumentException");
    }
    public static void main(String[] a) {
        Servidor nuevo = Servidor.desdeCampos(new String[] { "s1", "norte", "60", "50", "ALERTA", "1300" });
        Servidor viejo = Servidor.desdeCampos(new String[] { "s2", "sur", "60", "50", "CRITICO" });
        igual(57, nuevo.getIndiceCarga(), "índice");
        igual(741, nuevo.costoRiesgoOperativo(), "costo con ingresos 1300");
        igual(570, viejo.costoRiesgoOperativo(), "costo del formato viejo");
        igual(1311, new Cloud(List.of(nuevo, viejo)).total(), "total() con los dos");
        igual(845, new ServidorConIngresos("x", "n", 65, 1300).costoRiesgoOperativo(), "ejemplo del enunciado");
        lanza(() -> Servidor.desdeCampos(new String[] { "s", "n", "60", "50", "ALERTA", "1900" }), "1900");
        lanza(() -> Servidor.desdeCampos(new String[] { "s", "n", "60", "50", "ALERTA", "999" }), "999");
        Servidor.desdeCampos(new String[] { "s", "n", "60", "50", "ALERTA", "1000" });
        System.out.println("OK");
    }
}
