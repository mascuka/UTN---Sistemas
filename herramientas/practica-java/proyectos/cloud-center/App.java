package ar.edu.backend;

import java.io.IOException;
import java.nio.file.Path;

public class App {
    public static void main(String[] args) throws IOException {
        Path archivo = Path.of(args.length == 0 ? "datos/datos.csv" : args[0]);
        ResultadoParseo resultado = new ParserServidores().leer(archivo);
        Cloud colector = new Cloud(resultado.getServidores());

        System.out.println(resultado.informe());
        resultado.getDescartes().forEach(System.out::println);
        resultado.getErrores().forEach(System.out::println);
        System.out.println(colector.panorama());
    }
}
