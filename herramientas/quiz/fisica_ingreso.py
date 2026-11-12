#!/usr/bin/env python3
"""Física del cursillo de ingreso: arma el quiz (quiz/fisica-ingreso.json), las dos figuras de cuerdas (quiz/img/)
y la guía en PDF con las 5 preguntas del examen del campus resueltas (material/cursillo/fisica/).

Las respuestas se calculan acá (g = 9,8 m/s², como la cátedra), así cada número está verificado.
De dónde sale cada pregunta:
- Simulacros 1, 2 y 3 del campus y el Examen de ingreso 2021: las mismas 5 preguntas con otros números.
  Del campus solo se pasan los enunciados y las respuestas (no se publican las capturas de los intentos).
- Exámenes finales y recuperatorios de marzo 2011 y marzo 2012, con su clave de corrección.
  En la clave las opciones correctas están resaltadas; cuando el resaltado tapa el texto, la opción se reescribió.

Uso, desde la raíz del repo:
  python3 herramientas/quiz/fisica_ingreso.py                 (quiz y figuras)
  python3 herramientas/quiz/fisica_ingreso.py --pdf --fuente CARPETA_OPEN_SANS   (además, la guía en PDF)
"""
import argparse, html, json, math, os, shutil, subprocess, tempfile

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
G = 9.8
rad, deg = math.radians, math.degrees
sen, cos, tg = (lambda a: math.sin(rad(a))), (lambda a: math.cos(rad(a))), (lambda a: math.tan(rad(a)))


def f(x, d=2):
    """Número con coma decimal, como en el campus."""
    return f'{x:.{d}f}'.replace('.', ',')


def R(t):
    return f'<span class="resp">{t}</span>'


# ───────────────────────── Las 5 preguntas del examen del campus ─────────────────────────
def campus_conversion(v1, v2):
    dv = v2 - v1
    k = 1609 / 3600
    r = dv * k
    return dict(
        en=f'El límite de velocidad de una carretera pasó de <b>{f(v1, 1)} [millas/h]</b> a <b>{f(v2, 1)} [millas/h]</b>. ¿Cuál es la diferencia de velocidad en <b>m/s</b>?<br><b>Datos:</b> 1 milla = 1,609 km.<br>Expresá el resultado en m/s con dos decimales.',
        num=f'Δv = {R(f(r))} m/s',
        ex=f'1) La diferencia en mi/h: {f(v2, 1)} − {f(v1, 1)} = {f(dv, 1)} mi/h.<br>2) Pasás a m/s: 1 mi/h = 1609 m / 3600 s = {f(k, 4)} m/s.<br>3) {f(dv, 1)} × {f(k, 4)} = <b>{f(r)} m/s</b>.<br>Ojo: primero restá y después convertí (da lo mismo, pero hacés una sola conversión).',
        r=r)


def campus_vector(d1, ang, d2):
    x1, y1 = d1 * cos(ang), d1 * sen(ang)
    x, y = x1 + d2, y1
    a = deg(math.atan2(y, x))
    return dict(
        en=f'Un barco de turismo zarpa desde una isla y navega <b>{d1} [km]</b> con rumbo noroeste (<b>{ang}°</b> medidos respecto del este) hacia otra isla. Después sigue navegando <b>{d2} [km]</b> hacia el este. Encontrá el vector posición final: ¿en qué dirección (ángulo respecto del este) está? Usá el método de las componentes.',
        num=f'ángulo = {R(f(a))}°',
        ex=f'1) Primer tramo en componentes: x₁ = {d1}·cos {ang}° = {f(x1)} km; y₁ = {d1}·sen {ang}° = {f(y1)} km.<br>2) Segundo tramo, todo en x: x₂ = {d2} km; y₂ = 0.<br>3) Sumás: x = {f(x)} km; y = {f(y)} km.<br>4) Dirección: α = arctg(y/x) = arctg({f(y)}/{f(x)}) = <b>{f(a)}°</b> (primer cuadrante: x e y positivas).',
        r=a)


def campus_mru(v, d, menos):
    t = d / v
    t2 = t - menos / 60
    v2 = d / t2
    return dict(
        en=f'Un vehículo va por una carretera recta, sin detenerse, a velocidad constante de <b>{v} [km/h]</b> durante <b>{d} [km]</b> de recorrido. ¿A qué velocidad constante tendría que ir para tardar <b>{menos} minutos</b> menos en ese recorrido? Expresá el resultado en [km/h].',
        num=f'v = {R(f(v2))} km/h',
        ex=f'Es MRU: t = d / v.<br>1) Tiempo que tarda: t = {d} km / {v} km/h = {f(t, 4)} h.<br>2) {menos} min = {menos}/60 h = {f(menos / 60, 4)} h → el tiempo nuevo es {f(t, 4)} − {f(menos / 60, 4)} = {f(t2, 4)} h.<br>3) v = {d} km / {f(t2, 4)} h = <b>{f(v2)} km/h</b>.<br>Ojo: no restes los minutos a la velocidad; lo que cambia es el tiempo.',
        r=v2)


def campus_trabajo(F, ang, d):
    w = F * d * cos(ang)
    return dict(
        en=f'Un mecánico empuja una caja de herramientas por la entrada de una cochera, con una fuerza de <b>{f(F)} N</b> dirigida hacia abajo con un ángulo de <b>{f(ang)}°</b> respecto de la horizontal. ¿Cuánto trabajo hace si la caja se mueve <b>{f(d)} m</b> horizontalmente? Respondé en joules [J].',
        num=f'W = {R(f(w))} J',
        ex=f'W = F · d · cos θ, con θ el ángulo entre la fuerza y el desplazamiento (horizontal).<br>W = {f(F)} N × {f(d)} m × cos {f(ang)}° = {f(F)} × {f(d)} × {f(cos(ang), 4)} = <b>{f(w)} J</b>.<br>Que la fuerza vaya hacia abajo no cambia la cuenta: solo trabaja su componente horizontal.',
        r=w)


def campus_tension(a, t, P):
    ta = P / (sen(a) + cos(a) * tg(t))
    tb = ta * cos(a) / cos(t)
    return dict(
        en=f'Para el sistema de la figura, determiná el módulo de la tensión en la <b>cuerda A</b>.<br><b>Datos:</b> α = {a}°; θ = {t}°; P = {P} [N].<br>Usá un sistema de coordenadas con el origen en el punto donde se unen las cuerdas. Resultado en [N].',
        img='quiz/img/fisica-cuerdas-techo.svg',
        num=f'T<sub>A</sub> = {R(f(ta, 0))} N &nbsp; (T<sub>B</sub> = {f(tb, 0)} N)',
        ex=f'Equilibrio en el nudo: ΣFx = 0 y ΣFy = 0. A tira hacia la izquierda y arriba (α con el techo); B, hacia la derecha y arriba (θ con el techo); P, hacia abajo.<br>ΣFx: T<sub>B</sub>·cos θ − T<sub>A</sub>·cos α = 0 → T<sub>B</sub> = T<sub>A</sub>·cos α / cos θ.<br>ΣFy: T<sub>A</sub>·sen α + T<sub>B</sub>·sen θ − P = 0.<br>Reemplazando: T<sub>A</sub>·(sen α + cos α·tg θ) = P → T<sub>A</sub> = {P} / ({f(sen(a), 4)} + {f(cos(a), 4)}·{f(tg(t), 4)}) = <b>{f(ta, 0)} N</b>.',
        r=ta)


CAMPUS = [
    ('Simulacro 1', campus_conversion(43.3, 60.7), campus_vector(133, 129, 256), campus_mru(72, 124, 38), campus_trabajo(39.49, 32.11, 2.81), campus_tension(37, 40, 1089)),
    ('Simulacro 2', campus_conversion(44.6, 59.3), campus_vector(130, 124, 204), campus_mru(70, 129, 39), campus_trabajo(42.35, 39.88, 2.68), campus_tension(37, 49, 1104)),
    ('Simulacro 3', campus_conversion(46.6, 62.2), campus_vector(136, 140, 273), campus_mru(62, 124, 24), campus_trabajo(48.26, 46.69, 1.76), campus_tension(31, 54, 1145)),
]
# Lo que da el campus en cada simulacro (para verificar las cuentas de arriba)
ESPERADO = [(7.78, 30.96, 113.88, 93.99, 856), (6.57, 39.38, 108.14, 87.10, 726), (6.97, 27.38, 77.50, 58.26, 676)]
for (_, *qs), esp in zip(CAMPUS, ESPERADO):
    for q, e in zip(qs, esp):
        assert abs(q['r'] - e) <= (0.6 if e > 500 else 0.006), (q['en'][:40], q['r'], e)

# Examen de ingreso 2021: las mismas 5 preguntas, con otros enunciados
vol = 5.5 * 10 * 3.9 / 0.305 ** 3
d2 = 3 * 476 / math.sqrt(10)
v84 = 84 / 3.6
fren = v84 * 5 / 2
wtri = 79.10 * 50.8 * cos(5.4)
tb21 = 1055 / (sen(70) - cos(70) / tg(56))
ta21 = tb21 * cos(70) / sen(56)
for x, e in ((vol, 7560.10), (d2, 451.56), (fren, 58.33), (wtri, 4000.45), (tb21, 1488)):
    assert abs(x - e) < (0.6 if 1000 < e < 2000 else 0.02), (x, e)   # 451,56: el campus redondea D1 antes de multiplicar
