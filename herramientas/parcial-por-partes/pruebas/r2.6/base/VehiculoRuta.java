package ar.edu.backend;

public class VehiculoRuta {
    private final String patente;
    private final String zona;
    private final int velocidadPromedio;
    private final int cargaToneladas;
    private final String estado;
    private final int indiceDesgaste;

    public VehiculoRuta(
            String patente,
            String zona,
            int velocidadPromedio,
            int cargaToneladas,
            String estado,
            int indiceDesgaste) {
        this.patente = validarTexto(patente, "La patente no puede estar vacía");
        this.zona = validarTexto(zona, "La zona no puede estar vacía");
        if (velocidadPromedio <= 0 || velocidadPromedio >= 130) {
            throw new IllegalArgumentException("La velocidad promedio debe ser mayor a 0 y menor a 130");
        }
        if (cargaToneladas > 45) {
            throw new IllegalArgumentException("La carga no puede superar las 45 toneladas");
        }
        if (!"EN_RUTA".equals(estado) && !"DEMORADO".equals(estado)) {
            throw new IllegalArgumentException("Estado de vehículo inválido: " + estado);
        }
        int indiceCalculado = calcularIndiceDesgaste(velocidadPromedio, cargaToneladas);
        if (indiceDesgaste < 1 || indiceDesgaste > 90 || indiceDesgaste != indiceCalculado) {
            throw new IllegalArgumentException("El índice de desgaste debe coincidir con el cálculo y estar entre 1 y 90");
        }
        this.velocidadPromedio = velocidadPromedio;
        this.cargaToneladas = cargaToneladas;
        this.estado = estado;
        this.indiceDesgaste = indiceDesgaste;
    }

    public static VehiculoRuta desdeCampos(String[] campos) {
        if (campos == null || (campos.length != 5 && campos.length != 6)) {
            throw new IllegalArgumentException("La fila debe tener cinco o seis columnas");
        }

        String patente = limpiar(campos[0]);
        String zona = limpiar(campos[1]);
        int velocidadPromedio = convertirEntero(campos[2], "velocidad promedio");
        int cargaToneladas = convertirEntero(campos[3], "carga en toneladas");
        String estado = limpiar(campos[4]);
        int indiceDesgaste = calcularIndiceDesgaste(velocidadPromedio, cargaToneladas);
        if (campos.length == 6) {
            int facturacion = convertirEntero(campos[5], "facturación");
            return new VehiculoConFacturacion(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste, facturacion);
        }
        return new VehiculoRuta(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste);
    }

    private static int calcularIndiceDesgaste(int velocidadPromedio, int cargaToneladas) {
        return (int) (velocidadPromedio * 0.6 + cargaToneladas * 0.4);
    }

    private static int convertirEntero(String valor, String nombreCampo) {
        try {
            return Integer.parseInt(limpiar(valor));
        } catch (NumberFormatException exception) {
            throw new IllegalArgumentException("El campo " + nombreCampo + " debe ser un entero", exception);
        }
    }

    private static String validarTexto(String valor, String mensaje) {
        String texto = limpiar(valor);
        if (texto.isEmpty()) {
            throw new IllegalArgumentException(mensaje);
        }
        return texto;
    }

    private static String limpiar(String valor) {
        if (valor == null) {
            throw new IllegalArgumentException("Los campos no pueden ser nulos");
        }
        return valor.trim();
    }

    /** El gancho: la facturación por flete que usa el costo. La subclase lo redefine con la de la fila. */
    protected int getFacturacionPorFlete() {
        return 2000;
    }

    public int getCostoDesgasteOperativo() {
        return getFacturacionPorFlete() * indiceDesgaste / 100;
    }

    public String getPatente() {
        return patente;
    }

    public String getZona() {
        return zona;
    }

    public int getVelocidadPromedio() {
        return velocidadPromedio;
    }

    public int getCargaToneladas() {
        return cargaToneladas;
    }

    public String getEstado() {
        return estado;
    }

    public int getIndiceDesgaste() {
        return indiceDesgaste;
    }
}
