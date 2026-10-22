# Arma el simulacro del 1º y del 2º parcial de TPA: practica/tpa-p1/simulacro.json y practica/tpa-p2/simulacro.json.
# Son los ejercicios del parcial como en el campus, con números al azar: cada problema trae "azar" (los parámetros y,
# si hace falta, un "previo" en Octave que calcula los datos) y la página arma los números, la consigna y las
# respuestas corriendo la solución con el Octave del navegador y la carpeta del profe.
# Acá no se calcula nada: después, node herramientas/tpa-practica/validar.js arma cada problema con varias semillas y
# compara las respuestas con las del Octave de verdad.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import j, parte, guardar, RAIZ

def R(pregunta, expr, dec=4, unidad=None, opciones=None, motivo=None):
    """Una respuesta que sale de la cuenta (expr, en Octave, después de la solución). Tolerancia: la de los decimales
    pedidos, y además 1e-4 relativa (lo que muestra Octave son 5 cifras)"""
    x = {'pregunta': pregunta, 'expr': expr}
    if opciones: x['opciones'] = opciones
    else:
        x['dec'] = dec
        x['tol'] = 0.01 if dec == 0 else 10 ** -min(dec, 3)
        x['tolRel'] = 1e-4
    if unidad: x['unidad'] = unidad
    if motivo: x['motivo'] = motivo
    return x

def jj(t):
    """Como j(), pero el código puede venir pegado a partes sin sangría (la cabecera, los puntos): se saca la sangría
    más chica de las líneas que tienen"""
    ls = t.strip('\n').split('\n')
    m = min((len(l) - len(l.lstrip(' ')) for l in ls if l.strip() and l.startswith(' ')), default=0)
    return '\n'.join(l[m:] if l.startswith(' ' * m) else l for l in ls).rstrip() + '\n'

def az(id, tema, titulo, consigna, params, inicial, solucion, respuestas, previo=None, imagen=None, pistas=(), datos=None, tabla=None):
    e = {'id': id, 'tema': tema, 'titulo': titulo, 'tipo': 'octave', 'consigna': consigna, 'azar': {'params': params}}
    if previo: e['azar']['previo'] = jj(previo)
    if imagen: e['imagen'] = imagen
    if datos: e['datos'] = datos
    if tabla: e['tabla'] = tabla
    if pistas: e['pistas'] = list(pistas)
    e['archivos'] = [{'nombre': 'mi_codigo.m', 'inicial': jj(inicial), 'solucion': jj(solucion)}]
    e['respuestas'] = list(respuestas)
    return e

def figura(url, alt, pie=None):
    x = {'url': url, 'alt': alt}
    if pie: x['pie'] = pie
    return x

ANG = {'de': -170, 'a': 170, 'no': [0]}
ENT = {'de': -10, 'a': 10}
xyz = lambda v: [R(f'{v}x', f'{v}(1)'), R(f'{v}y', f'{v}(2)'), R(f'{v}z', f'{v}(3)')]
CABEZA = '% Las funciones del profe (sus pestañas) ya están en la carpeta: llamalas desde acá.\n'