EXAMEN_2021 = [
    dict(en='Una habitación mide <b>5,5 [m]</b> de largo, <b>10 [m]</b> de ancho y <b>3,9 [m]</b> de alto. ¿Cuál es el <b>volumen</b> en <b>pies cúbicos (pie³)</b>?<br><b>Datos:</b> 1 pie = 0,305 m. Resultado con dos decimales.',
         num=f'V = {R(f(vol))} pie³',
         ex=f'1) Volumen en m³: 5,5 × 10 × 3,9 = 214,5 m³.<br>2) 1 pie³ = (0,305 m)³ = 0,028372625 m³ (¡se eleva al cubo el factor!).<br>3) 214,5 / 0,028372625 = <b>{f(vol)} pie³</b>.', sec='conv'),
    dict(en='Un ciclista viaja una distancia <b>D1</b> hacia el norte y después el triple hacia el oeste (<b>D2</b>). Al final, la distancia en línea recta desde el punto de partida es de <b>476 m</b>. ¿Cuál es la longitud de la segunda etapa, <b>D2</b>?',
         num=f'D2 = {R(f(d2))} m',
         ex=f'Los dos tramos son perpendiculares → Pitágoras: 476² = D1² + (3·D1)² = 10·D1².<br>D1 = 476 / √10 = {f(476 / math.sqrt(10))} m → D2 = 3·D1 = <b>{f(d2)} m</b>.',
         mal='El campus da 451,56 porque redondea D1 a 150,52 antes de multiplicar por 3. Acepta las dos.', sec='vec'),
    dict(en='Al frenar de manera uniforme, un auto de competición que iba a <b>84 [km/h]</b> se detiene en <b>5 [s]</b>. Si la aceleración de frenado es constante, ¿cuál fue la distancia de frenado? Resultado en metros, con dos decimales.',
         num=f'd = {R(f(fren))} m',
         ex=f'MRUV hasta detenerse.<br>1) 84 km/h / 3,6 = {f(v84, 4)} m/s.<br>2) Con aceleración constante, la velocidad media es (v₀ + 0)/2, así que d = (v₀/2)·t = {f(v84 / 2, 4)} × 5 = <b>{f(fren)} m</b>.<br>(También: a = v₀/t = {f(v84 / 5, 3)} m/s² y d = v₀·t − ½·a·t².)', sec='cin'),
    dict(en='Unos perros arrastran un trineo de <b>150 kg</b> un tramo de <b>50,8 m</b> sobre nieve horizontal a velocidad constante. Tiran con una fuerza de <b>79,10 N</b>, a <b>5,4°</b> por encima de la horizontal; la nieve ejerce una fuerza de fricción que la equilibra. ¿Qué trabajo hacen los perros?',
         num=f'W = {R(f(wtri))} J',
         ex=f'W = F · d · cos θ = 79,10 N × 50,8 m × cos 5,4° = <b>{f(wtri)} J</b>.<br>La masa (150 kg) y la fricción no hacen falta: te piden solo el trabajo de la fuerza de los perros.', sec='trab'),
    dict(en='Para el sistema de la figura (la cuerda A va a la pared y la B al techo), determiná el módulo de la tensión en la <b>cuerda B</b>.<br><b>Datos:</b> α = 56° (entre la cuerda A y la pared); θ = 70° (entre la cuerda B y el techo); P = 1055 [N].<br>Usá un sistema de coordenadas con el origen en el punto donde se unen las cuerdas.',
         img='quiz/img/fisica-pared-techo.svg',
         num=f'T<sub>B</sub> = {R(f(tb21, 0))} N &nbsp; (T<sub>A</sub> = {f(ta21, 0)} N)',
         ex=f'Ojo con los ángulos: α se mide desde la pared (vertical) y θ desde el techo (horizontal).<br>A tira hacia la pared y hacia abajo: (−T<sub>A</sub>·sen α ; −T<sub>A</sub>·cos α). B tira hacia el techo: (T<sub>B</sub>·cos θ ; T<sub>B</sub>·sen θ).<br>ΣFx: T<sub>B</sub>·cos θ = T<sub>A</sub>·sen α → T<sub>A</sub> = T<sub>B</sub>·cos θ / sen α.<br>ΣFy: T<sub>B</sub>·sen θ − T<sub>A</sub>·cos α = P → T<sub>B</sub>·(sen θ − cos θ / tg α) = P.<br>T<sub>B</sub> = 1055 / ({f(sen(70), 4)} − {f(cos(70), 4)}/{f(tg(56), 4)}) = <b>{f(tb21, 0)} N</b>.', sec='est'),
]


# ───────────────────────── Exámenes 2011 y 2012 (clave de corrección) ─────────────────────────
def mc(en, ops, bien, ex, fuente, sec):
    return dict(tipo='una', en=en, op=[[o, i == bien] for i, o in enumerate(ops)], ex=ex, fuente=fuente, sec=sec)


def ej(en, num, ex, fuente, sec, mal=None):
    d = dict(tipo='num', en=en, num=num, ex=ex, fuente=fuente, sec=sec)
    if mal: d['mal'] = mal
    return d


F12R = 'Recuperatorio mar. 2012 · Tema '
F12F = 'Final mar. 2012 · Tema '
F11 = 'Final mar. 2011 · Tema '
F11E = 'Recuperatorio especial mar. 2011'

# cuentas de los ejercicios
heli_d, heli_a = math.hypot(120, 75), deg(math.atan2(120, 75))
f4x, f4y = 25 * cos(37), 25 * sen(37)
f5x = 30 * cos(45)
t50 = math.sqrt(50 / 4.9)
atl_v2 = 32 / 3.6
atl_t = 700 / 7 + 300 / atl_v2
atl = 1000 / atl_t
r14x, r14y = 14 * cos(30), 14 * sen(30) + 7
r14, a14 = math.hypot(r14x, r14y), deg(math.atan2(r14y, r14x))
v80 = 80 / 3.6
a1050 = v80 ** 2 / (2 * 75)
r5x, r5y = 5 * cos(150) + 7 * cos(240), 5 * sen(150) + 7 * sen(240)
r5, a5 = math.hypot(r5x, r5y), deg(math.atan2(r5y, r5x)) % 360
a25 = 2 * 25 / 7.5 ** 2
afus = 350 ** 2 / (2 * 0.85)
pozo = 12 * 2 + 0.5 * G * 4
a90 = 25 ** 2 / (2 * 75)
grasa = 5 / 0.454 / 2.15
din_fx, din_fy = 10 * sen(35), 10 * cos(35)
din_f2y = 12 - din_fy
din_f2, din_a = math.hypot(din_fx, din_f2y), deg(math.atan2(din_fx, din_f2y))
pr_t1, pr_t2 = 2 * 50 / G, 2 * 30 / G
a12a, a12b = v80 / 5, v80 ** 2 / (2 * 50)
pint_gal = 3785 / 475.25
aceite = 95.75 / 1.75 * pint_gal
lan_d = 3.7 / math.sqrt(1 + 1 / 16)
tren_a = (54 ** 2 - 33 ** 2) / (2 * 160)
tren_t = (54 - 33) / tren_a
fle_a = 80 ** 2 / (2 * 0.225)
c10x, c10y = 25 * cos(30), 25 * sen(30) - 10
c10r, c10ang = math.hypot(c10x, c10y), deg(math.atan2(c10y, c10x))
c10a = c10r / (10 / G)
puerta = (6 * 12 + 8) * 0.0254
bala = 250 ** 2 / (2 * G)

