# Arma practica/tpa-p1/ejercicios.json: la Práctica del 1º parcial de TPA (robótica), por partes y con su explicación.
# Necesita octave-cli: los valores esperados salen de correr cada solución con las funciones del profe.
# Desde la raíz:  python3 herramientas/tpa-practica/armar_p1.py  y después  node herramientas/tpa-practica/validar.js
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import *

IMG = 'practica/tpa-p1/img/'
def figura(nombre, alt, pie=None):
    x = {'url': IMG + nombre, 'alt': alt}
    if pie: x['pie'] = pie
    return x
r3 = lambda v='r': [{'pregunta': f'{v}x', 'expr': f'{v}(1)'}, {'pregunta': f'{v}y', 'expr': f'{v}(2)'}, {'pregunta': f'{v}z', 'expr': f'{v}(3)'}]
p3 = lambda v='p': [{'pregunta': 'px', 'expr': f'{v}(1)'}, {'pregunta': 'py', 'expr': f'{v}(2)'}, {'pregunta': 'pz', 'expr': f'{v}(3)'}]

partes = []

# ======================= 1 · Robots =======================
partes.append(parte(1, 'robots', 'Robots: partes, grados de libertad y tipos', 'Robots',
  'Un robot es una cadena de **eslabones** unidos por **articulaciones** (R: giran; P: se deslizan). Cada articulación suma un **grado de libertad**, y el tipo de robot sale de qué articulaciones tiene y cómo están puestas.',
  {
    'que': 'Un robot manipulador es una cadena de piezas rígidas (**eslabones**) unidas por **articulaciones**. Arranca en la **base**, que está fija, y termina en el **efector final**: la pinza, el soldador, la ventosa… lo que actúa con el medio.\n'
           'Cada articulación es **rotativa** (R: gira un ángulo) o **prismática** (P: se desliza una distancia), y cada una suma un **grado de libertad** (GDL). Según qué articulaciones tenga y cómo estén puestas, el robot tiene un nombre: cartesiano, cilíndrico, esférico, SCARA, antropomórfico.',
    'consta': [
      ['Base y eslabones', 'La base es fija; los eslabones son las piezas rígidas entre una articulación y la siguiente.'],
      ['Articulaciones R y P', 'R gira (su variable es un ángulo q); P se desliza (su variable es una distancia d).'],
      ['Grados de libertad', 'Uno por articulación: un robot RPPR tiene 4. Para ubicar y orientar algo en el espacio hacen falta 6.'],
      ['Efector final', 'La herramienta del extremo: lo que actúa con el medio.'],
      ['El tipo de robot', 'Sale de la secuencia de articulaciones: PPP cartesiano, RPP cilíndrico, RRP esférico o SCARA, RRR antropomórfico.'],
    ],
    'ejemplo': ejemplo('robot.m', 'El robot cilíndrico del 1º y del 2º parcial', '''
      % El robot cilíndrico (libro de Barrientos): el de los dos parciales de robótica
      base = 'columna fija en el piso';          «1»
      tipo = 'RPPR';     % gira, sube, estira y gira la muñeca «2»
      gdl  = length(tipo)        % 4 grados de libertad «3»
      q    = [30 200 150 0];     % un valor por articulación: ° o mm «3»
      efector = 'pinza en la punta del brazo';    «4»
      nombre  = 'cilíndrico';    % R P P: gira en la base, sube y estira «5»
    '''),
    'ojo': ['La **articulación** es la unión; el **eslabón**, la pieza rígida. Y el efector final no es la última articulación: es la herramienta.',
            'SCARA y esférico son los dos RRP. En el SCARA los dos giros tienen ejes verticales y paralelos (trabaja sobre una mesa y baja con la P); el esférico gira la base, inclina el brazo y lo estira.',
            'El delta es un robot **paralelo** (tres brazos unidos a una plataforma), no una cadena.'],
    'parcial': 'Con Pailos salía de opción múltiple («el efector final es…», «el robot de la figura se llama…»). Con Pedroni te dan la figura del robot para armar la tabla de Denavit–Hartenberg: primero hay que reconocer cada articulación.',
    'pdf': 2,
  },
  [
    elegir_ej('1.1', 'Partes', 'cada parte, con su nombre', 'Indicá qué es cada cosa.', ['Base', 'Eslabón', 'Articulación', 'Efector final', 'Grados de libertad'], [
      ('La pinza, el soldador o la ventosa: lo que actúa con el medio', 'Efector final', 'Es la herramienta del extremo del robot.'),
      ('Une dos piezas y deja que se muevan una respecto de la otra', 'Articulación', 'Puede ser rotativa (R) o prismática (P).'),
      ('Cada pieza rígida del brazo', 'Eslabón', 'Entre una articulación y la siguiente.'),
      ('La parte fija, apoyada en el piso o en una mesa', 'Base', 'Ahí va el sistema de referencia 0XYZ.'),
      ('La cantidad de movimientos independientes que puede hacer el robot', 'Grados de libertad', 'Uno por articulación.'),
      ('Lo que en un robot RPPR vale 4', 'Grados de libertad', 'Cuatro articulaciones, cuatro grados de libertad.'),
    ], pregunta='¿Qué es cada cosa?'),
    elegir_ej('1.2', 'Tipos', '¿qué robot es?', 'Cada descripción corresponde a un tipo de robot. Elegí el nombre.', ['Cartesiano', 'Cilíndrico', 'Esférico', 'SCARA', 'Antropomórfico', 'Delta'], [
      ('Tres guías perpendiculares: se mueve en x, en y y en z (P P P)', 'Cartesiano', 'También se llama pórtico. Su espacio de trabajo es un prisma.'),
      ('Gira en la base, sube por una columna y estira el brazo (R P P)', 'Cilíndrico', 'Su espacio de trabajo es un cilindro hueco.'),
      ('Gira en la base, inclina el brazo y lo estira (R R P): su espacio de trabajo es una esfera', 'Esférico', 'También se llama polar.'),
      ('Dos giros con ejes verticales paralelos y una bajada (R R P): trabaja sobre una mesa', 'SCARA', 'Rígido en vertical y flexible en el plano: ideal para armar piezas.'),
      ('Tres giros, como un brazo humano: hombro, codo y muñeca (R R R)', 'Antropomórfico', 'También se llama articulado.'),
      ('Tres brazos unidos a una plataforma: muy rápido para tomar y dejar piezas', 'Delta', 'Es un robot paralelo.'),
    ], pregunta='¿Qué robot es?'),
    resp_ej('1.3', 'Tipos', 'el robot de la figura', 'Como en el parcial de Pailos: ¿cómo se llama el robot de cada figura?', [
      {'pregunta': 'Figura 1', 'opciones': ['Cartesiano', 'Cilíndrico', 'Esférico', 'SCARA', 'Antropomórfico', 'Delta'], 'valor': 'Cartesiano', 'motivo': 'Tres prismáticas perpendiculares (x, y, z).'},
      {'pregunta': 'Figura 2', 'opciones': ['Cartesiano', 'Cilíndrico', 'Esférico', 'SCARA', 'Antropomórfico', 'Delta'], 'valor': 'Esférico', 'motivo': 'Dos rotaciones (θ y β) y una prismática: el espacio de trabajo es una esfera.'},
      {'pregunta': 'Figura 3', 'opciones': ['Cartesiano', 'Cilíndrico', 'Esférico', 'SCARA', 'Antropomórfico', 'Delta'], 'valor': 'Delta', 'motivo': 'Robot paralelo de tres brazos.'},
    ], imagen=figura('tipos-de-robots.png', 'Tres robots: uno con tres guías perpendiculares, uno que gira y se estira dentro de una esfera, y uno con tres brazos colgando de una plataforma', 'Figuras del cuestionario de Pailos (2023–2024)')),
    resp_ej('1.4', 'Grados de libertad', 'contá los grados de libertad', 'Son los cuatro robots de Denavit–Hartenberg de los parciales. ¿Cuántos grados de libertad tiene cada uno? Contá las articulaciones (las variables: q o θ si gira, d si se desliza).', [
      {'pregunta': 'Robot A', 'valor': 3, 'tol': 0, 'motivo': 'RPR: q1, d y q2.'},
      {'pregunta': 'Robot B (cilíndrico)', 'valor': 4, 'tol': 0, 'motivo': 'θ1, d2, d3 y θ4.'},
      {'pregunta': 'Robot C', 'valor': 5, 'tol': 0, 'motivo': 'q1, q2, d3, q4 y q5.'},
      {'pregunta': 'Robot D', 'valor': 6, 'tol': 0, 'motivo': 'θ1, θ2, θ3, d4, θ5 y θ6.'},
      {'pregunta': '¿Cuántas prismáticas tiene el B?', 'valor': 2, 'tol': 0, 'motivo': 'd2 (sube) y d3 (estira).'},
    ], imagen=figura('cuatro-robots.png', 'Cuatro robots con sus sistemas de ejes: A un RPR, B el cilíndrico, C uno de 5 articulaciones y D uno de 6', 'Las figuras de los parciales 2023–2026')),
    elegir_ej('1.5', 'Teoría', 'verdadero o falso', 'Las preguntas de teoría que tomaba Pailos, en verdadero o falso.', ['Verdadero', 'Falso'], [
      ('Denavit–Hartenberg sirve para la cinemática **directa** de robots con articulaciones rotativas y/o prismáticas', 'Verdadero', 'Da la matriz T completa: posición y orientación del efector.'),
      ('La cinemática directa da los valores de las articulaciones para llegar a un punto', 'Falso', 'Esa es la inversa. La directa va de las articulaciones a la posición y orientación del efector.'),
      ('La cinemática inversa parte de dónde tiene que estar el efector y calcula las articulaciones', 'Verdadero', 'Posición deseada → valores de las articulaciones.'),
      ('Los reductores hacen que la articulación gire más lento (y con más fuerza) que el motor', 'Verdadero', 'El motor gira rápido y con poco torque; el reductor baja la velocidad y sube el torque.'),
      ('La regla de la mano derecha sirve para ubicar los ejes X, Y, Z (y el sentido positivo de los giros)', 'Verdadero', 'Da el sentido del tercer eje.'),
      ('Un robot delta es un brazo en serie con tres articulaciones rotativas', 'Falso', 'Es un robot paralelo: tres brazos unidos a una misma plataforma.'),
      ('El efector final es la articulación rotativa más cercana a la herramienta', 'Falso', 'Es la herramienta misma: la parte que actúa con el medio.'),
    ], pregunta='¿Verdadero o falso?'),
  ]))

