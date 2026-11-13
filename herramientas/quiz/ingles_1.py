#!/usr/bin/env python3
"""Inglés 1: arma el quiz (quiz/ingles-1.json) y la guía con todo resuelto (material/ingles-1/01-guia-del-parcial-resuelta.pdf).

El parcial es de lectocomprensión: un texto técnico en inglés y ejercicios que se responden en español
(preguntas, traducción de frases, referencia contextual, antónimos, sinónimos y conectores).
De dónde sale cada pregunta:
- El parcial 2023 (texto sobre empresas que generan su propia energía renovable).
- El modelo de parcial que dio la profe antes de empezar (texto sobre Internet de las cosas).
- La práctica de clase del 7 de septiembre de 2023 (The anatomy of a virus).
- La práctica del campus «Práctica primer parcial» (texto sobre la primera ley de Newton). Del campus solo se pasan
  las consignas; la impresión no se publica.
Las respuestas son nuestras: en el material no venía la corrección.

Uso, desde la raíz del repo:
  python3 herramientas/quiz/ingles_1.py                                   (el quiz)
  python3 herramientas/quiz/ingles_1.py --pdf --fuente CARPETA_OPEN_SANS  (además, la guía en PDF)
"""
import argparse, html, json, os, shutil, subprocess, tempfile

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

PARCIAL = 'Parcial 2023 · Energía renovable'
MODELO = 'Modelo de parcial · Internet de las cosas'
VIRUS = 'Práctica de clase · The anatomy of a virus'
CAMPUS = 'Práctica del campus · Primera ley de Newton'


def frag(t):
    return f'<i>«{t}»</i>'


def abierta(sec, fuente, en, modelo, ex=None):
    q = dict(sec=sec, tipo='modelo', en=en, modelo=modelo, fuente=fuente)
    if ex: q['ex'] = ex
    return q


def opcion(sec, fuente, en, ops, bien, ex, vf=False):
    q = dict(sec=sec, tipo='una', en=en, op=[[o, i == bien] for i, o in enumerate(ops)], ex=ex, fuente=fuente)
    if vf: q['vf'] = True
    return q


def conector(fuente, nombre, linea, cita, trad, rel, idea1, idea2):
    en = f'Completá el cuadro de conectores para <b>{nombre}</b>{f" (línea {linea})" if linea else ""}: traducción, tipo de relación, idea uno e idea dos.<br>{frag(cita)}'
    modelo = f'<b>Traducción:</b> {trad}<br><b>Relación:</b> {rel}<br><b>Idea uno:</b> {idea1}<br><b>Idea dos:</b> {idea2}'
    return abierta('con', fuente, en, modelo)


def referente(fuente, palabra, linea, cita, resp, ex=None):
    en = f'Referencia contextual: ¿a qué o a quién se refiere <b>{palabra}</b>{f" (línea {linea})" if linea else ""}?<br>{frag(cita)}'
    return abierta('ref', fuente, en, resp, ex)


def traducir(fuente, ingles, resp, ex=None):
    return abierta('trad', fuente, f'Traducí al español: <b>{ingles}</b>', resp, ex)