VIEJAS = [
    # ── Recuperatorio marzo 2012 · Tema 1
    mc('Sabiendo que en 1 pie³ hay 28,32 litros y en 1 galón 3,785 litros, ¿cuántos pie³ hay en 18 galones?',
       ['5,96 pie³', '134,7 pie³', '1,57 pie³', '2,41 pie³'], 3,
       '18 gal × 3,785 L/gal = 68,13 L → 68,13 L / 28,32 L/pie³ = <b>2,41 pie³</b>. Primero a litros (la unidad que comparten) y después a pie³.', F12R + '1', 'conv'),
    mc('Un objeto es arrojado hacia arriba con cierta velocidad (sin resistencia del aire). Una vez que fue soltado, su aceleración:',
       ['Permanece constante', 'Disminuye', 'Aumenta', 'Es cero'], 0,
       'Una vez soltado, la única fuerza es el peso: la aceleración es <b>g, constante</b> (9,8 m/s² hacia abajo) al subir, arriba y al bajar. Lo que cambia es la velocidad.', F12R + '1', 'cin'),
    mc('Un camión cargado choca contra un auto, y los daños del auto son mayores que los del camión. Podemos afirmar que:',
       ['La fuerza que el camión ejerce sobre el auto es mayor que la que el auto ejerce sobre el camión',
        'La fuerza que el camión ejerce sobre el auto es menor que la que el auto ejerce sobre el camión',
        'La fuerza que el camión ejerce sobre el auto es igual a la que el auto ejerce sobre el camión',
        'No se pueden comparar las fuerzas si no se conocen las masas de los vehículos'], 2,
       '<b>Tercera ley de Newton</b> (acción y reacción): las dos fuerzas son <b>iguales</b> y opuestas, siempre. El auto se rompe más porque tiene menos masa (más aceleración, a = F/m) y es más frágil, no porque reciba más fuerza.', F12R + '1', 'din'),
    ej('Un helicóptero vuela 120 km desde su base hacia el norte y, desde ahí, 75,0 km hacia el este. Determiná la magnitud y la dirección del desplazamiento (ejes x hacia el este, y hacia el norte).',
       f'D = {R(f(heli_d, 1))} km &nbsp; α = {R(f(heli_a, 0))}° respecto del este',
       f'Los dos tramos son perpendiculares → Pitágoras: D = √(120² + 75²) = <b>{f(heli_d, 1)} km</b>.<br>Dirección: α = arctg(120/75) = <b>{f(heli_a, 0)}°</b> sobre el eje +x (el este), hacia el norte.', F12R + '1', 'vec'),
    ej('Un bloque de 4,0 kg apoya sobre una superficie lisa. Se le aplica una fuerza de 25 N a 37° por encima de la horizontal. a) ¿Qué aceleración adquiere? b) ¿Se levanta del suelo?',
       f'a) a = {R(f(f4x / 4, 1))} m/s² &nbsp; b) {R("no se levanta")}',
       f'Componentes: Fx = 25·cos 37° = {f(f4x, 1)} N; Fy = 25·sen 37° = {f(f4y, 1)} N.<br>Peso: w = 4,0 × 9,8 = 39,2 N. Como Fy &lt; w, <b>no se levanta</b> (la normal compensa el resto).<br>Sin rozamiento, solo acelera Fx: a = Fx/m = {f(f4x, 1)} / 4,0 = <b>{f(f4x / 4, 1)} m/s²</b> (la clave usa cos 37° ≈ 0,80 y da 5,0).', F12R + '1', 'din'),
    # ── Recuperatorio marzo 2012 · Tema 2
    mc('Para pasar una velocidad de m/s a pie/min, ¿qué hay que hacer? (1 min = 60 s; 1 m = 3,28 pie)',
       ['Multiplicar por 196,8', 'Dividir por 196,8', 'Multiplicar por 0,055', 'Dividir por 0,055'], 0,
       '1 m/s = 3,28 pie / (1/60 min) = 3,28 × 60 pie/min = <b>196,8 pie/min</b>. Se multiplica: el pie es más chico que el metro y el minuto más largo que el segundo, así que el número crece.', F12R + '2', 'conv'),
    mc('Un objeto se arroja verticalmente hacia arriba desde el suelo (sin resistencia del aire). ¿Cuál de estas afirmaciones es válida?',
       ['La altura máxima es independiente de la velocidad inicial', 'El tiempo de ascenso es un poco mayor que el tiempo de descenso',
        'El tiempo de ascenso es igual al tiempo de descenso', 'La aceleración cuando sube es opuesta a la aceleración cuando baja'], 2,
       'Sin aire el movimiento es simétrico: tarda lo mismo en subir que en bajar. La altura máxima sí depende de v₀ (h = v₀²/2g) y la aceleración es siempre g hacia abajo. (En la clave el resaltado tapa el texto de esta opción.)', F12R + '2', 'cin'),
    mc('Un cuerpo está apoyado sobre una mesa. ¿Cuál es la reacción a la fuerza que la mesa ejerce sobre el cuerpo?',
       ['El peso del cuerpo', 'La fuerza que el cuerpo ejerce sobre la mesa', 'La fuerza que el cuerpo ejerce sobre la Tierra', 'La fuerza que la Tierra ejerce sobre la mesa'], 1,
       'Acción y reacción actúan entre <b>los mismos dos cuerpos</b>, con los papeles invertidos: mesa→cuerpo y <b>cuerpo→mesa</b>. El peso no es la reacción de la normal: el peso es Tierra→cuerpo (su reacción es cuerpo→Tierra).', F12R + '2', 'din'),
    ej('Desde la azotea de un edificio de 50 m se deja caer un objeto. ¿Cuánto tarda en llegar al suelo?',
       f't = {R(f(t50, 1))} s',
       f'Caída libre desde el reposo: h = ½·g·t² → t = √(2h/g) = √(50 / 4,9) = <b>{f(t50, 1)} s</b>.', F12R + '2', 'cin'),
    ej('Calculá la aceleración de un bloque de 3,0 kg apoyado en una superficie horizontal lisa, al que se le aplica una fuerza de 30 N a 45° por encima de la horizontal.',
       f'a = {R(f(f5x / 3, 1))} m/s², horizontal',
       f'Fx = Fy = 30·cos 45° = {f(f5x, 1)} N. Peso: 3,0 × 9,8 = 29,4 N &gt; Fy → no se levanta.<br>a = Fx/m = {f(f5x, 1)} / 3,0 = <b>{f(f5x / 3, 1)} m/s²</b>, en la dirección de x.', F12R + '2', 'din'),
    # ── Final marzo 2012 · Tema 3
    mc('Comparada con una botella de gaseosa de 2 litros, una de tres cuartos de galón (1 galón = 3,785 litros) contiene:',
       ['Mayor cantidad', 'La misma cantidad', 'Menos cantidad', 'Depende de la forma del envase'], 0,
       '¾ galón = 0,75 × 3,785 L = <b>2,84 L</b> &gt; 2 L.', F12F + '3', 'conv'),
    mc('¿Qué aceleración tiene un cuerpo lanzado verticalmente hacia arriba, cuando sube, cuando baja y en el punto más alto?',
       ['Es g: cuando sube apunta hacia arriba, cuando cae apunta hacia abajo y en el punto más alto es cero',
        'Es g: cuando sube apunta hacia abajo, cuando cae apunta hacia arriba y en el punto más alto es cero',
        'Es g y apunta siempre hacia abajo: cuando sube, cuando baja y en el punto más alto',
        'Es g: cuando sube y cuando baja apunta hacia abajo, pero en el punto más alto es cero'], 2,
       'La única fuerza es el peso, siempre hacia abajo → la aceleración es <b>g hacia abajo en todo momento</b>, también arriba de todo. Lo que vale cero en el punto más alto es la velocidad, no la aceleración. (En la clave el resaltado tapa esta opción.)', F12F + '3', 'cin'),
    mc('Un cuerpo se desliza con velocidad constante sobre una superficie horizontal sin rozamiento. Esto significa que:',
       ['Ninguna fuerza actúa sobre el cuerpo', 'Actúa una sola fuerza sobre el cuerpo', 'Tres fuerzas actúan sobre el cuerpo', 'La fuerza neta (resultante) sobre el cuerpo es cero'], 3,
       'Velocidad constante → aceleración cero → <b>fuerza neta cero</b> (primera ley). Sí actúan fuerzas: el peso y la normal, que se anulan.', F12F + '3', 'est'),
    ej('Un camionero maneja a 80 km/h sin parar y tiene que completar un viaje de 200 km en 3,5 h. ¿De cuánto tiempo dispone para almorzar?',
       f'{R("1 h")}', 'MRU: t = d/v = 200 km / 80 km/h = 2,5 h de manejo. Le sobran 3,5 h − 2,5 h = <b>1 h</b>.', F12F + '3', 'cin'),
    ej('Una bolsa de 4,5 kg cuelga de una cuerda que tira hacia arriba con 45 N. ¿Hacia dónde se mueve y con qué aceleración?',
       f'a = {R(f((45 - 4.5 * G) / 4.5, 1))} m/s² hacia arriba',
       f'Peso: w = 4,5 × 9,8 = 44,1 N. Segunda ley: a = (T − w)/m = (45 − 44,1)/4,5 = <b>{f((45 - 4.5 * G) / 4.5, 1)} m/s²</b>. Como T &gt; w, la aceleración es <b>hacia arriba</b>.', F12F + '3', 'din'),
    # ── Final marzo 2012 · Tema 1
    mc('¿Cuál de estas es una unidad fundamental del Sistema Internacional de Unidades (SI)?',
       ['El minuto', 'El newton', 'La yarda', 'Ninguna de las anteriores'], 3,
       'Las fundamentales del SI son 7: metro, kilogramo, <b>segundo</b>, ampere, kelvin, mol y candela. El minuto no es del SI, el newton es <b>derivada</b> (kg·m/s²) y la yarda es inglesa.', F12F + '1', 'conv'),
    mc('Que un cuerpo se mueva con aceleración constante de 2 m/s² significa que:',
       ['En cada segundo el móvil se desplaza 2 m', 'En cada segundo la velocidad cambia 2 m/s', 'En cada segundo la aceleración cambia 2 m/s²', 'Cada 2 s la velocidad cambia 1 m/s'], 1,
       'La aceleración es cuánto cambia la velocidad por unidad de tiempo: 2 m/s² = <b>2 (m/s) por cada segundo</b>.', F12F + '1', 'cin'),
    mc('Sobre un cuerpo apoyado en un piso liso se aplica una fuerza horizontal F. ¿Cuántas fuerzas actúan sobre el cuerpo?',
       ['Una', 'Dos', 'Tres', 'Cuatro'], 2,
       'Diagrama de cuerpo libre: el <b>peso</b> (Tierra), la <b>normal</b> (el piso) y <b>F</b>. Son tres; sin rozamiento no hay una cuarta.', F12F + '1', 'est'),
    ej('Un atleta corre 1000 m en línea recta: los primeros 700 m a 7 m/s y los últimos 300 m a 32 km/h. ¿Cuál es la velocidad promedio del recorrido?',
       f'v = {R(f(atl, 2))} m/s',
       f'1) 32 km/h = {f(atl_v2, 2)} m/s.<br>2) Tiempos: 700/7 = 100 s; 300/{f(atl_v2, 2)} = {f(300 / atl_v2, 2)} s → total {f(atl_t, 2)} s.<br>3) v = desplazamiento / tiempo total = 1000 / {f(atl_t, 2)} = <b>{f(atl, 2)} m/s</b>.<br>Ojo: no es el promedio de las dos velocidades.', F12F + '1', 'cin'),
    ej('Una partícula de masa m va a 20 m/s. Una fuerza neta constante de frenado de 20 N la detiene en 50 m. ¿Cuál es la masa?',
       f'm = {R("5 kg")}',
       'MRUV hasta detenerse: 0 − v₀² = −2·a·Δx → a = 20² / (2 × 50) = 4 m/s².<br>Segunda ley: m = F/a = 20 N / 4 m/s² = <b>5 kg</b>.', F12F + '1', 'din'),
    # ── Recuperatorio marzo 2012 · Tema 4
    mc('Una lata de cerveza tiene una pinta. ¿Cuánto es en galones? (1 galón = 3,785 L; 1 pinta = 0,47325 L)',
       ['1,79 galones', '8,00 galones', '4,00 galones', '0,125 galones'], 3,
       '0,47325 L / 3,785 L/gal = <b>0,125 gal</b> (un galón son 8 pintas). (En la clave el resaltado tapa esta opción.)', F12R + '4', 'conv'),
    mc('Dos objetos de distinto tamaño se dejan caer al mismo tiempo desde un edificio. ¿Cuál llega primero al suelo?',
       ['Llega primero el más pesado', 'Llega primero el más liviano', 'Llegan los dos al mismo tiempo', 'Depende de la altura del edificio'], 2,
       'En caída libre (sin aire) todos caen con la misma aceleración g, sin importar la masa: <b>llegan juntos</b>.', F12R + '4', 'cin'),
    mc('El vector de una fuerza tiene módulo 10 N y su componente x vale 6 N. ¿Cuánto vale la componente y?',
       ['Es igual a 8 N', 'Es igual a 4 N', 'Está entre 4 N y 6 N', 'Es mayor que 8 N'], 0,
       'Pitágoras: Fy = √(10² − 6²) = √64 = <b>8 N</b>. No se restan los módulos (10 − 6 = 4 está mal).', F12R + '4', 'vec'),
    ej('Una fuerza F1 de 14,0 N actúa a 30,0° del eje +x y otra, F2 de 7,00 N, a lo largo del eje +y. Encontrá la magnitud y la dirección de la resultante.',
       f'R = {R(f(r14, 1))} N &nbsp; α = {R(f(a14, 1))}°',
       f'F1x = 14·cos 30° = {f(14 * cos(30), 2)} N; F1y = 14·sen 30° = 7,00 N; F2x = 0; F2y = 7,00 N.<br>Rx = {f(r14x, 2)} N; Ry = 14,0 N → R = √(Rx² + Ry²) = <b>{f(r14, 1)} N</b>.<br>α = arctg(Ry/Rx) = <b>{f(a14, 1)}°</b>, en el primer cuadrante.', F12R + '4', 'vec',
       mal='La clave da 49,2° porque redondea Rx a 12,1 antes de dividir; con todos los decimales da 49,1°.'),
    ej('¿Qué fuerza de frenado hace falta para detener de manera uniforme un auto de 1050 kg que va a 80 km/h, en 75 m de camino recto y horizontal?',
       f'F = {R(f(1050 * a1050, 0))} N',
       f'80 km/h = {f(v80, 2)} m/s. a = v₀²/(2·Δx) = {f(v80, 2)}² / 150 = {f(a1050, 2)} m/s².<br>F = m·a = 1050 × {f(a1050, 2)} = <b>{f(1050 * a1050, 0)} N</b>, opuesta al movimiento.', F12R + '4', 'din',
       mal='La clave da 3381 N porque redondea la velocidad a 22 m/s; con 22,22 m/s da 3457 N.'),
    # ── Recuperatorio marzo 2012 · Tema 3
    mc('En un pie hay 12 pulgadas y en una yarda 3 pies. ¿Cuántas pulgadas hay en 5 yardas?',
       ['20 pulgadas', '7,2 pulgadas', '180 pulgadas', '80 pulgadas'], 2,
       '5 yd × 3 pie/yd × 12 pulg/pie = <b>180 pulgadas</b>.', F12R + '3', 'conv'),
    mc('La aceleración de un vehículo es nula cuando:',
       ['Gira hacia la derecha con rapidez constante', 'Sube por una carretera recta con pendiente, con rapidez constante',
        'Baja por una carretera recta con pendiente, aumentando su rapidez', 'Arranca desde el reposo'], 1,
       'Aceleración nula = la velocidad (vector) no cambia: <b>línea recta y rapidez constante</b>. Al girar cambia la dirección, así que hay aceleración aunque la rapidez sea constante. (En la clave el resaltado tapa esta opción.)', F12R + '3', 'cin'),
    mc('Una fuerza F empuja al bloque de masa m2, que a su vez empuja al bloque de masa m1 (m2 &gt; m1), y los dos aceleran juntos sobre un piso liso. ¿Cuánto vale la fuerza que acelera al bloque m1?',
       ['Es la fuerza F', 'Es mayor que F', 'Es menor que F', 'Es imposible de determinar'], 2,
       'Los dos aceleran juntos con a = F/(m1 + m2). Sobre m1 actúa solo el empuje de m2: m1·a = F·m1/(m1 + m2), que es <b>menor que F</b>.', F12R + '3', 'din'),
    ej('Dos fuerzas F1 y F2, de 5,0 N y 7,0 N, forman ángulos de 150° y 240° con el eje +x. ¿Cuál es la magnitud y la dirección de la resultante?',
       f'R = {R(f(r5, 1))} N &nbsp; α ≈ {R(f(a5, 0))}°',
       f'F1x = 5·cos 150° = {f(5 * cos(150), 2)}; F1y = 5·sen 150° = {f(5 * sen(150), 2)}.<br>F2x = 7·cos 240° = {f(7 * cos(240), 2)}; F2y = 7·sen 240° = {f(7 * sen(240), 2)}.<br>Rx = {f(r5x, 2)} N; Ry = {f(r5y, 2)} N → R = <b>{f(r5, 1)} N</b>.<br>Las dos componentes son negativas → <b>tercer cuadrante</b>: α = arctg(Ry/Rx) + 180° = <b>{f(a5, 0)}°</b>. La calculadora da {f(deg(math.atan(r5y / r5x)), 0)}°: hay que sumarle 180°.', F12R + '3', 'vec'),
    ej('Una fuerza neta de 15 N actúa de forma constante sobre un objeto que parte del reposo y recorre 25 m en línea recta en 7,5 s. ¿Cuál es la masa?',
       f'm = {R(f(15 / a25, 0))} kg',
       f'Desde el reposo: x = ½·a·t² → a = 2x/t² = 50/7,5² = {f(a25, 2)} m/s².<br>m = F/a = 15 / {f(a25, 3)} = <b>{f(15 / a25, 1)} kg ≈ 17 kg</b>.', F12R + '3', 'din'),
    # ── Final marzo 2012 · Tema 2
    mc('¿Cuál es la unidad de fuerza en el Sistema Internacional de Unidades?',
       ['El kilogramo', 'La dina', 'La onza', 'El newton'], 3,
       'El <b>newton</b>: 1 N = 1 kg·m/s². El kilogramo es de masa y la dina es del sistema cgs.', F12F + '2', 'conv'),
    mc('Un objeto se arroja verticalmente hacia arriba desde el suelo, llega a una altura máxima y vuelve al punto de partida. ¿Cuál es la correcta?',
       ['Cuando sube, g tiene un sentido y cuando cae cambia de sentido', 'Al llegar al punto más alto, la aceleración se anula un instante',
        'Al llegar al punto más alto, la velocidad se anula un instante', 'Justo antes de tocar el suelo tiene la misma velocidad con que fue arrojado'], 2,
       'Arriba de todo la <b>velocidad</b> es cero un instante; la aceleración sigue siendo g. La d) es trampa: tiene la misma rapidez, pero la <b>velocidad</b> (vector) apunta al revés.', F12F + '2', 'cin'),
    mc('El bloque m2 está apoyado en el piso, contra una pared. Una fuerza horizontal F empuja al bloque m1 contra m2. ¿Cuántas fuerzas actúan sobre m2?',
       ['Una', 'Dos', 'Tres', 'Cuatro'], 3,
       'Sobre m2: el <b>peso</b>, la <b>normal del piso</b>, el <b>empuje de m1</b> y la <b>reacción de la pared</b>. Cuatro. F no actúa sobre m2: actúa sobre m1.', F12F + '2', 'est'),
    ej('Un vehículo va en línea recta a 55 millas/h durante 1,5 h y después a 40 millas/h durante 30 minutos, en el mismo sentido. ¿Cuál es la velocidad promedio del recorrido total? (En millas/h.)',
       f'v = {R("51,25")} millas/h',
       'Desplazamientos: 55 × 1,5 = 82,5 mi; 40 × 0,5 = 20 mi → total 102,5 mi.<br>Tiempo total: 1,5 h + 0,5 h = 2 h. v = 102,5 / 2 = <b>51,25 mi/h</b>.', F12F + '2', 'cin'),
    ej('El cañón de un fusil mide 0,85 m y dispara un proyectil de 22,0 g que sale a 350 m/s, con aceleración uniforme dentro del cañón. ¿Qué fuerza actúa sobre el proyectil?',
       f'F = {R(f(0.022 * afus, 0))} N',
       f'Parte del reposo: v² = 2·a·Δx → a = 350² / (2 × 0,85) = {f(afus, 0)} m/s².<br>F = m·a = 0,022 kg × {f(afus, 0)} = <b>{f(0.022 * afus, 0)} N</b> (pasá los gramos a kg).', F12F + '2', 'din'),
    # ── Final marzo 2012 · Tema 4
    mc('Comparando 7 barriles de petróleo con un metro cúbico, ¿cuál tiene mayor volumen? (1 barril = 42,0 galones; 1 galón = 3,785 litros; 1 m³ = 1000 litros)',
       ['El metro cúbico tiene mayor volumen que los siete barriles', 'Los siete barriles tienen mayor volumen que el metro cúbico', 'Tienen el mismo volumen', 'No se puede determinar con estos datos'], 1,
       f'7 × 42,0 × 3,785 = <b>{f(7 * 42 * 3.785, 0)} L</b> &gt; 1000 L. (En la clave el resaltado tapa esta opción.)', F12F + '4', 'conv'),
    mc('Un ciclista da 10 vueltas completas en un velódromo, una pista circular de radio R = 25 m. ¿Cuál es su desplazamiento?',
       ['1571 m', '785 m', '250 m', 'Cero'], 3,
       'El desplazamiento va del punto de partida al de llegada: termina donde empezó → <b>cero</b>. 1571 m (10 × 2π × 25) es la <b>distancia recorrida</b>.', F12F + '4', 'vec'),
    mc('Sobre un bloque de peso W apoyado en el piso se aplica una fuerza F que empuja hacia abajo y forma un ángulo θ con la vertical. ¿Cuánto vale la normal N?',
       ['N = W', 'N = W + F', 'N = W + F·cos θ', 'N = W + F·sen θ'], 2,
       'En vertical hay equilibrio: N = W + (componente vertical de F). Como θ se mide desde la <b>vertical</b>, esa componente es <b>F·cos θ</b>. Si el ángulo fuera con la horizontal, sería F·sen θ.', F12F + '4', 'est'),
    ej('Desde la boca de un pozo se arroja una piedra verticalmente hacia abajo a 12 m/s. Llega al agua 2 s después. ¿Cuál es la profundidad del pozo hasta el agua?',
       f'h = {R(f(pozo, 1))} m',
       f'Eje hacia abajo, origen en la boca: y = v₀·t + ½·g·t² = 12 × 2 + 4,9 × 2² = 24 + 19,6 = <b>{f(pozo, 1)} m</b>.', F12F + '4', 'cin'),
    ej('Un auto de 1000 kg va a 90 km/h por una carretera recta y horizontal. ¿Qué fuerza de frenado hace falta para que se detenga uniformemente en 75,0 m?',
       f'F = {R(f(1000 * a90, 0))} N',
       f'90 km/h = 25 m/s. a = 25² / (2 × 75) = {f(a90, 2)} m/s².<br>F = 1000 × {f(a90, 3)} = <b>{f(1000 * a90, 0)} N</b>, contraria al movimiento.', F12F + '4', 'din',
       mal='La clave da 4200 N porque redondea la aceleración a 4,2 m/s²; con 4,167 da 4167 N.'),
    # ── Final marzo 2011 · Tema 2
    mc('Hacé la operación π / (4,56 × 10⁻³), redondeando al número correcto de cifras significativas. El resultado es:',
       ['688,945757…', '688,95', '688', '689'], 3,
       'Al dividir, el resultado lleva tantas cifras significativas como el dato que tiene menos: 4,56 tiene <b>3</b>. π/0,00456 = 688,95… → <b>689</b>.', F11 + '2', 'conv'),
    mc('En la ecuación x = C₁·cos(C₂·t), x está en metros y t en segundos. ¿Cuáles son las unidades en el SI de C₁ y C₂?',
       ['C₁ en m/s y C₂ adimensional', 'C₁ en m y C₂ en s⁻¹', 'No puede estar el tiempo dentro del coseno: la fórmula está mal', 'Para saberlo hay que conocer los valores de C₁ y C₂'], 1,
       'Lo que va dentro del coseno es un ángulo: no tiene unidades → C₂·t adimensional → <b>C₂ en 1/s</b>. El coseno tampoco tiene unidades → C₁ lleva las de x: <b>metros</b>.', F11 + '2', 'conv'),
    mc('Del techo de un edificio se suelta una esfera A; 2 s después se suelta otra esfera B. Mientras caen, la distancia que las separa:',
       ['Permanece constante', 'Disminuye', 'Va en aumento', 'Faltan datos'], 2,
       'Las dos aceleran igual, pero A ya tiene 2 s de ventaja y va siempre <b>más rápido</b> (19,6 m/s más). Por eso la distancia entre las dos <b>crece</b>.', F11 + '2', 'cin'),
    mc('El peso de un cuerpo en la Luna es:',
       ['Cero, porque en la Luna no hay gravedad', 'Igual que en la Tierra', 'Mayor que en la Tierra', 'Menor que en la Tierra'], 3,
       'P = m·g y la gravedad de la Luna es ~1/6 de la terrestre: el peso es <b>menor</b>. La masa sí es la misma.', F11 + '2', 'din'),
    mc('Un bloque de 8 N cuelga del techo con una cuerda (T₁) y de él cuelga, con otra cuerda (T₂), un bloque de 2 N. ¿Cuánto valen T₁ y T₂?',
       ['8 N y 2 N', '8 N y 8 N', '10 N y 2 N', '10 N y 10 N'], 2,
       'T₂ sostiene solo el bloque de abajo: <b>2 N</b>. T₁ sostiene los dos: 8 + 2 = <b>10 N</b>.', F11 + '2', 'est'),
    ej('Un taller necesita 5,00 kgf de una grasa especial que se vende en envases de 2,15 libras. ¿Cuántos envases tiene que comprar? (1 libra = 0,454 kgf)',
       f'{R("6 envases")}',
       f'5,00 kgf / 0,454 kgf/lb = {f(5 / 0.454, 1)} lb → {f(5 / 0.454, 1)} / 2,15 = {f(grasa, 2)} envases. Con 5 no alcanza: hay que comprar <b>6</b>.', F11 + '2', 'conv'),
    ej('Un peso de 12,0 N cuelga de dos dinamómetros. Uno marca 10,0 N y está inclinado 35,0° respecto de la vertical. ¿Cuánto marca el otro y qué ángulo α forma con la vertical?',
       f'F₂ = {R(f(din_f2, 2))} N &nbsp; α = {R(f(din_a, 1))}°',
       f'Equilibrio. Ojo: los ángulos se miden desde la <b>vertical</b> (eje y), así que la x lleva seno y la y, coseno.<br>F1x = 10·sen 35° = {f(din_fx, 2)} N; F1y = 10·cos 35° = {f(din_fy, 2)} N.<br>ΣFx = 0 → F2x = {f(din_fx, 2)} N. ΣFy = 0 → F2y = 12,0 − {f(din_fy, 2)} = {f(din_f2y, 2)} N.<br>F₂ = √(F2x² + F2y²) = <b>{f(din_f2, 2)} N</b>; α = arctg(F2x/F2y) = <b>{f(din_a, 1)}°</b>.', F11 + '2', 'est'),
    ej('Un auto arranca con aceleración constante y a los 10,0 s va a 108 km/h. Desde ahí frena, con una desaceleración de 10,0 m/s², hasta detenerse. Calculá el tiempo total y la distancia recorrida desde que arranca hasta que se detiene.',
       f't = {R("13,0")} s &nbsp; Δx = {R("195")} m',
       '108 km/h = 30,0 m/s.<br>Etapa 1: a = 30/10 = 3,00 m/s²; Δx₁ = ½ × 3 × 10² = 150 m.<br>Etapa 2: t₂ = 30/10 = 3,00 s; Δx₂ = 30²/(2 × 10) = 45,0 m.<br>Total: t = 10 + 3 = <b>13,0 s</b>; Δx = 150 + 45 = <b>195 m</b>.', F11 + '2', 'cin'),
    ej('Dos proyectiles se lanzan verticalmente hacia arriba, el primero a 50 m/s y el segundo a 30 m/s. ¿Cuánto tiempo después del primero hay que lanzar el segundo para que lleguen juntos al suelo?',
       f'Δt = {R(f(pr_t1 - pr_t2, 1))} s',
       f'Tiempo de vuelo = 2 × tiempo de subida = 2·v₀/g.<br>Primero: 2 × 50/9,8 = {f(pr_t1, 2)} s. Segundo: 2 × 30/9,8 = {f(pr_t2, 2)} s.<br>Δt = {f(pr_t1, 2)} − {f(pr_t2, 2)} = {f(pr_t1 - pr_t2, 2)} s ≈ <b>{f(pr_t1 - pr_t2, 1)} s</b>.', F11 + '2', 'cin'),
    ej('Un auto de 1200 kg va a 80 km/h por una carretera horizontal y frena uniformemente hasta detenerse. ¿Cuánto vale la fuerza de frenado si se detiene a) en 5,0 s; b) en 50 m?',
       f'a) F = {R(f(1200 * a12a, 0))} N &nbsp; b) F = {R(f(1200 * a12b, 0))} N',
       f'80 km/h = {f(v80, 2)} m/s.<br>a) a = v₀/t = {f(v80, 2)}/5 = {f(a12a, 2)} m/s² → F = 1200 × {f(a12a, 3)} = <b>{f(1200 * a12a, 0)} N</b>.<br>b) a = v₀²/(2·Δx) = {f(a12b, 2)} m/s² → F = <b>{f(1200 * a12b, 0)} N</b>.<br>La fuerza va contraria al movimiento.', F11 + '2', 'din',
       mal='La clave redondea las aceleraciones a 4,4 y 4,9 m/s² y da 5280 N y 5880 N (≈ 5,3 × 10³ y 5,9 × 10³ N).'),
    # ── Final marzo 2011 · Tema 1
    mc('Hacé la operación (0,000000513) × (62,30 × 10⁷), redondeando al número correcto de cifras significativas. El resultado es:',
       ['319,599', '320', '319,6', '320,0'], 1,
       'En una multiplicación manda el dato con menos cifras significativas: 0,000000513 tiene <b>3</b> (los ceros de adelante no cuentan). 319,599 → <b>320</b>.', F11 + '1', 'conv'),
    mc('En la ecuación v² = C₁·x·e^(−C₂·t), x está en metros, t en segundos y v en m/s. ¿Cuáles son las unidades en el SI de C₁ y C₂?',
       ['C₁ en m/s² y C₂ adimensional', 'C₁ en m/s y C₂ adimensional', 'C₁ en m/s² y C₂ en s⁻¹', 'La fórmula está mal: no puede haber tiempo en el exponente'], 2,
       'El exponente no tiene unidades → C₂·t adimensional → <b>C₂ en 1/s</b>.<br>Del resto: m²/s² = C₁·m → <b>C₁ en m/s²</b>.', F11 + '1', 'conv'),
    mc('Desde lo alto de un edificio se arroja un cuerpo A hacia arriba con rapidez v₀ y otro B hacia abajo con la misma rapidez. A tiene el doble de masa que B. Justo antes de tocar el suelo:',
       ['A y B llegan con la misma rapidez', 'A llega con mayor rapidez que B', 'B llega con mayor rapidez que A', 'Para compararlas hay que conocer la altura'], 0,
       'A sube y vuelve a pasar por la altura de partida con rapidez v₀ hacia abajo: desde ahí hace lo mismo que B. La masa no influye en la caída. Llegan con la <b>misma rapidez</b> (A, más tarde).', F11 + '1', 'cin'),
    mc('Un bloque se desliza sobre una superficie horizontal rugosa con velocidad constante. La fuerza neta que actúa sobre él es:',
       ['Nula', 'Constante', 'Igual a la de rozamiento', 'Variable'], 0,
       'Velocidad constante → aceleración cero → <b>fuerza neta nula</b>: lo que lo empuja compensa exactamente al rozamiento.', F11 + '1', 'est'),
    mc('Un peso de 25 N cuelga de una polea móvil, sostenida por dos tramos verticales de la misma cuerda (los dos con tensión T). ¿Cuánto vale T?',
       ['25 N', '12,5 N', '50 N', '0'], 1,
       'Equilibrio: los dos tramos sostienen el peso entre los dos: 2T = 25 N → <b>T = 12,5 N</b>.', F11 + '1', 'est'),
    ej('Un aceite se vende en latas de 1,75 pintas a $95,75 la lata. ¿Cuánto cuesta un galón? (1 pinta = 475,25 cm³; 1 galón = 3,785 litros)',
       f'$ {R(f(aceite, 2))}',
       f'1 galón = 3785 cm³ → 3785 / 475,25 = {f(pint_gal, 3)} pintas.<br>Precio por pinta: 95,75 / 1,75 = $ {f(95.75 / 1.75, 2)}.<br>Galón: {f(95.75 / 1.75, 4)} × {f(pint_gal, 4)} = <b>$ {f(aceite, 2)}</b>.', F11 + '1', 'conv',
       mal='La clave da $435,71 porque redondea antes de multiplicar; con todos los decimales da $435,76.'),
    ej('Una lancha navega hacia el norte una distancia d y después gira al este y recorre la cuarta parte de esa distancia. En línea recta queda a 3,7 km del punto de partida. Calculá cada tramo y el ángulo del desplazamiento total respecto del norte.',
       f'norte: {R(f(lan_d, 1))} km &nbsp; este: {R(f(lan_d / 4, 2))} km &nbsp; ángulo: {R(f(deg(math.atan(0.25)), 0))}°',
       f'Pitágoras: 3,7 = √(d² + (d/4)²) = d·√(1 + 1/16) = d × 1,031 → d = <b>{f(lan_d, 2)} km ≈ 3,6 km</b> (norte).<br>Este: d/4 = <b>{f(lan_d / 4, 2)} km</b>.<br>Respecto del norte: α = arctg((d/4)/d) = arctg 0,25 = <b>{f(deg(math.atan(0.25)), 0)}°</b>.', F11 + '1', 'vec'),
    ej('Un tren acelera de manera constante. En un momento va a 33,0 m/s y 160 m más adelante va a 54,0 m/s. Calculá a) la aceleración; b) el tiempo que tarda en recorrer esos 160 m.',
       f'a) a = {R(f(tren_a, 2))} m/s² &nbsp; b) t = {R(f(tren_t, 2))} s',
       f'a) v² − v₀² = 2·a·Δx → a = (54² − 33²)/(2 × 160) = <b>{f(tren_a, 2)} m/s²</b>.<br>b) t = (v − v₀)/a = 21 / {f(tren_a, 3)} = <b>{f(tren_t, 2)} s</b> (la clave llega al mismo número con la cuadrática de Δx = v₀·t + ½·a·t²).', F11 + '1', 'cin'),
    ej('Una flecha disparada hacia arriba vuelve y golpea el suelo a 80,0 m/s, y se entierra 225 mm hasta frenarse. Calculá a) la aceleración (constante) que la frena; b) el tiempo que tarda en detenerse.',
       f'a) a = {R(f(fle_a / 1e4, 2) + " × 10⁴")} m/s² &nbsp; b) t = {R(f(80 / fle_a * 1e3, 2) + " × 10⁻³")} s',
       f'a) Pasá 225 mm a 0,225 m. a = v₀²/(2·Δx) = 80² / 0,45 = <b>{f(fle_a, 0)} m/s²</b>, hacia arriba (contraria a la velocidad).<br>b) t = v₀/a = 80 / {f(fle_a, 0)} = <b>{f(80 / fle_a * 1e3, 2)} ms</b>.', F11 + '1', 'cin'),
    ej('Sobre un cuerpo de 10,0 N de peso, que no está apoyado en ninguna superficie, actúa una fuerza de 25,0 N a 30,0° sobre la horizontal. Determiná la magnitud y la dirección de la aceleración.',
       f'a = {R(f(c10a, 1))} m/s² &nbsp; a {R(f(c10ang, 2))}° sobre la horizontal',
       f'Fx = 25·cos 30° = {f(c10x, 1)} N; Fy = 25·sen 30° − 10 (el peso) = {f(c10y, 1)} N.<br>Resultante: R = √(Fx² + Fy²) = {f(c10r, 1)} N, a arctg(2,5/21,65) = {f(c10ang, 2)}°.<br>Masa: m = P/g = 10/9,8 = {f(10 / G, 2)} kg → a = R/m = <b>{f(c10a, 1)} m/s²</b>, en la dirección de la resultante.', F11 + '1', 'din'),
    # ── Recuperatorio especial marzo 2011
    mc('El número 0,00570 cm corresponde a una cantidad medida. ¿Cuántas cifras significativas tiene?',
       ['Tres', 'Cuatro', 'Cinco', 'Seis'], 0,
       'Los ceros de adelante no cuentan (solo ubican la coma); el cero del final sí: <b>5, 7 y 0 → tres</b>.', F11E, 'conv'),
    mc('En la expresión F = k·x, con F una fuerza y x un desplazamiento, la unidad de la constante k es:',
       ['k es adimensional', 'k se mide en metros', 'k se mide en newton', 'k se mide en newton/metro'], 3,
       'k = F/x → <b>N/m</b>. (Es la constante del resorte, ley de Hooke.)', F11E, 'conv'),
    mc('Una pelota se arroja verticalmente hacia arriba con velocidad v₀. Cuando llega al punto más alto:',
       ['La velocidad es nula', 'La aceleración de la gravedad es nula', 'La fuerza neta sobre la pelota es nula', 'Son correctas b) y c)'], 0,
       'Arriba de todo la <b>velocidad es cero</b>; g y el peso siguen ahí (si no, no volvería a bajar).', F11E, 'cin'),
    mc('Dos vehículos van a la misma velocidad y frenan con aceleración constante. La distancia de frenado de A es el doble que la de B. Sus aceleraciones de frenado son:',
       ['Iguales', 'La de A es la mitad de la de B', 'La de A es el doble de la de B', 'La de A es un cuarto de la de B'], 1,
       'Hasta detenerse: d = v₀²/(2a) → con el mismo v₀, d y a son inversamente proporcionales. Doble distancia → <b>la mitad de aceleración</b>.', F11E, 'cin'),
    mc('Un cuerpo de masa m cae en caída libre. ¿Qué fuerza actúa sobre él mientras cae?',
       ['Ninguna', 'El peso del cuerpo', 'El peso del cuerpo y su reacción', 'El peso del cuerpo y la normal'], 1,
       'En caída libre solo actúa el <b>peso</b>. Su reacción existe, pero actúa sobre la Tierra, no sobre el cuerpo; y no hay normal porque no está apoyado.', F11E, 'din'),
    ej('El marco de una puerta mide 6 pies y 8 pulgadas. Expresá esa altura en metros. (1 pie = 12 pulgadas; 1 pulgada = 2,54 cm)',
       f'h = {R(f(puerta, 2))} m',
       f'6 pies × 12 = 72 pulg; + 8 = 80 pulgadas.<br>80 × 0,0254 m = <b>{f(puerta, 2)} m</b>.', F11E, 'conv'),
    ej('Un vehículo va a v₀ = 5,0 m/s y acelera de manera uniforme con a = 2,0 m/s². ¿Qué distancia recorre hasta llegar a 15 m/s?',
       f'x = {R("50")} m',
       'Sin tiempo como dato, usás v² − v₀² = 2·a·x → x = (15² − 5²)/(2 × 2) = (225 − 25)/4 = <b>50 m</b>.', F11E, 'cin'),
    ej('Un rifle dispara una bala verticalmente hacia arriba a 250,0 m/s. ¿Qué altura máxima alcanza la bala?',
       f'h = {R(f(bala, 1))} m ≈ 3,19 × 10³ m',
       f'Arriba de todo v = 0: h = v₀²/(2g) = 250² / 19,6 = <b>{f(bala, 1)} m</b> (con tres cifras significativas, 3,19 × 10³ m).', F11E, 'cin'),
    ej('Un remolcador arrastra un buque con una fuerza constante de 2500,0 N. La velocidad del buque aumenta 1,00 m/s en 10,0 s. ¿Cuál es la masa del buque?',
       f'm = {R("2,50 × 10⁴")} kg',
       'a = Δv/Δt = 1,00/10,0 = 0,100 m/s². m = F/a = 2500 / 0,100 = <b>25 000 kg</b> = 2,50 × 10⁴ kg.', F11E, 'din'),
]

