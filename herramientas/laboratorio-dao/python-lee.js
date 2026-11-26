/* Un lector de Python (lo que hace falta para entender un archivo de tests de pytest): separa en tokens con la sangría,
   y arma el árbol de sentencias y expresiones. No ejecuta nada.
   Uso: PyLee.leer(texto) → [sentencias]   (cada nodo trae «t» con su tipo y «l» con su línea) */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica();
  else raiz.PyLee = fabrica();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const PALABRAS = new Set('and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield True False None'.split(' '));
  const OPS = ['**=', '//=', '>>=', '<<=', '...', '->', ':=', '**', '//', '==', '!=', '<=', '>=', '<<', '>>', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '@=',
    '+', '-', '*', '/', '%', '@', '<', '>', '=', '(', ')', '[', ']', '{', '}', ',', ':', '.', ';', '~', '&', '|', '^'];

  // ── Tokens (con NEWLINE, INDENT y DEDENT como en Python)
  function tokens(texto) {
    const t = texto.replace(/\r\n?/g, '\n').replace(/\t/g, '    ') + '\n';
    const out = [], pila = [0];
    let i = 0, linea = 1, prof = 0, inicio = true;
    const push = (tipo, v, l) => out.push({ tipo, v, l: l || linea });
    while (i < t.length) {
      if (inicio && prof === 0) {
        // sangría de una línea lógica nueva (las vacías y los comentarios no cuentan)
        let j = i, col = 0;
        while (t[j] === ' ') { col++; j++; }
        if (t[j] === '\n' || t[j] === '#' || (t[j] === '\\' && t[j + 1] === '\n')) { while (j < t.length && t[j] !== '\n') j++; i = j + 1; linea++; continue; }
        if (col > pila[pila.length - 1]) { pila.push(col); push('INDENT'); }
        while (col < pila[pila.length - 1]) { pila.pop(); push('DEDENT'); }
        i = j; inicio = false;
      }
      const c = t[i];
      if (c === '\n') { if (prof === 0) { push('NEWLINE'); inicio = true; } i++; linea++; continue; }
      if (c === ' ') { i++; continue; }
      if (c === '#') { while (i < t.length && t[i] !== '\n') i++; continue; }
      if (c === '\\' && t[i + 1] === '\n') { i += 2; linea++; continue; }
      // cadenas (con prefijos f, r, b, u)
      const mp = t.slice(i).match(/^([rRbBuUfF]{0,2})("""|'''|"|')/);
      if (mp && (mp[1] === '' || /^[rRbBuUfF]{1,2}$/.test(mp[1])) && (mp[1] === '' || !/[\w]/.test(t[i - 1] || ''))) {
        const pre = mp[1].toLowerCase(), q = mp[2], l0 = linea;
        let j = i + mp[0].length, s = '';
        while (j < t.length && t.slice(j, j + q.length) !== q) {
          if (t[j] === '\\' && !pre.includes('r')) {
            const e = t[j + 1];
            s += ({ n: '\n', t: '\t', '\\': '\\', "'": "'", '"': '"', '\n': '' })[e] ?? ('\\' + e); j += 2; if (e === '\n') linea++; continue;
          }
          if (t[j] === '\n') { if (q.length === 1) break; linea++; }
          s += t[j]; j++;
        }
        i = j + q.length;
        push(pre.includes('f') ? 'FSTR' : 'STR', s, l0);
        continue;
      }
      const mn = t.slice(i).match(/^(?:0[xX][\da-fA-F_]+|(?:\d[\d_]*\.?[\d_]*|\.\d[\d_]*)(?:[eE][+-]?\d+)?j?)/);
      if (mn && /[\d.]/.test(c) && !(c === '.' && !/\d/.test(t[i + 1] || ''))) {
        const s = mn[0].replace(/_/g, '');
        push('NUM', { v: Number(s), real: /[.eE]/.test(s) && !/^0[xX]/.test(s) });
        i += mn[0].length; continue;
      }
      const mi = t.slice(i).match(/^[A-Za-z_À-ɏ][\wÀ-ɏ]*/);
      if (mi) { push(PALABRAS.has(mi[0]) ? 'KW' : 'NAME', mi[0]); i += mi[0].length; continue; }
      const op = OPS.find(o => t.startsWith(o, i));
      if (op) { if ('([{'.includes(op)) prof++; else if (')]}'.includes(op)) prof = Math.max(0, prof - 1); push('OP', op); i += op.length; continue; }
      i++;   // algo que no se entiende: se saltea
    }
    push('NEWLINE');
    while (pila.length > 1) { pila.pop(); push('DEDENT'); }
    push('EOF');
    return out;
  }

  // ── Sentencias y expresiones
  function leer(texto) {
    const tk = tokens(texto);
    let p = 0;
    const ver = (k = 0) => tk[p + k];
    const es = (tipo, v) => ver().tipo === tipo && (v === undefined || ver().v === v);
    const op = v => es('OP', v), kw = v => es('KW', v);
    const tomar = () => tk[p++];
    const pedir = (tipo, v) => { if (!es(tipo, v)) throw new Error(`Línea ${ver().l}: esperaba ${v || tipo} y encontré ${typeof ver().v === 'object' ? 'un número' : ver().v || ver().tipo}`); return tomar(); };
    const saltarNL = () => { while (es('NEWLINE') || op(';')) tomar(); };

    function bloque() {
      if (es('NEWLINE')) { tomar(); saltarNL(); pedir('INDENT'); const ss = []; while (!es('DEDENT') && !es('EOF')) { ss.push(...sentencia()); saltarNL(); } if (es('DEDENT')) tomar(); return ss; }
      return simples();   // «if x: return y» en la misma línea
    }
    function sentencia() {
      const l = ver().l;
      if (op('@')) { const dec = []; while (op('@')) { tomar(); dec.push(expr()); saltarNL(); } const s = sentencia(); s[0].decoradores = dec; return s; }
      if (kw('def') || (es('KW', 'async') && tk[p + 1].v === 'def')) {
        if (kw('async')) tomar();
        tomar(); const nombre = pedir('NAME').v; pedir('OP', '('); const params = parametros(')'); pedir('OP', ')');
        if (op('->')) { tomar(); expr(); }
        pedir('OP', ':'); return [{ t: 'def', nombre, params, cuerpo: bloque(), l }];
      }
      if (kw('class')) {
        tomar(); const nombre = pedir('NAME').v; let bases = [];
        if (op('(')) { tomar(); bases = argumentos(')').pos; pedir('OP', ')'); }
        pedir('OP', ':'); return [{ t: 'class', nombre, bases, cuerpo: bloque(), l }];
      }
      if (kw('if')) {
        tomar(); const ramas = [[expr(), (pedir('OP', ':'), bloque())]]; let sino = null;
        saltarNL();
        while (kw('elif')) { tomar(); ramas.push([expr(), (pedir('OP', ':'), bloque())]); saltarNL(); }
        if (kw('else')) { tomar(); pedir('OP', ':'); sino = bloque(); }
        return [{ t: 'if', ramas, sino, l }];
      }
      if (kw('for')) { tomar(); const destino = listaDestinos(); pedir('KW', 'in'); const it = exprLista(); pedir('OP', ':'); const cuerpo = bloque(); saltarNL(); let sino = null; if (kw('else')) { tomar(); pedir('OP', ':'); sino = bloque(); } return [{ t: 'for', destino, it, cuerpo, sino, l }]; }
      if (kw('while')) { tomar(); const c = expr(); pedir('OP', ':'); return [{ t: 'while', c, cuerpo: bloque(), l }]; }
      if (kw('with')) {
        tomar(); const items = [];
        do { const e = expr(); let como = null; if (kw('as')) { tomar(); como = destinoSimple(); } items.push({ e, como }); } while (op(',') && tomar());
        pedir('OP', ':'); return [{ t: 'with', items, cuerpo: bloque(), l }];
      }
      if (kw('try')) {
        tomar(); pedir('OP', ':'); const cuerpo = bloque(), manejadores = []; let sino = null, fin = null;
        saltarNL();
        while (kw('except')) { tomar(); let tipo = null, como = null; if (!op(':')) { tipo = expr(); if (kw('as')) { tomar(); como = pedir('NAME').v; } } pedir('OP', ':'); manejadores.push({ tipo, como, cuerpo: bloque() }); saltarNL(); }
        if (kw('else')) { tomar(); pedir('OP', ':'); sino = bloque(); saltarNL(); }
        if (kw('finally')) { tomar(); pedir('OP', ':'); fin = bloque(); }
        return [{ t: 'try', cuerpo, manejadores, sino, fin, l }];
      }
      return simples();
    }
    function simples() {
      const ss = [];
      for (;;) { ss.push(simple()); if (op(';')) { tomar(); if (es('NEWLINE')) break; continue; } break; }
      if (es('NEWLINE')) tomar();
      return ss;
    }
    function simple() {
      const l = ver().l;
      if (kw('pass')) { tomar(); return { t: 'pass', l }; }
      if (kw('break') || kw('continue')) return { t: tomar().v, l };
      if (kw('return')) { tomar(); return { t: 'return', e: es('NEWLINE') || op(';') ? null : exprLista(), l }; }
      if (kw('raise')) { tomar(); const e = es('NEWLINE') ? null : expr(); if (kw('from')) { tomar(); expr(); } return { t: 'raise', e, l }; }
      if (kw('assert')) { tomar(); const e = expr(); let msj = null; if (op(',')) { tomar(); msj = expr(); } return { t: 'assert', e, msj, l }; }
      if (kw('global') || kw('nonlocal')) { tomar(); do { pedir('NAME'); } while (op(',') && tomar()); return { t: 'pass', l }; }
      if (kw('del')) { tomar(); exprLista(); return { t: 'pass', l }; }
      if (kw('import')) { tomar(); const mods = []; do { let n = pedir('NAME').v; while (op('.')) { tomar(); n += '.' + pedir('NAME').v; } let como = null; if (kw('as')) { tomar(); como = pedir('NAME').v; } mods.push({ n, como }); } while (op(',') && tomar()); return { t: 'import', mods, l }; }
      if (kw('from')) {
        tomar(); let mod = ''; while (op('.') || op('...')) mod += tomar().v; if (es('NAME')) { mod += tomar().v; while (op('.')) { tomar(); mod += '.' + pedir('NAME').v; } }
        pedir('KW', 'import'); const nombres = []; const par = op('(') && tomar();
        do { if (par && op(')')) break; if (op('*')) { tomar(); nombres.push({ n: '*' }); continue; } const n = pedir('NAME').v; let como = null; if (kw('as')) { tomar(); como = pedir('NAME').v; } nombres.push({ n, como }); } while (op(',') && tomar());
        if (par) pedir('OP', ')');
        return { t: 'from', mod, nombres, l };
      }
      const e = exprLista();
      if (op('=')) { const destinos = [e]; let v; for (;;) { tomar(); v = exprLista(); if (op('=')) { destinos.push(v); continue; } break; } return { t: 'asig', destinos, e: v, l }; }
      const aug = ['+=', '-=', '*=', '/=', '//=', '%=', '**='].find(o => op(o));
      if (aug) { tomar(); return { t: 'aug', destino: e, op: aug.slice(0, -1), e: exprLista(), l }; }
      if (op(':')) { tomar(); expr(); let v = null; if (op('=')) { tomar(); v = exprLista(); } return v ? { t: 'asig', destinos: [e], e: v, l } : { t: 'pass', l }; }   // anotación
      return { t: 'expr', e, l };
    }
    function parametros(cierre) {
      const ps = [], lambda = cierre === ':';
      while (!op(cierre)) {
        if (op('/')) { tomar(); } else if (op('*') || op('**')) { const k = tomar().v; const n = es('NAME') ? tomar().v : null; if (n) ps.push({ n, estrella: k }); if (!lambda && op(':')) { tomar(); expr(); } }
        else { const n = pedir('NAME').v; if (!lambda && op(':')) { tomar(); expr(); } let def = null; if (op('=')) { tomar(); def = expr(); } ps.push({ n, def }); }
        if (op(',')) tomar(); else break;
      }
      return ps;
    }
    function argumentos(cierre) {
      const pos = [], kws = [];
      while (!op(cierre)) {
        if (op('*') || op('**')) { tomar(); pos.push({ t: 'estrella', e: expr() }); }
        else if (es('NAME') && tk[p + 1].tipo === 'OP' && tk[p + 1].v === '=') { const n = tomar().v; tomar(); kws.push({ n, e: expr() }); }
        else { let e = expr(); if (kw('for')) e = comprension('gen', e); pos.push(e); }
        if (op(',')) tomar(); else break;
      }
      return { pos, kws };
    }
    const destinoSimple = () => postfijo();
    function listaDestinos() { const ds = [postfijoSinComparar()]; while (op(',')) { tomar(); if (kw('in')) break; ds.push(postfijoSinComparar()); } return ds.length === 1 ? ds[0] : { t: 'tupla', items: ds }; }
    const postfijoSinComparar = () => { if (op('(')) { tomar(); const d = listaDestinos(); pedir('OP', ')'); return d; } return postfijo(); };
    function exprLista() {
      const l = ver().l, e = expr();
      if (!op(',')) return e;
      const items = [e];
      while (op(',')) { tomar(); if (es('NEWLINE') || op('=') || op(')') || op(':')) break; items.push(expr()); }
      return { t: 'tupla', items, l };
    }
    function expr() {
      const l = ver().l;
      if (kw('lambda')) { tomar(); const params = parametros(':'); pedir('OP', ':'); return { t: 'lambda', params, cuerpo: expr(), l }; }
      const a = o();
      if (kw('if')) { tomar(); const c = o(); pedir('KW', 'else'); return { t: 'ifexp', c, si: a, no: expr(), l }; }
      return a;
    }
    function o() { let a = y(); while (kw('or')) { tomar(); a = { t: 'bool', op: 'or', a, b: y(), l: a.l }; } return a; }
    function y() { let a = no(); while (kw('and')) { tomar(); a = { t: 'bool', op: 'and', a, b: no(), l: a.l }; } return a; }
    function no() { if (kw('not')) { const l = tomar().l; return { t: 'not', e: no(), l }; } return comparar(); }
    function comparar() {
      const a = bits(), ops = [], cs = [];
      for (;;) {
        let o_ = null;
        if (['==', '!=', '<', '>', '<=', '>='].some(x => op(x))) o_ = tomar().v;
        else if (kw('in')) { tomar(); o_ = 'in'; }
        else if (kw('not') && tk[p + 1].v === 'in') { tomar(); tomar(); o_ = 'not in'; }
        else if (kw('is')) { tomar(); o_ = 'is'; if (kw('not')) { tomar(); o_ = 'is not'; } }
        if (!o_) break;
        ops.push(o_); cs.push(bits());
      }
      return ops.length ? { t: 'cmp', a, ops, cs, l: a.l } : a;
    }
    function bits() { let a = suma(); while (op('|') || op('&') || op('^') || op('<<') || op('>>')) { const o_ = tomar().v; a = { t: 'bin', op: o_, a, b: suma(), l: a.l }; } return a; }
    function suma() { let a = prod(); while (op('+') || op('-')) { const o_ = tomar().v; a = { t: 'bin', op: o_, a, b: prod(), l: a.l }; } return a; }
    function prod() { let a = unario(); while (op('*') || op('/') || op('//') || op('%') || op('@')) { const o_ = tomar().v; a = { t: 'bin', op: o_, a, b: unario(), l: a.l }; } return a; }
    function unario() { if (op('-') || op('+') || op('~')) { const t0 = tomar(); return { t: 'un', op: t0.v, e: unario(), l: t0.l }; } return potencia(); }
    function potencia() { const a = postfijo(); if (op('**')) { tomar(); return { t: 'bin', op: '**', a, b: unario(), l: a.l }; } return a; }
    function postfijo() {
      if (kw('await')) tomar();
      let a = atomo();
      for (;;) {
        if (op('.')) { tomar(); a = { t: 'attr', e: a, n: pedir('NAME').v, l: a.l }; }
        else if (op('(')) { tomar(); const args = argumentos(')'); pedir('OP', ')'); a = { t: 'call', f: a, args: args.pos, kws: args.kws, l: a.l }; }
        else if (op('[')) { tomar(); const i = subindice(); pedir('OP', ']'); a = { t: 'sub', e: a, i, l: a.l }; }
        else break;
      }
      return a;
    }
    function subindice() {
      const parte = () => (op(':') || op(']') || op(',')) ? null : expr();
      const a = parte();
      if (op(':')) { tomar(); const b = parte(); let c = null; if (op(':')) { tomar(); c = parte(); } return { t: 'slice', a, b, c }; }
      if (op(',')) { const items = [a]; while (op(',')) { tomar(); if (op(']')) break; items.push(expr()); } return { t: 'tupla', items }; }
      return a;
    }
    function comprension(tipo, e, valor) {
      const gens = [];
      while (kw('for')) { tomar(); const destino = listaDestinos(); pedir('KW', 'in'); const it = o(); const conds = []; while (kw('if')) { tomar(); conds.push(o()); } gens.push({ destino, it, conds }); }
      return { t: 'comp', tipo, e, valor, gens, l: e.l };
    }
    function atomo() {
      const k = ver(), l = k.l;
      if (k.tipo === 'NUM') { tomar(); return { t: 'num', v: k.v.v, real: k.v.real, l }; }
      if (k.tipo === 'STR' || k.tipo === 'FSTR') {
        const partes = [];
        while (es('STR') || es('FSTR')) { const s = tomar(); partes.push(s.tipo === 'FSTR' ? { f: fstring(s.v, s.l) } : { s: s.v }); }
        if (partes.every(x => 's' in x)) return { t: 'str', v: partes.map(x => x.s).join(''), l };
        return { t: 'fstr', partes: partes.flatMap(x => 's' in x ? [{ s: x.s }] : x.f), l };
      }
      if (k.tipo === 'NAME') { tomar(); return { t: 'name', n: k.v, l }; }
      if (k.tipo === 'KW') {
        if (k.v === 'True' || k.v === 'False') { tomar(); return { t: 'bool_', v: k.v === 'True', l }; }
        if (k.v === 'None') { tomar(); return { t: 'none', l }; }
      }
      if (op('...')) { tomar(); return { t: 'none', l }; }
      if (op('(')) {
        tomar(); if (op(')')) { tomar(); return { t: 'tupla', items: [], l }; }
        const e = expr();
        if (kw('for')) { const c = comprension('gen', e); pedir('OP', ')'); return c; }
        if (op(',')) { const items = [e]; while (op(',')) { tomar(); if (op(')')) break; items.push(expr()); } pedir('OP', ')'); return { t: 'tupla', items, l }; }
        pedir('OP', ')'); return e;
      }
      if (op('[')) {
        tomar(); if (op(']')) { tomar(); return { t: 'lista', items: [], l }; }
        const e = op('*') ? (tomar(), { t: 'estrella', e: expr() }) : expr();
        if (kw('for')) { const c = comprension('lista', e); pedir('OP', ']'); return c; }
        const items = [e]; while (op(',')) { tomar(); if (op(']')) break; items.push(op('*') ? (tomar(), { t: 'estrella', e: expr() }) : expr()); }
        pedir('OP', ']'); return { t: 'lista', items, l };
      }
      if (op('{')) {
        tomar(); if (op('}')) { tomar(); return { t: 'dict', pares: [], l }; }
        if (op('**')) { tomar(); const e = expr(); const pares = [{ estrella: e }]; while (op(',')) { tomar(); if (op('}')) break; if (op('**')) { tomar(); pares.push({ estrella: expr() }); } else { const kk = expr(); pedir('OP', ':'); pares.push({ k: kk, v: expr() }); } } pedir('OP', '}'); return { t: 'dict', pares, l }; }
        const a = expr();
        if (op(':')) {
          tomar(); const v = expr();
          if (kw('for')) { const c = comprension('dict', a, v); pedir('OP', '}'); return c; }
          const pares = [{ k: a, v }]; while (op(',')) { tomar(); if (op('}')) break; if (op('**')) { tomar(); pares.push({ estrella: expr() }); continue; } const kk = expr(); pedir('OP', ':'); pares.push({ k: kk, v: expr() }); }
          pedir('OP', '}'); return { t: 'dict', pares, l };
        }
        if (kw('for')) { const c = comprension('set', a); pedir('OP', '}'); return c; }
        const items = [a]; while (op(',')) { tomar(); if (op('}')) break; items.push(expr()); }
        pedir('OP', '}'); return { t: 'set', items, l };
      }
      throw new Error(`Línea ${l}: no entiendo «${typeof k.v === 'object' ? '' : k.v || k.tipo}»`);
    }
    // f"…{expr:formato}…": las partes de texto y las expresiones con su formato
    function fstring(s, l) {
      const partes = [];
      let i = 0, txt = '';
      while (i < s.length) {
        if (s[i] === '{' && s[i + 1] === '{') { txt += '{'; i += 2; continue; }
        if (s[i] === '}' && s[i + 1] === '}') { txt += '}'; i += 2; continue; }
        if (s[i] === '{') {
          if (txt) { partes.push({ s: txt }); txt = ''; }
          let j = i + 1, d = 0, q = null;
          for (; j < s.length; j++) { const ch = s[j]; if (q) { if (ch === q) q = null; continue; } if (ch === '"' || ch === "'") q = ch; else if ('([{'.includes(ch)) d++; else if (')]}'.includes(ch)) { if (d === 0) break; d--; } else if (ch === ':' && d === 0) break; else if (ch === '!' && d === 0 && s[j + 1] !== '=') break; }
          const codigo = s.slice(i + 1, j);
          let conv = null, fmt = '';
          if (s[j] === '!') { conv = s[j + 1]; j += 2; }
          if (s[j] === ':') { let k = j + 1, dd = 0; for (; k < s.length; k++) { if (s[k] === '{') dd++; else if (s[k] === '}') { if (dd === 0) break; dd--; } } fmt = s.slice(j + 1, k); j = k; }
          const igual = /=\s*$/.test(codigo) && !/[=!<>]=\s*$/.test(codigo);
          partes.push({ e: leerExpr(igual ? codigo.replace(/=\s*$/, '') : codigo, l), conv, fmt, igual: igual ? codigo : null });
          i = j + 1; continue;
        }
        txt += s[i]; i++;
      }
      if (txt) partes.push({ s: txt });
      return partes;
    }
    saltarNL();
    const ss = [];
    while (!es('EOF')) { if (es('DEDENT') || es('INDENT')) { tomar(); continue; } ss.push(...sentencia()); saltarNL(); }
    return ss;
  }
  function leerExpr(codigo, l) { const ss = leer(codigo); if (!ss.length || ss[0].t !== 'expr') throw new Error(`Línea ${l}: no entiendo «${codigo}»`); return ss[0].e; }

  return { leer, tokens, leerExpr };
});
