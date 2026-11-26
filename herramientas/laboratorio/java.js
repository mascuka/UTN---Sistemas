/* Un ejecutor de Java para el navegador, sin internet: lee el código de un proyecto (el de un preenunciado) y corre
   su main con los archivos que se le den, con las reglas de Java (enteros de 32 bits, long, división entera, (int) que
   trunca, String.split, HashMap con el mismo orden que Java, printf con el idioma de la compu, excepciones con sus
   mensajes). No es una JVM: entiende el Java que usan los proyectos de la cátedra (clases, herencia, colecciones,
   streams, lambdas, archivos de texto) y, si encuentra algo que no sabe, lo dice con el archivo y la línea.
   Uso: JavaMini.ejecutar({ fuentes: {ruta: código}, archivos: {'datos/datos.csv': texto}, args: [] })
        → { salida, error, codigo }   (también corre en Node: require('./java.js')) */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica();
  else raiz.JavaMini = fabrica();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ═════════════════════════════ 1) Las palabras del código ═════════════════════════════
  const PALABRAS = new Set(('abstract assert boolean break byte case catch char class const continue default do double else enum extends final '
    + 'finally float for goto if implements import instanceof int interface long native new package private protected public return short static '
    + 'strictfp super switch synchronized this throw throws transient try void volatile while true false null').split(' '));
  const OPERADORES = ['>>>=', '<<=', '>>=', '...', '->', '::', '++', '--', '&&', '||', '==', '!=', '<=', '>=', '+=', '-=', '*=', '/=', '%=',
    '&=', '|=', '^=', '<<', '(', ')', '{', '}', '[', ']', ';', ',', '.', '@', '=', '>', '<', '!', '~', '?', ':', '+', '-', '*', '/', '&', '|',
    '^', '%'];

  class ErrorJava extends Error {}                         // un problema del código (no de Java en ejecución)
  const falla = (msg, archivo, linea) => { throw new ErrorJava((archivo ? archivo + (linea ? ':' + linea : '') + ': ' : '') + msg); };

  function lexico(texto, archivo) {
    const ts = [];
    let i = 0, linea = 1;
    const n = texto.length;
    while (i < n) {
      const c = texto[i];
      if (c === '\n') { linea++; i++; continue; }
      if (c === ' ' || c === '\t' || c === '\r' || c === '\f' || c === '﻿') { i++; continue; }
      if (c === '/' && texto[i + 1] === '/') { while (i < n && texto[i] !== '\n') i++; continue; }
      if (c === '/' && texto[i + 1] === '*') {
        i += 2;
        while (i < n && !(texto[i] === '*' && texto[i + 1] === '/')) { if (texto[i] === '\n') linea++; i++; }
        i += 2; continue;
      }
      const ini = i, lin = linea;
      if (/[A-Za-z_$À-￿]/.test(c)) {
        while (i < n && /[\w$À-￿]/.test(texto[i])) i++;
        const v = texto.slice(ini, i);
        ts.push({ t: PALABRAS.has(v) ? 'kw' : 'id', v, l: lin, p: ini, f: i });
        continue;
      }
      if (/[0-9]/.test(c) || (c === '.' && /[0-9]/.test(texto[i + 1] || ''))) {
        let v, tipo;
        if (c === '0' && /[xX]/.test(texto[i + 1] || '')) {
          i += 2; while (i < n && /[0-9a-fA-F_]/.test(texto[i])) i++;
          v = texto.slice(ini + 2, i).replace(/_/g, '');
          if (/[lL]/.test(texto[i] || '')) { i++; ts.push({ t: 'num', tipo: 'long', v: BigInt.asIntN(64, BigInt('0x' + v)), l: lin, p: ini, f: i }); }
          else ts.push({ t: 'num', tipo: 'int', v: Number(BigInt.asIntN(32, BigInt('0x' + v))), l: lin, p: ini, f: i });
          continue;
        }
        while (i < n && /[0-9_]/.test(texto[i])) i++;
        let real = false;
        if (texto[i] === '.' && /[0-9]/.test(texto[i + 1] || '')) { real = true; i++; while (i < n && /[0-9_]/.test(texto[i])) i++; }
        else if (texto[i] === '.' && !/[A-Za-z_]/.test(texto[i + 1] || '')) { real = true; i++; }
        if (/[eE]/.test(texto[i] || '') && /[0-9+-]/.test(texto[i + 1] || '')) { real = true; i++; if (/[+-]/.test(texto[i])) i++; while (i < n && /[0-9]/.test(texto[i])) i++; }
        v = texto.slice(ini, i).replace(/_/g, '');
        if (/[lL]/.test(texto[i] || '') && !real) { i++; tipo = 'long'; ts.push({ t: 'num', tipo, v: BigInt.asIntN(64, BigInt(v)), l: lin, p: ini, f: i }); continue; }
        if (/[dDfF]/.test(texto[i] || '')) { i++; real = true; }
        if (real) ts.push({ t: 'num', tipo: 'double', v: Number(v), l: lin, p: ini, f: i });
        else {
          const x = Number(v);
          if (x > 2147483648) falla('el número ' + v + ' no entra en un int', archivo, lin);
          ts.push({ t: 'num', tipo: 'int', v: x | 0, l: lin, p: ini, f: i });
        }
        continue;
      }
      if (c === '"') {
        if (texto.startsWith('"""', i)) {                    // bloque de texto
          i += 3; while (i < n && texto[i] !== '\n') i++; i++; linea++;
          let crudo = '';
          while (i < n && !texto.startsWith('"""', i)) { if (texto[i] === '\n') linea++; crudo += texto[i]; i++; }
          i += 3;
          const ls = crudo.split('\n'), sangria = Math.min(...ls.filter(x => x.trim()).map(x => x.match(/^[ \t]*/)[0].length).concat([ls[ls.length - 1].length]));
          ts.push({ t: 'str', v: escapes(ls.map(x => x.slice(sangria).replace(/[ \t]+$/, '')).join('\n'), archivo, lin), l: lin, p: ini, f: i });
          continue;
        }
        i++; let s = '';
        while (i < n && texto[i] !== '"') { if (texto[i] === '\\') { s += texto[i] + texto[i + 1]; i += 2; } else { if (texto[i] === '\n') falla('una cadena sin cerrar', archivo, lin); s += texto[i++]; } }
        i++;
        ts.push({ t: 'str', v: escapes(s, archivo, lin), l: lin, p: ini, f: i });
        continue;
      }
      if (c === "'") {
        i++; let s = '';
        while (i < n && texto[i] !== "'") { if (texto[i] === '\\') { s += texto[i] + texto[i + 1]; i += 2; } else s += texto[i++]; }
        i++;
        const v = escapes(s, archivo, lin);
        if (v.length !== 1) falla('un char con más de un carácter', archivo, lin);
        ts.push({ t: 'chr', v: v.charCodeAt(0), l: lin, p: ini, f: i });
        continue;
      }
      const op = OPERADORES.find(o => texto.startsWith(o, i));
      if (!op) falla('no entiendo el carácter «' + c + '»', archivo, lin);
      i += op.length;
      ts.push({ t: 'op', v: op, l: lin, p: ini, f: i });
    }
    ts.push({ t: 'eof', v: '', l: linea, p: n, f: n });
    return ts;
  }
  function escapes(s, archivo, linea) {
    return s.replace(/\\(u+[0-9a-fA-F]{4}|[0-7]{1,3}|.)/g, (m, x) => {
      if (x[0] === 'u') return String.fromCharCode(parseInt(x.replace(/^u+/, ''), 16));
      if (/^[0-7]/.test(x)) return String.fromCharCode(parseInt(x, 8));
      const e = { n: '\n', t: '\t', r: '\r', b: '\b', f: '\f', s: ' ', '"': '"', "'": "'", '\\': '\\' }[x];
      if (e === undefined) falla('escape «\\' + x + '» desconocido', archivo, linea);
      return e;
    });
  }

  // ═════════════════════════════ 2) La estructura: clases, métodos, sentencias, expresiones ═════════════════════════════
  const PRIMITIVOS = new Set(['int', 'long', 'double', 'float', 'boolean', 'char', 'byte', 'short', 'void']);
  const MODIFICADORES = new Set(['public', 'private', 'protected', 'static', 'final', 'abstract', 'native', 'synchronized', 'transient',
    'volatile', 'strictfp', 'default', 'sealed', 'non-sealed']);

  function sintaxis(texto, archivo) {
    const ts = lexico(texto, archivo);
    let k = 0;
    const ver = (d = 0) => ts[Math.min(k + d, ts.length - 1)];
    const es = (v, d = 0) => { const t = ver(d); return (t.t === 'op' || t.t === 'kw') && t.v === v; };
    const esId = (d = 0) => ver(d).t === 'id';
    const err = (msg, t = ver()) => falla(msg + (t.t !== 'eof' ? ' (cerca de «' + (t.t === 'str' ? '"…"' : t.v) + '»)' : ''), archivo, t.l);
    const tomar = v => { if (!es(v)) err('esperaba «' + v + '»'); return ts[k++]; };
    const opc = v => { if (es(v)) { k++; return true; } return false; };
    const id = () => { if (!esId()) err('esperaba un nombre'); return ts[k++].v; };

    function anotaciones() { while (es('@') && !es('interface', 1)) { k++; nombreCalificado(); if (es('(')) saltarParentesis(); } }
    function saltarParentesis() { let d = 0; do { if (es('(')) d++; else if (es(')')) d--; k++; } while (d > 0 && ver().t !== 'eof'); }
    function nombreCalificado() { let s = id(); while (es('.') && esId(1)) { k++; s += '.' + id(); } return s; }
    function modificadores() {
      const m = new Set();
      for (;;) {
        anotaciones();
        const t = ver();
        if ((t.t === 'kw' || t.t === 'id') && MODIFICADORES.has(t.v) && !(t.v === 'default' && (es(':', 1) || es('->', 1)))) { m.add(t.v); k++; }
        else if (t.t === 'id' && t.v === 'non' && es('-', 1)) { k += 3; }
        else return m;
      }
    }
    // Tipos: int, String, List<Map<String, Integer>>, int[], String... (los genéricos se leen y se guardan aparte)
    function argsDeTipo() {
      const as = [];
      tomar('<');
      if (opc('>')) return as;                                // <>
      do {
        anotaciones();
        if (opc('?')) { if (opc('extends') || opc('super')) as.push(tipo()); else as.push({ n: 'Object', d: 0 }); }
        else as.push(tipo());
      } while (opc(','));
      tomar('>');
      return as;
    }
    function tipo() {
      anotaciones();
      const t = ver();
      let n;
      if (t.t === 'kw' && PRIMITIVOS.has(t.v)) { k++; n = t.v; }
      else if (t.t === 'id') {
        n = id(); let as = es('<') ? argsDeTipo() : null;
        while (es('.') && esId(1)) { k++; n = id(); if (es('<')) as = argsDeTipo(); }   // Map.Entry → Entry
        const d0 = dimensiones();
        return { n, a: as, d: d0 + (opc('...') ? 1 : 0) };
      } else err('esperaba un tipo');
      const d = dimensiones();
      return { n, d: d + (opc('...') ? 1 : 0) };
    }
    function dimensiones() { let d = 0; while (es('[') && es(']', 1)) { k += 2; d++; } return d; }
    // ¿Empieza acá una declaración «Tipo nombre»? (se prueba sin consumir)
    function pareceDeclaracion() {
      const g = k;
      try {
        if (es('final')) k++;
        anotaciones();
        if (ver().t === 'id' && ver().v === 'var' && esId(1)) return true;
        if (ver().t !== 'id' && !(ver().t === 'kw' && PRIMITIVOS.has(ver().v) && ver().v !== 'void')) return false;
        tipo();
        return esId() && (es('=', 1) || es(';', 1) || es(',', 1) || es(':', 1) || es('[', 1));
      } catch (e) { if (e instanceof ErrorJava) return false; throw e; } finally { k = g; }
    }

    // ── Clases
    function unidad() {
      const u = { paquete: '', imports: [], clases: [] };
      anotaciones();
      if (opc('package')) { u.paquete = nombreCalificado(); tomar(';'); }
      while (es('import')) { k++; opc('static'); let s = nombreCalificado(); if (opc('.')) { tomar('*'); s += '.*'; } tomar(';'); u.imports.push(s); }
      while (ver().t !== 'eof') { if (opc(';')) continue; u.clases.push(declaracionDeTipo(modificadores())); }
      return u;
    }
    function declaracionDeTipo(mods) {
      const l = ver().l;
      let tipoDecl;
      if (opc('class')) tipoDecl = 'class';
      else if (opc('interface')) tipoDecl = 'interface';
      else if (es('@') && es('interface', 1)) { k += 2; tipoDecl = 'anotacion'; }
      else if (opc('enum')) tipoDecl = 'enum';
      else if (ver().t === 'id' && ver().v === 'record') { k++; tipoDecl = 'record'; }
      else err('esperaba una clase');
      const c = { tipo: tipoDecl, nombre: id(), mods, padre: null, interfaces: [], miembros: [], archivo, l, componentes: null, constantes: [] };
      if (es('<')) argsDeTipo();
      if (tipoDecl === 'record') {
        tomar('('); c.componentes = [];
        if (!es(')')) do { anotaciones(); const t = tipo(); c.componentes.push({ t, nombre: id() }); } while (opc(','));
        tomar(')');
      }
      if (opc('extends')) { if (tipoDecl === 'interface') { do c.interfaces.push(tipo().n); while (opc(',')); } else c.padre = tipo().n; }
      if (opc('implements')) do c.interfaces.push(tipo().n); while (opc(','));
      if (ver().t === 'id' && ver().v === 'permits') { k++; do tipo(); while (opc(',')); }
      cuerpoDeClase(c);
      return c;
    }
    function cuerpoDeClase(c) {
      tomar('{');
      if (c.tipo === 'enum') {
        while (esId()) {
          const l = ver().l, nombre = id(); let args = [];
          if (es('(')) args = argumentos();
          if (es('{')) err('constantes de enum con cuerpo propio');
          c.constantes.push({ nombre, args, l });
          if (!opc(',')) break;
        }
        opc(';');
      }
      while (!opc('}')) {
        if (opc(';')) continue;
        const l = ver().l;
        if (es('{')) { c.miembros.push({ m: 'init', estatico: false, cuerpo: bloque(), l }); continue; }
        if (es('static') && es('{', 1)) { k++; c.miembros.push({ m: 'init', estatico: true, cuerpo: bloque(), l }); continue; }
        const mods = modificadores();
        if (es('class') || es('interface') || es('enum') || (ver().t === 'id' && ver().v === 'record' && esId(1)) || (es('@') && es('interface', 1))) {
          const anidada = declaracionDeTipo(mods); c.miembros.push({ m: 'clase', clase: anidada, l }); continue;
        }
        if (es('<')) argsDeTipo();
        if (esId() && ver().v === c.nombre && es('(', 1)) {                 // constructor
          k++;
          const params = parametros(); excepciones();
          c.miembros.push({ m: 'ctor', mods, params, cuerpo: bloque(), l });
          continue;
        }
        if (c.tipo === 'record' && esId() && ver().v === c.nombre && es('{', 1)) {   // constructor compacto del record
          k++; c.miembros.push({ m: 'ctor', mods, params: null, compacto: true, cuerpo: bloque(), l }); continue;
        }
        const t = tipo();
        const nombre = id();
        if (es('(')) {
          const params = parametros(); dimensiones(); excepciones();
          let cuerpo = null;
          if (opc('default')) { expresion(); tomar(';'); }
          else if (!opc(';')) cuerpo = bloque();
          if (c.tipo === 'interface' && !mods.has('static') && !mods.has('private')) { if (cuerpo) mods.add('default'); else mods.add('abstract'); mods.add('public'); }
          c.miembros.push({ m: 'metodo', mods, t, nombre, params, cuerpo, l });
          continue;
        }
        let actual = nombre;
        for (;;) {
          const dims = dimensiones();
          const init = opc('=') ? (es('{') ? inicializadorDeArreglo() : expresion()) : null;
          const mf = new Set(mods); if (c.tipo === 'interface') { mf.add('static'); mf.add('final'); }
          c.miembros.push({ m: 'campo', mods: mf, t: { ...t, d: t.d + dims }, nombre: actual, init, l });
          if (!opc(',')) break;
          actual = id();
        }
        tomar(';');
      }
    }
    function parametros() {
      tomar('(');
      const ps = [];
      if (!es(')')) do {
        modificadores();
        const t = tipo();
        if (es('this')) { k++; continue; }
        const nombre = id();
        ps.push({ t: { ...t, d: t.d + dimensiones() }, nombre });
      } while (opc(','));
      tomar(')');
      return ps;
    }
    function excepciones() { if (opc('throws')) do tipo(); while (opc(',')); }

    // ── Sentencias
    function bloque() {
      const l = ver().l;
      tomar('{');
      const ss = [];
      while (!opc('}')) { if (ver().t === 'eof') err('falta cerrar una llave'); ss.push(sentencia()); }
      return { s: 'bloque', ss, l };
    }
    function declaracionLocal(final) {
      const l = ver().l;
      const t = ver().t === 'id' && ver().v === 'var' && esId(1) ? (k++, { n: 'var', d: 0 }) : tipo();
      const vars = [];
      do {
        const nombre = id();
        const dims = dimensiones();
        const init = opc('=') ? (es('{') ? inicializadorDeArreglo() : expresion()) : null;
        vars.push({ nombre, t: { ...t, d: t.d + dims }, init });
      } while (opc(','));
      return { s: 'local', vars, l, final };
    }
    function sentencia() {
      const t = ver(), l = t.l;
      if (es('{')) return bloque();
      if (opc(';')) return { s: 'nada', l };
      if (esId() && es(':', 1) && !es('::', 1)) { const etiqueta = id(); k++; const cuerpo = sentencia(); return { s: 'etiqueta', etiqueta, cuerpo, l }; }
      if (opc('if')) {
        tomar('('); const c = expresion(); tomar(')');
        const si = sentencia(); const sino = opc('else') ? sentencia() : null;
        return { s: 'if', c, si, sino, l };
      }
      if (opc('while')) { tomar('('); const c = expresion(); tomar(')'); return { s: 'while', c, cuerpo: sentencia(), l }; }
      if (opc('do')) { const cuerpo = sentencia(); tomar('while'); tomar('('); const c = expresion(); tomar(')'); tomar(';'); return { s: 'do', c, cuerpo, l }; }
      if (opc('for')) {
        tomar('(');
        const g = k;
        const final = opc('final'); anotaciones();
        if (pareceDeclaracion()) {
          const tv = ver().t === 'id' && ver().v === 'var' && esId(1) ? (k++, { n: 'var', d: 0 }) : tipo();
          const nombre = id();
          if (opc(':')) { const col = expresion(); tomar(')'); return { s: 'foreach', t: tv, nombre, col, cuerpo: sentencia(), l }; }
          k = g; if (final) k++;
        } else k = g;
        let init = [];
        if (!es(';')) { opc('final'); if (pareceDeclaracion()) init = [declaracionLocal(false)]; else do init.push({ s: 'expr', e: expresion(), l }); while (opc(',')); }
        tomar(';');
        const c = es(';') ? null : expresion(); tomar(';');
        const paso = [];
        if (!es(')')) do paso.push(expresion()); while (opc(','));
        tomar(')');
        return { s: 'for', init, c, paso, cuerpo: sentencia(), l };
      }
      if (opc('return')) { const e = es(';') ? null : expresion(); tomar(';'); return { s: 'return', e, l }; }
      if (opc('throw')) { const e = expresion(); tomar(';'); return { s: 'throw', e, l }; }
      if (opc('break')) { const etiqueta = esId() ? id() : null; tomar(';'); return { s: 'break', etiqueta, l }; }
      if (opc('continue')) { const etiqueta = esId() ? id() : null; tomar(';'); return { s: 'continue', etiqueta, l }; }
      if (ver().t === 'id' && ver().v === 'yield' && !es('=', 1) && !es('(', 1) && !es('.', 1)) { k++; const e = expresion(); tomar(';'); return { s: 'yield', e, l }; }
      if (opc('try')) {
        const recursos = [];
        if (opc('(')) {
          while (!opc(')')) {
            opc('final');
            if (pareceDeclaracion()) { const d = declaracionLocal(true); recursos.push(d); }
            else recursos.push({ s: 'expr', e: expresion(), l });
            opc(';');
          }
        }
        const cuerpo = bloque();
        const capturas = [];
        while (opc('catch')) {
          tomar('('); modificadores();
          const tipos = [tipo().n]; while (opc('|')) tipos.push(tipo().n);
          const nombre = id(); tomar(')');
          capturas.push({ tipos, nombre, cuerpo: bloque() });
        }
        const fin = opc('finally') ? bloque() : null;
        return { s: 'try', recursos, cuerpo, capturas, fin, l };
      }
      if (es('switch')) { const e = switchExpr(); opc(';'); return { s: 'expr', e, l }; }
      if (opc('assert')) { expresion(); if (opc(':')) expresion(); tomar(';'); return { s: 'nada', l }; }
      if (es('class') || es('interface') || es('enum') || ((es('final') || es('abstract') || es('static')) && (es('class', 1) || es('interface', 1)))) err('clases locales');
      if (es('final') || pareceDeclaracion()) { const final = opc('final'); const d = declaracionLocal(final); tomar(';'); return d; }
      const e = expresion(); tomar(';');
      return { s: 'expr', e, l };
    }

    // ── Expresiones
    function expresion() { return asignacion(); }
    const ASIGNACIONES = new Set(['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '>>>=']);
    function asignacion() {
      if (esLambda()) return lambda();
      const izq = ternario();
      const t = ver();
      if (t.t === 'op' && ASIGNACIONES.has(t.v)) {
        if (!['var', 'campo', 'indice'].includes(izq.e)) err('no se puede asignar a esto');
        k++;
        return { e: 'asig', op: t.v, a: izq, b: asignacion(), l: t.l };
      }
      // «>>=» y «>>>=» vienen como «>» «>=» (por los genéricos)
      if (es('>') && (es('>=', 1) || (es('>', 1) && es('>=', 2))) && ver().f === ver(1).p) {
        const triple = es('>', 1); k += triple ? 3 : 2;
        return { e: 'asig', op: triple ? '>>>=' : '>>=', a: izq, b: asignacion(), l: t.l };
      }
      return izq;
    }
    function esLambda() {
      if (esId() && es('->', 1)) return true;
      if (!es('(')) return false;
      let d = 0, j = k;
      for (;;) { const t = ts[j]; if (t.t === 'eof') return false; if (t.v === '(' && t.t === 'op') d++; else if (t.v === ')' && t.t === 'op') { d--; if (d === 0) break; } j++; }
      return ts[j + 1] && ts[j + 1].t === 'op' && ts[j + 1].v === '->';
    }
    function lambda() {
      const l = ver().l, params = [];
      if (esId()) params.push({ nombre: id(), t: null });
      else {
        tomar('(');
        if (!es(')')) do {
          modificadores();
          if (esId() && (es(',', 1) || es(')', 1))) params.push({ nombre: id(), t: null });
          else { const t = ver().t === 'id' && ver().v === 'var' ? (k++, null) : tipo(); params.push({ nombre: id(), t }); }
        } while (opc(','));
        tomar(')');
      }
      tomar('->');
      const cuerpo = es('{') ? bloque() : expresion();
      return { e: 'lambda', params, cuerpo, l };
    }
    function ternario() {
      const c = binaria(0);
      if (es('?')) {
        const l = ver().l; k++;
        const a = es('(') && esLambda() ? lambda() : ternarioOLambda(); tomar(':');
        const b = ternarioOLambda();
        return { e: 'cond', c, a, b, l };
      }
      return c;
    }
    function ternarioOLambda() { return esLambda() ? lambda() : ternario(); }
    const NIVELES = [['||'], ['&&'], ['|'], ['^'], ['&'], ['==', '!='], ['<', '>', '<=', '>=', 'instanceof'], ['<<', '>>', '>>>'], ['+', '-'], ['*', '/', '%']];
    function operadorBinario(nivel) {
      const t = ver();
      if (nivel === 7) {                                       // corrimientos: «>>» y «>>>» llegan como «>» pegados
        if (es('<<')) return { op: '<<', largo: 1 };
        if (es('>') && es('>', 1) && t.f === ver(1).p && !es('>=', 2) && !(es('>', 2) && es('>=', 3))) {
          if (es('>', 2) && ver(1).f === ver(2).p) return { op: '>>>', largo: 3 };
          return { op: '>>', largo: 2 };
        }
        return null;
      }
      if (nivel === 6 && es('>') && es('>', 1) && t.f === ver(1).p) return null;   // es un corrimiento
      if ((t.t === 'op' || t.t === 'kw') && NIVELES[nivel].includes(t.v)) return { op: t.v, largo: 1 };
      return null;
    }
    function binaria(nivel) {
      if (nivel >= NIVELES.length) return unaria();
      let a = binaria(nivel + 1);
      for (;;) {
        const o = operadorBinario(nivel);
        if (!o) return a;
        const l = ver().l; k += o.largo;
        if (o.op === 'instanceof') {
          const final = opc('final');
          const t = tipo();
          const nombre = esId() ? id() : null;
          void final;
          a = { e: 'instanceof', a, t, nombre, l };
          continue;
        }
        a = { e: 'bin', op: o.op, a, b: binaria(nivel + 1), l };
      }
    }
    function esCast() {
      if (!es('(')) return false;
      const t1 = ver(1);
      if (t1.t === 'kw' && PRIMITIVOS.has(t1.v)) {
        const g = k; k++;
        try { tipo(); return es(')'); } catch (e) { if (e instanceof ErrorJava) return false; throw e; } finally { k = g; }
      }
      if (t1.t !== 'id') return false;
      const g = k; k++;
      try {
        tipo(); while (opc('&')) tipo();
        if (!es(')')) return false;
        const s = ver(1);
        return s.t === 'id' || s.t === 'str' || s.t === 'chr' || s.t === 'num' || (s.t === 'kw' && ['this', 'new', 'super', 'true', 'false', 'null', 'switch'].includes(s.v))
          || (s.t === 'op' && ['(', '!', '~'].includes(s.v));
      } catch (e) { if (e instanceof ErrorJava) return false; throw e; } finally { k = g; }
    }
    function unaria() {
      const t = ver(), l = t.l;
      if (t.t === 'op' && ['+', '-', '!', '~'].includes(t.v)) {
        k++;
        if (t.v === '-' && ver().t === 'num' && ver().p === t.f) {   // -2147483648 y -9223372036854775808L
          const n = ver();
          if (n.tipo === 'int' || n.tipo === 'long') { k++; return sufijos({ e: 'lit', v: n.tipo === 'int' ? (-n.v) | 0 : BigInt.asIntN(64, -n.v), tipo: n.tipo, l }); }
        }
        return { e: 'un', op: t.v, a: unaria(), l };
      }
      if (t.t === 'op' && (t.v === '++' || t.v === '--')) { k++; return { e: 'pre', op: t.v, a: unaria(), l }; }
      if (esCast()) {
        k++; const ct = tipo(); while (opc('&')) tipo(); tomar(')');
        const a = esLambda() ? lambda() : unaria();
        return { e: 'cast', t: ct, a, l };
      }
      return sufijos(primaria());
    }
    function argumentos() {
      tomar('(');
      const as = [];
      if (!es(')')) do as.push(expresion()); while (opc(','));
      tomar(')');
      return as;
    }
    function sufijos(x) {
      for (;;) {
        const t = ver(), l = t.l;
        if (opc('.')) {
          if (es('<')) argsDeTipo();
          if (opc('new')) { x = { e: 'new', t: tipo(), args: argumentos(), fuera: x, l }; continue; }
          if (es('this')) { k++; x = { e: 'this', clase: x, l }; continue; }
          if (es('class')) { k++; x = { e: 'claseLit', t: x, l }; continue; }
          const nombre = ver().t === 'kw' ? ts[k++].v : id();
          if (es('(')) x = { e: 'llamada', obj: x, nombre, args: argumentos(), l };
          else x = { e: 'campo', obj: x, nombre, l };
          continue;
        }
        if (es('::')) {
          k++;
          const nombre = opc('new') ? 'new' : id();
          x = { e: 'ref', obj: x, nombre, l };
          continue;
        }
        if (es('[')) { k++; const i = expresion(); tomar(']'); x = { e: 'indice', arr: x, i, l }; continue; }
        if (es('++') || es('--')) { k++; x = { e: 'post', op: t.v, a: x, l }; continue; }
        return x;
      }
    }
    function inicializadorDeArreglo() {
      const l = ver().l; tomar('{');
      const vs = [];
      while (!opc('}')) { vs.push(es('{') ? inicializadorDeArreglo() : expresion()); if (!es('}')) tomar(','); }
      return { e: 'arrInit', vs, l };
    }
    function switchExpr() {
      const l = ver().l;
      tomar('switch'); tomar('('); const sel = expresion(); tomar(')'); tomar('{');
      const casos = [];
      let flecha = null;
      while (!opc('}')) {
        const etiquetas = []; let def = false;
        for (;;) {
          if (opc('default')) def = true;
          else { tomar('case'); do { if (es('null')) { k++; etiquetas.push({ e: 'lit', v: null, tipo: 'null' }); } else etiquetas.push(ternario()); } while (opc(',')); }
          if (es('->')) { k++; flecha = true; break; }
          tomar(':'); flecha = false;
          if (!es('case') && !es('default')) break;
        }
        let cuerpo;
        if (flecha) {
          if (es('{')) cuerpo = bloque();
          else if (es('throw')) cuerpo = sentencia();
          else { const e = expresion(); tomar(';'); cuerpo = { s: 'yieldFlecha', e, l: ver().l }; }
          casos.push({ etiquetas, def, cuerpo: [cuerpo] });
        } else {
          const ss = [];
          while (!es('case') && !es('default') && !es('}')) ss.push(sentencia());
          casos.push({ etiquetas, def, cuerpo: ss });
        }
      }
      return { e: 'switch', sel, casos, flecha, l };
    }
    function primaria() {
      const t = ver(), l = t.l;
      if (t.t === 'num') { k++; return { e: 'lit', v: t.v, tipo: t.tipo, l }; }
      if (t.t === 'str') { k++; return { e: 'lit', v: t.v, tipo: 'String', l }; }
      if (t.t === 'chr') { k++; return { e: 'lit', v: t.v, tipo: 'char', l }; }
      if (t.t === 'kw') {
        if (t.v === 'true' || t.v === 'false') { k++; return { e: 'lit', v: t.v === 'true', tipo: 'boolean', l }; }
        if (t.v === 'null') { k++; return { e: 'lit', v: null, tipo: 'null', l }; }
        if (t.v === 'this') { k++; if (es('(')) return { e: 'thisLlamada', args: argumentos(), l }; return { e: 'this', l }; }
        if (t.v === 'super') {
          k++;
          if (es('(')) return { e: 'superLlamada', args: argumentos(), l };
          if (opc('::')) return { e: 'ref', obj: { e: 'super', l }, nombre: id(), l };
          tomar('.'); const nombre = id();
          if (es('(')) return { e: 'llamada', obj: { e: 'super', l }, nombre, args: argumentos(), l };
          return { e: 'campo', obj: { e: 'this', l }, nombre, l };
        }
        if (t.v === 'new') {
          k++;
          anotaciones();
          const bt = ver().t === 'kw' && PRIMITIVOS.has(ver().v) ? { n: ts[k++].v, d: 0 } : (() => { let n = id(); let as = null; if (es('<')) as = argsDeTipo(); while (es('.') && esId(1)) { k++; n = id(); if (es('<')) as = argsDeTipo(); } return { n, a: as, d: 0 }; })();
          if (es('[')) {
            const dims = [];
            let d = 0;
            while (es('[')) { k++; if (es(']')) { k++; d++; } else { dims.push(expresion()); tomar(']'); d++; } }
            const init = es('{') ? inicializadorDeArreglo() : null;
            return { e: 'newArr', t: bt, dims, d, init, l };
          }
          const args = argumentos();
          if (es('{')) {                                            // clase anónima
            const c = { tipo: 'class', nombre: '', mods: new Set(), padre: bt.n, interfaces: [], miembros: [], archivo, l, anonima: true, constantes: [] };
            cuerpoDeClase(c);
            return { e: 'new', t: bt, args, anonima: c, l };
          }
          return { e: 'new', t: bt, args, l };
        }
        if (t.v === 'switch') return switchExpr();
        if (PRIMITIVOS.has(t.v)) {                                // int.class, int[]::new
          k++; const d = dimensiones();
          if (opc('::')) { tomar('new'); return { e: 'ref', obj: { e: 'tipo', t: { n: t.v, d } }, nombre: 'new', l }; }
          if (opc('.')) { tomar('class'); return { e: 'claseLit', t: { e: 'tipo', t: { n: t.v, d } }, l }; }
          err('no esperaba «' + t.v + '»');
        }
      }
      if (t.t === 'op' && t.v === '(') { k++; const e = expresion(); tomar(')'); return { e: 'paren', a: e, l }; }
      if (t.t === 'id') {
        // String[]::new  ·  List<String>::size (raro)
        if (es('[', 1) && es(']', 2)) {
          const g = k; const tt = tipo();
          if (opc('::')) { tomar('new'); return { e: 'ref', obj: { e: 'tipo', t: tt }, nombre: 'new', l }; }
          if (opc('.')) { tomar('class'); return { e: 'claseLit', t: { e: 'tipo', t: tt }, l }; }
          k = g;
        }
        k++;
        if (es('(')) return { e: 'llamada', obj: null, nombre: t.v, args: argumentos(), l };
        return { e: 'var', nombre: t.v, l };
      }
      err('no esperaba esto');
    }
    return unidad();
  }

  // ═════════════════════════════ 3) Los valores de Java ═════════════════════════════
  class D { constructor(v) { this.v = v; } }              // double (y float)
  class Ch { constructor(c) { this.c = c; } }             // char
  // int, short y byte son números de JS; long es BigInt; boolean es boolean; String es string de JS
  const esInt = v => typeof v === 'number';
  const esLong = v => typeof v === 'bigint';
  const esNum = v => typeof v === 'number' || typeof v === 'bigint' || v instanceof D || v instanceof Ch;
  const aNumero = v => typeof v === 'number' ? v : typeof v === 'bigint' ? Number(v) : v instanceof D ? v.v : v instanceof Ch ? v.c : NaN;
  const L = x => BigInt.asIntN(64, x);

  // Double.toString de Java (el más corto que identifica el número, como Java 19+)
  function dobleATexto(x) {
    if (Number.isNaN(x)) return 'NaN';
    if (x === Infinity) return 'Infinity';
    if (x === -Infinity) return '-Infinity';
    if (x === 0) return Object.is(x, -0) ? '-0.0' : '0.0';
    const a = Math.abs(x);
    if (a >= 1e-3 && a < 1e7) { const s = String(x); return s.includes('.') ? s : s + '.0'; }
    const [m, e] = x.toExponential().split('e');
    return (m.includes('.') ? m : m + '.0') + 'E' + (e[0] === '+' ? e.slice(1) : e);
  }

  // ═════════════════════════════ 4) Las colecciones y demás objetos de la biblioteca ═════════════════════════════
  const JAVA_ESPACIO = new Set([9, 10, 11, 12, 13, 28, 29, 30, 31, 32, 0x1680, 0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2008, 0x2009,
    0x200A, 0x2028, 0x2029, 0x205F, 0x3000]);                          // Character.isWhitespace (sin los espacios duros)
  const esEspacioJava = c => JAVA_ESPACIO.has(c);
  function hashTexto(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (Math.imul(h, 31) + s.charCodeAt(i)) | 0; return h; }
  const bufDoble = new DataView(new ArrayBuffer(8));
  function hashDoble(x) {
    if (x === 0 && !Object.is(x, -0)) return 0;
    bufDoble.setFloat64(0, Number.isNaN(x) ? NaN : x);
    return (bufDoble.getInt32(0) ^ bufDoble.getInt32(4)) | 0;
  }
  let siguienteIdentidad = 0x1b6d3586;
  const identidades = new WeakMap();
  function identidad(o) { if (!identidades.has(o)) { identidades.set(o, siguienteIdentidad); siguienteIdentidad = (Math.imul(siguienteIdentidad, 1103515245) + 12345) | 0; } return identidades.get(o); }

  class JArr { constructor(t, a) { this.t = t; this.a = a; } }                       // t: tipo de los elementos
  class JLista { constructor(a, soloLectura) { this.a = a || []; this.ro = !!soloLectura; } }
  class JMapa {                                                                        // HashMap, LinkedHashMap y TreeMap
    constructor(clase, cmp, capacidad) {
      this.clase = clase; this.cmp = cmp || null; this.e = []; this.ro = false;
      this.cap = 16; if (capacidad) { let c = 1; while (c < capacidad) c *= 2; this.cap = Math.max(1, c); }
    }
  }
  class JConjunto { constructor(mapa) { this.m = mapa; this.ro = false; } }          // HashSet, LinkedHashSet, TreeSet
  class JEntrada { constructor(k, v, h) { this.k = k; this.v = v; this.h = h; } }
  class JStream { constructor(a, tipo) { this.a = a; this.tipo = tipo || 'obj'; } }  // obj · int · long · double
  class JOpcional { constructor(hay, v, tipo) { this.hay = hay; this.v = v; this.tipo = tipo || 'obj'; } }
  class JFn { constructor(llamar, info) { this.llamar = llamar; Object.assign(this, info || {}); } }   // lambdas y referencias a métodos
  class JColector { constructor(c, o) { this.c = c; Object.assign(this, o); } }
  class JSB { constructor(s) { this.s = s || ''; } }                                   // StringBuilder
  class JRuta { constructor(s) { this.s = s; } }                                       // Path y File
  class JLector { constructor(lineas) { this.l = lineas; this.i = 0; } }               // BufferedReader
  class JScanner { constructor(texto) { this.t = texto; this.i = 0; } }
  class JImpresora { constructor(destino) { this.d = destino; } }                      // System.out y System.err
  class JClaseRef { constructor(c, nombre) { this.c = c; this.nombre = nombre; } }     // getClass(), X.class
  class JIterador { constructor(a) { this.a = a; this.i = 0; } }
  class JCharset { constructor(n) { this.n = n; } }
  class JObjeto { constructor(clase) { this.clase = clase; this.f = new Map(); } }     // un objeto de una clase del proyecto (o una excepción)
  class RefClase { constructor(c) { this.c = c; } }                                    // el nombre de una clase del proyecto usado como valor
  class RefLib { constructor(n) { this.n = n; } }                                      // el nombre de una clase de Java (Integer, Math, …)
  class RefPaquete { constructor(n) { this.n = n; } }                                  // java.util (en «java.util.TreeMap::new»)

  // Señales para cortar la ejecución
  class Retorno { constructor(v) { this.v = v; } }
  class Corte { constructor(etiqueta) { this.etiqueta = etiqueta; } }
  class Sigue { constructor(etiqueta) { this.etiqueta = etiqueta; } }
  class Lanzado { constructor(ex) { this.ex = ex; } }                                  // una excepción de Java en vuelo
  class Fin { constructor(codigo) { this.codigo = codigo; } }                          // System.exit
  class Rinde { constructor(v) { this.v = v; } }                                       // yield en un switch

  // Las excepciones y demás clases que trae Java
  const NATIVAS = {
    Object: [null, 'java.lang'], Throwable: ['Object', 'java.lang'], Exception: ['Throwable', 'java.lang'], Error: ['Throwable', 'java.lang'],
    RuntimeException: ['Exception', 'java.lang'], IllegalArgumentException: ['RuntimeException', 'java.lang'],
    IllegalStateException: ['RuntimeException', 'java.lang'], NumberFormatException: ['IllegalArgumentException', 'java.lang'],
    NullPointerException: ['RuntimeException', 'java.lang'], ArithmeticException: ['RuntimeException', 'java.lang'],
    IndexOutOfBoundsException: ['RuntimeException', 'java.lang'], ArrayIndexOutOfBoundsException: ['IndexOutOfBoundsException', 'java.lang'],
    StringIndexOutOfBoundsException: ['IndexOutOfBoundsException', 'java.lang'], UnsupportedOperationException: ['RuntimeException', 'java.lang'],
    ClassCastException: ['RuntimeException', 'java.lang'], NegativeArraySizeException: ['RuntimeException', 'java.lang'],
    NoSuchElementException: ['RuntimeException', 'java.util'], InputMismatchException: ['NoSuchElementException', 'java.util'],
    ConcurrentModificationException: ['RuntimeException', 'java.util'], IllegalFormatException: ['IllegalArgumentException', 'java.util'],
    IllegalFormatConversionException: ['IllegalFormatException', 'java.util'], MissingFormatArgumentException: ['IllegalFormatException', 'java.util'],
    UnknownFormatConversionException: ['IllegalFormatException', 'java.util'],
    IOException: ['Exception', 'java.io'], FileNotFoundException: ['IOException', 'java.io'], UncheckedIOException: ['RuntimeException', 'java.io'],
    FileSystemException: ['IOException', 'java.nio.file'], NoSuchFileException: ['FileSystemException', 'java.nio.file'],
    DateTimeException: ['RuntimeException', 'java.time'], DateTimeParseException: ['DateTimeException', 'java.time.format'],
    CloneNotSupportedException: ['Exception', 'java.lang'], InterruptedException: ['Exception', 'java.lang'],
  };
  const LIB_ESTATICAS = new Set(['Integer', 'Long', 'Double', 'Float', 'Short', 'Byte', 'Boolean', 'Character', 'Math', 'String', 'List', 'Map', 'Set',
    'Arrays', 'Collections', 'Collectors', 'Comparator', 'Files', 'Path', 'Paths', 'Objects', 'Optional', 'OptionalInt', 'OptionalDouble',
    'IntStream', 'LongStream', 'DoubleStream', 'Stream', 'System', 'StandardCharsets', 'Entry', 'Function', 'Predicate', 'Thread', 'Locale',
    'StrictMath', 'Number', 'CharSequence', 'Iterable', 'Collection', 'ArrayList', 'HashMap', 'TreeMap', 'LinkedHashMap', 'HashSet',
    'LinkedHashSet', 'TreeSet', 'StringBuilder', 'Scanner', 'File', 'BufferedReader', 'FileReader', 'InputStreamReader', 'Charset', 'Object',
    'LinkedList', 'ArrayDeque', 'Deque', 'Queue', 'Iterator', 'BigDecimal', 'RoundingMode', 'UnaryOperator', 'BinaryOperator', 'Supplier',
    'Consumer', 'BiFunction', 'BiConsumer', 'ToIntFunction', 'ToDoubleFunction', 'IntBinaryOperator', 'Runnable', 'Comparable']);

  // ═════════════════════════════ 5) El intérprete ═════════════════════════════
  function ejecutar(op) {
    const { fuentes, archivos = {}, args = [], idioma = 'es-AR', limitePasos = 3e7, entrada = '' } = op;
    const salida = [], errores = [];
    let pasos = 0;
    const SEP_DEC = /^es|^de|^fr|^it|^pt/.test(idioma) ? ',' : '.', SEP_MIL = SEP_DEC === ',' ? '.' : ',';

    // ── Las clases: las del proyecto y las nativas
    const clases = new Map();
    function nuevaClase(nombre, o) {
      return Object.assign({ nombre, fq: nombre, padre: null, interfaces: [], campos: [], metodos: new Map(), ctors: [], inits: [], initsE: [],
        estaticos: new Map(), iniciada: false, nativa: false, abstracta: false, interfaz: false, enumC: null, record: null, exterior: null,
        archivo: '', decl: null, entornoAnonimo: null }, o);
    }
    for (const [n, [p, pkg]] of Object.entries(NATIVAS)) clases.set(n, nuevaClase(n, { padreNombre: p, fq: pkg + '.' + n, nativa: true, iniciada: true }));
    function registrar(decl, exterior, paquete) {
      const c = nuevaClase(decl.nombre, { padreNombre: decl.padre || (decl.tipo === 'enum' ? 'Enum' : decl.tipo === 'record' ? 'Record' : 'Object'),
        interfaces: decl.interfaces, abstracta: decl.mods.has('abstract') || decl.tipo === 'interface', interfaz: decl.tipo === 'interface',
        archivo: decl.archivo, decl, exterior, fq: (paquete ? paquete + '.' : '') + (exterior ? exterior.nombre + '$' : '') + decl.nombre,
        estaticoAnidado: !exterior || decl.mods.has('static') || decl.tipo !== 'class' });
      for (const m of decl.miembros) {
        if (m.m === 'campo') c.campos.push({ nombre: m.nombre, t: m.t, estatico: m.mods.has('static'), init: m.init, l: m.l });
        else if (m.m === 'metodo') { if (!c.metodos.has(m.nombre)) c.metodos.set(m.nombre, []); c.metodos.get(m.nombre).push({ ...m, clase: c, estatico: m.mods.has('static') }); }
        else if (m.m === 'ctor') c.ctors.push({ ...m, clase: c });
        else if (m.m === 'init') (m.estatico ? c.initsE : c.inits).push(m.cuerpo);
        else if (m.m === 'clase') registrar(m.clase, c, paquete);
      }
      if (decl.tipo === 'enum') c.enumC = decl.constantes;
      if (decl.tipo === 'record') {
        c.record = decl.componentes;
        for (const comp of decl.componentes) {
          c.campos.push({ nombre: comp.nombre, t: comp.t, estatico: false, init: null });
          if (!c.metodos.has(comp.nombre)) c.metodos.set(comp.nombre, [{ m: 'metodo', mods: new Set(['public']), t: comp.t, nombre: comp.nombre, params: [], clase: c,
            cuerpo: { s: 'bloque', ss: [{ s: 'return', e: { e: 'campo', obj: { e: 'this' }, nombre: comp.nombre } }] } }]);
        }
      }
      if (clases.has(c.nombre) && !clases.get(c.nombre).nativa) falla('hay dos clases que se llaman ' + c.nombre, decl.archivo, decl.l);
      if (!decl.anonima) clases.set(c.nombre, c);
      return c;
    }
    clases.set('Enum', nuevaClase('Enum', { padreNombre: 'Object', fq: 'java.lang.Enum', nativa: true, iniciada: true }));
    clases.set('Record', nuevaClase('Record', { padreNombre: 'Object', fq: 'java.lang.Record', nativa: true, iniciada: true }));
    for (const [ruta, texto] of Object.entries(fuentes)) {
      const u = sintaxis(texto, ruta.split('/').pop());
      for (const d of u.clases) registrar(d, null, u.paquete);
    }
    const resolverPadres = () => { for (const c of clases.values()) if (c.padreNombre && !c.padre) c.padre = clases.get(c.padreNombre) || clases.get('Object'); };
    resolverPadres();
    clases.get('Object').padre = null;

    const esSubclase = (c, nombre) => { for (let x = c; x; x = x.padre) { if (x.nombre === nombre) return true; if (x.interfaces.some(i => i === nombre || (clases.has(i) && esSubclase(clases.get(i), nombre)))) return true; } return false; };

    // ── Excepciones
    function crearExcepcion(nombre, mensaje, causa) {
      const c = clases.get(nombre) || clases.get('RuntimeException');
      const o = new JObjeto(c);
      o.f.set('message', mensaje === undefined ? null : mensaje);
      o.f.set('cause', causa || null);
      return o;
    }
    const lanzar = (nombre, mensaje, causa) => { throw new Lanzado(crearExcepcion(nombre, mensaje, causa)); };
    const npe = () => lanzar('NullPointerException', null);
    function textoExcepcion(o) {
      const m = o.f.get('message');
      const deUsuario = metodoDe(o.clase, 'getMessage', 0);
      const msj = deUsuario && !deUsuario.clase.nativa ? llamarMetodo(o, 'getMessage', []) : m;
      return o.clase.fq + (msj !== null && msj !== undefined ? ': ' + aTexto(msj) : '');
    }

    // ── Tipos: conversiones al asignar y casts
    const NUMERICOS = new Set(['int', 'long', 'double', 'float', 'short', 'byte', 'char']);
    function convertir(v, t) {
      if (!t || t.d > 0 || v === null || v === undefined) return v;
      switch (t.n) {
        case 'int': case 'short': case 'byte': case 'Integer': case 'Short': case 'Byte':
          return v instanceof Ch ? v.c : v;
        case 'long': case 'Long': return typeof v === 'number' ? BigInt(v) : v instanceof Ch ? BigInt(v.c) : v;
        case 'double': case 'float': case 'Double': case 'Float': return typeof v === 'number' ? new D(v) : typeof v === 'bigint' ? new D(Number(v)) : v instanceof Ch ? new D(v.c) : v;
        case 'char': case 'Character': return typeof v === 'number' ? new Ch(v & 0xFFFF) : v;
        default: return v;
      }
    }
    function d2i(x) { if (Number.isNaN(x)) return 0; if (x >= 2147483647) return 2147483647; if (x <= -2147483648) return -2147483648; return Math.trunc(x) | 0; }
    function d2l(x) { if (Number.isNaN(x)) return 0n; if (x >= 9.223372036854776e18) return 9223372036854775807n; if (x <= -9.223372036854776e18) return -9223372036854775808n; return BigInt(Math.trunc(x)); }
    function castear(t, v, nodo, ctx) {
      if (t.d > 0) return v;
      if (v === null) { if (PRIMITIVOS.has(t.n)) npe(); return null; }
      switch (t.n) {
        case 'int': return typeof v === 'number' ? v : typeof v === 'bigint' ? Number(BigInt.asIntN(32, v)) : v instanceof D ? d2i(v.v) : v instanceof Ch ? v.c : err(nodo, 'cast a int');
        case 'long': return typeof v === 'bigint' ? v : typeof v === 'number' ? BigInt(v) : v instanceof D ? d2l(v.v) : v instanceof Ch ? BigInt(v.c) : err(nodo, 'cast a long');
        case 'double': case 'float': { const x = aNumero(v); if (Number.isNaN(x) && !(v instanceof D)) err(nodo, 'cast a double'); return new D(t.n === 'float' ? Math.fround(x) : x); }
        case 'short': return (castear({ n: 'int', d: 0 }, v, nodo) << 16) >> 16;
        case 'byte': return (castear({ n: 'int', d: 0 }, v, nodo) << 24) >> 24;
        case 'char': return new Ch(castear({ n: 'int', d: 0 }, v, nodo) & 0xFFFF);
        default: {
          const c = clases.get(t.n);
          if (c && !c.nativa && v instanceof JObjeto && !esSubclase(v.clase, t.n)) lanzar('ClassCastException', 'class ' + v.clase.fq + ' cannot be cast to class ' + c.fq);
          return v;
        }
      }
    }
    function valorPorDefecto(t) {
      if (t.d > 0) return null;
      switch (t.n) { case 'int': case 'short': case 'byte': return 0; case 'long': return 0n; case 'double': case 'float': return new D(0); case 'char': return new Ch(0); case 'boolean': return false; default: return null; }
    }
    function err(nodo, que) { falla('el ejecutor no sabe todavía: ' + que, nodo && nodo.archivo, nodo && nodo.l); }

    // ── A texto (String.valueOf)
    function aTexto(v) {
      if (v === null || v === undefined) return 'null';
      if (typeof v === 'string') return v;
      if (typeof v === 'number') return String(v);
      if (typeof v === 'bigint') return v.toString();
      if (typeof v === 'boolean') return v ? 'true' : 'false';
      if (v instanceof D) return dobleATexto(v.v);
      if (v instanceof Ch) return String.fromCharCode(v.c);
      if (v instanceof JObjeto) return aTexto(llamarMetodo(v, 'toString', []));
      if (v instanceof JLista) return '[' + v.a.map(x => x === v ? '(this Collection)' : aTexto(x)).join(', ') + ']';
      if (v instanceof JConjunto) return '[' + entradas(v.m).map(e => aTexto(e.k)).join(', ') + ']';
      if (v instanceof JMapa) return '{' + entradas(v).map(e => aTexto(e.k) + '=' + aTexto(e.v)).join(', ') + '}';
      if (v instanceof JEntrada) return aTexto(v.k) + '=' + aTexto(v.v);
      if (v instanceof JOpcional) {
        const n = v.tipo === 'int' ? 'OptionalInt' : v.tipo === 'double' ? 'OptionalDouble' : v.tipo === 'long' ? 'OptionalLong' : 'Optional';
        return v.hay ? n + '[' + aTexto(v.v) + ']' : n + '.empty';
      }
      if (v instanceof JSB) return v.s;
      if (v instanceof JRuta) return v.s;
      if (v instanceof JClaseRef) return (v.c && v.c.interfaz ? 'interface ' : 'class ') + (v.c ? v.c.fq : v.nombre);
      if (v instanceof JArr) return '[' + ({ int: 'I', long: 'J', double: 'D', char: 'C', boolean: 'Z', byte: 'B', short: 'S', float: 'F' }[v.t.n] || 'L' + nombreFq(v.t.n) + ';') + '@' + (identidad(v) >>> 0).toString(16);
      if (v instanceof JFn) return 'Lambda$' + (identidad(v) >>> 0).toString(16);
      if (v instanceof JCharset) return v.n;
      if (v instanceof JStream) return 'java.util.stream.ReferencePipeline@' + (identidad(v) >>> 0).toString(16);
      return String(v);
    }
    const nombreFq = n => clases.has(n) ? clases.get(n).fq : (['String', 'Integer', 'Long', 'Double', 'Object', 'Character', 'Boolean'].includes(n) ? 'java.lang.' + n : n);

    // ── Igualdad, hash y orden de Java
    function iguales(a, b) {
      if (a === b) return true;
      if (a === null || b === null || a === undefined || b === undefined) return false;
      if (typeof a === 'string' || typeof b === 'string') return a === b;
      if (typeof a === 'number' && typeof b === 'number') return a === b;
      if (typeof a === 'bigint' && typeof b === 'bigint') return a === b;
      if (a instanceof D && b instanceof D) return a.v === b.v || (Number.isNaN(a.v) && Number.isNaN(b.v));
      if (a instanceof Ch && b instanceof Ch) return a.c === b.c;
      if (a instanceof JObjeto) return !!llamarMetodo(a, 'equals', [b]);
      if (a instanceof JLista && (b instanceof JLista)) return a.a.length === b.a.length && a.a.every((x, i) => iguales(x, b.a[i]));
      if (a instanceof JMapa && b instanceof JMapa) return a.e.length === b.e.length && a.e.every(e => { const o = buscarEntrada(b, e.k); return o && iguales(e.v, o.v); });
      if (a instanceof JConjunto && b instanceof JConjunto) return a.m.e.length === b.m.e.length && a.m.e.every(e => !!buscarEntrada(b.m, e.k));
      if (a instanceof JEntrada && b instanceof JEntrada) return iguales(a.k, b.k) && iguales(a.v, b.v);
      if (a instanceof JOpcional && b instanceof JOpcional) return a.hay === b.hay && (!a.hay || iguales(a.v, b.v));
      if (a instanceof JClaseRef && b instanceof JClaseRef) return a.c === b.c && a.nombre === b.nombre;
      return false;
    }
    function hash(v) {
      if (v === null || v === undefined) return 0;
      if (typeof v === 'string') return hashTexto(v);
      if (typeof v === 'number') return v | 0;
      if (typeof v === 'bigint') return Number(BigInt.asIntN(32, v ^ (v >> 32n)));
      if (typeof v === 'boolean') return v ? 1231 : 1237;
      if (v instanceof D) return hashDoble(v.v);
      if (v instanceof Ch) return v.c;
      if (v instanceof JObjeto) return llamarMetodo(v, 'hashCode', []) | 0;
      if (v instanceof JLista) return v.a.reduce((h, x) => (Math.imul(h, 31) + hash(x)) | 0, 1);
      if (v instanceof JConjunto) return v.m.e.reduce((h, e) => (h + hash(e.k)) | 0, 0);
      if (v instanceof JMapa) return v.e.reduce((h, e) => (h + (hash(e.k) ^ hash(e.v))) | 0, 0);
      if (v instanceof JEntrada) return hash(v.k) ^ hash(v.v);
      return identidad(v);
    }
    function compararNatural(a, b) {
      if (a === null || b === null) npe();
      if (typeof a === 'string' && typeof b === 'string') {
        const n = Math.min(a.length, b.length);
        for (let i = 0; i < n; i++) { const d = a.charCodeAt(i) - b.charCodeAt(i); if (d) return d; }
        return a.length - b.length;
      }
      if (esNum(a) && esNum(b)) {
        if (typeof a === 'bigint' && typeof b === 'bigint') return a < b ? -1 : a > b ? 1 : 0;
        const x = aNumero(a), y = aNumero(b);
        return x < y ? -1 : x > y ? 1 : 0;
      }
      if (typeof a === 'boolean' && typeof b === 'boolean') return a === b ? 0 : a ? 1 : -1;
      if (a instanceof JObjeto) {
        if (a.clase.enumC) return a.f.get('$ordinal') - b.f.get('$ordinal');
        if (!metodoDe(a.clase, 'compareTo', 1)) lanzar('ClassCastException', 'class ' + a.clase.fq + ' cannot be cast to class java.lang.Comparable');
        return aNumero(llamarMetodo(a, 'compareTo', [b]));
      }
      lanzar('ClassCastException', 'no se pueden comparar');
    }
    const comparadorDe = cmp => cmp ? (a, b) => aNumero(llamarFn(cmp, [a, b])) : compararNatural;
    function ordenar(a, cmp) {                      // estable, como List.sort / Collections.sort de Java
      const f = comparadorDe(cmp);
      return a.map((x, i) => [x, i]).sort((p, q) => f(p[0], q[0]) || p[1] - q[1]).map(p => p[0]);
    }

    // ── Mapas: HashMap con el orden de Java, LinkedHashMap en orden de llegada, TreeMap ordenado
    const dispersar = h => h ^ (h >>> 16);
    function entradas(m) {
      if (m.clase !== 'HashMap') return m.e;
      return m.e.map((e, i) => [e, i]).sort((p, q) => ((dispersar(p[0].h) & (m.cap - 1)) - (dispersar(q[0].h) & (m.cap - 1))) || p[1] - q[1]).map(p => p[0]);
    }
    function buscarEntrada(m, k) {
      if (m.clase === 'TreeMap') {
        if (k === null && !m.cmp) npe();
        const f = comparadorDe(m.cmp);
        let lo = 0, hi = m.e.length - 1;
        while (lo <= hi) { const mid = (lo + hi) >> 1, c = f(m.e[mid].k, k); if (c === 0) return m.e[mid]; if (c < 0) lo = mid + 1; else hi = mid - 1; }
        return null;
      }
      const h = hash(k);
      return m.e.find(e => e.h === h && iguales(e.k, k)) || null;
    }
    function poner(m, k, v) {
      if (m.ro) lanzar('UnsupportedOperationException', null);
      const e = buscarEntrada(m, k);
      if (e) { const viejo = e.v; e.v = v; return viejo; }
      if (m.clase === 'TreeMap') {
        const f = comparadorDe(m.cmp);
        if (k === null && !m.cmp) npe();
        let i = 0; while (i < m.e.length && f(m.e[i].k, k) < 0) i++;
        m.e.splice(i, 0, new JEntrada(k, v, 0));
      } else {
        m.e.push(new JEntrada(k, v, hash(k)));
        if (m.e.length > m.cap * 0.75) m.cap *= 2;
      }
      return null;
    }
    function sacar(m, k) {
      if (m.ro) lanzar('UnsupportedOperationException', null);
      const e = buscarEntrada(m, k);
      if (!e) return null;
      m.e.splice(m.e.indexOf(e), 1);
      return e.v;
    }
    const nuevoMapa = (clase, cmp, cap) => new JMapa(clase, cmp, cap);
    const nuevaLista = (a, ro) => new JLista(a, ro);
    const elementos = v => {
      if (v instanceof JLista) return v.a;
      if (v instanceof JConjunto) return entradas(v.m).map(e => e.k);
      if (v instanceof JArr) return v.a;
      if (v instanceof JStream) return v.a;
      if (v === null) npe();
      if (v instanceof JMapa) lanzar('ClassCastException', 'un Map no es una colección');
      return null;
    };

    // ── Archivos
    const normalizar = r => { const p = []; for (const x of String(r).replace(/\\/g, '/').split('/')) { if (x === '' || x === '.') continue; if (x === '..') p.pop(); else p.push(x); } return p.join('/'); };
    const ARCH = new Map(Object.entries(archivos).map(([r, t]) => [normalizar(r), t]));
    function leerArchivo(ruta, excepcion) {
      const r = normalizar(ruta);
      if (!ARCH.has(r)) {
        if (excepcion === 'FileNotFoundException') lanzar('FileNotFoundException', ruta + ' (No such file or directory)');
        lanzar('NoSuchFileException', ruta);
      }
      return ARCH.get(r);
    }
    const lineasDe = t => { const ls = t.split(/\r\n|\r|\n/); if (ls.length && ls[ls.length - 1] === '') ls.pop(); return ls; };

    // ── Formato (String.format, printf, formatted)
    function decimalesJava(x, prec) {      // %.Nf de Java: redondeo HALF_UP sobre el decimal más corto del double
      if (!Number.isFinite(x)) return Number.isNaN(x) ? 'NaN' : x > 0 ? 'Infinity' : '-Infinity';
      const neg = x < 0 || Object.is(x, -0);
      let s = Math.abs(x).toString();
      if (/e/.test(s)) { const [m, e] = s.split('e'); const ex = Number(e); let [ent, dec = ''] = m.split('.'); let dig = ent + dec, pos = ent.length + ex; if (pos <= 0) { dig = '0'.repeat(1 - pos) + dig; pos = 1; } while (dig.length < pos) dig += '0'; s = dig.slice(0, pos) + '.' + dig.slice(pos); }
      let [ent, dec = ''] = s.split('.');
      dec = dec.padEnd(prec + 1, '0');
      let num = (ent + dec.slice(0, prec)).split('').map(Number);
      if (Number(dec[prec]) >= 5) { let i = num.length - 1; while (i >= 0) { if (num[i] === 9) { num[i] = 0; i--; } else { num[i]++; break; } } if (i < 0) num.unshift(1); }
      const tot = num.join(''), corte = tot.length - prec;
      return { neg, ent: tot.slice(0, corte).replace(/^0+(?=\d)/, '') || '0', dec: tot.slice(corte) };
    }
    const agrupar = (ent, sep) => ent.replace(/\B(?=(\d{3})+(?!\d))/g, sep);
    function formatear(fmt, as, nodo) {
      let n = 0;
      const re = /%(\d+\$)?([-#+ 0,(]*)(\d+)?(\.\d+)?([a-zA-Z%])/g;
      return fmt.replace(re, (m, pos, flags, ancho, prec, conv) => {
        if (conv === 'n') return '\n';
        if (conv === '%') return '%';
        let v;
        if (pos) v = as[parseInt(pos, 10) - 1]; else { if (n >= as.length) lanzar('MissingFormatArgumentException', "Format specifier '" + m + "'"); v = as[n++]; }
        let s;
        const p = prec ? parseInt(prec.slice(1), 10) : null;
        switch (conv) {
          case 'd': {
            if (!(typeof v === 'number' || typeof v === 'bigint') && v !== null) lanzar('IllegalFormatConversionException', 'd != ' + claseDeValor(v));
            if (v === null) { s = 'null'; break; }
            const neg = v < 0; let t = (neg ? -BigInt(v) : BigInt(v)).toString();
            if (flags.includes(',')) t = agrupar(t, SEP_MIL);
            s = (neg ? (flags.includes('(') ? '(' : '-') : flags.includes('+') ? '+' : flags.includes(' ') ? ' ' : '') + t + (neg && flags.includes('(') ? ')' : '');
            if (flags.includes('0') && ancho) { const sig = /^[-+ (]/.test(s) ? s[0] : ''; s = sig + s.slice(sig.length).padStart(parseInt(ancho, 10) - sig.length, '0'); }
            break;
          }
          case 'f': case 'e': case 'E': {
            if (v === null) { s = 'null'; break; }
            if (!(v instanceof D)) lanzar('IllegalFormatConversionException', conv + ' != ' + claseDeValor(v));
            if (conv !== 'f') { const t = v.v.toExponential(p === null ? 6 : p).replace(/e([+-])(\d)$/, 'e$10$2'); s = (conv === 'E' ? t.toUpperCase() : t).replace('.', SEP_DEC); break; }
            const r = decimalesJava(v.v, p === null ? 6 : p);
            if (typeof r === 'string') { s = r; break; }
            s = (r.neg ? '-' : flags.includes('+') ? '+' : flags.includes(' ') ? ' ' : '') + (flags.includes(',') ? agrupar(r.ent, SEP_MIL) : r.ent) + (r.dec ? SEP_DEC + r.dec : '');
            if (flags.includes('0') && ancho) { const sig = /^[-+ ]/.test(s) ? s[0] : ''; s = sig + s.slice(sig.length).padStart(parseInt(ancho, 10) - sig.length, '0'); }
            break;
          }
          case 's': case 'S': s = aTexto(v); if (p !== null) s = s.slice(0, p); if (conv === 'S') s = s.toUpperCase(); break;
          case 'c': s = v instanceof Ch ? String.fromCharCode(v.c) : typeof v === 'number' ? String.fromCharCode(v) : aTexto(v); break;
          case 'b': case 'B': s = v === null ? 'false' : typeof v === 'boolean' ? String(v) : 'true'; break;
          case 'x': case 'X': s = (typeof v === 'bigint' ? BigInt.asUintN(64, v) : (v >>> 0)).toString(16); if (conv === 'X') s = s.toUpperCase(); break;
          case 'o': s = (v >>> 0).toString(8); break;
          case 'h': s = (hash(v) >>> 0).toString(16); break;
          default: lanzar('UnknownFormatConversionException', "Conversion = '" + conv + "'");
        }
        if (ancho) s = flags.includes('-') ? s.padEnd(parseInt(ancho, 10)) : s.padStart(parseInt(ancho, 10));
        return s;
      });
    }
    function claseDeValor(v) {
      if (typeof v === 'string') return 'java.lang.String';
      if (typeof v === 'number') return 'java.lang.Integer';
      if (typeof v === 'bigint') return 'java.lang.Long';
      if (v instanceof D) return 'java.lang.Double';
      if (v instanceof Ch) return 'java.lang.Character';
      if (typeof v === 'boolean') return 'java.lang.Boolean';
      if (v instanceof JObjeto) return v.clase.fq;
      return 'java.lang.Object';
    }

    // ── Números de texto: Integer.parseInt, Long.parseLong, Double.parseDouble
    function parseEntero(s, largo) {
      if (s === null) lanzar('NumberFormatException', 'Cannot parse null string: null');
      if (!/^[+-]?\d+$/.test(s)) lanzar('NumberFormatException', s === '' ? 'For input string: ""' + (largo ? '' : '') : 'For input string: "' + s + '"');
      const b = BigInt(s);
      if (largo) { if (b > 9223372036854775807n || b < -9223372036854775808n) lanzar('NumberFormatException', 'For input string: "' + s + '"'); return b; }
      if (b > 2147483647n || b < -2147483648n) lanzar('NumberFormatException', 'For input string: "' + s + '"' + (s.length > 10 ? '' : ''));
      return Number(b);
    }
    function parseDoble(s) {
      if (s === null) npe();
      const t = s.replace(/^[\u0000- ]+|[\u0000- ]+$/g, '');
      if (t === '') lanzar('NumberFormatException', 'empty String');
      const m = t.match(/^([+-]?)(NaN|Infinity|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)[fFdD]?$/);
      if (!m) lanzar('NumberFormatException', 'For input string: "' + t + '"');
      return new D(Number(m[1] + m[2]));
    }

    // ── Texto: split de Java
    function regexDeJava(r) {
      // las expresiones regulares de Java y JS se parecen; lo que no existe en JS se avisa
      if (/\(\?<[=!]|\\p\{|\+\+|\*\+|\?\+/.test(r)) { /* posesivos o propiedades unicode: JS los entiende distinto */ }
      try { return new RegExp(r.replace(/\\Q(.*?)\\E/g, (m, x) => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')), 'g'); }
      catch (e) { lanzar('PatternSyntaxException', 'expresión regular inválida: ' + r); }
    }
    function split(s, r, limite) {
      const re = regexDeJava(r), partes = [];
      let indice = 0, m;
      const limitado = limite > 0;
      re.lastIndex = 0;
      while ((m = re.exec(s))) {
        if (m[0] === '') { re.lastIndex++; if (m.index === 0 || m.index >= s.length) continue; }
        if (limitado && partes.length >= limite - 1) break;
        if (indice === 0 && m.index === 0 && m[0] === '') continue;
        partes.push(s.slice(indice, m.index));
        indice = m.index + m[0].length;
      }
      if (indice === 0 && partes.length === 0) return [s];
      partes.push(s.slice(indice));
      if (limite === 0) while (partes.length && partes[partes.length - 1] === '') partes.pop();
      return partes;
    }
    const trim = s => s.replace(/^[\u0000- ]+|[\u0000- ]+$/g, '');
    const strip = (s, ini = true, fin = true) => { let a = 0, b = s.length; if (ini) while (a < b && esEspacioJava(s.charCodeAt(a))) a++; if (fin) while (b > a && esEspacioJava(s.charCodeAt(b - 1))) b--; return s.slice(a, b); };

    // ═══ Ejecución: entornos, búsqueda de nombres y llamadas
    class Entorno {
      constructor(padre) { this.padre = padre; this.vars = new Map(); }
      buscar(n) { for (let e = this; e; e = e.padre) { const v = e.vars.get(n); if (v) return v; } return null; }
      definir(n, v, t) { this.vars.set(n, { v, t }); }
    }
    function iniciarClase(c) {
      if (c.iniciada) return;
      c.iniciada = true;
      if (c.padre) iniciarClase(c.padre);
      const ctx = { clase: c, yo: null, env: new Entorno(null) };
      if (c.enumC) {
        c.enumC.forEach((k, i) => {
          const o = construir(c, k.args.map(a => evaluar(a, ctx)), { archivo: c.archivo, l: k.l });
          o.f.set('$nombre', k.nombre); o.f.set('$ordinal', i);
          c.estaticos.set(k.nombre, { v: o, t: { n: c.nombre, d: 0 } });
        });
      }
      for (const f of c.campos) if (f.estatico) c.estaticos.set(f.nombre, { v: f.init ? convertir(valorInit(f, ctx), f.t) : valorPorDefecto(f.t), t: f.t });
      for (const b of c.initsE) ejecutarSentencia(b, ctx);
    }
    function valorInit(f, ctx) { return f.init.e === 'arrInit' ? arregloDesdeInit(f.init, f.t, ctx) : evaluar(f.init, ctx); }
    function campoEstatico(c, n) { for (let x = c; x; x = x.padre) { iniciarClase(x); if (x.estaticos.has(n)) return x.estaticos.get(n); for (const i of x.interfaces) { const ic = clases.get(i); if (ic) { const r = campoEstatico(ic, n); if (r) return r; } } } return null; }
    function tipoDeCampo(c, n) { for (let x = c; x; x = x.padre) { const f = x.campos.find(y => y.nombre === n && !y.estatico); if (f) return f.t; } return null; }
    function metodoDe(c, nombre, aridad, args) {
      for (let x = c; x; x = x.padre) {
        const ms = (x.metodos.get(nombre) || []).filter(m => aceptaAridad(m, aridad));
        if (ms.length) return elegirSobrecarga(ms, args);
        for (const i of x.interfaces) { const ic = clases.get(i); if (ic) { const m = metodoDe(ic, nombre, aridad, args); if (m && m.cuerpo) return m; } }
      }
      return null;
    }
    const esVarargs = m => m.params.length && m.params[m.params.length - 1].t.d > 0 && m.varargs !== false;
    const aceptaAridad = (m, n) => m.params.length === n || (esVarargs(m) && n >= m.params.length - 1);
    function puntaje(t, v) {
      if (v === null) return PRIMITIVOS.has(t.n) && t.d === 0 ? -100 : 1;
      if (t.d > 0) return v instanceof JArr ? 3 : -10;
      switch (t.n) {
        case 'int': case 'Integer': case 'short': case 'byte': return typeof v === 'number' ? 3 : v instanceof Ch ? 2 : -10;
        case 'long': case 'Long': return typeof v === 'bigint' ? 3 : typeof v === 'number' || v instanceof Ch ? 1 : -10;
        case 'double': case 'Double': case 'float': case 'Float': return v instanceof D ? 3 : esNum(v) ? 1 : -10;
        case 'char': case 'Character': return v instanceof Ch ? 3 : -10;
        case 'boolean': case 'Boolean': return typeof v === 'boolean' ? 3 : -10;
        case 'String': case 'CharSequence': return typeof v === 'string' ? 3 : -10;
        case 'Object': return 0;
        default: { const c = clases.get(t.n); if (c && !c.nativa) return v instanceof JObjeto && esSubclase(v.clase, t.n) ? 2 : -10; return 0; }
      }
    }
    function elegirSobrecarga(ms, args) {
      if (ms.length === 1 || !args) return ms[0];
      let mejor = ms[0], p = -Infinity;
      for (const m of ms) { const s = m.params.reduce((a, q, i) => a + (i < args.length ? puntaje(q.t, args[i]) : 0), 0) - (m.params.length !== args.length ? 5 : 0); if (s > p) { p = s; mejor = m; } }
      return mejor;
    }
    function enlazarArgs(m, args) {
      if (esVarargs(m) && !(args.length === m.params.length && (args[args.length - 1] instanceof JArr || args[args.length - 1] === null))) {
        const fijos = m.params.length - 1, t = m.params[fijos].t;
        return args.slice(0, fijos).concat([new JArr({ n: t.n, d: t.d - 1 }, args.slice(fijos).map(v => convertir(v, { n: t.n, d: t.d - 1 })))]);
      }
      return args;
    }
    function invocar(m, yo, args, nodo) {
      if (!m.cuerpo) { if (m.mods && m.mods.has('abstract')) lanzar('AbstractMethodError', m.nombre); err(nodo, 'el método ' + m.nombre + ' no tiene cuerpo'); }
      const env = new Entorno(m.clase.entornoAnonimo || null);
      const as = enlazarArgs(m, args);
      m.params.forEach((p, i) => env.definir(p.nombre, convertir(as[i], p.t), p.t));
      const ctx = { clase: m.clase, yo, env, metodo: m };
      try { ejecutarSentencia(m.cuerpo, ctx); }
      catch (e) { if (e instanceof Retorno) return m.t ? convertir(e.v, m.t) : e.v; throw e; }
      return undefined;
    }
    function construir(c, args, nodo) {
      if (c.abstracta) err(nodo, 'crear un objeto de una clase abstracta (' + c.nombre + ')');
      iniciarClase(c);
      if (c.nativa && esSubclase(c, 'Throwable')) return construirExcepcion(c, args);
      const o = new JObjeto(c);
      inicializarObjeto(c, o, args, nodo);
      return o;
    }
    function construirExcepcion(c, args) {
      const o = new JObjeto(c);
      if (args.length === 0) { o.f.set('message', null); o.f.set('cause', null); }
      else if (args[0] instanceof JObjeto && esSubclase(args[0].clase, 'Throwable')) { o.f.set('message', textoExcepcion(args[0])); o.f.set('cause', args[0]); }
      else { o.f.set('message', args[0] === null ? null : aTexto(args[0])); o.f.set('cause', args[1] || null); }
      return o;
    }
    function inicializarObjeto(c, o, args, nodo) {
      if (c.nativa) {
        if (esSubclase(c, 'Throwable')) { const e = construirExcepcion(c, args); o.f.set('message', e.f.get('message')); o.f.set('cause', e.f.get('cause')); }
        return;
      }
      if (c.record && !c.ctors.some(k => !k.compacto && k.params.length === c.record.length)) {        // constructor canónico del record
        const env = new Entorno(null);
        c.record.forEach((comp, i) => env.definir(comp.nombre, convertir(args[i], comp.t), comp.t));
        const compacto = c.ctors.find(k => k.compacto);
        if (compacto) { try { ejecutarSentencia(compacto.cuerpo, { clase: c, yo: o, env }); } catch (e) { if (!(e instanceof Retorno)) throw e; } }
        c.record.forEach(comp => o.f.set(comp.nombre, env.buscar(comp.nombre).v));
        return;
      }
      const ks = c.ctors.filter(k => !k.compacto && aceptaAridad(k, args.length));
      if (!ks.length && (c.ctors.filter(k => !k.compacto).length || args.length)) err(nodo, 'no hay un constructor de ' + c.nombre + ' con ' + args.length + ' parámetros');
      const k = ks.length ? elegirSobrecarga(ks, args) : null;
      const env = new Entorno(c.entornoAnonimo || null);
      if (k) { const as = enlazarArgs(k, args); k.params.forEach((p, i) => env.definir(p.nombre, convertir(as[i], p.t), p.t)); }
      const ctx = { clase: c, yo: o, env, metodo: k };
      const ss = k ? k.cuerpo.ss : [];
      let desde = 0;
      const primera = ss[0];
      if (primera && primera.s === 'expr' && primera.e.e === 'thisLlamada') {
        inicializarObjeto(c, o, primera.e.args.map(a => evaluar(a, ctx)), primera.e);
        desde = 1;
      } else {
        let argsPadre = [];
        if (primera && primera.s === 'expr' && primera.e.e === 'superLlamada') { argsPadre = primera.e.args.map(a => evaluar(a, ctx)); desde = 1; }
        if (c.padre) { iniciarClase(c.padre); if (c.anonimaDe && c.padre.nativa === false) inicializarObjeto(c.padre, o, c.argsAnonimos || [], nodo); else inicializarObjeto(c.padre, o, argsPadre, primera || nodo); }
        for (const f of c.campos) if (!f.estatico) o.f.set(f.nombre, f.init ? convertir(valorInit(f, ctx), f.t) : valorPorDefecto(f.t));
        for (const b of c.inits) ejecutarSentencia(b, ctx);
      }
      try { for (let i = desde; i < ss.length; i++) ejecutarSentencia(ss[i], ctx); }
      catch (e) { if (!(e instanceof Retorno)) throw e; }
    }

    // Llamar a un método sobre cualquier valor
    function llamarMetodo(r, nombre, args, nodo, ctx) {
      if (r instanceof JObjeto) {
        const m = metodoDe(r.clase, nombre, args.length, args);
        if (m && !m.estatico) return invocar(m, r, args, nodo);
        if (m && m.estatico) return invocar(m, null, args, nodo);
        return metodoDeObject(r, nombre, args, nodo);
      }
      if (r instanceof RefClase) return llamarEstatico(r.c, nombre, args, nodo);
      if (r instanceof RefLib) return estaticoLib(r.n, nombre, args, nodo, ctx);
      if (r === null || r === undefined) lanzar('NullPointerException', 'Cannot invoke "' + nombre + '()" because value is null');
      return metodoLib(r, nombre, args, nodo);
    }
    function llamarEstatico(c, nombre, args, nodo) {
      iniciarClase(c);
      if (c.enumC && nombre === 'values' && args.length === 0) return new JArr({ n: c.nombre, d: 0 }, c.enumC.map(k => c.estaticos.get(k.nombre).v));
      if (c.enumC && nombre === 'valueOf' && args.length === 1) { const k = c.estaticos.get(args[0]); if (!k || !c.enumC.some(x => x.nombre === args[0])) lanzar('IllegalArgumentException', 'No enum constant ' + c.fq + '.' + args[0]); return k.v; }
      const m = metodoDe(c, nombre, args.length, args);
      if (!m) err(nodo, 'no encuentro el método ' + c.nombre + '.' + nombre + '(' + args.length + ' parámetros)');
      return invocar(m, null, args, nodo);
    }
    function metodoDeObject(o, nombre, args, nodo) {
      const c = o.clase;
      switch (nombre) {
        case 'toString':
          if (c.enumC) return o.f.get('$nombre');
          if (c.record) return c.nombre + '[' + c.record.map(k => k.nombre + '=' + aTexto(o.f.get(k.nombre))).join(', ') + ']';
          if (esSubclase(c, 'Throwable')) return textoExcepcion(o);
          return c.fq + '@' + (identidad(o) >>> 0).toString(16);
        case 'equals': return c.record ? args[0] instanceof JObjeto && args[0].clase === c && c.record.every(k => iguales(o.f.get(k.nombre), args[0].f.get(k.nombre))) : o === args[0];
        case 'hashCode': return c.record ? c.record.reduce((h, k) => (Math.imul(h, 31) + hash(o.f.get(k.nombre))) | 0, 0) : identidad(o);
        case 'getClass': return new JClaseRef(c);
        case 'name': if (c.enumC) return o.f.get('$nombre'); break;
        case 'ordinal': if (c.enumC) return o.f.get('$ordinal'); break;
        case 'compareTo': if (c.enumC) return o.f.get('$ordinal') - args[0].f.get('$ordinal'); break;
        case 'getMessage': case 'getLocalizedMessage': return o.f.get('message');
        case 'getCause': return o.f.get('cause');
        case 'printStackTrace': errores.push(textoExcepcion(o) + '\n'); return undefined;
        case 'initCause': o.f.set('cause', args[0]); return o;
        case 'addSuppressed': return undefined;
        case 'getStackTrace': return new JArr({ n: 'StackTraceElement', d: 0 }, []);
        case 'describeConstable': break;
      }
      err(nodo, 'el método ' + nombre + ' en un objeto de ' + c.nombre);
    }

    // Funciones (lambdas y referencias a métodos)
    function llamarFn(f, args) {
      if (f instanceof JFn) return f.llamar(args);
      if (f instanceof JObjeto) {        // un objeto de una clase que implementa la interfaz (Comparator, Function, …)
        const nombre = ['compare', 'apply', 'test', 'accept', 'get', 'applyAsInt', 'applyAsDouble', 'applyAsLong', 'run', 'call'].find(n => metodoDe(f.clase, n, args.length));
        if (nombre) return llamarMetodo(f, nombre, args);
      }
      if (f === null) npe();
      falla('esto no es una función: ' + aTexto(f));
    }
    const fn = (llamar, info) => new JFn(llamar, info);
    function comparadorPorClave(clave, cmpClave) { return fn(([a, b]) => { const x = llamarFn(clave, [a]), y = llamarFn(clave, [b]); return cmpClave ? llamarFn(cmpClave, [x, y]) : compararNatural(x, y); }, { cmp: true }); }
    function metodoDeFn(f, nombre, args) {
      switch (nombre) {
        case 'apply': case 'test': case 'accept': case 'get': case 'applyAsInt': case 'applyAsDouble': case 'applyAsLong': case 'compare': case 'run': case 'call': return llamarFn(f, args);
        case 'reversed': return fn(([a, b]) => llamarFn(f, [b, a]), { cmp: true });
        case 'thenComparing': case 'thenComparingInt': case 'thenComparingDouble': case 'thenComparingLong': {
          const otro = args.length === 2 ? comparadorPorClave(args[0], args[1]) : esComparador(args[0]) ? args[0] : comparadorPorClave(args[0]);
          return fn(([a, b]) => { const c = aNumero(llamarFn(f, [a, b])); return c !== 0 ? c : llamarFn(otro, [a, b]); }, { cmp: true });
        }
        case 'negate': return fn(as => !llamarFn(f, as));
        case 'and': return fn(as => !!llamarFn(f, as) && !!llamarFn(args[0], as));
        case 'or': return fn(as => !!llamarFn(f, as) || !!llamarFn(args[0], as));
        case 'andThen': return fn(as => { const r = llamarFn(f, as); return f.consumidor ? llamarFn(args[0], as) : llamarFn(args[0], [r]); });
        case 'compose': return fn(as => llamarFn(f, [llamarFn(args[0], as)]));
        case 'identity': return fn(([x]) => x);
        case 'equals': return f === args[0];
        case 'hashCode': return identidad(f);
        case 'toString': return aTexto(f);
      }
      falla('el método ' + nombre + ' sobre una función');
    }
    const esComparador = f => (f instanceof JFn && (f.cmp || f.aridad === 2)) || (f instanceof JObjeto && !!metodoDe(f.clase, 'compare', 2));

    // ═══ Evaluar expresiones
    function evaluar(e, ctx) {
      if (++pasos > limitePasos) falla('el programa tardó demasiado (¿un ciclo que no termina?)');
      switch (e.e) {
        case 'lit': return e.tipo === 'double' ? new D(e.v) : e.tipo === 'char' ? new Ch(e.v) : e.v;
        case 'paren': return evaluar(e.a, ctx);
        case 'var': return leerNombre(e, ctx);
        case 'this': return ctx.yo;
        case 'campo': return leerCampo(e, ctx);
        case 'indice': {
          const a = evaluar(e.arr, ctx), i = aIndice(evaluar(e.i, ctx));
          if (a === null) npe();
          if (i < 0 || i >= a.a.length) lanzar('ArrayIndexOutOfBoundsException', 'Index ' + i + ' out of bounds for length ' + a.a.length);
          return a.a[i];
        }
        case 'llamada': return evaluarLlamada(e, ctx);
        case 'new': return evaluarNew(e, ctx);
        case 'newArr': {
          if (e.init) return arregloDesdeInit(e.init, { n: e.t.n, d: e.d }, ctx);
          const tams = e.dims.map(x => aIndice(evaluar(x, ctx)));
          const crear = (nivel, d) => {
            const n = tams[nivel];
            if (n < 0) lanzar('NegativeArraySizeException', String(n));
            const te = { n: e.t.n, d: d - 1 };
            return new JArr(te, Array.from({ length: n }, () => nivel + 1 < tams.length ? crear(nivel + 1, d - 1) : valorPorDefecto(te)));
          };
          return crear(0, e.d);
        }
        case 'arrInit': return arregloDesdeInit(e, { n: 'Object', d: 1 }, ctx);
        case 'un': {
          const a = evaluar(e.a, ctx);
          if (e.op === '!') return !a;
          if (e.op === '+') return a instanceof Ch ? a.c : a;
          if (e.op === '-') return a instanceof D ? new D(-a.v) : typeof a === 'bigint' ? L(-a) : (-(a instanceof Ch ? a.c : a)) | 0;
          if (e.op === '~') return typeof a === 'bigint' ? L(~a) : ~(a instanceof Ch ? a.c : a);
          break;
        }
        case 'bin': return evaluarBinaria(e, ctx);
        case 'cond': return evaluar(e.c, ctx) ? evaluar(e.a, ctx) : evaluar(e.b, ctx);
        case 'cast': return castear(e.t, evaluar(e.a, ctx), e, ctx);
        case 'instanceof': {
          const v = evaluar(e.a, ctx);
          const si = v !== null && esDeTipo(v, e.t);
          if (si && e.nombre) ctx.env.definir(e.nombre, v, e.t);
          return si;
        }
        case 'asig': return asignar(e, ctx);
        case 'pre': case 'post': {
          const viejo = evaluar(e.a, ctx), t = tipoDestino(e.a, ctx);
          const nuevo = castear(t || { n: tipoNumerico(viejo), d: 0 }, aritmetica(e.op === '++' ? '+' : '-', viejo, 1, e), e);
          guardar(e.a, nuevo, ctx);
          return e.e === 'pre' ? nuevo : viejo;
        }
        case 'lambda': return crearLambda(e, ctx);
        case 'ref': return crearReferencia(e, ctx);
        case 'switch': return evaluarSwitch(e, ctx, true);
        case 'claseLit': { const n = e.t.e === 'var' ? e.t.nombre : e.t.e === 'tipo' ? e.t.t.n : null; return new JClaseRef(clases.get(n) || null, n); }
        case 'thisLlamada': case 'superLlamada': err(e, 'this(...) o super(...) fuera del comienzo de un constructor');
        case 'tipo': return new RefLib(e.t.n);
      }
      err(e, 'la expresión ' + e.e);
    }
    const aIndice = v => v instanceof Ch ? v.c : typeof v === 'number' ? v : err(null, 'índice que no es int');
    function tipoNumerico(v) { return typeof v === 'bigint' ? 'long' : v instanceof D ? 'double' : v instanceof Ch ? 'char' : 'int'; }
    function arregloDesdeInit(init, t, ctx) {
      const te = { n: t.n, d: t.d - 1 };
      return new JArr(te, init.vs.map(x => x.e === 'arrInit' ? arregloDesdeInit(x, te, ctx) : convertir(evaluar(x, ctx), te)));
    }
    function esDeTipo(v, t) {
      if (t.d > 0) return v instanceof JArr;
      switch (t.n) {
        case 'Object': return true;
        case 'String': case 'CharSequence': return typeof v === 'string';
        case 'Integer': return typeof v === 'number';
        case 'Long': return typeof v === 'bigint';
        case 'Double': return v instanceof D;
        case 'Number': return typeof v === 'number' || typeof v === 'bigint' || v instanceof D;
        case 'Character': return v instanceof Ch;
        case 'Boolean': return typeof v === 'boolean';
        case 'Comparable': return typeof v === 'string' || esNum(v) || (v instanceof JObjeto && !!metodoDe(v.clase, 'compareTo', 1));
        case 'List': case 'ArrayList': case 'Collection': case 'Iterable': return v instanceof JLista || (t.n !== 'List' && t.n !== 'ArrayList' && v instanceof JConjunto);
        case 'Set': case 'HashSet': case 'TreeSet': case 'LinkedHashSet': return v instanceof JConjunto;
        case 'Map': case 'HashMap': case 'TreeMap': case 'LinkedHashMap': return v instanceof JMapa && (t.n === 'Map' || v.clase === t.n);
      }
      if (v instanceof JObjeto) return esSubclase(v.clase, t.n);
      return false;
    }
    function leerNombre(e, ctx) {
      const local = ctx.env.buscar(e.nombre);
      if (local) return local.v;
      for (let c = ctx.clase; c; c = c.exterior) {
        const t = tipoDeCampo(c, e.nombre);
        if (t && ctx.yo) { const dueno = c === ctx.clase ? ctx.yo : ctx.yo.f.get('$exterior') || ctx.yo; if (dueno.f.has(e.nombre)) return dueno.f.get(e.nombre); }
        const s = campoEstatico(c, e.nombre);
        if (s) return s.v;
      }
      if (clases.has(e.nombre)) return new RefClase(clases.get(e.nombre));
      if (LIB_ESTATICAS.has(e.nombre)) return new RefLib(e.nombre);
      if (/^[a-z]\w*$/.test(e.nombre) && ['java', 'javax', 'jdk', 'ar', 'utnfc', 'org', 'com', 'edu'].includes(e.nombre)) return new RefPaquete(e.nombre);
      falla('no conozco «' + e.nombre + '»', ctx.clase && ctx.clase.archivo, e.l);
    }
    function leerCampo(e, ctx) {
      const o = evaluar(e.obj, ctx);
      if (o instanceof RefPaquete) {
        if (/^[A-Z]/.test(e.nombre)) { if (clases.has(e.nombre)) return new RefClase(clases.get(e.nombre)); if (LIB_ESTATICAS.has(e.nombre) || ESTATICOS[e.nombre]) return new RefLib(e.nombre); err(e, 'la clase ' + o.n + '.' + e.nombre); }
        return new RefPaquete(o.n + '.' + e.nombre);
      }
      if (o instanceof RefClase) {
        if (e.nombre === 'length') err(e, 'length de una clase');
        const s = campoEstatico(o.c, e.nombre);
        if (s) return s.v;
        if (clases.has(e.nombre)) return new RefClase(clases.get(e.nombre));
        falla('la clase ' + o.c.nombre + ' no tiene el campo ' + e.nombre, ctx.clase && ctx.clase.archivo, e.l);
      }
      if (o instanceof RefLib) return campoLib(o.n, e.nombre, e);
      if (o === null) lanzar('NullPointerException', 'Cannot read field "' + e.nombre + '" because value is null');
      if (o instanceof JArr && e.nombre === 'length') return o.a.length;
      if (o instanceof JObjeto) {
        if (o.f.has(e.nombre)) return o.f.get(e.nombre);
        const s = campoEstatico(o.clase, e.nombre);
        if (s) return s.v;
      }
      err(e, 'el campo ' + e.nombre);
    }
    function tipoDestino(x, ctx) {
      if (x.e === 'var') { const l = ctx.env.buscar(x.nombre); if (l) return l.t && l.t.n !== 'var' ? l.t : null; for (let c = ctx.clase; c; c = c.exterior) { const t = tipoDeCampo(c, x.nombre); if (t) return t; const s = campoEstatico(c, x.nombre); if (s) return s.t; } return null; }
      if (x.e === 'campo') { const o = evaluar(x.obj, ctx); if (o instanceof JObjeto) return tipoDeCampo(o.clase, x.nombre); if (o instanceof RefClase) { const s = campoEstatico(o.c, x.nombre); return s && s.t; } return null; }
      if (x.e === 'indice') { const a = evaluar(x.arr, ctx); return a instanceof JArr ? a.t : null; }
      if (x.e === 'paren') return tipoDestino(x.a, ctx);
      return null;
    }
    function guardar(x, v, ctx) {
      if (x.e === 'paren') return guardar(x.a, v, ctx);
      if (x.e === 'var') {
        const l = ctx.env.buscar(x.nombre);
        if (l) { l.v = l.t && l.t.n !== 'var' ? convertir(v, l.t) : v; return; }
        for (let c = ctx.clase; c; c = c.exterior) {
          const t = tipoDeCampo(c, x.nombre);
          if (t && ctx.yo) { (c === ctx.clase ? ctx.yo : ctx.yo.f.get('$exterior') || ctx.yo).f.set(x.nombre, convertir(v, t)); return; }
          const s = campoEstatico(c, x.nombre);
          if (s) { s.v = convertir(v, s.t); return; }
        }
        falla('no conozco «' + x.nombre + '»', ctx.clase && ctx.clase.archivo, x.l);
      }
      if (x.e === 'campo') {
        const o = evaluar(x.obj, ctx);
        if (o === null) npe();
        if (o instanceof RefClase) { const s = campoEstatico(o.c, x.nombre); if (!s) err(x, 'el campo ' + x.nombre); s.v = convertir(v, s.t); return; }
        if (o instanceof JObjeto) { o.f.set(x.nombre, convertir(v, tipoDeCampo(o.clase, x.nombre))); return; }
        err(x, 'asignar el campo ' + x.nombre);
      }
      if (x.e === 'indice') {
        const a = evaluar(x.arr, ctx), i = aIndice(evaluar(x.i, ctx));
        if (a === null) npe();
        if (i < 0 || i >= a.a.length) lanzar('ArrayIndexOutOfBoundsException', 'Index ' + i + ' out of bounds for length ' + a.a.length);
        a.a[i] = convertir(v, a.t);
        return;
      }
      err(x, 'asignar a esto');
    }
    function asignar(e, ctx) {
      if (e.op === '=') {
        let v = e.b.e === 'arrInit' ? arregloDesdeInit(e.b, tipoDestino(e.a, ctx) || { n: 'Object', d: 1 }, ctx) : evaluar(e.b, ctx);
        guardar(e.a, v, ctx);
        const t = tipoDestino(e.a, ctx);
        return t ? convertir(v, t) : v;
      }
      const viejo = evaluar(e.a, ctx), b = evaluar(e.b, ctx), op = e.op.slice(0, -1);
      const t = tipoDestino(e.a, ctx);
      let r;
      if (op === '+' && (typeof viejo === 'string' || (t && t.n === 'String'))) r = aTexto(viejo) + aTexto(b);
      else r = operar(op, viejo, b, e);
      if (t && t.d === 0 && t.n !== 'String' && t.n !== 'var') r = castear(t, r, e);
      guardar(e.a, r, ctx);
      return r;
    }
    function evaluarBinaria(e, ctx) {
      if (e.op === '&&') return !!evaluar(e.a, ctx) && !!evaluar(e.b, ctx);
      if (e.op === '||') return !!evaluar(e.a, ctx) || !!evaluar(e.b, ctx);
      const a = evaluar(e.a, ctx), b = evaluar(e.b, ctx);
      return operar(e.op, a, b, e);
    }
    function operar(op, a, b, e) {
      switch (op) {
        case '+':
          if (typeof a === 'string' || typeof b === 'string') return aTexto(a) + aTexto(b);
          return aritmetica('+', a, b, e);
        case '-': case '*': case '/': case '%': return aritmetica(op, a, b, e);
        case '==': case '!=': {
          let r;
          if (esNum(a) && esNum(b)) r = compararNum(a, b) === 0;
          else if (typeof a === 'boolean' || typeof b === 'boolean') r = a === b;
          else if (typeof a === 'string' && typeof b === 'string') r = a === b;
          else if (a instanceof JClaseRef && b instanceof JClaseRef) r = a.c === b.c && a.nombre === b.nombre;
          else r = a === b || (a === undefined && b === null) || (a === null && b === undefined);
          return op === '==' ? r : !r;
        }
        case '<': case '>': case '<=': case '>=': {
          if (a === null || b === null) npe();
          const c = compararNum(a, b);
          if (Number.isNaN(c)) return false;
          return op === '<' ? c < 0 : op === '>' ? c > 0 : op === '<=' ? c <= 0 : c >= 0;
        }
        case '&': case '|': case '^':
          if (typeof a === 'boolean' && typeof b === 'boolean') return op === '&' ? a && b : op === '|' ? a || b : a !== b;
          if (typeof a === 'bigint' || typeof b === 'bigint') { const x = aLong(a), y = aLong(b); return L(op === '&' ? x & y : op === '|' ? x | y : x ^ y); }
          { const x = aInt(a), y = aInt(b); return op === '&' ? x & y : op === '|' ? x | y : x ^ y; }
        case '<<': case '>>': case '>>>':
          if (typeof a === 'bigint') { const s = BigInt(aInt(b) & 63); return op === '<<' ? L(a << s) : op === '>>' ? L(a >> s) : L(BigInt.asUintN(64, a) >> s); }
          { const x = aInt(a), s = aInt(typeof b === 'bigint' ? Number(BigInt.asIntN(32, b)) : b) & 31; return op === '<<' ? x << s : op === '>>' ? x >> s : (x >>> s) | 0; }
      }
      err(e, 'el operador ' + op);
    }
    const aInt = v => v instanceof Ch ? v.c : typeof v === 'number' ? v : typeof v === 'bigint' ? Number(BigInt.asIntN(32, v)) : v === null ? npe() : err(null, 'operar con algo que no es número');
    const aLong = v => typeof v === 'bigint' ? v : v instanceof Ch ? BigInt(v.c) : typeof v === 'number' ? BigInt(v) : v === null ? npe() : err(null, 'operar con algo que no es número');
    function compararNum(a, b) {
      if (!esNum(a) || !esNum(b)) { if (a === null || b === null) npe(); return a === b ? 0 : NaN; }
      if (a instanceof D || b instanceof D) { const x = aNumero(a), y = aNumero(b); return Number.isNaN(x) || Number.isNaN(y) ? NaN : x < y ? -1 : x > y ? 1 : 0; }
      if (typeof a === 'bigint' || typeof b === 'bigint') { const x = aLong(a), y = aLong(b); return x < y ? -1 : x > y ? 1 : 0; }
      const x = aInt(a), y = aInt(b); return x < y ? -1 : x > y ? 1 : 0;
    }
    function aritmetica(op, a, b, e) {
      if (a === null || b === null || a === undefined || b === undefined) npe();
      if (!esNum(a) || !esNum(b)) err(e, 'la cuenta ' + aTexto(a) + ' ' + op + ' ' + aTexto(b));
      if (a instanceof D || b instanceof D) {
        const x = aNumero(a), y = aNumero(b);
        return new D(op === '+' ? x + y : op === '-' ? x - y : op === '*' ? x * y : op === '/' ? x / y : x % y);
      }
      if (typeof a === 'bigint' || typeof b === 'bigint') {
        const x = aLong(a), y = aLong(b);
        if ((op === '/' || op === '%') && y === 0n) lanzar('ArithmeticException', '/ by zero');
        return L(op === '+' ? x + y : op === '-' ? x - y : op === '*' ? x * y : op === '/' ? x / y : x % y);
      }
      const x = aInt(a), y = aInt(b);
      switch (op) {
        case '+': return (x + y) | 0;
        case '-': return (x - y) | 0;
        case '*': return Math.imul(x, y);
        case '/': if (y === 0) lanzar('ArithmeticException', '/ by zero'); return (x / y) | 0;
        case '%': if (y === 0) lanzar('ArithmeticException', '/ by zero'); return (x % y) | 0;
      }
    }

    // Llamadas
    function evaluarLlamada(e, ctx) {
      const args = () => e.args.map(a => evaluar(a, ctx));
      if (e.obj === null) {                                       // método de la propia clase (o de la de afuera)
        const as = args();
        for (let c = ctx.clase; c; c = c.exterior) {
          const m = metodoDe(ctx.yo && c === ctx.clase ? ctx.yo.clase : c, e.nombre, as.length, as) || metodoDe(c, e.nombre, as.length, as);
          if (m) {
            if (m.estatico) return invocar(m, null, as, e);
            const yo = c === ctx.clase ? ctx.yo : (ctx.yo && ctx.yo.f.get('$exterior'));
            if (!yo) err(e, 'llamar a ' + e.nombre + ' (que no es static) desde un método static');
            return invocar(metodoDe(yo.clase, e.nombre, as.length, as) || m, yo, as, e);
          }
        }
        if (ctx.yo && ctx.yo.clase.nativa === false && esSubclase(ctx.yo.clase, 'Throwable')) return metodoDeObject(ctx.yo, e.nombre, as, e);
        falla('no encuentro el método ' + e.nombre + '(' + as.length + ' parámetros)', ctx.clase && ctx.clase.archivo, e.l);
      }
      if (e.obj.e === 'super') {
        const as = args();
        const m = metodoDe(ctx.clase.padre, e.nombre, as.length, as);
        if (m) return invocar(m, ctx.yo, as, e);
        return metodoDeObject(ctx.yo, e.nombre, as, e);
      }
      const r = evaluar(e.obj, ctx);
      const as = args();
      return llamarMetodo(r, e.nombre, as, e, ctx);
    }
    function evaluarNew(e, ctx) {
      const as = e.args.map(a => evaluar(a, ctx));
      if (e.anonima) {
        const base = clases.get(e.t.n);
        const c = registrar(e.anonima, ctx.clase, '');
        c.nombre = (ctx.clase ? ctx.clase.nombre : '') + '$' + (++anonimas); c.fq = c.nombre;
        if (base && base.interfaz) { c.padre = clases.get('Object'); c.interfaces = [base.nombre]; }
        else if (base) { c.padre = base; c.argsAnonimos = as; c.anonimaDe = true; }
        else { c.padre = clases.get('Object'); c.interfaces = [e.t.n]; }
        c.entornoAnonimo = ctx.env;
        const o = construir(c, [], e);
        if (ctx.yo) o.f.set('$exterior', ctx.yo);
        return o;
      }
      const c = clases.get(e.t.n);
      if (c && !c.nativa) {
        const o = construir(c, as, e);
        if (!c.estaticoAnidado && ctx.yo) o.f.set('$exterior', ctx.yo);
        return o;
      }
      if (c && c.nativa) return construir(c, as, e);
      return nuevoLib(e.t.n, as, e);
    }
    let anonimas = 0;
    function crearLambda(e, ctx) {
      const cap = ctx;
      return fn(as => {
        const env = new Entorno(cap.env);
        e.params.forEach((p, i) => env.definir(p.nombre, p.t ? convertir(as[i], p.t) : as[i], p.t));
        const c2 = { clase: cap.clase, yo: cap.yo, env, metodo: cap.metodo };
        if (e.cuerpo.s === 'bloque') {
          try { ejecutarSentencia(e.cuerpo, c2); } catch (x) { if (x instanceof Retorno) return x.v; throw x; }
          return undefined;
        }
        return evaluar(e.cuerpo, c2);
      }, { aridad: e.params.length });
    }
    function crearReferencia(e, ctx) {
      const n = e.nombre;
      if (e.obj.e === 'tipo') {                                         // int[]::new, String[]::new
        const t = e.obj.t;
        return fn(([len]) => new JArr({ n: t.n, d: t.d - 1 }, Array.from({ length: len }, () => valorPorDefecto({ n: t.n, d: t.d - 1 }))));
      }
      if (e.obj.e === 'super') return fn(as => { const m = metodoDe(ctx.clase.padre, n, as.length, as); return invocar(m, ctx.yo, as, e); });
      const base = e.obj.e === 'var' && !ctx.env.buscar(e.obj.nombre) && !tipoDestino(e.obj, ctx) ? (clases.has(e.obj.nombre) ? new RefClase(clases.get(e.obj.nombre)) : LIB_ESTATICAS.has(e.obj.nombre) ? new RefLib(e.obj.nombre) : null) : null;
      let r = base || evaluar(e.obj, ctx);
      if (r instanceof RefPaquete) err(e, 'la referencia ' + r.n + '::' + n);
      if (r instanceof RefClase) {
        const c = r.c;
        if (n === 'new') return fn(as => evaluarNewDeClase(c, as, e, ctx));
        return fn(as => {
          const m = metodoDe(c, n, as.length, as);
          if (m && m.estatico) return invocar(m, null, as, e);
          if (as.length && as[0] instanceof JObjeto) return llamarMetodo(as[0], n, as.slice(1), e);
          if (m) return invocar(m, null, as, e);
          if (as.length) return llamarMetodo(as[0], n, as.slice(1), e);
          err(e, 'la referencia ' + c.nombre + '::' + n);
        }, { aridad: (() => { const m = (c.metodos.get(n) || [])[0]; return m ? m.params.length + (m.estatico ? 0 : 1) : undefined; })() });
      }
      if (r instanceof RefLib) {
        if (n === 'new') return fn(as => nuevoLib(r.n, as, e));
        return fn(as => {
          if (existeEstaticoLib(r.n, n, as.length)) return estaticoLib(r.n, n, as, e, ctx);
          if (!as.length) err(e, 'la referencia ' + r.n + '::' + n);
          return llamarMetodo(as[0], n, as.slice(1), e);
        }, { aridad: n === 'compare' || n === 'sum' || n === 'max' || n === 'min' ? 2 : undefined });
      }
      return fn(as => llamarMetodo(r, n, as, e), { consumidor: r instanceof JImpresora });   // obj::metodo
    }
    function evaluarNewDeClase(c, as, e, ctx) { const o = construir(c, as, e); if (!c.estaticoAnidado && ctx.yo) o.f.set('$exterior', ctx.yo); return o; }

    // ═══ Sentencias
    function ejecutarSentencia(s, ctx) {
      if (++pasos > limitePasos) falla('el programa tardó demasiado (¿un ciclo que no termina?)');
      switch (s.s) {
        case 'bloque': {
          const c2 = { ...ctx, env: new Entorno(ctx.env) };
          for (const x of s.ss) ejecutarSentencia(x, c2);
          return;
        }
        case 'nada': return;
        case 'expr': evaluar(s.e, ctx); return;
        case 'local':
          for (const v of s.vars) {
            const val = v.init === null ? undefined : v.init.e === 'arrInit' ? arregloDesdeInit(v.init, v.t, ctx) : evaluar(v.init, ctx);
            ctx.env.definir(v.nombre, v.t.n === 'var' ? val : convertir(val, v.t), v.t);
          }
          return;
        case 'if': if (evaluar(s.c, ctx)) ejecutarSentencia(s.si, ctx); else if (s.sino) ejecutarSentencia(s.sino, ctx); return;
        case 'while':
          while (evaluar(s.c, ctx)) { try { ejecutarSentencia(s.cuerpo, ctx); } catch (x) { if (x instanceof Corte && (!x.etiqueta || x.etiqueta === s.etiqueta)) break; if (x instanceof Sigue && (!x.etiqueta || x.etiqueta === s.etiqueta)) continue; throw x; } }
          return;
        case 'do':
          do { try { ejecutarSentencia(s.cuerpo, ctx); } catch (x) { if (x instanceof Corte && (!x.etiqueta || x.etiqueta === s.etiqueta)) break; if (x instanceof Sigue && (!x.etiqueta || x.etiqueta === s.etiqueta)) continue; throw x; } } while (evaluar(s.c, ctx));
          return;
        case 'for': {
          const c2 = { ...ctx, env: new Entorno(ctx.env) };
          for (const i of s.init) ejecutarSentencia(i, c2);
          for (; s.c === null || evaluar(s.c, c2); s.paso.forEach(p => evaluar(p, c2))) {
            try { ejecutarSentencia(s.cuerpo, c2); } catch (x) { if (x instanceof Corte && (!x.etiqueta || x.etiqueta === s.etiqueta)) break; if (x instanceof Sigue && (!x.etiqueta || x.etiqueta === s.etiqueta)) continue; throw x; }
          }
          return;
        }
        case 'foreach': {
          const col = evaluar(s.col, ctx);
          if (col === null) npe();
          const it = col instanceof JObjeto ? iterarObjeto(col) : elementos(col);
          if (!it) err(s, 'recorrer con for algo que no es una colección');
          for (const v of it.slice ? it.slice() : it) {
            const c2 = { ...ctx, env: new Entorno(ctx.env) };
            c2.env.definir(s.nombre, s.t.n === 'var' ? v : convertir(v, s.t), s.t);
            try { ejecutarSentencia(s.cuerpo, c2); } catch (x) { if (x instanceof Corte && (!x.etiqueta || x.etiqueta === s.etiqueta)) break; if (x instanceof Sigue && (!x.etiqueta || x.etiqueta === s.etiqueta)) continue; throw x; }
          }
          return;
        }
        case 'etiqueta': {
          s.cuerpo.etiqueta = s.etiqueta;
          try { ejecutarSentencia(s.cuerpo, ctx); } catch (x) { if (x instanceof Corte && x.etiqueta === s.etiqueta) return; throw x; }
          return;
        }
        case 'return': throw new Retorno(s.e ? evaluar(s.e, ctx) : undefined);
        case 'break': throw new Corte(s.etiqueta);
        case 'continue': throw new Sigue(s.etiqueta);
        case 'yield': case 'yieldFlecha': throw new Rinde(evaluar(s.e, ctx));
        case 'throw': {
          const ex = evaluar(s.e, ctx);
          if (ex === null) npe();
          throw new Lanzado(ex);
        }
        case 'try': return ejecutarTry(s, ctx);
      }
      err(s, 'la sentencia ' + s.s);
    }
    function iterarObjeto(o) {
      const it = llamarMetodo(o, 'iterator', []);
      const r = [];
      while (llamarMetodo(it, 'hasNext', [])) r.push(llamarMetodo(it, 'next', []));
      return r;
    }
    function ejecutarTry(s, ctx) {
      const c2 = { ...ctx, env: new Entorno(ctx.env) };
      const recursos = [];
      let pendiente = null;
      try {
        try {
          for (const r of s.recursos) {
            if (r.s === 'local') { ejecutarSentencia(r, c2); recursos.push(c2.env.buscar(r.vars[0].nombre).v); }
            else recursos.push(evaluar(r.e, c2));
          }
          ejecutarSentencia(s.cuerpo, c2);
        } finally {
          for (const r of recursos.reverse()) if (r && !(r instanceof JLector) && !(r instanceof JScanner) && r instanceof JObjeto) llamarMetodo(r, 'close', []);
        }
      } catch (x) {
        if (!(x instanceof Lanzado)) { pendiente = x; }
        else {
          const cap = s.capturas.find(c => c.tipos.some(t => esSubclase(x.ex.clase, t)));
          if (cap) {
            const c3 = { ...ctx, env: new Entorno(ctx.env) };
            c3.env.definir(cap.nombre, x.ex, { n: cap.tipos[0], d: 0 });
            try { ejecutarSentencia(cap.cuerpo, c3); } catch (y) { pendiente = y; }
          } else pendiente = x;
        }
      }
      if (s.fin) ejecutarSentencia(s.fin, ctx);
      if (pendiente) throw pendiente;
    }
    function evaluarSwitch(e, ctx, comoExpresion) {
      const v = evaluar(e.sel, ctx);
      if (v === null && !e.casos.some(c => c.etiquetas.some(x => x.e === 'lit' && x.v === null))) npe();
      let i = e.casos.findIndex(c => c.etiquetas.some(x => coincideCaso(x, v, ctx)));
      if (i < 0) i = e.casos.findIndex(c => c.def);
      if (i < 0) { if (comoExpresion && e.flecha) lanzar('MatchException', null); return undefined; }
      const c2 = { ...ctx, env: new Entorno(ctx.env) };
      try {
        if (e.flecha) {
          const cuerpo = e.casos[i].cuerpo[0];
          if (cuerpo.s === 'yieldFlecha') return evaluar(cuerpo.e, c2);
          ejecutarSentencia(cuerpo, c2);
        } else for (let j = i; j < e.casos.length; j++) for (const x of e.casos[j].cuerpo) ejecutarSentencia(x, c2);
      } catch (x) {
        if (x instanceof Rinde) return x.v;
        if (x instanceof Corte && !x.etiqueta) return undefined;
        throw x;
      }
      return undefined;
    }
    function coincideCaso(x, v, ctx) {
      if (x.e === 'var' && v instanceof JObjeto && v.clase.enumC) return v.f.get('$nombre') === x.nombre;
      const w = evaluar(x, ctx);
      if (esNum(w) && esNum(v)) return compararNum(w, v) === 0;
      return w === v || iguales(w, v);
    }
    // ═══ La biblioteca de Java: campos, métodos estáticos y constructores
    function campoLib(n, campo, e) {
      const K = {
        'Integer.MAX_VALUE': 2147483647, 'Integer.MIN_VALUE': -2147483648, 'Long.MAX_VALUE': 9223372036854775807n, 'Long.MIN_VALUE': -9223372036854775808n,
        'Double.MAX_VALUE': new D(Number.MAX_VALUE), 'Double.MIN_VALUE': new D(Number.MIN_VALUE), 'Double.POSITIVE_INFINITY': new D(Infinity),
        'Double.NEGATIVE_INFINITY': new D(-Infinity), 'Double.NaN': new D(NaN), 'Math.PI': new D(Math.PI), 'Math.E': new D(Math.E),
        'Short.MAX_VALUE': 32767, 'Byte.MAX_VALUE': 127, 'Character.MAX_VALUE': new Ch(0xFFFF), 'Boolean.TRUE': true, 'Boolean.FALSE': false,
      };
      if ((n + '.' + campo) in K) return K[n + '.' + campo];
      if (n === 'System' && campo === 'out') return SALIDA;
      if (n === 'System' && campo === 'err') return ERROR;
      if (n === 'System' && campo === 'in') return new JScanner(entrada);
      if (n === 'StandardCharsets' || n === 'Charset') return new JCharset(campo.replace(/_/g, '-'));
      if (n === 'Locale') return campo;
      if (n === 'Map' && campo === 'Entry') return new RefLib('Entry');
      err(e, n + '.' + campo);
    }
    const SALIDA = new JImpresora(salida), ERROR = new JImpresora(errores);
    const ESTATICOS = {
      Integer: ['parseInt', 'valueOf', 'compare', 'sum', 'max', 'min', 'toString', 'signum', 'abs', 'toBinaryString', 'toHexString', 'hashCode'],
      Long: ['parseLong', 'valueOf', 'compare', 'sum', 'max', 'min', 'toString', 'hashCode'],
      Double: ['parseDouble', 'valueOf', 'compare', 'sum', 'max', 'min', 'toString', 'isNaN', 'isInfinite', 'isFinite', 'hashCode'],
      Float: ['parseFloat', 'valueOf'], Short: ['parseShort'], Byte: ['parseByte'],
      Boolean: ['parseBoolean', 'valueOf', 'toString', 'compare', 'logicalAnd', 'logicalOr'],
      Character: ['isDigit', 'isLetter', 'isLetterOrDigit', 'isWhitespace', 'isUpperCase', 'isLowerCase', 'toUpperCase', 'toLowerCase', 'getNumericValue', 'valueOf', 'isSpaceChar', 'isAlphabetic', 'toString', 'compare'],
      Math: ['abs', 'max', 'min', 'pow', 'sqrt', 'round', 'floor', 'ceil', 'floorDiv', 'floorMod', 'random', 'hypot', 'cbrt', 'log', 'log10', 'exp', 'signum', 'addExact', 'multiplyExact', 'subtractExact', 'toIntExact', 'rint', 'clamp'],
      StrictMath: ['abs', 'max', 'min', 'pow', 'sqrt', 'round', 'floor', 'ceil'],
      String: ['valueOf', 'join', 'format', 'copyValueOf'],
      List: ['of', 'copyOf'], Set: ['of', 'copyOf'], Map: ['of', 'copyOf', 'entry', 'ofEntries'],
      Arrays: ['stream', 'asList', 'toString', 'sort', 'copyOf', 'copyOfRange', 'fill', 'equals', 'hashCode', 'deepToString'],
      Collections: ['unmodifiableList', 'unmodifiableMap', 'unmodifiableSet', 'unmodifiableCollection', 'emptyList', 'emptyMap', 'emptySet', 'sort', 'reverseOrder', 'max', 'min', 'reverse', 'singletonList', 'frequency', 'addAll', 'nCopies', 'shuffle'],
      Collectors: ['toList', 'toSet', 'groupingBy', 'counting', 'summingInt', 'summingLong', 'summingDouble', 'averagingInt', 'averagingDouble', 'averagingLong', 'mapping', 'maxBy', 'minBy', 'collectingAndThen', 'toMap', 'joining', 'partitioningBy', 'toUnmodifiableList', 'reducing', 'filtering', 'summarizingInt', 'summarizingDouble', 'toCollection', 'flatMapping', 'teeing'],
      Comparator: ['comparing', 'comparingInt', 'comparingDouble', 'comparingLong', 'naturalOrder', 'reverseOrder', 'nullsFirst', 'nullsLast'],
      Entry: ['comparingByKey', 'comparingByValue'],
      Files: ['newBufferedReader', 'readAllLines', 'lines', 'exists', 'readString', 'isRegularFile', 'size'],
      Path: ['of'], Paths: ['get'],
      Objects: ['requireNonNull', 'equals', 'hash', 'isNull', 'nonNull', 'toString', 'hashCode', 'requireNonNullElse', 'compare'],
      Optional: ['of', 'empty', 'ofNullable'], OptionalInt: ['of', 'empty'], OptionalDouble: ['of', 'empty'],
      IntStream: ['range', 'rangeClosed', 'of', 'empty'], LongStream: ['range', 'rangeClosed', 'of'], DoubleStream: ['of'], Stream: ['of', 'empty', 'concat', 'iterate', 'generate'],
      System: ['lineSeparator', 'exit', 'currentTimeMillis', 'nanoTime', 'getProperty', 'arraycopy', 'identityHashCode', 'getenv'],
      Function: ['identity'], UnaryOperator: ['identity'], Thread: ['sleep'], Locale: ['of', 'forLanguageTag', 'getDefault', 'setDefault'],
      BigDecimal: [], Predicate: ['not', 'isEqual'],
    };
    const existeEstaticoLib = (n, m) => (ESTATICOS[n] || []).includes(m);
    function nuevoLib(n, as, e) {
      switch (n) {
        case 'ArrayList': case 'LinkedList': case 'ArrayDeque': case 'Vector': case 'CopyOnWriteArrayList':
          return nuevaLista(as.length && typeof as[0] !== 'number' ? [...elementos(as[0])] : []);
        case 'HashMap': case 'LinkedHashMap': case 'TreeMap': case 'Hashtable': case 'ConcurrentHashMap': {
          const clase = n === 'LinkedHashMap' ? 'LinkedHashMap' : n === 'TreeMap' ? 'TreeMap' : 'HashMap';
          const cmp = n === 'TreeMap' && as.length && !(as[0] instanceof JMapa) ? as[0] : null;
          const m = nuevoMapa(clase, cmp, clase === 'HashMap' && typeof as[0] === 'number' ? as[0] : null);
          if (as.length && as[0] instanceof JMapa) for (const x of entradas(as[0])) poner(m, x.k, x.v);
          return m;
        }
        case 'HashSet': case 'LinkedHashSet': case 'TreeSet': {
          const clase = n === 'LinkedHashSet' ? 'LinkedHashMap' : n === 'TreeSet' ? 'TreeMap' : 'HashMap';
          const cmp = n === 'TreeSet' && as.length && (as[0] instanceof JFn || (as[0] instanceof JObjeto && metodoDe(as[0].clase, 'compare', 2))) ? as[0] : null;
          const c = new JConjunto(nuevoMapa(clase, cmp, null));
          if (as.length && !cmp && typeof as[0] !== 'number') for (const x of elementos(as[0])) poner(c.m, x, true);
          return c;
        }
        case 'StringBuilder': case 'StringBuffer': return new JSB(as.length && typeof as[0] === 'string' ? as[0] : '');
        case 'String': return as.length ? (as[0] instanceof JArr ? as[0].a.map(c => String.fromCharCode(c.c)).join('') : aTexto(as[0])) : '';
        case 'File': return new JRuta(as.length === 2 ? aTexto(as[0]) + '/' + aTexto(as[1]) : aTexto(as[0]));
        case 'FileReader': return new JLector(lineasDe(leerArchivo(as[0] instanceof JRuta ? as[0].s : as[0], 'FileNotFoundException')));
        case 'BufferedReader': case 'InputStreamReader': return as[0];
        case 'Scanner': {
          if (as[0] instanceof JRuta) return new JScanner(leerArchivo(as[0].s, as[0].archivo ? 'NoSuchFileException' : 'FileNotFoundException'));
          if (as[0] instanceof JScanner) return as[0];
          if (typeof as[0] === 'string') return new JScanner(as[0]);
          return new JScanner(entrada);
        }
        case 'Object': return new JObjeto(clases.get('Object'));
        case 'Random': err(e, 'números al azar (Random)');
      }
      err(e, 'crear un objeto de la clase ' + n);
    }
    function estaticoLib(n, m, as, e, ctx) {
      const a = as[0], b = as[1];
      switch (n + '.' + m) {
        case 'Integer.parseInt': case 'Integer.valueOf': case 'Short.parseShort': case 'Byte.parseByte':
          if (typeof a === 'number') return a; if (as.length > 1 && b !== 10) err(e, 'parseInt con otra base'); return parseEntero(a, false);
        case 'Long.parseLong': case 'Long.valueOf': if (typeof a === 'bigint') return a; if (typeof a === 'number') return BigInt(a); return parseEntero(a, true);
        case 'Double.parseDouble': case 'Double.valueOf': case 'Float.parseFloat': case 'Float.valueOf': return a instanceof D ? a : typeof a === 'string' || a === null ? parseDoble(a) : new D(aNumero(a));
        case 'Integer.compare': case 'Long.compare': case 'Double.compare': case 'Character.compare': case 'Boolean.compare': case 'Objects.compare':
          return m === 'compare' && n === 'Objects' ? (a === b ? 0 : llamarFn(as[2], [a, b])) : compararNatural(a, b);
        case 'Integer.sum': return (a + b) | 0;
        case 'Long.sum': return L(aLong(a) + aLong(b));
        case 'Double.sum': return new D(aNumero(a) + aNumero(b));
        case 'Integer.max': case 'Long.max': case 'Math.max': case 'StrictMath.max': return compararNum(a, b) >= 0 || Number.isNaN(compararNum(a, b)) ? promover(a, b, a) : promover(a, b, b);
        case 'Integer.min': case 'Long.min': case 'Math.min': case 'StrictMath.min': return compararNum(a, b) <= 0 || Number.isNaN(compararNum(a, b)) ? promover(a, b, a) : promover(a, b, b);
        case 'Double.max': return new D(Math.max(aNumero(a), aNumero(b)));
        case 'Double.min': return new D(Math.min(aNumero(a), aNumero(b)));
        case 'Integer.toString': case 'Long.toString': case 'Double.toString': case 'Boolean.toString': case 'Character.toString': case 'String.valueOf': case 'Objects.toString':
          if (m === 'toString' && n === 'Objects' && as.length === 2 && a === null) return b;
          if (n === 'String' && a instanceof JArr) return a.a.map(c => String.fromCharCode(c.c)).join('');
          return aTexto(n === 'Character' && typeof a === 'number' ? new Ch(a) : a);
        case 'Integer.signum': return Math.sign(a);
        case 'Integer.abs': case 'Math.abs': case 'StrictMath.abs': return a instanceof D ? new D(Math.abs(a.v)) : typeof a === 'bigint' ? (a < 0n ? L(-a) : a) : Math.abs(aInt(a)) | 0;
        case 'Integer.hashCode': case 'Long.hashCode': case 'Double.hashCode': case 'Objects.hashCode': return hash(a);
        case 'Integer.toBinaryString': return (a >>> 0).toString(2);
        case 'Integer.toHexString': return (a >>> 0).toString(16);
        case 'Double.isNaN': return Number.isNaN(aNumero(a));
        case 'Double.isInfinite': return Math.abs(aNumero(a)) === Infinity;
        case 'Double.isFinite': return Number.isFinite(aNumero(a));
        case 'Boolean.parseBoolean': case 'Boolean.valueOf': return typeof a === 'boolean' ? a : a !== null && a.toLowerCase() === 'true';
        case 'Boolean.logicalAnd': return a && b;
        case 'Boolean.logicalOr': return a || b;
        case 'Character.isDigit': return /\d/.test(String.fromCharCode(aInt(a)));
        case 'Character.isLetter': case 'Character.isAlphabetic': return /\p{L}/u.test(String.fromCharCode(aInt(a)));
        case 'Character.isLetterOrDigit': return /[\p{L}\d]/u.test(String.fromCharCode(aInt(a)));
        case 'Character.isWhitespace': return esEspacioJava(aInt(a));
        case 'Character.isSpaceChar': return /\s/.test(String.fromCharCode(aInt(a)));
        case 'Character.isUpperCase': { const s = String.fromCharCode(aInt(a)); return s !== s.toLowerCase(); }
        case 'Character.isLowerCase': { const s = String.fromCharCode(aInt(a)); return s !== s.toUpperCase(); }
        case 'Character.toUpperCase': return new Ch(String.fromCharCode(aInt(a)).toUpperCase().charCodeAt(0));
        case 'Character.toLowerCase': return new Ch(String.fromCharCode(aInt(a)).toLowerCase().charCodeAt(0));
        case 'Character.getNumericValue': { const s = String.fromCharCode(aInt(a)); return /\d/.test(s) ? Number(s) : /[a-z]/i.test(s) ? s.toLowerCase().charCodeAt(0) - 87 : -1; }
        case 'Character.valueOf': return a;
        case 'Math.pow': case 'StrictMath.pow': return new D(Math.pow(aNumero(a), aNumero(b)));
        case 'Math.sqrt': case 'StrictMath.sqrt': return new D(Math.sqrt(aNumero(a)));
        case 'Math.cbrt': return new D(Math.cbrt(aNumero(a)));
        case 'Math.hypot': return new D(Math.hypot(aNumero(a), aNumero(b)));
        case 'Math.log': return new D(Math.log(aNumero(a)));
        case 'Math.log10': return new D(Math.log10(aNumero(a)));
        case 'Math.exp': return new D(Math.exp(aNumero(a)));
        case 'Math.signum': return new D(Math.sign(aNumero(a)));
        case 'Math.floor': case 'StrictMath.floor': return new D(Math.floor(aNumero(a)));
        case 'Math.ceil': case 'StrictMath.ceil': return new D(Math.ceil(aNumero(a)));
        case 'Math.rint': { const x = aNumero(a), f = Math.floor(x), d = x - f; return new D(d > 0.5 || (d === 0.5 && f % 2 !== 0) ? f + 1 : f); }
        case 'Math.round': case 'StrictMath.round':
          if (a instanceof D) { const x = a.v; if (Number.isNaN(x)) return 0n; return d2l(Math.floor(x + 0.5)); }
          return a;
        case 'Math.floorDiv': if (aNumero(b) === 0) lanzar('ArithmeticException', '/ by zero'); return typeof a === 'bigint' ? L((a - ((a % b) + b) % b) / b) : Math.floor(a / b) | 0;
        case 'Math.floorMod': if (aNumero(b) === 0) lanzar('ArithmeticException', '/ by zero'); return typeof a === 'bigint' ? L(((a % b) + b) % b) : (((a % b) + b) % b) | 0;
        case 'Math.addExact': { const r = aNumero(a) + aNumero(b); if (typeof a === 'number' && (r > 2147483647 || r < -2147483648)) lanzar('ArithmeticException', 'integer overflow'); return typeof a === 'bigint' ? L(a + b) : r; }
        case 'Math.multiplyExact': { const r = aNumero(a) * aNumero(b); if (typeof a === 'number' && (r > 2147483647 || r < -2147483648)) lanzar('ArithmeticException', 'integer overflow'); return typeof a === 'bigint' ? L(a * b) : r; }
        case 'Math.subtractExact': { const r = aNumero(a) - aNumero(b); if (typeof a === 'number' && (r > 2147483647 || r < -2147483648)) lanzar('ArithmeticException', 'integer overflow'); return typeof a === 'bigint' ? L(a - b) : r; }
        case 'Math.toIntExact': if (a > 2147483647n || a < -2147483648n) lanzar('ArithmeticException', 'integer overflow'); return Number(a);
        case 'Math.clamp': return promover(a, b, Math.min(Math.max(aNumero(a), aNumero(b)), aNumero(as[2])));
        case 'Math.random': err(e, 'números al azar (Math.random)');
        case 'String.join': { const xs = as.length === 2 && !(typeof b === 'string') ? elementos(b) : as.slice(1); return xs.map(aTexto).join(aTexto(a)); }
        case 'String.format': return formatear(typeof a === 'string' ? a : aTexto(b), typeof a === 'string' ? as.slice(1) : as.slice(2), e);
        case 'String.copyValueOf': return a.a.map(c => String.fromCharCode(c.c)).join('');
        case 'List.of': case 'Set.of': {
          const xs = as.length === 1 && a instanceof JArr ? a.a : as;
          if (xs.some(x => x === null)) npe();
          if (m === 'of' && n === 'List') return nuevaLista([...xs], true);
          const c = new JConjunto(nuevoMapa('HashMap')); for (const x of xs) { if (buscarEntrada(c.m, x)) lanzar('IllegalArgumentException', 'duplicate element: ' + aTexto(x)); poner(c.m, x, true); } c.ro = true; c.m.ro = true; return c;
        }
        case 'List.copyOf': { const xs = elementos(a); if (xs.some(x => x === null)) npe(); return nuevaLista([...xs], true); }
        case 'Set.copyOf': { const c = new JConjunto(nuevoMapa('HashMap')); for (const x of elementos(a)) poner(c.m, x, true); c.ro = true; c.m.ro = true; return c; }
        case 'Map.of': { const mm = nuevoMapa('HashMap'); for (let i = 0; i < as.length; i += 2) { if (buscarEntrada(mm, as[i])) lanzar('IllegalArgumentException', 'duplicate key: ' + aTexto(as[i])); poner(mm, as[i], as[i + 1]); } mm.ro = true; return mm; }
        case 'Map.copyOf': { const mm = nuevoMapa('HashMap'); for (const x of entradas(a)) poner(mm, x.k, x.v); mm.ro = true; return mm; }
        case 'Map.entry': return new JEntrada(a, b, 0);
        case 'Map.ofEntries': { const mm = nuevoMapa('HashMap'); for (const x of as) poner(mm, x.k, x.v); mm.ro = true; return mm; }
        case 'Arrays.stream': return new JStream([...a.a], ['int', 'long', 'double'].includes(a.t.n) && a.t.d === 0 ? a.t.n : 'obj');
        case 'Arrays.asList': return nuevaLista(as.length === 1 && a instanceof JArr ? a.a : [...as]);
        case 'Arrays.toString': return a === null ? 'null' : '[' + a.a.map(aTexto).join(', ') + ']';
        case 'Arrays.deepToString': { const f = x => x instanceof JArr ? '[' + x.a.map(f).join(', ') + ']' : aTexto(x); return f(a); }
        case 'Arrays.sort': { const r = ordenar(a.a, as.length === 2 ? b : null); a.a.splice(0, a.a.length, ...r); return undefined; }
        case 'Arrays.copyOf': return new JArr(a.t, Array.from({ length: b }, (_, i) => i < a.a.length ? a.a[i] : valorPorDefecto(a.t)));
        case 'Arrays.copyOfRange': return new JArr(a.t, a.a.slice(b, as[2]));
        case 'Arrays.fill': a.a.fill(b); return undefined;
        case 'Arrays.equals': return a.a.length === b.a.length && a.a.every((x, i) => iguales(x, b.a[i]));
        case 'Arrays.hashCode': return a.a.reduce((h, x) => (Math.imul(h, 31) + hash(x)) | 0, 1);
        case 'Collections.unmodifiableList': case 'Collections.unmodifiableCollection': return new JLista(a.a, true);
        case 'Collections.unmodifiableMap': { const mm = Object.create(JMapa.prototype); Object.assign(mm, a); mm.ro = true; mm.e = a.e; Object.defineProperty(mm, 'e', { get: () => a.e }); Object.defineProperty(mm, 'cap', { get: () => a.cap }); return mm; }
        case 'Collections.unmodifiableSet': { const c = new JConjunto(a.m); c.ro = true; return c; }
        case 'Collections.emptyList': return nuevaLista([], true);
        case 'Collections.emptyMap': { const mm = nuevoMapa('HashMap'); mm.ro = true; return mm; }
        case 'Collections.emptySet': { const c = new JConjunto(nuevoMapa('HashMap')); c.ro = true; return c; }
        case 'Collections.singletonList': return nuevaLista([a], true);
        case 'Collections.nCopies': return nuevaLista(Array.from({ length: a }, () => b), true);
        case 'Collections.sort': { if (a.ro) lanzar('UnsupportedOperationException', null); const r = ordenar(a.a, as.length === 2 ? b : null); a.a.splice(0, a.a.length, ...r); return undefined; }
        case 'Collections.reverse': a.a.reverse(); return undefined;
        case 'Collections.reverseOrder': case 'Comparator.reverseOrder': return as.length ? fn(([x, y]) => llamarFn(a, [y, x]), { cmp: true }) : fn(([x, y]) => compararNatural(y, x), { cmp: true });
        case 'Collections.max': case 'Collections.min': {
          const xs = elementos(a); if (!xs.length) lanzar('NoSuchElementException', null);
          const f = comparadorDe(as.length === 2 ? b : null);
          return xs.reduce((p, x) => (m === 'max' ? f(x, p) > 0 : f(x, p) < 0) ? x : p);
        }
        case 'Collections.frequency': return elementos(a).filter(x => iguales(x, b)).length;
        case 'Collections.addAll': { for (const x of as.slice(1)) a.a.push(x); return true; }
        case 'Collections.shuffle': err(e, 'Collections.shuffle (azar)');
        case 'Comparator.comparing': case 'Comparator.comparingInt': case 'Comparator.comparingDouble': case 'Comparator.comparingLong': return comparadorPorClave(a, as.length === 2 ? b : null);
        case 'Comparator.naturalOrder': return fn(([x, y]) => compararNatural(x, y), { cmp: true });
        case 'Comparator.nullsFirst': case 'Comparator.nullsLast': return fn(([x, y]) => x === null ? (y === null ? 0 : m === 'nullsFirst' ? -1 : 1) : y === null ? (m === 'nullsFirst' ? 1 : -1) : llamarFn(a, [x, y]), { cmp: true });
        case 'Entry.comparingByKey': return fn(([x, y]) => as.length ? llamarFn(a, [x.k, y.k]) : compararNatural(x.k, y.k), { cmp: true });
        case 'Entry.comparingByValue': return fn(([x, y]) => as.length ? llamarFn(a, [x.v, y.v]) : compararNatural(x.v, y.v), { cmp: true });
        case 'Files.newBufferedReader': return new JLector(lineasDe(leerArchivo(a.s)));
        case 'Files.readAllLines': return nuevaLista(lineasDe(leerArchivo(a.s)));
        case 'Files.lines': return new JStream(lineasDe(leerArchivo(a.s)));
        case 'Files.readString': return leerArchivo(a.s);
        case 'Files.exists': case 'Files.isRegularFile': return ARCH.has(normalizar(a.s));
        case 'Files.size': return BigInt(new TextEncoder().encode(leerArchivo(a.s)).length);
        case 'Path.of': case 'Paths.get': { const r = new JRuta([a, ...as.slice(1)].map(aTexto).join('/')); r.archivo = true; return r; }
        case 'Objects.requireNonNull': if (a === null) lanzar('NullPointerException', as.length > 1 ? (b instanceof JFn ? llamarFn(b, []) : b) : null); return a;
        case 'Objects.requireNonNullElse': return a === null ? b : a;
        case 'Objects.equals': return a === b || (a !== null && iguales(a, b));
        case 'Objects.hash': return as.reduce((h, x) => (Math.imul(h, 31) + hash(x)) | 0, 1);
        case 'Objects.isNull': return a === null;
        case 'Objects.nonNull': return a !== null;
        case 'Optional.of': if (a === null) npe(); return new JOpcional(true, a);
        case 'Optional.ofNullable': return new JOpcional(a !== null, a);
        case 'Optional.empty': return new JOpcional(false, null);
        case 'OptionalInt.of': return new JOpcional(true, a, 'int');
        case 'OptionalInt.empty': return new JOpcional(false, null, 'int');
        case 'OptionalDouble.of': return new JOpcional(true, a, 'double');
        case 'OptionalDouble.empty': return new JOpcional(false, null, 'double');
        case 'IntStream.range': case 'IntStream.rangeClosed': { const fin = m === 'range' ? b : b + 1; return new JStream(Array.from({ length: Math.max(0, fin - a) }, (_, i) => a + i), 'int'); }
        case 'LongStream.range': case 'LongStream.rangeClosed': { const fin = m === 'range' ? b : b + 1n; const r = []; for (let i = BigInt(a); i < fin; i++) r.push(i); return new JStream(r, 'long'); }
        case 'IntStream.of': return new JStream(as.length === 1 && a instanceof JArr ? [...a.a] : as, 'int');
        case 'DoubleStream.of': return new JStream(as.length === 1 && a instanceof JArr ? [...a.a] : as, 'double');
        case 'LongStream.of': return new JStream(as, 'long');
        case 'IntStream.empty': return new JStream([], 'int');
        case 'Stream.of': return new JStream(as.length === 1 && a instanceof JArr ? [...a.a] : [...as]);
        case 'Stream.empty': return new JStream([]);
        case 'Stream.concat': return new JStream([...a.a, ...b.a], a.tipo);
        case 'Stream.iterate': if (as.length === 3) { const r = []; for (let x = a; llamarFn(b, [x]); x = llamarFn(as[2], [x])) r.push(x); return new JStream(r); } err(e, 'Stream.iterate sin fin');
        case 'System.lineSeparator': return '\n';
        case 'System.exit': throw new Fin(a);
        case 'System.currentTimeMillis': return BigInt(Date.now());
        case 'System.nanoTime': return BigInt(Math.round(performance.now() * 1e6));
        case 'System.getProperty': return a === 'line.separator' ? '\n' : a === 'user.dir' ? '/proyecto' : null;
        case 'System.getenv': return null;
        case 'System.identityHashCode': return identidad(a);
        case 'System.arraycopy': for (let i = 0; i < as[4]; i++) as[2].a[as[3] + i] = a.a[b + i]; return undefined;
        case 'Function.identity': case 'UnaryOperator.identity': return fn(([x]) => x);
        case 'Predicate.not': return fn(xs => !llamarFn(a, xs));
        case 'Predicate.isEqual': return fn(([x]) => iguales(a, x));
        case 'Thread.sleep': return undefined;
        case 'Locale.of': case 'Locale.forLanguageTag': case 'Locale.getDefault': return idioma;
        case 'Locale.setDefault': return undefined;
      }
      if (n === 'Collectors') return colector(m, as, e);
      err(e, n + '.' + m + '(' + as.length + ' parámetros)');
    }
    function promover(a, b, r) {     // el resultado de Math.max/min con el tipo «más ancho» de los dos
      if (a instanceof D || b instanceof D) return r instanceof D ? r : new D(aNumero(r));
      if (typeof a === 'bigint' || typeof b === 'bigint') return typeof r === 'bigint' ? r : BigInt(aNumero(r));
      return r instanceof Ch ? r.c : typeof r === 'number' ? r : aNumero(r);
    }
    // ═══ Métodos de los valores de la biblioteca
    function noModificable(x) { if (x.ro) lanzar('UnsupportedOperationException', null); }
    function fueraDeRango(i, n) { lanzar('IndexOutOfBoundsException', 'Index ' + i + ' out of bounds for length ' + n); }
    function metodoLib(r, m, as, e) {
      const a = as[0], b = as[1];
      if (typeof r === 'string') return metodoString(r, m, as, e);
      if (typeof r === 'number' || typeof r === 'bigint' || r instanceof D || r instanceof Ch || typeof r === 'boolean') {
        switch (m) {
          case 'equals': return a !== null && typeof a === typeof r && (r instanceof D ? a instanceof D && iguales(r, a) : r instanceof Ch ? a instanceof Ch && a.c === r.c : a === r);
          case 'compareTo': case 'compare': return compararNatural(r, a);
          case 'hashCode': return hash(r);
          case 'toString': return aTexto(r);
          case 'intValue': return castear({ n: 'int', d: 0 }, r);
          case 'longValue': return castear({ n: 'long', d: 0 }, r);
          case 'doubleValue': case 'floatValue': return new D(aNumero(r));
          case 'booleanValue': return r;
          case 'charValue': return r;
          case 'isNaN': return Number.isNaN(aNumero(r));
          case 'isInfinite': return Math.abs(aNumero(r)) === Infinity;
          case 'getClass': return new JClaseRef(null, claseDeValor(r).replace('java.lang.', ''));
        }
      }
      if (r instanceof JLista) return metodoLista(r, m, as, e);
      if (r instanceof JMapa) return metodoMapa(r, m, as, e);
      if (r instanceof JConjunto) return metodoConjunto(r, m, as, e);
      if (r instanceof JStream) return metodoStream(r, m, as, e);
      if (r instanceof JOpcional) return metodoOpcional(r, m, as, e);
      if (r instanceof JFn) return metodoDeFn(r, m, as);
      if (r instanceof JImpresora) {
        const salidaTxt = x => r.d.push(x);
        switch (m) {
          case 'println': salidaTxt((as.length ? (a instanceof JArr && a.t.n === 'char' ? a.a.map(c => String.fromCharCode(c.c)).join('') : aTexto(a)) : '') + '\n'); return undefined;
          case 'print': salidaTxt(a instanceof JArr && a.t.n === 'char' ? a.a.map(c => String.fromCharCode(c.c)).join('') : aTexto(a)); return undefined;
          case 'printf': case 'format': salidaTxt(formatear(typeof a === 'string' ? a : b, typeof a === 'string' ? as.slice(1) : as.slice(2), e)); return r;
          case 'flush': case 'close': return undefined;
          case 'write': salidaTxt(String.fromCharCode(a)); return undefined;
        }
      }
      if (r instanceof JSB) {
        switch (m) {
          case 'append': r.s += a instanceof JArr && a.t.n === 'char' ? a.a.map(c => String.fromCharCode(c.c)).join('') : aTexto(a); return r;
          case 'toString': return r.s;
          case 'length': return r.s.length;
          case 'insert': r.s = r.s.slice(0, a) + aTexto(b) + r.s.slice(a); return r;
          case 'reverse': r.s = [...r.s].reverse().join(''); return r;
          case 'setLength': r.s = a <= r.s.length ? r.s.slice(0, a) : r.s.padEnd(a, '\0'); return undefined;
          case 'deleteCharAt': r.s = r.s.slice(0, a) + r.s.slice(a + 1); return r;
          case 'delete': r.s = r.s.slice(0, a) + r.s.slice(b); return r;
          case 'charAt': return new Ch(r.s.charCodeAt(a));
          case 'isEmpty': return r.s.length === 0;
          case 'indexOf': return r.s.indexOf(a);
          case 'replace': r.s = r.s.slice(0, a) + as[2] + r.s.slice(b); return r;
          case 'setCharAt': r.s = r.s.slice(0, a) + String.fromCharCode(b.c) + r.s.slice(a + 1); return undefined;
          case 'equals': return r === a;
          case 'hashCode': return identidad(r);
          case 'chars': return new JStream([...r.s].map(c => c.charCodeAt(0)), 'int');
        }
      }
      if (r instanceof JRuta) {
        switch (m) {
          case 'toString': case 'getPath': return r.s;
          case 'getFileName': return new JRuta(r.s.split('/').pop());
          case 'getName': return r.s.split('/').pop();
          case 'resolve': return new JRuta(r.s + '/' + aTexto(a));
          case 'exists': case 'isFile': return ARCH.has(normalizar(r.s));
          case 'toPath': return r;
          case 'toFile': return r;
          case 'getParent': { const p = r.s.split('/'); p.pop(); return p.length ? new JRuta(p.join('/')) : null; }
          case 'equals': return a instanceof JRuta && normalizar(a.s) === normalizar(r.s);
          case 'toAbsolutePath': return r;
          case 'normalize': return new JRuta(normalizar(r.s));
        }
      }
      if (r instanceof JLector) {
        switch (m) {
          case 'readLine': return r.i < r.l.length ? r.l[r.i++] : null;
          case 'lines': { const ls = r.l.slice(r.i); r.i = r.l.length; return new JStream(ls); }
          case 'close': return undefined;
          case 'ready': return r.i < r.l.length;
        }
      }
      if (r instanceof JScanner) return metodoScanner(r, m, as, e);
      if (r instanceof JEntrada) {
        switch (m) {
          case 'getKey': return r.k;
          case 'getValue': return r.v;
          case 'setValue': { const v = r.v; r.v = a; return v; }
          case 'toString': return aTexto(r);
          case 'equals': return iguales(r, a);
          case 'hashCode': return hash(r);
        }
      }
      if (r instanceof JClaseRef) {
        switch (m) {
          case 'getSimpleName': return r.c ? (r.c.decl && r.c.decl.anonima ? '' : r.c.decl ? r.c.decl.nombre : r.c.nombre) : r.nombre;
          case 'getName': case 'getTypeName': case 'getCanonicalName': return r.c ? r.c.fq : 'java.lang.' + r.nombre;
          case 'toString': return aTexto(r);
          case 'equals': return iguales(r, a);
          case 'hashCode': return identidad(r.c || r);
          case 'isInstance': return a !== null && esDeTipo(a, { n: r.c ? r.c.nombre : r.nombre, d: 0 });
          case 'getSuperclass': return r.c && r.c.padre ? new JClaseRef(r.c.padre) : null;
        }
      }
      if (r instanceof JIterador) {
        switch (m) {
          case 'hasNext': return r.i < r.a.length;
          case 'next': if (r.i >= r.a.length) lanzar('NoSuchElementException', null); return r.a[r.i++];
          case 'remove': if (!r.dueno) err(e, 'remove de un iterador'); { const x = r.a[r.i - 1]; r.dueno(x); return undefined; }
        }
      }
      if (r instanceof JArr) {
        switch (m) {
          case 'clone': return new JArr(r.t, [...r.a]);
          case 'equals': return r === a;
          case 'hashCode': return identidad(r);
          case 'getClass': return new JClaseRef(null, r.t.n + '[]');
          case 'toString': return aTexto(r);
        }
      }
      if (r instanceof JCharset) { if (m === 'name' || m === 'toString' || m === 'displayName') return r.n; }
      err(e, 'el método ' + m + ' sobre ' + (r && r.constructor ? r.constructor.name.replace(/^J/, '') : typeof r));
    }

    function metodoString(s, m, as, e) {
      const a = as[0], b = as[1];
      const idx = (i, n = s.length) => { if (i < 0 || i > n) lanzar('StringIndexOutOfBoundsException', 'begin ' + i + ', end ' + n + ', length ' + s.length); return i; };
      switch (m) {
        case 'length': return s.length;
        case 'isEmpty': return s.length === 0;
        case 'isBlank': return strip(s) === '';
        case 'trim': return trim(s);
        case 'strip': return strip(s);
        case 'stripLeading': return strip(s, true, false);
        case 'stripTrailing': return strip(s, false, true);
        case 'equals': return typeof a === 'string' && a === s;
        case 'equalsIgnoreCase': return typeof a === 'string' && a.toLowerCase() === s.toLowerCase() && a.length === s.length;
        case 'compareTo': if (a === null) npe(); return compararNatural(s, a);
        case 'compareToIgnoreCase': return compararNatural(s.toUpperCase().toLowerCase(), a.toUpperCase().toLowerCase());
        case 'contains': if (a === null) npe(); return s.includes(aTexto(a));
        case 'startsWith': return s.startsWith(a, b || 0);
        case 'endsWith': return s.endsWith(a);
        case 'indexOf': return s.indexOf(a instanceof Ch ? String.fromCharCode(a.c) : typeof a === 'number' ? String.fromCharCode(a) : a, b === undefined ? 0 : b);
        case 'lastIndexOf': return s.lastIndexOf(a instanceof Ch ? String.fromCharCode(a.c) : typeof a === 'number' ? String.fromCharCode(a) : a);
        case 'charAt': if (a < 0 || a >= s.length) lanzar('StringIndexOutOfBoundsException', 'Index ' + a + ' out of bounds for length ' + s.length); return new Ch(s.charCodeAt(a));
        case 'substring': { const fin = b === undefined ? s.length : b; if (a < 0 || fin > s.length || a > fin) lanzar('StringIndexOutOfBoundsException', 'begin ' + a + ', end ' + fin + ', length ' + s.length); return s.slice(a, fin); }
        case 'subSequence': return s.slice(idx(a), idx(b));
        case 'toUpperCase': return s.toUpperCase();
        case 'toLowerCase': return s.toLowerCase();
        case 'replace': {
          const x = a instanceof Ch ? String.fromCharCode(a.c) : aTexto(a), y = b instanceof Ch ? String.fromCharCode(b.c) : aTexto(b);
          return s.split(x).join(y);
        }
        case 'replaceAll': return s.replace(regexDeJava(a), b.replace(/\$(\d)/g, '$$$1'));
        case 'replaceFirst': { const re = regexDeJava(a); return s.replace(new RegExp(re.source), b); }
        case 'matches': return new RegExp('^(?:' + regexDeJava(a).source + ')$').test(s);
        case 'split': return new JArr({ n: 'String', d: 0 }, split(s, a, b === undefined ? 0 : b));
        case 'toCharArray': return new JArr({ n: 'char', d: 0 }, [...s].map(c => new Ch(c.charCodeAt(0))));
        case 'chars': return new JStream(Array.from(s, c => c.charCodeAt(0)), 'int');
        case 'hashCode': return hashTexto(s);
        case 'toString': case 'intern': case 'strip_': return s;
        case 'formatted': return formatear(s, as, e);
        case 'repeat': if (a < 0) lanzar('IllegalArgumentException', 'count is negative: ' + a); return s.repeat(a);
        case 'concat': return s + a;
        case 'lines': return new JStream(lineasDe(s));
        case 'getClass': return new JClaseRef(null, 'String');
        case 'codePointAt': return s.codePointAt(a);
        case 'indent': return lineasDe(s).map(l => (a >= 0 ? ' '.repeat(a) + l : l.replace(new RegExp('^ {0,' + -a + '}'), ''))).join('\n') + '\n';
      }
      err(e, 'el método ' + m + ' de String');
    }

    function metodoLista(r, m, as, e) {
      const a = as[0], b = as[1], x = r.a;
      switch (m) {
        case 'add': noModificable(r); if (as.length === 2) { if (a < 0 || a > x.length) fueraDeRango(a, x.length); x.splice(a, 0, b); return undefined; } x.push(a); return true;
        case 'addAll': noModificable(r); { const ys = [...elementos(as.length === 2 ? b : a)]; if (as.length === 2) x.splice(a, 0, ...ys); else x.push(...ys); return ys.length > 0; }
        case 'get': if (a < 0 || a >= x.length) fueraDeRango(a, x.length); return x[a];
        case 'set': noModificable(r); if (a < 0 || a >= x.length) fueraDeRango(a, x.length); { const v = x[a]; x[a] = b; return v; }
        case 'size': return x.length;
        case 'isEmpty': return x.length === 0;
        case 'contains': return x.some(y => iguales(y, a));
        case 'containsAll': return elementos(a).every(z => x.some(y => iguales(y, z)));
        case 'indexOf': return x.findIndex(y => iguales(y, a));
        case 'lastIndexOf': { for (let i = x.length - 1; i >= 0; i--) if (iguales(x[i], a)) return i; return -1; }
        case 'remove': noModificable(r);
          if (typeof a === 'number' && !(e && e.objetoEntero)) { if (a < 0 || a >= x.length) fueraDeRango(a, x.length); return x.splice(a, 1)[0]; }
          { const i = x.findIndex(y => iguales(y, a)); if (i >= 0) x.splice(i, 1); return i >= 0; }
        case 'removeIf': noModificable(r); { const antes = x.length; const quedan = x.filter(y => !llamarFn(a, [y])); x.splice(0, x.length, ...quedan); return quedan.length !== antes; }
        case 'clear': noModificable(r); x.length = 0; return undefined;
        case 'stream': return new JStream([...x]);
        case 'forEach': for (const y of [...x]) llamarFn(a, [y]); return undefined;
        case 'iterator': case 'listIterator': { const it = new JIterador(x); it.dueno = y => { noModificable(r); const i = x.indexOf(y); x.splice(i, 1); it.i--; }; return it; }
        case 'sort': noModificable(r); { const s = ordenar(x, a); x.splice(0, x.length, ...s); return undefined; }
        case 'toArray': return new JArr({ n: as.length && a instanceof JArr ? a.t.n : 'Object', d: 0 }, [...x]);
        case 'subList': return nuevaLista(x.slice(a, b), r.ro);
        case 'toString': return aTexto(r);
        case 'equals': return iguales(r, a);
        case 'hashCode': return hash(r);
        case 'getFirst': case 'peekFirst': case 'peek': case 'element': if (!x.length) { if (m.startsWith('peek')) return null; lanzar('NoSuchElementException', null); } return x[0];
        case 'getLast': case 'peekLast': if (!x.length) { if (m === 'peekLast') return null; lanzar('NoSuchElementException', null); } return x[x.length - 1];
        case 'removeFirst': case 'poll': case 'pollFirst': case 'pop': noModificable(r); if (!x.length) { if (m.startsWith('poll')) return null; lanzar('NoSuchElementException', null); } return x.shift();
        case 'removeLast': case 'pollLast': noModificable(r); if (!x.length) { if (m === 'pollLast') return null; lanzar('NoSuchElementException', null); } return x.pop();
        case 'addFirst': case 'push': case 'offerFirst': noModificable(r); x.unshift(a); return undefined;
        case 'addLast': case 'offer': case 'offerLast': noModificable(r); x.push(a); return true;
        case 'reversed': return nuevaLista([...x].reverse(), r.ro);
        case 'replaceAll': noModificable(r); for (let i = 0; i < x.length; i++) x[i] = llamarFn(a, [x[i]]); return undefined;
        case 'getClass': return new JClaseRef(null, r.ro ? 'ImmutableCollections$ListN' : 'ArrayList');
      }
      err(e, 'el método ' + m + ' de una lista');
    }
    function metodoMapa(r, m, as, e) {
      const a = as[0], b = as[1];
      switch (m) {
        case 'put': return poner(r, a, b);
        case 'get': { if (r.clase === 'TreeMap' && a === null && !r.cmp) npe(); const x = buscarEntrada(r, a); return x ? x.v : null; }
        case 'getOrDefault': { const x = buscarEntrada(r, a); return x ? x.v : b; }
        case 'containsKey': return !!buscarEntrada(r, a);
        case 'containsValue': return r.e.some(x => iguales(x.v, a));
        case 'remove': return sacar(r, a);
        case 'size': return r.e.length;
        case 'isEmpty': return r.e.length === 0;
        case 'clear': noModificable(r); r.e.length = 0; return undefined;
        case 'putIfAbsent': { const x = buscarEntrada(r, a); if (x && x.v !== null) return x.v; poner(r, a, b); return null; }
        case 'merge': {
          const x = buscarEntrada(r, a);
          if (!x || x.v === null) { poner(r, a, b); return b; }
          const v = llamarFn(as[2], [x.v, b]);
          if (v === null) sacar(r, a); else { noModificable(r); x.v = v; }
          return v;
        }
        case 'computeIfAbsent': { const x = buscarEntrada(r, a); if (x && x.v !== null) return x.v; const v = llamarFn(b, [a]); if (v !== null) poner(r, a, v); return v; }
        case 'computeIfPresent': { const x = buscarEntrada(r, a); if (!x || x.v === null) return null; const v = llamarFn(b, [a, x.v]); if (v === null) sacar(r, a); else x.v = v; return v; }
        case 'compute': { const x = buscarEntrada(r, a); const v = llamarFn(b, [a, x ? x.v : null]); if (v === null) { if (x) sacar(r, a); } else poner(r, a, v); return v; }
        case 'putAll': for (const x of entradas(a)) poner(r, x.k, x.v); return undefined;
        case 'keySet': { const c = new JConjunto(nuevoMapa('LinkedHashMap')); for (const x of entradas(r)) c.m.e.push(new JEntrada(x.k, true, hash(x.k))); c.vistaDe = r; return c; }
        case 'values': return nuevaLista(entradas(r).map(x => x.v), r.ro);
        case 'entrySet': { const c = new JConjunto(nuevoMapa('LinkedHashMap')); for (const x of entradas(r)) c.m.e.push(new JEntrada(x, true, 0)); c.entradas = true; c.vistaDe = r; return c; }
        case 'forEach': for (const x of [...entradas(r)]) llamarFn(a, [x.k, x.v]); return undefined;
        case 'toString': return aTexto(r);
        case 'equals': return iguales(r, a);
        case 'hashCode': return hash(r);
        case 'firstKey': case 'lastKey': if (!r.e.length) lanzar('NoSuchElementException', null); return m === 'firstKey' ? r.e[0].k : r.e[r.e.length - 1].k;
        case 'firstEntry': case 'lastEntry': return r.e.length ? (m === 'firstEntry' ? r.e[0] : r.e[r.e.length - 1]) : null;
        case 'headMap': case 'tailMap': {
          const f = comparadorDe(r.cmp), mm = nuevoMapa('TreeMap', r.cmp);
          for (const x of r.e) { const c = f(x.k, a); if (m === 'headMap' ? c < 0 || (b && c === 0) : c >= 0) mm.e.push(x); }
          return mm;
        }
        case 'replaceAll': for (const x of r.e) x.v = llamarFn(a, [x.k, x.v]); return undefined;
        case 'getClass': return new JClaseRef(null, r.clase);
      }
      err(e, 'el método ' + m + ' de un Map');
    }
    function metodoConjunto(r, m, as, e) {
      const a = as[0];
      const lista = () => entradas(r.m).map(x => x.k);
      switch (m) {
        case 'add': noModificable(r); if (buscarEntrada(r.m, a)) return false; poner(r.m, a, true); return true;
        case 'addAll': noModificable(r); { let cambio = false; for (const x of elementos(a)) if (!buscarEntrada(r.m, x)) { poner(r.m, x, true); cambio = true; } return cambio; }
        case 'contains': return r.entradas ? r.m.e.some(x => iguales(x.k, a)) : !!buscarEntrada(r.m, a);
        case 'remove': noModificable(r); { const ok = !!buscarEntrada(r.m, a); sacar(r.m, a); if (ok && r.vistaDe) sacar(r.vistaDe, a); return ok; }
        case 'size': return r.m.e.length;
        case 'isEmpty': return r.m.e.length === 0;
        case 'clear': noModificable(r); r.m.e.length = 0; return undefined;
        case 'stream': return new JStream(lista());
        case 'forEach': for (const x of lista()) llamarFn(a, [x]); return undefined;
        case 'iterator': return new JIterador(lista());
        case 'toArray': return new JArr({ n: 'Object', d: 0 }, lista());
        case 'toString': return aTexto(r);
        case 'equals': return iguales(r, a);
        case 'hashCode': return hash(r);
        case 'containsAll': return elementos(a).every(x => !!buscarEntrada(r.m, x));
        case 'retainAll': { const ys = elementos(a); const quedan = r.m.e.filter(x => ys.some(y => iguales(y, x.k))); const c = quedan.length !== r.m.e.length; r.m.e.splice(0, r.m.e.length, ...quedan); return c; }
        case 'removeAll': { let c = false; for (const y of elementos(a)) if (sacar(r.m, y) !== null) c = true; return c; }
        case 'removeIf': { const antes = r.m.e.length; const quedan = r.m.e.filter(x => !llamarFn(a, [x.k])); r.m.e.splice(0, r.m.e.length, ...quedan); return quedan.length !== antes; }
        case 'first': case 'last': if (!r.m.e.length) lanzar('NoSuchElementException', null); return m === 'first' ? r.m.e[0].k : r.m.e[r.m.e.length - 1].k;
      }
      err(e, 'el método ' + m + ' de un Set');
    }
    function metodoOpcional(r, m, as, e) {
      const a = as[0];
      switch (m) {
        case 'isPresent': return r.hay;
        case 'isEmpty': return !r.hay;
        case 'get': case 'getAsInt': case 'getAsDouble': case 'getAsLong': case 'orElseThrow':
          if (!r.hay) { if (m === 'orElseThrow' && as.length) throw new Lanzado(llamarFn(a, [])); lanzar('NoSuchElementException', 'No value present'); }
          return r.v;
        case 'orElse': return r.hay ? r.v : a;
        case 'orElseGet': return r.hay ? r.v : llamarFn(a, []);
        case 'ifPresent': if (r.hay) llamarFn(a, [r.v]); return undefined;
        case 'ifPresentOrElse': if (r.hay) llamarFn(a, [r.v]); else llamarFn(as[1], []); return undefined;
        case 'map': return r.hay ? (v => new JOpcional(v !== null, v))(llamarFn(a, [r.v])) : r;
        case 'flatMap': return r.hay ? llamarFn(a, [r.v]) : r;
        case 'filter': return r.hay && llamarFn(a, [r.v]) ? r : new JOpcional(false, null, r.tipo);
        case 'or': return r.hay ? r : llamarFn(a, []);
        case 'stream': return new JStream(r.hay ? [r.v] : []);
        case 'toString': return aTexto(r);
        case 'equals': return iguales(r, a);
      }
      err(e, 'el método ' + m + ' de un Optional');
    }
    function metodoScanner(r, m, as, e) {
      const resto = () => r.t.slice(r.i);
      switch (m) {
        case 'hasNextLine': return r.i < r.t.length;
        case 'nextLine': {
          if (r.i >= r.t.length) lanzar('NoSuchElementException', 'No line found');
          const mm = /\r\n|\r|\n/.exec(resto());
          const l = mm ? resto().slice(0, mm.index) : resto();
          r.i += mm ? mm.index + mm[0].length : resto().length;
          return l;
        }
        case 'hasNext': return /\S/.test(resto());
        case 'next': case 'nextInt': case 'nextDouble': case 'nextLong': {
          const mm = /^\s*(\S+)/.exec(resto());
          if (!mm) lanzar('NoSuchElementException', null);
          if (m === 'nextInt' && !/^[+-]?\d+$/.test(mm[1])) lanzar('InputMismatchException', 'For input string: "' + mm[1] + '"');
          r.i += mm[0].length;
          return m === 'nextInt' ? parseEntero(mm[1]) : m === 'nextLong' ? parseEntero(mm[1], true) : m === 'nextDouble' ? parseDoble(mm[1].replace(SEP_DEC, '.')) : mm[1];
        }
        case 'hasNextInt': return /^\s*[+-]?\d+(\s|$)/.test(resto());
        case 'useDelimiter': err(e, 'Scanner.useDelimiter');
        case 'close': return undefined;
      }
      err(e, 'el método ' + m + ' de Scanner');
    }

    // ── Streams
    function metodoStream(r, m, as, e) {
      const a = as[0], b = as[1], x = r.a, T = r.tipo;
      const prim = T !== 'obj';
      const suma = () => T === 'double' ? new D(x.reduce((s, y) => s + aNumero(y), 0)) : T === 'long' ? x.reduce((s, y) => L(s + aLong(y)), 0n) : x.reduce((s, y) => (s + aInt(y)) | 0, 0);
      switch (m) {
        case 'filter': return new JStream(x.filter(y => llamarFn(a, [y])), T);
        case 'map': return new JStream(x.map(y => prim ? convertir(llamarFn(a, [y]), { n: T, d: 0 }) : llamarFn(a, [y])), T);
        case 'mapToInt': return new JStream(x.map(y => castear({ n: 'int', d: 0 }, llamarFn(a, [y]))), 'int');
        case 'mapToLong': return new JStream(x.map(y => convertir(llamarFn(a, [y]), { n: 'long', d: 0 })), 'long');
        case 'mapToDouble': case 'asDoubleStream': return new JStream(x.map(y => convertir(m === 'asDoubleStream' ? y : llamarFn(a, [y]), { n: 'double', d: 0 })), 'double');
        case 'mapToObj': return new JStream(x.map(y => llamarFn(a, [y])));
        case 'boxed': return new JStream([...x]);
        case 'asLongStream': return new JStream(x.map(y => aLong(y)), 'long');
        case 'flatMap': return new JStream(x.flatMap(y => [...elementos(llamarFn(a, [y]))]));
        case 'peek': for (const y of x) llamarFn(a, [y]); return new JStream([...x], T);
        case 'distinct': { const out = []; for (const y of x) if (!out.some(z => iguales(z, y))) out.push(y); return new JStream(out, T); }
        case 'sorted': return new JStream(ordenar(x, a || null), T);
        case 'limit': return new JStream(x.slice(0, Number(a)), T);
        case 'skip': return new JStream(x.slice(Number(a)), T);
        case 'takeWhile': { const i = x.findIndex(y => !llamarFn(a, [y])); return new JStream(i < 0 ? [...x] : x.slice(0, i), T); }
        case 'dropWhile': { const i = x.findIndex(y => !llamarFn(a, [y])); return new JStream(i < 0 ? [] : x.slice(i), T); }
        case 'forEach': case 'forEachOrdered': for (const y of x) llamarFn(a, [y]); return undefined;
        case 'count': return BigInt(x.length);
        case 'sum': return suma();
        case 'average': return x.length ? new JOpcional(true, new D(aNumero(suma()) / x.length), 'double') : new JOpcional(false, null, 'double');
        case 'max': case 'min': {
          if (!x.length) return new JOpcional(false, null, prim ? T : 'obj');
          const f = comparadorDe(prim ? null : a);
          return new JOpcional(true, x.reduce((p, y) => (m === 'max' ? f(y, p) > 0 : f(y, p) < 0) ? y : p), prim ? T : 'obj');
        }
        case 'findFirst': case 'findAny': return x.length ? new JOpcional(true, x[0], prim ? T : 'obj') : new JOpcional(false, null, prim ? T : 'obj');
        case 'anyMatch': return x.some(y => llamarFn(a, [y]));
        case 'allMatch': return x.every(y => llamarFn(a, [y]));
        case 'noneMatch': return !x.some(y => llamarFn(a, [y]));
        case 'reduce':
          if (as.length === 1) return x.length ? new JOpcional(true, x.reduce((p, y) => llamarFn(a, [p, y])), prim ? T : 'obj') : new JOpcional(false, null, prim ? T : 'obj');
          return x.reduce((p, y) => llamarFn(b, [p, y]), a);
        case 'collect': if (a instanceof JColector) return recolectar(a, x); err(e, 'collect con tres parámetros');
        case 'toList': return nuevaLista([...x], true);
        case 'toArray': return new JArr({ n: prim ? T : 'Object', d: 0 }, [...x]);
        case 'iterator': return new JIterador([...x]);
        case 'summaryStatistics': return resumenEstadistico(x, T);
        case 'getAsInt': case 'getAsDouble': break;
        case 'parallel': case 'sequential': case 'unordered': case 'onClose': return r;
        case 'close': return undefined;
      }
      err(e, 'el método ' + m + ' de un stream');
    }
    function resumenEstadistico(x, T) {
      const o = nuevoMapa('LinkedHashMap');
      const n = x.length, s = x.reduce((p, y) => p + aNumero(y), 0);
      const st = { getCount: BigInt(n), getSum: T === 'double' ? new D(s) : T === 'int' ? BigInt(s) : BigInt(s), getMin: n ? (T === 'double' ? new D(Math.min(...x.map(aNumero))) : Math.min(...x.map(aNumero))) : (T === 'double' ? new D(Infinity) : 2147483647),
        getMax: n ? (T === 'double' ? new D(Math.max(...x.map(aNumero))) : Math.max(...x.map(aNumero))) : (T === 'double' ? new D(-Infinity) : -2147483648), getAverage: new D(n ? s / n : 0) };
      return fn(() => o, { estadisticas: st });
    }
    // Collectors
    function colector(m, as, e) {
      const a = as[0], b = as[1], c = as[2];
      switch (m) {
        case 'toList': case 'toUnmodifiableList': return new JColector('lista', { ro: m === 'toUnmodifiableList' });
        case 'toSet': return new JColector('conjunto');
        case 'toCollection': return new JColector('coleccion', { proveedor: a });
        case 'counting': return new JColector('contar');
        case 'summingInt': case 'summingLong': case 'summingDouble': return new JColector('sumar', { f: a, tipo: m === 'summingInt' ? 'int' : m === 'summingLong' ? 'long' : 'double' });
        case 'averagingInt': case 'averagingLong': case 'averagingDouble': return new JColector('promedio', { f: a });
        case 'mapping': return new JColector('mapear', { f: a, abajo: b });
        case 'filtering': return new JColector('filtrar', { f: a, abajo: b });
        case 'flatMapping': return new JColector('aplanar', { f: a, abajo: b });
        case 'maxBy': case 'minBy': return new JColector(m, { cmp: a });
        case 'collectingAndThen': return new JColector('luego', { abajo: a, f: b });
        case 'joining': return new JColector('unir', { sep: a === undefined ? '' : a, pre: b || '', suf: c || '' });
        case 'groupingBy': {
          if (as.length === 1) return new JColector('agrupar', { f: a, fabrica: null, abajo: new JColector('lista', {}) });
          if (as.length === 2) return new JColector('agrupar', { f: a, fabrica: null, abajo: b });
          return new JColector('agrupar', { f: a, fabrica: b, abajo: c });
        }
        case 'partitioningBy': return new JColector('particion', { f: a, abajo: b || new JColector('lista', {}) });
        case 'toMap': return new JColector('aMapa', { k: a, v: b, unir: c || null, fabrica: as[3] || null });
        case 'reducing': return new JColector('reducir', { id: a, op: b });
        case 'summarizingInt': case 'summarizingDouble': return new JColector('resumen', { f: a, tipo: m === 'summarizingInt' ? 'int' : 'double' });
        case 'teeing': return new JColector('teeing', { c1: a, c2: b, f: c });
      }
      err(e, 'Collectors.' + m);
    }
    function recolectar(c, xs) {
      switch (c.c) {
        case 'lista': return nuevaLista([...xs], c.ro);
        case 'conjunto': { const s = new JConjunto(nuevoMapa('HashMap')); for (const x of xs) poner(s.m, x, true); return s; }
        case 'coleccion': { const col = llamarFn(c.proveedor, []); for (const x of xs) llamarMetodo(col, 'add', [x]); return col; }
        case 'contar': return BigInt(xs.length);
        case 'sumar': return c.tipo === 'double' ? new D(xs.reduce((s, x) => s + aNumero(llamarFn(c.f, [x])), 0)) : c.tipo === 'long' ? xs.reduce((s, x) => L(s + aLong(llamarFn(c.f, [x]))), 0n) : xs.reduce((s, x) => (s + aInt(llamarFn(c.f, [x]))) | 0, 0);
        case 'promedio': return new D(xs.length ? xs.reduce((s, x) => s + aNumero(llamarFn(c.f, [x])), 0) / xs.length : 0);
        case 'mapear': return recolectar(c.abajo, xs.map(x => llamarFn(c.f, [x])));
        case 'filtrar': return recolectar(c.abajo, xs.filter(x => llamarFn(c.f, [x])));
        case 'aplanar': return recolectar(c.abajo, xs.flatMap(x => elementos(llamarFn(c.f, [x]))));
        case 'maxBy': case 'minBy': {
          if (!xs.length) return new JOpcional(false, null);
          const f = comparadorDe(c.cmp);
          return new JOpcional(true, xs.reduce((p, y) => (c.c === 'maxBy' ? f(y, p) > 0 : f(y, p) < 0) ? y : p));
        }
        case 'luego': return llamarFn(c.f, [recolectar(c.abajo, xs)]);
        case 'unir': return c.pre + xs.map(aTexto).join(aTexto(c.sep)) + c.suf;
        case 'agrupar': {
          const mapa = c.fabrica ? llamarFn(c.fabrica, []) : nuevoMapa('HashMap');
          const grupos = nuevoMapa('LinkedHashMap');
          for (const x of xs) {
            const k = llamarFn(c.f, [x]);
            if (k === null) lanzar('NullPointerException', 'element cannot be mapped to a null key');
            const g = buscarEntrada(grupos, k);
            if (g) g.v.push(x); else poner(grupos, k, [x]);
          }
          for (const g of grupos.e) poner(mapa, g.k, recolectar(c.abajo, g.v));
          return mapa;
        }
        case 'particion': {
          const mapa = nuevoMapa('LinkedHashMap');
          poner(mapa, false, recolectar(c.abajo, xs.filter(x => !llamarFn(c.f, [x]))));
          poner(mapa, true, recolectar(c.abajo, xs.filter(x => llamarFn(c.f, [x]))));
          return mapa;
        }
        case 'aMapa': {
          const mapa = c.fabrica ? llamarFn(c.fabrica, []) : nuevoMapa('HashMap');
          for (const x of xs) {
            const k = llamarFn(c.k, [x]), v = llamarFn(c.v, [x]);
            const viejo = buscarEntrada(mapa, k);
            if (viejo) { if (!c.unir) lanzar('IllegalStateException', 'Duplicate key ' + aTexto(k) + ' (attempted merging values ' + aTexto(viejo.v) + ' and ' + aTexto(v) + ')'); viejo.v = llamarFn(c.unir, [viejo.v, v]); }
            else poner(mapa, k, v);
          }
          return mapa;
        }
        case 'reducir': return xs.reduce((p, y) => llamarFn(c.op, [p, y]), c.id);
        case 'resumen': return resumenEstadistico(xs.map(x => llamarFn(c.f, [x])), c.tipo);
        case 'teeing': return llamarFn(c.f, [recolectar(c.c1, xs), recolectar(c.c2, xs)]);
      }
      falla('no sé recolectar con ' + c.c);
    }

    // ═══ El main
    let codigo = 0;
    const mains = [...clases.values()].filter(c => !c.nativa && (c.metodos.get('main') || []).some(m => m.estatico && m.params.length === 1 && m.params[0].t.n === 'String'));
    const principal = op.principal ? mains.find(c => c.nombre === op.principal || c.fq === op.principal) : mains[0];
    if (!principal) return { salida: '', error: 'No encontré ninguna clase con public static void main(String[] args).', codigo: -1, clases: [...clases.values()].filter(c => !c.nativa).map(c => c.nombre) };
    try {
      const m = principal.metodos.get('main').find(x => x.estatico && x.params.length === 1);
      iniciarClase(principal);
      invocar(m, null, [new JArr({ n: 'String', d: 0 }, args.map(String))], m);
    } catch (x) {
      if (x instanceof Fin) codigo = x.codigo;
      else if (x instanceof Lanzado) {
        errores.push('Exception in thread "main" ' + textoExcepcion(x.ex) + '\n');
        for (let c = x.ex.f.get('cause'); c; c = c.f.get('cause')) errores.push('Caused by: ' + textoExcepcion(c) + '\n');
        codigo = 1;
      } else if (x instanceof ErrorJava) return { salida: salida.join(''), error: x.message, codigo: -1, noSoportado: true, principal: principal.fq };
      else if (x instanceof Retorno || x instanceof Corte || x instanceof Sigue) codigo = 0;
      else if (x instanceof RangeError) return { salida: salida.join(''), error: 'Exception in thread "main" java.lang.StackOverflowError', codigo: 1, principal: principal.fq };
      else throw x;
    }
    return { salida: salida.join(''), error: errores.join(''), codigo, principal: principal.fq };
  }

  return { ejecutar, lexico, sintaxis, ErrorJava, D, Ch, dobleATexto };
});
