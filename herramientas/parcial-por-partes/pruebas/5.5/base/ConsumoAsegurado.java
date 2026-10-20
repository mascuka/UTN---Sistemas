package utnfc.backend.parcial;

public class ConsumoAsegurado extends Consumo {
    private final int diasCobertura;

    public ConsumoAsegurado(String id, String rubro, int importe, int bonificacion, int diasCobertura) {
        super(id, rubro, importe, bonificacion);
        if (diasCobertura != 30 && diasCobertura != 90 && diasCobertura != 180) {
            throw new IllegalArgumentException("plazo de cobertura inválido: " + diasCobertura);
        }
        if (getCentavos() > 500_000) {
            throw new IllegalArgumentException("asegurado supera 500000 centavos: " + getCentavos());
        }
        this.diasCobertura = diasCobertura;
    }

    public int getDiasCobertura() { return diasCobertura; }
    @Override public String modalidad() { return "ASEGURADO"; }
    @Override public int comision() { return super.comision() + 200 * (diasCobertura / 30); }
    @Override public boolean equals(Object o) {
        return super.equals(o) && diasCobertura == ((ConsumoAsegurado) o).diasCobertura;
    }
    @Override public int hashCode() { return java.util.Objects.hash(super.hashCode(), diasCobertura); }
}
