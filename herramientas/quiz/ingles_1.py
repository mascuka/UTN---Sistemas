#!/usr/bin/env python3
"""Inglés 1: la práctica para escribir (quiz/ingles-1.json), el resumen y los parciales y prácticas con su resolución.

El parcial es de lectocomprensión: un texto técnico en inglés y ejercicios que se responden en español
(preguntas, traducción de frases, referencia contextual, antónimos, sinónimos y conectores).

- La práctica son frases y palabras cortas para escribir: traducir frases nominales, vocabulario, conectores
  (traducción y relación), antónimos (también con prefijos), sinónimos y referentes. Cada una tiene las respuestas
  que valen ("resp"); la página las corrige sola (tipo "escribir").
- Cada parcial o práctica queda en un PDF: primero en blanco, tal cual, y a continuación el mismo resuelto.
  Las respuestas son nuestras (el material no traía la corrección).
- La práctica del campus («Práctica primer parcial», primera ley de Newton) se vuelve a escribir: la impresión del
  campus no se publica.

Uso, desde la raíz del repo:
  python3 herramientas/quiz/ingles_1.py                                   (la práctica)
  python3 herramientas/quiz/ingles_1.py --pdf --fuente CARPETA_OPEN_SANS  (además, los PDF de material/ingles-1/)
"""
import argparse, html, json, os, shutil, subprocess, tempfile

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
DESTINO = os.path.join(RAIZ, 'material', 'ingles-1')

# ───────────────────────── La práctica para escribir ─────────────────────────
ADI, CTR, CAU, CSQ, CND, FIN, EJE, TIE = (
    ['adición', 'suma', 'agregado'], ['contraste', 'oposición', 'contraposición', 'concesión'], ['causa', 'causalidad'],
    ['consecuencia', 'resultado', 'efecto', 'causa-efecto'], ['condición'], ['finalidad', 'propósito', 'objetivo', 'fin'],
    ['ejemplificación', 'ejemplo', 'ejemplificar'], ['tiempo', 'temporal', 'secuencia', 'simultaneidad'])
RELACIONES = 'adición, contraste, causa, consecuencia, condición, finalidad, ejemplificación o tiempo'

