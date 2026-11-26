/* La guía de un parcial cualquiera: cruza el enunciado del parcial (y su CSV, si está) con el código del preenunciado
   y arma los pasos, cada uno con los lugares exactos (archivo y línea), lo que dice el enunciado y, cuando se puede,
   el código para pegar con los nombres del proyecto. Señala qué cambiar y dónde: no escribe la solución.
   Todo sale del enunciado, del código y de los datos; nunca de los tests.
   Uso: Guia.armar({ fuentes: {ruta: código} }, textoDelEnunciado, csvDelParcial) → { pasos: [...], codigo, encabezadoNuevo } */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica();
  else raiz.Guia = fabrica();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const sinTildes = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '');
  const bajo = s => sinTildes(s).toLowerCase();
  const nombreDe = r => r.split('/').pop();
  const escRe = s => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const pascal = s => String(s).toLowerCase().split(/[_\s]+/).filter(Boolean).map(w => w[0].toUpperCase() + w.slice(1)).join('');
  const capital = s => s[0].toUpperCase() + s.slice(1);
  const camel = s => s.replace(/_(\w)/g, (_, x) => x.toUpperCase());
  const sepDe = h => h.includes(';') ? ';' : h.includes('|') ? '|' : ',';
  const esEncabezado = v => /^[A-Za-z_]\w*([,;|])[A-Za-z_]\w*(?:\1[A-Za-z_]\w*){2,}$/.test(v);
  const comentario = l => /^\s*(\/\/|\*|\/\*)/.test(l);
  const NO_VALOR = new Set('CSV USD ARS ID ZIP MD JDK UTF IDE API IT OK PDF JSON SQL NULL DECISIONES'.split(' '));
  const JAVA = new Set('String Integer Double Long Boolean Character Math List ArrayList Map HashMap TreeMap LinkedHashMap Set HashSet TreeSet Path Paths Files Stream Collectors Optional Objects Arrays IllegalArgumentException NumberFormatException IOException RuntimeException Exception BufferedReader Scanner StringBuilder JUnit Junit System Main App DECISIONES'.split(' '));
  const PARA = /[Pp]ara\s+(?:las\s+)?(?:filas|solicitudes|registros)\s+(?:con\s+(?:el|los)\s+estados?\s+)?([A-Z][A-Z0-9_]+(?:(?:\s*,\s*|\s+[yo]\s+)[A-Z][A-Z0-9_]+)*)/;

  // ───────── Lo que hay en el código ─────────
  function analizarCodigo(fuentes) {
    const L = [];
    for (const [r, t] of Object.entries(fuentes)) t.split('\n').forEach((x, i) => L.push({ archivo: r, n: i + 1, texto: x }));
    const siguientes = (l, k) => { const i = L.findIndex(x => x.archivo === l.archivo && x.n === l.n); return L.slice(i, i + k).filter(x => x.archivo === l.archivo); };
    const clases = new Set(Object.keys(fuentes).map(r => nombreDe(r).replace(/\.java$/, '')));
    const archivoDe = c => Object.keys(fuentes).find(r => nombreDe(r) === c + '.java') || null;

    // el encabezado que acepta hoy (un literal con forma de encabezado CSV) y, si es una constante, dónde se usa
    let enc = null;
    for (const l of L) { if (comentario(l.texto)) continue; const m = [...l.texto.matchAll(/"([^"\n]+)"/g)].find(m => esEncabezado(m[1])); if (m) { enc = { ...l, valor: m[1] }; break; } }
    const sep = enc ? sepDe(enc.valor) : ',';
    const viejos = enc ? enc.valor.split(sep) : [];
    const ancho = enc ? viejos.length : null;
    let usosEnc = [];
    if (enc) { const k = enc.texto.match(/(\w+)\s*=\s*"/); if (k && /\bfinal\b|\bstatic\b/.test(enc.texto)) usosEnc = L.filter(l => l !== enc && !comentario(l.texto) && new RegExp('\\b' + k[1] + '\\b').test(l.texto)); }
    const mensajeEnc = enc ? [enc, ...usosEnc].map(l => siguientes(l, 5).map(x => (x.texto.match(/Exception\(\s*"([^"]*)"/) || [])[1]).find(Boolean)).find(Boolean) || null : null;

    // los controles de ancho (campos.length != 8, o con una constante que vale 8)
    let controlesAncho = [];
    if (ancho) {
      const ks = L.map(l => (l.texto.match(new RegExp('static\\s+final\\s+int\\s+(\\w+)\\s*=\\s*' + ancho + '\\s*;')) || [])[1]).filter(Boolean);
      const v = [String(ancho), ...ks].join('|');
      const re = new RegExp(`\\.length\\s*(?:!=|==|<=?|>=?)\\s*(?:${v})\\b|\\b(?:${v})\\s*(?:!=|==)\\s*[\\w.]+\\.length`);
      controlesAncho = L.filter(l => !comentario(l.texto) && re.test(l.texto));
    }

    // estados: literales en mayúsculas que se comparan, y las constantes de los enum
    const estados = [];
    for (const l of L) {
      if (comentario(l.texto) || !/equals|contains|case\s|Set\.of|List\.of|asList|==|switch/.test(l.texto)) continue;
      for (const m of l.texto.matchAll(/"([A-Z][A-Z0-9_]{1,})"/g)) estados.push({ ...l, valor: m[1] });
      for (const m of l.texto.matchAll(/equalsIgnoreCase\(\s*"([A-Za-z][A-Za-z0-9_]{1,})"\s*\)/g)) if (!/^[A-Z0-9_]+$/.test(m[1])) estados.push({ ...l, valor: m[1].toUpperCase() });
    }
    for (const [r, t] of Object.entries(fuentes)) for (const m of t.matchAll(/\benum\s+(\w+)\s*\{([^}]*)\}/g)) {
      const n = t.slice(0, m.index).split('\n').length;
      for (const v of m[2].split(';')[0].split(',')) { const x = v.trim().split(/[\s(]/)[0]; if (/^[A-Z][A-Z0-9_]+$/.test(x)) estados.push({ archivo: r, n, texto: t.split('\n')[n - 1], valor: x, enumDe: m[1] }); }
    }
    const descartes = estados.filter(e => siguientes(e, 4).some(x => /\bcontinue\b|descart/i.test(x.texto)));

    // la fábrica: un método static que recibe String[] (no el main); si no hay, el «new Entidad(» del parser
    let fabrica = null, entidad = null;
    for (const l of L) {
      const m = l.texto.match(/static\s+(?!void\b)(\w+)(?:<[^>]*>)?\s+(\w+)\s*\(\s*(?:final\s+)?String\s*\[\s*\]\s*\w+\s*\)/);
      if (m && clases.has(m[1]) && !/Resultado|Parser|Lector/.test(m[1])) { fabrica = { ...l, metodo: m[2] }; entidad = m[1]; break; }
    }
    if (!entidad && enc) {
      const c = L.filter(l => l.archivo === enc.archivo && /new\s+([A-Z]\w*)\s*\(/.test(l.texto)).map(l => ({ ...l, clase: l.texto.match(/new\s+([A-Z]\w*)\s*\(/)[1] }))
        .find(x => clases.has(x.clase) && !/Resultado|Error|Exception|Parser|Lector|Reader/.test(x.clase));
      if (c) { fabrica = { ...c, metodo: null }; entidad = c.clase; }
    }
    const archivoEntidad = entidad ? archivoDe(entidad) : null;
    const tEnt = archivoEntidad ? fuentes[archivoEntidad] : '';
    const esRecord = !!entidad && new RegExp('\\brecord\\s+' + entidad + '\\s*\\(').test(tEnt);
    // su constructor (o los componentes del record)
    let ctor = null;
    if (archivoEntidad) {
      const m = esRecord ? tEnt.match(new RegExp('\\brecord\\s+' + entidad + '\\s*\\(([^)]*)\\)')) : tEnt.match(new RegExp('(?:^|\\n)[ \\t]*(?:public|protected|private)?[ \\t]*' + entidad + '\\s*\\(([^)]*)\\)\\s*(?:throws[^{]*)?\\{'));
      if (m) ctor = { n: tEnt.slice(0, m.index).split('\n').length + (m[0].startsWith('\n') ? 1 : 0), params: m[1].split(',').map(x => x.trim()).filter(Boolean).map(x => { const ps = x.replace(/\bfinal\s+/, '').replace(/@\w+\s*/g, '').split(/\s+/); return { tipo: ps.slice(0, -1).join(' '), nombre: ps[ps.length - 1] }; }) };
    }
    // sus métodos sin parámetros: los getters y los que hacen una cuenta
    const metodos = [];
    if (archivoEntidad) {
      const ls = tEnt.split('\n');
      ls.forEach((x, i) => {
        const m = x.match(/^\s*(?:public|protected)\s+(?:final\s+)?([\w<>]+)\s+(\w+)\s*\(\s*\)\s*\{/);
        if (!m || comentario(x)) return;
        let cuerpo = '', prof = 0;
        for (let j = i; j < ls.length; j++) { cuerpo += ls[j] + '\n'; prof += (ls[j].match(/\{/g) || []).length - (ls[j].match(/\}/g) || []).length; if (prof <= 0) break; }
        const adentro = cuerpo.slice(cuerpo.indexOf('{') + 1, cuerpo.lastIndexOf('}'));
        const simple = /^\s*return\s+(?:this\.)?\w+\s*;\s*$/.test(adentro);
        metodos.push({ archivo: archivoEntidad, n: i + 1, texto: x, tipo: m[1], nombre: m[2], simple, cuenta: !simple && /^(int|long|double|float|BigDecimal)$/.test(m[1]) && /[*+\/-]|Math\.|\w+\(\)/.test(adentro) });
      });
    }
    const calculos = metodos.filter(m => m.cuenta);
    const getter = campo => { const k = capital(camel(campo)); const g = metodos.find(m => m.nombre === 'get' + k || m.nombre === 'is' + k || m.nombre === camel(campo)); return g ? g.nombre : null; };
    // el colector: la clase que guarda una List<Entidad>
    let colector = null;
    if (entidad) {
      const re = new RegExp('(?:List|Collection|ArrayList|Set)<\\s*' + entidad + '\\s*>\\s+(\\w+)\\s*[;=]');
      const l = L.find(l => l.archivo !== archivoEntidad && (!enc || l.archivo !== enc.archivo) && /\bprivate\b|\bfinal\b/.test(l.texto) && re.test(l.texto) && !/Resultado|Parser|Main|App/.test(nombreDe(l.archivo)));
      if (l) colector = { ...l, clase: nombreDe(l.archivo).replace(/\.java$/, ''), campo: l.texto.match(re)[1] };
    }
    // el main y su CSV por defecto
    const main = L.find(l => /static\s+void\s+main\s*\(/.test(l.texto)) || null;
    const csvMain = main ? L.find(l => l.archivo === main.archivo && /"[^"]*\.(?:csv|txt)"/.test(l.texto)) || null : null;
    const paquete = archivoEntidad ? (tEnt.match(/^\s*package\s+([\w.]+)\s*;/m) || [])[1] : main ? (fuentes[main.archivo].match(/^\s*package\s+([\w.]+)\s*;/m) || [])[1] : null;
    return { enc, usosEnc, sep, viejos, ancho, mensajeEnc, controlesAncho, estados, descartes, fabrica, entidad, archivoEntidad, esRecord, ctor, metodos, calculos, getter, colector, main, csvMain, paquete, clases };
  }

  // ───────── El texto del enunciado: párrafos y oraciones ─────────
  function limpiar(texto) {
    let t = String(texto).replace(/\r/g, '').replace(/```[a-z]*\n?/g, '\n').replace(/`([^`\n]+)`/g, '$1').replace(/\*\*([^*\n]+)\*\*/g, '$1').replace(/(^|[^\w*])\*([^*\n]+)\*(?![\w*])/g, '$1$2');
    t = t.replace(/[ \t]+([.,;:)])/g, '$1').replace(/\([ \t]+/g, '(');
    // pies de página de los PDF y números de página sueltos
    return t.split('\n').filter(l => !/^\s*\d{1,3}\s*$/.test(l) && !/·.*\b\d+\s*\/\s*\d+\s*$/.test(l) && !/^\s*[\w-]+\.md\s+\d{4}-\d\d-\d\d\s*$/.test(l)).join('\n');
  }
  function parrafos(texto) {
    const ls = limpiar(texto).split('\n'), pars = [];
    let par = [];
    const cerrar = () => { if (par.length) pars.push(par.join(' ').replace(/\s+/g, ' ').trim()); par = []; };
    const titulo = l => l.length <= 45 && /^[A-ZÁÉÍÓÚ]/.test(l) && !/[.:;,]$/.test(l) && l.split(' ').length <= 6;
    for (let i = 0; i < ls.length; i++) {
      const l = ls[i].trim();
      if (!l) {
        const ant = par[par.length - 1] || '', sig = (ls.slice(i + 1).find(x => x.trim()) || '').trim();
        const esLista = par.length && /^(?:\d{1,2}[.)]|[-•*])\s+/.test(par[0]);
        if (!ant || /[.;!?]$/.test(ant) || (esLista && /^[A-ZÁÉÍÓÚ¿]/.test(sig))) cerrar();
        continue;
      }
      if (!pars.length && !par.length) { pars.push(l); continue; }   // la primera línea: el título
      if (/^#{1,6}\s/.test(l)) { cerrar(); pars.push(l.replace(/^#+\s*/, '')); continue; }
      if (/^(?:\d{1,2}[.)]|[-•*])\s+/.test(l)) { cerrar(); par.push(l); continue; }
      if (par.length && /^(?:\d{1,2}[.)]|[-•*])\s+/.test(par[0]) && /[.!?]$/.test(par[par.length - 1]) && /^[A-ZÁÉÍÓÚ¿]/.test(l)) cerrar();   // el ítem terminó
      if (!par.length && titulo(l)) { const sig = (ls[i + 1] || '').trim(); if (!sig || /^[A-ZÁÉÍÓÚ0-9]/.test(sig)) { pars.push(l); continue; } }
      par.push(l);
    }
    cerrar();
    return pars;
  }
  function oraciones(pars) {
    const os = [];
    pars.forEach((p, k) => { const lista = /^\d{1,2}[.)]\s+/.test(p); p.replace(/^(?:\d{1,2}[.)]|[-•*])\s+/, '').split(/(?<=[^\s.]{2}[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿"«(]|\d[\d_.,]*\s+[a-záéíóú])/).forEach(t => os.push({ t: t.trim(), p: k, lista })); });
    return os.filter(o => o.t);
  }
  const corta = t => t.length > 280 ? t.slice(0, 270).replace(/\s+\S*$/, '') + '…' : t;
  const mayus = t => (t.match(/\b[A-Z][A-Z0-9_]{1,}\b/g) || []).filter(w => !NO_VALOR.has(w) && !/^\d/.test(w));

  // ───────── Rangos y valores ─────────
  const num = s => Number(String(s).replace(/[._](?=\d{3}\b)/g, '').replace(',', '.'));
  function rango(t) {
    const n = bajo(t), r = {}, N = '(\\d[\\d._]*(?:,\\d+)?)';
    let m;
    if ((m = n.match(new RegExp('entre\\s+' + N + '\\s+y\\s+' + N)))) { r.min = num(m[1]); r.max = num(m[2]); }
    if ((m = n.match(new RegExp('mayor(?:es)?\\s+(?:o\\s+)?igual(?:es)?\\s+(?:a|que)\\s+' + N)))) r.min = num(m[1]);
    else if ((m = n.match(new RegExp('mayor(?:es)?\\s+(?:a|que)\\s+' + N)))) r.minEx = num(m[1]);
    if ((m = n.match(new RegExp('menor(?:es)?\\s+(?:o\\s+)?igual(?:es)?\\s+(?:a|que)\\s+' + N)))) r.max = num(m[1]);
    else if ((m = n.match(new RegExp('menor(?:es)?\\s+(?:a|que)\\s+' + N)))) r.maxEx = num(m[1]);
    if (r.min == null && (m = n.match(new RegExp('como\\s+minimo\\s+' + N)))) r.min = num(m[1]);
    if (/no\s+negativ/.test(n) && r.min == null) r.min = 0;
    return Object.keys(r).length ? r : null;
  }
  const condicionFuera = (v, r) => [r.min != null && `${v} < ${r.min}`, r.minEx != null && `${v} <= ${r.minEx}`, r.max != null && `${v} > ${r.max}`, r.maxEx != null && `${v} >= ${r.maxEx}`].filter(Boolean).join(' || ');
  // los valores de una columna en el CSV del parcial (solo las filas del ancho nuevo)
  function columnaCsv(csv, sep, ancho, i) {
    if (!csv) return null;
    const vs = csv.replace(/\r/g, '').split('\n').slice(1).filter(l => l.trim()).map(l => l.split(sep)).filter(cs => cs.length === ancho).map(cs => cs[i].trim());
    if (!vs.length) return null;
    const lleno = vs.filter(Boolean), cuenta = new Map();
    for (const v of lleno) cuenta.set(v, (cuenta.get(v) || 0) + 1);
    const enteros = lleno.filter(v => /^[+-]?\d+$/.test(v)).length, numeros = lleno.filter(v => /^[+-]?\d+(?:\.\d+)?$/.test(v)).length;
    const frecuentes = [...cuenta].filter(([, k]) => k >= Math.max(2, lleno.length * 0.03)).sort((a, b) => b[1] - a[1]).map(([v]) => v);
    return { total: vs.length, vacios: vs.length - lleno.length, entero: lleno.length > 0 && enteros >= lleno.length * 0.7 && enteros === numeros, numero: lleno.length > 0 && numeros >= lleno.length * 0.7, frecuentes, todos: [...cuenta.keys()], distintos: cuenta.size };
  }
  const ORD = ['', 'primer[oa]?', 'segund[oa]', 'tercer[oa]?', 'cuart[oa]', 'quint[oa]', 'sext[oa]', 's[e]?ptim[oa]', 'octav[oa]', 'noven[oa]', 'decim[oa]', 'undecim[oa]|onceav[oa]|decimo\\s+primer[oa]?', 'duodecim[oa]|doceav[oa]|decimo\\s+segund[oa]', 'decimo\\s*tercer[oa]?|treceav[oa]'];
  function reColumna(col, i) {
    const ps = col.replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/_/g, ' ').toLowerCase().split(/\s+/).filter(Boolean).map(bajo);
    const vs = [escRe(bajo(col))];
    if (ps.length > 1) vs.push(ps.map(escRe).join('\\s+(?:de\\s+(?:la\\s+|los\\s+|las\\s+)?|del\\s+)?'));
    if (i >= 0) { const n = i + 1; vs.push(`(?:${[ORD[n], `${n}\\s*(?:ro|do|to|mo|vo|no|ma|a|o|\\.?º|°)`].filter(Boolean).join('|')})\\s+(?:campo|columna|dato)`, `(?:campo|columna)\\s+(?:n[º°.]?\\s*)?${n}\\b`); }
    return new RegExp('(?:^|[^\\w])(?:' + vs.join('|') + ')(?![\\w])');
  }

  // el bloque «Ejemplo:» tal cual viene, renglón por renglón (hasta el próximo título o un párrafo largo)
  function ejemplos(texto) {
    const ls = limpiar(texto).split('\n'), i = ls.findIndex(l => /^\s*ejemplos?\b/i.test(l));
    if (i < 0) return null;
    const out = [];
    let blanco = false;
    for (const l of ls.slice(i)) {
      const t = l.trim();
      if (!t) { blanco = true; continue; }
      if (out.length && /^(resultado|reglas|pruebas|preparaci|nuevo formato|se evalua|entrega)/i.test(bajo(t))) break;
      if (out.length >= 3 && blanco && t.length > 70) break;
      if (out.length >= 14) break;
      out.push(t); blanco = false;
    }
    return out.join('\n');
  }

  // ───────── La guía ─────────
  function armar(proyecto, texto, csv) {
    const c = analizarCodigo(proyecto.fuentes);
    const pasos = [];
    if (!texto || !String(texto).trim()) return { codigo: c, pasos, columnas: [] };
    const pars = parrafos(texto), os = oraciones(pars), plano = pars.join(' '), planoB = bajo(plano);
    const lugar = l => l && { archivo: l.archivo, linea: l.n, texto: l.texto.trim() };
    const lugares = ls => ls.filter(Boolean).map(lugar).filter((x, i, a) => a.findIndex(y => y.archivo === x.archivo && y.linea === x.linea) === i);
    const parrafoDe = o => os.filter(x => x.p === o.p);
    const E = c.entidad || 'Entidad', e1 = E[0].toLowerCase();
    const metodosTexto = [...new Set((plano.match(/\b([a-z]\w*)\(\)/g) || []).map(x => x.slice(0, -2)))];
    const calc = c.calculos.find(m => metodosTexto.includes(m.nombre)) || c.calculos[0] || null;

    // estados: los del código, los que el enunciado dice que son estados y los que descarta
    const estadosCodigo = new Set(c.estados.map(e => e.valor));
    const estadosTexto = new Set(estadosCodigo);
    for (const o of os) {
      const n = bajo(o.t), m = o.t.match(PARA);
      if (m) m[1].split(/\s*,\s*|\s+[yo]\s+/).forEach(w => estadosTexto.add(w));
      for (const k of o.t.matchAll(/\b(?:filas?|solicitud(?:es)?|registros?)\s+([A-Z][A-Z0-9_]{2,})\b/g)) estadosTexto.add(k[1]);
      if (/descart/.test(n)) for (const k of o.t.matchAll(/descart\w*\s+(?:las?\s+|los?\s+)?(?:filas\s+)?([A-Z][A-Z0-9_]+)/g)) estadosTexto.add(k[1]);
      if (/estado\s+(?:valido|nuevo)|es\s+un\s+estado|son\s+estados|conservan?\s+el\s+comportamiento/.test(n)) (mayus(o.t).length ? mayus(o.t) : mayus(parrafoDe(o)[0].t).slice(0, 1)).forEach(w => estadosTexto.add(w));
    }

    // 1) El encabezado nuevo: el del CSV del parcial, o el que dice el enunciado
    let nuevo = null, sepN = c.sep;
    if (c.enc) {
      const comparte = h => { const fs = h.split(sepDe(h)); return fs.length > c.viejos.length && c.viejos.filter(v => fs.includes(v)).length >= Math.ceil(c.viejos.length * 0.6); };
      const primera = csv ? (csv.replace(/^﻿/, '').split(/\r?\n/)[0] || '').trim() : '';
      if (primera && esEncabezado(primera) && comparte(primera)) nuevo = primera;
      if (!nuevo) nuevo = [...plano.matchAll(/(?<![\w,;|])([A-Za-z_]\w*(?:\s?[,;|]\s?[A-Za-z_]\w*){3,})/g)].map(m => m[1].replace(/\s+/g, '')).find(h => esEncabezado(h) && comparte(h)) || null;
    }
    const columnas = [];
    if (csv) {
      const ls = csv.replace(/\r/g, '').split('\n').filter(l => l.trim()), sp = sepDe(ls[0] || ','), cab = (ls[0] || '').split(sp);
      cab.forEach((h, j) => { if (/estado|status|situacion/i.test(h)) for (const l of ls.slice(1)) { const v = (l.split(sp)[j] || '').trim(); if (/^[A-Z][A-Z0-9_]+$/.test(v)) estadosTexto.add(v); } });
    }
    const otroFormato = os.find(o => /formato\s+(?:original|inicial|anterior|viejo|del\s+pre)|\b(?:cinco|seis|siete|ocho|nueve|diez|\d+)\s+columnas/.test(bajo(o.t)) && /conserv|mantener|acept/.test(bajo(o.t)));
    if (nuevo) {
      sepN = sepDe(nuevo);
      const fs = nuevo.split(sepN);
      const msj = c.mensajeEnc || 'encabezado incorrecto';
      pasos.push({
        clave: 'encabezado', titulo: `Aceptar los dos encabezados: el de ${c.viejos.length} columnas y el nuevo de ${fs.length}`,
        detalle: `Hoy el código solo acepta el de ${c.viejos.length}. Se guarda en «largo» cuántas columnas trae el archivo y con eso se controla cada fila.`,
        cita: otroFormato && (otroFormato.t.includes(nuevo) ? otroFormato.t.slice(otroFormato.t.indexOf(nuevo) + nuevo.length).replace(/^\s*[.:]?\s*/, '') : otroFormato.t), lugares: lugares([c.enc, ...c.usosEnc]),
        codigo: `String encabezado = lector.readLine();\nint largo;\nif ("${c.enc.valor}".equals(encabezado)) {\n    largo = ${c.viejos.length};\n} else if ("${nuevo}".equals(encabezado)) {\n    largo = ${fs.length};\n} else {\n    throw new IllegalArgumentException("${msj}");\n}`,
      });
      const mixto = /admiten\s+filas\s+de\s+\w+\s+campos[^.]*y\s+de\s+\w+\s+campos|formato\s+de\s+cada\s+fila\s+por\s+su\s+ancho/.test(planoB);
      if (c.controlesAncho.length) {
        const enParser = c.controlesAncho.filter(l => l.archivo === c.enc.archivo), otros = c.controlesAncho.filter(l => !enParser.includes(l));
        pasos.push({
          clave: 'ancho', titulo: mixto ? `El ancho de cada fila: bajo el encabezado nuevo, ${c.viejos.length} o ${fs.length}` : `Cada fila con el ancho de su encabezado (${c.viejos.length} o ${fs.length})`,
          detalle: [enParser.length && 'En el parser: «largo» en vez del número fijo.', otros.length && 'Donde se arma el objeto: que acepte los dos anchos.'].filter(Boolean).join(' '),
          cita: (os.find(o => mixto ? /admiten\s+filas|por\s+su\s+ancho/.test(bajo(o.t)) : /ancho/.test(bajo(o.t)) && /encabezado/.test(bajo(o.t))) || {}).t,
          lugares: lugares(c.controlesAncho),
          codigo: [enParser.length && (mixto ? `// bajo el encabezado nuevo se admiten los dos anchos\nboolean anchoOk = largo == ${c.viejos.length} ? campos.length == ${c.viejos.length} : campos.length == ${c.viejos.length} || campos.length == ${fs.length};\nif (!anchoOk) {` : `if (campos.length != largo) {`), otros.length && `${enParser.length ? '\n// y en ' + nombreDe(otros[0].archivo) + ':\n' : ''}if (campos.length != ${c.viejos.length} && campos.length != ${fs.length}) {`].filter(Boolean).join('\n'),
        });
      }
      // 2) Cada columna nueva
      const nuevas = fs.map((col, i) => ({ col, i, re: reColumna(col, i) })).filter(x => !c.viejos.includes(x.col));
      for (const { col, i, re } of nuevas) {
        // lo que dice el enunciado: las oraciones que la nombran y el resto de su párrafo si el párrafo es sobre ella
        const nombran = os.filter(o => o.p > 0 && re.test(bajo(o.t)) && !/^(?:por\s+)?ejemplos?\b/i.test(o.t) && !o.t.includes(nuevo) && !o.t.replace(/\s+/g, '').includes(nuevo));
        const dice = [];
        for (const o of nombran) {
          if (!dice.includes(o)) dice.push(o);
          const par = parrafoDe(o), k = par.indexOf(o);
          if (k === 0 || re.test(bajo(par[0].t))) {
            let n = 0;
            for (const x of par.slice(k + 1)) { if (n++ >= 3 || /^(?:por\s+)?ejemplos?\b/i.test(x.t) || nuevas.some(y => y.col !== col && y.re.test(bajo(x.t)))) break; if (!dice.includes(x)) dice.push(x); }
            const sig = os.filter(x => x.p === o.p + 1);
            if (sig.length && /^\d/.test(sig[0].t) && !sig[0].lista) for (const x of sig) if (!dice.includes(x)) dice.push(x);
            if (/:$/.test(par[par.length - 1].t)) for (let q = o.p + 1; q < pars.length && /^[-•*]\s/.test(pars[q]); q++) for (const x of os.filter(y => y.p === q)) if (!dice.includes(x)) dice.push(x);
          }
        }
        const datos = columnaCsv(csv, sepN, fs.length, i);
        // valores posibles: palabras en mayúsculas de lo que dice, que no sean estados; con CSV, las que están en los datos
        const tramo = o => {
          const b = bajo(o.t), m = b.match(re);
          if (!m) return o.t;
          const ini = m.index, fin = Math.min(...nuevas.filter(y => y.col !== col).map(y => { const r2 = new RegExp(y.re.source, 'g'); let q; while ((q = r2.exec(b))) if (q.index > ini) return q.index; return b.length; }), b.length);
          return o.t.slice(ini, fin);
        };
        let valores = [...new Set(dice.flatMap(o => mayus(tramo(o))))].filter(w => !estadosTexto.has(w) && w !== col.toUpperCase());
        if (datos && !datos.numero) {
          const en = valores.filter(v => datos.todos.includes(v));
          if (en.length >= 2) valores = en;
          else if (datos.frecuentes.length && datos.frecuentes.every(v => /^[A-Z][A-Z0-9_]*$/.test(v)) && datos.frecuentes.length <= 8) valores = datos.frecuentes.filter(v => !estadosTexto.has(v));
        }
        // números que enumera («0/30/90/180», «30, 90 o 180»), o los pocos valores del CSV que el enunciado nombra
        const ref = bajo(dice.map(o => o.t).join(' '));
        const listaDe = t => { const m = bajo(t).match(/\b\d+\s*(?:\/\s*\d+\s*){2,}/) || bajo(t).match(/\b\d+\s*,\s*\d+(?:\s*,\s*\d+)*\s+o\s+\d+\b/); return m ? m[0].split(/\s*(?:\/|,|\so\s)\s*/).map(Number).filter(n => !isNaN(n)) : []; };
        let numeros = dice.map(o => listaDe(o.t)).sort((a, b) => b.length - a.length)[0] || [];
        if (datos && datos.entero && datos.frecuentes.length <= 6) {
          // otra oración que nombra varios de los valores que trae el CSV («un plazo distinto de 0/30/90/180»)
          const hay = o => datos.frecuentes.filter(v => new RegExp('(?:^|[^\\d.,_])' + v + '(?![\\d_])').test(o.t)).length;
          const o = os.filter(o => !o.lista && hay(o) >= Math.min(3, datos.frecuentes.length)).sort((a, b) => listaDe(b.t).length - listaDe(a.t).length)[0];
          if (o && listaDe(o.t).length >= numeros.length) { numeros = listaDe(o.t).length ? listaDe(o.t) : datos.frecuentes.map(Number); if (!dice.includes(o)) dice.push(o); }
        }
        // si el texto presenta un valor que la lista no tiene («0 conserva todas las reglas…»), también va
        for (const o of dice) { const m = o.t.match(/^(\d+)\s+conserva/); if (m && numeros.length && !numeros.includes(Number(m[1]))) numeros.push(Number(m[1])); }
        numeros = [...new Set(numeros)].sort((a, b) => a - b);
        const textoCol = dice.map(o => o.t).join(' ');
        const diceNumero = /\bentero\b|numeric|\bimporte|\bmonto|decimal|porcentaje|cantidad\s+de/.test(ref);
        const decimal = !/\bentero\b/.test(ref) && (/decimal|double|con\s+coma/.test(ref) || (datos ? datos.numero && !datos.entero : false));
        const esTexto = valores.length >= 2 && !numeros.length && !(datos && datos.numero) && !/\bentero\b/.test(ref);
        const numerico = !esTexto && (diceNumero || (datos ? datos.numero : /negativ|dias|horas|\d/.test(ref)));
        const tipo = numerico ? (decimal ? 'double' : 'int') : 'String';
        const conRango = dice.filter(o => rango(o.t) && !/^(con|si|cuando)\s/i.test(o.t)).sort((a, b) => (/\bentre\b/.test(bajo(b.t)) - /\bentre\b/.test(bajo(a.t))) || (/admite|debe|invalid|rango|maximo|negativ/.test(bajo(b.t)) - /admite|debe|invalid|rango|maximo|negativ/.test(bajo(a.t))));
        const r = numerico && !numeros.length && conRango.length ? rango(conRango[0].t) : null;
        const presencia = /presencia\s+de\s+un\s+valor|si\s+(?:la\s+columna\s+)?(?:viene|esta)\s+vaci|si\s+tiene\s+(?:un\s+)?valor/.test(ref);
        let vals = esTexto ? valores : numeros;
        // el valor «normal», el que conserva las reglas de antes: es el que les toca a las filas del formato viejo
        const conserva = os.find(o => /conserva\s+(?:todas\s+)?(?:las\s+reglas|el\s+comportamiento|sus\s+calculos)/.test(bajo(o.t)) && vals.some(v => new RegExp('(?:^|:\\s*)' + escRe(String(v)) + '\\s+conserva').test(o.t)));
        let normal = conserva ? vals.find(v => new RegExp('(?:^|:\\s*)' + escRe(String(v)) + '\\s+conserva').test(conserva.t)) : undefined;
        if (normal === undefined) normal = vals.find(v => /^(NORMAL|NO|COMUN|ESTANDAR|GENERAL|BASICO|SIMPLE|NINGUNO|SIN_\w+)$/.test(String(v)));
        if (normal === undefined && numerico && !numeros.length) { const o = os.find(o => /^(\d+)\s+conserva/.test(o.t) && (dice.includes(o) || dice.some(d => d.p === o.p || d.p === o.p - 1))); if (o) { normal = Number(o.t.match(/^(\d+)/)[1]); if (!dice.includes(o)) dice.push(o); } }
        if (normal === undefined && numeros.includes(0) && /\b0\b[^.]*conserva|sin\s+(?:seguro|recargo|cargo|cobertura)/.test(bajo(textoCol))) normal = 0;
        if (conserva && !dice.includes(conserva)) dice.push(conserva);
        if (normal !== undefined && esTexto) valores = [normal, ...valores.filter(x => x !== normal)];
        let porDefecto = normal === undefined ? null : normal, notaDefecto = normal !== undefined ? 'el que conserva las reglas de antes' : '';
        if (porDefecto == null && numerico && !presencia) {
          const n = otroFormato && (bajo(otroFormato.t.split(':').slice(1).join(':')).match(/\b(\d[\d._]*)\b(?!\s*[-/]\s*\d)(?!\s*columnas)/) || [])[1];
          if (n) { porDefecto = num(n); notaDefecto = 'lo que dice el enunciado del formato viejo'; } else { porDefecto = 0; notaDefecto = 'revisalo con el enunciado'; }
        }
        const v = camel(col);
        const lit = x => tipo === 'String' ? `"${x}"` : String(x);
        const leer = numerico ? `${decimal ? 'Double.parseDouble' : 'Integer.parseInt'}(campos[${i}].strip())` : `campos[${i}].strip()`;
        let codigo = presencia
          ? `boolean ${'tiene' + capital(v)} = campos.length > ${i} && !campos[${i}].isBlank();\n${tipo} ${v} = ${'tiene' + capital(v)} ? ${leer} : 0;`
          : `${tipo} ${v} = campos.length > ${i} ? ${leer} : ${porDefecto == null ? (tipo === 'String' ? '""' : '0') : lit(porDefecto)};`;
        const regla = presencia ? (conRango.length ? rango(conRango[0].t) : null) : r;
        if (esTexto) codigo += `\nif (${valores.map(x => `!${v}.equals("${x}")`).join(' && ')}) {\n    throw new IllegalArgumentException("${col} inválido: " + ${v});\n}`;
        else if (numeros.length) codigo += `\nif (${numeros.map(x => `${v} != ${x}`).join(' && ')}) {\n    throw new IllegalArgumentException("${col} inválido: " + ${v});\n}`;
        else if (regla) codigo += `\nif (${presencia ? 'tiene' + capital(v) + ' && (' + condicionFuera(v, regla) + ')' : condicionFuera(v, regla)}) {\n    throw new IllegalArgumentException("${col} fuera de rango: " + ${v});\n}`;
        // ¿solo para algunos estados? («Para filas LISTO del nuevo formato…»)
        const para = dice.map(o => o.t.match(PARA)).find(Boolean);
        const soloEstados = para ? para[1].split(/\s*,\s*|\s+[yo]\s+/) : [];
        if (soloEstados.length && /\nif \(/.test(codigo)) codigo = codigo.replace(/\nif \((.*)\) \{/, (_, cond) => `\nif ((${soloEstados.map(s => `estado.equals("${s}")`).join(' || ')}) && (${cond})) {`);
        const fuera = regla ? 'inválido si ' + condicionFuera('x', regla).replace(/x /g, '').replace(/ \|\| /g, ' o ') : '';
        const desc = [esTexto ? valores.join(' / ') : numeros.length ? tipo + ': ' + numeros.join(' / ') : tipo + (fuera ? ', ' + fuera : ''), presencia ? 'decide si viene vacía' : '', soloEstados.length ? 'para ' + soloEstados.join(', ') : ''].filter(Boolean).join(' · ');
        vals = esTexto ? valores : numeros;
        columnas.push({ col, i, tipo, valores: vals, normal, porDefecto, presencia, soloEstados, leer });
        pasos.push({
          clave: 'columna', valor: col, titulo: `La columna nueva «${col}» (${desc})`,
          detalle: presencia ? 'Lo que decide es si la columna trae un valor o viene vacía; en el formato viejo no viene.'
            : `Leerla donde se crea el objeto${soloEstados.length ? ' y validarla solo en esos estados' : ''}. Para las filas del formato viejo: ${porDefecto == null ? 'fijate qué valor les corresponde' : lit(porDefecto) + ' (' + notaDefecto + ')'}.`,
          cita: dice.map(o => corta(o.t)).join(' '),
          datos: datos && (datos.numero ? `En el CSV del parcial: ${datos.total - datos.vacios} filas con valor${datos.distintos <= 8 ? ' (' + datos.frecuentes.join(', ') + ')' : ''}${datos.vacios ? ' y ' + datos.vacios + ' vacías' : ''}.` : `En el CSV del parcial aparecen: ${datos.frecuentes.slice(0, 8).join(', ')}${datos.vacios ? ' y ' + datos.vacios + ' vacías' : ''}.`),
          lugares: lugares([c.fabrica]), codigo,
        });
      }
    }

    // 3) Estados nuevos y descartes
    const descartados = new Set(c.descartes.map(e => e.valor)), vistos = new Set();
    const esValor = w => columnas.some(x => x.valores.includes(w));
    for (const o of os) {
      const n = bajo(o.t);
      if (!/descart/.test(n) || /no\s+se\s+descart|sin\s+descartar/.test(n)) continue;
      for (const m of o.t.matchAll(/descart\w*\s+(?:las?\s+|los?\s+)?(?:filas\s+)?([A-Z][A-Z0-9_]+)|\b([A-Z][A-Z0-9_]+)\b[^.]{0,60}?\bse\s+descarta/g)) {
        const w = m[1] || m[2];
        if (!w || descartados.has(w) || vistos.has(w) || esValor(w) || NO_VALOR.has(w)) continue;
        vistos.add(w);
        pasos.push({ clave: 'descarte', valor: w, titulo: `Descartar ${w}`, detalle: 'Después de controlar el ancho y antes de validar lo demás, igual que el descarte que ya hay.', cita: o.t, lugares: lugares(c.descartes) });
      }
    }
    for (const o of os) {
      const n = bajo(o.t);
      if (!/estado\s+valido|son\s+estados\s+validos|estado\s+nuevo|nuevo\s+estado|es\s+un\s+estado|debe\s+incorporarse/.test(n)) continue;
      const ws = mayus(o.t).length ? mayus(o.t) : mayus(parrafoDe(o)[0].t).slice(0, 1);
      for (const w of ws) {
        if (estadosCodigo.has(w) || descartados.has(w) || vistos.has(w) || esValor(w)) continue;
        vistos.add(w);
        const donde = c.estados.filter(e => !descartados.has(e.valor) && /estado/i.test(e.texto));
        pasos.push({ clave: 'estado', valor: w, titulo: `Aceptar el estado ${w}`, detalle: 'Agregarlo donde se validan los estados.', cita: [parrafoDe(o)[0] !== o ? parrafoDe(o)[0].t : '', o.t].filter(Boolean).join(' '), lugares: lugares(donde.length ? donde : c.estados.filter(e => !descartados.has(e.valor))) });
      }
    }

    // 4) Clases nuevas: las que nombra el enunciado o, si no nombra ninguna, una para el dato que cambia las reglas
    const iReq = pars.findIndex(p => /^resultado\s+requerido/i.test(p) || /resultado\s+requerido\s*$/i.test(p));
    const requerido = iReq >= 0 ? pars.slice(iReq + 1).filter(p => /^\d{1,2}[.)]\s/.test(p)).map(p => p.replace(/^\d{1,2}[.)]\s+/, '')) : [];
    const etiquetas = requerido.map(t => t.match(/\b([A-Z][A-Za-z_]+)\s*\/\s*([A-Z][A-Za-z_]+)\b/)).find(m => m && !estadosTexto.has(m[1]) && !estadosTexto.has(m[2]));
    const deCuentas = /cost|cuesta|recargo|adicional|prima|comisi|import|precio|admite|valid|puntuaci|calcula|ingreso|tarifa/;
    const nombra = (o, v) => new RegExp('(?:^|[^\\w])' + escRe(String(v)) + '(?![\\w])', isNaN(Number(v)) ? 'i' : '').test(o.t);
    const citaDe = (vs, extra) => os.filter(o => !o.lista && (vs.some(v => nombra(o, v)) || (extra && extra.test(o.t))) && deCuentas.test(bajo(o.t))).map(o => o.t);
    const clasesNuevas = [];
    for (const x of [...new Set(plano.match(/\b[A-Z][a-z]+(?:[A-Z][a-z0-9]*)+\b/g) || [])]) {
      if (c.clases.has(x) || JAVA.has(x)) continue;
      const o = os.find(o => o.t.includes(x) && /hered|extiend|extends|especializ|subclase|clase|crea\s+una/.test(bajo(o.t)));
      if (!o) continue;
      const propias = os.filter(y => y.t.includes(x)).map(y => y.t);
      const k = columnas.find(k => k.valores.length >= 2 && k.normal !== undefined && k.valores.some(v => v !== k.normal && propias.some(t => t.includes(String(v)))));
      clasesNuevas.push({ nombre: x, padre: (o.t.match(/(?:hereda\s+de|extiende\s+(?:a\s+)?|extends|especializaci[oó]n\s+de)\s+(\w+)/) || [])[1] || c.entidad, col: k, cita: [...new Set(propias.concat(citaDe(k ? k.valores.filter(v => v !== k.normal) : [])))].join(' ') });
    }
    if (!clasesNuevas.length && c.entidad) {
      const sinAlterar = /sin\s+alterar\s+la\s+estructura/.test(planoB);
      const k = columnas.find(x => x.valores.length >= 2 && x.normal !== undefined) || columnas.find(x => x.presencia) || columnas.find(x => x.tipo !== 'String' && x.normal !== undefined) || (sinAlterar ? columnas.find(x => x.tipo !== 'String') : null);
      if (k) {
        const otros = k.presencia ? [] : k.valores.filter(v => v !== k.normal);
        const nombre = etiquetas ? E + pascal(etiquetas[2]) : otros.length === 1 && isNaN(Number(otros[0])) ? E + pascal(otros[0]) : E + 'Con' + capital(camel(k.col));
        const raizEt = etiquetas ? new RegExp(escRe(etiquetas[2].replace(/[aeo]$/i, '')), 'i') : null;
        if (!c.clases.has(nombre)) clasesNuevas.push({ nombre, padre: c.entidad, opcional: true, col: k, porFormato: !k.valores.length && !k.presencia && k.normal === undefined, cita: [...new Set(citaDe(otros.length ? otros : [k.col], raizEt))].slice(0, 4).join(' ') });
      }
    }
    // los datos nuevos que valen para todos van en la entidad; el que decide la subclase y lo que solo usa ella, en la subclase
    const enSub = x => x.col && (x.col.presencia || x.col.tipo !== 'String') ? [x.col] : [];
    const propiosSub = new Set(clasesNuevas.flatMap(enSub).map(k => k.col));
    const lodiceLaClase = new Set(clasesNuevas.filter(x => x.col && x.col.tipo === 'String' && !x.col.presencia).map(x => x.col.col));
    const enBase = columnas.filter(k => !propiosSub.has(k.col) && !lodiceLaClase.has(k.col));
    if (enBase.length && c.entidad) {
      const ps = enBase.map(k => k.tipo + ' ' + camel(k.col));
      pasos.push({
        clave: 'dominio', titulo: `Guardar en ${E} ${enBase.length > 1 ? 'los datos nuevos' : 'el dato nuevo'} (${enBase.map(k => k.col).join(', ')})`,
        detalle: c.esRecord ? `${E} es un record: se agregan como componentes.` : `Un campo, el parámetro en el constructor y su getter. La fábrica le pasa lo que leyó.`,
        lugares: lugares([c.ctor && { archivo: c.archivoEntidad, n: c.ctor.n, texto: (proyecto.fuentes[c.archivoEntidad].split('\n')[c.ctor.n - 1] || '') }]),
        codigo: c.esRecord ? `public record ${E}(${c.ctor ? c.ctor.params.map(p => p.tipo + ' ' + p.nombre).join(', ') + ', ' : ''}${ps.join(', ')}) { ... }`
          : `// en ${E}:\n` + enBase.map(k => `private final ${k.tipo} ${camel(k.col)};`).join('\n') + `\n\n// el constructor recibe también ${ps.join(', ')}:\n` + enBase.map(k => `this.${camel(k.col)} = ${camel(k.col)};`).join('\n') + '\n\n' + enBase.map(k => `public ${k.tipo} get${capital(camel(k.col))}() {\n    return ${camel(k.col)};\n}`).join('\n\n'),
      });
    }
    for (const x of clasesNuevas) {
      let cod = null;
      const k = x.col, propios = enSub(x);
      if (x.padre === c.entidad && c.ctor && !c.esRecord) {
        const params = c.ctor.params.map(p => [p.tipo, p.nombre]).concat(enBase.map(y => [y.tipo, camel(y.col)]));
        const ps = params.concat(propios.map(y => [y.tipo, camel(y.col)])).map(([t, n]) => t + ' ' + n).join(', ');
        const regla = bajo(x.cita || '');
        let cuenta = 'comun;   // ← lo que cambia, según el enunciado', m;
        const f = propios[0] && camel(propios[0].col);
        if ((m = regla.match(/recargo\s+del?\s+(\d+(?:[.,]\d+)?)\s*%/))) cuenta = `comun * ${1 + num(m[1]) / 100};   // recargo del ${m[1]}%`;
        else if (f && (m = regla.match(/(\d[\d._]*)\s+(?:pesos|centavos|usd|dolares|\$)?\s*por\s+cada\s+(\d+)\s+\w+/))) cuenta = `comun + ${num(m[1])} * (${f} / ${m[2]});   // ${m[1]} por cada ${m[2]}`;
        else if (f && (m = regla.match(/(\d[\d._]*)\s+(?:pesos|centavos|usd|dolares|\$)?\s*por\s+cada\s+(?!\d)\w+/))) cuenta = `comun + ${num(m[1])} * ${f};   // ${m[1]} por cada uno`;
        else if ((m = regla.match(/(\d[\d._]*)\s+(?:pesos|centavos|usd|dolares|\$)?\s*adicionales/))) cuenta = `comun + ${num(m[1])};`;
        else if (f && (m = (x.cita || '').match(new RegExp('\\+\\s*\\(?\\s*' + escRe(propios[0].col) + '\\s*([*/])\\s*(\\d+(?:\\.\\d+)?)\\s*\\)?')))) cuenta = `comun + ${f} ${m[1]} ${m[2]};   // según la fórmula del enunciado`;
        cod = `${c.paquete ? 'package ' + c.paquete + ';\n\n' : ''}public class ${x.nombre} extends ${x.padre} {\n` + propios.map(y => `\n    private final ${y.tipo} ${camel(y.col)};\n`).join('') +
          `\n    public ${x.nombre}(${ps}) {\n        super(${params.map(p => p[1]).join(', ')});\n` + propios.map(y => `        this.${camel(y.col)} = ${camel(y.col)};\n`).join('') + '    }\n' +
          (calc ? `\n    @Override\n    public ${calc.tipo} ${calc.nombre}() {\n        ${calc.tipo} comun = super.${calc.nombre}();\n        return ${cuenta}\n    }\n` : '') + '}\n';
      }
      const fab = c.fabrica && c.fabrica.metodo ? c.fabrica.metodo : 'la fábrica';
      let cuando = null;
      if (k && k.presencia) cuando = 'tiene' + capital(camel(k.col));
      else if (x.porFormato && k) cuando = `campos.length > ${k.i}`;
      else if (k && k.normal !== undefined) { const otro = k.valores.filter(v => v !== k.normal); cuando = k.tipo === 'String' ? (otro.length === 1 ? `${camel(k.col)}.equals("${otro[0]}")` : `!${camel(k.col)}.equals("${k.normal}")`) : `${camel(k.col)} != ${k.normal}`; }
      const crea = cuando ? `\n// en ${fab}:\nif (${cuando}) {\n    return new ${x.nombre}(...);\n}\nreturn new ${E}(...);` : '';
      pasos.push({
        clave: 'clase', valor: x.nombre, titulo: `${x.opcional ? 'Si usás herencia: ' : ''}la clase ${x.nombre}${x.padre ? ' extends ' + x.padre : ''}`,
        detalle: c.esRecord ? `${E} es un record y un record no se puede heredar: o lo pasás a clase, o agregás el dato nuevo al record.` : 'Con «+ Clase nueva». La crea la fábrica según el dato nuevo; el resto del programa la usa como si fuera la de siempre (polimorfismo).' + (x.opcional ? ' El enunciado acepta herencia, composición u otra solución.' : ''),
        cita: x.cita, lugares: lugares([c.fabrica, calc]), codigo: cod ? cod + crea : (crea.trim() || null),
      });
    }

    // 5) Las cuentas: lo que dice el enunciado de costos, recargos, y sus ejemplos
    if (c.calculos.length) {
      const reglas = os.filter(o => /\b(costo|importe|precio|recargo|descuento|bonificaci|cargo|tarifa|comisi|prima|puntuaci|score|ingreso)/.test(bajo(o.t)) && /\d|%/.test(o.t) && /%|\*|por\s+cada|se\s+calcula|suma|agrega|descuenta|multiplica|cuesta|adicional|sobre/.test(bajo(o.t)) && !/minutos|filas\s+de\s+datos|lineas/.test(bajo(o.t)) && !/^\d+[.)]/.test(o.t)).slice(0, 5);
      const ejemplo = ejemplos(texto);
      if (reglas.length || ejemplo) pasos.push({ clave: 'calculo', titulo: `Las cuentas${calc ? ': ' + calc.nombre + '()' : ''}`, detalle: 'Donde hoy se calcula (y en la subclase, si la hay). Con los ejemplos del enunciado comprobás que dé lo mismo.', cita: reglas.map(o => o.t).join(' · '), ejemplo, lugares: lugares(calc ? [calc] : c.calculos) });
    }

    // 6) El resultado requerido: lo que va en el colector, con el código para contar por un dato
    if (requerido.length) {
      let cod = null;
      const conteo = requerido.map(t => t.match(/(?:conteo|agrupamiento|cantidad(?:es)?|cuente\s+\w+)\s+(?:o\s+conteo\s+)?por\s+((?:tipo\s+de\s+)?[\wáéíóúñ]+(?:\s+de\s+[\wáéíóúñ]+)?)/i)).find(Boolean);
      if (conteo && c.colector) {
        const que = bajo(conteo[1]).replace(/^tipo\s+de\s+/, '');
        const todas = nuevo ? nuevo.split(sepN) : c.viejos;
        const col = todas.find(k => reColumna(k, -1).test(' ' + que + ' ') || bajo(k) === que.replace(/\s+/g, ''));
        const nueva = clasesNuevas[0];
        const metodo = 'cantidadPor' + capital(camel(col || 'tipo'));
        const valor = col ? `${e1}.${c.getter(col) || 'get' + capital(camel(col))}()` : nueva && etiquetas ? `${e1} instanceof ${nueva.nombre} ? "${etiquetas[2]}" : "${etiquetas[1]}"` : `${e1}.getTipo()`;
        cod = `// en ${c.colector.clase} (import java.util.Map; import java.util.TreeMap;)\npublic Map<String, Integer> ${metodo}() {\n    Map<String, Integer> cantidades = new TreeMap<>();\n    for (${E} ${e1} : ${c.colector.campo}) {\n        cantidades.merge(${col && columnas.some(k => k.col === col && k.tipo !== 'String') ? 'String.valueOf(' + valor + ')' : valor}, 1, Integer::sum);\n    }\n    return cantidades;\n}`;
        const k = col && columnas.find(y => y.col === col);
        const sub = k && clasesNuevas.find(x => x.col === k && lodiceLaClase.has(k.col));
        if (sub) cod += `\n\n// el dato lo dice la clase: en ${E}\npublic String get${capital(camel(col))}() {\n    return "${k.normal}";\n}\n\n// y en ${sub.nombre}\n@Override\npublic String get${capital(camel(col))}() {\n    return "${k.valores.find(v => v !== k.normal)}";\n}`;
      }
      pasos.push({ clave: 'requerido', titulo: 'Lo que pide «Resultado requerido»', detalle: c.colector ? `Agrupar, contar o sumar va en ${c.colector.clase}; el main solo muestra.` : 'La lógica va en las clases, no en el main.', lista: requerido, lugares: lugares([c.colector]), codigo: cod });
    }

    // 7) El main con el CSV del parcial
    const csvNuevo = (plano.match(/\b(datos[\w-]*\.csv)\b/g) || []).find(x => x !== 'datos.csv');
    if (csvNuevo && c.csvMain && !c.csvMain.texto.includes(csvNuevo)) {
      pasos.push({ clave: 'main', titulo: `El main: ${csvNuevo} por defecto`, detalle: 'La ruta que usa cuando no le pasás argumentos.', cita: requerido.find(t => /\bmain\b/i.test(t)) || null, lugares: lugares([c.csvMain]), codigo: c.csvMain.texto.trim().replace(/datos[\w-]*\.csv/, csvNuevo) });
    }

    // 8) DECISIONES.md, si lo pide: un borrador contado en criollo, para ajustar
    if (/DECISIONES(?:\.md)?/.test(plano)) {
      const ls = [];
      if (nuevo) ls.push(`- Dejé un solo parser para los dos formatos: miro el encabezado, guardo en «largo» si son ${c.viejos.length} o ${nuevo.split(sepN).length} columnas y cada fila tiene que tener ese ancho.`);
      if (columnas.length) ls.push(`- ${columnas.length > 1 ? 'Las columnas nuevas (' + columnas.map(k => k.col).join(', ') + ') las leo' : 'La columna nueva (' + columnas[0].col + ') la leo'} donde se arma ${E}; las filas del formato viejo siguen como antes${columnas.some(k => k.porDefecto != null) ? ' (van con ' + columnas.filter(k => k.porDefecto != null).map(k => k.col + ' = ' + k.porDefecto).join(', ') + ')' : ''}.`);
      for (const p of pasos.filter(p => p.clave === 'clase')) ls.push(`- Hice ${p.valor}, que hereda de ${E} y cambia ${calc ? calc.nombre + '()' : 'la cuenta'}; el resto del programa no se entera.`);
      const est = pasos.filter(p => p.clave === 'estado').map(p => p.valor), des = pasos.filter(p => p.clave === 'descarte').map(p => p.valor);
      if (est.length || des.length) ls.push(`- ${est.length ? est.join(' y ') + ' ahora entra como válido' : ''}${est.length && des.length ? '; ' : ''}${des.length ? des.join(' y ') + ' se descarta después de ver el ancho' : ''}.`);
      if (c.colector && requerido.some(t => /conteo|agrup|cuente|suma\s+total|total\s+de/i.test(t))) ls.push(`- Lo nuevo de contar o sumar quedó en ${c.colector.clase}; el main solo muestra${csvNuevo ? ' y lee ' + csvNuevo + ' por defecto' : ''}.`);
      ls.push('- Pendiente: nada (o anotá acá lo que te quedó).');
      pasos.push({ clave: 'decisiones', titulo: 'DECISIONES.md (un borrador para ajustar)', detalle: 'Sale de los pasos de arriba: cambialo según lo que hiciste de verdad.', cita: (os.find(o => /DECISIONES/.test(o.t)) || {}).t, lugares: [], codigo: '# Decisiones\n\n' + ls.slice(0, 6).join('\n') + '\n', archivo: 'DECISIONES.md' });
    }
    return { codigo: c, pasos, encabezadoNuevo: nuevo, columnas };
  }

  return { armar, analizarCodigo, parrafos };
});
