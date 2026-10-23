# Página de Ingeniería en Sistemas de Información

## Estructura
- `index.html` → la página. Todo el contenido se edita al principio del `<script>`:
  - `CARRERA` → el plan de estudios (página de inicio): materias por nivel, correlativas y electivas.
  - `MATERIAS` → el contenido de cada materia (parciales, material, videos, actividades), usando como clave el número de la materia (ej: `26` = Redes de Datos).
- `material/<materia>/<parcial>/<teorico|practico>/` → los PDF de cada materia (ej: `material/redes-de-datos/p2/teorico/apunte.pdf`).
- `material/<materia>/actividades/` → trabajos prácticos y entregas.
- `miniaturas/` → la tapa de cada PDF (se genera con `herramientas/miniaturas.py`).
- `quiz/` → las preguntas de cada quiz (JSON) y sus imágenes.
- `horarios/2026.json` → los horarios de cursado de todas las comisiones (para el Cronograma). Se arma con `herramientas/horarios/extraer.py` a partir de los PDF de horarios de la facultad.
- `practica/` → la Práctica por partes: el corrector de Python (`corrector.py`), el Java del navegador (`practica/java/`) y un JSON por ejercicio (`practica/dao-p1/` en Python, `practica/bk-p1/` en Java). Los ejercicios por partes de Backend van en `practica/bk-practica/` (lo que trae el preenunciado) y `practica/bk-parcial/` (lo que agrega el parcial). Se arman con `herramientas/practica/` y `herramientas/practica-java/`; el Java del navegador, con `herramientas/java-navegador/`. Los de TPA van en `practica/tpa-p1/`, `tpa-p2/` (con sus figuras en `img/`, y corren en el Octave del navegador, `practica/octave/octave.js`) `tpa-p3/` (C++ de la ESP32) y `tpa-tp/` (el TP: corren en la placa simulada, `practica/esp32/esp32.js`, con los casos del profe en `practica/esp32/profe/`); se arman con `herramientas/tpa-practica/`.

## Links
Cada página tiene su propio link, por ejemplo:
- `#/` → inicio: las clases de hoy, lo que viene y dónde quedaste
- `#/cronograma` → el cronograma y el calendario de la cursada
- `#/plan` → Plan de la carrera: el resumen del avance
- `#/nivel/3` → las materias de 3º Nivel (`#/nivel/0` es el Ingreso)
- `#/m26` → Redes de Datos
- `#/m26/p2` → 2º Parcial de Redes de Datos
- `#/m26/p2/teorico/videos` → videos del teórico

## Agregar una materia con contenido
Dentro de `MATERIAS`, copiá el bloque de la `26` y cambiale el número por el de la materia (el número está en `CARRERA.materias`). En la lista de su año, su fila muestra la etiqueta "Material" (y si es electiva, pasa a tener link).

## Página de la materia
`#/m201` (`viewMateria`). Solo el material y la info de la materia: nada de tu cursada (comisión, días, fechas, notas: eso va en el Cronograma) ni de tu avance (va en "Tu avance").
- **Arriba**: la sigla, el año y el nombre; a la derecha, cómo se aprueba ("Directa con 6 · Sin regularidad", de `condiciones`; al tocarlo se despliega cada requisito) y el ZIP completo.
- **Las partes**: cada parcial / TPI / final es una tarjeta simple, con su nombre y su descripción corta. Lo suelto (Cuestionarios, Actividades) va abajo en filas, y al final el cuadro de comisiones.
- **Adentro** (un parcial, el TPI, una sección…): todo está en una sola fila de pestañas, fija arriba, y cada pestaña muestra su contenido directo, sin más páginas para entrar. A la izquierda, "‹ BDA Backend de Aplicaciones" (la sigla con el color de la materia y el nombre) vuelve a la materia; en el celular queda solo la sigla. Al entrar a una parte se abre su primera pestaña.
- **Los archivos**: cada bloque es una tarjeta con una fila por archivo (tapa, nombre y detalle); los niveles (Esencial, Para profundizar, Extra) son títulos.

## Estilo
Colores y fuentes como Claude: fondo casi blanco (`--bg: #fcfcfb`), barra lateral apenas más oscura, bordes grises neutros, títulos en Source Serif 4 y texto en Inter (de Google Fonts), letra base de 15 px y puntos de color chicos. El acento sale del color de la carrera y queda solo para los botones principales, el logo, lo de "hoy" y lo que estás cursando; los íconos, títulos y etiquetas van en gris (bloque "Suave, como Claude" al final del `<style>`). Los colores están en `:root` al principio del `<style>`, con su versión para el modo oscuro. Además del acento hay una paleta chica y apagada: `--ok` (verde salvia: aprobado, correcto), `--rojo`, `--rojo-f`, `--rojo-l` y `--error` (ladrillo suave: errores, "No"), `--mark` (arena: resaltados) y `--nv2` / `--nv3` (gris azulado y gris: las líneas de "Para profundizar" y "Extra"; la de "Esencial" va en el acento). Los dibujos de las herramientas usan los mismos tonos.