FRASES = [  # (inglés, respuestas, por qué)
    ('energy resources', ['recursos energéticos', 'recursos de energía'], 'Núcleo al final: <i>resources</i> (recursos).'),
    ('clean energy', ['energía limpia'], None),
    ('renewable energy sources', ['fuentes de energía renovable', 'fuentes de energía renovables', 'fuentes renovables de energía'], 'Núcleo: <i>sources</i> (fuentes) → de energía → renovable.'),
    ('solar panels', ['paneles solares', 'placas solares'], None),
    ('carbon footprint', ['huella de carbono'], None),
    ('long-term investment', ['inversión a largo plazo'], '<i>long-term</i> = a largo plazo.'),
    ('energy supply', ['suministro de energía', 'suministro energético', 'abastecimiento de energía', 'abastecimiento energético'], None),
    ('the energy grid', ['la red eléctrica', 'la red de energía', 'la red energética'], '<i>grid</i> = red (de distribución).'),
    ('processing ability', ['capacidad de procesamiento', 'habilidad de procesamiento', 'capacidad de procesar'], None),
    ('embedded systems', ['sistemas embebidos', 'sistemas integrados', 'sistemas incrustados'], None),
    ('increasingly powerful systems', ['sistemas cada vez más potentes', 'sistemas cada vez más poderosos'], '<i>increasingly</i> + adjetivo = cada vez más + adjetivo.'),
    ('more and more devices', ['cada vez más dispositivos'], '<i>more and more</i> = cada vez más.'),
    ('operating system', ['sistema operativo'], None),
    ('hard disk', ['disco rígido', 'disco duro'], None),
    ('computer system', ['sistema informático', 'sistema de computación', 'sistema computacional', 'sistema de computadora'], None),
    ('program files', ['archivos de programa', 'archivos de programas'], None),
    ('smart home', ['casa inteligente', 'hogar inteligente'], None),
    ('home appliances', ['electrodomésticos', 'aparatos del hogar', 'aparatos domésticos', 'artefactos del hogar'], None),
    ('wireless networks', ['redes inalámbricas'], '<i>wireless</i> = sin cable, inalámbrico.'),
    ('machine learning', ['aprendizaje automático', 'aprendizaje de máquina', 'aprendizaje de máquinas'], None),
    ('data exchange', ['intercambio de datos'], None),
    ('network security', ['seguridad de red', 'seguridad de redes', 'seguridad de la red'], None),
    ('user interface', ['interfaz de usuario', 'interfaz del usuario'], None),
    ('real-time monitoring', ['monitoreo en tiempo real', 'monitorización en tiempo real', 'control en tiempo real'], None),
    ('short-range devices', ['dispositivos de corto alcance'], None),
    ('software development', ['desarrollo de software'], None),
    ('power plant', ['central eléctrica', 'planta de energía', 'planta eléctrica', 'central de energía'], None),
    ('external force', ['fuerza externa'], None),
    ('reference frame', ['marco de referencia', 'sistema de referencia'], None),
    ('harmless joke', ['broma inofensiva'], None),
]
VOCABULARIO = [
    ('scarcity', ['escasez']), ('issue', ['tema', 'problema', 'cuestión', 'asunto']), ('trend', ['tendencia']),
    ('supply', ['suministro', 'abastecimiento', 'provisión']), ('growth', ['crecimiento']), ('device', ['dispositivo', 'aparato']),
    ('network', ['red']), ('concern', ['preocupación', 'inquietud']), ('investment', ['inversión']), ('storage', ['almacenamiento']),
    ('feature', ['característica', 'función', 'funcionalidad']), ('damage', ['daño']), ('host', ['huésped', 'anfitrión']),
    ('payload', ['carga útil', 'carga']), ('requirement', ['requisito', 'requerimiento']), ('goal', ['objetivo', 'meta']),
]
CONECTORES = [  # (conector, traducciones, relación)
    ('therefore', ['por lo tanto', 'por consiguiente', 'por ende', 'entonces', 'así que'], CSQ),
    ('however', ['sin embargo', 'no obstante'], CTR),
    ('although', ['aunque', 'si bien', 'a pesar de que'], CTR),
    ('because', ['porque', 'ya que', 'debido a que'], CAU),
    ('due to', ['debido a', 'a causa de'], CAU),
    ('unless', ['a menos que', 'salvo que', 'a no ser que', 'excepto que'], CND),
    ('if', ['si'], CND),
    ('in order to', ['para', 'con el fin de', 'a fin de'], FIN),
    ('such as', ['como', 'tales como', 'tal como', 'como por ejemplo'], EJE),
    ('for example', ['por ejemplo'], EJE),
    ('moreover', ['además', 'más aún', 'asimismo'], ADI),
    ('also', ['también', 'además'], ADI),
    ('whereas', ['mientras que', 'en tanto que'], CTR),
    ('so', ['así que', 'entonces', 'por lo tanto', 'por eso'], CSQ),
    ('this is why', ['es por esto que', 'por eso', 'por esto', 'es por eso que', 'por esta razón'], CSQ),
    ('since', ['ya que', 'dado que', 'puesto que'], CAU),
    ('meanwhile', ['mientras tanto', 'entretanto'], TIE),
    ('as a result', ['como resultado', 'como consecuencia', 'por consiguiente'], CSQ),
]
ANTONIMOS = [  # (palabra, antónimos que valen, por qué)
    ('strong', ['weak'], None), ('scarcity', ['abundance', 'plenty'], None), ('cheap', ['expensive', 'costly'], None),
    ('begin', ['end', 'finish', 'stop'], None), ('increase', ['decrease', 'reduce', 'reduction'], None), ('internal', ['external'], None),
    ('success', ['failure'], None), ('before', ['after'], None), ('input', ['output'], None), ('upload', ['download'], None),
    ('always', ['never'], None), ('high', ['low'], None), ('large', ['small', 'little'], None), ('simple', ['complex', 'complicated'], None),
    ('public', ['private'], None), ('straight', ['curved', 'crooked'], None), ('moving', ['resting', 'still', 'stationary', 'static'], None),
    ('local', ['global'], None), ('dormant', ['active'], None), ('destructive', ['harmless', 'constructive'], None),
]
PREFIJOS = [
    ('possible', ['impossible'], '<i>im-</i> delante de p, b y m.'), ('connected', ['disconnected'], None),
    ('renewable', ['non-renewable', 'nonrenewable'], '<i>non-</i> se escribe con guion.'), ('secure', ['insecure', 'unsecure'], None),
    ('able', ['unable'], None), ('legal', ['illegal'], '<i>il-</i> delante de l.'), ('regular', ['irregular'], '<i>ir-</i> delante de r.'),
    ('advantage', ['disadvantage'], None), ('correct', ['incorrect'], None), ('visible', ['invisible'], None),
    ('accessible', ['inaccessible'], None), ('necessary', ['unnecessary'], None), ('known', ['unknown'], None),
    ('dependent', ['independent'], None), ('efficient', ['inefficient'], None), ('available', ['unavailable'], None),
    ('appear', ['disappear'], None), ('responsible', ['irresponsible'], None),
    ('harmful', ['harmless'], 'El sufijo <i>-ful</i> (con) se cambia por <i>-less</i> (sin).'), ('useful', ['useless'], 'De <i>-ful</i> a <i>-less</i>.'),
    ('wired', ['wireless'], '<i>-less</i> = sin: sin cable.'),
]
SINONIMOS = [
    ('guarantee', ['secure', 'ensure', 'assure', 'warrant']), ('announced', ['reported', 'declared', 'stated']),
    ('state-of-the-art', ['ultra modern', 'ultramodern', 'cutting-edge', 'modern', 'advanced', 'latest']),
    ('begin', ['start', 'commence']), ('finish', ['end', 'complete', 'conclude']), ('big', ['large', 'huge', 'great']),
    ('buy', ['purchase', 'acquire']), ('need', ['require']), ('use', ['utilize', 'utilise', 'employ']),
    ('get', ['obtain', 'receive', 'acquire', 'gain']), ('show', ['display', 'present', 'exhibit']), ('often', ['frequently', 'usually']),
    ('fast', ['quick', 'rapid', 'speedy']), ('main', ['principal', 'primary', 'chief', 'major']), ('damage', ['harm', 'injury']),
    ('enough', ['sufficient']), ('help', ['assist', 'aid', 'support']), ('whole', ['entire', 'complete', 'total']),
]
REFERENTES = [  # (oración, palabra, respuestas)
    ('Companies want to secure THEIR own electricity supply.', 'THEIR', ['companies', 'empresas', 'compañías']),
    ('IKEA placed solar panels on the roofs of ITS buildings.', 'ITS', ['IKEA']),
    ('The virus copies ITSELF into other program files.', 'ITSELF', ['virus', 'the virus']),
    ('Devices do not need the public internet: THEY only need a network.', 'THEY', ['devices', 'dispositivos']),
    ('Kevin Ashton coined the term, though HE prefers another phrase.', 'HE', ['Kevin Ashton', 'Ashton']),
    ('Apple opened a new campus WHICH has 75,000 square metres of solar arrays.', 'WHICH', ['campus', 'new campus', 'nuevo campus']),
    ('Engineers test the sensors before installing THEM.', 'THEM', ['sensors', 'sensores']),
    ('When the user runs an infected program, IT is loaded into memory.', 'IT', ['infected program', 'program', 'programa infectado', 'programa']),
    ('IoT enables communication between people and things, and between things THEMSELVES.', 'THEMSELVES', ['things', 'cosas']),
    ('Consumers prefer companies THAT take care of the environment.', 'THAT', ['companies', 'empresas']),
    ('Solar panels are cheap, but THEY need sunlight.', 'THEY', ['solar panels', 'paneles solares', 'panels', 'paneles']),
    ('Peter Lewis gave a speech in 1985. HIS definition of IoT was published that year.', 'HIS', ['Peter Lewis', 'Lewis']),
]


