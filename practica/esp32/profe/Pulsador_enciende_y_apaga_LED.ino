
const int pinBoton = 19; // Pin del pulsador
int estadoLed = LOW; // Estado del LED
int ultimoEstado = HIGH; // Estado anterior del pulsador

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Configurar el pin del LED INTEGRADO como salida
  pinMode(pinBoton, INPUT_PULLUP); // Configurar el pin del pulsador como entrada
  Serial.begin(115200);
}

void loop() {
  // Toma la lectura del pulsador
  int lectura = digitalRead(pinBoton);
  // Si el pulsador ha sido presionado...
  if (lectura != ultimoEstado) {

    // Si el pulsador ha sido presionado (?), cambia el estado del LED
    if (lectura == HIGH) {
      estadoLed = !estadoLed;
      digitalWrite(LED_BUILTIN, estadoLed);
    }
  }
  
  Serial.printf("Pulsador:  %u  \n", lectura);

  // Guardar el último estado del pulsador
  ultimoEstado = lectura;
  delay(50);
}