**Color de la carrera** (`CARRERA.color`): el celeste de la insignia de Sistemas (#3ce8ee), pasado a una versión suave con el mismo brillo que el naranja de Claude: `acento` #2d8992 (botones, links, hoy), `logo` #3a9fab y `suave` #e4f3f5 (fondos), con otros tres para el modo oscuro. Al cargar, pisa `--accent`, `--brand` y `--accent-soft`. Si la web suma otras carreras, cada una trae su `color` (el de su insignia, en versión suave) y la web toma ese.

## Barra lateral
A la izquierda queda fija una barra (`renderLado`) con:
- **Inicio**, **Cronograma** y **Plan de la carrera**, y el botón de modo claro/oscuro arriba.
- **Cursando**: las materias del cronograma de este cuatrimestre o, si no hay cronograma, las marcadas como "Cursando" en el plan. Cada una con el punto de su color (el de los horarios).
- La materia abierta se despliega con sus partes (parciales, TPI, secciones como Cuestionarios, Actividades): `partesMateria`. Tocar el nombre de la materia lleva a su página. Si abrís una materia que no estás cursando, aparece arriba en "Estás viendo".
- Abajo, **Tu avance** (el % y cuántas materias), que lleva al plan.

En el celular la barra es un menú que se abre con el botón de arriba a la izquierda.
Adentro de una parte, una sola fila de pestañas con todo (sale de `pestanasDe(p)`), siempre en el mismo orden: **Temas**, el material de cada sección que tiene archivos (Teórico, Práctico…), **Práctica**, **Videos** (todos juntos; si hay de más de una sección, arriba se elige "Teórico · Práctico") y al final **Parciales / Simulacros**. El quiz y las herramientas no son pestañas: van arriba de Parciales, en "Herramientas para practicar" (`parcialBox`). En una parte de una sola página (`secciones: []`) o una sección de la materia: Temas, Material, Práctica (con las herramientas) y Videos. Arriba de cada pestaña va el nombre de la parte y su descripción (`cabParte`). Si hay una sola pestaña, la fila muestra solo la vuelta a la materia.

**Colores de las materias** (`colorMat`): salen de `COLORES_PDF` (el color de cada materia en los horarios en PDF) y se bajan de tono: un fondo suave, un borde y un texto oscuro del mismo tono, y otros tres para el modo oscuro. Los grises se oscurecen un poco y los naranjas fuertes pasan a un terracota suave.

## Inicio
Sin buscador (`viewInicio`):
- **Hoy**: las clases del día según el cronograma, con "en 15 min" o "ahora". Si no hay cronograma, un acceso para armarlo; si hoy no cursás, cuándo es la próxima clase.
- **Lo que viene**: las próximas fechas del calendario (parciales, recuperatorios y TP, también las tentativas), con "Repasar" en los parciales.
- **Seguí donde dejaste**: las últimas páginas de estudio que abriste (una por parcial; si abriste un ejercicio de práctica, ese, con el paso en el que vas). Se guardan en el navegador (`isi-vistas`).

## Cronograma
`#/cronograma` (`viewCronograma`). Los horarios de todas las comisiones salen de `horarios/2026.json` (se baja la primera vez que se abre).
- **Armarlo**: "+ Materia" muestra las materias de ese cuatrimestre que no tenés aprobadas ni regulares; primero las que podés cursar según las correlativas. Al elegir una se marcan todas sus comisiones en la grilla (mañana, tarde y noche), punteadas; al pasar por una se marcan sus dos días juntos y al tocarla queda elegida. Las que se pisan con algo que ya elegiste salen en rojo suave y no se pueden elegir. Tocando una materia elegida (en la fila de arriba o en la grilla) se le cambia la comisión; con la ✕ se saca. Mientras se elige, cada comisión lleva un pulgar verde si está recomendada o rojo si no, según el cuadro de comisiones de la materia (`recomendada` y `motivo` o `comentario`, que se ven al pasar el mouse); si de esa comisión no hay nada cargado, no lleva nada. En "+ Materia" se ve cuántas comisiones recomendadas tiene cada una.
- **Siglas**: en el cronograma cada materia se ve con su sigla (`abr`, ej.: DAO). En la grilla guardada, la sigla va grande y centrada, y abajo el nombre, la comisión y el horario; en las próximas fechas, en las notas y en la fila de arriba al editar, la sigla (el nombre completo aparece al pasar el mouse).
- **Guardado**: la grilla muestra solo los turnos que usás (si todo es a la noche, solo la noche) y en el celular, un día a la vez. Con "Editar" se vuelve a armar. Se puede pasar del 1º al 2º cuatrimestre.
- **Calendario**: a la derecha (en el celular, abajo), los meses de la cursada de a dos: marzo a junio o agosto a noviembre en fila, y abajo, a lo largo, julio o diciembre (por las fechas que caen después; `mesesCuatri` devuelve cinco meses). Tocando un día se anota qué hay (Parcial, Recuperatorio o TP), con un nombre y la materia; el día se pinta con el color de la materia. Con dos cosas el mismo día, el día se parte en diagonal (de abajo a la izquierda hasta arriba a la derecha), un color de cada lado; con tres, en tres franjas (se muestran hasta tres). Cada tipo tiene su ícono, que va en la parte de su color: ★ parcial, ☆ recuperatorio (la estrella del parcial, vacía) y ● TP (`ICONO_TIPO`); lo anotado con tipos que ya no están (TPI, Entrega, Otro) va como TP (`tipoFecha`). En «¿Cuándo?» se elige «Este día» o «Tentativa · varios días» con un «Hasta el…» (de entrada, el viernes de esa semana): se guarda en el primer día con `hasta` y pinta todos los días hábiles del rango más suave y con borde punteado (`fechasDelDia`); en un día partido, solo su parte va más suave. Se borra desde cualquier día del rango. Abajo de los meses va la leyenda y después las próximas fechas, cada una con su ícono; las tentativas muestran el rango (19–23 oct) y siguen ahí hasta su último día («puede ser hoy»).
- **Dónde se guarda**: en el navegador (`isi-cronograma` y `isi-fechas`) y, con la clave de GitHub, en `aprobadas.json` (`"cronogramas": { "2026-2": { "materias": { "201": { "c": "3K4", "b": [[1, "19:55", "23:05"]] } } } }` y `"fechas": { "2026-10-28": [{ "k": "201", "tipo": "Parcial", "nombre": "1º Parcial" }], "2026-11-30": [{ "k": "206", "tipo": "Parcial", "nombre": "Recuperatorio", "hasta": "2026-12-04" }] }`). Al guardar el cronograma del cuatrimestre actual con la clave, sus materias pasan a "Cursando".
- **Notas de la cursada**: abajo de la grilla, un cuadro con las materias del cronograma (salen solas) y una columna por instancia: 1º, 2º y 3º Parcial, TP / TPI, Recuperatorio y Otra. Si la materia tiene `parciales` cargados, solo se habilitan los que tiene (`p1`, `p2`, `p3`, y `tp…` para TP / TPI); el resto queda con "—". La última columna, **Promo**, es la nota para promocionar: sale de `condiciones.directa` y se puede cambiar a mano (borrándola vuelve a la de la materia). Cada nota (1 a 10, con coma) se pinta verde si llega a la de promo y rojo suave si no. En el celular, la abreviatura queda fija a la izquierda y Promo a la derecha. Se guarda en `isi-notas-cursada` y en `aprobadas.json` como `"notasCursada": { "2026-2": { "201": { "p1": 7, "tp": 8, "promo": 6 } } }` (`aprobadas.json` es público, como las notas finales).

**Horarios nuevos**: cuando salgan los del próximo ciclo, se corre, desde la raíz:
`python3 herramientas/horarios/extraer.py horarios_1er.pdf horarios_2do.pdf horarios_3ro.pdf horarios_4.pdf horarios_5.pdf`
Reconoce las abreviaturas de los PDF con la tabla `NUM` (abreviatura → número de materia) y avisa lo que no reconoce. Las electivas que no están en el plan de la web van en `EXTRAS` (y en `EXTRAS_NOM` del `index.html`).

## Plan de la carrera: resumen del avance
`#/plan` (`viewResumen`) no lista las materias: muestra el avance de la carrera (anillo con el %, materias, horas, créditos de electivas y promedio), **Tu camino** y una tarjeta por año con sus materias como pastillas (verde aprobada, violeta regular, azul cursando) y el promedio del año. Tocar la tarjeta lleva al año; tocar una pastilla, a la materia. Abajo van las notas del plan. Arriba, unas pestañas (`pestanasPlan`) pasan del avance a cada año.
**Tu camino** (`viewCamino`): Ingreso, 1º, 2º, 3º, ★ Analista, 4º, 5º y la ★ grande de Ingeniero/a. Cada año se completa con sus obligatorias aprobadas; "Estás acá" marca el primero que falta. La estrella de Analista se llena con 1º a 3º completos (con el Seminario Integrador) y 4 créditos de electivas de cualquier nivel (`CREDITOS_ANALISTA`); la de Ingeniero/a, con todas las obligatorias y las electivas que faltan.
En la tarjeta de horas se marca la meta de `CARRERA.metaHoras`: cuando faltan 32 hs para el total (160 − 32 = 128 hs) se puede pedir equivalencias. Se ve una rayita en la barra y un aviso con cuántas horas faltan para llegar, o en verde cuando ya se llegó. Para cambiar el número o el texto, se edita esa línea.

## Cada año
`#/nivel/N` (`viewNivel`) muestra solo las materias de ese año: las obligatorias y debajo las electivas, con los créditos mínimos que pide (`CREDITOS_NIVEL`). Cada materia es una fila redondeada, separada de las demás; las que tienen material cargado llevan la etiqueta "Material". Arriba están las mismas pestañas del plan y al final, botones para ir al año anterior o al siguiente. Al volver de una materia, la lista queda donde estaba.
Cada materia tiene su estado: **Cursando**, **Regular** o **Aprobada** (tocar el que ya está lo saca) y, si está aprobada, la **nota** con la que se aprobó (1 a 10). Con las notas se calcula el promedio del año (en su cabecera) y el de la carrera (en el plan). La cabecera del año muestra cuántas hay en cada estado con una barra de colores. Hasta 1180 px de ancho la fila se muestra como tarjeta para que entre el estado.
Los estados y las notas se guardan junto con las aprobadas en `aprobadas.json` (`{ "aprobadas": [...], "estados": { "m29": "cursando" }, "notas": { "m1": 8 } }`), con la misma clave de GitHub, y en este navegador (`isi-estados`).
Cada materia lleva su abreviatura en una pastilla con su color (el de los horarios bajado de tono, `colorMat`); las correlativas van en pastillas grises, en verde las ya aprobadas y en violeta las regulares. El gris es `--beige` y `--beige-t` (con su versión para el modo oscuro).

## Modo simulacro
Un grupo de material (o una de sus `partes`) puede tener `simulacro: { id, titulo, minutos, preenunciado: { pdf, zip }, enunciado: { pdf, zip }, solucion: { zip }, control }` (ver los Simulacros del 1º Parcial de Backend, `201`). Arriba del grupo aparece un panel: 1) el preenunciado para el día antes, 2) el parcial con reloj (se puede cambiar de a 5 min) y 3) la solución. Al tocar **Empezar** corre el reloj y se habilitan el enunciado (PDF en el visor) y el ZIP con el CSV y los tests; hay pausa y "Terminé". Cuando se acaba el tiempo suena un aviso y se habilita la solución. El estado queda en el navegador (`isi-simulacros`): se puede recargar, ir a otra página o al IDE y el reloj sigue. La pestaña muestra el tiempo que queda; afuera del panel aparece un reloj flotante y en el visor, un reloj en la barra.
Por ahora está en el Simulacro 4 de Backend (`material/backend-de-aplicaciones/p1/parcial/simulacros/simulacro-4/`: preenunciado, enunciado y solución separados).

