#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include <ArduinoOTA.h>
#include <DHT.h>
#include <ThingSpeak.h>
#include <WiFi.h>
#include <Wire.h>

// Set to 1 only in the Wokwi copy to emulate touch pads with pushbuttons on GPIO25/26.
// Keep 0 on the physical ESP32, where GPIO13/4 are capacitive touch inputs.
#define TOUCH_SIMULATION_MODE 0

// Update these placeholders locally. Do not publish the real Wi-Fi password or key.
const char *WIFI_SSID = "TU_RED_WIFI";
const char *WIFI_PASSWORD = "TU_CLAVE_WIFI";
const char *THINGSPEAK_WRITE_API_KEY = "TU_API_KEY";
const unsigned long THINGSPEAK_CHANNEL_ID = 1234567;  // tu número de canal

// Pin assignments from the course board diagram and examples.
constexpr uint8_t DHT_PIN = 33;
constexpr uint8_t POT_PIN = 32;
constexpr uint8_t INTEGRATED_LED_PIN = 2;  // Assumption from caso_1_led_interno.txt.
constexpr uint8_t EXTERNAL_LED_PIN = 23;
constexpr uint8_t TOUCH_UP_PIN = 13;
constexpr uint8_t TOUCH_DOWN_PIN = 4;
constexpr uint8_t SIM_TOUCH_UP_BUTTON_PIN = 25;
constexpr uint8_t SIM_TOUCH_DOWN_BUTTON_PIN = 26;
constexpr uint8_t OLED_SDA_PIN = 21;
constexpr uint8_t OLED_SCL_PIN = 22;

constexpr uint8_t PWM_BITS = 12;
constexpr uint16_t PWM_MAX = (1U << PWM_BITS) - 1;
constexpr uint16_t TOUCH_UP_THRESHOLD = 950;    // Starting point from the instructor's example.
constexpr uint16_t TOUCH_DOWN_THRESHOLD = 850;  // Calibrate on the physical board if needed.
constexpr uint16_t TOUCH_RELEASE_MARGIN = 100;
constexpr uint16_t EXTERNAL_LED_STEP = PWM_MAX / 20;  // 5% per touch.
constexpr unsigned long SENSOR_INTERVAL_MS = 2000;
constexpr unsigned long DISPLAY_INTERVAL_MS = 250;
constexpr unsigned long THINGSPEAK_INTERVAL_MS = 16000;
constexpr unsigned long WIFI_RETRY_INTERVAL_MS = 10000;

Adafruit_SH1106G display(128, 64, &Wire, -1);
DHT dht(DHT_PIN, DHT22);
WiFiClient thingspeakClient;

float temperatureC = NAN;
float humidityPct = NAN;
uint16_t integratedPwm = 0;
uint16_t externalPwm = 0;
bool touchUpLatched = false;
bool touchDownLatched = false;
bool displayAvailable = false;
bool otaStarted = false;

unsigned long lastSensorReadMs = 0;
unsigned long lastDisplayMs = 0;
unsigned long lastThingSpeakMs = 0;
unsigned long lastWiFiRetryMs = 0;

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  lastWiFiRetryMs = millis();
  Serial.printf("Connecting to Wi-Fi: %s\n", WIFI_SSID);
}

void startOtaWhenConnected() {
  if (WiFi.status() != WL_CONNECTED || otaStarted) {
    return;
  }

  ArduinoOTA.setHostname("ESP32_TPI4K3");
  ArduinoOTA.onStart([]() { Serial.println("OTA upload started"); });
  ArduinoOTA.onEnd([]() { Serial.println("OTA upload finished; restarting"); });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("OTA error: %u\n", static_cast<unsigned>(error));
  });
  ArduinoOTA.begin();
  otaStarted = true;
  Serial.print("OTA ready at ");
  Serial.println(WiFi.localIP());
}

void updateSensorReadings() {
  const float newTemperature = dht.readTemperature();
  const float newHumidity = dht.readHumidity();

  if (isnan(newTemperature) || isnan(newHumidity)) {
    Serial.println("DHT22 read failed; keeping the last valid reading");
    return;
  }

  temperatureC = newTemperature;
  humidityPct = newHumidity;
}

void updatePotentiometerLed() {
  const int rawPot = analogRead(POT_PIN);
  integratedPwm = static_cast<uint16_t>(map(rawPot, 0, 4095, 0, PWM_MAX));
  analogWrite(INTEGRATED_LED_PIN, integratedPwm);
}

void applyExternalLedBrightness() {
  analogWrite(EXTERNAL_LED_PIN, externalPwm);
}

