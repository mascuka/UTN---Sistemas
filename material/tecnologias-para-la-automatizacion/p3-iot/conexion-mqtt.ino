#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid        = "TuWiFi";
const char* password    = "TuContraseña";
const char* mqtt_server = "192.168.1.50"; // IP de tu PC

WiFiClient espClient;
PubSubClient client(espClient);

void callback(char* topic, byte* message, unsigned int length) {
  String msg = "";
  for (int i = 0; i < length; i++) msg += (char)message[i];
  Serial.println("Gaspar dice: " + msg);
}

void setup_wifi() {
  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("Daniel")) {
      Serial.println("Daniel conectado al broker!");
      client.subscribe("gaspar/saludo"); // Daniel escucha a Gaspar
    } else {
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  static unsigned long lastMsg = 0;
  if (millis() - lastMsg > 5000) {
    lastMsg = millis();
    client.publish("daniel/saludo", "Hola Gaspar, soy Daniel!");
    Serial.println("Daniel: mensaje enviado!");
  }
}