package ar.edu.backend.juegos;

public class JuegoCooperativo extends JuegoMesa {
    private final int dificultad;

    public JuegoCooperativo(String id, String nombre, int anio, int minJugadores, int maxJugadores, int duracion,
            double rating, double peso, String categoria, int dificultad) {
        super(id, nombre, anio, minJugadores, maxJugadores, duracion, rating, peso, categoria);
        this.dificultad = dificultad;
    }

    @Override
    public double getPuntuacionAjustada() {
        return super.getPuntuacionAjustada() + dificultad / 2.0;
    }

    @Override
    public String getTipo() {
        return "Cooperativo";
    }

    public int getDificultadCooperativa() {
        return dificultad;
    }
}
