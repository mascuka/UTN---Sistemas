package ar.edu.backend.envios;

public class Envio {
    private final String id;
    private final String zona;
    private final int gramos;

    public Envio(String id, String zona, int gramos) {
        if (id == null || id.isBlank() || zona == null || zona.isBlank()) {
            throw new IllegalArgumentException("id y zona obligatorios");
        }
        if (gramos <= 0 || gramos > 30000) {
            throw new IllegalArgumentException("gramos fuera de rango: " + gramos);
        }
        this.id = id.strip();
        this.zona = zona.strip();
        this.gramos = gramos;
    }

    public static Envio desdeCampos(String[] c) {
        if (c.length != 5 && c.length != 6) throw new IllegalArgumentException("se esperan 5 o 6 columnas");
        int bruto = Integer.parseInt(c[2]);
        int embalaje = Integer.parseInt(c[3]);
        if (bruto <= 0 || bruto > 50000 || embalaje < 0 || embalaje >= bruto) {
            throw new IllegalArgumentException("pesos incompatibles: " + c[2] + "/" + c[3]);
        }
        String modalidad = c.length == 6 ? c[5].strip() : "NORMAL";
        return switch (modalidad) {
            case "NORMAL" -> new Envio(c[0], c[1], bruto - embalaje);
            case "PRIORITARIO" -> new EnvioPrioritario(c[0], c[1], bruto - embalaje);
            default -> throw new IllegalArgumentException("modalidad desconocida: " + modalidad);
        };
    }

    public String getId() { return id; }
    public String getZona() { return zona; }
    public int getGramos() { return gramos; }
    public String getModalidad() { return "NORMAL"; }
    public int costo() { return 500 + 200 * ((gramos + 999) / 1000); }
}
