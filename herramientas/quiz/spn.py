#!/usr/bin/env python3
"""Sistemas y Procesos de Negocio (SPN): la práctica de los dos parciales y los recuperatorios 2023 resueltos.

- 1º Parcial (Unidad 1, Teoría General de Sistemas): quiz/spn-1er-parcial.json. Teoría (de práctica) y el caso
  SEMYBAL del recuperatorio 2023 (objetivo, ambiente, recursos, entradas, alcances y salidas).
- 2º Parcial (Unidades 2 y 3: organización, procesos y sistemas de información): quiz/spn-2do-parcial.json.
  Las preguntas del cuestionario teórico-práctico del recuperatorio 2023 del campus, con la clave del campus
  (de la revisión del intento solo se pasan los enunciados y las respuestas correctas; la impresión no se publica),
  y otras de práctica sobre la teoría.
- Los recuperatorios 2023 (SEMYBAL y Todo Casa) quedan en un PDF: primero el enunciado tal cual y a continuación
  resuelto, con el mapa de procesos, el diagrama de estructura básica y el de secuencia de actividades dibujados como
  en el simulacro de la cátedra. Las respuestas son nuestras (en lo que preguntó el campus, coinciden con su clave).

Uso, desde la raíz del repo:
  python3 herramientas/quiz/spn.py                                   (las prácticas)
  python3 herramientas/quiz/spn.py --pdf --fuente CARPETA_OPEN_SANS  (además, los recuperatorios resueltos)
"""
import argparse, html, json, os, random, shutil, subprocess, tempfile, zlib

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
DESTINO = os.path.join(RAIZ, 'material', 'sistemas-y-procesos-de-negocio')
REC = 'Recuperatorio 2023'


def barajar(en, ops):
    """El quiz muestra las opciones en el orden del JSON: se mezclan acá, siempre igual para cada pregunta"""
    ops = list(ops)
    random.Random(zlib.crc32(en.encode())).shuffle(ops)
    return ops


def una(en, ok, malas, ex=None, fuente=None, practica=False):
    q = dict(tipo='una', en=en, op=barajar(en, [[ok, True]] + [[m, False] for m in malas]))
    if ex: q['ex'] = ex
    if fuente: q['fuente'] = fuente
    if practica: q['practica'] = True
    return q


def varias(en, ops, ex=None, fuente=None, practica=False):
    q = dict(tipo='varias', en=en, op=barajar(en, [[t, bool(v)] for t, v in ops]))
    if ex: q['ex'] = ex
    if fuente: q['fuente'] = fuente
    if practica: q['practica'] = True
    return q


def vf(en, verdadero, ex=None, fuente=None, practica=False):
    q = dict(tipo='una', vf=True, en=en, op=[['Verdadero', verdadero], ['Falso', not verdadero]])
    if ex: q['ex'] = ex
    if fuente: q['fuente'] = fuente
    if practica: q['practica'] = True
    return q


