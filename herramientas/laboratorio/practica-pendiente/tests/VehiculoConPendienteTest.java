package ar.edu.backend;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class VehiculoConPendienteTest {
    private static final String ENCABEZADO_NUEVO =
            "patente,zona,velocidadPromedio,cargaToneladas,estado,pendientePromedio\n";

    @Test
    void cincoCamposEsUnVehiculoRutaConLaFormulaOriginal() {
        VehiculoRuta vehiculo = VehiculoRuta.desdeCampos(new String[] {"trk-1", "NORTE", "70", "25", "EN_RUTA"});

        assertEquals(VehiculoRuta.class, vehiculo.getClass());
        assertEquals(52, vehiculo.getIndiceDesgaste());
        assertEquals(1040, vehiculo.getCostoDesgasteOperativo());
    }

    @Test
    void seisCamposEsUnVehiculoConPendienteConLaFormulaPonderada() {
        VehiculoRuta vehiculo = VehiculoRuta.desdeCampos(
                new String[] {" trk-1 ", " NORTE ", "70", "25", "EN_RUTA", " 12 "});

        VehiculoConPendiente conPendiente = assertInstanceOf(VehiculoConPendiente.class, vehiculo);
        assertEquals(12, conPendiente.getPendientePromedio());
        assertEquals(44, vehiculo.getIndiceDesgaste());
        assertEquals(880, vehiculo.getCostoDesgasteOperativo());
    }

    @Test
    void aceptaLosDosLimitesDeLaPendienteYRechazaLoDeAfuera() {
        assertEquals(33, VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "60", "10", "DEMORADO", "0"}).getIndiceDesgaste());
        assertEquals(60, VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "90", "30", "EN_RUTA", "30"}).getIndiceDesgaste());
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "80", "20", "EN_RUTA", "31"}));
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "75", "15", "DEMORADO", "-1"}));
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "85", "40", "DEMORADO", "diez"}));
    }

    @Test
    void elIndiceSeValidaConLaFormulaDeCadaFormato() {
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-5", "NORTE", "128", "43", "EN_RUTA"}));
        VehiculoRuta nuevo = VehiculoRuta.desdeCampos(new String[] {"trk-6", "NORTE", "128", "43", "EN_RUTA", "10"});
        assertEquals(78, nuevo.getIndiceDesgaste());
        assertEquals(1560, nuevo.getCostoDesgasteOperativo());
        assertThrows(IllegalArgumentException.class,
                () -> new VehiculoConPendiente("trk-1", "NORTE", 70, 25, "EN_RUTA", 52, 12));
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "NORTE", "2", "-5", "EN_RUTA", "0"}));
    }

    @Test
    void rechazaAnchosDistintosDeCincoYSeis() {
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "NORTE", "70", "20"}));
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "NORTE", "70", "20", "EN_RUTA", "10", "extra"}));
    }

    @Test
    void bajoElEncabezadoOriginalNoAceptaSeisCampos(@TempDir Path directorio) throws IOException {
        Path archivo = directorio.resolve("viejo.csv");
        Files.writeString(archivo, "patente,zona,velocidadPromedio,cargaToneladas,estado\n"
                + "trk-1,NORTE,70,25,EN_RUTA,12\n"
                + "trk-2,NORTE,70,25,EN_RUTA\n", StandardCharsets.UTF_8);

        ResultadoParseo resultado = new ParserVehiculos().parsear(archivo);

        assertEquals(1, resultado.getFilasProcesadas());
        assertEquals(1, resultado.getFilasInvalidas());
        assertEquals(2, resultado.getErrores().get(0).getNumeroLinea());
    }

    @Test
    void bajoElEncabezadoNuevoAceptaCincoYSeisYDescartaSinValidar(@TempDir Path directorio) throws IOException {
        Path archivo = directorio.resolve("nuevo.csv");
        Files.writeString(archivo, ENCABEZADO_NUEVO
                + "trk-1,NORTE,70,25,EN_RUTA,12\n"
                + "trk-2,NORTE,70,25,EN_RUTA\n"
                + "trk-3,SUR,999,abc,EN_DEPOSITO,x\n"
                + "\n", StandardCharsets.UTF_8);

        ResultadoParseo resultado = new ParserVehiculos().parsear(archivo);
        Flota flota = new Flota(resultado.getVehiculos());

        assertEquals(4, resultado.getFilasLeidas());
        assertEquals(2, resultado.getFilasProcesadas());
        assertEquals(1, resultado.getFilasDescartadas());
        assertEquals(1, resultado.getFilasInvalidas());
        assertEquals(5, resultado.getErrores().get(0).getNumeroLinea());
        assertEquals(1920, flota.getCostoTotalDesgasteOperativo());
    }

    @Test
    void procesaElArchivoCombinadoDelParcial() throws IOException {
        ResultadoParseo resultado = new ParserVehiculos().parsear(Path.of("datos", "datos-parcial.csv"));
        Flota flota = new Flota(resultado.getVehiculos());

        assertEquals(22, resultado.getFilasLeidas());
        assertEquals(9, resultado.getFilasProcesadas());
        assertEquals(2, resultado.getFilasDescartadas());
        assertEquals(11, resultado.getFilasInvalidas());
        assertEquals(9340, flota.getCostoTotalDesgasteOperativo());
        assertEquals(3440, flota.getCostoPorZona().get("NORTE"));
        assertEquals(1360, flota.getCostoPorZona().get("SUR"));
        assertEquals(4540, flota.getCostoPorZona().get("CENTRO"));
        assertEquals(5, flota.contarConIndiceDesgasteMenorA(55));
    }
}
