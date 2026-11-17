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
        VehiculoRuta x = v("trk-1", "NORTE", "60", "10", "EN_RUTA", "3");
        igual(3, x.getPeajes(), "3 peajes"); igual(950, x.getCostoDesgasteOperativo(), "800 + 150");
        igual(0, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "").getPeajes(), "vacío = 0");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "  ").getCostoDesgasteOperativo(), "con espacios también");
        igual(1300, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "10").getCostoDesgasteOperativo(), "10 vale");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_RUTA").getCostoDesgasteOperativo(), "formato viejo");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "0"), "un 0 escrito");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "11"), "más de 10");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "x"), "no es entero");
        igual(0, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40).getPeajes(), "el constructor viejo delega con 0");
        lanza(() -> new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, 11), "el constructor nuevo valida");
        System.out.println("OK");
    }
}