## Parciales y simulacros en filas
Un grupo con `filas: true` y `partes` muestra cada parte en una sola fila: "Parcial 3K1 · 2026 — Cloud Center", con el detalle abajo y cuántos archivos tiene. Al tocarla se despliega con sus archivos (y el panel del modo simulacro, si la parte tiene `simulacro`; si hay uno en curso, la fila ya aparece abierta). Cada parte: `{ titulo, tema, detalle, archivos, simulacro? }` (ver Parciales / Simulacros del 1º Parcial de Backend, `201`).

En Backend, los ZIP de la cátedra que venían con errores están corregidos: tests nuevos que no compilaban o contradecían la consigna, carpetas y nombres de CSV distintos de los de la consigna y cuentas mal en los ejemplos (3K1, 3K8 / Simulacro 1 y Simulacro 2). Cada uno lleva un `CORRECCIONES.md` en la carpeta del enunciado con lo que se cambió, y el detalle de la fila lo dice. Para revisar uno: copiar los tests nuevos al proyecto inicial (tienen que compilar, salvo que usen clases que pide el parcial) y al proyecto resuelto (tienen que pasar todos con `mvn -o test`). Las soluciones propuestas (hechas por nosotros) llevan un `DECISIONES.md`.

## Práctica por partes
Un parcial puede tener `practica: [{ id, titulo, origen, detalle, pasos, url }]` (ver DAO, `206`, 1º Parcial). En la página del parcial aparece primero la tarjeta "Práctica por partes" (`#/m206/p1/practica`), con la lista de ejercicios y cuánto lleva hecho cada uno.

Cada ejercicio (`#/m206/p1/practica/<id>`) se resuelve de a pasos (las clases, la herencia, la lógica, leer el CSV, el main…):
- **Izquierda:** lo que pide el paso y el enunciado completo, con resaltado lo que corresponde a ese paso.
- **Derecha:** un editor de Python con una pestaña por archivo. Las pestañas de los CSV son de solo lectura.
- **Abajo del editor:** "Pista", "Ver solución", "▶ Ejecutar" (corre el main del paso, si tiene), "Corregir" y "Corregir y seguir →". Este último corrige y, si todo está bien, pasa al paso siguiente.

En el celular se elige "Enunciado" o "Código" arriba, y debajo del editor hay una fila de teclas (tab, `:`, `()`, `self.`…). Lo escrito y los pasos hechos quedan en el navegador (`isi-practica:<id>`).

La corrección es Python de verdad, en el navegador:
- **Cómo corre:** se usa Pyodide 0.26.4, bajado de jsDelivr la primera vez (unos segundos), dentro de un Web Worker. El worker carga `practica/corrector.py`, escribe los archivos del alumno y los CSV, y corre los controles del paso.
- **Cuánto puede tardar:** si el código no termina en 10 s (por ejemplo, un `while` infinito), se corta y se avisa.
- **Mensajes:** los errores (de sintaxis, falta de constructor, atributo con otro nombre, `super().__init__` faltante…) se explican en castellano, con un botón que lleva a la línea.

Cada JSON tiene:
- `enunciado`: bloques `{ k: "h"|"p"|"li"|"code", t, p: [pasos donde se resalta] }`.
- `datos`: `{ "archivo.csv": contenido }`.
- `pasos`: en cada uno, `titulo`, `archivo`, `tambien`, `hacer`, `contrato`, `checks: [{ d, c }]` (código Python con `igual`, `cerca`, `lanza`, `es_abstracta`, `hereda`, `atributo`, `correr_main`…), `solucion`, `inicio`, `pistas` y `ejecutar`.

Los JSON no se escriben a mano: se editan `herramientas/practica/ej1.py … ej5.py` (los CSV están en `herramientas/practica/datos/`) y después se corre, desde la raíz:
`python3 herramientas/practica/validar.py ej1 ej2 ej3 ej4 ej5` y `python3 herramientas/practica/armar.py`.
`validar.py` usa el mismo `practica/corrector.py` que la página y revisa dos cosas: que la solución de cada paso pase todos los controles, y que el código de inicio falle al menos uno.

### Ejercicios de a pasos en Java (Backend)
En Backend la pestaña Práctica es la **Práctica por partes** (ver "El parcial por partes", más abajo). Los ejercicios de a pasos con Java que corre en el navegador siguen en su dirección (`#/m201/p1/practica/bk-servidor`) y las explicaciones de cada parte los enlazan ("Con Java de verdad"). Sin `practicaPartes`, con `practicaGrupos`, `practicaTemas` y `practicaLenguaje: "java"` la Práctica se ordenaba por temas:
- `practicaGrupos: [{ id, titulo, detalle, material? }]`: Básico (lo que trae el preenunciado) y Para el parcial (los cambios del día del parcial). Con `material` (archivos, como en cualquier sección) el grupo muestra esos archivos arriba de sus temas: en Básico va la guía rápida, el resumen de lo básico.
- `practicaTemas: [{ id, grupo, titulo, detalle, herramientas, parte? }]`: cada tema muestra sus explicaciones ("Entendelo", las `herramientas`) y sus ejercicios ("Practicalo": los de `practica` con ese `tema`). Con `parte: [id, título]`, la página de su explicación visual (`#/m201/p1/h/csv`) enlaza esa parte de la Práctica por partes.
- En cada ejercicio de `practica` van además `grupo` y `tema`.
- `quizEn: "parcial"`: arriba de esa sección (Parciales / Simulacros) aparece "Herramientas para practicar", en este orden: las herramientas de `herramientasParcial` (en Backend, el paso a paso del parcial), El parcial por partes (si está `practicaParcial`) y el quiz. Una herramienta que está en `herramientasParcial` abre con la pestaña Parciales marcada y vuelve ahí; las demás van adentro de su tema en la Práctica.