SECCIONES = [
    ('conv', 'Conversión de unidades'),
    ('vec', 'Vectores'),
    ('est', 'Estática'),
    ('cin', 'Cinemática'),
    ('din', 'Dinámica (leyes de Newton)'),
    ('trab', 'Trabajo mecánico'),
]
SEC_CAMPUS = ['conv', 'vec', 'cin', 'trab', 'est']   # el orden de las 5 preguntas del campus

GLOSARIO = [
    dict(t='Factor de conversión', que='Una fracción que vale 1, con la misma cantidad en dos unidades (ej.: 1609 m / 1 milla). Se multiplica las veces que haga falta, cancelando unidades hasta llegar a la que piden. Si la unidad está al cuadrado o al cubo, el factor también.', re=r'pasó de|Expres|expres|¿Cuánto es en|¿cuántos|¿Cuántas|equivalen|1 milla|1 pie|1 galón|1 pinta|1 libra|1 barril|Pasar|pasar una', i=False),
    dict(t='Unidades inglesas de longitud', que='1 pulgada = 2,54 cm; 1 pie = 12 pulgadas = 0,305 m; 1 yarda = 3 pies; 1 milla = 1,609 km.', re=r'milla|pie|pulgada|yarda', i=True),
    dict(t='Unidades de volumen', que='1 m³ = 1000 litros; 1 galón = 3,785 litros; 1 pinta = 0,473 litros (1 galón = 8 pintas); 1 barril de petróleo = 42 galones.', re=r'gal[oó]n|pinta|barril|litro|cúbic', i=True),
    dict(t='Kilogramo fuerza (kgf) y libra', sig='kgf', que='El kgf es el peso de 1 kg en la Tierra: 1 kgf = 9,8 N. La libra (lb) inglesa equivale a 0,454 kgf.', re=r'kgf|libra', i=True),
    dict(t='Pasar km/h a m/s', que='Se divide por 3,6 (1 km/h = 1000 m / 3600 s). Al revés, de m/s a km/h, se multiplica por 3,6.', re=r'km/h', i=False),
    dict(t='Cifras significativas', que='Las cifras que se midieron de verdad. Los ceros de adelante no cuentan (0,00570 tiene 3); los de atrás, después de la coma, sí. Al multiplicar o dividir, el resultado lleva tantas como el dato que tiene menos.', re=r'cifras significativas', i=True),
    dict(t='Sistema Internacional', sig='SI', que='El sistema de unidades que se usa en física. Fundamentales: metro (m), kilogramo (kg), segundo (s), ampere, kelvin, mol y candela. Las demás son derivadas: el newton (N = kg·m/s²), el joule (J = N·m)…', re=r'Sistema Internacional|\bSI\b', i=False),
    dict(t='Análisis dimensional', que='Los dos lados de una ecuación tienen que tener las mismas unidades. Lo que va dentro de un coseno, un seno o un exponente no tiene unidades (es un número puro).', re=r'unidades en el SI|la unidad de la constante|cos\(C|e\^', i=False),
    dict(t='Vector y sus componentes', que='Una magnitud con módulo, dirección y sentido. Con el ángulo θ medido desde el eje +x: componente x = módulo·cos θ; componente y = módulo·sen θ. Si el ángulo se mide desde el eje y, se invierten: x con seno, y con coseno.', re=r'vector|componente|rumbo|respecto del este|del eje \+x|eje \+y', i=True),
    dict(t='Módulo (Pitágoras)', que='El largo del vector: √(x² + y²). Sirve para sumar dos tramos perpendiculares (norte y este, por ejemplo).', re=r'magnitud|módulo|línea recta|Pitágoras|distancia en línea', i=True),
    dict(t='Dirección (ángulo)', que='α = arctg(y/x). La calculadora devuelve un ángulo entre −90° y 90°: si x es negativa, hay que sumarle 180° (segundo o tercer cuadrante).', re=r'dirección|ángulo', i=True),
    dict(t='Desplazamiento y distancia recorrida', que='El desplazamiento es el vector que va del punto de partida al de llegada (si volvés al mismo lugar, es cero). La distancia recorrida es todo el camino hecho.', re=r'desplazamiento|vueltas', i=True),
    dict(t='Movimiento rectilíneo uniforme', sig='MRU', que='En línea recta a velocidad constante: d = v·t. No hay aceleración.', re=r'velocidad constante|sin detenerse|sin parar|a 7 m/s|millas/h durante', i=True),
    dict(t='Velocidad promedio (media)', que='Desplazamiento total dividido el tiempo total. No es el promedio de las velocidades: el tramo en el que estás más tiempo pesa más.', re=r'promedio', i=True),
    dict(t='Movimiento uniformemente variado', sig='MRUV', que='Aceleración constante. v = v₀ + a·t; x = v₀·t + ½·a·t²; v² − v₀² = 2·a·x. Para frenar hasta detenerse, v = 0.', re=r'aceleraci|frena|acelera|arranca|desacelera|detenerse|se detiene|se entierra', i=True),
    dict(t='Caída libre y tiro vertical', que='Solo actúa el peso: la aceleración es g = 9,8 m/s² hacia abajo todo el tiempo (también en el punto más alto, donde la velocidad es cero). Subida y bajada son simétricas.', re=r'caída libre|caer|cae |caen|arroja|lanza|verticalmente|altura máxima|se suelta|se dej[ae]', i=True),
    dict(t='Peso', que='La fuerza con que la Tierra atrae a un cuerpo: P = m·g (g = 9,8 m/s²). Se mide en newton; la masa, en kg. En la Luna, g es ~1/6.', re=r'peso|pesado', i=True),
    dict(t='Normal', sig='N', que='La fuerza que hace una superficie sobre lo que está apoyado, perpendicular a ella. No siempre es igual al peso: si empujás hacia abajo o tirás hacia arriba, cambia.', re=r'normal|apoya|piso|mesa|superficie', i=True),
    dict(t='Tensión', sig='T', que='La fuerza que hace una cuerda, siempre tirando, a lo largo de la cuerda. En una cuerda ideal es la misma en toda su longitud.', re=r'tensi[oó]n|cuerda|dinamómetro|polea', i=True),
    dict(t='Diagrama de cuerpo libre', sig='DCL', que='El dibujo de un solo cuerpo con todas las fuerzas que actúan sobre él (peso, normal, tensiones, rozamiento, empujes). Las que el cuerpo hace sobre otros no van.', re=r'fuerzas actúan|fuerza actúa|Cuántas fuerzas', i=True),
    dict(t='Equilibrio', que='Fuerza neta cero: ΣFx = 0 y ΣFy = 0. Pasa en reposo y también a velocidad constante.', re=r'equilibr|figura|cuelga|sostenid', i=True),
    dict(t='Segunda ley de Newton', que='F neta = m·a. La aceleración tiene la dirección de la fuerza neta.', re=r'masa|aceleración|fuerza de frenado|fuerza neta', i=True),
    dict(t='Acción y reacción (tercera ley)', que='Si A empuja a B, B empuja a A con una fuerza igual y opuesta. Actúan sobre cuerpos distintos, por eso no se anulan entre sí.', re=r'reacción|ejerce sobre|choca', i=True),
    dict(t='Fuerza neta (resultante)', que='La suma vectorial de todas las fuerzas sobre el cuerpo. Si es cero, el cuerpo está en reposo o a velocidad constante.', re=r'neta|resultante', i=True),
    dict(t='Rozamiento', que='La fuerza del piso que se opone al deslizamiento. "Liso" o "sin rozamiento" quiere decir que no hay; "rugoso", que sí.', re=r'rozamiento|fricción|lis[oa]|rugosa', i=True),
    dict(t='Trabajo mecánico', sig='W', que='W = F·d·cos θ, con θ el ángulo entre la fuerza y el desplazamiento. Se mide en joules (J = N·m). Una fuerza perpendicular al movimiento no hace trabajo.', re=r'trabajo|joule', i=True),
]


