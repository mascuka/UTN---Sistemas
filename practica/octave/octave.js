/* Octave en el navegador, para la Práctica de Tecnologías para la Automatización.
   Un intérprete chico de Octave/Matlab escrito en JavaScript, con lo que se usa en los parciales de robótica:
   matrices (hasta 3 dimensiones), rangos, índices con "end", if / for / while / switch / try, funciones propias,
   funciones anónimas, structs, fprintf / sprintf, la salida con el formato de Octave ("format short") y las
   funciones del profe (Rotx, Roty, Rotz, Traslacion, matrizDenavitHartenberg, cinematica_directa,
   jacobiano_analitico, jacobiano_numerico, cinematica_inversa y generacion_de_trayectorias).
   Los gráficos (plot, plot3, DibujarEjes, dibujarOrigen…) se guardan para que la página los dibuje.
   No hace números complejos, celdas ni matemática simbólica: si aparecen, lo avisa con un error claro.

   Uso:  Octave.correr(codigo, { ocultar: ["Rotz"], archivos: [{ nombre: "Rotx.m", texto }] })
         → { salida, vars: { nombre: valor en JS }, error: null | { msg, linea, archivo }, graficos }
   archivos: los .m de funciones que están «en la carpeta» (los del profe). Cada uno se lee aparte, como en Octave,
   y sus funciones le ganan a las que ya trae el intérprete.
   Un valor en JS: número (escalar), texto, true/false, matriz como arreglo de filas, o un objeto (struct).
   Se prueba contra el Octave de verdad con herramientas/tpa-practica/probar_octave.js. */
