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
        VehiculoRuta x = v("trk-1", "NORTE", "60", "10", "EN_RUTA", "REFRIGERADA");
        igual("REFRIGERADA", x.getTipoCarga(), "el tipo"); igual(800, x.getCostoDesgasteOperativo(), "el costo no cambia");
        igual("GENERAL", v("trk-1", "NORTE", "60", "10", "EN_RUTA", " GENERAL ").getTipoCarga(), "con espacios");
        igual("GENERAL", v("trk-1", "NORTE", "60", "10", "EN_RUTA").getTipoCarga(), "formato viejo: GENERAL");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "REFRIGERADO"), "desconocido");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "general"), "en minúsculas");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", ""), "vacío");
        lanza(() -> v("trk-1", "NORTE", "60", "10"), "4 campos");
        igual("GENERAL", new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40).getTipoCarga(), "el constructor viejo delega con GENERAL");
        lanza(() -> new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, "OTRA"), "el constructor nuevo valida");
        System.out.println("OK");
    }
}