Las pestañas del parcial quedan: Temas · Teórico · Práctica · Videos · Parciales / Simulacros. Parciales / Simulacros tiene, en orden: las tres herramientas para practicar (Paso a paso del parcial, El parcial por partes y Quiz), "Para estudiar" (la guía única, con el multiple choice) y una fila por parcial o simulacro. La página de cada explicación trae abajo los ejercicios de su tema. `practicaGrupos` sigue sirviendo para la descarga de la materia (la guía rápida va en la carpeta Práctica).

Los ejercicios de Java tienen el mismo formato que los de Python, con `lenguaje: "java"` e `importar` (los paquetes que usan los controles). Cada control (`c`) es un bloque de Java que usa `practica/java/Prueba.java`: `Prueba.igual`, `verdad`, `lanza`, `noLanza`, `contiene`, `salida(() -> …)` (lo que imprime) y `archivo(ruta, texto)` (un CSV de prueba). Se editan `herramientas/practica-java/ej1.py … ej5.py` (los CSV y los proyectos originales están en `datos/` y `proyectos/`) y se corre, desde la raíz:
`python3 herramientas/practica-java/validar.py ej1 ej2 ej3 ej4 ej5` (con el JDK 21: compila y corre los controles igual que la página) y `python3 herramientas/practica-java/armar.py`.

### Java en el navegador
`practica/java/trabajador.js` es un Web Worker que compila con javac y arma el programa con TeaVM 0.13.1 (WebAssembly GC), y lo corre con WASI (`practica/java/wasi/`). Necesita Chrome o Edge 119+, Firefox 120+ o Safari 18.2+.
- **La primera vez** baja 4,8 MB (`compilador.wasm.gz`, `compilar.bin.gz`, `armar.bin.gz`) y los guarda en la caché del navegador (`isi-java`). Si se cambian, hay que subir `VERSION` en `trabajador.js`.
- **Corregir:** compila primero el código del alumno (los errores de javac se muestran en castellano, con el original abajo y un botón a la línea). Después compila los controles en `Controles.java`: el control que no compila (falta un método, una clase…) cuenta como mal y se saca, y el resto se corre.
- **Ejecutar:** corre el `main` del paso con los CSV en un sistema de archivos en memoria. Una excepción sin atrapar se muestra como en el JDK (`Exception in thread "main" …`).
- **Cuánto puede tardar:** si el programa corre más de 8 s, se corta el worker y se avisa (casi siempre es un ciclo infinito). La próxima vez se arma de nuevo desde la caché.
- **Diferencias con el JDK:** la división entera por cero corta el programa en vez de tirar `ArithmeticException` (se avisa en castellano), y algunas excepciones (índices, casteos, null) no traen mensaje.

`herramientas/java-navegador/armar.sh` rehace los tres archivos desde el paquete de npm `@wasm-oj/toolchain-java` 0.2.0 (necesita el JDK 21 y ASM 9). `ParcheClasslib.java` corrige la biblioteca de TeaVM: nombres internos de métodos, `Long.sum`, `String.format` y `Scanner` livianos, `getSimpleName`, rutas relativas, `Files.createDirectories`, `System.exit` y los mensajes de `parseInt`, `parseDouble` y `Enum.valueOf` iguales a los del JDK. Las licencias están en `practica/java/LICENCIAS.md`.

## El parcial por partes
Con `practicaParcial: "practica/bk-parcial/ejercicios.json"` en el parcial (ver Backend, `201`) aparece la tarjeta "El parcial por partes" en Herramientas para practicar (`#/m201/p1/pp`, o `#/m201/p1/pp/1.2` para un ejercicio). Son las 6 partes de siempre del parcial, en pestañas: 0 Consigna (dónde va cada cambio), 1 CSV (los dos formatos), 2 Dominio, 3 Polimorfismo, 4 Colector y 5 Main. Arriba de cada parte va su explicación corta y sus ejemplos, de los seis parciales cargados (Fintech, Taller de reparaciones, Juegos de mesa, Tarjetas de crédito, Cloud Center y Central de envíos): 39 en total, para cubrir las variantes de cada uno.
- **Izquierda:** el ejercicio, la línea **Dónde** (en qué clase o método se trabaja) y las pestañas Consigna, CSV (en una tabla, con la columna nueva resaltada y las filas de otro ancho marcadas), Pasos y Pistas (de a una). En la parte 0, además, lo que pide el enunciado de ese parcial (`enunciado`) y "Cómo decidir dónde va" (`guia` de la parte).
- **Derecha, según el tipo:** `codigo`: el editor de Java, con **una pestaña por archivo** (`archivos`). Cuando un punto toca dos clases (el parser y el dominio, la clase y su subclase nueva, el dominio y el colector) hay dos pestañas, como en el proyecto; las de solo lectura (`soloLectura: true`) son para mirar qué métodos hay. Botones: "Verificar" (o Ctrl + Enter; apretándolo otra vez se oculta el resultado y el editor vuelve a su tamaño, y si cambiaste el código verifica de nuevo), "Pista", "Ver solución" (pide confirmar; arriba aparece "Mi código | Solución" para cada pestaña, con lo nuevo marcado en color), "Reiniciar código" y "Otro ejemplo →" (el siguiente de la misma parte, en ciclo). `ubicacion` y `clasificacion`: una opción por fila y "Corregir", que muestra el motivo de cada una (la clasificación muestra la `cabecera` del CSV). `texto`: un área para escribir, la autoevaluación y las verificaciones.
- **Verificar:** no se corre Java. Se buscan con expresiones regulares (los `checks` del ejercicio: `contiene`, `noContiene`, `cuenta` con `veces` y `lineas` con `min` y `max`) en el código sin comentarios, así un comentario no hace pasar nada. Cada check mira su `archivo` o, si no dice, todos los que se editan. Es orientativa, y se avisa.
- **Progreso:** el código (por archivo), las respuestas, los ejercicios resueltos y las explicaciones leídas quedan en el navegador, en una clave por archivo de ejercicios (`isi-pp:<archivo>`): lo resuelto en El parcial por partes aparece resuelto en la Práctica y al revés. Un ejercicio queda resuelto cuando pasa todo, o a mano después de ver la solución.
- En el celular los paneles van uno abajo del otro y el editor ocupa todo el ancho.

