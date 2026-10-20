package ar.edu.backend;

public class ServidorConIngresos extends Servidor {
    private final int ingresos;

    public ServidorConIngresos(String id, String region, int indiceCarga, String estado, int ingresos) {
        super(id, region, indiceCarga, estado);

        if (ingresos < 1000 || ingresos >= 1900)
            throw new IllegalArgumentException("los ingresos estan fuera de rango");

        this.ingresos = ingresos;
    }

    public int getIngresos() {
        return ingresos;
    }

    @Override
    protected int ingresoPorHora() {
        return ingresos;
    }

}