def escribir(sec, en, resp, ph=None, ex=None):
    q = dict(sec=sec, tipo='escribir', en=en, resp=resp)
    if ph: q['ph'] = ph
    if ex: q['ex'] = ex
    return q


def practica():
    qs = []
    for ing, resp, ex in FRASES:
        qs.append(escribir('frases', f'Traducí al español: <b>{ing}</b>', resp, 'En español…', ex))
    for ing, resp in VOCABULARIO:
        qs.append(escribir('vocab', f'¿Qué significa <b>{ing}</b>?', resp, 'En español…'))
    for c, trad, rel in CONECTORES:
        qs.append(escribir('con', f'Traducí el conector <b>{c.upper()}</b>', trad, 'En español…'))
        qs.append(escribir('con', f'¿Qué relación establece el conector <b>{c.upper()}</b>?', rel, RELACIONES,
                           f'<b>{c}</b> = {trad[0]}: {rel[0]}.'))
    for w, resp, ex in ANTONIMOS:
        qs.append(escribir('ant', f'Escribí en inglés un antónimo de <b>{w.upper()}</b>', resp, 'En inglés…', ex))
    for w, resp, ex in PREFIJOS:
        qs.append(escribir('pref', f'Formá el antónimo de <b>{w.upper()}</b> con un prefijo o un sufijo', resp, 'En inglés…', ex))
    for w, resp in SINONIMOS:
        qs.append(escribir('sin', f'Escribí en inglés un sinónimo de <b>{w.upper()}</b>', resp, 'En inglés…'))
    for o, w, resp in REFERENTES:
        qs.append(escribir('ref', f'Referencia contextual: ¿a qué o a quién se refiere <b>{w}</b>?<br><i>«{html.escape(o)}»</i>', resp,
                           'La palabra del texto (en inglés o en español)…'))
    return qs


SECCIONES = [
    ('frases', 'Traducir frases'), ('vocab', 'Vocabulario'), ('con', 'Conectores'), ('ant', 'Antónimos'),
    ('pref', 'Antónimos con prefijos y sufijos'), ('sin', 'Sinónimos'), ('ref', 'Referencia contextual'),
]
GLOSARIO = [
    dict(t='Frase nominal', que='Un grupo de palabras cuyo núcleo es un sustantivo. En inglés los modificadores van <b>antes</b> del núcleo; en español, después: se traduce de derecha a izquierda (<i>renewable energy sources</i> → fuentes de energía renovable).', re=r'Traducí al español'),
    dict(t='Vocabulario técnico', que='Las palabras que más se repiten en los textos: <i>issue</i> (tema), <i>trend</i> (tendencia), <i>supply</i> (suministro), <i>device</i> (dispositivo), <i>network</i> (red), <i>scarcity</i> (escasez).', re=r'¿Qué significa'),
    dict(t='Conector (nexo lógico)', que='Une dos ideas y dice cómo se relacionan. En el cuadro del parcial: traducción, tipo de relación, idea uno (antes) e idea dos (después).', re=r'conector'),
    dict(t='Relaciones lógicas', que='<b>Adición</b>: and, also, moreover. <b>Contraste</b>: but, however, although, whereas. <b>Causa</b>: because, since, due to. <b>Consecuencia</b>: so, therefore, this is why, as a result. <b>Condición</b>: if, unless. <b>Finalidad</b>: to, in order to. <b>Ejemplificación</b>: such as, for example. <b>Tiempo</b>: when, meanwhile.', re=r'relación'),
    dict(t='Antónimo', que='La palabra de significado <b>opuesto</b>. En el parcial te dan una palabra que no está en el texto y tenés que encontrar su opuesta en la línea que indican.', re=r'antónimo de'),
    dict(t='Prefijos y sufijos negativos', que='<b>un-</b> (unable), <b>in-</b> (incorrect), <b>im-</b> delante de p/b/m (impossible), <b>il-</b> delante de l (illegal), <b>ir-</b> delante de r (irregular), <b>dis-</b> (disconnected), <b>non-</b> (non-renewable). Sufijos: <b>-ful</b> (con) ↔ <b>-less</b> (sin): harmful ↔ harmless.', re=r'con un prefijo'),
    dict(t='Sinónimo', que='La palabra de significado <b>parecido</b>: <i>guarantee</i> ≈ <i>secure</i>, <i>reported</i> ≈ <i>announced</i>.', re=r'sinónimo de'),
    dict(t='Referencia contextual', que='A qué o a quién reemplaza un pronombre. Casi siempre está <b>antes</b>, en la misma oración o en la anterior, y coincide en número.', re=r'Referencia contextual'),
    dict(t='Pronombres', que='<i>it / its / itself</i>: algo singular. <i>they / them / their / themselves</i>: plural. <i>he / him / his</i>: un hombre. <i>which / that</i>: que, el cual (retoman el sustantivo de antes).', re=r'se refiere\s+(ITSELF|ITS|IT|THEY|THEM|THEIR|THEMSELVES|HE|HIM|HIS|WHICH|THAT)\b'),
]


