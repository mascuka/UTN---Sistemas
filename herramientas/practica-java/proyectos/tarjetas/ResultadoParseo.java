package utnfc.backend.parcial;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public final class ResultadoParseo {
    private final List<Consumo> consumos;
    private final int leidas;
    private final Map<Integer, String> errores;
    private final Map<Integer, String> descartes;

    public ResultadoParseo(List<Consumo> consumos, int leidas,
                           Map<Integer, String> errores, Map<Integer, String> descartes) {
        this.consumos = List.copyOf(consumos);
        this.leidas = leidas;
        this.errores = Collections.unmodifiableMap(new TreeMap<>(errores));
        this.descartes = Collections.unmodifiableMap(new TreeMap<>(descartes));
    }
    public List<Consumo> getConsumos() { return consumos; }
    public int getLeidas() { return leidas; }
    public int getDescartadas() { return descartes.size(); }
    public Map<Integer, String> getErrores() { return errores; }
    public Map<Integer, String> getDescartes() { return descartes; }
    public int getProcesadas() { return consumos.size(); }
    public int getInvalidas() { return errores.size(); }
    @Override public String toString() {
        return "Leídas: %d | procesadas: %d | descartadas: %d | inválidas: %d | objetos: %d"
                .formatted(leidas, getProcesadas(), getDescartadas(), getInvalidas(), consumos.size());
    }
}
