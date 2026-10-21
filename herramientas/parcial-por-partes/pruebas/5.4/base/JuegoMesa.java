package ar.edu.backend.juegos;

import java.util.Objects;

public class JuegoMesa {
    private final String id;
    private final String nombre;
    private final int anio;
    private final int minJugadores;
    private final int maxJugadores;
    private final int duracion;
    private final double rating;
    private final double peso;
    private final String categoria;

    public JuegoMesa(String id, String nombre, int anio, int minJugadores, int maxJugadores, int duracion, double rating, double peso, String categoria) {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("ID no puede ser vacío");
        if (nombre == null || nombre.isBlank()) throw new IllegalArgumentException("Nombre no puede ser vacío");
        if (anio < 1900 || anio > 2026) throw new IllegalArgumentException("Año inválido");
        if (minJugadores < 1) throw new IllegalArgumentException("Mínimo de jugadores debe ser al menos 1");
        if (maxJugadores < minJugadores) throw new IllegalArgumentException("Máximo de jugadores no puede ser menor al mínimo");
        if (rating < 0 || rating > 10) throw new IllegalArgumentException("Rating debe estar entre 0 y 10");
        if (peso < 1 || peso > 5) throw new IllegalArgumentException("Peso debe estar entre 1 y 5");

        this.id = id;
        this.nombre = nombre;
        this.anio = anio;
        this.minJugadores = minJugadores;
        this.maxJugadores = maxJugadores;
        this.duracion = duracion;
        this.rating = rating;
        this.peso = peso;
        this.categoria = categoria;
    }

    public static JuegoMesa desdeCampos(String[] campos) {
        if (campos.length < 9) throw new IllegalArgumentException("Faltan campos");
        
        String id = campos[0].trim();
        String nombre = campos[1].trim();
        int anio = Integer.parseInt(campos[2].trim());
        int minJug = Integer.parseInt(campos[3].trim());
        int maxJug = Integer.parseInt(campos[4].trim());
        int duracion = Integer.parseInt(campos[5].trim());
        double rating = Double.parseDouble(campos[6].trim());
        double peso = Double.parseDouble(campos[7].trim());
        String categoria = campos[8].trim();

        if (campos.length == 10 && !campos[9].trim().isEmpty()) {
            int dificultad = Integer.parseInt(campos[9].trim());
            if (dificultad < 1 || dificultad > 10) throw new IllegalArgumentException("Dificultad fuera de rango");
            return new JuegoCooperativo(id, nombre, anio, minJug, maxJug, duracion, rating, peso, categoria, dificultad);
        }
        return new JuegoMesa(id, nombre, anio, minJug, maxJug, duracion, rating, peso, categoria);
    }

    public double getPuntuacionAjustada() {
        return rating * peso;
    }

    public String getTipo() {
        return "Normal";
    }

    public String getId() { return id; }
    public String getNombre() { return nombre; }
    public int getAnio() { return anio; }
    public int getMinJugadores() { return minJugadores; }
    public int getMaxJugadores() { return maxJugadores; }
    public int getDuracion() { return duracion; }
    public double getRating() { return rating; }
    public double getPeso() { return peso; }
    public String getCategoria() { return categoria; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        JuegoMesa juegoMesa = (JuegoMesa) o;
        return Objects.equals(id, juegoMesa.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return String.format("%s (%d) - Rating: %.2f, Peso: %.2f, Ajustada: %.2f", 
                nombre, anio, rating, peso, getPuntuacionAjustada());
    }
}
