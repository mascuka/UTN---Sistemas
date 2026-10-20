package utnfc.backend.parcial;

public class Consumo {
    private final String id;
    private final String rubro;
    private final int centavos;

    public Consumo(String id, String rubro, int importe, int bonificacion) {
        if (id == null || id.isBlank() || rubro == null || rubro.isBlank()) {
            throw new IllegalArgumentException("id y rubro obligatorios");
        }
        if (importe <= 0 || importe > 5_000_000 || bonificacion < 0 || bonificacion >= importe) {
            throw new IllegalArgumentException("montos incompatibles: " + importe + "/" + bonificacion);
        }
        int neto = importe - bonificacion;
        if (neto > 3_000_000) {
            throw new IllegalArgumentException("centavos fuera de rango: " + neto);
        }
        this.id = id.strip();
        this.rubro = rubro.strip();
        this.centavos = neto;
    }

    public static Consumo desdeCampos(String[] c) {
        if (c.length != 5 && c.length != 6) throw new IllegalArgumentException("se esperan 5 o 6 columnas");
        int importe = Integer.parseInt(c[2]);
        int bonificacion = Integer.parseInt(c[3]);
        if (c.length == 5) return new Consumo(c[0], c[1], importe, bonificacion);
        int dias = Integer.parseInt(c[5]);
        if (dias == 0) return new Consumo(c[0], c[1], importe, bonificacion);
        return new ConsumoAsegurado(c[0], c[1], importe, bonificacion, dias);
    }

    public String getId() { return id; }
    public String getRubro() { return rubro; }
    public int getCentavos() { return centavos; }
    public String modalidad() { return "SIN_SEGURO"; }
    public int comision() { return centavos * 2 / 100; }

    @Override public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Consumo c = (Consumo) o;
        return centavos == c.centavos && id.equals(c.id) && rubro.equals(c.rubro);
    }
    @Override public int hashCode() { return java.util.Objects.hash(id, rubro, centavos); }
    @Override public String toString() {
        return "%s %s %d %d".formatted(id, rubro, centavos, comision());
    }
}
