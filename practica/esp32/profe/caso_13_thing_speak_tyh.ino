#include "ThingSpeak.h"
#include "WiFi.h"
#include "DHT.h"


#define pin2 33       //Pin del DHT22.


//Credenciales red Wifi
const char *ssid = "TU_RED_WIFI";   //Colocar nombre de la red
const char *password = ""; //Password de la red


//unsigned long channelID = 0000000;                //ID de vuestro canal.
//const char* WriteAPIKey = "TU_API_KEY";     //Write API Key de vuestro canal.
unsigned long channelID = 0000000;                //ID de vuestro canal.
const char* WriteAPIKey = "TU_API_KEY"; 


WiFiClient cliente;


DHT dht2(pin2, DHT22);    //El sensor de T y H blanco.


//Adafruit_BMP085 bmp;


void setup() {
  Serial.begin(115200);
  Serial.println("Test de sensores:");


  WiFi.begin(ssid,password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Wifi conectado!");


  ThingSpeak.begin(cliente);


  dht2.begin();


}


void loop() {


  delay(2000);
  leerdht2();


  ThingSpeak.writeFields(channelID,WriteAPIKey);
  Serial.println("Datos enviados a ThingSpeak!");
  delay(14000);
}


void leerdht2() {
  
  float t2 = dht2.readTemperature();
  float h2 = dht2.readHumidity();


  while (isnan(t2) || isnan(h2)){
    Serial.println("Lectura fallida en el sensor DHT22, repitiendo lectura...");
    delay(2000);
    t2 = dht2.readTemperature();
    h2 = dht2.readHumidity();
  }


  Serial.print("Temperatura DHT22: ");
  Serial.print(t2);
  Serial.println(" ºC.");


  Serial.print("Humedad DHT22: ");
  Serial.print(h2);
  Serial.println(" %."); 


  Serial.println("-----------------------");


  ThingSpeak.setField (1,t2);
  ThingSpeak.setField (2,h2);
}