# ───────────────────────── 1º Parcial: Teoría General de Sistemas ─────────────────────────
P = dict(practica=True)
SEM = dict(fuente='Recuperatorio 2023 (el caso)')
PARCIAL1 = [
    ('Teoría General de Sistemas', [
        una('¿Quién propuso la Teoría General de Sistemas (TGS)?', 'Ludwig von Bertalanffy', ['Kenneth Boulding', 'John Van Gigch', 'Harold Koontz'],
            'Biólogo austríaco: veía al organismo como un sistema abierto y publicó «Teoría General de Sistemas» en 1969. Boulding propuso los 9 niveles.', **P),
        una('La idea central de la TGS parte de una frase de Aristóteles. ¿Cuál?', 'El todo es más que la suma de las partes', ['Divide y vencerás', 'Las partes explican el todo', 'Todo sistema tiende al orden'],
            'Es la base de la sinergia: las partes relacionadas producen algo que no tienen por separado.', **P),
        una('¿Qué busca la TGS?', 'Principios y leyes aplicables a los sistemas en general, sin importar la naturaleza de sus elementos',
            ['Estudiar solo los sistemas físicos y mecánicos', 'Reemplazar a las ciencias particulares', 'Dividir cada fenómeno en sus partes más pequeñas'],
            'Es una metateoría: busca reglas de valor general, para cualquier sistema y nivel de la realidad.', **P),
        una('La correspondencia entre sistemas de disciplinas distintas que tienen las mismas características se llama…', 'Isomorfismo', ['Sinergia', 'Entropía', 'Homeostasis'], None, **P),
        vf('La concepción clásica de la ciencia era mecanicista: descomponía los fenómenos en unidades elementales y procesos aislados.', True,
           'La moderna, en cambio, estudia totalidades, la organización y las interacciones.', **P),
        una('¿Qué aplicación de la TGS explica los mecanismos de comunicación y control en las máquinas y los seres vivos?', 'La cibernética',
            ['La teoría de los juegos', 'La teoría de la decisión', 'El análisis factorial'], 'Por eso se la asocia con la informática.', **P),
        una('La teoría de los juegos…', 'Analiza la competencia racional entre dos o más antagonistas que buscan la máxima ganancia y la mínima pérdida',
            ['Mide la información con fórmulas matemáticas (entropía)', 'Estudia la conducta del sistema social al tomar decisiones', 'Aísla factores en fenómenos de muchas variables'], None, **P),
        una('La entropía es…', 'La tendencia de un sistema a avanzar hacia el desorden máximo',
            ['La fuerza que produce mayores niveles de orden', 'El intercambio de energía con el ambiente', 'La integración de partes que forman algo nuevo'],
            'Pasa cuando el sistema deja de recibir suficiente energía o información.', **P),
        una('La neguentropía es…', 'La fuerza opuesta a la entropía: se le inyecta energía e información al sistema para mantener o aumentar el orden',
            ['La medida del desorden de un sistema', 'La pérdida de energía de un sistema cerrado', 'La compatibilidad del sistema con su contexto'], None, **P),
        una('Un sistema abierto…', 'Intercambia energía, materia e información con el ambiente, a través de entradas y salidas',
            ['Es hermético a cualquier influencia del ambiente', 'Tiene un comportamiento determinista y programado', 'No tiene objetivo propio'],
            'Los organismos vivos y las organizaciones son sistemas abiertos: se adaptan para sobrevivir.', **P),
        vf('En rigor, no existen sistemas totalmente cerrados.', True,
           'Se llama cerrado al que tiene un comportamiento determinista y muy poco intercambio con el ambiente (una máquina, un reloj).', **P),
        una('¿Quién propuso jerarquizar los sistemas en 9 niveles según su complejidad?', 'Kenneth Boulding', ['Ludwig von Bertalanffy', 'Aristóteles', 'Norbert Wiener'],
            'Niveles 1 a 3: no vivientes; 4 a 7: vivientes; 8 y 9: metavivientes.', **P),
        varias('¿Cuáles son aportes metodológicos de la TGS?', [('El modelo del isomorfismo sistémico', 1), ('El modelo de rango (de las estructuras de los sistemas)', 1),
               ('El modelo procesal o del sistema adaptativo', 1), ('El modelo de departamentalización', 0), ('El organigrama', 0)],
               'Los aportes semánticos, en cambio, son el vocabulario común: sistema, ambiente, límite, alcances, recursos, E-P-S, retroalimentación…', **P),
    ]),
    ('Elementos de un sistema', [
        una('Un sistema es…', 'Un conjunto de elementos interrelacionados que tienen un objetivo en común',
            ['Un conjunto de personas que trabajan en un mismo lugar', 'Cualquier grupo de objetos, aunque no se relacionen', 'Un programa de computadora'], None, **P),
        una('El objetivo de un sistema es…', 'La meta o fin que debe alcanzar: su razón de ser',
            ['La lista de actividades que realiza', 'Lo que ingresa al sistema', 'El conjunto de elementos que lo forman'], None, **P),
        una('Las funciones o actividades que el sistema debe hacer dentro de su límite para alcanzar el objetivo, enunciadas en infinitivo, son…', 'Los alcances',
            ['Las entradas', 'Los recursos', 'Las salidas'], 'Por ejemplo: registrar el pedido, controlar la mercadería, emitir la factura.', **P),
        una('Lo que transforma las entradas en salidas es…', 'El proceso', ['El ambiente', 'El límite', 'La retroalimentación'], None, **P),
        una('Cuando se conocen las entradas y las salidas pero no cómo se transforman, el proceso se representa como…', 'Una caja negra',
            ['Una caja blanca', 'Un metasistema', 'Un subsistema'], 'Si se conoce (o se puede «ver») cómo se transforman, es una caja blanca.', **P),
        una('La retroalimentación se produce cuando…', 'Las salidas (o su efecto en el contexto) vuelven a entrar al sistema como información, para controlarlo y corregirlo',
            ['El control se hace a la entrada, para que no ingresen entradas malas', 'El sistema pierde energía y tiende al desorden', 'El sistema se divide en subsistemas'],
            'Lo de controlar a la entrada es el feed-forward (alimentación delantera).', **P),
        una('La retroalimentación que obliga a analizar y cambiar las entradas o el proceso porque hubo errores es…', 'De cambio',
            ['De circuito', 'Feed-forward', 'Neguentropía'], 'La de circuito indica que todo funciona bien y el proceso sigue igual.', **P),
        una('El ambiente (contexto) de un sistema es…', 'El conjunto de objetos exteriores al sistema que influyen en él (y en menor medida, el sistema influye en ellos)',
            ['Las personas que trabajan dentro del sistema', 'La línea que separa el sistema del contexto', 'Lo que el sistema produce'], None, **P),
        una('La línea que divide al sistema de su contexto («desde–hasta») es…', 'El límite', ['La estructura', 'El alcance', 'El metasistema'], None, **P),
        una('El sistema mayor que incluye al sistema bajo estudio es…', 'El metasistema (suprasistema)', ['El subsistema', 'El ambiente', 'La estructura'],
            'Los subsistemas son las partes del sistema, de rango inferior.', **P),
        varias('¿Cuáles son tipos de recursos de un sistema?', [('Humanos', 1), ('Materiales', 1), ('Financieros', 1), ('Objetivos', 0), ('Salidas', 0)],
               'Recursos: los elementos humanos, materiales, tecnológicos y financieros que intervienen en la transformación de las entradas en salidas.', **P),
        vf('Las salidas de un sistema pueden convertirse en las entradas de otro.', True, None, **P),
    ]),
    ('Clasificación y propiedades', [
        una('Según su relación con el entorno, los sistemas son…', 'Abiertos o cerrados', ['Concretos o abstractos', 'Simples o complejos', 'Determinísticos o probabilísticos'], None, **P),
        una('Según su comportamiento, los sistemas son…', 'Determinísticos o probabilísticos', ['Abiertos o cerrados', 'Concretos o abstractos', 'Simples o complejos'], None, **P),
        una('Según su naturaleza, los sistemas son…', 'Concretos o abstractos', ['Abiertos o cerrados', 'Determinísticos o probabilísticos', 'Simples o complejos'], None, **P),
        una('La sinergia es…', 'Cuando el efecto conjunto de las partes es mayor que la suma de sus efectos individuales',
            ['Cuando el sistema cumple sus objetivos con los mínimos recursos', 'La compatibilidad del sistema con su contexto', 'La tendencia al desorden'], None, **P),
        una('La propiedad de aprender y modificarse según los cambios del contexto es…', 'La adaptabilidad', ['La estabilidad', 'La armonía', 'La tensión'], None, **P),
        una('Un sistema es eficiente cuando…', 'Cumple sus objetivos con los mínimos recursos', ['Su salida está acotada', 'Es compatible con su contexto', 'Se mantiene en operación'],
            'O al revés: logra más objetivos con los mismos o menos recursos.', **P),
        una('Un sistema es estable cuando…', 'Se mantiene cumpliendo su objetivo en el tiempo (su salida está acotada)',
            ['Usa los mínimos recursos', 'Se adapta a cada cambio del contexto', 'Intercambia energía con el ambiente'], None, **P),
        una('La armonía de un sistema mide…', 'Su nivel de compatibilidad con el contexto', ['Cuántos recursos usa', 'Su tendencia al desorden', 'Cuántos subsistemas tiene'], None, **P),
    ]),
    ('Caso SEMYBAL', [
        una('En el caso SEMYBAL, ¿cuál es el mejor objetivo de la organización como sistema?',
            'Fabricar alimentos balanceados y comercializar alimentos balanceados, semillas y granos para sembrado, en forma minorista y mayorista',
            ['Vender productos en sus tres locales de la ciudad de Córdoba', 'Controlar la entrada y salida de mercadería del depósito', 'Ganarles a NutriVet y a Balanceados SA'],
            'El objetivo abarca todo lo que hace la organización (fabricar y comercializar), en infinitivo. Lo del depósito es un alcance; los locales, solo una parte de las ventas.', **SEM),
        varias('En el caso SEMYBAL, ¿cuáles forman parte del ambiente (contexto)?', [('Los proveedores Agro Industrial SA y la Cooperativa de Acopiadores', 1),
               ('Los competidores NutriVet y Balanceados SA', 1), ('El estudio contable Martínez y Asociados', 1), ('El encargado del depósito', 0), ('El software de facturación', 0)],
               'El ambiente es lo de afuera que influye en la organización. El encargado y el software son recursos.', **SEM),
        varias('En el caso SEMYBAL, ¿cuáles son recursos?', [('El depósito central', 1), ('El viajante que recorre la provincia', 1), ('El sistema de producción', 1),
               ('La Cámara de Comercio de Córdoba', 0), ('La agencia de publicidad Total Medios', 0)],
               'Recursos humanos (viajante), materiales (depósito) y tecnológicos (sistema de producción). Las cámaras y las empresas contratadas son ambiente.', **SEM),
        una('En el caso SEMYBAL, «Registrar el ingreso de materia prima al depósito» es…', 'Un alcance', ['Una entrada', 'Una salida', 'Un recurso'], 'Es una actividad, en infinitivo.', **SEM),
        una('En el caso SEMYBAL, «las materias primas e insumos que entregan los proveedores» son…', 'Entradas', ['Salidas', 'Alcances', 'Ambiente'], None, **SEM),
        una('En el caso SEMYBAL, «los alimentos balanceados vendidos y entregados a los clientes» son…', 'Salidas', ['Entradas', 'Recursos', 'Alcances'], None, **SEM),
        una('En el caso SEMYBAL, «las notas de pedido que se envían a los proveedores» son…', 'Salidas', ['Entradas', 'Recursos', 'Ambiente'],
            'Salen de la organización hacia el ambiente (los proveedores). Emitirlas es un alcance.', **SEM),
        una('En el caso SEMYBAL, «la Asociación Gremial de Empleados de Comercio de Córdoba» es…', 'Parte del ambiente', ['Un recurso', 'Una entrada', 'Un alcance'],
            'Es el sindicato: está afuera e influye en la organización.', **SEM),
        una('En el caso SEMYBAL, «el encargado de compras» es…', 'Un recurso humano', ['Parte del ambiente', 'Una salida', 'Un alcance'], None, **SEM),
        vf('En el caso SEMYBAL, INSOMIX (la empresa que desarrolla el software) es un recurso humano de la organización.', False,
           'Es una empresa contratada: forma parte del ambiente. El software que usan sí es un recurso tecnológico.', **SEM),
        una('En el caso SEMYBAL, «Seleccionar los presupuestos según precio y plazo de entrega» es…', 'Un alcance', ['Un objetivo', 'Una entrada', 'Un recurso'], None, **SEM),
    ]),
]
GLOSARIO1 = [
    dict(t='Teoría General de Sistemas (TGS)', que='Propuesta por Ludwig von Bertalanffy (biólogo): busca principios válidos para cualquier sistema. Parte de «el todo es más que la suma de las partes». Aplicaciones: cibernética, teoría de la información, de los juegos, de la decisión.', re=r'TGS|Teor[ií]a General|Bertalanffy|Arist[oó]teles|isomorf|Boulding|cibern[eé]tica|juegos|mecanicista', i=True),
    dict(t='Entropía y neguentropía', que='<b>Entropía</b>: la tendencia de un sistema al desorden cuando deja de recibir energía o información. <b>Neguentropía</b>: la fuerza contraria, que mantiene o aumenta el orden.', re=r'entrop', i=True),
    dict(t='Sistemas abiertos y cerrados', que='<b>Abiertos</b>: intercambian energía, materia e información con el ambiente (organismos, organizaciones). <b>Cerrados</b>: casi no intercambian; en rigor no existen.', re=r'abierto|cerrado', i=True),
    dict(t='Sistema', que='Conjunto de elementos interrelacionados que tienen un objetivo en común. Se representa como Entrada → Proceso → Salida (E-P-S).', re=r'Un sistema es|E-P-S', i=True),
    dict(t='Objetivo', que='La razón de ser del sistema: la meta que debe alcanzar. Se escribe en infinitivo y abarca todo lo que hace.', re=r'objetivo', i=True),
    dict(t='Entradas y salidas', que='<b>Entradas</b>: lo que ingresa al sistema (materiales, datos, pedidos, dinero). <b>Salidas</b>: los resultados que produce (productos, servicios, información). Las salidas de uno pueden ser entradas de otro.', re=r'entrada|salida', i=True),
    dict(t='Alcances', que='Las funciones o actividades que el sistema hace dentro de su límite para cumplir el objetivo. Se enuncian como lista de verbos en infinitivo.', re=r'alcance|en infinitivo', i=True),
    dict(t='Proceso, caja negra y caja blanca', que='El <b>proceso</b> transforma las entradas en salidas. Si no se sabe cómo, es una <b>caja negra</b>; si se lo puede ver, una <b>caja blanca</b>.', re=r'proceso|caja negra|transforma', i=True),
    dict(t='Retroalimentación', que='Las salidas vuelven como información para controlar y corregir. <b>De circuito</b>: sigue igual. <b>De cambio</b>: hay que cambiar. <b>Feed-forward</b>: el control se hace a la entrada.', re=r'retroalimentaci[oó]n|feed-forward', i=True),
    dict(t='Ambiente (contexto)', que='Lo que está fuera del sistema e influye en él: clientes, proveedores, competidores, el Estado, cámaras, sindicatos, empresas contratadas.', re=r'ambiente|contexto|entorno', i=True),
    dict(t='Límite, subsistema y metasistema', que='<b>Límite</b>: separa el sistema del contexto. <b>Subsistema</b>: una parte del sistema. <b>Metasistema</b>: el sistema mayor que lo contiene.', re=r'l[ií]mite|metasistema|subsistema|suprasistema', i=True),
    dict(t='Recursos', que='Los elementos que intervienen en la transformación: <b>humanos</b> (personas), <b>materiales</b> (edificios, máquinas, mercadería), <b>tecnológicos</b> (software, equipos) y <b>financieros</b> (dinero).', re=r'recurso', i=True),
    dict(t='Clasificación de sistemas', que='Según su naturaleza: concretos o abstractos. Según su relación con el entorno: abiertos o cerrados. Según su complejidad: simples o complejos. Según su comportamiento: determinísticos o probabilísticos.', re=r'seg[uú]n su', i=True),
    dict(t='Propiedades de los sistemas', que='Sinergia, estabilidad, adaptabilidad, eficiencia, tensión y armonía.', re=r'sinergia|adaptabilidad|eficien|estab|armon[ií]a', i=True),
    dict(t='Caso SEMYBAL', que='Fabrica alimentos balanceados y vende semillas y granos: tres locales en Córdoba y venta mayorista con un viajante. Tiene depósito central, encargados de ventas, compras, depósito, producción y RR. HH.; contrata un estudio contable, una agencia de publicidad y una empresa de software.', re=r'SEMYBAL'),
]