PREGUNTAS = [
    # ───────────── Parcial 2023 · Energía renovable ─────────────
    abierta('comp', PARCIAL, '¿Qué puede llegar a pasar en la transición entre la energía tradicional y la energía sustentable? (Respondé en español.)<br>'
            + frag('Meanwhile, as we switch from cheap, accessible, traditional energy to green energy, there’s a real possibility that clean electricity could become scarce.'),
            'Que la <b>electricidad limpia se vuelva escasa</b>: al pasar de la energía tradicional (barata y accesible) a la energía verde puede faltar electricidad limpia. Por eso las empresas buscan asegurarse su propio suministro.',
            'La respuesta está en las líneas 6 y 7. Se contesta con tus palabras y en español: no se copia la oración en inglés.'),
    traducir(PARCIAL, 'Energy resources scarcity is a concerning issue.', 'La escasez de recursos energéticos es un tema preocupante.',
             '<i>Energy resources scarcity</i> es una frase nominal: el núcleo (<i>scarcity</i>) va al final en inglés y primero en español.'),
    traducir(PARCIAL, 'There is every reason to believe that society will continue to use more and more machines and devices.',
             'Hay todas las razones para creer que la sociedad seguirá usando cada vez más máquinas y dispositivos.',
             '<i>more and more</i> = cada vez más.'),
    traducir(PARCIAL, 'The self-generated clean energy trend', 'La tendencia de la energía limpia autogenerada.',
             'Frase nominal: se lee de derecha a izquierda. Núcleo <i>trend</i> (tendencia) → de la energía (<i>energy</i>) → limpia (<i>clean</i>) → autogenerada (<i>self-generated</i>).'),
    traducir(PARCIAL, 'Installing your own energy production is a long-term investment', 'Instalar tu propia producción de energía es una inversión a largo plazo.'),
    referente(PARCIAL, 'THEMSELVES', 3, '…companies are looking for opportunities to operate independently of the energy grid by generating renewable energy themselves…',
              '<b>Companies</b> (las empresas).', 'Pronombre reflexivo plural: busca hacia atrás un sustantivo en plural.'),
    referente(PARCIAL, 'THEIR', 9, '…companies are looking to secure their own electricity supply for the future.', '<b>Companies</b> (las empresas): su propio suministro.'),
    referente(PARCIAL, 'WHICH', 13, 'One of the trailblazers was Swedish flat-pack furniture emporium IKEA, which started placing solar panels…', '<b>IKEA</b>.'),
    referente(PARCIAL, 'ITS', 14, '…started placing solar panels on the roofs of its buildings in 2011 in order to help reduce its carbon footprint.', '<b>IKEA</b>: sus edificios, su huella de carbono.'),
    referente(PARCIAL, 'WHICH', 20, '…around 75,000 square metres of solar arrays, which provide 75 percent of the building’s daytime electricity.', '<b>Solar arrays</b> (los paneles solares).'),
    referente(PARCIAL, 'HE', 27, '“…to differentiate themselves from the competition,” he says.', '<b>Mats Alvem</b> (el gerente ambiental de Sandvik).'),
    abierta('ant', PARCIAL, 'Antónimo en el texto de <b>ABUNDANCE</b> (línea 1).<br>' + frag('Energy resource scarcity is a concerning issue.'), '<b>Scarcity</b> (escasez).'),
    abierta('ant', PARCIAL, 'Antónimo en el texto de <b>FINISHED</b> (línea 11).<br>' + frag('The self-generated clean energy trend began among B2C corporations about a decade ago.'), '<b>Began</b> (empezó).'),
    abierta('ant', PARCIAL, 'Antónimo en el texto de <b>WEAK</b> (línea 28).<br>' + frag('…having a strong sustainability profile is good for your reputation…'), '<b>Strong</b> (fuerte).'),
    abierta('ant', PARCIAL, 'Sinónimo en el texto de <b>GUARANTEE</b> (línea 9).<br>' + frag('…companies are looking to secure their own electricity supply for the future.'), '<b>Secure</b> (asegurar).'),
    abierta('ant', PARCIAL, 'Sinónimo en el texto de <b>REPORTED</b> (línea 15).<br>' + frag('In 2019, the retail giant announced its investment in two large solar power plants…'), '<b>Announced</b> (anunció).'),
    abierta('ant', PARCIAL, 'Sinónimo en el texto de <b>ULTRA MODERN</b> (línea 19).<br>' + frag('Apart from providing state-of-the-art facilities for as many as 13,000 employees…'), '<b>State-of-the-art</b> (de última generación).'),
    conector(PARCIAL, 'THEREFORE', 5, 'There is every reason to believe that society will continue to use more and more machines and devices, therefore consuming more electricity.',
             'por lo tanto', 'consecuencia', 'la sociedad va a seguir usando cada vez más máquinas y dispositivos', 'va a consumir más electricidad'),
    conector(PARCIAL, 'THIS IS WHY', 7, '…there’s a real possibility that clean electricity could become scarce. This is why, apart from the obvious benefits […], companies are looking to secure their own electricity supply…',
             'es por esto que / por eso', 'consecuencia (causa → efecto)', 'la electricidad limpia podría volverse escasa', 'las empresas buscan asegurar su propio suministro de electricidad'),
    conector(PARCIAL, 'IN ORDER TO', 14, '…IKEA, which started placing solar panels on the roofs of its buildings in 2011 in order to help reduce its carbon footprint.',
             'para / con el fin de', 'finalidad (propósito)', 'IKEA empezó a poner paneles solares en los techos de sus edificios', 'ayudar a reducir su huella de carbono'),
    conector(PARCIAL, 'SUCH AS', 23, 'It is no coincidence that leading retailers such as Apple and IKEA were among the first to blaze the self-generated energy trail.',
             'como / tales como', 'ejemplificación', 'los grandes minoristas fueron de los primeros en generar su propia energía', 'Apple e IKEA'),
    # ───────────── Modelo de parcial · Internet de las cosas ─────────────
    abierta('comp', MODELO, '¿Cuáles son las preocupaciones respecto al crecimiento de los productos y las tecnologías de IoT? (Respondé en español.)<br>'
            + frag('There are a number of concerns about the risks in the growth of IoT technologies and products, especially in the areas of privacy and security…'),
            'Los <b>riesgos en la privacidad y la seguridad</b>. Por eso la industria y los gobiernos empezaron a desarrollar normas internacionales y locales, guías y marcos regulatorios.'),
    traducir(MODELO, 'Processing ability', 'Capacidad de procesamiento.'),
    traducir(MODELO, 'Increasingly powerful embedded systems', 'Sistemas embebidos cada vez más potentes.',
             '<i>increasingly</i> + adjetivo = cada vez más + adjetivo. El núcleo es <i>systems</i>.'),
    traducir(MODELO, 'The concept of the “smart home”', 'El concepto de «casa inteligente».'),
    traducir(MODELO, 'Short-range mobile transceivers', 'Transceptores móviles de corto alcance.',
             'Un <i>transceiver</i> es un transmisor-receptor (transceptor). Núcleo al final: <i>transceivers</i>.'),
    referente(MODELO, 'THAT', 2, '…physical objects (or groups of such objects) with sensors, processing ability, software and other technologies that connect and exchange data with other devices…',
              'A los <b>objetos físicos</b> (con sus sensores, su software y sus otras tecnologías): son los que se conectan e intercambian datos.',
              'Si la consigna pide la palabra más cercana, es <i>technologies</i>. Leé la oración completa: lo que se conecta son los objetos.'),
    referente(MODELO, 'THEY', 4, '…devices do not need to be connected to the public internet, they only need to be connected to a network…', '<b>Devices</b> (los dispositivos).'),
    referente(MODELO, 'ITSELF', 17, 'The concept of the “Internet of things” and the term itself, first appeared in a speech by Peter T. Lewis…', 'Al <b>término «Internet of things»</b>.'),
    referente(MODELO, 'HIM', 19, 'According to him, “The Internet of Things, or IoT, is the integration of people, processes and technology…”', '<b>Peter T. Lewis</b>.'),
    referente(MODELO, 'HE', 22, 'The term “Internet of things” was coined independently by Kevin Ashton, in 1999, though he prefers the phrase “Internet for things”.', '<b>Kevin Ashton</b>.'),
    referente(MODELO, 'THEMSELVES', 26, '…new forms of communication between people and things, and between things themselves.', '<b>Things</b> (las cosas).'),
    conector(MODELO, 'DUE TO', 6, 'The field has evolved due to the convergence of multiple technologies…',
             'debido a', 'causa', 'el campo (de la IoT) evolucionó', 'la convergencia de múltiples tecnologías'),
    conector(MODELO, 'SUCH AS', 12, '…can be controlled via devices associated with that ecosystem, such as smartphones and smart speakers.',
             'como / tales como', 'ejemplificación', 'dispositivos asociados a ese ecosistema', 'teléfonos inteligentes y parlantes inteligentes'),
    # ───────────── Práctica de clase · The anatomy of a virus ─────────────
    abierta('comp', VIRUS, 'How are computer viruses like biological viruses? (Respondé en español.)',
            'Los dos son muy pequeños, <b>infectan a un huésped</b> (una célula o un sistema informático), <b>usan sus recursos para reproducirse</b> y muchas veces le causan daño.'),
    abierta('comp', VIRUS, 'What is the effect of a virus patching the operating system? (Respondé en español.)',
            'Le permite <b>detectar los archivos de programa</b> (como los COM o EXE) para después copiarse dentro de ellos.'),
    abierta('comp', VIRUS, 'Why are some viruses designed to be loaded into memory? (Respondé en español.)',
            'Para <b>quedar residentes en memoria</b> y, desde ahí, infectar otros programas con su rutina de reproducción hasta que se apague la computadora.'),
    abierta('comp', VIRUS, 'What examples of payload does the writer of the text provide? (Respondé en español.)',
            'Uno <b>inofensivo</b>: mostrar un mensaje en el monitor. Uno <b>destructivo</b>: borrar archivos del disco rígido.'),
    abierta('comp', VIRUS, 'How does a Trojan differ from a virus? (Respondé en español.)',
            'El <b>troyano</b> tiene payload (la parte que hace algo) pero <b>no tiene rutina de reproducción</b>: no se copia a otros programas.'),
    opcion('comp', VIRUS, 'Uní la rutina con su función. <b>MISDIRECTION</b>:', ['Does the damage', 'Attaches a copy of itself to another program', 'Hides the presence of the code', 'Decides when and how to activate the payload'], 2,
           '<i>Misdirection</i> = despiste: la rutina que <b>esconde</b> al virus.'),
    opcion('comp', VIRUS, 'Uní la rutina con su función. <b>REPRODUCTION</b>:', ['Does the damage', 'Attaches a copy of itself to another program', 'Hides the presence of the code', 'Decides when and how to activate the payload'], 1,
           'La reproducción es la que <b>copia</b> al virus en otro programa. Es la única que necesita para ser virus.'),
    opcion('comp', VIRUS, 'Uní la rutina con su función. <b>TRIGGER</b>:', ['Does the damage', 'Attaches a copy of itself to another program', 'Hides the presence of the code', 'Decides when and how to activate the payload'], 3,
           '<i>Trigger</i> = disparador: <b>decide cuándo</b> se activa el payload (una fecha, una tecla…).'),
    opcion('comp', VIRUS, 'Uní la rutina con su función. <b>PAYLOAD</b>:', ['Does the damage', 'Attaches a copy of itself to another program', 'Hides the presence of the code', 'Decides when and how to activate the payload'], 0,
           'El payload es la carga: lo que <b>hace el daño</b> (o la broma).'),
    conector(VIRUS, 'SUCH AS', None, 'It often does this by patching the operating system to enable it to detect program files, such as COM or EXE files.',
             'como / tales como', 'ejemplificación', 'archivos de programa', 'archivos COM o EXE'),
    conector(VIRUS, 'ALSO', None, 'This virus may also contain a payload that remains dormant until a trigger event activates it…',
             'también', 'adición', 'el virus se queda en memoria e infecta otros programas', 'puede contener un payload'),
    conector(VIRUS, 'TO', None, 'To be a virus, a program only needs to have a reproduction routine that enables it to infect other programs.',
             'para', 'finalidad (propósito)', 'ser un virus', 'un programa solo necesita una rutina de reproducción'),
    conector(VIRUS, 'BUT', None, 'A program that has a payload but does not have a reproduction routine is known as a Trojan.',
             'pero', 'contraste', 'el programa tiene un payload', 'no tiene rutina de reproducción'),
    referente(VIRUS, 'ITSELF', None, 'A biological virus is a very small, simple organism that infects living cells […] by attaching itself to them…', 'Al <b>virus biológico</b>.'),
    referente(VIRUS, 'THEM', None, '…infects living cells, known as the host, by attaching itself to them and using them to reproduce itself.', 'A las <b>living cells</b> (las células vivas, el huésped).'),
    referente(VIRUS, 'ITS', None, '…a computer virus is a very small program, routine that infects a computer system and uses its resources to reproduce itself.', 'Al <b>sistema informático</b> (usa los recursos del sistema).'),
    referente(VIRUS, 'IT', None, 'When the user runs an infected program, it is loaded into memory carrying the virus.', 'Al <b>programa infectado</b>.'),
    referente(VIRUS, 'WHICH', None, 'The virus then returns control to the host program which then continues with its normal sequence of instructions…', 'Al <b>host program</b> (el programa huésped).'),
    traducir(VIRUS, 'host computer system', 'Sistema informático huésped (anfitrión).'),
    traducir(VIRUS, 'common programming techniques', 'Técnicas de programación comunes.'),
    traducir(VIRUS, 'normal sequence of instructions', 'Secuencia normal de instrucciones.'),
    traducir(VIRUS, 'harmless joke', 'Broma inofensiva.'),
    traducir(VIRUS, 'deleting files on the hard disk', 'Borrar archivos del disco rígido.'),
    # ───────────── Práctica del campus · Primera ley de Newton ─────────────
    abierta('con', CAMPUS, 'Identificá el nexo lógico y la relación lógica.<br>' + frag('Newton’s First Law states that an object will remain at rest or in uniform motion in a straight line unless acted upon by an external force.'),
            '<b>UNLESS</b> («a menos que»): <b>condición</b>.', 'En el fragmento también aparece AND («y»), que suma una idea: adición.'),
    abierta('con', CAMPUS, 'Identificá el nexo lógico y la relación lógica.<br>' + frag('…objects will remain in their state of motion unless a force acts to change the motion.'),
            '<b>UNLESS</b> («a menos que»): <b>condición</b>.'),
    abierta('con', CAMPUS, 'Identificá el nexo lógico y la relación lógica.<br>' + frag('The statement of these laws must be generalized if you are dealing with a rotating reference frame or any frame which is accelerating.'),
            '<b>IF</b> («si»): <b>condición</b>.', 'También aparece OR («o»): alternativa.'),
    abierta('con', CAMPUS, 'Identificá el nexo lógico y la relación lógica.<br>' + frag('If an object is at rest in one frame of reference, it will appear to be moving in a straight line to an observer in a reference frame which is moving by the object.'),
            '<b>IF</b> («si»): <b>condición</b>.'),
    abierta('con', CAMPUS, 'Identificá el nexo lógico y la relación lógica.<br>' + frag('There is no way to say which reference frame is “special”, so all constant velocity reference frames must be equivalent.'),
            '<b>SO</b> («por lo tanto», «así que»): <b>consecuencia</b>.'),
    opcion('comp', CAMPUS, 'Elegí el mejor título para el texto sobre la primera ley de Newton (inercia, marcos de referencia inerciales y simetría del universo).',
           ['La primera ley de Newton', 'Las fuerzas que actúan sobre el movimiento', 'El movimiento uniforme de los objetos', 'Las leyes de Newton'], 0,
           'Los tres párrafos hablan de la <b>primera ley</b>: la segunda aparece solo para compararla. «Las leyes de Newton» es demasiado amplio y los otros dos son temas puntuales.'),
    abierta('ant', CAMPUS, 'Antónimo en el texto de <b>CURVED</b> (línea 2).<br>' + frag('…remain at rest or in uniform motion in a straight line unless acted upon by an external force.'), '<b>Straight</b> (recto).'),
    abierta('ant', CAMPUS, 'Antónimo en el texto de <b>COMMONPLACE</b> (línea 5).<br>' + frag('The First Law could be viewed as just a special case of the Second Law…'), '<b>Special</b> (especial).'),
    abierta('ant', CAMPUS, 'Antónimo en el texto de <b>RESTING</b> (línea 4).<br>' + frag('…to an observer in a reference frame which is moving by the object.'), '<b>Moving</b> (en movimiento).'),
    abierta('ant', CAMPUS, 'Antónimo en el texto de <b>STILLNESS</b> (línea 5).<br>' + frag('…a state of motion in a straight line must be just as “natural” as being at rest. […] so all constant velocity reference frames must be equivalent.'),
            '<b>Velocity</b> (velocidad), la palabra de la línea 5. También es antónimo <i>motion</i> (movimiento), de la línea 2.'),
    referente(CAMPUS, 'THEIR', None, '…that objects will remain in their state of motion unless a force acts to change the motion.', '<b>Objects</b> (los objetos).'),
    referente(CAMPUS, 'FOR WHICH', None, 'The First Law could be viewed as just a special case of the Second Law for which the net external force is zero…',
              'Al <b>special case</b> (el caso especial de la segunda ley): el caso en el que la fuerza externa neta es cero.'),
    referente(CAMPUS, 'IT', None, 'If an object is at rest in one frame of reference, it will appear to be moving in a straight line…', '<b>An object</b> (el objeto).'),
    opcion('comp', CAMPUS, '¿Verdadero o falso? «A menos que una fuerza externa actúe sobre un objeto, el mismo permanecerá en reposo o en movimiento uniforme en línea recta.»<br>'
           + frag('…an object will remain at rest or in uniform motion in a straight line unless acted upon by an external force.'), ['Verdadero', 'Falso'], 0,
           'Es la traducción de la primera oración: <i>unless</i> = a menos que.', vf=True),
    opcion('comp', CAMPUS, '¿Verdadero o falso? «Ningún cambio de movimiento involucra una aceleración, por eso aplica la segunda ley de Newton.»<br>'
           + frag('Any change in motion involves an acceleration, and then Newton’s Second Law applies.'), ['Verdadero', 'Falso'], 1,
           '<i>Any change</i> = <b>cualquier</b> cambio (no «ningún»): todo cambio de movimiento involucra una aceleración.', vf=True),
    opcion('comp', CAMPUS, '¿Verdadero o falso? «El marco inercial es aquel marco de referencia que se asume no experimenta aceleración.»<br>'
           + frag('…a reference frame which is not itself accelerating. Such a frame is often referred to as an “inertial frame”.'), ['Verdadero', 'Falso'], 0,
           '<i>Such a frame</i> retoma «un marco de referencia que no está acelerando»: a eso se le llama marco inercial.', vf=True),
]