### La Práctica por partes (Backend)
Con `practicaPartes: { fuentes: [archivos], resumen: { nombre, url, paginas } }` en el parcial, la pestaña Práctica (`#/m201/p1/practica`) es el mismo formato con tres agregados:
- **Varios archivos seguidos:** las partes de `practica/bk-practica/ejercicios.json` ("Lo que trae el preenunciado": 1 Clase, 2 Validaciones, 3 desdeCampos, 4 Parser, 5 Streams, 6 Agrupar, 7 Main; 42 ejercicios de los seis preenunciados) y después las de `practica/bk-parcial/ejercicios.json` ("Lo que agrega el parcial", los mismos ejercicios de El parcial por partes). Se numeran de corrido (1 a 13) y el nombre de cada grupo (`grupo` del JSON) va en la fila de partes antes de su primera parte. 81 ejercicios en total.
- **La explicación antes de practicar:** cada parte tiene `leccion`: qué es (`que`), de qué consta (`consta: [[título, detalle]]`), un código de ejemplo de un preenunciado o un parcial resuelto con cada elemento marcado en su color (`ejemplo: { archivo, origen, codigo, marcas: [[elemento, desde, hasta]], texto? }`; al pasar el mouse o tocar un elemento se resaltan sus líneas, y al pasar por una línea se marca su elemento), "Ojo con" (`ojo`), "En el parcial" (`parcial`) y enlaces: la página del resumen (`pdf`), la explicación visual (`herramienta`) y los ejercicios de a pasos con Java (`java`). Al entrar a una parte se ve su explicación; "Empezar a practicar" la deja leída y la próxima vez la parte abre en el primer ejercicio sin resolver. El botón **Explicación**, antes de los ejercicios de la parte, vuelve a ella. La dirección es `#/m201/p1/practica/<id de la parte>` para la explicación y `#/m201/p1/practica/<id del ejercicio>` para un ejercicio; la Práctica se acuerda de dónde quedaste (`isi-pp:practica:201/p1`).
- **El resumen en PDF:** arriba, al lado del avance, "Resumen en PDF" abre la guía rápida en el visor de la página; en cada explicación, "En el resumen · pág. N" la abre en esa página (`data-pag` en el enlace).

En El parcial por partes (`#/m201/p1/pp`) las explicaciones no se muestran.

El JSON: `grupo`, `partes: [{ n, id, titulo, pestana, explicacion, guia?, leccion?, ejercicios }]`, y cada ejercicio con `id, parte, tema, titulo, tipo, donde, consigna, enunciado?, csv, csvNota, tabla, datos, pasos, pistas, archivos: [{ nombre, inicial, solucion, soloLectura? }], checks: [{ tipo, regex, flags?, veces?, archivo?, ok, error }], items, opciones, cabecera?, resumen, extra`. Los que salen del código real de un parcial llevan `proyecto` (`cc`, `env`, `fin`, `tal`, `jue` o `tar`); los que se compilan solos, `compilar: "solo"`.

Después de cambiar algo, desde la raíz: `python3 herramientas/parcial-por-partes/validar.py` (necesita el JDK 21). Revisa los dos archivos: que la solución de cada ejercicio pase todos sus checks y el código inicial no; que los de `proyecto` compilen sobre el proyecto real (sacado del ZIP del preenunciado) y pasen su prueba (`herramientas/parcial-por-partes/pruebas/<id>/Prueba.java`, con los archivos de otras partes que da por hechos en `base/`), y los de `compilar: "solo"` también, si tienen prueba; que las respuestas de las clasificaciones sean las que da la solución con esas filas (o con esos `new`, en las de "¿Se crea o tira excepción?", que llevan `pregunta`); que no se repitan los id de partes ni de ejercicios; y que el código de cada explicación marque líneas que existen y todos los elementos de "consta de".

### La Práctica de TPA (Octave en el navegador)
Los parciales de TPA (`29`) tienen tres secciones: **Teórico** (solo las clases, los apuntes y los videos), **Práctica** y **Parciales** (el resumen, el banco de preguntas, el **Simulacro del parcial**, el quiz y lo que hace falta para rendir: las funciones del profe en Octave). La Práctica es el mismo formato que la de Backend (`practicaPartes`, con `practicaLenguaje: "octave"` en robótica y `"cpp"` en IoT), con la consigna a la izquierda y, a la derecha, el código y las respuestas:
- **`octave`:** el editor (con colores y sangría de Octave) y **▶ Ejecutar** (Ctrl + Enter), que corre el código en el navegador y muestra la salida como Octave (`format short`, los errores con su línea) y los gráficos (`plot`, `plot3`, `DibujarEjes`, `dibujarSistemasDeEjesCoordenadosDeRobot`, `Dibujar_Temporal`…) en SVG, en 3D con la vista de Octave. **Verificar** corre el código y compara las variables (`vars: [{ nombre, valor, tol, error? }]`, con tolerancia relativa; un vector vale en fila o en columna), los `checks` (en el código sin comentarios) y las respuestas.
- **Respuestas:** cualquier ejercicio puede llevar `respuestas: [{ pregunta, valor, tol, mostrar, motivo?, unidad?, opciones? }]`: un número (acepta coma o punto; `tol` absoluta, o relativa con `relativa: true`) o, con `opciones`, un desplegable. Se escriben abajo del editor, como en el campus. "Ver solución" muestra también las respuestas con su porqué.
- **`respuestas`:** un ejercicio solo de respuestas, con un código para mirar al costado (`codigo: { nombre, texto }`), como leer una matriz que te dan.
- **`codigo` en C++ (IoT):** el editor con colores de C++/Arduino; no se corre en la placa: se verifica con los `checks` (expresiones regulares en el código sin comentarios), como en Backend, y las respuestas si tiene. El aviso dice que lo prueben en Wokwi o en la ESP32.
- **Figuras:** `imagen: { url, alt, pie? }` va abajo de la consigna (fondo blanco también en modo oscuro; se abre grande).
- **La carpeta del profe:** con `carpetaProfe: "practica/octave/profe/pN/"` en el parcial, el editor muestra `mi_codigo.m` y, al lado, una pestaña de solo lectura por cada `.m` del ZIP del profe (copiados tal cual, en UTF-8; `archivos.json` dice cuáles hay). Al correr, esos `.m` se cargan como en la carpeta de Octave: lo que se ejecuta es el código del profe. Los que usan celdas o handles de gráficos (`dibujarSistemasDeEjesCoordenadosDeRobot`, `animar_trayectoria`) llevan `ejecuta: false` y una nota: se ven, pero se usa la versión propia del intérprete. Un ejercicio que pide escribir una función la oculta con `ocultar: ["Rotz"]` (y su pestaña no aparece). Si el error pasa adentro de un `.m` del profe, se dice en cuál y en qué línea.

**El Octave del navegador** (`practica/octave/octave.js`, se carga la primera vez que se ejecuta): un intérprete chico en JavaScript (matrices de hasta 3 dimensiones, lógicos, texto, structs, funciones en el mismo archivo, `if/for/while/switch/try`, `printf`/`disp`/`num2str`/`mat2str`, álgebra lineal y versiones propias de las funciones del profe). Con la opción `archivos` carga `.m` de funciones como si estuvieran en la carpeta (cada uno se lee aparte; la primera función se llama como el archivo). No tiene números complejos, celdas ni toolboxes. `node herramientas/tpa-practica/probar_octave.js` corre los casos de `casos-octave.json` en `octave-cli` y en el navegador dos veces (con sus funciones y con los `.m` del profe cargados): las tres salidas tienen que dar igual.

