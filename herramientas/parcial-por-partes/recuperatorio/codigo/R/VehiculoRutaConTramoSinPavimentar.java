package ar.edu.backend;

public class VehiculoRutaConTramoSinPavimentar extends VehiculoRuta {
    private final int porcentajeRutaSinPAvimentar;

    public VehiculoRutaConTramoSinPavimentar(
            String patente,
            String zona,
            int velocidadPromedio,
            int cargaToneladas,
            String estado,
            int indiceDesgaste,
            int porcentajeRutaSinPAvimentar) {
        super(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste,
                calcularIndiceDesgaste(velocidadPromedio, cargaToneladas, porcentajeRutaSinPAvimentar));
        if (porcentajeRutaSinPAvimentar < 0 || porcentajeRutaSinPAvimentar > 100) {
            throw new IllegalArgumentException("El campo porcentajeRutaSinPAvimentar debe ser mayor o igual a 0 y menor o igual a 100");
        }
        this.porcentajeRutaSinPAvimentar = porcentajeRutaSinPAvimentar;
    }

    static int calcularIndiceDesgaste(int velocidadPromedio, int cargaToneladas, int porcentajeRutaSinPAvimentar) {
        return (int) (velocidadPromedio * 0.55 + cargaToneladas * 0.30 + porcentajeRutaSinPAvimentar * 0.15);
    }

    public int getPorcentajeRutaSinPAvimentar() {
        return porcentajeRutaSinPAvimentar;
    }
}