SECCIONES = [
    ('comp', 'Comprensión del texto'),
    ('trad', 'Traducción'),
    ('ref', 'Referencia contextual'),
    ('ant', 'Antónimos y sinónimos'),
    ('con', 'Conectores (nexos lógicos)'),
]

GLOSARIO = [
    dict(t='Lectocomprensión', que='Leer un texto técnico en inglés y demostrar que lo entendiste respondiendo <b>en español</b>. No se pide hablar ni escribir en inglés.', re=r'Respondé en español|título|Verdadero o falso|Uní la rutina'),
    dict(t='Frase nominal', que='Un grupo de palabras cuyo núcleo es un sustantivo. En inglés los modificadores van <b>antes</b> del núcleo; en español, después: se traduce de derecha a izquierda (<i>host computer system</i> → sistema informático huésped).', re=r'Traducí'),
    dict(t='Referencia contextual', que='Encontrar a qué o a quién reemplaza un pronombre. Casi siempre está <b>antes</b>, en la misma oración o en la anterior. Fijate el número: si el pronombre es plural (<i>they, them, their, themselves</i>), el referente también.', re=r'Referencia contextual'),
    dict(t='Pronombres', que='<i>it / its / itself</i>: eso, su, sí mismo (algo singular). <i>they / them / their / themselves</i>: ellos, sus, sí mismos (plural). <i>he / him</i>: él (una persona). <i>which / that</i>: que, el cual (retoman el sustantivo de antes).', re=r'se refiere\s+(FOR WHICH|ITSELF|ITS|IT|THEY|THEM|THEIR|THEMSELVES|HE|HIM|WHICH|THAT)\b'),
    dict(t='Antónimo y sinónimo', que='El antónimo es la palabra de significado <b>opuesto</b> (<i>weak</i> ↔ <i>strong</i>); el sinónimo, la de significado <b>parecido</b> (<i>guarantee</i> ≈ <i>secure</i>). Hay que encontrarlo en el texto, en la línea que indican.', re=r'Antónimo|Sinónimo'),
    dict(t='Conector (nexo lógico)', que='La palabra que une dos ideas y dice cómo se relacionan. En el cuadro se completa: traducción, tipo de relación, idea uno (la de antes) e idea dos (la de después).', re=r'conector|nexo lógico', i=True),
    dict(t='Relaciones lógicas', que='<b>Adición</b>: and, also, moreover. <b>Contraste</b>: but, however, although. <b>Causa</b>: because, since, due to. <b>Consecuencia</b>: so, therefore, this is why. <b>Condición</b>: if, unless. <b>Finalidad</b>: to, in order to. <b>Ejemplificación</b>: such as, for example.', re=r'relación', i=True),
    dict(t='Unless / If', que='Condición. <i>if</i> = si; <i>unless</i> = a menos que (si no).', re=r'UNLESS|IF\b|\bunless\b'),
    dict(t='So / Therefore / This is why', que='Consecuencia: lo que viene después es el resultado de lo anterior. <i>so</i> = así que; <i>therefore</i> = por lo tanto; <i>this is why</i> = por eso.', re=r'\bSO\b|THEREFORE|THIS IS WHY'),
    dict(t='In order to / To', que='Finalidad (propósito): para, con el fin de.', re=r'para\s+(IN ORDER TO|TO)\b'),
    dict(t='Such as', que='Ejemplificación: como, tales como. La idea dos son los ejemplos.', re=r'SUCH AS'),
    dict(t='Due to', que='Causa: debido a. La idea dos es la causa de la idea uno.', re=r'DUE TO'),
    dict(t='But / Also', que='<i>but</i> = pero (contraste); <i>also</i> = también (adición).', re=r'para\s+(BUT|ALSO)\b'),
    dict(t='Virus, payload y troyano', que='<b>Payload</b>: la carga, lo que hace el virus (una broma o un daño). <b>Trigger</b>: lo que dispara el payload. <b>Trojan</b> (troyano): programa con payload pero sin rutina para copiarse.', re=r'virus|payload|Trojan|MISDIRECTION|REPRODUCTION|TRIGGER|PAYLOAD|host|harmless|hard disk', i=True),
    dict(t='Primera ley de Newton', que='Un objeto sigue en reposo o en movimiento rectilíneo uniforme a menos que una fuerza externa actúe sobre él (inercia). Un <b>marco inercial</b> es un sistema de referencia que no está acelerando.', re=r'Newton|inercial|frame|at rest|motion', i=True),
    dict(t='Internet de las cosas', sig='IoT · Internet of things', que='Objetos físicos con sensores, software y conectividad que intercambian datos por una red. <i>Embedded system</i>: sistema embebido; <i>transceiver</i>: transceptor (transmisor-receptor).', re=r'IoT|Internet of things|devices|embedded|transceivers|smart home|Processing ability|Lewis|Ashton|things themselves', i=True),
    dict(t='Energía renovable', que='<i>Scarcity</i>: escasez. <i>Renewable / clean / green energy</i>: energía renovable, limpia, verde. <i>Solar arrays</i>: paneles solares. <i>Carbon footprint</i>: huella de carbono.', re=r'energy|electricity|scarcity|solar|IKEA|Alvem|began|announced|state-of-the-art|ABUNDANCE|WEAK|GUARANTEE', i=True),
]