**El simulacro del parcial** (tarjeta «Simulacro del parcial» arriba de Parciales, `#/m29/p1/pp`): con `practicaParcial: "practica/tpa-pN/simulacro.json"` y `practicaParcialTarjeta: { titulo, detalle }`, es el formato de «El parcial por partes» con los ejercicios del parcial como en el campus (en el 1º: tres giros, giros y traslaciones, la posición del efector con DH de los robots 2023–2026, la tabla DH y el avión; en el 2º: la CI geométrica del RRR, las tablas del parcial 2026 —cilíndrico, RPP, RPR e IRB2400—, DLS con resultados a completar y trayectorias). Cada problema trae `azar: { params, previo? }` y **los números cambian** («Otros números», o «Otro problema» cuando sale bien; se cuenta cuántos salieron bien): `params` dice cómo sortear cada dato (`{ de, a, paso?, no? }`, `{ elegir: [...] }` o `{ perm: [...] }`), `previo` es Octave que calcula otros datos (por ejemplo, el punto que sale de la directa con articulaciones al azar) y en la consigna, la tabla, el código y las preguntas `{x}` se cambia por su valor (`{x|2}`: con 2 decimales; `{E|min}`, `{E|uvw}`, `{q|pi}`). Las respuestas correctas se calculan en el navegador corriendo la solución con el Octave del navegador y la carpeta del profe; si una semilla da un caso raro (una inversa que no converge o cae en la rama imposible), se prueba otra. Cada respuesta acepta el redondeo de sus decimales y además 1e-4 relativo (lo que muestra Octave son 5 cifras); se puede escribir con coma, punto o el signo «−». Se arma con `python3 herramientas/tpa-practica/armar_simulacro.py`; `validar.js` arma cada problema con 12 semillas (`SEMILLAS=n` para otra cantidad) y compara cada respuesta con `octave-cli`.

**Los ejercicios** se arman con `python3 herramientas/tpa-practica/armar_p1.py` y `armar_p2.py` (lo común está en `comun.py`): cada valor esperado sale de correr la solución en `octave-cli` con las funciones del profe (los gráficos ahí no hacen nada: solo importan los números). Cada respuesta numérica lleva `dec` (con cuántos decimales se muestra; la tolerancia es 10^-dec). Después, `node herramientas/tpa-practica/validar.js` corre cada ejercicio con el Octave del navegador y las mismas comparaciones de la página: la solución tiene que pasar todo, el código inicial no, cada respuesta que se muestra tiene que dar bien y cada figura tiene que existir.
- 1º parcial (`practica/tpa-p1/`, 28 ejercicios): 1 Robots (partes, tipos, grados de libertad, verdadero o falso), 2 Rotaciones, 3 Homogéneas, 4 Composición (respecto del fijo o del móvil), 5 Cambio de sistema (el avión, sistemas encadenados, la inversa) y 6 Denavit–Hartenberg (los robots de los parciales 2023–2026).
- 2º parcial (`practica/tpa-p2/`, 30 ejercicios): 1 Directa e inversa, 2 CI geométrica del RRR (las dos soluciones y la verificación), 3 Jacobiano, 4 CI numérica con DLS (la primera vuelta a mano, la carga de offsets, la trampa de la semilla, el RPP y el IRB2400), 5 La tabla del parcial 2026 (cilíndrico, RPP, RPR y corregir una fila) y 6 Trayectorias (con `Dibujar_Temporal`, la recta y el círculo del parcial 2026).
- 3º parcial (`practica/tpa-p3/`, 29 ejercicios, `armar_p3.py`): 1 La ESP32, 2 Entradas y salidas (con el pulsador y el DHT22 de la placa de la cátedra), 3 ADC, map y PWM (las cuentas), 4 Programación (setup, loop, millis, el monitor serie), 5 Protocolos (UART, I2C, SPI y el display) y 6 Redes y nube (WiFi, ThingSpeak, MQTT y las preguntas del banco). Las opciones de las preguntas de 2025 van como «¿La marcarías?» (Correcta / Incorrecta), con la clave del campus.
- TP (`practica/tpa-tp/`, 22 ejercicios, `armar_tp.py`): 1 LEDs y relé, 2 Pulsador y pote, 3 PWM (con los 12 bits del TPI), 4 Display, 5 DHT22 y touch, 6 millis(), 7 WiFi y ThingSpeak (los 6 campos cada 16 s del sketch 1 del TPI y la lectura del sketch 2) y 8 MQTT y EEPROM. Cada uno parte de un caso resuelto del profe, que va en una pestaña al lado.
- `node herramientas/tpa-practica/validar.js` revisa todos los `practica/tpa-*/ejercicios.json` (en los de C++, que la solución pase los checks y el código inicial no; en los `esp32`, que la solución pase las pruebas en la placa simulada y el inicial no, y que lo que se lee en la placa dé cada respuesta con `medir`).

### El TP de TPA: la ESP32 simulada
El TP (`#/m29/tp`, una parte de una sola página) tiene **Práctica** (`practicaPartes`: en una parte de una sola página, la pestaña aparece aunque no tenga herramientas). Sus ejercicios son de tipo **`esp32`**: el sketch de C++ corre de verdad en la placa de la cátedra simulada en el navegador.
- **▶ Ejecutar** (Ctrl + Enter) prende la placa en la pestaña **Placa** de la izquierda (con la placa a la vista, las dos columnas van mitad y mitad): el LED azul (GPIO 2), el verde (23) y el relé (14) con su brillo o el valor de PWM; el pulsador (19), los dos touch (13 y 4) para mantener apretados; el pote (32) y el DHT22 (33) con deslizador y número; el display OLED SH1106 dibujado (texto, rectángulos, líneas, círculos); el monitor serie con su línea para mandar (con salto de línea al final, como el monitor del IDE); y, si el sketch usa WiFi, ThingSpeak o MQTT, la nube: el WiFi, los envíos a ThingSpeak con su código (−401 si van con menos de 15 s) y lo que pasa por MQTT, con un formulario para publicar como otro cliente. El tiempo de la placa va con el reloj; ⏸ Pausa y ↺ Reiniciar (con el código de la pestaña abierta). Con la pestaña de un caso del profe abierta, ▶ Ejecutar corre ese.
- **Verificar** corre las `pruebas` del ejercicio sin pantalla y más rápido que el reloj: `[{ nombre, hasta, entradas: [{ t, boton | pote | dht | touch | serial | mqtt }], opts: { pote, temp, hum, canales, eeprom }, esperar: [...] }]`. Lo que se espera (`esperar`) son controles `{ k, ..., ok?, error? }`: `pin` (prendido o apagado en t), `brillo` y `pwm` (en t), `cambios`, `periodo`, `recorre` (el PWM pasa de un valor a otro de a poco), `serial` (expresión regular, con `desde`/`hasta`, `no` o `veces`), `display` (lo que se ve en t o en algún momento), `ts` (cuántos envíos, cada cuánto, los campos y los rechazos), `mqtt` (conexión, suscripción, publicación) y `eeprom`. Además los `checks` y las respuestas, como siempre. Abajo se ve qué pasó en cada prueba (el monitor serie, los cambios de los LEDs, el display, ThingSpeak).
- **Los casos del profe:** `carpetaProfe: "practica/esp32/profe/"` y, en cada ejercicio, `delProfe: [...]` con los que van al lado (de solo lectura). `armar_tp.py` los copia del ZIP de casos resueltos (con las claves tapadas); los que necesitan un `.h` lo dicen en `archivos.json` (`h: [...]`).
- **El simulador** (`practica/esp32/esp32.js`, se carga la primera vez; también anda en node): preprocesador (`#define` con parámetros, `#include "x.h"`), tipos de C++ (división entera, `String`, `char`, `unsigned long`, arreglos, lambdas), funciones de Arduino (`pinMode`, `digitalWrite/Read`, `analogRead/Write` con su resolución, `ledc*`, `map`, `millis`, `delay`, `attachInterrupt`, `touchRead`, `touchAttachInterrupt`) y las librerías de la cátedra: Serial, WiFi, ThingSpeak, DHT, Adafruit_SH110X/SSD1306, PubSubClient, EEPROM, Ticker y ESP32Servo; el servidor web, Telegram, OTA y Arduino Cloud no hacen nada (avisan). `ESP32.crear(codigo, opts)` arma la placa y `avanzar(hasta)` la corre; `ESP32.pruebas(codigo, pruebas)` corre y controla. De los 53 sketches del ZIP del profe corren 43: no corren los que tienen un error propio (el `ssid` comentado de los casos 11 y 20), las propiedades de Arduino Cloud, ArduinoJson, las páginas OTA con `R"(...)"`, el `SECRET_SSID` sin `secrets.h` y el punto de acceso, que da vueltas sin esperar (en las pruebas se corta; en la placa de la página corre, lento).

