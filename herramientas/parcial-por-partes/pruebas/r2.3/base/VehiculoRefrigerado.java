package ar.edu.backend;

/** Carga REFRIGERADA: las mismas validaciones, como máximo 30 toneladas y 300 USD más que una general. */
public class VehiculoRefrigerado extends VehiculoRuta {
    private static final int CARGA_MAXIMA = 30;
    private static final int RECARGO = 300;

    public VehiculoRefrigerado(
            String patente,
            String zona,
            int velocidadPromedio,
            int cargaToneladas,
            String estado,
            int indiceDesgaste) {
        super(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste);
        if (cargaToneladas > CARGA_MAXIMA) {
            throw new IllegalArgumentException("Una carga refrigerada no puede superar las 30 toneladas");
        }
    }

    @Override
    public int getCostoDesgasteOperativo() {
        return super.getCostoDesgasteOperativo() + RECARGO;
    }

    @Override
    public String getTipoCarga() {
        return "REFRIGERADA";
    }
}
