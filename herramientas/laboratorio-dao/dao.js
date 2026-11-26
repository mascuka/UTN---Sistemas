/* El parcial de DAO resuelto desde cero: con el enunciado, el CSV y el archivo de tests arma todo el programa en Python
   (la clase base, las subclases con su cálculo, la clase que guarda la colección con sus métodos y el main que lee el
   CSV). Los nombres (módulos, clases, constructores, métodos y atributos) los fija el test; las reglas salen del
   enunciado y los tipos de cada dato, del CSV. Antes de entregar, prueba el modelo contra cada assert del test (sin
   Python) y, si una regla admite más de una lectura, se queda con la que cumple.
   Uso: Dao.resolver({ enunciado, csvs: { 'x.csv': texto }, tests: { 'test_x.py': texto } })
        → { archivos: { 'ruta.py': código }, avisos: [], comprobacion: { ok, total, fallan: [] }, modelo } */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica(require('./test-lee.js'));
  else raiz.Dao = fabrica(raiz.TestLee);
})(typeof self !== 'undefined' ? self : this, function (TestLee) {
  'use strict';
  const sinTildes = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '');
  const bajo = s => sinTildes(s).toLowerCase();
  const capital = s => s ? s[0].toUpperCase() + s.slice(1) : s;
  const palabrasDe = n => String(n).replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/_/g, ' ').toLowerCase().split(/\s+/).filter(Boolean).map(bajo);
  const snake = s => bajo(s).replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
  const singular = w => w.replace(/(?<=[^aeiou])es$/, '').replace(/(?<=[aeiou])s$/, '');
  const plural = w => /[aeiou]$/.test(w) ? w + 's' : w + 'es';
  const num = s => Number(String(s).replace(/\$/g, '').replace(/[._](?=\d{3}\b)/g, '').replace(',', '.'));
  const NUMRE = '\\$?\\s*(\\d+(?:[.,_]\\d{3})*(?:[.,]\\d+)?)';
  const ORDINALES = { primer: 1, primero: 1, segundo: 2, tercer: 3, tercero: 3, cuarto: 4, quinto: 5, sexto: 6, septimo: 7, octavo: 8, noveno: 9, decimo: 10 };
  const VACIAS = new Set('de del la el los las un una que en con por para a al se le les su sus y o es son lo cuyo cuya cual'.split(' '));
  // palabras del enunciado que nombran a un dato con otro nombre
  const SINONIMOS = { duracion: ['horas', 'parada', 'duracion', 'tiempo'], ganancia: ['resultado', 'ganancia'], rentable: ['indice', 'rentabilidad', 'rentable'], rentabilidad: ['indice', 'rentabilidad'],
    recaudacion: ['importe', 'recaudado', 'recaudacion'], recaudado: ['importe', 'recaudado'], gastos: ['gasto'], gasto: ['gasto'], caro: ['gasto', 'importe', 'costo', 'total'], caros: ['gasto', 'importe', 'costo', 'total'],
    alquileres: ['alquiler'], dormitorio: ['dormitorios', 'habitaciones'], dormitorios: ['dormitorios', 'habitaciones'], habitaciones: ['habitaciones', 'dormitorios'], nombre: ['nombre', 'propietario', 'operario', 'conductor', 'cliente'],
    importe: ['importe', 'alquiler', 'monto', 'precio', 'costo'], tecnico: ['tecnico'], pileta: ['pileta'], cantidad: ['cantidad'] };

  // ───────── El texto del enunciado
  function limpiar(t) {
    return String(t || '').replace(/\r/g, '').replace(/```[a-z]*\n?/g, '\n').replace(/\*\*([^*\n]+)\*\*/g, '$1').replace(/(^|[^\w*])\*([^*\n]+)\*(?![\w*])/g, '$1$2')
      .replace(/`([^`\n]+)`/g, '$1').replace(/^#+\s*/gm, '').replace(/[ \t]+([.,;:)])/g, '$1').replace(/ /g, ' ').replace(/×/g, ' × ');
  }
  // los ítems numerados del texto («1. Algo: …», «2. Otro»), también los que vienen en la misma línea
  function items(t) {
    const out = [];
    const ls = t.split('\n');
    for (let i = 0; i < ls.length; i++) {
      const l = ls[i].trim();
      if (/^(\d+)[.)-]\s+\S/.test(l)) {
        const partes = l.split(/\s+(?=\d+[.)]\s+[A-ZÁÉÍÓÚ¿])/);
        for (const p of partes) { const m = p.match(/^(\d+)[.)-]\s+(.*)$/); if (m) out.push({ n: Number(m[1]), texto: m[2].trim(), linea: i }); }
        // la continuación en la línea siguiente (si no es otro ítem ni una línea en blanco)
        while (ls[i + 1] && ls[i + 1].trim() && !/^(\d+)[.)-]\s/.test(ls[i + 1].trim()) && !/^[-*•]\s/.test(ls[i + 1].trim()) && /^\s{2,}|^[a-záéíóú(]/.test(ls[i + 1])) { out[out.length - 1].texto += ' ' + ls[i + 1].trim(); i++; }
      }
    }
    return out;
  }
  // grupos de ítems seguidos (1, 2, 3…): la estructura del CSV y los métodos pedidos son listas distintas
  function listas(its) {
    const gs = [];
    for (const it of its) { const g = gs[gs.length - 1]; if (g && it.n === g[g.length - 1].n + 1 && it.linea - g[g.length - 1].linea <= 3) g.push(it); else gs.push([it]); }
    return gs;
  }
  const oraciones = t => t.replace(/\n(?!\s*\n)/g, ' ').split(/(?<=[.;!?])\s+|\n\s*\n/).map(s => s.trim()).filter(Boolean);

  // ───────── Resolver
  function resolver({ enunciado, csvs, tests }) {
    const avisos = [];
    const T = TestLee.analizar(tests || {});
    for (const e of T.errores) avisos.push('Del test: ' + e);
    const texto = limpiar(enunciado);
    const tb = bajo(texto);
    const its = items(texto), grupos = listas(its);
    const ors = oraciones(texto);

    // ── las clases que usa el test
    const nombres = Object.keys(T.clases);
    const esColector = n => { const c = T.clases[n]; return T.objetos.some(o => o.clase === n && o.agregados.length) || Object.keys(c.metodos).some(m => /^(agregar|add|cargar|registrar)/i.test(m)); };
    const colectorN = nombres.find(esColector) || null;
    const entidades = nombres.filter(n => n !== colectorN);
    // la base: la del isinstance, la que se importa y no se construye, o la del «Tipo de X»
    let baseN = [...new Set(entidades.flatMap(n => [...T.clases[n].bases]))].find(b => b !== colectorN) || entidades.find(n => !T.clases[n].ctores.length) || null;
    const tipoDe = (texto.match(/^\s*\d+[.)]\s*tipo\s+de\s+([a-záéíóúñ]+)/im) || texto.match(/\btipo\s+de\s+(?!la\b|el\b|los\b|las\b|un\b|una\b|cobro\b)([a-záéíóúñ]+)/i) || [])[1];
    if (!baseN) { const m = texto.match(/\b([A-Z][A-Za-z0-9_]*)\([^)]*\)\s*[—–-]\s*clase\s+base/); if (m && !nombres.includes(m[1])) baseN = m[1]; }
    if (!baseN) {
      const pref = entidades.length > 1 ? palabrasDe(entidades[0]).filter((w, i) => entidades.every(n => palabrasDe(n)[i] === w)) : [];
      baseN = pref.length ? pref.map(capital).join('') : tipoDe ? capital(singular(bajo(tipoDe))) : 'Entidad';
    }
    const subsN = entidades.filter(n => n !== baseN && T.clases[n].ctores.length);
    if (!subsN.length) avisos.push('El test no construye ninguna clase: no sé qué clases armar.');
    const modDe = n => (T.clases[n] && T.clases[n].mod) || null;
    const unArchivo = (() => { const ms = [...new Set(Object.values(T.imports))]; return ms.length === 1 && nombres.length > 1 ? ms[0] : null; })();

    // ── el contrato, si el enunciado lo trae: «Clase(a, b, c)» y lo que dice cada línea
    const contrato = {};
    for (const l of texto.split('\n')) {
      for (const m of l.matchAll(/\b([A-Z][A-Za-z0-9_]*)\(([a-z_][\w]*(?:\s*,\s*[a-z_][\w]*)*)?\)/g)) {
        if (!(m[1] in contrato) && (nombres.includes(m[1]) || m[1] === baseN)) contrato[m[1]] = { params: (m[2] || '').split(',').map(x => x.trim()).filter(Boolean), linea: l };
      }
    }

    // ── el CSV: encabezado, separador y valores de cada columna
    const csvNombres = Object.keys(csvs || {});
    const csvPrincipal = csvNombres.find(n => texto.includes(n)) || csvNombres[0] || null;
    const csvT = csvPrincipal ? csvs[csvPrincipal].replace(/^﻿/, '').replace(/\r/g, '') : '';
    const lineasCsv = csvT.split('\n').filter(l => l.trim());
    const sep = (lineasCsv[0] || '').includes(';') && !(lineasCsv[0] || '').includes(',') ? ';' : ',';
    const primera = lineasCsv.length ? lineasCsv[0].split(sep).map(x => x.trim()) : [];
    const conEncabezado = primera.length > 1 && primera.every(x => /^[A-Za-z_][\w ]*$/.test(x)) && !primera.every(x => /^(true|false|si|no)$/i.test(x));
    const filas = (conEncabezado ? lineasCsv.slice(1) : lineasCsv).map(l => l.split(sep).map(x => x.trim()));
    const nCols = Math.max(0, ...filas.map(f => f.length));
    const columna = i => filas.map(f => f[i]).filter(x => x != null && x !== '');
    const tipoCol = (vs, etiqueta) => {
      const e = bajo(etiqueta || '');
      if (/\b1\b[^.;]*\bsi\b[^.;]*\b0\b|true|false|booleano/.test(e) && !/cantidad|importe/.test(e)) return 'bool';
      if (vs.length && vs.every(v => /^(true|false)$/i.test(v))) return 'bool';
      if (/float|decimal|importe|monto|precio|facturaci/.test(e) && vs.every(v => /^-?\d+(\.\d+)?$/.test(v))) return 'float';
      if (vs.length && vs.every(v => /^-?\d+$/.test(v))) return 'int';
      if (vs.length && vs.every(v => /^-?\d+(\.\d+)?$/.test(v))) return 'float';
      return 'str';
    };

    // ── la estructura del CSV que describe el enunciado (o su encabezado)
    let estructura = null;
    const gEst = grupos.find(g => g.length >= 3 && g.some(x => /^tipo\b/i.test(x.texto)) && g.length >= nCols - 1);
    if (gEst) estructura = gEst.map(x => x.texto);
    else {
      const f = texto.match(/formato\s*:\s*([a-z_][\w]*(?:\s*,\s*[a-z_][\w]*){2,})/i);
      if (f) estructura = f[1].split(/\s*,\s*/);
      else if (conEncabezado) estructura = primera.slice();
    }
    if (!estructura) { estructura = []; avisos.push('No encontré en el enunciado cómo es cada línea del CSV.'); }
    const iTipo = Math.max(0, estructura.findIndex(x => /^tipo\b/i.test(x)));
    // «1 para casas y 2 para departamentos», «Tipo 1=urbano; 2=interurbano», «1 para hiper, 2 para super y 3 para mini»
    const etiquetasTipo = {};
    const fuenteTipo = (estructura[iTipo] || '') + ' ' + texto;
    for (const m of fuenteTipo.matchAll(/(\d+)\s*(?:=|:|para|->|→)\s*(?:los\s+|las\s+|el\s+|la\s+|un\s+|una\s+)?[“"«]?([A-Za-záéíóúñ]+)/g)) if (!(m[1] in etiquetasTipo) && !/^(el|la|cada|que|los|las|si)$/i.test(m[2])) etiquetasTipo[m[1]] = bajo(m[2]);
    // qué subclase es cada tipo
    const tipoDeSub = {};
    for (const [k, et] of Object.entries(etiquetasTipo)) {
      const cand = subsN.filter(n => palabrasDe(n).some(w => w === et || singular(et) === w || et.startsWith(w) && w.length >= 4 || w.startsWith(singular(et)) && singular(et).length >= 4));
      const exacto = cand.find(n => palabrasDe(n).includes(et) || palabrasDe(n).includes(singular(et)));
      const n = exacto || cand[0];
      if (n && !Object.values(tipoDeSub).includes(n)) tipoDeSub[k] = n;
    }
    const valorTipoDe = n => Object.keys(tipoDeSub).find(k => tipoDeSub[k] === n);
    const etiquetaDe = n => { const k = valorTipoDe(n); return k ? etiquetasTipo[k] : bajo(palabrasDe(n).slice(-1)[0]); };

    // ── los campos de cada clase: cuántos (el test), cómo se llaman (contrato, encabezado o enunciado) y de qué tipo
    const muestra = n => (T.clases[n] && T.clases[n].ctores[0]) ? T.clases[n].ctores[0].args : [];
    const aridad = n => { const cs = T.clases[n] ? T.clases[n].ctores : []; return cs.length ? Math.max(...cs.map(c => c.args.length + Object.keys(c.kws).length)) : 0; };
    // columnas del CSV para cada subclase: las comunes y las propias («Si es una casa, …; si es un departamento, …»)
    const colsDe = {};   // sub → [{ i (columna del CSV), etiqueta }]
    for (const n of subsN) colsDe[n] = [];
    estructura.forEach((e, i) => {
      if (i === iTipo) return;
      const partes = e.split(/;\s*(?=si\s)/i);
      if (/^si\s+es\b/i.test(e) || partes.length > 1) {
        for (const p of partes) {
          const m = p.match(/^si\s+es\s+(?:un|una)?\s*([a-záéíóúñ ]+?),\s*(.*)$/i);
          if (!m) continue;
          const quien = bajo(m[1]).trim();
          const n = subsN.find(x => { const et = etiquetaDe(x); return quien.includes(singular(et)) || palabrasDe(x).some(w => w.length >= 4 && quien.includes(singular(w))); });
          if (n) colsDe[n].push({ i, etiqueta: m[2] });
        }
      } else for (const n of subsN) colsDe[n].push({ i, etiqueta: e });
    });
    // un nombre de campo a partir de cómo lo describe el enunciado
    const nombreDeEtiqueta = e => {
      if (/^[a-z_][\w]*$/.test(e)) return e;
      let x = bajo(e).split(/:|\(|\bsi\b(?!\s+es\b)|,|\buna?\s+numero\b|\bnumero\s+de\s+tipo\b/)[0].trim();
      x = x.replace(/^(la|el|los|las|un|una)\s+/, '').replace(/\b(cantidad\s+de|nombre\s+del?|importe\s+(?:de\s+)?(?:los|las|el|la)?|total\s+(?:de\s+)?|numero\s+(?:de\s+)?)\s*/g, '').replace(/\b(que|cobro|cobró|abono|pagado)\b.*$/, '').trim();
      const ws = x.split(/\s+/).filter(w => w && !VACIAS.has(w));
      return snake(ws.slice(0, 2).join(' ')) || 'dato';
    };
    const campos = {};   // clase → [{ n, tipo, col }]
    for (const n of subsN) {
      const k = aridad(n), cols = colsDe[n];
      let ns = contrato[n] ? contrato[n].params.slice() : null;
      if (!ns && conEncabezado && cols.length === k) ns = cols.map(c => primera[c.i]);
      if (!ns) ns = cols.map(c => nombreDeEtiqueta(c.etiqueta));
      if (ns.length !== k) { if (ns.length > k) ns = ns.slice(0, k); else while (ns.length < k) ns.push('dato' + (ns.length + 1)); }
      // qué columna del CSV es cada parámetro: por nombre; si no, en orden; y se mira que los valores del test se parezcan
      const asign = ns.map(() => null), libres = cols.slice();
      ns.forEach((p, j) => {
        const pw = palabrasDe(p);
        const c = libres.find(c => { const ew = bajo(c.etiqueta).split(/[^a-z0-9]+/); return pw.every(w => ew.some(x => x === w || singular(x) === singular(w) || (SINONIMOS[x] || []).includes(w))); }) || libres.find(c => conEncabezado && primera[c.i] === p);
        if (c) { asign[j] = c; libres.splice(libres.indexOf(c), 1); }
      });
      ns.forEach((p, j) => { if (!asign[j] && libres.length) asign[j] = libres.shift(); });
      const args = muestra(n);
      campos[n] = ns.map((p, j) => {
        const c = asign[j], vs = c ? columna(c.i) : [];
        let tipo = c ? tipoCol(vs, c.etiqueta) : 'str';
        const a = args[j];
        if (a && a.k === 'bool') tipo = 'bool';
        else if (a && a.k === 'str' && tipo !== 'str') tipo = 'str';
        if (tipo === 'int' && /float|importe|monto|precio|facturaci|\$/.test(bajo(c ? c.etiqueta : ''))) tipo = 'float';
        return { n: p, tipo, col: c ? c.i : null, etiqueta: c ? c.etiqueta : p };
      });
    }
    // la base se queda con los campos que comparten todas las subclases (en el mismo lugar y con el mismo nombre)
    const comunes = [];
    if (subsN.length) {
      const c0 = campos[subsN[0]];
      for (let j = 0; j < c0.length; j++) if (subsN.every(n => campos[n][j] && campos[n][j].n === c0[j].n)) comunes.push(c0[j]); else break;
    }
    if (contrato[baseN]) { const k = contrato[baseN].params.length; comunes.splice(k); }
    campos[baseN] = comunes;
    const propios = n => campos[n].slice(comunes.length);
    const todosCampos = n => campos[n] || [];

    // ── los métodos de las entidades y sus reglas
    const metodosEnt = {};   // clase → { nombre: [candidatos IR] }
    const metodosTest = n => Object.keys((T.clases[n] || { metodos: {} }).metodos);
    const colMet = colectorN ? Object.keys(T.clases[colectorN].metodos) : [];
    const nombresMet = [...new Set(subsN.flatMap(metodosTest).concat([...(T.metodosSueltos || [])].filter(m => !colMet.includes(m))))];
    // las oraciones que hablan de cada subclase (y el contrato de esa clase)
    const formasDe = n => { const et = etiquetaDe(n); const fs = new Set([et, singular(et), plural(singular(et))]); for (const w of palabrasDe(n)) if (w.length >= 4 && w !== bajo(baseN)) { fs.add(w); fs.add(plural(w)); } return [...fs].filter(Boolean); };
    const hablaDe = (o, n) => formasDe(n).some(f => new RegExp('(^|[^a-z])' + f.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![a-z])').test(bajo(o)) || new RegExp('(^|[^a-z])' + f + '[a-z]*', '').test(bajo(o)) && f.length >= 4 && new RegExp('(^|[^a-z])' + f).test(bajo(o)));
    const fraseDe = n => {
      const out = [];
      const delCsv = o => estructura.some(e => e.length > 12 && (bajo(o).includes(bajo(e).slice(0, 40)) || bajo(e).includes(bajo(o).slice(0, 30)))) || /\bsi\s+es\s+(?:un|una|de)\b|\bun\s+(?:numero\s+)?\d+\s+si\b|\bnumero\s+de\s+tipo\b|\b1\s+si\b.*\b0\s+si\b/.test(bajo(o));
      for (const o of ors) {
        if (delCsv(o)) continue;
        // una oración puede hablar de varias subclases: se parte en cláusulas («…; en los de modalidad Mini se resta…»)
        const cls = o.split(/;\s*|\.\s+(?=[A-ZÁÉÍÓÚ])/);
        for (const c of cls) if (hablaDe(c, n) && !subsN.some(x => x !== n && hablaDe(c, x) && !formasDe(n).some(f => formasDe(x).includes(f)) && etiquetaDe(x).length > etiquetaDe(n).length && bajo(c).includes(etiquetaDe(x)))) out.push(c);
      }
      if (contrato[n]) out.push(contrato[n].linea.replace(/^.*?\)\s*[—–-]\s*/, ''));
      return out;
    };
    // a qué campo se refiere una palabra o frase del enunciado
    function campoDe(frase, n, soloTipo) {
      const fw = bajo(frase).split(/[^a-z0-9]+/).filter(w => w && !VACIAS.has(w));
      const cs = todosCampos(n).filter(c => !soloTipo || soloTipo.includes(c.tipo));
      let mejor = null, pm = 0;
      for (const c of cs) {
        const cw = palabrasDe(c.n).concat(bajo(c.etiqueta || '').split(/[^a-z0-9]+/).filter(w => w.length > 3 && !VACIAS.has(w)));
        let p = 0;
        for (const w of fw) for (const x of cw) { if (x === w || singular(x) === singular(w)) p += 2; else if ((SINONIMOS[w] || []).includes(x) || (SINONIMOS[x] || []).includes(w)) p += 1; else if (w.length >= 5 && x.length >= 5 && (x.startsWith(w.slice(0, 5)) || w.startsWith(x.slice(0, 5)))) p += 1; }
        if (p > pm) { pm = p; mejor = c; }
      }
      return mejor;
    }
    // ── IR: { t:'campo'|'num'|'bin'|'met'|'si'|'cmp'|'no'|'super'|'cadena' }
    const C = (n) => ({ t: 'campo', n }), N = v => ({ t: 'num', v }), B = (op, a, b) => ({ t: 'bin', op, a, b });
    const MET = n => ({ t: 'met', n }), SI = (c, a, b) => ({ t: 'si', c, a, b }), CMP = (op, a, b) => ({ t: 'cmp', op, a, b });
    function numerico(n, metodo, sub) {
      // las reglas que el enunciado da para esa subclase, traducidas a una cuenta (puede haber más de una lectura)
      const fr = fraseDe(sub).map(bajo);
      const cands = [];
      const conBase = () => { const c = todosCampos(sub).find(c => /base/.test(c.n)) || todosCampos(sub).find(c => /base/.test(bajo(c.etiqueta || ''))); return c ? C(c.n) : null; };
      let inicio = null, sumas = [], factor = null, deOtra = null;
      for (const f0 of fr) {
        const f = f0.replace(/\s+/g, ' ');
        // «A × B», «A * B», «A x B»
        const pr = f.match(/([a-z_ ]+?)\s*(?:×|\*|\bx\b)\s*([a-z_ ]+?)(?:[.,;]|$|\s+(?:y|mas|\+))/);
        if (pr) { const a = campoDe(pr[1], sub, ['int', 'float']), b = campoDe(pr[2], sub, ['int', 'float']); if (a && b && a !== b) inicio = B('*', C(a.n), C(b.n)); }
        // «A + B» (el contrato: «redefine gasto_total() como repuestos + insumos»)
        const sm = f.match(/como\s+([a-z_]+(?:\s*[+-]\s*[a-z_]+)+)/);
        if (sm) { const ps = sm[1].split(/\s*([+-])\s*/); let e = null; for (let k = 0; k < ps.length; k += 2) { const c = campoDe(ps[k], sub, ['int', 'float']); if (!c) { e = null; break; } e = e ? B(ps[k - 1], e, C(c.n)) : C(c.n); } if (e) inicio = e; }
        // «mismo importe +10%»: la cuenta de la otra subclase
        if (/\bmismo\b|\bmisma\b|\bigual que\b/.test(f)) { const otra = subsN.find(x => x !== sub && fr.length && fraseDe(x).some(o => /×|\*|\+|equivalente/.test(o))); if (otra) deOtra = otra; }
        // «es equivalente a la facturación»
        const eq = f.match(/(?:equivalente|igual)\s+a\s+(?:la|el|los|las)?\s*([a-z_ ]+)/);
        if (eq && !inicio) { const c = campoDe(eq[1], sub, ['int', 'float']); if (c) inicio = C(c.n); }
        // «$30.000 por cada dormitorio»
        for (const m of f.matchAll(new RegExp(NUMRE + '\\s+por\\s+cada\\s+([a-z]+)', 'g'))) { const c = campoDe(m[2], sub, ['int', 'float']); if (c) sumas.push(B('*', N(num(m[1])), C(c.n))); }
        // «$100.000 si posee pileta», «en $20.000 si se encuentran en un piso inferior al tercero»
        for (const m of f.matchAll(new RegExp(NUMRE + '\\s+si\\s+(?:se\\s+encuentran?\\s+en\\s+(?:un|una|el|la)?\\s*|posee[n]?\\s+|tiene[n]?\\s+|es\\s+|cuenta[n]?\\s+con\\s+)?([a-z ]+?)(?:\\s+(inferior|menor|superior|mayor)(?:es)?\\s+(?:al?|que)\\s+(?:el\\s+|la\\s+)?([a-z0-9]+))?(?=[,.;]|\\s+y\\s|$)', 'g'))) {
          const v = num(m[1]);
          if (m[3]) { const c = campoDe(m[2], sub, ['int', 'float']); const lim = ORDINALES[m[4]] != null ? ORDINALES[m[4]] : num(m[4]); if (c && !isNaN(lim)) sumas.push(SI(CMP(/inferior|menor/.test(m[3]) ? '<' : '>', C(c.n), N(lim)), N(v), N(0))); }
          else { const c = campoDe(m[2], sub, ['bool']); if (c) sumas.push(SI(C(c.n), N(v), N(0))); }
        }
        // «se les incorpora el importe de las expensas», «se suma el total ganado en concepto de alquileres», «se resta el alquiler»
        for (const m of f.matchAll(/se\s+(?:le[s]?\s+)?(incorpora|suma|agrega|adiciona|anade|resta|descuenta)[n]?\s+(?:el|la|los|las)?\s*([a-z ]+?)(?=[,.;]|\s+y\s|$)/g)) {
          if (/\d/.test(m[2])) continue;
          const c = campoDe(m[2].replace(/\b(importe|total|ganado|en|concepto|abonado|pagado|monto)\b/g, ' '), sub, ['int', 'float']) || campoDe(m[2], sub, ['int', 'float']);
          if (c && !(inicio && JSON.stringify(inicio).includes('"' + c.n + '"'))) sumas.push(/resta|descuenta/.test(m[1]) ? { t: 'resta', e: C(c.n) } : C(c.n));
        }
        // porcentajes: «+10%», «un 20% más», «recargo del 25%», «descuento del 10%»
        const pc = f.match(/\+\s*(\d+(?:[.,]\d+)?)\s*%|(\d+(?:[.,]\d+)?)\s*%\s+mas|recargo\s+(?:del?\s+)?(\d+(?:[.,]\d+)?)\s*%|incrementa\w*\s+(?:en\s+)?(?:un\s+)?(\d+(?:[.,]\d+)?)\s*%/);
        const dc = f.match(/descuento\s+(?:del?\s+)?(\d+(?:[.,]\d+)?)\s*%|-\s*(\d+(?:[.,]\d+)?)\s*%|(\d+(?:[.,]\d+)?)\s*%\s+menos/);
        if (pc) factor = 1 + num(pc.slice(1).find(Boolean)) / 100;
        else if (dc) factor = 1 - num(dc.slice(1).find(Boolean)) / 100;
      }
      if (!inicio && deOtra) inicio = { t: 'otra', sub: deOtra, metodo };
      if (!inicio && sumas.length) inicio = conBase();
      if (!inicio && sumas.length) {
        // «es equivalente a la facturación» en otra subclase: ese es el valor de partida («se suma …», «se resta …»)
        for (const x of subsN) if (x !== sub) for (const o of fraseDe(x).map(bajo)) { const eq = o.match(/(?:equivalente|igual)\s+a\s+(?:la|el|los|las)?\s*([a-z_ ]+)/); if (eq) { const c = campoDe(eq[1], sub, ['int', 'float']); if (c && !inicio) inicio = C(c.n); } }
      }
      if (!inicio && /importe\s+base|alquiler\s+base|precio\s+base|a\s+partir\s+de/.test(fr.join(' '))) inicio = conBase();
      let e = inicio;
      for (const s of sumas) { if (!e) { e = s.t === 'resta' ? B('-', N(0), s.e) : s; continue; } e = s.t === 'resta' ? B('-', e, s.e) : B('+', e, s); }
      if (e && factor != null) e = B('*', e, N(Math.round(factor * 1e6) / 1e6));
      if (e) cands.push(e);
      // otra lectura: el total por todo concepto (todos los importes de la clase sumados)
      const plata = todosCampos(sub).filter(c => c.tipo !== 'str' && c.tipo !== 'bool' && /importe|monto|costo|precio|repuesto|insumo|tecnico|gasto|abon|cobr|pag/.test(bajo(c.n + ' ' + c.etiqueta)));
      if (plata.length >= 2) cands.push(plata.slice(1).reduce((a, c) => B('+', a, C(c.n)), C(plata[0].n)));
      return cands;
    }
    // los métodos que devuelven verdadero o falso: «es rentable si su índice es mayor a 50»
    function booleano(metodo, sub, helper) {
      const fr = fraseDe(sub).map(bajo).join(' ; ');
      const cands = [];
      const umbrales = [...fr.matchAll(/(mayor|menor|superior|inferior)(?:es)?\s+(?:o\s+igual\s+)?(?:a|al|que)\s+(\d+(?:[.,]\d+)?)|([<>]=?)\s*(\d+(?:[.,]\d+)?)/g)].map(m => ({ op: m[3] || (/mayor|superior/.test(m[1]) ? '>' : '<'), v: num(m[2] || m[4]), i: m.index }));
      const sujeto = helper ? MET(helper) : null;
      if (!sujeto || !umbrales.length) return cands;
      if (umbrales.length >= 2) {
        // «… mayor a 40, pero los mayoristas deben tener un índice mayor a 45» / «> 40 (tradicional) o > 45 (mayorista)»
        const bools = todosCampos(sub).filter(c => c.tipo === 'bool');
        const b = bools.find(c => fr.includes(singular(palabrasDe(c.n)[0]).slice(0, 6))) || bools[0];
        if (b) {
          const w = singular(palabrasDe(b.n)[0]).slice(0, 6);
          const posW = [...fr.matchAll(new RegExp(w, 'g'))].map(m => m.index);
          const dist = u => Math.min(...posW.map(p => Math.abs(p - u.i)), 1e9);
          const uB = umbrales.slice().sort((a, b) => dist(a) - dist(b))[0];
          const uN = umbrales.find(u => u !== uB);
          cands.push(SI(C(b.n), CMP(uB.op, sujeto, N(uB.v)), CMP(uN.op, sujeto, N(uN.v))));
        }
      }
      cands.push(CMP(umbrales[0].op, sujeto, N(umbrales[0].v)));
      return cands;
    }
    // un método auxiliar que define el enunciado: «el índice de rentabilidad es el cociente entre el resultado comercial y la superficie»
    const auxiliares = [];
    for (const o of ors) {
      const m = bajo(o).match(/(?:el|la)\s+([a-z ]+?)\s+es\s+el\s+(cociente|producto|suma|diferencia)\s+entre\s+(?:el|la)\s+([a-z ]+?)\s+y\s+(?:el|la)\s+([a-z ]+?)(?=[.,;]|$)/);
      if (!m) continue;
      const nombre = snake(m[1].split(' ').filter(w => !VACIAS.has(w)).join(' '));
      const parte = x => { const met = nombresMet.find(mm => palabrasDe(mm).every(w => x.includes(w))); if (met) return MET(met); const c = campoDe(x, subsN[0], ['int', 'float']); return c ? C(c.n) : null; };
      const a = parte(m[3]), b = parte(m[4]);
      if (a && b) auxiliares.push({ n: nombre, ir: B({ cociente: '/', producto: '*', suma: '+', diferencia: '-' }[m[2]], a, b) });
    }
    // cada método del test, para cada subclase
    const contratoTipo = n => { const m = contrato[n] && contrato[n].linea.match(/tipo\(\)\s*=\s*(\d+)/); return m ? Number(m[1]) : null; };
    for (const sub of subsN) {
      metodosEnt[sub] = {};
      for (const m of nombresMet) {
        let cands = [];
        if (m === 'tipo' || /^(get_)?tipo$/.test(m)) { const v = contratoTipo(sub) ?? Number(valorTipoDe(sub)); if (!isNaN(v)) cands = [N(v)]; }
        else if (/^(es|esta|tiene|puede)_/.test(m)) cands = booleano(m, sub, (auxiliares.find(a => palabrasDe(m).some(w => a.n.includes(w.slice(0, 6)))) || auxiliares[0] || {}).n);
        else cands = numerico(m, m, sub);
        metodosEnt[sub][m] = cands;
      }
    }

    // ── la clase que guarda la colección y sus métodos
    const col = colectorN ? T.clases[colectorN] : null;
    const nColectorFinal = colectorN || (/\bempresa\b/.test(tb) ? 'Empresa' : 'Gestor');
    const listaN = col ? ([...col.attrsLeidos].find(a => !/^(nombre|razon)/.test(a)) || plural(snake(baseN))) : plural(snake(baseN));
    const agregarN = col ? (Object.keys(col.metodos).find(m => /^(agregar|add|cargar|registrar)/i.test(m)) || 'agregar') : 'agregar';
    // los ítems del enunciado que piden métodos («1. Suma de alquileres: …»)
    const gMet = grupos.filter(g => g !== gEst).sort((a, b) => b.length - a.length).find(g => g.length >= 2) || [];
    const pedidos = gMet.map(x => { const m = x.texto.match(/^([^:]{2,80}):\s*(.*)$/); return { titulo: m ? m[1] : x.texto.replace(/\.$/, ''), desc: m ? m[2] : '', todo: x.texto }; })
      .filter(p => !/polimorfismo/i.test(p.todo));
    const parecido = (nm, p) => { const ws = palabrasDe(nm).filter(w => !VACIAS.has(w)); const pw = bajo(p.titulo + ' ' + p.desc).split(/[^a-z0-9]+/); return ws.filter(w => pw.some(x => x === w || singular(x) === singular(w) || x.startsWith(w.slice(0, 5)) && w.length >= 5)).length / Math.max(1, ws.length); };
    const metodosCol = col ? Object.keys(col.metodos).filter(m => m !== agregarN) : [];
    for (const m of metodosCol) {
      if (pedidos.some(p => parecido(m, p) >= 0.6)) continue;
      const ws = palabrasDe(m).filter(w => !VACIAS.has(w));
      const l = texto.split('\n').map(x => x.trim()).find(x => { const mm = x.match(/^([^:]{3,60}):\s*(.+)$/); if (!mm) return false; const tw = bajo(mm[1]).split(/[^a-z0-9]+/); return ws.every(w => tw.some(t => t === w || singular(t) === singular(w) || t.startsWith(w.slice(0, 5)))); });
      if (l) {
        const ls2 = texto.split('\n').map(x => x.trim()), i0 = ls2.indexOf(l);
        let desc = l.match(/^([^:]{3,60}):\s*(.+)$/)[2];
        for (let i = i0 + 1; i < ls2.length; i++) { const x = ls2[i]; if (/^[A-ZÁÉÍÓÚ][^:.]{2,60}:\s/.test(x)) break; if (!x) { if (/[.:]$/.test(desc)) break; continue; } desc += ' ' + x; }
        pedidos.push({ titulo: l.match(/^([^:]{3,60}):/)[1], desc, todo: l });
      }
    }
    // a qué pedido corresponde cada método del test (por las palabras)
    const metCol = [];
    const usados = new Set();
    for (const m of metodosCol) {
      const p = pedidos.map(p => [p, parecido(m, p)]).filter(([p]) => !usados.has(p)).sort((a, b) => b[1] - a[1])[0];
      if (p && p[1] > 0) { usados.add(p[0]); metCol.push({ n: m, pedido: p[0] }); } else metCol.push({ n: m, pedido: { titulo: m.replace(/_/g, ' '), desc: '' } });
    }
    for (const p of pedidos) if (!usados.has(p)) metCol.push({ n: snake(p.titulo.split(/\s+/).filter(w => !VACIAS.has(bajo(w))).join(' ')), pedido: p, sinTest: true });
    // qué hace cada uno
    const metodoCalc = nombresMet.filter(m => !/^(es|esta|tiene|puede)_|^tipo$/.test(m));
    const calcDe = frase => { const f = bajo(frase); return metodoCalc.find(m => palabrasDe(m).some(w => w.length > 3 && f.includes(singular(w).slice(0, 6)))) || (/(total|suma|recaud|import|gast|alquiler|ganancia)/.test(f) ? metodoCalc[0] : null); };
    const subDe = frase => subsN.find(n => formasDe(n).some(fm => fm.length >= 4 && new RegExp('(^|[^a-z])' + fm).test(bajo(frase))));
    for (const mc of metCol) {
      const f = bajo(mc.pedido.titulo + ': ' + mc.pedido.desc), fd = bajo(mc.pedido.desc || mc.pedido.titulo);
      const filtro = [];
      const s = subDe(fd);
      if (s && !/cualquier tipo/.test(fd)) filtro.push({ t: 'es', n: s });
      // condiciones: «de más de 150 metros cuadrados», «más de 2 dormitorios», «que posean pileta», «gasto total de más de $10.000»
      for (const m of fd.matchAll(new RegExp('(?:([a-z ]{3,30}?)\\s+de\\s+)?(mas|menos)\\s+de\\s+' + NUMRE + '\\s*([a-z]+(?:\\s+[a-z]+)?)?', 'g'))) {
        const v = num(m[3]), op = m[2] === 'mas' ? '>' : '<';
        const cerca = (m[4] || '') + ' ' + (m[1] || '');
        const met = metodoCalc.find(mm => palabrasDe(mm).every(w => cerca.includes(w.slice(0, 5))));
        const c = met ? null : campoDe(m[4] && !/^(metros|cuadrados|m2|pesos)$/.test(m[4].split(' ')[0]) ? m[4] : (m[4] || '') + ' ' + (m[1] || ''), s || subsN[0], ['int', 'float']);
        if (met) filtro.push({ t: 'cmp', op, e: MET(met), v });
        else if (c) filtro.push({ t: 'cmp', op, e: C(c.n), v });
      }
      for (const m of fd.matchAll(/que\s+(?:posean|tengan|cuenten\s+con)\s+([a-z]+)/g)) { const c = campoDe(m[1], s || subsN[0], ['bool']); if (c) filtro.push({ t: 'campo', n: c.n }); }
      if (/no\s+rentable|menor\s+al\s+exigido/.test(f)) { const mb = nombresMet.find(m => /^es_/.test(m)); if (mb) filtro.push({ t: 'no', e: MET(mb) }); }
      if (/\bsuma\b|\btotal\b|recaudaci/.test(f) && !/cantidad/.test(bajo(mc.pedido.titulo)) && !/\bmas\b|\bmayor\b|\bmenor\b|\bpor\s+[a-z]+$/.test(bajo(mc.pedido.titulo))) mc.tipo = 'suma';
      if ((/cantidad/.test(bajo(mc.pedido.titulo)) && !/(mayor|menor)\s+cantidad/.test(bajo(mc.pedido.titulo))) || /^cantidad|^contar|^cuantos/.test(mc.n)) mc.tipo = 'cuenta';
      const pm = bajo(mc.pedido.titulo).match(/^([a-z]+)\s+por\s+([a-z]+)$/);
      if (pm) { mc.tipo = 'por'; mc.clave = campoDe(pm[2], subsN[0]); mc.valor = campoDe(pm[1], subsN[0], ['int', 'float']); }
      const fSin = f.replace(/menor\s+al\s+exigido|mayor\s+al\s+exigido/g, '');
      if (/\bmas\s+(?:alto|bajo|largo|corto|caro|barato|rentable|grande|chico)|\bmayor\b|\bmenor\b|\bmaxim|\bminim/.test(fSin) && mc.tipo !== 'por' && mc.tipo !== 'cuenta') {
        mc.tipo = /bajo|corto|barato|chico|menor|minim/.test(f.replace(/menor\s+al\s+exigido/, '')) ? 'min' : 'max';
        // la clave: «de mayor duración», «más rentable», «cuyo importe … sea el más bajo», «mayor cantidad de pasajeros»
        // la clave: todas las frases que la pueden nombrar; primero un auxiliar, después una cuenta y al final un dato
        const ks = [f.match(/(?:de|con)\s+(?:mayor|menor)\s+(?:cantidad\s+de\s+)?([a-z]+)/), f.match(/(?:cuyo|cuya)\s+([a-z ]+?)\s+sea\s+(?:el|la)\s+(?:mas|mayor|menor)/), bajo(mc.pedido.titulo).match(/([a-z]+)\s+mas\s+(?:alto|bajo|largo|corto|caro|barato|rentable)/), f.match(/([a-z]+)\s+mas\s+(?:alto|bajo|largo|corto|caro|barato|rentable)/), f.match(/mas\s+([a-z]+)/)].filter(Boolean).map(m => m[1]);
        const k = ks[0] || '';
        let aux = null, met = null;
        for (const kk of ks) { aux = auxiliares.find(a => palabrasDe(a.n).some(w => kk.includes(w.slice(0, 6)) || w.startsWith(kk.slice(0, 6)))); if (aux) break; }
        if (!aux) for (const kk of ks) { met = metodoCalc.find(mm => palabrasDe(mm).some(w => w.length > 3 && (kk.split(' ').some(x => x === w || singular(x) === singular(w)) || singular(kk).startsWith(singular(w).slice(0, 5))))) || (/definitivo|final|a\s+cobrar|calculad/.test(kk) && metodoCalc.length === 1 ? metodoCalc[0] : null); if (met) break; }
        const c = !aux && !met ? campoDe(k, s || subsN[0], ['int', 'float']) : null;
        mc.clave = aux ? MET(aux.n) : met ? MET(met) : c ? C(c.n) : null;
        // qué devuelve: un dato («nombre del propietario»), dos («la fecha y el nombre del operario») o el objeto
        const dv = (fd.match(/informe\s+(?:el|la|los|las)?\s*(.*?)\s+(?:del|de\s+la|de\s+los|de\s+las)\s+(?:[a-z]+\s+){0,3}(?:cuyo|cuya|con|de\s+mayor|de\s+menor|que)/) || [])[1] || (fd.match(/^(?:el|la)?\s*([a-z ]+?)\s+(?:del|de\s+la)\s+/) || [])[1] || '';
        const partes = dv.split(/\s+y\s+|,\s*/).map(x => x.trim()).filter(Boolean);
        const cs = partes.map(x => campoDe(x, s || subsN[0])).filter(Boolean);
        mc.devuelve = cs.length ? cs.map(c => c.n) : null;
      }
      if (!mc.tipo) mc.tipo = 'suma';
      if (mc.tipo === 'suma') mc.expr = (() => { const m = calcDe(f); return m ? MET(m) : null; })();
      mc.filtro = filtro;
    }

    // ── comprobar el modelo contra cada assert del test (sin Python) y elegir la lectura que cumple
    const modelo = { baseN, subsN, campos, comunes, metodosEnt, auxiliares, colectorN: nColectorFinal, listaN, agregarN, metCol, strDe: {}, tipoDeSub, etiquetasTipo, sep, conEncabezado, csvPrincipal, csvs, unArchivo, modDe, textoCsv: csvT };
    const elegido = {};   // sub.metodo → IR
    for (const sub of subsN) for (const m of nombresMet) elegido[sub + '.' + m] = (metodosEnt[sub][m] || [])[0] || null;
    const valorCampo = (o, c) => { if (!campos[o.clase]) return null; const i = campos[o.clase].findIndex(x => x.n === c); const a = o.args[i]; return a ? (a.k === 'num' ? a.v : a.k === 'bool' ? a.v : a.k === 'str' ? a.v : null) : null; };
    function evalIR(ir, o) {
      if (!ir) return undefined;
      switch (ir.t) {
        case 'num': return ir.v;
        case 'campo': return valorCampo(o, ir.n);
        case 'met': return llamarMet(o, ir.n);
        case 'otra': { const ir2 = elegido[ir.sub + '.' + ir.metodo]; return ir2 ? evalIR(ir2, o) : undefined; }
        case 'bin': { const a = evalIR(ir.a, o), b = evalIR(ir.b, o); if (a == null || b == null) return undefined; return ir.op === '+' ? a + b : ir.op === '-' ? a - b : ir.op === '*' ? a * b : ir.op === '/' ? a / b : undefined; }
        case 'si': return evalIR(ir.c, o) ? evalIR(ir.a, o) : evalIR(ir.b, o);
        case 'cmp': { const a = evalIR(ir.a, o), b = evalIR(ir.b, o); return ir.op === '>' ? a > b : ir.op === '<' ? a < b : ir.op === '>=' ? a >= b : ir.op === '<=' ? a <= b : a === b; }
        case 'no': return !evalIR(ir.e, o);
        default: return undefined;
      }
    }
    function llamarMet(o, n) {
      if (elegido[o.clase + '.' + n] !== undefined) return evalIR(elegido[o.clase + '.' + n], o);
      const a = auxiliares.find(x => x.n === n); if (a) return evalIR(a.ir, o);
      return undefined;
    }
    function filtrar(lista, filtro) {
      return lista.filter(o => filtro.every(f => f.t === 'es' ? o.clase === f.n : f.t === 'campo' ? !!valorCampo(o, f.n) : f.t === 'no' ? !evalIR(f.e, o) : f.t === 'cmp' ? (f.op === '>' ? evalIR(f.e, o) > f.v : evalIR(f.e, o) < f.v) : true));
    }
    function llamarCol(o, mc) {
      const lista = filtrar(o.agregados, mc.filtro || []);
      if (mc.tipo === 'suma') return lista.reduce((s, x) => s + (evalIR(mc.expr, x) || 0), 0);
      if (mc.tipo === 'cuenta') return lista.length;
      if (mc.tipo === 'max' || mc.tipo === 'min') {
        if (!lista.length) return null;
        let mejor = lista[0];
        for (const x of lista) { const a = evalIR(mc.clave, x), b = evalIR(mc.clave, mejor); if (mc.tipo === 'max' ? a > b : a < b) mejor = x; }
        return mc.devuelve ? (mc.devuelve.length === 1 ? valorCampo(mejor, mc.devuelve[0]) : mc.devuelve.map(c => valorCampo(mejor, c)).join(' ')) : mejor;
      }
      if (mc.tipo === 'por') { const d = {}; for (const x of lista) { const k = valorCampo(x, mc.clave && mc.clave.n); d[k] = (d[k] || 0) + (mc.valor ? valorCampo(x, mc.valor.n) : 1); } return d; }
      return undefined;
    }
    const valorPy = v => v == null ? null : v.k === 'num' ? v.v : v.k === 'str' ? v.v : v.k === 'bool' ? v.v : v.k === 'none' ? null : v.k === 'approx' ? valorPy(v.v) : v;
    // el valor de algo del test según el modelo (o «undefined» si no se sabe)
    function valorTest(v) {
      if (!v) return undefined;
      if (v.k !== 'sym') return v.k === 'obj' ? v : valorPy(v);
      if (v.op === 'call') {
        const o = valorTest(v.obj);
        if (!o || o.k !== 'obj') return undefined;
        if (o.clase === colectorN) { const mc = metCol.find(x => x.n === v.n); return mc ? llamarCol(o, mc) : undefined; }
        return llamarMet(o, v.n);
      }
      if (v.op === 'attr') { const o = valorTest(v.obj); if (o && o.k === 'obj') { if (o.clase === colectorN && v.n === listaN) return { k: 'lista', items: o.agregados }; return valorCampo(o, v.n); } return undefined; }
      if (v.op === 'len') { const a = valorTest(v.a); return a && a.k === 'lista' ? a.items.length : undefined; }
      if (v.op === 'isinstance') { const o = valorTest(v.a); return o && o.k === 'obj' ? (o.clase === v.c || v.c === baseN) : undefined; }
      if (v.op === 'str') { const o = valorTest(v.a); return o && o.k === 'obj' && modelo.strDe[o.clase] ? modelo.strDe[o.clase](o) : undefined; }
      return undefined;
    }
    const igual = (a, b, approx) => { if (typeof a === 'number' && typeof b === 'number') return Math.abs(a - b) <= (approx ? Math.max(1e-6 * Math.abs(b), 1e-9) : 1e-9); return a === b; };
    function comprobar(soloDe) {
      let ok = 0, total = 0;
      const fallan = [];
      for (const a of T.asserts) {
        if (soloDe && !soloDe(a)) continue;
        const izq = valorTest(a.a);
        let bien;
        if (a.op === '==' || a.op === 'is' || a.op === '!=' || a.op === 'is not') {
          const der = a.b.k === 'sym' ? valorTest(a.b) : valorPy(a.b);
          if (der === undefined) continue;
          if (izq === undefined) { if (a.a.k === 'sym' && a.a.op === 'call' && a.a.obj && a.a.obj.k === 'obj') { total++; fallan.push(a); } continue; }
          bien = igual(izq, der, a.b.k === 'approx'); if (a.op === '!=' || a.op === 'is not') bien = !bien;
        } else if (a.op === 'truthy' || a.op === 'falsy') { if (izq === undefined) continue; bien = a.op === 'truthy' ? !!izq : !izq; }
        else if (['>', '<', '>=', '<='].includes(a.op)) { const der = valorPy(a.b); if (izq === undefined || der == null) continue; bien = a.op === '>' ? izq > der : a.op === '<' ? izq < der : a.op === '>=' ? izq >= der : izq <= der; }
        else continue;
        total++; if (bien) ok++; else fallan.push(a);
      }
      return { ok, total, fallan };
    }
    // para cada método de cada subclase: la primera lectura que cumple sus asserts
    const assertDe = (sub, m) => a => a.a.k === 'sym' && a.a.op === 'call' && a.a.n === m && a.a.obj && a.a.obj.k === 'obj' && a.a.obj.clase === sub;
    for (const sub of subsN) for (const m of nombresMet) {
      const cands = metodosEnt[sub][m] || [];
      const r0 = comprobar(assertDe(sub, m));
      if (r0.total && r0.ok === r0.total) continue;
      let listo = false;
      for (const c of cands.slice(1).concat(variantes(cands))) { elegido[sub + '.' + m] = c; const r = comprobar(assertDe(sub, m)); if (r.total && r.ok === r.total) { listo = true; break; } }
      if (!listo) { elegido[sub + '.' + m] = cands[0] || null; if (!cands.length) avisos.push(`${sub}.${m}(): no encontré en el enunciado cómo se calcula.`); else if (r0.total) avisos.push(`${sub}.${m}(): la cuenta que leí del enunciado no da lo que espera el test; revisala.`); }
    }
    // lo que devuelve cada método «el más/el menos»: si el test compara con un texto, ese dato; si mira sus atributos, el objeto
    for (const mc of metCol.filter(x => x.tipo === 'max' || x.tipo === 'min')) {
      const usos = T.asserts.filter(a => a.a.k === 'sym' && a.a.op === 'call' && a.a.n === mc.n && a.b && a.b.k === 'str');
      const atributos = T.asserts.some(a => JSON.stringify(a.a, (k, v) => k === 'obj' || k === 'a' ? (v && v.k === 'sym' && v.n === mc.n ? 'ES' : v) : v).includes('ES'));
      if (usos.length) {
        const dev0 = mc.devuelve; mc.devuelve = null;
        const o = valorTest(usos[0].a.obj), gan = o ? llamarCol(o, mc) : null;
        mc.devuelve = dev0;
        if (gan && gan.k === 'obj') {
          const esperado = usos[0].b.v, cs = todosCampos(gan.clase);
          const uno = cs.find(c => String(valorCampo(gan, c.n)) === esperado);
          if (uno) mc.devuelve = [uno.n];
          else { const toks = esperado.split(' '); const dos = toks.map(tk => (cs.find(c => String(valorCampo(gan, c.n)) === tk) || {}).n); if (dos.every(Boolean)) mc.devuelve = dos; }
        }
      } else if (atributos) mc.devuelve = null;
    }
    // __str__: lo que espera el test («"1 1"» es número y tipo)
    for (const a of T.asserts) {
      if (!(a.a.k === 'sym' && a.a.op === 'str' && a.b.k === 'str')) continue;
      let o = valorTest(a.a.a);
      if (!o || o.k !== 'obj') continue;
      const toks = a.b.v.split(' ');
      const valores = todosCampos(o.clase).map(c => ({ e: C(c.n), v: valorCampo(o, c.n) })).concat(nombresMet.map(m => ({ e: MET(m), v: llamarMet(o, m) })));
      const usadas = new Set();
      const partes = toks.map(tk => { const x = valores.find(x => String(x.v) === tk && !usadas.has(x)); if (x) usadas.add(x); return x && x.e; });
      if (partes.every(Boolean)) { modelo.strFmt = partes; modelo.strDe = Object.fromEntries(subsN.map(n => [n, oo => modelo.strFmt.map(p => String(evalIR(p, oo))).join(' ')])); }
    }
    const comprobacion = comprobar();
    if (comprobacion.total && comprobacion.ok < comprobacion.total) avisos.push(`El modelo no cumple ${comprobacion.total - comprobacion.ok} de las ${comprobacion.total} comprobaciones del test: revisá esos métodos.`);
    modelo.elegido = elegido;
    const archivos = escribir(modelo);
    return { archivos, avisos, comprobacion: { ok: comprobacion.ok, total: comprobacion.total, fallan: comprobacion.fallan.map(a => `línea ${a.l}: ${TestLee.texto(a.a)} ${a.op} ${a.b ? TestLee.texto(a.b) : ''}`) }, modelo, test: T };
  }
  // otras lecturas de una regla: el límite incluido o no, el redondeo del porcentaje
  function variantes(cands) {
    const out = [];
    const cambiar = (ir, f) => { const x = f(ir); if (x) return x; if (!ir || typeof ir !== 'object') return ir; const c = { ...ir }; for (const k of ['a', 'b', 'c', 'e']) if (c[k]) c[k] = cambiar(c[k], f); return c; };
    for (const c of cands) {
      out.push(cambiar(c, ir => ir.t === 'cmp' && ir.op === '<' ? { ...ir, op: '<=' } : ir.t === 'cmp' && ir.op === '>' ? { ...ir, op: '>=' } : null));
      out.push(cambiar(c, ir => ir.t === 'cmp' && ir.op === '<=' ? { ...ir, op: '<' } : ir.t === 'cmp' && ir.op === '>=' ? { ...ir, op: '>' } : null));
    }
    return out;
  }

  // ───────── El código Python
  function escribir(M) {
    const archivos = {};
    const py = (ir, yo = 'self') => {
      switch (ir.t) {
        case 'num': return Number.isInteger(ir.v) ? String(ir.v) : String(ir.v);
        case 'campo': return `${yo}.${ir.n}`;
        case 'met': return `${yo}.${ir.n}()`;
        case 'otra': { const e = M.elegido[ir.sub + '.' + ir.metodo]; return e ? py(e, yo) : '0'; }
        case 'bin': { const a = py(ir.a, yo), b = py(ir.b, yo); const pa = ir.a.t === 'bin' && prec(ir.a.op) < prec(ir.op) ? `(${a})` : a; const pb = ir.b.t === 'bin' && prec(ir.b.op) <= prec(ir.op) && !(ir.op === '+' && ir.b.op === '+') ? `(${b})` : b; return `${pa} ${ir.op} ${pb}`; }
        case 'si': return `(${py(ir.a, yo)} if ${py(ir.c, yo)} else ${py(ir.b, yo)})`;
        case 'cmp': return `${py(ir.a, yo)} ${ir.op} ${py(ir.b, yo)}`;
        case 'no': return `not ${py(ir.e, yo)}`;
        default: return '0';
      }
    };
    const prec = op => op === '+' || op === '-' ? 1 : 2;
    const metodosDe = sub => Object.keys(M.metodosEnt[sub] || {});
    const todosMet = [...new Set(M.subsN.flatMap(metodosDe))];
    const comunesN = M.comunes.map(c => c.n);
    const imports = new Set();
    const bloques = {};   // módulo → [texto]
    const modulo = n => M.unArchivo || M.modDe(n) || snake(n);
    const poner = (n, t) => { const m = modulo(n); (bloques[m] || (bloques[m] = [])).push({ n, t }); };
    const nombreLegible = n => n.replace(/_/g, ' ');
    // la base
    {
      const ls = ['from abc import ABC, abstractmethod', '', '', `class ${M.baseN}(ABC):`, `    def __init__(self, ${comunesN.join(', ')}):`];
      for (const c of comunesN) ls.push(`        self.${c} = ${c}`);
      if (!comunesN.length) ls[ls.length - 1] = '    def __init__(self):', ls.push('        pass');
      for (const m of todosMet) { ls.push('', '    @abstractmethod', `    def ${m}(self):`, `        """Cada tipo lo calcula a su manera (polimorfismo)."""`); }
      for (const a of M.auxiliares) ls.push('', `    def ${a.n}(self):`, `        return ${py(a.ir)}`);
      if (M.strFmt) ls.push('', '    def __str__(self):', `        return f"${M.strFmt.map(p => '{' + py(p) + '}').join(' ')}"`);
      else ls.push('', '    def __str__(self):', `        return f"{type(self).__name__}: ${comunesN.slice(0, 3).map(c => '{self.' + c + '}').join(' · ')}"`);
      poner(M.baseN, ls.join('\n'));
    }
    // las subclases
    for (const sub of M.subsN) {
      const pr = M.campos[sub].slice(M.comunes.length).map(c => c.n);
      const ls = [`class ${sub}(${M.baseN}):`, `    def __init__(self, ${comunesN.concat(pr).join(', ')}):`, `        super().__init__(${comunesN.join(', ')})`];
      for (const c of pr) ls.push(`        self.${c} = ${c}`);
      for (const m of metodosDe(sub)) { const ir = M.elegido[sub + '.' + m]; ls.push('', `    def ${m}(self):`, `        return ${ir ? py(ir) : 'None  # no está en el enunciado: completalo'}`); }
      poner(sub, ls.join('\n'));
    }
    // la colección
    {
      const L = M.listaN, ls = [`class ${M.colectorN}:`, '    def __init__(self):', `        self.${L} = []`, '', `    def ${M.agregarN}(self, ${snake(M.baseN)}):`, `        self.${L}.append(${snake(M.baseN)})`];
      const v = snake(M.baseN)[0];
      const cond = f => f.t === 'es' ? `isinstance(${v}, ${f.n})` : f.t === 'campo' ? `${v}.${f.n}` : f.t === 'no' ? `not ${py(f.e, v)}` : f.t === 'cmp' ? `${py(f.e, v)} ${f.op} ${f.v}` : 'True';
      const donde = filtro => filtro.length ? ' if ' + filtro.map(cond).join(' and ') : '';
      for (const mc of M.metCol) {
        ls.push('', `    def ${mc.n}(self):`);
        const f = mc.filtro || [];
        if (mc.tipo === 'suma') ls.push(`        return sum(${mc.expr ? py(mc.expr, v) : '0'} for ${v} in self.${L}${donde(f)})`);
        else if (mc.tipo === 'cuenta') ls.push(`        return len([${v} for ${v} in self.${L}${donde(f)}])`);
        else if (mc.tipo === 'max' || mc.tipo === 'min') {
          ls.push(`        candidatos = [${v} for ${v} in self.${L}${donde(f)}]`, '        if not candidatos:', '            return None', `        elegido = ${mc.tipo}(candidatos, key=lambda ${v}: ${mc.clave ? py(mc.clave, v) : '0'})`);
          ls.push(`        return ${!mc.devuelve ? 'elegido' : mc.devuelve.length === 1 ? 'elegido.' + mc.devuelve[0] : 'f"' + mc.devuelve.map(c => '{elegido.' + c + '}').join(' ') + '"'}`);
        } else if (mc.tipo === 'por') {
          const k = mc.clave ? mc.clave.n : 'tipo';
          ls.push('        resultado = {}', `        for ${v} in self.${L}${donde(f) ? ':' : ':'}`);
          if (f.length) ls.push(`            if not (${f.map(cond).join(' and ')}):`, '                continue');
          ls.push(`            resultado[${v}.${k}] = resultado.get(${v}.${k}, 0) + ${mc.valor ? v + '.' + mc.valor.n : '1'}`, '        return resultado');
        }
      }
      poner(M.colectorN, ls.join('\n'));
    }
    // el main: lee el CSV y muestra cada resultado
    const conv = (c, x) => c.tipo === 'int' ? `int(${x})` : c.tipo === 'float' ? `float(${x})` : c.tipo === 'bool' ? (/true|false/i.test(M.textoCsv) ? `${x}.strip().lower() == "true"` : `${x}.strip() == "1"`) : `${x}.strip()`;
    const archivoCsv = M.csvPrincipal || 'datos.csv';
    const lee = [`def leer_${M.listaN}(nombre_archivo, ${snake(M.colectorN)}):`, '    with open(nombre_archivo, encoding="utf-8") as archivo:'];
    if (M.conEncabezado) lee.push('        archivo.readline()   # la primera línea son los títulos');
    lee.push('        for linea in archivo:', '            if not linea.strip():', '                continue', `            datos = linea.strip().split("${M.sep}")`);
    const tipos = Object.entries(M.tipoDeSub);
    tipos.forEach(([k, sub], i) => {
      const iTipo = 0;
      const args = M.campos[sub].map(c => conv(c, `datos[${c.col}]`));
      lee.push(`            ${i === 0 ? 'if' : i === tipos.length - 1 ? 'else' : 'elif'}${i === tipos.length - 1 && i > 0 ? '' : ` datos[${iTipo}].strip() == "${k}"`}:`, `                ${snake(M.colectorN)}.${M.agregarN}(${sub}(${args.join(', ')}))`);
    });
    if (!tipos.length && M.subsN.length) lee.push(`            ${snake(M.colectorN)}.${M.agregarN}(${M.subsN[0]}(${M.campos[M.subsN[0]].map(c => conv(c, `datos[${c.col}]`)).join(', ')}))`);
    const main = ['def main():', `    ${snake(M.colectorN)} = ${M.colectorN}()`, `    leer_${M.listaN}("${archivoCsv}", ${snake(M.colectorN)})`, `    print("Cantidad de ${M.listaN.replace(/_/g, ' ')}:", len(${snake(M.colectorN)}.${M.listaN}))`];
    for (const mc of M.metCol) main.push(`    print("${capital(nombreLegible(mc.pedido && mc.pedido.titulo ? bajo(mc.pedido.titulo) : mc.n)).replace(/"/g, '')}:", ${snake(M.colectorN)}.${mc.n}())`);
    main.push('', '', 'if __name__ == "__main__":', '    main()');
    // armar los archivos: uno solo (si el test importa todo de un módulo) o uno por clase
    const orden = [M.baseN, ...M.subsN, M.colectorN];
    const modulos = [...new Set(orden.map(modulo))];
    const claseDeMod = m => orden.filter(n => modulo(n) === m);
    for (const m of modulos) {
      const ns = claseDeMod(m);
      const deps = new Set();
      for (const n of ns) {
        if (M.subsN.includes(n) && modulo(M.baseN) !== m) deps.add(M.baseN);
        if (n === M.colectorN) for (const f of M.metCol.flatMap(x => x.filtro || [])) if (f.t === 'es' && modulo(f.n) !== m) deps.add(f.n);
      }
      const cab = [];
      const tieneABC = ns.includes(M.baseN);
      for (const d of deps) cab.push(`from ${modulo(d)} import ${d}`);
      let cuerpo = ns.map(n => bloques[m].find(b => b.n === n).t).join('\n\n\n');
      if (!tieneABC) cuerpo = cuerpo;
      else cuerpo = cuerpo.replace('from abc import ABC, abstractmethod\n\n\n', '');
      const top = (tieneABC ? ['from abc import ABC, abstractmethod'] : []).concat(cab);
      archivos[m + '.py'] = (top.length ? top.join('\n') + '\n\n\n' : '') + cuerpo + '\n';
    }
    // el main va en el mismo archivo si es uno solo; si no, en main.py
    const usa = [...new Set([M.colectorN, ...M.subsN])];
    if (M.unArchivo) archivos[M.unArchivo + '.py'] = archivos[M.unArchivo + '.py'].replace(/\n$/, '') + '\n\n\n' + lee.join('\n') + '\n\n\n' + main.join('\n') + '\n';
    else archivos['main.py'] = usa.map(n => `from ${modulo(n)} import ${n}`).sort().join('\n') + '\n\n\n' + lee.join('\n') + '\n\n\n' + main.join('\n') + '\n';
    return archivos;
  }

  return { resolver, limpiar, items };
});
