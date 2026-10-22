# Arma practica/tpa-p2/ejercicios.json: la Práctica del 2º parcial de TPA (cinemática inversa y trayectorias).
# Necesita octave-cli: los valores esperados salen de correr cada solución con las funciones del profe.
# Desde la raíz:  python3 herramientas/tpa-practica/armar_p2.py  y después  node herramientas/tpa-practica/validar.js
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import *

def figura(url, alt, pie=None):
    x = {'url': url, 'alt': alt}
    if pie: x['pie'] = pie
    return x
IMG = 'practica/tpa-p2/img/'
RRR = figura(IMG + 'rrr-plano-y-vista-superior.png', 'El brazo RRR en su plano vertical (l1, l2, l3, q2, q3, r y s) y visto desde arriba (q1 y r)', 'El RRR partido en dos problemas 2D')
CIL = figura('practica/tpa-p1/img/robot-cilindrico.png', 'Robot cilíndrico: columna que gira (θ1), sube (d2), un brazo que se estira (d3) y una muñeca que gira (θ4)', 'Robot cilíndrico RPPR')
RPR = figura(IMG + 'robot-rpr.png', 'Robot RPR: base que gira q1, altura A, brazo horizontal que se desliza d y un eslabón B que gira q2', 'Robot RPR del parcial 2026')
RPP = figura(IMG + 'robot-rpp.png', 'Robot RPP: base que gira θ1, una prismática vertical d2 y una horizontal d3', 'Robot RPP del parcial 2026')

R = lambda pregunta, expr, dec=2, unidad=None, motivo=None: {k: v for k, v in
    {'pregunta': pregunta, 'expr': expr, 'dec': dec, 'unidad': unidad, 'motivo': motivo}.items() if v is not None}
OP = lambda pregunta, opciones, valor, motivo=None: {k: v for k, v in
    {'pregunta': pregunta, 'opciones': opciones, 'valor': valor, 'motivo': motivo}.items() if v is not None}

# El cilíndrico del resumen, cargado como lo pide cinematica_inversa
CIL_RES = '''
l1 = 400;  l4 = 100;                        % [mm]
tipo     = 'RPPR';
q_offset = [0; 90; 0; 0];                   % columna θ (las variables van en 0)
d_offset = [l1; 0; 0; l4];                  % columna d (las variables van en 0)
a        = [0; 0; 0; 0];
alpha    = [0; 90; 0; 0];
'''

partes = []

# ======================= 1 · Directa e inversa =======================
partes.append(parte(1, 'directa', 'Directa e inversa: el mapa', 'Directa e inversa',
  'La **directa** va de las articulaciones a la punta (multiplicando las matrices de Denavit–Hartenberg) y siempre tiene una respuesta. La **inversa** va al revés y puede tener dos, una o ninguna. La directa es la que se usa para verificar.',
  {
    'que': 'Un robot tiene dos «idiomas»: el **espacio articular** (el valor de cada articulación: ángulos q en las rotativas, desplazamientos d en las prismáticas) y el **espacio cartesiano** (dónde está la punta: x, y, z).\n'
           'La **cinemática directa** va de las articulaciones a la punta: se multiplican las matrices de Denavit–Hartenberg y la posición es `T(1:3,4)`. Siempre tiene una sola respuesta. La **inversa** va al revés, de (x, y, z) a las articulaciones, y puede tener dos soluciones (codo arriba y codo abajo), una o ninguna. Se resuelve por geometría o iterando con el Jacobiano.',
    'consta': [
      ['La tabla DH', 'Una fila por articulación (θ, d, a, α); la variable va en θ (R) o en d (P).'],
      ['cinematica_directa', "`T = cinematica_directa(theta, d, a, alpha, 'deg')`: los cuatro vectores son las columnas de la tabla, con los números."],
      ['La posición', '`T(1:3,4)`; la orientación es `T(1:3,1:3)`.'],
      ['La forma cerrada', 'Para el RRR: x = cos q1·[l2·cos q2 + l3·cos(q2+q3)], y = sen q1·[…], z = l1 + l2·sen q2 + l3·sen(q2+q3).'],
      ['Directa para verificar', 'La inversa se controla metiendo la solución en la directa: tiene que volver al punto.'],
    ],
    'ejemplo': ejemplo('rrr_directa.m', 'La prueba del resumen: el RRR de la clase', '''
      l1 = 0.5; l2 = 0.3; l3 = 0.2;       % [m]
      %  i   θ    d    a    α «1»
      %  1   q1   l1   0    90 «1»
      %  2   q2   0    l2   0 «1»
      %  3   q3   0    l3   0 «1»
      q = [0 30 30];                       % [deg]
      T = cinematica_directa(q, [l1 0 0], [0 l2 l3], [90 0 0], 'deg'); «2»
      p = T(1:3, 4)                        % (0,3598; 0; 0,8232) «3»
      x = cosd(q(1)) * (l2*cosd(q(2)) + l3*cosd(q(2) + q(3)))   % 0,3598 «4»
      % la inversa de (0,3598; 0; 0,8232) tiene que volver a q = (0, 30, 30) «5»
    '''),
    'ojo': ['q2 se mide desde la horizontal y q3 es relativo: q3 = 0 es l3 en la prolongación de l2.',
            'Con grados: `sind`, `cosd`, `atan2d`. `sin(30)` es el seno de 30 **radianes**.',
            'La del 2º parcial devuelve más cosas: `[T, origins, Tsist] = cinematica_directa(...)`. Con una sola salida te quedás con T.'],
    'parcial': 'No se pide sola, pero se usa en todos los ejercicios para verificar: si la directa de tu respuesta vuelve al punto pedido, está bien.',
    'pdf': 2,
  },
  [
    elegir_ej('1.1', 'Directa o inversa', '¿directa o inversa?', '¿Cada frase es de la cinemática directa o de la inversa?', ['Directa', 'Inversa'], [
      ('Te dan q1, q2 y q3, y piden dónde queda la punta', 'Directa', 'De las articulaciones a la punta.'),
      ('Te dan el punto (x, y, z) y piden los valores articulares', 'Inversa', 'De la punta a las articulaciones.'),
      ('Siempre tiene una sola respuesta', 'Directa', 'Multiplicar matrices da un único resultado.'),
      ('Puede tener dos soluciones (codo arriba y codo abajo), una o ninguna', 'Inversa', 'Si el punto está fuera de alcance, no hay solución.'),
      ('Se resuelve multiplicando las matrices de Denavit–Hartenberg', 'Directa', '`T = A1·A2·…·An`.'),
      ('Se usa para verificar la respuesta de la otra', 'Directa', 'La solución de la inversa, metida en la directa, tiene que volver al punto.'),
    ], pregunta='¿Directa o inversa?'),
    elegir_ej('1.2', 'Geométrica o numérica', '¿geométrica o numérica?', 'La inversa se resuelve por geometría (ejercicio 1 del parcial) o iterando con DLS (ejercicio 2). ¿De cuál es cada frase?', ['Geométrica', 'Numérica (DLS)'], [
      ('Trigonometría en el dibujo: atan2 y la ley del coseno', 'Geométrica', 'Sale una fórmula cerrada.'),
      ('Arranca en una semilla q0 y corrige con el Jacobiano hasta llegar', 'Numérica (DLS)', 'Itera hasta que el error es menor que la tolerancia.'),
      ('Da todas las soluciones, exactas', 'Geométrica', 'Las dos ramas del codo salen del ± de la raíz.'),
      ('Da la solución más cercana a la semilla, aproximada', 'Numérica (DLS)', 'El error final es menor que tol_pos.'),
      ('Sirve para robots simples (2R, 3R)', 'Geométrica', 'En robots más complicados no hay una fórmula fácil.'),
      ('Sirve para cualquier robot, con articulaciones R y P', 'Numérica (DLS)', 'Solo necesita la directa y el Jacobiano.'),
    ], pregunta='¿Geométrica o numérica?'),
    oct_ej('1.3', 'cinematica_directa', 'la directa del RRR', 'Robot RRR de la cátedra con l1 = 0,5 m, l2 = 0,3 m y l3 = 0,2 m. Con `cinematica_directa`, ¿dónde queda la punta con q = (0°, 30°, 30°)?\n\nGuardá la posición en `p` (columna de 3).',
      r'''
      l1 = 0.5; l2 = 0.3; l3 = 0.2;   % [m]
      q = [0 30 30];                   % [deg]
      % la tabla:  θ = q,  d = [l1 0 0],  a = [0 l2 l3],  α = [90 0 0]
      % T = cinematica_directa( ... );
      % p = ...
      ''', r'''
      l1 = 0.5; l2 = 0.3; l3 = 0.2;
      q = [0 30 30];
      T = cinematica_directa(q, [l1 0 0], [0 l2 l3], [90 0 0], 'deg');
      p = T(1:3, 4)
      ''', vars=['p'], respuestas=[R('x', 'p(1)', 4, 'm'), R('y', 'p(2)', 4, 'm'), R('z', 'p(3)', 4, 'm')], imagen=RRR,
      pasos=['Las cuatro columnas de la tabla: `[q1 q2 q3]`, `[l1 0 0]`, `[0 l2 l3]` y `[90 0 0]`.', "`T = cinematica_directa(q, d, a, alpha, 'deg')`.", '`p = T(1:3, 4)`.'],
      pistas=['Es la prueba que pide el resumen antes del parcial: tiene que dar (0,3598; 0; 0,8232).'],
      checks=[C(r'cinematica_directa\s*\(', 'Usa cinematica_directa', 'Calculá T con cinematica_directa')]),
    oct_ej('1.4', 'Forma cerrada', 'la forma cerrada', 'RRR con l1 = 0,45 m, l2 = 0,35 m y l3 = 0,25 m, en q = (40°, 20°, 60°). Calculá la punta de dos formas y comprobá que dan igual:\n- `pf`: con las fórmulas cerradas (x, y, z en una columna).\n- `pc`: con `cinematica_directa`.',
      r'''
      l1 = 0.45; l2 = 0.35; l3 = 0.25;
      q1 = 40; q2 = 20; q3 = 60;
      % pf = [ x; y; z ]   con las fórmulas
      % pc = ...           con cinematica_directa
      ''', r'''
      l1 = 0.45; l2 = 0.35; l3 = 0.25;
      q1 = 40; q2 = 20; q3 = 60;
      brazo = l2*cosd(q2) + l3*cosd(q2 + q3);
      pf = [cosd(q1)*brazo; sind(q1)*brazo; l1 + l2*sind(q2) + l3*sind(q2 + q3)]
      T = cinematica_directa([q1 q2 q3], [l1 0 0], [0 l2 l3], [90 0 0], 'deg');
      pc = T(1:3, 4)
      ''', vars=['pf', 'pc'], respuestas=[R('z', 'pf(3)', 4, 'm')],
      pasos=['El «brazo» horizontal es `l2*cosd(q2) + l3*cosd(q2 + q3)`.', 'x = cos q1 · brazo, y = sen q1 · brazo.', 'z = l1 + l2·sen q2 + l3·sen(q2 + q3).'],
      checks=[C(r'cosd\s*\(', 'Las fórmulas, en grados', 'Usá `cosd` y `sind` para las fórmulas')],
      mensajes={'pf': '`pf` no da: revisá las fórmulas (q3 es relativo: va q2 + q3)'}),
    oct_ej('1.5', 'Cilíndrico', 'la directa del cilíndrico', 'Robot cilíndrico RPPR del resumen (l1 = 400 mm, l4 = 100 mm). Su tabla (θ, d, a, α) es (q1, l1, 0, 0), (90, d2, 0, 90), (0, d3, 0, 0), (q4, l4, 0, 0). ¿Dónde está la punta con q1 = 30°, d2 = 200 mm, d3 = 250 mm y q4 = 45°?\n\nGuardá `p`.',
      r'''
      l1 = 400; l4 = 100;
      q1 = 30; d2 = 200; d3 = 250; q4 = 45;
      % T = cinematica_directa([ ... ], [ ... ], [0 0 0 0], [0 90 0 0], 'deg');
      % p = ...
      ''', r'''
      l1 = 400; l4 = 100;
      q1 = 30; d2 = 200; d3 = 250; q4 = 45;
      T = cinematica_directa([q1 90 0 q4], [l1 d2 d3 l4], [0 0 0 0], [0 90 0 0], 'deg');
      p = T(1:3, 4)
      ''', vars=['p'], respuestas=[R('x', 'p(1)', 2, 'mm'), R('y', 'p(2)', 2, 'mm'), R('z', 'p(3)', 2, 'mm'),
        OP('¿Cambia la punta si q4 vale 0?', ['Sí', 'No'], 'No', 'q4 gira la muñeca sobre su propio eje: solo cambia la orientación.')], imagen=CIL,
      pasos=['θ = `[q1 90 0 q4]` y d = `[l1 d2 d3 l4]`.'],
      pistas=['Control: x = (d3 + l4)·cos q1, y = (d3 + l4)·sen q1, z = l1 + d2.']),
  ]))