## Cuestionarios de Backend
Los PDF de `material/backend-de-aplicaciones/cuestionarios/` no son las capturas del campus: se arman con `herramientas/cuestionarios-back/` y copian el estilo de la revisión del intento. Arriba de cada pregunta va la cabecera gris (número, estado y puntaje) y después el recuadro azul con las opciones: la tilde verde en lo bien marcado, la cruz roja en lo mal marcado y «faltaba» en lo que había que marcar. Abajo, el recuadro beige con la respuesta correcta, el «Por qué», la «Corrección» si estaba mal y un «Ojo» cuando la clave del campus es discutible. Cada cuestionario tiene primero el intento 2026 y después las preguntas de 2023 y 2025 que no se repiten, ubicadas por tema. Por ejemplo, el JDBC del 05 de 2023 va al 06 y el Spring Data del 07 de 2023 va al 08. Las preguntas repetidas y las que tenían la clave del campus equivocada o dudosa no se agregaron.

Los datos están en `herramientas/cuestionarios-back/preguntas.json`. Hay una entrada por cuestionario (`n`, `archivo`, `titulo`, `intento: {anio, nota}`) y cada pregunta lleva estos campos:
- `origen`: el año;
- `en`, `codigo`, `varias`, `vf` y `op`;
- `marcadas` y `ok` (índices de las opciones);
- `puntos: [obtenido, máximo]` y `estado`;
- `ex`, y opcionales `corr` y `ojo`.

Para sumar o corregir una, se edita el JSON y se corre, desde la raíz:
`python3 herramientas/cuestionarios-back/generar.py --fuente CARPETA` y después `python3 herramientas/miniaturas.py`. `CARPETA` tiene los `open-sans-latin-{400,600,700}-normal.woff2` del paquete de npm `@fontsource/open-sans`; sin `--fuente`, usa DejaVu Sans. El script necesita el Chromium de Playwright (o la variable `CHROMIUM`) y pymupdf, y deja los PDF sin metadatos. Con `--solo 01,05` arma solo esos.

## Modo oscuro y carga suave
El botón de la luna/sol de la barra lateral (en el celular, el de arriba) elige claro u oscuro y lo guarda (`isi-tema`); si nunca se tocó, sigue al sistema. Funciona prendiendo o apagando las reglas `@media (prefers-color-scheme: dark)` de la hoja de estilos (un script chico en el `<head>`, para que no parpadee al abrir), así que los colores oscuros se siguen escribiendo dentro de esos `@media`.
Al cambiar de página el contenido aparece con un fundido corto; mientras cargan, las tapas de los PDF, las miniaturas de los videos, el reproductor y las hojas del visor muestran su forma con un brillo que pasa. Con "reducir movimiento" del sistema no hay animaciones.

## Agregar un PDF
1. Subilo a la carpeta que corresponde (ej: `material/redes-de-datos/p2/teorico/apunte.pdf`).
2. En `index.html`, dentro de la materia en `MATERIAS`, agregá una línea en `material`:
   `{ nombre: "Apunte", tipo: "PDF", url: "material/redes-de-datos/p2/teorico/apunte.pdf" }`

## Secciones de cada parcial
Cada parcial tiene tres secciones: `teorico`, `practico` y `parciales` (parciales de años anteriores). Todas se muestran aunque estén vacías; para cargar algo, agregá la sección en el parcial con `{ material: [...], videos: [...] }`.

## Agregar un video
En `videos`, agregá:
`{ url: "https://www.youtube.com/watch?v=XXXXXXXXXXX" }`
Sin `titulo`, el nombre se trae de YouTube (el video tiene que estar publicado u oculto, no en borrador) y, si todos empiezan con "Clase N", se ordenan por número. Si ponés `titulo: "..."`, se usa ese.

Opcionales en cada video: `bloque: "..."` agrupa la lista con un título por bloque (ver Backend, 1º Parcial), `detalle: "..."` se muestra debajo del video, y si el link tiene `&t=440s` el video arranca en ese segundo.

El reproductor usa la API de YouTube (`youtube.com/iframe_api`): cuando termina un video arranca solo el siguiente de la lista, y la velocidad que se elige (por ejemplo 1.5) se mantiene en los videos siguientes y queda guardada en el navegador (`isi-yt-vel`). Tocar un video de la lista lo arranca. Si la API no carga, se ve el video común de YouTube, sin esas dos cosas.

En la compu, el botón "Modo cine" (o la tecla `t`) agranda el video a todo el ancho, sin pantalla completa, y pasa la lista abajo en una fila horizontal (con flechas y la rueda del mouse). Es solo CSS, así que el video no se corta; la elección queda guardada (`isi-yt-cine`). En el celular la lista ya va abajo y el botón no aparece.

Si una sección no tiene videos (`videos: []`), no aparece la pestaña Videos ni el botón "▶ Videos".

Los archivos con `tipo: "ZIP"` o `tipo: "INO"` se descargan (botón "Descargar ↓") en vez de abrirse en otra pestaña.

## Niveles del material (esencial, para profundizar, extra)
Cada grupo de material puede llevar `nivel: "esencial"`, `"profundizar"` o `"extra"` (también un archivo suelto, para que vaya a otro nivel que su grupo). Si una lista usa niveles, se ordena por nivel con su color y lo extra queda plegado ("Ver N más"). Lo que no tiene nivel cuenta como esencial. Si ninguna parte de la lista tiene nivel, se ve como siempre.
`{ nivel: "profundizar", grupo: "Material del profe", archivos: [...] }`

## Tapas de los PDF y visor
Cada PDF del repo muestra su primera página en la lista y se abre en el visor de la página, en la compu y en el celular. El visor dibuja el PDF con PDF.js (se carga de cdnjs la primera vez que se abre un PDF), así no depende del navegador: antes, Chrome de Android los descargaba y los navegadores de WhatsApp o Instagram los dejaban en blanco. Tiene las páginas al costado (en pantallas anchas), zoom, buscar una palabra, descargar, la cruz para cerrar arriba a la derecha, y pasar al archivo anterior o siguiente de la misma página. En la compu ancha (1280 px o más) se abre al costado, como un artefacto de Claude: la página se corre a la izquierda y se sigue usando (Esc o la cruz lo cierran). En pantallas más chicas y en el celular ocupa toda la pantalla y el botón "atrás" lo cierra. Si PDF.js no carga, ofrece abrir o descargar el PDF. Ctrl/Cmd + clic sigue abriendo el PDF en otra pestaña.
Cada hoja se dibuja en un lienzo del tamaño justo de la hoja en pantalla, al doble de los píxeles de la pantalla (hasta 3×, con un tope de 12 millones de píxeles por hoja). Así el navegador no lo estira, que es lo que lo hacía ver borroso con el zoom de Windows al 125%, y el texto chico queda nítido como en el visor del navegador.
Las tapas están en `miniaturas/` (misma ruta que en `material/`, en .jpg). Cuando subas PDFs nuevos, corré desde la raíz del repo:
`python3 herramientas/miniaturas.py` (necesita `pip install pymupdf`). Crea las que faltan y borra las que ya no tienen PDF. Si un PDF no tiene tapa, se ve el cartel "PDF" como antes.