(function(raiz){
"use strict";

class OctErr extends Error {}
const err = m => { throw new OctErr(m); };

/* ================= Valores ================= */
// Una matriz: dims ([filas, columnas] o [f, c, páginas]), los datos por columnas y el tipo (double, logical o char)
class Mat {
  constructor(dims, d, tipo){
    while(dims.length > 2 && dims[dims.length - 1] === 1) dims = dims.slice(0, -1);
    this.dims = dims; this.d = d; this.tipo = tipo || "double";
  }
  get r(){ return this.dims[0]; }
  get c(){ return this.dims[1]; }
  get p(){ return this.dims.length > 2 ? this.dims[2] : 1; }
  get n(){ return this.d.length; }
}
class Est { constructor(c){ this.c = c || new Map(); } }               // struct escalar
class Fh { constructor(params, cuerpo, captura, nombre, texto){ Object.assign(this, { params, cuerpo, captura, nombre, texto }); } }

const esc = (v, tipo) => new Mat([1, 1], [v], tipo);
const vacio = (r = 0, c = 0, tipo) => new Mat([r, c], [], tipo);
const ceros = (r, c) => new Mat([r, c], new Array(r * c).fill(0));
const texto = s => s.length ? new Mat([1, s.length], [...s].map(ch => ch.charCodeAt(0)), "char") : vacio(0, 0, "char");
const logico = v => esc(v ? 1 : 0, "logical");
const deFilas = filas => { const r = filas.length, c = r ? filas[0].length : 0, d = new Array(r * c); for(let i = 0; i < r; i++) for(let j = 0; j < c; j++) d[i + j * r] = filas[i][j]; return new Mat([r, c], d); };
const aFilas = m => Array.from({ length: m.r }, (_, i) => Array.from({ length: m.c * m.p }, (_, j) => m.d[i + j * m.r]));
const colDe = arr => new Mat([arr.length, 1], arr.slice());
const filaDe = arr => new Mat([1, arr.length], arr.slice());
const esMat = v => v instanceof Mat;
const esTexto = v => esMat(v) && v.tipo === "char";
const esEscalar = v => esMat(v) && v.n === 1;
const aTexto = v => { if(!esMat(v)) err("se esperaba un texto"); if(v.r <= 1) return String.fromCharCode(...v.d); return aFilas(v).map(f => String.fromCharCode(...f)).join("\n"); };
const num = (v, que = "valor") => { if(!esMat(v) || !v.n) err(`${que}: se esperaba un número`); return v.d[0]; };
const nombreTipo = v => v instanceof Est ? "struct" : v instanceof Fh ? "function handle" : v.tipo === "char" ? "char" : v.tipo === "logical" ? "logical" : "double";
const dimsTxt = v => esMat(v) ? v.dims.join("x") : "1x1";
const verdadero = v => { if(v instanceof Est || v instanceof Fh) err("no se puede usar como condición"); if(!v.n) return false; for(const x of v.d){ if(Number.isNaN(x)) return false; if(x === 0) return false; } return true; };
const clonar = m => new Mat(m.dims.slice(), m.d.slice(), m.tipo);

/* ================= Léxico ================= */
const PALABRAS = new Set(["if", "elseif", "else", "end", "endif", "while", "endwhile", "for", "endfor", "function", "endfunction", "return", "break", "continue",
  "switch", "case", "otherwise", "endswitch", "do", "until", "try", "catch", "end_try_catch", "global", "persistent"]);
const OPS = ["...", "==", "~=", "!=", "<=", ">=", "&&", "||", ".*", "./", ".\\", ".^", ".'", "+=", "-=", "*=", "/=", "^=",
  "+", "-", "*", "/", "\\", "^", "'", "<", ">", "&", "|", "!", "~", "=", "(", ")", "[", "]", "{", "}", ",", ";", ":", ".", "@"];
function lexico(src){
  const toks = [], pila = []; let i = 0, linea = 1, esp = false;
  const n = src.length;
  const enMatriz = () => pila.length && pila[pila.length - 1] !== "(";
  const ultimo = () => toks[toks.length - 1];
  const finValor = t => !!t && (t.t === "num" || t.t === "str" || t.t === "id" || (t.t === "kw" && t.v === "end" && pila.length > 0)
    || (t.t === "op" && [")", "]", "}", "'", ".'"].includes(t.v)));
  const poner = (t, v, ini) => toks.push({ t, v, linea, ini, fin: i, esp });
  const inicioLinea = () => { let k = i - 1; while(k >= 0 && (src[k] === " " || src[k] === "\t")) k--; return k < 0 || src[k] === "\n"; };
  while(i < n){
    const ch = src[i];
    // Comentario de bloque: %{ ... %} solos en su línea
    if((ch === "%" || ch === "#") && src[i + 1] === "{" && inicioLinea() && /^[ \t]*(\r?\n|$)/.test(src.slice(i + 2))){
      let prof = 0;
      while(i < n){
        const fin = src.indexOf("\n", i), l = src.slice(i, fin < 0 ? n : fin).trim();
        if(/^[%#]\{$/.test(l)) prof++; else if(/^[%#]\}$/.test(l)) prof--;
        i = fin < 0 ? n : fin + 1; linea++;
        if(prof === 0) break;
      }
      if(!enMatriz()) poner("nl"); continue;
    }
    if(ch === "%" || ch === "#"){ while(i < n && src[i] !== "\n") i++; continue; }
    if(ch === "." && src.startsWith("...", i)){ while(i < n && src[i] !== "\n") i++; i++; linea++; esp = true; continue; }
    if(ch === " " || ch === "\t" || ch === "\r"){
      while(i < n && (src[i] === " " || src[i] === "\t" || src[i] === "\r")) i++;
      esp = true;
      // En una matriz, el espacio separa elementos: [1 -2] son dos, [1 - 2] es uno
      if(enMatriz() && finValor(ultimo())){
        const c = src[i], c2 = src[i + 1];
        const empieza = c !== undefined && (/[0-9A-Za-z_"'@([{]/.test(c) || (c === "." && /[0-9]/.test(c2 || ""))
          || ((c === "+" || c === "-") && c2 !== undefined && !/[\s=]/.test(c2) && c2 !== c)
          || ((c === "~" || c === "!") && c2 !== "="));
        if(empieza) toks.push({ t: "op", v: ",", linea, ini: i, fin: i, esp: true, auto: true });
      }
      continue;
    }
    if(ch === "\n"){
      i++;
      if(enMatriz()) toks.push({ t: "op", v: ";", linea, ini: i, fin: i, esp: true, auto: true });
      else if(!pila.length) toks.push({ t: "nl", linea, ini: i, fin: i });
      linea++; esp = true; continue;
    }
    const ini = i;
    // Números
    if(/[0-9]/.test(ch) || (ch === "." && /[0-9]/.test(src[i + 1] || ""))){
      let j = i;
      while(j < n && /[0-9]/.test(src[j])) j++;
      if(src[j] === "." && !/[*/\\^']/.test(src[j + 1] || "")){ j++; while(j < n && /[0-9]/.test(src[j])) j++; }
      if(/[eEdD]/.test(src[j] || "") && /[0-9]/.test((src[j + 1] === "+" || src[j + 1] === "-") ? src[j + 2] || "" : src[j + 1] || "")){
        j += src[j + 1] === "+" || src[j + 1] === "-" ? 2 : 1; while(j < n && /[0-9]/.test(src[j])) j++;
      }
      const txt = src.slice(i, j).replace(/[dD]/, "e");
      i = j;
      if(/[ij]/.test(src[i] || "") && !/[A-Za-z0-9_]/.test(src[i + 1] || "")) err(`línea ${linea}: los números complejos (${txt}${src[i]}) no están disponibles en el navegador`);
      poner("num", parseFloat(txt), ini); esp = false; continue;
    }
    if(/[A-Za-z_]/.test(ch)){
      let j = i; while(j < n && /[A-Za-z0-9_]/.test(src[j])) j++;
      const w = src.slice(i, j); i = j;
      poner(PALABRAS.has(w) ? "kw" : "id", w, ini); esp = false; continue;
    }
    if(ch === '"'){
      let j = i + 1, s = "";
      const ESC = { n: "\n", t: "\t", r: "\r", a: "\x07", "\\": "\\", '"': '"', "'": "'", "0": "\0" };
      while(j < n && src[j] !== "\n"){
        if(src[j] === "\\" && j + 1 < n){ s += ESC[src[j + 1]] ?? src[j + 1]; j += 2; continue; }
        if(src[j] === '"'){ if(src[j + 1] === '"'){ s += '"'; j += 2; continue; } break; }
        s += src[j++];
      }
      if(src[j] !== '"') err(`línea ${linea}: falta cerrar las comillas`);
      i = j + 1; poner("str", s, ini); toks[toks.length - 1].dq = true; esp = false; continue;
    }
    if(ch === "'"){
      const u = ultimo();
      if(finValor(u) && (!esp || !enMatriz())){ i++; poner("op", "'", ini); esp = false; continue; }
      let j = i + 1, s = "";
      while(j < n && src[j] !== "\n"){
        if(src[j] === "'"){ if(src[j + 1] === "'"){ s += "'"; j += 2; continue; } break; }
        s += src[j++];
      }
      if(src[j] !== "'") err(`línea ${linea}: falta cerrar la comilla`);
      i = j + 1; poner("str", s, ini); esp = false; continue;
    }
    const op = OPS.find(o => src.startsWith(o, i));
    if(!op) err(`línea ${linea}: no entiendo el carácter "${ch}"`);
    i += op.length;
    if(op === "(" || op === "[" || op === "{") pila.push(op);
    else if(op === ")" || op === "]" || op === "}"){
      // un salto de línea justo antes de cerrar una matriz no agrega una fila vacía
      pila.pop();
    }
    poner("op", op, ini); esp = false;
  }
  toks.push({ t: "eof", linea, ini: n, fin: n });
  return toks;
}

/* ================= Sintaxis ================= */
const COMANDOS = new Set(["clear", "clc", "close", "format", "hold", "grid", "axis", "figure", "pkg", "warning", "more", "clf", "echo", "graphics_toolkit", "disp", "box", "rotate3d", "shg"]);
const FINES = { if: ["end", "endif"], for: ["end", "endfor"], while: ["end", "endwhile"], switch: ["end", "endswitch"], try: ["end", "end_try_catch"], function: ["end", "endfunction"] };
function sintaxis(toks, src){
  let k = 0, enIndice = 0;
  const ver = () => toks[k], sig = (d = 1) => toks[k + d];
  const es = (t, v) => ver().t === t && (v === undefined || ver().v === v);
  const esOp = v => es("op", v);
  const tomar = () => toks[k++];
  const acepta = (t, v) => es(t, v) ? tomar() : null;
  const espera = (t, v, que) => { if(!es(t, v)) err(`línea ${ver().linea}: ${que || `se esperaba "${v || t}"`}${ver().t === "eof" ? " y terminó el código" : ` y vino "${ver().v ?? ver().t}"`}`); return tomar(); };
  const separadores = () => { while(es("nl") || esOp(";") || esOp(",")) tomar(); };

  function programa(){
    const cuerpo = [], funcs = new Map();
    separadores();
    while(!es("eof")){
      if(es("kw", "function")){ const f = funcion(); funcs.set(f.nombre, f); }
      else cuerpo.push(sentencia());
      separadores();
    }
    return { cuerpo, funcs };
  }
  function bloque(fines){
    const out = [];
    separadores();
    while(!(ver().t === "kw" && fines.includes(ver().v))){
      if(es("eof")) err(`falta un "end": el bloque que empieza antes no se cerró`);
      if(es("kw", "function")) err(`línea ${ver().linea}: una función no puede definirse adentro de otro bloque`);
      out.push(sentencia());
      separadores();
    }
    return out;
  }
  function cerrar(clave){ const t = espera("kw", undefined, `falta el "end" del ${clave}`); if(!FINES[clave].includes(t.v)) err(`línea ${t.linea}: se esperaba "end" y vino "${t.v}"`); }
  function fin(s){
    if(esOp(";")){ tomar(); s.mostrar = false; }
    else if(esOp(",") || es("nl")){ tomar(); s.mostrar = true; }
    else if(es("eof") || es("kw")) s.mostrar = true;
    else err(`línea ${ver().linea}: no entiendo "${ver().v ?? ver().t}" (¿falta un operador o un ";"?)`);
    return s;
  }
  function funcion(){
    const t = tomar(), linea = t.linea;
    let salidas = [], nombre;
    if(esOp("[")){
      tomar();
      while(!esOp("]")){ if(esOp(",")){ tomar(); continue; } salidas.push(espera("id", undefined, "en la lista de salidas va un nombre").v); }
      tomar(); espera("op", "=");
      nombre = espera("id", undefined, "falta el nombre de la función").v;
    } else {
      const a = espera("id", undefined, "falta el nombre de la función").v;
      if(esOp("=")){ tomar(); salidas = [a]; nombre = espera("id", undefined, "falta el nombre de la función").v; }
      else nombre = a;
    }
    const params = [];
    if(esOp("(")){
      tomar();
      while(!esOp(")")){
        if(esOp(",")){ tomar(); continue; }
        if(esOp("~") || esOp("!")){ tomar(); params.push("~"); continue; }
        params.push(espera("id", undefined, "en los parámetros va un nombre").v);
      }
      tomar();
    }
    const cuerpo = [];
    separadores();
    while(!es("eof") && !es("kw", "function") && !(es("kw", "end") || es("kw", "endfunction"))){ cuerpo.push(sentencia()); separadores(); }
    if(es("kw", "end") || es("kw", "endfunction")) tomar();
    return { nombre, params, salidas, cuerpo, linea };
  }
  function sentencia(){
    const t = ver(), linea = t.linea;
    if(t.t === "kw"){
      switch(t.v){
        case "if": {
          tomar(); const ramas = [{ cond: expr(), cuerpo: bloque(["elseif", "else", "end", "endif"]) }]; let sino = null;
          while(es("kw", "elseif")){ tomar(); ramas.push({ cond: expr(), cuerpo: bloque(["elseif", "else", "end", "endif"]) }); }
          if(acepta("kw", "else")) sino = bloque(["end", "endif"]);
          cerrar("if"); return fin({ k: "if", ramas, sino, linea });
        }
        case "for": {
          tomar(); const par = acepta("op", "(");
          const v = espera("id", undefined, "después de for va el nombre de la variable").v; espera("op", "=");
          const e = expr(); if(par) espera("op", ")");
          const cuerpo = bloque(["end", "endfor"]); cerrar("for"); return fin({ k: "for", v, e, cuerpo, linea });
        }
        case "while": { tomar(); const cond = expr(); const cuerpo = bloque(["end", "endwhile"]); cerrar("while"); return fin({ k: "while", cond, cuerpo, linea }); }
        case "do": { tomar(); const cuerpo = bloque(["until"]); tomar(); const cond = expr(); return fin({ k: "do", cuerpo, cond, linea }); }
        case "switch": {
          tomar(); const e = expr(); separadores(); const casos = []; let otro = null;
          while(es("kw", "case")){
            tomar(); let vals;
            if(esOp("{")){ tomar(); vals = []; while(!esOp("}")){ if(esOp(",")){ tomar(); continue; } vals.push(expr()); } tomar(); }
            else vals = [expr()];
            casos.push({ vals, cuerpo: bloque(["case", "otherwise", "end", "endswitch"]) });
          }
          if(acepta("kw", "otherwise")) otro = bloque(["end", "endswitch"]);
          cerrar("switch"); return fin({ k: "switch", e, casos, otro, linea });
        }
        case "try": {
          tomar(); const cuerpo = bloque(["catch", "end", "end_try_catch"]); let v = null, captura = [];
          if(acepta("kw", "catch")){ if(es("id") && sig().t === "nl"){ v = tomar().v; } captura = bloque(["end", "end_try_catch"]); }
          cerrar("try"); return fin({ k: "try", cuerpo, v, captura, linea });
        }
        case "break": case "continue": case "return": tomar(); return fin({ k: t.v, linea });
        case "global": case "persistent": tomar(); while(es("id")) tomar(); return fin({ k: "nada", linea });
        default: err(`línea ${linea}: "${t.v}" no va acá`);
      }
    }
    // Comandos: "clear all", "hold on", "format long"…
    if(t.t === "id" && COMANDOS.has(t.v) && (sig().t === "id" || sig().t === "num") && !(sig(2).t === "op" && sig(2).v === "=") ){
      tomar(); const args = [];
      while(es("id") || es("num") || (esOp("-") && sig().t === "id")){ const x = tomar(); args.push(String(x.v)); }
      return fin({ k: "cmd", nombre: t.v, args, linea });
    }
    // [a, b] = f(...)
    if(esOp("[")){
      let prof = 0, j = k;
      for(; j < toks.length; j++){ const x = toks[j]; if(x.t === "op" && (x.v === "[" || x.v === "(" || x.v === "{")) prof++; else if(x.t === "op" && (x.v === "]" || x.v === ")" || x.v === "}")){ prof--; if(!prof) break; } else if(x.t === "eof") break; }
      if(toks[j + 1] && toks[j + 1].t === "op" && toks[j + 1].v === "="){
        tomar(); const destinos = [];
        while(!esOp("]")){
          if(esOp(",")){ tomar(); continue; }
          if(esOp("~") || esOp("!")){ tomar(); destinos.push(null); continue; }
          destinos.push(aDestino(postfijo(primario())));
        }
        tomar(); espera("op", "=");
        return fin({ k: "asig", destinos, e: expr(), linea });
      }
    }
    const e = expr();
    if(esOp("=")){ tomar(); return fin({ k: "asig", destinos: [aDestino(e)], e: derecha(), linea }); }
    for(const op of ["+=", "-=", "*=", "/=", "^="]) if(esOp(op)){ tomar(); const d = aDestino(e); return fin({ k: "asig", destinos: [d], e: { k: "bin", op: op[0], a: e, b: expr() }, linea }); }
    return fin({ k: "expr", e, linea });
  }
  // Lo que va a la derecha del "=": puede ser otra asignación (a = b = 3)
  function derecha(){ const e = expr(); if(esOp("=")){ tomar(); return { k: "asigExpr", destino: aDestino(e), e: derecha() }; } return e; }
  function aDestino(e){
    const acc = [];
    while(e.k === "idx" || e.k === "campo" || e.k === "campoDin"){
      if(e.k === "idx") acc.unshift({ t: "()", args: e.args }); else if(e.k === "campo") acc.unshift({ t: ".", n: e.n }); else acc.unshift({ t: ".()", e: e.e });
      e = e.a;
    }
    if(e.k !== "id") err(`no se puede asignar a eso: a la izquierda del "=" va una variable`);
    return { n: e.n, acc };
  }
  // Precedencias de Octave, de menor a mayor
  const expr = () => oo();
  function oo(){ let a = yy(); while(esOp("||")){ tomar(); a = { k: "bin", op: "||", a, b: yy() }; } return a; }
  function yy(){ let a = o1(); while(esOp("&&")){ tomar(); a = { k: "bin", op: "&&", a, b: o1() }; } return a; }
  function o1(){ let a = y1(); while(esOp("|")){ tomar(); a = { k: "bin", op: "|", a, b: y1() }; } return a; }
  function y1(){ let a = cmp(); while(esOp("&")){ tomar(); a = { k: "bin", op: "&", a, b: cmp() }; } return a; }
  function cmp(){ let a = rango(); while(["==", "~=", "!=", "<", "<=", ">", ">="].some(esOp)){ const op = tomar().v; a = { k: "bin", op: op === "!=" ? "~=" : op, a, b: rango() }; } return a; }
  function rango(){
    const a = suma();
    if(esOp(":") && !(sig().t === "op" && [")", ","].includes(sig().v) && enIndice)){
      tomar(); const b = suma();
      if(esOp(":")){ tomar(); const c = suma(); return { k: "rango", ini: a, paso: b, fin: c }; }
      return { k: "rango", ini: a, fin: b };
    }
    return a;
  }
  function suma(){ let a = prod(); while(esOp("+") || esOp("-")){ const op = tomar().v; a = { k: "bin", op, a, b: prod() }; } return a; }
  function prod(){ let a = unario(); while(["*", "/", ".*", "./", "\\", ".\\"].some(esOp)){ const op = tomar().v; a = { k: "bin", op, a, b: unario() }; } return a; }
  function unario(){
    if(esOp("-") || esOp("+") || esOp("!") || esOp("~")){ const op = tomar().v; return { k: "un", op: op === "!" ? "~" : op, a: unario() }; }
    return potencia();
  }
  function potencia(){
    let a = postfijo(primario());
    while(esOp("^") || esOp(".^")){
      const op = tomar().v;
      let b;
      if(esOp("-") || esOp("+") || esOp("!") || esOp("~")){ const u = tomar().v; b = { k: "un", op: u === "!" ? "~" : u, a: postfijo(primario()) }; }
      else b = postfijo(primario());
      a = { k: "bin", op, a, b };
    }
    return a;
  }
  function argumentos(){
    const args = []; enIndice++;
    tomar();   // (
    while(!esOp(")")){
      if(esOp(",")){ tomar(); continue; }
      if(esOp(":") && sig().t === "op" && (sig().v === ")" || sig().v === ",")){ tomar(); args.push({ k: "colon" }); continue; }
      args.push(expr());
      if(!esOp(",") && !esOp(")")) err(`línea ${ver().linea}: en la lista de argumentos falta una coma o el ")"`);
    }
    tomar(); enIndice--;
    return args;
  }
  function postfijo(a){
    for(;;){
      if(esOp("(")){ a = { k: "idx", a, args: argumentos() }; continue; }
      if(esOp(".") && sig().t === "id"){ tomar(); a = { k: "campo", a, n: tomar().v }; continue; }
      if(esOp(".") && sig().t === "op" && sig().v === "("){ tomar(); tomar(); const e = expr(); espera("op", ")"); a = { k: "campoDin", a, e }; continue; }
      if(esOp("'") || esOp(".'")){ tomar(); a = { k: "tr", a }; continue; }
      if(esOp("{")) err(`línea ${ver().linea}: las celdas ({ }) no están disponibles en el navegador`);
      return a;
    }
  }
  function primario(){
    const t = ver();
    if(t.t === "num"){ tomar(); return { k: "num", v: t.v }; }
    if(t.t === "str"){ tomar(); return { k: "str", v: t.v, dq: !!t.dq }; }
    if(t.t === "id"){ tomar(); return { k: "id", n: t.v }; }
    if(t.t === "kw" && t.v === "end" && enIndice){ tomar(); return { k: "end" }; }
    if(esOp("(")){ tomar(); const prevI = enIndice; enIndice = 0; const e = expr(); enIndice = prevI; espera("op", ")"); return { k: "par", e }; }
    if(esOp("[")) return matriz();
    if(esOp("{")) err(`línea ${t.linea}: las celdas ({ }) no están disponibles en el navegador`);
    if(esOp("@")){
      const ini = t.ini; tomar();
      if(esOp("(")){
        tomar(); const params = [];
        while(!esOp(")")){ if(esOp(",")){ tomar(); continue; } params.push(espera("id", undefined, "en @( ) van nombres").v); }
        tomar();
        const prevI = enIndice; enIndice = 0; const cuerpo = expr(); enIndice = prevI;
        return { k: "anon", params, cuerpo, texto: src.slice(ini, toks[k - 1].fin).replace(/\s+/g, " ") };
      }
      return { k: "fh", n: espera("id", undefined, "después de @ va el nombre de una función").v };
    }
    if(esOp(":") && enIndice) { tomar(); return { k: "colon" }; }
    err(`línea ${t.linea}: ${t.t === "eof" ? "el código terminó antes de tiempo (¿falta algo al final?)" : `no se esperaba "${t.v ?? t.t}"`}`);
  }
  function matriz(){
    const linea = ver().linea; tomar();
    const filas = [[]]; const prevI = enIndice; enIndice = prevI;   // "end" sigue valiendo adentro de A([1 end])
    for(;;){
      if(esOp("]")){ tomar(); break; }
      if(es("eof")) err(`línea ${linea}: falta cerrar el "["`);
      if(esOp(";") || es("nl")){ tomar(); filas.push([]); continue; }
      if(esOp(",")){ tomar(); continue; }
      if((esOp("~") || esOp("!")) && sig().t === "op" && (sig().v === "," || sig().v === "]")){ tomar(); filas[filas.length - 1].push({ k: "tilde" }); continue; }
      filas[filas.length - 1].push(expr());
    }
    return { k: "mat", filas: filas.filter(f => f.length) };
  }
  return { programa, toks };
}

/* ================= Formato de salida (como "format short" de Octave) ================= */
const digitos = x => x === 0 ? 0 : Math.floor(Math.log10(Math.abs(x)) + 1e-12) + 1;
/* toFixed y toExponential redondean los empates exactos hacia arriba; C (y Octave) los redondea al par: 2.25 → "2.2" */
function fijo(x, d){
  const s = x.toFixed(d), ax = Math.abs(x);
  if(ax >= 1e15 || !Number.isFinite(x)) return s;
  const t = ax.toFixed(Math.min(100, d + 30)), p = t.indexOf("."), resto = t.slice(p + 1 + d);
  if(!/^50*$/.test(resto)) return s;
  const corto = d ? t.slice(0, p + 1 + d) : t.slice(0, p);
  if(+corto[corto.length - 1] % 2) return s;
  return (x < 0 && /[1-9]/.test(corto) ? "-" : "") + corto;
}
function expo(x, d){
  const s = x.toExponential(d), ax = Math.abs(x);
  if(!Number.isFinite(x) || ax === 0) return s;
  const t = ax.toExponential(Math.min(100, d + 30)), [m, e] = t.split("e"), p = m.indexOf(".");
  const resto = m.slice(p + 1 + d);
  if(!/^50*$/.test(resto)) return s;
  const corto = d ? m.slice(0, p + 1 + d) : m.slice(0, p);
  if(+corto[corto.length - 1] % 2) return s;
  return (x < 0 ? "-" : "") + corto + "e" + e;
}
function expTxt(x, dec){ if(!Number.isFinite(x)) return x > 0 ? "Inf" : x < 0 ? "-Inf" : "NaN"; let s = expo(x, dec); return s.replace(/e([+-])(\d)$/, "e$10$2"); }
function especial(x){ return Number.isNaN(x) ? "NaN" : x > 0 ? "Inf" : "-Inf"; }
/* Elige el formato de un conjunto de números: entero, fijo (con ld enteros y rd decimales) o exponencial */
function elegirFormato(vals, modo, logical){
  const prec = modo === "long" ? 16 : 5;
  const fin = vals.filter(Number.isFinite), infnan = fin.length < vals.length;
  if(modo === "bank"){
    const mx = fin.length ? Math.max(...fin.map(Math.abs)) : 0, ld = Math.max(1, digitos(mx));
    return { tipo: "fijo", rd: 2, fw: 1 + ld + 1 + 2 };
  }
  if(logical) return { tipo: "int", fw: 1 };
  if(fin.every(Number.isInteger)){
    const mx = fin.length ? Math.max(...fin.map(Math.abs)) : 0;
    let fw = 1 + Math.max(1, digitos(mx));
    if(infnan && fw < 4) fw = 4;
    if(fw > 10) return { tipo: "e", dec: prec - 1, fw: prec + 6 };
    return { tipo: "int", fw };
  }
  const mx = Math.max(...fin.map(Math.abs)), mn = Math.min(...fin.map(Math.abs));
  const ldrd = x => x > 0 ? [x, prec > x ? prec - x : prec] : x < 0 ? [1, prec > x ? prec - x : prec] : [1, prec > 1 ? prec - 1 : prec];
  const [l1, r1] = ldrd(digitos(mx)), [l2, r2] = ldrd(digitos(mn));
  const ld = Math.max(l1, l2), rd = Math.max(r1, r2);
  let fw = 1 + ld + 1 + rd;
  if(infnan && fw < 4) fw = 4;
  if(fw > (modo === "long" ? 19 : 9)) return { tipo: "e", dec: prec - 1, fw: prec + 6 };
  return { tipo: "fijo", rd, fw };
}
function fmtCon(x, f){
  if(Object.is(x, -0)) x = 0;
  if(!Number.isFinite(x)) return especial(x);
  if(f.tipo === "int") return String(x);
  if(x === 0) return "0";
  if(f.tipo === "e") return expTxt(x, f.dec);
  return fijo(x, f.rd);
}
function fmtEscalar(x, modo, logical){ return fmtCon(x, elegirFormato([x], modo, logical)); }
/* Las filas de una matriz 2D, con "Columns N through M" si no entra en 80 caracteres */
function lineasMatriz(m, modo, sangria = ""){
  const f = elegirFormato(m.d, modo, m.tipo === "logical"), w = f.fw + 2 + (m.rango && f.tipo === "fijo" ? 1 : 0);
  const celda = x => fmtCon(x, f).padStart(w);
  const cols = m.c, porTramo = Math.max(1, Math.floor((80 - sangria.length) / w));
  const filas = j0 => j1 => Array.from({ length: m.r }, (_, i) => sangria + Array.from({ length: j1 - j0 }, (_, j) => celda(m.d[i + (j0 + j) * m.r])).join(""));
  if(cols <= porTramo) return filas(0)(cols);
  const out = [];
  for(let j0 = 0; j0 < cols; j0 += porTramo){
    const j1 = Math.min(cols, j0 + porTramo);
    out.push(`${sangria} ${j1 - j0 === 1 ? `Column ${j0 + 1}` : j1 - j0 === 2 ? `Columns ${j0 + 1} and ${j1}` : `Columns ${j0 + 1} through ${j1}`}:`, "", ...filas(j0)(j1), "");
  }
  out.pop();
  return out;
}
function mostrarValor(nombre, v, modo, sangria = ""){
  if(v instanceof Est){
    const out = [`${sangria}${nombre} =`, "", `${sangria}  scalar structure containing the fields:`, ""];
    for(const [k, x] of v.c) out.push(...mostrarValor(k, x, modo, sangria + "    ").map(l => l), ...(esMat(x) && x.n > 1 && x.tipo !== "char" ? [] : []));
    out.push("");
    return out;
  }
  if(v instanceof Fh) return [`${sangria}${nombre} =`, "", `${sangria}${v.texto || "@" + v.nombre}`, ""];
  if(v.tipo === "char"){
    if(v.r <= 1) return [`${sangria}${nombre} = ${aTexto(v)}`];
    return [`${sangria}${nombre} =`, "", ...aTexto(v).split("\n").map(l => sangria + l), ""];
  }
  if(!v.n) return [`${sangria}${nombre} = [](${dimsTxt(v)})`];
  if(v.n === 1) return [`${sangria}${nombre} = ${fmtEscalar(v.d[0], modo, v.tipo === "logical")}`];
  if(v.p > 1){
    const out = [`${sangria}${nombre} =`, ""];
    const tam = v.r * v.c;
    for(let k = 0; k < v.p; k++){
      const pag = new Mat([v.r, v.c], v.d.slice(k * tam, (k + 1) * tam), v.tipo);
      out.push(`${sangria}ans(:,:,${k + 1}) =`, "", ...lineasMatriz(pag, modo, sangria), "");
    }
    return out;
  }
  return [`${sangria}${nombre} =`, "", ...lineasMatriz(v, modo, sangria), ""];
}
function textoDisp(v, modo){
  if(v instanceof Est) return mostrarValor("", v, modo).slice(2).join("\n");
  if(v instanceof Fh) return v.texto || "@" + v.nombre;
  if(v.tipo === "char") return aTexto(v);
  if(!v.n) return "";
  if(v.n === 1) return fmtEscalar(v.d[0], modo, v.tipo === "logical");
  return lineasMatriz(v, modo).join("\n");
}

/* ================= printf ================= */
function escapes(s){ return s.replace(/\\(.)/g, (_, c) => ({ n: "\n", t: "\t", r: "\r", a: "\x07", "\\": "\\", '"': '"', "'": "'", "0": "\0" })[c] ?? "\\" + c); }
function formatear(fmt, args){
  // Los datos van de a uno (las matrices por columnas); un texto entero es un dato para %s
  const datos = [];
  for(const a of args){
    if(esTexto(a)) datos.push(aTexto(a));
    else if(esMat(a)) for(const x of a.d) datos.push(x);
    else if(a instanceof Est) err("printf: no se puede imprimir un struct");
    else datos.push(String(a));
  }
  const re = /%(%|[-+ 0#]*(\*|\d+)?(?:\.(\*|\d+))?([diouxXfFeEgGcs]))/g;
  const hay = [...fmt.matchAll(re)].filter(m => m[1] !== "%").length;
  let out = "", k = 0;
  const uno = () => {
    let corto = false;
    const r = fmt.replace(re, (todo, cuerpo, ancho, prec, conv) => {
      if(corto) return "";
      if(cuerpo === "%") return "%";
      if(k >= datos.length && (datos.length || hay)){ if(datos.length || k > 0){ corto = true; return ""; } }
      let x = datos[k++];
      const flags = (todo.match(/^%([-+ 0#]*)/) || ["", ""])[1];
      if(ancho === "*"){ ancho = String(x); x = datos[k++]; }
      if(prec === "*"){ prec = String(x); x = datos[k++]; }
      if(x === undefined) return "";
      return unaConv(x, flags, ancho, prec, conv);
    });
    return { r, corto };
  };
  if(!hay || !datos.length){ return uno().r; }
  while(k < datos.length){
    const { r, corto } = uno();
    out += r;
    if(corto) break;
  }
  return out;
}
function unaConv(x, flags, ancho, prec, conv){
  let s;
  const izq = flags.includes("-"), cero = flags.includes("0") && !izq, mas = flags.includes("+"), espacio = flags.includes(" ");
  if(conv === "s"){
    s = typeof x === "string" ? x : Number.isInteger(x) ? String(x) : String(+x.toPrecision(5)).replace(/e\+?/, "e+");
    if(typeof x === "number" && !Number.isInteger(x)) s = fmtG(x, 5, false);
    if(prec != null) s = s.slice(0, +prec);
  } else if(conv === "c"){ s = typeof x === "string" ? x : String.fromCharCode(x); }
  else {
    if(typeof x === "string"){ if(conv === "d" || conv === "i") return x; x = x.length ? x.charCodeAt(0) : 0; }
    if((conv === "d" || conv === "i" || conv === "u" || conv === "x" || conv === "X" || conv === "o") && !Number.isInteger(x)){
      // Como Octave: un %d con decimales se escribe como %f (o %g si es muy chico o grande)
      conv = "f"; if(prec == null){ s = fmtShortG(x); return pad(s, ancho, izq, false); }
    }
    if(!Number.isFinite(x)) s = Number.isNaN(x) ? "NaN" : x > 0 ? "Inf" : "-Inf";
    else switch(conv){
      case "d": case "i": case "u": s = String(Math.abs(x)); break;
      case "x": s = Math.abs(x).toString(16); break;
      case "X": s = Math.abs(x).toString(16).toUpperCase(); break;
      case "o": s = Math.abs(x).toString(8); break;
      case "f": case "F": s = fijo(Math.abs(x), prec == null ? 6 : +prec); break;
      case "e": case "E": s = expTxt(Math.abs(x), prec == null ? 6 : +prec); if(conv === "E") s = s.toUpperCase(); break;
      case "g": case "G": s = fmtG(Math.abs(x), prec == null ? 6 : Math.max(1, +prec), flags.includes("#")); if(conv === "G") s = s.toUpperCase(); break;
    }
    if(Number.isFinite(x)){
      const signo = x < 0 || Object.is(x, -0) && false ? "-" : mas ? "+" : espacio ? " " : "";
      if(cero && ancho && !izq){ s = s.padStart(+ancho - signo.length, "0"); }
      s = signo + s;
    } else if(x < 0) s = s; // ya trae el signo
  }
  return pad(s, ancho, izq, false);
}
const pad = (s, ancho, izq) => ancho ? (izq ? s.padEnd(+ancho) : s.padStart(+ancho)) : s;
function fmtG(x, p, alt){
  if(x === 0) return "0";
  const e = Math.floor(Math.log10(Math.abs(x)));
  let s;
  if(e < -4 || e >= p){ s = expTxt(x, p - 1); if(!alt) s = s.replace(/\.?0+e/, "e"); }
  else { s = fijo(x, Math.max(0, p - 1 - e)); if(!alt && s.includes(".")) s = s.replace(/\.?0+$/, ""); }
  return s;
}
const fmtShortG = x => { const s = fmtG(Math.abs(x), 5, false); return (x < 0 ? "-" : "") + s; };

/* ================= Álgebra ================= */
function mult(a, b){
  if(a.n === 1 || b.n === 1) return elem(a, b, (x, y) => x * y);
  if(a.p > 1 || b.p > 1) err("operator *: no está definido para arreglos de 3 dimensiones");
  if(a.c !== b.r) err(`operator *: nonconformant arguments (op1 is ${a.r}x${a.c}, op2 is ${b.r}x${b.c})`);
  const r = a.r, c = b.c, k = a.c, d = new Array(r * c).fill(0);
  for(let j = 0; j < c; j++) for(let t = 0; t < k; t++){ const bt = b.d[t + j * k]; if(bt === 0) continue; for(let i = 0; i < r; i++) d[i + j * r] += a.d[i + t * r] * bt; }
  // 0 * Inf da NaN como en Octave
  if(a.d.some(x => !Number.isFinite(x)) || b.d.some(x => !Number.isFinite(x))){
    for(let i = 0; i < r; i++) for(let j = 0; j < c; j++){ let s = 0; for(let t = 0; t < k; t++) s += a.d[i + t * r] * b.d[t + j * k]; d[i + j * r] = s; }
  }
  return new Mat([r, c], d);
}
function transp(m){
  if(m.p > 1) err("transpose not defined for N-D objects");
  const d = new Array(m.n);
  for(let i = 0; i < m.r; i++) for(let j = 0; j < m.c; j++) d[j + i * m.c] = m.d[i + j * m.r];
  return new Mat([m.c, m.r], d, m.tipo);
}
// Resuelve A x = B (A cuadrada con pivoteo parcial; si no es cuadrada, por mínimos cuadrados)
function resolver(A, B, avisar){
  if(A.n === 1) return elem(B, A, (x, y) => x / y);
  if(A.r !== B.r) err(`operator \\: nonconformant arguments (op1 is ${A.r}x${A.c}, op2 is ${B.r}x${B.c})`);
  if(A.r !== A.c){ const At = transp(A); return resolver(mult(At, A), mult(At, B), avisar); }
  const n = A.r, m = B.c, a = aFilas(A), b = aFilas(B);
  let singular = false;
  for(let c = 0; c < n; c++){
    let p = c; for(let i = c + 1; i < n; i++) if(Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
    if(Math.abs(a[p][c]) < 1e-300){ singular = true; continue; }
    [a[c], a[p]] = [a[p], a[c]]; [b[c], b[p]] = [b[p], b[c]];
    for(let i = c + 1; i < n; i++){ const f = a[i][c] / a[c][c]; if(!f) continue; for(let j = c; j < n; j++) a[i][j] -= f * a[c][j]; for(let j = 0; j < m; j++) b[i][j] -= f * b[c][j]; }
  }
  const x = Array.from({ length: n }, () => new Array(m).fill(0));
  for(let j = 0; j < m; j++) for(let i = n - 1; i >= 0; i--){ let s = b[i][j]; for(let t = i + 1; t < n; t++) s -= a[i][t] * x[t][j]; x[i][j] = s / a[i][i]; }
  const rc = rcond(A);
  if(singular || rc < 1e-16) avisar("warning: matrix singular to machine precision");
  return deFilas(x);
}
function inversa(A, avisar){
  if(A.r !== A.c) err("inverse: argument must be a square matrix");
  if(A.p > 1) err("inverse: argument must be a square matrix");
  const n = A.r, I = ceros(n, n); for(let i = 0; i < n; i++) I.d[i + i * n] = 1;
  if(n === 0) return vacio();
  return resolver(A, I, avisar);
}
function rcond(A){
  // Estimación simple: 1 / (norma1(A) * norma1(inv(A))) con Gauss-Jordan
  const n = A.r, a = aFilas(A).map((f, i) => [...f, ...Array.from({ length: n }, (_, j) => +(i === j))]);
  for(let c = 0; c < n; c++){
    let p = c; for(let i = c + 1; i < n; i++) if(Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
    if(Math.abs(a[p][c]) < 1e-300) return 0;
    [a[c], a[p]] = [a[p], a[c]];
    const v = a[c][c]; for(let j = 0; j < 2 * n; j++) a[c][j] /= v;
    for(let i = 0; i < n; i++) if(i !== c){ const f = a[i][c]; if(f) for(let j = 0; j < 2 * n; j++) a[i][j] -= f * a[c][j]; }
  }
  const n1 = M => Math.max(...Array.from({ length: n }, (_, j) => M.reduce((s, f) => s + Math.abs(f[j]), 0)));
  const inv = a.map(f => f.slice(n)), A2 = aFilas(A);
  return 1 / (n1(A2) * n1(inv));
}
function determinante(A){
  if(A.r !== A.c) err("det: A must be a square matrix");
  const n = A.r, a = aFilas(A); let det = 1;
  for(let c = 0; c < n; c++){
    let p = c; for(let i = c + 1; i < n; i++) if(Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
    if(a[p][c] === 0) return 0;
    if(p !== c){ [a[c], a[p]] = [a[p], a[c]]; det = -det; }
    det *= a[c][c];
    for(let i = c + 1; i < n; i++){ const f = a[i][c] / a[c][c]; for(let j = c; j < n; j++) a[i][j] -= f * a[c][j]; }
  }
  return det;
}
// Autovalores de una matriz simétrica (Jacobi): para la norma 2 y para svd
function autovaloresSim(S){
  const n = S.length, a = S.map(f => f.slice());
  for(let it = 0; it < 100; it++){
    let off = 0; for(let i = 0; i < n; i++) for(let j = i + 1; j < n; j++) off += a[i][j] ** 2;
    if(off < 1e-30) break;
    for(let p = 0; p < n; p++) for(let q = p + 1; q < n; q++){
      if(Math.abs(a[p][q]) < 1e-300) continue;
      const th = (a[q][q] - a[p][p]) / (2 * a[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for(let k = 0; k < n; k++){ const akp = a[k][p], akq = a[k][q]; a[k][p] = c * akp - s * akq; a[k][q] = s * akp + c * akq; }
      for(let k = 0; k < n; k++){ const apk = a[p][k], aqk = a[q][k]; a[p][k] = c * apk - s * aqk; a[q][k] = s * apk + c * aqk; }
    }
  }
  return a.map((f, i) => f[i]);
}
function valoresSingulares(A){ const At = transp(A), S = aFilas(A.r >= A.c ? mult(At, A) : mult(A, At)); return autovaloresSim(S).map(x => Math.sqrt(Math.max(0, x))).sort((x, y) => y - x); }

/* Operación elemento a elemento con expansión (broadcasting) */
function elem(a, b, f, tipo){
  if(!esMat(a) || !esMat(b)) err("operación no definida para ese tipo de dato");
  if(a.n === 1 && b.n === 1) return new Mat([1, 1], [f(a.d[0], b.d[0])], tipo);
  if(a.n === 1){ const x = a.d[0]; return new Mat(b.dims.slice(), b.d.map(y => f(x, y)), tipo); }
  if(b.n === 1){ const y = b.d[0]; return new Mat(a.dims.slice(), a.d.map(x => f(x, y)), tipo); }
  const da = a.dims, db = b.dims, nd = Math.max(da.length, db.length), dims = [];
  for(let i = 0; i < nd; i++){
    const x = da[i] ?? 1, y = db[i] ?? 1;
    if(x !== y && x !== 1 && y !== 1) return err(`operator: nonconformant arguments (op1 is ${da.join("x")}, op2 is ${db.join("x")})`);
    dims.push(x === 1 ? y : x);
  }
  const total = dims.reduce((s, x) => s * x, 1), d = new Array(total);
  const r = dims[0], c = dims[1];
  const ra = da[0], ca = da[1], rb = db[0], cb = db[1];
  for(let k = 0; k < total; k++){
    const i = k % r, j = Math.floor(k / r) % c, p = Math.floor(k / (r * c));
    const ia = (ra === 1 ? 0 : i) + (ca === 1 ? 0 : j) * ra + ((da[2] ?? 1) === 1 ? 0 : p) * ra * ca;
    const ib = (rb === 1 ? 0 : i) + (cb === 1 ? 0 : j) * rb + ((db[2] ?? 1) === 1 ? 0 : p) * rb * cb;
    d[k] = f(a.d[ia], b.d[ib]);
  }
  return new Mat(dims, d, tipo);
}
const mapa = (m, f, tipo) => { if(!esMat(m)) err("se esperaba un número o una matriz"); return new Mat(m.dims.slice(), m.d.map(f), tipo); };

function potMat(a, b){
  if(a.n === 1 && b.n === 1) return esc(Math.pow(a.d[0], b.d[0]));
  if(b.n === 1 && a.r === a.c && a.p === 1){
    let e = b.d[0];
    if(!Number.isInteger(e)) err("mpower: para una matriz, el exponente tiene que ser entero (o usá .^)");
    let base = a; if(e < 0){ base = inversa(a, () => {}); e = -e; }
    let res = ceros(a.r, a.r); for(let i = 0; i < a.r; i++) res.d[i + i * a.r] = 1;
    while(e > 0){ if(e & 1) res = mult(res, base); base = mult(base, base); e >>= 1; }
    return res;
  }
  err("for x^y, only square matrix arguments are permitted and one argument must be scalar.  Use .^ for elementwise power.");
}

// Concatenación [a b] y [a; b]
function horz(vals){
  vals = vals.filter(v => !(esMat(v) && v.r === 0 && v.c === 0));
  if(!vals.length) return vacio();
  if(vals.some(v => !esMat(v))){ if(vals.length === 1) return vals[0]; err("concatenation operator not implemented for 'struct' / 'function handle' values"); }
  const r = vals[0].r;
  for(const v of vals) if(v.r !== r) err(`horizontal dimensions mismatch (${vals.map(dimsTxt).join(" vs ")})`);
  const tipo = vals.some(v => v.tipo === "char") ? "char" : vals.every(v => v.tipo === "logical") ? "logical" : "double";
  return new Mat([r, vals.reduce((s, v) => s + v.c, 0)], vals.flatMap(v => v.d), tipo);
}
function vert(vals){
  vals = vals.filter(v => !(esMat(v) && v.n === 0));
  if(!vals.length) return vacio();
  if(vals.some(v => !esMat(v))){ if(vals.length === 1) return vals[0]; err("concatenation operator not implemented for 'struct' / 'function handle' values"); }
  const c = vals[0].c;
  for(const v of vals) if(v.c !== c){
    if(vals.every(x => x.tipo === "char")) err(`vertical dimensions mismatch (${vals.map(dimsTxt).join(" vs ")}): las filas de texto tienen que tener el mismo largo`);
    err(`vertical dimensions mismatch (${vals.map(dimsTxt).join(" vs ")})`);
  }
  const r = vals.reduce((s, v) => s + v.r, 0), d = new Array(r * c);
  let r0 = 0;
  for(const v of vals){ for(let i = 0; i < v.r; i++) for(let j = 0; j < c; j++) d[(r0 + i) + j * r] = v.d[i + j * v.r]; r0 += v.r; }
  const tipo = vals.some(v => v.tipo === "char") ? "char" : vals.every(v => v.tipo === "logical") ? "logical" : "double";
  return new Mat([r, c], d, tipo);
}

/* ================= Índices ================= */
// Convierte un subíndice (número, vector, lógico o ":") en la lista de posiciones (desde 0) sobre una dimensión de tamaño "tam"
function posiciones(s, tam, quien){
  if(s === ":") return Array.from({ length: tam }, (_, i) => i);
  if(!esMat(s)) err("subscript indices must be either positive integers or logicals");
  if(s.tipo === "logical"){
    if(s.n > tam && s.d.slice(tam).some(x => x)) err(`${quien}(${s.n}): out of bound ${tam}`);
    const out = []; s.d.forEach((x, i) => { if(x) out.push(i); }); return out;
  }
  return s.d.map(x => {
    if(!Number.isInteger(x)) err(`${quien}(${fmtShortG(x)}): subscripts must be either integers 1 to (2^63)-1 or logicals`);
    if(x < 1) err(`index (${x}): out of bound; value ${x} out of bound ${tam}`);
    return x - 1;
  });
}
function indexar(v, subs, nombre = "index"){
  if(v instanceof Est){ if(subs.every(s => s === ":" || (esMat(s) && s.n === 1 && s.d[0] === 1))) return v; err("index out of bound for a struct"); }
  if(!esMat(v)) err("no se puede indexar ese valor");
  const ns = subs.length;
  if(ns === 0) return v;
  if(ns === 1){
    const s = subs[0], tam = v.n;
    const pos = posiciones(s, tam, nombre);
    for(const p of pos) if(p >= tam) err(`index (${p + 1}): out of bound ${tam} (dimensions are ${dimsTxt(v)})`);
    const d = pos.map(p => v.d[p]);
    let dims;
    if(s === ":") dims = [tam, 1];
    else if(s.tipo === "logical") dims = (v.r === 1 && v.dims.length === 2) ? [1, d.length] : [d.length, 1];
    else if(v.dims.length === 2 && (v.r === 1 || v.c === 1) && v.n > 1 && s.dims.length === 2 && (s.r === 1 || s.c === 1)) dims = v.r === 1 ? [1, d.length] : [d.length, 1];
    else dims = s.dims.slice();
    return new Mat(dims, d, v.tipo);
  }
  const r = v.r, c = ns === 2 ? v.c * v.p : v.c, p = ns >= 3 ? v.p : 1;
  const P = [posiciones(subs[0], r, nombre), posiciones(subs[1], c, nombre), ns >= 3 ? posiciones(subs[2], p, nombre) : [0]];
  for(let k = 3; k < ns; k++) for(const x of posiciones(subs[k], 1, nombre)) if(x > 0) err(`${nombre}: out of bound; value ${x + 1} out of bound 1`);
  const lim = [r, c, p];
  P.forEach((ps, k) => { for(const x of ps) if(x >= lim[k]) err(`${nombre}(${k === 0 ? `${x + 1},_` : k === 1 ? `_,${x + 1}` : `_,_,${x + 1}`}): out of bound ${lim[k]} (dimensions are ${dimsTxt(v)})`); });
  const dims = [P[0].length, P[1].length, P[2].length], d = [];
  for(const kk of P[2]) for(const j of P[1]) for(const i of P[0]) d.push(v.d[i + j * r + kk * r * c]);
  return new Mat(dims, d, v.tipo);
}
function asignarIdx(v, subs, rhs, nombre){
  if(rhs instanceof Est || rhs instanceof Fh){
    if((v === undefined || v instanceof Est) && subs.every(s => s === ":" || (esMat(s) && s.n === 1 && s.d[0] === 1))) return rhs;
    err("no se puede guardar un struct adentro de una matriz");
  }
  if(v === undefined) v = vacio(0, 0, rhs.tipo === "char" ? "char" : "double");
  if(!esMat(v)) err("no se puede indexar ese valor");
  const borrar = rhs.n === 0 && rhs.r === 0 && rhs.c === 0 && rhs.tipo === "double";
  const ns = subs.length;
  if(borrar) return borrarIdx(v, subs);
  const tipo = v.n === 0 ? rhs.tipo : (v.tipo === rhs.tipo ? v.tipo : v.tipo === "char" && rhs.tipo !== "char" ? "double" : v.tipo === "logical" ? "double" : v.tipo);
  if(ns === 1){
    const s = subs[0];
    let pos = s === ":" ? Array.from({ length: v.n }, (_, i) => i) : posiciones(s, v.n, nombre);
    if(rhs.n !== 1 && rhs.n !== pos.length) err(`=: nonconformant arguments (op1 is 1x${pos.length}, op2 is ${dimsTxt(rhs)})`);
    const mx = pos.length ? Math.max(...pos) + 1 : 0;
    let w = v;
    if(mx > v.n){
      if(v.n === 0 || v.r === 1 && v.dims.length === 2) w = new Mat([1, mx], [...v.d, ...new Array(mx - v.n).fill(0)], v.tipo);
      else if(v.c === 1 && v.dims.length === 2) w = new Mat([mx, 1], [...v.d, ...new Array(mx - v.n).fill(0)], v.tipo);
      else err(`Octave:index out of bound; value ${mx} out of bound ${v.n}: A(I) = X: X must have the same size as I`);
    } else w = clonar(v);
    pos.forEach((p, k) => { w.d[p] = rhs.n === 1 ? rhs.d[0] : rhs.d[k]; });
    w.tipo = tipo;
    return w;
  }
  const r = v.r, c = ns === 2 ? v.c * v.p : v.c, p = ns >= 3 ? v.p : 1;
  const P = [subs[0] === ":" ? null : posiciones(subs[0], r, nombre), subs[1] === ":" ? null : posiciones(subs[1], c, nombre), ns >= 3 ? (subs[2] === ":" ? null : posiciones(subs[2], p, nombre)) : [0]];
  // Con ":" en una dimensión de una matriz vacía, toma el tamaño del lado derecho
  const nr = P[0] ? Math.max(r, P[0].length ? Math.max(...P[0]) + 1 : 0) : (v.n === 0 ? rhs.r : r);
  const nc = P[1] ? Math.max(c, P[1].length ? Math.max(...P[1]) + 1 : 0) : (v.n === 0 ? (ns === 2 ? rhs.c : rhs.c) : c);
  const np = ns >= 3 ? (P[2] ? Math.max(p, P[2].length ? Math.max(...P[2]) + 1 : 0) : (v.n === 0 ? rhs.p : p)) : 1;
  const I = P[0] || Array.from({ length: nr }, (_, i) => i), J = P[1] || Array.from({ length: nc }, (_, i) => i), K = P[2] || Array.from({ length: np }, (_, i) => i);
  const cuenta = I.length * J.length * K.length;
  if(rhs.n !== 1 && rhs.n !== cuenta) err(`=: nonconformant arguments (op1 is ${I.length}x${J.length}${ns >= 3 ? "x" + K.length : ""}, op2 is ${dimsTxt(rhs)})`);
  // Copia agrandada si hace falta
  let w;
  if(nr !== r || nc !== c || np !== p){
    const dims = ns >= 3 ? [nr, nc, np] : (v.p > 1 && ns === 2 ? err("A(i,j) = X en un arreglo de 3 dimensiones: usá tres índices") : [nr, nc]);
    w = new Mat(dims, new Array(nr * nc * np).fill(0), tipo);
    for(let kk = 0; kk < p; kk++) for(let j = 0; j < c; j++) for(let i = 0; i < r; i++) w.d[i + j * nr + kk * nr * nc] = v.d[i + j * r + kk * r * c];
  } else { w = clonar(v); w.tipo = tipo; }
  let t = 0;
  for(const kk of K) for(const j of J) for(const i of I){ w.d[i + j * nr + kk * nr * nc] = rhs.n === 1 ? rhs.d[0] : rhs.d[t]; t++; }
  return w;
}
function borrarIdx(v, subs){
  if(subs.length === 1){
    const quitar = new Set(subs[0] === ":" ? v.d.map((_, i) => i) : posiciones(subs[0], v.n, "index"));
    const d = v.d.filter((_, i) => !quitar.has(i));
    return v.c === 1 && v.r > 1 ? new Mat([d.length, 1], d, v.tipo) : new Mat([d.length ? 1 : (v.r === 1 ? 1 : 0), d.length], d, v.tipo);
  }
  const [s0, s1] = subs;
  if(s0 === ":" || (esMat(s0) && posiciones(s0, v.r).length === v.r && v.r)){
    const q = new Set(s1 === ":" ? Array.from({ length: v.c }, (_, i) => i) : posiciones(s1, v.c));
    const cols = Array.from({ length: v.c }, (_, j) => j).filter(j => !q.has(j));
    return new Mat([v.r, cols.length], cols.flatMap(j => v.d.slice(j * v.r, (j + 1) * v.r)), v.tipo);
  }
  if(s1 === ":" || (esMat(s1) && posiciones(s1, v.c).length === v.c && v.c)){
    const q = new Set(posiciones(s0, v.r));
    const filas = Array.from({ length: v.r }, (_, i) => i).filter(i => !q.has(i)), d = [];
    for(let j = 0; j < v.c; j++) for(const i of filas) d.push(v.d[i + j * v.r]);
    return new Mat([filas.length, v.c], d, v.tipo);
  }
  err("a null assignment can only have one non-colon index");
}

/* ================= Intérprete ================= */
const BREAK = 1, CONTINUE = 2, RETURN = 3;
class Interprete {
  constructor(opts = {}){
    this.salida = [];
    this.graficos = [];
    this.fig = null;
    this.modo = "short";
    this.pasos = 0;
    this.t0 = Date.now();
    this.limiteMs = opts.limiteMs || 4000;
    this.ocultar = new Set(opts.ocultar || []);
    this.funcs = new Map();
    this.prof = 0;
    this.linea = 0;
    this.archivo = null;       // el .m de la carpeta donde se está ejecutando (null: el script)
    this.archivos = opts.archivos || [];
    this.ctxEnd = [];
  }
  escribir(s){ this.salida.push(s); }
  avisar(s){ this.escribir(s + "\n"); }
  tic(){
    if(++this.pasos % 2000 === 0 && Date.now() - this.t0 > this.limiteMs) err(`el programa tardó más de ${this.limiteMs / 1000} segundos y se cortó (¿un while que nunca termina?)`);
  }
  correr(src){
    // Primero los .m de la carpeta: cada archivo se lee solo (una función sin "end" termina donde termina el archivo)
    for(const a of this.archivos){
      this.archivo = a.nombre; this.linea = 0;
      const pa = sintaxis(lexico(String(a.texto).replace(/\r\n?/g, "\n")), a.texto).programa();
      let primera = true;
      for(const [k, f] of pa.funcs){
        f.archivo = a.nombre; this.funcs.set(k, f);
        // Como en Octave, la primera función del archivo se llama como el archivo (DibujarEjes.m define dibujarEjes)
        if(primera){ this.funcs.set(a.nombre.replace(/\.m$/, ""), f); primera = false; }
      }
    }
    this.archivo = null;
    const toks = lexico(src);
    const { programa } = sintaxis(toks, src);
    const p = programa();
    for(const [k, f] of p.funcs) this.funcs.set(k, f);
    const sc = { vars: new Map(), nargin: 0, nargout: 0, raiz: true };
    this.raiz = sc;
    this.bloque(p.cuerpo, sc);
    return sc;
  }
  bloque(ss, sc){
    for(const s of ss){ const r = this.sentencia(s, sc); if(r) return r; }
    return 0;
  }
  sentencia(s, sc){
    this.linea = s.linea; this.tic();
    switch(s.k){
      case "expr": {
        const e = s.e;
        if(e.k === "id" && sc.vars.has(e.n)){ if(s.mostrar) this.mostrar(e.n, sc.vars.get(e.n)); return 0; }
        const outs = this.valores(e, sc, 0);
        if(outs.length && outs[0] !== undefined){ sc.vars.set("ans", outs[0]); if(s.mostrar) this.mostrar("ans", outs[0]); }
        return 0;
      }
      case "asig": {
        if(s.destinos.length === 1){
          const v = this.eval(s.e, sc);
          if(v === undefined) err("value on right hand side of assignment is undefined (la función no devuelve nada)");
          this.asignar(s.destinos[0], v, sc);
          if(s.mostrar) this.mostrar(s.destinos[0].n, sc.vars.get(s.destinos[0].n));
          return 0;
        }
        const outs = this.valores(s.e, sc, s.destinos.length);
        s.destinos.forEach((d, i) => {
          if(!d) return;
          if(outs[i] === undefined) err(`element number ${i + 1} undefined in return list`);
          this.asignar(d, outs[i], sc);
          if(s.mostrar) this.mostrar(d.n, sc.vars.get(d.n));
        });
        return 0;
      }
      case "if": {
        for(const r of s.ramas) if(verdadero(this.eval(r.cond, sc))) return this.bloque(r.cuerpo, sc);
        return s.sino ? this.bloque(s.sino, sc) : 0;
      }
      case "for": {
        const v = this.eval(s.e, sc);
        if(v instanceof Est || v instanceof Fh){ sc.vars.set(s.v, v); return this.ejecutarCuerpo(s.cuerpo, sc); }
        const cols = v.n ? v.n / v.r : 0;
        for(let j = 0; j < cols; j++){
          this.tic();
          sc.vars.set(s.v, new Mat([v.r, 1], v.d.slice(j * v.r, (j + 1) * v.r), v.tipo));
          const r = this.bloque(s.cuerpo, sc);
          if(r === BREAK) break;
          if(r === RETURN) return r;
        }
        return 0;
      }
      case "while": {
        while(verdadero(this.eval(s.cond, sc))){
          this.tic();
          const r = this.bloque(s.cuerpo, sc);
          if(r === BREAK) break;
          if(r === RETURN) return r;
        }
        return 0;
      }
      case "do": {
        do { this.tic(); const r = this.bloque(s.cuerpo, sc); if(r === BREAK) break; if(r === RETURN) return r; } while(!verdadero(this.eval(s.cond, sc)));
        return 0;
      }
      case "switch": {
        const v = this.eval(s.e, sc);
        const igual = c => esTexto(v) || esTexto(c) ? esTexto(v) && esTexto(c) && aTexto(v) === aTexto(c) : esMat(c) && c.n && esMat(v) && v.n && c.d[0] === v.d[0];
        for(const c of s.casos) if(c.vals.some(e => igual(this.eval(e, sc)))) return this.bloque(c.cuerpo, sc);
        return s.otro ? this.bloque(s.otro, sc) : 0;
      }
      case "try": {
        const archivo = this.archivo;
        try { return this.bloque(s.cuerpo, sc); }
        catch(e){
          if(!(e instanceof OctErr)) throw e;
          this.archivo = archivo;
          if(s.v){ const st = new Est(); st.c.set("message", texto(e.message)); sc.vars.set(s.v, st); }
          return this.bloque(s.captura, sc);
        }
      }
      case "break": return BREAK;
      case "continue": return CONTINUE;
      case "return": return RETURN;
      case "nada": return 0;
      case "cmd": this.comando(s.nombre, s.args, sc); return 0;
    }
    err("sentencia desconocida");
  }
  ejecutarCuerpo(ss, sc){ const r = this.bloque(ss, sc); return r === RETURN ? r : 0; }
  comando(n, args, sc){
    if(n === "format") this.modo = ["long", "bank"].includes((args[0] || "short").toLowerCase()) ? args[0].toLowerCase() : "short";
    else if(n === "clear"){ if(!args.length || args.includes("all") || args.includes("-all")) sc.vars.clear(); else args.forEach(a => sc.vars.delete(a)); }
    else this.llamar(n, args.map(texto), 0, sc);
  }
  mostrar(nombre, v){ this.escribir(mostrarValor(nombre, v, this.modo).join("\n") + "\n"); }
  // ---- Expresiones
  eval(e, sc){ const v = this.valores(e, sc, 1); return v[0]; }
  valores(e, sc, nout){
    switch(e.k){
      case "num": return [esc(e.v)];
      case "str": return [texto(e.v)];
      case "par": return [this.eval(e.e, sc)];
      case "id": {
        if(sc.vars.has(e.n)) return [sc.vars.get(e.n)];
        return this.llamar(e.n, [], nout, sc);
      }
      case "end": {
        const c = this.ctxEnd[this.ctxEnd.length - 1];
        if(!c) err("'end': nonconformant arguments");
        const v = c.v;
        if(!esMat(v)) return [esc(1)];
        if(c.n === 1) return [esc(v.n)];
        if(c.k === 0) return [esc(v.r)];
        if(c.k === 1) return [esc(c.n === 2 ? v.c * v.p : v.c)];
        if(c.k === 2) return [esc(v.p)];
        return [esc(1)];
      }
      case "colon": err("':' solo va adentro de un índice");
      case "tilde": err("'~' solo va a la izquierda de una asignación");
      case "mat": {
        const filas = e.filas.map(f => horz(f.map(x => { const v = this.eval(x, sc); if(v === undefined) err("una función que no devuelve nada no puede ir adentro de [ ]"); return v; })));
        return [vert(filas)];
      }
      case "rango": {
        const a = num(this.eval(e.ini, sc), "rango"), s = e.paso ? num(this.eval(e.paso, sc), "rango") : 1, b = num(this.eval(e.fin, sc), "rango");
        return [rango(a, s, b)];
      }
      case "un": {
        const a = this.eval(e.a, sc);
        if(e.op === "-") return [mapa(a, x => -x)];
        if(e.op === "+") return [a.tipo === "char" || a.tipo === "logical" ? mapa(a, x => x) : a];
        return [mapa(a, x => x === 0 ? 1 : 0, "logical")];
      }
      case "tr": { const a = this.eval(e.a, sc); if(!esMat(a)) err("transpose not defined for this value"); return [transp(a)]; }
      case "bin": return [this.binaria(e, sc)];
      case "asigExpr": { const v = this.eval(e.e, sc); this.asignar(e.destino, v, sc); return [v]; }
      case "anon": {
        const cap = new Map(sc.vars);
        return [new Fh(e.params, e.cuerpo, cap, null, e.texto)];
      }
      case "fh": return [new Fh(null, null, null, e.n, "@" + e.n)];
      case "campo": case "campoDin": {
        const b = this.eval(e.a, sc), n = e.k === "campo" ? e.n : aTexto(this.eval(e.e, sc));
        if(!(b instanceof Est)) err(`invalid use of a N_-D array... (no es un struct: no tiene el campo "${n}")`);
        if(!b.c.has(n)) err(`invalid use of undefined value: el struct no tiene el campo "${n}"`);
        return [b.c.get(n)];
      }
      case "idx": {
        // Variable → índice; si no, llamada a función
        if(e.a.k === "id" && !sc.vars.has(e.a.n)){
          const args = e.args.map(x => { if(x.k === "colon") err(`'${e.a.n}': ':' no se puede pasar a una función`); return this.eval(x, sc); });
          return this.llamar(e.a.n, args, nout, sc);
        }
        const base = this.eval(e.a, sc);
        if(base instanceof Fh) return this.llamarFh(base, e.args.map(x => this.eval(x, sc)), nout, sc);
        const subs = this.subindices(base, e.args, sc);
        return [indexar(base, subs, e.a.k === "id" ? e.a.n : "index")];
      }
    }
    err(`expresión desconocida (${e.k})`);
  }
  subindices(base, args, sc){
    return args.map((x, k) => {
      if(x.k === "colon") return ":";
      this.ctxEnd.push({ v: base, k, n: args.length });
      try { return this.eval(x, sc); } finally { this.ctxEnd.pop(); }
    });
  }
  binaria(e, sc){
    const op = e.op;
    if(op === "&&" || op === "||"){
      const a = this.eval(e.a, sc);
      const va = verdaderoLogico(a, op);
      if(op === "&&" && !va) return logico(false);
      if(op === "||" && va) return logico(true);
      return logico(verdaderoLogico(this.eval(e.b, sc), op));
    }
    const a = this.eval(e.a, sc), b = this.eval(e.b, sc);
    if(a === undefined || b === undefined) err("una función que no devuelve nada no se puede usar en una cuenta");
    if(!esMat(a) || !esMat(b)) err(`binary operator '${op}' not implemented for '${nombreTipo(a)}' by '${nombreTipo(b)}' operations`);
    switch(op){
      case "+": return elem(a, b, (x, y) => x + y);
      case "-": return elem(a, b, (x, y) => x - y);
      case ".*": return elem(a, b, (x, y) => x * y);
      case "./": return elem(a, b, (x, y) => x / y);
      case ".\\": return elem(a, b, (x, y) => y / x);
      case ".^": return elem(a, b, (x, y) => Math.pow(x, y));
      case "*": return mult(a, b);
      case "/": if(b.n === 1) return elem(a, b, (x, y) => x / y); return transp(resolver(transp(b), transp(a), m => this.avisar(m)));
      case "\\": return resolver(a, b, m => this.avisar(m));
      case "^": return potMat(a, b);
      case "==": return elem(a, b, (x, y) => +(x === y), "logical");
      case "~=": return elem(a, b, (x, y) => +(x !== y), "logical");
      case "<": return elem(a, b, (x, y) => +(x < y), "logical");
      case "<=": return elem(a, b, (x, y) => +(x <= y), "logical");
      case ">": return elem(a, b, (x, y) => +(x > y), "logical");
      case ">=": return elem(a, b, (x, y) => +(x >= y), "logical");
      case "&": return elem(a, b, (x, y) => +(x !== 0 && y !== 0), "logical");
      case "|": return elem(a, b, (x, y) => +(x !== 0 || y !== 0), "logical");
    }
    err(`operador desconocido ${op}`);
  }
  // ---- Asignación: x = v, x(i,j) = v, s.campo = v, s.campo(i) = v
  asignar(d, v, sc){
    const actual = sc.vars.has(d.n) ? sc.vars.get(d.n) : undefined;
    if(!d.acc.length){ sc.vars.set(d.n, v); return; }
    if(actual === undefined && this.esFuncion(d.n) && d.acc[0].t === "()") {/* se puede crear una variable con el nombre de una función */}
    sc.vars.set(d.n, this.asignarEn(actual, d.acc, v, sc, d.n));
  }
  asignarEn(base, acc, v, sc, nombre){
    const [a, ...resto] = acc;
    if(a.t === "()"){
      const subs = this.subindices(base === undefined ? vacio() : base, a.args, sc);
      if(!resto.length) return asignarIdx(base, subs, v, nombre);
      const dentro = base === undefined ? undefined : indexar(base, subs, nombre);
      return asignarIdx(base, subs, this.asignarEn(dentro, resto, v, sc, nombre), nombre);
    }
    const campo = a.t === "." ? a.n : aTexto(this.eval(a.e, sc));
    let st;
    if(base === undefined || (esMat(base) && base.n === 0)) st = new Est();
    else if(base instanceof Est) st = new Est(new Map(base.c));
    else err(`no se puede agregar el campo "${campo}": "${nombre}" no es un struct`);
    st.c.set(campo, resto.length ? this.asignarEn(st.c.get(campo), resto, v, sc, nombre) : v);
    return st;
  }
  esFuncion(n){ return this.funcs.has(n) || (BUILTIN.has(n) && !this.ocultar.has(n)); }
  // ---- Llamadas
  llamar(n, args, nout, sc){
    const f = this.funcs.get(n);
    if(f) return this.llamarUsuario(f, args, nout);
    if(n === "nargin" && sc) return [esc(sc.nargin)];
    if(n === "nargout" && sc) return [esc(sc.nargout)];
    if(n === "exist" && sc) return [esc(sc.vars.has(aTexto(args[0])) ? 1 : this.esFuncion(aTexto(args[0])) ? 2 : 0)];
    const b = BUILTIN.get(n);
    if(b && !this.ocultar.has(n)){
      const r = b.call(this, args, nout, sc);
      return r === undefined ? [] : Array.isArray(r) ? r : [r];
    }
    if(SIMBOLICO.has(n)) err(`'${n}': la matemática simbólica (syms) no está en el navegador. Usá números`);
    if(this.ocultar.has(n)) err(`'${n}' undefined: en este ejercicio la función ${n} la escribís vos`);
    err(`'${n}' undefined`);
  }
  llamarUsuario(f, args, nout){
    if(++this.prof > 200) err("max_recursion_depth exceeded");
    try {
      if(args.length > f.params.length) err(`${f.nombre}: function called with too many inputs`);
      if(nout > Math.max(1, f.salidas.length)) err(`${f.nombre}: function called with too many outputs`);
      const sc = { vars: new Map(), nargin: args.length, nargout: nout };
      f.params.forEach((p, i) => { if(i < args.length && p !== "~") sc.vars.set(p, args[i]); });
      const lineaAntes = this.linea, archivoAntes = this.archivo;
      this.archivo = f.archivo || null;
      this.bloque(f.cuerpo, sc);
      this.linea = lineaAntes; this.archivo = archivoAntes;
      const outs = [];
      for(let i = 0; i < Math.max(1, nout); i++){
        const o = f.salidas[i];
        if(o === undefined) break;
        if(!sc.vars.has(o)){ if(i === 0 && nout === 0) break; err(`${f.nombre}: '${o}' undefined (la función no le dio valor a ${o})`); }
        outs.push(sc.vars.get(o));
      }
      return outs;
    } finally { this.prof--; }
  }
  llamarFh(fh, args, nout, sc){
    if(fh.nombre) return this.llamar(fh.nombre, args, nout, sc);
    const sc2 = { vars: new Map(fh.captura), nargin: args.length, nargout: nout };
    fh.params.forEach((p, i) => { if(i < args.length) sc2.vars.set(p, args[i]); });
    return this.valores(fh.cuerpo, sc2, nout);
  }
  // ---- Gráficos: cada figura junta sus series; sin "hold on", plot reemplaza lo anterior
  figura(){ if(!this.fig){ this.fig = { series: [], hold: false, titulo: "", ejes: ["", "", ""], tres: false, igual: false, grilla: false }; this.graficos.push(this.fig); } return this.fig; }
  serie(s){ const f = this.figura(); if(!f.hold && !s.extra) f.series = []; if(s.z) f.tres = true; f.series.push(s); if(f.series.length > 400) f.series.shift(); }
}
function verdaderoLogico(v, op){
  if(!esMat(v)) err(`invalid conversion to logical value (${op})`);
  if(!v.n) err(`invalid conversion from empty value to real scalar (${op})`);
  return v.d.every(x => x !== 0 && !Number.isNaN(x));
}
function rango(a, s, b){
  if(s === 0 || (s > 0 && a > b) || (s < 0 && a < b) || [a, s, b].some(Number.isNaN)) return vacio(1, 0);
  const n = Math.floor((b - a) / s * (1 + 1e-15) + 1e-10) + 1;
  if(n > 5e6) err("el rango es demasiado largo");
  const d = new Array(n); for(let i = 0; i < n; i++) d[i] = a + i * s;
  // como Octave: si el último queda a un pelito del límite, es el límite
  if(Math.abs(d[n - 1] - b) < Math.abs(s) * 1e-10) d[n - 1] = b;
  const m = new Mat([1, n], d);
  m.rango = true;   // Octave muestra los rangos con decimales con una columna un espacio más ancha
  return m;
}

/* ================= Funciones ================= */
const SIMBOLICO = new Set(["syms", "sym", "simplify", "subs", "vpa", "eval", "diff_sym", "solve"]);
const BUILTIN = new Map();
const def = (nombres, f) => nombres.split(" ").forEach(n => BUILTIN.set(n, f));
const arg = (args, i, nombre) => { if(args[i] === undefined) err(`Invalid call to ${nombre}`); return args[i]; };
// Funciones de un argumento, elemento a elemento
const elemental = (n, f) => def(n, function(args){ return mapa(arg(args, 0, n), f); });
const r180 = Math.PI / 180;
const sind = x => { const I = x / 180; if(Number.isFinite(I) && I === Math.trunc(I)) return 0; return Math.sin(I * Math.PI); };
const cosd = x => { const I = x / 180; if(Number.isFinite(I) && I + 0.5 === Math.trunc(I + 0.5)) return 0; return Math.cos(I * Math.PI); };
const complejo = (n, cond, f) => def(n, function(args){
  const a = arg(args, 0, n);
  if(esMat(a) && a.d.some(cond)) this.avisar(`warning: ${n}: el resultado es un número complejo (no disponible en el navegador): da NaN. ¿El punto está fuera del alcance del robot?`);
  return mapa(a, x => cond(x) ? NaN : f(x));
});
elemental("sin", Math.sin); elemental("cos", Math.cos); elemental("tan", Math.tan);
elemental("atan", Math.atan); elemental("exp", Math.exp); elemental("abs", Math.abs);
elemental("sinh", Math.sinh); elemental("cosh", Math.cosh); elemental("tanh", Math.tanh);
complejo("asin", x => x > 1 || x < -1, Math.asin); complejo("acos", x => x > 1 || x < -1, Math.acos);
complejo("asind", x => x > 1 || x < -1, x => Math.asin(x) / r180); complejo("acosd", x => x > 1 || x < -1, x => Math.acos(x) / r180);
complejo("sqrt", x => x < 0, Math.sqrt); complejo("log", x => x < 0, Math.log); complejo("log10", x => x < 0, Math.log10); complejo("log2", x => x < 0, Math.log2);
elemental("sind", sind); elemental("cosd", cosd); elemental("tand", x => { const s = sind(x), c = cosd(x); return c === 0 ? (s > 0 ? Infinity : -Infinity) : s === 0 ? 0 : s / c; });
elemental("atand", x => Math.atan(x) / r180);
elemental("deg2rad", x => x * r180); elemental("rad2deg", x => x / r180);
elemental("floor", Math.floor); elemental("ceil", Math.ceil); elemental("fix", Math.trunc); elemental("sign", Math.sign);
elemental("isnan", x => +Number.isNaN(x)); elemental("isinf", x => +(x === Infinity || x === -Infinity)); elemental("isfinite", x => +Number.isFinite(x));
for(const n of ["isnan", "isinf", "isfinite"]){ const f = BUILTIN.get(n); BUILTIN.set(n, function(a){ const r = f.call(this, a); r.tipo = "logical"; return r; }); }
def("round", function(args){ const a = arg(args, 0, "round"); const k = args[1] ? num(args[1]) : 0; const f = 10 ** k; return mapa(a, x => (Math.sign(x) * Math.round(Math.abs(x) * f)) / f); });
def("atan2", function(args){ return elem(arg(args, 0, "atan2"), arg(args, 1, "atan2"), Math.atan2); });
def("atan2d", function(args){ return elem(arg(args, 0, "atan2d"), arg(args, 1, "atan2d"), (y, x) => Math.atan2(y, x) / r180); });
def("hypot", function(args){ return elem(args[0], args[1], Math.hypot); });
def("mod", function(args){ return elem(arg(args, 0, "mod"), arg(args, 1, "mod"), (x, y) => { if(y === 0) return x; const r = x - Math.floor(x / y) * y; return Math.abs(r - y) < Math.abs(y) * 1e-14 ? 0 : r; }); });
def("rem", function(args){ return elem(arg(args, 0, "rem"), arg(args, 1, "rem"), (x, y) => y === 0 ? x : x - Math.trunc(x / y) * y); });
def("power", function(args){ return elem(args[0], args[1], Math.pow); });
def("pi", () => esc(Math.PI)); def("e", () => esc(Math.E)); def("Inf inf", () => esc(Infinity)); def("NaN nan", () => esc(NaN)); def("eps", function(args){ return esc(args[0] ? Math.abs(num(args[0])) * 2.220446049250313e-16 : 2.220446049250313e-16); });
def("true", function(args){ const [r, c] = tamDe(args); return new Mat([r, c], new Array(r * c).fill(1), "logical"); });
def("false", function(args){ const [r, c] = tamDe(args); return new Mat([r, c], new Array(r * c).fill(0), "logical"); });
function tamDe(args){
  if(!args.length) return [1, 1];
  if(args.length === 1){ const a = args[0]; if(a.n === 1) return [a.d[0], a.d[0]]; return [a.d[0], a.d[1], ...(a.d.slice(2))]; }
  return args.map(x => num(x));
}
const lleno = v => function(args){ const dims = tamDe(args.filter(a => !esTexto(a))); const t = dims.reduce((s, x) => s * Math.max(0, x), 1); return new Mat(dims.map(x => Math.max(0, x)), new Array(t).fill(v)); };
def("zeros", lleno(0)); def("ones", lleno(1));
def("eye", function(args){ const [r, c] = tamDe(args); const m = ceros(r, c); for(let i = 0; i < Math.min(r, c); i++) m.d[i + i * r] = 1; return m; });
def("rand", function(args){ const dims = tamDe(args); const t = dims.reduce((s, x) => s * x, 1); return new Mat(dims, Array.from({ length: t }, Math.random)); });
def("randn", function(args){ const dims = tamDe(args); const t = dims.reduce((s, x) => s * x, 1); return new Mat(dims, Array.from({ length: t }, () => Math.sqrt(-2 * Math.log(Math.random() || 1e-12)) * Math.cos(2 * Math.PI * Math.random()))); });
def("linspace", function(args){
  const a = num(arg(args, 0, "linspace")), b = num(arg(args, 1, "linspace")), n = args[2] ? Math.floor(num(args[2])) : 100;
  if(n < 1) return vacio(1, 0);
  const d = Array.from({ length: n }, (_, i) => n === 1 ? b : a + i * (b - a) / (n - 1)); d[n - 1] = b;
  return filaDe(d);
});
def("size", function(args, nout){
  const v = arg(args, 0, "size"), dims = esMat(v) ? v.dims : [1, 1];
  if(args[1]) return esc(dims[num(args[1]) - 1] ?? 1);
  if(nout > 1){ const out = dims.slice(0, nout); while(out.length < nout) out.push(1); if(nout < dims.length) out[nout - 1] = dims.slice(nout - 1).reduce((s, x) => s * x, 1); return out.map(x => esc(x)); }
  return filaDe(dims);
});
def("numel", function(args){ const v = arg(args, 0, "numel"); return esc(esMat(v) ? v.n : 1); });
def("length", function(args){ const v = arg(args, 0, "length"); return esc(esMat(v) ? (v.n ? Math.max(...v.dims) : 0) : 1); });
def("ndims", function(args){ return esc(esMat(args[0]) ? args[0].dims.length : 2); });
def("rows", function(args){ return esc(args[0].r); }); def("columns", function(args){ return esc(args[0].c); });
def("isempty", function(args){ const v = arg(args, 0, "isempty"); return logico(esMat(v) && v.n === 0); });
def("isscalar", function(args){ return logico(esMat(args[0]) && args[0].n === 1); });
def("isvector", function(args){ const v = args[0]; return logico(esMat(v) && v.dims.length === 2 && (v.r === 1 || v.c === 1) && v.n >= 1); });
def("isnumeric", function(args){ return logico(esMat(args[0]) && args[0].tipo === "double"); });
def("ischar", function(args){ return logico(esTexto(args[0])); });
def("islogical", function(args){ return logico(esMat(args[0]) && args[0].tipo === "logical"); });
def("isstruct", function(args){ return logico(args[0] instanceof Est); });
def("isreal", function(args){ return logico(esMat(args[0])); });
def("isa", function(args){ const t = aTexto(args[1]), v = args[0]; return logico(t === "numeric" || t === "float" ? esMat(v) && v.tipo === "double" : t === nombreTipo(v)); });
def("isfield", function(args){ const s = args[0], f = args[1]; return logico(s instanceof Est && esTexto(f) && s.c.has(aTexto(f))); });
def("isequal", function(args){
  const [a, b] = args;
  const igual = (x, y) => { if(x instanceof Est || y instanceof Est){ if(!(x instanceof Est && y instanceof Est) || x.c.size !== y.c.size) return false; for(const [k, v] of x.c) if(!y.c.has(k) || !igual(v, y.c.get(k))) return false; return true; } return esMat(x) && esMat(y) && x.dims.join() === y.dims.join() && x.d.every((v, i) => v === y.d[i]); };
  return logico(args.slice(1).every(b2 => igual(a, b2)));
});
def("class", function(args){ return texto(nombreTipo(args[0])); });
def("double", function(args){ return mapa(args[0], x => x); });
def("logical", function(args){ return mapa(args[0], x => +(x !== 0), "logical"); });
def("int32 int16 int8 int64 uint8 uint16 uint32", function(args){ return mapa(args[0], x => Math.round(x)); });
def("char", function(args){ return mapa(args[0], x => x, "char"); });
def("transpose", function(args){ return transp(args[0]); });
def("inv", function(args){ const A = arg(args, 0, "inv"); if(A.n === 1) return esc(1 / A.d[0]); return inversa(A, m => this.avisar(m)); });
def("pinv", function(args){ const A = args[0]; const At = transp(A); return A.r >= A.c ? mult(inversa(mult(At, A), () => {}), At) : mult(At, inversa(mult(A, At), () => {})); });
def("det", function(args){ return esc(determinante(arg(args, 0, "det"))); });
def("trace", function(args){ const A = args[0]; let s = 0; for(let i = 0; i < Math.min(A.r, A.c); i++) s += A.d[i + i * A.r]; return esc(s); });
def("rank", function(args){ const s = valoresSingulares(args[0]); const tol = Math.max(args[0].r, args[0].c) * (s[0] || 0) * 2.220446049250313e-16; return esc(s.filter(x => x > tol).length); });
def("svd", function(args){ return colDe(valoresSingulares(args[0])); });
def("norm", function(args){
  const A = arg(args, 0, "norm"), t = args[1] ? (esTexto(args[1]) ? aTexto(args[1]) : num(args[1])) : 2;
  if(!A.n) return esc(0);
  const vec = A.r === 1 || A.c === 1;
  if(t === "fro" || (vec && t === 2)) return esc(Math.sqrt(A.d.reduce((s, x) => s + x * x, 0)));
  if(vec){ if(t === Infinity || t === "inf" || t === "Inf") return esc(Math.max(...A.d.map(Math.abs))); if(t === 1) return esc(A.d.reduce((s, x) => s + Math.abs(x), 0)); return esc(A.d.reduce((s, x) => s + Math.abs(x) ** t, 0) ** (1 / t)); }
  if(t === 1) return esc(Math.max(...Array.from({ length: A.c }, (_, j) => A.d.slice(j * A.r, (j + 1) * A.r).reduce((s, x) => s + Math.abs(x), 0))));
  if(t === Infinity || t === "inf" || t === "Inf") return esc(Math.max(...aFilas(A).map(f => f.reduce((s, x) => s + Math.abs(x), 0))));
  return esc(valoresSingulares(A)[0]);
});
def("cross", function(args){
  const a = args[0], b = args[1];
  if(a.n !== 3 || b.n !== 3) err("cross: both X and Y must have 3 elements");
  const [x1, y1, z1] = a.d, [x2, y2, z2] = b.d;
  const d = [y1 * z2 - z1 * y2, z1 * x2 - x1 * z2, x1 * y2 - y1 * x2];
  return a.c === 1 && b.c === 1 ? colDe(d) : a.r === 1 && b.r === 1 ? filaDe(d) : colDe(d);
});
def("dot", function(args){ const a = args[0], b = args[1]; if(a.n !== b.n) err("dot: sizes of X and Y must match"); return esc(a.d.reduce((s, x, i) => s + x * b.d[i], 0)); });
def("kron", function(args){ const [A, B] = args, r = A.r * B.r, c = A.c * B.c, m = ceros(r, c); for(let i = 0; i < A.r; i++) for(let j = 0; j < A.c; j++) for(let k = 0; k < B.r; k++) for(let l = 0; l < B.c; l++) m.d[(i * B.r + k) + (j * B.c + l) * r] = A.d[i + j * A.r] * B.d[k + l * B.r]; return m; });
// Reducciones a lo largo de una dimensión (por defecto la primera que no es 1)
function reducir(nombre, f, inicial){
  def(nombre, function(args){
    const A = arg(args, 0, nombre);
    if(!A.n) return esc(inicial);
    const dim = args[1] ? num(args[1]) : (A.r === 1 ? 2 : 1);
    if(dim === 1){ const d = []; for(let j = 0; j < A.c * A.p; j++) d.push(A.d.slice(j * A.r, (j + 1) * A.r).reduce(f, inicial)); return new Mat([1, A.c, A.p], d); }
    const d = []; for(let i = 0; i < A.r; i++){ let s = inicial; for(let j = 0; j < A.c; j++) s = f(s, A.d[i + j * A.r]); d.push(s); }
    return colDe(d);
  });
}
reducir("sum", (s, x) => s + x, 0); reducir("prod", (s, x) => s * x, 1);
def("mean", function(args){ const A = args[0]; const s = BUILTIN.get("sum").call(this, args); const n = args[1] ? A.dims[num(args[1]) - 1] : (A.r === 1 ? A.c : A.r); return mapa(s, x => x / n); });
def("any", function(args){ const A = args[0]; if(A.r === 1 || A.c === 1) return logico(A.d.some(x => x !== 0 && !Number.isNaN(x))); const d = []; for(let j = 0; j < A.c; j++) d.push(+A.d.slice(j * A.r, (j + 1) * A.r).some(x => x !== 0)); return new Mat([1, A.c], d, "logical"); });
def("all", function(args){ const A = args[0]; if(!A.n) return logico(true); if(A.r === 1 || A.c === 1) return logico(A.d.every(x => x !== 0)); const d = []; for(let j = 0; j < A.c; j++) d.push(+A.d.slice(j * A.r, (j + 1) * A.r).every(x => x !== 0)); return new Mat([1, A.c], d, "logical"); });
def("cumsum", function(args){ const A = args[0]; if(A.r === 1 || A.c === 1){ let s = 0; return new Mat(A.dims.slice(), A.d.map(x => s += x)); } const m = clonar(A); for(let j = 0; j < A.c; j++){ let s = 0; for(let i = 0; i < A.r; i++){ s += A.d[i + j * A.r]; m.d[i + j * A.r] = s; } } return m; });
def("diff", function(args){ const A = args[0]; if(A.r === 1 || A.c === 1){ const d = A.d.slice(1).map((x, i) => x - A.d[i]); return A.r === 1 ? filaDe(d) : colDe(d); } const f = aFilas(A); return deFilas(f.slice(1).map((r, i) => r.map((x, j) => x - f[i][j]))); });
function minmax(nombre, mejor){
  def(nombre, function(args, nout){
    const A = arg(args, 0, nombre);
    if(args.length >= 2 && args[1] && args[1].n) return elem(A, args[1], (x, y) => Number.isNaN(x) ? y : Number.isNaN(y) ? x : mejor(x, y) ? x : y);
    if(!A.n) return [vacio(), vacio()];
    const dim = args[2] ? num(args[2]) : (A.r === 1 ? 2 : 1);
    const uno = xs => { let k = -1; xs.forEach((x, i) => { if(!Number.isNaN(x) && (k < 0 || mejor(x, xs[k]))) k = i; }); return k < 0 ? [NaN, 1] : [xs[k], k + 1]; };
    if(A.r === 1 || A.c === 1 ? true : false){ if(dim === 1 && A.r === 1 && A.c > 1){ return [mapa(A, x => x), mapa(A, () => 1)]; } const [v, i] = uno(A.d); return [esc(v), esc(i)]; }
    const vs = [], is = [];
    if(dim === 1) for(let j = 0; j < A.c; j++){ const [v, i] = uno(A.d.slice(j * A.r, (j + 1) * A.r)); vs.push(v); is.push(i); }
    else for(let i0 = 0; i0 < A.r; i0++){ const [v, i] = uno(Array.from({ length: A.c }, (_, j) => A.d[i0 + j * A.r])); vs.push(v); is.push(i); }
    return dim === 1 ? [filaDe(vs), filaDe(is)] : [colDe(vs), colDe(is)];
  });
}
minmax("max", (x, y) => x > y); minmax("min", (x, y) => x < y);
def("sort", function(args, nout){
  const A = args[0], desc = args[1] && esTexto(args[1]) && aTexto(args[1]).toLowerCase() === "descend";
  const ordenar = xs => xs.map((x, i) => [x, i]).sort((a, b) => desc ? b[0] - a[0] : a[0] - b[0]);
  if(A.r === 1 || A.c === 1){ const o = ordenar(A.d); return [new Mat(A.dims.slice(), o.map(x => x[0])), new Mat(A.dims.slice(), o.map(x => x[1] + 1))]; }
  const m = clonar(A), ix = clonar(A);
  for(let j = 0; j < A.c; j++){ const o = ordenar(A.d.slice(j * A.r, (j + 1) * A.r)); o.forEach(([x, i], k) => { m.d[k + j * A.r] = x; ix.d[k + j * A.r] = i + 1; }); }
  return [m, ix];
});
def("find", function(args, nout){
  const A = args[0], lim = args[1] ? num(args[1]) : Infinity;
  const ks = []; A.d.forEach((x, i) => { if(x !== 0 && ks.length < lim) ks.push(i); });
  if(nout >= 2) return [colDe(ks.map(k => k % A.r + 1)), colDe(ks.map(k => Math.floor(k / A.r) + 1))];
  const d = ks.map(k => k + 1);
  return A.r === 1 && A.dims.length === 2 ? filaDe(d) : colDe(d);
});
def("abs", function(args){ return mapa(arg(args, 0, "abs"), Math.abs); });
def("repmat", function(args){
  const A = arg(args, 0, "repmat");
  let reps = args.slice(1).length === 1 ? (args[1].n === 1 ? [args[1].d[0], args[1].d[0]] : args[1].d.slice()) : args.slice(1).map(x => num(x));
  while(reps.length < 2) reps.push(1);
  const [m, n, p = 1] = reps, R = A.r * m, C = A.c * n, P = A.p * p, d = new Array(R * C * P);
  for(let k = 0; k < P; k++) for(let j = 0; j < C; j++) for(let i = 0; i < R; i++) d[i + j * R + k * R * C] = A.d[(i % A.r) + (j % A.c) * A.r + (k % A.p) * A.r * A.c];
  return new Mat([R, C, P], d, A.tipo);
});
def("reshape", function(args){
  const A = args[0]; let dims = args.length === 2 ? args[1].d.slice() : args.slice(1).map(x => x.n ? x.d[0] : -1);
  const conocido = dims.filter(x => x >= 0).reduce((s, x) => s * x, 1);
  dims = dims.map(x => x < 0 ? A.n / conocido : x);
  if(dims.reduce((s, x) => s * x, 1) !== A.n) err(`reshape: can't reshape ${dimsTxt(A)} array to ${dims.join("x")} array`);
  return new Mat(dims, A.d.slice(), A.tipo);
});
def("cat", function(args){ const dim = num(args[0]), vs = args.slice(1); if(dim === 1) return vert(vs); if(dim === 2) return horz(vs); const r = vs[0].r, c = vs[0].c; return new Mat([r, c, vs.reduce((s, v) => s + v.p, 0)], vs.flatMap(v => v.d)); });
def("horzcat", function(args){ return horz(args); }); def("vertcat", function(args){ return vert(args); });
def("fliplr", function(args){ const A = args[0]; return deFilas(aFilas(A).map(f => f.reverse())); });
def("flipud", function(args){ const A = args[0]; return deFilas(aFilas(A).reverse()); });
def("floor", function(args){ return mapa(args[0], Math.floor); });
def("squeeze", function(args){ const A = args[0]; const dims = A.dims.filter(x => x !== 1); return new Mat(dims.length >= 2 ? dims : dims.length === 1 ? [dims[0], 1] : [1, 1], A.d.slice(), A.tipo); });
def("numel", function(args){ return esc(esMat(args[0]) ? args[0].n : 1); });
// Texto
def("num2str", function(args){
  const v = arg(args, 0, "num2str");
  if(esTexto(v)) return v;
  if(args[1]){ if(esTexto(args[1])) return texto(formatear(aTexto(args[1]), [v])); const p = num(args[1]); return texto(v.d.map(x => fmtG(Math.abs(x), p, false).replace(/^/, x < 0 ? "-" : "")).join("  ")); }
  if(!v.n) return texto("");
  const fin = v.d.filter(Number.isFinite);
  if(v.d.every(x => Number.isInteger(x) || !Number.isFinite(x))){
    const w = Math.max(1, digitos(Math.max(0, ...fin.map(Math.abs)))) + (v.d.some(x => x < 0) ? 1 : 0) + 2;
    const filas = aFilas(v).map(f => f.map(x => fmtCon(x, { tipo: "int" }).padStart(w)).join("").trimEnd());
    return texto(quitarComun(filas));
  }
  const dgt = Math.min(16, Math.max(Math.floor(Math.log10(Math.max(...fin.map(Math.abs)))) + 5, 5));
  if(v.n === 1) return texto(fmtG(Math.abs(v.d[0]), dgt, false).replace(/^/, v.d[0] < 0 ? "-" : ""));
  const w = dgt + 7 + (v.d.some(x => x < 0) ? 1 : 0);
  const filas = aFilas(v).map(f => f.map(x => (Number.isFinite(x) ? (x < 0 ? "-" : "") + fmtG(Math.abs(x), dgt, false) : especial(x)).padStart(w)).join("").trimEnd());
  return texto(quitarComun(filas));
});
function quitarComun(filas){ const k = Math.min(...filas.map(f => f.match(/^ */)[0].length)); return filas.map(f => f.slice(k)).join("\n"); }
def("int2str", function(args){ return BUILTIN.get("num2str").call(this, [mapa(args[0], x => Math.round(x))]); });
def("mat2str", function(args){
  const v = args[0], p = args[1] ? num(args[1]) : 15;
  const f = x => Number.isInteger(x) ? String(x) : !Number.isFinite(x) ? especial(x) : String(+x.toPrecision(p));
  if(esTexto(v)) return texto(`"${aTexto(v)}"`);
  if(v.n === 1) return texto(v.tipo === "logical" ? (v.d[0] ? "true" : "false") : f(v.d[0]));
  return texto("[" + aFilas(v).map(r => r.map(f).join(" ")).join(";") + "]");
});
def("sprintf", function(args){ const fmt = arg(args, 0, "sprintf"); return texto(formatear(escapesSi(fmt), args.slice(1))); });
def("fprintf printf", function(args){
  if(!args.length) return;
  let a = args;
  if(esMat(a[0]) && !esTexto(a[0]) && a[0].n === 1 && (a[0].d[0] === 1 || a[0].d[0] === 2) && a.length > 1) a = a.slice(1);   // fprintf(1, ...)
  if(!esTexto(a[0])){ this.escribir(formatear("%g\n", a)); return; }
  this.escribir(formatear(escapesSi(a[0]), a.slice(1)));
});
const escapesSi = fmt => escapes(aTexto(fmt));
def("disp display", function(args){ const v = arg(args, 0, "disp"); this.escribir(textoDisp(v, this.modo) + "\n"); });
def("error", function(args){
  if(!args.length) err("Invalid call to error");
  let a = args; if(a.length > 1 && esTexto(a[0]) && /^[\w-]+(:[\w-]+)+$/.test(aTexto(a[0])) && !aTexto(a[0]).includes(" ")) a = a.slice(1);
  err(formatear(escapesSi(a[0]), a.slice(1)));
});
def("warning", function(args){ if(!args.length || !esTexto(args[0])) return; const s = aTexto(args[0]); if(["on", "off", "query", "error"].includes(s)) return; this.avisar("warning: " + formatear(escapes(s), args.slice(1))); });
def("assert", function(args){
  const c = args[0];
  if(args.length >= 2 && !esTexto(args[1])){ const ok = BUILTIN.get("isequal").call(this, [c, args[1]]); if(!ok.d[0]) err("ASSERT errors: los valores no coinciden"); return; }
  if(!verdadero(c)) err(args[1] ? formatear(escapesSi(args[1]), args.slice(2)) : "assert (cond) failed");
});
def("upper toupper", function(args){ return texto(aTexto(args[0]).toUpperCase()); });
def("lower tolower", function(args){ return texto(aTexto(args[0]).toLowerCase()); });
def("strcmp", function(args){ return logico(esTexto(args[0]) && esTexto(args[1]) && aTexto(args[0]) === aTexto(args[1])); });
def("strcmpi", function(args){ return logico(esTexto(args[0]) && esTexto(args[1]) && aTexto(args[0]).toLowerCase() === aTexto(args[1]).toLowerCase()); });
def("strcat", function(args){ return texto(args.map(a => esTexto(a) ? aTexto(a).replace(/\s+$/, "") : aTexto(a)).join("")); });
def("strtrim", function(args){ return texto(aTexto(args[0]).trim()); });
def("strrep", function(args){ return texto(aTexto(args[0]).split(aTexto(args[1])).join(aTexto(args[2]))); });
def("str2num str2double", function(args){ const x = parseFloat(aTexto(args[0])); return esc(Number.isNaN(x) ? NaN : x); });
def("fieldnames", function(){ err("fieldnames: las celdas no están disponibles en el navegador"); });
def("struct", function(args){ const s = new Est(); for(let i = 0; i + 1 < args.length; i += 2) s.c.set(aTexto(args[i]), args[i + 1]); return s; });
def("rmfield", function(args){ const s = new Est(new Map(args[0].c)); s.c.delete(aTexto(args[1])); return s; });
def("clear", function(args, nout, sc){ if(!sc) return; const ns = args.map(aTexto); if(!ns.length || ns.includes("all") || ns.includes("-all")) sc.vars.clear(); else ns.forEach(n => sc.vars.delete(n)); });
def("i j I J", function(){ err("los números complejos no están disponibles en el navegador (¿usaste i o j sin darle un valor?)"); });
def("feval", function(args, nout, sc){ const f = args[0]; if(f instanceof Fh) return this.llamarFh(f, args.slice(1), nout, sc); return this.llamar(aTexto(f), args.slice(1), nout, sc); });
def("nnz", function(args){ return esc(args[0].d.filter(x => x !== 0).length); });
def("isrow", function(args){ return logico(esMat(args[0]) && args[0].r === 1 && args[0].dims.length === 2); });
def("iscolumn", function(args){ return logico(esMat(args[0]) && args[0].c === 1 && args[0].dims.length === 2); });
def("tic", () => undefined); def("toc", () => esc(0));
def("clc close clf more pause beep drawnow input keyboard pkg format echo graphics_toolkit shg rotate3d box colorbar colormap set gca gcf daspect light", () => undefined);
def("rand_semilla", () => undefined);
// Gráficos
const COLORES = { r: "#d33", g: "#2a2", b: "#26c", k: "#222", m: "#b3b", c: "#1aa", y: "#cb2", w: "#999" };
function estilo(s){ const out = { color: null, marca: null, linea: "-" }; if(!s) return out; const t = aTexto(s); for(const ch of t) if(COLORES[ch]) out.color = COLORES[ch]; const m = t.match(/[o*.x+sd^v]/); if(m) out.marca = m[0]; if(/--/.test(t)) out.linea = "--"; else if(/:/.test(t)) out.linea = ":"; else if(/-\./.test(t)) out.linea = "-."; else if(!/-/.test(t) && out.marca) out.linea = ""; return out; }
function opcionesGraf(args){ const o = {}; for(let i = 0; i + 1 < args.length; i += 2){ if(!esTexto(args[i])) break; const k = aTexto(args[i]).toLowerCase(), v = args[i + 1]; if(k === "color") o.color = esTexto(v) ? COLORES[aTexto(v)] || aTexto(v) : `rgb(${v.d.map(x => Math.round(x * 255)).join(",")})`; if(k === "linewidth") o.ancho = num(v); if(k === "linestyle") o.linea = aTexto(v); if(k === "markersize") o.tam = num(v); } return o; }
def("figure", function(){ this.fig = null; this.figura(); });
def("hold", function(args){ const f = this.figura(); f.hold = !args.length ? !f.hold : aTexto(args[0]) !== "off"; });
def("grid", function(args){ this.figura().grilla = !args.length || aTexto(args[0]) !== "off"; });
def("axis", function(args){ if(args[0] && esTexto(args[0]) && aTexto(args[0]) === "equal") this.figura().igual = true; else if(args[0] && esMat(args[0]) && !esTexto(args[0])) this.figura().limites = args[0].d.slice(); });
def("title", function(args){ this.figura().titulo = esTexto(args[0]) ? aTexto(args[0]) : ""; });
def("xlabel", function(args){ this.figura().ejes[0] = aTexto(args[0]); }); def("ylabel", function(args){ this.figura().ejes[1] = aTexto(args[0]); }); def("zlabel", function(args){ this.figura().ejes[2] = aTexto(args[0]); this.figura().tres = true; });
def("legend", function(args){ this.figura().leyenda = args.filter(esTexto).map(aTexto); });
def("view", function(args){ const f = this.figura(); if(args.length >= 2) f.vista = [num(args[0]), num(args[1])]; else if(args[0] && num(args[0]) === 3) f.tres = true; else if(args[0] && num(args[0]) === 2) f.tres = false; });
def("subplot", function(){ this.fig = null; this.figura(); });
def("text", function(args){ const f = this.figura(); const tres = args.length >= 4 && esMat(args[2]) && !esTexto(args[2]); f.textos = f.textos || []; f.textos.push({ x: num(args[0]), y: num(args[1]), z: tres ? num(args[2]) : 0, t: aTexto(args[tres ? 3 : 2]) }); if(tres) f.tres = true; });
function seriesPlot(args, tres){
  const out = []; let i = 0;
  while(i < args.length){
    if(esTexto(args[i])) break;
    let x, y, z;
    if(tres){ x = args[i]; y = args[i + 1]; z = args[i + 2]; i += 3; }
    else if(i + 1 < args.length && !esTexto(args[i + 1])){ x = args[i]; y = args[i + 1]; i += 2; }
    else { y = args[i]; x = filaDe(y.d.map((_, k) => k + 1)); i += 1; }
    let st = estilo(null);
    if(i < args.length && esTexto(args[i]) && !["color", "linewidth", "linestyle", "markersize", "marker", "displayname", "markerfacecolor"].includes(aTexto(args[i]).toLowerCase())){ st = estilo(args[i]); i++; }
    if(!x || !y || (tres && !z)) err(`${tres ? "plot3" : "plot"}: faltan datos`);
    // Una matriz: una serie por columna (si x es un vector)
    if(!tres && y.r > 1 && y.c > 1){ for(let j = 0; j < y.c; j++) out.push({ x: x.d.slice(0, y.r), y: y.d.slice(j * y.r, (j + 1) * y.r), ...st }); continue; }
    if(x.n !== y.n || (tres && z.n !== x.n)) err(`${tres ? "plot3" : "plot"}: los vectores tienen que tener el mismo largo (${x.n}, ${y.n}${tres ? ", " + z.n : ""})`);
    out.push({ x: x.d.slice(), y: y.d.slice(), z: tres ? z.d.slice() : null, ...st });
  }
  const o = opcionesGraf(args.slice(i));
  out.forEach(s => { if(o.color) s.color = o.color; if(o.ancho) s.ancho = o.ancho; if(o.linea) s.linea = o.linea; if(o.tam) s.tam = o.tam; });
  return out;
}
def("plot", function(args){ seriesPlot(args, false).forEach((s, k) => this.serie({ ...s, extra: k > 0 })); });
def("plot3", function(args){ seriesPlot(args, true).forEach((s, k) => this.serie({ ...s, extra: k > 0 })); });
def("scatter", function(args){ this.serie({ x: args[0].d.slice(), y: args[1].d.slice(), marca: "o", linea: "" }); });
def("scatter3", function(args){ this.serie({ x: args[0].d.slice(), y: args[1].d.slice(), z: args[2].d.slice(), marca: "o", linea: "" }); });
def("line", function(args){ const tres = args.length >= 3 && !esTexto(args[2]); const o = opcionesGraf(args.slice(tres ? 3 : 2)); this.serie({ x: args[0].d.slice(), y: args[1].d.slice(), z: tres ? args[2].d.slice() : null, color: o.color, linea: o.linea || "-", extra: true }); });
def("quiver3", function(args){
  const [x, y, z, u, v, w] = args.slice(0, 6).map(a => a.d.slice()); const o = opcionesGraf(args.slice(esMat(args[6]) && !esTexto(args[6]) ? 7 : 6));
  x.forEach((_, k) => this.serie({ x: [x[k], x[k] + u[k]], y: [y[k], y[k] + v[k]], z: [z[k], z[k] + w[k]], color: o.color || "#26c", linea: o.linea || "-", ancho: o.ancho, flecha: true, extra: true }));
});
def("quiver", function(args){ const [x, y, u, v] = args.slice(0, 4).map(a => a.d.slice()); x.forEach((_, k) => this.serie({ x: [x[k], x[k] + u[k]], y: [y[k], y[k] + v[k]], color: "#26c", linea: "-", flecha: true, extra: true })); });
// Los ejes de una matriz homogénea: X en rojo, Y en verde y Z en azul (como DibujarEjes del profe)
function ejes(T, L, punteado, extra, nombre){
  const o = [T.d[12], T.d[13], T.d[14]];
  [["#d33", 0], ["#2a2", 1], ["#26c", 2]].forEach(([col, j]) => this.serie({ x: [o[0], o[0] + L * T.d[j * 4]], y: [o[1], o[1] + L * T.d[1 + j * 4]], z: [o[2], o[2] + L * T.d[2 + j * 4]], color: col, linea: punteado ? ":" : "-", ancho: 2.5, flecha: true, extra: true }));
  const f = this.figura(); f.tres = true; f.igual = true; f.grilla = true;
  if(nombre){ f.textos = f.textos || []; f.textos.push({ x: o[0], y: o[1], z: o[2], t: nombre }); }
}
def("DibujarEjes dibujarEjes", function(args){ const T = arg(args, 0, "DibujarEjes"); if(T.r !== 4 || T.c !== 4) err("DibujarEjes: se esperaba una matriz homogénea de 4x4"); this.figura().hold = true; ejes.call(this, T, 3, false, true); });
def("dibujarOrigen", function(){ this.fig = null; const f = this.figura(); f.hold = true; ejes.call(this, eye4(), 3, true, true); });
def("dibujarSistemasDeEjesCoordenadosDeRobot", function(args){
  this.fig = null; const f = this.figura(); f.hold = true; f.titulo = esTexto(args[0]) ? aTexto(args[0]) : "";
  let T = eye4(), ant = null;
  const dibujar = (M, k) => { ejes.call(this, M, 100, false, true, `S${k}`); if(ant) this.serie({ x: [ant.d[12], M.d[12]], y: [ant.d[13], M.d[13]], z: [ant.d[14], M.d[14]], color: "#222", linea: "-.", ancho: 2, extra: true }); ant = M; };
  dibujar(T, 0);
  args.slice(1).forEach((A, k) => { if(!esMat(A) || A.r !== 4 || A.c !== 4) err("Cada argumento debe ser una matriz 4x4 (A01, A12, ...)"); T = mult(T, A); dibujar(T, k + 1); });
});
def("animar_trayectoria", function(){ this.avisar("(la animación no se muestra en el navegador: probala en Octave)"); });
// Como la del profe: posiciones y velocidades en el tiempo, una figura para cada una
def("Dibujar_Temporal", function(args){
  if(args.length < 3) err("Dibujar_Temporal: se esperan (T_total, Q_total, DQ_total)");
  [[args[1], "Posiciones"], [args[2], "Velocidades"]].forEach(([m, tit]) => {
    this.fig = null;
    const f = this.figura();
    seriesPlot([args[0], m], false).forEach((x, k) => this.serie({ ...x, ancho: 2, extra: k > 0 }));
    Object.assign(f, { titulo: tit, grilla: true }); f.ejes[0] = "tiempo";
  });
});

/* ---- Las funciones del profe (1º y 2º parcial), con los mismos cálculos que sus .m ---- */
const eye4 = () => { const m = ceros(4, 4); for(let i = 0; i < 4; i++) m.d[i * 5] = 1; return m; };
def("Rotx", function(args){ const a = num(arg(args, 0, "Rotx")), c = cosd(a), s = sind(a); return deFilas([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]); });
def("Roty", function(args){ const a = num(arg(args, 0, "Roty")), c = cosd(a), s = sind(a); return deFilas([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]); });
def("Rotz", function(args){ const a = num(arg(args, 0, "Rotz")), c = cosd(a), s = sind(a); return deFilas([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]); });
def("Traslacion", function(args){
  if(args.length > 1) err("Traslacion: recibe un solo vector, Traslacion([dx dy dz]) (no tres números sueltos)");
  const v = arg(args, 0, "Traslacion").d.slice();
  if(v.length < 1 || v.length > 3){ this.escribir("Dimension no valida\n"); return; }
  while(v.length < 3) v.push(0);
  return deFilas([[1, 0, 0, v[0]], [0, 1, 0, v[1]], [0, 0, 1, v[2]], [0, 0, 0, 1]]);
});
function dh(q, d, a, al, rad){
  const cq = rad ? Math.cos(q) : cosd(q), sq = rad ? Math.sin(q) : sind(q), ca = rad ? Math.cos(al) : cosd(al), sa = rad ? Math.sin(al) : sind(al);
  return deFilas([[cq, -sq * ca, sq * sa, a * cq], [sq, cq * ca, -cq * sa, a * sq], [0, sa, ca, d], [0, 0, 0, 1]]);
}
const esRad = u => u !== undefined && !(esTexto(u) && aTexto(u).toLowerCase() === "deg");
def("matrizDenavitHartenberg", function(args){ return dh(num(arg(args, 0, "matrizDenavitHartenberg")), num(arg(args, 1, "matrizDenavitHartenberg")), num(arg(args, 2, "matrizDenavitHartenberg")), num(arg(args, 3, "matrizDenavitHartenberg")), esRad(args[4])); });
function cd(theta, d, a, al, rad){
  const n = theta.length;
  if(d.length !== n || a.length !== n || al.length !== n) err("theta, d, a, alpha deben tener la misma longitud");
  let T = eye4(); const origins = ceros(3, n + 1), Ts = [];
  for(let i = 0; i < n; i++){ const A = dh(theta[i], d[i], a[i], al[i], rad); Ts.push(A); T = mult(T, A); for(let k = 0; k < 3; k++) origins.d[k + (i + 1) * 3] = T.d[12 + k]; }
  return { T, origins, Tsist: new Mat([4, 4, n], Ts.flatMap(A => A.d)) };
}
def("cinematica_directa", function(args){
  const [th, d, a, al] = [0, 1, 2, 3].map(i => arg(args, i, "cinematica_directa").d.slice());
  const r = cd(th, d, a, al, esRad(args[4]));
  return [r.T, r.origins, r.Tsist];
});
function tiposDe(t, n){ const s = aTexto(t).toUpperCase().replace(/\s/g, ""); if(s.length !== n) err(`tipo debe tener ${n} caracteres`); return s; }
function articular(q, tipo, qoff, doff){ const th = qoff.slice(), d = doff.slice(); q.forEach((x, i) => { if(tipo[i] === "R") th[i] += x; else if(tipo[i] === "P") d[i] += x; else err(`tipo(${i + 1}) invalido: ${tipo[i]}`); }); return [th, d]; }
function jacAnalitico(q, tipo, qoff, doff, a, al, rad){
  const n = q.length, [th, d] = articular(q, tipo, qoff, doff);
  const Tc = [eye4()]; for(let i = 0; i < n; i++) Tc.push(mult(Tc[i], dh(th[i], d[i], a[i], al[i], rad)));
  const Tn = Tc[n], pn = [12, 13, 14].map(k => Tn.d[k]);
  const J = ceros(6, n);
  for(let i = 0; i < n; i++){
    const z = [8, 9, 10].map(k => Tc[i].d[k]), p = [12, 13, 14].map(k => Tc[i].d[k]);
    let jv, jw;
    if(tipo[i] === "R"){
      const r = [pn[0] - p[0], pn[1] - p[1], pn[2] - p[2]];
      jv = [z[1] * r[2] - z[2] * r[1], z[2] * r[0] - z[0] * r[2], z[0] * r[1] - z[1] * r[0]];
      jw = [0, 1, 2].map(c => Tn.d[c * 4] * z[0] + Tn.d[1 + c * 4] * z[1] + Tn.d[2 + c * 4] * z[2]);   // R_n' * z
    } else { jv = z; jw = [0, 0, 0]; }
    const k = !rad && tipo[i] === "R" ? Math.PI / 180 : 1;
    [...jv, ...jw].forEach((x, f) => { J.d[f + i * 6] = x * k; });
  }
  return J;
}
function ejeAngulo(R){
  let c = (R[0][0] + R[1][1] + R[2][2] - 1) / 2; c = Math.max(-1, Math.min(1, c));
  const ang = Math.acos(c);
  if(Math.abs(ang) < 1e-9) return [0, 0, 0];
  const k = 1 / (2 * Math.sin(ang));
  return [(R[2][1] - R[1][2]) * k * ang, (R[0][2] - R[2][0]) * k * ang, (R[1][0] - R[0][1]) * k * ang];
}
function jacNumerico(q, tipo, qoff, doff, a, al, rad){
  const n = q.length, [th, d] = articular(q, tipo, qoff, doff);
  const T0 = cd(th, d, a, al, rad).T, R0 = aFilas(T0).slice(0, 3).map(f => f.slice(0, 3));
  const hR = rad ? 1e-6 : 1e-3, hP = 1e-3, J = ceros(6, n);
  const relativa = T => { const R = aFilas(T).slice(0, 3).map(f => f.slice(0, 3)); return [0, 1, 2].map(i => [0, 1, 2].map(j => R0[0][i] * R[0][j] + R0[1][i] * R[1][j] + R0[2][i] * R[2][j])); };
  for(let i = 0; i < n; i++){
    const thp = th.slice(), dp = d.slice(), thm = th.slice(), dm = d.slice(); let h;
    if(tipo[i] === "R"){ thp[i] += hR; thm[i] -= hR; h = hR; } else { dp[i] += hP; dm[i] -= hP; h = hP; }
    const Tp = cd(thp, dp, a, al, rad).T, Tm = cd(thm, dm, a, al, rad).T;
    const dpos = [12, 13, 14].map(k => (Tp.d[k] - Tm.d[k]) / (2 * h));
    const ap = ejeAngulo(relativa(Tp)), am = ejeAngulo(relativa(Tm));
    [...dpos, ...ap.map((x, k) => (x - am[k]) / (2 * h))].forEach((x, f) => { J.d[f + i * 6] = x; });
  }
  return J;
}
function argsJac(args, nombre){
  const q = arg(args, 0, nombre).d.slice(), n = q.length, tipo = tiposDe(arg(args, 1, nombre), n);
  return [q, tipo, arg(args, 2, nombre).d.slice(), arg(args, 3, nombre).d.slice(), arg(args, 4, nombre).d.slice(), arg(args, 5, nombre).d.slice(), esRad(args[6])];
}
def("jacobiano_analitico", function(args){ return jacAnalitico(...argsJac(args, "jacobiano_analitico")); });
def("jacobiano_numerico", function(args){ return jacNumerico(...argsJac(args, "jacobiano_numerico")); });
def("cinematica_inversa", function(args, nout){
  const nombre = "cinematica_inversa";
  const pd = arg(args, 0, nombre).d.slice(), q0 = arg(args, 1, nombre).d.slice(), n = q0.length;
  if(pd.length !== 3) err("cinematica_inversa: pd tiene que ser la posición deseada [x; y; z]");
  const tipo = tiposDe(arg(args, 2, nombre), n), qoff = arg(args, 3, nombre).d.slice(), doff = arg(args, 4, nombre).d.slice(), a = arg(args, 5, nombre).d.slice(), al = arg(args, 6, nombre).d.slice();
  const rad = esRad(args[7]), uni = args[7] && esTexto(args[7]) ? aTexto(args[7]) : "deg";
  if([qoff, doff, a, al].some(x => x.length !== n)) err(`cinematica_inversa: q0, q_offset, d_offset, a y alpha tienen que tener ${n} elementos`);
  const op = args[8] instanceof Est ? args[8].c : new Map();
  const o = (k, def) => op.has(k) ? op.get(k) : def;
  const maxIter = num(o("max_iter", esc(200))), tol = num(o("tol_pos", esc(1e-3))), lambda = num(o("lambda", esc(0.05))), paso = num(o("alpha_step", esc(1)));
  const analitico = verdadero(o("use_analitico", logico(true))), verbose = verdadero(o("verbose", logico(false))), wrap = verdadero(o("wrap", logico(true)));
  const qmin = o("q_min", vacio()).d.slice(), qmax = o("q_max", vacio()).d.slice(), lim = qmin.length > 0 && qmax.length > 0;
  let q = q0.slice();
  if(lim){ if(qmin.length !== n || qmax.length !== n) err(`q_min/q_max deben tener ${n} elementos`); q = q.map((x, i) => Math.min(Math.max(x, qmin[i]), qmax[i])); }
  let ok = false, errPos = NaN, k = 0, th = [], d = [];
  for(k = 1; k <= maxIter; k++){
    [th, d] = articular(q, tipo, qoff, doff);
    const T = cd(th, d, a, al, rad).T, e = [0, 1, 2].map(i => pd[i] - T.d[12 + i]);
    errPos = Math.hypot(...e);
    if(verbose) this.escribir(formatear("  iter %3d  err=%.4e mm  q=[%s]\n", [esc(k), esc(errPos), texto(formatear("%6.2f ", [filaDe(q)]))]));
    if(errPos < tol){ ok = true; break; }
    const J = (analitico ? jacAnalitico : jacNumerico)(q, tipo, qoff, doff, a, al, rad);
    const Jp = new Mat([3, n], Array.from({ length: 3 * n }, (_, t) => J.d[(t % 3) + Math.floor(t / 3) * 6]));
    const JJt = mult(Jp, transp(Jp)); for(let i = 0; i < 3; i++) JJt.d[i * 4] += lambda * lambda;
    const dq = mult(transp(Jp), resolver(JJt, colDe(e), () => {})).d;
    let step = dq.map(x => paso * x);
    if(lim){
      const tb = 1e-9;
      step = step.map((s, i) => ((q[i] <= qmin[i] + tb && s < 0) || (q[i] >= qmax[i] - tb && s > 0)) ? 0 : s);
      let f = 1;
      step.forEach((s, i) => { if(s > 0){ const m = qmax[i] - q[i]; if(s > m) f = Math.min(f, m / s); } else if(s < 0){ const m = qmin[i] - q[i]; if(s < m) f = Math.min(f, m / s); } });
      step = step.map(s => Math.max(0, f) * s);
      q = q.map((x, i) => Math.min(Math.max(x + step[i], qmin[i]), qmax[i]));
    } else q = q.map((x, i) => x + step[i]);
  }
  if(k > maxIter) k = maxIter;
  if(wrap && !lim){
    const per = rad ? 2 * Math.PI : 360;
    q = q.map((x, i) => { if(tipo[i] !== "R") return x; const delta = x - q0[i]; const m = (delta + per / 2) - Math.floor((delta + per / 2) / per) * per; return q0[i] + (m - per / 2); });
  }
  const info = new Est();
  info.c.set("iters", esc(k)); info.c.set("err_pos", esc(errPos)); info.c.set("lambda", esc(lambda)); info.c.set("unidad", texto(uni));
  info.c.set("en_q_min", lim ? new Mat([n, 1], q.map((x, i) => +(x <= qmin[i] + 1e-6)), "logical") : new Mat([n, 1], new Array(n).fill(0), "logical"));
  info.c.set("en_q_max", lim ? new Mat([n, 1], q.map((x, i) => +(x >= qmax[i] - 1e-6)), "logical") : new Mat([n, 1], new Array(n).fill(0), "logical"));
  return [colDe(q), colDe(th), colDe(d), logico(ok), info];
});
def("generacion_de_trayectorias", function(args){
  const qi = arg(args, 0, "generacion_de_trayectorias").d.slice(), qf = arg(args, 1, "generacion_de_trayectorias").d.slice(), wmax = arg(args, 2, "generacion_de_trayectorias").d.slice(), h = num(arg(args, 3, "generacion_de_trayectorias"));
  const dof = Math.max(qf.length, 1);
  const w = wmax.length === 1 ? qf.map(() => wmax[0]) : wmax;
  if(w.length !== qf.length || qi.length !== qf.length) err("generacion_de_trayectorias: qi, qf y wmax tienen que tener el mismo largo");
  const T = Math.max(...qf.map((x, i) => Math.abs(x - qi[i]) / w[i]));
  if(T === 0) return [deFilas([qi, qf]), ceros(2, dof), colDe([0, h])];
  const wT = qf.map((x, i) => (x - qi[i]) / T), n = Math.max(2, Math.ceil(T / h) + 1);
  const t = Array.from({ length: n }, (_, i) => i * T / (n - 1)); t[n - 1] = T;
  return [deFilas(t.map(tt => qi.map((x, j) => x + tt * wT[j]))), deFilas(t.map(() => wT.slice())), colDe(t)];
});

/* ================= Hacia JavaScript ================= */
function aJS(v){
  if(v instanceof Est){ const o = {}; for(const [k, x] of v.c) o[k] = aJS(x); return o; }
  if(v instanceof Fh) return { funcion: v.texto };
  if(v.tipo === "char") return aTexto(v);
  if(v.n === 1) return v.tipo === "logical" ? !!v.d[0] : v.d[0];
  if(v.p > 1) return Array.from({ length: v.p }, (_, k) => aFilas(new Mat([v.r, v.c], v.d.slice(k * v.r * v.c, (k + 1) * v.r * v.c))));
  return aFilas(v);
}
function correr(codigo, opts = {}){
  const it = new Interprete(opts);
  let sc = null, error = null;
  try { sc = it.correr(String(codigo).replace(/\r\n?/g, "\n")); }
  catch(e){
    if(!(e instanceof OctErr) && !(e instanceof RangeError)) throw e;
    const msg = e instanceof RangeError ? "el cálculo se fue de tamaño (¿una recursión sin fin?)" : e.message;
    error = { msg, linea: it.linea || null, archivo: it.archivo };
    sc = it.raiz;
  }
  const vars = {};
  if(sc) for(const [k, v] of sc.vars) vars[k] = aJS(v);
  return { salida: it.salida.join(""), vars, error, graficos: it.graficos.filter(f => f.series.length) };
}
const API = { correr, version: 1 };
if(typeof module !== "undefined" && module.exports) module.exports = API; else raiz.Octave = API;
})(typeof window !== "undefined" ? window : globalThis);
