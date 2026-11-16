package ar.edu.backend;

/** Fila del formato nuevo: la facturación del flete viene en la 6.ª columna (de 2000 inclusive a 3800 exclusive). */
public class VehiculoConFacturacion extends VehiculoRuta {
    private final int facturacion;

    public VehiculoConFacturacion(
            String patente,
            String zona,
            int velocidadPromedio,
            int cargaToneladas,
            String estado,
            int indiceDesgaste,
            int facturacion) {
        super(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste);
        if (facturacion < 2000 || facturacion >= 3800) {
            throw new IllegalArgumentException("La facturación debe ser de 2000 a menos de 3800 USD");
        }
        this.facturacion = facturacion;
    }

    public int getFacturacion() {
        return facturacion;
    }

    @Override
    protected int getFacturacionPorFlete() {
        return facturacion;
    }
}