# =================================== 1º parcial ===================================
I1 = 'practica/tpa-p1/img/'
p1 = []
p1.append(parte(1, 'ej1', 'Ejercicio 1 · Tres giros', 'Tres giros',
  'Como el ejercicio 1 del parcial 2026: tres giros y un vector ruvw. Respecto del sistema **fijo** se premultiplica (el último giro, a la izquierda); respecto del **móvil**, en el orden en que se hace. Las coordenadas, con 4 decimales.', None, [
  az('s1.1', 'Respecto del fijo', 'tres giros respecto del sistema fijo',
     'Un sistema OUVW ha sido girado {a1}° alrededor del eje 0{E1}, luego ha sido girado {a2}° alrededor del eje 0{E2} y finalmente ha sido girado {a3}° alrededor del eje 0{E3}. Calcular las coordenadas (rx, ry, rz) del vector r con coordenadas ruvw = ({u}, {v}, {w}).',
     {'E': {'perm': ['X', 'Y', 'Z']}, 'a1': ANG, 'a2': ANG, 'a3': ANG, 'u': ENT, 'v': ENT, 'w': ENT},
     CABEZA + '''
     ruvw = [{u}; {v}; {w}];
     ''', '''
     ruvw = [{u}; {v}; {w}];
     T = Rot{E3|min}({a3}) * Rot{E2|min}({a2}) * Rot{E1|min}({a1});
     r = T * [ruvw; 1]
     ''', xyz('r'),
     pistas=['Respecto del fijo se escribe al revés: `T = Rot{E3|min}(…) * Rot{E2|min}(…) * Rot{E1|min}(…)`.', 'El vector va con un 1 al final: `r = T * [ruvw; 1]`.']),
  az('s1.2', 'Respecto del móvil', 'tres giros respecto del sistema móvil',
     'Un sistema OUVW, que al principio coincide con 0XYZ, gira {a1}° alrededor de su eje O{E1|uvw}, después {a2}° alrededor de su eje O{E2|uvw} y por último {a3}° alrededor de su eje O{E3|uvw}. Calcular las coordenadas (rx, ry, rz) del vector r con coordenadas ruvw = ({u}, {v}, {w}).',
     {'E': {'perm': ['X', 'Y', 'Z']}, 'a1': ANG, 'a2': ANG, 'a3': ANG, 'u': ENT, 'v': ENT, 'w': ENT},
     CABEZA + '''
     ruvw = [{u}; {v}; {w}];
     ''', '''
     ruvw = [{u}; {v}; {w}];
     T = Rot{E1|min}({a1}) * Rot{E2|min}({a2}) * Rot{E3|min}({a3});
     r = T * [ruvw; 1]
     ''', xyz('r'),
     pistas=['Son los ejes del propio sistema (OU, OV, OW): se posmultiplica, en el orden del enunciado.', 'OU es como X, OV como Y y OW como Z: `T = Rot{E1|min}(…) * Rot{E2|min}(…) * Rot{E3|min}(…)`.']),
]))
p1.append(parte(2, 'ej2', 'Ejercicio 2 · Giros y traslaciones', 'Giros y traslaciones',
  'Como el ejercicio 2 del parcial 2026: giros y traslaciones respecto de 0XYZ. Se premultiplica: lo primero queda pegado al vector. Ojo con el orden cuando primero se traslada.', None, [
  az('s2.1', 'Gira, traslada, gira, traslada', 'giros y traslaciones respecto del fijo',
     'Un sistema OUVW ha sido girado {a1}° alrededor del eje 0{E1}, y posteriormente trasladado un vector p1 = ({p1x}, {p1y}, {p1z}), y luego ha sido girado {a2}° alrededor del eje 0{E2} y trasladado un vector p2 = ({p2x}, {p2y}, {p2z}) con respecto al sistema 0XYZ. Calcular las coordenadas (rx, ry, rz) del vector r con coordenadas ruvw = ({u}, {v}, {w}).',
     {'E': {'perm': ['X', 'Y', 'Z']}, 'a1': ANG, 'a2': ANG, 'p1x': ENT, 'p1y': ENT, 'p1z': ENT, 'p2x': ENT, 'p2y': ENT, 'p2z': ENT, 'u': ENT, 'v': ENT, 'w': ENT},
     CABEZA + '''
     ruvw = [{u}; {v}; {w}];
     ''', '''
     ruvw = [{u}; {v}; {w}];
     T = Traslacion([{p2x} {p2y} {p2z}]) * Rot{E2|min}({a2}) * Traslacion([{p1x} {p1y} {p1z}]) * Rot{E1|min}({a1});
     r = T * [ruvw; 1]
     ''', xyz('r'),
     pistas=['La secuencia es giro → traslación p1 → giro → traslación p2, todo respecto del fijo: se escribe al revés.', '`T = Traslacion(p2) * Rot{E2|min}(…) * Traslacion(p1) * Rot{E1|min}(…)`; `Traslacion` recibe un vector entre corchetes.']),
  az('s2.2', 'Primero traslada', 'primero trasladado y después girado',
     'Un sistema OUVW ha sido trasladado un vector p = ({px}, {py}, {pz}) con respecto al sistema 0XYZ, y posteriormente girado {a}° alrededor del eje 0{E1}. Calcular las coordenadas (rx, ry, rz) del vector r con coordenadas ruvw = ({u}, {v}, {w}).',
     {'E': {'perm': ['X', 'Y', 'Z']}, 'a': ANG, 'px': ENT, 'py': ENT, 'pz': ENT, 'u': ENT, 'v': ENT, 'w': ENT},
     CABEZA + '''
     ruvw = [{u}; {v}; {w}];
     ''', '''
     ruvw = [{u}; {v}; {w}];
     T = Rot{E1|min}({a}) * Traslacion([{px} {py} {pz}]);
     r = T * [ruvw; 1]
     ''', xyz('r'),
     pistas=['Es la trampa del recuperatorio 2024: «primero se traslada y luego se rota: la composición es R * T».']),
]))
DHP = 'Calcular la posición (x, y, z) del efector final, con 4 decimales.'
p1.append(parte(3, 'ej3', 'Ejercicio 3 · Denavit–Hartenberg: dónde queda el efector', 'DH: el efector',
  'La parte B del ejercicio de Denavit–Hartenberg: con la tabla del robot de la figura y unos valores articulares, la posición del efector `T(1:3,4)`. Son los robots de los parciales 2023–2026.', None, [
  az('s3.1', 'RPR', 'el robot RPR',
     'Robot RPR de la figura (codo extendido: la tercera fila usa q2 − 90°; tabla (θ, d, a, α): (q1, A, 0, −90), (−90, d, 0, −90), (q2 − 90, 0, B, 0)). Datos: A = {A}, B = {B}. Configuración: q1 = {q1}°, d = {d}, q2 = {q2}°. ' + DHP,
     {'A': {'de': 3, 'a': 9}, 'B': {'de': 2, 'a': 6}, 'q1': {'de': -170, 'a': 170, 'paso': 5}, 'd': {'de': 1, 'a': 8}, 'q2': {'de': -80, 'a': 80, 'paso': 5}},
     CABEZA + '''
     A = {A}; B = {B}; q1 = {q1}; d = {d}; q2 = {q2};
     ''', '''
     A = {A}; B = {B}; q1 = {q1}; d = {d}; q2 = {q2};
     T = matrizDenavitHartenberg(q1, A, 0, -90) * matrizDenavitHartenberg(-90, d, 0, -90) * matrizDenavitHartenberg(q2 - 90, 0, B, 0);
     p = T(1:3, 4)
     ''', xyz('p'), imagen=figura(I1 + 'robot-rpr.png', 'Robot RPR: base que gira q1, altura A, brazo que se desliza d y un eslabón B que gira q2', 'Robot RPR del parcial 2026')),
  az('s3.2', 'Cilíndrico', 'el robot cilíndrico',
     'Robot cilíndrico de la figura (tabla (θ, d, a, α): (θ1, l1, 0, 0), (90, d2, 0, 90), (0, d3, 0, 0), (θ4, l4, 0, 0)). Datos: l1 = {l1}, l4 = {l4}. Configuración: θ1 = {t1}°, d2 = {d2}, d3 = {d3}, θ4 = {t4}°. ' + DHP,
     {'l1': {'de': 2, 'a': 6}, 'l4': {'de': 1, 'a': 3}, 't1': {'de': -170, 'a': 170, 'paso': 5}, 'd2': {'de': 1, 'a': 8}, 'd3': {'de': 1, 'a': 8}, 't4': {'de': -90, 'a': 90, 'paso': 15}},
     CABEZA + '''
     l1 = {l1}; l4 = {l4}; t1 = {t1}; d2 = {d2}; d3 = {d3}; t4 = {t4};
     ''', '''
     l1 = {l1}; l4 = {l4}; t1 = {t1}; d2 = {d2}; d3 = {d3}; t4 = {t4};
     T = cinematica_directa([t1 90 0 t4], [l1 d2 d3 l4], [0 0 0 0], [0 90 0 0], 'deg');
     p = T(1:3, 4)
     ''', xyz('p'), imagen=figura(I1 + 'robot-cilindrico.png', 'Robot cilíndrico: columna que gira (θ1), sube (d2), un brazo que se estira (d3) y una muñeca (θ4)', 'Robot cilíndrico (libro de Barrientos)')),
  az('s3.3', '6 GDL', 'el robot de 6 GDL',
     'Robot de 6 articulaciones de la figura (parcial 2025). Tabla (θ, d, a, α): (q1, l1, 0, −90), (q2, 0, l2, 0), (q3, 0, 0, 90), (0, l3 + d4, 0, −90), (q5, 0, 0, 90), (q6, l4, 0, 0). Datos: l1 = {l1}, l2 = {l2}, l3 = {l3}, l4 = {l4}. Configuración: q1 = {q1}°, q2 = {q2}°, q3 = {q3}°, d4 = {d4}, q5 = {q5}°, q6 = {q6}°. ' + DHP,
     {'l1': {'de': 4, 'a': 8}, 'l2': {'de': 3, 'a': 7}, 'l3': {'de': 2, 'a': 5}, 'l4': {'de': 1, 'a': 3}, 'q1': {'de': -90, 'a': 90, 'paso': 5}, 'q2': {'de': -60, 'a': 60, 'paso': 5}, 'q3': {'de': -90, 'a': 90, 'paso': 5}, 'd4': {'de': 0, 'a': 4}, 'q5': {'de': -90, 'a': 90, 'paso': 5}, 'q6': {'de': -90, 'a': 90, 'paso': 15}},
     CABEZA + '''
     l1 = {l1}; l2 = {l2}; l3 = {l3}; l4 = {l4};
     q1 = {q1}; q2 = {q2}; q3 = {q3}; d4 = {d4}; q5 = {q5}; q6 = {q6};
     ''', '''
     l1 = {l1}; l2 = {l2}; l3 = {l3}; l4 = {l4};
     q1 = {q1}; q2 = {q2}; q3 = {q3}; d4 = {d4}; q5 = {q5}; q6 = {q6};
     T = cinematica_directa([q1 q2 q3 0 q5 q6], [l1 0 0 l3+d4 0 l4], [0 l2 0 0 0 0], [-90 0 90 -90 90 0], 'deg');
     p = T(1:3, 4)
     ''', xyz('p'), imagen=figura(I1 + 'robot-6gdl.png', 'Robot de seis articulaciones con sus sistemas de ejes', 'Robot de 6 GDL del parcial 2025')),
  az('s3.4', 'En radianes', 'el robot de 5 GDL, en radianes',
     'Robot de 5 articulaciones de la figura (parcial 2024). Tabla (θ, d, a, α): (q1, L1, 0, π/2), (q2 + π/2, L2, 0, π/2), (0, d3, 0, −π/2), (q4, 0, 0, π/2), (q5, L4, 0, 0). Datos: L1 = {L1}, L2 = {L2}, L4 = {L4}. Configuración (en radianes): q1 = {q1|pi}, q2 = {q2|pi}, d3 = {d3}, q4 = {q4|pi}, q5 = {q5|pi}. ' + DHP,
     {'L1': {'de': 5, 'a': 10}, 'L2': {'de': 2, 'a': 6}, 'L4': {'de': 1, 'a': 3}, 'd3': {'de': 2, 'a': 8},
      'q1': {'elegir': ['pi/6', 'pi/4', 'pi/3', '-pi/6', '-pi/4', 'pi/2', '2*pi/3']}, 'q2': {'elegir': ['pi/6', 'pi/4', '-pi/6', 'pi/3', '-pi/3']},
      'q4': {'elegir': ['pi/6', 'pi/3', '-pi/4', 'pi/2', '-pi/6']}, 'q5': {'elegir': ['pi/6', '-pi/6', 'pi/4', '-pi/3', 'pi/2']}},
     CABEZA + '''
     L1 = {L1}; L2 = {L2}; L4 = {L4};
     q1 = {q1}; q2 = {q2}; d3 = {d3}; q4 = {q4}; q5 = {q5};   % radianes
     ''', '''
     L1 = {L1}; L2 = {L2}; L4 = {L4};
     q1 = {q1}; q2 = {q2}; d3 = {d3}; q4 = {q4}; q5 = {q5};
     T = cinematica_directa([q1 q2+pi/2 0 q4 q5], [L1 L2 d3 0 L4], [0 0 0 0 0], [pi/2 pi/2 -pi/2 pi/2 0], 'rad');
     p = T(1:3, 4)
     ''', xyz('p'), imagen=figura(I1 + 'robot-5gdl.png', 'Robot de cinco articulaciones: columna L1, brazo L2, prismática d3 y muñeca', 'Robot de 5 GDL del parcial 2024'),
     pistas=['Todo está en radianes: pasale `\'rad\'` a la función (o pasá todo a grados).']),
  az('s3.5', '2R plano', 'el robot 2R plano',
     'Robot plano de dos eslabones (la figura), con L1 = {L1} m y L2 = {L2} m. ¿Dónde está la punta con q1 = {q1}° y q2 = {q2}°? ' + DHP,
     {'L1': {'de': 0.3, 'a': 1.2, 'paso': 0.1}, 'L2': {'de': 0.2, 'a': 0.8, 'paso': 0.1}, 'q1': {'de': -170, 'a': 170, 'paso': 5}, 'q2': {'de': -150, 'a': 150, 'paso': 5}},
     CABEZA + '''
     L1 = {L1}; L2 = {L2}; q1 = {q1}; q2 = {q2};
     ''', '''
     L1 = {L1}; L2 = {L2}; q1 = {q1}; q2 = {q2};
     T = matrizDenavitHartenberg(q1, 0, L1, 0) * matrizDenavitHartenberg(q2, 0, L2, 0);
     p = T(1:3, 4)
     ''', xyz('p'), imagen=figura(I1 + 'robot-2r.png', 'Robot plano de dos eslabones L1 y L2', 'Robot 2R plano')),
]))
fila = lambda n, nombres: [R(f'Fila {n} · {k}', f'tabla({n},{c + 1})', 2, u) for c, (k, u) in enumerate(nombres)]
TH = [('θ', '°'), ('d', None), ('a', None), ('α', '°')]
p1.append(parte(4, 'ej4', 'Ejercicio 4 · La tabla de Denavit–Hartenberg', 'La tabla DH',
  'La parte A del ejercicio: la tabla (θ, d, a, α) del robot de la figura, con los valores de la configuración que te dan. Podés armarla en Octave como una matriz `tabla` de una fila por articulación.', None, [
  az('s4.1', 'RPR', 'la tabla del RPR',
     'Robot RPR de la figura, con A = {A} y B = {B}, en la configuración q1 = {q1}°, d = {d}, q2 = {q2}° (en reposo x1 coincide con x2 y el brazo está extendido). Completá la tabla de Denavit–Hartenberg con los valores de esa configuración (los ángulos en grados).',
     {'A': {'de': 3, 'a': 9}, 'B': {'de': 2, 'a': 6}, 'q1': {'de': -170, 'a': 170, 'paso': 5}, 'd': {'de': 1, 'a': 8}, 'q2': {'de': -80, 'a': 80, 'paso': 5}},
     CABEZA + '''
     A = {A}; B = {B}; q1 = {q1}; d = {d}; q2 = {q2};
     %        θ      d     a     α
     % tabla = [ ... ];
     ''', '''
     A = {A}; B = {B}; q1 = {q1}; d = {d}; q2 = {q2};
     tabla = [q1      A  0  -90;
              -90     d  0  -90;
              q2-90   0  B    0]
     ''', fila(1, TH) + fila(2, TH) + fila(3, TH), imagen=figura(I1 + 'robot-rpr.png', 'Robot RPR', 'Robot RPR del parcial 2026'),
     pistas=['La prismática pone su variable en d; las rotativas, en θ.', 'La tercera fila tiene el corrimiento de −90° porque en reposo el brazo está extendido.']),
  az('s4.2', 'Cilíndrico', 'la tabla del cilíndrico',
     'Robot cilíndrico de la figura, con l1 = {l1} y l4 = {l4}, en la configuración θ1 = {t1}°, d2 = {d2}, d3 = {d3}, θ4 = {t4}°. Completá la tabla de Denavit–Hartenberg con los valores de esa configuración.',
     {'l1': {'de': 2, 'a': 6}, 'l4': {'de': 1, 'a': 3}, 't1': {'de': -170, 'a': 170, 'paso': 5}, 'd2': {'de': 1, 'a': 8}, 'd3': {'de': 1, 'a': 8}, 't4': {'de': -90, 'a': 90, 'paso': 15}},
     CABEZA + '''
     l1 = {l1}; l4 = {l4}; t1 = {t1}; d2 = {d2}; d3 = {d3}; t4 = {t4};
     % tabla = [ ... ];
     ''', '''
     l1 = {l1}; l4 = {l4}; t1 = {t1}; d2 = {d2}; d3 = {d3}; t4 = {t4};
     tabla = [t1  l1  0   0;
              90  d2  0  90;
              0   d3  0   0;
              t4  l4  0   0]
     ''', fila(1, TH) + fila(2, TH) + fila(3, TH) + fila(4, TH), imagen=figura(I1 + 'robot-cilindrico.png', 'Robot cilíndrico', 'Robot cilíndrico (libro de Barrientos)'),
     pistas=['La fila 2 lleva 90° en θ y en α para que z2 quede horizontal.']),
]))
p1.append(parte(5, 'extra', 'Extra · Cambio de sistema', 'Cambio de sistema',
  'Las de opción múltiple de Pailos: el problema del avión. `T` lleva del sistema del avión al de la torre; para el camino al revés, `inv(T)`.', None, [
  az('s5.1', 'El avión', 'la torre vista desde el avión',
     'La torre de control es el sistema fijo XYZ. Un avión está en ({x}, {y}, {z}) m y rotado {a}° alrededor del eje Z. ¿En qué coordenadas (u, v, w) ve el avión a la torre? Con 2 decimales.',
     {'x': {'de': -6000, 'a': 6000, 'paso': 100}, 'y': {'de': -6000, 'a': 6000, 'paso': 100}, 'z': {'de': 100, 'a': 1500, 'paso': 50}, 'a': {'elegir': [30, 45, 60, 90, 120, 135, 180, -45, -90, -120]}},
     CABEZA, '''
     T = Traslacion([{x} {y} {z}]) * Rotz({a});
     torre = inv(T) * [0; 0; 0; 1]
     ''', [R('u', 'torre(1)', 2, 'm'), R('v', 'torre(2)', 2, 'm'), R('w', 'torre(3)', 2, 'm')],
     pistas=['La torre es el origen del fijo; del fijo al móvil va `inv(T)`.']),
  az('s5.2', 'La pasajera', 'un punto del avión visto desde la torre',
     'El avión está en ({x}, {y}, {z}) m respecto de la torre y rotado {a}° alrededor del eje Z. Una pasajera está en el punto (0, {py}, 0) del sistema del avión. ¿Cuáles son sus coordenadas vistas desde la torre? Con 2 decimales.',
     {'x': {'de': -6000, 'a': 6000, 'paso': 100}, 'y': {'de': -6000, 'a': 6000, 'paso': 100}, 'z': {'de': 100, 'a': 1500, 'paso': 50}, 'a': {'elegir': [30, 45, 60, 90, 120, 135, 180, -45, -90, -120]}, 'py': {'de': -30, 'a': -5}},
     CABEZA, '''
     T = Traslacion([{x} {y} {z}]) * Rotz({a});
     pt = T * [0; {py}; 0; 1]
     ''', [R('x', 'pt(1)', 2, 'm'), R('y', 'pt(2)', 2, 'm'), R('z', 'pt(3)', 2, 'm')]),
]))
guardar(os.path.join(RAIZ, 'practica', 'tpa-p1', 'simulacro.json'), 'Simulacro · 1º parcial', p1)