# ───────────────────────── Figuras (SVG) ─────────────────────────
def svg_cuerdas_techo():
    # Techo, dos cuerdas (A a la izquierda con α, B a la derecha con θ) y el peso P colgando del nudo
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 250" width="360" height="250" font-family="Arial, sans-serif">
<rect width="360" height="250" fill="#fff"/>
<line x1="30" y1="40" x2="330" y2="40" stroke="#222" stroke-width="3"/>
<g stroke="#999" stroke-width="1.2">''' + ''.join(f'<line x1="{x}" y1="40" x2="{x + 10}" y2="30"/>' for x in range(34, 330, 14)) + '''</g>
<line x1="70" y1="40" x2="215" y2="128" stroke="#555" stroke-width="2.4"/>
<line x1="295" y1="40" x2="215" y2="128" stroke="#555" stroke-width="2.4"/>
<line x1="215" y1="128" x2="215" y2="168" stroke="#555" stroke-width="2.4"/>
<circle cx="70" cy="40" r="5" fill="#111"/><circle cx="295" cy="40" r="5" fill="#111"/><circle cx="215" cy="128" r="5" fill="#111"/>
<path d="M 108 40 A 38 38 0 0 1 102.5 59.5" fill="none" stroke="#1f6fb2" stroke-width="2"/>
<text x="113" y="62" font-size="18" font-style="italic" fill="#1f6fb2">α</text>
<path d="M 265 40 A 30 30 0 0 0 275 62.5" fill="none" stroke="#1f6fb2" stroke-width="2"/>
<text x="246" y="66" font-size="18" font-style="italic" fill="#1f6fb2">θ</text>
<text x="128" y="104" font-size="18" font-style="italic">A</text>
<text x="263" y="104" font-size="18" font-style="italic">B</text>
<rect x="188" y="168" width="54" height="40" fill="#4a86c8" stroke="#2b5d94" stroke-width="2"/>
<line x1="215" y1="182" x2="215" y2="232" stroke="#1d9a4b" stroke-width="4"/>
<path d="M 207 224 L 215 240 L 223 224 Z" fill="#1d9a4b"/>
<text x="227" y="238" font-size="18" font-style="italic">P</text>
</svg>
'''


def svg_pared_techo():
    # Pared a la izquierda y techo arriba. A va de la pared (abajo) al nudo, con α medido desde la pared;
    # B va del nudo al techo, con θ medido desde el techo. P cuelga del nudo
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 270" width="330" height="270" font-family="Arial, sans-serif">
<rect width="330" height="270" fill="#fff"/>
<line x1="40" y1="30" x2="300" y2="30" stroke="#222" stroke-width="3"/>
<line x1="40" y1="30" x2="40" y2="250" stroke="#222" stroke-width="3"/>
<g stroke="#999" stroke-width="1.2">''' + ''.join(f'<line x1="{x}" y1="30" x2="{x + 10}" y2="20"/>' for x in range(44, 300, 14)) + ''.join(f'<line x1="40" y1="{y}" x2="30" y2="{y + 10}"/>' for y in range(36, 250, 14)) + '''</g>
<line x1="40" y1="170" x2="148" y2="97" stroke="#555" stroke-width="2.4"/>
<line x1="148" y1="97" x2="172" y2="30" stroke="#555" stroke-width="2.4"/>
<line x1="148" y1="97" x2="148" y2="160" stroke="#555" stroke-width="2.4"/>
<circle cx="40" cy="170" r="5" fill="#111"/><circle cx="172" cy="30" r="5" fill="#111"/><circle cx="148" cy="97" r="5" fill="#111"/>
<path d="M 40 140 A 30 30 0 0 1 65 153" fill="none" stroke="#1f6fb2" stroke-width="2"/>
<text x="50" y="134" font-size="18" font-style="italic" fill="#1f6fb2">α</text>
<path d="M 142 30 A 30 30 0 0 0 161.9 58.2" fill="none" stroke="#1f6fb2" stroke-width="2"/>
<text x="130" y="58" font-size="18" font-style="italic" fill="#1f6fb2">θ</text>
<text x="80" y="128" font-size="18" font-style="italic">A</text>
<text x="167" y="78" font-size="18" font-style="italic">B</text>
<rect x="118" y="160" width="60" height="50" rx="6" fill="#4a86c8" stroke="#2b5d94" stroke-width="2"/>
<text x="141" y="192" font-size="18" font-style="italic" fill="#fff">P</text>
</svg>
'''