# ───────────────────────── 2º Parcial: organización, procesos y sistemas de información ─────────────────────────
R = dict(fuente=REC)
TC = 'de Todo Casa'
PARCIAL2 = [
    ('Organización y autoridad', [
        vf('Una organización es más eficiente mientras más niveles jerárquicos tenga.', False,
           'Al contrario: hoy se tiende a reducir los niveles para que la organización sea más simple, ágil y competitiva.', **R),
        vf('La autoridad y la responsabilidad se pueden delegar.', False, 'La autoridad se delega; la responsabilidad no: quien delega sigue siendo responsable.', **R),
        vf('Un staff puede dar órdenes.', False, 'El staff asesora (autoridad de asesoría, línea punteada en el organigrama). Solo con autoridad funcional manda, sobre un tema y por un tiempo.', **R),
        varias('Los siguientes son principios de la organización formal:', [('Jerarquización', 0), ('Unidad de mando', 1), ('Tramo de control', 1), ('Cadena de mando', 1), ('Coordinación', 0)],
               'También: autoridad, delegación, responsabilidad, división del trabajo, unidad de objetivos, eficiencia y definición funcional.', **R),
        vf('Un organigrama es la representación gráfica de la estructura de una organización formal.', True, None, **R),
        vf('La planificación es el proceso por el cual se enuncia anticipadamente lo que se ha de hacer, cómo hacerlo, cuándo hacerlo y quién ha de hacerlo.', True, None, **R),
        varias('¿Cuáles son las funciones de la administración?', [('Planear', 1), ('Organizar', 1), ('Dirigir', 1), ('Controlar', 1), ('Departamentalizar', 0)], None, **P),
        una('La unidad de mando dice que…', 'Para cada tarea, una persona recibe órdenes de un solo jefe',
            ['Un jefe puede controlar a cualquier cantidad de personas', 'Todos los subsistemas contribuyen al mismo objetivo', 'Los objetivos se logran con el mínimo costo'], None, **P),
        una('El tramo de control es…', 'La cantidad de subordinados que un jefe puede manejar en forma eficiente',
            ['La cantidad de niveles jerárquicos', 'La cadena de relaciones desde el nivel más bajo al más alto', 'El derecho de un jefe a dar órdenes'], None, **P),
        una('La autoridad que va de arriba hacia abajo, con líneas directas y únicas entre el jefe y sus subordinados, es la autoridad…', 'De línea', ['Staff', 'Funcional', 'Informal'],
            'En el organigrama: línea continua. Staff: punteada. Funcional: raya y punto.', **P),
        una('La organización que surge en forma espontánea de las relaciones entre las personas es…', 'La organización informal', ['La organización formal', 'El organigrama ideal', 'La departamentalización'], None, **P),
        una('El organigrama que muestra la organización tal como funciona hoy, con sus errores, es el…', 'Real', ['Racional', 'Ideal', 'Nominal'],
            'Ideal: hacia el que debería tender. Racional: con las unidades agrupadas en forma homogénea.', **P),
    ]),
    ('Departamentalización', [
        varias('¿Cuáles son los criterios para la departamentalización en una organización?', [('Asignar actividades a cada una de las áreas agrupadas', 1),
               ('Agruparlas según orden jerárquico', 1), ('Listar todas las funciones de la empresa', 1), ('Clasificar según su función', 1),
               ('Establecer líneas de comunicación e interrelación entre los departamentos', 1)], 'Son todos: listar, clasificar, agrupar, asignar, especificar las relaciones y establecer la comunicación.', **R),
        una('Una empresa con un departamento de finanzas, uno de producción, uno de comercialización y uno de recursos humanos está departamentalizada…', 'Por funciones',
            ['Por producto', 'Por territorio', 'Por clientes'], None, **P),
        una('Una láctea con un departamento de leche, uno de crema y uno de yogur está departamentalizada…', 'Por producto', ['Por funciones', 'Por proceso', 'Por tiempo'], None, **P),
        una('Departamento zona norte, zona sur y zona centro es una departamentalización…', 'Por territorio (geográfica)', ['Por clientes', 'Por producto', 'Matricial'], None, **P),
        una('Departamento de damas, de niños y de caballeros es una departamentalización…', 'Por clientes', ['Por producto', 'Por territorio', 'Por funciones'], None, **P),
        una('Una empresa que trabaja las 24 horas y se organiza en turno mañana, tarde y noche está departamentalizada…', 'Por tiempo', ['Por proceso', 'Matricial', 'Por funciones'], None, **P),
        una('La estructura en la que los empleados participan en proyectos puntuales sin dejar sus funciones, con doble línea de mando, es…', 'Matricial',
            ['Por proyecto', 'Por funciones', 'Por clientes'], None, **P),
    ]),
    ('Procesos y toma de decisiones', [
        una('¿Cuál es la diferencia entre proceso y procedimiento?', 'El proceso es una sucesión de acciones hacia una finalidad; el procedimiento es el documento escrito que describe paso a paso cómo hacer una actividad',
            ['Son lo mismo', 'El procedimiento es más general que el proceso', 'El proceso es solo de las áreas de producción'], None, **P),
        varias('En un mapa de procesos, los procesos se agrupan en…', [('Estratégicos', 1), ('Esenciales (operativos)', 1), ('De soporte (apoyo)', 1), ('Contables', 0), ('Informáticos', 0)],
               'Estratégicos arriba (definir políticas), esenciales en el medio (los que generan el producto o servicio) y de soporte abajo (comprar, liquidar sueldos…).', **P),
        varias('¿Qué muestra el diagrama de estructura básica de un proceso?', [('El objetivo del proceso', 1), ('La entrada (el evento que lo dispara)', 1), ('La salida (el resultado)', 1),
               ('Los recursos (las personas que intervienen)', 1), ('La secuencia de actividades', 0)], 'La secuencia va en el diagrama de secuencia de actividades.', **P),
        varias('¿Qué símbolos se usan en el diagrama de secuencia de actividades?', [('Inicio y fin', 1), ('Actividad', 1), ('Decisión (rombo)', 1), ('Documento', 1), ('Organigrama', 0)], None, **P),
        una('La actividad que implica una decisión (bifurcación) en el proceso de compra es:', 'Controlar si lo que se recibió es lo que se solicitó',
            ['Verificar si llegó el pedido del proveedor', 'Verificar si hay stock', 'Controlar si la factura está correcta', 'Verificar si el proveedor recibió la orden de compra'],
            'Según lo que se controla, el camino se abre: si coincide, se ingresa; si no, se reclama al proveedor.', **R),
        una('La toma de decisiones es…', 'La elección de un curso de acción entre varias alternativas: el núcleo de la planeación',
            ['La ejecución de un procedimiento escrito', 'El control de los resultados', 'La delegación de autoridad'], None, **P),
        una('Las decisiones que se toman ante problemas repetitivos y rutinarios, con un procedimiento ya establecido, son…', 'Programadas',
            ['No programadas', 'Estratégicas', 'Informales'], 'Las no programadas son para problemas nuevos o poco estructurados.', **P),
    ]),
    ('Sistemas de información', [
        varias('¿Cuáles de estas son características de la información?', [('Estándar', 0), ('Eficiente', 0), ('Completa', 1), ('Relevante', 1), ('Oportuna', 1)], None, **R),
        varias('Son características de la información:', [('Económica', 1), ('Aislada', 0), ('Simple', 1), ('Rápida', 0), ('Verificable', 1)],
               'También: precisa, completa, confiable, flexible, relevante, oportuna, segura y accesible.', **R),
        varias('Las necesidades de procesamiento de datos están determinadas por algunas de las siguientes consideraciones:', [('Volumen de datos involucrados', 1),
               ('Necesidad de tomar decisiones no programadas', 0), ('Complejidad de las operaciones de procesamiento', 1), ('Exigencia en cuanto a tiempo de procesamiento', 1),
               ('Tipos de requerimientos de información por parte de los niveles más altos de la organización', 0)], None, **R),
        varias('Los siguientes sistemas se reconocen como tipos de sistemas de información:', [('Sistema de procesamiento de transacciones', 1), ('Sistema de facturación', 0),
               ('Sistemas expertos de inteligencia artificial', 1), ('Sistema contable', 0), ('Sistema de apoyo a las decisiones', 1)],
               'Facturación y contabilidad son aplicaciones, no tipos. Los tipos: TPS, gerencial (MIS), apoyo a las decisiones (DSS), expertos e IA, de grupo (GDSS) y para ejecutivos.', **R),
        varias('Considerando SOLO la entrada de un sistema de información, ¿qué actividades se realizan sobre los datos?', [('Distribuir', 0), ('Capturar', 1), ('Ordenar', 0), ('Verificar', 1), ('Almacenar', 0)],
               'La entrada recopila y captura los datos (y los verifica). Ordenar y almacenar son del procesamiento; distribuir, de la salida.', **R),
        vf('El costo de la información son los recursos que se requieren para obtenerla.', True, 'El valor, en cambio, es el beneficio que se obtiene a partir de ella.', **R),
        una('Podemos definir a los alcances del sistema de información como…', 'Las tareas del sistema de información que transforman las entradas en salidas',
            ['Las actividades que realiza la organización para obtener salidas de valor para sus clientes', 'Los usuarios del sistema de información',
             'El conjunto de elementos utilizados en el procesamiento de información', 'El conjunto de entradas que debe procesar el sistema de información'], None, **R),
        una('¿Qué diferencia hay entre dato e información?', 'Un dato es un hecho aislado; la información son datos organizados que tienen un valor adicional',
            ['Son lo mismo', 'La información es un dato sin procesar', 'Un dato siempre es un número'], None, **P),
        una('El tipo de sistema de información que se implanta primero, en el nivel operativo, y procesa gran cantidad de transacciones rutinarias es…', 'El de procesamiento de transacciones (TPS)',
            ['El de información gerencial (MIS)', 'El de apoyo a las decisiones (DSS)', 'El sistema experto'], None, **P),
        una('El sistema que captura el conocimiento de un experto y propone la mejor solución a un problema es…', 'El sistema experto', ['El de apoyo a las decisiones (DSS)', 'El TPS', 'El MIS'],
            'El DSS, en cambio, deja la decisión en manos de quien decide.', **P),
        una('Un informe comparativo de ventas de distintos períodos, para tomar decisiones importantes, es información…', 'Directiva', ['Operativa', 'De control', 'Aislada'],
            'Operativa: para hacer cada tarea (el pedido del cliente). De control: para detectar desvíos (el informe de inventario).', **P),
    ]),
    ('Caso Todo Casa', [
        una(f'Para la organización {TC}, ¿cuál de las siguientes opciones representa mejor la lista de procesos?', 'Comprar materia prima / Fabricar muebles / Vender amoblamientos / Liquidar sueldos',
            ['Comercialización / Producción / Mantenimiento', 'Comprar / Fabricar / Vender / Liquidar sueldos / Realizar contabilidad', 'Comercialización / Fabricación / Control de calidad',
             'Realizar análisis de mercado / Comercializar / Fabricar / Vender'], 'Procesos con verbo y objeto. La contabilidad la hace un estudio externo: no es un proceso de la organización.', **R),
        varias(f'Para la organización {TC}, ¿cuáles de las siguientes opciones son procesos de la organización?', [('Contactar proveedor', 0), ('Atender al cliente', 0),
               ('Generar orden de compra', 0), ('Liquidar sueldos', 1), ('Vender muebles de cocina', 1)], 'Las otras son actividades dentro de un proceso.', **R),
        varias(f'Para la organización {TC}, ¿cuáles de las siguientes opciones NO son procesos de la organización?', [('Comprar materia prima', 0), ('Fabricar muebles de cocina', 0),
               ('Registrar libros contables', 1), ('Vender muebles de cocina', 0), ('Generar informe de pagos a proveedores', 1)], None, **R),
        una(f'Para el proceso Vender amoblamientos {TC}, ¿cuál se ajusta más al objetivo?', 'Realizar la venta de amoblamientos para cocina al contado y con tarjeta, en forma minorista',
            ['Diseñar muebles estándares y a medida', 'Comercializar y distribuir amoblamientos', 'Fabricar y vender amoblamiento para cocina, de diseño y producción propia',
             'Realizar la venta y entrega domiciliaria de muebles de cocina'], None, **R),
        una(f'Para el proceso Vender amoblamientos {TC}, «Realizar la venta de amoblamientos en forma minorista, al contado y con tarjeta» es…', 'El objetivo',
            ['Una salida', 'Una entrada', 'Un alcance', 'Un recurso'], None, **R),
        una(f'¿A continuación de qué actividad se debe confeccionar el remito en el proceso Vender amoblamientos {TC}?', 'Buscar el producto',
            ['Generar orden de compra', 'Controlar factura', 'Almacenar producto', 'Recibir mercadería'],
            'El responsable de despacho controla que la factura esté pagada, busca el producto y recién ahí genera el remito.', **R),
        una(f'¿Cuál representa mejor la finalización del diagrama de secuencia de actividades del proceso Vender amoblamientos {TC}?',
            'Generar remito de entrega / Solicitar firma del cliente / Sellar copia del remito / Entregar copia del remito, factura y producto al cliente',
            ['Generar remito / Solicitar firma al cliente / Entregar producto y factura al cliente', 'Generar remito de entrega / Entregar copia de remito, factura y producto al cliente',
             'Generar factura / Generar remito / Entregar producto, remito y factura al cliente', 'Generar remito / Cobrar producto / Entregar producto, remito y factura al cliente'], None, **R),
        varias(f'Para el proceso Vender amoblamientos {TC}, ¿qué actividades NO pertenecen al diagrama de secuencia?', [('Generar orden de compra', 1), ('Solicitar autorización de tarjeta', 0),
               ('Controlar factura cobrada', 0), ('Buscar producto', 0), ('Pagar factura', 1)], 'Generar la orden de compra es del proceso de compras; el cliente es quien paga.', **R),
        vf(f'En el proceso Vender amoblamientos {TC}, el cliente debe firmar la factura como constancia de que retira el producto.', False, 'Firma el remito.', **R),
        una(f'Indique cuál se ajusta más al objetivo del sistema de información que da soporte al proceso Vender amoblamientos {TC}.', 'Brindar información para gestionar las ventas de amoblamientos de cocina',
            ['Brindar información para gestionar la producción de amoblamientos de cocina', 'Vender muebles de cocina al contado y con tarjeta',
             'Realizar la comercialización de muebles de cocina con producción y diseños propios', 'Informar al gerente sobre los muebles más vendidos, discriminados por modelo'],
            'El objetivo de un SI siempre es brindar información para el proceso; vender es el objetivo del proceso, y el informe es una salida.', **R),
        vf(f'El objetivo del sistema de información que dará soporte al proceso Vender amoblamientos {TC} es «Generar informe sobre muebles más vendidos, discriminados por modelo».', False,
           'Eso es una salida (el informe) o un alcance (generarlo).', **R),
        varias('Son alcances de un sistema de información de ventas…', [('Registrar datos del pedido', 1), ('Cobrar pedido', 0), ('Registrar datos del cliente', 1),
               ('Registrar datos de los proveedores', 0), ('Generar y emitir factura', 1)], 'Cobrar lo hace una persona; el SI registra el cobro.', **R),
        varias(f'¿Cuáles se corresponden con alcances del sistema de información que da soporte al proceso Vender productos {TC}?', [('Registrar forma de pago', 1), ('Registrar datos de cliente', 1),
               ('Generar orden de compra', 0), ('Cobrar productos', 0), ('Consultar disponibilidad y precios', 1)], None, **R),
        varias(f'Para el sistema de información que da soporte al proceso de ventas {TC}, ¿cuáles se corresponden con alcances?', [('Generar factura', 1), ('Controlar factura', 0),
               ('Atender al cliente', 0), ('Consultar disponibilidad y precio', 1), ('Registrar pago a proveedor', 0)], 'Controlar la factura y atender al cliente los hacen personas.', **R),
        vf(f'Para el sistema de información que da soporte al proceso Vender amoblamientos {TC}, «Generar orden de compra» NO es un alcance.', True, 'Es del proceso de compras.', **R),
        una(f'Para el sistema de información que da soporte al proceso Vender amoblamientos {TC}, «Registrar cobro del pedido» es…', 'Un alcance', ['Una entrada', 'El objetivo', 'Una salida', 'Un dato'], None, **R),
        una(f'Para el sistema de información que da soporte al proceso Vender amoblamientos {TC}, «Factura de venta» es…', 'Una salida', ['Un alcance', 'Una entrada', 'El objetivo', 'Un proceso'],
            '«Generar factura» sería el alcance; la factura es lo que sale.', **R),
        una('Para el sistema de información asociado al proceso Vender, «Encargado de compras» es…', 'Un usuario', ['Un alcance', 'Una salida', 'Una entrada'],
            'En la misma pregunta del campus: «Registrar pedido del cliente», «Generar factura» y «Consultar stock» son alcances, y «Factura», una salida.', **R),
        varias(f'¿Cuáles son entradas del sistema de información que da soporte al proceso Vender amoblamientos {TC}?', [('Datos de la forma de pago', 1), ('Factura', 0), ('Datos del cliente', 1),
               ('Datos del proveedor', 0), ('Datos de la orden de compra', 0)], 'Entradas al SI: datos. La factura es una salida.', **R),
        vf('Los datos del cliente y los datos de los productos pedidos son entradas al SI.', True, None, **R),
        varias(f'¿Cuáles NO son salidas del sistema de información que da soporte al proceso Vender amoblamientos {TC}?', [('Cupón de tarjeta', 0), ('Informe de productos más vendidos, discriminados por modelo', 0),
               ('Remito', 0), ('Generar remito', 1), ('Emitir factura', 1)], 'Con verbo en infinitivo son alcances; las salidas son los documentos e informes.', **R),
    ]),
]
GLOSARIO2 = [
    dict(t='Administración', que='Diseñar y mantener un ambiente en el que personas que trabajan en grupo cumplen metas. Funciones: <b>planear</b> (decidir de antemano qué, cómo, cuándo y quién), organizar, dirigir y controlar.', re=r'planificaci[oó]n|administraci[oó]n|planear', i=True),
    dict(t='Autoridad y delegación', que='<b>Autoridad</b>: el derecho del puesto a dar órdenes; fluye hacia abajo. <b>Delegar</b>: pasar autoridad a un puesto inferior; la responsabilidad no se delega. Tipos: de línea, staff (asesora) y funcional.', re=r'autoridad|staff|delega', i=True),
    dict(t='Principios de la organización formal', que='Autoridad, delegación, responsabilidad, división del trabajo, unidad de mando, tramo de control, unidad de objetivos, eficiencia, cadena de mando y definición funcional.', re=r'unidad de mando|tramo de control|cadena de mando|principios', i=True),
    dict(t='Organigrama', que='La representación gráfica de la estructura formal: cuadros (puestos) y líneas (autoridad y comunicación). Puede ser vertical, horizontal, mixto o circular; real, racional o ideal.', re=r'organigrama|niveles jer[aá]rquicos', i=True),
    dict(t='Organización formal e informal', que='<b>Formal</b>: la planeada por la dirección (la del organigrama). <b>Informal</b>: la red de relaciones que surge sola entre las personas.', re=r'informal', i=True),
    dict(t='Departamentalización', que='Agrupar actividades y personas en departamentos para que la organización pueda crecer. Por funciones, producto, territorio, clientes, proceso, proyecto, tiempo o matricial.', re=r'departamentaliz|matricial', i=True),
    dict(t='Proceso y procedimiento', que='<b>Proceso</b>: sucesión de acciones ordenadas hacia una finalidad. <b>Procedimiento</b>: documento escrito que describe paso a paso cómo se hace una actividad.', re=r'procedimiento', i=True),
    dict(t='Mapa de procesos', que='Los procesos de la organización en tres grupos: estratégicos (arriba), esenciales u operativos (en el medio, los que generan el producto o servicio) y de soporte (abajo). Cada proceso se nombra con un verbo y su objeto.', re=r'mapa de procesos|lista de procesos|son procesos|NO son procesos', i=True),
    dict(t='Diagrama de estructura básica', que='El proceso en el centro, la entrada (el evento que lo dispara) a la izquierda, la salida (el resultado) a la derecha, el objetivo arriba y los recursos (las personas) abajo.', re=r'estructura b[aá]sica', i=True),
    dict(t='Diagrama de secuencia de actividades', que='Las actividades del proceso en orden, en carriles (uno por responsable): inicio y fin, actividades, rombos de decisión y documentos.', re=r'diagrama de secuencia|s[ií]mbolos|bifurcaci[oó]n|remito', i=True),
    dict(t='Toma de decisiones', que='Elegir un curso de acción entre alternativas. <b>Programadas</b>: problemas rutinarios con un procedimiento. <b>No programadas</b>: problemas nuevos o poco estructurados.', re=r'decisi[oó]n|decisiones', i=True),
    dict(t='Dato e información', que='<b>Dato</b>: un hecho aislado. <b>Información</b>: datos organizados con un valor adicional. Su <b>valor</b> es el beneficio que da; su <b>costo</b>, los recursos para obtenerla.', re=r'dato|informaci[oó]n', i=True),
    dict(t='Sistema de información (SI)', que='Componentes que recolectan, procesan, almacenan y distribuyen información para la toma de decisiones y el control. Su objetivo es <b>brindar información</b> para un proceso; sus alcances son lo que hace con los datos (registrar, consultar, generar, emitir).', re=r'sistema de informaci[oó]n|\bSI\b', i=True),
    dict(t='Tipos de sistemas de información', que='De procesamiento de transacciones (TPS), de información gerencial (MIS), de apoyo a las decisiones (DSS), expertos e inteligencia artificial, de apoyo a decisiones en grupo y para ejecutivos.', re=r'TPS|MIS|DSS|transacciones|experto', i=True),
    dict(t='Caso Todo Casa', que='Fabrica y vende muebles de cocina. El vendedor atiende al cliente, consulta stock y forma de pago y hace la factura; el cajero cobra (si es con tarjeta pide autorización y emite el cupón) y sella la factura; el responsable de despacho controla la factura, busca el producto, genera el remito, pide la firma, sella la copia y entrega todo.', re=r'Todo Casa'),
]


