/******************************************************
 * ESP32 #2 - SUBSCRIBER + THINGSPEAK
 * Recibe datos MQTT y los guarda en ThingSpeak
 ******************************************************/

#include <WiFi.h>
#include <PubSubClient.h>
#include <HTTPClient.h>

// ================= CONFIGURACIÓN =================

// WiFi
const char* ssid = "TU_RED_WIFI";
const char* password = "";

// Broker MQTT (PC)
const char* mqtt_server = "192.168.0.10";  // 🔴 CAMBIAR

// Topic
const char* topic1 = "curso/iot/temperatura";
const char* topic2 = "curso/iot/humedad";


// ThingSpeak
String apiKey = "TU_API_KEY";  // 🔴 CAMBIAR
String server = "http://api.thingspeak.com/update";

// Clientes
WiFiClient espClient;
PubSubClient client(espClient);

// ================= FUNCIONES =================

// Conectar WiFi
void conectarWiFi() {
  Serial.print("Conectando a WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
}

// Callback: se ejecuta cuando llega un mensaje MQTT
void callback(char* topicRecibido, byte* payload, unsigned int length) {

  String mensaje = "";

  // Convertir payload a String
  for (int i = 0; i < length; i++) {
    mensaje += (char)payload[i];
  }

  Serial.print("Dato recibido: ");
  Serial.println(mensaje);

  // ================= ENVIAR A THINGSPEAK =================

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;

    // Construir URL
    ///
    String campo;
    if (strcmp(topicRecibido, "curso/iot/temperatura") == 0) {
        Serial.println("Mensaje recibido de TEMPERATURA");
        campo = "&field2=";
    }
    
    if (strcmp(topicRecibido, "curso/iot/humedad") == 0) {
        Serial.println("Mensaje recibido de HUMEDAD");
        campo = "&field3=";
    }
    ///
    String url = server + "?api_key=" + apiKey + campo + mensaje;

///    String url = server + "?api_key=" + apiKey + "&field2=" + mensaje;

    http.begin(url);

    int httpCode = http.GET();

    Serial.print("Código HTTP: ");
    Serial.println(httpCode);

    http.end();
  }
}

// Reconectar MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando a MQTT...");

    if (client.connect("ESP32_sub_01")) {
      Serial.println("Conectado");

      // Suscribirse al topic
      client.subscribe(topic1);
      client.subscribe(topic2);
      
    } else {
      Serial.print("Error: ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

// ================= SETUP =================

void setup() {
  Serial.begin(115200);

  conectarWiFi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

// ================= LOOP =================

void loop() {

  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  // ⚠️ No usar delay largo (afecta MQTT)
}