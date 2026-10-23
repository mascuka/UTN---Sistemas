const int potePin = 32;  //Pin del potenciometro
const int relayPin = 14;  //Pin del relay
volatile int estadoPote;
volatile int entradaPin;
volatile int limite = 2000;


void setup(){
  Serial.begin(115200);
  pinMode(potePin, INPUT);
  
  pinMode(relayPin,OUTPUT);
 analogWriteResolution(14,12); 
 analogReadResolution(12); 
}


void loop(){
  estadoPote=analogRead(potePin);
  if (estadoPote > limite) {
    digitalWrite(relayPin, HIGH);
  } else {
    digitalWrite(relayPin, LOW);
  }


  Serial.println(estadoPote);


  delay(100);
}

