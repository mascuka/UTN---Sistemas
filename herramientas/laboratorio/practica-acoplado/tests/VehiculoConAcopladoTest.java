package ar.edu.backend;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class VehiculoConAcopladoTest {
    @Test
    void sinAcopladoConservaTodoLoAnterior() {
        VehiculoRuta vehiculo = VehiculoRuta.desdeCampos(new String[] {"trk-1", "NORTE", "76", "11", "EN_RUTA", "0"});

        assertEquals(VehiculoRuta.class, vehiculo.getClass());
        assertEquals(0, vehiculo.getAcoplado());
        assertEquals(1000, vehiculo.getCostoDesgasteOperativo());
        assertEquals(1320, VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "100", "15", "EN_RUTA", "0"}).getCostoDesgasteOperativo());
    }

    @Test
    void conAcopladoEsLaSubclaseYSumaPorCadaTonelada() {
        VehiculoRuta vehiculo = VehiculoRuta.desdeCampos(new String[] {" trk-1 ", "NORTE", "76", "11", "EN_RUTA", " 5 "});

        assertInstanceOf(VehiculoConAcoplado.class, vehiculo);
        assertEquals(5, vehiculo.getAcoplado());
        assertEquals(1200, vehiculo.getCostoDesgasteOperativo());
        assertEquals(2040, VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "90", "20", "DEMORADO", "20"}).getCostoDesgasteOperativo());
    }

    @Test
    void elTopeDeVelocidadEsSoloParaLosQueLlevanAcoplado() {
        VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "90", "20", "EN_RUTA", "10"});
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "91", "20", "EN_RUTA", "10"}));
        assertEquals(1800, VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "121", "45", "EN_RUTA", "0"}).getCostoDesgasteOperativo());
        assertThrows(IllegalArgumentException.class,
                () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "121", "45", "EN_RUTA", "3"}));
    }

    @Test
    void elAcopladoEsUnEnteroDe0A20() {
        for (String malo : new String[] {"21", "-1", "", "cinco"}) {
            assertThrows(IllegalArgumentException.class,
                    () -> VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "60", "10", "EN_RUTA", malo}), malo);
        }
        assertEquals(0, VehiculoRuta.desdeCampos(new String[] {"trk-1", "SUR", "60", "10", "EN_RUTA"}).getAcoplado());
        assertEquals(0, new VehiculoRuta("trk-1", "SUR", 60, 10, "EN_RUTA", 40).getAcoplado());
    }

    @Test
    void cuentaPorModalidadSinInstanceof() {
        Flota flota = new Flota(List.of(
                VehiculoRuta.desdeCampos(new String[] {"a", "NORTE", "60", "10", "EN_RUTA", "0"}),
                VehiculoRuta.desdeCampos(new String[] {"b", "NORTE", "60", "10", "EN_RUTA", "4"}),
                VehiculoRuta.desdeCampos(new String[] {"c", "SUR", "60", "10", "DEMORADO", "1"})));

        assertEquals(1L, flota.contarPorTipo().get("SIN_ACOPLADO"));
        assertEquals(2L, flota.contarPorTipo().get("CON_ACOPLADO"));
        assertTrue(new Flota(List.of()).contarPorTipo().isEmpty());
    }

    @Test
    void cadaFilaConElAnchoDeSuEncabezado(@TempDir Path directorio) throws IOException {
        Path archivo = directorio.resolve("datos.csv");
        Files.writeString(archivo, "patente,zona,velocidadPromedio,cargaToneladas,estado,acoplado\n"
                + "trk-1,NORTE,60,10,EN_RUTA,2\n"
                + "trk-2,NORTE,60,10,EN_RUTA\n"
                + "trk-3,SUR,999,abc,EN_DEPOSITO,x\n", StandardCharsets.UTF_8);

        ResultadoParseo resultado = new ParserVehiculos().parsear(archivo);

        assertEquals(1, resultado.getFilasProcesadas());
        assertEquals(1, resultado.getFilasDescartadas());
        assertEquals(1, resultado.getFilasInvalidas());
        assertEquals(3, resultado.getErrores().get(0).getNumeroLinea());
    }

    @Test
    void procesaElArchivoDelParcial() throws IOException {
        ResultadoParseo resultado = new ParserVehiculos().parsear(Path.of("datos", "datos-parcial.csv"));
        Flota flota = new Flota(resultado.getVehiculos());

        assertEquals(26, resultado.getFilasLeidas());
        assertEquals(11, resultado.getFilasProcesadas());
        assertEquals(2, resultado.getFilasDescartadas());
        assertEquals(13, resultado.getFilasInvalidas());
        assertEquals(12700, flota.getCostoTotalDesgasteOperativo());
        assertEquals(4480, flota.getCostoPorZona().get("NORTE"));
        assertEquals(2880, flota.getCostoPorZona().get("SUR"));
        assertEquals(5340, flota.getCostoPorZona().get("CENTRO"));
        assertEquals(5L, flota.contarPorTipo().get("SIN_ACOPLADO"));
        assertEquals(6L, flota.contarPorTipo().get("CON_ACOPLADO"));
    }
}