# =================================== 2º parcial ===================================
I2 = 'practica/tpa-p2/img/'
CIL = figura(I1 + 'robot-cilindrico.png', 'Robot cilíndrico RPPR', 'Robot cilíndrico RPPR')
p2 = []
p2.append(parte(1, 'ej1', 'Ejercicio 1 · Cinemática inversa geométrica (RRR)', 'CI geométrica',
  'Como el ejercicio 1: el RRR de la cátedra y un punto. Por geometría: q1 = atan2d(y, x), el plano del brazo (r, s = z − l1), la ley del coseno para q3 y un q2 para cada q3. Las dos soluciones, con 2 decimales.', None, [
  az('s1.1', 'RRR', 'las dos soluciones del RRR',
     'Un robot antropomorfo RRR tiene la tabla DH de la cátedra (θ = q1, q2, q3; d = l1, 0, 0; a = 0, l2, l3; α = 90°, 0, 0) con l1 = {l1} m, l2 = {l2} m y l3 = {l3} m. Calcular por el método geométrico los valores articulares que llevan el extremo al punto P = ({Px|3}; {Py|3}; {Pz|3}) m. Informar ambas soluciones (A con q3 > 0 y B con q3 < 0), en grados con 2 decimales.',
     {'l1': {'elegir': [0.4, 0.45, 0.5]}, 'l2': {'elegir': [0.3, 0.35, 0.4]}, 'l3': {'elegir': [0.2, 0.25, 0.3]},
      'g1': {'de': -170, 'a': 170}, 'g2': {'de': -40, 'a': 70}, 'g3': {'de': 25, 'a': 150}},
     CABEZA + '''
     l1 = {l1}; l2 = {l2}; l3 = {l3};   % [m]
     P = [{Px|3} {Py|3} {Pz|3}];
     ''', '''
     l1 = {l1}; l2 = {l2}; l3 = {l3};
     P = [{Px|3} {Py|3} {Pz|3}];  x = P(1); y = P(2); z = P(3);
     q1 = atan2d(y, x);
     r = hypot(x, y);  s = z - l1;
     D = (r^2 + s^2 - l2^2 - l3^2) / (2*l2*l3);
     q3A =  atan2d(sqrt(1 - D^2), D);
     q3B = -atan2d(sqrt(1 - D^2), D);
     q2A = atan2d(s, r) - atan2d(l3*sind(q3A), l2 + l3*cosd(q3A));
     q2B = atan2d(s, r) - atan2d(l3*sind(q3B), l2 + l3*cosd(q3B));
     solA = [q1 q2A q3A]
     solB = [q1 q2B q3B]
     ''', [R('q1', 'q1', 2, '°'), R('q2 (A)', 'q2A', 2, '°'), R('q3 (A)', 'q3A', 2, '°'), R('q2 (B)', 'q2B', 2, '°'), R('q3 (B)', 'q3B', 2, '°')],
     previo='''
     b = l2*cosd(g2) + l3*cosd(g2 + g3);
     Px = round(cosd(g1)*b*1000)/1000;  Py = round(sind(g1)*b*1000)/1000;
     Pz = round((l1 + l2*sind(g2) + l3*sind(g2 + g3))*1000)/1000;
     ''', imagen=figura(I2 + 'rrr-plano-y-vista-superior.png', 'El RRR en su plano vertical y visto desde arriba', 'El RRR partido en dos problemas 2D'),
     pistas=['Verificá cada solución con `cinematica_directa(sol, [l1 0 0], [0 l2 l3], [90 0 0])`: tiene que volver a P.']),
]))
def tres(n, cols):
    return [R(f'Punto {k} · {c}', f'Q({k},{i + 1})', 2, u) for k in range(1, n + 1) for i, (c, u) in enumerate(cols)]
