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
  const palabrasDe = n => String(n).replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/([A-Z])([A-Z][a-z])/g, '$1 $2').replace(/_/g, ' ').toLowerCase().split(/\s+/).filter(Boolean).map(bajo);
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
  function resolver({ enunciado, csvs, tests, carpetaCsv }) {
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
    const componentes = entidades.filter(n => n !== baseN && !T.clases[n].bases.has(baseN) && T.objetos.some(o => o.clase !== n && o.args.some(a => a && a.k === 'obj' && a.clase === n)));
    const subsN = entidades.filter(n => n !== baseN && T.clases[n].ctores.length && !componentes.includes(n));
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

    const infoCsv = {};
    for (const n of csvNombres) {
      const t = csvs[n].replace(/^\uFEFF/, '').replace(/\r/g, ''), ls = t.split('\n').filter(l => l.trim());
      const sp = (ls[0] || '').includes(';') && !(ls[0] || '').includes(',') ? ';' : ',';
      const pr = ls.length ? ls[0].split(sp).map(x => x.trim()) : [];
      const enc = pr.length > 1 && pr.every(x => /^[A-Za-z_][\w ]*$/.test(x)) && !pr.every(x => /^(true|false|si|no)$/i.test(x));
      infoCsv[n] = { n, sep: sp, primera: pr, conEncabezado: enc, filas: (enc ? ls.slice(1) : ls).map(l => l.split(sp).map(x => x.trim())), texto: t };
    }
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

    const mismoValor = (x, y) => x && y && (x === y || (x.k !== 'obj' && y.k !== 'obj' && x.k === y.k && x.v === y.v));
    function nombresDelTest(n) {
      const votos = [];
      for (const a of T.asserts) {
        const sa = a.a;
        if (!(sa.k === 'sym' && sa.op === 'attr' && sa.obj && sa.obj.k === 'obj' && sa.obj.clase === n) || !['==', 'is'].includes(a.op)) continue;
        const b = a.b.k === 'approx' ? a.b.v : a.b;
        let pos = sa.obj.args.map((x, i) => mismoValor(x, b) ? i : -1).filter(i => i >= 0);
        // 4.0 y 4 valen lo mismo, pero si el test escribe uno con decimales y el otro no, son datos distintos
        if (pos.length > 1 && b.k === 'num') { const p2 = pos.filter(i => !!sa.obj.args[i].real === !!b.real); if (p2.length === 1) pos = p2; }
        if (pos.length === 1) { const v = votos[pos[0]] || (votos[pos[0]] = {}); v[sa.n] = (v[sa.n] || 0) + 1; }
      }
      return Array.from(votos, v => v ? Object.entries(v).sort((x, y) => y[1] - x[1])[0][0] : null);
    }
    // el valor por defecto de un parámetro que a veces no se pasa: el que espera el test («.habitual is False») o el vacío del tipo
    function porDefecto(n, j, nombre, tipo) {
      const sin = T.objetos.filter(o => o.clase === n && o.args.length <= j);
      if (!sin.length) return undefined;
      for (const a of T.asserts) if (a.a.k === 'sym' && a.a.op === 'attr' && a.a.n === nombre && sin.includes(a.a.obj) && ['==', 'is'].includes(a.op)) return a.b;
      return tipo === 'bool' ? { k: 'bool', v: false } : tipo === 'str' ? { k: 'str', v: '' } : tipo === 'obj' ? { k: 'none' } : { k: 'num', v: 0 };
    }
    // cada clase con su CSV, si hay uno por clase: por el nombre del archivo y por las columnas
    const csvDe = {};
    const variosCsv = Object.values(infoCsv).filter(x => x.conEncabezado).length > 1 && !estructura.some(x => /^tipo\b/i.test(x));
    if (variosCsv) {
      const clasesCsv = subsN.concat(componentes);
      const puntos = (n, info) => {
        const fw = bajo(info.n.replace(/\.csv$/i, '')).split(/[^a-z0-9]+/).map(singular), cw = palabrasDe(n).map(singular);
        let p = cw.filter(w => fw.includes(w)).length * 3 - fw.filter(w => !cw.includes(w)).length;
        const nt = nombresDelTest(n).filter(Boolean).map(x => palabrasDe(x).filter(w => !VACIAS.has(w)));
        const hw = info.primera.map(h => bajo(h).split(/[^a-z0-9]+/));
        p += nt.filter(ws => hw.some(h => ws.every(w => h.includes(w)))).length;
        return p;
      };
      const libres = Object.values(infoCsv).filter(x => x.conEncabezado);
      for (const n of clasesCsv.slice().sort((a, b) => Math.max(...libres.map(i => puntos(b, i))) - Math.max(...libres.map(i => puntos(a, i))))) {
        const mejor = libres.map(i => [i, puntos(n, i)]).sort((a, b) => b[1] - a[1])[0];
        if (mejor && mejor[1] > 0) { csvDe[n] = mejor[0].n; libres.splice(libres.indexOf(mejor[0]), 1); }
      }
    }
    // ── los campos de cada clase: cuántos (el test), cómo se llaman (contrato, encabezado o enunciado) y de qué tipo
    const muestra = n => (T.clases[n] && T.clases[n].ctores[0]) ? T.clases[n].ctores[0].args : [];
    const aridad = n => { const cs = T.clases[n] ? T.clases[n].ctores : []; return cs.length ? Math.max(...cs.map(c => c.args.length + Object.keys(c.kws).length)) : 0; };
    // columnas del CSV para cada subclase: las comunes y las propias («Si es una casa, …; si es un departamento, …»)
    const colsDe = {};   // sub → [{ i (columna del CSV), etiqueta }]
    for (const n of subsN.concat(componentes)) colsDe[n] = csvDe[n] ? infoCsv[csvDe[n]].primera.map((h, i) => ({ i, etiqueta: h, csv: csvDe[n] })) : [];
    if (!variosCsv) estructura.forEach((e, i) => {
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
    for (const n of subsN.concat(componentes)) {
      const k = aridad(n), cols = colsDe[n];
      let ns = contrato[n] ? contrato[n].params.slice() : null;
      const delTest = nombresDelTest(n);
      if (!ns && conEncabezado && cols.length === k) ns = cols.map(c => primera[c.i]);
      if (!ns) ns = cols.map(c => nombreDeEtiqueta(c.etiqueta));
      if (ns.length !== k) { if (ns.length > k) ns = ns.slice(0, k); else while (ns.length < k) ns.push('dato' + (ns.length + 1)); }
      if (!contrato[n]) delTest.forEach((x, j) => { if (x && j < k) ns[j] = x; });
      // si un nombre quedó repetido, el que no vino del test se renombra
      ns = ns.map((x, j) => ns.indexOf(x) !== j && !delTest[j] ? x + '_' + (j + 1) : x);
      // qué columna del CSV es cada parámetro: por nombre; si no, en orden; y se mira que los valores del test se parezcan
      const asign = ns.map(() => null), libres = cols.slice();
      ns.forEach((p, j) => {
        const pw = palabrasDe(p);
        const pw2 = pw.filter(w => !VACIAS.has(w));
        const c = libres.find(c => { const ew = bajo(c.etiqueta).split(/[^a-z0-9]+/); return pw2.every(w => ew.some(x => x === w || singular(x) === singular(w) || (SINONIMOS[x] || []).includes(w))); }) || libres.find(c => conEncabezado && primera[c.i] === p);
        if (c) { asign[j] = c; libres.splice(libres.indexOf(c), 1); }
      });
      const args = muestra(n);
      // un objeto que se pasa adentro (el paciente de la atención) no es una columna
      ns.forEach((p, j) => { if (!asign[j] && libres.length && !(args[j] && args[j].k === 'obj')) asign[j] = libres.shift(); });
      campos[n] = ns.map((p, j) => {
        const c = asign[j], vs = c ? (c.csv ? infoCsv[c.csv].filas.map(f => f[c.i]).filter(x => x != null && x !== '') : columna(c.i)) : [];
        if (args[j] && args[j].k === 'obj') return { n: p, tipo: 'obj', clase: args[j].clase, col: null, etiqueta: p, defecto: porDefecto(n, j, p, 'obj') };
        let tipo = c ? tipoCol(vs, c.etiqueta) : 'str';
        const a = args[j];
        if (a && a.k === 'bool') tipo = 'bool';
        else if (a && a.k === 'str' && tipo !== 'str') tipo = 'str';
        if (tipo === 'int' && /float|importe|monto|precio|facturaci|\$/.test(bajo(c ? c.etiqueta : ''))) tipo = 'float';
        if (a && a.k === 'num' && a.real && tipo === 'int') tipo = 'float';
        return { n: p, tipo, col: c ? c.i : null, csv: c ? c.csv : null, etiqueta: c ? c.etiqueta : p, defecto: porDefecto(n, j, p, tipo) };
      });
    }
    // la base se queda con los campos que comparten todas las subclases (en el mismo lugar y con el mismo nombre)
    const comunes = [];
    if (subsN.length) {
      const c0 = campos[subsN[0]];
      for (let j = 0; j < c0.length; j++) if (subsN.every(n => campos[n][j] && campos[n][j].n === c0[j].n)) comunes.push(c0[j]); else break;
    }
    if (contrato[baseN]) { const k = contrato[baseN].params.length; comunes.splice(k); }
    else if (T.clases[baseN] && T.clases[baseN].ctores.length) { const k = Math.max(...T.clases[baseN].ctores.map(c => c.args.length)); if (k < comunes.length) comunes.splice(k); }
    campos[baseN] = comunes;
    const propios = n => campos[n].slice(comunes.length);
    const todosCampos = n => campos[n] || [];

    // ── los valores posibles de un dato («el síntoma que prevalece (1: “corazon”, 2: “pulmon”, 3: “otras”)») y lo que no
    // puede valer («el cupón de descuento debe ser 0 o positivo»): de quién es el dato, por el nombre
    const clasesConDatos = [baseN, ...componentes, ...subsN];
    function duenio(frase, soloTipo) {
      let mejor = null;
      for (const n of clasesConDatos) {
        const c = campoDe(frase, n, soloTipo);
        if (!c) continue;
        const p = puntosCampo(frase, c);
        if (!mejor || p > mejor.p) mejor = { n: comunes.includes(c) ? baseN : n, c, p };
      }
      return mejor && mejor.p >= 2 ? mejor : null;
    }
    const etiquetas = {};      // clase → { campo: { '1': 'corazon', … } }
    const validaciones = {};   // clase → [{ campo, valores | minimo, exc }]
    const raisesDe = n => T.raises.filter(r => r.v && r.v.k === 'obj' && (r.v.clase === n || (n === baseN && subsN.includes(r.v.clase))));
    for (const m of texto.matchAll(/\(([^()]*?\d+\s*[:=]\s*[“"«][^()]*?)\)/g)) {
      const vals = {};
      for (const x of m[1].matchAll(/(\d+)\s*[:=]\s*[“"«]([^”"»]+)[”"»]/g)) vals[x[1]] = x[2].trim();
      if (Object.keys(vals).length < 2) continue;
      const antes = texto.slice(Math.max(0, m.index - 150), m.index).split(/[.;:]\s|\n/).pop();
      const d = duenio(antes, ['int']);
      if (!d) continue;
      (etiquetas[d.n] || (etiquetas[d.n] = {}))[d.c.n] = vals;
      d.c.etiquetas = vals;
      if (d.n === baseN) for (const sb of subsN) for (const c of campos[sb]) if (c.n === d.c.n) c.etiquetas = vals;
      // si el test espera un error con un valor que no es de la lista, el constructor lo rechaza
      const j = (campos[d.n] || []).indexOf(d.c);
      const malos = raisesDe(d.n).filter(r => { const a = r.v.args[j]; return a && !(a.k === 'num' && String(a.v) in vals); });
      if (malos.length) (validaciones[d.n] || (validaciones[d.n] = [])).push({ campo: d.c.n, valores: Object.keys(vals).map(Number), exc: malos[0].exc || 'ValueError' });
    }
    for (const o of ors) {
      const m = bajo(o).match(/\b(?:el|la|los|las)\s+([a-z ]+?)\s+(?:debe|deben)\s+ser\s+(?:0|cero)\s+o\s+positiv|\b(?:el|la|los|las)\s+([a-z ]+?)\s+no\s+(?:puede|pueden)\s+ser\s+negativ/);
      if (!m) continue;
      const d = duenio(m[1] || m[2], ['int', 'float']);
      if (d && !(validaciones[d.n] || []).some(v => v.campo === d.c.n)) (validaciones[d.n] || (validaciones[d.n] = [])).push({ campo: d.c.n, minimo: 0, exc: 'ValueError' });
    }

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
      // un párrafo que arranca nombrando a una sola subclase (y no es una lista) habla de ella entero
      const estricto = (o, x) => formasDe(x).some(f => new RegExp('(^|[^a-z])' + f.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(s|es)?(?![a-z])').test(bajo(o)));
      for (const par of texto.split(/\n\s*\n/)) {
        if ((par.match(/^\s*(?:[-*•]|\d+[.)])\s/gm) || []).length > 1) continue;
        const os2 = oraciones(par);
        if (os2.length < 2 || delCsv(os2[0]) || !estricto(os2[0], n) || subsN.some(x => x !== n && os2.some(o => estricto(o, x)))) continue;
        for (const o of os2.slice(1)) if (!out.includes(o) && !delCsv(o)) out.push(o);
      }
      if (contrato[n]) out.push(contrato[n].linea.replace(/^.*?\)\s*[—–-]\s*/, ''));
      return out;
    };
    // a qué campo se refiere una palabra o frase del enunciado
    function puntosCampo(frase, c) {
      const fw = bajo(frase).split(/[^a-z0-9]+/).filter(w => w && !VACIAS.has(w));
      const cw = palabrasDe(c.n).concat(bajo(c.etiqueta || '').split(/[^a-z0-9]+/).filter(w => w.length > 3 && !VACIAS.has(w)));
      let p = 0;
      for (const w of fw) for (const x of cw) { if (x === w || singular(x) === singular(w)) p += 2; else if ((SINONIMOS[w] || []).includes(x) || (SINONIMOS[x] || []).includes(w)) p += 1; else if (w.length >= 5 && x.length >= 5 && (x.startsWith(w.slice(0, 5)) || w.startsWith(x.slice(0, 5)))) p += 1; }
      return p;
    }
    function campoDe(frase, n, soloTipo) {
      const cs = todosCampos(n).filter(c => !soloTipo || soloTipo.includes(c.tipo));
      let mejor = null, pm = 0;
      for (const c of cs) { const p = puntosCampo(frase, c); if (p > pm) { pm = p; mejor = c; } }
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
      const ps = pasosDe(sub);
      if (ps) cands.push(ps);
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
    function condicion(t, sub) {
      let m = t.match(/(?:el|la|los|las)?\s*([a-z ]+?)\s+(?:sea|es|sean|son)\s+igual(?:es)?\s+(?:a|que)\s+(\d+)/);
      if (m) { const c = campoDe(m[1], sub, ['int', 'float', 'str']); if (c) return CMP('==', C(c.n), N(num(m[2]))); }
      m = t.match(/([a-z]+)\s+(?:sea|es|este|esta)\s+[“"«]?([a-z]+)/);
      if (m) {
        const own = campoDe(m[2], sub, ['bool']); if (own) return C(own.n);
        for (const c of todosCampos(sub).filter(c => c.tipo === 'obj')) { const b = campoDe(m[2], c.clase, ['bool']); if (b) return { t: 'de', obj: c.n, n: b.n }; }
      }
      return null;
    }
    function pasosDe(sub) {
      let inicio = null;
      const pasos = [];
      for (const f0 of fraseDe(sub).map(bajo)) {
        const f = f0.replace(/\s+/g, ' ');
        const ap = f.match(/a\s+partir\s+(?:del|de\s+la|de\s+los|de\s+las|de)\s+([a-z ]+?)(?=[.,;(]|$)/);
        if (ap && !inicio) { const c = campoDe(ap[1], sub, ['int', 'float']); if (c) inicio = C(c.n); }
        const rd = f.match(/(?:realiza|aplica|hace|resta)\w*\s+el\s+descuento\s+del?\s+([a-z ]+?)(?=[.,;(]|\s+cuyo|$)/);
        if (rd && !/%/.test(f)) { const c = campoDe(rd[1], sub, ['int', 'float']); if (c) pasos.push({ cond: null, op: '-', v: C(c.n) }); }
        for (const cl of f.split(/;\s*/)) {
          const pc = cl.match(/(\d+(?:[.,]\d+)?)\s*%/);
          if (!pc) continue;
          const condTxt = (cl.match(/(?:\bsi|en\s+caso\s+(?:de\s+)?que)\s+(.+?)\s+(?:se\s+le|se\s+les|se\s|,)/) || [])[1];
          const cond = condTxt ? condicion(condTxt, sub) : null;
          if (condTxt && !cond) continue;
          const v = num(pc[1]), mas = /\bmas\b|increment|recargo|aument/.test(cl) && !/descuento/.test(cl);
          pasos.push({ cond, op: '*', v: N(Math.round((1 + (mas ? v : -v) / 100) * 1e6) / 1e6) });
        }
      }
      return inicio && pasos.some(p => p.cond) ? { t: 'pasos', inicio, pasos } : null;
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
        else if (/^(es|esta|tiene|puede)$/.test(palabrasDe(m)[0])) {
          cands = booleano(m, sub, (auxiliares.find(a => palabrasDe(m).some(w => a.n.includes(w.slice(0, 6)))) || auxiliares[0] || {}).n);
          if (!cands.length) { const c = condicion(palabrasDe(m).slice(1).join(' ') + ' sea ' + palabrasDe(m).slice(-1)[0], sub); if (c) cands = [c]; }
        }
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
    const delMain = (T.metodosDeMain || []).filter(x => colectorN && bajo(x.fn).includes(bajo(colectorN))).map(x => x.m);
    const metodosCol = col ? [...new Set(Object.keys(col.metodos).concat(delMain))].filter(m => m !== agregarN) : [];
    // los datos del colector («Del Hospital sólo interesa registrar la razón social»): los que recibe su constructor
    if (col && col.ctores.length) {
      const k = Math.max(...col.ctores.map(c => c.args.length));
      const ns = contrato[colectorN] ? contrato[colectorN].params.slice(0, k) : nombresDelTest(colectorN).slice(0, k);
      campos[colectorN] = Array.from({ length: k }, (_, j) => { const a = col.ctores[0].args[j]; return { n: ns[j] || (j ? 'dato' + (j + 1) : 'nombre'), tipo: a && a.k === 'num' ? (a.real ? 'float' : 'int') : a && a.k === 'bool' ? 'bool' : 'str' }; });
    } else if (col) campos[colectorN] = [];
    const paramsDe = m => { const ll = col && col.metodos[m] ? col.metodos[m].llamadas : []; return ll.length ? Math.max(...ll.map(x => x.args.length)) : 0; };
    // un renglón que nombra al método tal cual («- importe_promedio_atenciones: debe calcular…»)
    const exacto = {};
    const tituloExacto = (x, m) => { const mm = x.match(/^(?:[-*•]|\d+[.)])?\s*`?([A-Za-z_][\w]*)`?(?:\(\))?\s*:\s*(.+)$/); return mm && mm[1] === m; };
    for (const m of metodosCol) {
      const lineas = texto.split('\n').map(x => x.trim());
      const ex = lineas.find(x => tituloExacto(x, m));
      if (!ex && pedidos.some(p => parecido(m, p) >= 0.6)) continue;
      const ws = palabrasDe(m).filter(w => !VACIAS.has(w));
      const l = ex || lineas.find(x => { const mm = x.match(/^([^:]{3,60}):\s*(.+)$/); if (!mm) return false; const tw = bajo(mm[1]).split(/[^a-z0-9]+/); return ws.every(w => tw.some(t => t === w || singular(t) === singular(w) || t.startsWith(w.slice(0, 5)))); });
      if (l) {
        const ls2 = texto.split('\n').map(x => x.trim()), i0 = ls2.indexOf(l);
        let desc = l.match(/^([^:]{3,60}):\s*(.+)$/)[2];
        for (let i = i0 + 1; i < ls2.length; i++) { const x = ls2[i]; if (/^[A-ZÁÉÍÓÚ][^:.]{2,60}:\s/.test(x) || /^(?:[-*•]|\d+[.)])\s/.test(x) || /^#/.test(x)) break; if (!x) { if (/[.:]$/.test(desc)) break; continue; } desc += ' ' + x; }
        const pd = { titulo: l.match(/^([^:]{3,60}):/)[1].replace(/^(?:[-*•]|\d+[.)])\s*/, '').replace(/`/g, ''), desc, todo: l };
        pedidos.push(pd);
        if (ex) exacto[m] = pd;
      }
    }
    // a qué pedido corresponde cada método del test (por las palabras)
    const metCol = [];
    const usados = new Set();
    for (const m of Object.keys(exacto)) usados.add(exacto[m]);
    for (const m of metodosCol) {
      if (exacto[m]) { metCol.push({ n: m, pedido: exacto[m] }); continue; }
      const p = pedidos.map(p => [p, parecido(m, p)]).filter(([p]) => !usados.has(p)).sort((a, b) => b[1] - a[1])[0];
      if (p && p[1] > 0) { usados.add(p[0]); metCol.push({ n: m, pedido: p[0] }); } else metCol.push({ n: m, pedido: { titulo: m.replace(/_/g, ' '), desc: '' } });
    }
    for (const p of pedidos) if (!usados.has(p)) metCol.push({ n: snake(p.titulo.split(/\s+/).filter(w => !VACIAS.has(bajo(w))).join(' ')), pedido: p, sinTest: true });
    // qué hace cada uno
    const metodoCalc = nombresMet.filter(m => !/^(es|esta|tiene|puede)$/.test(palabrasDe(m)[0]) && !/^tipo$/.test(m));
    const calcDe = frase => { const f = bajo(frase); return metodoCalc.find(m => palabrasDe(m).some(w => w.length > 3 && f.includes(singular(w).slice(0, 6)))) || (/(total|suma|recaud|import|gast|alquiler|ganancia)/.test(f) ? metodoCalc[0] : null); };
    const subDe = frase => subsN.find(n => formasDe(n).some(fm => fm.length >= 4 && new RegExp('(^|[^a-z])' + fm).test(bajo(frase))));
    // «la suma de los importes de las consultas» es el dato importe; «el promedio de los importes a cobrar», el método
    const deClases = new Set(subsN.concat(componentes, [baseN]).flatMap(n => palabrasDe(n).concat(palabrasDe(n).map(plural))));
    const tocan = (ws, cw) => cw.filter(w => !VACIAS.has(w)).filter(w => ws.some(x => x === w || singular(x) === singular(w) || w.length >= 5 && x.startsWith(w.slice(0, 5)))).length;
    function queCuenta(frase, sub) {
      const ws = bajo(frase).split(/[^a-z0-9]+/).filter(w => w && !VACIAS.has(w) && !deClases.has(w));
      let mejor = null, pm = 0;
      for (const m of metodoCalc) { const p = tocan(ws, palabrasDe(m)); if (p > pm) { pm = p; mejor = MET(m); } }
      for (const c of todosCampos(sub || subsN[0]).filter(c => c.tipo === 'int' || c.tipo === 'float')) {
        const p = Math.max(tocan(ws, palabrasDe(c.n)), tocan(ws, bajo(c.etiqueta || '').split(/[^a-z0-9]+/)));
        if (p > pm && p >= 2) { pm = p; mejor = C(c.n); }
      }
      return mejor;
    }
    const booleanos = nombresMet.filter(m => /^(es|esta|tiene|puede)$/.test(palabrasDe(m)[0]));
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
      // «para un paciente habitual»: el método que dice si lo es (esPacienteHabitual)
      for (const mb of booleanos) {
        const ws = palabrasDe(mb).slice(1).filter(w => !VACIAS.has(w));
        if (!ws.length || filtro.some(x => x.e && x.e.n === mb) || !ws.every(w => new RegExp('(^|[^a-z])' + singular(w).slice(0, 6)).test(fd))) continue;
        const neg = new RegExp('\\bno\\s+(?:sea[n]?\\s+|es\\s+|son\\s+)?' + singular(ws.slice(-1)[0]).slice(0, 6)).test(fd);
        filtro.push(neg ? { t: 'no', e: MET(mb) } : { t: 'met', e: MET(mb) });
      }
      // «entre dos valores recibidos como parámetros»
      const np = paramsDe(mc.n);
      if (np >= 2 && /\bentre\b/.test(fd)) {
        const qq = (fd.match(/(?:cuyo|cuya|con)\s+([a-z ]+?)\s+(?:se\s+encuentre|este|esté|sea|quede)\w*\s+entre/) || [])[1];
        mc.params = ['minimo', 'maximo'];
        filtro.push({ t: 'entre', e: queCuenta(qq || fd, s) || (metodoCalc[0] ? MET(metodoCalc[0]) : null), a: 0, b: 1 });
      } else if (np) mc.params = Array.from({ length: np }, (_, j) => 'valor' + (j + 1));
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
      if (/\bpromedio\b/.test(f)) mc.tipo = 'promedio';
      // «el código de la primera atención … o 0 si no existe ninguna»
      if (/\bprimer[oa]?\b/.test(fd) && !mc.tipo) {
        mc.tipo = 'primero';
        const dv = (fd.match(/(?:retorn|devuelv|informe|mostr)\w*\s+(?:el|la)?\s*([a-z ]+?)\s+(?:del?|de\s+la)\s+(?:primer[oa]?)/) || [])[1];
        const c = dv ? campoDe(dv, s || subsN[0]) : null;
        mc.devuelve = c ? [c.n] : null;
        const sino = fd.match(/\bo\s+(-?\d+)\s+si\s+no\b/);
        mc.sino = sino ? N(num(sino[1])) : null;
      }
      // «atencionesMedicas()»: la lista de una sola subclase
      if (!mc.tipo && !mc.pedido.desc && s) { mc.tipo = 'lista'; }
      if (!mc.tipo) { const sl = subsN.find(n => palabrasDe(mc.n).map(singular).join(' ').includes(palabrasDe(n).map(singular).join(' '))); if (sl && !mc.pedido.desc) { mc.tipo = 'lista'; if (!filtro.length) filtro.push({ t: 'es', n: sl }); } }
      if (!mc.tipo) mc.tipo = 'suma';
      if (mc.tipo === 'suma' || mc.tipo === 'promedio') mc.expr = (() => {
        const tras = (f.match(/(?:suma|promedio|total)\s+de\s+(.*)$/) || [])[1];
        const q = tras ? queCuenta(tras.split(/\b(?:cuyo|cuya|que|entre|por\s+aquell)/)[0], s) : null;
        if (q) return q;
        const m = calcDe(f); return m ? MET(m) : null;
      })();
      mc.filtro = filtro;
    }

    const usaCol = new Set();
    for (const mc of metCol) { const sinEs = !(mc.filtro || []).some(f => f.t === 'es'); for (const x of [mc.expr, mc.clave, ...(mc.filtro || []).map(f => f.e)]) if (x && x.t === 'met' && sinEs) usaCol.add(x.n); }
    for (const m of nombresMet) {
      const en = subsN.filter(sb => metodosTest(sb).includes(m));
      if (en.length !== 1 || (T.metodosSueltos && T.metodosSueltos.has(m)) || usaCol.has(m) || auxiliares.some(a => JSON.stringify(a.ir).includes('"' + m + '"'))) continue;
      for (const sb of subsN) if (sb !== en[0] && !(metodosEnt[sb][m] || []).length) delete metodosEnt[sb][m];
    }
    // el texto de cada objeto si el test no da uno exacto: el nombre de la clase, sus datos y sus cuentas (con dos decimales)
    const legible = n => palabrasDe(n).map(capital).join(' ');
    const partesStr = n => {
      const ps = [{ lit: legible(n) + ' ' }];
      todosCampos(n).forEach((c, i) => { if (i) ps.push({ lit: ' - ' + palabrasDe(c.n).join(' ') + ': ' }); ps.push({ campo: c }); });
      for (const m of Object.keys(metodosEnt[n] || {}).filter(m => metodoCalc.includes(m))) ps.push({ lit: ' - ' + palabrasDe(m).join(' ') + ': ' }, { met: m });
      return ps;
    };
    const strPartes = Object.fromEntries(subsN.concat(componentes).map(n => [n, partesStr(n)]));

    // ── comprobar el modelo contra cada assert del test (sin Python) y elegir la lectura que cumple
    // la carpeta de los CSV: la que dice el enunciado («se encuentran en la carpeta data/») o la del ZIP
    const mc0 = enunciado && String(enunciado).match(/\bcarpeta\s+(?:`([A-Za-z_][\w-]*)\/?`|[“"']([A-Za-z_][\w-]*)\/?[”"']|([A-Za-z_][\w-]*)\/(?![\w]))/);
    const carpeta = carpetaCsv || (mc0 ? mc0[1] || mc0[2] || mc0[3] : null);
    const modelo = { baseN, subsN, componentes, campos, comunes, metodosEnt, auxiliares, colectorN: nColectorFinal, listaN, agregarN, metCol, strDe: {}, tipoDeSub, etiquetasTipo, sep, conEncabezado, csvPrincipal, csvs, unArchivo, modDe, textoCsv: csvT,
      etiquetas, validaciones, strPartes, mainUsa: Object.fromEntries(Object.entries(T.mainUsa).map(([f, us]) => [f, Math.max(0, ...us.map(u => u.args.length))])), variosCsv, csvDe, infoCsv, carpeta,
      llamadasCol: col ? Object.fromEntries(Object.entries(col.metodos).map(([m, x]) => [m, x.llamadas[0] ? x.llamadas[0].args.map(TestLee.texto) : []])) : {} };
    const elegido = {};   // sub.metodo → IR
    for (const sub of subsN) for (const m of Object.keys(metodosEnt[sub])) elegido[sub + '.' + m] = (metodosEnt[sub][m] || [])[0] || null;
    const valorCampo = (o, c) => {
      if (!o || o.k !== 'obj') return null;
      if (o.attrs && c in o.attrs) { const a = o.attrs[c]; return a.k === 'obj' ? a : a.k === 'num' || a.k === 'bool' || a.k === 'str' ? a.v : null; }
      if (!campos[o.clase]) return null;
      const i = campos[o.clase].findIndex(x => x.n === c);
      let a = o.args[i];
      if (a === undefined && i >= 0) a = campos[o.clase][i].defecto;
      return a ? (a.k === 'obj' ? a : a.k === 'num' || a.k === 'bool' || a.k === 'str' ? a.v : null) : null;
    };
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
        case 'de': return valorCampo(valorCampo(o, ir.obj), ir.n);
        case 'pasos': {
          let v = evalIR(ir.inicio, o);
          if (v == null) return undefined;
          for (const p of ir.pasos) { if (p.cond && !evalIR(p.cond, o)) continue; const x = evalIR(p.v, o); if (x == null) return undefined; v = p.op === '*' ? v * x : p.op === '-' ? v - x : v + x; }
          return v;
        }
        default: return undefined;
      }
    }
    function llamarMet(o, n) {
      if (elegido[o.clase + '.' + n] !== undefined) return evalIR(elegido[o.clase + '.' + n], o);
      const a = auxiliares.find(x => x.n === n); if (a) return evalIR(a.ir, o);
      return undefined;
    }
    function filtrar(lista, filtro, args) {
      const arg = i => valorPy((args || [])[i]);
      return lista.filter(o => filtro.every(f => f.t === 'es' ? o.clase === f.n : f.t === 'campo' ? !!valorCampo(o, f.n) : f.t === 'no' ? !evalIR(f.e, o) : f.t === 'met' ? !!evalIR(f.e, o) : f.t === 'entre' ? (v => v >= arg(f.a) && v <= arg(f.b))(evalIR(f.e, o)) : f.t === 'cmp' ? (f.op === '>' ? evalIR(f.e, o) > f.v : evalIR(f.e, o) < f.v) : true));
    }
    function llamarCol(o, mc, args) {
      const lista = filtrar(o.agregados, mc.filtro || [], args);
      if (mc.tipo === 'promedio') return lista.length ? lista.reduce((s, x) => s + (evalIR(mc.expr, x) || 0), 0) / lista.length : 0;
      if (mc.tipo === 'primero') return lista.length ? (mc.devuelve ? valorCampo(lista[0], mc.devuelve[0]) : lista[0]) : (mc.sino ? mc.sino.v : null);
      if (mc.tipo === 'lista') return { k: 'lista', items: lista };
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
        if (o.clase === colectorN) { const mc = metCol.find(x => x.n === v.n); return mc ? llamarCol(o, mc, v.args) : undefined; }
        return llamarMet(o, v.n);
      }
      if (v.op === 'attr') { const o = valorTest(v.obj); if (o && o.k === 'obj') { if (o.clase === colectorN && v.n === listaN) return { k: 'lista', items: o.agregados }; if (o.clase === colectorN) { const i = (campos[colectorN] || []).findIndex(c => c.n === v.n); return i >= 0 ? valorPy(o.args[i]) : undefined; } return valorCampo(o, v.n); } return undefined; }
      if (v.op === 'len') { const a = valorTest(v.a); return a && a.k === 'lista' ? a.items.length : undefined; }
      if (v.op === 'isinstance') { const o = valorTest(v.a); return o && o.k === 'obj' ? (o.clase === v.c || v.c === baseN) : undefined; }
      if (v.op === 'str') { const o = valorTest(v.a); return o && o.k === 'obj' && modelo.strDe[o.clase] ? modelo.strDe[o.clase](o) : undefined; }
      return undefined;
    }
    const igual = (a, b, approx) => {
      if (typeof a === 'number' && typeof b === 'number') return Math.abs(a - b) <= (approx ? Math.max(1e-6 * Math.abs(b), 1e-9) : 1e-9);
      // una lista del modelo contra una del test: los mismos objetos, en el mismo orden
      if (a && a.k === 'lista' && b && b.k === 'list') return a.items.length === b.items.length && a.items.every((x, i) => x === b.items[i]);
      return a === b;
    };
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
        } else if (a.op === 'in' || a.op === 'not in') {
          // «"900.00" in str(atencion)»
          const aguja = valorPy(a.a), pajar = valorTest(a.b);
          if (typeof aguja !== 'string' || typeof pajar !== 'string') continue;
          bien = pajar.includes(aguja); if (a.op === 'not in') bien = !bien;
        } else if (a.op === 'truthy' || a.op === 'falsy') { if (izq === undefined) continue; bien = a.op === 'truthy' ? !!izq : !izq; }
        else if (['>', '<', '>=', '<='].includes(a.op)) { const der = valorPy(a.b); if (izq === undefined || der == null) continue; bien = a.op === '>' ? izq > der : a.op === '<' ? izq < der : a.op === '>=' ? izq >= der : izq <= der; }
        else continue;
        total++; if (bien) ok++; else fallan.push(a);
      }
      return { ok, total, fallan };
    }
    // para cada método de cada subclase: la primera lectura que cumple sus asserts
    const assertDe = (sub, m) => a => a.a.k === 'sym' && a.a.op === 'call' && a.a.n === m && a.a.obj && a.a.obj.k === 'obj' && a.a.obj.clase === sub;
    for (const sub of subsN) for (const m of Object.keys(metodosEnt[sub])) {
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
    if (!modelo.strFmt) {
      const valorStr = (o, p) => {
        if (p.lit != null) return p.lit;
        if (p.met) { const v = llamarMet(o, p.met); return typeof v === 'number' ? v.toFixed(2) : String(v); }
        const c = p.campo, v = valorCampo(o, c.n);
        if (v && v.k === 'obj') return modelo.strDe[v.clase] ? modelo.strDe[v.clase](v) : '';
        if (c.etiquetas) return c.etiquetas[v] != null ? c.etiquetas[v] : String(v);
        if (c.tipo === 'bool') return v ? 'sí' : 'no';
        if (c.tipo === 'float' && typeof v === 'number') return v.toFixed(2);
        return String(v);
      };
      for (const n of Object.keys(strPartes)) modelo.strDe[n] = o => strPartes[n].map(p => valorStr(o, p)).join('');
      if (colectorN) modelo.strDe[colectorN] = o => [o.args[0] ? String(valorPy(o.args[0])) : colectorN].concat(o.agregados.map(x => modelo.strDe[x.clase] ? modelo.strDe[x.clase](x) : '')).join('\n');
    }
    const comprobacion = comprobar();
    if (comprobacion.total && comprobacion.ok < comprobacion.total) avisos.push(`El modelo no cumple ${comprobacion.total - comprobacion.ok} de las ${comprobacion.total} comprobaciones del test: revisá esos métodos.`);
    modelo.elegido = elegido;
    const archivos = escribir(modelo);
    return { archivos, avisos, carpetaCsv: carpeta, comprobacion: { ok: comprobacion.ok, total: comprobacion.total, fallan: comprobacion.fallan.map(a => `línea ${a.l}: ${TestLee.texto(a.a)} ${a.op} ${a.b ? TestLee.texto(a.b) : ''}`) }, modelo, test: T };
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
        case 'de': return `${yo}.${ir.obj}.${ir.n}`;
        default: return '0';
      }
    };
    // un método: una línea con el return o, si la cuenta va en pasos, cada paso con su if
    const cuerpoMetodo = (ir, sangria) => {
      if (!ir) return [sangria + 'return None  # no está en el enunciado: completalo'];
      if (ir.t !== 'pasos') return [sangria + 'return ' + py(ir)];
      const v = palabrasDe(ir.inicio.n || 'importe')[0] || 'importe', ls = [`${sangria}${v} = ${py(ir.inicio)}`];
      ir.pasos.forEach((p, i) => {
        const op = p.op === '*' ? '*=' : p.op === '-' ? '-=' : '+=';
        if (!p.cond) { ls.push(`${sangria}${v} ${op} ${py(p.v)}`); return; }
        const ant = ir.pasos[i - 1], mismo = ant && ant.cond && ant.cond.t === 'cmp' && p.cond.t === 'cmp' && JSON.stringify(ant.cond.a) === JSON.stringify(p.cond.a);
        ls.push(`${sangria}${mismo ? 'elif' : 'if'} ${py(p.cond)}:`, `${sangria}    ${v} ${op} ${py(p.v)}`);
      });
      ls.push(`${sangria}return ${v}`);
      return ls;
    };
    const prec = op => op === '+' || op === '-' ? 1 : 2;
    const metodosDe = sub => Object.keys(M.metodosEnt[sub] || {});
    const todosMet = [...new Set(M.subsN.flatMap(metodosDe))];
    // en la base, abstractos, solo los que tienen todas las subclases
    const abstractos = todosMet.filter(m => M.subsN.every(sb => metodosDe(sb).includes(m)));
    // «SINTOMAS = {1: "corazon", …}»: el nombre de cada valor, para mostrarlo
    const constante = c => { const ws = palabrasDe(c); ws[0] = plural(ws[0]); return ws.join('_').toUpperCase(); };
    const etiquetasDe = n => Object.entries((M.etiquetas || {})[n] || {});
    const constantesDe = n => etiquetasDe(n).map(([c, vals]) => `${constante(c)} = {${Object.entries(vals).map(([k, v]) => `${k}: ${JSON.stringify(v)}`).join(', ')}}`);
    const validar = n => ((M.validaciones || {})[n] || []).flatMap(v => v.valores
      ? [`        if ${v.campo} not in ${etiquetasDe(n).some(([c]) => c === v.campo) ? constante(v.campo) : '(' + v.valores.join(', ') + ')'}:`, `            raise ${v.exc}("${palabrasDe(v.campo).join(' ')} inválido: " + str(${v.campo}))`]
      : [`        if ${v.campo} < ${v.minimo}:`, `            raise ${v.exc}("${palabrasDe(v.campo).join(' ')} no puede ser negativo: " + str(${v.campo}))`]);
    const valorPyTxt = d => !d ? 'None' : d.k === 'bool' ? (d.v ? 'True' : 'False') : d.k === 'str' ? JSON.stringify(d.v) : d.k === 'num' ? String(d.v) : 'None';
    // los parámetros del constructor: los últimos que el test a veces no pasa llevan su valor por defecto
    const params = cs => { let desde = cs.length; while (desde > 0 && cs[desde - 1].defecto) desde--; return cs.map((c, j) => j >= desde ? `${c.n}=${valorPyTxt(c.defecto)}` : c.n); };
    const legible = n => palabrasDe(n).map(capital).join(' ');
    const strLegible = n => {
      const ps = (M.strPartes || {})[n];
      if (!ps) return null;
      const t = ps.map(p => {
        if (p.lit != null) return p.lit.replace(/[{}]/g, x => x + x);
        if (p.met) return `{self.${p.met}():.2f}`;
        const c = p.campo;
        if (c.etiquetas) return `{${constante(c.n)}.get(self.${c.n}, self.${c.n})}`;
        if (c.tipo === 'bool') return `{'sí' if self.${c.n} else 'no'}`;
        if (c.tipo === 'float') return `{self.${c.n}:.2f}`;
        return `{self.${c.n}}`;
      }).join('');
      return ['', '    def __str__(self):', `        return f"${t}"`];
    };
    const comunesN = M.comunes.map(c => c.n);
    const imports = new Set();
    const bloques = {};   // módulo → [texto]
    const modulo = n => M.unArchivo || M.modDe(n) || snake(n);
    const poner = (n, t) => { const m = modulo(n); (bloques[m] || (bloques[m] = [])).push({ n, t }); };
    const nombreLegible = n => n.replace(/_/g, ' ');
    // la base
    {
      const ls = ['from abc import ABC, abstractmethod', '', '', `class ${M.baseN}(ABC):`, `    def __init__(self, ${params(M.comunes).join(', ')}):`];
      ls.push(...validar(M.baseN));
      for (const c of comunesN) ls.push(`        self.${c} = ${c}`);
      if (!comunesN.length) ls[ls.length - 1] = '    def __init__(self):', ls.push('        pass');
      for (const m of abstractos) { ls.push('', '    @abstractmethod', `    def ${m}(self):`, `        """Cada tipo lo calcula a su manera (polimorfismo)."""`); }
      for (const a of M.auxiliares) ls.push('', `    def ${a.n}(self):`, `        return ${py(a.ir)}`);
      if (M.strFmt) ls.push('', '    def __str__(self):', `        return f"${M.strFmt.map(p => '{' + py(p) + '}').join(' ')}"`);
      else if (!M.strPartes) ls.push('', '    def __str__(self):', `        return f"{type(self).__name__}: ${comunesN.slice(0, 3).map(c => '{self.' + c + '}').join(' · ')}"`);
      poner(M.baseN, ls.join('\n'));
    }
    // las subclases
    for (const sub of M.subsN) {
      const pr = M.campos[sub].slice(M.comunes.length).map(c => c.n);
      const ls = [`class ${sub}(${M.baseN}):`, `    def __init__(self, ${params(M.campos[sub]).join(', ')}):`, `        super().__init__(${comunesN.join(', ')})`];
      ls.push(...validar(sub));
      for (const c of pr) ls.push(`        self.${c} = ${c}`);
      for (const m of metodosDe(sub)) ls.push('', `    def ${m}(self):`, ...cuerpoMetodo(M.elegido[sub + '.' + m], '        '));
      if (!M.strFmt) ls.push(...(strLegible(sub) || []));
      poner(sub, ls.join('\n'));
    }
    for (const n of M.componentes || []) {
      const cs = M.campos[n] || [];
      const ls = [`class ${n}:`, `    def __init__(self${cs.length ? ', ' + params(cs).join(', ') : ''}):`];
      ls.push(...validar(n));
      for (const c of cs) ls.push(`        self.${c.n} = ${c.n}`);
      if (!cs.length) ls.push('        pass');
      ls.push(...(strLegible(n) || []));
      poner(n, ls.join('\n'));
    }
    // la colección
    {
      const datosCol = (M.campos[M.colectorN] || []).map(c => c.n);
      const L = M.listaN, ls = [`class ${M.colectorN}:`, `    def __init__(self${datosCol.map(c => ', ' + c).join('')}):`, ...datosCol.map(c => `        self.${c} = ${c}`), `        self.${L} = []`, '', `    def ${M.agregarN}(self, ${snake(M.baseN)}):`, `        self.${L}.append(${snake(M.baseN)})`];
      const v = snake(M.baseN)[0];
      let mcAct = null;
      const cond = f => f.t === 'es' ? `isinstance(${v}, ${f.n})` : f.t === 'campo' ? `${v}.${f.n}` : f.t === 'no' ? `not ${py(f.e, v)}` : f.t === 'met' ? py(f.e, v) : f.t === 'entre' ? `${mcAct.params[f.a]} <= ${py(f.e, v)} <= ${mcAct.params[f.b]}` : f.t === 'cmp' ? `${py(f.e, v)} ${f.op} ${f.v}` : 'True';
      const donde = filtro => filtro.length ? ' if ' + filtro.map(cond).join(' and ') : '';
      for (const mc of M.metCol) {
        mcAct = mc;
        ls.push('', `    def ${mc.n}(self${(mc.params || []).map(x => ', ' + x).join('')}):`);
        const f = mc.filtro || [];
        if (mc.tipo === 'promedio') ls.push(`        valores = [${mc.expr ? py(mc.expr, v) : '0'} for ${v} in self.${L}${donde(f)}]`, '        if not valores:', '            return 0', '        return sum(valores) / len(valores)');
        else if (mc.tipo === 'primero') {
          ls.push(`        for ${v} in self.${L}:`);
          const ret = mc.devuelve ? `${v}.${mc.devuelve[0]}` : v;
          if (f.length) ls.push(`            if ${f.map(cond).join(' and ')}:`, `                return ${ret}`); else ls.push(`            return ${ret}`);
          ls.push(`        return ${mc.sino ? py(mc.sino) : 'None'}`);
        }
        else if (mc.tipo === 'lista') ls.push(`        return [${v} for ${v} in self.${L}${donde(f)}]`);
        else if (mc.tipo === 'suma') ls.push(`        return sum(${mc.expr ? py(mc.expr, v) : '0'} for ${v} in self.${L}${donde(f)})`);
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
      if (M.strPartes && !M.strFmt) ls.push('', '    def __str__(self):', `        lineas = [${datosCol.length ? `str(self.${datosCol[0]})` : JSON.stringify(M.colectorN)}]`, `        lineas += [str(${v}) for ${v} in self.${L}]`, '        return "\\n".join(lineas)');
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
    const rutaCsv = M.carpeta ? `os.path.join(os.path.dirname(os.path.abspath(__file__)), "${M.carpeta}", "${archivoCsv}")` : `"${archivoCsv}"`;
    const main = ['def main():', `    ${snake(M.colectorN)} = ${M.colectorN}()`, `    leer_${M.listaN}(${rutaCsv}, ${snake(M.colectorN)})`, `    print("Cantidad de ${M.listaN.replace(/_/g, ' ')}:", len(${snake(M.colectorN)}.${M.listaN}))`];
    for (const mc of M.metCol) main.push(`    print("${capital(nombreLegible(mc.pedido && mc.pedido.titulo ? bajo(mc.pedido.titulo) : mc.n)).replace(/"/g, '')}:", ${snake(M.colectorN)}.${mc.n}())`);
    main.push('', '', 'if __name__ == "__main__":', '    main()');
    // armar los archivos: uno solo (si el test importa todo de un módulo) o uno por clase
    const orden = [M.baseN, ...M.subsN, ...(M.componentes || []), M.colectorN];
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
      const cts = ns.flatMap(constantesDe);
      archivos[m + '.py'] = (top.length ? top.join('\n') + '\n\n' + (cts.length ? '' : '\n') : '') + (cts.length ? cts.join('\n') + '\n\n\n' : '') + cuerpo + '\n';
    }
    // el main va en el mismo archivo si es uno solo; si no, en main.py
    const usa = [...new Set([M.colectorN, ...M.subsN])];
    if (M.variosCsv || Object.keys(M.mainUsa || {}).length) { archivos['main.py'] = mainConFunciones(M, modulo); return archivos; }
    const conOs = M.carpeta ? 'import os\n\n' : '';
    if (M.unArchivo) archivos[M.unArchivo + '.py'] = archivos[M.unArchivo + '.py'].replace(/\n$/, '') + '\n\n\n' + lee.join('\n') + '\n\n\n' + main.join('\n') + '\n';
    else archivos['main.py'] = conOs + usa.map(n => `from ${modulo(n)} import ${n}`).sort().join('\n') + '\n\n\n' + lee.join('\n') + '\n\n\n' + main.join('\n') + '\n';
    return archivos;
  }

  // ───────── El main con una función por cosa que se carga (lo que pide el test o, si no, lo que hace falta)
  function mainConFunciones(M, modulo) {
    const mismo = (a, b) => a === b || a === b + 's' || b === a + 's' || a === plural(b) || b === plural(a) || singular(a) === singular(b);
    const igualNombre = (ws, n) => { const cw = palabrasDe(n); return ws.length === cw.length && ws.every((w, i) => mismo(w, cw[i])); };
    const fns = Object.keys(M.mainUsa || {});
    const resto = f => palabrasDe(f.replace(/^(cargar|leer|crear|armar|obtener|get|load)_?/i, ''));
    const clases = M.subsN.concat(M.componentes || []);
    const fnDe = n => fns.find(f => igualNombre(resto(f), n)) || 'cargar' + palabrasDe(n).map(w => capital(plural(w))).join('');
    const fnCol = fns.find(f => igualNombre(resto(f), M.colectorN)) || 'cargar' + M.colectorN;
    const fnBool = fns.find(f => /bool/i.test(f)) || 'aBooleano';
    const var_ = n => { const f = fns.find(f => igualNombre(resto(f), n)); if (f) { const r = f.replace(/^(cargar|leer|crear|armar|obtener|get|load)_?/i, ''); return r[0].toLowerCase() + r.slice(1); } return palabrasDe(n).map((w, i) => i ? capital(plural(w)) : plural(w)).join(''); };
    const posFn = n => { const i = fns.findIndex(f => igualNombre(resto(f), n)); return i < 0 ? 1e9 : i; };
    M = { ...M, subsN: M.subsN.slice().sort((a, b) => posFn(a) - posFn(b)) };
    const info = n => M.csvDe[n] ? M.infoCsv[M.csvDe[n]] : null;
    const conv = (c, x) => c.tipo === 'int' ? `int(${x})` : c.tipo === 'float' ? `float(${x})` : c.tipo === 'bool' ? `${fnBool}(${x})` : `${x}.strip()`;
    // la clase de adentro se carga en un diccionario por la columna que la une con la de afuera («codigo_atencion» ↔ «codigo»)
    const clave = {};
    for (const n of M.componentes || []) {
      const ic = info(n); if (!ic) continue;
      const usadas = new Set((M.campos[n] || []).map(c => c.col));
      const libres = ic.primera.map((h, i) => ({ h, i })).filter(x => !usadas.has(x.i));
      const duenios = M.subsN.filter(sb => (M.campos[sb] || []).some(c => c.tipo === 'obj' && c.clase === n));
      for (const sb of duenios) {
        const is = info(sb); if (!is) continue;
        let mejor = null;
        for (const l of libres) for (const [j, h] of is.primera.entries()) { const p = palabrasDe(l.h).filter(w => palabrasDe(h).some(x => mismo(x, w))).length; if (p && (!mejor || p > mejor.p)) mejor = { p, i: l.i, j }; }
        if (mejor) { clave[n] = { i: mejor.i, tipo: /^-?\d+$/.test((ic.filas[0] || [])[mejor.i] || '') ? 'int' : 'str' }; clave[sb + '>' + n] = mejor.j; }
      }
    }
    const ls = ['import os', ''];
    const imp = {};
    for (const n of clases.concat([M.colectorN])) (imp[modulo(n)] || (imp[modulo(n)] = [])).push(n);
    ls.push(...Object.keys(imp).sort().map(m => `from ${m} import ${imp[m].sort().join(', ')}`), '');
    ls.push(M.carpeta ? `CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "${M.carpeta}")` : 'CARPETA = os.path.dirname(os.path.abspath(__file__))', '', '');
    ls.push(`def ${fnBool}(texto):`, '    return str(texto).strip().lower() in ("true", "1", "si", "sí", "verdadero")', '', '');
    ls.push('def leerFilas(nombre, separador=",", conTitulos=True):', '    with open(os.path.join(CARPETA, nombre), encoding="utf-8") as archivo:', '        filas = [linea.strip().split(separador) for linea in archivo if linea.strip()]', '    return filas[1:] if conTitulos else filas', '', '');
    const cargables = clases.filter(n => info(n));
    const orden = (M.componentes || []).filter(n => info(n)).concat(M.subsN.filter(n => info(n)));
    const recibe = n => (M.campos[n] || []).filter(c => c.tipo === 'obj' && clave[c.clase]).map(c => c.clase);
    for (const n of orden) {
      const ic = info(n), lee = `leerFilas("${ic.n}"${ic.sep !== ',' ? `, "${ic.sep}"` : ''}${ic.conEncabezado ? '' : ', conTitulos=False'})`;
      const pide = recibe(n), conParam = M.mainUsa[fnDe(n)] > 0;
      ls.push(`def ${fnDe(n)}(${conParam ? pide.map(var_).join(', ') : ''}):`);
      if (!conParam) for (const c of pide) ls.push(`    ${var_(c)} = ${fnDe(c)}()`);
      const args = (M.campos[n] || []).map(c => c.tipo === 'obj' ? (clave[c.clase] ? `${var_(c.clase)}[${clave[c.clase].tipo === 'int' ? `int(datos[${clave[n + '>' + c.clase]}])` : `datos[${clave[n + '>' + c.clase]}].strip()`}]` : 'None') : c.col == null ? valorPyTxtM(c.defecto) : conv(c, `datos[${c.col}]`));
      const obj = `${n}(${args.join(', ')})`;
      if (clave[n]) {
        const k = clave[n].tipo === 'int' ? `int(datos[${clave[n].i}])` : `datos[${clave[n].i}].strip()`;
        ls.push(`    ${var_(n)} = {}`, `    for datos in ${lee}:`, `        ${var_(n)}[${k}] = ${obj}`, `    return ${var_(n)}`, '', '');
      } else ls.push(`    ${var_(n)} = []`, `    for datos in ${lee}:`, `        ${var_(n)}.append(${obj})`, `    return ${var_(n)}`, '', '');
    }
    // el colector: con sus datos (de ejemplo: el nombre de la clase) y todo lo cargado
    const vc = snake(M.colectorN), datosCol = M.campos[M.colectorN] || [];
    ls.push(`def ${fnCol}():`, `    ${vc} = ${M.colectorN}(${datosCol.map(c => c.tipo === 'str' ? JSON.stringify(M.colectorN) : c.tipo === 'bool' ? 'False' : '0').join(', ')})`);
    const cargados = new Set();
    for (const n of M.subsN.filter(n => info(n))) for (const c of recibe(n)) if (!cargados.has(c) && M.mainUsa[fnDe(n)] > 0) { ls.push(`    ${var_(c)} = ${fnDe(c)}()`); cargados.add(c); }
    for (const n of M.subsN.filter(n => info(n))) ls.push(`    for ${snake(M.baseN)} in ${fnDe(n)}(${M.mainUsa[fnDe(n)] > 0 ? recibe(n).map(var_).join(', ') : ''}):`, `        ${vc}.${M.agregarN}(${snake(M.baseN)})`);
    ls.push(`    return ${vc}`, '', '');
    // lo que la función principal muestra: los métodos pedidos (los que reciben valores, con los del test, de ejemplo)
    ls.push('def main():', `    ${vc} = ${fnCol}()`, `    print("Cantidad de ${palabrasDe(M.listaN).join(' ')}:", len(${vc}.${M.listaN}))`);
    for (const mc of M.metCol) {
      if (mc.tipo === 'lista') continue;
      const ej = (M.llamadasCol || {})[mc.n] || [];
      const args = (mc.params || []).map((x, i) => ej[i] || '0').join(', ');
      ls.push(`    print("${capital(bajo(mc.pedido && mc.pedido.titulo ? mc.pedido.titulo : mc.n).replace(/_/g, ' ').replace(/"/g, ''))}:", ${vc}.${mc.n}(${args}))${args ? '   # valores de ejemplo' : ''}`);
    }
    ls.push('', '', 'if __name__ == "__main__":', '    main()', '');
    void cargables;
    return ls.join('\n');
  }
  const valorPyTxtM = d => !d ? 'None' : d.k === 'bool' ? (d.v ? 'True' : 'False') : d.k === 'str' ? JSON.stringify(d.v) : d.k === 'num' ? String(d.v) : 'None';

  return { resolver, limpiar, items };
});