# ======================= 2 · CI geométrica del RRR =======================
partes.append(parte(2, 'geometrica', 'Cinemática inversa geométrica del RRR', 'CI geométrica',
  'El problema 3D se parte en dos 2D: desde arriba sale q1 = atan2d(y, x); en el plano del brazo queda un 2R, que se resuelve con la ley del coseno. Hay dos soluciones (q3 > 0 y q3 < 0) y cada q3 tiene su q2.',
  {
    'que': 'El problema 3D se parte en **dos problemas 2D**. Mirando desde arriba sale q1, el ángulo del punto. Después se «para» el brazo en su plano vertical y queda un brazo 2R plano, que se resuelve con la **ley del coseno**.\n'
           'Hay dos soluciones: una con q3 > 0 y otra con q3 < 0, y cada q3 tiene su propio q2. Se cierra verificando las dos con la directa.',
    'consta': [
      ['El giro de la base', '`q1 = atan2d(y, x)`: atan2 reconoce el cuadrante (`atand(y/x)` no).'],
      ['El plano del brazo', '`r = hypot(x, y)` y `s = z - l1`: distancia horizontal y altura medidas desde el hombro.'],
      ['¿Llega?', '`L = hypot(r, s)` tiene que cumplir |l2 − l3| ≤ L ≤ l2 + l3.'],
      ['Ley del coseno → q3', '`D = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3)` y `q3 = ±atan2d(sqrt(1 - D^2), D)`.'],
      ['Un q2 para cada q3', '`q2 = atan2d(s, r) - atan2d(l3*sind(q3), l2 + l3*cosd(q3))`.'],
      ['Verificar', 'Las dos soluciones en `cinematica_directa`: tienen que volver al punto.'],
    ],
    'ejemplo': ejemplo('ci_rrr.m', 'Ejercicio 1 del resumen (modelo del 2º parcial)', r'''
      l1 = 0.45; l2 = 0.35; l3 = 0.25;              % [m]
      x = 0.30; y = 0.25; z = 0.60;                  % el punto P
      q1 = atan2d(y, x)                              % 39,806° «1»
      r  = hypot(x, y);   s = z - l1;                % 0,39051 y 0,15 «2»
      L  = hypot(r, s);                              % 0,41833 «3»
      if L > l2 + l3 || L < abs(l2 - l3), error('Fuera de alcance'); end «3»
      D  = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3)     % -0,057143 «4»
      q3A =  atan2d(sqrt(1 - D^2), D);               % +93,276° «4»
      q3B = -atan2d(sqrt(1 - D^2), D);               % -93,276° «4»
      q2A = atan2d(s, r) - atan2d(l3*sind(q3A), l2 + l3*cosd(q3A));   % -15,617° «5»
      q2B = atan2d(s, r) - atan2d(l3*sind(q3B), l2 + l3*cosd(q3B));   % 57,642° «5»
      TA = cinematica_directa([q1 q2A q3A], [l1 0 0], [0 l2 l3], [90 0 0], 'deg'); «6»
      PA = TA(1:3, 4)'                               % 0,3  0,25  0,6 «6»
    '''),
    'ojo': ['`atand(y/x)` se equivoca de cuadrante: con P = (−0,2; 0,35) da −60,26° en vez de 119,74°.',
            'La ley del coseno se plantea desde el **hombro**: s = z − l1, no z.',
            'Calcular un solo q2 para las dos soluciones: cada q3 tiene el suyo.',
            'Con q3 > 0 el codo queda abajo y con q3 < 0, arriba. Si el enunciado no aclara, informá las dos.'],
    'parcial': 'Es el ejercicio 1: te dan l1, l2, l3 y el punto, y piden las dos soluciones (q1, q2, q3) verificadas con la directa, con el código.',
    'pdf': 3, 'herramienta': 'robot2r',
  },
  [
    oct_ej('2.1', 'atan2d', 'el giro de la base', 'El punto es P = (−0,2; 0,35; 0,5) m. Calculá q1 con `atan2d` y guardalo en `q1`. Calculá también `mal = atand(y/x)` para ver por qué no se usa.',
      r'''
      x = -0.2; y = 0.35; z = 0.5;
      % q1  = ...
      % mal = ...
      ''', r'''
      x = -0.2; y = 0.35; z = 0.5;
      q1  = atan2d(y, x)
      mal = atand(y/x)
      ''', vars=['q1', 'mal'], respuestas=[R('q1', 'q1', 2, '°'), OP('¿Cuál apunta al punto?', ['atan2d(y, x)', 'atand(y/x)'], 'atan2d(y, x)', 'El punto está en el 2º cuadrante (x < 0, y > 0): atand(y/x) da un ángulo del 4º.')],
      imagen=RRR, pasos=['`q1 = atan2d(y, x)`: primero y, después x.'],
      mensajes={'q1': '`q1` no da: es atan2d(y, x), con y primero'}),
    oct_ej('2.2', 'El plano del brazo', 'r, s y la ley del coseno', 'RRR con l1 = 0,4 m, l2 = 0,3 m y l3 = 0,3 m; el punto es P = (−0,2; 0,35; 0,5) m. Calculá `r`, `s`, `L` y `D` (el coseno de q3).',
      r'''
      l1 = 0.4; l2 = 0.3; l3 = 0.3;
      x = -0.2; y = 0.35; z = 0.5;
      % r = ...   distancia horizontal
      % s = ...   altura desde el hombro
      % L = ...   distancia hombro-punto
      % D = ...   ley del coseno
      ''', r'''
      l1 = 0.4; l2 = 0.3; l3 = 0.3;
      x = -0.2; y = 0.35; z = 0.5;
      r = hypot(x, y)
      s = z - l1
      L = hypot(r, s)
      D = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3)
      ''', vars=['r', 's', 'L', 'D'], respuestas=[R('r', 'r', 4, 'm'), R('s', 's', 4, 'm'), R('D', 'D', 4)],
      pasos=['`r = hypot(x, y)` (es lo mismo que `sqrt(x^2 + y^2)`).', '`s = z - l1`.', '`D = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3)`.'],
      pistas=['Si te da s = 0,5, te olvidaste de restar l1.'],
      mensajes={'s': '`s` no da: la altura se mide desde el hombro (z − l1)', 'D': '`D` no da: (r² + s² − l2² − l3²) / (2·l2·l3)'}),
    oct_ej('2.3', 'Las dos soluciones', 'las dos soluciones', 'Con el robot y el punto del ejercicio anterior, calculá las dos soluciones: `solA = [q1 q2A q3A]` con q3 > 0 y `solB = [q1 q2B q3B]` con q3 < 0.',
      r'''
      l1 = 0.4; l2 = 0.3; l3 = 0.3;
      x = -0.2; y = 0.35; z = 0.5;
      q1 = atan2d(y, x);
      r = hypot(x, y);  s = z - l1;
      D = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3);
      % q3A = ...   (positivo)
      % q3B = ...   (negativo)
      % q2A = ...
      % q2B = ...
      % solA = [q1 q2A q3A]
      % solB = [q1 q2B q3B]
      ''', r'''
      l1 = 0.4; l2 = 0.3; l3 = 0.3;
      x = -0.2; y = 0.35; z = 0.5;
      q1 = atan2d(y, x);
      r = hypot(x, y);  s = z - l1;
      D = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3);
      q3A =  atan2d(sqrt(1 - D^2), D);
      q3B = -atan2d(sqrt(1 - D^2), D);
      q2A = atan2d(s, r) - atan2d(l3*sind(q3A), l2 + l3*cosd(q3A));
      q2B = atan2d(s, r) - atan2d(l3*sind(q3B), l2 + l3*cosd(q3B));
      solA = [q1 q2A q3A]
      solB = [q1 q2B q3B]
      ''', vars=['solA', 'solB'], respuestas=[R('q2 (A)', 'q2A', 2, '°'), R('q3 (A)', 'q3A', 2, '°'), R('q2 (B)', 'q2B', 2, '°'), R('q3 (B)', 'q3B', 2, '°')],
      pasos=['`q3A = atan2d(sqrt(1 - D^2), D)` y `q3B = -q3A`.', 'q2 se calcula una vez con cada q3.'],
      pistas=['Es la «Práctica 2» del resumen: q1 = 119,74°.'],
      mensajes={'solB': '`solB` no da: ¿calculaste q2B con q3B (y no con q3A)?'}),
    oct_ej('2.4', 'Ejercicio completo', 'el ejercicio 1 completo, con la verificación', 'Un robot RRR tiene l1 = 0,5 m, l2 = 0,4 m y l3 = 0,3 m. Calcular por el método geométrico los valores articulares que llevan el extremo al punto P = (0,25; −0,35; 0,75) m. Informar ambas soluciones (`solA` con q3 > 0, `solB` con q3 < 0) y verificarlas con `cinematica_directa` (`PA` y `PB`, la posición de cada una como columna).',
      r'''
      l1 = 0.5; l2 = 0.4; l3 = 0.3;   % [m]
      x = 0.25; y = -0.35; z = 0.75;
      % 1) q1   2) r y s   3) ¿llega?   4) D, q3A y q3B   5) q2A y q2B
      % solA = ...;  solB = ...;
      % 6) verificación
      % PA = ...;  PB = ...;
      ''', r'''
      l1 = 0.5; l2 = 0.4; l3 = 0.3;
      x = 0.25; y = -0.35; z = 0.75;
      q1 = atan2d(y, x);
      r = hypot(x, y);  s = z - l1;
      L = hypot(r, s);
      if L > l2 + l3 || L < abs(l2 - l3), error('Fuera de alcance'); end
      D = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3);
      q3A =  atan2d(sqrt(1 - D^2), D);
      q3B = -atan2d(sqrt(1 - D^2), D);
      q2A = atan2d(s, r) - atan2d(l3*sind(q3A), l2 + l3*cosd(q3A));
      q2B = atan2d(s, r) - atan2d(l3*sind(q3B), l2 + l3*cosd(q3B));
      solA = [q1 q2A q3A]
      solB = [q1 q2B q3B]
      TA = cinematica_directa(solA, [l1 0 0], [0 l2 l3], [90 0 0], 'deg');  PA = TA(1:3, 4)
      TB = cinematica_directa(solB, [l1 0 0], [0 l2 l3], [90 0 0], 'deg');  PB = TB(1:3, 4)
      ''', vars=['solA', 'solB', 'PA', 'PB'], respuestas=[R('q1', 'q1', 2, '°'), R('q2 (A)', 'q2A', 2, '°'), R('q3 (A)', 'q3A', 2, '°'), R('q2 (B)', 'q2B', 2, '°'), R('q3 (B)', 'q3B', 2, '°')],
      imagen=RRR, pasos=['Seguí los 6 pasos de la explicación, en orden.', 'La verificación: las dos tienen que dar (0,25; −0,35; 0,75).'],
      pistas=['q1 queda negativo: el punto está en el 4º cuadrante.'],
      checks=[C(r'cinematica_directa\s*\(', 'Verifica con cinematica_directa', 'Falta verificar con `cinematica_directa`')]),
    oct_ej('2.5', '¿Llega?', 'un punto fuera de alcance', 'Con l1 = 0,45 m, l2 = 0,35 m y l3 = 0,25 m, ¿llega el robot al punto P = (0,6; 0,2; 0,9) m? Calculá `L` y `D`, y guardá en `llega` si se cumple |l2 − l3| ≤ L ≤ l2 + l3 (verdadero o falso).',
      r'''
      l1 = 0.45; l2 = 0.35; l3 = 0.25;
      x = 0.6; y = 0.2; z = 0.9;
      % L = ...
      % D = ...
      % llega = ...   (una condición: true o false)
      ''', r'''
      l1 = 0.45; l2 = 0.35; l3 = 0.25;
      x = 0.6; y = 0.2; z = 0.9;
      r = hypot(x, y);  s = z - l1;
      L = hypot(r, s)
      D = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3)
      llega = L >= abs(l2 - l3) && L <= l2 + l3
      ''', vars=['L', 'D', 'llega'], respuestas=[R('L', 'L', 4, 'm'), OP('¿Llega?', ['Sí', 'No'], 'No', 'L = 0,776 m es más que l2 + l3 = 0,6 m. Por eso D da más que 1 y sqrt(1 − D²) no es real.')],
      pasos=['`llega = L >= abs(l2 - l3) && L <= l2 + l3`.'],
      pistas=['Con D > 1, `sqrt(1 - D^2)` daría un número complejo: la función del profe tira error.']),
    oct_ej('2.6', 'Codo arriba o abajo', '¿cuál es codo arriba?', 'Las dos soluciones del ejemplo de la explicación (l1 = 0,45 m, l2 = 0,35 m) son A = (39,806°; −15,617°; 93,276°) y B = (39,806°; 57,642°; −93,276°). Calculá la altura del codo (el origen 2) en cada una, `zA` y `zB`: es l1 + l2·sen q2.',
      r'''
      l1 = 0.45; l2 = 0.35;
      solA = [39.806 -15.617 93.276];
      solB = [39.806  57.642 -93.276];
      % zA = ...
      % zB = ...
      ''', r'''
      l1 = 0.45; l2 = 0.35;
      solA = [39.806 -15.617 93.276];
      solB = [39.806  57.642 -93.276];
      zA = l1 + l2*sind(solA(2))
      zB = l1 + l2*sind(solB(2))
      ''', vars=['zA', 'zB'], respuestas=[R('Altura del codo en A', 'zA', 3, 'm'), R('Altura del codo en B', 'zB', 3, 'm'),
        OP('¿Cuál es codo arriba?', ['A (q3 > 0)', 'B (q3 < 0)'], 'B (q3 < 0)', 'En B el codo queda a 0,746 m, más alto que la punta: codo arriba. En la rutina del profe, use_elbow = "up" elige q3 positivo: fijate la convención del enunciado.')],
      pasos=['q2 es el segundo elemento: `solA(2)`.']),
  ]))

