# Arma practica/tpa-p3/ejercicios.json: la Práctica del 3º parcial de TPA (IoT con la ESP32).
# El parcial es de opción múltiple: los ejercicios son de C++ de la ESP32 (no se corre: se verifica la estructura con
# expresiones regulares, como en Backend), de cuentas (ADC, map, PWM, millis) y de conceptos, sacados del resumen,
# del banco de preguntas de 2025 y de los casos del profe.
# Desde la raíz:  python3 herramientas/tpa-practica/armar_p3.py  y después  node herramientas/tpa-practica/validar.js
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import *

N = lambda pregunta, valor, dec=0, unidad=None, motivo=None: {k: v for k, v in
    {'pregunta': pregunta, 'valor': valor, 'dec': dec, 'unidad': unidad, 'motivo': motivo}.items() if v is not None}
OP = lambda pregunta, opciones, valor, motivo=None: {k: v for k, v in
    {'pregunta': pregunta, 'opciones': opciones, 'valor': valor, 'motivo': motivo}.items() if v is not None}
CI = ['Correcta', 'Incorrecta']
def cuenta(regex, veces, ok, error):
    return {'tipo': 'cuenta', 'regex': regex, 'veces': veces, 'ok': ok, 'error': error}

partes = []

# ======================= 1 · La ESP32 =======================
partes.append(parte(1, 'esp32', 'La ESP32', 'La ESP32',
  'Un SoC de Espressif con WiFi y Bluetooth integrados: doble núcleo de 32 bits a 240 MHz, 3,3 V, ADC de 12 bits, 16 canales PWM y el LED integrado en el GPIO 2. Sus números salen siempre en el parcial.',
  {
    'que': 'La **ESP32** es un SoC (System on Chip) de Espressif: un microcontrolador de bajo costo y bajo consumo con **WiFi y Bluetooth integrados** («un Arduino con esteroides»). Es un **sistema embebido**: hace una tarea dedicada, normalmente en tiempo real, a diferencia de una PC.\n'
           'En el parcial se preguntan sus números (núcleos, tensión, memorias, periféricos) y para qué sirve cada cosa de la placa.',
    'consta': [
      ['El procesador', 'Xtensa LX6 de Tensilica: doble núcleo, 32 bits, hasta 240 MHz; los núcleos pueden trabajar en paralelo.'],
      ['La tensión', '3,3 V. Por USB entran 5 V y el regulador los baja; más de 3,3 V en un pin la puede dañar.'],
      ['Las memorias', 'Flash hasta 4 MB (el programa) · SRAM 520 KB (datos, volátil) · ROM 448 KB (bootloader) · EEPROM (configuraciones).'],
      ['La conectividad', 'WiFi 802.11 b/g/n en 2,4 GHz y Bluetooth 4.2 (clásico y BLE).'],
      ['Los periféricos', '2 ADC de 12 bits, 2 DAC de 8 bits (GPIO25 y 26), 16 canales PWM, 3 UART, 2 I2C, 3 SPI y pines touch.'],
      ['Botones y LED', 'EN = reset, BOOT = modo de carga de firmware y el LED integrado en el GPIO 2.'],
    ],
    'ejemplo': ejemplo('placa.ino', 'Lo que hay que saber de la placa (DOIT DevKit V1)', '''
      // Procesador: Xtensa LX6, 2 núcleos de 32 bits, hasta 240 MHz «1»
      // Trabaja a 3,3 V: más tensión en un pin la puede dañar «2»
      // Flash 4 MB (programa) · SRAM 520 KB (datos) · ROM 448 KB (bootloader) «3»
      // WiFi 2,4 GHz y Bluetooth 4.2 + BLE, sin módulos externos «4»
      // ADC 12 bits · DAC 8 bits en GPIO25/26 · 16 PWM · 3 UART · 2 I2C · 3 SPI «5»
      const int LED = 2;            // el LED integrado (LED_BUILTIN) «6»
      // EN = reset · BOOT = modo de carga de firmware «6»
      void setup() { pinMode(LED, OUTPUT); }
      void loop()  { digitalWrite(LED, HIGH); }
    ''', 'cpp'),
    'ojo': ['16 MHz y 5 V son del Arduino UNO, no de la ESP32.',
            'El chip no tiene USB nativo: la placa trae un conversor USB–UART (CP210x), por eso hay que instalar el driver. Igual, para el campus «no tiene interfaz USB directa» es incorrecta.',
            'GPIO34 a GPIO39 son solo de entrada: no sirven como salida ni para PWM.',
            'BOOT no reinicia: el que reinicia es EN.'],
    'parcial': '10 preguntas de opción múltiple, casi todas con varias correctas y puntaje parcial. Las de la ESP32 salen siempre: arquitectura, LED integrado, botones y tensión.',
    'pdf': 2,
  },
  [
    resp_ej('1.1', 'Los números', 'la ESP32 en números', 'Completá los números de la ESP32 de la cátedra (DOIT DevKit V1).', [
      N('Tensión de trabajo', 3.3, 1, 'V', 'Por USB entran 5 V y el regulador los baja.'),
      N('Núcleos del procesador', 2, 0, motivo='Xtensa LX6 de doble núcleo.'),
      N('Bits del procesador', 32, 0, motivo='El Arduino UNO es de 8.'),
      N('Frecuencia máxima', 240, 0, 'MHz', 'El UNO va a 16 MHz.'),
      N('SRAM', 520, 0, 'KB', 'Los datos mientras el programa corre.'),
      N('Canales PWM', 16, 0, motivo='Cada uno con su frecuencia y resolución.'),
      N('Pin del LED integrado', 2, 0, motivo='LED_BUILTIN = 2 (en la mayoría de los Arduino es el 13).'),
    ], pistas=['Están todos en la explicación de la parte.']),
    elegir_ej('1.2', 'Arquitectura', 'arquitectura y procesador (parcial 2025)', 'Las opciones de dos preguntas del parcial 2025: «¿Qué afirmaciones sobre la arquitectura de la ESP32 son verdaderas?» y «¿Qué características tiene el procesador Xtensa LX6?». ¿Cuáles marcarías?', CI, [
      ('Puede manejar hasta 16 canales PWM', 'Correcta', 'Tiene 16 canales.'),
      ('Posee coprocesadores para ciertas tareas', 'Correcta', 'El coprocesador ULP lee sensores con muy bajo consumo y despierta al sistema.'),
      ('Solo soporta un núcleo de ejecución', 'Incorrecta', 'Es de doble núcleo.'),
      ('Tiene soporte para múltiples ADC y DAC', 'Correcta', '2 ADC y 2 DAC.'),
      ('No tiene interfaz USB directa', 'Incorrecta', 'Para el campus es incorrecta, aunque el chip no tiene USB nativo (la placa usa un conversor USB–UART). No la marques.'),
      ('El Xtensa LX6 es de doble núcleo y 32 bits', 'Correcta', 'Hasta 240 MHz.'),
      ('Lo fabrica Texas Instruments', 'Incorrecta', 'El chip es de Espressif Systems (el núcleo, de Tensilica).'),
      ('Corre a 16 MHz', 'Incorrecta', 'Eso es el Arduino UNO.'),
      ('Tiene capacidad para procesamiento paralelo', 'Correcta', 'Los dos núcleos pueden trabajar juntos.'),
    ], pregunta='¿La marcarías?'),
    elegir_ej('1.3', 'Botones y memorias', 'botones y memorias', '¿Qué botón o qué memoria es?', ['EN', 'BOOT', 'Flash', 'SRAM', 'ROM', 'EEPROM'], [
      ('Reinicia la placa', 'EN', 'EN (ENABLE) es el reset.'),
      ('Pone la placa en modo de carga de firmware', 'BOOT', 'Pregunta del recuperatorio 2025: no «carga el bootloader» ni reinicia.'),
      ('Guarda el programa y no se borra al apagar', 'Flash', 'Hasta 4 MB.'),
      ('Guarda los datos mientras el programa corre; se borra al apagar', 'SRAM', '520 KB, volátil.'),
      ('Tiene el bootloader', 'ROM', '448 KB.'),
      ('Guarda configuraciones que sobreviven al reinicio y a un apagón', 'EEPROM', 'Por ejemplo, el último estado de un LED.'),
    ], pregunta='¿Qué es?'),
    cod_ej('1.4', 'Blink', 'el LED integrado parpadea', 'El primer programa de todos: que el **LED integrado** parpadee, medio segundo prendido y medio segundo apagado.',
      '''
      const int LED = 2;          // el LED integrado

      void setup() {
        // configurá el pin del LED como salida
      }

      void loop() {
        // prendelo medio segundo y apagalo medio segundo
      }
      ''', '''
      const int LED = 2;          // el LED integrado

      void setup() {
        pinMode(LED, OUTPUT);
      }

      void loop() {
        digitalWrite(LED, HIGH);   // 3,3 V: prende
        delay(500);
        digitalWrite(LED, LOW);    // 0 V: apaga
        delay(500);
      }
      ''', [
        C(r'pinMode\s*\(\s*LED\s*,\s*OUTPUT\s*\)', 'El LED es una salida', 'Falta `pinMode(LED, OUTPUT)` en el setup'),
        C(r'digitalWrite\s*\(\s*LED\s*,\s*HIGH\s*\)', 'Lo prende con HIGH', 'Falta prenderlo: `digitalWrite(LED, HIGH)`'),
        C(r'digitalWrite\s*\(\s*LED\s*,\s*LOW\s*\)', 'Lo apaga con LOW', 'Falta apagarlo: `digitalWrite(LED, LOW)`'),
        cuenta(r'delay\s*\(\s*500\s*\)', 2, 'Espera medio segundo en cada estado', 'Hacen falta dos `delay(500)`: uno prendido y otro apagado'),
      ], respuestas=[N('¿Cuántas veces parpadea por segundo?', 1, 0), N('¿Qué tensión hay en el pin con HIGH?', 3.3, 1, 'V')],
      pasos=['En el setup: `pinMode(LED, OUTPUT)`.', 'En el loop: HIGH, esperar, LOW, esperar.'],
      pistas=['Es el sketch A del resumen.']),
  ]))

