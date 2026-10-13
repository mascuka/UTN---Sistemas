package ar.edu.backend;

public class Servidor {
    private final String id;
    private final String region;
    private final int indiceCarga;

    private static final int INGRESO_PROMEDIO = 1000;

    public Servidor(String id, String region, int indiceCarga) {

        if (id == null || id.isBlank() || region == null || region.isBlank())
            throw new IllegalArgumentException("El id y la region son obligatorios");

        if (indiceCarga < 1 || indiceCarga > 70)
            throw new IllegalArgumentException("El indice de carga es un valor fuera del rango permitido");

        this.id = id;
        this.region = region;
        this.indiceCarga = indiceCarga;
    }

    public static Servidor desdeCampos(String[] tokens) {
        if (tokens.length != 5)
            throw new IllegalArgumentException("se esperan 5 columnas");

        int usoCpu = Integer.parseInt(tokens[2]);
        int usoMemoria = Integer.parseInt(tokens[3]);

        if (usoCpu < 1 || usoCpu > 100)
            throw new IllegalArgumentException("uso del cpu esta fuera de rango");

        if (usoMemoria < 1 || usoMemoria > 24576)
            throw new IllegalArgumentException("uso de memoria esta fuera de rango");

        int indiceCarga = (int) ((usoCpu * 0.7) + (usoMemoria * 0.3));

        return new Servidor(tokens[0], tokens[1], indiceCarga);
    }

    public String getId() {
        return id;
    }

    public String getRegion() {
        return region;
    }

    public int getIndiceCarga() {
        return indiceCarga;
    }

    public int costoRiesgoOperativo() {
        int v = (INGRESO_PROMEDIO * this.indiceCarga) / 100;
        return v;
    }

}