# ======================= 3 · Jacobiano =======================
partes.append(parte(3, 'jacobiano', 'El Jacobiano', 'Jacobiano',
  'El Jacobiano dice cuánto se mueve la punta si se mueve un poquito cada articulación: ΔP ≈ J·Δq. Cada columna es una articulación: z × (p − p_i) si gira, z si se desliza; las rotativas, por π/180 porque se trabaja en grados.',
  {
    'que': 'El **Jacobiano** es la matriz de derivadas de la posición de la punta respecto de cada articulación: dice cuánto se mueve la punta si se mueve un poquito cada una, ΔP ≈ J·Δq.\n'
           'Cada **columna** es el movimiento de la punta cuando se mueve una sola articulación. Es lo que usa la inversa numérica para saber cuánto corregir en cada vuelta.',
    'consta': [
      ['Una columna por articulación', '`jacobiano_analitico` devuelve 6×n: las filas 1–3 son la posición (las que usa DLS) y las 4–6, la orientación.'],
      ['Rotativa', '`cross(z, p - p_i)`: la punta se mueve perpendicular al eje y al «brazo de palanca».'],
      ['Prismática', '`z`: la punta se mueve en la dirección del eje.'],
      ['El factor π/180', 'Las funciones trabajan en grados: las columnas de las rotativas se multiplican por π/180 (las prismáticas no).'],
      ['Analítico o numérico', '`jacobiano_numerico` lo calcula por diferencias finitas: tiene que dar lo mismo.'],
    ],
    'ejemplo': ejemplo('jacobiano.m', 'Ejercicio 2 del resumen: el cilíndrico en la semilla', r'''
      l1 = 400; l4 = 100;                          % [mm]
      tipo = 'RPPR'; q_offset = [0; 90; 0; 0]; d_offset = [l1; 0; 0; l4];
      a = [0; 0; 0; 0]; alpha = [0; 90; 0; 0];
      q0 = [0; 100; 100; 0];                       % [deg; mm; mm; deg]
      J  = jacobiano_analitico(q0, tipo, q_offset, d_offset, a, alpha, 'deg');
      Jp = J(1:3, :)                               % 3x4: la parte de posición «1»
      % columna q1 (R): cross([0;0;1], p - p0) = (0; 200; 0) mm por radián «2»
      % columna d2 (P): (0; 0; 1), sube en z.   columna d3 (P): (1; 0; 0) «3»
      % por grado: 200 * pi/180 = 3,4907 mm (la columna q1 de Jp) «4»
      Jn = jacobiano_numerico(q0, tipo, q_offset, d_offset, a, alpha, 'deg'); «5»
    '''),
    'ojo': ['Las derivadas son por radián: sin el π/180 la columna de una rotativa da 57 veces más grande.',
            'Una columna de ceros (como la muñeca q4 del cilíndrico) quiere decir que esa articulación no mueve la punta.',
            'Cerca de una singularidad (brazo estirado, punto sobre el eje Z) J pierde rango y su inversa «explota»: por eso se usa DLS.'],
    'parcial': 'En el formato «resultados a completar» piden el Jacobiano en la semilla: es la primera iteración de la inversa numérica.',
    'pdf': 4,
  },
  [
    oct_ej('3.1', 'jacobiano_analitico', 'el Jacobiano en la semilla', 'El cilíndrico del resumen, cargado como para la inversa (ya está en el código). Calculá el Jacobiano en la semilla q0 = (0°; 100 mm; 100 mm; 0°) con `jacobiano_analitico` y guardá su parte de posición (filas 1 a 3) en `Jp`.',
      CIL_RES + r'''
      q0 = [0; 100; 100; 0];
      % J  = jacobiano_analitico( ... );
      % Jp = ...
      ''', CIL_RES + r'''
      q0 = [0; 100; 100; 0];
      J  = jacobiano_analitico(q0, tipo, q_offset, d_offset, a, alpha, 'deg');
      Jp = J(1:3, :)
      ''', vars=['Jp'], respuestas=[R('¿Cuántos mm se mueve la punta en y por cada grado de q1? (Jp(2,1))', 'Jp(2,1)', 4, 'mm'),
        OP('¿Qué articulación tiene la columna de ceros?', ['q1', 'd2', 'd3', 'q4'], 'q4', 'La muñeca gira sobre su eje: no mueve la punta.')], imagen=CIL,
      pasos=["`J = jacobiano_analitico(q0, tipo, q_offset, d_offset, a, alpha, 'deg')`: los mismos argumentos que la inversa, sin pd.", '`Jp = J(1:3, :)`.'],
      mensajes={'Jp': '`Jp` no da: son las filas 1 a 3 (todas las columnas)'}),
    oct_ej('3.2', 'Columna de una rotativa', 'la columna de q1, a mano', 'Con el mismo robot en q0 = (0°; 100 mm; 200 mm; 0°): calculá a mano la columna de q1, `c1 = cross([0; 0; 1], p) * pi/180`, donde p es la punta (el eje z0 pasa por el origen). Compará con la primera columna del Jacobiano de la función, `J1`.',
      CIL_RES + r'''
      q0 = [0; 100; 200; 0];
      th = q_offset + [q0(1); 0; 0; q0(4)];     % los θ con las variables
      dd = d_offset + [0; q0(2); q0(3); 0];     % los d con las variables
      T = cinematica_directa(th, dd, a, alpha, 'deg');
      p = T(1:3, 4);
      % c1 = ...
      % J1 = ...   (la columna 1 de jacobiano_analitico, filas 1 a 3)
      ''', CIL_RES + r'''
      q0 = [0; 100; 200; 0];
      th = q_offset + [q0(1); 0; 0; q0(4)];
      dd = d_offset + [0; q0(2); q0(3); 0];
      T = cinematica_directa(th, dd, a, alpha, 'deg');
      p = T(1:3, 4);
      c1 = cross([0; 0; 1], p) * pi/180
      J  = jacobiano_analitico(q0, tipo, q_offset, d_offset, a, alpha, 'deg');
      J1 = J(1:3, 1)
      ''', vars=['c1', 'J1'], respuestas=[R('La componente y de la columna', 'c1(2)', 4, 'mm/°')],
      pasos=['`cross([0; 0; 1], p)` da (−py, px, 0).', 'Multiplicalo por `pi/180`.'],
      pistas=['El brazo radial ahora mide d3 + l4 = 300 mm: 300·π/180.'],
      checks=[C(r'cross\s*\(', 'Usa cross', 'Calculá `c1` con `cross`')],
      mensajes={'c1': '`c1` no da: ¿lo multiplicaste por pi/180?'}),
    oct_ej('3.3', 'Analítico o numérico', 'analítico contra numérico', 'Para el RRR de la clase (l1 = 0,5 m, l2 = 0,3 m, l3 = 0,2 m) en q = (0°, 30°, 30°), calculá `Ja` con `jacobiano_analitico` y `Jn` con `jacobiano_numerico` (los dos, solo las filas 1 a 3), y la diferencia más grande entre los dos, `dif`.',
      r'''
      l1 = 0.5; l2 = 0.3; l3 = 0.2;
      tipo = 'RRR';
      q_offset = [0; 0; 0];  d_offset = [l1; 0; 0];
      a = [0; l2; l3];  alpha = [90; 0; 0];
      q = [0; 30; 30];
      % Ja  = ...
      % Jn  = ...
      % dif = max(max(abs(Ja - Jn)))
      ''', r'''
      l1 = 0.5; l2 = 0.3; l3 = 0.2;
      tipo = 'RRR';
      q_offset = [0; 0; 0];  d_offset = [l1; 0; 0];
      a = [0; l2; l3];  alpha = [90; 0; 0];
      q = [0; 30; 30];
      J  = jacobiano_analitico(q, tipo, q_offset, d_offset, a, alpha, 'deg');  Ja = J(1:3, :)
      J  = jacobiano_numerico(q, tipo, q_offset, d_offset, a, alpha, 'deg');   Jn = J(1:3, :)
      dif = max(max(abs(Ja - Jn)))
      ''', vars=['Ja'], respuestas=[OP('¿Dan lo mismo?', ['Sí (salvo redondeo)', 'No'], 'Sí (salvo redondeo)', 'Las diferencias finitas aproximan la derivada: la diferencia es chiquita.')],
      pasos=['Con las tres R, q_offset es 0 y d_offset es la columna d de la tabla.']),
    elegir_ej('3.4', 'Las columnas', '¿cómo es cada columna?', 'Para cada articulación, ¿cómo es su columna de posición en el Jacobiano?', ['z × (p − p_i)', 'z', 'Ceros'], [
      ('Una articulación rotativa', 'z × (p − p_i)', 'Al girar, la punta se mueve perpendicular al eje y al brazo de palanca.'),
      ('Una articulación prismática', 'z', 'Al deslizar, la punta se mueve en la dirección del eje.'),
      ('q1 del cilíndrico (gira la base)', 'z × (p − p_i)', 'Es rotativa: la punta se mueve tangente al giro.'),
      ('d2 del cilíndrico (sube y baja)', 'z', 'Su eje es vertical: la columna es (0, 0, 1).'),
      ('q4 del cilíndrico (gira la muñeca sobre su eje, con la punta en el eje)', 'Ceros', 'p − p_i es paralelo al eje: el producto vectorial da cero.'),
    ], pregunta='¿Cómo es su columna?'),
  ]))

