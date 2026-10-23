# Arma practica/tpa-tp/ejercicios.json: la Práctica del TP de TPA (la ESP32 de la cátedra).
# Los ejercicios son de tipo "esp32": el sketch corre en la placa simulada de la página (practica/esp32/esp32.js) y
# Verificar corre las "pruebas" (aprieta el pulsador, mueve el pote, manda por el monitor serie… en momentos fijos) y
# compara lo que pasó. Al lado del sketch van los casos resueltos del profe que sirven de base: se copian del ZIP
# (con las claves ya tapadas) a practica/esp32/profe/.
# Desde la raíz:  python3 herramientas/tpa-practica/armar_tp.py  y después  node herramientas/tpa-practica/validar.js
import json, os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import RAIZ, MAT, j, ejemplo, C, NO, mostrar, guardar

ZIP = os.path.join(MAT, 'tp-esp32', 'casos-resueltos-del-profe.zip')
PROFE = os.path.join(RAIZ, 'practica', 'esp32', 'profe')
# Los del profe que se usan: nombre en la página → ruta en el ZIP (y los .h que necesita para correr)
DEL_PROFE = {
    'caso_01_led_interno.ino': 'casos/caso_01_led_interno.ino',
    'caso_02_aumentar_disminuir_led_externo.ino': 'casos/caso_02_aumentar_disminuir_led_externo.ino',
    'caso_03_control_led_verde_azul.ino': 'casos/caso_03_control_led_verde_azul.ino',
    'caso_04_leer_pot.ino': 'casos/caso_04_leer_pot.ino',
    'caso_05_rele_pote.ino': 'casos/caso_05_rele_pote.ino',
    'caso_06_led_on_off_relay.ino': 'casos/caso_06_led_on_off_relay.ino',
    'caso_07_display_led_externo_relay.ino': 'casos/caso_07_display_led_externo_relay.ino',
    'caso_08_aumentar_disminuir_led-externo.ino': 'casos/caso_08_aumentar_disminuir_led-externo.ino',
    'caso_09_sensor_touch.ino': 'casos/caso_09_sensor_touch.ino',
    'caso_10_display_sensor_tyh.ino': 'casos/caso_10_display_sensor_tyh.ino',
    'caso_13_thing_speak_tyh.ino': 'casos/caso_13_thing_speak_tyh.ino',
    'Pulsador_enciende_y_apaga_LED.ino': 'ejemplos/Pulsador_enciende_y_apaga_LED/Pulsador_enciende_y_apaga_LED.ino',
    'LED_con_Potenciometro_AnalogWrite.ino': 'ejemplos/Aumentar_y_disminuir_un_LED_con_Potenciometro_AnalogWrite/Aumentar_y_disminuir_un_LED_con_Potenciometro_AnalogWrite.ino',
    'Display_con_Pote.ino': 'ejemplos/Display_con_Pote/Display_con_Pote.ino',
    'Display_con_Pote/config.h': 'ejemplos/Display_con_Pote/config.h',
    'ThingSpeak_DHT_Ticker.ino': 'ejemplos/ThingSpeak_DHT_Ticker/ThingSpeak_DHT_Ticker.ino',
    'ThingSpeak_LeerDatos.ino': 'ejemplos/ThingSpeak_LeerDatos/ThingSpeak_LeerDatos.ino',
    'ThingSpeak_LeerDatos/secrets.h': 'ejemplos/ThingSpeak_LeerDatos/secrets.h',
    'MQTT_Publicar_Mosquitto.ino': 'ejemplos/MQTT_Publicar_Mosquitto/MQTT_Publicar_Mosquitto.ino',
    'MQTT_Suscriber_Mosquitto_graba_ThingSpeak.ino': 'ejemplos/MQTT_Suscriber_Mosquitto_graba_ThingSpeak/MQTT_Suscriber_Mosquitto_graba_ThingSpeak.ino',
    'Memoria_EEPROM.ino': 'ejemplos/Memoria_EEPROM/Memoria_EEPROM.ino',
}
NECESITA = {'Display_con_Pote.ino': ['Display_con_Pote/config.h'], 'ThingSpeak_LeerDatos.ino': ['ThingSpeak_LeerDatos/secrets.h']}
NOTAS = {
    'caso_09_sensor_touch.ino': 'Sus umbrales (950 y 850) son de otra placa: en el simulador el touch lee 72 suelto y 10 tocado.',
    'caso_13_thing_speak_tyh.ino': 'Manda con delay(2000) + delay(14000): 16 s entre envíos.',
    'ThingSpeak_LeerDatos.ino': 'Las claves están en secrets.h (también tapadas).',
}

