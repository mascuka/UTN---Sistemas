package ar.edu.backend;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class Cloud {
    private final List<Servidor> servidores;

    public Cloud(List<Servidor> servidores) {
        this.servidores = List.copyOf(servidores);
    }

    public List<Servidor> filtrar(Predicate<Servidor> criterio) {
        return this.servidores.stream().filter(criterio).toList();
    }

    /**
     * Metodo que retorna el costo total del riesgo operativo por los servidores que
     * se estan procesando
     */
    public int total() {
        return this.servidores.stream().mapToInt(Servidor::costoRiesgoOperativo).sum();
    }

    /**
     * Metodo que retorna el Map donde por cada region a la que pertence el servidor
     * 
     * @return
     */
    public Map<String, Integer> totalesPorRegion() {
        return this.servidores.stream()
                .collect(Collectors.groupingBy(Servidor::getRegion,
                        Collectors.summingInt(Servidor::costoRiesgoOperativo)));
    }

    public String panorama() {
        String reporte = "Total: %d | Por Region: %s | indice menores a 50: %d";
        return reporte.formatted(this.total(), new TreeMap<>(this.totalesPorRegion()),
                this.filtrar(s -> s.getIndiceCarga() < 50).size());
    }

}
