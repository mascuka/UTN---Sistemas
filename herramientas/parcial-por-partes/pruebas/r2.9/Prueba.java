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
        igual("EN_TALLER", v("trk-1", "NORTE", "60", "10", "EN_TALLER").getEstado(), "EN_TALLER es válido");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_TALLER").getCostoDesgasteOperativo(), "el mismo costo");
        anda(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA"), "EN_RUTA sigue");
        anda(() -> v("trk-1", "NORTE", "60", "10", "DEMORADO"), "DEMORADO sigue");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "en_taller"), "en minúsculas");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "PERDIDO"), "desconocido");
        ResultadoParseo r = leer("patente,zona,velocidadPromedio,cargaToneladas,estado", "trk-1,NORTE,60,10,EN_TALLER", "trk-2,SUR,999,x,EN_DEPOSITO");
        igual(1, r.getFilasProcesadas(), "procesada"); igual(1, r.getFilasDescartadas(), "EN_DEPOSITO se sigue descartando");
        System.out.println("OK");
    }
}
