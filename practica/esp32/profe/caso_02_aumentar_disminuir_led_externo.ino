const int LED1 = 23;
void setup(){
pinMode(LED1, OUTPUT);
}
void loop(){
// aumenta el brillo
for(int ciclo = 0; ciclo <= 255; ciclo++){
analogWrite(LED1, ciclo);
delay(5);
}
// disminuye el brillo
for(int ciclo = 255; ciclo >= 0; ciclo--){
analogWrite(LED1, ciclo);
delay(5);
}
delay(1000);
}