# ======================= 2 · Entradas y salidas =======================
partes.append(parte(2, 'pines', 'Entradas y salidas', 'Entradas y salidas',
  'Cada pin es entrada o salida, digital (HIGH o LOW) o analógica (0 a 3,3 V). La pregunta que sale siempre: qué se conecta dónde.',
  {
    'que': 'Cada pin se programa como **entrada** o **salida**, **digital** (dos estados: HIGH ≈ 3,3 V y LOW ≈ 0 V) o **analógica** (una tensión entre 0 y 3,3 V que el ADC convierte en un número).\n'
           'La pregunta que sale siempre es **qué se conecta dónde**. En la placa de la cátedra: el potenciómetro en el 32, el DHT22 en el 33, el pulsador en el 19, el relé en el 14 y un LED en el 23.',
    'consta': [
      ['Entrada digital', 'Pulsador, llave, fin de carrera, touch: `digitalRead(pin)`. Con `INPUT_PULLUP` queda en HIGH si está suelto.'],
      ['Entrada analógica', 'Potenciómetro, LDR, sensor con salida de tensión: `analogRead(pin)` da 0 a 4095.'],
      ['Salida digital', 'LED (prender y apagar), relé, LCD, transistor: `digitalWrite(pin, HIGH)`.'],
      ['Salida PWM', 'Brillo de un LED, posición de un servo, tono de un buzzer, velocidad de un motor (con driver).'],
      ['Sensor digital', 'DHT22 y sensores I2C/SPI: el dato llega «procesado», sin pasar por el ADC y más robusto al ruido.'],
      ['Cuidado eléctrico', 'Más de 3,3 V daña el pin; un motor o una tira de LEDs van con transistor o relé.'],
    ],
    'ejemplo': ejemplo('placa_utn.ino', 'La placa de la cátedra: qué hay en cada pin', '''
      const int BOTON = 19;            // pulsador: entrada digital «1»
      const int POT = 32;              // potenciómetro: entrada analógica «2»
      const int RELAY = 14;            // relé: salida digital «3»
      const int LED = 23;              // LED: salida, se le puede dar PWM «4»
      void setup() {
        pinMode(BOTON, INPUT_PULLUP);  // suelto = HIGH, apretado = LOW «1»
        pinMode(RELAY, OUTPUT); «3»
        pinMode(LED, OUTPUT);
      }
      void loop() {
        if (digitalRead(BOTON) == LOW) digitalWrite(RELAY, HIGH);   // apretado: prende «1»
        int valor = analogRead(POT);   // 0..4095 «2»
        analogWrite(LED, valor / 16);  // 0..255: el brillo «4»
        // el DHT22 (pin 33) se lee con su librería: no pasa por el ADC «5»
        // un motor DC nunca directo al pin: transistor o driver «6»
      }
    ''', 'cpp'),
    'ojo': ['Un pulsador es una entrada **digital**, aunque esté en un pin con ADC.',
            'Una entrada sin conectar queda flotante: usá pull-up o pull-down.',
            'Un relé es todo o nada: salida digital, no PWM.'],
    'parcial': '«¿Qué se puede conectar a una entrada analógica?», «¿Qué componentes se controlan con salidas digitales?», «¿Qué se puede usar con PWM?»: salen todos los años, con varias correctas.',
    'pdf': 3,
  },
  [
    elegir_ej('2.1', 'Qué va dónde', '¿qué se conecta dónde?', 'Para cada componente: ¿a qué tipo de pin va?', ['Entrada digital', 'Entrada analógica', 'Salida digital', 'Salida PWM'], [
      ('Pulsador', 'Entrada digital', 'Dos estados: apretado o suelto.'),
      ('Potenciómetro', 'Entrada analógica', 'Una tensión que varía entre 0 y 3,3 V.'),
      ('LDR (sensor de luz)', 'Entrada analógica', 'Su tensión varía con la luz.'),
      ('Fin de carrera', 'Entrada digital', 'Un sensor discreto: tocó o no tocó.'),
      ('Relé', 'Salida digital', 'Todo o nada.'),
      ('LED que solo se prende y se apaga', 'Salida digital', '`digitalWrite`.'),
      ('LED al que se le regula el brillo', 'Salida PWM', 'El duty cycle da el brillo.'),
      ('Servo', 'Salida PWM', 'El ancho del pulso da la posición.'),
      ('Buzzer (para hacer un tono)', 'Salida PWM', 'La frecuencia da el tono.'),
      ('Sensor de temperatura con salida de tensión variable', 'Entrada analógica', 'Se lee con `analogRead`.'),
      ('Pantalla LCD', 'Salida digital', 'Así la da el apunte.'),
    ], pregunta='¿A qué pin va?'),
    elegir_ej('2.2', 'Parcial 2025', 'entradas, salidas y sensores (parcial 2025)', 'Opciones de las preguntas de 2025 sobre entradas analógicas, sensores, la señal LOW y las salidas digitales. ¿Son correctas?', CI, [
      ('A un pin de entrada analógica se puede conectar un potenciómetro', 'Correcta', 'Es el ejemplo típico (pin 32 de la placa).'),
      ('A un pin de entrada analógica se puede conectar un pulsador', 'Incorrecta', 'El pulsador es una entrada digital.'),
      ('Los sensores analógicos varían su salida en voltaje y se leen con analogRead()', 'Correcta', 'El ADC convierte esa tensión en un número.'),
      ('Los sensores digitales no requieren conversión ADC', 'Correcta', 'La salida ya viene en unos y ceros.'),
      ('Los sensores digitales siempre usan menos corriente', 'Incorrecta', 'No se puede afirmar en general.'),
      ('LOW equivale a una tensión cercana a 0 V y apaga una salida digital', 'Correcta', 'Es el 0 lógico.'),
      ('LOW representa un 1 lógico', 'Incorrecta', 'El 1 lógico es HIGH (≈ 3,3 V).'),
      ('Con salidas digitales se controlan LEDs, relés y pantallas LCD', 'Correcta', 'Así lo da el apunte.'),
      ('Un motor DC se conecta directo a una salida digital', 'Incorrecta', 'Un GPIO da poca corriente: hace falta un transistor o un driver.'),
    ], pregunta='¿La marcarías?'),
    cod_ej('2.3', 'Pulsador', 'el pulsador prende el LED', 'Con la placa de la cátedra: mientras el **pulsador** (pin 19) está apretado, el LED integrado se prende; cuando lo soltás, se apaga. Usá el pull-up interno.',
      '''
      const int BOTON = 19;      // el pulsador de la placa de la cátedra
      const int LED = 2;         // el LED integrado

      void setup() {
        // el pulsador con pull-up interno y el LED como salida
        Serial.begin(115200);
      }

      void loop() {
        // si está apretado (LOW), prendé el LED; si no, apagalo
      }
      ''', '''
      const int BOTON = 19;      // el pulsador de la placa de la cátedra
      const int LED = 2;         // el LED integrado

      void setup() {
        pinMode(BOTON, INPUT_PULLUP);   // suelto = HIGH, apretado = LOW
        pinMode(LED, OUTPUT);
        Serial.begin(115200);
      }

      void loop() {
        if (digitalRead(BOTON) == LOW) {
          digitalWrite(LED, HIGH);
        } else {
          digitalWrite(LED, LOW);
        }
      }
      ''', [
        C(r'pinMode\s*\(\s*BOTON\s*,\s*INPUT_PULLUP\s*\)', 'El pulsador con pull-up', 'Configurá el pulsador con `pinMode(BOTON, INPUT_PULLUP)`'),
        C(r'pinMode\s*\(\s*LED\s*,\s*OUTPUT\s*\)', 'El LED es una salida', 'Falta `pinMode(LED, OUTPUT)`'),
        C(r'digitalRead\s*\(\s*BOTON\s*\)\s*==\s*LOW|!\s*digitalRead\s*\(\s*BOTON\s*\)', 'Apretado es LOW', 'Con pull-up, apretado es LOW: `digitalRead(BOTON) == LOW`'),
        C(r'digitalWrite\s*\(\s*LED\s*,\s*HIGH\s*\)', 'Prende el LED', 'Falta prender el LED con HIGH'),
        C(r'digitalWrite\s*\(\s*LED\s*,\s*LOW\s*\)', 'Apaga el LED', 'Falta apagar el LED con LOW cuando lo soltás'),
      ], respuestas=[OP('¿Qué lee digitalRead con el pulsador suelto?', ['HIGH', 'LOW'], 'HIGH', 'El pull-up deja la entrada en HIGH mientras nadie la lleve a 0 V.')],
      pasos=['En el setup: `INPUT_PULLUP` para el pulsador y `OUTPUT` para el LED.', 'En el loop: un if con `digitalRead(BOTON) == LOW`.'],
      pistas=['Con pull-up la lógica queda «al revés»: apretado es LOW.']),
    cod_ej('2.4', 'DHT22', 'leer el DHT22', 'El DHT22 de la placa (pin 33) es un **sensor digital** de temperatura y humedad. Con la librería `DHT.h` (como el caso del profe), leé la temperatura y la humedad cada 2 segundos y mostralas en el monitor serie. Si la lectura falla (`isnan`), avisá y salí del loop.',
      '''
      #include "DHT.h"

      #define DHTPIN 33
      #define DHTTYPE DHT22
      // creá el objeto dht

      void setup() {
        Serial.begin(115200);
        // iniciá el sensor
      }

      void loop() {
        delay(2000);              // el DHT22 es lento: una lectura cada 2 s
        // leé la humedad y la temperatura
        // si alguna falla, avisá y return
        // mostralas por el monitor serie
      }
      ''', '''
      #include "DHT.h"

      #define DHTPIN 33
      #define DHTTYPE DHT22
      DHT dht(DHTPIN, DHTTYPE);

      void setup() {
        Serial.begin(115200);
        dht.begin();
      }

      void loop() {
        delay(2000);
        float h = dht.readHumidity();
        float t = dht.readTemperature();
        if (isnan(h) || isnan(t)) {
          Serial.println("Error al leer el DHT22");
          return;
        }
        Serial.print("Humedad: ");
        Serial.print(h);
        Serial.print(" %  Temperatura: ");
        Serial.print(t);
        Serial.println(" C");
      }
      ''', [
        C(r'DHT\s+dht\s*\(\s*DHTPIN\s*,\s*DHTTYPE\s*\)', 'Crea el objeto dht', 'Creá el objeto: `DHT dht(DHTPIN, DHTTYPE);`'),
        C(r'dht\.begin\s*\(\s*\)', 'Inicia el sensor', 'Falta `dht.begin()` en el setup'),
        C(r'dht\.readTemperature\s*\(', 'Lee la temperatura', 'Falta `dht.readTemperature()`'),
        C(r'dht\.readHumidity\s*\(', 'Lee la humedad', 'Falta `dht.readHumidity()`'),
        C(r'isnan\s*\(', 'Controla si falló', 'Controlá la lectura con `isnan(...)`'),
      ], respuestas=[OP('¿El DHT22 pasa por el ADC?', ['Sí', 'No'], 'No', 'Es un sensor digital: la lectura llega procesada.'), N('¿En qué pin está en la placa de la cátedra?', 33, 0)],
      pasos=['`DHT dht(DHTPIN, DHTTYPE);` arriba del setup.', '`dht.begin()` en el setup.', '`float t = dht.readTemperature();` y `float h = dht.readHumidity();`.'],
      pistas=['Es el caso «Sensor_Hum_y_Temp» del profe.']),
    elegir_ej('2.5', '¿Se puede?', '¿se puede hacer?', 'Cosas que podés querer hacer con la placa. ¿Se puede?', ['Sí', 'No'], [
      ('Usar el GPIO 34 como salida para un LED', 'No', 'GPIO34 a GPIO39 son solo de entrada.'),
      ('Generar una tensión continua de 1,5 V en el GPIO 25', 'Sí', 'El GPIO25 tiene DAC.'),
      ('Usar el GPIO 36 para PWM', 'No', 'Es solo de entrada.'),
      ('Leer el potenciómetro en el pin 32', 'Sí', 'Es entrada analógica (ADC1).'),
      ('Leer un pin del ADC2 con el WiFi encendido', 'No', 'Con WiFi, evitá el ADC2.'),
      ('Conectar un motor DC directo a un GPIO', 'No', 'Hace falta un transistor o un relé y una fuente aparte.'),
      ('Meterle 5 V a un pin de entrada', 'No', 'Puede dañar el microcontrolador: divisor de tensión o conversor de nivel.'),
      ('Despertar la placa del deep sleep con un pin touch', 'Sí', 'Los touch pueden despertarla.'),
    ], pregunta='¿Se puede?'),
  ]))