# ───────────────────────── El quiz ─────────────────────────
def armar_quiz():
    porsec = {k: [] for k, _ in SECCIONES}
    for nombre, *qs in CAMPUS:
        for k, q in zip(SEC_CAMPUS, qs):
            d = dict(tipo='num', en=q['en'], num=q['num'], ex=q['ex'], fuente=f'{nombre} · campus', practica=True)
            if q.get('img'): d['img'] = q['img']
            porsec[k].append(d)
    for q in EXAMEN_2021:
        d = dict(tipo='num', en=q['en'], num=q['num'], ex=q['ex'], fuente='Examen de ingreso 2021')
        for k in ('img', 'mal'):
            if q.get(k): d[k] = q[k]
        porsec[q['sec']].append(d)
    for q in VIEJAS:
        d = {k: v for k, v in q.items() if k != 'sec'}
        porsec[q['sec']].append(d)
    return dict(
        titulo='Física · Ingreso',
        descripcion='Las preguntas de los simulacros y del examen 2021 del campus (5 preguntas numéricas: conversión, vectores, cinemática, trabajo y tensiones) y las de los finales de 2011 y 2012, con la resolución paso a paso (g = 9,8 m/s²).',
        secciones=[dict(titulo=t, preguntas=porsec[k]) for k, t in SECCIONES if porsec[k]],
        glosario=[{k: v for k, v in g.items() if not (k == 'i' and not v)} for g in GLOSARIO],
    )


