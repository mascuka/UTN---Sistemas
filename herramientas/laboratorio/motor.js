/* Laboratorio del parcial · Flota Logística: el motor.
   - simular(texto, cfg): procesa el CSV con las mismas reglas que el Java generado (enteros de 32 bits, división entera,
     el índice con double y (int), los mensajes de error de cada validación) y devuelve cada fila, los totales y la
     salida del main.
   - generar(cfg, originales): el Java resuelto (ParserVehiculos, VehiculoRuta, las subclases, Flota y App).
   - leerEnunciado(texto, csv): saca las reglas nuevas del enunciado buscando las frases con las que escribe la cátedra.
   Sin internet y sin IA: todo son reglas fijas. Funciona en el navegador (window.Motor) y en Node (require). */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica();
  else raiz.Motor = fabrica();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ───────────────────────── El preenunciado (fijo) ─────────────────────────
  const CAMPOS = ['patente', 'zona', 'velocidadPromedio', 'cargaToneladas', 'estado'];
  const ENCABEZADO = CAMPOS.join(',');
  const ESTADOS_BASE = ['EN_RUTA', 'DEMORADO'];
  const DESCARTES_BASE = ['EN_DEPOSITO'];
  const FACTURACION = 2000;
  const CLASES = ['App', 'ErrorParseo', 'Flota', 'ParserVehiculos', 'ResultadoParseo', 'VehiculoRuta'];
  const RESERVADAS = new Set(('abstract assert boolean break byte case catch char class const continue default do double else enum extends final finally float for goto if implements import instanceof int interface long native new package private protected public return short static strictfp super switch synchronized this throw throws transient try void volatile while true false null var record yield sealed permits'
    + ' campos presente texto numero valor costo indiceCalculado args').split(' '));

  function configBase() {
    return {
      columna: null,          // { nombre, tipo: 'texto'|'entero', valores: [], rango: {min,minIncl,max,maxIncl}, vacio: 'invalida'|'defecto', defecto }
      separador: ',',         // el del formato nuevo
      estados: ESTADOS_BASE.slice(),
      descartes: DESCARTES_BASE.slice(),
      restricciones: [],      // [{ estado, valores: [] }]: en el formato nuevo, con ese estado la columna solo admite esos valores
      especiales: [],         // [{ cuando: {campo:'columna'|'estado', op:'igual'|'mayor'|'presente', valor}, ops: [], topes: [], clase, etiqueta }]
      baseDesdeColumna: false,// el costo usa la columna en lugar de los 2000 USD
      extras: [],             // operaciones sobre el costo de todos: [{op:'suma'|'porcentaje'|'multiplica'|'sumaPorCada', n, cada}]
      conteo: null,           // null | 'estado' | 'zona' | 'columna' | 'tipo'
      etiquetaBase: '',       // para el conteo por tipo: cómo se llama el vehículo común
      totales: [],            // [{ campo: 'estado'|'columna', valor }]: el main muestra el costo total de esos
      archivo: 'datos.csv',   // el CSV que usa el main por defecto
    };
  }

  // ───────────────────────── Enteros como en Java ─────────────────────────
  const i32 = x => x | 0;
  const mul = (a, b) => Math.imul(a, b);
  const div = (a, b) => i32(Math.trunc(a / b));          // a y b ya son int: la división entera de Java
  const add = (a, b) => i32(a + b);
  const INT_MIN = -2147483648, INT_MAX = 2147483647;
  function parseIntJava(s) {                               // Integer.parseInt
    if (!/^[+-]?\d+$/.test(s)) return null;
    const n = Number(s);
    return n < INT_MIN || n > INT_MAX ? null : n;
  }
  const trim = s => s.replace(/^[\u0000-\u0020]+|[\u0000-\u0020]+$/g, '');   // String.trim(): todo lo <= ' '
  const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
  const pascal = s => String(s).toLowerCase().split(/[^a-z0-9ñ]+/).filter(Boolean).map(cap).join('');
  const constante = s => s.replace(/([a-z0-9])([A-Z])/g, '$1_$2').toUpperCase();
  const comparar = (a, b) => (a < b ? -1 : a > b ? 1 : 0);  // String.compareTo (unidades UTF-16)
  const unicos = a => [...new Set(a.map(String))];

  // ───────────────────────── Mensajes (los mismos en el Java) ─────────────────────────
  const NOMBRE_CAMPO = { carga: 'La carga', velocidad: 'La velocidad', indice: 'El índice de desgaste', columna: 'El valor de la columna nueva' };
  const MSG = {
    ancho: (cfg, n) => cfg.columna ? `La fila debe tener exactamente ${n} columnas` : 'La fila debe tener exactamente cinco columnas',
    entero: campo => `El campo ${campo} debe ser un entero`,
    patente: 'La patente no puede estar vacía',
    zona: 'La zona no puede estar vacía',
    velocidad: 'La velocidad promedio debe ser mayor a 0 y menor a 130',
    carga: 'La carga no puede superar las 45 toneladas',
    estado: e => 'Estado de vehículo inválido: ' + e,
    indice: 'El índice de desgaste debe coincidir con el cálculo y estar entre 1 y 90',
    vacio: c => `El campo ${c} no puede estar vacío`,
    valor: (c, v) => `Valor de ${c} inválido: ${v}`,
    rango: (c, r) => `El campo ${c} debe ser ${textoRango(r)}`,
    restriccion: (e, c) => `Un vehículo ${e} no admite ese valor de ${c}`,
    tope: (clase, t) => `${NOMBRE_CAMPO[t.campo] || t.campo} no cumple el tope de ${clase}`,
  };
  function textoRango(r) {
    const p = [];
    if (r.min != null) p.push((r.minIncl ? 'mayor o igual a ' : 'mayor a ') + r.min);
    if (r.max != null) p.push((r.maxIncl ? 'menor o igual a ' : 'menor a ') + r.max);
    return p.join(' y ');
  }
  const enRango = (n, r) => !r || ((r.min == null || (r.minIncl ? n >= r.min : n > r.min)) && (r.max == null || (r.maxIncl ? n <= r.max : n < r.max)));
  const tieneRango = r => !!r && (r.min != null || r.max != null);

  // ───────────────────────── El CSV, fila por fila ─────────────────────────
  function lineas(texto) {                                 // BufferedReader.readLine
    const ls = texto.split(/\r\n|\r|\n/);
    if (ls.length && ls[ls.length - 1] === '') ls.pop();
    return ls;
  }
  const encabezadoNuevo = cfg => cfg.columna ? CAMPOS.concat(cfg.columna.nombre).join(cfg.separador) : null;

  function cumple(cuando, v) {
    if (cuando.op === 'presente') return v.presente;
    const x = cuando.campo === 'estado' ? v.estado : v.columna;
    if (cuando.op === 'mayor') return typeof x === 'number' && x > Number(cuando.valor);
    return String(x) === String(cuando.valor);
  }
  const valorCampo = (v, campo) => ({ carga: v.carga, velocidad: v.velocidad, indice: v.indice, columna: v.columna })[campo];
  const pasaTope = (n, t) => t.op === 'min' ? (t.incl ? n >= t.n : n > t.n) : (t.incl ? n <= t.n : n < t.n);
  const etiquetaBase = cfg => cfg.etiquetaBase || (cfg.columna && cfg.columna.tipo === 'texto' && cfg.columna.defecto) || 'NORMAL';

  function aplicar(costo, ops, v) {
    for (const o of ops) {
      if (o.op === 'suma') costo = add(costo, o.n);
      else if (o.op === 'porcentaje') costo = div(mul(costo, add(100, o.n)), 100);
      else if (o.op === 'multiplica') costo = mul(costo, o.n);
      else if (o.op === 'sumaPorCada') costo = add(costo, mul(o.n, div(v.columna, o.cada)));
    }
    return costo;
  }

  /* Una fila ya partida y con el ancho correcto → el vehículo o el motivo por el que es inválida */
  function desdeCampos(c, cfg) {
    const col = cfg.columna, n = c.length;
    const patente = trim(c[0]), zona = trim(c[1]);
    const vel = parseIntJava(trim(c[2]));
    if (vel === null) return { error: MSG.entero('velocidad promedio') };
    const carga = parseIntJava(trim(c[3]));
    if (carga === null) return { error: MSG.entero('carga en toneladas') };
    const estado = trim(c[4]);
    const indice = Math.trunc(vel * 0.6 + carga * 0.4) | 0;
    const v = { patente, zona, velocidad: vel, carga, estado, indice, columna: null, presente: false };
    if (col) {
      v.columna = col.defecto;
      if (n === 6) {
        const t = trim(c[5]);
        if (t === '' && col.vacio === 'defecto') v.columna = col.defecto;
        else if (col.tipo === 'texto') {
          if (t === '') return { error: MSG.vacio(col.nombre) };
          if (col.valores.length && !col.valores.map(String).includes(t)) return { error: MSG.valor(col.nombre, t) };
          v.columna = t; v.presente = true;
        } else {
          const x = parseIntJava(t);
          if (x === null) return { error: MSG.entero(col.nombre) };
          if (col.valores.length && !col.valores.map(Number).includes(x)) return { error: MSG.valor(col.nombre, x) };
          if (!enRango(x, col.rango)) return { error: MSG.rango(col.nombre, col.rango) };
          v.columna = x; v.presente = true;
        }
        for (const r of cfg.restricciones) {
          if (r.estado === estado && !r.valores.map(String).includes(String(v.columna))) return { error: MSG.restriccion(estado, col.nombre) };
        }
      }
    }
    // El constructor de VehiculoRuta
    if (patente === '') return { error: MSG.patente };
    if (zona === '') return { error: MSG.zona };
    if (vel <= 0 || vel >= 130) return { error: MSG.velocidad };
    if (carga > 45) return { error: MSG.carga };
    if (!cfg.estados.includes(estado)) return { error: MSG.estado(estado) };
    if (indice < 1 || indice > 90) return { error: MSG.indice };
    // La subclase, si corresponde: sus topes van después de super(...)
    const esp = cfg.especiales.find(e => cumple(e.cuando, v));
    if (esp) {
      for (const t of esp.topes) if (!pasaTope(valorCampo(v, t.campo), t)) return { error: MSG.tope(esp.clase, t) };
      v.clase = esp.clase; v.tipo = esp.etiqueta;
    } else { v.clase = 'VehiculoRuta'; v.tipo = etiquetaBase(cfg); }
    let costo = div(mul(cfg.baseDesdeColumna && col ? v.columna : FACTURACION, indice), 100);
    costo = aplicar(costo, cfg.extras, v);
    if (esp) costo = aplicar(costo, esp.ops, v);
    v.costo = costo;
    return { vehiculo: v };
  }

  function simular(texto, cfg) {
    if (texto.charCodeAt(0) === 0xFEFF) return { abortado: 'El archivo empieza con un BOM (UTF-8 con firma): Java lo lee como parte del encabezado y tira IllegalArgumentException("Encabezado CSV incorrecto"). Guardalo como UTF-8 sin BOM.' };
    const ls = lineas(texto);
    const enc = ls.length ? ls[0] : null;
    let sep, ancho;
    if (enc === ENCABEZADO) { sep = ','; ancho = 5; }
    else if (cfg.columna && enc === encabezadoNuevo(cfg)) { sep = cfg.separador; ancho = 6; }
    else return { abortado: 'Encabezado CSV incorrecto: «' + (enc == null ? '(archivo vacío)' : enc) + '». Se esperaba «' + ENCABEZADO + '»' + (cfg.columna ? ' o «' + encabezadoNuevo(cfg) + '»' : '') + '. Java tira IllegalArgumentException y no procesa nada.' };
    const filas = [];
    for (let i = 1; i < ls.length; i++) {
      const f = { linea: i + 1, texto: ls[i] };
      const c = ls[i].split(sep);
      if (c.length !== ancho) { f.resultado = 'Inválida'; f.motivo = MSG.ancho(cfg, ancho); }
      else if (cfg.descartes.includes(trim(c[4]))) { f.resultado = 'Descartada'; f.motivo = 'Estado ' + trim(c[4]) + ': se descarta sin validar'; }
      else {
        const r = desdeCampos(c, cfg);
        if (r.error) { f.resultado = 'Inválida'; f.motivo = r.error; }
        else { f.resultado = 'Procesada'; f.vehiculo = r.vehiculo; }
      }
      filas.push(f);
    }
    const vs = filas.filter(f => f.vehiculo).map(f => f.vehiculo);
    const porZona = [];
    for (const v of vs) {
      const e = porZona.find(z => z[0] === v.zona);
      if (e) e[1] = add(e[1], v.costo); else porZona.push([v.zona, v.costo]);
    }
    let conteo = null;
    if (cfg.conteo) {
      const m = new Map();
      for (const v of vs) {
        const k = claveConteo(v, cfg);
        m.set(k, (m.get(k) || 0) + 1);
      }
      conteo = [...m.entries()].sort((a, b) => typeof a[0] === 'number' ? a[0] - b[0] : comparar(a[0], b[0]));
    }
    const totales = cfg.totales.map(t => [t, vs.filter(v => String(t.campo === 'estado' ? v.estado : v.columna) === String(t.valor)).reduce((s, v) => add(s, v.costo), 0)]);
    const res = {
      filas, leidas: filas.length, procesadas: vs.length,
      descartadas: filas.filter(f => f.resultado === 'Descartada').length,
      invalidas: filas.filter(f => f.resultado === 'Inválida').length,
      total: vs.reduce((t, v) => add(t, v.costo), 0), porZona, conteo, totales,
      menor55: vs.filter(v => v.indice < 55).length, encabezado: ancho === 6 ? 'nuevo' : 'original',
    };
    res.salida = salidaMain(res, cfg);
    return res;
  }
  const claveConteo = (v, cfg) => cfg.conteo === 'estado' ? v.estado : cfg.conteo === 'zona' ? v.zona : cfg.conteo === 'tipo' ? v.tipo : v.columna;

  /* Lo que imprime el main generado (o el del preenunciado, si no hay cambios) */
  function salidaMain(r, cfg) {
    const L = [];
    L.push('Filas leídas: ' + r.leidas, 'Procesadas: ' + r.procesadas, 'Descartadas: ' + r.descartadas, 'Inválidas: ' + r.invalidas,
      'Vehículos con índice de desgaste menor a 55: ' + r.menor55);
    for (const f of r.filas) if (f.resultado === 'Inválida') L.push('Línea ' + f.linea + ': ' + f.motivo);
    if (hayCambios(cfg)) {
      L.push('Objetos: ' + r.procesadas);
      if (cfg.conteo) L.push(lineaConteo(r.conteo, cfg));
      for (const [t, n] of r.totales) L.push('Total ' + t.valor + ': ' + n);
    }
    L.push('Costo total por desgaste operativo: ' + r.total);
    for (const [z, t] of r.porZona) L.push(z + ': ' + t);
    return L.join('\n');
  }
  function clavesConteo(cfg) {
    if (cfg.conteo === 'estado') return cfg.estados.slice();
    if (cfg.conteo === 'tipo') return unicos([etiquetaBase(cfg)].concat(cfg.especiales.map(e => e.etiqueta)));
    if (cfg.conteo === 'columna' && cfg.columna && cfg.columna.tipo === 'texto' && cfg.columna.valores.length) return cfg.columna.valores.map(String);
    return null;
  }
  function lineaConteo(conteo, cfg) {
    const ks = clavesConteo(cfg), m = new Map(conteo);
    if (ks) return ks.map(k => k + ': ' + (m.get(k) || 0)).join(' | ');
    return 'Por ' + nombreConteo(cfg) + ': {' + conteo.map(([k, n]) => k + '=' + n).join(', ') + '}';
  }
  const nombreConteo = cfg => cfg.conteo === 'columna' ? cfg.columna.nombre : cfg.conteo;
  function hayCambios(cfg) {
    return !!(cfg.columna || cfg.especiales.length || cfg.extras.length || cfg.conteo || cfg.restricciones.length || cfg.totales.length
      || cfg.descartes.join() !== DESCARTES_BASE.join() || cfg.estados.join() !== ESTADOS_BASE.join() || cfg.archivo !== 'datos.csv');
  }

  // ───────────────────────── Revisar y acomodar una configuración ─────────────────────────
  /* Deja la configuración lista para simular y generar: sin repetidos, nombres de clase válidos y únicos, etiquetas */
  function normalizar(cfg) {
    cfg.estados = unicos(cfg.estados.filter(Boolean));
    cfg.descartes = unicos(cfg.descartes.filter(Boolean));
    const col = cfg.columna;
    if (col) {
      col.valores = col.tipo === 'entero' ? [...new Set(col.valores.map(Number).filter(Number.isFinite))] : unicos(col.valores.filter(v => v !== ''));
      if (col.tipo === 'entero') col.defecto = Number.isFinite(Number(col.defecto)) && String(col.defecto).trim() !== '' ? Number(col.defecto) : 0;
      else col.defecto = String(col.defecto == null ? '' : col.defecto);
      col.rango = col.rango || { min: null, minIncl: true, max: null, maxIncl: true };
      if (col.tipo !== 'entero') col.rango = { min: null, minIncl: true, max: null, maxIncl: true };
    }
    const usados = new Set(CLASES);
    for (const e of cfg.especiales) {
      let c = /^[A-Z][A-Za-z0-9_]*$/.test(e.clase || '') ? e.clase : e.cuando.op === 'igual' ? 'Vehiculo' + pascal(e.cuando.valor) : 'VehiculoCon' + cap(col ? col.nombre : 'Valor');
      if (!/^[A-Z]/.test(c)) c = 'Vehiculo' + c;
      while (usados.has(c)) c += 'Especial';
      usados.add(c); e.clase = c;
      if (!e.etiqueta) e.etiqueta = e.cuando.op === 'igual' ? String(e.cuando.valor).toUpperCase() : 'CON_' + constante(col ? col.nombre : 'VALOR');
    }
    if (!cfg.etiquetaBase) cfg.etiquetaBase = etiquetaBase(cfg);
    return cfg;
  }
  function revisar(cfg) {
    const av = [], col = cfg.columna;
    if (col) {
      if (!/^[a-zA-Z_]\w*$/.test(col.nombre)) av.push('El nombre de la columna nueva no sirve como nombre de Java: «' + col.nombre + '».');
      else if (RESERVADAS.has(col.nombre)) av.push('«' + col.nombre + '» es una palabra reservada o choca con una variable del código: cambiale el nombre.');
      if (CAMPOS.includes(col.nombre)) av.push('La columna nueva no puede llamarse como una que ya existe.');
      if (col.tipo === 'texto' && col.valores.length && col.vacio !== 'defecto' && !col.valores.includes(col.defecto)) av.push('El valor del formato viejo («' + col.defecto + '») no está entre los valores permitidos.');
      if (col.tipo === 'entero' && col.valores.length && !col.valores.includes(col.defecto) && !cfg.baseDesdeColumna) av.push('El valor del formato viejo (' + col.defecto + ') no está entre los valores permitidos.');
      if (cfg.separador !== ',' && cfg.separador !== ';' && cfg.separador !== '|') av.push('Separador raro: «' + cfg.separador + '».');
    }
    if ((cfg.baseDesdeColumna || cfg.extras.some(o => o.op === 'sumaPorCada')) && !(col && col.tipo === 'entero')) av.push('Para usar la columna en el costo, tiene que ser entera.');
    for (const e of cfg.especiales) {
      if (e.cuando.campo === 'columna' && !col) av.push(e.clase + ' depende de la columna nueva, pero no hay columna nueva.');
      if (e.cuando.op === 'mayor' && !(col && col.tipo === 'entero')) av.push(e.clase + ': «mayor a» necesita una columna entera.');
      if (e.ops.some(o => o.op === 'sumaPorCada') && !(col && col.tipo === 'entero')) av.push(e.clase + ': «por cada» necesita una columna entera.');
      if (e.topes.some(t => t.campo === 'columna') && !(col && col.tipo === 'entero')) av.push(e.clase + ': un tope sobre la columna necesita que sea entera.');
      if (e.cuando.campo === 'estado' && !cfg.estados.includes(String(e.cuando.valor))) av.push(e.clase + ' es para el estado ' + e.cuando.valor + ', que no está entre los válidos: no se va a usar nunca.');
      if (e.cuando.campo === 'columna' && e.cuando.op === 'igual' && col && col.valores.length && !col.valores.map(String).includes(String(e.cuando.valor))) av.push(e.clase + ' es para ' + col.nombre + ' = ' + e.cuando.valor + ', que no está entre los valores permitidos.');
      if (!e.ops.length && !e.topes.length) av.push(e.clase + ' no cambia nada: sin costo distinto ni topes.');
      for (const o of e.ops.concat(cfg.extras)) if (o.op === 'sumaPorCada' && !(o.cada > 0)) av.push('«Por cada» necesita un número mayor a 0.');
    }
    for (const r of cfg.restricciones) if (!cfg.estados.includes(r.estado)) av.push('La restricción para ' + r.estado + ' no se usa: no es un estado válido.');
    if (cfg.conteo === 'columna' && !col) av.push('Elegiste contar por la columna nueva, pero no hay columna nueva.');
    if (cfg.conteo === 'tipo' && !cfg.especiales.length) av.push('El conteo por tipo necesita al menos una subclase.');
    for (const d of cfg.descartes) if (cfg.estados.includes(d)) av.push('El estado ' + d + ' está como válido y como descartado: se descarta (el parser lo mira primero).');
    for (const t of cfg.totales) if (t.campo === 'columna' && !col) av.push('El total por ' + t.valor + ' necesita la columna nueva.');
    if (!/^[\w.-]+\.csv$/i.test(cfg.archivo)) av.push('El archivo del main tiene que ser un nombre de CSV (por ejemplo datos-parcial.csv).');
    return av;
  }

  /* ¿Cambia algo de las filas del formato de cinco columnas? Entonces los tests del preenunciado que esperan los valores
     viejos van a fallar (en un parcial, la consigna pide conservar el comportamiento anterior). */
  function afectaFormatoViejo(cfg) {
    const col = cfg.columna, p = [];
    const viejo = { columna: col ? col.defecto : null, presente: false, estado: '' };
    const cambiaCosto = ops => ops.some(o => (o.op === 'suma' && o.n) || (o.op === 'porcentaje' && o.n) || (o.op === 'multiplica' && o.n !== 1)
      || (o.op === 'sumaPorCada' && typeof viejo.columna === 'number' && o.cada > 0 && Math.trunc(viejo.columna / o.cada) * o.n !== 0));
    if (cambiaCosto(cfg.extras)) p.push('el costo de todos los vehículos');
    if (cfg.baseDesdeColumna && col && Number(col.defecto) !== FACTURACION) p.push(`la base del costo (${col.defecto} en lugar de 2000)`);
    for (const e of cfg.especiales) {
      const loToca = (e.cuando.campo === 'estado' && ESTADOS_BASE.includes(String(e.cuando.valor))) || (e.cuando.op === 'igual' && col && String(e.cuando.valor) === String(col.defecto)) || (e.cuando.op === 'mayor' && col && Number(col.defecto) > Number(e.cuando.valor));
      if (loToca && (cambiaCosto(e.ops) || e.topes.length)) p.push(`${e.clase} (${quienEs(e, cfg)})`);
    }
    for (const x of ESTADOS_BASE) if (!cfg.estados.includes(x) || cfg.descartes.includes(x)) p.push('el estado ' + x);
    return p.length ? 'Esto cambia filas del formato de cinco columnas: ' + p.join(', ') + '. Los tests del preenunciado que esperan los valores viejos van a fallar; en el parcial, la consigna pide conservar el comportamiento anterior, así que fijate si el enunciado realmente dice eso.' : null;
  }

  // ───────────────────────── El Java ─────────────────────────
  const j = s => JSON.stringify(String(s));
  const tipoJava = col => col.tipo === 'entero' ? 'int' : 'String';
  const literal = (col, v) => col.tipo === 'entero' ? String(Number(v)) : j(v);
  function condJava(cuando, col) {
    if (cuando.op === 'presente') return 'presente';
    if (cuando.campo === 'estado') return j(cuando.valor) + '.equals(estado)';
    if (cuando.op === 'mayor') return col.nombre + ' > ' + Number(cuando.valor);
    return col.tipo === 'entero' ? col.nombre + ' == ' + Number(cuando.valor) : j(cuando.valor) + '.equals(' + col.nombre + ')';
  }
  function opsJava(ops, col, ind) {
    return ops.map(o => {
      if (o.op === 'suma') return `${ind}costo = costo + ${o.n};`;
      if (o.op === 'porcentaje') return `${ind}costo = costo * ${100 + o.n} / 100;`;
      if (o.op === 'multiplica') return `${ind}costo = costo * ${o.n};`;
      return `${ind}costo = costo + ${o.n} * (get${cap(col.nombre)}() / ${o.cada});`;
    }).join('\n');
  }
  const campoJava = { carga: 'cargaToneladas', velocidad: 'velocidadPromedio', indice: 'indiceDesgaste' };

  function generarParser(cfg) {
    const col = cfg.columna, descSet = cfg.descartes.join() !== DESCARTES_BASE.join();
    const imp = ['java.io.BufferedReader', 'java.io.IOException', 'java.nio.charset.StandardCharsets', 'java.nio.file.Files', 'java.nio.file.Path', 'java.util.ArrayList', 'java.util.List'];
    if (descSet) imp.push('java.util.Set');
    let s = 'package ar.edu.backend;\n\n' + imp.map(i => `import ${i};\n`).join('') + '\npublic final class ParserVehiculos {\n';
    s += `    private static final String ENCABEZADO = ${j(ENCABEZADO)};\n`;
    if (col) s += `    private static final String ENCABEZADO_NUEVO = ${j(encabezadoNuevo(cfg))};\n`;
    if (descSet) s += `    private static final Set<String> ESTADOS_DESCARTADOS = Set.of(${cfg.descartes.map(j).join(', ')});\n`;
    s += `
    public ResultadoParseo parsear(Path archivo) throws IOException {
        List<VehiculoRuta> vehiculos = new ArrayList<>();
        List<ErrorParseo> errores = new ArrayList<>();
        int filasLeidas = 0;
        int filasDescartadas = 0;

        try (BufferedReader lector = Files.newBufferedReader(archivo, StandardCharsets.UTF_8)) {
            String encabezado = lector.readLine();
`;
    if (col) s += `            String separador;
            int columnas;
            if (ENCABEZADO.equals(encabezado)) {
                separador = ",";
                columnas = 5;
            } else if (ENCABEZADO_NUEVO.equals(encabezado)) {
                separador = ${j(cfg.separador === '|' ? '\\|' : cfg.separador)};
                columnas = 6;
            } else {
                throw new IllegalArgumentException("Encabezado CSV incorrecto");
            }
`;
    else s += `            if (!ENCABEZADO.equals(encabezado)) {
                throw new IllegalArgumentException("Encabezado CSV incorrecto");
            }
`;
    s += `
            String linea;
            int numeroLinea = 1;
            while ((linea = lector.readLine()) != null) {
                numeroLinea++;
                filasLeidas++;
`;
    s += col ? `                String[] campos = linea.split(separador, -1);
                if (campos.length != columnas) {
                    errores.add(new ErrorParseo(numeroLinea, "La fila debe tener exactamente " + columnas + " columnas"));
                    continue;
                }
` : `                String[] campos = linea.split(",", -1);
                if (campos.length != 5) {
                    errores.add(new ErrorParseo(numeroLinea, "La fila debe tener exactamente cinco columnas"));
                    continue;
                }
`;
    s += `
                String estado = campos[4].trim();
                if (${descSet ? 'ESTADOS_DESCARTADOS.contains(estado)' : '"EN_DEPOSITO".equals(estado)'}) {
                    filasDescartadas++;
                    continue;
                }

                try {
                    vehiculos.add(VehiculoRuta.desdeCampos(campos));
                } catch (IllegalArgumentException exception) {
                    errores.add(new ErrorParseo(numeroLinea, exception.getMessage()));
                }
            }
        }

        return new ResultadoParseo(vehiculos, errores, filasLeidas, filasDescartadas);
    }
}
`;
    return s;
  }

  function generarVehiculo(cfg) {
    const col = cfg.columna, sub = cfg.especiales.length > 0, estSet = cfg.estados.join() !== ESTADOS_BASE.join();
    const T = col && tipoJava(col), N = col && col.nombre, G = col && 'get' + cap(N), K = col && constante(N);
    const PARAMS = `            String patente,
            String zona,
            int velocidadPromedio,
            int cargaToneladas,
            String estado,
            int indiceDesgaste`;
    const usaSet = estSet || (col && col.valores.length) || (col && cfg.restricciones.length);
    let s = 'package ar.edu.backend;\n\n' + (usaSet ? 'import java.util.Set;\n\n' : '');
    s += `public ${sub ? '' : 'final '}class VehiculoRuta {\n`;
    if (estSet) s += `    private static final Set<String> ESTADOS_VALIDOS = Set.of(${cfg.estados.map(j).join(', ')});\n`;
    if (col && col.valores.length) s += `    private static final Set<${col.tipo === 'entero' ? 'Integer' : 'String'}> VALORES_${K} = Set.of(${col.valores.map(v => literal(col, v)).join(', ')});\n`;
    if (col) s += `    private static final ${T} ${K}_POR_DEFECTO = ${literal(col, col.defecto)};\n`;
    if (estSet || col) s += '\n';
    s += `    private final String patente;
    private final String zona;
    private final int velocidadPromedio;
    private final int cargaToneladas;
    private final String estado;
    private final int indiceDesgaste;
`;
    if (col) s += `    private final ${T} ${N};\n`;
    s += '\n';
    if (col) s += `    public VehiculoRuta(
${PARAMS}) {
        this(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste, ${K}_POR_DEFECTO);
    }

`;
    s += `    public VehiculoRuta(
${PARAMS}${col ? `,\n            ${T} ${N}` : ''}) {
        this.patente = validarTexto(patente, "La patente no puede estar vacía");
        this.zona = validarTexto(zona, "La zona no puede estar vacía");
        if (velocidadPromedio <= 0 || velocidadPromedio >= 130) {
            throw new IllegalArgumentException("La velocidad promedio debe ser mayor a 0 y menor a 130");
        }
        if (cargaToneladas > 45) {
            throw new IllegalArgumentException("La carga no puede superar las 45 toneladas");
        }
        if (${estSet ? '!ESTADOS_VALIDOS.contains(estado)' : '!"EN_RUTA".equals(estado) && !"DEMORADO".equals(estado)'}) {
            throw new IllegalArgumentException("Estado de vehículo inválido: " + estado);
        }
        int indiceCalculado = calcularIndiceDesgaste(velocidadPromedio, cargaToneladas);
        if (indiceDesgaste < 1 || indiceDesgaste > 90 || indiceDesgaste != indiceCalculado) {
            throw new IllegalArgumentException("El índice de desgaste debe coincidir con el cálculo y estar entre 1 y 90");
        }
        this.velocidadPromedio = velocidadPromedio;
        this.cargaToneladas = cargaToneladas;
        this.estado = estado;
        this.indiceDesgaste = indiceDesgaste;
${col ? `        this.${N} = ${N};\n` : ''}    }

    public static VehiculoRuta desdeCampos(String[] campos) {
`;
    s += col ? `        if (campos == null || (campos.length != 5 && campos.length != 6)) {
            throw new IllegalArgumentException("La fila debe tener cinco o seis columnas");
        }
` : `        if (campos == null || campos.length != 5) {
            throw new IllegalArgumentException("La fila debe tener exactamente cinco columnas");
        }
`;
    s += `
        String patente = limpiar(campos[0]);
        String zona = limpiar(campos[1]);
        int velocidadPromedio = convertirEntero(campos[2], "velocidad promedio");
        int cargaToneladas = convertirEntero(campos[3], "carga en toneladas");
        String estado = limpiar(campos[4]);
        int indiceDesgaste = calcularIndiceDesgaste(velocidadPromedio, cargaToneladas);
`;
    const usaPresente = cfg.especiales.some(e => e.cuando.op === 'presente');
    if (col) {
      s += `        ${T} ${N} = campos.length == 6 ? leer${cap(N)}(campos[5]) : ${K}_POR_DEFECTO;\n`;
      if (usaPresente) s += `        boolean presente = campos.length == 6 && !limpiar(campos[5]).isEmpty();\n`;
      for (const r of cfg.restricciones) {
        s += `        if (campos.length == 6 && ${j(r.estado)}.equals(estado) && !Set.of(${unicos(r.valores).map(v => literal(col, v)).join(', ')}).contains(${N})) {
            throw new IllegalArgumentException(${j(MSG.restriccion(r.estado, N))});
        }
`;
      }
    }
    const args = `patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste${col ? ', ' + N : ''}`;
    s += '\n';
    for (const e of cfg.especiales) s += `        if (${condJava(e.cuando, col)}) {
            return new ${e.clase}(${args});
        }
`;
    s += `        return new VehiculoRuta(${args});
    }
`;
    if (col) {
      s += `
    private static ${T} leer${cap(N)}(String valor) {
        String texto = limpiar(valor);
`;
      if (col.vacio === 'defecto') s += `        if (texto.isEmpty()) {
            return ${K}_POR_DEFECTO;
        }
`;
      if (col.tipo === 'texto') {
        if (col.vacio !== 'defecto') s += `        if (texto.isEmpty()) {
            throw new IllegalArgumentException(${j(MSG.vacio(N))});
        }
`;
        if (col.valores.length) s += `        if (!VALORES_${K}.contains(texto)) {
            throw new IllegalArgumentException("Valor de ${N} inválido: " + texto);
        }
`;
        s += `        return texto;
    }
`;
      } else {
        s += `        int numero = convertirEntero(texto, ${j(N)});
`;
        if (col.valores.length) s += `        if (!VALORES_${K}.contains(numero)) {
            throw new IllegalArgumentException("Valor de ${N} inválido: " + numero);
        }
`;
        if (tieneRango(col.rango)) {
          const r = col.rango, c = [];
          if (r.min != null) c.push(`numero ${r.minIncl ? '<' : '<='} ${r.min}`);
          if (r.max != null) c.push(`numero ${r.maxIncl ? '>' : '>='} ${r.max}`);
          s += `        if (${c.join(' || ')}) {
            throw new IllegalArgumentException(${j(MSG.rango(N, r))});
        }
`;
        }
        s += `        return numero;
    }
`;
      }
    }
    s += `
    private static int calcularIndiceDesgaste(int velocidadPromedio, int cargaToneladas) {
        return (int) (velocidadPromedio * 0.6 + cargaToneladas * 0.4);
    }

    private static int convertirEntero(String valor, String nombreCampo) {
        try {
            return Integer.parseInt(limpiar(valor));
        } catch (NumberFormatException exception) {
            throw new IllegalArgumentException("El campo " + nombreCampo + " debe ser un entero", exception);
        }
    }

    private static String validarTexto(String valor, String mensaje) {
        String texto = limpiar(valor);
        if (texto.isEmpty()) {
            throw new IllegalArgumentException(mensaje);
        }
        return texto;
    }

    private static String limpiar(String valor) {
        if (valor == null) {
            throw new IllegalArgumentException("Los campos no pueden ser nulos");
        }
        return valor.trim();
    }

    public int getCostoDesgasteOperativo() {
`;
    const base = cfg.baseDesdeColumna && col ? N : '2000';
    if (!cfg.extras.length) s += `        return ${base} * indiceDesgaste / 100;\n`;
    else s += `        int costo = ${base} * indiceDesgaste / 100;\n${opsJava(cfg.extras, col, '        ')}\n        return costo;\n`;
    s += `    }

    public String getPatente() {
        return patente;
    }

    public String getZona() {
        return zona;
    }

    public int getVelocidadPromedio() {
        return velocidadPromedio;
    }

    public int getCargaToneladas() {
        return cargaToneladas;
    }

    public String getEstado() {
        return estado;
    }

    public int getIndiceDesgaste() {
        return indiceDesgaste;
    }
`;
    if (col) s += `
    public ${T} ${G}() {
        return ${N};
    }
`;
    if (cfg.conteo === 'tipo') s += `
    /** Para el conteo por tipo: cada subclase dice cómo se llama. */
    public String getTipo() {
        return ${j(etiquetaBase(cfg))};
    }
`;
    return s + '}\n';
  }

  function quienEs(e, cfg) {
    const N = cfg.columna && cfg.columna.nombre;
    if (e.cuando.op === 'presente') return `con un valor en ${N}`;
    if (e.cuando.op === 'mayor') return `con ${N} mayor a ${e.cuando.valor}`;
    return e.cuando.campo === 'estado' ? `en estado ${e.cuando.valor}` : `con ${N} ${e.cuando.valor}`;
  }

  function generarSubclase(e, cfg) {
    const col = cfg.columna, N = col && col.nombre, T = col && tipoJava(col);
    let s = `package ar.edu.backend;

/** Vehículo ${quienEs(e, cfg)}: ${describirEspecial(e, cfg)}. */
public class ${e.clase} extends VehiculoRuta {
    public ${e.clase}(
            String patente,
            String zona,
            int velocidadPromedio,
            int cargaToneladas,
            String estado,
            int indiceDesgaste${col ? `,\n            ${T} ${N}` : ''}) {
        super(patente, zona, velocidadPromedio, cargaToneladas, estado, indiceDesgaste${col ? ', ' + N : ''});
`;
    for (const t of e.topes) {
      const x = t.campo === 'columna' ? N : campoJava[t.campo];
      const mal = t.op === 'min' ? `${x} ${t.incl ? '<' : '<='} ${t.n}` : `${x} ${t.incl ? '>' : '>='} ${t.n}`;
      s += `        if (${mal}) {
            throw new IllegalArgumentException(${j(MSG.tope(e.clase, t))});
        }
`;
    }
    s += `    }
`;
    if (e.ops.length) s += `
    @Override
    public int getCostoDesgasteOperativo() {
        int costo = super.getCostoDesgasteOperativo();
${opsJava(e.ops, col, '        ')}
        return costo;
    }
`;
    if (cfg.conteo === 'tipo') s += `
    @Override
    public String getTipo() {
        return ${j(e.etiqueta)};
    }
`;
    return s + '}\n';
  }

  function getterConteo(cfg) {
    if (cfg.conteo === 'estado') return 'VehiculoRuta::getEstado';
    if (cfg.conteo === 'zona') return 'VehiculoRuta::getZona';
    if (cfg.conteo === 'tipo') return 'VehiculoRuta::getTipo';
    return 'VehiculoRuta::get' + cap(cfg.columna.nombre);
  }
  const claveJava = cfg => cfg.conteo === 'columna' && cfg.columna.tipo === 'entero' ? 'Integer' : 'String';

  function generarFlota(cfg, original) {
    if (!cfg.conteo) return original;
    const met = `    public Map<${claveJava(cfg)}, Long> contarPor${cap(nombreConteo(cfg))}() {
        return vehiculos.stream()
                .collect(Collectors.groupingBy(${getterConteo(cfg)}, TreeMap::new, Collectors.counting()));
    }

`;
    const s = original.replace('import java.util.Map;\n', 'import java.util.Map;\nimport java.util.TreeMap;\n')
      .replace('import java.util.function.Predicate;\n', 'import java.util.function.Predicate;\nimport java.util.stream.Collectors;\n');
    return s.replace('    public List<VehiculoRuta> getVehiculos() {', met + '    public List<VehiculoRuta> getVehiculos() {');
  }

  function filtroJava(t, cfg) {
    if (t.campo === 'estado') return `vehiculo -> ${j(t.valor)}.equals(vehiculo.getEstado())`;
    const G = 'get' + cap(cfg.columna.nombre);
    return cfg.columna.tipo === 'entero' ? `vehiculo -> vehiculo.${G}() == ${Number(t.valor)}` : `vehiculo -> ${j(t.valor)}.equals(vehiculo.${G}())`;
  }

  function generarApp(cfg) {
    let s = `package ar.edu.backend;

import java.io.IOException;
import java.nio.file.Path;
${cfg.conteo ? 'import java.util.Map;\n' : ''}
public class App {
    public static void main(String[] args) throws IOException {
        Path archivo = args.length == 0 ? Path.of("datos", ${j(cfg.archivo)}) : Path.of(args[0]);
        ResultadoParseo resultado = new ParserVehiculos().parsear(archivo);
        Flota flota = new Flota(resultado.getVehiculos());
`;
    if (cfg.conteo) s += `        Map<${claveJava(cfg)}, Long> conteo = flota.contarPor${cap(nombreConteo(cfg))}();\n`;
    s += `
        System.out.println(resultado.getResumenErrores());
        System.out.println("Objetos: " + resultado.getVehiculos().size());
`;
    if (cfg.conteo) {
      const ks = clavesConteo(cfg);
      if (ks) s += `        System.out.println(${ks.map((k, i) => `${i ? '" | ' : '"'}${k.replace(/["\\]/g, '\\$&')}: " + conteo.getOrDefault(${j(k)}, 0L)`).join('\n                + ')});\n`;
      else s += `        System.out.println("Por ${nombreConteo(cfg)}: " + conteo);\n`;
    }
    for (const t of cfg.totales) s += `        System.out.println(${j('Total ' + t.valor + ': ')} + flota.sumarCostoDesgasteOperativo(${filtroJava(t, cfg)}));\n`;
    s += `        System.out.println(flota.panorama());
    }
}
`;
    return s;
  }

  /* El proyecto: los archivos que cambian o se agregan (nombre → texto) */
  function generar(cfg, originales) {
    const out = {};
    out['ParserVehiculos.java'] = generarParser(cfg);
    out['VehiculoRuta.java'] = generarVehiculo(cfg);
    for (const e of cfg.especiales) out[e.clase + '.java'] = generarSubclase(e, cfg);
    if (cfg.conteo && originales && originales['Flota.java']) out['Flota.java'] = generarFlota(cfg, originales['Flota.java']);
    if (hayCambios(cfg)) out['App.java'] = generarApp(cfg);
    return out;
  }

  // ───────────────────────── En palabras ─────────────────────────
  function describirOp(o, cfg) {
    if (o.op === 'suma') return `${o.n >= 0 ? '+' : '−'} ${Math.abs(o.n)} USD`;
    if (o.op === 'porcentaje') return `${o.n >= 0 ? '+' : '−'} ${Math.abs(o.n)} % (× ${100 + o.n} / 100)`;
    if (o.op === 'multiplica') return `× ${o.n}`;
    return `+ ${o.n} USD por cada ${o.cada} de ${cfg.columna ? cfg.columna.nombre : 'la columna'}`;
  }
  const signoTope = t => t.op === 'min' ? (t.incl ? '≥' : '>') : (t.incl ? '≤' : '<');
  function describirEspecial(e, cfg) {
    const p = [];
    if (e.ops.length) p.push('costo ' + e.ops.map(o => describirOp(o, cfg)).join(', '));
    for (const t of e.topes) p.push(`${(NOMBRE_CAMPO[t.campo] || t.campo).toLowerCase()} ${signoTope(t)} ${t.n}`);
    return p.join('; ') || 'las mismas reglas';
  }

  // ───────────────────────── Leer el enunciado (sin IA) ─────────────────────────
  const sinTildes = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const NUM = '(\\d[\\d_.]*\\d|\\d)';
  const num = s => Number(String(s).replace(/[_.](?=\d{3}(?!\d))/g, '').replace(/_/g, ''));
  const PALABRAS_NO = new Set(['CSV', 'USD', 'UTF', 'JDK', 'API', 'JSON', 'ZIP', 'NO', 'OK', 'IDE', 'MD', 'DECISIONES', 'IT', 'PDF', 'JAVA', 'MAIN', 'BOM', 'NETOS', 'TP', 'TPI', 'IVA']);
  const UNIDADES_CADA = /^(unidad|km|kilometro|punto|dia|hora|peaje|parada|entrega|tonelada|litro|minuto)/;

  function oraciones(texto) {
    const t = texto.replace(/\r/g, '').replace(/^[ \t]*[\u2022\u25AA\u25E6\u25CF\u25A0\u2013\u2014\uF000-\uF8FF·]+[ \t]*/gm, '- ').replace(/[ \t]+/g, ' ');
    // Un renglón en blanco separa párrafos, salvo que lo que sigue arranque en minúscula (en los PDF, un `código` suele
    // quedar en su propio renglón: «El nuevo encabezado es␤␤patente,zona,…»)
    return t.replace(/\n\s*\n(?=\s*[a-zñáéíóú`])/g, ' ').split(/(?<=[.;:!?])\s+(?=[A-ZÁÉÍÓÚÑ0-9¿"«(`-])|\n{2,}|\n(?=\s*(?:\d+[.)]|[-*])\s)/)
      .map(s => s.replace(/\s+/g, ' ').replace(/^- /, '').trim()).filter(Boolean);
  }
  const mayusculas = s => (s.match(/\b[A-Z][A-Z0-9_]+\b/g) || []).filter(w => !PALABRAS_NO.has(w) && !/^\d/.test(w) && w.length > 1);
  function campoPorPalabras(n) {
    if (/tonelad|\bcarga\b|\bt\b/.test(n)) return 'carga';
    if (/km\s*\/\s*h|velocidad/.test(n)) return 'velocidad';
    if (/indice|desgaste/.test(n)) return 'indice';
    return null;
  }
  const partesNombre = nombre => sinTildes(nombre).replace(/([a-z])([A-Z])/g, '$1 $2').toLowerCase().split(/[\s_]+/)
    .filter(p => p.length >= 4 && !['patente', 'zona', 'velocidad', 'promedio', 'carga', 'toneladas', 'estado'].includes(p));

  function leerEnunciado(texto, csvTexto) {
    const cfg = configBase(), ev = [], avisos = [];
    const nota = (clave, oracion, que) => ev.push({ clave, oracion, que });
    const O = oraciones(texto || '');
    const N = O.map(o => sinTildes(o).toLowerCase());
    const C = O.map(o => sinTildes(o));                       // sin tildes pero con mayúsculas
    const todo = sinTildes(texto || '').toLowerCase();
    cfg.archivo = 'datos-parcial.csv';
    // Las reglas están antes de «Resultado requerido»; los ejemplos no son reglas
    let finReglas = N.findIndex(n => /^resultado\s+requerido|^\d[.)]?\s*integrar\s+la\s+lectura/.test(n));
    if (finReglas < 0) finReglas = O.length;
    const esEjemplo = i => /^ejemplos?\b|^por\s+ejemplo|^\d[\d_.]*\s*(?:g|t|toneladas|km|usd)?\s+\w+\s+cuesta/.test(N[i]);

    // 1) El encabezado nuevo: la columna y el separador
    let campos = null;
    O.forEach((o, i) => {
      if (campos) return;
      const m = o.match(/encabezado\s+(?:nuevo\s+|evolucionado\s+)?(?:del\s+archivo\s+|del\s+csv\s+)?(?:es|queda|pasa\s+a\s+ser)\s*:?\s*[`"«]?([A-Za-z_]\w*(?:\s*[,;|]\s*[A-Za-z_]\w*){3,})/i)
        || (N[i].includes('encabezado') && o.match(/[`"«]?([A-Za-z_]\w*(?:\s*[,;|]\s*[A-Za-z_]\w*){4,})/));
      if (m) { campos = m[1].replace(/\s+/g, ''); nota('columna', o, 'El encabezado nuevo'); }
    });
    if (!campos && csvTexto) {
      const enc = lineas(csvTexto)[0];
      if (enc && enc !== ENCABEZADO && /^[\w,;|]+$/.test(enc)) { campos = enc; avisos.push('El enunciado no dice el encabezado nuevo: lo saqué de la primera línea del CSV.'); }
    }
    if (campos) {
      const sep = campos.includes(';') ? ';' : campos.includes('|') ? '|' : ',';
      const fs = campos.split(sep);
      const nuevos = fs.length === 6 ? [fs[5]] : fs.filter(f => !CAMPOS.includes(f));
      if (fs.slice(0, 5).join() !== CAMPOS.join()) avisos.push('Las primeras cinco columnas del encabezado nuevo no son las del preenunciado (' + fs.slice(0, 5).join(sep) + '): revisalo.');
      if (nuevos.length > 1) avisos.push('El encabezado trae más de una columna nueva (' + nuevos.join(', ') + '): este laboratorio maneja una sola, la primera.');
      if (nuevos.length) {
        cfg.separador = sep;
        cfg.columna = { nombre: nuevos[0], tipo: 'texto', valores: [], rango: { min: null, minIncl: true, max: null, maxIncl: true }, vacio: 'invalida', defecto: '' };
      }
    }
    const col = cfg.columna;
    const estadosEnTexto = new Set(ESTADOS_BASE.concat(DESCARTES_BASE));

    // 2) Estados nuevos y descartes
    const agregarDescarte = (w, o) => {
      if (w === 'EN_DEPOSITO' || ESTADOS_BASE.includes(w) || (col && w === col.nombre.toUpperCase()) || cfg.descartes.includes(w)) return;
      cfg.descartes.push(w); estadosEnTexto.add(w); nota('descartes', o, 'Se descarta ' + w);
    };
    O.forEach((o, i) => {
      const n = N[i], c = C[i];
      if (/descart/.test(n) && !/no\s+se\s+descart/.test(n)) {
        let hallado = false;
        const m1 = c.match(/descart\w*\s+(?:tambien\s+)?(?:(?:a\s+)?(?:las\s+filas|los\s+vehiculos|los\s+registros|las\s+de|los\s+de)\s+)?(?:(?:con|en)\s+(?:el\s+)?estado\s+)?([A-Z][A-Z0-9_]+(?:\s*(?:,|\by\b|\bo\b)\s*[A-Z][A-Z0-9_]+)*)/i);
        if (m1) for (const w of mayusculas(m1[1])) { agregarDescarte(w, o); hallado = true; }
        const m2 = c.match(/([A-Z][A-Z0-9_]+)(?:\s*(?:,|\by\b|\bo\b)\s*([A-Z][A-Z0-9_]+))*\s+(?:tambien\s+)?(?:se\s+descarta|son\s+descartad|quedan?\s+descartad|se\s+descartan)/);
        if (m2) for (const w of mayusculas(m2[0])) { agregarDescarte(w, o); hallado = true; }
        if (!hallado && /^se\s+descarta/.test(n) && i > 0) {
          const w = mayusculas(C[i - 1].split(/\s/).slice(0, 3).join(' '))[0];
          if (w) agregarDescarte(w, O[i - 1] + ' ' + o);
        }
      }
      const ne = c.match(/(?:estado\s+nuevo|nuevo\s+estado|(?:se\s+)?(?:agrega|incorpora|suma)\s+(?:tambien\s+)?(?:el\s+)?estado|aparece\s+(?:el\s+)?estado)\s*[,:]?\s*([A-Z][A-Z0-9_]+)/i);
      if (ne && /^[A-Z][A-Z0-9_]+$/.test(ne[1]) && !/descart/.test(n) && !cfg.estados.includes(ne[1]) && !DESCARTES_BASE.includes(ne[1])) {
        cfg.estados.push(ne[1]); estadosEnTexto.add(ne[1]); nota('estados', o, 'Estado válido nuevo: ' + ne[1]);
      }
      if (/es\s+(?:un\s+|tambien\s+un\s+)?estado\s+valido|son\s+estados\s+validos|tambien\s+(?:es|son)\s+validos?/.test(n)) {
        let ws = mayusculas(c).filter(x => !cfg.estados.includes(x) && !cfg.descartes.includes(x));
        if (!ws.length && i > 0) ws = mayusculas(C[i - 1].split(/\s/).slice(0, 3).join(' ')).filter(x => !cfg.estados.includes(x));
        for (const w of ws) { cfg.estados.push(w); estadosEnTexto.add(w); nota('estados', o, 'Estado válido nuevo: ' + w); }
      }
    });

    // 3) La columna: tipo, valores, rango, vacío y el valor del formato viejo
    if (col) {
      const cn = sinTildes(col.nombre).toLowerCase(), partes = partesNombre(col.nombre);
      const hablaDeCol = n => n.includes(cn) || partes.some(p => n.includes(p)) || /sexto\s+campo|6\s*(?:ta|a|ª|\.ª|º)?\s*columna|sexta\s+columna|columna\s+nueva|nueva\s+columna|campo\s+nuevo|nuevo\s+campo|presencia\s+de\s+un\s+valor/.test(n);
      const otroCampo = n => /tonelad|velocidad|km\s*\/\s*h|indice/.test(n);
      const esEstado = w => estadosEnTexto.has(w) || cfg.estados.includes(w) || cfg.descartes.includes(w);
      // Restricciones: «los vehículos DEMORADO solo admiten GENERAL»
      O.forEach((o, i) => {
        if (i >= finReglas) return;
        const re = /([A-Z][A-Z0-9_]+)\s+(?:solo|unicamente)\s+(?:admi?n?ten?|aceptan?|puede[n]?\s+(?:ser|tener|llevar))\s+([A-Z0-9][A-Z0-9_]*(?:\s*(?:,|\bo\b|\by\b)\s*[A-Z0-9][A-Z0-9_]*)*)/g;
        let m;
        while ((m = re.exec(C[i]))) {
          if (!cfg.estados.includes(m[1])) continue;
          const vals = (m[2].match(/[A-Z0-9][A-Z0-9_]*/g) || []).filter(w => !PALABRAS_NO.has(w));
          if (vals.length) { cfg.restricciones.push({ estado: m[1], valores: vals }); nota('restricciones', o, `En el formato nuevo, ${m[1]} solo admite ${vals.join(' o ')}`); }
        }
      });
      // Valores en mayúsculas que no son estados
      O.forEach((o, i) => {
        if (i >= finReglas) return;
        const n = N[i];
        if (!hablaDeCol(n) && !/admite\s+exactamente|unicos\s+valores|solo\s+admite|valores\s+validos|valores\s+posibles/.test(n)) return;
        const pre = C[i].replace(/[A-Z][A-Z0-9_]+\s+(?:solo|unicamente)\s+(?:admi?n?ten?|aceptan?)\s+[A-Z0-9_ ,]+/g, ' ');
        const vs = mayusculas(pre).filter(w => !esEstado(w) && w !== col.nombre.toUpperCase());
        if (vs.length && /admite|valores?|puede\s+(?:ser|admitir|tomar)|acepta|son\s+los\s+unicos|exactamente|indica|\bes\b|\bson\b/.test(n)) {
          const nuevos = vs.filter(v => !col.valores.includes(v));
          if (nuevos.length) { col.valores.push(...nuevos); nota('columna', o, 'Valores permitidos: ' + nuevos.join(', ')); }
        }
      });
      // ¿Entero?
      const esEntero = O.some((o, i) => i < finReglas && hablaDeCol(N[i]) && /\bentero|numeric|un\s+numero|un\s+importe|valores?\s+mayores|valores?\s+menores|mayores?\s+(?:o\s+)?iguales?|entre\s+\d|de\s+\d+\s+a\s+\d+|\d+\s*,\s*\d+\s*(?:,\s*\d+\s*)*(?:o|y)\s*\d+|\d+(?:\s*\/\s*\d+){2,}/.test(N[i]))
        || (!col.valores.length && csvTexto && columnaNumerica(csvTexto, cfg));
      if (esEntero && !col.valores.length) col.tipo = 'entero';
      if (col.tipo === 'entero') {
        O.forEach((o, i) => {
          const n = N[i];
          if (i >= finReglas || otroCampo(n) || esEjemplo(i)) return;
          const r = col.rango, habla = hablaDeCol(n);
          const set = n.match(/(\d+(?:\s*,\s*\d+)+\s*(?:o|y)\s*\d+)/) || n.match(/(\d+(?:\s*\/\s*\d+){2,})/);
          if (set && (habla || /distint[oa]s?\s+de|plazos?|unicos\s+valores|valores\s+(?:validos|posibles|permitidos)/.test(n)) && /plazo|valores?|admite|son\b|validos|distint|posibles/.test(n)) {
            const nuevos = set[1].match(/\d+/g).map(Number).filter(x => !col.valores.includes(x));
            if (nuevos.length) { col.valores.push(...nuevos); nota('columna', o, 'Valores permitidos: ' + col.valores.join(', ')); }
          }
          const m0 = n.match(/^(\d+)\s+(?:conserva|mantiene|es\s+(?:un|el)\s+(?:vehiculo|valor)\s+(?:sin|comun|normal))/);
          if (m0 && col.valores.length && !col.valores.includes(Number(m0[1]))) { col.valores.push(Number(m0[1])); nota('columna', o, 'Valor permitido: ' + m0[1]); }
          if (!habla) return;
          let m;
          if ((m = n.match(new RegExp('mayor(?:es)?\\s+(?:o\\s+)?iguales?\\s+(?:a|que)\\s+' + NUM)))) { r.min = num(m[1]); r.minIncl = true; nota('columna', o, 'Mínimo ' + r.min + ' (inclusive)'); }
          else if ((m = n.match(new RegExp('(?:mayor(?:es)?|superior(?:es)?)\\s+(?:a|que)\\s+' + NUM)))) { r.min = num(m[1]); r.minIncl = false; nota('columna', o, 'Mayor a ' + r.min); }
          if ((m = n.match(new RegExp('menor(?:es)?\\s+(?:o\\s+)?iguales?\\s+(?:a|que)\\s+' + NUM)))) { r.max = num(m[1]); r.maxIncl = true; nota('columna', o, 'Máximo ' + r.max + ' (inclusive)'); }
          else if ((m = n.match(new RegExp('(?:menor(?:es)?|inferior(?:es)?)\\s+(?:a|que)\\s+' + NUM)))) { r.max = num(m[1]); r.maxIncl = false; nota('columna', o, 'Menor a ' + r.max); }
          if ((m = n.match(new RegExp('entre\\s+' + NUM + '\\s+y\\s+' + NUM + '(\\s+\\(?(?:inclusive|ambos\\s+inclusive|exclusive|excluyente|sin\\s+incluir)\\)?)?'))) || (m = n.match(new RegExp('\\bde(?:sde)?\\s+' + NUM + '\\s+(?:a|hasta)\\s+' + NUM + '(\\s+\\(?(?:inclusive|exclusive|excluyente|sin\\s+incluir)\\)?)?')))) {
            const exc = m[3] && /exclu|sin/.test(m[3]);
            r.min = num(m[1]); r.max = num(m[2]); r.minIncl = !exc; r.maxIncl = !exc;
            nota('columna', o, `Entre ${r.min} y ${r.max} (${exc ? 'exclusive' : 'inclusive'})`);
          }
          if ((m = n.match(new RegExp('(?:como\\s+)?maximo\\s+(?:de\\s+)?' + NUM))) && r.max == null) { r.max = num(m[1]); r.maxIncl = !/exclusive/.test(n); nota('columna', o, 'Máximo ' + r.max); }
          if ((m = n.match(new RegExp('(?:como\\s+)?minimo\\s+(?:de\\s+)?' + NUM))) && r.min == null) { r.min = num(m[1]); r.minIncl = true; nota('columna', o, 'Mínimo ' + r.min); }
          if (/no\s+negativ|\bnegativos?\b.*\binvalid/.test(n) && r.min == null) { r.min = 0; r.minIncl = true; nota('columna', o, 'No negativo (≥ 0)'); }
          if (/\bpositiv/.test(n) && !/no\s+negativ/.test(n) && r.min == null) { r.min = 0; r.minIncl = false; nota('columna', o, 'Positivo (> 0)'); }
        });
      }
      // Vacío: inválido, o «como en el formato viejo» si la regla es por presencia de un valor
      const iv = N.findIndex(n => /presencia\s+de\s+(?:un\s+)?valor|si\s+(?:la\s+columna|el\s+sexto\s+campo|el\s+campo)\s+(?:esta|viene|queda)\s+vaci|vacio\s+(?:equivale|es\s+como|cuenta\s+como)/.test(n));
      if (iv >= 0) { col.vacio = 'defecto'; nota('columna', O[iv], 'Vacío = como en el formato de cinco columnas'); }
      // El valor del formato viejo
      O.forEach((o, i) => {
        const n = N[i];
        if (i >= finReglas || !/formato\s+(?:original|viejo|inicial|anterior|de\s+(?:cinco|5)\s+columnas)|cinco\s+columnas|5\s+columnas/.test(n)) return;
        const vm = mayusculas(C[i]).find(w => col.valores.map(String).includes(w));
        let m;
        if (col.tipo === 'texto' && vm) { col.defecto = vm; nota('columna', o, 'Formato viejo: ' + vm); return; }
        if (col.tipo === 'texto' && (m = n.match(/todos\s+(?:sus\s+|los\s+|esos\s+|estos\s+)?(?:\w+\s+){0,3}?(?:son|tienen|se\s+consideran|cuentan\s+como|van\s+como|quedan\s+como)\s+(.{0,40})/))) {
          const ws = m[1].split(/[^a-zñ]+/).filter(w => w.length > 2);
          const v = col.valores.find(x => { const xn = sinTildes(String(x)).toLowerCase(); return ws.some(w => xn.startsWith(w.slice(0, Math.min(5, w.length))) || w.startsWith(xn.slice(0, Math.min(5, xn.length)))); });
          if (v) { col.defecto = v; nota('columna', o, 'Formato viejo: ' + v); }
        }
        if (col.tipo === 'entero') {
          if ((m = n.match(new RegExp('(?:costo|valor|facturan?|facturacion|de|en|con|tienen?|vale[n]?)\\s+(?:de\\s+|un\\s+|una\\s+)?' + NUM + '(?![\\d_.])(?!\\s*(?:columnas|campos|filas))')))) { col.defecto = num(m[1]); nota('columna', o, 'Formato viejo: ' + col.defecto); }
          else if (/\bsin\s+\w+|\bningun/.test(n) && (col.valores.includes(0) || (col.rango.min != null && col.rango.min <= 0))) { col.defecto = 0; nota('columna', o, 'Formato viejo: 0'); }
        }
      });
      if (col.tipo === 'texto' && !col.defecto) col.defecto = col.valores[0] || '';
      if (col.tipo === 'entero' && typeof col.defecto !== 'number') col.defecto = col.valores.includes(0) || col.vacio === 'defecto' ? 0 : col.rango.min != null && col.rango.minIncl ? col.rango.min : 0;
    }

    // 4) El costo: la columna en lugar de los 2000, extras para todos y las subclases
    O.forEach((o, i) => {
      const n = N[i];
      if (i < finReglas && col && col.tipo === 'entero' && /(reemplaza|en\s+lugar\s+de|en\s+vez\s+de|toma(?:r)?\s+el\s+valor|tome\s+el\s+valor|usar?\s+(?:el|ese|su)\s+valor|considerad[oa]s?\s+al\s+realizar\s+el\s+calculo|se\s+usa(?:n)?\s+(?:en|para)\s+el\s+(?:calculo|costo)|base\s+del\s+costo)/.test(n)
        && /costo|calculo|2\.?000|facturacion/.test(n)) {
        cfg.baseDesdeColumna = true; nota('costo', o, 'El costo usa ' + col.nombre + ' en lugar de los 2000 USD');
      }
    });
    if (col && col.tipo === 'entero' && cfg.baseDesdeColumna && col.defecto === 0 && !col.valores.includes(0)) col.defecto = FACTURACION;
    const sujetos = [];
    if (col && col.tipo === 'texto') for (const v of col.valores) sujetos.push({ cuando: { campo: 'columna', op: 'igual', valor: v }, palabra: v });
    for (const e of cfg.estados) sujetos.push({ cuando: { campo: 'estado', op: 'igual', valor: e }, palabra: e });
    const sujetoPorTexto = (n, c) => {
      for (const w of mayusculas(c.replace(/[A-Z][A-Z0-9_]+\s+(?:solo|unicamente)\s+admi?n?ten?\s+[A-Z0-9_ ,]+/g, ' '))) { const s = sujetos.find(x => x.palabra === w); if (s) return s; }
      if (col && col.tipo === 'entero' && /asegurad|con\s+cobertura|plazos?\s+de|mayor\s+a\s+0|distint[oa]\s+de\s+0|valor\s+positivo/.test(n)) return { cuando: { campo: 'columna', op: 'mayor', valor: 0 } };
      if (col && col.vacio === 'defecto' && /presencia\s+de|con\s+(?:un\s+)?valor\s+en/.test(n)) return { cuando: { campo: 'columna', op: 'presente', valor: '' } };
      return null;
    };
    let contexto = null;   // «Para vehículos REFRIGERADA:» y las viñetas que siguen
    O.forEach((o, i) => {
      const n = N[i];
      if (i >= finReglas) return;
      if (/:\s*$/.test(o) || /^para\s/.test(n)) contexto = sujetoPorTexto(n, C[i]);
      if (esEjemplo(i)) return;
      const ops = opsDe(n, col), topes = topesDe(n, col);
      if (!ops.length && !topes.length) return;
      let s = sujetoPorTexto(n, C[i]);
      if (!s && i > 0 && col && col.tipo === 'entero' && /asegurad|cobertura|plazos?\s+de/.test(N[i - 1])) s = { cuando: { campo: 'columna', op: 'mayor', valor: 0 } };
      if (!s && contexto && !/todos|cada\s+vehiculo|el\s+costo\s+de\s+(?:todos|cada)/.test(n)) s = contexto;
      if (s && s.palabra && /conserva\s+(?:todas\s+)?las\s+reglas|conserva\s+el\s+comportamiento/.test(n) && !ops.length && !topes.length) return;
      if (!s) {
        if (ops.length && !topes.length && (/todos|cada\s+vehiculo|el\s+costo\s+de\s+(?:todos|cada)|el\s+costo\s+(?:se\s+calcula|pasa|queda)/.test(n) || ops.some(x => x.op === 'sumaPorCada'))) {
          for (const x of ops) cfg.extras.push(x);
          nota('costo', o, 'Para todos: ' + ops.map(x => describirOp(x, cfg)).join(', '));
        } else if (!/^\d/.test(n)) avisos.push('No supe a quién se aplica: «' + o + '» (cargalo a mano si hace falta).');
        return;
      }
      let e = cfg.especiales.find(x => x.cuando.campo === s.cuando.campo && x.cuando.op === s.cuando.op && String(x.cuando.valor) === String(s.cuando.valor));
      if (!e) {
        const clase = s.cuando.op === 'igual' ? 'Vehiculo' + pascal(String(s.cuando.valor)) : 'VehiculoCon' + cap(col.nombre);
        e = { cuando: s.cuando, ops: [], topes: [], clase, etiqueta: '' };
        cfg.especiales.push(e);
      }
      for (const x of ops) if (!e.ops.some(y => y.op === x.op && y.n === x.n)) e.ops.push(x);
      for (const t of topes) if (!e.topes.some(y => y.campo === t.campo && y.op === t.op)) e.topes.push(t);
      nota('especiales', o, e.clase + ': ' + describirEspecial(e, cfg));
    });

    // 5) El conteo y los totales
    const etiquetas = (() => { const m = (texto || '').match(/cantidades\s+([A-Z][A-Z0-9_]*(?:\s*\/\s*[A-Z][A-Z0-9_]*)+)/); return m ? m[1].split('/').map(x => x.trim()) : null; })();
    O.forEach((o, i) => {
      if (cfg.conteo) return;
      const n = N[i];
      const m = n.match(/(?:conteo|cantidad(?:es)?|agrupamiento|cuente\s+(?:\w+\s+)?|contar\s+(?:\w+\s+)?|contabilizar\s+(?:\w+\s+)?)\s*(?:de\s+\w+\s+)?(?:por|en\s+cada|segun)\s+(?:el\s+|la\s+)?(?:tipo\s+de\s+)?(\w+)/);
      if (!m) return;
      const w = m[1];
      const deCol = col && (sinTildes(col.nombre).toLowerCase().startsWith(w.slice(0, 5)) || partesNombre(col.nombre).some(p => p.startsWith(w.slice(0, 5))));
      if (/^estado/.test(w)) cfg.conteo = 'estado';
      else if (/^(zona|region)/.test(w)) cfg.conteo = 'zona';
      else if (deCol && col.tipo === 'texto') cfg.conteo = 'columna';
      else if (deCol && !cfg.especiales.length) cfg.conteo = 'columna';
      else if (cfg.especiales.length && (/^(tipo|clase|modalidad|categoria|cobertura)/.test(w) || deCol)) cfg.conteo = col && col.tipo === 'texto' && !(etiquetas && etiquetas.some(x => !col.valores.includes(x))) ? 'columna' : 'tipo';
      else if (col && col.tipo === 'texto') cfg.conteo = 'columna';
      else if (cfg.especiales.length) cfg.conteo = 'tipo';
      if (cfg.conteo) nota('conteo', o, 'Conteo por ' + (cfg.conteo === 'columna' ? col.nombre : cfg.conteo));
    });
    if (etiquetas) {
      if (!cfg.conteo) {
        if (etiquetas.every(x => cfg.estados.includes(x))) cfg.conteo = 'estado';
        else if (col && col.tipo === 'texto' && etiquetas.every(x => col.valores.includes(x))) cfg.conteo = 'columna';
        else if (cfg.especiales.length) cfg.conteo = 'tipo';
      }
      if (cfg.conteo === 'tipo') {
        cfg.etiquetaBase = etiquetas[0];
        cfg.especiales.forEach((e, k) => { e.etiqueta = etiquetas[k + 1] || etiquetas[etiquetas.length - 1]; });
        nota('conteo', 'cantidades ' + etiquetas.join('/'), 'Nombres del conteo: ' + etiquetas.join(' y '));
      }
    }
    O.forEach((o, i) => {
      const re = /\btotal(?:es)?\s+(?:de\s+(?:costo\s+de\s+)?)?(?:(?:los|las)\s+)?(?:vehiculos\s+|camiones\s+|fletes\s+)?(?:en\s+estado\s+|con\s+estado\s+)?([A-Z][A-Z0-9_]+)\b/g;
      let m;
      while ((m = re.exec(C[i]))) {
        const w = m[1];
        if (PALABRAS_NO.has(w) || cfg.totales.some(t => t.valor === w)) continue;
        if (cfg.estados.includes(w)) { cfg.totales.push({ campo: 'estado', valor: w }); nota('totales', o, 'Total de los ' + w); }
        else if (col && col.valores.map(String).includes(w)) { cfg.totales.push({ campo: 'columna', valor: w }); nota('totales', o, 'Total de los ' + w); }
      }
    });

    // 6) El archivo del main
    const arch = (texto || '').match(/\b(datos[\w-]*\.csv)\b/g);
    if (arch) { const a = arch.find(x => x !== 'datos.csv'); if (a) cfg.archivo = a; }

    normalizar(cfg);
    if (!col && !cfg.especiales.length && !cfg.extras.length && cfg.descartes.length === 1 && cfg.estados.length === 2) avisos.push('No encontré reglas nuevas. ¿Es un enunciado del parcial? Podés cargarlas a mano.');
    for (const a of revisar(cfg)) avisos.push(a);
    const v = afectaFormatoViejo(cfg); if (v) avisos.push(v);
    return { cfg, evidencias: ev, avisos };
  }

  function opsDe(n, col) {
    const ops = []; let m;
    const unidadCol = w => UNIDADES_CADA.test(w) || (col && partesNombre(col.nombre).concat(sinTildes(col.nombre).toLowerCase()).some(p => p.slice(0, 4) === w.slice(0, 4)));
    if ((m = n.match(new RegExp('(?:prima|recargo|suma|agrega|cuesta|cobra|adicional)\\D{0,30}?' + NUM + '\\s*(?:usd|dolares?|pesos|centavos|u\\$s|\\$)?\\s+(?:adicionales\\s+|mas\\s+|extra\\s+)?por\\s+cada\\s+' + NUM)))) ops.push({ op: 'sumaPorCada', n: num(m[1]), cada: num(m[2]) });
    else if ((m = n.match(new RegExp('(?:prima|recargo|suma|agrega|cuesta|cobra|adicional)\\D{0,30}?' + NUM + '\\s*(?:usd|dolares?|pesos|centavos|u\\$s|\\$)?\\s+(?:adicionales\\s+|mas\\s+|extra\\s+)?(?:por\\s+cada|por|cada)\\s+(?:un[oa]?\\s+)?(?:de\\s+)?(?:los\\s+|las\\s+)?([a-z]+)'))) && unidadCol(m[2])) ops.push({ op: 'sumaPorCada', n: num(m[1]), cada: 1 });
    else if ((m = n.match(new RegExp(NUM + '\\s*(?:usd|dolares?|pesos|u\\$s|\\$)\\s+(?:adicionales|mas|de\\s+recargo|extra|por\\s+(?:vehiculo|viaje|flete|fila))'))) || (m = n.match(new RegExp('(?:recargo|adicional|suma|agrega|cuesta)\\s+(?:fijo\\s+)?(?:de\\s+)?' + NUM + '\\s*(?:usd|dolares?|pesos|u\\$s|\\$)')))) ops.push({ op: 'suma', n: num(m[1]) });
    if ((m = n.match(new RegExp(NUM + '\\s*(?:%|por\\s*ciento)\\s*(?:mas|adicional|de\\s+recargo|extra|de\\s+aumento|sobre)'))) || (m = n.match(new RegExp('(?:recargo|aumento|incremento)\\s+del?\\s+' + NUM + '\\s*(?:%|por\\s*ciento)')))) ops.push({ op: 'porcentaje', n: num(m[1]) });
    else if ((m = n.match(new RegExp(NUM + '\\s*(?:%|por\\s*ciento)\\s*(?:menos|de\\s+descuento|de\\s+bonificacion)'))) || (m = n.match(new RegExp('(?:descuento|bonificacion)\\s+del?\\s+' + NUM + '\\s*(?:%|por\\s*ciento)')))) ops.push({ op: 'porcentaje', n: -num(m[1]) });
    if (/\bel\s+doble\b|\bduplica/.test(n)) ops.push({ op: 'multiplica', n: 2 });
    else if (/\bel\s+triple\b|\btriplica/.test(n)) ops.push({ op: 'multiplica', n: 3 });
    return ops;
  }
  function topesDe(n, col) {
    const ts = []; let m;
    const U = '\\s*([a-z/]+(?:\\s+[a-z]+)?)?';
    const re = [
      [new RegExp('como\\s+maximo\\s+(?:de\\s+)?' + NUM + U), 'max', true],
      [new RegExp('no\\s+puede[n]?\\s+(?:llevar|superar|tener|pasar(?:\\s+de)?|exceder)\\s+(?:mas\\s+de\\s+|los\\s+|las\\s+)?' + NUM + U), 'max', true],
      [new RegExp('(?:hasta|maximo\\s+de)\\s+' + NUM + U + '(?:\\s+inclusive)?'), 'max', true],
      [new RegExp('como\\s+minimo\\s+(?:de\\s+)?' + NUM + U), 'min', true],
      [new RegExp('(?:velocidad|carga|indice)\\w*\\s+(?:\\w+\\s+){0,2}(?:menor|inferior)(?:es)?\\s+a\\s+' + NUM + U), 'max', false],
      [new RegExp('(?:velocidad|carga|indice)\\w*\\s+(?:\\w+\\s+){0,2}(?:mayor|superior)(?:es)?\\s+a\\s+' + NUM + U), 'min', false],
      [new RegExp('(?:velocidad|carga|indice)\\w*\\s+(?:\\w+\\s+){0,2}(?:supere[n]?|supera[n]?)\\s+(?:los\\s+|las\\s+)?' + NUM + U), 'min', false],
      [new RegExp('(?:velocidad|carga|indice)\\w*\\s+(?:\\w+\\s+){0,2}(?:de\\s+)?al\\s+menos\\s+' + NUM + U), 'min', true],
    ];
    for (const [r, op, incl] of re) {
      if (!(m = n.match(r))) continue;
      const unidad = m[2] || '';
      const zona = n.slice(Math.max(0, m.index - 50), m.index + m[0].length + 5);
      let campo = campoPorPalabras(unidad) || campoPorPalabras(zona);
      if (!campo && col && (n.includes(sinTildes(col.nombre).toLowerCase()) || partesNombre(col.nombre).some(p => zona.includes(p)))) campo = 'columna';
      if (!campo) continue;   // un número suelto (por ejemplo «hasta 30 días») no es un tope
      const cola = n.slice(m.index, m.index + m[0].length + 25);
      const exc = /exclusive|excluyente|sin\s+incluir/.test(cola);
      const inc = /inclusive/.test(cola);
      if (!ts.some(t => t.campo === campo && t.op === op)) ts.push({ campo, op, n: num(m[1]), incl: inc ? true : exc ? false : incl });
    }
    return ts;
  }
  function columnaNumerica(csvTexto, cfg) {
    const ls = lineas(csvTexto).slice(1, 80), sep = cfg.separador;
    const vs = ls.map(l => l.split(sep)).filter(c => c.length === 6).map(c => trim(c[5])).filter(Boolean);
    return vs.length > 3 && vs.filter(v => /^[+-]?\d+$/.test(v)).length >= vs.length * 0.7;
  }

  // ───────────────────────── Un CSV de prueba ─────────────────────────
  /* 140 filas con el encabezado nuevo (o el original si no hay columna): válidas de todos los tipos y una o más
     inválidas por cada regla, mezcladas con una semilla fija (con la misma semilla sale siempre el mismo) */
  function csvDePrueba(cfg, semilla = 7, total = 140) {
    let x = semilla >>> 0 || 1;
    const azar = () => { x = (Math.imul(x, 1664525) + 1013904223) >>> 0; return x / 4294967296; };
    const elegir = a => a[Math.floor(azar() * a.length)];
    const col = cfg.columna, sep = col ? cfg.separador : ',', zonas = ['NORTE', 'CENTRO', 'SUR'];
    let k = 0;
    const pat = () => 'trk-' + String(++k).padStart(4, '0');
    let vs = [null];
    if (col) {
      if (col.valores.length) vs = col.valores.slice();
      else if (col.tipo === 'entero') {
        const r = col.rango, lo = r.min != null ? r.min + (r.minIncl ? 0 : 1) : 0, hi = r.max != null ? r.max - (r.maxIncl ? 0 : 1) : lo + 1000;
        vs = [...new Set([lo, hi, Math.round((lo + hi) / 2), lo + Math.round((hi - lo) / 3)])];
      } else vs = ['A'];
    }
    const fila = (vel, carga, estado, c) => [pat(), elegir(zonas), vel, carga, estado].concat(col ? [c] : []).join(sep);
    const fila5 = (vel, carga, estado) => [pat(), elegir(zonas), vel, carga, estado].join(sep);
    const filas = [];
    const nValidas = total;
    for (let i = 0; i < nValidas; i++) {
      const vel = 40 + Math.floor(azar() * 75), carga = 3 + Math.floor(azar() * 40);
      let est = elegir(cfg.estados), c = elegir(vs);
      const esp = cfg.especiales.length ? cfg.especiales[i % cfg.especiales.length] : null;
      if (esp && i % 2 === 0) {   // que haya de cada subclase
        if (esp.cuando.campo === 'columna' && esp.cuando.op === 'igual') c = esp.cuando.valor;
        if (esp.cuando.op === 'mayor') c = vs.find(v => Number(v) > Number(esp.cuando.valor)) ?? c;
        if (esp.cuando.campo === 'estado') est = esp.cuando.valor;
      }
      const r = cfg.restricciones.find(q => q.estado === est);
      if (r && !r.valores.map(String).includes(String(c))) c = r.valores[0];
      if (col && col.vacio === 'defecto' && i % 7 === 3) c = '';
      filas.push(i % 9 === 4 && col ? fila(vel, carga, est, ' ' + c + ' ') : fila(vel, carga, est, c));
    }
    const cv = elegir(vs);
    const malas = [];
    for (const d of cfg.descartes) for (let i = 0; i < 4; i++) malas.push([pat(), elegir(zonas), i % 2 ? 'abc' : 999, -5, i === 3 ? ' ' + d + ' ' : d].concat(col ? ['?'] : []).join(sep));
    malas.push(fila(0, 10, 'EN_RUTA', cv), fila(130, 10, 'EN_RUTA', cv), fila(129, 10, 'DEMORADO', cv), fila(60, 46, 'DEMORADO', cv), fila(60, 45, 'EN_RUTA', cv),
      fila(60, 10, 'PERDIDO', cv), fila('6x', 10, 'EN_RUTA', cv), fila(60, '', 'EN_RUTA', cv), fila(60, 10, 'en_ruta', cv));
    malas.push([pat(), '', 60, 10, 'EN_RUTA'].concat(col ? [cv] : []).join(sep), ['', 'SUR', 60, 10, 'EN_RUTA'].concat(col ? [cv] : []).join(sep), [pat(), 'NORTE', 60, 10].join(sep), '');
    malas.push(fila(121, 45, 'EN_RUTA', cv), fila(10, -5, 'EN_RUTA', cv), fila(1, -10, 'EN_RUTA', cv));   // índice 90 (vale), carga negativa (vale) e índice 0 (no)
    if (col) {
      malas.push(fila5(60, 10, 'EN_RUTA'), fila(60, 10, 'EN_RUTA', cv) + sep + 'extra');   // ancho viejo y de más bajo la cabecera nueva
      malas.push(fila(60, 10, 'EN_RUTA', ''));
      if (col.tipo === 'texto') malas.push(fila(60, 10, 'EN_RUTA', 'OTRO'), fila(60, 10, 'EN_RUTA', String(col.valores[0] || 'x').toLowerCase()), fila(60, 10, 'DEMORADO', ' ' + (col.valores[1] || col.valores[0] || 'X') + ' '));
      else {
        const r = col.rango;
        malas.push(fila(60, 10, 'EN_RUTA', 'diez'), fila(60, 10, 'EN_RUTA', '1.5'));
        if (r.min != null) malas.push(fila(60, 10, 'EN_RUTA', r.min), fila(60, 10, 'DEMORADO', r.min - 1));
        if (r.max != null) malas.push(fila(60, 10, 'EN_RUTA', r.max), fila(60, 10, 'DEMORADO', r.max + 1));
        if (col.valores.length) malas.push(fila(60, 10, 'EN_RUTA', Math.max(...col.valores.map(Number)) + 1), fila(60, 10, 'EN_RUTA', Math.min(...col.valores.map(Number)) - 1));
      }
      for (const r of cfg.restricciones) { const otro = vs.find(v => !r.valores.map(String).includes(String(v))); if (otro != null) malas.push(fila(60, 10, r.estado, otro)); }
    }
    for (const e of cfg.especiales) {
      const c = e.cuando.campo === 'columna' ? (e.cuando.op === 'igual' ? e.cuando.valor : e.cuando.op === 'mayor' ? (vs.find(v => Number(v) > Number(e.cuando.valor)) ?? cv) : vs[0]) : cv;
      const est = e.cuando.campo === 'estado' ? e.cuando.valor : 'EN_RUTA';
      for (const t of e.topes) {
        const lim = t.n, dentro = t.op === 'min' ? (t.incl ? lim : lim + 1) : (t.incl ? lim : lim - 1), fuera = t.op === 'min' ? dentro - 1 : dentro + 1;
        if (t.campo === 'carga') malas.push(fila(60, dentro, est, c), fila(60, fuera, est, c));
        if (t.campo === 'velocidad') malas.push(fila(dentro, 10, est, c), fila(fuera, 10, est, c));
        if (t.campo === 'columna') malas.push(fila(60, 10, est, dentro), fila(60, 10, est, fuera));
      }
    }
    const todas = filas.slice(0, Math.max(0, total - malas.length)).concat(malas);
    for (let i = todas.length - 1; i > 0; i--) { const r = Math.floor(azar() * (i + 1)); [todas[i], todas[r]] = [todas[r], todas[i]]; }
    return [col ? encabezadoNuevo(cfg) : ENCABEZADO].concat(todas).join('\n') + '\n';
  }

  return {
    CAMPOS, ENCABEZADO, ESTADOS_BASE, DESCARTES_BASE, FACTURACION, configBase, simular, generar, leerEnunciado, revisar, normalizar,
    csvDePrueba, describirEspecial, describirOp, afectaFormatoViejo, encabezadoNuevo, textoRango, hayCambios, etiquetaBase, signoTope, oraciones,
  };
}));
