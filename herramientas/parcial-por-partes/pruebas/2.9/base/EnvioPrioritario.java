package ar.edu.backend.envios;

/** Envío PRIORITARIO: hasta 5000 g netos y 400 pesos más que uno normal del mismo peso. */
public class EnvioPrioritario extends Envio {
    private static final int MAXIMO_GRAMOS = 5000;
    private static final int RECARGO = 400;

    public EnvioPrioritario(String id, String zona, int gramos) {
        super(id, zona, gramos);
        if (gramos > MAXIMO_GRAMOS) {
            throw new IllegalArgumentException("prioritario de más de 5000 g: " + gramos);
        }
    }

    @Override
    public String getModalidad() { return "PRIORITARIO"; }

    @Override
    public int costo() { return super.costo() + RECARGO; }
}