def armar_quiz():
    porsec = {k: [] for k, _ in SECCIONES}
    for q in PREGUNTAS:
        porsec[q['sec']].append({k: v for k, v in q.items() if k != 'sec'})
    return dict(
        titulo='Inglés 1 · Parcial',
        descripcion='Los ejercicios del parcial 2023, del modelo de parcial, de la práctica de clase y de la práctica del campus, con la respuesta. Las preguntas abiertas: respondé primero y después mirá.',
        secciones=[dict(titulo=t, preguntas=porsec[k]) for k, t in SECCIONES if porsec[k]],
        glosario=[{k: v for k, v in g.items()} for g in GLOSARIO],
    )


# ───────────────────────── La guía en PDF ─────────────────────────
CSS = '''
@page { size: A4; margin: 15mm 15mm 15mm; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; box-sizing: border-box; }
body { font-family: 'Open Sans', 'DejaVu Sans', sans-serif; font-size: 9.6pt; line-height: 1.45; color: #1f1e1c; margin: 0; }
h1 { font-family: Georgia, 'DejaVu Serif', serif; font-weight: 400; font-size: 22pt; margin: 0 0 2pt; }
.bajada { color: #5b5a54; margin: 0 0 10pt; font-size: 10pt; }
h2 { font-family: Georgia, 'DejaVu Serif', serif; font-weight: 400; font-size: 14.5pt; margin: 16pt 0 5pt; padding-top: 6pt; border-top: 1px solid #e3e1da; break-after: avoid; }
h3 { font-size: 10.5pt; margin: 10pt 0 3pt; break-after: avoid; }
table { width: 100%; border-collapse: collapse; margin: 3pt 0 8pt; font-size: 9pt; break-inside: avoid; }
th, td { text-align: left; padding: 3.5pt 6pt; border-bottom: 1px solid #e3e1da; vertical-align: top; }
th { background: #f3f2ee; }
.paso { display: grid; grid-template-columns: 22pt 1fr; gap: 6pt; margin: 5pt 0; break-inside: avoid; }
.paso .n { width: 18pt; height: 18pt; border-radius: 50%; background: #2d8992; color: #fff; font-weight: 700; text-align: center; line-height: 18pt; font-size: 9pt; }
.paso b.t { display: block; }
.caso { border-bottom: 1px dashed #e3e1da; padding: 4pt 0 5pt; break-inside: avoid; }
.caso .r { margin-top: 2pt; }
.caso .ex { color: #5b5a54; font-size: 8.8pt; margin-top: 1pt; }
.f { font-size: 8pt; text-transform: uppercase; letter-spacing: .06em; color: #7c7b75; font-weight: 700; }
.tip { background: #e4f3f5; border-left: 3pt solid #2d8992; border-radius: 4pt; padding: 5pt 9pt; margin: 4pt 0 8pt; break-inside: avoid; }
i { color: #46453f; }
'''

