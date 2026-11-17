# Decisiones

- La columna acoplado vive en VehiculoRuta (atributo, getter y validación de 0 a 20 en el dominio); el constructor de seis parámetros delega con this(..., 0), así los tests de siempre siguen andando, y desdeCampos lee el sexto campo solo si la fila lo trae.
- Herencia: VehiculoConAcoplado extiende VehiculoRuta (se le sacó el final). desdeCampos la crea cuando el acoplado es mayor a 0; valida el tope de 90 km/h después de super(...) y redefine getCostoDesgasteOperativo() sumando 40 USD por tonelada al costo común.
- El parser elige separador y ancho según el encabezado y conserva el orden: ancho, descarte de EN_DEPOSITO y recién después las validaciones.
- El conteo por modalidad usa getTipo(), que la subclase redefine (sin instanceof); el main lee datos/datos-parcial.csv por defecto y solo delega. Pendiente: nada.
