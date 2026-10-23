#include <Adafruit_SH110X.h>
#include <Wire.h>

const int ledpin = 23;
const int potePin = 32;  //Pin del potenciometro
volatile int estadoPote;
volatile int entradaPin;
volatile int limite = 2000;
Adafruit_SH1106G display = Adafruit_SH1106G(128, 64, &Wire, -1);
void setup(){
  Serial.begin(115200);
  pinMode(potePin, INPUT);
  pinMode(ledpin, OUTPUT);  
  pinMode(4,OUTPUT); // pin 4 rele
  //analogWriteResolution(12);
  //analogReadResolution(12);

 //Inicializar pantalla OLED
  display.begin(0x3c, true); //Dirección por defecto: 0x3C
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
}


void loop(){
  estadoPote=analogRead(potePin);
    if (estadoPote > limite) {
    digitalWrite(ledpin, HIGH);
    display.clearDisplay();  
    display.setCursor(0,0);
    display.print("LED ENCENDIDO");
    display.display();
  } else {
    digitalWrite(ledpin, LOW);
    display.clearDisplay();  
    display.setCursor(0,0);
    display.print("LED APAGADO");
    display.display();
  }
}


