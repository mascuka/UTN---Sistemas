package utnfc.backend.parcial;

import java.nio.file.Files;
import java.nio.file.Path;

public class Prueba {
    public static void main(String[] a) throws Exception {
        Path p = Files.createTempFile("pp", ".csv");
        Files.writeString(p, String.join("\n", a[0].split("\\|", -1)) + "\n");
        ResultadoParseo r = new ParserLiquidaciones().leer(p);
        StringBuilder sb = new StringBuilder();
        int filas = a[0].split("\\|", -1).length - 1;
        for (int i = 2; i <= filas + 1; i++)
            sb.append(r.getDescartes().containsKey(i) ? "Descartada" : r.getErrores().containsKey(i) ? "Inválida" : "Procesada").append(i <= filas ? "," : "");
        System.out.println(sb);
    }
}
