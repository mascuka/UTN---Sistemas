package utnfc.backend.parcial;

import java.io.IOException;
import java.nio.file.Path;

public class Main {
    public static void main(String[] args) throws IOException {
        Path archivo = Path.of(args.length == 0 ? "datos/datos.csv" : args[0]);
        ResultadoParseo resultado = new ParserLiquidaciones().leer(archivo);
        LiquidadorTarjetas liquidador = new LiquidadorTarjetas(resultado.getConsumos());
        System.out.println(resultado);
        resultado.getDescartes().forEach((linea, motivo) -> System.out.println("Línea " + linea + ": " + motivo));
        resultado.getErrores().forEach((linea, motivo) -> System.out.println("Línea " + linea + ": " + motivo));
        System.out.println(liquidador.panorama());
    }
}
