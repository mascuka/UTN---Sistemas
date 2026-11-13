#!/usr/bin/env python3
"""Inglés 2: la práctica para escribir (quiz/ingles-2.json), el resumen y el simulacro y el ejemplo de parcial resueltos.

Es como Inglés 1 (la misma profe): la prueba de suficiencia (PdS) se toma apenas arranca la cursada y es de
lectocomprensión de un texto técnico. Suma, respecto de Inglés 1: referencia exofórica (el autor, el lector),
«it» anticipatorio y sustitución; más conectores (disyunción, énfasis, aclaración, resumen); aspectos de estructura
(voz pasiva, tiempos, modales, comparación, la forma -ing, caso posesivo); funciones comunicativas y cloze.

- La práctica son frases y palabras cortas para escribir, en secciones (cada una con su tarjeta en la Práctica).
  Cada ejercicio tiene las respuestas que valen ("resp"); la página las corrige sola (tipo "escribir").
- El simulacro 2024 y el ejemplo de parcial quedan en un PDF: primero las hojas originales en blanco y a continuación
  resueltos. Las respuestas son nuestras. Los originales ya están en material/ingles-2/ (sin metadatos); volver a
  correrlo no duplica hojas.

Uso, desde la raíz del repo:
  python3 herramientas/quiz/ingles_2.py                                   (la práctica)
  python3 herramientas/quiz/ingles_2.py --pdf --fuente CARPETA_OPEN_SANS  (además, el resumen y los resueltos)
"""
import argparse, html, json, os, shutil, subprocess, tempfile

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
DESTINO = os.path.join(RAIZ, 'material', 'ingles-2')

# ───────────────────────── La práctica para escribir ─────────────────────────
# Las relaciones como las nombra la cátedra (el apunte «A tener en cuenta»)
ADI = ['adición', 'agregado', 'adición-agregado', 'suma']
CAU = ['causa', 'causa-efecto', 'causalidad']
EFE = ['efecto', 'consecuencia', 'resultado', 'causa-efecto']
CND = ['condición', 'condición-predicción', 'predicción']
TIE = ['secuencia en el tiempo', 'tiempo', 'secuencia', 'temporal', 'secuencia temporal']
CTR = ['contraste', 'oposición', 'concesión']
EJE = ['ejemplificación', 'ejemplo', 'enumeración']
FIN = ['propósito', 'finalidad', 'intención', 'propósito, intención, finalidad']
RES = ['resumen', 'conclusión', 'recapitulación']
DIS = ['disyunción', 'alternancia', 'disyunción o alternancia', 'alternativa']
ENF = ['énfasis', 'repetición', 'repetición o énfasis']
ACL = ['aclaración', 'explicación', 'reformulación']
RELACIONES = 'adición, contraste, causa, efecto, condición, tiempo, propósito…'