# ======================= 3 · ADC, map y PWM =======================
POTE = '''
const int POT = 32, LED = 26;
void setup() { pinMode(LED, OUTPUT); }
void loop() {
  int lectura = analogRead(POT);                // 0..4095
  int brillo = map(lectura, 0, 4095, 0, 255);
  analogWrite(LED, brillo);                     // duty 0..100 %
  float volt = lectura * 3.3 / 4095;
}
'''
partes.append(parte(3, 'adc', 'ADC, map y PWM: las cuentas', 'ADC y PWM',
  'Con N bits hay 2ᴺ valores (12 bits → 0 a 4095). `map` pasa de un rango a otro con cuentas enteras, y el PWM da una tensión promedio igual al duty por la tensión.',
  {
    'que': 'El **ADC** convierte una tensión en un número: con N bits hay 2ᴺ valores (12 bits → 0 a 4095). `map` lleva ese número a otro rango, y el **PWM** «simula» una tensión con una onda cuadrada: lo que importa es el **duty cycle**, el porcentaje del tiempo en HIGH.\n'
           'Saber hacer estas cuentas sirve para entender qué hace un sketch y qué pasa si se cambia algo.',
    'consta': [
      ['2ᴺ valores', '8 bits → 256 · 10 bits → 1024 · 12 bits → 4096.'],
      ['De lectura a volts', '`volt = lectura * 3.3 / 4095`. La resolución es 3,3 V / 4096 ≈ 0,8 mV.'],
      ['map', '`map(x, 0, 4095, 0, 255)` escala de un rango a otro con cuentas enteras (corta los decimales).'],
      ['El duty cycle', 'duty = t_alto / T. Tensión promedio = duty × tensión: con 5 V y 20 %, 1 V.'],
      ['analogWrite', '`analogWrite(pin, 0…255)` con 8 bits: 0 es 0 % y 255 es 100 %.'],
      ['El DAC', 'Una tensión continua de verdad, en el GPIO25 y el 26, con 8 bits: `dacWrite(25, valor)`.'],
    ],
    'ejemplo': ejemplo('pote_led.ino', 'Sketch C del resumen: el potenciómetro le da el brillo al LED', '''
      const int POT = 32, LED = 26;
      void setup() { pinMode(LED, OUTPUT); }
      void loop() {
        int lectura = analogRead(POT);                // 0..4095: 12 bits = 4096 valores «1»
        float volt = lectura * 3.3 / 4095;            // de 0 a 3,3 V «2»
        int brillo = map(lectura, 0, 4095, 0, 255);   // con 2048 da 127 «3»
        // 127 de 255: duty ≈ 50 %, tensión promedio ≈ 1,64 V «4»
        analogWrite(LED, brillo); «5»
        // dacWrite(25, 127) daría 1,64 V continuos de verdad «6»
      }
    ''', 'cpp'),
    'ojo': ['PWM **no** es una salida analógica: es una onda cuadrada. La analógica de verdad es el DAC.',
            '`map` trabaja con enteros: map(2048, 0, 4095, 0, 255) da 127, no 127,5.',
            'Con el WiFi encendido, no uses los pines del ADC2 para leer.'],
    'parcial': 'Salen el rango de analogRead (0 a 4095), qué hace el DAC y qué se puede manejar con PWM. Las cuentas sirven para entender qué pasa si cambiás algo del sketch.',
    'pdf': 3,
  },
  [
    resp_ej('3.1', 'Bits', 'cuántos valores', 'Completá cuántos valores distintos da un conversor de cada cantidad de bits, y la resolución del ADC de la ESP32.', [
      N('Con 8 bits', 256, 0, motivo='2⁸ = 256 (0 a 255).'),
      N('Con 10 bits', 1024, 0, motivo='2¹⁰ = 1024 (0 a 1023).'),
      N('Con 12 bits (el ADC de la ESP32)', 4096, 0, motivo='2¹² = 4096 (0 a 4095).'),
      N('Resolución del ADC de 12 bits con 3,3 V', 3.3 / 4096 * 1000, 2, 'mV', '3,3 V / 4096 ≈ 0,8 mV por cuenta.'),
    ], pistas=['N bits → 2ᴺ valores.']),
    resp_ej('3.2', 'Leer el sketch', 'leé el sketch del potenciómetro', 'Con el sketch de al lado, el potenciómetro está en la mitad y `analogRead` devuelve **2048**. ¿Cuánto valen `brillo` y `volt`, y qué duty cycle tiene el LED?', [
      N('brillo', 127, 0, motivo='map con enteros: 2048 × 255 / 4095 = 127,5 → 127.'),
      N('volt', 2048 * 3.3 / 4095, 2, 'V'),
      N('duty cycle', 127 / 255 * 100, 1, '%', '127 de 255.'),
    ], codigo={'nombre': 'pote_led.ino', 'texto': POTE}, lenguaje='cpp',
      pistas=['map(x, 0, 4095, 0, 255) = x × 255 / 4095, cortando los decimales.', 'duty = brillo / 255.']),
    resp_ej('3.3', 'PWM', 'la tensión promedio del PWM', 'Calculá la tensión promedio y el duty de cada señal PWM.', [
      N('Con 5 V y un duty de 20 %: tensión promedio', 1, 1, 'V', '5 V × 0,2 = 1 V (el ejemplo del apunte).'),
      N('analogWrite(LED, 64) con 8 bits: duty', 64 / 255 * 100, 1, '%'),
      N('Con 3,3 V y analogWrite(LED, 191): tensión promedio', 191 / 255 * 3.3, 2, 'V'),
      N('¿Qué valor de analogWrite da 100 %?', 255, 0),
    ], pistas=['Tensión promedio = duty × tensión.', 'Con 8 bits, el duty es valor / 255.']),
    cod_ej('3.4', 'Pote → LED', 'el potenciómetro regula el LED', 'El potenciómetro de la placa (pin 32) tiene que regular el brillo del LED del pin 23: leé el ADC, escalalo de 0–4095 a 0–255 con `map` y mandalo con `analogWrite`.',
      '''
      const int POT = 32;       // potenciómetro de la placa
      const int LED = 23;       // LED de la placa

      void setup() {
        pinMode(LED, OUTPUT);
      }

      void loop() {
        // 1) leé el potenciómetro (0..4095)
        // 2) pasalo a 0..255 con map
        // 3) mandalo al LED con analogWrite
      }
      ''', '''
      const int POT = 32;       // potenciómetro de la placa
      const int LED = 23;       // LED de la placa

      void setup() {
        pinMode(LED, OUTPUT);
      }

      void loop() {
        int lectura = analogRead(POT);
        int brillo = map(lectura, 0, 4095, 0, 255);
        analogWrite(LED, brillo);
      }
      ''', [
        C(r'analogRead\s*\(\s*POT\s*\)', 'Lee el potenciómetro', 'Leé el potenciómetro con `analogRead(POT)`'),
        C(r'map\s*\([^;]*0\s*,\s*4095\s*,\s*0\s*,\s*255\s*\)', 'Escala con map', 'Escalá con `map(lectura, 0, 4095, 0, 255)`'),
        C(r'analogWrite\s*\(\s*LED\s*,', 'Manda el PWM al LED', 'Mandá el valor con `analogWrite(LED, brillo)`'),
        NO(r'digitalWrite\s*\(\s*LED', 'Sin digitalWrite en el LED', 'Con `digitalWrite` el LED solo se prende o se apaga: usá `analogWrite`'),
      ], respuestas=[N('Si la lectura es 3000, ¿qué valor le manda al LED?', 186, 0, motivo='3000 × 255 / 4095 = 186,8 → 186.')],
      pasos=['`int lectura = analogRead(POT);`', '`int brillo = map(lectura, 0, 4095, 0, 255);`', '`analogWrite(LED, brillo);`'],
      pistas=['En el caso del profe se invierte el sentido con map(x, 0, 4095, 255, 0).']),
    elegir_ej('3.5', 'ADC, DAC o PWM', '¿ADC, DAC o PWM?', '¿De cuál es cada frase?', ['ADC', 'DAC', 'PWM'], [
      ('Convierte una tensión en un número de 0 a 4095', 'ADC', 'Analógico → digital.'),
      ('Genera una tensión continua de verdad, en el GPIO25 y el GPIO26', 'DAC', 'Digital → analógico.'),
      ('Onda cuadrada de frecuencia fija y ancho de pulso variable', 'PWM', 'Lo que cambia es el duty.'),
      ('Se usa con analogRead()', 'ADC', 'Lee la tensión del pin.'),
      ('analogWrite() a un LED', 'PWM', 'Regula el brillo con el duty.'),
      ('8 bits (0 a 255), en solo dos pines', 'DAC', 'Las únicas salidas analógicas «puras».'),
      ('16 canales, con frecuencia y resolución por canal', 'PWM', 'Pregunta del recuperatorio 2025.'),
      ('Con el WiFi encendido, conviene no usar el número 2', 'ADC', 'El ADC2 comparte recursos con el WiFi.'),
    ], pregunta='¿De cuál es?'),
  ]))