def armar_quiz():
    porsec = {k: [] for k, _ in SECCIONES}
    for q in practica():
        porsec[q['sec']].append({k: v for k, v in q.items() if k != 'sec'})
    return dict(
        titulo='Inglés 1 · Práctica para escribir',
        descripcion='Frases y palabras cortas como las del parcial: escribís la respuesta y te dice si está bien. No importan las mayúsculas, las tildes ni el artículo del principio. Si tu traducción dice lo mismo con otras palabras, tocá «Mi respuesta también vale».',
        secciones=[dict(titulo=t, preguntas=porsec[k]) for k, t in SECCIONES if porsec[k]],
        glosario=GLOSARIO,
    )


# ───────────────────────── Las resoluciones ─────────────────────────
# Cada documento: título y sus ejercicios, con la misma numeración que el original.
# Un ejercicio es (consigna, [(ítem, respuesta), …]) o (consigna, 'tabla', [(conector, traducción, relación, idea 1, idea 2), …])
PARCIAL_2023 = ('Parcial 2023 · Energía renovable', [
    ('1) Responder las siguientes preguntas en ESPAÑOL.', [
        ('¿Qué puede llegar a pasar en la transición entre energía tradicional y energía sustentable?',
         'Que la electricidad limpia se vuelva escasa: al pasar de la energía tradicional (barata y accesible) a la energía verde puede faltar electricidad limpia. Por eso las empresas buscan asegurarse su propio suministro (líneas 6 a 9).')]),
    ('2) Traducir los siguientes fragmentos al ESPAÑOL.', [
        ('Energy resources scarcity is a concerning issue.', 'La escasez de recursos energéticos es un tema preocupante.'),
        ('There is every reason to believe that society will continue to use more and more machines and devices.', 'Hay todas las razones para creer que la sociedad seguirá usando cada vez más máquinas y dispositivos.'),
        ('The self-generated clean energy trend', 'La tendencia de la energía limpia autogenerada.'),
        ('Installing your own energy production is a long-term investment', 'Instalar tu propia producción de energía es una inversión a largo plazo.')]),
    ('3) Referencia contextual. Indicar a qué o quién hacen referencia las siguientes palabras o frases.', [
        ('Themselves (línea 3)', 'companies (las empresas)'), ('Their (línea 9)', 'companies (las empresas)'),
        ('Which (línea 13)', 'IKEA'), ('Its (línea 14)', 'IKEA'), ('Which (línea 20)', 'solar arrays (los paneles solares)'),
        ('He (línea 27)', 'Mats Alvem')]),
    ('4) Indicar los antónimos de las siguientes palabras.', [
        ('Abundance (línea 1)', 'scarcity'), ('Finished (línea 11)', 'began'), ('Weak (línea 28)', 'strong')]),
    ('5) Indicar los sinónimos de las siguientes palabras.', [
        ('Guarantee (línea 9)', 'secure'), ('Reported (línea 15)', 'announced'), ('Ultra modern (línea 19)', 'state-of-the-art')]),
    ('6) Completar el siguiente cuadro de conectores en ESPAÑOL.', 'tabla', [
        ('therefore (línea 5)', 'por lo tanto', 'consecuencia', 'La sociedad va a seguir usando cada vez más máquinas y dispositivos.', 'Va a consumir más electricidad.'),
        ('This is why (línea 7)', 'es por esto que / por eso', 'consecuencia', 'La electricidad limpia podría volverse escasa.', 'Las empresas buscan asegurar su propio suministro de electricidad.'),
        ('In order to (línea 14)', 'para / con el fin de', 'finalidad', 'IKEA empezó a poner paneles solares en los techos de sus edificios.', 'Ayudar a reducir su huella de carbono.'),
        ('Such as (línea 23)', 'como / tales como', 'ejemplificación', 'Los grandes minoristas fueron de los primeros en generar su propia energía.', 'Apple e IKEA.')]),
])
MODELO_IOT = ('Modelo de parcial · Internet de las cosas', [
    ('1) Responder las siguientes preguntas en ESPAÑOL.', [
        ('¿Cuáles son las preocupaciones respecto al crecimiento de productos y tecnologías de IoT?',
         'Los riesgos en la privacidad y en la seguridad. Por eso la industria y los gobiernos empezaron a desarrollar normas internacionales y locales, guías y marcos regulatorios.')]),
    ('2) Traducir los siguientes fragmentos al ESPAÑOL.', [
        ('Processing ability', 'Capacidad de procesamiento.'), ('Increasingly powerful embedded systems', 'Sistemas embebidos cada vez más potentes.'),
        ('The concept of the “smart home”', 'El concepto de «casa inteligente».'), ('Short-range mobile transceivers', 'Transceptores móviles de corto alcance.')]),
    ('3) Referencia contextual. Indicar a qué o quién hacen referencia las siguientes palabras o frases.', [
        ('That (línea 2)', 'physical objects: los objetos físicos (con sus sensores, su software y otras tecnologías), que son los que se conectan e intercambian datos'),
        ('They (línea 4)', 'devices (los dispositivos)'), ('Itself (línea 17)', 'the term «Internet of things» (el término)'),
        ('Him (línea 19)', 'Peter T. Lewis'), ('He (línea 22)', 'Kevin Ashton'), ('Themselves (línea 26)', 'things (las cosas)')]),
    ('4) Completar el siguiente cuadro de conectores en ESPAÑOL.', 'tabla', [
        ('Due to (línea 6)', 'debido a', 'causa', 'El campo (de la IoT) evolucionó.', 'La convergencia de múltiples tecnologías.'),
        ('Such as (línea 12)', 'como / tales como', 'ejemplificación', 'Dispositivos asociados a ese ecosistema.', 'Teléfonos inteligentes y parlantes inteligentes.')]),
])
PRACTICA_VIRUS = ('Práctica de clase · The anatomy of a virus', [
    ('1. Leer el texto y encontrar las respuestas a las siguientes preguntas (en español).', [
        ('How are computer viruses like biological viruses?', 'Los dos son muy pequeños, infectan a un huésped (una célula o un sistema informático), usan sus recursos para reproducirse y muchas veces le causan daño.'),
        ('What is the effect of a virus patching the operating system?', 'Le permite detectar los archivos de programa (como los COM o EXE) para copiarse dentro de ellos.'),
        ('Why are some viruses designed to be loaded into memory?', 'Para quedar residentes en memoria y, desde ahí, infectar otros programas hasta que se apague la computadora.'),
        ('What examples of payload does the writer of the text provide?', 'Uno inofensivo: mostrar un mensaje en el monitor. Uno destructivo: borrar archivos del disco rígido.'),
        ('How does a Trojan differ from a virus?', 'El troyano tiene payload, pero no tiene rutina de reproducción: no se copia a otros programas.')]),
    ('2. Unir cada rutina de virus con su función.', [
        ('I. Misdirection', 'c) Hides the presence of the code'), ('II. Reproduction', 'b) Attaches a copy of itself to another program'),
        ('III. Trigger', 'd) Decides when and how to activate the payload'), ('IV. Payload', 'a) Does the damage')]),
    ('3. Conectores. Completar el siguiente cuadro en español.', 'tabla', [
        ('Such as', 'como / tales como', 'ejemplificación', 'Archivos de programa.', 'Archivos COM o EXE.'),
        ('Also', 'también', 'adición', 'El virus se queda en memoria e infecta otros programas.', 'Puede contener un payload.'),
        ('To', 'para', 'finalidad', 'Ser un virus.', 'Un programa solo necesita una rutina de reproducción.'),
        ('But', 'pero', 'contraste', 'El programa tiene un payload.', 'No tiene rutina de reproducción.')]),
    ('4. Referencia contextual. Encontrar los referentes a las siguientes palabras.', [
        ('Itself', 'a biological virus (el virus biológico)'), ('Them', 'living cells (las células vivas, el huésped)'),
        ('Its', 'a computer system (el sistema informático)'), ('It', 'an infected program (el programa infectado)'),
        ('Which', 'the host program (el programa huésped)')]),
    ('5. Traducir las siguientes frases.', [
        ('host computer system', 'sistema informático huésped (anfitrión)'), ('common programming techniques', 'técnicas de programación comunes'),
        ('normal sequence of instructions', 'secuencia normal de instrucciones'), ('harmless joke', 'broma inofensiva'),
        ('deleting files on the hard disk', 'borrar archivos del disco rígido')]),
])
NEWTON_TEXTO = [
    'Newton’s First Law states that an object will remain at rest or in uniform motion in a straight line unless acted upon by an external force. It may be seen as a statement about inertia, that objects will remain in their state of motion unless a force acts to change the motion. Any change in motion involves an acceleration, and then Newton’s Second Law applies. The First Law could be viewed as just a special case of the Second Law for which the net external force is zero, but that carries some presumptions about the frame of reference in which the motion is being viewed.',
    'The statements of both the Second Law and the First Law here are presuming that the measurements are being made in a reference frame which is not itself accelerating. Such a frame is often referred to as an “inertial frame”. The statement of these laws must be generalized if you are dealing with a rotating reference frame or any frame which is accelerating.',
    'Newton’s First Law contains implications about the fundamental symmetry of the universe in that a state of motion in a straight line must be just as “natural” as being at rest. If an object is at rest in one frame of reference, it will appear to be moving in a straight line to an observer in a reference frame which is moving by the object. There is no way to say which reference frame is “special”, so all constant velocity reference frames must be equivalent.',
]
PRACTICA_NEWTON = ('Práctica del campus · Primera ley de Newton', [
    ('1. Identificar y transcribir el nexo lógico de cada fragmento e indicar la relación lógica.', [
        ('«…an object will remain at rest or in uniform motion in a straight line unless acted upon by an external force.»', 'UNLESS (a menos que): condición'),
        ('«…objects will remain in their state of motion unless a force acts to change the motion.»', 'UNLESS (a menos que): condición'),
        ('«The statement of these laws must be generalized if you are dealing with a rotating reference frame…»', 'IF (si): condición'),
        ('«If an object is at rest in one frame of reference, it will appear to be moving in a straight line…»', 'IF (si): condición'),
        ('«There is no way to say which reference frame is “special”, so all constant velocity reference frames must be equivalent.»', 'SO (por lo tanto, así que): consecuencia')]),
    ('2. Título. Seleccionar el mejor título para el texto: a) La primera ley de Newton · b) Las fuerzas que actúan sobre el movimiento · c) El movimiento uniforme de los objetos · d) Las leyes de Newton.', [
        ('Título', 'a) La primera ley de Newton: los tres párrafos hablan de ella; «Las leyes de Newton» es demasiado amplio.')]),
    ('3. Señalar el antónimo de la palabra dada, en el párrafo indicado.', [
        ('CURVED (párrafo 1)', 'straight'), ('COMMONPLACE (párrafo 1)', 'special'), ('RESTING (párrafo 3)', 'moving'),
        ('STILLNESS (párrafo 3)', 'motion (también velocity)')]),
    ('4. Señalar el referente de la palabra dada.', [
        ('THEIR (párrafo 1: «…objects will remain in their state of motion…»)', 'objects (los objetos)'),
        ('FOR WHICH (párrafo 1: «…a special case of the Second Law for which the net external force is zero…»)', 'a special case (el caso especial de la segunda ley)'),
        ('IT (párrafo 3: «If an object is at rest […], it will appear to be moving…»)', 'an object (el objeto)')]),
    ('5. Leer el texto e indicar si la oración es verdadera o falsa.', [
        ('A menos que una fuerza externa actúe sobre un objeto, el mismo permanecerá en reposo o en movimiento uniforme en línea recta.', 'Verdadero.'),
        ('Ningún cambio de movimiento involucra una aceleración, por eso aplica la segunda ley de Newton.', 'Falso: any change = cualquier cambio (todo cambio de movimiento involucra una aceleración).'),
        ('El marco inercial es aquel marco de referencia que se asume no experimenta aceleración.', 'Verdadero.')]),
])