def armar_quiz(titulo, descripcion, partes, glosario):
    return dict(titulo=titulo, descripcion=descripcion, secciones=[dict(titulo=t, preguntas=qs) for t, qs in partes], glosario=glosario)


# ───────────────────────── Las resoluciones ─────────────────────────
E = html.escape
CSS = '''
@page { size: A4; margin: 15mm 15mm 15mm; }
@page apaisada { size: A4 landscape; margin: 10mm 10mm; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; box-sizing: border-box; }
body { font-family: 'Open Sans', 'DejaVu Sans', sans-serif; font-size: 10pt; line-height: 1.45; color: #1f1e1c; margin: 0; }
h1 { font-family: Georgia, 'DejaVu Serif', serif; font-weight: 400; font-size: 20pt; margin: 0 0 4pt; }
h2 { font-family: Georgia, 'DejaVu Serif', serif; font-weight: 400; font-size: 13.5pt; margin: 14pt 0 6pt; padding-top: 6pt; border-top: 1px solid #e3e1da; break-after: avoid; }
.bajada { color: #5b5a54; margin: 0 0 8pt; }
.resuelto { display: inline-block; background: #e8f0fb; color: #1f5fbf; font-weight: 700; font-size: 8pt; letter-spacing: .1em; padding: 2pt 8pt; border-radius: 99pt; margin-bottom: 6pt; }
.r { color: #1f5fbf; }
ul { margin: 3pt 0 6pt; padding-left: 16pt; } li { margin: 1.5pt 0; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 8pt; font-size: 9pt; }
th, td { border: 1px solid #b9b6ad; padding: 4pt 6pt; vertical-align: top; text-align: left; }
th { background: #f3f2ee; }
td { color: #1f5fbf; } td b { color: #1f1e1c; }
.tip { background: #e4f3f5; border-left: 3pt solid #2d8992; border-radius: 4pt; padding: 5pt 9pt; margin: 6pt 0; break-inside: avoid; color: #1f1e1c; }
.dos { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; }
.dos > div { break-inside: avoid; }
.caja { border: 1px solid #d8d5cc; border-radius: 6pt; padding: 6pt 9pt; break-inside: avoid; }
.caja h3 { font-size: 10pt; margin: 0 0 3pt; }
.horizontal { page: apaisada; break-before: page; }
.horizontal h2 { border-top: 0; margin-top: 0; padding-top: 0; }
svg { display: block; width: 100%; height: auto; }
svg text { font-family: 'Open Sans', 'DejaVu Sans', sans-serif; }
'''


