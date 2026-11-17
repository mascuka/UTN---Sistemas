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
        VehiculoRuta x = v("trk-1", "NORTE", "60", "10", "EN_RUTA", "3000");
        igual(3000, x.getFacturacion(), "la facturación"); igual(1200, x.getCostoDesgasteOperativo(), "3000 × 40 / 100");
        igual(800, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "2000").getCostoDesgasteOperativo(), "2000 vale");
        igual(1519, v("trk-1", "NORTE", "60", "10", "EN_RUTA", "3799").getCostoDesgasteOperativo(), "división entera");
        igual(1950, v("trk-1", "NORTE", "101", "11", "EN_RUTA", "3000").getCostoDesgasteOperativo(), "el ejemplo: índice 65");
        VehiculoRuta viejo = v("trk-1", "NORTE", "60", "10", "EN_RUTA");
        igual(2000, viejo.getFacturacion(), "formato viejo: 2000"); igual(800, viejo.getCostoDesgasteOperativo(), "formato viejo: el costo de siempre");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "3800"), "3800 no");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "1999"), "menos de 2000");
        lanza(() -> v("trk-1", "NORTE", "60", "10", "EN_RUTA", "mucho"), "no es entero");
        igual(2000, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40).getFacturacion(), "el constructor viejo delega con 2000");
        igual(1000, new VehiculoRuta("trk-1", "NORTE", 60, 10, "EN_RUTA", 40, 2500).getCostoDesgasteOperativo(), "el constructor nuevo");
        System.out.println("OK");
    }
}