FRASES = [  # frases sustantivas: (inglés, respuestas, por qué)
    ('computer systems engineering', ['ingeniería de sistemas informáticos', 'ingeniería en sistemas informáticos', 'ingeniería de sistemas de computación', 'ingeniería en sistemas de computación'], 'Núcleo al final: <i>engineering</i> → de sistemas → informáticos.'),
    ('computer-aided design', ['diseño asistido por computadora', 'diseño asistido por ordenador', 'diseño asistido por computador'], None),
    ('real-time processing', ['procesamiento en tiempo real'], None),
    ('signal processing', ['procesamiento de señales', 'procesamiento de la señal'], None),
    ('random access memory', ['memoria de acceso aleatorio'], 'Núcleo: <i>memory</i> → de acceso → aleatorio.'),
    ('graphics processing unit', ['unidad de procesamiento gráfico', 'unidad de procesamiento de gráficos'], None),
    ('digital integrated circuits', ['circuitos integrados digitales'], None),
    ('control unit', ['unidad de control'], 'No es lo mismo que <i>unit control</i> (control de la unidad): el núcleo siempre es el último.'),
    ('unwanted disturbances', ['perturbaciones no deseadas', 'interferencias no deseadas', 'alteraciones no deseadas'], '<i>un-</i> + wanted = no deseado.'),
    ('emerging technologies', ['tecnologías emergentes'], None),
    ('our increasing energy demands', ['nuestras crecientes demandas de energía', 'nuestras crecientes demandas energéticas', 'nuestras demandas de energía crecientes', 'nuestra creciente demanda de energía'], 'La forma <i>-ing</i> antes del sustantivo se traduce como adjetivo: <i>increasing</i> = creciente.'),
    ('the biggest market share', ['la mayor participación de mercado', 'la mayor cuota de mercado', 'la mayor participación en el mercado', 'la mayor porción del mercado'], '<i>the biggest</i> = el/la mayor (superlativo).'),
    ('greenhouse gas emissions', ['emisiones de gases de efecto invernadero', 'emisiones de gases invernadero'], None),
    ('the circular economy action plan', ['el plan de acción de economía circular', 'el plan de acción para la economía circular', 'el plan de acción de la economía circular'], 'Núcleo: <i>plan</i> → de acción → de economía circular.'),
    ('labeled training data', ['datos de entrenamiento etiquetados'], None),
    ('natural language processing', ['procesamiento del lenguaje natural', 'procesamiento de lenguaje natural'], None),
    ('speech recognition', ['reconocimiento de voz', 'reconocimiento del habla'], None),
    ('machine vision', ['visión artificial', 'visión por computadora', 'visión de máquina'], None),
    ('expert systems', ['sistemas expertos'], None),
    ('image recognition tool', ['herramienta de reconocimiento de imágenes'], None),
    ('treatment wetlands', ['humedales de tratamiento'], None),
    ('wastewater treatment', ['tratamiento de aguas residuales', 'tratamiento de efluentes'], None),
    ('air pollution control systems', ['sistemas de control de la contaminación del aire', 'sistemas de control de contaminación del aire', 'sistemas de control de la contaminación atmosférica'], 'Núcleo: <i>systems</i> → de control → de la contaminación → del aire.'),
    ("Ohm's law", ['la ley de Ohm', 'ley de Ohm'], 'Caso posesivo: <i>poseedor + \'s + lo poseído</i> → lo poseído de el poseedor.'),
    ("the engineers' association", ['la asociación de ingenieros', 'la asociación de los ingenieros'], 'Plural terminado en <i>s</i>: el posesivo es solo el apóstrofo.'),
    ("children's computer class", ['la clase de computación de los niños', 'clase de computación para niños', 'clase de informática de los niños', 'clase de informática para niños'], None),
    ("today's largest enterprises", ['las empresas más grandes de hoy', 'las empresas más grandes de la actualidad', 'las mayores empresas de hoy', 'las empresas más grandes actuales'], 'Caso posesivo (<i>today\'s</i> = de hoy) + superlativo (<i>largest</i> = las más grandes).'),
    ('general purpose high performance computer', ['computadora de alto rendimiento de propósito general', 'computadora de propósito general de alto rendimiento', 'computadora de uso general de alto rendimiento', 'computadora de alto rendimiento de uso general'], None),
    ('courses containing a lot of units', ['cursos que contienen muchas unidades', 'los cursos que contienen muchas unidades'], 'La forma <i>-ing</i> después del sustantivo se traduce «que + verbo».'),
    ('students admitted to an international course', ['estudiantes admitidos en un curso internacional', 'alumnos admitidos en un curso internacional', 'los estudiantes admitidos en un curso internacional'], 'Participio pasado después del sustantivo: «admitidos».'),
]
VERBOS = [  # voz pasiva, tiempos verbales y modales: (pista, inglés, respuestas, por qué)
    ('voz pasiva', 'These rules are called algorithms.', ['estas reglas se llaman algoritmos', 'estas reglas son llamadas algoritmos', 'estas reglas se denominan algoritmos', 'a estas reglas se las llama algoritmos'], 'Voz pasiva en presente: <i>are called</i> = son llamadas, o mejor con «se»: se llaman.'),
    ('voz pasiva', 'Many cars are built by computers.', ['muchos autos son construidos por computadoras', 'muchos autos son fabricados por computadoras', 'las computadoras construyen muchos autos', 'muchos autos son construidos por las computadoras'], 'Pasiva: <i>are built</i> (to be + participio). La activa sería <i>computers build many cars</i>.'),
    ('voz pasiva', 'Programming languages are used by engineers.', ['los lenguajes de programación son usados por los ingenieros', 'los lenguajes de programación son utilizados por los ingenieros', 'los ingenieros usan los lenguajes de programación'], None),
    ('voz pasiva', 'The paper was presented in Copenhagen.', ['el trabajo fue presentado en Copenhague', 'el artículo fue presentado en Copenhague', 'el trabajo se presentó en Copenhague', 'la ponencia fue presentada en Copenhague'], 'Pasiva en pasado simple: <i>was</i> + participio.'),
    ('voz pasiva', 'The concept was introduced by Faraday.', ['el concepto fue introducido por Faraday', 'el concepto fue presentado por Faraday'], None),
    ('voz pasiva', 'were found', ['fueron encontrados', 'fueron encontradas', 'se encontraron', 'fueron hallados', 'se hallaron'], '<i>find – found – found</i>.'),
    ('voz pasiva', 'was written', ['fue escrito', 'fue escrita', 'se escribió'], '<i>write – wrote – written</i>.'),
    ('voz pasiva', 'is being tested', ['está siendo probado', 'está siendo probada', 'se está probando', 'está siendo testeado'], 'Pasiva en presente continuo: <i>is being</i> + participio.'),
    ('voz pasiva', 'have been published', ['han sido publicados', 'han sido publicadas', 'se han publicado', 'fueron publicados', 'se publicaron'], 'Pasiva en presente perfecto: <i>have been</i> + participio.'),
    ('voz pasiva', 'will be built', ['será construido', 'será construida', 'se construirá', 'va a ser construido', 'se va a construir'], 'Pasiva en futuro: <i>will be</i> + participio.'),
    ('voz pasiva', 'has been chosen', ['ha sido elegido', 'ha sido elegida', 'fue elegido', 'fue elegida', 'se eligió', 'se ha elegido'], '<i>choose – chose – chosen</i>.'),
    ('voz pasiva', 'it is estimated that', ['se estima que', 'se calcula que'], '<i>It</i> anticipatorio + pasiva → «se» impersonal.'),
    ('tiempo verbal', 'has developed', ['se ha desarrollado', 'ha desarrollado', 'se desarrolló', 'desarrolló'], 'Presente perfecto: <i>has</i> + participio.'),
    ('tiempo verbal', 'had already finished', ['ya habían terminado', 'ya había terminado', 'ya habían finalizado', 'ya había finalizado'], 'Pasado perfecto: <i>had</i> + participio.'),
    ('tiempo verbal', 'He is working for a small company.', ['está trabajando para una pequeña empresa', 'él está trabajando para una pequeña empresa', 'trabaja para una pequeña empresa', 'está trabajando para una empresa pequeña'], 'Presente continuo: <i>is</i> + forma <i>-ing</i> → -ando / -endo.'),
    ('modal y voz pasiva', 'must be updated', ['debe ser actualizado', 'debe actualizarse', 'se debe actualizar', 'tiene que ser actualizado', 'debe ser actualizada'], 'Modal + <i>be</i> + participio.'),
    ('modal y voz pasiva', 'can be reused', ['puede ser reutilizado', 'puede reutilizarse', 'se puede reutilizar', 'pueden ser reutilizados', 'se pueden reutilizar', 'puede ser reusado'], None),
    ('modal y voz pasiva', 'should be avoided', ['debería evitarse', 'debería ser evitado', 'se debería evitar', 'debe evitarse', 'deberían evitarse'], '<i>should</i> = debería (consejo).'),
    ('modal', 'may', ['puede', 'podría', 'quizás', 'tal vez', 'puede que'], 'Posibilidad.'),
    ('modal', 'must', ['debe', 'tiene que', 'deber', 'tener que'], 'Obligación.'),
]
ESTRUCTURA = [  # casos especiales: (pista, inglés, respuestas, por qué)
    ('it anticipatorio', 'It is important to study English grammar.', ['es importante estudiar gramática inglesa', 'es importante estudiar la gramática inglesa', 'es importante estudiar gramática en inglés', 'es importante estudiar la gramática del inglés'], '<i>It</i> no se traduce: anticipa el sujeto real (<i>to study English grammar</i>).'),
    ('it anticipatorio', 'It is nice to see you again.', ['es lindo verte de nuevo', 'es lindo verte otra vez', 'es bueno verte de nuevo', 'es bueno verte otra vez', 'qué lindo verte de nuevo', 'es lindo volver a verte'], None),
    ('it anticipatorio', 'it is expected that', ['se espera que'], None),
    ('caso especial', 'when it comes to', ['cuando se trata de', 'en lo que respecta a', 'en cuanto a'], 'Expresión fija: no se traduce palabra por palabra.'),
    ('caso especial', 'AI allows enterprises to improve their operations.', ['la IA les permite a las empresas mejorar sus operaciones', 'la IA permite a las empresas mejorar sus operaciones', 'la IA permite que las empresas mejoren sus operaciones'], '<i>allow</i> + persona + <i>to</i> + verbo = permitir a alguien + infinitivo.'),
    ('comparación', 'as fast as', ['tan rápido como', 'tan rápida como'], 'Igualdad: <i>as … as</i> = tan … como.'),
    ('comparación', 'not as expensive as', ['no tan caro como', 'no tan costoso como', 'no tan cara como'], None),
    ('comparación', 'faster than', ['más rápido que', 'más rápida que'], '<i>-er than</i> = más … que.'),
    ('comparación', 'the most accurate results', ['los resultados más precisos', 'los resultados más exactos'], '<i>the most</i> + adjetivo = el más…'),
    ('comparación', 'the more, the better', ['cuanto más, mejor', 'mientras más, mejor'], 'Doble comparación: cuanto más…, más…'),
    ('comparación', 'the least expensive', ['el menos caro', 'la menos cara', 'el menos costoso', 'lo menos caro'], None),
    ('comparativo', 'good', ['better'], 'Irregular: <i>good – better – best</i>.'),
    ('superlativo', 'bad', ['worst', 'the worst'], 'Irregular: <i>bad – worse – worst</i>.'),
    ('forma -ing', 'Swimming is a healthy activity.', ['nadar es una actividad saludable', 'la natación es una actividad saludable'], 'Como sujeto: sustantivo o infinitivo.'),
    ('forma -ing', 'tips for improving', ['consejos para mejorar', 'recomendaciones para mejorar', 'sugerencias para mejorar'], 'Después de preposición: infinitivo.'),
    ('forma -ing', 'the living cell', ['la célula viva'], 'Antes del sustantivo: adjetivo.'),
    ('forma -ing', 'He broke his leg skiing.', ['se quebró la pierna esquiando', 'se rompió la pierna esquiando'], 'Función adverbial: -ando / -endo.'),
    ('forma -ing', 'The film was boring.', ['la película fue aburrida', 'la película era aburrida'], 'Después de <i>to be</i> (verbo copulativo): adjetivo.'),
    ('forma -ing', 'competing activities', ['actividades que compiten', 'actividades en competencia', 'actividades competidoras'], None),
    ('cuantificador', 'Any evidence will be enough.', ['cualquier prueba será suficiente', 'cualquier evidencia será suficiente', 'cualquier prueba va a ser suficiente'], 'En oraciones afirmativas <i>any</i> = cualquier.'),
    ('cuantificador', 'Is there any evidence?', ['hay pruebas', 'hay alguna prueba', 'hay evidencia', 'hay alguna evidencia'], 'En preguntas <i>any</i> casi no se traduce.'),
    ('cuantificador', "I'm busy every day.", ['estoy ocupado todos los días', 'estoy ocupada todos los días', 'estoy ocupado cada día'], '<i>every</i> = cada / todos; <i>all day</i> = todo el día.'),
]
VOCABULARIO = [  # (palabra, respuestas, falso amigo)
    ('actual', ['real', 'verdadero', 'efectivo'], True), ('actually', ['en realidad', 'realmente', 'de hecho'], True),
    ('sensible', ['sensato', 'razonable'], True), ('sensitive', ['sensible'], True), ('attend', ['asistir', 'concurrir'], True),
    ('assist', ['ayudar', 'atender', 'asistir', 'brindar asistencia'], True), ('large', ['grande', 'amplio'], True),
    ('embarrassed', ['avergonzado', 'avergonzada', 'apenado'], True), ('injuries', ['lesiones', 'heridas'], True),
    ('eventually', ['finalmente', 'con el tiempo', 'al final', 'a la larga'], True), ('lately', ['últimamente', 'recientemente'], True),
    ('vendors', ['proveedores', 'vendedores'], False), ('hype', ['expectativa', 'entusiasmo', 'furor', 'exageración', 'bombo'], False),
    ('insights', ['conocimientos', 'perspectivas', 'ideas', 'información valiosa', 'comprensión'], False),
    ('enterprises', ['empresas', 'compañías'], False), ('outcome', ['resultado'], False), ('skills', ['habilidades', 'destrezas', 'competencias'], False),
    ('wetlands', ['humedales'], False), ('waste', ['residuos', 'desechos', 'desperdicio', 'basura'], False),
    ('lifespan', ['vida útil', 'duración', 'vida'], False), ('feedback', ['retroalimentación', 'devolución', 'respuesta'], False),
    ('fine-tune', ['ajustar', 'afinar', 'perfeccionar', 'ajustar con precisión'], False),
    ('actionable', ['útil', 'aplicable', 'procesable', 'práctico', 'accionable'], False),
]
CONECTORES = [  # (conector, traducciones, relación)
    ('furthermore', ['además', 'asimismo', 'más aún', 'por otra parte'], ADI), ('as well as', ['así como', 'así como también', 'además de', 'como también'], ADI),
    ('both … and', ['tanto... como', 'tanto como'], ADI), ('besides', ['además', 'además de', 'aparte de'], ADI),
    ('therefore', ['por lo tanto', 'por consiguiente', 'por ende', 'por eso'], EFE), ('thus', ['así', 'por lo tanto', 'de este modo', 'de esta manera', 'por consiguiente'], EFE),
    ('hence', ['por lo tanto', 'de ahí que', 'por ende', 'por eso', 'por consiguiente'], EFE), ('consequently', ['en consecuencia', 'por consiguiente', 'consecuentemente', 'por lo tanto'], EFE),
    ('owing to', ['debido a', 'a causa de', 'gracias a'], CAU), ('due to', ['debido a', 'a causa de'], CAU), ('because of', ['debido a', 'a causa de', 'por'], CAU),
    ('unless', ['a menos que', 'a no ser que', 'salvo que', 'excepto que'], CND), ('provided that', ['siempre que', 'siempre y cuando', 'con tal de que'], CND),
    ('as long as', ['siempre que', 'siempre y cuando', 'mientras', 'en tanto'], CND),
    ('meanwhile', ['mientras tanto', 'entretanto'], TIE), ('eventually', ['finalmente', 'con el tiempo', 'al final', 'a la larga'], TIE),
    ('nevertheless', ['sin embargo', 'no obstante', 'aun así'], CTR), ('whereas', ['mientras que', 'en tanto que', 'en cambio'], CTR),
    ('despite', ['a pesar de', 'pese a'], CTR), ('even though', ['aunque', 'si bien', 'a pesar de que', 'aun cuando'], CTR),
    ('on the other hand', ['por otro lado', 'por otra parte', 'en cambio'], CTR), ('yet', ['sin embargo', 'no obstante', 'pero', 'aun así'], CTR),
    ('for instance', ['por ejemplo'], EJE), ('namely', ['a saber', 'es decir', 'concretamente', 'específicamente'], EJE),
    ('in order to', ['para', 'con el fin de', 'a fin de'], FIN), ('so that', ['para que', 'de modo que', 'de manera que', 'así'], FIN),
    ('so as to', ['para', 'con el fin de', 'a fin de', 'de modo de'], FIN),
    ('in summary', ['en resumen', 'en síntesis', 'resumiendo'], RES), ('in conclusion', ['en conclusión', 'para concluir', 'para terminar'], RES),
    ('either … or', ['o... o', 'ya sea... o', 'o bien... o'], DIS), ('neither … nor', ['ni... ni'], DIS), ('whether … or', ['si... o', 'ya sea... o'], DIS),
    ('above all', ['sobre todo', 'por sobre todo', 'ante todo', 'más que nada'], ENF), ('indeed', ['de hecho', 'en efecto', 'efectivamente', 'realmente'], ENF),
    ('that is to say', ['es decir', 'o sea', 'esto es'], ACL), ('i.e.', ['es decir', 'o sea', 'esto es'], ACL),
]
ANTONIMOS = [  # (palabra, antónimos que valen)
    ('artificial', ['natural']), ('apart', ['together']), ('largest', ['smallest']), ('increase', ['decrease', 'reduce', 'diminish', 'decline']),
    ('diminish', ['increase', 'grow', 'rise', 'amplify']), ('presence', ['absence']), ('slowly', ['quickly', 'rapidly', 'fast']),
    ('upper', ['lower']), ('inner', ['outer']), ('front', ['back', 'rear']), ('cheap', ['expensive', 'costly']), ('input', ['output']),
    ('attraction', ['repulsion']), ('buy', ['sell']), ('maximum', ['minimum']), ('success', ['failure']), ('private', ['public']),
    ('first', ['last']), ('many', ['few']), ('forward', ['backward', 'backwards']),
]
PREFIJOS = [  # (tipo, palabra, respuestas, por qué)
    ('antónimo', 'applicable', ['inapplicable'], None), ('antónimo', 'accurate', ['inaccurate'], None),
    ('antónimo', 'mature', ['immature'], '<i>im-</i> delante de m, p y b.'), ('antónimo', 'legible', ['illegible'], '<i>il-</i> delante de l.'),
    ('antónimo', 'responsible', ['irresponsible'], '<i>ir-</i> delante de r.'), ('antónimo', 'fair', ['unfair'], None),
    ('antónimo', 'agree', ['disagree'], None), ('antónimo', 'employed', ['unemployed'], None), ('antónimo', 'patient', ['impatient'], None),
    ('antónimo', 'polite', ['impolite'], None), ('antónimo', 'predictable', ['unpredictable'], None),
    ('antónimo', 'clockwise', ['counterclockwise', 'anticlockwise'], '<i>counter-</i>: lo contrario.'),
    ('prefijo', 'underestimate', ['subestimar', 'subvalorar'], '<i>under-</i>: por debajo, insuficiente.'), ('prefijo', 'overestimate', ['sobreestimar', 'sobrestimar', 'sobrevalorar'], '<i>over-</i>: por encima, excesivo.'),
    ('prefijo', 'misunderstanding', ['malentendido'], '<i>mis-</i>: mal.'), ('prefijo', 'rewrite', ['reescribir', 'volver a escribir'], '<i>re-</i>: de nuevo.'),
    ('prefijo', 'self-service', ['autoservicio'], '<i>self-</i>: auto-.'), ('prefijo', 'postwar', ['posguerra', 'de posguerra'], '<i>post-</i>: después.'),
    ('sufijo', 'shorten', ['acortar'], '<i>-en</i>: adjetivo → verbo.'), ('sufijo', 'widen', ['ensanchar', 'ampliar'], None),
    ('sufijo', 'twofold', ['doble', 'el doble', 'duplicado'], '<i>-fold</i>: multiplicado por.'), ('sufijo', 'jobless', ['desempleado', 'sin trabajo', 'desocupado'], '<i>-less</i>: sin.'),
    ('sufijo', 'driverless', ['sin conductor', 'autónomo'], None), ('sufijo', 'reliable', ['confiable', 'fiable'], '<i>-able</i>: verbo → adjetivo.'),
    ('sufijo', 'employee', ['empleado', 'empleada'], '<i>-ee</i>: la persona que recibe la acción.'), ('sufijo', 'employer', ['empleador', 'empleadora'], '<i>-er</i>: la persona que la hace.'),
    ('sufijo', 'usefulness', ['utilidad'], '<i>-ness</i>: adjetivo → sustantivo.'), ('sufijo', 'northward', ['hacia el norte', 'rumbo al norte'], '<i>-ward</i>: en dirección a.'),
]
SINONIMOS = [
    ('particularly', ['especially', 'specially']), ('suggestions', ['recommendations', 'proposals', 'advice']), ('traditional', ['conventional']),
    ('restrictions', ['limitations', 'limits', 'constraints']), ('goals', ['objectives', 'aims', 'targets']), ('quickly', ['rapidly', 'fast', 'swiftly']),
    ('huge', ['enormous', 'vast', 'massive', 'immense']), ('outcome', ['result']), ('enterprises', ['companies', 'firms', 'businesses', 'corporations']),
    ('improve', ['enhance', 'upgrade', 'better']), ('ensure', ['guarantee', 'assure', 'secure']), ('obtain', ['get', 'acquire', 'gain']),
    ('reduce', ['decrease', 'diminish', 'lower', 'cut']), ('purpose', ['aim', 'goal', 'objective', 'intention']), ('precise', ['accurate', 'exact']),
    ('choose', ['select', 'pick', 'elect']), ('begin', ['start', 'commence']), ('important', ['significant', 'relevant', 'crucial', 'essential']),
]
REFERENTES = [  # (oración, palabra, respuestas, por qué)
    ('Russell and Norvig published a book on AI. In it, THEY delve into four definitions of AI.', 'THEY', ['Russell and Norvig', 'Russell y Norvig'], 'Anafórica: retoma algo que apareció antes.'),
    ('Russell and Norvig published a book on AI. In IT, they delve into four definitions of AI.', 'IT', ['the book', 'book', 'el libro', 'a book on AI'], None),
    ('Many mobile devices incorporate speech recognition into THEIR systems.', 'THEIR', ['mobile devices', 'devices', 'dispositivos móviles', 'los dispositivos móviles'], None),
    ('After HE received her questions by email, the engineer sent back the results to Alice.', 'HE', ['the engineer', 'engineer', 'el ingeniero'], 'Catafórica: el referente aparece después.'),
    ('After he received HER questions by email, the engineer sent back the results to Alice.', 'HER', ['Alice'], 'Catafórica.'),
    ('IT is important to study English grammar.', 'IT', ['to study English grammar', 'estudiar gramática inglesa', 'it anticipatorio', 'anticipatory it'], '«It» anticipatorio: anticipa el sujeto real, que está más adelante.'),
    ('Let ME explain the concept to you.', 'ME', ['el autor', 'autor', 'the author'], 'Exofórica: la primera persona es EL AUTOR.'),
    ('Let me explain the concept to YOU.', 'YOU', ['el lector', 'lector', 'the reader', 'los lectores'], 'Exofórica: la segunda persona es EL LECTOR.'),
    ('As conversations emerge around the ethics of AI, WE can begin to see the first problems.', 'WE', ['el autor', 'autor', 'the author', 'el autor y los lectores'], 'Exofórica, primera persona: EL AUTOR.'),
    ('Both hardware and software need to be considered. THE FORMER refers to the actual machinery.', 'THE FORMER', ['hardware', 'el hardware'], '<i>the former</i> = el primero de los dos.'),
    ('Both hardware and software need to be considered. THE LATTER refers to the programs.', 'THE LATTER', ['software', 'el software'], '<i>the latter</i> = el segundo (el último) de los dos.'),
    ('Most programs are user-friendly but SOME are very complicated.', 'SOME', ['programs', 'some programs', 'programas', 'algunos programas'], 'Sustitución: <i>some</i> reemplaza al sustantivo para no repetirlo.'),
    ('Price is important to some people, while quality is important to OTHERS.', 'OTHERS', ['other people', 'people', 'otras personas', 'otros'], None),
    ('This is the old edition; I think I will buy the new ONE.', 'ONE', ['edition', 'the new edition', 'edición', 'la edición', 'la nueva edición'], 'Sustitución nominal: <i>one</i> = el núcleo que no se repite.'),
    ("I don't know the meaning of those words and I don't believe you DO either.", 'DO', ['know the meaning of those words', 'saber el significado de esas palabras', 'saber el significado', 'know the meaning'], 'Sustitución verbal: <i>do</i> reemplaza al verbo y su complemento.'),
    ('I am sure I will pass the exam and SO will you.', 'SO', ['pass the exam', 'aprobar el examen'], 'Sustitución verbal con <i>so</i>.'),
    ('Everyone uses computers. THESE SMART MACHINES make their lives easier.', 'THESE SMART MACHINES', ['computers', 'las computadoras', 'computadoras'], None),
    ('Physics is one of the most fundamental sciences, and ITS main goal is to understand the universe.', 'ITS', ['physics', 'la física', 'física'], None),
    ('An operating system is a master control program WHICH controls the functions of the computer.', 'WHICH', ['a master control program', 'master control program', 'an operating system', 'operating system', 'el sistema operativo', 'el programa de control maestro'], None),
    ('Al Schoenbrunn was an engineer WHOSE career involved the construction of nuclear reactors.', 'WHOSE', ['Al Schoenbrunn', 'an engineer', 'engineer', 'el ingeniero'], '<i>whose</i> = cuyo/a: de quién es lo que sigue.'),
]
FUNCIONES = [  # (fragmento, función, por qué)
    ('Artificial intelligence is the simulation of human intelligence processes by machines.', 'definición', 'Dice <b>qué es</b>: «X is …».'),
    ('Loop: A loop is any closed path in a circuit.', 'definición', None),
    ('Ampere: standard unit for measuring an electric current.', 'definición', None),
    ('Telecommunications is the transmission of signals over a distance for the purpose of communication.', 'definición', None),
    ('Engineering is broken down into several sub-disciplines: civil, mechanical, electrical and chemical engineering.', 'clasificación', 'Divide algo en <b>tipos</b> o grupos.'),
    ('AI programming focuses on three cognitive skills: learning, reasoning and self-correction.', 'clasificación', None),
    ('Computers can be divided into supercomputers, mainframes, minicomputers and microcomputers.', 'clasificación', None),
    ('The device is small, light and made of aluminium. It has a touch screen and two USB ports.', 'descripción', 'Dice <b>cómo es</b>: forma, partes, características.'),
    ('The new campus has 75,000 square metres of solar panels on its roof.', 'descripción', None),
    ('The circuit board is green and rectangular, with dozens of small components soldered to it.', 'descripción', None),
]
FUNCIONES_RESP = {'definición': ['definición', 'definir'], 'clasificación': ['clasificación', 'clasificar'], 'descripción': ['descripción', 'describir']}
CLOZE = [  # (oración con ___, palabras para elegir, respuesta)
    ('What are the ___ and disadvantages of artificial intelligence?', 'advantages · are · because · more · while', 'advantages'),
    ('Deep learning technologies ___ quickly evolving.', 'advantages · are · because · more · while', 'are'),
    ('They are evolving primarily ___ AI processes large amounts of data much faster.', 'advantages · are · because · more · while', 'because'),
    ('AI makes predictions ___ accurately than humanly possible.', 'advantages · are · because · more · while', 'more'),
    ('___ the huge volume of data would bury a human researcher, AI can turn it into actionable information.', 'advantages · are · because · more · while', 'while'),
    ('It is expensive to ___ the large amounts of data that AI programming requires.', 'process · requires · disadvantage', 'process'),
    ('It is expensive to process the large amounts of data that AI programming ___.', 'process · requires · disadvantage', 'requires'),
    ('This system is as fast ___ that one.', 'as · than · the · most', 'as'),
    ('The new processor is faster ___ the old one.', 'as · than · the · most', 'than'),
    ('The more RAM your computer can hold, ___ better.', 'as · than · the · most', 'the'),
    ('Python is one of the ___ popular programming languages.', 'as · than · the · most', 'most'),
    ('Programming languages are ___ by engineers.', 'use · uses · used · using', 'used'),
    ('Courses ___ a lot of units are hard to study.', 'contain · containing · contained', 'containing'),
]