# ======================= 4 · CI numérica (DLS) =======================
partes.append(parte(4, 'dls', 'Cinemática inversa numérica (DLS)', 'CI numérica',
  'Se prueba, se mide el error y se corrige: directa en q → e = pd − p → Jacobiano → Δq por DLS → q = q + Δq, hasta que el error sea menor que la tolerancia. `cinematica_inversa` hace el ciclo; lo difícil es cargar bien el robot y elegir la semilla.',
  {
    'que': 'Cuando el robot es más complicado (o mezcla R y P) no se busca una fórmula: se **prueba, se mide el error y se corrige**, muchas veces, hasta llegar. En cada vuelta: directa en q → error e = pd − p → Jacobiano → corrección Δq por **DLS** → q = q + Δq.\n'
           'La función del profe `cinematica_inversa` hace todo el ciclo. Lo que hay que hacer bien es **cargar el robot** (la tabla DH en forma de offsets) y elegir la **semilla**.',
    'consta': [
      ['El robot en offsets', 'Copiá las columnas θ y d de la tabla: donde hay una variable va 0 (o su offset). `tipo` dice si cada una es R o P.'],
      ['La semilla q0', 'Converge a la solución más cercana: poné q1 ≈ atan2d(y, x).'],
      ['La corrección DLS', "`dq = Jp' * ((Jp*Jp' + lambda^2*eye(3)) \\ e)`, con λ = 0,05 por defecto."],
      ['Las 5 salidas', '`[q_sol, theta, d, success, info]`: `success` es 1 si llegó, `info.iters` son las vueltas e `info.err_pos` el error final.'],
      ['Las opciones', '`opts.q_min` y `opts.q_max` (límites), `opts.verbose = true` (una línea por vuelta) y `opts.tol_pos` (1e-3: trabajá en mm).'],
      ['Verificar', 'La directa con la solución tiene que volver a pd, y los valores tienen que tener sentido (una prismática no puede ser negativa).'],
    ],
    'ejemplo': ejemplo('ci_dls.m', 'Ejercicio 2 del resumen (modelo del 2º parcial)', r'''
      l1 = 400;  l4 = 100;                         % [mm]
      tipo     = 'RPPR'; «1»
      q_offset = [0; 90; 0; 0];    % θ: q1 -> 0, 90 fijo, 0 fijo, q4 -> 0 «1»
      d_offset = [l1; 0; 0; l4];   % d: l1 fijo, d2 -> 0, d3 -> 0, l4 fijo «1»
      a = [0; 0; 0; 0];   alpha = [0; 90; 0; 0];
      pd = [300; 250; 650];                        % [mm]
      q0 = [0; 100; 100; 0];                       % [deg; mm; mm; deg] «2»
      % por dentro, en cada vuelta: dq = Jp' * ((Jp*Jp' + 0.05^2*eye(3)) \ e) «3»
      [q_sol, theta, d, success, info] = cinematica_inversa(pd, q0, tipo, q_offset, d_offset, a, alpha, 'deg') «4»
      % q_sol = (39,81; 250; 290,51; 0), success = 1, info.iters = 6 «4»
      opts.verbose = true;  opts.q_min = [-180; 0; 0; -180];  opts.q_max = [180; 600; 600; 180]; «5»
      T = cinematica_directa(q_offset + [q_sol(1); 0; 0; q_sol(4)], d_offset + [0; q_sol(2); q_sol(3); 0], a, alpha, 'deg'); «6»
      error_final = norm(pd - T(1:3, 4))           % 2,83e-4 mm «6»
    '''),
    'ojo': ['`[q, ok] = cinematica_inversa(...)`: la del 2º parcial tiene 5 salidas, y en `ok` te queda theta, no el éxito.',
            'La variable **no** va en q_offset ni en d_offset: ahí va 0 (o su offset).',
            'Con una semilla lejos, DLS puede llegar a una solución imposible (girar 180° de más con d3 negativo) y dar success = 1. Mejor semilla o límites.',
            'Trabajá en mm: la tolerancia 1e-3 está pensada en mm. En metros, pasá `opts.tol_pos = 1e-6`.'],
    'parcial': 'Es el ejercicio 2: un robot (cilíndrico, RPR, RPP o el ABB IRB2400 de 6 GDL) y puntos para completar con los valores articulares. A veces piden también la primera iteración (p0, e, J y Δq).',
    'pdf': 5,
  },
  [
    oct_ej('4.1', 'Una vuelta a mano', 'la primera iteración, a mano', 'Hacé a mano la primera vuelta de DLS del ejemplo (pd = (300; 250; 650) mm, q0 = (0°; 100; 100; 0°), λ = 0,05): la punta en la semilla `p0`, el error `e`, la parte de posición del Jacobiano `Jp`, la corrección `dq` y la postura después de la vuelta, `qn`.',
      CIL_RES + r'''
      pd = [300; 250; 650];
      q0 = [0; 100; 100; 0];
      lambda = 0.05;
      th = q_offset + [q0(1); 0; 0; q0(4)];
      dd = d_offset + [0; q0(2); q0(3); 0];
      % p0 = ...   (cinematica_directa con th y dd)
      % e  = ...
      % Jp = ...
      % dq = ...   (la fórmula de DLS)
      % qn = ...
      ''', CIL_RES + r'''
      pd = [300; 250; 650];
      q0 = [0; 100; 100; 0];
      lambda = 0.05;
      th = q_offset + [q0(1); 0; 0; q0(4)];
      dd = d_offset + [0; q0(2); q0(3); 0];
      T  = cinematica_directa(th, dd, a, alpha, 'deg');
      p0 = T(1:3, 4)
      e  = pd - p0
      J  = jacobiano_analitico(q0, tipo, q_offset, d_offset, a, alpha, 'deg');
      Jp = J(1:3, :);
      dq = Jp' * ((Jp*Jp' + lambda^2*eye(3)) \ e)
      qn = q0 + dq
      ''', vars=['p0', 'e', 'dq', 'qn'], respuestas=[R('‖e‖ (el error inicial)', 'norm(e)', 2, 'mm'), R('Δq1', 'dq(1)', 2, '°'), R('d3 después de la vuelta', 'qn(3)', 2, 'mm')],
      pasos=['`p0 = T(1:3, 4)` y `e = pd - p0`.', "`Jp = J(1:3, :)`, con `jacobiano_analitico`.", "`dq = Jp' * ((Jp*Jp' + lambda^2*eye(3)) \\ e)`."],
      pistas=['q1 se pasa de largo (71,6° cuando la respuesta es 39,8°): el Jacobiano es lineal y el giro no. Por eso hacen falta varias vueltas.'],
      mensajes={'dq': "`dq` no da: Jp' * ((Jp*Jp' + lambda^2*eye(3)) \\ e)"}),
    oct_ej('4.2', 'Cargar el robot', 'cargar el robot y resolver', 'El cilíndrico RPPR del parcial 2026, con l1 = 600 mm y l4 = 200 mm (tabla θ = q1 90 0 q4, d = l1 d2 d3 l4, a = 0 0 0 0, α = 0 90 0 0). Cargalo para `cinematica_inversa` y resolvé el punto pd = (375; −649,52; 1350) mm con la semilla q0 = (atan2d(y, x); 500; 500; 0).\n\nGuardá la solución en `q` y el éxito en `ok`.',
      r'''
      l1 = 600; l4 = 200;
      % tipo = ...;  q_offset = ...;  d_offset = ...;  a = ...;  alpha = ...;
      pd = [375; -649.52; 1350];
      q0 = [atan2d(pd(2), pd(1)); 500; 500; 0];
      % [q, theta, d, ok, info] = cinematica_inversa( ... );
      ''', r'''
      l1 = 600; l4 = 200;
      tipo = 'RPPR';
      q_offset = [0; 90; 0; 0];
      d_offset = [l1; 0; 0; l4];
      a = [0; 0; 0; 0];
      alpha = [0; 90; 0; 0];
      pd = [375; -649.52; 1350];
      q0 = [atan2d(pd(2), pd(1)); 500; 500; 0];
      [q, theta, d, ok, info] = cinematica_inversa(pd, q0, tipo, q_offset, d_offset, a, alpha, 'deg')
      ''', vars=['q', 'ok'], respuestas=[R('q1', 'q(1)', 2, '°'), R('d2', 'q(2)', 2, 'mm'), R('d3', 'q(3)', 2, 'mm')], imagen=CIL,
      pasos=['q_offset es la columna θ con 0 donde está q1 y q4: `[0; 90; 0; 0]`.', 'd_offset es la columna d con 0 donde están d2 y d3: `[l1; 0; 0; l4]`.', 'Pedí las 5 salidas.'],
      pistas=['Control: d2 = z − l1 = 750 y d3 = √(x² + y²) − l4 = 550.'],
      checks=[C(r'cinematica_inversa\s*\(', 'Usa cinematica_inversa', 'Resolvelo con `cinematica_inversa`')],
      mensajes={'q': '`q` no da: revisá q_offset y d_offset (donde hay una variable va 0)', 'ok': '`ok` tiene que ser el success: la 4ª salida'}),
    oct_ej('4.3', 'La semilla', 'la trampa de la semilla', 'Con el cilíndrico del resumen, el punto pd = (−150; 200; 550) mm y la semilla q0 = (0°; 100; 100; 0°), DLS converge a una solución imposible. Probalo, y después pasale límites con `opts.q_min = [-180; 0; 0; -180]` y `opts.q_max = [180; 600; 600; 180]` para que dé la correcta.\n\nGuardá la solución buena en `q`, el éxito en `ok` y la cantidad de vueltas en `iters`.',
      CIL_RES + r'''
      pd = [-150; 200; 550];
      q0 = [0; 100; 100; 0];
      [qmal, ~, ~, okmal] = cinematica_inversa(pd, q0, tipo, q_offset, d_offset, a, alpha, 'deg')
      % opts.q_min = ...;  opts.q_max = ...;
      % [q, ~, ~, ok, info] = cinematica_inversa( ..., opts);
      % iters = info.iters
      ''', CIL_RES + r'''
      pd = [-150; 200; 550];
      q0 = [0; 100; 100; 0];
      [qmal, ~, ~, okmal] = cinematica_inversa(pd, q0, tipo, q_offset, d_offset, a, alpha, 'deg')
      opts.q_min = [-180; 0; 0; -180];
      opts.q_max = [180; 600; 600; 180];
      [q, ~, ~, ok, info] = cinematica_inversa(pd, q0, tipo, q_offset, d_offset, a, alpha, 'deg', opts)
      iters = info.iters
      ''', vars=['q', 'ok', 'iters'], respuestas=[R('q1', 'q(1)', 2, '°'), R('d3', 'q(3)', 2, 'mm'), R('¿Cuánto daba d3 sin límites?', 'qmal(3)', 2, 'mm', 'Negativo: el brazo «hacia atrás». success daba 1 igual.')],
      pasos=['Mirá `qmal`: d3 sale negativo.', 'Armá `opts` con los dos límites y pasalo como último argumento.', '`iters = info.iters`.'],
      pistas=['La otra forma de arreglarlo: semilla con q1 ≈ atan2d(200, −150) = 126,87°.'],
      checks=[C(r'q_min', 'Usa límites', 'Agregá los límites con `opts.q_min` y `opts.q_max`')],
      mensajes={'q': '`q` no da la solución con d3 positivo: ¿pasaste opts como último argumento?'}),
    oct_ej('4.4', 'RPP', 'el cilíndrico de 3 GDL', 'Cilíndrico de 3 GDL (RPP) con l1 = 300 mm, sin muñeca: `tipo = \'RPP\'`, `q_offset = [0; 90; 0]`, `d_offset = [300; 0; 0]`, `a = [0; 0; 0]`, `alpha = [0; 90; 0]`. Resolvé pd = (250; −250; 500) mm con q0 = (−45°; 100; 100).\n\nGuardá `q` e `iters`.',
      r'''
      % tipo = ...;  q_offset = ...;  d_offset = ...;  a = ...;  alpha = ...;
      pd = [250; -250; 500];
      q0 = [-45; 100; 100];
      % [q, ~, ~, ok, info] = cinematica_inversa( ... );
      ''', r'''
      tipo = 'RPP';
      q_offset = [0; 90; 0];
      d_offset = [300; 0; 0];
      a = [0; 0; 0];
      alpha = [0; 90; 0];
      pd = [250; -250; 500];
      q0 = [-45; 100; 100];
      [q, ~, ~, ok, info] = cinematica_inversa(pd, q0, tipo, q_offset, d_offset, a, alpha, 'deg')
      iters = info.iters
      ''', vars=['q', 'iters'], respuestas=[R('q1', 'q(1)', 2, '°'), R('d2', 'q(2)', 2, 'mm'), R('d3', 'q(3)', 2, 'mm'), R('Iteraciones', 'iters', 0)],
      pistas=['Con la semilla bien orientada (q1 = −45°), llega en pocas vueltas.']),
    oct_ej('4.5', '6 GDL', 'el ABB IRB2400 (6 GDL)', 'El ABB IRB2400 del parcial 2026 (RRRPRR): l1 = 770, l2 = 420, l3 = 400, l4 = 250 mm. La tabla (θ, d, a, α) es (q1, l1, 0, −90), (q2, 0, l2, 0), (q3, 0, 0, 90), (0, l3 + d4, 0, −90), (q5, 0, 0, 90), (q6, l4, 0, 0). El enunciado fija d4 = 0, θ5 = 0 y θ6 = 0: se congelan con límites iguales.\n\nResolvé el punto (−127,12; −115,63; 1024,95) mm con la semilla [atan2d(y, x); 20; −45; 0; 0; 0]. Guardá `q` y `ok`.',
      r'''
      l1 = 770; l2 = 420; l3 = 400; l4 = 250;
      tipo     = 'RRRPRR';
      q_offset = [0; 0; 0; 0; 0; 0];
      d_offset = [l1; 0; 0; l3; 0; l4];
      a        = [0; l2; 0; 0; 0; 0];
      alpha    = [-90; 0; 90; -90; 90; 0];
      % opts.q_min = ...;  opts.q_max = ...;   (d4, q5 y q6 congelados en 0)
      P = [-127.12; -115.63; 1024.95];
      % q0 = ...
      % [q, ~, ~, ok] = cinematica_inversa( ..., opts);
      ''', r'''
      l1 = 770; l2 = 420; l3 = 400; l4 = 250;
      tipo     = 'RRRPRR';
      q_offset = [0; 0; 0; 0; 0; 0];
      d_offset = [l1; 0; 0; l3; 0; l4];
      a        = [0; l2; 0; 0; 0; 0];
      alpha    = [-90; 0; 90; -90; 90; 0];
      opts.q_min = [-360; -360; -360; 0; 0; 0];
      opts.q_max = [ 360;  360;  360; 0; 0; 0];
      P = [-127.12; -115.63; 1024.95];
      q0 = [atan2d(P(2), P(1)); 20; -45; 0; 0; 0];
      [q, ~, ~, ok] = cinematica_inversa(P, q0, tipo, q_offset, d_offset, a, alpha, 'deg', opts)
      ''', vars=['q', 'ok'], respuestas=[R('θ1', 'q(1)', 2, '°'), R('θ2', 'q(2)', 2, '°'), R('θ3', 'q(3)', 2, '°')],
      pasos=['Límites iguales congelan una articulación: `q_min(4:6) = q_max(4:6) = 0`.', 'Las tres primeras, libres: ±360.'],
      pistas=['La otra rama del codo sale con la semilla [q1; −170; −135; 0; 0; 0]. En el parcial se aceptaban las dos, consistentes en la fila.'],
      checks=[C(r'q_max', 'Congela con límites', 'Congelá d4, θ5 y θ6 con `opts.q_min` y `opts.q_max` iguales')]),
    elegir_ej('4.6', 'Errores típicos', '¿está bien o resta puntos?', 'Los errores que más puntos hacen perder en el ejercicio 2. ¿Está bien o mal?', ['Bien', 'Mal'], [
      ('`[q, ok] = cinematica_inversa(...)` para saber si llegó', 'Mal', 'La del 2º parcial tiene 5 salidas: en la 2ª queda theta. El éxito es la 4ª.'),
      ('Poner la variable de la articulación en q_offset', 'Mal', 'Donde hay una variable va 0 (o su offset).'),
      ('Semilla con q1 ≈ atan2d(y, x)', 'Bien', 'Así converge a la solución del lado del punto.'),
      ('Aceptar d3 = −350 mm porque success dio 1', 'Mal', 'Es matemáticamente correcta pero físicamente imposible: mejor semilla o límites.'),
      ('Trabajar en mm con la tolerancia por defecto (1e-3)', 'Bien', 'Está pensada en mm. En metros sería 1 mm de error.'),
      ('Verificar con cinematica_directa que la solución vuelve al punto', 'Bien', 'Es la forma de no entregar un error de carga.'),
    ], pregunta='¿Bien o mal?'),
  ]))