# ======================= 2 · Rotaciones =======================
partes.append(parte(2, 'rotaciones', 'Matrices de rotación', 'Rotaciones',
  'Un giro alrededor de un eje se escribe con una matriz: `Rotx`, `Roty` o `Rotz` (en grados). Multiplicar un punto por la matriz lo gira, y las columnas son los ejes del sistema girado.',
  {
    'que': 'Girar un sistema (o un punto) un ángulo alrededor de un eje se escribe con una **matriz de rotación**. Las funciones del profe devuelven la versión 4×4 (homogénea) y reciben el ángulo en **grados**: `Rotx(a)`, `Roty(a)`, `Rotz(a)`.\n'
           'Para girar un punto se lo multiplica por la matriz, como columna y con un 1 al final: `q = Rotz(90) * [x; y; z; 1]`. Y cada columna de la matriz dice hacia dónde apunta un eje del sistema girado, visto desde el fijo.',
    'consta': [
      ['El eje que no cambia', 'El eje alrededor del que se gira no se mueve: su fila y su columna tienen un 1 y ceros.'],
      ['Coseno y seno en grados', '`cosd` y `sind` trabajan en grados; `cos` y `sin`, en radianes.'],
      ['El lugar del −sen', 'En Rotx y Rotz el −sen va arriba a la derecha; en Roty, abajo a la izquierda.'],
      ['Las columnas son los ejes girados', 'La columna 1 es hacia dónde apunta x′; la 2, y′; la 3, z′.'],
      ['Girar un punto', 'La matriz por el punto como columna, con un 1 al final.'],
    ],
    'ejemplo': ejemplo('Rotz.m', 'La función del profe y cómo se usa', '''
      function T = Rotz(a)          % a en grados
        ca = cosd(a);               «2»
        sa = sind(a);               «2»
        T = [ ca -sa  0  0;         «3»
              sa  ca  0  0;         «3»
               0   0  1  0;         «1»
               0   0  0  1];        «1»
      end

      R = Rotz(90);
      xprima = R(1:3, 1)            % x' apunta hacia y: (0, 1, 0) «4»
      q = R * [2; 0; 0; 1]          % el punto (2, 0, 0) girado: (0, 2, 0) «5»
    '''),
    'ojo': ['`cos(90)` no es 0: es el coseno de 90 **radianes**. Con grados, `cosd(90)`.',
            'Sin el 1 del final, `Rotz(90) * [2; 0; 0]` da un error de dimensiones (una 4×4 por una 3×1).',
            'Roty tiene el seno al revés que las otras dos: `[c 0 s; 0 1 0; -s 0 c]`.'],
    'parcial': 'Con Pailos te mostraban una matriz y había que decir de qué eje era. Con Pedroni las rotaciones están adentro de los ejercicios de composición (la parte 4).',
    'pdf': 2, 'herramienta': 'rotaciones',
  },
  [
    oct_ej('2.1', 'Rotz', 'tu propia Rotz', 'Escribí la función `Rotz(a)`: la matriz homogénea 4×4 de un giro de `a` grados alrededor de Z. Después calculá `R30 = Rotz(30)` y `R90 = Rotz(90)`.\n\nEn este ejercicio la función del profe no está: la escribís vos.',
      '''
      function T = Rotz(a)
        % completá: la matriz 4x4 de un giro de a grados alrededor de Z

      end

      R30 = Rotz(30)
      R90 = Rotz(90)
      ''', '''
      function T = Rotz(a)
        ca = cosd(a);
        sa = sind(a);
        T = [ ca -sa 0 0;
              sa  ca 0 0;
               0   0 1 0;
               0   0 0 1];
      end

      R30 = Rotz(30)
      R90 = Rotz(90)
      ''', vars=['R30', 'R90'], ocultar=['Rotz'],
      pasos=['Calculá `ca = cosd(a)` y `sa = sind(a)`.', 'Armá la matriz con `[ ]`: filas separadas por `;`.', 'El eje Z no cambia: tercera fila y tercera columna `0 0 1 0`.', 'La última fila es `0 0 0 1`.'],
      pistas=['La fila 1 es `ca -sa 0 0`.', 'Con `cos` en vez de `cosd`, Rotz(90) no da 0 donde tiene que dar.'],
      checks=[C(r'cosd\s*\(', 'Usa cosd (el ángulo viene en grados)', 'Usá `cosd` y `sind`: el ángulo viene en grados')],
      mensajes={'R30': '`R30` no da: revisá el lugar del −sen (arriba a la derecha) y que uses cosd y sind', 'R90': '`R90` no da: con 90° tiene que dar ceros y unos'}),
    oct_ej('2.2', 'Girar un punto', 'girar un punto', 'El punto p = (3, 1, 2) se gira 90° alrededor de Z. ¿Dónde queda? Guardá el punto girado (con el 1 del final) en `q`.',
      '''
      p = [3; 1; 2; 1];   % el 1 del final es para multiplicar por una 4x4
      % q = ...           % el punto girado 90° alrededor de Z
      ''', '''
      p = [3; 1; 2; 1];
      q = Rotz(90) * p
      ''', vars=['q'], respuestas=r3('q'),
      pasos=['Multiplicá la matriz por el punto: `q = Rotz(90) * p`.'],
      pistas=['Girar 90° alrededor de Z lleva x a y, e y a −x: (3, 1) pasa a (−1, 3).', 'La z no cambia.']),
    elegir_ej('2.3', 'Reconocer', '¿qué matriz es?', 'Mirá dónde están el 1 y los ceros, y dónde está el −sen. (`b` es un ángulo cualquiera.)', ['Rotación en X', 'Rotación en Y', 'Rotación en Z', 'Traslación'], [
      ('[1 0 0 0; 0 cos(b) -sin(b) 0; 0 sin(b) cos(b) 0; 0 0 0 1]', 'Rotación en X', 'La fila y la columna de X tienen el 1.'),
      ('[cos(b) 0 sin(b) 0; 0 1 0 0; -sin(b) 0 cos(b) 0; 0 0 0 1]', 'Rotación en Y', 'El 1 en el lugar de Y, y el −sen abajo a la izquierda (salió en el multiple choice de Pailos).'),
      ('[cos(b) -sin(b) 0 0; sin(b) cos(b) 0 0; 0 0 1 0; 0 0 0 1]', 'Rotación en Z', 'El 1 en el lugar de Z.'),
      ('[1 0 0 4; 0 1 0 0; 0 0 1 -2; 0 0 0 1]', 'Traslación', 'La parte 3×3 es la identidad: no gira. La columna 4 es la traslación (4, 0, −2).'),
      ('[0 -1 0 0; 1 0 0 0; 0 0 1 0; 0 0 0 1]', 'Rotación en Z', 'Es Rotz(90): cos 90 = 0 y sen 90 = 1.'),
      ('[1 0 0 0; 0 0 -1 0; 0 1 0 0; 0 0 0 1]', 'Rotación en X', 'Es Rotx(90).'),
    ], pregunta='¿Qué representa cada matriz?', tipo='clasificacion'),
    oct_ej('2.4', 'Los ejes girados', 'el versor j′ del robot 2R', 'En el robot de la figura, con q1 = π/6 y q2 = π/7, el extremo queda girado q1 + q2 alrededor de Z. ¿Cuáles son las componentes del versor j′ (el eje y del extremo) respecto de i, j, k?\n\nGuardá la rotación en `R` y el versor en `jp` (una columna de 3).',
      '''
      q1 = pi/6;  q2 = pi/7;   % en radianes
      % R  = ...   el giro total alrededor de Z (Rotz recibe grados)
      % jp = ...   la columna de y'
      ''', '''
      q1 = pi/6;  q2 = pi/7;
      R  = Rotz(rad2deg(q1 + q2));
      jp = R(1:3, 2)
      ''', vars=['jp'], respuestas=[{'pregunta': 'i', 'expr': 'jp(1)'}, {'pregunta': 'j', 'expr': 'jp(2)'}, {'pregunta': 'k', 'expr': 'jp(3)'}],
      imagen=figura('robot-2r.png', 'Robot plano de dos eslabones L1 y L2, con el sistema del extremo x2, y2 girado', 'Pregunta de Pailos (2024)'),
      pasos=['El giro total es `q1 + q2` (en radianes); `Rotz` recibe grados: `rad2deg`.', 'El versor j′ es la columna 2 de la rotación: `R(1:3, 2)`.'],
      pistas=['Las longitudes de los eslabones no importan para la orientación.', 'Tiene que dar (−sen 55,7°; cos 55,7°; 0).'],
      mensajes={'jp': '`jp` no da: es la segunda columna de Rotz(q1 + q2) en grados'}),
    oct_ej('2.5', 'Propiedades', 'la inversa es la traspuesta', 'Con `R = Roty(35) * Rotx(-50)`, tomá la parte de rotación `R3 = R(1:3,1:3)` y comprobá dos propiedades de toda matriz de rotación: `E = R3\' * R3` tiene que dar la identidad, y `d = det(R3)` tiene que dar 1.',
      '''
      R  = Roty(35) * Rotx(-50);
      % R3 = ...   la parte 3x3
      % E  = ...   la traspuesta por R3
      % d  = ...   el determinante
      ''', '''
      R  = Roty(35) * Rotx(-50);
      R3 = R(1:3, 1:3);
      E  = R3' * R3
      d  = det(R3)
      ''', vars=['E', 'd'], respuestas=[{'pregunta': '¿Cuánto da el determinante?', 'expr': 'd'}],
      pasos=['`R3 = R(1:3, 1:3)`.', 'La traspuesta es `R3\'`.', '`det(R3)`.'],
      pistas=['Como la traspuesta es la inversa, `R3\' * R3` da la identidad (con algún 0.0000 por redondeo).']),
  ]))

