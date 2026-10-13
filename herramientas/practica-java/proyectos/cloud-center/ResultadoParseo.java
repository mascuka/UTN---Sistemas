package ar.edu.backend;

import java.util.List;

public class ResultadoParseo {
    private final List<Servidor> servidores;
    private final int leidas;
    private final int descartadas;
    private final List<String> errores;
    private final List<String> descartes;

    public ResultadoParseo(List<Servidor> servidores, int leidas, int descartadas, List<String> errores,
            List<String> descartes) {
        this.servidores = List.copyOf(servidores);
        this.leidas = leidas;
        this.descartadas = descartadas;
        this.errores = List.copyOf(errores);
        this.descartes = List.copyOf(descartes);
    }

    public List<Servidor> getServidores() {
        return servidores;
    }

    public int getLeidas() {
        return leidas;
    }

    public int getDescartadas() {
        return descartadas;
    }

    public List<String> getErrores() {
        return errores;
    }

    public List<String> getDescartes() {
        return descartes;
    }

    public int getProcesadas() {
        return servidores.size();
    }

    public int getInvalidas() {
        return errores.size();
    }

    public String informe() {
        return "Leídas: %d | procesadas: %d | descartadas: %d | inválidas: %d | objetos: %d"
                .formatted(leidas, getProcesadas(), descartadas, getInvalidas(), servidores.size());
    }

}
