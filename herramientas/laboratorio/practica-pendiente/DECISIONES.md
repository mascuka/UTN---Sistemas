# Decisiones

- Herencia por ancho: VehiculoRuta.desdeCampos es la fábrica; con cinco campos crea un VehiculoRuta y con seis un VehiculoConPendiente, que extiende directamente a VehiculoRuta (se le sacó el final), guarda pendientePromedio y valida su rango (0 a 30) después de super(...).
- El índice de las filas nuevas sale de VehiculoConPendiente.calcularIndiceDesgaste (0.50, 0.30 y 0.20, truncado). Se lo pasa a un constructor protegido de VehiculoRuta para que lo verifique; el constructor público sigue exigiendo la fórmula original, como pide el test existente.
- El parser acepta cinco o seis campos bajo el encabezado nuevo y solo cinco bajo el original, y conserva el orden: ancho, descarte de EN_DEPOSITO y recién después las validaciones. Todo se guarda como VehiculoRuta, así que Flota suma, filtra y agrupa los dos tipos sin cambios.
- El main lee datos/datos-parcial.csv por defecto. Tests nuevos en VehiculoConPendienteTest; pendiente: nada.
