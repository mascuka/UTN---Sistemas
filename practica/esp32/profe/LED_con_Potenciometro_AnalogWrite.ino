
const int potePin = 32;  //Pin del potenciometro
volatile int estadoPote;

void setup(){
  Serial.begin(115200);
  pinMode(potePin, INPUT);
  pinMode(2, OUTPUT);  
  analogWriteResolution(LED_BUILTIN, 12);
  analogReadResolution(10);
  //analogWriteResolution(2, 10);
}

void loop(){
  estadoPote = analogRead(potePin);
  analogWrite(2, estadoPote);
//  analogWrite(2, map(analogRead(potePin),0 ,4095, 255, 0));
  Serial.println(estadoPote);
  delay(100);
}



//    VER RESOLUCION











//  analogWrite(LED_BUILTIN, map(analogRead(potePin),0 ,4095, 255, 0));
