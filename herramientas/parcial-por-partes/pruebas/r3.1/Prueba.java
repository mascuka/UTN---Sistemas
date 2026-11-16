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
        VehiculoRuta g = v("A", "NORTE", "60", "10", "EN_RUTA", "GENERAL");
        igual(800, g.getCostoDesgasteOperativo(), "general"); igual(VehiculoRuta.class, g.getClass(), "GENERAL crea un VehiculoRuta");
        VehiculoRuta r = v("B", "NORTE", "60", "10", "EN_RUTA", "REFRIGERADA");
        igual(1100, r.getCostoDesgasteOperativo(), "refrigerada"); igual(true, r instanceof VehiculoRefrigerado, "REFRIGERADA crea la subclase");
        igual(1260, v("C", "SUR", "60", "30", "DEMORADO", "REFRIGERADA").getCostoDesgasteOperativo(), "refrigerada de 30 t");
        lanza(() -> v("D", "SUR", "60", "31", "DEMORADO", "REFRIGERADA"), "refrigerada de 31 t");
        anda(() -> v("E", "SUR", "60", "31", "DEMORADO", "GENERAL"), "general de 31 t");
        lanza(() -> v("F", "SUR", "60", "10", "EN_RUTA", ""), "tipo vacío");
        lanza(() -> v("F", "SUR", "60", "10", "EN_RUTA", "CONGELADA"), "tipo desconocido");
        lanza(() -> v("F", "SUR", "60", "10", "EN_RUTA", "refrigerada"), "en minúsculas");
        lanza(() -> v("F", "SUR", "0", "10", "EN_RUTA", "REFRIGERADA"), "las validaciones de siempre");
        igual(1100, v("G", "SUR", "60", "10", "EN_RUTA", " REFRIGERADA ").getCostoDesgasteOperativo(), "con espacios");
        igual(800, v("H", "SUR", "60", "10", "EN_RUTA").getCostoDesgasteOperativo(), "formato viejo: general");
        Flota f = new Flota(leer("patente,zona,velocidadPromedio,cargaToneladas,estado,tipoCarga", "A,NORTE,60,10,EN_RUTA,GENERAL", "B,NORTE,60,10,EN_RUTA,REFRIGERADA", "C,SUR,60,30,DEMORADO,REFRIGERADA").getVehiculos());
        igual(3160, f.getCostoTotalDesgasteOperativo(), "el total, con el recargo"); igual(1900, f.getCostoPorZona().get("NORTE"), "NORTE"); igual(1260, f.getCostoPorZona().get("SUR"), "SUR");
        System.out.println("OK");
    }
}
