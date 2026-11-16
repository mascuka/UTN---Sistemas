package ar.edu.backend;

/** Vehículo DEMORADO: el costo por desgaste operativo es un 15 % más alto (en enteros). */
public class VehiculoDemorado extends VehiculoRuta {
    private static final int PORCENTAJE = 115;

    public VehiculoDemorado(
            String patente,
            String zona,
            int velocidadPromedio,
            int cargaToneladas,
            String estado,
            int indiceDesgaste) {
        super(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste);
    }

    @Override
    public int getCostoDesgasteOperativo() {
        return super.getCostoDesgasteOperativo() * PORCENTAJE / 100;
    }
}
