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
        VehiculoRuta x = v("A", "NORTE", "60", "10", "EN_RUTA", "3000");
        igual(1200, x.getCostoDesgasteOperativo(), "3000 × 40 / 100"); igual(true, x instanceof VehiculoConFacturacion, "6 campos crea la subclase");
        igual(1690, v("B", "CENTRO", "101", "11", "DEMORADO", "2600").getCostoDesgasteOperativo(), "2600 × 65 / 100");
        igual(800, v("C", "SUR", "60", "10", "EN_RUTA", "2000").getCostoDesgasteOperativo(), "el mínimo es inclusive");
        igual(1519, v("C", "SUR", "60", "10", "EN_RUTA", "3799").getCostoDesgasteOperativo(), "división entera");
        lanza(() -> v("C", "SUR", "60", "10", "EN_RUTA", "3800"), "el tope es exclusive");
        lanza(() -> v("C", "SUR", "60", "10", "EN_RUTA", "1999"), "menos de 2000");
        lanza(() -> v("C", "SUR", "60", "10", "EN_RUTA", ""), "vacía");
        lanza(() -> v("C", "SUR", "0", "10", "EN_RUTA", "3000"), "las validaciones de siempre");
        VehiculoRuta viejo = v("D", "SUR", "60", "10", "EN_RUTA");
        igual(800, viejo.getCostoDesgasteOperativo(), "formato viejo: 2000"); igual(VehiculoRuta.class, viejo.getClass(), "5 campos crea un VehiculoRuta");
        Flota f = new Flota(leer("patente,zona,velocidadPromedio,cargaToneladas,estado,facturacion", "A,NORTE,60,10,EN_RUTA,3000", "B,CENTRO,101,11,DEMORADO,2600", "C,SUR,60,10,EN_RUTA,3800").getVehiculos());
        igual(2890, f.getCostoTotalDesgasteOperativo(), "el total, con la facturación"); igual(1690, f.getCostoPorZona().get("CENTRO"), "CENTRO");
        System.out.println("OK");
    }
}
