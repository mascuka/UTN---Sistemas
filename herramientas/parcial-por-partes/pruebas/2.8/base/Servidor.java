package ar.edu.backend;

public class Servidor {
    private final String id;
    private final String region;
    private final int indiceCarga;
    private final String estado;

    private static final int INGRESO_PROMEDIO = 1000;

    public Servidor(String id, String region, int indiceCarga) {
        this(id, region, indiceCarga, "SIN ESTADO");
    }

    public Servidor(String id, String region, int indiceCarga, String estado) {

        if (id == null || id.isBlank() || region == null || region.isBlank())
            throw new IllegalArgumentException("El id y la region son obligatorios");

        if (indiceCarga < 1 || indiceCarga > 70)
            throw new IllegalArgumentException("El indice de carga es un valor fuera del rango permitido");

        this.id = id;
        this.region = region;
        this.indiceCarga = indiceCarga;
        this.estado = estado;
    }

    public static Servidor desdeCampos(String[] tokens) {
        if (tokens.length != 5 && tokens.length != 6)
            throw new IllegalArgumentException("se esperan 5 o 6 columnas");

        int usoCpu = Integer.parseInt(tokens[2]);
        int usoMemoria = Integer.parseInt(tokens[3]);

        if (usoCpu < 1 || usoCpu > 100)
            throw new IllegalArgumentException("uso del cpu esta fuera de rango");

        if (usoMemoria < 1 || usoMemoria > 24576)
            throw new IllegalArgumentException("uso de memoria esta fuera de rango");

        int indiceCarga = (int) ((usoCpu * 0.7) + (usoMemoria * 0.3));

        if (tokens.length == 6)
            return new ServidorConIngresos(tokens[0], tokens[1], indiceCarga, tokens[4], Integer.parseInt(tokens[5]));

        return new Servidor(tokens[0], tokens[1], indiceCarga, tokens[4]);
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

    public String getEstado() {
        return estado;
    }

    /**
     * Ingreso por hora que se usa para el costo. La subclase ServidorConIngresos lo
     * redefine con el valor leido del archivo.
     */
    protected int ingresoPorHora() {
        return INGRESO_PROMEDIO;
    }

    public int costoRiesgoOperativo() {
        int v = (this.ingresoPorHora() * this.indiceCarga) / 100;
        return v;
    }

}
