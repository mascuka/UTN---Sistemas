/******************************************************
 * ESP32 #1 - PUBLICADOR MQTT
 * Publica datos a broker Mosquitto (PC)
 ******************************************************/

#include <WiFi.h>
#include <PubSubClient.h>

// ================= CONFIGURACIÓN =================

// WiFi
const char* ssid = "TU_RED_WIFI";
const char* password = "";

// IP del broker (PC con Mosquitto)
const char* mqtt_server = "192.168.0.14";  // 🔴 CAMBIAR por tu IP

// Topic
const char* topic = "curso/iot/temperatura";

// Clientes
WiFiClient espClient;
PubSubClient client(espClient);

// ================= FUNCIONES =================

// Conectar a WiFi
void conectarWiFi() {
  Serial.print("Conectando a WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// Reconectar a MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando a MQTT...");

    // IMPORTANTE: clientID único
    if (client.connect("ESP32_pub_01")) {
      Serial.println("Conectado al broker");
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

  // Configurar broker MQTT
  client.setServer(mqtt_server, 1883);
}

// ================= LOOP =================

void loop() {

  // Mantener conexión MQTT
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // 🔹 Simular temperatura (podés reemplazar por sensor real)
  float temperatura = random(200, 300) / 10.0;

  // Convertir a string
  String mensaje = String(temperatura);

  // Publicar
  client.publish(topic, mensaje.c_str());

  Serial.print("Publicado: ");
  Serial.println(mensaje);

  delay(2000);  // cada 2 segundos
}