package ar.edu.backend;

import java.util.List;
import java.util.Map;

public class Prueba {
    static void igual(Object esperado, Object real, String que) {
        if (!java.util.Objects.equals(esperado, real)) throw new AssertionError(que + ": se esperaba " + esperado + " y dio " + real);
    }
    public static void main(String[] a) {
        Cloud c = new Cloud(List.of(Servidor.desdeCampos(new String[] { "a", "n", "60", "50", "ALERTA" }),
                Servidor.desdeCampos(new String[] { "b", "n", "60", "50", "ALERTA", "1300" }),
                Servidor.desdeCampos(new String[] { "c", "s", "60", "50", "CRITICO" })));
        igual(Map.of("ALERTA", 2L, "CRITICO", 1L), c.conteoPorEstado(), "conteo por estado");
        igual(Map.of(), new Cloud(List.of()).conteoPorEstado(), "colección vacía");
        igual("SIN ESTADO", new Servidor("x", "n", 10).getEstado(), "constructor viejo");
        System.out.println("OK");
    }
}