PASOS = [
    ('Preguntas de comprensión', 'Buscá en el texto el párrafo que habla de lo que preguntan y respondé <b>en español y con tus palabras</b>. No copies la oración en inglés.'),
    ('Traducción de frases', 'Casi siempre son frases nominales: encontrá el <b>núcleo</b> (el último sustantivo) y traducí de derecha a izquierda. <i>Increasingly powerful embedded systems</i> → sistemas embebidos cada vez más potentes.'),
    ('Referencia contextual', 'Buscá <b>hacia atrás</b> el sustantivo que el pronombre reemplaza, respetando el número: <i>it/its</i> singular, <i>they/them/their</i> plural, <i>he/him</i> una persona. Probá reemplazarlo en la oración: si se entiende, está bien.'),
    ('Antónimos y sinónimos', 'Te dan una palabra que <b>no</b> está en el texto y una línea: buscá en esa línea la palabra opuesta (antónimo) o equivalente (sinónimo). Es la que tiene la misma clase (sustantivo, verbo, adjetivo).'),
    ('Cuadro de conectores', 'Por cada conector: su traducción, el <b>tipo de relación</b> y las dos ideas que une (la de antes y la de después), resumidas en español.'),
    ('Título y verdadero o falso', 'En la práctica del campus también hay que elegir el título (el que cubre <b>todo</b> el texto, ni más amplio ni más chico) y decir si una oración en español dice lo mismo que el texto: mirá los detalles (<i>any</i> = cualquier, no «ningún»).'),
]

