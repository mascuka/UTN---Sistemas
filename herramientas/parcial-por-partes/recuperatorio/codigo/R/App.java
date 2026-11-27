package ar.edu.backend;

import java.io.IOException;
import java.nio.file.Path;

public class App {
    public static void main(String[] args) throws IOException {
        Path archivo = args.length == 0 ? Path.of("datos", "datos-parcial.csv") : Path.of(args[0]);
        ResultadoParseo resultado = new ParserVehiculos().parsear(archivo);
        Flota flota = new Flota(resultado.getVehiculos());

        System.out.println(resultado.getResumenErrores());
        System.out.println("Objetos: " + resultado.getVehiculos().size());
        System.out.println(flota.panorama());
    }
}
