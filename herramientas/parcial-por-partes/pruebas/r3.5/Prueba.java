package ar.edu.backend;

import java.util.*;

public class Prueba {
    static java.nio.file.Path csv(String... lineas) throws Exception {
        java.nio.file.Path p = java.nio.file.Files.createTempFile("pp", ".csv");
        java.nio.file.Files.writeString(p, String.join("\n", lineas) + "\n");
        return p;
    }
    static ResultadoParseo leer(String... lineas) {
        try { return new ParserVehiculos().parsear(csv(lineas)); }
        catch (IllegalArgumentException e) { throw e; }
        catch (Exception e) { throw new RuntimeException(e); }
    }
    static VehiculoRuta v(String... campos) { return VehiculoRuta.desdeCampos(campos); }
    static void igual(Object esperado, Object real, String que) {
        if (!Objects.equals(esperado, real)) throw new AssertionError(que + ": se esperaba " + esperado + " y dio " + real);
    }
    static void lanza(Runnable r, String que) {
        try { r.run(); } catch (IllegalArgumentException e) { return; }
        throw new AssertionError(que + ": tenía que lanzar IllegalArgumentException");
    }
    static void anda(Runnable r, String que) {
        try { r.run(); } catch (RuntimeException e) { throw new AssertionError(que + ": no tenía que fallar y tiró " + e); }
    }
    static String salida(String... args) {
        java.io.PrintStream antes = System.out;
        java.io.ByteArrayOutputStream b = new java.io.ByteArrayOutputStream();
        System.setOut(new java.io.PrintStream(b, true));
        try { App.main(args); } catch (Exception e) { throw new RuntimeException(e); } finally { System.setOut(antes); }
        return b.toString();
    }
    static void contiene(String texto, String parte) {
        if (!texto.contains(parte)) throw new AssertionError("la salida no tiene \"" + parte + "\":\n" + texto);
    }
    public static void main(String[] a) throws Exception {
        VehiculoRuta va = v("A", "NORTE", "76", "11", "EN_RUTA", "30");
        igual(49, va.getIndiceDesgaste(), "índice nuevo (49.6 truncado)"); igual(980, va.getCostoDesgasteOperativo(), "costo del nuevo");
        VehiculoRuta vb = v("B", "NORTE", "76", "11", "EN_RUTA");
        igual(50, vb.getIndiceDesgaste(), "índice original"); igual(1000, vb.getCostoDesgasteOperativo(), "costo del original");
        igual(25, v("C", "SUR", "40", "10", "DEMORADO", "0").getIndiceDesgaste(), "con 0 %");
        igual(40, v("D", "SUR", "40", "10", "DEMORADO", "100").getIndiceDesgaste(), "con 100 %");
        igual(1980, new Flota(List.of(va, vb)).getCostoTotalDesgasteOperativo(), "la flota suma los dos");
        anda(() -> new VehiculoRuta("X", "NORTE", 76, 11, "EN_RUTA", 50), "el constructor público con la fórmula vieja");
        lanza(() -> new VehiculoRuta("X", "NORTE", 76, 11, "EN_RUTA", 49), "el público sigue chequeando la fórmula vieja");
        System.out.println("OK");
    }
}