CONECTORES = [
    ('Adición', 'and, also, moreover, in addition, as well as', 'y, también, además'),
    ('Contraste', 'but, however, although, while, whereas, yet', 'pero, sin embargo, aunque, mientras que'),
    ('Causa', 'because, since, as, due to, because of', 'porque, ya que, debido a'),
    ('Consecuencia', 'so, therefore, thus, consequently, this is why', 'así que, por lo tanto, por eso'),
    ('Condición', 'if, unless, provided that', 'si, a menos que, siempre que'),
    ('Finalidad', 'to, in order to, so that', 'para, con el fin de, para que'),
    ('Ejemplificación', 'such as, for example, for instance, like', 'como, tales como, por ejemplo'),
    ('Tiempo / secuencia', 'when, then, after, before, until, meanwhile', 'cuando, luego, después, antes, hasta, mientras tanto'),
]


def guia_html(css_fuentes):
    e = html.escape
    c = '<h1>Inglés 1 · El parcial</h1><p class="bajada">Es de lectocomprensión: un texto técnico en inglés y ejercicios que se responden en español. Con 7 o más, la materia queda aprobada. Acá está cómo se encara cada ejercicio, los conectores que más salen y todo el material resuelto.</p>'
    c += '<h2>Cómo se encara cada ejercicio</h2>' + ''.join(f'<div class="paso"><span class="n">{i}</span><div><b class="t">{t}</b>{x}</div></div>' for i, (t, x) in enumerate(PASOS, 1))
    c += '<h2>Los conectores y su relación</h2><table><tr><th>Relación</th><th>En inglés</th><th>En español</th></tr>' + ''.join(f'<tr><td><b>{a}</b></td><td><i>{b}</i></td><td>{x}</td></tr>' for a, b, x in CONECTORES) + '</table>'
    c += '<div class="tip"><b>Idea uno e idea dos:</b> la idea uno es lo que está antes del conector y la idea dos, lo que viene después. Se escriben resumidas y en español.</div>'
    for fuente, titulo in ((PARCIAL, 'El parcial 2023 resuelto'), (MODELO, 'El modelo de parcial resuelto'), (VIRUS, 'La práctica de clase resuelta'), (CAMPUS, 'La práctica del campus resuelta')):
        c += f'<h2>{titulo}</h2><p class="f">{e(fuente)}</p>'
        for k, sec in SECCIONES:
            qs = [q for q in PREGUNTAS if q['fuente'] == fuente and q['sec'] == k]
            if not qs: continue
            c += f'<h3>{sec}</h3>'
            for q in qs:
                if q['tipo'] == 'modelo':
                    r = q['modelo']
                else:
                    r = next(o for o, b in q['op'] if b)
                c += f'<div class="caso"><div>{q["en"]}</div><div class="r"><b>→</b> {r}</div>' + (f'<div class="ex">{q["ex"]}</div>' if q.get('ex') else '') + '</div>'
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Inglés 1 · El parcial, resuelto</title>'
            f'<style>{css_fuentes}{CSS}</style></head><body>{c}</body></html>')


