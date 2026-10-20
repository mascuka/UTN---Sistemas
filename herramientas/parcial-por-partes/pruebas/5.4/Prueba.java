package ar.edu.backend.juegos;

import java.util.List;

public class Prueba {
    static void contiene(String texto, String parte) {
        if (!texto.contains(parte)) throw new AssertionError("el panorama no tiene \"" + parte + "\":\n" + texto);
    }
    public static void main(String[] a) {
        ServicioJuegos s = new ServicioJuegos(List.of(
                new JuegoMesa("J1", "Catan", 1995, 3, 4, 90, 7.0, 2.0, "Estrategia"),
                new JuegoCooperativo("J2", "Pandemic", 2008, 2, 4, 45, 8.0, 2.0, "Cooperativo", 6)));
        String p = s.panorama();
        contiene(p, String.format("%.2f", 33.0));
        contiene(p, "COOPERATIVO=1");
        contiene(p, "NORMAL=1");
        System.out.println("OK");
    }
}