# ───────────────────────── La guía en PDF: las 5 preguntas del campus, resueltas ─────────────────────────
GUIA_TIPOS = [
    ('Conversión de unidades', 'Te dan dos velocidades en millas/h y piden la diferencia en m/s.',
     'Restá primero y convertí una sola vez: 1 mi/h = 1609 m / 3600 s = 0,4469 m/s.'),
    ('Vectores: dirección de la posición final', 'Un barco hace un tramo con rumbo noroeste (ángulo desde el este) y otro hacia el este. Piden el ángulo del vector posición.',
     'Cada tramo en componentes (x = d·cos θ; y = d·sen θ), se suman las x y las y, y α = arctg(y/x).'),
    ('Cinemática: MRU', 'Un vehículo recorre una distancia a velocidad constante; piden la velocidad para tardar cierta cantidad de minutos menos.',
     'Lo que cambia es el tiempo: t = d/v, le restás los minutos (pasados a horas) y v = d / t nuevo.'),
    ('Trabajo mecánico', 'Una fuerza inclinada mueve una caja en horizontal. Piden el trabajo.',
     'W = F·d·cos θ, con θ el ángulo entre la fuerza y el desplazamiento.'),
    ('Estática: tensión en una cuerda', 'Un peso cuelga de dos cuerdas atadas al techo con ángulos α y θ. Piden la tensión de la cuerda A.',
     'Equilibrio en el nudo: ΣFx = 0 da T<sub>B</sub> en función de T<sub>A</sub>; ΣFy = 0 da T<sub>A</sub> = P / (sen α + cos α·tg θ).'),
]