# ======================= 3 · Homogéneas =======================
partes.append(parte(3, 'homogeneas', 'Traslaciones y matrices homogéneas', 'Homogéneas',
  'Una matriz 4×4 junta una rotación y una traslación: `T = [R p; 0 0 0 1]`. La columna 4 es dónde está el origen; las tres primeras, hacia dónde apuntan los ejes. Y el orden en que se multiplican importa.',
  {
    'que': 'Para hacer giros y traslaciones con una sola multiplicación se usa la **matriz homogénea** 4×4:\n`T = [R p; 0 0 0 1]`\n'
           'R (3×3) es la orientación del sistema y p (3×1), la posición de su origen, vistos desde el sistema de referencia. `Traslacion([x y z])` del profe es una homogénea sin giro. Para llevar un punto se multiplica: `T * [x; y; z; 1]`.',
    'consta': [
      ['La rotación', '`T(1:3, 1:3)`: hacia dónde apuntan los ejes del sistema.'],
      ['La posición', '`T(1:3, 4)`: dónde está el origen del sistema.'],
      ['La última fila', 'Siempre `0 0 0 1`.'],
      ['Traslacion del profe', 'Recibe **un** vector: `Traslacion([x y z])`.'],
      ['El orden importa', 'Girar y después trasladar no da lo mismo que trasladar y después girar.'],
    ],
    'ejemplo': ejemplo('homogenea.m', 'Rotar y trasladar', '''
      R = Rotz(90);                   % la orientación «1»
      P = Traslacion([4 2 0]);        % la traslación: un vector entre corchetes «4»
      T = P * R                       % gira y después traslada «5»
      orientacion = T(1:3, 1:3)       % los ejes del sistema «1»
      origen = T(1:3, 4)              % (4, 2, 0): dónde quedó el origen «2»
      ultima = T(4, :)                % siempre 0 0 0 1 «3»
      T2 = R * P;                     % al revés: «5»
      otro = T2(1:3, 4)               % el origen queda en (-2, 4, 0) «5»
    '''),
    'ojo': ['`Traslacion(1, 2, 3)` con tres números sueltos no anda: va un vector, `Traslacion([1 2 3])`.',
            'El punto va como columna y con un 1 al final: si ponés 0, la traslación no se aplica.',
            'La posición de un sistema es la **columna** 4 (`T(1:3,4)`), no la fila 4.'],
    'parcial': 'Es la base de los ejercicios de rotaciones y traslaciones: la respuesta se lee en las tres primeras filas de `T * [r; 1]`.',
    'pdf': 3, 'herramienta': 'rotaciones',
  },
  [
    oct_ej('3.1', 'Armar T', 'armá la homogénea a mano', 'Un sistema está girado 90° alrededor de Z y su origen está en (1, 2, 3). Armá su matriz homogénea `T` a mano, con `[ ]` y los números (cos 90° = 0, sen 90° = 1). Después compará con `T2 = Traslacion([1 2 3]) * Rotz(90)`: tienen que dar igual.',
      '''
      % T  = [ ... ]                         % a mano, fila por fila
      % T2 = Traslacion([1 2 3]) * Rotz(90)  % con las funciones del profe
      ''', '''
      T  = [0 -1 0 1;
            1  0 0 2;
            0  0 1 3;
            0  0 0 1]
      T2 = Traslacion([1 2 3]) * Rotz(90)
      ''', vars=['T', 'T2'],
      pasos=['Las tres primeras columnas son Rotz(90): `[0 -1 0; 1 0 0; 0 0 1]`.', 'La columna 4 es el origen: `1; 2; 3`.', 'La última fila: `0 0 0 1`.'],
      checks=[C(r'\bT\s*=\s*\[', 'Arma T con [ ]', 'Armá `T` a mano, con corchetes y los números')],
      mensajes={'T': '`T` no da: la rotación va en las 3 primeras columnas y el origen en la cuarta'}),
    resp_ej('3.2', 'Leer T', 'leé una homogénea', 'Esta es la matriz de un sistema visto desde el de referencia. Sin hacer cuentas: ¿dónde está su origen, y hacia dónde apunta su eje z′?', [
      {'pregunta': 'Origen: x', 'expr': 'T(1,4)'}, {'pregunta': 'Origen: y', 'expr': 'T(2,4)'}, {'pregunta': 'Origen: z', 'expr': 'T(3,4)'},
      {'pregunta': 'z′: componente x', 'expr': 'T(1,3)'}, {'pregunta': 'z′: componente y', 'expr': 'T(2,3)'}, {'pregunta': 'z′: componente z', 'expr': 'T(3,3)'},
    ], calc='''
      T = Traslacion([12 -3 5]) * Rotx(90) * Rotz(30)
    ''', codigo={'nombre': 'T.txt', 'texto': '@salida'}, pistas=['El origen es la columna 4.', 'z′ es la columna 3.']),
    oct_ej('3.3', 'Trasladar y girar', 'trasladar y después girar un punto', 'Al punto p = (3, 3, 3) se le aplica primero una traslación de −4 según el eje X y después una rotación de π alrededor del eje X (las dos respecto del sistema fijo). Guardá el punto trasladado en `p1` y el final en `p2` (con el 1 al final).',
      '''
      p = [3; 3; 3; 1];
      % p1 = ...   trasladado -4 en X
      % p2 = ...   y después girado 180° alrededor de X
      ''', '''
      p  = [3; 3; 3; 1];
      p1 = Traslacion([-4 0 0]) * p
      p2 = Rotx(180) * p1
      ''', vars=['p1', 'p2'], respuestas=r3('p2'),
      pasos=['`p1 = Traslacion([-4 0 0]) * p`.', '`p2 = Rotx(180) * p1` (π radianes son 180°).'],
      pistas=['Girar 180° alrededor de X cambia el signo de y y de z.'],
      datos='Ojo: en el multiple choice de Pailos el campus daba como correcta (−1, −3, 3): tenía un error. La cuenta da (−1, −3, −3).'),
    oct_ej('3.4', 'El orden', 'el orden importa', 'Con el punto r = (1, 0, 0): calculá `a = Traslacion([2 0 0]) * Rotz(90) * r` (gira y después traslada) y `b = Rotz(90) * Traslacion([2 0 0]) * r` (traslada y después gira). ¿Dan lo mismo?',
      '''
      r = [1; 0; 0; 1];
      % a = ...   gira y después traslada
      % b = ...   traslada y después gira
      ''', '''
      r = [1; 0; 0; 1];
      a = Traslacion([2 0 0]) * Rotz(90) * r
      b = Rotz(90) * Traslacion([2 0 0]) * r
      ''', vars=['a', 'b'], respuestas=[{'pregunta': '¿Dan lo mismo?', 'opciones': ['Sí', 'No'], 'valor': 'No', 'motivo': 'a = (2, 1, 0) y b = (0, 3, 0): el producto de matrices no conmuta.'}],
      pistas=['La transformación que está más cerca del punto (a la derecha) es la que se hace primero.']),
  ]))