def tabla_puntos(n):
    return {'titulo': 'Los puntos', 'cabecera': ['Punto', 'x [mm]', 'y [mm]', 'z [mm]'], 'filas': [[str(k), f'{{X{k}|2}}', f'{{Y{k}|2}}', f'{{Z{k}|2}}'] for k in range(1, n + 1)]}
P_INI = lambda n: 'P = [' + ';\n          '.join(f'{{X{k}|2}} {{Y{k}|2}} {{Z{k}|2}}' for k in range(1, n + 1)) + '];'
p2.append(parte(2, 'ej2', 'Ejercicio 2 · Completar la tabla (parcial 2026)', 'Completar la tabla',
  'Como en el parcial 2026: un robot y una tabla de puntos para completar con los valores articulares. En el cilíndrico, el RPP y el RPR sale por geometría; el IRB2400, con `cinematica_inversa`. Verificá cada fila con la directa.', None, [
  az('s2.1', 'Cilíndrico', 'la tabla del cilíndrico RPPR',
     'Dado el robot cilíndrico (RPPR) de la figura, con l1 = {l1} mm y l4 = {l4} mm (tabla θ = q1 90 0 q4, d = l1 d2 d3 l4, a = 0 0 0 0, α = 0 90 0 0), determinar q1, d2 y d3 para que el efector final se ubique en cada punto de la tabla (q4 = 0). Con 2 decimales.',
     dict({'l1': {'elegir': [400, 500, 600]}, 'l4': {'elegir': [100, 150, 200]}},
          **{f'{v}{k}': d for k in (1, 2, 3) for v, d in (('a', {'de': -175, 'a': 175, 'paso': 5}), ('h', {'de': 100, 'a': 900, 'paso': 50}), ('r', {'de': 100, 'a': 1000, 'paso': 50}))}),
     CABEZA + '''
     l1 = {l1}; l4 = {l4};   % [mm]
     ''' + P_INI(3), '''
     l1 = {l1}; l4 = {l4};
     ''' + P_INI(3) + '''
     Q = zeros(3, 4);
     for k = 1:3
       x = P(k,1); y = P(k,2); z = P(k,3);
       Q(k,:) = [atan2d(y, x), z - l1, hypot(x, y) - l4, 0];
     end
     Q
     ''', tres(3, [('q1', '°'), ('d2', 'mm'), ('d3', 'mm')]),
     previo='\n'.join(f'X{k} = round((r{k} + l4)*cosd(a{k})*100)/100; Y{k} = round((r{k} + l4)*sind(a{k})*100)/100; Z{k} = l1 + h{k};' for k in (1, 2, 3)),
     tabla=tabla_puntos(3), imagen=CIL),
  az('s2.2', 'RPP', 'la tabla del RPP',
     'Dado el robot RPP de 3 GDL de la figura, con l1 = {l1} mm (tabla θ = q1 0 0, d = l1 d2 d3, a = 0 0 0, α = 0 −90 0; el estado de reposo es el de la figura), determinar q1, d2 y d3 para cada punto de la tabla. Con 2 decimales.',
     dict({'l1': {'elegir': [100, 200, 300]}},
          **{f'{v}{k}': d for k in (1, 2, 3) for v, d in (('a', {'de': -175, 'a': 175, 'paso': 5}), ('h', {'de': 100, 'a': 600, 'paso': 50}), ('r', {'de': 100, 'a': 600, 'paso': 50}))}),
     CABEZA + '''
     l1 = {l1};   % [mm]
     ''' + P_INI(3), '''
     l1 = {l1};
     ''' + P_INI(3) + '''
     Q = zeros(3, 3);
     for k = 1:3
       x = P(k,1); y = P(k,2); z = P(k,3);
       Q(k,:) = [atan2d(-x, y), z - l1, hypot(x, y)];
     end
     Q
     ''', tres(3, [('q1', '°'), ('d2', 'mm'), ('d3', 'mm')]),
     previo='\n'.join(f'T = cinematica_directa([a{k} 0 0], [l1 h{k} r{k}], [0 0 0], [0 -90 0]); X{k} = round(T(1,4)*100)/100; Y{k} = round(T(2,4)*100)/100; Z{k} = round(T(3,4)*100)/100;' for k in (1, 2, 3)),
     tabla=tabla_puntos(3), imagen=figura(I2 + 'robot-rpp.png', 'Robot RPP', 'Robot RPP del parcial 2026'),
     pistas=['Con q1 = 0 el brazo apunta hacia +y: q1 = atan2d(−x, y).']),
  az('s2.3', 'RPR codo arriba', 'la tabla del RPR (codo arriba)',
     'Dado el robot RPR (codo arriba) de la figura, con l1 = {l1} mm y l2 = {l2} mm (tabla θ = q1 −90 q3, d = l1 d2 0, a = 0 0 l2, α = −90 −90 0; en reposo x0 coincide con x1 y el último eslabón apunta hacia arriba), determinar q1, d2 y q3 en la rama codo arriba (q3 < 0) para cada punto. Con 2 decimales.',
     dict({'l1': {'elegir': [100, 150, 200]}, 'l2': {'elegir': [200, 300, 400]}},
          **{f'{v}{k}': d for k in (1, 2, 3) for v, d in (('a', {'de': -165, 'a': 165, 'paso': 15}), ('d', {'de': 100, 'a': 400, 'paso': 50}), ('c', {'de': -165, 'a': -15, 'paso': 15}))}),
     CABEZA + '''
     l1 = {l1}; l2 = {l2};   % [mm]
     ''' + P_INI(3), '''
     l1 = {l1}; l2 = {l2};
     ''' + P_INI(3) + '''
     Q = zeros(3, 3);
     for k = 1:3
       x = P(k,1); y = P(k,2); z = P(k,3);
       q3 = -acosd((z - l1) / l2);
       Q(k,:) = [atan2d(-x, y), hypot(x, y) + l2*sind(q3), q3];
     end
     Q
     ''', tres(3, [('q1', '°'), ('d2', 'mm'), ('q3', '°')]),
     previo='\n'.join(f'T = cinematica_directa([a{k} -90 c{k}], [l1 d{k} 0], [0 0 l2], [-90 -90 0]); X{k} = round(T(1,4)*100)/100; Y{k} = round(T(2,4)*100)/100; Z{k} = round(T(3,4)*100)/100;' for k in (1, 2, 3)),
     tabla=tabla_puntos(3), imagen=figura(I2 + 'robot-rpr.png', 'Robot RPR', 'Robot RPR del parcial 2026'),
     pistas=['z − l1 = l2·cos q3 → q3 = −acosd((z − l1)/l2).', '√(x² + y²) = d2 − l2·sen q3 y q1 = atan2d(−x, y).']),
  az('s2.4', 'IRB2400', 'el ABB IRB2400 (6 GDL)',
     'El ABB IRB2400 (RRRPRR) del parcial 2026: l1 = 770, l2 = 420, l3 = 400, l4 = 250 mm; tabla (θ, d, a, α): (q1, l1, 0, −90), (q2, 0, l2, 0), (q3, 0, 0, 90), (0, l3 + d4, 0, −90), (q5, 0, 0, 90), (q6, l4, 0, 0). Se adopta d4 = 0, θ5 = 0 y θ6 = 0. Determinar θ1, θ2 y θ3 para cada punto con `cinematica_inversa`, usando la semilla [atan2d(y, x); 20; −45; 0; 0; 0] y las tres últimas congeladas con límites iguales. Con 2 decimales.',
     dict(**{f'{v}{k}': d for k in (1, 2) for v, d in (('a', {'de': -160, 'a': 160, 'paso': 1}), ('b', {'de': 5, 'a': 55, 'paso': 1}), ('c', {'de': -80, 'a': -25, 'paso': 1}))}),
     CABEZA + '''
     l1 = 770; l2 = 420; l3 = 400; l4 = 250;
     P = [{X1|2} {Y1|2} {Z1|2};
          {X2|2} {Y2|2} {Z2|2}];
     ''', '''
     l1 = 770; l2 = 420; l3 = 400; l4 = 250;
     P = [{X1|2} {Y1|2} {Z1|2};
          {X2|2} {Y2|2} {Z2|2}];
     tipo = 'RRRPRR';  q_offset = zeros(6, 1);  d_offset = [l1; 0; 0; l3; 0; l4];
     a = [0; l2; 0; 0; 0; 0];  alpha = [-90; 0; 90; -90; 90; 0];
     opts.q_min = [-360; -360; -360; 0; 0; 0];  opts.q_max = [360; 360; 360; 0; 0; 0];
     Q = zeros(2, 3);
     for k = 1:2
       q0 = [atan2d(P(k,2), P(k,1)); 20; -45; 0; 0; 0];
       [q, ~, ~, ok] = cinematica_inversa(P(k,:)', q0, tipo, q_offset, d_offset, a, alpha, 'deg', opts);
       if ~ok, error('no convergió'); end
       Q(k,:) = q(1:3)';
     end
     Q
     ''', tres(2, [('θ1', '°'), ('θ2', '°'), ('θ3', '°')]),
     previo='\n'.join(f'T = cinematica_directa([a{k} b{k} c{k} 0 0 0], [770 0 0 400 0 250], [0 420 0 0 0 0], [-90 0 90 -90 90 0]); X{k} = round(T(1,4)*100)/100; Y{k} = round(T(2,4)*100)/100; Z{k} = round(T(3,4)*100)/100;' for k in (1, 2)),
     tabla=tabla_puntos(2),
     pistas=['Congelar = límites iguales: `opts.q_min(4:6) = opts.q_max(4:6) = 0`.', 'La semilla elige la rama del codo: con [q1; 20; −45; 0; 0; 0] sale la del enunciado.']),
]))
p2.append(parte(3, 'ej3', 'Ejercicio 2 · CI numérica (DLS) con resultados a completar', 'DLS a completar',
  'El formato «resultados a completar»: el cilíndrico, una semilla y un punto. La primera vuelta de DLS (el error inicial y la postura después de la 1ª iteración) y la solución de `cinematica_inversa` con la cantidad de iteraciones.', None, [
  az('s3.1', 'Cilíndrico', 'DLS paso a paso con el cilíndrico',
     'El robot cilíndrico RPPR (tabla θ = q1 90 0 q4, d = l1 d2 d3 l4, a = 0 0 0 0, α = 0 90 0 0) tiene l1 = {l1} mm y l4 = {l4} mm. Usando `cinematica_inversa` (DLS, parámetros por defecto: λ = 0,05) con la semilla q0 = [0°; 100 mm; 100 mm; 0°], hallar la postura que lleva el TCP a pd = ({Pdx}; {Pdy}; {Pdz}) mm. Completar con 2 decimales.',
     {'l1': {'elegir': [300, 400, 500]}, 'l4': {'elegir': [50, 100, 150]}, 'g': {'de': 15, 'a': 75}, 'h': {'de': 100, 'a': 400, 'paso': 10}, 'r': {'de': 150, 'a': 400, 'paso': 10}},
     CABEZA + '''
     l1 = {l1}; l4 = {l4};   % [mm]
     pd = [{Pdx}; {Pdy}; {Pdz}];
     q0 = [0; 100; 100; 0];
     ''', '''
     l1 = {l1}; l4 = {l4};
     pd = [{Pdx}; {Pdy}; {Pdz}];
     q0 = [0; 100; 100; 0];
     tipo = 'RPPR';  q_offset = [0; 90; 0; 0];  d_offset = [l1; 0; 0; l4];
     a = [0; 0; 0; 0];  alpha = [0; 90; 0; 0];
     % la primera vuelta, a mano
     T  = cinematica_directa(q_offset + [q0(1); 0; 0; q0(4)], d_offset + [0; q0(2); q0(3); 0], a, alpha, 'deg');
     e0 = pd - T(1:3, 4);
     J  = jacobiano_analitico(q0, tipo, q_offset, d_offset, a, alpha, 'deg');  Jp = J(1:3, :);
     q1v = q0 + Jp' * ((Jp*Jp' + 0.05^2*eye(3)) \\ e0)
     % la función completa
     [q, theta, d, ok, info] = cinematica_inversa(pd, q0, tipo, q_offset, d_offset, a, alpha, 'deg')
     if q(3) < 0, error('d3 negativo: DLS llegó a la rama imposible'); end   % verificar que tenga sentido
     ''', [R('‖e0‖, el error en la semilla', 'norm(e0)', 2, 'mm'), R('q1 después de la 1ª iteración', 'q1v(1)', 2, '°'), R('d3 después de la 1ª iteración', 'q1v(3)', 2, 'mm'),
           R('Solución: q1', 'q(1)', 2, '°'), R('Solución: d2', 'q(2)', 2, 'mm'), R('Solución: d3', 'q(3)', 2, 'mm'), R('Iteraciones (info.iters)', 'info.iters', 0)],
     previo='''
     Pdx = round((r + l4)*cosd(g));  Pdy = round((r + l4)*sind(g));  Pdz = l1 + h;
     ''', imagen=CIL,
     pistas=['La primera vuelta: `dq = Jp\' * ((Jp*Jp\' + 0.05^2*eye(3)) \\ e0)` y `q = q0 + dq`.', 'La 4ª salida de `cinematica_inversa` es el éxito y la 5ª, `info` (con `info.iters`).']),
]))
p2.append(parte(4, 'ej4', 'Ejercicio 3 · Generación de trayectorias', 'Trayectorias',
  'El último ejercicio: `generacion_de_trayectorias` entre dos posturas (manda la articulación más lenta), con la inversa si te dan puntos cartesianos, o un círculo recorrido punto a punto. Graficá con `Dibujar_Temporal`.', None, [
  az('s4.1', 'Articular', 'una trayectoria articular',
     'Te dan las posturas de un RRR: qi = ({i1}°, {i2}°, {i3}°) y qf = ({f1}°, {f2}°, {f3}°), con velocidades máximas wmax = ({w1}, {w2}, {w3}) °/s y paso h = {h} s. Generá la trayectoria sincronizada con `generacion_de_trayectorias` e informá el tiempo total, la cantidad de puntos y la velocidad de cada articulación (2 decimales).',
     {'i1': {'de': -90, 'a': 90, 'paso': 5}, 'i2': {'de': -60, 'a': 60, 'paso': 5}, 'i3': {'de': -90, 'a': 90, 'paso': 5},
      'f1': {'de': -90, 'a': 90, 'paso': 5}, 'f2': {'de': -60, 'a': 60, 'paso': 5}, 'f3': {'de': -90, 'a': 90, 'paso': 5},
      'w1': {'elegir': [10, 15, 20, 25, 30, 40]}, 'w2': {'elegir': [10, 15, 20, 25, 30, 40]}, 'w3': {'elegir': [10, 15, 20, 25, 30, 40]}, 'h': {'elegir': [0.05, 0.1, 0.2]}},
     CABEZA + '''
     qi = [{i1} {i2} {i3}];  qf = [{f1} {f2} {f3}];   % [deg]
     wmax = [{w1} {w2} {w3}];  h = {h};
     ''', '''
     qi = [{i1} {i2} {i3}];  qf = [{f1} {f2} {f3}];
     wmax = [{w1} {w2} {w3}];  h = {h};
     [q, Dq, t] = generacion_de_trayectorias(qi, qf, wmax, h);
     T_total = t(end)
     N = size(q, 1)
     w = Dq(1, :)
     Dibujar_Temporal(t, q, Dq);
     ''', [R('Tiempo total', 'T_total', 2, 's'), R('Cantidad de puntos', 'N', 0), R('Velocidad de q1', 'w(1)', 2, '°/s'), R('Velocidad de q2', 'w(2)', 2, '°/s'), R('Velocidad de q3', 'w(3)', 2, '°/s')],
     pistas=['T = máx(|qf − qi| ./ wmax) y n = máx(2, ⌈T/h⌉ + 1).']),
  az('s4.2', 'De A a B', 'de un punto a otro con el cilíndrico',
     'Con el cilíndrico RPPR (l1 = 400 mm, l4 = 100 mm, cargado como para `cinematica_inversa`), generar la trayectoria articular sincronizada que lleve el TCP de A = ({Ax}; {Ay}; {Az}) mm a B = ({Bx}; {By}; {Bz}) mm, con wmax = (30, 50, 50, 30) y h = 0,1 s. La semilla de A es [atan2d(Ay, Ax); 100; 100; 0] y la de B, la solución de A. Informá el tiempo total, la cantidad de puntos y la velocidad de q1 (2 decimales), y qué articulación manda.',
     {'ga': {'de': 10, 'a': 80}, 'ha': {'de': 100, 'a': 400, 'paso': 10}, 'ra': {'de': 150, 'a': 400, 'paso': 10},
      'gb': {'de': 95, 'a': 170}, 'hb': {'de': 100, 'a': 400, 'paso': 10}, 'rb': {'de': 150, 'a': 400, 'paso': 10}},
     CABEZA + '''
     l1 = 400; l4 = 100;
     tipo = 'RPPR';  q_offset = [0; 90; 0; 0];  d_offset = [l1; 0; 0; l4];
     a = [0; 0; 0; 0];  alpha = [0; 90; 0; 0];
     PA = [{Ax}; {Ay}; {Az}];  PB = [{Bx}; {By}; {Bz}];
     wmax = [30 50 50 30];  h = 0.1;
     ''', '''
     l1 = 400; l4 = 100;
     tipo = 'RPPR';  q_offset = [0; 90; 0; 0];  d_offset = [l1; 0; 0; l4];
     a = [0; 0; 0; 0];  alpha = [0; 90; 0; 0];
     PA = [{Ax}; {Ay}; {Az}];  PB = [{Bx}; {By}; {Bz}];
     wmax = [30 50 50 30];  h = 0.1;
     qA = cinematica_inversa(PA, [atan2d(PA(2), PA(1)); 100; 100; 0], tipo, q_offset, d_offset, a, alpha, 'deg');
     qB = cinematica_inversa(PB, qA, tipo, q_offset, d_offset, a, alpha, 'deg');
     [q, Dq, t] = generacion_de_trayectorias(qA', qB', wmax, h);
     T_total = t(end)
     N_puntos = size(q, 1)
     velocidades = Dq(1, :)
     [~, manda] = max(abs(qB' - qA') ./ wmax);
     Dibujar_Temporal(t, q, Dq);
     ''', [R('Tiempo total', 'T_total', 2, 's'), R('Cantidad de puntos', 'N_puntos', 0), R('Velocidad de q1', 'velocidades(1)', 2, '°/s'),
           R('¿Qué articulación manda?', 'manda', opciones=['q1', 'd2', 'd3', 'q4'])],
     previo='''
     Ax = round((ra + 100)*cosd(ga)); Ay = round((ra + 100)*sind(ga)); Az = 400 + ha;
     Bx = round((rb + 100)*cosd(gb)); By = round((rb + 100)*sind(gb)); Bz = 400 + hb;
     ''', imagen=CIL,
     pistas=['Primero la inversa de A y de B; después `generacion_de_trayectorias(qA\', qB\', wmax, h)` (como filas).', 'Manda la que más tarda yendo a su velocidad máxima: max(|Δq| ./ wmax).']),
  az('s4.3', 'Círculo', 'el círculo del parcial 2026',
     'El cilíndrico RPPR con l1 = 600 mm y l4 = 200 mm tiene que recorrer un círculo de radio {R} mm en el plano XZ (y = {yc} mm constante), de centro (0; {yc}; {zc}) mm, con `w = 0:{paso}:360`. Resolver la inversa en cada punto (q_start = [90; 500; 500; 0], encadenando la semilla) y unir los tramos con `generacion_de_trayectorias` (wmax = [60 200 200 60], h = {h} s) sin repetir el punto de unión. Informá la cantidad de puntos del círculo, de muestras de la trayectoria y el tiempo total (2 decimales).',
     {'R': {'elegir': [100, 120, 150, 180]}, 'yc': {'elegir': [600, 700, 800]}, 'zc': {'elegir': [1000, 1100, 1200]}, 'paso': {'elegir': [10, 15, 20, 30]}, 'h': {'elegir': [0.05, 0.1]}},
     CABEZA + '''
     l1 = 600; l4 = 200;
     tipo = 'RPPR';  q_offset = [0; 90; 0; 0];  d_offset = [l1; 0; 0; l4];
     a = [0; 0; 0; 0];  alpha = [0; 90; 0; 0];
     R = {R}; x0 = 0; y0 = {yc}; z0 = {zc};
     w = 0:{paso}:360;
     wmax = [60 200 200 60];  h = {h};
     ''', '''
     l1 = 600; l4 = 200;
     tipo = 'RPPR';  q_offset = [0; 90; 0; 0];  d_offset = [l1; 0; 0; l4];
     a = [0; 0; 0; 0];  alpha = [0; 90; 0; 0];
     R = {R}; x0 = 0; y0 = {yc}; z0 = {zc};
     w = 0:{paso}:360;
     wmax = [60 200 200 60];  h = {h};
     P = [x0 + R*cosd(w); y0 + zeros(size(w)); z0 + R*sind(w)];
     N = size(P, 2);  Q = zeros(N, 4);  q = [90; 500; 500; 0];
     for k = 1:N
       q = cinematica_inversa(P(:,k), q, tipo, q_offset, d_offset, a, alpha, 'deg');
       Q(k,:) = q';
     end
     Qt = []; DQt = []; Tt = [];
     for k = 1:N-1
       [qk, dqk, tk] = generacion_de_trayectorias(Q(k,:), Q(k+1,:), wmax, h);
       if k > 1, qk = qk(2:end,:); dqk = dqk(2:end,:); tk = tk(2:end); end
       t0 = 0; if ~isempty(Tt), t0 = Tt(end); end
       Qt = [Qt; qk]; DQt = [DQt; dqk]; Tt = [Tt; t0 + tk];
     end
     printf('Puntos: %d | muestras: %d | tiempo: %.2f s\\n', N, size(Qt,1), Tt(end));
     Dibujar_Temporal(Tt, Qt, DQt);
     ''', [R('Puntos del círculo', 'N', 0), R('Muestras de la trayectoria', 'size(Qt,1)', 0), R('Tiempo total', 'Tt(end)', 2, 's')],
     imagen=CIL,
     pistas=['En cada tramo k > 1, sacá la primera fila (es la última del anterior) y sumale el tiempo acumulado.']),
]))
guardar(os.path.join(RAIZ, 'practica', 'tpa-p2', 'simulacro.json'), 'Simulacro · 2º parcial', p2)