# ======================= 4 · Programación =======================
partes.append(parte(4, 'programacion', 'Programar la ESP32: setup, loop y millis', 'Programación',
  'C++ adaptado para Arduino. `setup()` corre una vez y `loop()` se repite para siempre. Para esperar sin frenar todo se usa `millis()` (en un `unsigned long`), no `delay()`.',
  {
    'que': 'La ESP32 se programa en **C++ adaptado para Arduino**: compilado, fuertemente tipado y con la memoria a cargo del programador. Un sketch tiene dos funciones: `setup()`, que corre una vez al arrancar, y `loop()`, que se repite para siempre.\n'
           'Para esperar sin frenar todo se usa `millis()`, no `delay()`: se guarda el tiempo y se compara.',
    'consta': [
      ['setup()', 'Corre una sola vez: los pines, `Serial.begin(115200)`, el WiFi.'],
      ['loop()', 'Se repite para siempre: leer, decidir, actuar.'],
      ['delay()', 'Frena todo el programa: mientras espera no lee sensores ni atiende el WiFi.'],
      ['millis()', 'Los ms desde que arrancó, en un `unsigned long`: temporizadores sin bloquear.'],
      ['El monitor serie', "`Serial.available()` dice si llegó algo y `Serial.readStringUntil('\\n')` lo lee."],
    ],
    'ejemplo': ejemplo('temporizador.ino', 'Sketches D y E del resumen', r'''
      unsigned long antes = 0;               // millis() se guarda en unsigned long «4»
      void setup() {
        Serial.begin(115200);                // una sola vez «1»
        pinMode(2, OUTPUT); «1»
      }
      void loop() {                          // se repite para siempre «2»
        if (millis() - antes >= 1000) {      // ¿pasó 1 s? «4»
          antes = millis(); «4»
          // leer el sensor, enviar el dato...
        }
        // delay(1000) acá frenaría todo, también el WiFi «3»
        if (Serial.available()) {            // ¿llegó algo por el monitor serie? «5»
          String cmd = Serial.readStringUntil('\n'); «5»
          cmd.trim(); «5»
        }
      }
    ''', 'cpp'),
    'ojo': ['Si guardás millis() en un int, se desborda mucho antes: usá unsigned long.',
            'La cátedra da el int de 16 bits (es el del Arduino UNO); en la ESP32 es de 32.',
            'Las interrupciones (ISR) tienen que ser cortas y no bloqueantes: nada de delay adentro.'],
    'parcial': '«¿Qué afirmaciones son correctas sobre millis()?» y «¿sobre delay()?» salen siempre. También setup() y loop(), y cómo es el lenguaje.',
    'pdf': 4,
  },
  [
    elegir_ej('4.1', 'setup o loop', '¿en setup() o en loop()?', '¿Dónde va cada cosa?', ['setup()', 'loop()'], [
      ('Serial.begin(115200)', 'setup()', 'El puerto serie se abre una vez.'),
      ('pinMode(LED, OUTPUT)', 'setup()', 'Los pines se configuran al arrancar.'),
      ('WiFi.begin(ssid, password)', 'setup()', 'La conexión se arma una vez.'),
      ('Leer el potenciómetro todo el tiempo', 'loop()', 'Lo que se repite.'),
      ('client.loop() de MQTT', 'loop()', 'Atiende los mensajes en cada vuelta.'),
      ('Se ejecuta una sola vez al arrancar', 'setup()', 'Pregunta del parcial 2025.'),
      ('Se repite indefinidamente', 'loop()', 'Pregunta del parcial 2025.'),
    ], pregunta='¿Dónde va?'),
    cod_ej('4.2', 'millis', 'parpadear sin delay', 'Que el LED integrado cambie de estado **cada 1000 ms sin usar `delay()`**: el loop tiene que quedar libre para hacer otras cosas (leer sensores, atender el WiFi).',
      '''
      const int LED = 2;
      unsigned long antes = 0;
      int estado = LOW;

      void setup() {
        pinMode(LED, OUTPUT);
      }

      void loop() {
        // cada 1000 ms: guardá el tiempo, cambiá el estado y mandalo al LED
        // sin delay()
      }
      ''', '''
      const int LED = 2;
      unsigned long antes = 0;
      int estado = LOW;

      void setup() {
        pinMode(LED, OUTPUT);
      }

      void loop() {
        if (millis() - antes >= 1000) {   // ¿pasó 1 s?
          antes = millis();
          estado = !estado;
          digitalWrite(LED, estado);
        }
        // el loop sigue libre para otras tareas
      }
      ''', [
        C(r'millis\s*\(\s*\)\s*-\s*antes\s*>=?\s*1000', 'Compara cuánto pasó', 'Compará: `if (millis() - antes >= 1000)`'),
        C(r'antes\s*=\s*millis\s*\(\s*\)', 'Guarda el tiempo', 'Guardá el tiempo: `antes = millis();`'),
        C(r'estado\s*=\s*!\s*estado|estado\s*=\s*\(?\s*estado\s*==\s*LOW', 'Cambia el estado', 'Cambiá el estado: `estado = !estado;`'),
        C(r'digitalWrite\s*\(\s*LED\s*,\s*estado\s*\)', 'Lo manda al LED', 'Mandá el estado al LED: `digitalWrite(LED, estado)`'),
        NO(r'\bdelay\s*\(', 'Sin delay', 'Sin `delay()`: frena todo el programa'),
      ], respuestas=[OP('¿En qué tipo se guarda millis()?', ['int', 'unsigned long', 'float', 'byte'], 'unsigned long', 'Es un número que crece siempre y no tiene signo.')],
      pasos=['`if (millis() - antes >= 1000) { ... }`', 'Adentro: `antes = millis();`, `estado = !estado;` y `digitalWrite(LED, estado);`.'],
      pistas=['Es el sketch D del resumen.']),
    resp_ej('4.3', 'Tipos', 'los tipos y el desborde de millis', 'Los tamaños que da la cátedra y una cuenta: `millis()` se guarda en un `unsigned long` de 32 bits, así que después de 2³² ms vuelve a 0.', [
      N('Bits de un unsigned long', 32, 0),
      N('Bits de un int según la cátedra (Arduino UNO)', 16, 0, motivo='En la ESP32 el int es de 32 bits; el apunte da el del UNO.'),
      N('Bits de un bool, un byte o un char', 8, 0),
      N('¿Cuántos días tarda millis() en volver a 0?', 2 ** 32 / 1000 / 86400, 1, 'días', '2³² ms = 4.294.967.296 ms ≈ 49,7 días.'),
    ], pistas=['Un día tiene 86.400.000 ms.']),
    elegir_ej('4.4', 'Parcial 2025', 'millis, delay, setup y el lenguaje (parcial 2025)', 'Opciones de las preguntas de 2025 sobre millis(), delay(), setup() y loop(), y el lenguaje. ¿Son correctas?', CI, [
      ('millis() devuelve el tiempo en milisegundos desde que inició el programa', 'Correcta', 'En un unsigned long.'),
      ('millis() permite crear temporizadores sin bloquear el loop principal', 'Correcta', 'Se guarda el tiempo y se compara.'),
      ('millis() detiene el programa hasta que pasa el tiempo', 'Incorrecta', 'Eso es delay().'),
      ('delay() detiene completamente la ejecución por ese tiempo', 'Correcta', 'No lee sensores ni atiende el WiFi.'),
      ('El uso excesivo de delay() puede afectar el rendimiento', 'Correcta', 'Todo lo demás espera.'),
      ('setup() se ejecuta en cada vuelta del loop', 'Incorrecta', 'Una sola vez al arrancar.'),
      ('Se programa en C++ adaptado para Arduino: compilado y fuertemente tipado', 'Correcta', 'La memoria la maneja el programador.'),
      ('Una interrupción (ISR) puede tener un delay largo adentro', 'Incorrecta', 'Tienen que ser cortas y no bloqueantes.'),
    ], pregunta='¿La marcarías?'),
    cod_ej('4.5', 'Monitor serie', 'un comando por el monitor serie', 'Prender y apagar el **relé** de la placa (pin 14) escribiendo en el monitor serie: con `LUZ_ON` se prende y con `LUZ_OFF` se apaga.',
      r'''
      const int RELAY = 14;      // el relé de la placa de la cátedra

      void setup() {
        pinMode(RELAY, OUTPUT);
        // abrí el puerto serie a 115200
      }

      void loop() {
        // si llegó algo: leé la línea hasta el '\n', sacale los espacios
        // y con "LUZ_ON" prendé el relé, con "LUZ_OFF" apagalo
      }
      ''', r'''
      const int RELAY = 14;      // el relé de la placa de la cátedra

      void setup() {
        pinMode(RELAY, OUTPUT);
        Serial.begin(115200);
      }

      void loop() {
        if (Serial.available()) {
          String cmd = Serial.readStringUntil('\n');
          cmd.trim();
          if (cmd == "LUZ_ON")  digitalWrite(RELAY, HIGH);
          if (cmd == "LUZ_OFF") digitalWrite(RELAY, LOW);
        }
      }
      ''', [
        C(r'Serial\.begin\s*\(\s*115200\s*\)', 'Abre el puerto serie', 'Abrí el puerto serie: `Serial.begin(115200)`'),
        C(r'Serial\.available\s*\(\s*\)', 'Se fija si llegó algo', 'Fijate si llegó algo con `Serial.available()`'),
        C(r'readStringUntil\s*\(', 'Lee la línea', "Leé la línea con `Serial.readStringUntil('\\n')`"),
        C(r'\.trim\s*\(\s*\)', 'Le saca los espacios', 'Sacale los espacios y el fin de línea con `.trim()`'),
        C(r'==\s*"LUZ_ON"[^;]*digitalWrite\s*\(\s*RELAY\s*,\s*HIGH', 'LUZ_ON prende', 'Con "LUZ_ON", `digitalWrite(RELAY, HIGH)`'),
        C(r'==\s*"LUZ_OFF"[^;]*digitalWrite\s*\(\s*RELAY\s*,\s*LOW', 'LUZ_OFF apaga', 'Con "LUZ_OFF", `digitalWrite(RELAY, LOW)`'),
      ], respuestas=[OP('¿Qué protocolo usa el monitor serie?', ['UART', 'I2C', 'SPI'], 'UART', 'Asíncrono, por TX y RX.')],
      pasos=['`Serial.begin(115200)` en el setup.', '`if (Serial.available()) { ... }` en el loop.', 'Adentro: leer, `trim()` y comparar con `==`.'],
      pistas=['Es el sketch E del resumen. Sin `trim()`, el "\\r" del final hace que no coincida.']),
  ]))