def escribir(sec, en, resp, ph=None, ex=None):
    q = dict(sec=sec, tipo='escribir', en=en, resp=resp)
    if ph: q['ph'] = ph
    if ex: q['ex'] = ex
    return q


def practica():
    e = lambda x: html.escape(x, quote=False)
    qs = []
    for ing, resp, ex in FRASES:
        qs.append(escribir('frases', f'Traducí la frase sustantiva: <b>{e(ing)}</b>', resp, 'En español…', ex))
    for pista, ing, resp, ex in VERBOS:
        qs.append(escribir('verbos', f'Traducí ({pista}): <b>{e(ing)}</b>', resp, 'En español…', ex))
    for pista, ing, resp, ex in ESTRUCTURA:
        if pista in ('comparativo', 'superlativo'):
            qs.append(escribir('estr', f'Escribí el {pista} de <b>{ing.upper()}</b>', resp, 'En inglés…', ex))
        else:
            qs.append(escribir('estr', f'Traducí ({pista}): <b>{e(ing)}</b>', resp, 'En español…', ex))
    for w, resp, falso in VOCABULARIO:
        qs.append(escribir('vocab', f'¿Qué significa <b>{e(w)}</b>?' + (' <i>(ojo: falso amigo)</i>' if falso else ''), resp, 'En español…'))
    for c, trad, rel in CONECTORES:
        qs.append(escribir('con', f'Traducí el conector <b>{e(c.upper())}</b>', trad, 'En español…'))
        qs.append(escribir('con', f'¿Qué relación establece el conector <b>{e(c.upper())}</b>?', rel, RELACIONES, f'<b>{e(c)}</b> = {e(trad[0])}: {rel[0]}.'))
    for w, resp in ANTONIMOS:
        qs.append(escribir('ant', f'Escribí en inglés un antónimo de <b>{w.upper()}</b>', resp, 'En inglés…'))
    for tipo, w, resp, ex in PREFIJOS:
        if tipo == 'antónimo':
            qs.append(escribir('pref', f'Formá el antónimo de <b>{w.upper()}</b> con un prefijo', resp, 'En inglés…', ex))
        else:
            qs.append(escribir('pref', f'Traducí la palabra con {tipo}: <b>{w}</b>', resp, 'En español…', ex))
    for w, resp in SINONIMOS:
        qs.append(escribir('sin', f'Escribí en inglés un sinónimo de <b>{w.upper()}</b>', resp, 'En inglés…'))
    for o, w, resp, ex in REFERENTES:
        qs.append(escribir('ref', f'Referencia contextual: ¿a qué o a quién se refiere <b>{e(w)}</b>?<br><i>«{e(o)}»</i>', resp,
                           'La palabra del texto, o «el autor» / «el lector»…', ex))
    for frag, f, ex in FUNCIONES:
        qs.append(escribir('func', f'¿Qué función comunicativa tiene este fragmento?<br><i>«{e(frag)}»</i>', FUNCIONES_RESP[f],
                           'Definición, descripción o clasificación', ex))
    for o, banco, r in CLOZE:
        qs.append(escribir('cloze', f'Completá con una palabra: <i>«{e(o)}»</i><br><small>Elegí entre: {e(banco)}</small>', [r], 'Una palabra…'))
    return qs


