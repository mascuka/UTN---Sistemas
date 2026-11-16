package ar.edu.backend;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;

public class App {
    public static void main(String[] args) throws IOException {
        Path archivo = args.length == 0 ? Path.of("datos", "datos-parcial.csv") : Path.of(args[0]);
        ResultadoParseo resultado = new ParserVehiculos().parsear(archivo);
        Flota flota = new Flota(resultado.getVehiculos());
        Map<String, Long> porEstado = flota.contarPorEstado();

        System.out.println(resultado.getResumenErrores());
        System.out.println("Objetos: " + resultado.getVehiculos().size());
        System.out.println("EN_RUTA: " + porEstado.getOrDefault("EN_RUTA", 0L)
                + " | DEMORADO: " + porEstado.getOrDefault("DEMORADO", 0L));
        System.out.println(flota.panorama());
    }
}