CSS = '''
@page { size: A4; margin: 16mm 16mm 16mm; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; box-sizing: border-box; }
body { font-family: 'Open Sans', 'DejaVu Sans', sans-serif; font-size: 10pt; line-height: 1.45; color: #1f1e1c; margin: 0; }
h1 { font-family: Georgia, 'DejaVu Serif', serif; font-weight: 400; font-size: 20pt; margin: 0 0 4pt; }
.bajada { color: #5b5a54; margin: 0 0 10pt; }
h2 { font-family: Georgia, 'DejaVu Serif', serif; font-weight: 400; font-size: 14pt; margin: 14pt 0 5pt; padding-top: 6pt; border-top: 1px solid #e3e1da; break-after: avoid; }
.resuelto { display: inline-block; background: #e8f0fb; color: #1f5fbf; font-weight: 700; font-size: 8pt; letter-spacing: .1em; padding: 2pt 8pt; border-radius: 99pt; margin-bottom: 6pt; }
.ej { margin: 10pt 0 4pt; font-weight: 700; break-after: avoid; }
.it { margin: 3pt 0 6pt 14pt; break-inside: avoid; }
.it .r { color: #1f5fbf; margin-top: 1pt; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 8pt; font-size: 9pt; }
th, td { border: 1px solid #b9b6ad; padding: 4pt 5pt; vertical-align: top; text-align: left; }
th { background: #f3f2ee; }
td.a { color: #1f5fbf; }
.texto p { margin: 0 0 6pt; text-align: justify; }
.paso { display: grid; grid-template-columns: 20pt 1fr; gap: 6pt; margin: 5pt 0; break-inside: avoid; }
.paso .n { width: 17pt; height: 17pt; border-radius: 50%; background: #2d8992; color: #fff; font-weight: 700; text-align: center; line-height: 17pt; font-size: 9pt; }
.paso b.t { display: block; }
.tip { background: #e4f3f5; border-left: 3pt solid #2d8992; border-radius: 4pt; padding: 5pt 9pt; margin: 6pt 0; break-inside: avoid; }
.salto { break-before: page; }
'''