SECCIONES = [
    ('frases', 'Traducir frases'), ('verbos', 'Voz pasiva, tiempos y modales'), ('estr', 'Casos especiales de estructura'),
    ('vocab', 'Vocabulario y falsos amigos'), ('con', 'Conectores'), ('ant', 'Antónimos'), ('pref', 'Prefijos y sufijos'),
    ('sin', 'Sinónimos'), ('ref', 'Referencia contextual'), ('func', 'Funciones comunicativas'), ('cloze', 'Completar (cloze)'),
]
GLOSARIO = [
    dict(t='Frase sustantiva', que='Un grupo de palabras sin verbo conjugado cuyo núcleo es un sustantivo. En inglés los modificadores van <b>antes</b> del núcleo (el último); en español, después: se traduce de derecha a izquierda.', re=r'frase sustantiva'),
    dict(t='Caso posesivo', que='<i>poseedor + \'s + lo poseído</i> → «lo poseído de el poseedor». Si el poseedor es un plural terminado en s, va solo el apóstrofo (<i>boys\' games</i> = los juegos de los chicos).', re=r"\w'(s\b|\s)"),
    dict(t='Voz pasiva', que='<i>to be</i> (en el tiempo que sea) + participio pasado. Se traduce con «ser + participio» o, más natural, con «se»: <i>is made</i> = se hace.', re=r'voz pasiva|\(voz pasiva'),
    dict(t='Tiempos verbales', que='<i>has/have</i> + participio: presente perfecto (ha hecho). <i>had</i> + participio: pasado perfecto (había hecho). <i>is/are</i> + -ing: presente continuo (está haciendo). <i>will</i>: futuro.', re=r'tiempo verbal'),
    dict(t='Verbos modales', que='<i>can</i> (poder), <i>may / might</i> (puede que, posibilidad), <i>must</i> (deber, obligación), <i>should</i> (debería, consejo). Van seguidos del verbo sin <i>to</i>.', re=r'modal'),
    dict(t='«It» anticipatorio', que='Un <i>it</i> que no se refiere a nada anterior: anticipa el sujeto real, que viene más adelante (con <i>to</i> + verbo o <i>that</i>). No se traduce.', re=r'it anticipatorio'),
    dict(t='Casos especiales', que='Expresiones que no se traducen palabra por palabra: <i>when it comes to</i>, <i>allow somebody to</i>…: se busca el sentido.', re=r'caso especial'),
    dict(t='Comparación', que='<i>-er than / more … than</i>: más … que. <i>the -est / the most</i>: el más. <i>as … as</i>: tan … como. <i>the more…, the more…</i>: cuanto más…, más…. Irregulares: good, bad, far, little, much.', re=r'comparaci[oó]n|comparativo|superlativo'),
    dict(t='La forma -ing', que='Según dónde está: antes de un sustantivo, adjetivo; después de un sustantivo, «que + verbo»; con <i>to be</i>, -ando/-endo; como sujeto o después de una preposición, infinitivo o sustantivo.', re=r'forma -ing'),
    dict(t='Cuantificadores', que='<i>any</i>: en negativas «ningún», en preguntas casi no se traduce, en afirmativas «cualquier». <i>all</i> = todo, entero; <i>every</i> = cada, todos.', re=r'cuantificador'),
    dict(t='Vocabulario técnico', que='Las palabras que se repiten en los textos de la materia: empresas, datos, procesos, energía, medio ambiente.', re=r'¿Qué significa'),
    dict(t='Falsos amigos', que='Palabras que se parecen a una del español pero significan otra cosa (<i>library</i> = biblioteca, no librería). Si la traducción «parecida» no tiene sentido en la oración, sospechá.', re=r'falso amigo'),
    dict(t='Conector (nexo)', que='Explicita la relación entre dos ideas. En la prueba: transcribirlo, decir la relación lógica y traducirlo en su contexto; en el cuadro, las dos ideas que une.', re=r'conector'),
    dict(t='Relaciones lógicas', que='<b>Adición</b>, <b>causa</b>, <b>efecto</b>, <b>condición</b>, <b>secuencia en el tiempo</b>, <b>contraste</b>, <b>ejemplificación</b>, <b>propósito</b>, <b>resumen</b>, <b>disyunción</b>, <b>énfasis</b> y <b>aclaración</b> (como en el apunte «A tener en cuenta»).', re=r'relación'),
    dict(t='Antónimo', que='La palabra de significado <b>opuesto</b>. En la prueba te dan una palabra que no está en el texto y el renglón donde está su opuesta.', re=r'antónimo de'),
    dict(t='Prefijos', que='<b>un-, in-, im-, il-, ir-, dis-</b>: lo contrario. <b>counter-</b>: en contra. <b>mis-</b>: mal. <b>over-</b>: de más. <b>under-</b>: de menos. <b>re-</b>: de nuevo. <b>self-</b>: auto. <b>pre- / post-</b>: antes / después.', re=r'prefijo'),
    dict(t='Sufijos', que='<b>-able</b>: que se puede. <b>-ee</b>: quien recibe la acción; <b>-er</b>: quien la hace. <b>-en</b>: hace verbo. <b>-ful / -less</b>: con / sin. <b>-ness, -ment</b>: hacen sustantivo. <b>-ly</b>: -mente. <b>-ward</b>: hacia. <b>-fold</b>: veces.', re=r'sufijo'),
    dict(t='Sinónimo', que='La palabra de significado <b>parecido</b>, de la misma clase (sustantivo, verbo, adjetivo).', re=r'sinónimo de'),
    dict(t='Referencia contextual', que='<b>Anafórica</b>: el referente está antes. <b>Catafórica</b>: está después. Probá reemplazar la palabra por su referente: si se entiende, está bien.', re=r'Referencia contextual'),
    dict(t='Pronombres', que='<i>it / its</i>: algo singular. <i>they / them / their</i>: plural. <i>he / him / his</i>, <i>she / her</i>: personas. <i>which / that</i>: que, el cual. <i>whose</i>: cuyo. <i>these</i>: estos.', re=r'se refiere\s+(IT|ITS|THEY|THEIR|THEM|HE|HER|HIS|WHICH|THAT|WHOSE|THESE)\b'),
    dict(t='Referencia exofórica', que='El referente está <b>fuera del texto</b>. Primera persona (I, me, we, our): <b>el autor</b>. Segunda persona (you, your): <b>el lector</b>.', re=r'se refiere\s+(I|ME|MY|WE|US|OUR|YOU|YOUR)\b'),
    dict(t='Sustitución', que='Una palabra reemplaza a otra para no repetirla: <i>one, ones, some, others</i> reemplazan un sustantivo; <i>do</i> y <i>so</i>, un verbo con su complemento.', re=r'se refiere\s+(ONE|ONES|SOME|OTHERS|DO|SO)\b'),
    dict(t='The former / the latter', que='Cuando se nombraron dos cosas: <i>the former</i> = la primera; <i>the latter</i> = la segunda (la última).', re=r'THE (FORMER|LATTER)'),
    dict(t='Funciones comunicativas', que='<b>Definición</b>: qué es algo (X is…). <b>Descripción</b>: cómo es (partes, forma, características). <b>Clasificación</b>: en qué tipos se divide (there are three types…, can be divided into…).', re=r'función comunicativa'),
    dict(t='Cloze', que='Completar un texto con palabras dadas. Mirá qué <b>clase</b> de palabra falta (verbo, sustantivo, conector, comparativo) y que concuerde con lo que está antes y después.', re=r'Completá con una palabra'),
]