# ======================= 4 · Composición =======================
partes.append(parte(4, 'composicion', 'Composición: respecto del fijo o del móvil', 'Composición',
  'Si cada movimiento es respecto del sistema **fijo** (0XYZ), se **premultiplica**: el último queda a la izquierda. Si es respecto del sistema **móvil** (OUVW), se **posmultiplica**: se escribe en el orden en que se hace.',
  {
    'que': 'Cuando un sistema se mueve varias veces, la matriz total es el producto de cada movimiento, y el orden depende de **respecto de qué** se mueve:\n'
           '- Respecto del sistema **fijo** 0XYZ se **premultiplica**: cada movimiento nuevo va a la izquierda. «Gira R1, traslada p1, gira R2, traslada p2» → `T = Tras(p2)·R2·Tras(p1)·R1`.\n'
           '- Respecto del sistema **móvil** OUVW (sus propios ejes) se **posmultiplica**: se escribe en el mismo orden en que se hace.\n'
           'Con la matriz total, el punto: `r = T * [ruvw; 1]`.',
    'consta': [
      ['Respecto de qué', '«con respecto al sistema 0XYZ», «alrededor del eje 0X» → fijo. «alrededor de su eje OW» → móvil.'],
      ['Fijo: premultiplicar', 'La primera transformación queda pegada al vector (a la derecha); la última, a la izquierda.'],
      ['Móvil: posmultiplicar', 'Se escribe en el orden del enunciado.'],
      ['El punto con su 1', '`r = T * [ruvw; 1]`; la respuesta son las tres primeras filas.'],
      ['Controlar con la intuición', 'Un giro alrededor de X no cambia la x; uno alrededor de Z no cambia la z.'],
    ],
    'ejemplo': ejemplo('composicion.m', '1º parcial 2026 (pregunta 2 del banco)', '''
      % Girado 136° alrededor de 0X, trasladado p1 = (-9,-9,-8), girado 97°
      % alrededor de 0Y y trasladado p2 = (-2,-5,-7), respecto del sistema 0XYZ «1»
      ruvw = [0; -6; -5];
      T = Traslacion([-2 -5 -7]) * Roty(97) * ...   % lo último, a la izquierda «2»
          Traslacion([-9 -9 -8]) * Rotx(136);       % lo primero, pegado al vector «2»
      r = T * [ruvw; 1]                % (-9,4105; -6,2107; 2,9775) «4»
      % Si los movimientos fueran respecto del sistema móvil:
      Tm = Rotx(136) * Traslacion([-9 -9 -8]) * Roty(97) * Traslacion([-2 -5 -7]); «3»
      % Control: si el último giro fuera alrededor de Z, la z no cambiaría «5»
    '''),
    'ojo': ['El error que más puntos hace perder: escribir la composición en el orden del enunciado cuando es respecto del fijo. En 2024 un alumno multiplicó al revés y el profe le puso «Se deben premultiplicar».',
            '«Primero trasladado y después girado» es `R * T`, no `T * R` (corrección textual del profe en el recuperatorio 2024).',
            'El vector va con el 1: `[ruvw; 1]`, y la respuesta son las tres primeras filas.'],
    'parcial': 'Son los dos primeros ejercicios del parcial de Pedroni: te dan los giros y traslaciones respecto de 0XYZ y un vector ruvw; hay que dar (rx, ry, rz) con 4 decimales y pegar el código. Los números cambian de alumno a alumno, pero el enunciado se repite.',
    'pdf': 5, 'herramienta': 'rotaciones',
  },
  [
    oct_ej('4.1', 'Fijo', 'gira, traslada, gira y traslada', 'Un sistema OUVW ha sido girado 25° alrededor del eje 0X, y posteriormente trasladado un vector p1 = (3, −2, 1), y luego ha sido girado −60° alrededor del eje 0Y y trasladado un vector p2 = (1, 4, −2) con respecto al sistema 0XYZ. Calcular las coordenadas (rx, ry, rz) del vector r con coordenadas ruvw = (2, −1, 3).\n\nGuardá la matriz total en `T` y el resultado en `r`.',
      '''
      ruvw = [2; -1; 3];
      % T = ...   respecto del fijo: lo último a la izquierda
      % r = ...
      ''', '''
      ruvw = [2; -1; 3];
      T = Traslacion([1 4 -2]) * Roty(-60) * Traslacion([3 -2 1]) * Rotx(25);
      r = T * [ruvw; 1]
      ''', vars=['T'], respuestas=r3(), mensajes={'T': '`T` no da: respecto del fijo se premultiplica (lo último va a la izquierda)'},
      pasos=['La secuencia es Rx(25) → T(p1) → Ry(−60) → T(p2).', 'Respecto del fijo se escribe al revés: `Traslacion(p2) * Roty(-60) * Traslacion(p1) * Rotx(25)`.', '`r = T * [ruvw; 1]`.'],
      pistas=['La primera transformación queda pegada al vector.', 'Se puede controlar sin matrices 4×4: `r = p2 + Ry*(Rx*ruvw + p1)`.']),
    oct_ej('4.2', 'Fijo', 'tres giros respecto del fijo', 'Un sistema OUVW ha sido girado 20° alrededor del eje 0Y, luego ha sido girado −35° alrededor del eje 0X, y finalmente ha sido girado 110° alrededor del eje 0Z. Calcular las coordenadas (rx, ry, rz) del vector r con coordenadas ruvw = (−4, 7, 5).\n\nGuardá la matriz en `T` y el resultado en `r`.',
      '''
      ruvw = [-4; 7; 5];
      % T = ...
      % r = ...
      ''', '''
      ruvw = [-4; 7; 5];
      T = Rotz(110) * Rotx(-35) * Roty(20);
      r = T * [ruvw; 1]
      ''', vars=['T'], respuestas=r3(), mensajes={'T': '`T` no da: el orden de los giros es Y, X, Z y respecto del fijo se escribe al revés'},
      pasos=['Orden de los giros: Y, X, Z.', 'Respecto del fijo: `Rotz(110) * Rotx(-35) * Roty(20)`.'],
      pistas=['Es el ejercicio 1 del parcial 2026 con otros números.']),
    oct_ej('4.3', 'La trampa del orden', 'primero traslada y después gira', 'Un sistema OUVW ha sido trasladado un vector p = (2, −4, 1) con respecto al sistema 0XYZ, y posteriormente girado 30° alrededor del eje 0Z. Calcular las coordenadas (rx, ry, rz) del vector r con coordenadas ruvw = (1, 3, −2).',
      '''
      ruvw = [1; 3; -2];
      % T = ...   ojo: primero traslada
      % r = ...
      ''', '''
      ruvw = [1; 3; -2];
      T = Rotz(30) * Traslacion([2 -4 1]);
      r = T * [ruvw; 1]
      ''', vars=['T'], respuestas=r3(), mensajes={'T': '`T` no da: primero se traslada y después se gira, así que es R * T'},
      pasos=['Primero se traslada: la traslación va pegada al vector.', '`T = Rotz(30) * Traslacion([2 -4 1])`.'],
      pistas=['Es la corrección textual del profe en el recuperatorio 2024: «primero se traslada el sistema y luego se lo rota. La composición de matrices es R * T».', 'El giro es alrededor de Z: la z no cambia (−2 + 1 = −1).']),
    oct_ej('4.4', 'Móvil', 'respecto del sistema móvil', 'Un sistema OUVW gira 90° alrededor de su propio eje OW y después se traslada 5 unidades sobre su propio eje OU (el OU ya girado). ¿Dónde queda el punto de coordenadas ruvw = (1, 0, 0)?\n\nGuardá la matriz en `T` y el resultado en `r`.',
      '''
      ruvw = [1; 0; 0];
      % T = ...   respecto del móvil: en el orden en que se hace
      % r = ...
      ''', '''
      ruvw = [1; 0; 0];
      T = Rotz(90) * Traslacion([5 0 0]);
      r = T * [ruvw; 1]
      ''', vars=['T'], respuestas=r3(), mensajes={'T': '`T` no da: respecto del sistema móvil se posmultiplica (en el orden del enunciado)'},
      pasos=['Respecto del móvil se escribe en el orden en que se hace: primero `Rotz(90)`, después `Traslacion([5 0 0])`.'],
      pistas=['El OU girado 90° apunta hacia el Y fijo: el origen termina en (0, 5, 0).']),
    elegir_ej('4.5', 'Pre o pos', '¿premultiplicar o posmultiplicar?', 'Para cada frase del enunciado: ¿el movimiento se agrega a la izquierda (premultiplicar) o a la derecha (posmultiplicar)?', ['Premultiplicar', 'Posmultiplicar'], [
      ('girado 40° alrededor del eje **0X**', 'Premultiplicar', '0X es un eje del sistema fijo.'),
      ('trasladado un vector p **con respecto al sistema 0XYZ**', 'Premultiplicar', 'Respecto del fijo.'),
      ('girado alrededor de **su eje OU**', 'Posmultiplicar', 'OU es un eje del sistema móvil.'),
      ('trasladado sobre **su propio eje OW**', 'Posmultiplicar', 'Respecto del móvil.'),
      ('girado alrededor del eje Z **del sistema de referencia**', 'Premultiplicar', 'El de referencia es el fijo.'),
      ('luego, **respecto del sistema móvil**, se gira 30° en W', 'Posmultiplicar', 'Lo dice el enunciado.'),
    ], pregunta='¿Cómo se agrega cada movimiento?'),
  ]))