def ejercicios_html(doc, resuelto):
    e = html.escape
    titulo, ejs = doc
    c = ''
    for ej in ejs:
        c += f'<div class="ej">{e(ej[0])}</div>'
        if ej[1] == 'tabla':
            filas = ''.join(f'<tr><td><b>{e(f[0])}</b></td>' + ''.join(f'<td class="a">{e(x) if resuelto else "&nbsp;"}</td>' for x in f[1:]) + '</tr>' for f in ej[2])
            c += f'<table><tr><th style="width:16%">Conector</th><th style="width:16%">Traducción</th><th style="width:14%">Tipo de relación</th><th>Idea uno</th><th>Idea dos</th></tr>{filas}</table>'
        else:
            for it, r in ej[1]:
                c += f'<div class="it">• {e(it)}' + (f'<div class="r">→ {e(r)}</div>' if resuelto else '<div style="height:16pt"></div>') + '</div>'
    return c


def doc_resuelto(doc, css_fuentes):
    cuerpo = f'<span class="resuelto">RESUELTO</span><h1>{html.escape(doc[0])}</h1><p class="bajada">Las respuestas van en azul. Las consignas son las mismas de las hojas anteriores.</p>{ejercicios_html(doc, True)}'
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{css_fuentes}{CSS}</style></head><body>{cuerpo}</body></html>'