def pagina(titulo, cuerpo, css_fuentes):
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{E(titulo)}</title><style>{css_fuentes}{CSS}</style></head><body>{cuerpo}</body></html>'


def lista(xs, clase='r'):
    return f'<ul class="{clase}">' + ''.join(f'<li>{x}</li>' for x in xs) + '</ul>'


# ── SEMYBAL (1º parcial): objetivo, ambiente, recursos, entradas, alcances y salidas
def semybal_html(css_fuentes):
    c = ('<span class="resuelto">RESUELTO</span><h1>Recuperatorio del 1º parcial 2023 · SEMYBAL</h1>'
         '<p class="bajada">La organización vista como un sistema: qué persigue, qué la rodea, con qué trabaja y qué entra, qué hace y qué sale. '
         'Las respuestas van en azul; la consigna es la de las hojas anteriores.</p>')
    c += ('<h2>1) Objetivo y ambiente</h2><p><b>Objetivo</b> (en infinitivo y abarcando todo lo que hace):</p>'
          '<p class="r">Fabricar alimentos balanceados y comercializar alimentos balanceados, semillas y granos para sembrado, en forma minorista '
          '(en sus tres locales de la ciudad de Córdoba) y mayorista (en el interior de la provincia).</p>'
          '<p><b>Ambiente</b> (lo que está afuera e influye en la organización):</p>')
    c += lista([
        '<b>Clientes</b>: los minoristas de los tres locales y los mayoristas del interior de la provincia.',
        '<b>Proveedores</b>: Agro Industrial SA y la Cooperativa de Acopiadores de Córdoba.',
        '<b>Competidores</b>: NutriVet y Balanceados SA.',
        '<b>Cámaras</b>: la Cámara de Comercio de Córdoba y la Cámara de Industriales de Alimentos Balanceados de la Nación.',
        '<b>Sindicato</b>: la Asociación Gremial de Empleados de Comercio de Córdoba.',
        '<b>Empresas contratadas</b>: el estudio contable «Martínez y Asociados», la agencia de publicidad Total Medios S.R.L. y INSOMIX (desarrollo de software).',
        '<b>El Estado</b> (los organismos que cobran los impuestos que liquida el estudio contable).'])
    c += '<h2>2) Recursos</h2><div class="dos">'
    c += '<div class="caja"><h3>Humanos</h3>' + lista(['Gerente', 'Encargado de ventas', 'Encargados de cada local y personal de ventas', 'Viajante',
                                                      'Encargado del depósito', 'Encargado de producción y personal de fabricación', 'Encargado de compras',
                                                      'Encargado de Recursos Humanos', 'Personal de administración']) + '</div>'
    c += '<div class="caja"><h3>Materiales</h3>' + lista(['Los tres locales de venta', 'El depósito central', 'La planta y las máquinas de fabricación',
                                                         'El muestrario de productos', 'Las materias primas, los productos y la mercadería']) + '</div>'
    c += '<div class="caja"><h3>Tecnológicos</h3>' + lista(['El software de facturación', 'El software de control de stock',
                                                           'El sistema de producción (monitorea la producción, administra el stock de materiales y genera las alertas para compras)',
                                                           'El correo electrónico (por donde llegan los presupuestos)']) + '</div>'
    c += '<div class="caja"><h3>Financieros</h3>' + lista(['El capital de la empresa', 'El dinero de las ventas, con el que se pagan sueldos, proveedores, servicios e impuestos']) + '</div></div>'
    c += '<h2>3) Entradas, alcances y salidas</h2><div class="dos">'
    c += '<div class="caja"><h3>Entradas</h3>' + lista(['Las materias primas e insumos que entregan los proveedores', 'Las semillas y granos para revender',
                                                       'Los presupuestos de los proveedores (por mail) y sus facturas', 'Los pedidos de los clientes mayoristas (que toma el viajante)',
                                                       'Los clientes que compran en los locales', 'El dinero que pagan los clientes',
                                                       'Los servicios contratados (contables, de publicidad y de software)']) + '</div>'
    c += '<div class="caja"><h3>Salidas</h3>' + lista(['Los alimentos balanceados, semillas y granos vendidos y entregados (en los locales y a los clientes del interior)',
                                                      'Las facturas a los clientes', 'Los pedidos de cotización y las notas de pedido a los proveedores',
                                                      'Los avisos a los proveedores cuando hay diferencias o errores', 'Los pagos a los proveedores',
                                                      'Los sueldos pagados', 'La documentación que va al estudio contable']) + '</div></div>'
    c += '<div class="caja" style="margin-top:8pt"><h3>Alcances (lo que hace la organización, en infinitivo)</h3>' + lista([
        'Fijar las políticas de precios y las promociones', 'Establecer con los encargados de los locales los planes de venta de cada período',
        'Planificar y controlar las ventas mayoristas', 'Tomar los pedidos de los clientes del interior (viajante)', 'Vender en los locales y facturar',
        'Fabricar alimentos balanceados', 'Controlar la calidad de los productos fabricados', 'Detectar el faltante de materias primas y productos',
        'Generar y enviar los pedidos de cotización', 'Seleccionar los presupuestos según precio y plazo de entrega', 'Realizar las notas de pedido y cargarlas en el sistema',
        'Recibir la mercadería y controlarla contra la nota de pedido (cantidad y calidad)', 'Registrar los ingresos y salidas del depósito',
        'Informar a los proveedores las diferencias o errores', 'Autorizar el pago de las facturas de los proveedores', 'Enviar la mercadería a los locales y a los clientes del interior',
        'Capacitar al personal de ventas', 'Liquidar los sueldos']) + '</div>'
    c += ('<div class="tip"><b>Para no confundirse:</b> si está afuera y la organización no lo maneja → ambiente. Si la organización lo usa para trabajar → recurso. '
          'Si ingresa → entrada; si sale → salida. Si es una acción (un verbo en infinitivo) → alcance. Una misma empresa puede ser ambiente (INSOMIX) '
          'mientras lo que provee es un recurso (el software).</div>')
    return pagina('SPN · Recuperatorio del 1º parcial 2023 · SEMYBAL (resuelto)', c, css_fuentes)


