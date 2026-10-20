package ar.edu.backend;

import java.nio.file.Files;
import java.nio.file.Path;

public class Prueba {
    public static void main(String[] a) throws Exception {
        String[] lineas = a[0].split("\\|", -1);
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < lineas.length; i++) {
            Path p = Files.createTempFile("pp", ".csv");
            Files.writeString(p, lineas[0] + "\n" + lineas[i] + "\n");
            ResultadoParseo r = new ParserServidores().leer(p);
            sb.append(r.getDescartadas() == 1 ? "Descartada" : r.getInvalidas() == 1 ? "Inválida" : "Procesada").append(i < lineas.length - 1 ? "," : "");
        }
        System.out.println(sb);
    }
}