# ======================= 5 · Protocolos =======================
partes.append(parte(5, 'protocolos', 'Protocolos: UART, I2C y SPI', 'Protocolos',
  'Síncrona (con reloj: I2C y SPI) o asíncrona (sin reloj: UART). I2C usa 2 líneas y direcciones de 7 bits; SPI, 4 líneas y es la más rápida; UART, TX y RX cruzadas.',
  {
    'que': 'Para hablar con otros chips y con la PC, la ESP32 tiene hardware para tres protocolos. **Síncrona**: emisor y receptor comparten un reloj (I2C, SPI). **Asíncrona**: sin reloj, cada dato lleva bits de inicio y parada (UART).\n'
           'En la placa de la cátedra, el display OLED va por I2C (SDA en el 21 y SCL en el 22) y el monitor serie por UART.',
    'consta': [
      ['UART', 'Asíncrona, TX y RX cruzadas, punto a punto, el mismo baudrate en los dos: el monitor serie.'],
      ['I2C', 'Síncrona, 2 líneas (SDA y SCL), bus con dirección de 7 bits: muchos dispositivos con 2 cables. Librería Wire.'],
      ['SPI', 'Síncrona, 4 líneas (MOSI, MISO, SCLK y CS), la más rápida: tarjeta SD, pantallas gráficas.'],
      ['La dirección I2C', 'Cada dispositivo tiene la suya: el display de la placa es el 0x3C.'],
      ['Cuántos tiene', '3 UART, 2 I2C y 3 SPI, con hardware dedicado.'],
    ],
    'ejemplo': ejemplo('display.ino', 'El display OLED de la placa (casos del profe)', '''
      #include <Wire.h>                  // I2C: SDA en el pin 21 y SCL en el 22 «2»
      #include <Adafruit_SH110X.h>
      Adafruit_SH1106G display = Adafruit_SH1106G(128, 64, &Wire);
      void setup() {
        Serial.begin(115200);            // UART: el monitor serie, por TX y RX «1»
        display.begin(0x3C, true);       // la dirección I2C del display «4»
        display.clearDisplay();
        display.setTextColor(SH110X_WHITE);
        display.setCursor(0, 0);
        display.println("Hola");
        display.display();               // recién acá se ve
      }
      // una tarjeta SD iría por SPI: MOSI, MISO, SCLK y CS «3»
      // la ESP32 tiene 3 UART, 2 I2C y 3 SPI «5»
    ''', 'cpp'),
    'ojo': ['En la UART las líneas van cruzadas: el TX de uno al RX del otro.',
            'I2C y SPI son maestro–esclavo: en I2C se elige el esclavo por su dirección y en SPI por la línea CS.',
            'Los videos usan el display SSD1306: el código es casi igual, cambian la librería y el objeto.'],
    'parcial': 'Siempre sale una de SPI, I2C o UART («¿Qué afirmaciones describen el bus SPI?») y la diferencia entre síncrona y asíncrona.',
    'pdf': 4,
  },
  [
    elegir_ej('5.1', 'Cuál es', '¿UART, I2C o SPI?', '¿De qué protocolo es cada frase?', ['UART', 'I2C', 'SPI'], [
      ('TX y RX, cruzadas entre los dos dispositivos', 'UART', 'Punto a punto.'),
      ('SDA (datos) y SCL (reloj)', 'I2C', 'Dos líneas.'),
      ('MOSI, MISO, SCLK y CS', 'SPI', 'Cuatro líneas.'),
      ('Asíncrona: sin reloj, con bits de inicio y de parada', 'UART', 'Las otras dos son síncronas.'),
      ('Dirección de 7 bits: muchos dispositivos con 2 cables', 'I2C', 'Es un bus.'),
      ('La más rápida: tarjeta SD, pantallas gráficas', 'SPI', 'Alta velocidad.'),
      ('El monitor serie', 'UART', 'Serial.begin(115200).'),
      ('El display OLED de la placa de la cátedra', 'I2C', 'Librería Wire, dirección 0x3C.'),
      ('Los dos extremos tienen que usar el mismo baudrate', 'UART', 'No hay reloj compartido.'),
      ('La línea CS elige con qué esclavo se habla', 'SPI', 'Chip Select.'),
    ], pregunta='¿De cuál es?'),
    resp_ej('5.2', 'Números', 'los números de los protocolos', 'Completá.', [
      N('Líneas de I2C', 2, 0, motivo='SDA y SCL.'),
      N('Líneas de SPI', 4, 0, motivo='MOSI, MISO, SCLK y CS.'),
      N('Direcciones posibles con 7 bits', 128, 0, motivo='2⁷ = 128.'),
      N('UART de la ESP32', 3, 0),
      N('Pin SDA del display de la placa', 21, 0),
      N('Pin SCL del display de la placa', 22, 0),
    ], pistas=['Los pines del display están en el esquema de pines de la placa (Teórico).']),
    elegir_ej('5.3', 'Parcial 2025', 'SPI, I2C y UART (preguntas del banco)', 'Opciones de las preguntas sobre los buses. ¿Son correctas?', CI, [
      ('SPI usa las líneas CLK, MISO, MOSI y SS', 'Correcta', 'SS es el CS.'),
      ('SPI es una comunicación síncrona', 'Correcta', 'Comparte el reloj CLK.'),
      ('SPI usa solo dos cables', 'Incorrecta', 'Ese es I2C.'),
      ('En I2C cada dispositivo tiene una dirección de 7 bits, así que varios comparten el bus', 'Correcta', 'Con dos cables.'),
      ('En Arduino, I2C se usa con la librería Wire', 'Correcta', '`#include <Wire.h>`.'),
      ('La UART es síncrona', 'Incorrecta', 'Es asíncrona: no hay reloj.'),
      ('En la síncrona, emisor y receptor comparten una señal de reloj', 'Correcta', 'SPI e I2C.'),
      ('En la asíncrona, cada dato lleva bits de inicio y de parada', 'Correcta', 'UART.'),
    ], pregunta='¿La marcarías?'),
    cod_ej('5.4', 'Display', 'el potenciómetro en el display', 'Mostrá en el display OLED de la placa (I2C, dirección 0x3C) la tensión del potenciómetro (pin 32), actualizada cada 100 ms. Usá la librería del caso del profe (Adafruit SH110X).',
      '''
      #include <Wire.h>
      #include <Adafruit_SH110X.h>

      const int POT = 32;
      Adafruit_SH1106G display = Adafruit_SH1106G(128, 64, &Wire);

      void setup() {
        Serial.begin(115200);
        // iniciá el display en la dirección 0x3C
        // color de texto blanco
      }

      void loop() {
        float volt = analogRead(POT) * 3.3 / 4095;
        // borrá, poné el cursor arriba a la izquierda,
        // escribí la tensión y mostralo
        delay(100);
      }
      ''', '''
      #include <Wire.h>
      #include <Adafruit_SH110X.h>

      const int POT = 32;
      Adafruit_SH1106G display = Adafruit_SH1106G(128, 64, &Wire);

      void setup() {
        Serial.begin(115200);
        display.begin(0x3C, true);
        display.setTextColor(SH110X_WHITE);
      }

      void loop() {
        float volt = analogRead(POT) * 3.3 / 4095;
        display.clearDisplay();
        display.setCursor(0, 0);
        display.printf("Tension: %.2f V", volt);
        display.display();
        delay(100);
      }
      ''', [
        C(r'display\.begin\s*\(\s*0x3C', 'Inicia el display en 0x3C', 'Iniciá el display con `display.begin(0x3C, true)`'),
        C(r'display\.clearDisplay\s*\(\s*\)', 'Borra la pantalla', 'Borrá con `display.clearDisplay()` antes de escribir'),
        C(r'display\.setCursor\s*\(\s*0\s*,\s*0\s*\)', 'Pone el cursor arriba', 'Poné el cursor con `display.setCursor(0, 0)`'),
        C(r'display\.(print|println|printf)\s*\(', 'Escribe el valor', 'Escribí con `display.print(...)` o `display.printf(...)`'),
        C(r'display\.display\s*\(\s*\)', 'Lo muestra', 'Sin `display.display()` no se ve nada'),
      ], respuestas=[OP('¿Por qué protocolo va el display?', ['UART', 'I2C', 'SPI'], 'I2C', 'SDA y SCL, librería Wire.')],
      pasos=['En el setup: `display.begin(0x3C, true)` y el color.', 'En el loop: clearDisplay, setCursor, print y display().'],
      pistas=['Es el caso «Display_con_Pote» del profe.']),
  ]))

