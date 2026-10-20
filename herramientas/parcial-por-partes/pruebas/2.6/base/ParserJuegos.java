package ar.edu.backend.juegos;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class ParserJuegos {
    private static final String SEPARADOR = ";";
    private static final String CABECERA = "id;nombre;anio;min_jugadores;max_jugadores;duracion;rating;peso;categoria";
    private static final String CABECERA_10 = CABECERA + ";dificultad_cooperativa";

    public ResultadoParseo parsear(String rutaArchivo) {
        List<JuegoMesa> juegos = new ArrayList<>();
        int leidas = 0;
        int procesadas = 0;
        int descartadas = 0;
        int invalidas = 0;

        int columnas = 9;
        try (Scanner scanner = new Scanner(new File(rutaArchivo))) {
            if (scanner.hasNextLine()) {
                String lineaCabecera = scanner.nextLine();
                if (CABECERA_10.equals(lineaCabecera)) {
                    columnas = 10;
                } else if (!CABECERA.equals(lineaCabecera)) {
                    throw new IllegalArgumentException("Cabecera incorrecta");
                }
            }

            while (scanner.hasNextLine()) {
                leidas++;
                String linea = scanner.nextLine();
                if (linea.isBlank()) continue;

                try {
                    String[] campos = linea.split(SEPARADOR, -1);
                    if (campos.length != columnas) {
                        throw new IllegalArgumentException("Cantidad de columnas incorrecta");
                    }
                    
                    JuegoMesa juego = JuegoMesa.desdeCampos(campos);
                    
                    if (juego.getRating() < 1.0) {
                        descartadas++;
                    } else {
                        juegos.add(juego);
                        procesadas++;
                    }
                } catch (ArrayIndexOutOfBoundsException | IllegalArgumentException e) {
                    invalidas++;
                }
            }
        } catch (FileNotFoundException e) {
            throw new RuntimeException("Archivo no encontrado: " + rutaArchivo);
        }

        return new ResultadoParseo(juegos, leidas, procesadas, descartadas, invalidas);
    }
}