def fuentes_css(carpeta):
    if not carpeta: return ''
    return ''.join(f"@font-face{{font-family:'Open Sans';font-weight:{p};src:url('file://{os.path.join(carpeta, f'open-sans-latin-{p}-normal.woff2')}') format('woff2')}}"
                   for p in (400, 600, 700) if os.path.exists(os.path.join(carpeta, f'open-sans-latin-{p}-normal.woff2')))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', action='store_true')
    ap.add_argument('--fuente')
    a = ap.parse_args()
    q = armar_quiz()
    with open(os.path.join(RAIZ, 'quiz', 'ingles-1.json'), 'w', encoding='utf-8') as fh:
        json.dump(q, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print('quiz:', sum(len(s['preguntas']) for s in q['secciones']), 'preguntas ·', ', '.join(f"{s['titulo']} {len(s['preguntas'])}" for s in q['secciones']))
    if a.pdf:
        chromium = next((c for c in (os.environ.get('CHROMIUM'), '/opt/pw-browsers/chromium', shutil.which('chromium')) if c and os.path.exists(c)), None)
        if not chromium: raise SystemExit('No encuentro Chromium (poné su ruta en la variable CHROMIUM).')
        destino = os.path.join(RAIZ, 'material', 'ingles-1')
        os.makedirs(destino, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            h = os.path.join(tmp, 'guia.html')
            open(h, 'w', encoding='utf-8').write(guia_html(fuentes_css(a.fuente)))
            pdf = os.path.join(destino, '01-guia-del-parcial-resuelta.pdf')
            subprocess.run([chromium, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--disable-background-networking',
                            '--no-first-run', f'--print-to-pdf={pdf}', 'file://' + h], check=True, capture_output=True)
        print('guía:', pdf)


if __name__ == '__main__':
    main()