def armar_quiz():
    porsec = {k: [] for k, _ in SECCIONES}
    for q in practica():
        porsec[q['sec']].append({k: v for k, v in q.items() if k != 'sec'})
    return dict(
        titulo='Inglés 2 · Práctica para escribir',
        descripcion='Frases y palabras cortas como las de la prueba: escribís la respuesta y te dice si está bien. No importan las mayúsculas, las tildes ni el artículo del principio. Si no la sabés, «Ver respuesta»; si tu traducción dice lo mismo con otras palabras, «Mi respuesta también vale».',
        secciones=[dict(titulo=t, preguntas=porsec[k]) for k, t in SECCIONES if porsec[k]],
        glosario=GLOSARIO,
    )


# ───────────────────────── Las resoluciones ─────────────────────────
class Html(str):
    """Una respuesta que ya viene en HTML (para marcar en negrita lo que se completó)"""


# Un ejercicio es (consigna, [(ítem, respuesta), …]) o (consigna, 'tabla', [columnas], [filas])
SIMULACRO = ('Simulacro de la prueba 2024 · Inteligencia artificial', [
    ('1. REFERENCIA EN EL CONTEXTO: ¿A qué hacen referencia los siguientes términos?', [
        ('Their (4)', 'vendors: los proveedores (vendedores) que promocionan sus productos y servicios'),
        ('They (5)', 'vendors: los proveedores'),
        ('That (10)', 'a chatbot: el chatbot'),
        ('These rules (14)', 'rules for how to turn the data into actionable information: las reglas para convertir los datos en información útil (renglón 13)'),
        ('Which (14)', 'these rules: estas reglas, que se llaman algoritmos'),
        ('It (20)', 'AI: la inteligencia artificial'),
        ('It (23)', '«it» anticipatorio: no se refiere a nada anterior; anticipa «that AI tools complete jobs quickly…» (que las herramientas de IA completen los trabajos rápido)'),
        ('Their (24)', "today's largest and most successful enterprises: las empresas más grandes y exitosas de hoy")]),
    ('2. LÉXICO: Encuentre los sinónimos y antónimos de las siguientes palabras.', [
        ('Sinónimo de Particularly (1)', 'especially'), ('Sinónimo de Competing (4)', 'scrambling'),
        ('Antónimo de Inapplicable (14)', 'actionable'), ('Antónimo de Not adjust (18)', 'fine-tune')]),
    ('3. FUNCIONES DEL LENGUAJE: Transcriba el nexo, diga qué tipo de relación lógica establece y tradúzcalo teniendo en cuenta el contexto. '
     'Además, traduzca los nexos de los renglones 4 y 12 en los contextos que le dan sentido.', 'tabla',
     ['Línea', 'Nexo', 'Relación lógica', 'Traducción del nexo / contexto que le da sentido'], [
        ('4', 'As', 'secuencia en el tiempo (simultaneidad)', 'A medida que: «A medida que creció el entusiasmo por la IA, los proveedores se apuraron a promocionar cómo sus productos y servicios usan IA».'),
        ('5', 'such as', 'ejemplificación', 'como, tales como (solo nexo).'),
        ('12', 'as well as', 'adición', 'así como también: «La programación de IA se centra en tres habilidades cognitivas: el aprendizaje, el razonamiento y también la autocorrección».'),
        ('20', 'because', 'causa', 'porque (solo nexo).'),
        ('22', 'like', 'ejemplificación', 'como (solo nexo). En ese renglón también está TO (ensure): propósito, «para asegurar».')]),
    ('4. ASPECTOS DE ESTRUCTURA: Interprete los siguientes fragmentos teniendo en cuenta los casos especiales.', [
        ('a. When it comes to repetitive, detail-oriented tasks, it is expected that AI tools complete jobs quickly and with relatively few errors.',
         'Cuando se trata de tareas repetitivas y que requieren atención al detalle, se espera que las herramientas de IA completen los trabajos rápidamente '
         'y con relativamente pocos errores. (Casos especiales: «when it comes to» = cuando se trata de; «it is expected that» = se espera que: «it» anticipatorio + voz pasiva → «se».)'),
        ("b. AI allows today's largest and most successful enterprises to improve their operations and gain advantage on their competitors.",
         'La IA les permite a las empresas más grandes y exitosas de la actualidad mejorar sus operaciones y sacar ventaja sobre sus competidores. '
         "(Casos especiales: caso posesivo «today's» = de hoy; superlativos «largest» y «most successful»; «allow … to + verbo» = permitir … + infinitivo.)")]),
    ('5. LECTOCOMPRENSIÓN: Indique si las siguientes oraciones son verdaderas (V) o falsas (F) según el texto. Consigne los renglones de referencia.', [
        ('La programación de IA se centra en tres habilidades cognitivas.', 'V · renglón 12.'),
        ('El proceso de aprendizaje se enfoca en elegir el algoritmo correcto.', 'F · renglones 13 y 16: el aprendizaje se enfoca en adquirir datos y crear reglas; elegir el algoritmo correcto es el razonamiento.')]),
    ('6. TÍTULO. Observe en el texto las líneas A, B, C y elija uno de los títulos para cada espacio en blanco.', [
        ('A', 'What is artificial intelligence (AI)?'), ('B', 'How does AI work?'), ('C', 'Why is artificial intelligence important?')]),
    ('7. IDEA PRINCIPAL: Indique cuál oración expresa más acabadamente la idea principal del texto.', [
        ('Idea principal', '2. Se define a la inteligencia artificial, cómo funciona y por qué es crucial para las empresas.')]),
    ('8. FUNCIONES COMUNICATIVAS: Indique la función comunicativa existente en los renglones 1-2.', [
        ('Función', 'DEFINICIÓN: se define qué es la inteligencia artificial (la simulación de los procesos de la inteligencia humana por máquinas, sobre todo por sistemas informáticos).')]),
    ('9. CLOZE: Complete el texto con las palabras dadas.', [
        ('El texto completo', Html(
            'What are the <b>advantages</b> and <b>disadvantages</b> of artificial intelligence? Artificial neural networks and deep learning artificial intelligence '
            'technologies <b>are</b> quickly evolving, primarily <b>because</b> AI processes large amounts of data much faster and makes predictions <b>more</b> '
            'accurately than humanly possible. <b>While</b> the huge volume of data being created on a daily basis would bury a human researcher, AI applications '
            'that use machine learning can take that data and quickly turn it into actionable information. As of this writing, the primary disadvantage of using AI '
            'is that it is expensive to <b>process</b> the large amounts of data that AI programming <b>requires</b>.'))]),
])
EJEMPLO = ('Ejemplo de parcial · Ecological engineering', [
    ('1) Responder las siguientes preguntas en ESPAÑOL.', [
        ('¿En qué se están especializando muchas firmas privadas?',
         'En la restauración de arroyos, ríos, lagos, bosques, pastizales y humedales; en la rehabilitación de tierras mineras y de terrenos urbanos '
         'abandonados o contaminados (brownfields), y en la creación de humedales de tratamiento y sitios de fitorremediación (renglones 10 a 13).')]),
    ('2) Traducir los siguientes fragmentos al ESPAÑOL.', [
        ('This paper will review the history of ecological engineering', 'Este trabajo repasará (revisará) la historia de la ingeniería ecológica.'),
        ('Ecological engineering must involve the creation and restoration of an ecosystem.', 'La ingeniería ecológica debe implicar la creación y la restauración de un ecosistema.')]),
    ('3) Referencia contextual. Indicar a qué o quién hacen referencia las siguientes palabras o frases.', [
        ('its (línea 2)', 'human society: la sociedad humana (su ambiente natural)'),
        ('its (línea 4)', 'ecological engineering: la ingeniería ecológica (sus objetivos)'),
        ('I (línea 16)', 'el autor (referencia exofórica: primera persona)'),
        ('which (línea 21)', 'case studies and pollution control projects: los estudios de caso y los proyectos de control de la contaminación'),
        ('These two fields (línea 23)', 'engineering and ecology: la ingeniería y la ecología'),
        ('Their (línea 25)', 'ecologists: los ecólogos'),
        ('its (línea 32)', 'ecological engineering: la ingeniería ecológica (su progreso)')]),
    ('4) Indicar los antónimos de las siguientes palabras.', [
        ('apart (línea 29)', 'together («Ecologists and engineers need to work together»)'), ('artificial (línea 3)', 'natural («natural environment»)')]),
    ('5) Indicar los sinónimos de las siguientes palabras.', [
        ('suggestions (línea 24)', 'recommendations'), ('traditional (línea 6)', 'conventional'), ('Restrictions (línea 31)', 'limitations')]),
    ('6) Completar el siguiente cuadro de conectores en ESPAÑOL.', 'tabla', ['Conector', 'Traducción', 'Tipo de relación', 'Idea uno', 'Idea dos'], [
        ('Both…and (línea 5)', 'tanto… como', 'adición', 'Los nuevos ecosistemas sustentables tienen valores humanos…', '…y también valores ecológicos.'),
        ('Yet (línea 14)', 'sin embargo', 'contraste', 'Parece que empieza a darse la sincronización perfecta entre la academia, las publicaciones, los recursos de investigación y la práctica.',
         'El campo todavía no tiene una acreditación formal en ingeniería y lo aceptan con reservas en la universidad y en el trabajo.'),
        ('Whether…or (línea 37)', 'si… o', 'disyunción (alternancia)', 'Alguien habla de ingeniería ecológica…', '…o quizás solo de ingeniería ambiental (o simplemente de «ingeniería verde»).'),
        ('to (línea 43)', 'para', 'propósito (finalidad)', 'La sociedad haría bien en reconocer y usar las funciones importantes de la naturaleza…', '…para lograr una sociedad resiliente y sustentable.')]),
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
.it .r b { color: #0d3f8f; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 8pt; font-size: 9pt; }
th, td { border: 1px solid #b9b6ad; padding: 4pt 5pt; vertical-align: top; text-align: left; }
th { background: #f3f2ee; }
td.a { color: #1f5fbf; }
tr { break-inside: avoid; }
.paso { display: grid; grid-template-columns: 20pt 1fr; gap: 6pt; margin: 5pt 0; break-inside: avoid; }
.paso .n { width: 17pt; height: 17pt; border-radius: 50%; background: #2d8992; color: #fff; font-weight: 700; text-align: center; line-height: 17pt; font-size: 9pt; }
.paso b.t { display: block; }
.tip { background: #e4f3f5; border-left: 3pt solid #2d8992; border-radius: 4pt; padding: 5pt 9pt; margin: 6pt 0; break-inside: avoid; }
'''


def ejercicios_html(doc):
    e = html.escape
    val = lambda x: x if isinstance(x, Html) else e(x)
    c = ''
    for ej in doc[1]:
        c += f'<div class="ej">{e(ej[0])}</div>'
        if ej[1] == 'tabla':
            cab, filas = ej[2], ej[3]
            c += '<table><tr>' + ''.join(f'<th>{e(x)}</th>' for x in cab) + '</tr>'
            c += ''.join(f'<tr><td><b>{e(f[0])}</b></td>' + ''.join(f'<td class="a">{val(x)}</td>' for x in f[1:]) + '</tr>' for f in filas) + '</table>'
        else:
            for it, r in ej[1]:
                c += f'<div class="it">• {e(it)}<div class="r">→ {val(r)}</div></div>'
    return c


def doc_resuelto(doc, css_fuentes):
    cuerpo = (f'<span class="resuelto">RESUELTO</span><h1>{html.escape(doc[0])}</h1>'
              f'<p class="bajada">Las respuestas van en azul. Las consignas son las mismas de las hojas anteriores; los números entre paréntesis son los renglones del texto.</p>{ejercicios_html(doc)}')
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{css_fuentes}{CSS}</style></head><body>{cuerpo}</body></html>'


PASOS = [
    ('Referencia en el contexto', 'Buscá el referente: casi siempre está <b>antes</b> (anafórica) y a veces <b>después</b> (catafórica). Si es primera persona (I, we, our) la respuesta es <b>el autor</b>; si es segunda (you, your), <b>el lector</b>. Un <i>it</i> que anticipa «to + verbo» o «that…» es el <b>it anticipatorio</b>.'),
    ('Léxico: sinónimos y antónimos', 'Te dan una palabra que <b>no</b> está en el texto y el renglón: buscá ahí la de significado parecido (sinónimo) u opuesto (antónimo), de la misma clase. Pueden ser de más de una palabra (<i>not adjust</i> ↔ <i>fine-tune</i>).'),
    ('Funciones del lenguaje (nexos)', 'Transcribí el nexo del renglón, decí qué <b>relación lógica</b> establece y traducilo según el contexto. En los renglones que lo piden, traducí también la oración que le da sentido.'),
    ('Aspectos de estructura', 'Interpretá el fragmento atendiendo a los <b>casos especiales</b>: voz pasiva (se…), <i>it</i> anticipatorio, comparativos y superlativos, caso posesivo, la forma <i>-ing</i>, expresiones como <i>when it comes to</i>.'),
    ('Lectocomprensión (V o F)', 'Marcá V o F y anotá el <b>renglón</b> que lo justifica. Ojo con los cambios sutiles: otro proceso, otra cantidad, una negación.'),
    ('Título e idea principal', 'Cada título va con el bloque (A, B, C) que resume: <i>What is…</i> suele ir con la definición, <i>How does… work</i> con el funcionamiento, <i>Why is… important</i> con los beneficios. La idea principal es la que cubre <b>todo</b> el texto.'),
    ('Funciones comunicativas', '<b>Definición</b> (qué es: <i>X is…</i>), <b>descripción</b> (cómo es) o <b>clasificación</b> (en qué tipos se divide). Además, decí qué se define, describe o clasifica.'),
    ('Cloze', 'Mirá qué <b>clase</b> de palabra falta (verbo, conector, comparativo, sustantivo) y que concuerde con lo de antes y después. Cada palabra se usa una vez.'),
]
REFERENCIA_TABLA = [
    ('Anafórica', 'el referente está antes', 'Many devices incorporate speech recognition into <b>their</b> systems → devices'),
    ('Catafórica', 'el referente está después', 'After <b>he</b> received the questions, <b>the engineer</b> sent the results'),
    ('Exofórica', 'fuera del texto: el autor o el lector', 'Let <b>me</b> explain it to <b>you</b> → el autor / el lector'),
    ('It anticipatorio', 'anticipa el sujeto real (to… / that…)', '<b>It</b> is important <b>to study grammar</b>'),
    ('Sustitución', 'one, some, others (sustantivo); do, so (verbo)', 'I will buy the new <b>one</b> → edition'),
    ('The former / the latter', 'el primero / el segundo de dos', 'hardware and software: <b>the former</b> → hardware'),
]
CONECTORES_TABLA = [
    ('Adición', 'in addition, furthermore, moreover, as well as, besides, both … and, along with'),
    ('Causa', 'because (of), since, as, due to, owing to, in view of, for'),
    ('Efecto', 'so, therefore, hence, thus, consequently, as a result, for this reason'),
    ('Condición', 'if, unless, as long as, provided (that), or else'),
    ('Secuencia en el tiempo', 'after, before, meanwhile, at the same time, eventually (= finalmente), since then, first, then, at last'),
    ('Contraste', 'but, however, although, even though, nevertheless, yet, whereas, while, despite, in spite of, on the other hand'),
    ('Ejemplificación', 'e.g., for instance, for example, such as, like, namely'),
    ('Propósito', 'to + verbo, in order to, for + -ing, so that, so as to'),
    ('Resumen', 'in conclusion, in summary, to summarize'),
    ('Disyunción', 'either … or, neither … nor, whether … or'),
    ('Énfasis', 'above all, particularly, actually, in particular, indeed, in fact'),
    ('Aclaración', 'that is (to say), i.e., in other words'),
]
ESTRUCTURA_TABLA = [
    ('Voz pasiva', '<i>These rules are called algorithms</i>', 'Estas reglas <b>se llaman</b> algoritmos'),
    ('It anticipatorio + pasiva', '<i>it is expected that…</i>', '<b>se espera que…</b>'),
    ('Expresión fija', '<i>when it comes to…</i>', '<b>cuando se trata de…</b>'),
    ('Caso posesivo', "<i>today's enterprises</i>", 'las empresas <b>de hoy</b>'),
    ('Superlativo', '<i>the largest / the most successful</i>', '<b>las más grandes / las más exitosas</b>'),
    ('Comparación', '<i>faster than · as fast as · the more…, the better</i>', '<b>más rápido que · tan rápido como · cuanto más…, mejor</b>'),
    ('allow … to', '<i>AI allows enterprises to improve</i>', 'la IA <b>les permite a</b> las empresas <b>mejorar</b>'),
    ('any', '<i>Any evidence will be enough</i>', '<b>Cualquier</b> prueba será suficiente'),
]
ING_TABLA = [
    ('antes de un sustantivo', '<i>the living cell</i>', 'adjetivo: la célula <b>viva</b>'),
    ('después de un sustantivo', '<i>courses containing units</i>', 'que + verbo: cursos <b>que contienen</b>'),
    ('con to be (continuo)', '<i>he is working</i>', '-ando / -endo: está <b>trabajando</b>'),
    ('sujeto', '<i>Swimming is healthy</i>', 'infinitivo o sustantivo: <b>nadar / la natación</b>'),
    ('después de preposición', '<i>tips for improving</i>', 'infinitivo: consejos para <b>mejorar</b>'),
]
AFIJOS_TABLA = [
    ('un-, in-, im-, il-, ir-, dis-', 'lo contrario', 'unfair, inaccurate, immature, illegible, irresponsible, disagree'),
    ('counter- · mis- · over- · under-', 'en contra · mal · de más · de menos', 'counterclockwise, misunderstanding, overestimate, underestimate'),
    ('re- · self- · pre- · post-', 'de nuevo · auto · antes · después', 'rewrite, self-service, predate, postwar'),
    ('-able · -ful · -less', 'que se puede · con · sin', 'reliable, powerful, jobless'),
    ('-er · -ee', 'quien hace · quien recibe la acción', 'employer, employee'),
    ('-en · -ly · -ness / -ment · -ward · -fold', 'verbo · -mente · sustantivo · hacia · veces', 'shorten, slowly, usefulness, development, northward, twofold'),
]


def resumen_html(css_fuentes):
    tabla = lambda cab, filas: '<table><tr>' + ''.join(f'<th>{x}</th>' for x in cab) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in f) + '</tr>' for f in filas) + '</table>'
    c = ('<h1>Inglés 2 · Cómo se encara la prueba</h1><p class="bajada">La prueba de suficiencia (PdS) es de lectocomprensión: un texto técnico en inglés, con los renglones numerados, '
         'y ejercicios que se responden en español. Con 7 o más, la materia queda aprobada. El simulacro y el ejemplo de parcial resueltos están en los otros archivos.</p>')
    c += '<h2>Cada ejercicio</h2>' + ''.join(f'<div class="paso"><span class="n">{i}</span><div><b class="t">{t}</b>{x}</div></div>' for i, (t, x) in enumerate(PASOS, 1))
    c += '<h2>Referencia contextual</h2>' + tabla(['Tipo', 'Qué es', 'Ejemplo'], [(f'<b>{a}</b>', b, x) for a, b, x in REFERENCIA_TABLA])
    c += '<h2>Conectores y su relación</h2>' + tabla(['Relación', 'Conectores'], [(f'<b>{a}</b>', f'<i>{b}</i>') for a, b in CONECTORES_TABLA])
    c += '<div class="tip"><b>Ojo:</b> <i>since</i>, <i>as</i>, <i>while</i> y <i>then</i> pueden ser de tiempo o de otra relación (causa, contraste): decidilo por el contexto. <i>Eventually</i> es «finalmente», no «eventualmente».</div>'
    c += '<h2>Casos especiales de estructura</h2>' + tabla(['Caso', 'En inglés', 'En español'], [(f'<b>{a}</b>', b, x) for a, b, x in ESTRUCTURA_TABLA])
    c += '<h2>La forma -ing</h2>' + tabla(['Dónde está', 'Ejemplo', 'Se traduce como'], [(f'<b>{a}</b>', b, x) for a, b, x in ING_TABLA])
    c += '<h2>Prefijos y sufijos</h2>' + tabla(['Prefijo o sufijo', 'Significa', 'Ejemplos'], [(f'<b>{a}</b>', b, f'<i>{x}</i>') for a, b, x in AFIJOS_TABLA])
    c += ('<h2>Frase sustantiva</h2><p>El núcleo es el <b>último</b> sustantivo; lo de antes lo modifica. Se traduce de derecha a izquierda: '
          '<i>air pollution control systems</i> → sistemas de control de la contaminación del aire. Lo que va <b>después</b> del núcleo (<i>which…</i>, <i>-ing</i>, participio) se traduce «que…».</p>')
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Inglés 2 · Cómo se encara la prueba</title><style>{css_fuentes}{CSS}</style></head><body>{c}</body></html>'


# Los originales (en blanco) y cuántas hojas tienen: el PDF final es esas hojas + las resueltas
ORIGINALES = [
    ('02-simulacro-de-la-prueba-2024-inteligencia-artificial.pdf', 3, SIMULACRO),
    ('03-ejemplo-de-parcial-ecological-engineering.pdf', 3, EJEMPLO),
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
    with open(os.path.join(RAIZ, 'quiz', 'ingles-2.json'), 'w', encoding='utf-8') as fh:
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

    def guardar(doc, ruta, titulo):
        doc.set_metadata({'title': titulo, 'author': '', 'subject': '', 'keywords': '', 'creator': '', 'producer': '', 'creationDate': '', 'modDate': ''})
        doc.del_xml_metadata()
        doc.save(ruta + '.tmp', garbage=3, deflate=True)
        doc.close()
        os.replace(ruta + '.tmp', ruta)

    with tempfile.TemporaryDirectory() as tmp:
        ruta = os.path.join(tmp, 'resumen.pdf')
        imprimir(chromium, resumen_html(css), ruta)
        d = pymupdf.open(ruta)
        print('01-resumen-como-se-encara-la-prueba.pdf', d.page_count, 'hojas')
        guardar(d, os.path.join(DESTINO, '01-resumen-como-se-encara-la-prueba.pdf'), 'Inglés 2 · Cómo se encara la prueba')
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
            guardar(final, ruta, f'Inglés 2 · {doc[0]}')


if __name__ == '__main__':
    main()