# ======================= 5 · Cambio de sistema =======================
partes.append(parte(5, 'inversa', 'Un punto visto desde otro sistema', 'Cambio de sistema',
  '`T` lleva las coordenadas de un punto del sistema móvil al fijo (`p0 = T * p1`). Para el camino al revés, la inversa: `p1 = inv(T) * p0`. Con varios sistemas encadenados, las matrices se multiplican.',
  {
    'que': 'Una homogénea `T` (el sistema 1 visto desde el 0) sirve para **cambiar de sistema** un punto: si conocés sus coordenadas en el sistema 1, `p0 = T * p1` te da las del 0. Para el camino al revés, `p1 = inv(T) * p0`.\n'
           'Con sistemas encadenados (0 → 1 → 2), las matrices se multiplican: `T02 = T01 * T12`. Es el «problema del avión» de clase: la torre de control es el sistema fijo y el avión, el móvil.',
    'consta': [
      ['T: del móvil al fijo', '`p0 = T * p1`.'],
      ['inv(T): del fijo al móvil', '`p1 = inv(T) * p0`.'],
      ['La inversa sin inv', '`inv(T) = [R\' -R\'*p; 0 0 0 1]`: la rotación se traspone.'],
      ['Encadenar sistemas', '`T02 = T01 * T12`.'],
    ],
    'ejemplo': ejemplo('avion.m', 'El problema del avión (clase y multiple choice 2024)', '''
      % El avión está en (4000, 6000, 300) desde la torre, girado 180° en Z
      T = Traslacion([4000 6000 300]) * Rotz(180);   % del avión a la torre «1»
      pasajera = [0; -23; 0; 1];      % 23 m detrás de la cabina, en el sistema del avión
      desdeTorre = T * pasajera       % (4000, 6023, 300) «1»
      torre = inv(T) * [0; 0; 0; 1]   % la torre vista desde el avión: (4000, 6000, -300) «2»
      R = T(1:3, 1:3);  p = T(1:3, 4);
      Ti = [R' -R'*p; 0 0 0 1];       % lo mismo que inv(T) «3»
      Tcab = T * Traslacion([0 0 -12])   % la cabina, 12 m más abajo en el sistema del avión «4»
    '''),
    'ojo': ['`T * p` lleva del móvil al fijo. Si el dato está en el fijo y lo querés en el móvil, va `inv(T)`.',
            '`inv(T)` no es `-T` ni `T\'`: solo la rotación se traspone; la posición pasa a `-R\'*p`.'],
    'parcial': 'Salió de opción múltiple con Pailos (la torre de control y el avión). Con Pedroni aparece cuando piden un punto visto desde otro sistema.',
    'pdf': 5,
  },
  [
    oct_ej('5.1', 'El avión', 'la torre vista desde el avión', 'Un avión está en (2500, −1800, 600) m respecto de la torre de control y girado 90° alrededor del eje Z. ¿En qué coordenadas (u, v, w) ve el avión a la torre?\n\nGuardá la matriz del avión en `T` y la torre (con el 1) en `torre`.',
      '''
      % T = ...       el avión visto desde la torre
      % torre = ...   el origen de la torre, visto desde el avión
      ''', '''
      T = Traslacion([2500 -1800 600]) * Rotz(90);
      torre = inv(T) * [0; 0; 0; 1]
      ''', vars=['T', 'torre'], respuestas=[{'pregunta': 'u', 'expr': 'torre(1)'}, {'pregunta': 'v', 'expr': 'torre(2)'}, {'pregunta': 'w', 'expr': 'torre(3)'}],
      pasos=['`T = Traslacion([2500 -1800 600]) * Rotz(90)`.', 'La torre es el origen del fijo: `[0; 0; 0; 1]`.', 'Del fijo al móvil: `inv(T) * ...`.'],
      pistas=['Primero restás la posición: (−2500, 1800, −600). Después deshacés el giro de 90°.']),
    oct_ej('5.2', 'Encadenar', 'dos sistemas encadenados', 'El sistema 1 está en (2, 0, 1) respecto del 0, girado 90° alrededor de Z. El sistema 2 está en (0, 3, 0) respecto del 1, girado −90° alrededor del eje X del sistema 1. Un punto tiene coordenadas (1, 1, 1) en el sistema 2: ¿cuáles son sus coordenadas en el 0?\n\nGuardá `T01`, `T12`, `T02` y el punto en `p0`.',
      '''
      % T01 = ...
      % T12 = ...
      % T02 = ...
      % p0  = ...
      ''', '''
      T01 = Traslacion([2 0 1]) * Rotz(90);
      T12 = Traslacion([0 3 0]) * Rotx(-90);
      T02 = T01 * T12;
      p0  = T02 * [1; 1; 1; 1]
      ''', vars=['T02', 'p0'], respuestas=r3('p0'),
      pasos=['Cada sistema respecto del anterior: posición y giro.', '`T02 = T01 * T12`.', '`p0 = T02 * [1; 1; 1; 1]`.'],
      mensajes={'T02': '`T02` no da: es T01 * T12 (en ese orden)'}),
    oct_ej('5.3', 'La inversa a mano', 'la inversa sin inv', 'Calculá la inversa de `T = Traslacion([3 -1 2]) * Roty(40)` con la fórmula `[R\' -R\'*p; 0 0 0 1]`, sin usar `inv`, y guardala en `Ti`. Para comprobar, `I = T * Ti` tiene que dar la identidad.',
      '''
      T = Traslacion([3 -1 2]) * Roty(40);
      % R = ...    la rotación
      % p = ...    la posición
      % Ti = ...   la inversa con la fórmula
      % I = T * Ti
      ''', '''
      T = Traslacion([3 -1 2]) * Roty(40);
      R = T(1:3, 1:3);
      p = T(1:3, 4);
      Ti = [R' -R'*p; 0 0 0 1]
      I = T * Ti
      ''', vars=['Ti', 'I'], checks=[NO(r'\binv\s*\(', 'Sin inv', 'Usá la fórmula, sin `inv`')],
      pasos=['`R = T(1:3, 1:3)` y `p = T(1:3, 4)`.', '`Ti = [R\' -R\'*p; 0 0 0 1]`.']),
  ]))