# ======================= 6 · Redes y la nube =======================
partes.append(parte(6, 'redes', 'WiFi, MQTT y la nube', 'Redes y nube',
  'La ESP32 se conecta al WiFi (STA) o crea su red (AP). Desde ahí: servidor web por HTTP, datos a ThingSpeak con la API key, o MQTT con un broker (puerto 1883).',
  {
    'que': 'Con el WiFi integrado, la ESP32 se conecta a una red (modo **STA**) o crea la suya (**AP**), y desde ahí habla con la nube: como **servidor web**, mandando datos por **HTTP** a ThingSpeak, o con **MQTT** a través de un broker.\n'
           'En el parcial se pregunta qué protocolo conviene para qué y cómo funciona cada plataforma; en el TP se usa todo junto.',
    'consta': [
      ['Conectarse al WiFi', '`WiFi.begin(ssid, password)` y esperar `WL_CONNECTED`. Hacen falta el SSID y la contraseña.'],
      ['TCP o UDP', 'TCP: con conexión, ordenado y sin errores. UDP: sin conexión, rápido, para telemetría.'],
      ['HTTP y el servidor web', '`WiFiServer server(80)`: el navegador manda un GET (/ledon) y la ESP32 responde con HTML.'],
      ['MQTT', 'Publicador/suscriptor por topics, con un broker (Mosquitto) en el puerto 1883 (8883 con TLS). Librería PubSubClient.'],
      ['Las plataformas', 'ThingSpeak (canales de 8 campos, API key), Arduino IoT Cloud (Device Key) y bots de Telegram (TOKEN de @BotFather).'],
      ['Seguridad', 'Aceleradores de cifrado (AES, SHA, RSA), secure boot y cifrado del firmware.'],
    ],
    'ejemplo': ejemplo('mqtt.ino', 'Sketch F del resumen: publicar y suscribirse', '''
      #include <WiFi.h>
      #include <PubSubClient.h>
      WiFiClient esp;  PubSubClient client(esp);    // MQTT va sobre TCP «2»
      void setup() {
        WiFi.begin(ssid, password);                 // 1) el WiFi «1»
        while (WiFi.status() != WL_CONNECTED) delay(500); «1»
        client.setServer(broker, 1883);             // 2) el broker «4»
        client.setCallback(callback);               // 3) lo que llega «4»
      }
      void loop() {
        if (!client.connected()) {
          client.connect("esp-a");                  // un id único por placa «4»
          client.subscribe("casa/luz");             // escucha un topic «4»
        }
        client.loop();
        client.publish("casa/temp", "23.5");        // publica en otro «4»
        // un servidor web: WiFiServer server(80) y el navegador pide /ledon «3»
        // ThingSpeak: ThingSpeak.setField(1, t); ThingSpeak.writeFields(canal, apiKey); «5»
        // con TLS (puerto 8883) los datos viajan cifrados «6»
      }
    ''', 'cpp'),
    'ojo': ['UDP no garantiza la entrega: conviene cuando perder un dato no importa.',
            'Para ver la página de la ESP32, el navegador tiene que estar en la misma red (o la placa, con IP pública).',
            'Nunca subas el SSID, la contraseña o la API key a un repositorio: van en un secrets.h aparte.'],
    'parcial': 'MQTT, TCP y UDP, ThingSpeak, Telegram y los modos del WiFi salen como opción múltiple. En el TP se usa todo junto: ThingSpeak y la programación OTA.',
    'pdf': 5,
  },
  [
    cod_ej('6.1', 'WiFi', 'conectarse al WiFi', 'Conectá la ESP32 al WiFi y mostrá su IP en el monitor serie. Mientras no esté conectada, imprimí un punto cada medio segundo.',
      '''
      // conectate al WiFi (incluí la librería)

      const char* ssid = "TU_RED_WIFI";
      const char* password = "TU_CLAVE";

      void setup() {
        Serial.begin(115200);
        // 1) empezá la conexión
        // 2) esperá hasta que esté conectada (un punto cada 500 ms)
        // 3) mostrá la IP
      }

      void loop() {
      }
      ''', '''
      #include <WiFi.h>

      const char* ssid = "TU_RED_WIFI";
      const char* password = "TU_CLAVE";

      void setup() {
        Serial.begin(115200);
        WiFi.begin(ssid, password);
        while (WiFi.status() != WL_CONNECTED) {
          delay(500);
          Serial.print(".");
        }
        Serial.println(WiFi.localIP());
      }

      void loop() {
      }
      ''', [
        C(r'#include\s*[<"]WiFi\.h[>"]', 'Incluye WiFi.h', 'Incluí la librería: `#include <WiFi.h>`'),
        C(r'WiFi\.begin\s*\(\s*ssid\s*,\s*password\s*\)', 'Empieza la conexión', 'Empezá con `WiFi.begin(ssid, password)`'),
        C(r'while\s*\(\s*WiFi\.status\s*\(\s*\)\s*!=\s*WL_CONNECTED\s*\)', 'Espera a estar conectada', 'Esperá con `while (WiFi.status() != WL_CONNECTED)`'),
        C(r'WiFi\.localIP\s*\(\s*\)', 'Muestra la IP', 'Mostrá la IP con `WiFi.localIP()`'),
      ], respuestas=[OP('¿En qué modo está la ESP32?', ['STA (estación)', 'AP (punto de acceso)'], 'STA (estación)', 'Se conecta al router como un celular.'),
        N('¿En qué banda trabaja el WiFi de la ESP32?', 2.4, 1, 'GHz')],
      pasos=['`#include <WiFi.h>`.', '`WiFi.begin(ssid, password);`', 'Un while hasta `WL_CONNECTED`.'],
      pistas=['Es lo primero de todos los casos del profe con WiFi.']),
    cod_ej('6.2', 'ThingSpeak', 'mandar datos a ThingSpeak', 'Mandá a ThingSpeak la tensión del potenciómetro en el campo 1 y la temperatura del DHT22 en el campo 2, **cada 16 segundos y sin `delay()`** (como pide el TPI). El WiFi ya está conectado en el setup.',
      '''
      #include <WiFi.h>
      #include "ThingSpeak.h"
      #include "DHT.h"

      unsigned long canal = 0;                  // el número de tu canal
      const char* writeAPIKey = "TU_API_KEY";
      WiFiClient client;
      DHT dht(33, DHT22);
      unsigned long antes = 0;

      void setup() {
        Serial.begin(115200);
        WiFi.begin("TU_RED_WIFI", "TU_CLAVE");
        while (WiFi.status() != WL_CONNECTED) delay(500);
        dht.begin();
        // iniciá ThingSpeak con el cliente WiFi
      }

      void loop() {
        // cada 16000 ms: cargá los dos campos y escribilos en el canal
      }
      ''', '''
      #include <WiFi.h>
      #include "ThingSpeak.h"
      #include "DHT.h"

      unsigned long canal = 0;                  // el número de tu canal
      const char* writeAPIKey = "TU_API_KEY";
      WiFiClient client;
      DHT dht(33, DHT22);
      unsigned long antes = 0;

      void setup() {
        Serial.begin(115200);
        WiFi.begin("TU_RED_WIFI", "TU_CLAVE");
        while (WiFi.status() != WL_CONNECTED) delay(500);
        dht.begin();
        ThingSpeak.begin(client);
      }

      void loop() {
        if (millis() - antes >= 16000) {
          antes = millis();
          float volt = analogRead(32) * 3.3 / 4095;
          float temp = dht.readTemperature();
          ThingSpeak.setField(1, volt);
          ThingSpeak.setField(2, temp);
          int x = ThingSpeak.writeFields(canal, writeAPIKey);
          Serial.println(x == 200 ? "Canal actualizado" : "Error " + String(x));
        }
      }
      ''', [
        C(r'ThingSpeak\.begin\s*\(\s*client\s*\)', 'Inicia ThingSpeak', 'Iniciá con `ThingSpeak.begin(client)` en el setup'),
        C(r'ThingSpeak\.setField\s*\(\s*1\s*,', 'Carga el campo 1', 'Cargá el potenciómetro con `ThingSpeak.setField(1, ...)`'),
        C(r'ThingSpeak\.setField\s*\(\s*2\s*,', 'Carga el campo 2', 'Cargá la temperatura con `ThingSpeak.setField(2, ...)`'),
        C(r'ThingSpeak\.writeFields\s*\(\s*canal\s*,\s*writeAPIKey\s*\)', 'Escribe el canal', 'Escribí con `ThingSpeak.writeFields(canal, writeAPIKey)`'),
        C(r'millis\s*\(\s*\)\s*-\s*antes\s*>=?\s*16000', 'Cada 16 s con millis', 'Usá `if (millis() - antes >= 16000)`'),
        NO(r'\bdelay\s*\(\s*16000', 'Sin delay de 16 s', 'Sin `delay(16000)`: usá millis'),
      ], respuestas=[N('¿Cuántos campos de datos tiene un canal?', 8, 0), N('¿Qué devuelve writeFields si salió bien?', 200, 0, motivo='El código HTTP de éxito.')],
      pasos=['`ThingSpeak.begin(client)` en el setup.', 'En el loop, con millis cada 16000 ms: `setField(1, ...)`, `setField(2, ...)` y `writeFields(canal, writeAPIKey)`.'],
      pistas=['Con `setField` se cargan varios campos y con `writeFields` se mandan juntos; `writeField` (sin s) manda uno solo.', 'La cuenta gratis de ThingSpeak no acepta datos más seguido que cada 15 s.']),
    cod_ej('6.3', 'MQTT', 'publicar y suscribirse con MQTT', 'Completá el cliente MQTT: el broker en el puerto 1883, la función que recibe los mensajes, la reconexión suscribiéndose a `casa/luz` y la publicación de la temperatura en `casa/temp`.',
      '''
      #include <WiFi.h>
      #include <PubSubClient.h>

      const char* broker = "192.168.0.14";   // la PC con Mosquitto
      WiFiClient esp;
      PubSubClient client(esp);

      void callback(char* topic, byte* mensaje, unsigned int largo) {
        // llegó un mensaje de un topic al que estamos suscriptos
      }

      void setup() {
        Serial.begin(115200);
        WiFi.begin("TU_RED_WIFI", "TU_CLAVE");
        while (WiFi.status() != WL_CONNECTED) delay(500);
        // el broker (puerto 1883) y la función que recibe
      }

      void loop() {
        // si se desconectó: conectate con un id y suscribite a "casa/luz"
        // atendé los mensajes
        // publicá la temperatura en "casa/temp"
        delay(5000);
      }
      ''', '''
      #include <WiFi.h>
      #include <PubSubClient.h>

      const char* broker = "192.168.0.14";   // la PC con Mosquitto
      WiFiClient esp;
      PubSubClient client(esp);

      void callback(char* topic, byte* mensaje, unsigned int largo) {
        // llegó un mensaje de un topic al que estamos suscriptos
      }

      void setup() {
        Serial.begin(115200);
        WiFi.begin("TU_RED_WIFI", "TU_CLAVE");
        while (WiFi.status() != WL_CONNECTED) delay(500);
        client.setServer(broker, 1883);
        client.setCallback(callback);
      }

      void loop() {
        if (!client.connected()) {
          client.connect("esp-a");
          client.subscribe("casa/luz");
        }
        client.loop();
        client.publish("casa/temp", "23.5");
        delay(5000);
      }
      ''', [
        C(r'client\.setServer\s*\(\s*broker\s*,\s*1883\s*\)', 'El broker en el 1883', 'Configurá el broker: `client.setServer(broker, 1883)`'),
        C(r'client\.setCallback\s*\(\s*callback\s*\)', 'La función que recibe', 'Falta `client.setCallback(callback)`'),
        C(r'!\s*client\.connected\s*\(\s*\)', 'Se fija si está conectado', 'Fijate si se desconectó: `if (!client.connected())`'),
        C(r'client\.connect\s*\(\s*"', 'Se conecta con un id', 'Conectate con un id: `client.connect("esp-a")`'),
        C(r'client\.subscribe\s*\(\s*"casa/luz"\s*\)', 'Se suscribe a casa/luz', 'Suscribite: `client.subscribe("casa/luz")`'),
        C(r'client\.loop\s*\(\s*\)', 'Atiende los mensajes', 'Sin `client.loop()` no llegan los mensajes'),
        C(r'client\.publish\s*\(\s*"casa/temp"', 'Publica en casa/temp', 'Publicá: `client.publish("casa/temp", ...)`'),
      ], respuestas=[N('Puerto estándar de MQTT', 1883, 0), N('Puerto de MQTT con TLS', 8883, 0),
        OP('¿Quién recibe y reparte los mensajes?', ['El broker', 'El publicador', 'El suscriptor'], 'El broker', 'Por ejemplo, Mosquitto en la PC.')],
      pasos=['En el setup: `setServer` y `setCallback`.', 'En el loop: reconectar y suscribirse, `client.loop()` y `publish`.'],
      pistas=['Es el sketch F del resumen y el caso «MQTT_Publicar_Mosquitto» del profe.', 'El id del cliente tiene que ser único: dos placas con el mismo id se desconectan entre sí.']),
    elegir_ej('6.4', 'Protocolos de red', '¿qué protocolo es?', '¿De qué protocolo es cada frase?', ['TCP', 'UDP', 'HTTP', 'MQTT', 'WebSockets'], [
      ('Orientado a conexión: entrega ordenada y sin errores', 'TCP', 'Usa más memoria y CPU.'),
      ('Sin conexión, «dispara y olvida»: ideal para telemetría', 'UDP', 'Si se pierde un paquete, no importa.'),
      ('El navegador pide /ledon con un GET y la ESP32 responde con HTML', 'HTTP', 'El servidor web en el puerto 80.'),
      ('Publicador/suscriptor por topics, con un broker', 'MQTT', 'Liviano, para miles de dispositivos.'),
      ('Una conexión persistente y bidireccional, en tiempo real', 'WebSockets', 'Para paneles de control.'),
      ('Ideal para conexiones inestables y muchos dispositivos', 'MQTT', 'Por eso es el de IoT.'),
      ('ThingSpeak recibe los datos así, con la API key', 'HTTP', 'La ESP32 como cliente.'),
    ], pregunta='¿Cuál es?'),
    elegir_ej('6.5', 'Plataformas', '¿qué plataforma es?', 'Las plataformas de los prácticos. ¿De cuál es cada frase?', ['ThingSpeak', 'Arduino IoT Cloud', 'Bot de Telegram'], [
      ('Canales con 8 campos de datos', 'ThingSpeak', 'Más 3 de ubicación y 1 de estado.'),
      ('Gráficos y análisis con MATLAB', 'ThingSpeak', 'Es de MathWorks.'),
      ('Se crea con @BotFather (/newbot), que da el TOKEN', 'Bot de Telegram', 'Pregunta del banco.'),
      ('Librería UniversalTelegramBot', 'Bot de Telegram', 'Se manda la orden desde el celular.'),
      ('Un dashboard web para prender el LED; la placa se identifica con su Device Key', 'Arduino IoT Cloud', 'Librerías ArduinoIoTCloud y Arduino_ConnectionHandler.'),
      ('Se mandan los datos por HTTP con la API key', 'ThingSpeak', 'Con ThingSpeak.writeFields.'),
    ], pregunta='¿De cuál es?'),
    elegir_ej('6.6', 'Banco', 'redes, Bluetooth y seguridad (preguntas del banco)', 'Opciones de las preguntas del banco sobre redes, Bluetooth y seguridad. ¿Son correctas?', CI, [
      ('Para conectarse a una red WiFi hacen falta, como mínimo, el SSID y la contraseña', 'Correcta', 'Con WiFi.begin(ssid, password).'),
      ('En modo AP la ESP32 crea su propia red', 'Correcta', 'También existe el modo mixto (STA + AP).'),
      ('Para ver la página del servidor web de la ESP32 alcanza con cualquier conexión a internet', 'Incorrecta', 'El navegador tiene que estar en la misma red local (o la placa con IP pública).'),
      ('UDP garantiza que los paquetes lleguen en orden', 'Incorrecta', 'Eso es TCP.'),
      ('En MQTT los mensajes se organizan en topics', 'Correcta', 'Ej.: casa/temp.'),
      ('BLE está pensado para muy bajo consumo; sus roles son central y periférico', 'Correcta', 'Los datos van en GATT.'),
      ('Los sistemas embebidos son vulnerables por sus recursos limitados y sus ciclos de vida largos', 'Correcta', 'Y por la exposición física.'),
      ('La ESP32 tiene aceleradores de cifrado por hardware', 'Correcta', 'AES, SHA, RSA y un generador de números aleatorios.'),
    ], pregunta='¿La marcarías?'),
  ]))

guardar(os.path.join(RAIZ, 'practica', 'tpa-p3', 'ejercicios.json'), 'IoT · 3º parcial', partes)
