package ar.edu.backend;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class ParserVehiculos {
    private static final String ENCABEZADO = "patente,zona,velocidadPromedio,cargaToneladas,estado";
    private static final String ENCABEZADO_NUEVO = "patente;zona;velocidadPromedio;cargaToneladas;estado;kilometros";

    public ResultadoParseo parsear(Path archivo) throws IOException {
        List<VehiculoRuta> vehiculos = new ArrayList<>();
        List<ErrorParseo> errores = new ArrayList<>();
        int filasLeidas = 0;
        int filasDescartadas = 0;

        try (BufferedReader lector = Files.newBufferedReader(archivo, StandardCharsets.UTF_8)) {
            String encabezado = lector.readLine();
            String separador;
            int columnas;
            if (ENCABEZADO.equals(encabezado)) {
                separador = ",";
                columnas = 5;
            } else if (ENCABEZADO_NUEVO.equals(encabezado)) {
                separador = ";";
                columnas = 6;
            } else {
                throw new IllegalArgumentException("Encabezado CSV incorrecto");
            }

            String linea;
            int numeroLinea = 1;
            while ((linea = lector.readLine()) != null) {
                numeroLinea++;
                filasLeidas++;
                String[] campos = linea.split(separador, -1);
                if (campos.length != columnas) {
                    errores.add(new ErrorParseo(numeroLinea, "La fila debe tener exactamente " + columnas + " columnas"));
                    continue;
                }

                String estado = campos[4].trim();
                if ("EN_DEPOSITO".equals(estado)) {
                    filasDescartadas++;
                    continue;
                }

                try {
                    vehiculos.add(VehiculoRuta.desdeCampos(campos));
                } catch (IllegalArgumentException exception) {
                    errores.add(new ErrorParseo(numeroLinea, exception.getMessage()));
                }
            }
        }

        return new ResultadoParseo(vehiculos, errores, filasLeidas, filasDescartadas);
    }
}