# ── Todo Casa (2º parcial): los diagramas en SVG, con la notación del simulacro de la cátedra
AZUL, LINEA = '#2b6cb0', '#3a3833'


def envolver(t, ancho):
    palabras, lineas, ac = t.split(), [], ''
    for p in palabras:
        if ac and len(ac) + 1 + len(p) > ancho:
            lineas.append(ac); ac = p
        else:
            ac = (ac + ' ' + p).strip()
    return lineas + [ac] if ac else lineas


def texto(x, y, t, ancho=17, tam=10.5, peso=400, color=LINEA, ancla='middle'):
    ls = envolver(t, ancho)
    y0 = y - (len(ls) - 1) * tam * 0.6
    return f'<text x="{x}" y="{y0:.1f}" font-size="{tam}" font-weight="{peso}" fill="{color}" text-anchor="{ancla}" dominant-baseline="middle">' + \
        ''.join(f'<tspan x="{x}" dy="{0 if i == 0 else tam * 1.2:.1f}">{E(l)}</tspan>' for i, l in enumerate(ls)) + '</text>'


def actividad(x, y, t, w=112, h=46):
    h = max(h, len(envolver(t, 17)) * 12.6 + 10)          # que el texto entre siempre
    return f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{LINEA}" stroke-width="1.3"/>' + texto(x, y, t)


def rombo(x, y, t=None, r=20, arriba=True):
    s = f'<path d="M{x} {y - r} L{x + r} {y} L{x} {y + r} L{x - r} {y} Z" fill="#fff" stroke="{LINEA}" stroke-width="1.3"/>'
    if t: s += texto(x, y - r - 9 if arriba else y + r + 11, t, 22, 9.5, 600, AZUL)
    return s


def inicio(x, y):
    return f'<circle cx="{x}" cy="{y}" r="9" fill="#fff" stroke="{LINEA}" stroke-width="1.5"/>'


def fin(x, y, t=None):
    s = f'<circle cx="{x}" cy="{y}" r="10" fill="#fff" stroke="{LINEA}" stroke-width="1.5"/><circle cx="{x}" cy="{y}" r="6" fill="{LINEA}"/>'
    if t: s += texto(x, y + 22, t, 14, 9, 600, AZUL)
    return s


def documento(x, y, t, desde=None):
    w, h = 34, 38
    s = f'<path d="M{x - w / 2} {y - h / 2} h{w - 9} l9 9 v{h - 9} h{-w} Z" fill="#fff" stroke="{LINEA}" stroke-width="1.2"/>'
    s += texto(x, y + h / 2 + 10, t, 14, 9, 600, LINEA)
    if desde: s += f'<path d="M{desde[0]} {desde[1]} L{x} {y - h / 2}" stroke="{LINEA}" stroke-dasharray="3 3" fill="none"/>'
    return s