void updateTouchControls() {
  bool upPressed;
  bool downPressed;
#if TOUCH_SIMULATION_MODE
  upPressed = digitalRead(SIM_TOUCH_UP_BUTTON_PIN) == LOW;
  downPressed = digitalRead(SIM_TOUCH_DOWN_BUTTON_PIN) == LOW;
#else
  const uint16_t upReading = touchRead(TOUCH_UP_PIN);
  const uint16_t downReading = touchRead(TOUCH_DOWN_PIN);
  static unsigned long lastTouchReportMs = 0;
  if (millis() - lastTouchReportMs >= 1000) {
    lastTouchReportMs = millis();
    Serial.printf("Touch GPIO13=%u GPIO4=%u (thresholds %u/%u)\n",
                  static_cast<unsigned>(upReading), static_cast<unsigned>(downReading),
                  static_cast<unsigned>(TOUCH_UP_THRESHOLD),
                  static_cast<unsigned>(TOUCH_DOWN_THRESHOLD));
  }
  // Capacitive readings normally decrease when touched; use release hysteresis.
  upPressed = touchUpLatched
                  ? upReading <= TOUCH_UP_THRESHOLD + TOUCH_RELEASE_MARGIN
                  : upReading < TOUCH_UP_THRESHOLD;
  downPressed = touchDownLatched
                    ? downReading <= TOUCH_DOWN_THRESHOLD + TOUCH_RELEASE_MARGIN
                    : downReading < TOUCH_DOWN_THRESHOLD;
#endif

  if (!touchUpLatched && upPressed) {
    externalPwm = (externalPwm > PWM_MAX - EXTERNAL_LED_STEP)
                      ? PWM_MAX
                      : externalPwm + EXTERNAL_LED_STEP;
    touchUpLatched = true;
    applyExternalLedBrightness();
  } else if (touchUpLatched && !upPressed) {
    touchUpLatched = false;
  }

  if (!touchDownLatched && downPressed) {
    externalPwm = (externalPwm > EXTERNAL_LED_STEP) ? externalPwm - EXTERNAL_LED_STEP : 0;
    touchDownLatched = true;
    applyExternalLedBrightness();
  } else if (touchDownLatched && !downPressed) {
    touchDownLatched = false;
  }

  // Touch is edge-latched; holding a pad changes brightness only once.
}

void drawStatus() {
  if (!displayAvailable) {
    return;
  }

  const uint8_t externalPercent = static_cast<uint8_t>(map(externalPwm, 0, PWM_MAX, 0, 100));
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("TPA G1 - IoT ESP32");
  display.printf("PWM LED int: %u\n", static_cast<unsigned>(integratedPwm));
  if (isnan(temperatureC) || isnan(humidityPct)) {
    display.println("DHT22: esperando");
  } else {
    display.printf("Temp: %.1f C\nHum: %.1f %%\n", temperatureC, humidityPct);
  }
  display.printf("LED ext.: %u%%\n", static_cast<unsigned>(externalPercent));
  if (WiFi.status() == WL_CONNECTED) {
    display.printf("IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    display.println("WiFi: conectando...");
  }
  display.display();
}

bool haveValidReadings() {
  return !isnan(temperatureC) && !isnan(humidityPct);
}

void sendThingSpeakUpdate() {
  if (WiFi.status() != WL_CONNECTED || !haveValidReadings()) {
    Serial.println("ThingSpeak update skipped: Wi-Fi or sensor data unavailable");
    return;
  }
  if (String(THINGSPEAK_WRITE_API_KEY) == "PASTE_WRITE_API_KEY_HERE") {
    Serial.println("Set THINGSPEAK_WRITE_API_KEY before sending real channel updates");
    return;
  }

  const long randomValue = random(100, 501);
  const unsigned long elapsedSeconds = millis() / 1000UL;
  const uint8_t externalPercent = static_cast<uint8_t>(map(externalPwm, 0, PWM_MAX, 0, 100));

  ThingSpeak.setField(1, static_cast<long>(randomValue));
  ThingSpeak.setField(2, temperatureC);
  ThingSpeak.setField(3, humidityPct);
  ThingSpeak.setField(4, static_cast<long>(elapsedSeconds));
  ThingSpeak.setField(5, static_cast<long>(integratedPwm));
  ThingSpeak.setField(6, static_cast<long>(externalPercent));

  const int response = ThingSpeak.writeFields(THINGSPEAK_CHANNEL_ID, THINGSPEAK_WRITE_API_KEY);
  Serial.printf("ThingSpeak write status: %d\n", response);
  if (response == 200) {
    Serial.println("All six fields were accepted by ThingSpeak");
  }
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(PWM_BITS);
  analogWriteResolution(INTEGRATED_LED_PIN, PWM_BITS);
  analogWriteResolution(EXTERNAL_LED_PIN, PWM_BITS);
  pinMode(POT_PIN, INPUT);
  pinMode(INTEGRATED_LED_PIN, OUTPUT);
  pinMode(EXTERNAL_LED_PIN, OUTPUT);
#if TOUCH_SIMULATION_MODE
  pinMode(SIM_TOUCH_UP_BUTTON_PIN, INPUT_PULLUP);
  pinMode(SIM_TOUCH_DOWN_BUTTON_PIN, INPUT_PULLUP);
#endif

  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
  displayAvailable = display.begin(0x3C, true);
  if (!displayAvailable) {
    Serial.println("OLED unavailable; continuing without display");
  } else {
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
  }

  dht.begin();
  ThingSpeak.begin(thingspeakClient);
  randomSeed(micros());
  connectToWiFi();

  updatePotentiometerLed();
  applyExternalLedBrightness();
  updateSensorReadings();
  drawStatus();
}

void loop() {
  const unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED && now - lastWiFiRetryMs >= WIFI_RETRY_INTERVAL_MS) {
    WiFi.reconnect();
    lastWiFiRetryMs = now;
  }
  startOtaWhenConnected();
  if (otaStarted) {
    ArduinoOTA.handle();
  }

  updatePotentiometerLed();
  updateTouchControls();

  if (now - lastSensorReadMs >= SENSOR_INTERVAL_MS) {
    lastSensorReadMs = now;
    updateSensorReadings();
  }
  if (now - lastDisplayMs >= DISPLAY_INTERVAL_MS) {
    lastDisplayMs = now;
    drawStatus();
  }
  if (now - lastThingSpeakMs >= THINGSPEAK_INTERVAL_MS) {
    lastThingSpeakMs = now;
    sendThingSpeakUpdate();
  }
}
