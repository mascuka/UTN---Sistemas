const int LED1 = 23;
const int touchMas = 13;
const int touchMenos = 4;
const int maximo = 255;
const int minimo = 0;
int estadoLed = 0;
volatile bool touchDetectado1 = false;
volatile bool touchDetectado2 = false;
void IRAM_ATTR handleTouch1() {
  touchDetectado1 = true;
}
void IRAM_ATTR handleTouch2() {
  touchDetectado2 = true;
}
void setup() {
  Serial.begin(115200);
  delay(1000);
  pinMode(LED1, OUTPUT);
  // Umbrales determinados experimentalmente
  touchAttachInterrupt(touchMas, handleTouch1, 950);
  touchAttachInterrupt(touchMenos, handleTouch2, 850);
}
void loop() {
  if (touchDetectado1) {
    estadoLed += 50;
    estadoLed = min(estadoLed, maximo);
    touchDetectado1 = false;
  }
  else if (touchDetectado2) {
    estadoLed -= 50;
    estadoLed = max(estadoLed, minimo);
 
    touchDetectado2 = false;
  }
  analogWrite(LED1, estadoLed);
  Serial.printf(
    "PWM:%d   Touch(+):%d   Touch(-):%d\n",
    estadoLed,
    touchRead(touchMas),
    touchRead(touchMenos)
  );
  delay(100);
}

