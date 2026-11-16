package ar.edu.backend;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public final class ParserVehiculos {
    private static final String ENCABEZADO = "patente,zona,velocidadPromedio,cargaToneladas,estado";
    private static final Set<String> ESTADOS_DESCARTADOS = Set.of("EN_DEPOSITO", "MANTENIMIENTO");

    public ResultadoParseo parsear(Path archivo) throws IOException {
        List<VehiculoRuta> vehiculos = new ArrayList<>();
        List<ErrorParseo> errores = new ArrayList<>();
        int filasLeidas = 0;
        int filasDescartadas = 0;

        try (BufferedReader lector = Files.newBufferedReader(archivo, StandardCharsets.UTF_8)) {
            String encabezado = lector.readLine();
            if (!ENCABEZADO.equals(encabezado)) {
                throw new IllegalArgumentException("Encabezado CSV incorrecto");
            }

            String linea;
            int numeroLinea = 1;
            while ((linea = lector.readLine()) != null) {
                numeroLinea++;
                filasLeidas++;
                String[] campos = linea.split(",", -1);
                if (campos.length != 5) {
                    errores.add(new ErrorParseo(numeroLinea, "La fila debe tener exactamente cinco columnas"));
                    continue;
                }

                String estado = campos[4].trim();
                if (ESTADOS_DESCARTADOS.contains(estado)) {
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