# ======================= 6 · Denavit–Hartenberg =======================
partes.append(parte(6, 'dh', 'Denavit–Hartenberg y la posición del efector', 'Denavit–Hartenberg',
  'Cada articulación es una fila de la tabla (θ, d, a, α). Con `matrizDenavitHartenberg` se arma una matriz por fila y se multiplican en orden; la posición del efector es `T(1:3,4)`.',
  {
    'que': 'El algoritmo de **Denavit–Hartenberg** pone un sistema de ejes en cada articulación y describe el paso de uno al siguiente con solo **4 parámetros**, una fila de la tabla por articulación:\n'
           '- **θ**: el giro alrededor de z(i−1). Es la variable si la articulación es R.\n'
           '- **d**: el corrimiento sobre z(i−1). Es la variable si es P.\n'
           '- **a**: el largo sobre x(i), entre z(i−1) y z(i).\n'
           '- **α**: el giro alrededor de x(i), de z(i−1) a z(i).\n'
           'Cada fila da una matriz `A = Rotz(θ)·Tz(d)·Tx(a)·Rotx(α)`; multiplicándolas en orden sale `T`, y la posición del efector es `T(1:3, 4)`.',
    'consta': [
      ['Ubicar los ejes', 'z(i−1) en el eje de la articulación i; x(i) perpendicular a z(i−1) y a z(i).'],
      ['La tabla: θ, d, a, α', 'Una fila por articulación; la variable va en θ (R) o en d (P).'],
      ['Una matriz por fila', '`matrizDenavitHartenberg(θ, d, a, α)`, en grados (o con \'rad\').'],
      ['Multiplicar en orden', '`T = A1 * A2 * ... * An`, o `cinematica_directa` con las cuatro columnas.'],
      ['La posición del efector', '`p = T(1:3, 4)`.'],
    ],
    'ejemplo': ejemplo('rpr.m', 'Robot RPR del 1º parcial 2026', '''
      % A = 7, B = 4; configuración q1 = -90°, d = 2, q2 = 45°
      A = 7; B = 4; q1 = -90; d = 2; q2 = 45;
      % z0 en la base, z1 a lo largo de la prismática, x2 sobre el brazo B «1»
      %  art    θ        d    a    α «2»
      %   1     q1       A    0   -90 «2»
      %   2    -90       d    0   -90 «2»
      %   3     q2-90    0    B    0 «2»
      A1 = matrizDenavitHartenberg(q1,      A, 0, -90); «3»
      A2 = matrizDenavitHartenberg(-90,     d, 0, -90); «3»
      A3 = matrizDenavitHartenberg(q2 - 90, 0, B,   0); «3»
      T = A1 * A2 * A3; «4»
      p = T(1:3, 4)          % (4,8284; 0; 9,8284) «5»
    '''),
    'ojo': ['Si la articulación es prismática, su variable va en **d** y su θ queda fijo; con las rotativas, al revés.',
            'El orden de los argumentos es θ, d, a, α (no θ, a, d, α).',
            'Los ángulos van en grados; si te los dan en radianes, pasalos con `rad2deg` o agregá `\'rad\'`. No mezcles.',
            'Con el robot en la pose de la figura, la T tiene que coincidir con lo que ves: es la mejor forma de encontrar un error de signo.'],
    'parcial': 'Son los dos últimos ejercicios del parcial de Pedroni: la tabla DH del robot de la figura (parte A) y la posición del efector para unos valores dados (parte B), con el código.',
    'pdf': 4,
  },
  [
    oct_ej('6.1', 'Una fila', 'la matriz de una fila, a mano', 'Una fila de la tabla es θ = 30°, d = 10, a = 5, α = 90°. Calculá su matriz de dos formas y comprobá que dan igual:\n- `A1`: con las cuatro transformaciones, `Rotz(θ) * Traslacion([0 0 d]) * Traslacion([a 0 0]) * Rotx(α)`.\n- `A2`: con `matrizDenavitHartenberg`.',
      '''
      th = 30; d = 10; a = 5; al = 90;
      % A1 = ...   las 4 transformaciones
      % A2 = ...   la función del profe
      ''', '''
      th = 30; d = 10; a = 5; al = 90;
      A1 = Rotz(th) * Traslacion([0 0 d]) * Traslacion([a 0 0]) * Rotx(al)
      A2 = matrizDenavitHartenberg(th, d, a, al)
      ''', vars=['A1', 'A2'],
      checks=[C(r'Rotx\s*\(', 'A1 tiene las 4 transformaciones', 'Armá `A1` con Rotz, las dos traslaciones y Rotx'), C(r'matrizDenavitHartenberg\s*\(', 'A2 con la función del profe', 'Calculá `A2` con matrizDenavitHartenberg')],
      pasos=['El orden es: giro θ en z, corrimiento d en z, largo a en x, giro α en x.'],
      mensajes={'A1': '`A1` no da: el orden es Rotz(θ), Tz(d), Tx(a), Rotx(α)', 'A2': '`A2` no da: el orden de los argumentos es θ, d, a, α'}),
    oct_ej('6.2', 'Cilíndrico', 'el robot cilíndrico', 'Robot cilíndrico de la figura (el del parcial 2026). Datos: l1 = 4, l4 = 2. Configuración: θ1 = 30°, d2 = 5, d3 = 6, θ4 = 60°. Armá la tabla DH y calculá la posición del efector final.\n\nGuardá la matriz total en `T` y la posición en `p`.',
      '''
      l1 = 4; l4 = 2; t1 = 30; d2 = 5; d3 = 6; t4 = 60;
      % una matriz por fila de la tabla (θ, d, a, α):
      % A1 = matrizDenavitHartenberg( ... );
      % ...
      % T = ...
      % p = T(1:3, 4)
      ''', '''
      l1 = 4; l4 = 2; t1 = 30; d2 = 5; d3 = 6; t4 = 60;
      %  art   θ    d    a   α
      %   1    t1   l1   0   0
      %   2    90   d2   0   90
      %   3    0    d3   0   0
      %   4    t4   l4   0   0
      A1 = matrizDenavitHartenberg(t1, l1, 0, 0);
      A2 = matrizDenavitHartenberg(90, d2, 0, 90);
      A3 = matrizDenavitHartenberg(0,  d3, 0, 0);
      A4 = matrizDenavitHartenberg(t4, l4, 0, 0);
      T = A1 * A2 * A3 * A4;
      p = T(1:3, 4)
      ''', vars=['p'], respuestas=p3(), imagen=figura('robot-cilindrico.png', 'Robot cilíndrico: columna que gira (θ1), sube (d2), un brazo que se estira (d3) y una muñeca que gira (θ4), con l1 abajo y l4 en la punta', 'Robot cilíndrico (libro de Barrientos)'),
      pasos=['Fila 1 (R): gira la base, altura fija l1.', 'Fila 2 (P): sube d2; θ y α de 90° para que z2 quede horizontal.', 'Fila 3 (P): estira d3.', 'Fila 4 (R): gira la muñeca, l4 en d.'],
      pistas=['La tabla es (θ, d, a, α): (t1, l1, 0, 0), (90, d2, 0, 90), (0, d3, 0, 0), (t4, l4, 0, 0).', 'Control rápido: x = (d3 + l4)·cos θ1, y = (d3 + l4)·sen θ1, z = l1 + d2.'],
      mensajes={'p': '`p` no da: revisá la tabla (la fila 2 lleva 90° en θ y en α)'}),
    oct_ej('6.3', 'RPR', 'el robot RPR', 'Robot RPR de la figura (codo extendido; la tercera fila usa el corrimiento q2 − 90°). Datos: A = 5, B = 3. Configuración: q1 = 30°, d = 4, q2 = 60°. Calculá la posición del efector final.\n\nGuardá `T` y `p`.',
      '''
      A = 5; B = 3; q1 = 30; d = 4; q2 = 60;
      % A1 = ...
      % A2 = ...
      % A3 = ...
      % T = ...
      % p = T(1:3, 4)
      ''', '''
      A = 5; B = 3; q1 = 30; d = 4; q2 = 60;
      A1 = matrizDenavitHartenberg(q1,      A, 0, -90);
      A2 = matrizDenavitHartenberg(-90,     d, 0, -90);
      A3 = matrizDenavitHartenberg(q2 - 90, 0, B,   0);
      T = A1 * A2 * A3;
      p = T(1:3, 4)
      ''', vars=['p'], respuestas=p3(), imagen=figura('robot-rpr.png', 'Robot RPR: base que gira q1, altura A, brazo horizontal que se desliza d y un último eslabón B que gira q2', 'Robot RPR del parcial 2026 (y 2023)'),
      pistas=['Es el ejemplo de la explicación con otros números.', 'La tabla: (q1, A, 0, −90), (−90, d, 0, −90), (q2 − 90, 0, B, 0).'],
      mensajes={'p': '`p` no da: la tabla es la del ejemplo de la explicación'}),
    oct_ej('6.4', '2R plano', 'el robot 2R plano', 'Robot plano de dos eslabones (la figura), con L1 = 0,7 m y L2 = 0,3 m y las dos articulaciones rotativas. ¿Dónde está la punta con q1 = 30° y q2 = 30°?\n\nGuardá `T` y `p`.',
      '''
      L1 = 0.7; L2 = 0.3; q1 = 30; q2 = 30;
      % A1 = ...
      % A2 = ...
      % T = ...
      % p = T(1:3, 4)
      ''', '''
      L1 = 0.7; L2 = 0.3; q1 = 30; q2 = 30;
      A1 = matrizDenavitHartenberg(q1, 0, L1, 0);
      A2 = matrizDenavitHartenberg(q2, 0, L2, 0);
      T = A1 * A2;
      p = T(1:3, 4)
      ''', vars=['p'], respuestas=p3(), imagen=figura('robot-2r.png', 'Robot plano de dos eslabones L1 y L2', 'Robot 2R plano'),
      pasos=['Las dos filas son (q, 0, L, 0): el largo de cada eslabón va en a.'],
      pistas=['Control: x = L1·cos q1 + L2·cos(q1 + q2) = 0,7562; y = 0,6098.', 'Es la directa de la pregunta de Pailos de la cinemática inversa: con estos q la punta está en (0,7562; 0,6098).']),
    oct_ej('6.5', '6 GDL', 'el robot de 6 GDL con cinematica_directa', 'Robot de 6 articulaciones de la figura (parcial 2025). La tabla (θ, d, a, α) es:\n- 1: (q1, l1, 0, −90)\n- 2: (q2, 0, l2, 0)\n- 3: (q3, 0, 0, 90)\n- 4: (0, l3 + d4, 0, −90)\n- 5: (q5, 0, 0, 90)\n- 6: (q6, l4, 0, 0)\n\nCon l1 = 6, l2 = 5, l3 = 4, l4 = 2, q1 = 30°, q2 = 30°, q3 = 60°, d4 = 2, q5 = 30°, q6 = 0: armá los vectores `th`, `d`, `a`, `al`, calculá `T` con `cinematica_directa` y la posición `p`.',
      '''
      l1 = 6; l2 = 5; l3 = 4; l4 = 2;
      q1 = 30; q2 = 30; q3 = 60; d4 = 2; q5 = 30; q6 = 0;
      % th = [ ... ];  d = [ ... ];  a = [ ... ];  al = [ ... ];
      % T = cinematica_directa(th, d, a, al, 'deg');
      % p = T(1:3, 4)
      ''', '''
      l1 = 6; l2 = 5; l3 = 4; l4 = 2;
      q1 = 30; q2 = 30; q3 = 60; d4 = 2; q5 = 30; q6 = 0;
      th = [q1 q2 q3 0 q5 q6];
      d  = [l1 0 0 l3+d4 0 l4];
      a  = [0 l2 0 0 0 0];
      al = [-90 0 90 -90 90 0];
      T = cinematica_directa(th, d, a, al, 'deg');
      p = T(1:3, 4)
      ''', vars=['p'], respuestas=p3(), imagen=figura('robot-6gdl.png', 'Robot de seis articulaciones con sus sistemas de ejes O0 a O6', 'Robot de 6 GDL del parcial 2025'),
      checks=[C(r'cinematica_directa\s*\(', 'Usa cinematica_directa', 'Calculá T con cinematica_directa')],
      pasos=['Cada vector tiene un valor por articulación (6).', 'La 4 es prismática: su variable va en d (l3 + d4) y su θ es 0.'],
      pistas=['`th = [q1 q2 q3 0 q5 q6]` y `d = [l1 0 0 l3+d4 0 l4]`.']),
    oct_ej('6.6', 'Radianes', 'el robot de 5 GDL, en radianes', 'Robot de 5 articulaciones de la figura (parcial 2024). La tabla (θ, d, a, α) es:\n- 1: (q1, L1, 0, π/2)\n- 2: (q2 + π/2, L2, 0, π/2)\n- 3: (0, d3, 0, −π/2)\n- 4: (q4, 0, 0, π/2)\n- 5: (q5, L4, 0, 0)\n\nCon L1 = 8, L2 = 4, L4 = 2, q1 = π/4, q2 = π/6, d3 = 6, q4 = π/3, q5 = −π/6 (todo en radianes): calculá la posición del efector `p`. Pasale `\'rad\'` a la función, o pasá todo a grados.',
      '''
      L1 = 8; L2 = 4; L4 = 2;
      q1 = pi/4; q2 = pi/6; d3 = 6; q4 = pi/3; q5 = -pi/6;
      % th = ...;  d = ...;  a = ...;  al = ...;
      % T = cinematica_directa(th, d, a, al, 'rad');
      % p = T(1:3, 4)
      ''', '''
      L1 = 8; L2 = 4; L4 = 2;
      q1 = pi/4; q2 = pi/6; d3 = 6; q4 = pi/3; q5 = -pi/6;
      th = [q1 q2+pi/2 0 q4 q5];
      d  = [L1 L2 d3 0 L4];
      a  = [0 0 0 0 0];
      al = [pi/2 pi/2 -pi/2 pi/2 0];
      T = cinematica_directa(th, d, a, al, 'rad');
      p = T(1:3, 4)
      ''', vars=['p'], respuestas=p3(), imagen=figura('robot-5gdl.png', 'Robot de cinco articulaciones: columna L1, brazo L2, prismática d3 y muñeca con q4 y q5', 'Robot de 5 GDL del parcial 2024'),
      pistas=['Si te olvidás el `\'rad\'`, la función toma los números como grados y da cualquier cosa.'],
      mensajes={'p': '`p` no da: ¿le pasaste \'rad\' a la función (o pasaste todo a grados)?'}),
  ]))

guardar(os.path.join(RAIZ, 'practica', 'tpa-p1', 'ejercicios.json'), 'Robótica · 1º parcial', partes)