def conector(x, y, n):
    return f'<circle cx="{x}" cy="{y}" r="11" fill="#fff" stroke="#2f9e44" stroke-width="1.5"/>' + texto(x, y + 0.5, str(n), 4, 10, 700, '#2f9e44')


def flecha(puntos, etiqueta=None, donde=None):
    d = 'M' + ' L'.join(f'{x} {y}' for x, y in puntos)
    s = f'<path d="{d}" fill="none" stroke="{LINEA}" stroke-width="1.3" marker-end="url(#punta)"/>'
    if etiqueta:
        ex, ey = donde
        s += f'<text x="{ex}" y="{ey}" font-size="9.5" font-weight="700" fill="#b8541b" text-anchor="middle">{E(etiqueta)}</text>'
    return s


DEFS = f'<defs><marker id="punta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{LINEA}"/></marker></defs>'


def chevron(x, y, w, h, t, color='#fff'):
    p = 16
    return (f'<path d="M{x} {y} h{w - p} l{p} {h / 2} l{-p} {h / 2} h{-(w - p)} l{p} {-h / 2} Z" fill="{color}" stroke="{LINEA}" stroke-width="1.3"/>'
            + texto(x + w / 2 + 4, y + h / 2, t, 20, 10.5))


def mapa_svg():
    s = f'<svg viewBox="0 0 640 250" xmlns="http://www.w3.org/2000/svg">{DEFS}'
    for y, t in ((8, 'Procesos esenciales'), (148, 'Procesos de soporte')):
        s += f'<text x="0" y="{y + 8}" font-size="10" font-weight="700" fill="#6b6a64">{t.upper()}</text>'
    s += chevron(20, 30, 230, 70, 'Fabricar muebles de cocina', '#eef6f7') + chevron(260, 30, 230, 70, 'Vender amoblamientos', '#eef6f7')
    for x, t in ((20, 'Comprar materia prima'), (260, 'Liquidar sueldos')):
        s += f'<rect x="{x}" y="170" width="210" height="60" fill="#fff" stroke="{LINEA}" stroke-width="1.3"/>' + texto(x + 105, 200, t, 22)
    return s + '</svg>'


def estructura_svg():
    s = f'<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg">{DEFS}'
    s += f'<rect x="200" y="6" width="240" height="64" fill="#fff" stroke="{LINEA}" stroke-width="1.3"/>' + texto(320, 38, 'Realizar la venta de amoblamientos para cocina al contado y con tarjeta, en forma minorista', 34, 10)
    s += chevron(220, 110, 200, 70, 'Vender amoblamientos', '#eef6f7')
    s += f'<rect x="10" y="115" width="140" height="60" fill="#fff" stroke="{LINEA}" stroke-width="1.3"/>' + texto(80, 145, 'Cliente que quiere comprar un mueble de cocina', 20, 10)
    s += f'<rect x="490" y="110" width="140" height="70" fill="#fff" stroke="{LINEA}" stroke-width="1.3"/>' + texto(560, 145, 'Amoblamiento vendido y entregado (con factura y remito)', 20, 10)
    s += f'<rect x="200" y="214" width="240" height="78" fill="#fff" stroke="{LINEA}" stroke-width="1.3"/>'
    for i, t in enumerate(('Vendedores', 'Cajero', 'Responsable de despacho', 'Sistema de ventas y posnet')):
        s += f'<text x="218" y="{232 + i * 17}" font-size="10.5" fill="{LINEA}">– {E(t)}</text>'
    s += flecha([(150, 145), (236, 145)]) + flecha([(420, 145), (490, 145)]) + flecha([(320, 110), (320, 72)]) + flecha([(320, 214), (320, 182)])
    for x, y, t in ((80, 108, 'Entrada (evento)'), (560, 102, 'Salida (resultado)'), (470, 40, 'Objetivo'), (470, 250, 'Recursos')):
        s += f'<text x="{x}" y="{y}" font-size="9" font-weight="700" fill="#b8541b" text-anchor="middle">{t}</text>'
    return s + '</svg>'


def actividades_svg():
    W, H, L = 1100, 690, 34
    carriles = [('Vendedor', 0, 300), ('Cajero', 300, 520), ('Responsable de despacho', 520, 690)]
    s = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{DEFS}'
    for nombre, y0, y1 in carriles:
        s += f'<rect x="0" y="{y0}" width="{W}" height="{y1 - y0}" fill="#fff" stroke="{LINEA}" stroke-width="1.2"/>'
        s += f'<rect x="0" y="{y0}" width="{L}" height="{y1 - y0}" fill="#b9cbe8" stroke="{LINEA}" stroke-width="1.2"/>'
        cy = (y0 + y1) / 2
        s += f'<text x="{L / 2}" y="{cy}" font-size="12" font-weight="600" fill="{LINEA}" text-anchor="middle" dominant-baseline="middle" transform="rotate(-90 {L / 2} {cy})">{E(nombre)}</text>'
    # Vendedor: fila A (y 55), B (150) y C (245)
    s += inicio(65, 55) + flecha([(74, 55), (94, 55)])
    s += actividad(150, 55, 'Atender al cliente') + flecha([(206, 55), (219, 55)])
    s += actividad(275, 55, 'Mostrar productos y precios') + flecha([(331, 55), (344, 55)])
    s += actividad(400, 55, 'Consultar disponibilidad en stock') + flecha([(456, 55), (485, 55)])
    s += rombo(505, 55, '¿Hay stock?') + flecha([(525, 55), (563, 55)], 'sí', (544, 49))
    s += actividad(620, 55, 'Verificar si el cliente está registrado') + flecha([(676, 55), (710, 55)])
    s += rombo(730, 55, '¿Registrado?') + flecha([(750, 55), (793, 55)], 'sí', (771, 49))
    s += actividad(850, 55, 'Consultar la forma de pago') + flecha([(906, 55), (945, 55)])
    s += rombo(965, 55, '¿Con tarjeta?')
    s += flecha([(505, 75), (505, 126)], 'no', (518, 104)) + actividad(505, 150, 'Informar las alternativas posibles') + flecha([(505, 173), (505, 225)])
    s += rombo(505, 245, '¿Acepta alguna?', arriba=False) + flecha([(485, 245), (420, 245)], 'no', (452, 239)) + fin(408, 245, 'Venta no concretada')
    s += flecha([(525, 245), (620, 245), (620, 79)], 'sí', (560, 239))
    s += flecha([(730, 75), (730, 126)], 'no', (743, 104)) + actividad(730, 150, 'Registrar el cliente') + flecha([(786, 150), (850, 150), (850, 79)])
    s += flecha([(965, 75), (965, 126)], 'sí', (978, 104)) + actividad(965, 150, 'Informar opciones de pago e interés') + flecha([(965, 173), (965, 221)])
    s += flecha([(985, 55), (1065, 55), (1065, 245), (1022, 245)], 'no (contado)', (1040, 47))
    s += actividad(965, 245, 'Registrar la forma de pago') + flecha([(909, 245), (897, 245)])
    s += actividad(840, 245, 'Generar la factura y entregarla') + flecha([(784, 245), (766, 245)]) + conector(754, 245, 1)
    s += documento(700, 252, 'Factura', (784, 232))
    # Cajero: fila 1 (y 350) y fila 2 (y 440); la fila 3 es el camino del contado
    s += conector(70, 350, 1) + flecha([(81, 350), (118, 350)])
    s += rombo(140, 350, '¿Con tarjeta?') + flecha([(160, 350), (203, 350)], 'sí', (182, 344))
    s += actividad(260, 350, 'Solicitar autorización a la entidad emisora') + flecha([(316, 350), (358, 350)])
    s += rombo(380, 350, '¿Autorizada?') + flecha([(400, 350), (443, 350)], 'sí', (422, 344))
    s += actividad(500, 350, 'Emitir el cupón') + flecha([(556, 350), (618, 350)])
    s += documento(600, 395, 'Cupón', (530, 373))
    s += rombo(640, 350) + flecha([(660, 350), (703, 350)])
    s += actividad(760, 350, 'Sellar la factura como pagada') + flecha([(816, 350), (858, 350)]) + conector(870, 350, 2)
    s += flecha([(380, 370), (380, 418)], 'no', (393, 396)) + rombo(380, 440, '¿Paga en efectivo?', arriba=False)
    s += flecha([(400, 440), (463, 440)], 'sí', (430, 434)) + actividad(520, 440, 'Cobrar en efectivo') + flecha([(576, 440), (640, 440), (640, 372)])
    s += flecha([(360, 440), (316, 440)], 'no', (338, 434)) + actividad(260, 440, 'Cancelar la operación') + flecha([(204, 440), (192, 440)]) + fin(180, 440)
    s += flecha([(140, 370), (140, 495), (520, 495), (520, 465)], 'no (efectivo)', (180, 488))
    # Responsable de despacho
    s += conector(70, 605, 2) + flecha([(81, 605), (114, 605)])
    xs = [(170, 'Controlar que la factura esté pagada'), (305, 'Buscar el producto'), (440, 'Generar el remito'), (575, 'Solicitar la firma del cliente'),
          (710, 'Sellar la copia del remito'), (850, 'Entregar remito, factura y producto')]
    for i, (x, t) in enumerate(xs):
        s += actividad(x, 605, t, 120 if i == 5 else 112)
        if i < len(xs) - 1:
            s += flecha([(x + 56, 605), (xs[i + 1][0] - 57, 605)])
    s += flecha([(910, 605), (948, 605)]) + fin(960, 605)
    s += documento(500, 660, 'Remito', (440, 628))
    return s + '</svg>'


