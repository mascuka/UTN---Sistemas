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
        VehiculoRuta x = v("A", "NORTE", "60", "10", "EN_RUTA");
        igual(800, x.getCostoDesgasteOperativo(), "EN_RUTA"); igual(VehiculoRuta.class, x.getClass(), "EN_RUTA crea un VehiculoRuta");
        VehiculoRuta b = v("B", "NORTE", "60", "10", "DEMORADO");
        igual(920, b.getCostoDesgasteOperativo(), "DEMORADO"); igual(true, b instanceof VehiculoDemorado, "DEMORADO crea la subclase");
        igual(1495, v("C", "CENTRO", "101", "11", "DEMORADO").getCostoDesgasteOperativo(), "índice 65");
        igual(805, v("D", "SUR", "51", "11", "DEMORADO").getCostoDesgasteOperativo(), "índice 35");
        lanza(() -> v("E", "SUR", "60", "10", "PERDIDO"), "estado desconocido");
        Flota f = new Flota(leer("patente,zona,velocidadPromedio,cargaToneladas,estado", "A,NORTE,60,10,EN_RUTA", "B,NORTE,60,10,DEMORADO", "C,CENTRO,101,11,DEMORADO", "D,SUR,51,11,DEMORADO").getVehiculos());
        igual(4020, f.getCostoTotalDesgasteOperativo(), "el total, con el 15 %"); igual(1720, f.getCostoPorZona().get("NORTE"), "NORTE");
        System.out.println("OK");
    }
}
