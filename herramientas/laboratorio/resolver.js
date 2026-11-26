/* La solución de un parcial cualquiera: toma el código del preenunciado, el enunciado del parcial y su CSV, y devuelve
   el proyecto con los cambios hechos (como la solución automática de Flota, pero para cualquier preenunciado).
   Lo que hay que cambiar sale del análisis de guia.js (el enunciado, los datos y el código; nunca los tests); acá se
   aplica sobre el código, respetando su forma: el mismo estilo de llaves, los mismos nombres, la misma sangría.
   Lo que el enunciado pide y no se pudo armar solo queda en «avisos».
   Uso: Resolver.resolver({ fuentes }, textoDelEnunciado, csvDelParcial) → { fuentes, nuevos, avisos, hecho, plan } */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica(require('./guia.js'));
  else raiz.Resolver = fabrica(raiz.Guia);
})(typeof self !== 'undefined' ? self : this, function (Guia) {
  'use strict';
  const sinTildes = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '');
  const bajo = s => sinTildes(s).toLowerCase();
  const capital = s => s ? s[0].toUpperCase() + s.slice(1) : s;
  const camel = s => s.replace(/_(\w)/g, (_, x) => x.toUpperCase());
  const pascal = s => String(s).toLowerCase().split(/[_\s]+/).filter(Boolean).map(capital).join('');
  const escRe = s => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const nombreDe = r => r.split('/').pop();
  const sangria = l => (l.match(/^[ \t]*/) || [''])[0];
  const limpio = l => l.replace(/"(?:[^"\\]|\\.)*"/g, '""').replace(/'(?:[^'\\]|\\.)*'/g, "''").replace(/\/\/.*$/, '');
  const num = s => Number(String(s).replace(/[._](?=\d{3}\b)/g, '').replace(',', '.'));

  // ── Herramientas sobre las líneas de un archivo
  function profundidad(ls, i) { let d = 0; for (let k = 0; k < i; k++) for (const ch of limpio(ls[k])) { if (ch === '{') d++; else if (ch === '}') d--; } return d; }
  function cierre(ls, i) {   // la línea de la llave que cierra el bloque que abre la línea i
    let d = 0, abrio = false;
    for (let k = i; k < ls.length; k++) for (const ch of limpio(ls[k])) { if (ch === '{') { d++; abrio = true; } else if (ch === '}') { d--; if (abrio && d === 0) return k; } }
    return -1;
  }
  function finSentencia(ls, i) {   // la línea donde termina la sentencia que empieza en i (paréntesis parejos y ; o {)
    let p = 0;
    for (let k = i; k < ls.length; k++) { for (const ch of limpio(ls[k])) { if (ch === '(') p++; else if (ch === ')') p--; } if (p <= 0 && /[;{]\s*$/.test(limpio(ls[k]))) return k; }
    return i;
  }
  // lo que está entre el paréntesis que abre en «desde» (índice en el texto) y el que lo cierra
  function entreParentesis(t, desde) {
    let p = 0;
    for (let k = desde; k < t.length; k++) { if (t[k] === '(') p++; else if (t[k] === ')') { p--; if (p === 0) return { ini: desde + 1, fin: k }; } else if (t[k] === '"') { k++; while (k < t.length && t[k] !== '"') { if (t[k] === '\\') k++; k++; } } }
    return null;
  }
  const cierreClase = ls => { for (let k = ls.length - 1; k >= 0; k--) if (/^\s*}\s*$/.test(ls[k])) return k; return ls.length; };
  function agregarImports(t, imps) {
    const ls = t.split('\n');
    const faltan = imps.filter(x => !new RegExp('^\\s*import\\s+' + escRe(x) + '\\s*;', 'm').test(t) && !new RegExp('^\\s*import\\s+' + escRe(x.replace(/\.\w+$/, '')) + '\\.\\*\\s*;', 'm').test(t));
    if (!faltan.length) return t;
    let k = -1;
    ls.forEach((l, i) => { if (/^\s*import\s/.test(l)) k = i; });
    if (k < 0) { k = ls.findIndex(l => /^\s*package\s/.test(l)); ls.splice(k + 1, 0, ''); k++; }
    ls.splice(k + 1, 0, ...faltan.map(x => 'import ' + x + ';'));
    return ls.join('\n');
  }
  const unaLinea = s => s.replace(/\s*\n\s*/g, ' ').replace(/\s+/g, ' ').trim();

  function resolver(proyecto, texto, csv) {
    const g = Guia.armar(proyecto, texto, csv);
    const c = g.codigo, plan = g.plan;
    const fuentes = { ...proyecto.fuentes }, nuevos = [], avisos = [], hecho = [];
    if (!plan || !c.enc || !g.encabezadoNuevo) {
      if (texto && texto.trim()) avisos.push('No encontré en el enunciado un encabezado nuevo para el CSV: el resto de los cambios no los puedo armar solo.');
      return { fuentes, nuevos, avisos, hecho, plan, guia: g };
    }
    const E = c.entidad, N = c.viejos.length, nuevo = g.encabezadoNuevo, M = nuevo.split(plan.sepN).length;
    // las subclases que valen la pena: la que decide un dato (no «una por formato»: ese dato va en la entidad)
    const columnas = g.columnas, subs = plan.clasesNuevas.filter(x => x.padre === E && !x.porFormato && (!x.opcional || x.cuenta));
    const enSub = new Set(subs.flatMap(x => (x.propios || []).map(y => y.col)));
    const laDiceLaClase = new Set(subs.filter(x => x.col && x.col.tipo === 'String' && !x.col.presencia).map(x => x.col.col));
    const enBase = columnas.filter(k => !enSub.has(k.col) && !laDiceLaClase.has(k.col));
    // un dato viejo que el objeto no guarda y ahora hace falta (contar por estado, el total de un estado): también se guarda
    const idxEstado0 = c.viejos.findIndex(h => /estado|status/i.test(h));
    const necesita = new Set();
    if (plan.conteo && plan.conteo.col && !c.getter(plan.conteo.col) && c.viejos.includes(plan.conteo.col)) necesita.add(plan.conteo.col);
    if (idxEstado0 >= 0 && !c.getter(c.viejos[idxEstado0]) && plan.requerido.some(t => /total\s+de\s+(?:las?\s+|los?\s+)?\w+\s+[A-Z][A-Z0-9_]+/.test(t))) necesita.add(c.viejos[idxEstado0]);
    for (const col of necesita) { const i = c.viejos.indexOf(col); enBase.push({ col, i, tipo: 'String', porDefecto: null, leer: `campos[${i}].strip()`, valores: [], soloEstados: [], sintetica: true }); }
    const getterDe = col => c.getter(col) || (enBase.some(k => k.col === col) ? 'get' + capital(camel(col)) : null);
    const cambiar = (ruta, f) => { if (ruta && fuentes[ruta] != null) fuentes[ruta] = f(fuentes[ruta]); };
    const idxEstado = c.viejos.findIndex(h => /estado|status/i.test(h));
    const tipoCalc = plan.calc ? plan.calc.tipo : 'double';
    const lit = k => k.tipo === 'String' ? `"${k.porDefecto == null ? '' : k.porDefecto}"` : String(k.porDefecto == null ? 0 : k.porDefecto);
    const condFuera = (v, r) => [r.min != null && `${v} < ${r.min}`, r.minEx != null && `${v} <= ${r.minEx}`, r.max != null && `${v} > ${r.max}`, r.maxEx != null && `${v} >= ${r.maxEx}`].filter(Boolean).join(' || ');

    // ── 1) El parser: los dos encabezados con «largo», el ancho de cada fila, estados nuevos y descartes
    const P = c.enc.archivo;
    cambiar(P, t => {
      let ls = t.split('\n');
      const k = c.enc.texto.match(/(\w+)\s*=\s*"/), esConst = !!(k && /\bstatic\b|\bfinal\b/.test(c.enc.texto));
      const K = esConst ? k[1] : `"${c.enc.valor}"`;
      let K2 = `"${nuevo}"`;
      if (esConst) {
        const i = ls.findIndex(l => l.includes('"' + c.enc.valor + '"'));
        K2 = /CABECERA|ENCABEZADO|HEADER/i.test(K) ? K.replace(/(_[A-Z]+)?$/, m => (m || '') + '_NUEVA').replace(/_[A-Z]+_NUEVA$/, '_NUEVA') : K + '_NUEVA';
        if (K2 === K) K2 = K + '_NUEVA';
        const sufijo = nuevo.startsWith(c.enc.valor) ? `${K} + "${nuevo.slice(c.enc.valor.length)}"` : `"${nuevo}"`;
        ls.splice(i + 1, 0, `${sangria(ls[i])}private static final String ${K2} = ${sufijo};`);
      }
      const h = ls.findIndex(l => /\bif\s*\(\s*!/.test(l) && l.includes(K + '.equals('));
      if (h < 0) { avisos.push(`No encontré dónde ${nombreDe(P)} controla el encabezado: ahí hay que aceptar también el nuevo.`); return t; }
      const I = sangria(ls[h]);
      const pe = entreParentesis(ls[h], ls[h].indexOf(K + '.equals(') + (K + '.equals').length);
      const arg = ls[h].slice(pe.ini, pe.fin).trim();
      const resto = ls[h].slice(ls[h].indexOf(')', pe.fin + 1) + 1).trim();   // lo que viene después de «if (…)»
      let v = arg;
      const antes = [];
      if (/readLine\(\)|nextLine\(\)/.test(arg)) { antes.push(`${I}String encabezado = ${arg};`); v = 'encabezado'; }
      const cuerpo = [`${I}if (${K}.equals(${v})) {`, `${I}    largo = ${N};`, `${I}} else if (${K2}.equals(${v})) {`, `${I}    largo = ${M};`];
      if (resto === '{') cuerpo.push(`${I}} else {`);
      else if (resto) cuerpo.push(`${I}} else {`, `${I}    ${resto}`, `${I}}`);
      else { const e = finSentencia(ls, h + 1); ls.splice(e + 1, 0, `${I}}`); cuerpo.push(`${I}} else {`); }
      // «int largo» a la altura del ciclo que lee las filas (así se ve adentro del while)
      const w = ls.findIndex((l, i) => i > h && /\bwhile\s*\(/.test(l));
      const dw = w >= 0 ? profundidad(ls, w) : profundidad(ls, h);
      let d = h;
      while (d > 0 && profundidad(ls, d) > dw) d--;
      if (d === h) ls.splice(h, 1, ...antes, `${I}int largo;`, ...cuerpo);
      else { ls.splice(h, 1, ...antes, ...cuerpo); ls.splice(d, 0, `${sangria(ls[d])}int largo = ${N};`); }
      // el ancho de cada fila
      const ks = [String(N)];
      ls.forEach(l => { const m = l.match(new RegExp('static\\s+final\\s+int\\s+(\\w+)\\s*=\\s*' + N + '\\s*;')); if (m) ks.push(m[1]); });
      const reAncho = new RegExp('([\\w\\]\\[.]+\\.length)\\s*!=\\s*(?:' + ks.join('|') + ')\\b');
      ls = ls.map(l => reAncho.test(l) ? l.replace(reAncho, (_, x) => plan.mixto ? `(largo == ${N} ? ${x} != ${N} : ${x} != ${N} && ${x} != ${M})` : `${x} != largo`) : l);
      // estados nuevos y descartes nuevos
      const validos = new Set(c.estados.filter(e => e.archivo === P && !c.descartes.some(d => d.valor === e.valor)).map(e => e.valor));
      for (const w of plan.estadosNuevos) {
        let ok = false;
        for (let i = 0; i < ls.length && !ok; i++) {
          const l = ls[i];
          if (![...validos].some(s => l.includes('"' + s + '"'))) continue;
          const negs = [...l.matchAll(/!\s*([\w\][.()]+?)\.equals\(\s*"([A-Z][A-Z0-9_]*)"\s*\)/g)].filter(m => validos.has(m[2]));
          if (negs.length) { const m = negs[negs.length - 1]; const p = m.index + m[0].length; ls[i] = l.slice(0, p) + ` && !${m[1]}.equals("${w}")` + l.slice(p); ok = true; continue; }
          const de = l.match(/(?:List|Set)\.of\(([^)]*)\)/);
          if (de && [...validos].some(s => de[1].includes('"' + s + '"'))) { const p = l.indexOf(de[0]) + de[0].length - 1; ls[i] = l.slice(0, p) + `, "${w}"` + l.slice(p); ok = true; continue; }
          const pos = [...l.matchAll(/([\w\][.()]+?)\.equals\(\s*"([A-Z][A-Z0-9_]*)"\s*\)/g)].filter(m => validos.has(m[2]));
          if (pos.length && /\|\|/.test(l)) { const m = pos[pos.length - 1]; const p = m.index + m[0].length; ls[i] = l.slice(0, p) + ` || ${m[1]}.equals("${w}")` + l.slice(p); ok = true; }
        }
        if (ok) hecho.push({ que: 'estado', valor: w }); else avisos.push(`El estado ${w} pasa a ser válido: no encontré en ${nombreDe(P)} la línea que valida los estados.`);
      }
      for (const w of plan.descartesNuevos) {
        const d0 = c.descartes.find(d => d.archivo === P);
        const i = d0 ? ls.findIndex(l => l.includes('"' + d0.valor + '"') && /equals/.test(l)) : -1;
        if (i < 0) { avisos.push(`Hay que descartar ${w}: no encontré el descarte que ya existe para sumarlo.`); continue; }
        ls[i] = ls[i].replace(new RegExp('([\\w\\][.()]+?)\\.equals(?:IgnoreCase)?\\(\\s*"' + escRe(d0.valor) + '"\\s*\\)'), m => `(${m} || ${m.replace(/\.equals(IgnoreCase)?\(\s*"[^"]*"\s*\)/, `.equals("${w}")`)})`);
        hecho.push({ que: 'descarte', valor: w });
      }
      hecho.push({ que: 'encabezado', N, M, mixto: plan.mixto });
      return ls.join('\n');
    });

    // ── 2) La entidad: el ancho en la fábrica, las columnas nuevas, los datos nuevos y quién se crea
    const A = c.archivoEntidad;
    const extras = enBase.map(k => ({ tipo: k.tipo, nombre: camel(k.col), k }));
    cambiar(A, t => {
      let ls = t.split('\n');
      // el ancho en la fábrica (si controla «!= N»)
      ls = ls.map(l => { const m = l.match(new RegExp('([\\w\\]\\[.]+\\.length)\\s*!=\\s*' + N + '\\b')); return m ? l.replace(m[0], `${m[1]} != ${N} && ${m[1]} != ${M}`) : l; });
      // la fábrica
      const f = c.fabrica ? ls.findIndex(l => c.fabrica.metodo ? new RegExp('static\\s+\\w+(?:<[^>]*>)?\\s+' + c.fabrica.metodo + '\\s*\\(').test(l) : false) : -1;
      if (f < 0) { avisos.push(`No encontré en ${E} el método que arma el objeto desde los campos (desdeCampos o parecido): las columnas nuevas hay que leerlas ahí.`); return ls.join('\n'); }
      const arr = (ls[f].match(/String\s*\[\s*\]\s*(\w+)/) || [])[1] || 'campos';
      const fin = cierre(ls, f);
      let r = -1;
      for (let i = fin; i > f; i--) if (new RegExp('\\bnew\\s+' + E + '\\s*\\(').test(ls[i])) { r = i; break; }
      if (r < 0) { avisos.push(`No encontré dónde ${c.fabrica.metodo} crea el ${E}.`); return ls.join('\n'); }
      // la sentencia que crea el objeto (puede ocupar varias líneas)
      let ini = r; while (ini > f + 1 && !/[;{}]\s*$/.test(limpio(ls[ini - 1]))) ini--;
      const finR = finSentencia(ls, ini);
      const sent = ls.slice(ini, finR + 1).join('\n');
      const pNew = sent.search(new RegExp('\\bnew\\s+' + E + '\\s*\\('));
      const par = entreParentesis(sent, sent.indexOf('(', pNew));
      const args = unaLinea(sent.slice(par.ini, par.fin));
      const I = sangria(ls[ini]);
      // leer y validar cada columna nueva
      const lee = [];
      const estadoExpr = idxEstado >= 0 ? `${arr}[${idxEstado}].strip()` : null;
      for (const k of columnas) {
        const v = camel(k.col), leer = k.leer.replace(/\bcampos\[/g, arr + '[');
        let cond = null;
        if (k.presencia) { lee.push(`boolean tiene${capital(v)} = ${arr}.length > ${k.i} && !${arr}[${k.i}].isBlank();`, `${k.tipo} ${v} = tiene${capital(v)} ? ${leer} : 0;`); }
        else lee.push(`${k.tipo} ${v} = ${arr}.length > ${k.i} ? ${leer} : ${lit(k)};`);
        if (k.esTexto && k.valores.length) cond = k.valores.map(x => `!${v}.equals("${x}")`).join(' && ');
        else if (k.numeros && k.numeros.length) cond = k.numeros.map(x => `${v} != ${x}`).join(' && ');
        else if (k.regla) cond = condFuera(v, k.regla);
        if (cond && k.presencia) cond = `tiene${capital(v)} && (${cond})`;
        if (cond && k.soloEstados.length && estadoExpr) cond = `(${k.soloEstados.map(s => `${estadoExpr}.equals("${s}")`).join(' || ')}) && (${cond})`;
        if (cond) lee.push(`if (${cond}) {`, `    throw new IllegalArgumentException("${k.col} inválido: " + ${v});`, `}`);
        if (k.esTexto && k.valores.length) for (const o of plan.oraciones) {
          const so = o.match(/\b([A-Z][A-Z0-9_]+)\s+solo\s+adm\w*\s+([A-Z][A-Z0-9_]+(?:\s*(?:,|\bo\b|\by\b)\s*[A-Z][A-Z0-9_]+)*)/);
          if (so && estadoExpr && !k.valores.includes(so[1])) {
            const vs = so[2].split(/\s*(?:,|\bo\b|\by\b)\s*/).filter(x => k.valores.includes(x));
            if (vs.length) { lee.push(`if (${arr}.length > ${N} && ${estadoExpr}.equals("${so[1]}") && ${vs.map(x => `!${v}.equals("${x}")`).join(' && ')}) {`, `    throw new IllegalArgumentException("${so[1]} solo admite ${vs.join(' o ')}");`, `}`); hecho.push({ que: 'regla', texto: `${so[1]} solo admite ${vs.join(' o ')}` }); }
          }
          const val = o.replace(/\s+[A-Z][a-záéíóú]+\s.*$/, '').match(/^([A-Z][A-Z0-9_]+)\s+se\s+consideran?\b.*?\bvalid\w*\s+si\s+(.+?)\.?$/i);
          if (val && k.valores.includes(val[1])) {
            const conds = bajo(val[2]).split(/\s+y\s+/).map(x => condicionDe(x, arr)).filter(Boolean);
            if (conds.length) { lee.push(`if (${v}.equals("${val[1]}") && !(${conds.join(' && ')})) {`, `    throw new IllegalArgumentException("${val[1]} no cumple: ${val[2].replace(/"/g, '')}");`, `}`); hecho.push({ que: 'regla', texto: `${val[1]} solo vale si ${val[2]}` }); }
            else avisos.push(`No pude armar sola la regla «${o.slice(0, 160)}».`);
          }
        }
        hecho.push({ que: 'columna', k });
      }
      const cuerpoFab = ls.slice(f, fin + 1).join('\n');
      for (const k of enBase.filter(k => k.sintetica)) {
        const v = camel(k.col);
        if (!new RegExp('\\b[\\w<>\\[\\]]+\\s+' + v + '\\s*=').test(cuerpoFab)) lee.push(`String ${v} = ${arr}[${k.i}].strip();`);
      }
      // la columna de estado que el código no valida (el enunciado dice cuáles valen y que un estado desconocido invalida la fila)
      if (estadoExpr && /estado\s+(?:es\s+un\s+valor\s+)?desconocido|estado\s+invalido/.test(bajo(plan.oraciones.join(' ')))) {
        const todo = Object.values(fuentes).join('\n');
        const valida = new RegExp('\\[\\s*' + idxEstado + '\\s*\\]\\s*\\)?\\s*(?:\\.strip\\(\\)\\s*)?\\.equals|contains\\(\\s*\\w+\\s*\\[\\s*' + idxEstado + '\\s*\\]').test(todo);
        const deTexto = new Set();
        for (const o of plan.oraciones) {
          const m = o.match(/[Pp]ara\s+(?:las\s+)?(?:filas|solicitudes|registros)\s+(?:con\s+(?:el|los)\s+estados?\s+)?([A-Z][A-Z0-9_]+(?:(?:\s*,\s*|\s+[yo]\s+)[A-Z][A-Z0-9_]+)*)/);
          if (m) m[1].split(/\s*,\s*|\s+[yo]\s+/).forEach(w => deTexto.add(w));
          const so = o.match(/\b(?:filas|solicitud(?:es)?|registros?)\s+([A-Z][A-Z0-9_]+)\s+solo\s+adm/); if (so) deTexto.add(so[1]);
        }
        for (const w of plan.estadosNuevos) deTexto.add(w);
        if (!valida && deTexto.size >= 2) {
          lee.unshift(`if (${arr}.length > ${N} && !${[...deTexto].map(w => `${estadoExpr}.equals("${w}")`).join(' && !')}) {`, `    throw new IllegalArgumentException("estado desconocido: " + ${estadoExpr});`, `}`);
          hecho.push({ que: 'regla', texto: `el estado tiene que ser ${[...deTexto].join(', ')}` });
        }
      }
      // quién se crea: la subclase según el dato que decide, o el de siempre con los datos nuevos
      const crea = [];
      const masBase = extras.map(x => x.nombre);
      for (const x of subs) {
        const kc = x.col;
        let cond = null;
        if (kc && kc.presencia) cond = 'tiene' + capital(camel(kc.col));
        else if (kc && kc.normal !== undefined && kc.valores.length) { const otros = kc.valores.filter(v => v !== kc.normal); cond = kc.tipo === 'String' ? (otros.length === 1 ? `${camel(kc.col)}.equals("${otros[0]}")` : `!${camel(kc.col)}.equals("${kc.normal}")`) : `${camel(kc.col)} != ${kc.normal}`; }
        else if (kc && kc.tipo !== 'String' && kc.normal !== undefined) cond = `${camel(kc.col)} != ${kc.normal}`;
        if (!cond) { avisos.push(`La clase ${x.nombre}: no encontré qué dato decide cuándo crearla.`); continue; }
        const propios = (x.propios || []).map(y => camel(y.col));
        crea.push(`if (${cond}) {`, `    return new ${x.nombre}(${[args, ...masBase, ...propios].join(', ')});`, `}`);
      }
      // los datos nuevos que guarda el de siempre van al final de su «new»
      let sentNueva = sent;
      if (masBase.length) sentNueva = sent.slice(0, par.fin) + ', ' + masBase.join(', ') + sent.slice(par.fin);
      ls.splice(ini, finR - ini + 1, ...lee.map(x => I + x), ...crea.map(x => I + x), ...sentNueva.split('\n'));
      // el constructor: uno nuevo con los datos nuevos; el de antes lo llama con los valores de siempre (así los tests viejos compilan)
      if (extras.length && c.ctor && !c.esRecord) {
        const ci = ls.findIndex(l => new RegExp('^\\s*(?:public|protected|private)?\\s*' + E + '\\s*\\(').test(l) && !/\bnew\b/.test(l));
        if (ci >= 0) {
          const se = ls.findIndex((l, i) => i >= ci && /\{\s*$/.test(limpio(l)));
          const firma = ls.slice(ci, se + 1).join('\n');
          const pp = entreParentesis(firma, firma.indexOf('('));
          const params = unaLinea(firma.slice(pp.ini, pp.fin));
          const mod = (ls[ci].match(/^\s*((?:public|protected|private)\s+)?/) || ['', ''])[1] || '';
          const J = sangria(ls[ci]);
          const nombres = c.ctor.params.map(p => p.nombre);
          const firmaNueva = firma.slice(0, pp.fin) + ', ' + extras.map(x => x.tipo + ' ' + x.nombre).join(', ') + firma.slice(pp.fin);
          const fc = cierre(ls, ci);
          let ua = -1; for (let i = se; i < fc; i++) if (/^\s*this\.\w+\s*=/.test(ls[i])) ua = i;
          const K2 = ua >= 0 ? sangria(ls[ua]) : J + '    ';
          ls.splice(ua >= 0 ? ua + 1 : fc, 0, ...extras.map(x => `${K2}this.${x.nombre} = ${x.nombre};`));
          ls.splice(ci, se - ci + 1, `${J}${mod}${E}(${params}) {`, `${J}    this(${nombres.concat(extras.map(x => lit(x.k))).join(', ')});`, `${J}}`, '', ...firmaNueva.split('\n'));
          // los campos
          let uc = -1; ls.forEach((l, i) => { if (/^\s*(?:private|protected)\s+(?!static)(?:final\s+)?[\w<>[\], ]+\s+\w+\s*;/.test(l)) uc = i; });
          if (uc >= 0) ls.splice(uc + 1, 0, ...extras.map(x => `${sangria(ls[uc])}private final ${x.tipo} ${x.nombre};`));
          hecho.push({ que: 'datos', extras: extras.map(x => x.nombre) });
        }
      }
      // los getters de los datos nuevos (y el del dato que dice la clase, si se cuenta por él)
      const J = sangria(ls.find(l => /^\s+(public|private|protected)\s/.test(l) && !/\bclass\b/.test(l)) || '    ');
      const getters = [];
      for (const x of extras) if (!new RegExp('\\bget' + capital(x.nombre) + '\\s*\\(').test(ls.join('\n'))) getters.push('', `${J}public ${x.tipo} get${capital(x.nombre)}() {`, `${J}    return ${x.nombre};`, `${J}}`);
      const cont = plan.conteo;
      if (cont && cont.sub && cont.col && subs.some(x => x.nombre === cont.sub)) getters.push('', `${J}public String get${capital(camel(cont.col))}() {`, `${J}    return "${cont.normal}";`, `${J}}`);
      if (getters.length) ls.splice(cierreClase(ls), 0, ...getters);
      // las cuentas de la entidad con los datos nuevos
      return cuentasBase(ls.join('\n'));
    });

    // las cuentas que cambian para todos: un valor fijo que pasa a ser el dato nuevo, «+ repuestos», «20% de … si garantia = SI»
    function cuentasBase(t) {
      const calc = plan.calc;
      if (!calc) return t;
      let ls = t.split('\n');
      const ci = ls.findIndex(l => new RegExp('\\b' + calc.nombre + '\\s*\\(\\s*\\)\\s*\\{').test(l) && !/\bnew\b/.test(l));
      if (ci < 0) return t;
      const fc = cierre(ls, ci);
      const ret = ls.findIndex((l, i) => i > ci && i < fc && /^\s*return\b/.test(l));
      const textoTodo = plan.oraciones.join(' ');
      for (const x of extras) {
        const k = x.k;
        // 1) el valor fijo que tenían todos (el del formato viejo) pasa a ser el dato de cada uno
        if (k.tipo !== 'String' && k.normal === undefined && k.porDefecto) {
          const constantes = [...t.matchAll(new RegExp('static\\s+final\\s+\\w+\\s+(\\w+)\\s*=\\s*' + escRe(String(k.porDefecto)) + '\\s*;', 'g'))].map(m => m[1]);
          const re = new RegExp('\\b(?:' + [escRe(String(k.porDefecto)), ...constantes].join('|') + ')\\b');
          let ok = false;
          for (let i = ci + 1; i < fc; i++) if (re.test(limpio(ls[i]))) { ls[i] = ls[i].replace(re, 'this.' + x.nombre); ok = true; }
          if (ok) { hecho.push({ que: 'cuenta', texto: `${calc.nombre}() usa ${x.nombre} en vez del ${k.porDefecto} fijo` }); continue; }
        }
        // 2) «importe anterior + repuestos», «agregando los repuestos»
        const suma = new RegExp('\\+\\s*' + escRe(k.col) + '\\b|agregando\\s+(?:los\\s+|las\\s+|el\\s+|la\\s+)?' + escRe(k.col) + '\\b', 'i');
        if (k.tipo !== 'String' && suma.test(textoTodo) && ret >= 0 && /;\s*$/.test(ls[ret])) {
          ls[ret] = ls[ret].replace(/;\s*$/, ` + ${x.nombre};`);
          hecho.push({ que: 'cuenta', texto: `${calc.nombre}() suma ${x.nombre}` });
        }
      }
      // 3) «N% del <algo> si <dato> = <VALOR>»: <algo> lo define otra oración («… se calcula como horas * 850»)
      for (const x of extras.filter(x => x.k.tipo === 'String')) {
        const re = new RegExp('([-+])?\\s*(\\d+(?:[.,]\\d+)?)\\s*%\\s+del?\\s+([a-záéíóúñ ]+?)\\s+si\\s+' + escRe(x.k.col) + '\\s*=\\s*([A-Z_]+)', 'i');
        const m = String(texto).replace(/\s+/g, ' ').match(re);
        if (!m || ret < 0 || !/^\s*return\s+[^;]+;\s*$/.test(ls[ret])) continue;
        const concepto = bajo(m[3]).trim();
        const def = plan.oraciones.map(o => bajo(o).match(new RegExp(escRe(concepto) + '\\s+se\\s+calcula\\s+como\\s+([\\w\\s*+\\-/().]+?)\\s*\\.?$'))).find(Boolean);
        const campos = new Set([...t.matchAll(/^\s*(?:private|protected)\s+(?:final\s+)?[\w<>]+\s+(\w+)\s*;/gm)].map(mm => mm[1]));
        const expr = def ? def[1].trim() : null;
        if (!expr || !(expr.match(/[a-z_]\w*/gi) || []).every(w => campos.has(w))) { avisos.push(`No pude armar sola la regla «${m[0].trim()}»: va en ${calc.nombre}().`); continue; }
        const menos = m[1] === '-' || /descuent|bonificaci|absorbe/.test(bajo(texto)) && m[1] !== '+';
        const I = sangria(ls[ret]);
        const e = ls[ret].replace(/^\s*return\s+/, '').replace(/;\s*$/, '');
        const pct = num(m[2]);
        const parte = tipoCalc === 'int' || tipoCalc === 'long' ? `(${expr}) * ${pct} / 100` : `(${expr}) * ${pct / 100}`;
        ls.splice(ret, 1, `${I}${tipoCalc} total = ${e};`, `${I}if (${x.nombre}.equals("${m[4]}")) {`, `${I}    total ${menos ? '-' : '+'}= ${parte};`, `${I}}`, `${I}return total;`);
        hecho.push({ que: 'cuenta', texto: `${calc.nombre}() ${menos ? 'descuenta' : 'suma'} el ${pct}% de ${concepto} si ${x.nombre} es ${m[4]}` });
      }
      return ls.join('\n');
    }

    // «sus ingresos superan los 25000», «sus deudas no pueden superar el 12% de sus ingresos» → una condición sobre las columnas
    function condicionDe(t, arr) {
      const col = w => { const i = c.viejos.findIndex(h => bajo(h).includes(w.replace(/s$/, ''))); return i >= 0 ? `Double.parseDouble(${arr}[${i}].strip())` : null; };
      let m = t.match(/sus?\s+(\w+)\s+no\s+pueden?\s+superar\s+el\s+(\d+(?:[.,]\d+)?)\s*%\s+de\s+sus?\s+(\w+)/);
      if (m && col(m[1]) && col(m[3])) return `${col(m[1])} <= ${col(m[3])} * ${num(m[2]) / 100}`;
      m = t.match(/sus?\s+(\w+)\s+(no\s+(?:pueden?\s+)?)?super\w*\s+(?:los|las|el|la)?\s*(\d[\d._]*)(?!\s*%)/);
      if (m && col(m[1])) return `${col(m[1])} ${m[2] ? '<=' : '>'} ${num(m[3])}`;
      return null;
    }

    // ── 3) Las subclases
    for (const x of subs) {
      if (c.esRecord || !c.ctor) { avisos.push(`${E} es un record: no se puede heredar para hacer ${x.nombre}.`); continue; }
      const params = c.ctor.params.map(p => [p.tipo, p.nombre]).concat(extras.map(y => [y.tipo, y.nombre]));
      const propios = (x.propios || []).map(y => [y.tipo, camel(y.col)]);
      const calc = plan.calc;
      const lineas = [];
      if (c.paquete) lineas.push(`package ${c.paquete};`, '');
      lineas.push(`public class ${x.nombre} extends ${E} {`);
      for (const [tp, n] of propios) lineas.push(`    private final ${tp} ${n};`);
      if (propios.length) lineas.push('');
      lineas.push(`    public ${x.nombre}(${params.concat(propios).map(([tp, n]) => tp + ' ' + n).join(', ')}) {`, `        super(${params.map(p => p[1]).join(', ')});`);
      // topes propios: «admite como máximo 5000 g netos», «su velocidad promedio no puede superar los 90 km/h»
      const getters = (c.metodos || []).filter(m => m.simple && /^(get|is)/.test(m.nombre));
      for (const o of plan.oraciones.filter(o => x.cita && x.cita.includes(o))) {
        for (const m of bajo(o).matchAll(/(?:como\s+maximo|no\s+puede[n]?\s+superar(?:\s+(?:los|las|el|la))?)\s+(\d[\d_.]*)\s*(%|[a-z/]+)?/g)) {
          if (m[2] === '%') { avisos.push(`${x.nombre}: «${o.slice(0, 140)}» — es un tope relativo, armalo a mano.`); continue; }
          const antes = bajo(o).slice(0, m.index).split(/[^a-z]+/).filter(Boolean).slice(-3);
          const unidad = (m[2] || '').replace(/\/.*/, '');
          const raiz = { g: 'gram', gr: 'gram', gramos: 'gram', kg: 'kilo', centavos: 'centav', km: 'velocidad', usd: 'import', pesos: 'import' }[unidad] || unidad.slice(0, 5);
          const gtr = getters.find(gm => raiz && bajo(gm.nombre).includes(raiz)) || getters.find(gm => antes.filter(w => w.length > 3).every(w => bajo(gm.nombre).includes(w)) && antes.some(w => w.length > 3));
          if (!gtr) { avisos.push(`${x.nombre}: «${o.slice(0, 120)}» — no supe a qué dato se refiere el tope.`); continue; }
          lineas.push(`        if (${gtr.nombre}() > ${num(m[1])}) {`, `            throw new IllegalArgumentException("${gtr.nombre.replace(/^get/, '').toLowerCase()} supera el máximo de ${x.nombre}: " + ${gtr.nombre}());`, '        }');
          hecho.push({ que: 'tope', sub: x.nombre, texto: `${gtr.nombre}() hasta ${num(m[1])}` });
        }
      }
      for (const [, n] of propios) lineas.push(`        this.${n} = ${n};`);
      lineas.push('    }');
      if (calc && x.cuenta) lineas.push('', '    @Override', `    public ${calc.tipo} ${calc.nombre}() {`, `        return ${x.cuenta.replace(/\bcomun\b/, `super.${calc.nombre}()`)};`, '    }');
      else if (calc) avisos.push(`${x.nombre}: no pude armar sola la cuenta de ${calc.nombre}()${x.cita ? ' («' + x.cita.slice(0, 160) + '…»)' : ''}.`);
      const cont = plan.conteo;
      if (cont && cont.sub === x.nombre && cont.col && laDiceLaClase.has(cont.col)) { const kc = columnas.find(k => k.col === cont.col); lineas.push('', '    @Override', `    public String get${capital(camel(cont.col))}() {`, `        return "${kc.valores.find(v => v !== kc.normal)}";`, '    }'); }
      for (const [tp, n] of propios) lineas.push('', `    public ${tp} get${capital(n)}() {`, `        return ${n};`, '    }');
      lineas.push('}', '');
      const ruta = A.replace(/[^/]+\.java$/, x.nombre + '.java');
      fuentes[ruta] = lineas.join('\n'); nuevos.push(ruta);
      hecho.push({ que: 'subclase', nombre: x.nombre, cuenta: x.cuenta, col: x.col && x.col.col });
    }

    // ── 4) El colector: lo que pide «Resultado requerido» (conteo por un dato, total de un estado, suma de una cuenta)
    const agregados = [];
    if (c.colector) {
      const L = c.colector.campo, v1 = E[0].toLowerCase();
      const tCol = fuentes[c.colector.archivo];
      const metCol = [...tCol.matchAll(/public\s+[\w<>, ?]+\s+(\w+)\s*\(/g)].map(m => m[1]);
      const prefConteo = (metCol.map(n => n.match(/^((?:contar|cantidad|conteo|cuenta)\w*?)Por[A-Z]/)).find(Boolean) || [])[1];
      const prefSuma = metCol.some(n => /^calcular[A-Z]/.test(n)) ? 'calcularSuma' : 'total';
      if (plan.conteo && prefConteo) plan.conteo.metodo = prefConteo + 'Por' + plan.conteo.metodo.replace(/^cantidadPor/, '');
      const metodos = [];
      const cont = plan.conteo;
      if (cont) {
        let clave;
        if (cont.col && !laDiceLaClase.has(cont.col) && cont.sub && !subs.some(x => x.nombre === cont.sub)) cont.sub = null;
        if (cont.col) { const kc = columnas.find(k => k.col === cont.col); const gt = getterDe(cont.col) || 'get' + capital(camel(cont.col)); clave = kc && kc.tipo !== 'String' ? `${v1} -> String.valueOf(${v1}.${gt}())` : `${E}::${gt}`; }
        else if (cont.porTipo && subs[0] && plan.etiquetas) clave = `${v1} -> ${v1} instanceof ${subs[0].nombre} ? "${plan.etiquetas[1]}" : "${plan.etiquetas[0]}"`;
        if (clave) { metodos.push([`public Map<String, Long> ${cont.metodo}() {`, `    return ${L}.stream().collect(Collectors.groupingBy(${clave}, TreeMap::new, Collectors.counting()));`, `}`]); agregados.push({ metodo: cont.metodo, conteo: true, etiqueta: cont.col ? 'Por ' + (cont.col.replace(/([a-z])([A-Z])/g, '$1 $2').toLowerCase()) : 'Por tipo' }); }
      }
      const calc = plan.calc, mapTo = calc && (calc.tipo === 'int' ? 'mapToInt' : calc.tipo === 'long' ? 'mapToLong' : 'mapToDouble');
      for (const t of plan.requerido) {
        const m = t.match(/total\s+de\s+(?:las?\s+|los?\s+)?\w+\s+([A-Z][A-Z0-9_]+)/);
        const ge = idxEstado0 >= 0 ? getterDe(c.viejos[idxEstado0]) : null;
        if (m && calc && ge) {
          const met = 'total' + pascal(m[1]) + (/s$/i.test(m[1]) ? '' : 's');
          metodos.push([`public ${calc.tipo} ${met}() {`, `    return ${L}.stream().filter(${v1} -> ${v1}.${ge}().equals("${m[1]}")).${mapTo}(${E}::${calc.nombre}).sum();`, `}`]);
          agregados.push({ metodo: met, etiqueta: 'Total ' + m[1] });
        }
        const s = t.match(/suma\s+total\s+de\s+(?:la\s+|el\s+|los\s+|las\s+)?(\w+)/i);
        if (s) {
          const mt = (c.metodos || []).find(mm => bajo(mm.nombre).replace(/^get/, '') === bajo(s[1]) || bajo(mm.nombre) === bajo(s[1]));
          if (mt && /^(int|long|double)$/.test(mt.tipo)) {
            const met = prefSuma + capital(s[1]);
            const mp = mt.tipo === 'int' ? 'mapToInt' : mt.tipo === 'long' ? 'mapToLong' : 'mapToDouble';
            metodos.push([`public ${mt.tipo} ${met}() {`, `    return ${L}.stream().${mp}(${E}::${mt.nombre}).sum();`, `}`]);
            agregados.push({ metodo: met, etiqueta: 'Total ' + s[1] });
          }
        }
      }
      const pidePanorama = plan.requerido.find(t => /panorama/i.test(t) && /inclu/i.test(t));
      if (metodos.length) cambiar(c.colector.archivo, t => {
        const ls = t.split('\n');
        const pi = pidePanorama ? ls.findIndex(l => /\bString\s+panorama\s*\(\s*\)/.test(l)) : -1;
        if (pi >= 0) {
          const fp = cierre(ls, pi), ri = ls.findIndex((l, i) => i > pi && i < fp && /^\s*return\b/.test(l));
          if (ri >= 0) {
            const re = finSentencia(ls, ri);
            const total = (pidePanorama.match(/total\s+de\s+(\w+)/i) || [])[1];
            const partes = agregados.map(a => ` + " | ${/^(total|calcularSuma)/.test(a.metodo) && total ? 'Total ' + capital(total) : a.etiqueta}: " + ${a.metodo}()`);
            ls[re] = ls[re].replace(/;\s*$/, partes.join('') + ';');
            agregados.forEach(a => { a.enPanorama = true; });
            hecho.push({ que: 'panorama', metodos: agregados.map(a => a.metodo) });
          }
        }
        const J = sangria(ls.find(l => /^\s+(public|private|protected)\s/.test(l) && !/\bclass\b/.test(l)) || '    ');
        ls.splice(cierreClase(ls), 0, ...metodos.flatMap(m => ['', ...m.map(x => J + x)]));
        let r = ls.join('\n').replace(/\n\n\n+/g, '\n\n');
        if (metodos.some(m => m.join('').includes('Collectors.'))) r = agregarImports(r, ['java.util.Map', 'java.util.TreeMap', 'java.util.stream.Collectors']);
        hecho.push({ que: 'colector', clase: c.colector.clase, metodos: agregados.map(a => a.metodo) });
        return r;
      });
    }

    // ── 5) El main: el CSV del parcial por defecto y lo nuevo en pantalla
    if (c.main) cambiar(c.main.archivo, t => {
      let ls = t.split('\n');
      if (plan.csvNuevo) {
        const i = ls.findIndex(l => /"[^"]*\.csv"/.test(l));
        if (i >= 0 && !ls[i].includes(plan.csvNuevo)) { ls[i] = ls[i].replace(/"([^"]*\/)?[^"/]*\.csv"/, (_, d) => `"${d || ''}${plan.csvNuevo}"`); hecho.push({ que: 'main', csv: plan.csvNuevo }); }
      }
      if (agregados.some(a => !a.enPanorama) && c.colector) {
        const vm = ls.map(l => l.match(new RegExp('(\\w+)\\s*=\\s*new\\s+' + c.colector.clase + '\\s*\\('))).find(Boolean);
        if (vm) {
          const v = vm[1];
          let u = -1;
          ls.forEach((l, i) => { if (new RegExp('\\b' + v + '\\.').test(l) || new RegExp('\\b' + v + '\\s*=\\s*new').test(l)) u = i; });
          const e = finSentencia(ls, u);
          // «cantidades NORMAL/EN_MORA»: las dos, aunque una dé cero
          const par = (plan.requerido.map(t => t.match(/cantidades\s+([A-Za-z_]+)\s*\/\s*([A-Za-z_]+)/)).find(Boolean) || []).slice(1);
          const linea = a => a.conteo && par.length ? `System.out.println(${par.map((x, i) => `"${i ? ' | ' : ''}${x}: " + ${v}.${a.metodo}().getOrDefault("${x}", 0L)`).join(' + ')});` : `System.out.println("${a.etiqueta}: " + ${v}.${a.metodo}());`;
          ls.splice(e + 1, 0, ...agregados.filter(a => !a.enPanorama).map(a => sangria(ls[u]) + linea(a)));
          hecho.push({ que: 'mainMuestra', metodos: agregados.map(a => a.metodo) });
        }
      }
      return ls.join('\n');
    });

    // ── 6) Lo que el enunciado pide y no se armó solo
    for (const k of columnas) if (k.tipo !== 'String' && !k.presencia && extras.some(x => x.k === k) && !hecho.some(h => h.que === 'cuenta' && h.texto.includes(camel(k.col))) && /cost|import|cuent|calcul|suma/.test(bajo(k.textoCol || '')))
      avisos.push(`El dato ${k.col} se lee y se guarda, pero no supe sola cómo entra en ${plan.calc ? plan.calc.nombre + '()' : 'la cuenta'}: revisalo con el enunciado.`);

    return { fuentes, nuevos, avisos, hecho, plan, guia: g, nombreDecisiones: plan.pideDecisiones };
  }

  // DECISIONES.md (o el nombre que pida): lo hecho, contado en criollo, 3 a 5 renglones
  function decisiones(r) {
    const h = r.hecho, L = [];
    const enc = h.find(x => x.que === 'encabezado');
    if (enc) L.push(`Para leer los dos formatos no dupliqué el parser: guardo en «largo» las columnas del encabezado (${enc.N} el viejo, ${enc.M} el nuevo)${enc.mixto ? ' y bajo el nuevo acepto filas de los dos anchos' : ' y cada fila tiene que tener justo ese ancho'}; el orden quedó como estaba: primero el ancho, después el descarte y recién ahí valido.`);
    const cols = h.filter(x => x.que === 'columna').map(x => x.k);
    if (cols.length) L.push(`${cols.length > 1 ? 'Las columnas nuevas (' + cols.map(k => k.col).join(', ') + ') las leo' : 'La columna nueva (' + cols[0].col + ') la leo'} en la fábrica y las valido ahí; las filas viejas siguen como antes${cols.some(k => k.porDefecto != null && !k.presencia) ? ' (' + cols.filter(k => k.porDefecto != null && !k.presencia).map(k => k.col + ' = ' + k.porDefecto).join(', ') + ')' : ''}.`);
    const reglas = h.filter(x => x.que === 'regla').map(x => x.texto);
    if (reglas.length) L.push(`Validé también lo que pide para cada caso: ${reglas.join('; ')}.`);
    const d = h.find(x => x.que === 'datos');
    if (d) L.push(`Al constructor le agregué ${d.extras.join(' y ')}; el de antes llama al nuevo con los valores de siempre, así los tests viejos siguen andando.${h.filter(x => x.que === 'cuenta').length ? ' La cuenta: ' + h.filter(x => x.que === 'cuenta').map(x => x.texto).join('; ') + '.' : ''}`);
    for (const s of h.filter(x => x.que === 'subclase')) L.push(`Hice ${s.nombre}, que hereda y redefine la cuenta${s.cuenta ? ' (' + s.cuenta.replace(/\bcomun\b/, 'la común') + ')' : ''}; la fábrica la crea según ${s.col || 'el dato nuevo'} y el resto del programa no se entera.`);
    const est = h.filter(x => x.que === 'estado').map(x => x.valor), des = h.filter(x => x.que === 'descarte').map(x => x.valor);
    if (est.length || des.length) L.push(`${est.length ? est.join(' y ') + ' ahora es un estado válido' : ''}${est.length && des.length ? '; ' : ''}${des.length ? des.join(' y ') + ' se descarta sin validar' : ''}.`);
    const col = h.find(x => x.que === 'colector'), mn = h.find(x => x.que === 'main');
    const pan = h.find(x => x.que === 'panorama');
    if (col || mn) L.push(`${col ? `En ${col.clase} agregué ${col.metodos.map(m => m + '()').join(' y ')}${pan ? ' y lo sumé al panorama' : ''}` : ''}${col && mn ? '; ' : ''}${mn ? `el main lee ${mn.csv} si no le pasás nada y solo muestra` : ''}.`.replace(/^./, x => x.toUpperCase()));
    L.push(r.avisos.length ? 'Pendiente: ' + r.avisos.map(a => a.replace(/\.$/, '')).join('; ') + '.' : 'No me quedó nada pendiente.');
    while (L.length > 5) { const j = L.splice(L.length - 3, 2); L.splice(L.length - 1, 0, j.join(' ')); }
    return '# Decisiones\n\n' + L.map(x => '- ' + x).join('\n') + '\n';
  }

  return { resolver, decisiones };
});