# ======================= 5 · La tabla del parcial 2026 =======================
TABLA_CIL = '''
P = [ 375.00  -649.52  1350.00;
      282.84   282.84  1000.00;
     1200.00     0.00  1000.00;
      103.53   386.37  1100.00;
     1039.23   600.00  1500.00];
'''
TABLA_RPP = '''
P = [-200.00  346.41  550.00;
      150.00  259.81  600.00;
     -150.00    0.00  200.00;
     -389.71  225.00  600.00;
      318.20  318.20  250.00];
'''
TABLA_RPR = '''
P = [ 398.09  106.67  362.13;
     -444.14  119.01    0.00;
     -300.00  519.62  150.00;
     -312.13    0.00  -62.13;
      310.97  310.97   72.35];
'''
partes.append(parte(5, 'tabla', 'Completar la tabla (parcial 2026)', 'La tabla del parcial',
  'Cada alumno tuvo un robot y una tabla de puntos para completar con los valores articulares. En el cilíndrico, el RPP y el RPR sale por geometría con tres líneas por fila; siempre se cierra verificando con la directa.',
  {
    'que': 'En el parcial 2026 cada alumno tuvo un robot y una **tabla de puntos (x, y, z)** para completar con los valores articulares. Aunque el tema era la inversa numérica, en el cilíndrico, el RPP y el RPR la tabla sale **por geometría**, con tres líneas por fila, y se cierra verificando con la directa.\n'
           'Para el de 6 GDL (IRB2400) se usa `cinematica_inversa` congelando lo que fija el enunciado (la parte 4).',
    'consta': [
      ['Los puntos en una matriz', 'Una fila por punto: `P = [x1 y1 z1; x2 y2 z2; ...]`.'],
      ['El ángulo de la base', '`atan2d(y, x)`, o `atan2d(-x, y)` si con q1 = 0 el brazo apunta sobre el eje y.'],
      ['Altura y radio', 'La altura da la prismática vertical (`z - l1`) y `hypot(x, y)` la radial (menos l4 si hay muñeca).'],
      ['Un for por fila', 'La tabla Q se arma fila por fila y se muestra con `printf`.'],
      ['Verificar cada fila', '`cinematica_directa` con la fila tiene que volver a su punto.'],
    ],
    'ejemplo': ejemplo('tabla_cilindrico.m', '2º parcial 2026: el robot cilíndrico RPPR', r'''
      l1 = 600; l4 = 200;                                   % [mm]
      P = [375.00 -649.52 1350.00; 282.84 282.84 1000.00];  % una fila por punto «1»
      Q = zeros(size(P, 1), 4);
      for k = 1:size(P, 1) «4»
        x = P(k,1); y = P(k,2); z = P(k,3);
        q1 = atan2d(y, x);                    % el brazo apunta al punto «2»
        d2 = z - l1;                          % la altura «3»
        d3 = hypot(x, y) - l4;                % el radio, sin la muñeca «3»
        Q(k,:) = [q1 d2 d3 0];
        T = cinematica_directa([q1 90 0 0], [l1 d2 d3 l4], [0 0 0 0], [0 90 0 0], 'deg'); «5»
        printf('%8.2f %8.2f %8.2f | %7.2f %7.2f %7.2f %d\n', P(k,:), Q(k,:)); «4»
      end
    '''),
    'ojo': ['Si el brazo sale sobre el eje y del sistema 1 (como en el RPP y el RPR de 2026), el ángulo es `atan2d(-x, y)`. Si dudás, probá y verificá con la directa.',
            'q4 (la muñeca) no mueve la punta: va 0, como dice el enunciado.',
            'Los puntos vienen redondeados a 2 decimales: la verificación da un error de milésimas, no cero.'],
    'parcial': 'El parcial 2026 (online): tablas de 3 a 5 puntos para el cilíndrico RPPR, el RPR codo arriba, el RPP y el IRB2400, más la trayectoria con código.',
    'pdf': 6,
  },
  [
    oct_ej('5.1', 'Cilíndrico', 'la tabla del cilíndrico', 'Dado el robot cilíndrico (RPPR) de la figura, con l1 = 600 mm y l4 = 200 mm, determinar q1, d2, d3 y q4 para cada punto de la tabla (q4 = 0). Armá la tabla `Q` (una fila por punto: q1, d2, d3, q4).',
      TABLA_CIL + r'''
      l1 = 600; l4 = 200;
      Q = zeros(size(P, 1), 4);
      % for k = 1:size(P, 1)
      %   ...
      % end
      Q
      ''', TABLA_CIL + r'''
      l1 = 600; l4 = 200;
      Q = zeros(size(P, 1), 4);
      for k = 1:size(P, 1)
        x = P(k,1); y = P(k,2); z = P(k,3);
        Q(k,:) = [atan2d(y, x), z - l1, hypot(x, y) - l4, 0];
      end
      Q
      ''', vars=['Q'], respuestas=[R('Fila 1: q1', 'Q(1,1)', 2, '°'), R('Fila 1: d2', 'Q(1,2)', 2, 'mm'), R('Fila 1: d3', 'Q(1,3)', 2, 'mm'),
        R('Fila 4: q1', 'Q(4,1)', 2, '°'), R('Fila 4: d2', 'Q(4,2)', 2, 'mm'), R('Fila 4: d3', 'Q(4,3)', 2, 'mm')], imagen=CIL,
      pasos=['De la directa: x = (d3 + l4)·cos q1, y = (d3 + l4)·sen q1, z = l1 + d2.', 'Despejando: q1 = atan2d(y, x), d2 = z − l1, d3 = √(x² + y²) − l4.'],
      mensajes={'Q': '`Q` no da: q1 = atan2d(y, x), d2 = z − l1, d3 = hypot(x, y) − l4 y q4 = 0'}),
    oct_ej('5.2', 'RPP', 'la tabla del RPP', 'Dado el robot RPP de 3 GDL de la figura, con l1 = 100 mm (tabla θ = q1 0 0, d = l1 d2 d3, a = 0 0 0, α = 0 −90 0), determinar q1, d2 y d3 para cada punto. El brazo (z2) sale sobre y1. Armá `Q` y verificá cada fila con la directa.',
      TABLA_RPP + r'''
      l1 = 100;
      Q = zeros(size(P, 1), 3);
      % for k = 1:size(P, 1)
      %   ...
      % end
      Q
      ''', TABLA_RPP + r'''
      l1 = 100;
      Q = zeros(size(P, 1), 3);
      for k = 1:size(P, 1)
        x = P(k,1); y = P(k,2); z = P(k,3);
        Q(k,:) = [atan2d(-x, y), z - l1, hypot(x, y)];
        T = cinematica_directa([Q(k,1) 0 0], [l1 Q(k,2) Q(k,3)], [0 0 0], [0 -90 0], 'deg');
        printf('fila %d: error %.3f mm\n', k, norm(T(1:3,4) - P(k,:)'));
      end
      Q
      ''', vars=['Q'], respuestas=[R('Fila 1: q1', 'Q(1,1)', 2, '°'), R('Fila 1: d2', 'Q(1,2)', 2, 'mm'), R('Fila 1: d3', 'Q(1,3)', 2, 'mm')], imagen=RPP,
      pasos=['d2 = z − l1 y d3 = √(x² + y²): no hay muñeca.', 'Con q1 = 0 el brazo apunta hacia +y: q1 = atan2d(−x, y).'],
      pistas=['Si usás atan2d(y, x), la directa no vuelve al punto: te da 90° de diferencia.'],
      mensajes={'Q': '`Q` no da: revisá q1 (el brazo sale sobre y1: atan2d(−x, y))'}),
    oct_ej('5.3', 'RPR codo arriba', 'la tabla del RPR (codo arriba)', 'Dado el robot RPR (codo arriba) de la figura, con l1 = 150 mm y l2 = 300 mm (tabla θ = q1 −90 q3, d = l1 d2 0, a = 0 0 l2, α = −90 −90 0), determinar q1, d2 y q3 para cada punto, en la rama codo arriba (q3 < 0). Armá `Q`.',
      TABLA_RPR + r'''
      l1 = 150; l2 = 300;
      Q = zeros(size(P, 1), 3);
      % for k = 1:size(P, 1)
      %   ...
      % end
      Q
      ''', TABLA_RPR + r'''
      l1 = 150; l2 = 300;
      Q = zeros(size(P, 1), 3);
      for k = 1:size(P, 1)
        x = P(k,1); y = P(k,2); z = P(k,3);
        q3 = -acosd((z - l1) / l2);
        d2 = hypot(x, y) + l2*sind(q3);
        q1 = atan2d(-x, y);
        Q(k,:) = [q1 d2 q3];
        T = cinematica_directa([q1 -90 q3], [l1 d2 0], [0 0 l2], [-90 -90 0], 'deg');
        printf('fila %d: error %.3f mm\n', k, norm(T(1:3,4) - P(k,:)'));
      end
      Q
      ''', vars=['Q'], respuestas=[R('Fila 3: q1', 'Q(3,1)', 2, '°'), R('Fila 3: d2', 'Q(3,2)', 2, 'mm'), R('Fila 3: q3', 'Q(3,3)', 2, '°')], imagen=RPR,
      pasos=['La altura depende solo de q3: z − l1 = l2·cos q3, entonces q3 = −acosd((z − l1)/l2) (el menos es codo arriba).', 'El brazo horizontal mide d2 menos lo que «se come» el codo: √(x² + y²) = d2 − l2·sen q3.', 'Por cómo quedó x0 en la figura, q1 = atan2d(−x, y).'],
      pistas=['Verificá cada fila con `cinematica_directa([q1 -90 q3], [l1 d2 0], [0 0 l2], [-90 -90 0], \'deg\')`.'],
      mensajes={'Q': '`Q` no da: q3 = −acosd((z − l1)/l2), d2 = hypot(x, y) + l2·sind(q3) y q1 = atan2d(−x, y)'}),
    oct_ej('5.4', 'Corregir', 'corregí la fila de un alumno', 'En el parcial 2026 un alumno cargó para el IRB2400 (ver la parte 4) el punto (−87,59; −17,50; 1221,98) mm con θ1 = 11,2986°, θ2 = −5,2124°, θ3 = −46,7959° (y d4, θ5 y θ6 en 307, 395 y 0, cuando el enunciado los fijaba en 0). Con d4, θ5 y θ6 en 0, ¿adónde lleva su respuesta? Calculá la punta `p` y la distancia al punto pedido, `err`.',
      r'''
      l1 = 770; l2 = 420; l3 = 400; l4 = 250;
      q = [11.2986 -5.2124 -46.7959 0 0 0];     % la fila del alumno (d4, q5 y q6 en 0)
      Pd = [-87.59; -17.50; 1221.98];
      % th = ...;  d = ...;  a = ...;  al = ...;   (la tabla de la parte 4)
      % T = cinematica_directa(th, d, a, al, 'deg');
      % p = ...
      % err = ...
      ''', r'''
      l1 = 770; l2 = 420; l3 = 400; l4 = 250;
      q = [11.2986 -5.2124 -46.7959 0 0 0];
      Pd = [-87.59; -17.50; 1221.98];
      th = [q(1) q(2) q(3) 0 q(5) q(6)];
      d  = [l1 0 0 l3 + q(4) 0 l4];
      a  = [0 l2 0 0 0 0];
      al = [-90 0 90 -90 90 0];
      T = cinematica_directa(th, d, a, al, 'deg');
      p = T(1:3, 4)
      err = norm(p - Pd)
      ''', vars=['p', 'err'], respuestas=[R('¿A cuántos mm del punto queda?', 'err', 1, 'mm'), OP('¿Está bien la fila?', ['Sí', 'No'], 'No', 'Queda a 14,5 mm del punto. La respuesta verificada es (−168,70; 16,19; −45,08) con d4, θ5 y θ6 en 0.')],
      pasos=['La articulación 4 es prismática: su d es l3 + d4 y su θ es 0.', '`err = norm(p - Pd)`.']),
  ]))

