/* Lo que pide un archivo de tests de pytest, sin ejecutar Python: recorre los tests «en seco» (con los fixtures, los
   helpers, el parametrize y pytest.raises) y anota qué clases importa y de qué módulo, con qué argumentos las construye,
   qué métodos y atributos usa, qué se agrega a qué colección y qué resultado espera en cada assert.
   Uso: TestLee.analizar({ 'test_x.py': texto }) → { imports, clases, objetos, asserts, raises, mainUsa } */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica(require('./python-lee.js'));
  else raiz.TestLee = fabrica(raiz.PyLee);
})(typeof self !== 'undefined' ? self : this, function (PyLee) {
  'use strict';
  const NUM = (v, real) => ({ k: 'num', v, real: !!real });
  const STR = v => ({ k: 'str', v }), BOOL = v => ({ k: 'bool', v }), NONE = { k: 'none' };
  const sym = (op, x) => ({ k: 'sym', op, ...x });

  function analizar(textos) {
    const R = { imports: {}, modulos: new Set(), clases: {}, objetos: [], asserts: [], raises: [], mainUsa: {}, constantes: {}, errores: [] };
    const clase = n => R.clases[n] || (R.clases[n] = { n, ctores: [], metodos: {}, attrsLeidos: new Set(), attrsEscritos: new Set(), bases: new Set(), strs: [] });
    let idObj = 0;

    for (const [nombre, texto] of Object.entries(textos)) {
      let arbol;
      try { arbol = PyLee.leer(texto); } catch (e) { R.errores.push(`${nombre}: ${e.message}`); continue; }
      const glob = new Map();
      glob.set('pytest', { k: 'pytest' });
      const defs = {};
      // imports y definiciones de arriba
      const recorrerArriba = ss => {
        for (const s of ss) {
          if (s.t === 'from') {
            if (/^(pytest|typing|pathlib|sys|os|math|abc|unittest|io|csv|json|re|datetime|functools|itertools|collections|dataclasses|decimal|__future__)$/.test(s.mod)) continue;
            R.modulos.add(s.mod);
            for (const x of s.nombres) {
              if (x.n === '*') continue;
              const local = x.como || x.n;
              R.imports[x.n] = s.mod;
              if (/^[A-Z]/.test(x.n)) { glob.set(local, { k: 'clase', n: x.n, mod: s.mod }); clase(x.n).mod = s.mod; }
              else glob.set(local, { k: 'func', ext: x.n, mod: s.mod });
            }
          } else if (s.t === 'import') {
            for (const m of s.mods) if (!/^(pytest|sys|os|math|pathlib|typing|unittest|io|csv|json|re|datetime)$/.test(m.n)) { glob.set(m.como || m.n, { k: 'mod', n: m.n }); R.modulos.add(m.n); }
          } else if (s.t === 'def') defs[s.nombre] = s;
          else if (s.t === 'class') { for (const c of s.cuerpo) if (c.t === 'def') defs[s.nombre + '.' + c.nombre] = Object.assign(c, { claseTest: s.nombre }); }
          else if (s.t === 'asig' && s.destinos.every(d => d.t === 'name' || d.t === 'tupla')) {
            try { asignar(s.destinos[0], evaluar(s.e, glob), glob); for (const d of s.destinos) if (d.t === 'name') R.constantes[d.n] = glob.get(d.n); } catch (e) { /* constantes raras */ }
          } else if (s.t === 'if' || s.t === 'try') { /* «if __name__ == '__main__'», bootstrap de sys.path: se ignoran */ }
        }
      };

      // ── evaluación en seco
      function asignar(d, v, env) {
        if (d.t === 'name') env.set(d.n, v);
        else if (d.t === 'tupla' || d.t === 'lista') { const items = v && (v.k === 'tuple' || v.k === 'list') ? v.items : d.items.map(() => sym('desconocido', {})); d.items.forEach((x, i) => asignar(x, items[i], env)); }
        else if (d.t === 'attr') { const o = evaluar(d.e, env); if (o && o.k === 'obj') { o.attrs[d.n] = v; clase(o.clase).attrsEscritos.add(d.n); } }
      }
      const buscar = (n, env) => env.has(n) ? env.get(n) : glob.has(n) ? glob.get(n) : (defs[n] ? { k: 'def', d: defs[n] } : undefined);
      function evaluar(e, env) {
        switch (e.t) {
          case 'num': return NUM(e.v, e.real);
          case 'str': return STR(e.v);
          case 'fstr': return { k: 'fstr', partes: e.partes.map(p => p.s != null ? { s: p.s } : { v: evaluar(p.e, env), fmt: p.fmt }) };
          case 'bool_': return BOOL(e.v);
          case 'none': return NONE;
          case 'name': { const v = buscar(e.n, env); return v === undefined ? sym('nombre', { n: e.n }) : v; }
          case 'lista': return { k: 'list', items: e.items.map(x => evaluar(x, env)) };
          case 'tupla': return { k: 'tuple', items: e.items.map(x => evaluar(x, env)) };
          case 'set': return { k: 'set', items: e.items.map(x => evaluar(x, env)) };
          case 'dict': return { k: 'dict', pares: e.pares.filter(p => p.k).map(p => [evaluar(p.k, env), evaluar(p.v, env)]) };
          case 'un': { const v = evaluar(e.e, env); if (v.k === 'num' && e.op === '-') return NUM(-v.v, v.real); if (v.k === 'num') return v; return sym('un', { op: e.op, a: v }); }
          case 'bin': { const a = evaluar(e.a, env), b = evaluar(e.b, env); if (a.k === 'num' && b.k === 'num') return aritmetica(e.op, a, b); if (a.k === 'str' && b.k === 'str' && e.op === '+') return STR(a.v + b.v); return sym('bin', { op: e.op, a, b }); }
          case 'not': return sym('not', { a: evaluar(e.e, env) });
          case 'bool': return sym('bool', { op: e.op, a: evaluar(e.a, env), b: evaluar(e.b, env), ea: e.a, eb: e.b });
          case 'ifexp': return sym('ifexp', {});
          case 'lambda': return { k: 'lambda', e, env };
          case 'attr': {
            const o = evaluar(e.e, env);
            if (o.k === 'pytest') return { k: 'pytest', n: e.n };
            if (o.k === 'mod') return { k: 'func', ext: e.n, mod: o.n };
            if (o.k === 'obj') { if (e.n in o.attrs) return o.attrs[e.n]; clase(o.clase).attrsLeidos.add(e.n); return sym('attr', { obj: o, n: e.n }); }
            if (o.k === 'clase') return sym('attrClase', { clase: o.n, n: e.n });
            return sym('attr', { obj: o, n: e.n });
          }
          case 'sub': { const o = evaluar(e.e, env), i = evaluar(e.i, env); if ((o.k === 'list' || o.k === 'tuple') && i.k === 'num') return o.items[i.v < 0 ? o.items.length + i.v : i.v] || sym('sub', { a: o, i }); return sym('sub', { a: o, i }); }
          case 'cmp': return sym('cmp', { e, a: evaluar(e.a, env), cs: e.cs.map(c => evaluar(c, env)), ops: e.ops });
          case 'comp': return sym('comp', { e });
          case 'call': return llamar(e, env);
          default: return sym('desconocido', { t: e.t });
        }
      }
      function aritmetica(op, a, b) {
        const real = a.real || b.real || op === '/';
        const v = op === '+' ? a.v + b.v : op === '-' ? a.v - b.v : op === '*' ? a.v * b.v : op === '/' ? a.v / b.v : op === '//' ? Math.floor(a.v / b.v) : op === '%' ? a.v % b.v : op === '**' ? a.v ** b.v : NaN;
        return NUM(v, real);
      }
      function llamar(e, env) {
        const f = e.f.t === 'attr' ? (() => { const o = evaluar(e.f.e, env); return o.k === 'pytest' ? { k: 'pytest', n: e.f.n } : o.k === 'mod' ? { k: 'func', ext: e.f.n, mod: o.n } : { k: 'metodo' }; })() : evaluar(e.f, env);
        const args = e.args.map(a => evaluar(a, env)), kws = Object.fromEntries(e.kws.map(k => [k.n, evaluar(k.e, env)]));
        if (f.k === 'clase') {
          const o = { k: 'obj', id: ++idObj, clase: f.n, args, kws, attrs: {}, agregados: [] };
          clase(f.n).ctores.push({ args, kws, obj: o, l: e.l });
          R.objetos.push(o);
          return o;
        }
        if (f.k === 'pytest' && f.n === 'approx') return { k: 'approx', v: args[0], rel: kws.rel, abs: kws.abs };
        if (f.k === 'pytest' && f.n === 'raises') return { k: 'raises', exc: e.args[0] && (e.args[0].n || (e.args[0].t === 'attr' ? e.args[0].n : null)) };
        if (f.k === 'def') return correrDef(f.d, args, kws);
        if (f.k === 'lambda') return sym('lambda', {});
        if (f.k === 'func') { const s = sym('modcall', { mod: f.mod, n: f.ext, args }); (R.mainUsa[f.ext] || (R.mainUsa[f.ext] = [])).push({ args, s }); return s; }
        if (e.f.t === 'name') {
          const n = e.f.n;
          if (n === 'isinstance') { const c = args[1]; if (args[0].k === 'obj' && c && c.k === 'clase') clase(args[0].clase).bases.add(c.n); return sym('isinstance', { a: args[0], c: c && c.n }); }
          if (n === 'len') return sym('len', { a: args[0] });
          if (n === 'str' || n === 'repr') { const s = sym('str', { a: args[0], f: n }); return s; }
          if (['int', 'float', 'round', 'abs', 'sum', 'sorted', 'list', 'set', 'dict', 'tuple', 'max', 'min', 'any', 'all', 'type', 'bool', 'print', 'hasattr', 'getattr', 'issubclass'].includes(n)) {
            if (n === 'issubclass' && args[0] && args[0].k === 'clase' && args[1] && args[1].k === 'clase') clase(args[0].n).bases.add(args[1].n);
            return sym('builtin', { n, args });
          }
        }
        if (e.f.t === 'attr') {
          const o = evaluar(e.f.e, env), m = e.f.n;
          if (o.k === 'obj') {
            const c = clase(o.clase);
            (c.metodos[m] || (c.metodos[m] = { llamadas: [] })).llamadas.push({ obj: o, args, kws, l: e.l });
            if (/^(agregar|add|anadir|añadir|cargar|registrar|sumar|insertar|incorporar|alta)/i.test(m) && args[0] && args[0].k === 'obj') o.agregados.push(args[0]);
            return sym('call', { obj: o, n: m, args, kws });
          }
          if (o.k === 'clase') return sym('callClase', { clase: o.n, n: m, args });
          if (o.k === 'sym') (R.metodosSueltos || (R.metodosSueltos = new Set())).add(m);
          return sym('call', { obj: o, n: m, args, kws });
        }
        return sym('llamada', { args });
      }
      // un def (helper o fixture): se corre su cuerpo y se devuelve lo que retorna
      function correrDef(d, args, kws, envBase) {
        const env = new Map(envBase || []);
        const ps = d.params.filter(p => p.n !== 'self');
        ps.forEach((p, i) => env.set(p.n, i < args.length ? args[i] : p.n in kws ? kws[p.n] : p.def ? evaluar(p.def, env) : resolverFixture(p.n, env)));
        try { return ejecutar(d.cuerpo, env); } catch (x) { if (x && x.retorno) return x.v; throw x; }
      }
      const fixtureCache = new Map();
      function resolverFixture(n, env) {
        if (fixtureCache.has(n)) return fixtureCache.get(n);
        const d = Object.values(defs).find(x => x.nombre === n && (x.decoradores || []).some(dec => /fixture/.test(JSON.stringify(dec))));
        if (!d) return sym('fixture', { n });
        const v = correrDef(d, [], {}, env);
        fixtureCache.set(n, v);
        return v;
      }
      function ejecutar(ss, env, enRaises) {
        let ult = NONE;
        for (const s of ss) {
          if (s.t === 'asig') { const v = evaluar(s.e, env); for (const d of s.destinos) asignar(d, v, env); }
          else if (s.t === 'aug') { const a = evaluar(s.destino, env), b = evaluar(s.e, env); asignar(s.destino, a.k === 'num' && b.k === 'num' ? aritmetica(s.op, a, b) : sym('bin', { op: s.op, a, b }), env); }
          else if (s.t === 'expr') { const v = evaluar(s.e, env); if (enRaises) R.raises.push({ exc: enRaises, v, l: s.l }); ult = v; }
          else if (s.t === 'assert') registrarAssert(s.e, env, s.l);
          else if (s.t === 'return') throw { retorno: true, v: s.e ? evaluar(s.e, env) : NONE };
          else if (s.t === 'with') {
            const it = s.items[0], v = evaluar(it.e, env);
            if (v.k === 'raises') { const env2 = env; for (const x of s.cuerpo) { if (x.t === 'expr' || x.t === 'asig') { const val = evaluar(x.t === 'expr' ? x.e : x.e, env2); R.raises.push({ exc: v.exc, v: val, l: x.l }); if (x.t === 'asig') for (const d of x.destinos) asignar(d, val, env2); } else ejecutar([x], env2, v.exc); } }
            else ejecutar(s.cuerpo, env);
          }
          else if (s.t === 'for') {
            const it = evaluar(s.it, env);
            if (it.k === 'list' || it.k === 'tuple') for (const x of it.items) { asignar(s.destino, x, env); ejecutar(s.cuerpo, env); }
          }
          else if (s.t === 'if') { /* condiciones en un test: se recorren todas las ramas como si fueran ciertas */ for (const [, b] of s.ramas) ejecutar(b, env); }
          else if (s.t === 'def') env.set(s.nombre, { k: 'def', d: s });
        }
        return ult;
      }
      // un assert: «a == b», «a is None», «a», «not a», «x in y», «a and b»
      function registrarAssert(e, env, l) {
        if (e.t === 'bool' && e.op === 'and') { registrarAssert(e.a, env, l); registrarAssert(e.b, env, l); return; }
        if (e.t === 'cmp' && e.ops.length === 1) { R.asserts.push({ a: evaluar(e.a, env), op: e.ops[0], b: evaluar(e.cs[0], env), l, e }); return; }
        if (e.t === 'not') { R.asserts.push({ a: evaluar(e.e, env), op: 'falsy', l, e }); return; }
        R.asserts.push({ a: evaluar(e, env), op: 'truthy', l, e });
      }

      recorrerArriba(arbol);
      // cada test: con sus fixtures nuevos (y una vez por cada caso del parametrize)
      for (const [clave, d] of Object.entries(defs)) {
        if (!/^test/.test(d.nombre)) continue;
        const casos = parametrize(d, glob);
        for (const caso of casos) {
          fixtureCache.clear();
          const env = new Map();
          for (const [n, v] of Object.entries(caso)) env.set(n, v);
          for (const p of d.params) if (p.n !== 'self' && !env.has(p.n)) env.set(p.n, resolverFixture(p.n, env));
          try { ejecutar(d.cuerpo, env); } catch (x) { if (!(x && x.retorno)) R.errores.push(`${clave}: ${x.message || x}`); }
        }
      }
      function parametrize(d, env) {
        let casos = [{}];
        for (const dec of d.decoradores || []) {
          if (dec.t !== 'call' || !/parametrize/.test(JSON.stringify(dec.f))) continue;
          const nombres = evaluar(dec.args[0], env), valores = evaluar(dec.args[1], env);
          const ns = nombres.k === 'str' ? nombres.v.split(',').map(x => x.trim()) : (nombres.items || []).map(x => x.v);
          const vs = valores.k === 'list' || valores.k === 'tuple' ? valores.items : [];
          const nuevos = [];
          for (const c of casos) for (const v of vs) { const o = { ...c }; if (ns.length === 1) o[ns[0]] = v; else ns.forEach((n, i) => { o[n] = v.items ? v.items[i] : v; }); nuevos.push(o); }
          if (nuevos.length) casos = nuevos;
        }
        return casos;
      }
    }
    return R;
  }

  // Para mostrar un valor del test como Python
  function texto(v) {
    if (!v) return '?';
    switch (v.k) {
      case 'num': return v.real && Number.isInteger(v.v) ? v.v.toFixed(1) : String(v.v);
      case 'str': return JSON.stringify(v.v);
      case 'bool': return v.v ? 'True' : 'False';
      case 'none': return 'None';
      case 'list': return '[' + v.items.map(texto).join(', ') + ']';
      case 'tuple': return '(' + v.items.map(texto).join(', ') + ')';
      case 'obj': return `${v.clase}(${v.args.map(texto).join(', ')})`;
      case 'approx': return `approx(${texto(v.v)})`;
      case 'sym': return v.op === 'call' ? `${texto(v.obj)}.${v.n}(${(v.args || []).map(texto).join(', ')})` : v.op === 'attr' ? `${texto(v.obj)}.${v.n}` : v.op === 'len' ? `len(${texto(v.a)})` : v.op === 'str' ? `str(${texto(v.a)})` : v.op === 'isinstance' ? `isinstance(${texto(v.a)}, ${v.c})` : v.op === 'modcall' ? `${v.mod}.${v.n}(…)` : '…';
      default: return v.k;
    }
  }
  return { analizar, texto };
});
