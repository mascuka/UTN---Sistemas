const int LED_INT = 2;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("Hello, ESP32!");
  pinMode(LED_INT, OUTPUT);
}

void loop() {
  digitalWrite(LED_INT, HIGH);
  delay(1000); // this speeds up the simulation
  digitalWrite(LED_INT, LOW);
  delay(1000); // this speeds up the simulation
}