CSS_GUIA = '''
@page { size: A4; margin: 15mm 15mm 15mm; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; box-sizing: border-box; }
body { font-family: 'Open Sans', 'DejaVu Sans', sans-serif; font-size: 9.6pt; line-height: 1.45; color: #1f1e1c; margin: 0; }
h1 { font-family: Georgia, 'DejaVu Serif', serif; font-weight: 400; font-size: 22pt; margin: 0 0 2pt; }
.bajada { color: #5b5a54; margin: 0 0 10pt; font-size: 10pt; }
h2 { font-family: Georgia, 'DejaVu Serif', serif; font-weight: 400; font-size: 14.5pt; margin: 16pt 0 4pt; padding-top: 6pt; border-top: 1px solid #e3e1da; break-after: avoid; }
h2 .n { display: inline-block; width: 20pt; height: 20pt; line-height: 20pt; text-align: center; border-radius: 50%; background: #2d8992; color: #fff; font: 700 10pt 'Open Sans', sans-serif; margin-right: 6pt; vertical-align: 2pt; }
.que { margin: 0 0 4pt; color: #46453f; }
.como { background: #e4f3f5; border-left: 3pt solid #2d8992; border-radius: 4pt; padding: 5pt 9pt; margin: 4pt 0 8pt; }
.caso { border: 1px solid #e3e1da; border-radius: 6pt; padding: 7pt 10pt; margin: 6pt 0; break-inside: avoid; }
.caso .f { font-size: 8pt; text-transform: uppercase; letter-spacing: .06em; color: #7c7b75; font-weight: 700; margin-bottom: 2pt; }
.caso .en { margin-bottom: 4pt; }
.caso .ex { color: #2b2a27; border-top: 1px dashed #e3e1da; padding-top: 4pt; }
.caso img { display: block; height: 30mm; margin: 2pt 0 4pt; }
.resp { background: #e5efe7; color: #2f6b45; font-weight: 700; border-radius: 3pt; padding: 0 3pt; }
.chico { font-size: 8.4pt; color: #6b6a64; }
.dos { display: grid; grid-template-columns: 1fr 1fr; gap: 6pt; }
.res-t { width: 100%; border-collapse: collapse; margin: 4pt 0 0; font-size: 9pt; }
.res-t th, .res-t td { text-align: left; padding: 3pt 6pt; border-bottom: 1px solid #e3e1da; }
.res-t th { background: #f3f2ee; }
'''


def armar_guia_html(css_fuentes):
    e = html.escape
    filas = ''.join(f'<tr><td>{n}</td><td>{e(t)}</td></tr>' for n, (t, _, _) in enumerate(GUIA_TIPOS, 1))
    cuerpo = (f'<h1>Física · Examen de ingreso</h1><p class="bajada">Las 5 preguntas del examen del campus, resueltas: cómo se piensa cada una, '
              f'los tres simulacros y el examen 2021. En el campus cambian los números; el procedimiento es siempre el mismo. g = 9,8 m/s².</p>'
              f'<table class="res-t"><tr><th>#</th><th>Pregunta</th></tr>{filas}</table>')
    for n, (titulo, que, como) in enumerate(GUIA_TIPOS, 1):
        cuerpo += f'<h2><span class="n">{n}</span>{titulo}</h2><p class="que">{que}</p><div class="como"><b>Cómo se resuelve:</b> {como}</div>'
        casos = [(nombre, qs[n - 1]) for nombre, *qs in CAMPUS]
        cuerpo += '<div class="dos">' + ''.join(
            f'<div class="caso"><div class="f">{nombre}</div><div class="en">{q["en"]}</div>'
            + (f'<img src="file://{os.path.join(RAIZ, q["img"])}">' if q.get('img') and nombre == 'Simulacro 1' else '')
            + f'<div><b>Respuesta:</b> {q["num"]}</div><div class="ex">{q["ex"]}</div></div>' for nombre, q in casos[:2]) + '</div>'
        nombre, q = casos[2]
        cuerpo += (f'<div class="caso"><div class="f">{nombre}</div><div class="en">{q["en"]}</div><div><b>Respuesta:</b> {q["num"]}</div>'
                   f'<div class="ex">{q["ex"]}</div></div>')
    cuerpo += '<h2><span class="n">★</span>Examen de ingreso 2021</h2><p class="que">Las mismas cinco preguntas, con otros enunciados.</p>'
    for q in EXAMEN_2021:
        img = f'<img src="file://{os.path.join(RAIZ, q["img"])}">' if q.get('img') else ''
        cuerpo += f'<div class="caso"><div class="en">{q["en"]}</div>{img}<div><b>Respuesta:</b> {q["num"]}</div><div class="ex">{q["ex"]}</div></div>'
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Física · Examen de ingreso, resuelto</title>'
            f'<style>{css_fuentes}{CSS_GUIA}</style></head><body>{cuerpo}</body></html>')


def fuentes_css(carpeta):
    if not carpeta: return ''
    return ''.join(f"@font-face{{font-family:'Open Sans';font-weight:{p};src:url('file://{os.path.join(carpeta, f'open-sans-latin-{p}-normal.woff2')}') format('woff2')}}"
                   for p in (400, 600, 700) if os.path.exists(os.path.join(carpeta, f'open-sans-latin-{p}-normal.woff2')))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', action='store_true', help='armar también la guía en PDF')
    ap.add_argument('--fuente', help='carpeta con open-sans-latin-{400,600,700}-normal.woff2')
    a = ap.parse_args()
    os.makedirs(os.path.join(RAIZ, 'quiz', 'img'), exist_ok=True)
    for nombre, svg in (('fisica-cuerdas-techo.svg', svg_cuerdas_techo()), ('fisica-pared-techo.svg', svg_pared_techo())):
        open(os.path.join(RAIZ, 'quiz', 'img', nombre), 'w', encoding='utf-8').write(svg)
    q = armar_quiz()
    with open(os.path.join(RAIZ, 'quiz', 'fisica-ingreso.json'), 'w', encoding='utf-8') as fh:
        json.dump(q, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print('quiz:', sum(len(s['preguntas']) for s in q['secciones']), 'preguntas ·', ', '.join(f"{s['titulo']} {len(s['preguntas'])}" for s in q['secciones']))
    if a.pdf:
        chromium = next((c for c in (os.environ.get('CHROMIUM'), '/opt/pw-browsers/chromium', shutil.which('chromium')) if c and os.path.exists(c)), None)
        if not chromium: raise SystemExit('No encuentro Chromium (poné su ruta en la variable CHROMIUM).')
        destino = os.path.join(RAIZ, 'material', 'cursillo', 'fisica')
        os.makedirs(destino, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            h = os.path.join(tmp, 'guia.html')
            open(h, 'w', encoding='utf-8').write(armar_guia_html(fuentes_css(a.fuente)))
            pdf = os.path.join(destino, '01-examen-de-ingreso-resuelto.pdf')
            subprocess.run([chromium, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--disable-background-networking',
                            '--no-first-run', '--allow-file-access-from-files', f'--print-to-pdf={pdf}', 'file://' + h], check=True, capture_output=True)
        print('guía:', pdf)


if __name__ == '__main__':
    main()