# ======================= 6 · Trayectorias =======================
partes.append(parte(6, 'trayectorias', 'Generación de trayectorias', 'Trayectorias',
  'Una trayectoria es una matriz con una postura por fila. `generacion_de_trayectorias` mueve todas las articulaciones juntas (manda la más lenta); para que la punta haga una recta o un círculo, se hace la inversa de cada punto, encadenando la semilla.',
  {
    'que': 'Una trayectoria es una sucesión de posturas en el tiempo: una matriz `q` donde cada **fila** es la postura completa del robot en un instante t(k).\n'
           '`generacion_de_trayectorias(qi, qf, wmax, h)` hace el movimiento **sincronizado**: todas las articulaciones arrancan y llegan juntas, cada una a velocidad constante. Si la punta tiene que hacer una recta o un círculo, primero se generan los puntos cartesianos y después se hace la inversa de cada uno.',
    'consta': [
      ['El recorrido', '`dq = qf - qi` para cada articulación.'],
      ['El tiempo total', '`T = max(abs(dq) ./ wmax)`: el de la articulación más lenta.'],
      ['Las velocidades', '`w = dq / T`: solo la que manda va a su máximo.'],
      ['Los puntos', '`n = max(2, ceil(T/h) + 1)` y `t = linspace(0, T, n)` (el paso real es ≤ h).'],
      ['Los gráficos', '`Dibujar_Temporal(t, q, Dq)`: posiciones y velocidades en el tiempo.'],
      ['Recta o círculo', 'Puntos cartesianos y `cinematica_inversa` de cada uno, con la solución anterior como semilla.'],
    ],
    'ejemplo': ejemplo('trayectoria.m', 'Ejercicio 3 del resumen: el cilíndrico de A a B', r'''
      qA = [39.806 250 290.51 0];   qB = [119.74 100 303.11 0];  % la inversa de A y de B
      wmax = [30 50 50 30];  h = 0.1;          % [°/s mm/s mm/s °/s] y [s]
      dq = qB - qA                             % (79,93; -150; 12,6; 0) «1»
      T  = max(abs(dq) ./ wmax)                % 3 s: manda d2 (150/50) «2»
      w  = dq / T                              % (26,65; -50; 4,2; 0) «3»
      n  = max(2, ceil(T/h) + 1)               % 31 puntos «4»
      [q, Dq, t] = generacion_de_trayectorias(qA, qB, wmax, h);   % lo mismo, con la función «4»
      Dibujar_Temporal(t, q, Dq); «5»
      % para una recta: Pk = PA + s(k)*(PB - PA) y cinematica_inversa(Pk, qk, ...) en un for «6»
    '''),
    'ojo': ['Que las articulaciones vayan en línea recta no quiere decir que la punta vaya en línea recta: el TCP hace una curva.',
            '`q` sale con una fila por instante: la postura k es `q(k,:)`.',
            'Al encadenar tramos, sacá el primer punto de cada tramo nuevo (es el último del anterior) y sumale el tiempo acumulado.',
            'En el navegador se ven los gráficos de `Dibujar_Temporal` y de `plot`; la animación (`animar_trayectoria`) hay que probarla en Octave.'],
    'parcial': 'Es el último ejercicio y se responde pegando el código: la trayectoria entre dos puntos, o un círculo recorrido con la inversa punto a punto, con los gráficos de q(t) y dq(t) y la animación.',
    'pdf': 7,
  },
  [
    oct_ej('6.1', 'La función', 'una trayectoria articular', 'Te dan las posturas de un RRR directamente: qi = (0°, 30°, 30°) y qf = (90°, 60°, −30°), con wmax = (30, 20, 40) °/s y h = 0,1 s. Generá la trayectoria con `generacion_de_trayectorias`, guardá el tiempo total en `T_total`, la cantidad de puntos en `N` y las velocidades en `w` (una fila de Dq), y graficá con `Dibujar_Temporal`.',
      r'''
      qi = [0 30 30];  qf = [90 60 -30];   % [deg]
      wmax = [30 20 40];  h = 0.1;
      % [q, Dq, t] = generacion_de_trayectorias( ... );
      % T_total = ...;  N = ...;  w = ...
      % Dibujar_Temporal( ... );
      ''', r'''
      qi = [0 30 30];  qf = [90 60 -30];
      wmax = [30 20 40];  h = 0.1;
      [q, Dq, t] = generacion_de_trayectorias(qi, qf, wmax, h);
      T_total = t(end)
      N = size(q, 1)
      w = Dq(1, :)
      Dibujar_Temporal(t, q, Dq);
      ''', vars=['T_total', 'N', 'w'], respuestas=[R('Tiempo total', 'T_total', 2, 's'), R('Puntos', 'N', 0), R('Velocidad de q3', 'w(3)', 2, '°/s'),
        OP('¿Qué articulación manda?', ['q1', 'q2', 'q3'], 'q1', 'q1 recorre 90° a 30 °/s: 3 s, la que más tarda (q2 y q3 tardarían 1,5 s). Es la única que va a su máximo: w = (30, 10, −20).')],
      pasos=['`T_total = t(end)` y `N = size(q, 1)`.', 'Todas las filas de Dq son iguales: `w = Dq(1, :)`.'],
      checks=[C(r'Dibujar_Temporal\s*\(', 'Grafica con Dibujar_Temporal', 'Graficá con `Dibujar_Temporal(t, q, Dq)`')]),
    oct_ej('6.2', 'A mano', 'el tiempo, los puntos y las velocidades, a mano', 'Sin la función: con qi = (10°, 0°, 50°), qf = (−50°, 40°, 20°), wmax = (25, 25, 25) °/s y h = 0,15 s, calculá el recorrido `dq`, el tiempo total `T`, las velocidades `w` y la cantidad de puntos `n`.',
      r'''
      qi = [10 0 50];  qf = [-50 40 20];
      wmax = [25 25 25];  h = 0.15;
      % dq = ...
      % T  = ...
      % w  = ...
      % n  = ...
      ''', r'''
      qi = [10 0 50];  qf = [-50 40 20];
      wmax = [25 25 25];  h = 0.15;
      dq = qf - qi
      T  = max(abs(dq) ./ wmax)
      w  = dq / T
      n  = max(2, ceil(T/h) + 1)
      ''', vars=['dq', 'T', 'w', 'n'], respuestas=[R('T', 'T', 2, 's'), R('n', 'n', 0), R('Velocidad de q2', 'w(2)', 2, '°/s')],
      pasos=['`./` divide elemento a elemento.', 'Manda la que más tarda: q1 (60/25 = 2,4 s).'],
      checks=[NO(r'generacion_de_trayectorias', 'Sin la función', 'Hacelo sin `generacion_de_trayectorias`: con las 4 fórmulas')],
      mensajes={'T': '`T` no da: max(abs(dq) ./ wmax)', 'n': '`n` no da: max(2, ceil(T/h) + 1)'}),
    oct_ej('6.3', 'De A a B', 'de un punto a otro, con la inversa', 'Con el cilíndrico del resumen, generar la trayectoria articular sincronizada que lleve el TCP de A = (300; 250; 650) mm a B = (−200; 350; 500) mm, con wmax = (30, 50, 50, 30) y h = 0,1 s. La semilla de A es (0; 100; 100; 0) y la de B, la solución de A.\n\nGuardá `qA` y `qB` (como filas), `T_total`, `N_puntos` y `velocidades`, y graficá.',
      CIL_RES + r'''
      PA = [300; 250; 650];   PB = [-200; 350; 500];
      % qA = ...   (la inversa de A, como fila)
      % qB = ...   (la inversa de B, con qA como semilla)
      wmax = [30 50 50 30];  h = 0.1;
      % [q, Dq, t] = ...
      % T_total = ...;  N_puntos = ...;  velocidades = ...
      ''', CIL_RES + r'''
      PA = [300; 250; 650];   PB = [-200; 350; 500];
      [qA, ~, ~, okA] = cinematica_inversa(PA, [0; 100; 100; 0], tipo, q_offset, d_offset, a, alpha, 'deg');
      [qB, ~, ~, okB] = cinematica_inversa(PB, qA, tipo, q_offset, d_offset, a, alpha, 'deg');
      qA = qA'
      qB = qB'
      wmax = [30 50 50 30];  h = 0.1;
      [q, Dq, t] = generacion_de_trayectorias(qA, qB, wmax, h);
      T_total = t(end)
      N_puntos = size(q, 1)
      velocidades = Dq(1, :)
      Dibujar_Temporal(t, q, Dq);
      ''', vars=['qA', 'qB', 'T_total', 'N_puntos', 'velocidades'], respuestas=[R('Tiempo total', 'T_total', 2, 's'), R('Puntos', 'N_puntos', 0), R('Velocidad de q1', 'velocidades(1)', 2, '°/s'),
        OP('¿Qué articulación manda?', ['q1', 'd2', 'd3', 'q4'], 'd2', 'd2 recorre 150 mm a 50 mm/s: 3 s, la que más tarda.')], imagen=CIL,
      pasos=['Primero la inversa de A y de B (la semilla de B es qA).', 'Pasalas como fila: `qA\'`.', 'Después `generacion_de_trayectorias(qA, qB, wmax, h)`.'],
      mensajes={'qB': '`qB` no da: usá qA como semilla de B'}),
    oct_ej('6.4', 'Recta', 'que la punta vaya en línea recta', 'Con el mismo robot, que la punta vaya de A a B **en línea recta**: 51 puntos `Pk = PA + s(k)*(PB - PA)` con `s = linspace(0, 1, 51)`, y la inversa de cada uno con la solución anterior como semilla. Guardá las posturas en `Q` (51×4) y graficá q1 contra s.',
      CIL_RES + r'''
      PA = [300; 250; 650];   PB = [-200; 350; 500];
      qk = cinematica_inversa(PA, [0; 100; 100; 0], tipo, q_offset, d_offset, a, alpha, 'deg');
      s = linspace(0, 1, 51);
      Q = zeros(numel(s), 4);
      % for k = 1:numel(s)
      %   Pk = ...
      %   qk = cinematica_inversa(Pk, qk, ...);   % la semilla es la anterior
      %   Q(k,:) = qk';
      % end
      % plot(s, Q(:,1))
      ''', CIL_RES + r'''
      PA = [300; 250; 650];   PB = [-200; 350; 500];
      qk = cinematica_inversa(PA, [0; 100; 100; 0], tipo, q_offset, d_offset, a, alpha, 'deg');
      s = linspace(0, 1, 51);
      Q = zeros(numel(s), 4);
      for k = 1:numel(s)
        Pk = PA + s(k)*(PB - PA);
        qk = cinematica_inversa(Pk, qk, tipo, q_offset, d_offset, a, alpha, 'deg');
        Q(k,:) = qk';
      end
      mitad = Q(26, :)
      plot(s, Q(:,1)); grid on; xlabel('s'); title('q1 en la recta')
      ''', vars=['Q'], respuestas=[R('q1 en la mitad (k = 26)', 'Q(26,1)', 2, '°'), R('d3 en la mitad', 'Q(26,3)', 2, 'mm')],
      pasos=['`Pk = PA + s(k)*(PB - PA)`.', 'La semilla de cada punto es la solución del anterior: así converge en 2 o 3 vueltas y no salta de rama.'],
      pistas=['En la mitad la punta está en (50; 300; 575): d2 = 175 y d3 = √(50² + 300²) − 100.'],
      checks=[C(r'\bfor\b', 'Recorre los puntos con un for', 'Recorré los 51 puntos con un `for`')]),
    oct_ej('6.5', 'Círculo', 'el círculo del parcial 2026', 'El ejercicio de trayectoria del parcial 2026: el cilíndrico RPPR con l1 = 600 mm y l4 = 200 mm tiene que recorrer un círculo de radio 150 mm en el plano XZ (y = 700 mm), de centro (0; 700; 1100), con `w = 0:15:360`. Resolver la inversa en cada punto (q_start = [90; 500; 500; 0], encadenando la semilla) y unir los tramos con `generacion_de_trayectorias` (wmax = [60 200 200 60], h = 0,05 s), sin repetir el punto de unión. Graficá con `Dibujar_Temporal`.\n\nGuardá `Q` (una fila por punto del círculo), `Qt`, `DQt` y `Tt` (la trayectoria completa).',
      r'''
      l1 = 600; l4 = 200;
      tipo = 'RPPR';  q_offset = [0; 90; 0; 0];  d_offset = [l1; 0; 0; l4];
      a = [0; 0; 0; 0];  alpha = [0; 90; 0; 0];
      % 1) el círculo
      x0 = 0; y0 = 700; z0 = 1100; R = 150;
      w = 0:15:360;
      x = x0 + R*cosd(w);  y = y0 + zeros(size(w));  z = z0 + R*sind(w);
      P = [x; y; z];
      % 2) la inversa de cada punto (semilla: la anterior)
      N = size(P, 2);
      Q = zeros(N, 4);
      q = [90; 500; 500; 0];
      % for k = 1:N ... end
      % 3) encadenar generacion_de_trayectorias
      wmax = [60 200 200 60];  h = 0.05;
      Qt = []; DQt = []; Tt = [];
      % for k = 1:N-1 ... end
      % 4) Dibujar_Temporal(Tt, Qt, DQt);
      ''', r'''
      l1 = 600; l4 = 200;
      tipo = 'RPPR';  q_offset = [0; 90; 0; 0];  d_offset = [l1; 0; 0; l4];
      a = [0; 0; 0; 0];  alpha = [0; 90; 0; 0];
      x0 = 0; y0 = 700; z0 = 1100; R = 150;
      w = 0:15:360;
      x = x0 + R*cosd(w);  y = y0 + zeros(size(w));  z = z0 + R*sind(w);
      P = [x; y; z];
      N = size(P, 2);
      Q = zeros(N, 4);
      q = [90; 500; 500; 0];
      for k = 1:N
        [q, ~, ~, ok] = cinematica_inversa(P(:,k), q, tipo, q_offset, d_offset, a, alpha, 'deg');
        if ~ok, warning('No convergio en el punto %d', k); end
        Q(k,:) = q';
      end
      wmax = [60 200 200 60];  h = 0.05;
      Qt = []; DQt = []; Tt = [];
      for k = 1:N-1
        [qk, dqk, tk] = generacion_de_trayectorias(Q(k,:), Q(k+1,:), wmax, h);
        if k > 1
          qk = qk(2:end,:); dqk = dqk(2:end,:); tk = tk(2:end);
        end
        t0 = 0; if ~isempty(Tt), t0 = Tt(end); end
        Qt = [Qt; qk]; DQt = [DQt; dqk]; Tt = [Tt; t0 + tk];
      end
      printf('Puntos del circulo: %d | muestras: %d | tiempo total: %.2f s\n', N, size(Qt,1), Tt(end));
      Dibujar_Temporal(Tt, Qt, DQt);
      ''', vars=['Q', 'Qt', 'Tt'], respuestas=[R('Puntos del círculo', 'N', 0), R('Muestras de la trayectoria', 'size(Qt,1)', 0), R('Tiempo total', 'Tt(end)', 2, 's'), R('d3 en el primer punto', 'Q(1,3)', 2, 'mm')],
      pasos=['En el for de la inversa, la semilla es la `q` de la vuelta anterior.', 'En cada tramo k > 1, sacá la primera fila (es la última del tramo anterior).', 'Al tiempo de cada tramo sumale el último tiempo acumulado: `t0 = Tt(end)`.'],
      pistas=['El primer punto es (150; 700; 1100): q = (77,91°; 500; 515,89; 0).', 'Son 25 puntos y 24 tramos.'],
      checks=[C(r'generacion_de_trayectorias\s*\(', 'Usa generacion_de_trayectorias', 'Uní los tramos con `generacion_de_trayectorias`'), C(r'Dibujar_Temporal\s*\(', 'Grafica con Dibujar_Temporal', 'Graficá con `Dibujar_Temporal`')],
      mensajes={'Qt': '`Qt` no da: ¿sacaste el punto repetido de cada tramo nuevo (k > 1)?', 'Tt': '`Tt` no da: a cada tramo sumale el último tiempo acumulado'}),
  ]))

guardar(os.path.join(RAIZ, 'practica', 'tpa-p2', 'ejercicios.json'), 'Robótica · 2º parcial', partes)
