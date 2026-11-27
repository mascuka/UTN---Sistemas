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
        VehiculoRuta va = v("A", "NORTE", "76", "11", "EN_RUTA", "0");
        igual(true, va instanceof VehiculoRutaConTramoSinPavimentar, "6 campos crea la subclase");
        igual(VehiculoRuta.class, VehiculoRutaConTramoSinPavimentar.class.getSuperclass(), "hereda directo de VehiculoRuta");
        igual(0, ((VehiculoRutaConTramoSinPavimentar) va).getPorcentajeRutaSinPAvimentar(), "el porcentaje");
        igual(100, ((VehiculoRutaConTramoSinPavimentar) v("B", "SUR", "76", "11", "EN_RUTA", "100")).getPorcentajeRutaSinPAvimentar(), "100 es válido");
        lanza(() -> v("C", "SUR", "76", "11", "EN_RUTA", "101"), "101 está fuera de rango");
        lanza(() -> v("C", "SUR", "76", "11", "EN_RUTA", "-1"), "-1 está fuera de rango");
        lanza(() -> v("D", "SUR", "76", "11", "EN_RUTA", "abc"), "no es un número");
        igual(VehiculoRuta.class, v("E", "SUR", "76", "11", "EN_RUTA").getClass(), "5 campos crea un VehiculoRuta");
        lanza(() -> v("F", "SUR", "76", "11"), "4 campos");
        System.out.println("OK");
    }
}