## Quiz
Con `quiz: "quiz/archivo.json"` en el parcial aparece el Quiz en "Herramientas para practicar" (ruta `#/m201/p1/quiz`): arriba de la sección `quizEn` o, en una parte de una sola página, en la pestaña Práctica. El JSON tiene `titulo`, `descripcion` y `secciones: [ { titulo, preguntas: [...] } ]`. Cada pregunta: `tipo` (`una`, `varias`, `vf`, `num` o `modelo`), `en` (enunciado, acepta HTML), `op: [["texto", true/false], ...]` para las de opciones, `num` o `modelo` (la respuesta, para las que se resuelven y después se mira), y opcionales `ex` (por qué), `mal` (aviso, por ejemplo una clave del campus equivocada), `fuente`, `code`, `img` y `practica: true` (no salió en un parcial). Se elige la cantidad (5, 10, 15, 20, 25 o todas); entran todos los temas del parcial (están en su pestaña Temas). Las preguntas salen al azar y "Otras N" (la cantidad elegida) trae las que todavía no salieron. No se guarda nada de quien lo hace.

## Herramientas y explicaciones
Con `herramientas: ["csv", "streams"]` en el parcial cada una es una pestaña (ruta `#/m201/p1/h/csv`), o va adentro de su tema en la Práctica si el parcial tiene `practicaTemas`. Hay:
- `csv`: cómo se lee un CSV en Java. Las formas del apunte 11 (Scanner, BufferedReader, Files.lines, CSVReader, CSVReaderHeaderAware y CsvToBean) con un cuadro de qué hace cada una y, para cada forma, un paso a paso con dibujo y el código resaltado.
- `streams`: Streams y Collectors, con un stream recorrido paso a paso y cada operación sola (filter, map, sorted, limit, terminales y groupingBy).
- `pasos`: el paso a paso del parcial de Backend (antes era el PDF "Cómo resolver el parcial · paso a paso"). Arriba, lo que pide siempre la consigna, los 45 minutos y dónde se trabaja; después, ocho pasos (0 a 7) con dónde se trabaja, el código **antes y después** uno al lado del otro y la lista de cambios numerados: al pasar el mouse por un cambio (o tocarlo, y queda fijo) se marca qué se tocó en el antes y qué quedó en el después, y al pasar por una línea se marca su cambio. Cada paso trae las trampas, cómo verificar, qué hacer "si te piden" otra cosa (de los cinco parciales), lo que corre el profe para corregir y un link para practicarlo en El parcial por partes. El código se escribe con una marca por línea (`+`, `-` o espacio), `{n}` para el cambio y `[[n:texto]]` para el pedazo nuevo dentro de una línea (`codigoPasos`). Los pasos se marcan y quedan en el navegador (`isi-pasos-bk2`); "Antes de entregar" se pone en verde a medida que se marcan.
- `rotaciones` (rotaciones y traslaciones, TPA), `robot2r` (robot 2R directa e inversa, TPA) y `subredes` (subredes y VLSM, Redes).
Están en `HERRAMIENTAS`, en el código de la página.

## Temas del parcial (introducción)
Cada parcial puede tener un campo `temas` (ver el 2º Parcial de Redes de Datos):
`temas: { titulo: "...", unidades: [ { titulo: "Unidad ...", contenidos: ["...", "..."] } ] }`
Se muestra en la pestaña **Temas** (ruta `#/m201/p1/temas`) como una lista numerada: cada tema se despliega con lo que entra y su material, que sale solo: los archivos de las `partes` del material que se llaman igual que el tema (ej.: la parte "Streams" del Teórico) y los videos cuyo `bloque` empieza con el nombre del tema (ej.: "Streams · Apunte 10"). Tocando un video se abre la lista de videos arrancando por ese. Si el parcial no tiene `temas`, no aparece la pestaña.

## Bloques por evaluación
Los bloques de `parciales` son las evaluaciones de la materia, no las unidades de la cátedra. Por ejemplo, Desarrollo de Aplicaciones con Objetos (`206`) tiene dos:
- "1º Parcial", con Teórico, Práctico y "Parcial y simulacros".
- "TPI", con Teórico y Práctico.

Los temas de cada unidad van en el bloque de la evaluación donde se toman. Toda sección que se cargue lleva `material` y `videos`, aunque alguno quede vacío (`videos: []`).

## Secciones de un parcial a medida
Si un parcial no necesita las tres tarjetas, se puede limitar con `secciones`:
`secciones: ["teorico", "practico"]`

Además de `teorico`, `practico` y `parciales` hay dos secciones más: `parcial` (simulacros, parciales tomados y guía para prepararlo) y `tpi` (enunciado del TPI y sus guías). Su contenido va en el parcial con la misma clave, igual que las otras. Con `nombres` se le cambia el título a una sección de ese parcial (ver Backend, `201`: el 1º Parcial tiene Teórico y "1º Parcial", y el TPI tiene Teórico y "TPI"):
`secciones: ["teorico", "parcial"], nombres: { parcial: "1º Parcial" }`

## Comisiones
Cada profesor es una fila con `comision`, `profesor`, `rol` y `asistencia` (se ve como "Toma" o "No toma", centrado). El comentario (`comentario`), el examen (`examen`) y la recomendación (`recomendada: true/false` y `motivo`) son de la comisión: se ponen una sola vez, en el primer profesor de esa comisión. `horario` también va en el primero. La recomendación es una pastilla centrada (Sí / No) y el `motivo` va debajo del comentario. La recomendación también se ve en el Cronograma, al elegir comisión.

## Parcial o TPI en una sola página
Con `secciones: []` el parcial no tiene secciones de Teórico/Práctico: sus pestañas son Material y Videos, con su propio `material` y `videos` (ver los TPI de Green Software, `202`), más Quiz, herramientas y Temas si los tiene (ver Tecnologías para la Automatización, `29`).

## Condiciones de aprobación
Cada materia puede tener `condiciones` (ver Backend de Aplicaciones, `201`). Se muestra arriba a la derecha en la página de la materia:
`condiciones: { directa: 6, regular: 4, aclaracion: "...", requisitos: [ { titulo: "Parcial", corto: "Parcial ≥ 6", detalle: "6 o más" } ] }`
Se ve "Directa con 6" y la regularidad; tocándolo se despliegan la aclaración y cada requisito con su `corto` y su `detalle`. Si `regular` es `null`, aparece "Sin regularidad" (electivas, que solo se aprueban de forma directa). La asistencia no va acá: se indica en la columna de cada profesor en las comisiones.

## Descargar toda la materia (ZIP)
En la página de cada materia aparece el botón "Descargar todo (ZIP)" si tiene archivos propios (`material/...`). El ZIP se arma en el navegador, sin copias en el repo: una carpeta por parcial y sección (Teórico, Práctico…), y adentro una por grupo y parte, numeradas en el orden de la página. Los archivos se llaman como en la página ("01 - Nombre.pdf"). Los videos no van, y los links externos (Drive, webs) quedan en un `Enlaces.txt` dentro de su carpeta.

## Límites de GitHub
Hasta 100 MB por archivo. Conviene que el repositorio no pase de ~1 GB.