def doc_newton(css_fuentes):
    e = html.escape
    texto = '<div class="texto">' + ''.join(f'<p>{e(p)}</p>' for p in NEWTON_TEXTO) + '</div>'
    cuerpo = (f'<h1>{e(PRACTICA_NEWTON[0])}</h1><p class="bajada">La práctica del campus «Práctica primer parcial», escrita de nuevo. Primero en blanco y después resuelta.</p>'
              f'{texto}{ejercicios_html(PRACTICA_NEWTON, False)}'
              f'<div class="salto"></div><span class="resuelto">RESUELTO</span><h1>{e(PRACTICA_NEWTON[0])}</h1>{ejercicios_html(PRACTICA_NEWTON, True)}')
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(PRACTICA_NEWTON[0])}</title><style>{css_fuentes}{CSS}</style></head><body>{cuerpo}</body></html>'


PASOS = [
    ('Preguntas de comprensión', 'Buscá el párrafo que habla de lo que preguntan y respondé <b>en español y con tus palabras</b>. No copies la oración en inglés.'),
    ('Traducción de frases', 'Casi siempre son frases nominales: encontrá el <b>núcleo</b> (el último sustantivo) y traducí de derecha a izquierda. <i>Increasingly powerful embedded systems</i> → sistemas embebidos cada vez más potentes.'),
    ('Referencia contextual', 'Buscá <b>hacia atrás</b> el sustantivo que el pronombre reemplaza y que coincide en número: <i>it/its</i> singular, <i>they/them/their</i> plural, <i>he/him/his</i> una persona. Probá reemplazarlo en la oración: si se entiende, está bien.'),
    ('Antónimos y sinónimos', 'Te dan una palabra que <b>no</b> está en el texto y una línea: buscá en esa línea la palabra opuesta (antónimo) o equivalente (sinónimo), de la misma clase (sustantivo, verbo, adjetivo).'),
    ('Cuadro de conectores', 'Por cada conector: su traducción, el <b>tipo de relación</b> y las dos ideas que une (la de antes y la de después), resumidas en español.'),
    ('Título y verdadero o falso', 'El título es el que cubre <b>todo</b> el texto, ni más amplio ni más chico. En el verdadero o falso mirá los detalles: <i>any</i> = cualquier, no «ningún».'),
]
CONECTORES_TABLA = [
    ('Adición', 'and, also, moreover, in addition, as well as', 'y, también, además'),
    ('Contraste', 'but, however, although, while, whereas, yet', 'pero, sin embargo, aunque, mientras que'),
    ('Causa', 'because, since, as, due to, because of', 'porque, ya que, debido a'),
    ('Consecuencia', 'so, therefore, thus, consequently, this is why, as a result', 'así que, por lo tanto, por eso, como resultado'),
    ('Condición', 'if, unless, provided that', 'si, a menos que, siempre que'),
    ('Finalidad', 'to, in order to, so that', 'para, con el fin de, para que'),
    ('Ejemplificación', 'such as, for example, for instance, like', 'como, tales como, por ejemplo'),
    ('Tiempo', 'when, then, after, before, until, meanwhile', 'cuando, luego, después, antes, hasta, mientras tanto'),
]
PRONOMBRES = [
    ('it · its · itself', 'eso · su · sí mismo', 'algo singular'), ('they · them · their · themselves', 'ellos · los · sus · sí mismos', 'algo plural'),
    ('he · him · his', 'él · lo · su', 'un hombre'), ('she · her', 'ella · la, su', 'una mujer'),
    ('which · that', 'que · el cual', 'retoman el sustantivo de antes'), ('this · these', 'esto · estos', 'retoman una idea o algo cercano'),
]
PREFIJOS_TABLA = [
    ('un-', 'unable, unknown, unnecessary, unavailable'), ('in-', 'incorrect, invisible, inefficient, inaccessible'),
    ('im- (antes de p, b, m)', 'impossible, immobile'), ('il- (antes de l)', 'illegal'), ('ir- (antes de r)', 'irregular, irresponsible'),
    ('dis-', 'disconnected, disadvantage, disappear'), ('non-', 'non-renewable'), ('-ful ↔ -less', 'harmful ↔ harmless, useful ↔ useless, wired → wireless'),
]


