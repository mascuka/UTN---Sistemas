#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <Wire.h>

const char *WIFI_SSID = "TU_RED_WIFI";
const char *WIFI_PASSWORD = "TU_CLAVE_WIFI";
const char *THINGSPEAK_CHANNEL_ID = "1234567";  // tu número de canal
// Optional: uncomment and fill this only if the channel is made private.
// const char *THINGSPEAK_READ_API_KEY = "PASTE_READ_API_KEY_HERE";

constexpr uint8_t BUTTON_PIN = 19;  // Encoder push switch; assumed active LOW.
constexpr uint8_t OLED_SDA_PIN = 21;
constexpr uint8_t OLED_SCL_PIN = 22;
constexpr unsigned long READ_INTERVAL_MS = 16000;
constexpr unsigned long PAGE_INTERVAL_MS = 5000;
constexpr unsigned long DISPLAY_REFRESH_INTERVAL_MS = 250;
constexpr uint32_t BUTTON_DEBOUNCE_US = 200000;

Adafruit_SH1106G display(128, 64, &Wire, -1);
String fieldValues[6] = {"--", "--", "--", "--", "--", "--"};
const char *fieldLabels[6] = {
    "Aleatorio", "Temp C", "Humedad %", "Tiempo s", "PWM LED int.", "LED ext %"};

volatile uint32_t buttonPressCount = 0;
volatile uint32_t lastButtonInterruptUs = 0;
portMUX_TYPE buttonMux = portMUX_INITIALIZER_UNLOCKED;

unsigned long lastReadMs = 0;
unsigned long lastPageChangeMs = 0;
unsigned long lastDisplayMs = 0;
uint8_t currentPage = 0;
bool haveChannelData = false;
bool displayAvailable = false;

void IRAM_ATTR onButtonPressed() {
  const uint32_t nowUs = micros();
  portENTER_CRITICAL_ISR(&buttonMux);
  if (nowUs - lastButtonInterruptUs >= BUTTON_DEBOUNCE_US) {
    ++buttonPressCount;
    lastButtonInterruptUs = nowUs;
  }
  portEXIT_CRITICAL_ISR(&buttonMux);
}

uint32_t getButtonPressCount() {
  portENTER_CRITICAL(&buttonMux);
  const uint32_t count = buttonPressCount;
  portEXIT_CRITICAL(&buttonMux);
  return count;
}

bool connectToWiFi(unsigned long timeoutMs) {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.printf("Connecting to Wi-Fi: %s\n", WIFI_SSID);

  const unsigned long startedAt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startedAt < timeoutMs) {
    delay(100);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Wi-Fi connected; IP: ");
    Serial.println(WiFi.localIP());
    return true;
  }
  Serial.println("Wi-Fi connection timed out; will retry in loop");
  return false;
}

bool parseChannelResponse(const String &payload) {
  DynamicJsonDocument doc(1024);
  const DeserializationError error = deserializeJson(doc, payload);
  if (error) {
    Serial.printf("ThingSpeak JSON error: %s\n", error.c_str());
    return false;
  }

  const char *keys[6] = {"field1", "field2", "field3", "field4", "field5", "field6"};
  for (uint8_t i = 0; i < 6; ++i) {
    if (doc[keys[i]].isNull()) {
      Serial.printf("ThingSpeak response has no %s value\n", keys[i]);
      return false;
    }
  }

  for (uint8_t i = 0; i < 6; ++i) {
    fieldValues[i] = doc[keys[i]].as<String>();
  }
  haveChannelData = true;
  return true;
}

void readThingSpeak() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Cannot read ThingSpeak: Wi-Fi is disconnected");
    WiFi.reconnect();
    return;
  }

  HTTPClient http;
  String url = String("http://api.thingspeak.com/channels/") +
               THINGSPEAK_CHANNEL_ID + "/feeds/last.json";
  // If the channel becomes private, uncomment the read-key declaration above and:
  // url += String("?api_key=") + THINGSPEAK_READ_API_KEY;

  http.setTimeout(5000);
  if (!http.begin(url)) {
    Serial.println("Could not start ThingSpeak HTTP request");
    return;
  }

  const int httpCode = http.GET();
  if (httpCode == HTTP_CODE_OK) {
    const String payload = http.getString();
    if (parseChannelResponse(payload)) {
      Serial.println("Latest six ThingSpeak fields updated");
    }
  } else {
    Serial.printf("ThingSpeak HTTP error: %d\n", httpCode);
  }
  http.end();
}

void drawCurrentPage() {
  if (!displayAvailable) {
    return;
  }

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("TPA G1 - IoT ESP32");
  display.println(currentPage == 0 ? "Pagina 1/2" : "Pagina 2/2");

  const uint8_t firstField = currentPage * 3;
  for (uint8_t i = firstField; i < firstField + 3; ++i) {
    display.printf("%s: %s\n", fieldLabels[i],
                   haveChannelData ? fieldValues[i].c_str() : "waiting");
  }
  display.println("Pulsaciones:");
  display.println(static_cast<unsigned long>(getButtonPressCount()));
  display.display();
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), onButtonPressed, FALLING);

  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
  displayAvailable = display.begin(0x3C, true);
  if (!displayAvailable) {
    Serial.println("OLED unavailable; continuing without display");
  } else {
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    drawCurrentPage();
  }

  connectToWiFi(15000);
  readThingSpeak();
  lastReadMs = millis();
  lastPageChangeMs = millis();
}

void loop() {
  const unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED) {
    static unsigned long lastReconnectMs = 0;
    if (now - lastReconnectMs >= 10000) {
      WiFi.reconnect();
      lastReconnectMs = now;
    }
  }

  if (now - lastReadMs >= READ_INTERVAL_MS) {
    readThingSpeak();
    lastReadMs = millis();
  }
  if (now - lastPageChangeMs >= PAGE_INTERVAL_MS) {
    currentPage = (currentPage + 1) % 2;
    lastPageChangeMs = now;
  }
  if (now - lastDisplayMs >= DISPLAY_REFRESH_INTERVAL_MS) {
    drawCurrentPage();
    lastDisplayMs = now;
  }
  delay(20);
}
