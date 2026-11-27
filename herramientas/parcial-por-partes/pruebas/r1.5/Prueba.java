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
        ResultadoParseo r = leer("patente,zona,velocidadPromedio,cargaToneladas,estado,porcentajeRutaSinPAvimentar", "trk-1,NORTE,76,11,EN_RUTA", "trk-2,SUR,76,11,EN_RUTA,30", "trk-3,SUR,76,11", "trk-4,SUR,76,11,EN_RUTA,30,x", "trk-5,SUR,999,-5,EN_DEPOSITO,500");
        igual(5, r.getFilasLeidas(), "leídas"); igual(2, r.getFilasProcesadas(), "procesadas"); igual(1, r.getFilasDescartadas(), "descartadas"); igual(2, r.getFilasInvalidas(), "inválidas");
        igual(4, r.getErrores().get(0).getNumeroLinea(), "la fila de 4 campos está en la línea 4");
        ResultadoParseo viejo = leer("patente,zona,velocidadPromedio,cargaToneladas,estado", "trk-1,NORTE,76,11,EN_RUTA", "trk-2,NORTE,76,11,EN_RUTA,30");
        igual(1, viejo.getFilasProcesadas(), "formato original"); igual(1, viejo.getFilasInvalidas(), "6 campos bajo el encabezado original");
        igual(1, leer("patente,zona,velocidadPromedio,cargaToneladas,estado,porcentajeRutaSinPAvimentar", "trk-1,NORTE,76,11,EN_RUTA", "patente,zona,velocidadPromedio,cargaToneladas,estado,porcentajeRutaSinPAvimentar").getFilasInvalidas(), "el encabezado repetido es inválido");
        lanza(() -> leer("otra,cabecera"), "otro encabezado");
        System.out.println("OK");
    }
}
