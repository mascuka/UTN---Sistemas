const int potePin = 32; //Pin del potenciometro
volatile int estadoPote;
void setup(){
Serial.begin(115200);
delay(1000);
Serial.println();
Serial.println("Lecturas de Potenciometro");
pinMode(potePin, INPUT);
}
void loop(){
estadoPote=analogRead(potePin);
Serial.println(estadoPote);
delay(100);
}