def copiar_profe():
    z = zipfile.ZipFile(ZIP)
    raiz = z.namelist()[0].split('/')[0]
    lista = []
    for nombre, ruta in DEL_PROFE.items():
        texto = z.read(f'{raiz}/{ruta}').decode('utf-8').replace('\r\n', '\n')
        assert 'TU_' in texto or not any(k in texto for k in ('APIKey', 'password', 'SECRET', 'token')), nombre
        destino = os.path.join(PROFE, nombre)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        open(destino, 'w', encoding='utf-8').write(texto)
        a = {'nombre': nombre}
        if nombre in NECESITA: a['h'] = NECESITA[nombre]
        if nombre in NOTAS: a['nota'] = NOTAS[nombre]
        lista.append(a)
    json.dump(lista, open(os.path.join(PROFE, 'archivos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('practica/esp32/profe ·', len(lista), 'archivos del profe')

# ---------- Las pruebas: { nombre, hasta (ms), entradas: [{ t, boton | pote | dht | touch | serial | mqtt }], opts, esperar }
def P(nombre, hasta, esperar, entradas=(), **opts):
    p = {'nombre': nombre, 'hasta': hasta}
    if entradas: p['entradas'] = list(entradas)
    if opts: p['opts'] = opts
    p['esperar'] = list(esperar)
    return p
def _k(k, **x): return {'k': k, **{a: b for a, b in x.items() if b is not None}}
pin = lambda p, t, v, **x: _k('pin', pin=p, t=t, v=v, **x)
pwm = lambda p, t, v, tol=None, **x: _k('pwm', pin=p, t=t, v=v, tol=tol, **x)
brillo = lambda p, t, v, tol=None, **x: _k('brillo', pin=p, t=t, v=v, tol=tol, **x)
periodo = lambda p, ms, tol=None, **x: _k('periodo', pin=p, ms=ms, tol=tol, **x)
cambios = lambda p, **x: _k('cambios', pin=p, **x)
recorre = lambda p, de, a, **x: _k('recorre', pin=p, de=de, a=a, **x)
serial = lambda re, **x: _k('serial', re=re, **x)
display = lambda re, **x: _k('display', re=re, **x)
ts = lambda **x: _k('ts', **x)
mqtt = lambda **x: _k('mqtt', **x)
eeprom = lambda d, v, **x: _k('eeprom', dir=d, v=v, **x)
apretar = lambda t, hasta: [{'t': t, 'boton': True}, {'t': hasta, 'boton': False}]
tocar = lambda p, t, hasta: [{'t': t, 'touch': {str(p): 10}}, {'t': hasta, 'touch': {str(p): 72}}]

def N(pregunta, valor, dec=0, unidad=None, motivo=None, tol=None, medir=None):
    """Una respuesta numérica. medir: cómo sale en la placa ({opts, entradas, hasta, re}): validar.js corre la
    solución así y compara el último número que agarra la expresión con el valor"""
    x = {k: v for k, v in {'pregunta': pregunta, 'valor': valor, 'unidad': unidad, 'motivo': motivo, 'medir': medir}.items() if v is not None}
    x['tol'] = tol if tol is not None else 10 ** -dec
    x['mostrar'] = mostrar(valor, dec)
    return x
def OP(pregunta, opciones, valor, motivo=None):
    assert valor in opciones
    return {k: v for k, v in {'pregunta': pregunta, 'opciones': list(opciones), 'valor': valor, 'motivo': motivo, 'mostrar': valor}.items() if v is not None}

def codigo(s):
    """El sketch: los pedazos escritos adentro de esp(...) tienen 6 espacios de sangría y los de arriba (DISPLAY, WIFI…), ninguna"""
    s = '\n'.join(l[6:] if l.startswith('      ') else l.rstrip() for l in s.split('\n'))
    while '\n\n\n' in s: s = s.replace('\n\n\n', '\n\n')
    return s.strip('\n') + '\n'

def esp(id, tema, titulo, consigna, inicial, solucion, pruebas, profe=(), checks=(), respuestas=(), pasos=(), pistas=(), placa=None):
    for a in profe: assert a in DEL_PROFE, a
    e = {'id': id, 'tema': tema, 'titulo': titulo, 'tipo': 'esp32', 'lenguaje': 'cpp', 'consigna': j(consigna).strip()}
    if pasos: e['pasos'] = list(pasos)
    if pistas: e['pistas'] = list(pistas)
    e['archivos'] = [{'nombre': 'sketch.ino', 'inicial': codigo(inicial), 'solucion': codigo(solucion)}]
    if profe: e['delProfe'] = list(profe)
    if placa: e['placa'] = placa
    e['pruebas'] = list(pruebas)
    if checks: e['checks'] = list(checks)
    if respuestas: e['respuestas'] = list(respuestas)
    return e

def parte(n, id, titulo, pestana, explicacion, leccion, ejercicios):
    for e in ejercicios: e['parte'] = n
    leccion = {**leccion, 'parcialT': 'En el TP'}
    return {'n': n, 'id': id, 'titulo': titulo, 'explicacion': explicacion, 'corto': pestana, 'pestana': pestana, 'leccion': leccion, 'ejercicios': ejercicios}

WIFI = '''
const char* ssid = "TU_RED_WIFI";     // tu red (en el simulador conecta con cualquiera)
const char* password = "TU_CLAVE_WIFI";
'''
CONECTAR = '''
void conectarWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi conectado: ");
  Serial.println(WiFi.localIP());
}
'''
CANAL = {'1234567': {'1': 321, '2': 24.5, '3': 55, '4': 120, '5': 2048, '6': 40}}

partes = []

# ======================= 1 · LEDs y relé =======================
partes.append(parte(1, 'salidas', 'Salidas: LEDs y relé', 'LEDs y relé',
  'setup() corre una vez y loop() se repite sin fin. pinMode(pin, OUTPUT) y digitalWrite(pin, HIGH/LOW) prenden y apagan; delay(ms) espera. LED azul en el GPIO 2, verde en el 23 y relé en el 14.',
  {
    'que': 'Un sketch tiene dos funciones: **setup()** corre una vez al prender la placa y **loop()** se repite para siempre. Para prender un LED: el pin como salida con **pinMode(pin, OUTPUT)** y **digitalWrite(pin, HIGH)**. **delay(ms)** frena todo el programa esos milisegundos.\n'
           'En la placa de la cátedra: el **LED azul** (el integrado) en el GPIO **2**, el **LED verde** en el **23** y el **relé** en el **14**. El monitor serie (Serial) es la ventana para mandar y recibir texto desde la PC.',
    'consta': [
      ['Los pines', '`const int LED = 2;` arriba de todo: si cambia el pin, se cambia en un solo lugar.'],
      ['setup()', 'Corre una vez: `Serial.begin(115200)` y `pinMode(LED, OUTPUT)`.'],
      ['loop()', 'Se repite sin fin: `digitalWrite(LED, HIGH)`, `delay`, `digitalWrite(LED, LOW)`, `delay`.'],
      ['El monitor serie', '`Serial.println("texto")` manda; `Serial.available()` dice si llegó algo y `Serial.read()` lo lee.'],
    ],
    'ejemplo': ejemplo('blink.ino', 'El caso 1 del profe, comentado', '''
      const int LED_INT = 2;           // el LED azul «1»
      void setup() {
        Serial.begin(9600);            // la velocidad del monitor serie «2»
        Serial.println("Hello, ESP32!");  «4»
        pinMode(LED_INT, OUTPUT);      «2»
      }
      void loop() {
        digitalWrite(LED_INT, HIGH);   «3»
        delay(1000);                   «3»
        digitalWrite(LED_INT, LOW);    «3»
        delay(1000);                   «3»
      }
    ''', 'cpp'),
    'ojo': ['Sin `pinMode(pin, OUTPUT)` el LED no prende (en el simulador, avisa).',
            '`delay(1000)` son 1000 ms = 1 s, y mientras dura la placa no hace nada más.',
            'El monitor serie tiene que estar a la misma velocidad que `Serial.begin` (115200 o 9600): si no, se ven símbolos raros.',
            'Lo que mandás por el monitor serie llega con un salto de línea al final (`\\n`): también es un carácter.'],
    'parcial': 'Los casos 1, 3 y 6 de los Prácticos. En el TPI, el LED azul (integrado) y el verde (externo) se manejan con PWM, en la parte 3.',
  },
  [
    esp('1.1', 'Parpadeo', 'el LED azul titila', '''
      Hacé titilar el **LED azul** (GPIO 2): **300 ms prendido y 300 ms apagado**. Al arrancar, que el monitor serie muestre `Hola, ESP32!` una sola vez.

      El caso 1 del profe hace lo mismo cada 1 s: está en la pestaña de al lado. Con esa pestaña abierta, **▶ Ejecutar** lo corre en la placa.
    ''', '''
      const int LED = 2;   // LED azul (integrado)

      void setup() {
        Serial.begin(115200);
        // Configurá el pin del LED como salida y saludá por el monitor serie

      }

      void loop() {
        // Prendé el LED, esperá 300 ms, apagalo y esperá otros 300 ms

      }
    ''', '''
      const int LED = 2;   // LED azul (integrado)

      void setup() {
        Serial.begin(115200);
        pinMode(LED, OUTPUT);
        Serial.println("Hola, ESP32!");
      }

      void loop() {
        digitalWrite(LED, HIGH);
        delay(300);
        digitalWrite(LED, LOW);
        delay(300);
      }
    ''', [P('La placa corre 4 s', 4000, [pin(2, 150, 1), pin(2, 450, 0), periodo(2, 600, 40), serial(r'Hola, ESP32!', veces=[1, 1])])],
    profe=['caso_01_led_interno.ino'],
    pasos=['En `setup()`: `pinMode(LED, OUTPUT);` y `Serial.println("Hola, ESP32!");` (en el setup sale una sola vez).',
           'En `loop()`: `digitalWrite(LED, HIGH); delay(300); digitalWrite(LED, LOW); delay(300);`',
           '▶ Ejecutar: mirá el LED azul en la pestaña Placa y el saludo en el monitor serie.'],
    pistas=['Lo que va en `setup()` pasa una sola vez; lo de `loop()`, siempre.', 'Son cuatro líneas en el loop: prender, esperar, apagar, esperar.'],
    respuestas=[N('Veces que titila por segundo', 1.67, 2, 'Hz', 'Un ciclo dura 300 + 300 = 600 ms: 1000 / 600 = 1,67 por segundo.', tol=0.02)]),

    esp('1.2', 'Comandos de una letra', 'v y a por el monitor serie', '''
      Por el monitor serie: con `v` se prende el **LED verde** (GPIO 23) y se apaga el azul; con `a`, al revés: azul prendido y verde apagado. Que acepte también `V` y `A`. Cualquier otra cosa no cambia nada.

      Es el caso 3 de los Prácticos. Probalo: ▶ Ejecutar y escribí `v` en el monitor serie de la placa.
    ''', '''
      const int VERDE = 23;
      const int AZUL = 2;

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
        pinMode(AZUL, OUTPUT);
      }

      void loop() {
        if (Serial.available() > 0) {
          char c = Serial.read();
          // Si es 'v' o 'V': verde prendido y azul apagado
          // Si es 'a' o 'A': azul prendido y verde apagado

        }
      }
    ''', '''
      const int VERDE = 23;
      const int AZUL = 2;

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
        pinMode(AZUL, OUTPUT);
      }

      void loop() {
        if (Serial.available() > 0) {
          char c = Serial.read();
          if (c == 'v' || c == 'V') {
            digitalWrite(VERDE, HIGH);
            digitalWrite(AZUL, LOW);
          } else if (c == 'a' || c == 'A') {
            digitalWrite(AZUL, HIGH);
            digitalWrite(VERDE, LOW);
          }
        }
      }
    ''', [P('Mandás v, después a y después V', 3000, [pin(23, 1000, 1), pin(2, 1000, 0), pin(23, 2000, 0), pin(2, 2000, 1), pin(23, 2900, 1), pin(2, 2900, 0)],
            entradas=[{'t': 500, 'serial': 'v\n'}, {'t': 1500, 'serial': 'a\n'}, {'t': 2500, 'serial': 'V\n'}]),
          P('Mandás a y después x: x no cambia nada', 1500, [pin(2, 1200, 1), pin(23, 1200, 0)],
            entradas=[{'t': 300, 'serial': 'a\n'}, {'t': 800, 'serial': 'x\n'}])],
    profe=['caso_03_control_led_verde_azul.ino'],
    pasos=['Los caracteres van entre comillas simples: `c == \'v\'`.', 'Con `||` (o) aceptás la mayúscula: `if (c == \'v\' || c == \'V\')`.',
           'Si no es ninguna de las dos, no hagas nada: así el salto de línea (`\\n`) que llega después no apaga nada.'],
    pistas=['Un `if` para la v, un `else if` para la a y nada más.'],
    respuestas=[OP('¿Cuántos caracteres llegan al mandar «v» con el monitor en «Nueva línea»?', ['1', '2', '3'], '2', 'La `v` y el salto de línea `\\n`: por eso la otra letra no tiene que cambiar nada.')]),

    esp('1.3', 'Comandos de texto', 'LUZ_ON y LUZ_OFF con el relé', '''
      Leé **comandos de texto** por el monitor serie (uno por línea): `LUZ_ON` prende el LED verde y cierra el **relé** (GPIO 14); `LUZ_OFF` apaga los dos. Respondé `OK` si el comando existe y `Comando desconocido` si no.

      Es el caso 6. El profe arma el texto letra por letra; acá usá `Serial.readStringUntil('\\n')`, que lee hasta el salto de línea.
    ''', '''
      const int VERDE = 23;
      const int RELE = 14;

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
        pinMode(RELE, OUTPUT);
      }

      void loop() {
        if (Serial.available() > 0) {
          String cmd = Serial.readStringUntil('\\n');
          cmd.trim();   // saca los espacios y el \\r del final
          // Compará cmd con "LUZ_ON" y "LUZ_OFF" y respondé por el monitor serie

        }
      }
    ''', '''
      const int VERDE = 23;
      const int RELE = 14;

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
        pinMode(RELE, OUTPUT);
      }

      void loop() {
        if (Serial.available() > 0) {
          String cmd = Serial.readStringUntil('\\n');
          cmd.trim();   // saca los espacios y el \\r del final
          if (cmd == "LUZ_ON") {
            digitalWrite(VERDE, HIGH);
            digitalWrite(RELE, HIGH);
            Serial.println("OK");
          } else if (cmd == "LUZ_OFF") {
            digitalWrite(VERDE, LOW);
            digitalWrite(RELE, LOW);
            Serial.println("OK");
          } else {
            Serial.println("Comando desconocido");
          }
        }
      }
    ''', [P('LUZ_ON y después LUZ_OFF', 2500, [pin(14, 1000, 1), pin(23, 1000, 1), pin(14, 2000, 0), pin(23, 2000, 0), serial(r'OK', veces=[2, 2])],
            entradas=[{'t': 500, 'serial': 'LUZ_ON\n'}, {'t': 1500, 'serial': 'LUZ_OFF\n'}]),
          P('Un comando que no existe', 1500, [serial(r'Comando desconocido'), pin(14, 1000, 0)], entradas=[{'t': 500, 'serial': 'HOLA\n'}])],
    profe=['caso_06_led_on_off_relay.ino'],
    pasos=['Los `String` se comparan con `==`: `if (cmd == "LUZ_ON")`.', 'Tres ramas: `if` LUZ_ON, `else if` LUZ_OFF y `else` para lo desconocido.'],
    pistas=['El relé es una salida digital más: `digitalWrite(RELE, HIGH)` lo cierra.', 'Sin `trim()`, en Windows el comando llega como "LUZ_ON\\r" y no es igual a "LUZ_ON".']),
  ]))

# ======================= 2 · Pulsador y potenciómetro =======================
partes.append(parte(2, 'entradas', 'Entradas: pulsador y potenciómetro', 'Pulsador y pote',
  'digitalRead lee HIGH o LOW (el pulsador del GPIO 19, con INPUT_PULLUP, da LOW apretado) y analogRead lee de 0 a 4095 (el pote del GPIO 32, 0 a 3,3 V).',
  {
    'que': '**digitalRead(pin)** lee HIGH o LOW. El pulsador de la placa (GPIO **19**) va a masa: con **INPUT_PULLUP** suelto lee HIGH y apretado lee **LOW**.\n'
           '**analogRead(pin)** lee una tensión de 0 a 3,3 V como un número de **0 a 4095** (el ADC es de 12 bits). El potenciómetro está en el GPIO **32**.',
    'consta': [
      ['INPUT_PULLUP', '`pinMode(19, INPUT_PULLUP)`: la resistencia interna lo deja en HIGH mientras está suelto.'],
      ['El flanco', 'Para contar pulsaciones se compara con la lectura anterior: HIGH → LOW es «recién apretado».'],
      ['analogRead', '0 a 4095. En voltios: `lectura * 3.3 / 4095`.'],
      ['El umbral', '`if (lectura > 2000)` decide con un límite, como el relé del caso 5.'],
    ],
    'ejemplo': ejemplo('entradas.ino', 'Pulsador y pote en un mismo loop', '''
      const int BOTON = 19, POTE = 32;
      int anterior = HIGH;                         «2»
      void setup() {
        Serial.begin(115200);
        pinMode(BOTON, INPUT_PULLUP);              «1»
      }
      void loop() {
        int ahora = digitalRead(BOTON);            «2»
        if (anterior == HIGH && ahora == LOW) {    «2»
          Serial.println("Apretado");              «2»
        }
        anterior = ahora;                          «2»
        int pote = analogRead(POTE);               «3»
        float volt = pote * 3.3 / 4095;            «3»
        if (pote > 2000) Serial.println("Alto");   «4»
        delay(20);
      }
    ''', 'cpp'),
    'ojo': ['Con INPUT_PULLUP, **apretado es LOW** (al revés de lo que uno espera).',
            'Si leés el botón sin compararlo con la lectura anterior, mientras lo mantenés apretado cuenta una vez por vuelta del loop.',
            'El pote va en el 32 (ADC1): el ADC2 (pines 0, 2, 4, 12–15, 25–27) no anda con el WiFi prendido.',
            'En `pote * 3.3 / 4095`, el `3.3` hace que la cuenta sea con decimales; `pote * 3 / 4095` sería entera.'],
    'parcial': 'Los casos 4 y 5, y el contador de pulsaciones del sketch 2 del TPI.',
  },
  [
    esp('2.1', 'analogRead', 'leer el potenciómetro', '''
      Cada **200 ms**, mostrá por el monitor serie la lectura del potenciómetro (GPIO 32) y su tensión, así: `Pote: 3000 = 2.42 V`.

      Después: ▶ Ejecutar, poné el pote en **1234** (escribilo en el número al lado del deslizador) y completá lo que muestra.
    ''', '''
      const int POTE = 32;

      void setup() {
        Serial.begin(115200);
      }

      void loop() {
        int lectura = 0;   // leé el pote
        float volt = 0;    // pasalo a voltios: 3,3 V es 4095
        Serial.print("Pote: ");
        Serial.print(lectura);
        Serial.print(" = ");
        Serial.print(volt);   // un float sale con 2 decimales
        Serial.println(" V");
        delay(200);
      }
    ''', '''
      const int POTE = 32;

      void setup() {
        Serial.begin(115200);
      }

      void loop() {
        int lectura = analogRead(POTE);
        float volt = lectura * 3.3 / 4095;
        Serial.print("Pote: ");
        Serial.print(lectura);
        Serial.print(" = ");
        Serial.print(volt);   // un float sale con 2 decimales
        Serial.println(" V");
        delay(200);
      }
    ''', [P('Pote en 1000 y después al máximo', 1500, [serial(r'Pote: 1000 = 0\.81 V', hasta=650), serial(r'Pote: 4095 = 3\.30 V', desde=750), serial(r'Pote: ', veces=[6, 9])],
            entradas=[{'t': 700, 'pote': 4095}], pote=1000)],
    profe=['caso_04_leer_pot.ino'],
    pasos=['`int lectura = analogRead(POTE);`', '`float volt = lectura * 3.3 / 4095;`', '▶ Ejecutar, pote en 1234, y leé la tensión en el monitor serie.'],
    pistas=['4095 es el máximo del ADC de 12 bits y corresponde a 3,3 V: es una regla de tres.'],
    respuestas=[N('Tensión con el pote en 1234', 0.99, 2, 'V', '1234 × 3,3 / 4095 = 0,994 V: `Serial.print` de un float muestra 2 decimales.', tol=0.011,
                  medir={'opts': {'pote': 1234}, 'hasta': 500, 're': r'= ([\d.]+) V'})]),

    esp('2.2', 'Umbral', 'el relé se cierra con el pote', '''
      Cuando el pote pasa de **2000**, cerrá el relé (GPIO 14) y prendé el LED verde (GPIO 23) como aviso; si no, abrí el relé y apagá el LED. Mostrá la lectura por el monitor serie cada 100 ms.

      Es el caso 5 del profe, con el LED de aviso.
    ''', '''
      const int POTE = 32;
      const int RELE = 14;
      const int VERDE = 23;
      const int LIMITE = 2000;

      void setup() {
        Serial.begin(115200);
        pinMode(RELE, OUTPUT);
        pinMode(VERDE, OUTPUT);
      }

      void loop() {
        int lectura = analogRead(POTE);
        // Decidí con el límite: relé y LED juntos

        Serial.println(lectura);
        delay(100);
      }
    ''', '''
      const int POTE = 32;
      const int RELE = 14;
      const int VERDE = 23;
      const int LIMITE = 2000;

      void setup() {
        Serial.begin(115200);
        pinMode(RELE, OUTPUT);
        pinMode(VERDE, OUTPUT);
      }

      void loop() {
        int lectura = analogRead(POTE);
        if (lectura > LIMITE) {
          digitalWrite(RELE, HIGH);
          digitalWrite(VERDE, HIGH);
        } else {
          digitalWrite(RELE, LOW);
          digitalWrite(VERDE, LOW);
        }
        Serial.println(lectura);
        delay(100);
      }
    ''', [P('El pote sube a 2500 y baja a 1500', 3000, [pin(14, 800, 0), pin(14, 1500, 1), pin(23, 1500, 1), pin(14, 2500, 0), pin(23, 2500, 0)],
            entradas=[{'t': 1000, 'pote': 2500}, {'t': 2000, 'pote': 1500}], pote=1000),
          P('Justo en 2000: queda abierto', 600, [pin(14, 500, 0)], pote=2000)],
    profe=['caso_05_rele_pote.ino'],
    pasos=['`if (lectura > LIMITE) { … } else { … }`', 'En cada rama, el relé y el LED con el mismo valor.'],
    respuestas=[N('Tensión del límite de 2000', 1.61, 2, 'V', '2000 × 3,3 / 4095 = 1,61 V.', tol=0.011)]),

    esp('2.3', 'El flanco', 'el pulsador prende y apaga', '''
      Cada vez que **apretás** el pulsador (GPIO 19), el **LED verde** cambia: si estaba apagado se prende, y al revés. Mantenerlo apretado cuenta **una sola vez**. En cada pulsación, mostrá `Pulsaciones: N`.
    ''', '''
      const int BOTON = 19;
      const int VERDE = 23;
      int anterior = HIGH;   // la lectura de la vuelta anterior
      bool prendido = false;
      int pulsaciones = 0;

      void setup() {
        Serial.begin(115200);
        pinMode(BOTON, INPUT_PULLUP);   // suelto = HIGH, apretado = LOW
        pinMode(VERDE, OUTPUT);
      }

      void loop() {
        int ahora = digitalRead(BOTON);
        // Si recién se apretó (antes HIGH y ahora LOW): cambiá el LED, contá y mostrá

        anterior = ahora;
        delay(20);
      }
    ''', '''
      const int BOTON = 19;
      const int VERDE = 23;
      int anterior = HIGH;   // la lectura de la vuelta anterior
      bool prendido = false;
      int pulsaciones = 0;

      void setup() {
        Serial.begin(115200);
        pinMode(BOTON, INPUT_PULLUP);   // suelto = HIGH, apretado = LOW
        pinMode(VERDE, OUTPUT);
      }

      void loop() {
        int ahora = digitalRead(BOTON);
        if (anterior == HIGH && ahora == LOW) {
          prendido = !prendido;
          digitalWrite(VERDE, prendido);
          pulsaciones++;
          Serial.print("Pulsaciones: ");
          Serial.println(pulsaciones);
        }
        anterior = ahora;
        delay(20);
      }
    ''', [P('Tres pulsaciones, la última de 1 s', 4000, [pin(23, 400, 0), pin(23, 900, 1), pin(23, 1900, 0), pin(23, 3800, 1), cambios(23, desde=2400, hasta=3900, min=1, max=1),
                                                       serial(r'Pulsaciones: 3'), serial(r'Pulsaciones: 4', no=True)],
            entradas=apretar(500, 700) + apretar(1500, 1700) + apretar(2500, 3500))],
    profe=['Pulsador_enciende_y_apaga_LED.ino'],
    pasos=['La condición del flanco: `if (anterior == HIGH && ahora == LOW)`.', 'Adentro: `prendido = !prendido;`, `digitalWrite(VERDE, prendido);`, `pulsaciones++;` y el print.'],
    pistas=['El ejemplo del profe cambia el LED al **soltar** (cuando vuelve a HIGH); acá va al apretar.', '`anterior = ahora;` ya está al final: guarda la lectura para la vuelta siguiente.'],
    respuestas=[OP('Con el pulsador apretado, digitalRead(19) da', ['HIGH (1)', 'LOW (0)'], 'LOW (0)', 'Con INPUT_PULLUP, apretado conecta el pin a masa.')]),
  ]))

# ======================= 3 · PWM =======================
partes.append(parte(3, 'pwm', 'PWM: el brillo', 'PWM',
  'analogWrite(pin, valor) da brillo: de 0 a 255 con 8 bits, o de 0 a 4095 con analogWriteResolution(pin, 12), como pide el TPI. map() pasa de una escala a la otra.',
  {
    'que': 'Un pin digital solo prende o apaga, pero si lo prende y apaga muy rápido el LED se ve más o menos brillante: eso es **PWM**. **analogWrite(pin, valor)** fija cuánto tiempo está prendido: con 8 bits va de **0** (apagado) a **255** (al máximo).\n'
           'Con **analogWriteResolution(pin, 12)** el rango pasa a **0–4095**, como pide el TPI. **map(x, 0, 4095, 0, 255)** pasa de una escala a otra.',
    'consta': [
      ['analogWrite', '`analogWrite(VERDE, 128)` ≈ 50 % de brillo con 8 bits.'],
      ['La resolución', '`analogWriteResolution(AZUL, 12)`: de 0 a 4095 (el TPI pide 12 bits).'],
      ['map()', '`map(valor, deMin, deMax, aMin, aMax)`: una regla de tres con enteros (corta los decimales).'],
      ['El porcentaje', '`brillo * 100 / maximo`, para mostrarlo.'],
    ],
    'ejemplo': ejemplo('pwm.ino', 'Los dos LEDs con el pote', '''
      const int VERDE = 23, AZUL = 2, POTE = 32;
      void setup() {
        analogWriteResolution(AZUL, 12);          «2»
      }
      void loop() {
        int pote = analogRead(POTE);              // 0 a 4095
        int pwm8 = map(pote, 0, 4095, 0, 255);    «3»
        analogWrite(VERDE, pwm8);                 «1»
        analogWrite(AZUL, pote);                  «2»
        int porc = pote * 100 / 4095;             «4»
        delay(20);
      }
    ''', 'cpp'),
    'ojo': ['`map()` trabaja con enteros: `map(3000, 0, 4095, 0, 255)` da 186, no 186,8.',
            'Con 8 bits, 255 es el máximo: `analogWrite(LED, 4095)` queda en 255.',
            '`analogWrite` y `digitalWrite` en el mismo pin se pisan: manda el último.',
            'En el core viejo de la ESP32 no había analogWrite: se usaba `ledcSetup` + `ledcAttachPin` + `ledcWrite` (el simulador acepta los dos).'],
    'parcial': 'Los casos 2 y 8. El TPI pide el LED integrado con el pote y el externo con los touch, los dos con 12 bits y mostrando el valor en el display.',
  },
  [
    esp('3.1', 'analogWrite', 'subir y bajar el brillo', '''
      Hacé que el **LED verde** suba de 0 a 255 de a 1, con `delay(4)` entre paso y paso, después baje de 255 a 0 igual, y que repita.

      El caso 2 del profe lo hace con `delay(5)` y una pausa de 1 s.
    ''', '''
      const int VERDE = 23;

      void setup() {
        pinMode(VERDE, OUTPUT);
      }

      void loop() {
        // Un for que sube de 0 a 255 y otro que baja de 255 a 0, con analogWrite y delay(4)

      }
    ''', '''
      const int VERDE = 23;

      void setup() {
        pinMode(VERDE, OUTPUT);
      }

      void loop() {
        for (int b = 0; b <= 255; b++) {
          analogWrite(VERDE, b);
          delay(4);
        }
        for (int b = 255; b >= 0; b--) {
          analogWrite(VERDE, b);
          delay(4);
        }
      }
    ''', [P('Corre 2,5 s', 2500, [recorre(23, 0, 255, valores=200, hasta=2040), pwm(23, 512, 128, tol=6), pwm(23, 1536, 127, tol=6)])],
    profe=['caso_02_aumentar_disminuir_led_externo.ino'],
    pasos=['`for (int b = 0; b <= 255; b++) { analogWrite(VERDE, b); delay(4); }`', 'El otro baja: `for (int b = 255; b >= 0; b--)`.'],
    respuestas=[N('Duración de una vuelta del loop (subir y bajar)', 2048, 0, 'ms', 'Cada for hace 256 pasos (de 0 a 255) de 4 ms: 2 × 256 × 4 = 2048 ms.', tol=10)]),

    esp('3.2', 'map()', 'el brillo sigue al pote', '''
      El brillo del **LED verde** sigue al pote: con `map()` pasá la lectura (0–4095) a PWM de 8 bits (0–255). Mostrá `PWM: N` cada 100 ms.

      Después: ▶ Ejecutar, pote en **3000**, y anotá el PWM.
    ''', '''
      const int VERDE = 23;
      const int POTE = 32;

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
      }

      void loop() {
        int lectura = analogRead(POTE);
        int pwm = 0;   // pasá la lectura a 0–255 con map
        // mandalo al LED y mostralo

        delay(100);
      }
    ''', '''
      const int VERDE = 23;
      const int POTE = 32;

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
      }

      void loop() {
        int lectura = analogRead(POTE);
        int pwm = map(lectura, 0, 4095, 0, 255);
        analogWrite(VERDE, pwm);
        Serial.print("PWM: ");
        Serial.println(pwm);
        delay(100);
      }
    ''', [P('Pote en 0, 4095 y 2048', 1600, [pwm(23, 400, 0), pwm(23, 900, 255), pwm(23, 1500, 127), serial(r'PWM: 255')],
            entradas=[{'t': 500, 'pote': 4095}, {'t': 1000, 'pote': 2048}], pote=0)],
    profe=['LED_con_Potenciometro_AnalogWrite.ino', 'caso_08_aumentar_disminuir_led-externo.ino'],
    pasos=['`int pwm = map(lectura, 0, 4095, 0, 255);`', '`analogWrite(VERDE, pwm);` y el print.'],
    respuestas=[N('PWM con el pote en 3000', 186, 0, None, '3000 × 255 / 4095 = 186,8 → 186: `map` corta los decimales.',
                  medir={'opts': {'pote': 3000}, 'hasta': 400, 're': r'PWM: (\d+)'})]),

    esp('3.3', '12 bits', 'el LED integrado con 12 bits, como el TPI', '''
      Como pide el TPI: el **LED azul** (GPIO 2, el integrado) con el pote y **12 bits**: `analogWriteResolution(2, 12)` y el valor del pote directo, sin `map`. Cada 200 ms mostrá `PWM: N (P %)`, con el porcentaje entero.
    ''', '''
      const int AZUL = 2;
      const int POTE = 32;

      void setup() {
        Serial.begin(115200);
        pinMode(AZUL, OUTPUT);
        // 12 bits para el LED azul

      }

      void loop() {
        int pwm = analogRead(POTE);
        // mandalo al LED, calculá el porcentaje y mostralo: PWM: 1024 (25 %)

        delay(200);
      }
    ''', '''
      const int AZUL = 2;
      const int POTE = 32;

      void setup() {
        Serial.begin(115200);
        pinMode(AZUL, OUTPUT);
        analogWriteResolution(AZUL, 12);
      }

      void loop() {
        int pwm = analogRead(POTE);
        analogWrite(AZUL, pwm);
        int porc = pwm * 100 / 4095;
        Serial.printf("PWM: %d (%d %%)\\n", pwm, porc);
        delay(200);
      }
    ''', [P('Pote en 1024 y al máximo', 1000, [pwm(2, 400, 1024), brillo(2, 400, 0.25, tol=0.01), pwm(2, 900, 4095), serial(r'PWM: 1024 \(25 %\)')],
            entradas=[{'t': 500, 'pote': 4095}], pote=1024)],
    profe=['LED_con_Potenciometro_AnalogWrite.ino'],
    pasos=['En el setup: `analogWriteResolution(AZUL, 12);`', 'En el loop: `analogWrite(AZUL, pwm);` y `int porc = pwm * 100 / 4095;`',
           'Con printf, el % literal se escribe `%%`: `Serial.printf("PWM: %d (%d %%)\\n", pwm, porc);`'],
    respuestas=[N('Porcentaje con el pote en 2500', 61, 0, '%', '2500 × 100 / 4095 = 61,05 → 61 (división entera).',
                  medir={'opts': {'pote': 2500}, 'hasta': 400, 're': r'PWM: \d+ \((\d+) %\)'})]),
  ]))

# ======================= 4 · Display =======================
DISPLAY = '''
#include <Wire.h>
#include <Adafruit_SH110X.h>

Adafruit_SH1106G display = Adafruit_SH1106G(128, 64, &Wire, -1);
'''
partes.append(parte(4, 'display', 'El display OLED', 'Display',
  'OLED SH1106 de 128 × 64 por I2C (0x3C), con Adafruit_SH110X: clearDisplay, setCursor y print dibujan en memoria, y display.display() lo muestra.',
  {
    'que': 'El display de la placa es un **OLED SH1106 de 128 × 64** por **I2C** (dirección **0x3C**). Con la librería **Adafruit_SH110X** se dibuja en memoria (clearDisplay, setCursor, print) y **display.display()** lo manda a la pantalla. Sin display() no se ve nada.',
    'consta': [
      ['El objeto', '`Adafruit_SH1106G display = Adafruit_SH1106G(128, 64, &Wire, -1);` arriba de todo.'],
      ['begin', '`display.begin(0x3C, true)` en el setup, y `setTextSize(1)` / `setTextColor(SH110X_WHITE)`.'],
      ['Dibujar', '`clearDisplay()` borra, `setCursor(x, y)` ubica (en píxeles) y `print` / `println` / `printf` escriben. Con tamaño 1, cada letra ocupa 6 × 8 píxeles.'],
      ['Mostrar', '`display.display()` pasa todo a la pantalla de una vez.'],
    ],
    'ejemplo': ejemplo('display.ino', 'Lo mínimo para escribir', '''
      #include <Wire.h>
      #include <Adafruit_SH110X.h>
      Adafruit_SH1106G display = Adafruit_SH1106G(128, 64, &Wire, -1);  «1»
      void setup() {
        display.begin(0x3C, true);                   «2»
        display.setTextSize(1);                      «2»
        display.setTextColor(SH110X_WHITE);          «2»
      }
      void loop() {
        display.clearDisplay();                      «3»
        display.setCursor(0, 0);                     «3»
        display.println("Hola!");                    «3»
        display.printf("Pote: %d", analogRead(32));  «3»
        display.display();                           «4»
        delay(200);
      }
    ''', 'cpp'),
    'ojo': ['Sin `display.display()` no se ve nada: lo demás dibuja en memoria.',
            'Sin `clearDisplay()`, lo nuevo se escribe encima de lo viejo.',
            'La placa de la cátedra usa SH1106 (`Adafruit_SH110X`), no SSD1306: con la librería equivocada se ve basura.',
            'Con `setTextSize(2)` cada letra pasa a 12 × 16 píxeles: entran 10 por renglón.'],
    'parcial': 'Los casos 7, 8 y 10. El TPI muestra en el display el PWM, la temperatura, la humedad y el % del LED externo; el sketch 2, los campos leídos del canal.',
  },
  [
    esp('4.1', 'Texto', 'LUZ_ON y LUZ_OFF en el display', '''
      Al arrancar, el display muestra `Esperando...`. Con `LUZ_ON` por el monitor serie: LED verde y relé prendidos y el display muestra `RELAY ON!`; con `LUZ_OFF`: los dos apagados y `RELAY OFF!`.

      Completá la función `mostrar(texto)`, que limpia, escribe y muestra. Es el caso 7.
    ''', DISPLAY + '''
      const int VERDE = 23;
      const int RELE = 14;

      void mostrar(String txt) {
        // limpiá, ubicá el cursor arriba a la izquierda, escribí y mostrá

      }

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
        pinMode(RELE, OUTPUT);
        display.begin(0x3C, true);
        display.setTextSize(1);
        display.setTextColor(SH110X_WHITE);
        mostrar("Esperando...");
      }

      void loop() {
        if (Serial.available() > 0) {
          String cmd = Serial.readStringUntil('\\n');
          cmd.trim();
          // LUZ_ON y LUZ_OFF: los pines y el display

        }
      }
    ''', DISPLAY + '''
      const int VERDE = 23;
      const int RELE = 14;

      void mostrar(String txt) {
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println(txt);
        display.display();
      }

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
        pinMode(RELE, OUTPUT);
        display.begin(0x3C, true);
        display.setTextSize(1);
        display.setTextColor(SH110X_WHITE);
        mostrar("Esperando...");
      }

      void loop() {
        if (Serial.available() > 0) {
          String cmd = Serial.readStringUntil('\\n');
          cmd.trim();
          if (cmd == "LUZ_ON") {
            digitalWrite(VERDE, HIGH);
            digitalWrite(RELE, HIGH);
            mostrar("RELAY ON!");
          } else if (cmd == "LUZ_OFF") {
            digitalWrite(VERDE, LOW);
            digitalWrite(RELE, LOW);
            mostrar("RELAY OFF!");
          }
        }
      }
    ''', [P('Arranca, y llegan LUZ_ON y LUZ_OFF', 2500, [display(r'Esperando', t=500), display(r'RELAY ON!', t=1200), pin(14, 1200, 1), pin(23, 1200, 1), display(r'RELAY OFF!', t=2200), pin(14, 2200, 0)],
            entradas=[{'t': 800, 'serial': 'LUZ_ON\n'}, {'t': 1600, 'serial': 'LUZ_OFF\n'}])],
    profe=['caso_07_display_led_externo_relay.ino'],
    pasos=['`mostrar`: `display.clearDisplay(); display.setCursor(0, 0); display.println(txt); display.display();`', 'En el loop, como en el ejercicio 1.3, pero llamando a `mostrar("RELAY ON!")`.'],
    pistas=['Si el display queda vacío, falta `display.display()`.']),

    esp('4.2', 'Tamaños y una barra', 'el pote en el display', '''
      Cada 200 ms, mostrá en el display la lectura del pote en **tamaño 2** y abajo, en tamaño 1, la tensión con 2 decimales:
      ```
      3000
      2.42 V
      ```
      Debajo, una barra: `display.fillRect(0, 40, ancho, 10, SH110X_WHITE)`, con un `ancho` de 0 a 128 según el pote.
    ''', DISPLAY + '''
      const int POTE = 32;

      void setup() {
        display.begin(0x3C, true);
        display.setTextColor(SH110X_WHITE);
      }

      void loop() {
        int lectura = analogRead(POTE);
        float volt = lectura * 3.3 / 4095;
        display.clearDisplay();
        display.setCursor(0, 0);
        // la lectura en tamaño 2, la tensión en tamaño 1 y la barra

        display.display();
        delay(200);
      }
    ''', DISPLAY + '''
      const int POTE = 32;

      void setup() {
        display.begin(0x3C, true);
        display.setTextColor(SH110X_WHITE);
      }

      void loop() {
        int lectura = analogRead(POTE);
        float volt = lectura * 3.3 / 4095;
        display.clearDisplay();
        display.setCursor(0, 0);
        display.setTextSize(2);
        display.println(lectura);
        display.setTextSize(1);
        display.printf("%.2f V\\n", volt);
        int ancho = map(lectura, 0, 4095, 0, 128);
        display.fillRect(0, 40, ancho, 10, SH110X_WHITE);
        display.display();
        delay(200);
      }
    ''', [P('Pote en 3000', 600, [display(r'3000 2\.42 V', t=500)], pote=3000),
          P('Pote al máximo', 600, [display(r'4095 3\.30 V', t=500)], pote=4095)],
    profe=['Display_con_Pote.ino', 'caso_08_aumentar_disminuir_led-externo.ino'],
    checks=[C(r'fillRect\s*\(', 'Dibuja la barra con fillRect', 'Falta la barra: `display.fillRect(0, 40, ancho, 10, SH110X_WHITE);`'),
            C(r'map\s*\([^;]*128\s*\)|\*\s*128\s*/\s*4095', 'El ancho va de 0 a 128', 'El ancho de la barra tiene que ir de 0 a 128: `map(lectura, 0, 4095, 0, 128)`')],
    pasos=['`display.setTextSize(2); display.println(lectura);`', '`display.setTextSize(1); display.printf("%.2f V\\n", volt);`',
           '`int ancho = map(lectura, 0, 4095, 0, 128);` y `display.fillRect(0, 40, ancho, 10, SH110X_WHITE);`'],
    respuestas=[N('Ancho de la barra con el pote en 2048', 64, 0, 'píxeles', '`map(2048, 0, 4095, 0, 128)` = 2048 × 128 / 4095 = 64,02 → 64.')]),
  ]))

# ======================= 5 · DHT22 y touch =======================
DHT_INC = '''
#include <DHT.h>
'''
partes.append(parte(5, 'sensores', 'Sensores: DHT22 y touch', 'DHT22 y touch',
  'El DHT22 (GPIO 33) da temperatura y humedad con la librería DHT; los pines touch (13 y 4) dan un número que baja al tocarlos.',
  {
    'que': 'El **DHT22** (GPIO **33**) mide temperatura y humedad. Con la librería DHT: `DHT dht(33, DHT22);`, **dht.begin()** en el setup y **dht.readTemperature()** / **dht.readHumidity()**, que devuelven float (o **NaN** si falla). Conviene leerlo cada 2 s.\n'
           'Los **pines touch** (13 y 4) miden la capacidad: **touchRead(pin)** da un número que **baja al tocarlo**. En el simulador lee 72 suelto y 10 tocado; en la placa, depende del cable: medilo antes de elegir el umbral.',
    'consta': [
      ['El sensor', '`DHT dht(33, DHT22);` arriba y `dht.begin();` en el setup.'],
      ['Leer', '`float t = dht.readTemperature();` y `float h = dht.readHumidity();`, con `if (isnan(t))` por si falla.'],
      ['El touch', '`touchRead(13) < 40` → tocado. Para contar toques, como el pulsador: comparar con la lectura anterior (o `touchAttachInterrupt`).'],
      ['Mostrar', '`printf` con `%.1f`: un decimal (y `%%` para el signo de por ciento).'],
    ],
    'ejemplo': ejemplo('sensores.ino', 'DHT22 y un touch', '''
      #include <DHT.h>
      DHT dht(33, DHT22);                          «1»
      bool antes = false;
      void setup() {
        Serial.begin(115200);
        dht.begin();                               «1»
      }
      void loop() {
        float t = dht.readTemperature();           «2»
        float h = dht.readHumidity();              «2»
        if (isnan(t) || isnan(h)) return;          «2»
        bool tocado = touchRead(13) < 40;          «3»
        if (tocado && !antes) Serial.println("Toque");  «3»
        antes = tocado;                            «3»
        Serial.printf("%.1f C  %.1f %%\\n", t, h);  «4»
        delay(100);
      }
    ''', 'cpp'),
    'ojo': ['Si `readTemperature` da `nan`, el sensor no respondió: el pin equivocado o falta `dht.begin()`.',
            'El touch no es un botón: no da HIGH/LOW, es un número que baja al tocar.',
            'Los umbrales 950 y 850 del caso 9 son de otra placa: en el simulador el touch lee 72 suelto.',
            'Para el % literal en printf va `%%`.'],
    'parcial': 'Los casos 9 y 10. El TPI: temperatura y humedad en tiempo real en el display, y el LED externo con dos touch (uno sube, otro baja).',
  },
  [
    esp('5.1', 'DHT22', 'temperatura, humedad y un ventilador', '''
      Cada **2 s**, leé el DHT22 y mostrá en el display y en el monitor serie:
      ```
      Temp: 24.5 C
      Hum: 55.0 %
      ```
      Si la temperatura pasa de **28 °C**, cerrá el relé (un ventilador); si no, abrilo.
    ''', DISPLAY + DHT_INC + '''
      const int RELE = 14;
      DHT dht(33, DHT22);

      void setup() {
        Serial.begin(115200);
        pinMode(RELE, OUTPUT);
        display.begin(0x3C, true);
        display.setTextColor(SH110X_WHITE);
        dht.begin();
      }

      void loop() {
        // leé la temperatura y la humedad, mostralas (display y monitor serie) y decidí el relé

        delay(2000);
      }
    ''', DISPLAY + DHT_INC + '''
      const int RELE = 14;
      DHT dht(33, DHT22);

      void setup() {
        Serial.begin(115200);
        pinMode(RELE, OUTPUT);
        display.begin(0x3C, true);
        display.setTextColor(SH110X_WHITE);
        dht.begin();
      }

      void loop() {
        float t = dht.readTemperature();
        float h = dht.readHumidity();
        if (!isnan(t) && !isnan(h)) {
          display.clearDisplay();
          display.setCursor(0, 0);
          display.printf("Temp: %.1f C\\nHum: %.1f %%", t, h);
          display.display();
          Serial.printf("Temp: %.1f C\\nHum: %.1f %%\\n", t, h);
          digitalWrite(RELE, t > 28 ? HIGH : LOW);
        }
        delay(2000);
      }
    ''', [P('24,5 °C y después 31 °C', 7000, [display(r'Temp: 24\.5 C', t=1000), display(r'Hum: 55\.0 %', t=1000), pin(14, 2500, 0), display(r'Temp: 31\.0 C', t=6500), pin(14, 6500, 1), serial(r'Temp: 31\.0 C')],
            entradas=[{'t': 3000, 'dht': {'t': 31, 'h': 40}}], temp=24.5, hum=55)],
    profe=['caso_10_display_sensor_tyh.ino'],
    pasos=['`float t = dht.readTemperature(); float h = dht.readHumidity();`', 'El display: clear, setCursor(0, 0), `printf("Temp: %.1f C\\nHum: %.1f %%", t, h)` y display().',
           'El relé: `digitalWrite(RELE, t > 28 ? HIGH : LOW);`'],
    pistas=['En la placa, mové el deslizador de Temp. por encima de 28 y esperá la próxima lectura (2 s).']),

    esp('5.2', 'Touch', 'más y menos brillo con los touch, como el TPI', '''
      El **LED verde** con PWM de **12 bits**: cada toque en el **touch 13** sube el brillo **410** (10 %) y cada toque en el **touch 4** lo baja 410, sin pasarse de 0 ni de 4095. Mantener el dedo cuenta **un solo toque**. En cada cambio mostrá `Brillo: P %`.

      Es la parte de los touch del TPI (el caso 9 lo hace con interrupciones).
    ''', '''
      const int VERDE = 23;
      const int T_MAS = 13, T_MENOS = 4;
      const int UMBRAL = 40;   // tocado: menos de 40
      const int PASO = 410;    // 10 % de 4095
      int brillo = 0;
      bool antesMas = false, antesMenos = false;

      void cambiar(int d) {
        // sumá d sin salirte de 0..4095, mandalo al LED y mostrá el porcentaje

      }

      void setup() {
        Serial.begin(115200);
        analogWriteResolution(VERDE, 12);
        analogWrite(VERDE, brillo);
      }

      void loop() {
        bool mas = touchRead(T_MAS) < UMBRAL;
        bool menos = touchRead(T_MENOS) < UMBRAL;
        // llamá a cambiar(PASO) o cambiar(-PASO) solo cuando recién se toca

        delay(20);
      }
    ''', '''
      const int VERDE = 23;
      const int T_MAS = 13, T_MENOS = 4;
      const int UMBRAL = 40;   // tocado: menos de 40
      const int PASO = 410;    // 10 % de 4095
      int brillo = 0;
      bool antesMas = false, antesMenos = false;

      void cambiar(int d) {
        brillo = constrain(brillo + d, 0, 4095);
        analogWrite(VERDE, brillo);
        Serial.print("Brillo: ");
        Serial.print(brillo * 100 / 4095);
        Serial.println(" %");
      }

      void setup() {
        Serial.begin(115200);
        analogWriteResolution(VERDE, 12);
        analogWrite(VERDE, brillo);
      }

      void loop() {
        bool mas = touchRead(T_MAS) < UMBRAL;
        bool menos = touchRead(T_MENOS) < UMBRAL;
        if (mas && !antesMas) cambiar(PASO);
        if (menos && !antesMenos) cambiar(-PASO);
        antesMas = mas;
        antesMenos = menos;
        delay(20);
      }
    ''', [P('Tres toques en el 13 (uno largo) y uno en el 4', 3500, [pwm(23, 1000, 410), pwm(23, 2000, 1230), pwm(23, 3000, 820), serial(r'Brillo: 30 %')],
            entradas=tocar(13, 500, 900) + tocar(13, 1200, 1300) + tocar(13, 1600, 1700) + tocar(4, 2500, 2700)),
          P('Desde 0, el 4 no baja de 0', 1200, [pwm(23, 1000, 0)], entradas=tocar(4, 300, 500))],
    profe=['caso_09_sensor_touch.ino'],
    pasos=['`cambiar`: `brillo = constrain(brillo + d, 0, 4095);`, `analogWrite(VERDE, brillo);` y el print con `brillo * 100 / 4095`.',
           'En el loop, como el flanco del pulsador: `if (mas && !antesMas) cambiar(PASO);` (y lo mismo para el 4).', 'Al final: `antesMas = mas; antesMenos = menos;`'],
    pistas=['En la placa, mantené apretado «Touch 13»: tiene que subir una sola vez.'],
    respuestas=[N('Toques en el 13 para llegar al máximo desde 0', 10, 0, None, '9 × 410 = 3690 y el décimo pasaría de 4095: `constrain` lo deja en 4095.')]),
  ]))

# ======================= 6 · millis() =======================
partes.append(parte(6, 'millis', 'Sin bloquear: millis()', 'millis()',
  'delay() frena todo; con millis() se pregunta «¿ya pasó el tiempo?» y el loop sigue atendiendo el pulsador, los touch y el display. El TPI lo necesita.',
  {
    'que': '**delay()** frena todo: mientras espera, la placa no lee el pulsador ni el monitor serie. Con **millis()** (los ms desde que prendió) se pregunta «¿ya pasó el tiempo?» y el loop sigue dando vueltas: así se hacen varias cosas a la vez, cada una con su intervalo.',
    'consta': [
      ['La marca', '`unsigned long antes = 0;` guarda cuándo se hizo la última vez.'],
      ['La pregunta', '`if (millis() - antes >= 500) { … }`: siempre restando, así anda aunque millis() dé la vuelta.'],
      ['Actualizar', '`antes = millis();` adentro del if.'],
      ['Lo demás', 'Fuera del if, el loop sigue: el pulsador responde al instante.'],
    ],
    'ejemplo': ejemplo('millis.ino', 'Titila y atiende el pulsador a la vez', '''
      unsigned long antes = 0;                 «1»
      bool prendido = false;
      void setup() {
        pinMode(2, OUTPUT);
        pinMode(19, INPUT_PULLUP);
      }
      void loop() {
        if (millis() - antes >= 500) {         «2»
          antes = millis();                    «3»
          prendido = !prendido;
          digitalWrite(2, prendido);
        }
        if (digitalRead(19) == LOW) {          «4»
          Serial.println("Apretado");          «4»
        }
      }
    ''', 'cpp'),
    'ojo': ['`millis()` devuelve `unsigned long`: guardalo así (en un Arduino UNO, un int se desborda a los 32 s).',
            'Nada de delay largos en el loop: arruinan los demás intervalos.',
            'Un Ticker hace lo mismo con una función: `subirDatos.attach(16, leerySubir)` la llama cada 16 s (ThingSpeak_DHT_Ticker del profe).'],
    'parcial': 'El TPI hace muchas cosas a la vez: display en tiempo real, touch, pote y ThingSpeak cada 16 s. Con un `delay(16000)` los touch y el display quedarían congelados.',
  },
  [
    esp('6.1', 'millis()', 'titilar sin delay y atender el pulsador', '''
      El código de abajo titila con `delay(500)`: por eso el **LED verde**, que tendría que prenderse **mientras** apretás el pulsador, responde tarde. Pasalo a **millis()**: el LED azul sigue titilando (500 ms y 500 ms) y el verde responde al instante.

      Probalo en la placa antes y después: apretá el pulsador rápido.
    ''', '''
      const int AZUL = 2, VERDE = 23, BOTON = 19;
      bool prendido = false;

      void setup() {
        pinMode(AZUL, OUTPUT);
        pinMode(VERDE, OUTPUT);
        pinMode(BOTON, INPUT_PULLUP);
      }

      void loop() {
        // Así titila, pero el pulsador responde tarde: delay frena todo
        prendido = !prendido;
        digitalWrite(AZUL, prendido);
        delay(500);
        digitalWrite(VERDE, digitalRead(BOTON) == LOW);
      }
    ''', '''
      const int AZUL = 2, VERDE = 23, BOTON = 19;
      bool prendido = false;
      unsigned long antes = 0;

      void setup() {
        pinMode(AZUL, OUTPUT);
        pinMode(VERDE, OUTPUT);
        pinMode(BOTON, INPUT_PULLUP);
      }

      void loop() {
        if (millis() - antes >= 500) {
          antes = millis();
          prendido = !prendido;
          digitalWrite(AZUL, prendido);
        }
        digitalWrite(VERDE, digitalRead(BOTON) == LOW);
      }
    ''', [P('Apretás el pulsador a los 1,23 s y lo soltás a los 1,6 s', 3500, [periodo(2, 1000, 50), pin(23, 1260, 1), pin(23, 1700, 0)], entradas=apretar(1230, 1600))],
    pasos=['Arriba: `unsigned long antes = 0;`', 'El parpadeo adentro de `if (millis() - antes >= 500) { antes = millis(); … }`.', 'Sacá el `delay(500)`: la línea del pulsador queda afuera del if.'],
    pistas=['El pulsador tiene que leerse en cada vuelta del loop, no cada medio segundo.'],
    respuestas=[OP('Con el código inicial (con delay), el LED verde puede tardar en prenderse', ['nada: es instantáneo', 'hasta medio segundo', 'hasta 2 segundos'], 'hasta medio segundo',
                   'El loop se queda 500 ms en el delay: si apretás justo después, recién en la vuelta siguiente se lee el pulsador.')]),

    esp('6.2', 'Dos intervalos', 'cada cosa a su tiempo', '''
      Con dos marcas de tiempo y **sin delay**: cada **1 s** mostrá `Pote: N` y cada **3 s** mostrá `Temp: T C` (del DHT22, con un decimal).
    ''', DHT_INC + '''
      DHT dht(33, DHT22);
      unsigned long antesPote = 0;
      unsigned long antesTemp = 0;

      void setup() {
        Serial.begin(115200);
        dht.begin();
      }

      void loop() {
        // cada 1000 ms: Pote: N
        // cada 3000 ms: Temp: T C

      }
    ''', DHT_INC + '''
      DHT dht(33, DHT22);
      unsigned long antesPote = 0;
      unsigned long antesTemp = 0;

      void setup() {
        Serial.begin(115200);
        dht.begin();
      }

      void loop() {
        if (millis() - antesPote >= 1000) {
          antesPote = millis();
          Serial.print("Pote: ");
          Serial.println(analogRead(32));
        }
        if (millis() - antesTemp >= 3000) {
          antesTemp = millis();
          Serial.printf("Temp: %.1f C\\n", dht.readTemperature());
        }
      }
    ''', [P('Corre 7,5 s', 7500, [serial(r'Pote: \d+', veces=[7, 7]), serial(r'Temp: 24\.5 C', veces=[2, 2])])],
    checks=[NO(r'\bdelay\s*\(', 'Sin delay', 'Sacá los `delay`: con millis() no hacen falta.')],
    pasos=['Un `if (millis() - antesPote >= 1000) { antesPote = millis(); … }`.', 'Otro igual con `antesTemp` y 3000.'],
    respuestas=[N('Líneas que muestra en los primeros 6,5 s', 8, 0, None, 'Pote a los 1, 2, 3, 4, 5 y 6 s (6) y Temp a los 3 y 6 s (2): 8.',
                  medir={'hasta': 6500, 're': r'^(?:Pote|Temp):', 'cuenta': True})]),
  ]))

# ======================= 7 · WiFi y ThingSpeak =======================
TS_INC = '''
#include <WiFi.h>
#include <ThingSpeak.h>
#include <DHT.h>
'''
partes.append(parte(7, 'thingspeak', 'WiFi y ThingSpeak', 'ThingSpeak',
  'WiFi.begin y esperar WL_CONNECTED; ThingSpeak guarda hasta 8 campos por canal, con un envío cada 15 s como mínimo: setField y writeFields. El TPI manda 6 campos cada 16 s y el sketch 2 los lee.',
  {
    'que': 'Con **WiFi.begin(red, clave)** la placa se conecta (tarda: se espera con `while (WiFi.status() != WL_CONNECTED)`). **ThingSpeak** guarda y grafica datos en la nube: cada canal tiene hasta **8 campos** y la versión gratis acepta **un envío cada 15 s**. Se cargan los campos con **setField(n, valor)** y se mandan juntos con **writeFields(canal, writeAPIKey)**, que devuelve **200** si salió bien.',
    'consta': [
      ['Las claves', 'La red, el número de canal y la Write API Key (en el simulador sirven las de mentira: TU_RED_WIFI, TU_API_KEY).'],
      ['Conectarse', '`WiFi.begin(ssid, password)` y esperar `WL_CONNECTED`; después `ThingSpeak.begin(cliente)`.'],
      ['Cargar y mandar', '`ThingSpeak.setField(1, temp);` … y `int codigo = ThingSpeak.writeFields(canal, clave);`'],
      ['El intervalo', 'Cada 16 s (más de 15) con millis() o un Ticker: antes, ThingSpeak devuelve -401 y no lo guarda.'],
    ],
    'ejemplo': ejemplo('thingspeak.ino', 'Lo del caso 13, con millis()', '''
      #include <WiFi.h>
      #include <ThingSpeak.h>
      const char* ssid = "TU_RED_WIFI";            «1»
      const char* password = "";                   «1»
      unsigned long canal = 1234567;               «1»
      const char* clave = "TU_API_KEY";            «1»
      WiFiClient cliente;
      unsigned long antes = 0;
      void setup() {
        WiFi.begin(ssid, password);                «2»
        while (WiFi.status() != WL_CONNECTED) delay(500);  «2»
        ThingSpeak.begin(cliente);                 «2»
      }
      void loop() {
        if (millis() - antes >= 16000) {           «4»
          antes = millis();                        «4»
          ThingSpeak.setField(1, 24.5);            «3»
          int codigo = ThingSpeak.writeFields(canal, clave);  «3»
        }
      }
    ''', 'cpp'),
    'ojo': ['Con menos de 15 s entre envíos, writeFields devuelve **-401** y ese dato se pierde.',
            'El número de canal va como `unsigned long`; la API Key, como texto.',
            'En el simulador el WiFi conecta a los 1,2 s con cualquier red; en la placa poné la tuya (o «Wokwi-GUEST» en Wokwi).',
            'No subas tus claves de verdad a ningún lado: en la entrega, el canal y la clave van en el .txt.'],
    'parcial': 'El TPI: 6 campos cada 16 s (aleatorio de 100 a 500, temperatura, humedad, segundos desde el inicio, PWM del LED integrado y % del LED externo), y el sketch 2 que los lee y los muestra con las pulsaciones.',
  },
  [
    esp('7.1', 'WiFi', 'conectarse al WiFi', '''
      Conectá la placa al WiFi: mientras no conecta, mostrá un punto (`.`) cada 500 ms; cuando conecta, `WiFi conectado:` y la IP (`WiFi.localIP()`). Después, que el **LED azul** quede prendido como señal de «conectado».
    ''', '#include <WiFi.h>\n' + WIFI + '''
      const int AZUL = 2;

      void setup() {
        Serial.begin(115200);
        pinMode(AZUL, OUTPUT);
        // WiFi.begin, esperar con puntos, mostrar la IP y prender el LED

      }

      void loop() {
      }
    ''', '#include <WiFi.h>\n' + WIFI + '''
      const int AZUL = 2;

      void setup() {
        Serial.begin(115200);
        pinMode(AZUL, OUTPUT);
        WiFi.begin(ssid, password);
        while (WiFi.status() != WL_CONNECTED) {
          delay(500);
          Serial.print(".");
        }
        Serial.println();
        Serial.print("WiFi conectado: ");
        Serial.println(WiFi.localIP());
        digitalWrite(AZUL, HIGH);
      }

      void loop() {
      }
    ''', [P('Prende y se conecta', 3000, [serial(r'\.'), serial(r'WiFi conectado: 192\.168\.\d+\.\d+'), pin(2, 500, 0), pin(2, 2500, 1)])],
    profe=['caso_13_thing_speak_tyh.ino'],
    pasos=['`WiFi.begin(ssid, password);`', '`while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }`', 'Después del while: la IP y `digitalWrite(AZUL, HIGH);`'],
    respuestas=[OP('Si la red está mal escrita, este sketch', ['sigue sin WiFi', 'se queda para siempre en el while', 'se reinicia solo'], 'se queda para siempre en el while',
                   'El while espera WL_CONNECTED y nunca llega: por eso conviene un límite de intentos.')]),

    esp('7.2', 'ThingSpeak', 'temperatura y humedad cada 20 s', '''
      Mandá a ThingSpeak la **temperatura (campo 1)** y la **humedad (campo 2)** cada **20 s**, con millis(). Mostrá el código que devuelve writeFields: `ThingSpeak: 200`.

      En la placa, el cuadro **ThingSpeak** muestra cada envío. Probá cambiar 20000 por 5000: vas a ver el -401.
    ''', TS_INC + WIFI + '''
      unsigned long canal = 1234567;
      const char* clave = "TU_API_KEY";
      WiFiClient cliente;
      DHT dht(33, DHT22);
      unsigned long antes = 0;
      ''' + CONECTAR + '''
      void setup() {
        Serial.begin(115200);
        conectarWiFi();
        ThingSpeak.begin(cliente);
        dht.begin();
      }

      void loop() {
        // cada 20 s: los dos campos, writeFields y el código por el monitor serie

      }
    ''', TS_INC + WIFI + '''
      unsigned long canal = 1234567;
      const char* clave = "TU_API_KEY";
      WiFiClient cliente;
      DHT dht(33, DHT22);
      unsigned long antes = 0;
      ''' + CONECTAR + '''
      void setup() {
        Serial.begin(115200);
        conectarWiFi();
        ThingSpeak.begin(cliente);
        dht.begin();
      }

      void loop() {
        if (millis() - antes >= 20000) {
          antes = millis();
          ThingSpeak.setField(1, dht.readTemperature());
          ThingSpeak.setField(2, dht.readHumidity());
          int codigo = ThingSpeak.writeFields(canal, clave);
          Serial.print("ThingSpeak: ");
          Serial.println(codigo);
        }
      }
    ''', [P('Corre 65 s', 65000, [ts(min=3, max=3, cada=[19500, 20500], campos={'1': 24.5, '2': 55}, rechazos=0), serial(r'ThingSpeak: 200')])],
    profe=['caso_13_thing_speak_tyh.ino', 'ThingSpeak_DHT_Ticker.ino'],
    pasos=['`if (millis() - antes >= 20000) { antes = millis(); … }`', 'Adentro: los dos `setField`, `int codigo = ThingSpeak.writeFields(canal, clave);` y el print.'],
    respuestas=[N('Envíos en una hora', 180, 0, None, '3600 s / 20 s = 180.')]),

    esp('7.3', 'Los 6 campos', 'el envío del sketch 1 del TPI', '''
      La parte de ThingSpeak del **sketch 1 del TPI**: cada **16 s** mandá los 6 campos:
      1. un número al azar de 100 a 500 (`random(100, 501)`)
      2. la temperatura
      3. la humedad
      4. los segundos desde que prendió (`millis() / 1000`)
      5. el PWM del LED integrado (el pote, con 12 bits)
      6. el % de brillo del LED externo (acá, la variable `porcExterno`)

      Con millis(), o con un Ticker como el ThingSpeak_DHT_Ticker del profe.
    ''', TS_INC + WIFI + '''
      const int AZUL = 2, POTE = 32;
      unsigned long canal = 1234567;
      const char* clave = "TU_API_KEY";
      WiFiClient cliente;
      DHT dht(33, DHT22);
      int pwm = 0;              // el PWM del LED integrado (12 bits)
      int porcExterno = 40;     // el % del LED externo (en el TPI lo cambian los touch)
      unsigned long antes = 0;
      ''' + CONECTAR + '''
      void setup() {
        Serial.begin(115200);
        analogWriteResolution(AZUL, 12);
        conectarWiFi();
        ThingSpeak.begin(cliente);
        dht.begin();
      }

      void loop() {
        pwm = analogRead(POTE);
        analogWrite(AZUL, pwm);
        // cada 16 s: los 6 campos y writeFields

      }
    ''', TS_INC + WIFI + '''
      const int AZUL = 2, POTE = 32;
      unsigned long canal = 1234567;
      const char* clave = "TU_API_KEY";
      WiFiClient cliente;
      DHT dht(33, DHT22);
      int pwm = 0;              // el PWM del LED integrado (12 bits)
      int porcExterno = 40;     // el % del LED externo (en el TPI lo cambian los touch)
      unsigned long antes = 0;
      ''' + CONECTAR + '''
      void setup() {
        Serial.begin(115200);
        analogWriteResolution(AZUL, 12);
        conectarWiFi();
        ThingSpeak.begin(cliente);
        dht.begin();
      }

      void loop() {
        pwm = analogRead(POTE);
        analogWrite(AZUL, pwm);
        if (millis() - antes >= 16000) {
          antes = millis();
          ThingSpeak.setField(1, (int) random(100, 501));
          ThingSpeak.setField(2, dht.readTemperature());
          ThingSpeak.setField(3, dht.readHumidity());
          ThingSpeak.setField(4, (long) (millis() / 1000));
          ThingSpeak.setField(5, pwm);
          ThingSpeak.setField(6, porcExterno);
          int codigo = ThingSpeak.writeFields(canal, clave);
          Serial.print("ThingSpeak: ");
          Serial.println(codigo);
        }
      }
    ''', [P('Corre 50 s con el pote en 2048', 50000, [ts(min=3, cada=[15500, 16600], campos={'1': [100, 500], '2': 24.5, '3': 55, '4': [15, 50], '5': 2048, '6': 40}, rechazos=0)], pote=2048)],
    profe=['ThingSpeak_DHT_Ticker.ino'],
    pasos=['El if de millis() con 16000.', 'Seis `ThingSpeak.setField(n, valor);` y un solo `writeFields` al final.'],
    pistas=['`random(100, 501)` da de 100 a 500: el segundo número no entra.'],
    respuestas=[N('Envíos en 5 minutos', 18, 0, None, '300 s / 16 s = 18,75: 18 envíos completos.')]),

    esp('7.4', 'Leer el canal', 'el sketch 2 del TPI: leer y contar', '''
      El **sketch 2 del TPI**: leé los 6 campos del canal con `ThingSpeak.readFloatField(canal, n)` al arrancar y después cada 16 s; contá las pulsaciones y mostrá en el display, rotando cada **3 s**, dos pantallas:
      ```
      C1: 321.0          C4: 120.0
      C2: 24.5     y     C5: 2048.0
      C3: 55.0           C6: 40.0
      Pulsaciones: 2     Pulsaciones: 2
      ```
      En el simulador el canal 1234567 ya tiene datos (los de un sketch 1).
    ''', TS_INC + DISPLAY + WIFI + '''
      const int BOTON = 19;
      unsigned long canal = 1234567;
      WiFiClient cliente;
      float campos[7];          // campos[1] a campos[6]
      int pulsaciones = 0;
      int anterior = HIGH;
      int pantalla = 0;         // 0: campos 1 a 3 · 1: campos 4 a 6
      unsigned long antesLeer = 0, antesPantalla = 0;
      ''' + CONECTAR + '''
      void leerCanal() {
        // los 6 campos con readFloatField

      }

      void mostrar() {
        display.clearDisplay();
        display.setCursor(0, 0);
        // tres campos según la pantalla y las pulsaciones

        display.display();
      }

      void setup() {
        Serial.begin(115200);
        pinMode(BOTON, INPUT_PULLUP);
        display.begin(0x3C, true);
        display.setTextColor(SH110X_WHITE);
        conectarWiFi();
        ThingSpeak.begin(cliente);
        leerCanal();
        mostrar();
      }

      void loop() {
        // las pulsaciones (con el flanco), leer cada 16 s y cambiar de pantalla cada 3 s

      }
    ''', TS_INC + DISPLAY + WIFI + '''
      const int BOTON = 19;
      unsigned long canal = 1234567;
      WiFiClient cliente;
      float campos[7];          // campos[1] a campos[6]
      int pulsaciones = 0;
      int anterior = HIGH;
      int pantalla = 0;         // 0: campos 1 a 3 · 1: campos 4 a 6
      unsigned long antesLeer = 0, antesPantalla = 0;
      ''' + CONECTAR + '''
      void leerCanal() {
        for (int n = 1; n <= 6; n++) {
          campos[n] = ThingSpeak.readFloatField(canal, n);
        }
      }

      void mostrar() {
        display.clearDisplay();
        display.setCursor(0, 0);
        int primero = pantalla == 0 ? 1 : 4;
        for (int n = primero; n < primero + 3; n++) {
          display.printf("C%d: %.1f\\n", n, campos[n]);
        }
        display.printf("Pulsaciones: %d", pulsaciones);
        display.display();
      }

      void setup() {
        Serial.begin(115200);
        pinMode(BOTON, INPUT_PULLUP);
        display.begin(0x3C, true);
        display.setTextColor(SH110X_WHITE);
        conectarWiFi();
        ThingSpeak.begin(cliente);
        leerCanal();
        mostrar();
      }

      void loop() {
        int ahora = digitalRead(BOTON);
        if (anterior == HIGH && ahora == LOW) {
          pulsaciones++;
          mostrar();
        }
        anterior = ahora;
        if (millis() - antesLeer >= 16000) {
          antesLeer = millis();
          leerCanal();
        }
        if (millis() - antesPantalla >= 3000) {
          antesPantalla = millis();
          pantalla = 1 - pantalla;
          mostrar();
        }
        delay(20);
      }
    ''', [P('Lee el canal y apretás dos veces', 9000, [display(r'C1: 321\.0 C2: 24\.5 C3: 55\.0'), display(r'C4: 120\.0 C5: 2048\.0 C6: 40\.0'), display(r'Pulsaciones: 2', t=8500), display(r'Pulsaciones: 3', no=True)],
            entradas=apretar(2000, 2200) + apretar(4000, 4200), canales=CANAL)],
    profe=['ThingSpeak_LeerDatos.ino'],
    placa={'canales': CANAL},
    pasos=['`leerCanal`: un for de 1 a 6 con `campos[n] = ThingSpeak.readFloatField(canal, n);`',
           '`mostrar`: `int primero = pantalla == 0 ? 1 : 4;` y un for de tres `display.printf("C%d: %.1f\\n", n, campos[n]);`, más las pulsaciones.',
           'En el loop: el flanco del pulsador (llamá a `mostrar()` para que se vea al toque), y dos ifs de millis(): 16000 para leer y 3000 para `pantalla = 1 - pantalla; mostrar();`'],
    pistas=['El TPI dice «puede ser de a 3 campos por pantalla rotativa»: dos pantallas de 3.']),
  ]))

# ======================= 8 · MQTT y EEPROM =======================
MQTT_INC = '''
#include <WiFi.h>
#include <PubSubClient.h>
'''
partes.append(parte(8, 'mqtt', 'MQTT y EEPROM', 'MQTT y EEPROM',
  'MQTT: se publica en un topic y le llega a los suscriptos, a través de un broker (PubSubClient en la ESP32). La EEPROM guarda datos que sobreviven a un reinicio.',
  {
    'que': '**MQTT** es un protocolo liviano de **publicar / suscribirse**: los clientes no se hablan directo sino a través de un **broker** (Mosquitto, HiveMQ). Uno **publica** un mensaje en un **topic** (`utn/tpa/pote`) y le llega a todos los **suscriptos** a ese topic. En la ESP32 se usa la librería **PubSubClient**.\n'
           'La **EEPROM** (emulada en la flash) guarda datos que sobreviven a un reinicio: `EEPROM.write(dir, byte)` y `EEPROM.commit()`.',
    'consta': [
      ['El cliente', '`WiFiClient espClient; PubSubClient client(espClient);` y `client.setServer(broker, 1883)`.'],
      ['Conectarse', '`client.connect("idUnico")` (y reconectar si se cae); `client.loop()` en cada vuelta.'],
      ['Publicar y suscribirse', '`client.publish(topic, texto)` · `client.subscribe(topic)` y `client.setCallback(funcion)` para lo que llega.'],
      ['La EEPROM', '`EEPROM.begin(1)`, `EEPROM.read(0)` al arrancar y `EEPROM.write(0, v)` + `EEPROM.commit()` al cambiar.'],
    ],
    'ejemplo': ejemplo('mqtt.ino', 'Suscribirse y recibir (lo del ejemplo del profe)', '''
      #include <WiFi.h>
      #include <PubSubClient.h>
      WiFiClient espClient;
      PubSubClient client(espClient);                  «1»
      void callback(char* topic, byte* payload, unsigned int largo) {  «3»
        String msg = "";
        for (unsigned int i = 0; i < largo; i++) msg += (char) payload[i];  «3»
      }
      void setup() {
        WiFi.begin("TU_RED_WIFI", "");
        while (WiFi.status() != WL_CONNECTED) delay(500);
        client.setServer("broker.hivemq.com", 1883);   «1»
        client.setCallback(callback);                  «3»
      }
      void loop() {
        if (!client.connected()) {                     «2»
          client.connect("ESP32_tpa_01");              «2»
          client.subscribe("utn/tpa/led");             «3»
        }
        client.loop();                                 «2»
      }
    ''', 'cpp'),
    'ojo': ['Sin `client.loop()` no llegan los mensajes ni se mantiene la conexión.',
            'El callback recibe el mensaje como bytes (`byte* payload`, `unsigned int largo`): hay que armar el String.',
            'El id del cliente tiene que ser único en el broker: dos placas con el mismo id se desconectan entre sí.',
            '`EEPROM.write` sin `EEPROM.commit()` no queda guardado. La flash aguanta unas 100.000 escrituras: no grabes en cada vuelta del loop.'],
    'parcial': 'MQTT y la EEPROM están en los ejemplos de clase del profe (MQTT_Publicar_Mosquitto, MQTT_Suscriber…, Memoria_EEPROM) y en el 3º parcial.',
  },
  [
    esp('8.1', 'Publicar', 'publicar el pote', '''
      Publicá la lectura del pote en el topic `utn/tpa/pote` cada **2 s** (el mensaje: solo el número). El broker es `broker.hivemq.com`, puerto 1883, y el id del cliente `ESP32_tpa_01`.

      En la placa, el cuadro **MQTT** muestra lo que publica.
    ''', MQTT_INC + WIFI + '''
      const int POTE = 32;
      WiFiClient espClient;
      PubSubClient client(espClient);
      unsigned long antes = 0;
      ''' + CONECTAR + '''
      void setup() {
        Serial.begin(115200);
        conectarWiFi();
        // el broker

      }

      void loop() {
        if (!client.connected()) {
          // conectar con el id
        }
        client.loop();
        // cada 2 s, publicar el pote

      }
    ''', MQTT_INC + WIFI + '''
      const int POTE = 32;
      WiFiClient espClient;
      PubSubClient client(espClient);
      unsigned long antes = 0;
      ''' + CONECTAR + '''
      void setup() {
        Serial.begin(115200);
        conectarWiFi();
        client.setServer("broker.hivemq.com", 1883);
      }

      void loop() {
        if (!client.connected()) {
          client.connect("ESP32_tpa_01");
        }
        client.loop();
        if (millis() - antes >= 2000) {
          antes = millis();
          String msg = String(analogRead(POTE));
          client.publish("utn/tpa/pote", msg.c_str());
        }
      }
    ''', [P('Corre 7 s con el pote en 1500', 7000, [mqtt(tipo='conn'), mqtt(tipo='pub', topic='utn/tpa/pote', re=r'^1500$', min=2)], pote=1500)],
    profe=['MQTT_Publicar_Mosquitto.ino'],
    pasos=['En el setup: `client.setServer("broker.hivemq.com", 1883);`', 'En el if: `client.connect("ESP32_tpa_01");`',
           'Cada 2 s: `String msg = String(analogRead(POTE)); client.publish("utn/tpa/pote", msg.c_str());`'],
    respuestas=[OP('Si otra placa se suscribe a «utn/tpa/#», ¿recibe estos mensajes?', ['Sí', 'No'], 'Sí', '`#` es el comodín de varios niveles: `utn/tpa/#` incluye `utn/tpa/pote`.')]),

    esp('8.2', 'Suscribirse', 'prender el LED desde el broker', '''
      Suscribite al topic `utn/tpa/led`: si llega `ON`, prendé el **LED verde**; si llega `OFF`, apagalo.

      Probalo en la placa: en el cuadro **MQTT**, publicá `ON` en `utn/tpa/led` (como otro cliente).
    ''', MQTT_INC + WIFI + '''
      const int VERDE = 23;
      WiFiClient espClient;
      PubSubClient client(espClient);
      ''' + CONECTAR + '''
      void callback(char* topic, byte* payload, unsigned int largo) {
        String msg = "";
        for (unsigned int i = 0; i < largo; i++) msg += (char) payload[i];
        // ON prende y OFF apaga

      }

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
        conectarWiFi();
        client.setServer("broker.hivemq.com", 1883);
        // la función que recibe los mensajes

      }

      void loop() {
        if (!client.connected()) {
          client.connect("ESP32_tpa_02");
          // suscribirse

        }
        client.loop();
      }
    ''', MQTT_INC + WIFI + '''
      const int VERDE = 23;
      WiFiClient espClient;
      PubSubClient client(espClient);
      ''' + CONECTAR + '''
      void callback(char* topic, byte* payload, unsigned int largo) {
        String msg = "";
        for (unsigned int i = 0; i < largo; i++) msg += (char) payload[i];
        if (msg == "ON") digitalWrite(VERDE, HIGH);
        else if (msg == "OFF") digitalWrite(VERDE, LOW);
      }

      void setup() {
        Serial.begin(115200);
        pinMode(VERDE, OUTPUT);
        conectarWiFi();
        client.setServer("broker.hivemq.com", 1883);
        client.setCallback(callback);
      }

      void loop() {
        if (!client.connected()) {
          client.connect("ESP32_tpa_02");
          client.subscribe("utn/tpa/led");
        }
        client.loop();
      }
    ''', [P('Llegan ON y OFF', 5000, [mqtt(tipo='sub', topic='utn/tpa/led'), pin(23, 3000, 1), pin(23, 4500, 0)],
            entradas=[{'t': 2500, 'mqtt': {'topic': 'utn/tpa/led', 'payload': 'ON'}}, {'t': 3500, 'mqtt': {'topic': 'utn/tpa/led', 'payload': 'OFF'}}]),
          P('Llega otra cosa: no cambia', 3500, [pin(23, 3000, 0)], entradas=[{'t': 2500, 'mqtt': {'topic': 'utn/tpa/led', 'payload': 'HOLA'}}])],
    profe=['MQTT_Suscriber_Mosquitto_graba_ThingSpeak.ino'],
    pasos=['En el setup: `client.setCallback(callback);`', 'Después de conectar: `client.subscribe("utn/tpa/led");`', 'En el callback: `if (msg == "ON") … else if (msg == "OFF") …`'],
    pistas=['Si no llega nada, revisá que `client.loop()` se llame en cada vuelta.']),

    esp('8.3', 'EEPROM', 'recordar el LED después de un reinicio', '''
      El pulsador prende y apaga el **LED azul** (como en la parte 2), y el estado se guarda en la **dirección 0 de la EEPROM**: al prender la placa, el LED arranca como quedó.

      Las pruebas prenden la placa con un 1 guardado (tiene que arrancar prendido) y con un 0.
    ''', '''
      #include <EEPROM.h>

      const int AZUL = 2, BOTON = 19;
      int estado = 0;
      int anterior = HIGH;

      void setup() {
        Serial.begin(115200);
        EEPROM.begin(1);
        pinMode(AZUL, OUTPUT);
        pinMode(BOTON, INPUT_PULLUP);
        // leé el estado guardado y ponelo en el LED

      }

      void loop() {
        int ahora = digitalRead(BOTON);
        if (anterior == HIGH && ahora == LOW) {
          estado = !estado;
          digitalWrite(AZUL, estado);
          // guardalo en la EEPROM

        }
        anterior = ahora;
        delay(20);
      }
    ''', '''
      #include <EEPROM.h>

      const int AZUL = 2, BOTON = 19;
      int estado = 0;
      int anterior = HIGH;

      void setup() {
        Serial.begin(115200);
        EEPROM.begin(1);
        pinMode(AZUL, OUTPUT);
        pinMode(BOTON, INPUT_PULLUP);
        estado = EEPROM.read(0) == 1 ? 1 : 0;
        digitalWrite(AZUL, estado);
      }

      void loop() {
        int ahora = digitalRead(BOTON);
        if (anterior == HIGH && ahora == LOW) {
          estado = !estado;
          digitalWrite(AZUL, estado);
          EEPROM.write(0, estado);
          EEPROM.commit();
        }
        anterior = ahora;
        delay(20);
      }
    ''', [P('Arranca con un 1 guardado', 600, [pin(2, 300, 1)], eeprom={'0': 1}),
          P('Arranca con un 0 y apretás una vez', 1500, [pin(2, 300, 0), pin(2, 1000, 1), eeprom(0, 1)], entradas=apretar(500, 700), eeprom={'0': 0})],
    profe=['Memoria_EEPROM.ino'],
    pasos=['En el setup: `estado = EEPROM.read(0) == 1 ? 1 : 0;` y `digitalWrite(AZUL, estado);`', 'Al cambiar: `EEPROM.write(0, estado); EEPROM.commit();`'],
    pistas=['Una EEPROM nueva lee 255 en todas las direcciones: por eso se compara con 1.'],
    respuestas=[N('¿Qué lee EEPROM.read de una dirección que nunca se escribió?', 255, 0, None, 'La flash borrada tiene todos los bits en 1: 0xFF = 255.')]),
  ]))

if __name__ == '__main__':
    copiar_profe()
    guardar(os.path.join(RAIZ, 'practica', 'tpa-tp', 'ejercicios.json'), 'TP · la ESP32 de la cátedra', partes)
