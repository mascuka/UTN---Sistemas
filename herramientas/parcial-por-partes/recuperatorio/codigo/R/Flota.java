package ar.edu.backend;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

public final class Flota {
    private final List<VehiculoRuta> vehiculos;

    public Flota(List<VehiculoRuta> vehiculos) {
        if (vehiculos == null) {
            throw new IllegalArgumentException("La lista de vehículos no puede ser nula");
        }
        this.vehiculos = Collections.unmodifiableList(new ArrayList<>(vehiculos));
    }

    public int sumarCostoDesgasteOperativo(Predicate<VehiculoRuta> filtro) {
        if (filtro == null) {
            throw new IllegalArgumentException("El filtro no puede ser nulo");
        }
        return vehiculos.stream()
                .filter(filtro)
                .mapToInt(VehiculoRuta::getCostoDesgasteOperativo)
                .sum();
    }

    public int getCostoTotalDesgasteOperativo() {
        return sumarCostoDesgasteOperativo(vehiculo -> true);
    }

    public Map<String, Integer> getCostoPorZona() {
        Map<String, Integer> costos = new LinkedHashMap<>();
        for (VehiculoRuta vehiculo : vehiculos) {
            costos.merge(vehiculo.getZona(), vehiculo.getCostoDesgasteOperativo(), Integer::sum);
        }
        return Collections.unmodifiableMap(costos);
    }

    public long contarConIndiceDesgasteMenorA(int limite) {
        return vehiculos.stream()
                .filter(vehiculo -> vehiculo.getIndiceDesgaste() < limite)
                .count();
    }

    public List<VehiculoRuta> getVehiculos() {
        return vehiculos;
    }

    public String panorama() {
        StringBuilder panorama = new StringBuilder()
                .append("Costo total por desgaste operativo: ")
                .append(getCostoTotalDesgasteOperativo());
        for (Map.Entry<String, Integer> entrada : getCostoPorZona().entrySet()) {
            panorama.append(System.lineSeparator())
                    .append(entrada.getKey()).append(": ").append(entrada.getValue());
        }
        panorama.append(System.lineSeparator())
                .append("Vehículos con índice de desgaste menor a 55: ")
                .append(contarConIndiceDesgasteMenorA(55));
        return panorama.toString();
    }
}
