package ar.edu.backend;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ParserServidores {

    private static final String CABECERA = "id,region,porcentajeCPU,usoMemoria,estado";

    public ResultadoParseo leer(Path archivo) throws IOException {
        List<Servidor> servidores = new ArrayList<>();
        List<String> errores = new ArrayList<>();
        List<String> descartes = new ArrayList<>();
        String log = "Linea %d: %s";
        int leidas = 0;
        try (BufferedReader lector = Files.newBufferedReader(archivo, StandardCharsets.UTF_8)) {
            if (!CABECERA.equals(lector.readLine()))
                throw new IllegalArgumentException("encabezado incorrecto");

            String linea;
            while ((linea = lector.readLine()) != null) {
                leidas++;
                int numero = leidas + 1;
                try {
                    String[] tokens = Arrays.stream(linea.split(",", -1)).map(String::strip).toArray(String[]::new);
                    if (tokens.length != 5)
                        throw new IllegalArgumentException("cantiad de columnas incorrectas");

                    if (tokens[4].equals("ESTABLE")) {
                        descartes.add(log.formatted(numero, "ESTABLE"));
                        continue;
                    }

                    if (!List.of("ALERTA", "CRITICO").contains(tokens[4]))
                        throw new IllegalArgumentException("estado desconocido: " + tokens[4]);

                    servidores.add(Servidor.desdeCampos(tokens));
                } catch (IllegalArgumentException ex) {
                    errores.add(log.formatted(numero, ex.getMessage()));
                }
            }
        }
        return new ResultadoParseo(servidores, leidas, descartes.size(), errores, descartes);
    }

}