def resumen_html(css_fuentes):
    tabla = lambda cab, filas: '<table><tr>' + ''.join(f'<th>{x}</th>' for x in cab) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in f) + '</tr>' for f in filas) + '</table>'
    c = ('<h1>Inglés 1 · Cómo se encara el parcial</h1><p class="bajada">Es de lectocomprensión: un texto técnico en inglés y ejercicios que se responden en español. '
         'Con 7 o más, la materia queda aprobada. Los parciales y las prácticas resueltos están en los otros archivos.</p>')
    c += '<h2>Cada ejercicio</h2>' + ''.join(f'<div class="paso"><span class="n">{i}</span><div><b class="t">{t}</b>{x}</div></div>' for i, (t, x) in enumerate(PASOS, 1))
    c += '<h2>Conectores y su relación</h2>' + tabla(['Relación', 'En inglés', 'En español'], [(f'<b>{a}</b>', f'<i>{b}</i>', x) for a, b, x in CONECTORES_TABLA])
    c += '<div class="tip"><b>Idea uno e idea dos:</b> la idea uno es lo que está antes del conector y la idea dos, lo que viene después. Se escriben resumidas y en español.</div>'
    c += '<h2>Pronombres (referencia contextual)</h2>' + tabla(['En inglés', 'En español', 'Reemplaza a…'], [(f'<i>{a}</i>', b, x) for a, b, x in PRONOMBRES])
    c += '<h2>Antónimos con prefijos y sufijos</h2>' + tabla(['Prefijo o sufijo', 'Ejemplos'], [(f'<b>{a}</b>', f'<i>{b}</i>') for a, b in PREFIJOS_TABLA])
    c += ('<h2>Frases nominales</h2><p>En inglés lo que describe va <b>antes</b> del sustantivo; en español, después. Encontrá el núcleo (el último sustantivo) y traducí de derecha a izquierda:</p>'
          + tabla(['En inglés', 'En español'], [(f'<i>{a}</i>', b) for a, b in (
              ('renewable energy sources', 'fuentes de energía renovable'), ('the self-generated clean energy trend', 'la tendencia de la energía limpia autogenerada'),
              ('short-range mobile transceivers', 'transceptores móviles de corto alcance'), ('host computer system', 'sistema informático huésped'),
              ('long-term investment', 'inversión a largo plazo'))]))
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Inglés 1 · Cómo se encara el parcial</title><style>{css_fuentes}{CSS}</style></head><body>{c}</body></html>'


# Los originales (en blanco) y cuántas hojas tienen: el PDF final es esas hojas + las resueltas
ORIGINALES = [
    ('02-parcial-2023-energia-renovable.pdf', 3, PARCIAL_2023),
    ('03-modelo-de-parcial-internet-de-las-cosas.pdf', 3, MODELO_IOT),
    ('04-practica-the-anatomy-of-a-virus.pdf', 3, PRACTICA_VIRUS),
]


def fuentes_css(carpeta):
    if not carpeta: return ''
    return ''.join(f"@font-face{{font-family:'Open Sans';font-weight:{p};src:url('file://{os.path.join(carpeta, f'open-sans-latin-{p}-normal.woff2')}') format('woff2')}}"
                   for p in (400, 600, 700) if os.path.exists(os.path.join(carpeta, f'open-sans-latin-{p}-normal.woff2')))


def imprimir(chromium, html_txt, pdf):
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, 'doc.html')
        open(h, 'w', encoding='utf-8').write(html_txt)
        subprocess.run([chromium, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--disable-background-networking',
                        '--no-first-run', f'--print-to-pdf={pdf}', 'file://' + h], check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', action='store_true')
    ap.add_argument('--fuente')
    a = ap.parse_args()
    q = armar_quiz()
    with open(os.path.join(RAIZ, 'quiz', 'ingles-1.json'), 'w', encoding='utf-8') as fh:
        json.dump(q, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print('práctica:', sum(len(s['preguntas']) for s in q['secciones']), 'ejercicios ·', ', '.join(f"{s['titulo']} {len(s['preguntas'])}" for s in q['secciones']))
    if not a.pdf:
        return
    import pymupdf
    chromium = next((c for c in (os.environ.get('CHROMIUM'), '/opt/pw-browsers/chromium', shutil.which('chromium')) if c and os.path.exists(c)), None)
    if not chromium: raise SystemExit('No encuentro Chromium (poné su ruta en la variable CHROMIUM).')
    css = fuentes_css(a.fuente)
    os.makedirs(DESTINO, exist_ok=True)
    meta = lambda t: {'title': t, 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': '', 'creationDate': '', 'modDate': ''}

    def guardar(doc, ruta, titulo):
        doc.set_metadata(meta(titulo))
        doc.save(ruta + '.tmp', garbage=3, deflate=True)
        doc.close()
        os.replace(ruta + '.tmp', ruta)

    with tempfile.TemporaryDirectory() as tmp:
        for nombre, html_txt, titulo in (('01-resumen-como-se-encara-el-parcial.pdf', resumen_html(css), 'Inglés 1 · Cómo se encara el parcial'),
                                         ('05-practica-del-campus-primera-ley-de-newton.pdf', doc_newton(css), f'Inglés 1 · {PRACTICA_NEWTON[0]}')):
            ruta = os.path.join(tmp, nombre)
            imprimir(chromium, html_txt, ruta)
            d = pymupdf.open(ruta)
            print(nombre, d.page_count, 'hojas')
            guardar(d, os.path.join(DESTINO, nombre), titulo)
        for nombre, hojas, doc in ORIGINALES:
            ruta = os.path.join(DESTINO, nombre)
            res = os.path.join(tmp, 'res.pdf')
            imprimir(chromium, doc_resuelto(doc, css), res)
            orig = pymupdf.open(ruta)
            final = pymupdf.open()
            final.insert_pdf(orig, to_page=hojas - 1)          # las hojas en blanco, tal cual
            final.insert_pdf(pymupdf.open(res))                # y a continuación, resuelto
            orig.close()
            print(nombre, final.page_count, 'hojas')
            guardar(final, ruta, f'Inglés 1 · {doc[0]}')


if __name__ == '__main__':
    main()