TODO_CASA_PROCESOS = [
    ('Comprar materia prima', 'Soporte', 'Adquirir los materiales para fabricar los muebles a proveedores seleccionados, que se evalúan cada tres meses por tiempo de respuesta, precio y calidad.'),
    ('Fabricar muebles de cocina', 'Esencial', 'Producir los amoblamientos de cocina con los diseños exclusivos del propio equipo de producción.'),
    ('Vender amoblamientos', 'Esencial', 'Realizar la venta de amoblamientos para cocina al contado y con tarjeta, en forma minorista.'),
    ('Liquidar sueldos', 'Soporte', 'Calcular y pagar los sueldos del personal, incluidas las comisiones de cada vendedor por las ventas concretadas.'),
]
TODO_CASA_SI = [
    ('Vendedor', ['Consultar productos y precios', 'Consultar disponibilidad (stock) y alternativas', 'Consultar si el cliente está registrado', 'Registrar los datos del cliente',
                  'Consultar las opciones de pago con tarjeta y su interés', 'Registrar la forma de pago', 'Generar y emitir la factura']),
    ('Cajero', ['Consultar la factura', 'Registrar el cobro (efectivo o tarjeta)', 'Registrar la autorización y emitir el cupón', 'Registrar la factura como pagada', 'Registrar la operación cancelada']),
    ('Responsable de despacho', ['Consultar si la factura está pagada', 'Generar y emitir el remito', 'Registrar la entrega y actualizar el stock']),
    ('Gerente', ['Generar el informe de productos más vendidos, discriminados por modelo']),
    ('Encargado de sueldos', ['Generar el informe de ventas concretadas por vendedor (para las comisiones)']),
]


def todo_casa_html(css_fuentes):
    c = ('<span class="resuelto">RESUELTO</span><h1>Recuperatorio del 2º parcial 2023 · Todo Casa</h1>'
         '<p class="bajada">Con la misma notación que el simulacro de la cátedra (La Esquina). Las respuestas van en azul. '
         'En lo que preguntó el cuestionario del campus, coinciden con su clave.</p>')
    c += '<h2>1) Los procesos de la organización y su objetivo</h2><table><tr><th style="width:25%">Proceso</th><th style="width:12%">Tipo</th><th>Objetivo</th></tr>'
    c += ''.join(f'<tr><td><b>{E(p)}</b></td><td>{E(t)}</td><td>{E(o)}</td></tr>' for p, t, o in TODO_CASA_PROCESOS) + '</table>'
    c += f'<div style="max-width:118mm;margin:2pt auto 0">{mapa_svg()}</div>'
    c += ('<div class="tip">La contabilidad no es un proceso de Todo Casa: la hace un estudio contable externo (es parte del ambiente). Tampoco son procesos «Generar orden de compra», '
          '«Atender al cliente» o «Registrar libros contables»: son actividades.</div>')
    c += '<h2>2) Diagrama de estructura básica · Vender amoblamientos</h2>'
    c += f'<div style="max-width:128mm;margin:0 auto">{estructura_svg()}</div>'
    c += ('<div class="horizontal"><h2>3) Diagrama de secuencia de actividades · Vender amoblamientos</h2>'
          f'{actividades_svg()}'
          '<p style="margin:4pt 0 0"><b>Objetivo del sistema de información:</b> <span class="r">Brindar información para gestionar las ventas de amoblamientos de cocina.</span> '
          '<span style="color:#5b5a54">(No «vender»: ese es el objetivo del proceso.)</span></p></div>')
    c += '<h2 style="break-before:page;border-top:0;padding-top:0">4) Usuarios, alcances y salidas del sistema de información</h2><table><tr><th style="width:24%">Usuario</th><th>Alcances</th></tr>'
    c += ''.join(f'<tr><td><b>{E(u)}</b></td><td>{"<br>".join(E(a) for a in al)}</td></tr>' for u, al in TODO_CASA_SI) + '</table>'
    c += '<div class="dos"><div class="caja"><h3>Entradas (datos)</h3>' + lista(['Datos del cliente', 'Datos del producto elegido', 'Datos de la forma de pago',
                                                                                 'Datos de la autorización de la tarjeta', 'Datos del cobro']) + '</div>'
    c += '<div class="caja"><h3>Salidas (información)</h3>' + lista(['Factura', 'Cupón de tarjeta', 'Remito', 'Informe de productos más vendidos, discriminados por modelo',
                                                                     'Informe de ventas por vendedor (comisiones)']) + '</div></div>'
    c += ('<div class="tip"><b>Para no confundirse:</b> los alcances del SI son lo que hace el sistema con los datos (registrar, consultar, generar, emitir), no lo que hacen '
          'las personas: «Cobrar», «Atender al cliente» o «Controlar la factura» no son alcances. Con verbo en infinitivo es alcance («Emitir factura»); '
          'el documento es la salida («Factura»).</div>')
    return pagina('SPN · Recuperatorio del 2º parcial 2023 · Todo Casa (resuelto)', c, css_fuentes)


ORIGINALES = [  # (archivo, hojas del enunciado, cómo se arma la resolución)
    ('p1/03-recuperatorio-1er-parcial-2023-semybal.pdf', 2, semybal_html, 'Recuperatorio del 1º parcial 2023 · SEMYBAL'),
    ('p2/08-recuperatorio-2do-parcial-2023-todo-casa.pdf', 2, todo_casa_html, 'Recuperatorio del 2º parcial 2023 · Todo Casa'),
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
    ap.add_argument('--html', help='guarda también los HTML de las resoluciones en esta carpeta (para revisarlos)')
    a = ap.parse_args()
    for nombre, q in (('spn-1er-parcial.json', armar_quiz('SPN · 1º Parcial', 'Teoría General de Sistemas y el caso SEMYBAL del recuperatorio 2023: '
                                                           'objetivo, ambiente, recursos, entradas, alcances y salidas.', PARCIAL1, GLOSARIO1)),
                      ('spn-2do-parcial.json', armar_quiz('SPN · 2º Parcial', 'Organización, procesos y sistemas de información. Las preguntas del recuperatorio 2023 '
                                                           'son las del campus, con su clave; las del caso Todo Casa necesitan el enunciado (está en Material).', PARCIAL2, GLOSARIO2))):
        with open(os.path.join(RAIZ, 'quiz', nombre), 'w', encoding='utf-8') as fh:
            json.dump(q, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print(nombre, sum(len(s['preguntas']) for s in q['secciones']), 'preguntas ·', ', '.join(f"{s['titulo']} {len(s['preguntas'])}" for s in q['secciones']))
    if not a.pdf:
        return
    import pymupdf
    chromium = next((c for c in (os.environ.get('CHROMIUM'), '/opt/pw-browsers/chromium', shutil.which('chromium')) if c and os.path.exists(c)), None)
    if not chromium: raise SystemExit('No encuentro Chromium (poné su ruta en la variable CHROMIUM).')
    css = fuentes_css(a.fuente)
    with tempfile.TemporaryDirectory() as tmp:
        for nombre, hojas, armar, titulo in ORIGINALES:
            ruta = os.path.join(DESTINO, nombre)
            res = os.path.join(tmp, 'res.pdf')
            h = armar(css)
            if a.html:
                open(os.path.join(a.html, os.path.basename(nombre).replace('.pdf', '.html')), 'w', encoding='utf-8').write(h)
            imprimir(chromium, h, res)
            orig = pymupdf.open(ruta)
            final = pymupdf.open()
            final.insert_pdf(orig, to_page=hojas - 1)          # el enunciado, tal cual
            final.insert_pdf(pymupdf.open(res))                # y a continuación, resuelto
            orig.close()
            final.set_metadata({'title': f'SPN · {titulo}', 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': '', 'creationDate': '', 'modDate': ''})
            final.del_xml_metadata()
            final.save(ruta + '.tmp', garbage=3, deflate=True)
            final.close()
            os.replace(ruta + '.tmp', ruta)
            print(nombre, hojas, '+', pymupdf.open(ruta).page_count - hojas, 'hojas')


if __name__ == '__main__':
    main()
