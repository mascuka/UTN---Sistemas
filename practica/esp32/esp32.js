/* La ESP32 en el navegador, para la Práctica de Tecnologías para la Automatización.
   Un intérprete chico de C++ para Arduino (lo que se usa en los casos de la cátedra) con la placa de la cátedra
   simulada: LED integrado (GPIO 2), LED del pin 23, relé (14), pulsador (19, con pull-up), potenciómetro (32),
   DHT22 (33), touch (13 y 4) y el display OLED por I2C; el monitor serie, y WiFi, ThingSpeak y MQTT de mentira
   (se ven en un registro). Corre con tiempo virtual: delay() espera sin trabar la página y millis() avanza.

   Uso:  const s = ESP32.crear(codigo, { archivos: [{ nombre: "config.h", texto }] })
         s.error                → null | { msg, linea, archivo }   (si no compila)
         s.avanzar(hastaMs, limitePasos?)   corre hasta ese tiempo virtual
         s.entrada({ boton: true } | { pote: 2048 } | { dht: { t, h } } | { touch: { 13: 10 } } | { serial: "LUZ_ON\n" } | { mqtt: { topic, payload } })
         s.estado()             → lo que hay que dibujar (pines, PWM, display, monitor, nube, tiempo, error)
         s.h                    → la historia (cambios de cada pin, PWM, lo que salió por Serial, envíos…)
         ESP32.probar(codigo, prueba)  corre una prueba sin pantalla (ver probar()) */
(function(raiz){
"use strict";

class CppErr extends Error { constructor(m, linea, archivo){ super(m); this.linea = linea; this.archivo = archivo; } }
const err = (m, t) => { throw new CppErr(m, t && t.linea, t && t.archivo); };

/* ================= Léxico ================= */
const OPS = ["<<=", ">>=", "...", "==", "!=", "<=", ">=", "&&", "||", "++", "--", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<", ">>", "->", "::"];
function lexico(src, archivo){
  const toks = [], n = src.length;
  let i = 0, linea = 1, inicio = true;
  const add = (t, v, x) => { toks.push({ t, v, linea, archivo, ...x }); inicio = false; };
  while(i < n){
    const c = src[i];
    if(c === "\n"){ linea++; i++; inicio = true; continue; }
    if(c === " " || c === "\t" || c === "\r" || c === "\f" || c === "\v"){ i++; continue; }
    if(c === "/" && src[i + 1] === "/"){ while(i < n && src[i] !== "\n") i++; continue; }
    if(c === "/" && src[i + 1] === "*"){
      const f = src.indexOf("*/", i + 2), fin = f < 0 ? n : f + 2;
      for(let k = i; k < fin; k++) if(src[k] === "\n") linea++;
      i = fin; continue;
    }
    if(c === "#" && inicio){
      let j = i + 1, txt = "";
      const l0 = linea;
      while(j < n && src[j] !== "\n"){
        if(src[j] === "\\" && src[j + 1] === "\n"){ j += 2; linea++; continue; }
        if(src[j] === "/" && src[j + 1] === "/"){ while(j < n && src[j] !== "\n") j++; break; }
        txt += src[j]; j++;
      }
      toks.push({ t: "dir", v: txt.trim(), linea: l0, archivo }); i = j; continue;
    }
    const num = /^(0[xX][0-9a-fA-F]+|0[bB][01]+|(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)([uUlLfF]*)/.exec(src.slice(i, i + 40));
    if(num && /[\d.]/.test(c) && !(c === "." && !/\d/.test(src[i + 1] || ""))){
      const txt = num[1], suf = num[2].toLowerCase();
      let v, flot = false;
      if(/^0[xX]/.test(txt)) v = parseInt(txt.slice(2), 16);
      else if(/^0[bB]/.test(txt)) v = parseInt(txt.slice(2), 2);
      else { v = parseFloat(txt); flot = /[.eE]/.test(txt) || suf.includes("f"); }
      add("num", v, { flot, sinSigno: suf.includes("u") });
      i += num[0].length; continue;
    }
    if(/[A-Za-z_]/.test(c)){
      let j = i + 1; while(j < n && /[A-Za-z0-9_]/.test(src[j])) j++;
      const w = src.slice(i, j), alt = { and: "&&", or: "||", not: "!", not_eq: "!=" }[w];
      if(alt) add("op", alt); else add("id", w);
      i = j; continue;
    }
    if(c === '"' || c === "'"){
      let j = i + 1, s = "";
      while(j < n && src[j] !== c){
        if(src[j] === "\n") err("falta cerrar las comillas", { linea, archivo });
        if(src[j] === "\\"){
          const e = src[j + 1]; j += 2;
          if(e === "n") s += "\n"; else if(e === "t") s += "\t"; else if(e === "r") s += "\r"; else if(e === "0") s += "\0";
          else if(e === "x"){ const h = /^[0-9a-fA-F]{1,2}/.exec(src.slice(j))[0]; s += String.fromCharCode(parseInt(h, 16)); j += h.length; }
          else s += e;
          continue;
        }
        s += src[j]; j++;
      }
      if(j >= n) err("falta cerrar las comillas", { linea, archivo });
      if(c === '"') add("str", s); else add("chr", s.charCodeAt(0) || 0);
      i = j + 1; continue;
    }
    const op = OPS.find(o => src.startsWith(o, i)) || c;
    add("op", op); i += op.length;
  }
  return toks;
}

/* ================= Preprocesador: #define, #include "x.h" y #ifdef ================= */
function preprocesar(texto, nombre, archivos, libs){
  const macros = new Map();
  const salida = [];
  const pila = [];   // #if: true si se incluye
  const activo = () => pila.every(x => x);
  function procesar(src, archivo, prof){
    if(prof > 8) err("demasiados #include anidados");
    for(const t of lexico(src, archivo)){
      if(t.t !== "dir"){ if(activo()) salida.push(t); continue; }
      const m = /^(\w+)\s*(.*)$/.exec(t.v) || ["", "", ""];
      const d = m[1], resto = m[2];
      if(d === "ifdef" || d === "ifndef"){ const def = macros.has(resto.trim()); pila.push(d === "ifdef" ? def : !def); continue; }
      if(d === "if"){ pila.push(!/^0\b/.test(resto.trim())); continue; }
      if(d === "else"){ pila[pila.length - 1] = !pila[pila.length - 1]; continue; }
      if(d === "elif"){ pila[pila.length - 1] = false; continue; }
      if(d === "endif"){ pila.pop(); continue; }
      if(!activo()) continue;
      if(d === "define"){
        const md = /^(\w+)(\(([^)]*)\))?\s*(.*)$/.exec(resto);
        if(!md) err("#define mal escrito", t);
        const cuerpo = lexico(md[4] || "", archivo).map(x => ({ ...x, linea: t.linea }));
        macros.set(md[1], { params: md[2] ? md[3].split(",").map(s => s.trim()).filter(Boolean) : null, cuerpo });
        continue;
      }
      if(d === "undef"){ macros.delete(resto.trim()); continue; }
      if(d === "include"){
        const q = /^"([^"]+)"/.exec(resto), a = /^<([^>]+)>/.exec(resto);
        const nom = (q || a || [])[1] || "";
        libs.add(nom.replace(/\.h$/, ""));
        if(q){
          const f = archivos.find(x => x.nombre === nom || x.nombre.endsWith("/" + nom));
          if(f){ procesar(f.texto, f.nombre, prof + 1); continue; }
          if(!/^(config|secrets|OTA)\.h$/.test(nom) && !LIBRERIAS_CONOCIDAS.has(nom.replace(/\.h$/, ""))) err(`no encuentro "${nom}"`, t);
        }
        continue;
      }
      // #pragma, #error, #warning y otras: se ignoran
    }
  }
  procesar(texto, nombre, 0);
  // Las macros se expanden acá (con la línea donde se usan)
  const out = [], usando = new Set();
  function expandir(toks, i, dest, linea){
    const t = toks[i];
    const mac = t.t === "id" && macros.get(t.v);
    if(!mac || usando.has(t.v)){ dest.push(linea ? { ...t, linea, archivo: t.archivo } : t); return i + 1; }
    let k = i + 1, args = null;
    if(mac.params){
      if(!(toks[k] && toks[k].t === "op" && toks[k].v === "(")){ dest.push(t); return i + 1; }
      args = [[]]; let prof = 0; k++;
      for(; k < toks.length; k++){
        const x = toks[k];
        if(x.t === "op" && (x.v === "(" || x.v === "[")) prof++;
        if(x.t === "op" && (x.v === ")" || x.v === "]")){ if(prof === 0) break; prof--; }
        if(x.t === "op" && x.v === "," && prof === 0){ args.push([]); continue; }
        args[args.length - 1].push(x);
      }
      k++;
    }
    let cuerpo = mac.cuerpo;
    if(mac.params) cuerpo = cuerpo.flatMap(x => { const j = x.t === "id" ? mac.params.indexOf(x.v) : -1; return j >= 0 ? (args[j] || []) : [x]; });
    usando.add(t.v);
    const tmp = [];
    for(let j = 0; j < cuerpo.length;) j = expandir(cuerpo, j, tmp, linea || t.linea);
    usando.delete(t.v);
    dest.push(...tmp.map(x => ({ ...x, linea: linea || t.linea, archivo: t.archivo })));
    return k;
  }
  for(let i = 0; i < salida.length;) i = expandir(salida, i, out, 0);
  out.push({ t: "eof", linea: (salida[salida.length - 1] || { linea: 1 }).linea, archivo: nombre });
  return { toks: out, macros };
}

/* ================= Tipos ================= */
const ENTEROS = new Set(["int", "long", "short", "char", "byte", "word", "bool", "boolean", "size_t", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "int8_t", "int16_t", "int32_t", "int64_t", "unsigned", "signed"]);
const PALABRAS_TIPO = new Set([...ENTEROS, "float", "double", "void", "String", "auto", "const", "volatile", "static", "IRAM_ATTR", "unsigned", "signed", "constexpr", "inline", "extern", "struct", "IPAddress"]);
// Las clases de las librerías que entiende el simulador
const CLASES = new Set(["WiFiConnectionHandler", "DHT", "Adafruit_SH1106G", "Adafruit_SSD1306", "WiFiClient", "WiFiClientSecure", "PubSubClient", "Servo", "Ticker", "WiFiServer", "HTTPClient", "UniversalTelegramBot", "WebServer", "String", "IPAddress"]);
const LIBRERIAS_CONOCIDAS = new Set(["Arduino", "WiFi", "DHT", "Adafruit_Sensor", "Adafruit_GFX", "Adafruit_SH110X", "Adafruit_SSD1306", "Wire", "SPI", "ThingSpeak", "PubSubClient", "EEPROM", "Ticker", "ESP32Servo", "Servo", "HTTPClient", "WiFiClientSecure", "UniversalTelegramBot", "ArduinoJson", "WebServer", "ArduinoOTA", "ElegantOTA", "AsyncElegantOTA", "Update", "ESPmDNS", "splash", "ArduinoIoTCloud", "Arduino_ConnectionHandler", "thingProperties", "AsyncTCP", "ESPAsyncWebServer", "math", "stdio", "string"]);
const esEnteroT = t => t && ENTEROS.has(t.replace(/^unsigned /, "").replace(/^signed /, "").replace(/ int$/, "")) || /^unsigned/.test(t || "");
const esNumT = t => esEnteroT(t) || t === "float" || t === "double";
const sinSignoT = t => /^unsigned|^uint|^size_t|^byte|^word/.test(t || "");
/* Convierte un valor al tipo de la variable (como en C: corta los decimales y da la vuelta) */
function aTipo(v, tipo){
  if(!tipo || tipo === "auto") return v;
  if(tipo === "String") return aString(v);
  if(tipo === "char*" || tipo === "IPAddress") return typeof v === "string" ? v : aString(v);
  if(tipo === "bool" || tipo === "boolean") return typeof v === "string" ? v.length > 0 : !!v && !Number.isNaN(v);
  if(tipo === "float" || tipo === "double") return typeof v === "boolean" ? +v : typeof v === "number" ? v : err(`no se puede convertir ${JSON.stringify(v)} a ${tipo}`);
  if(esEnteroT(tipo)){
    if(typeof v === "string"){ if(v.length === 1 && /char/.test(tipo)) v = v.charCodeAt(0); else err(`no se puede guardar un texto en un ${tipo}`); }
    let x = typeof v === "boolean" ? +v : Math.trunc(v);
    if(!Number.isFinite(x)) x = 0;
    const t = tipo.replace(/^(const|volatile|static) /, "");
    if(/^(unsigned char|byte|uint8_t)$/.test(t)) return x & 0xFF;
    if(/^(char|int8_t|signed char)$/.test(t)) return (x << 24) >> 24;
    if(/^(short|int16_t)$/.test(t)) return (x << 16) >> 16;
    if(/^(unsigned short|uint16_t|word)$/.test(t)) return x & 0xFFFF;
    if(/64|long long/.test(t)) return x;
    if(sinSignoT(t) || /^unsigned/.test(t)) return x >>> 0;
    return x | 0;
  }
  return v;
}
/* Como imprime Arduino: float con 2 decimales, bool como 1/0 */
function aString(v, tipo){
  if(typeof v === "string") return v;
  if(typeof v === "boolean") return v ? "1" : "0";
  if(typeof v === "number"){
    if(tipo === "char") return String.fromCharCode(v);
    if(tipo === "float" || tipo === "double" || (!Number.isInteger(v) && tipo !== "int")) return flotante(v, 2);
    return String(v);
  }
  if(v && v.aTexto) return v.aTexto();
  if(Array.isArray(v)) return v.map(x => String.fromCharCode(x)).join("").replace(/\0.*$/, "");
  return String(v);
}
function flotante(v, dec){
  if(Number.isNaN(v)) return "nan";
  if(!Number.isFinite(v)) return v > 0 ? "inf" : "-inf";
  const s = (Math.round(v * 10 ** dec + (v >= 0 ? 1e-9 : -1e-9)) / 10 ** dec).toFixed(dec);
  return s === "-0" || /^-0\.0*$/.test(s) ? s.slice(1) : s;
}
/* printf de C */
function formatear(fmt, args){
  let k = 0;
  return fmt.replace(/%([-+ 0#]*)(\d+|\*)?(?:\.(\d+))?(hh|h|ll|l|L|z)?([diouxXeEfgGcs%])/g, (m, flags, ancho, prec, _, conv) => {
    if(conv === "%") return "%";
    if(ancho === "*") ancho = String(args[k++]);
    let v = args[k++], s;
    if(v === undefined) v = 0;
    switch(conv){
      case "d": case "i": { const x = Math.trunc(typeof v === "boolean" ? +v : typeof v === "string" ? v.charCodeAt(0) : v); s = String(Math.abs(x)); if(x < 0) s = "-" + s; else if(flags.includes("+")) s = "+" + s; break; }
      case "u": s = String(Math.trunc(v) >>> 0); break;
      case "x": s = (Math.trunc(v) >>> 0).toString(16); break;
      case "X": s = (Math.trunc(v) >>> 0).toString(16).toUpperCase(); break;
      case "o": s = (Math.trunc(v) >>> 0).toString(8); break;
      case "f": s = flotante(+v, prec == null ? 6 : +prec); if(flags.includes("+") && +v >= 0) s = "+" + s; break;
      case "e": case "E": { s = (+v).toExponential(prec == null ? 6 : +prec).replace(/e([+-])(\d)$/, "e$10$2"); if(conv === "E") s = s.toUpperCase(); break; }
      case "g": case "G": s = String(+(+v).toPrecision(prec == null ? 6 : Math.max(1, +prec))); break;
      case "c": s = typeof v === "string" ? v[0] || "" : String.fromCharCode(v); break;
      case "s": s = aString(v); if(prec != null) s = s.slice(0, +prec); break;
    }
    if(ancho && s.length < +ancho) s = flags.includes("-") ? s.padEnd(+ancho) : flags.includes("0") && /[dioxXuef]/.test(conv) ? (s[0] === "-" ? "-" + s.slice(1).padStart(+ancho - 1, "0") : s.padStart(+ancho, "0")) : s.padStart(+ancho);
    return s;
  });
}

/* ================= Sintaxis ================= */
function sintaxis(toks){
  let k = 0;
  const ver = (d = 0) => toks[Math.min(k + d, toks.length - 1)];
  const es = (t, v, d = 0) => ver(d).t === t && (v === undefined || ver(d).v === v);
  const op = (v, d = 0) => es("op", v, d);
  const tomar = () => toks[k++];
  const espera = (v, que) => { if(!op(v)) err(`${que || `falta "${v}"`}${ver().t === "eof" ? " (terminó el código)" : ` y vino "${ver().v ?? ver().t}"`}`, ver()); return tomar(); };
  const nombre = que => { if(!es("id")) err(que || "falta un nombre", ver()); return tomar().v; };
  const clases = new Set(CLASES);
  const funciones = new Map();   // nombre → tipo que devuelve (se juntan antes, como hace el IDE de Arduino)

  // ¿Empieza un tipo acá? (int, const char*, DHT, Adafruit_SH1106G…)
  function esTipo(d = 0){
    const t = ver(d);
    if(t.t !== "id") return false;
    if(PALABRAS_TIPO.has(t.v) || clases.has(t.v)) return true;
    // Una clase que no conozco: "Clase nombre(" o "Clase nombre;" o "Clase nombre ="
    const s = ver(d + 1), s2 = ver(d + 2);
    return s.t === "id" && !PALABRAS_TIPO.has(s.v) && s2.t === "op" && ["(", "=", ";", ",", "["].includes(s2.v) && /^[A-Z]/.test(t.v);
  }
  function tipo(){
    const quals = [];
    let base = null, uns = null, largos = 0;
    while(es("id")){
      const v = ver().v;
      if(["const", "volatile", "static", "IRAM_ATTR", "constexpr", "inline", "extern", "struct"].includes(v)){ tomar(); if(v === "static") quals.push("static"); if(v === "const" || v === "constexpr") quals.push("const"); continue; }
      if(v === "unsigned" || v === "signed"){ tomar(); uns = v; continue; }
      if(v === "long"){ tomar(); largos++; continue; }
      if(v === "short"){ tomar(); base = "short"; continue; }
      if(base || (largos && !["int", "double"].includes(v)) || (uns && !["int", "char", "long", "short"].includes(v))) break;
      if(PALABRAS_TIPO.has(v) || clases.has(v) || /^[A-Z]/.test(v)){ base = tomar().v; if(!PALABRAS_TIPO.has(base)) clases.add(base); continue; }
      break;
    }
    if(!base && !uns && !largos) err("falta el tipo", ver());
    if(largos && (!base || base === "int")) base = largos > 1 ? "long long" : "long";
    if(largos && base === "double") base = "double";
    if(!base) base = "int";
    if(base === "boolean") base = "bool";
    if(uns === "unsigned") base = "unsigned " + (base === "int" ? "int" : base);
    let ptr = 0;
    while(op("*") || op("&")){ if(tomar().v === "*") ptr++; }
    let t = base;
    if(ptr) t = (base === "char" || base === "unsigned char" || base === "byte" || base === "uint8_t") ? (base === "char" ? "char*" : "byte*") : base + "*";
    return { t, const: quals.includes("const"), estatico: quals.includes("static") };
  }

  // ---- Expresiones (con precedencia de C)
  const BIN = [["||"], ["&&"], ["|"], ["^"], ["&"], ["==", "!="], ["<", ">", "<=", ">="], ["<<", ">>"], ["+", "-"], ["*", "/", "%"]];
  const ASIG = new Set(["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="]);
  function expr(){ const e = asignacion(); if(op(",") && false) {} return e; }
  function exprComa(){ let e = asignacion(); while(op(",")){ const t = tomar(); e = { k: "coma", a: e, b: asignacion(), linea: t.linea, archivo: t.archivo }; } return e; }
  function asignacion(){
    const izq = ternario();
    if(es("op") && ASIG.has(ver().v)){ const t = tomar(); return { k: "asig", op: t.v, a: izq, b: asignacion(), linea: t.linea, archivo: t.archivo }; }
    return izq;
  }
  function ternario(){
    const c = binaria(0);
    if(op("?")){ const t = tomar(); const a = asignacion(); espera(":"); const b = asignacion(); return { k: "tern", c, a, b, linea: t.linea, archivo: t.archivo }; }
    return c;
  }
  function binaria(nivel){
    if(nivel >= BIN.length) return unaria();
    let a = binaria(nivel + 1);
    while(es("op") && BIN[nivel].includes(ver().v)){ const t = tomar(); a = { k: "bin", op: t.v, a, b: binaria(nivel + 1), linea: t.linea, archivo: t.archivo }; }
    return a;
  }
  function unaria(){
    const t = ver();
    if(t.t === "op" && ["!", "-", "+", "~", "++", "--", "*", "&"].includes(t.v)){ tomar(); return { k: "un", op: t.v, a: unaria(), linea: t.linea, archivo: t.archivo }; }
    // (tipo) x
    if(op("(") && esTipo(1)){
      let j = 1, prof = 0;
      while(!(op(")", j) && prof === 0)){ if(op("(", j)) prof++; if(op(")", j)) prof--; if(es("eof", undefined, j)) break; j++; }
      const despues = ver(j + 1);
      if(!(despues.t === "op" && [";", ")", ",", "]", "+", "-", "*", "/", "==", "<", ">", "&&", "||", "?", ":"].includes(despues.v) && j > 1 && !esTipo(1)) ){
        tomar(); const ty = tipo(); espera(")");
        return { k: "cast", t: ty.t, a: unaria(), linea: t.linea, archivo: t.archivo };
      }
    }
    if(t.t === "id" && t.v === "sizeof"){
      tomar(); espera("(");
      let e;
      if(esTipo()) e = { k: "sizeofT", t: tipo().t }; else e = { k: "sizeof", a: exprComa() };
      espera(")"); return { ...e, linea: t.linea, archivo: t.archivo };
    }
    return postfija(primaria());
  }
  function postfija(e){
    for(;;){
      const t = ver();
      if(op("(")){ tomar(); const args = []; while(!op(")")){ args.push(asignacion()); if(!op(")")) espera(",", "entre los argumentos va una coma"); } tomar(); e = { k: "call", f: e, args, linea: t.linea, archivo: t.archivo }; continue; }
      if(op(".") || op("->")){ tomar(); e = { k: "miembro", o: e, n: nombre("falta el nombre del método"), linea: t.linea, archivo: t.archivo }; continue; }
      if(op("::")){ tomar(); e = { k: "id", n: (e.n || "") + "::" + nombre(), linea: t.linea, archivo: t.archivo }; continue; }
      if(op("[")){ tomar(); const i = exprComa(); espera("]"); e = { k: "idx", a: e, i, linea: t.linea, archivo: t.archivo }; continue; }
      if(op("++") || op("--")){ tomar(); e = { k: "post", op: t.v, a: e, linea: t.linea, archivo: t.archivo }; continue; }
      return e;
    }
  }
  function primaria(){
    const t = tomar();
    if(t.t === "num") return { k: "num", v: t.v, flot: t.flot, sinSigno: t.sinSigno, linea: t.linea, archivo: t.archivo };
    if(t.t === "chr") return { k: "chr", v: t.v, linea: t.linea, archivo: t.archivo };
    if(t.t === "str"){ let s = t.v; while(es("str")) s += tomar().v; return { k: "str", v: s, linea: t.linea, archivo: t.archivo }; }
    if(t.t === "id") return { k: "id", n: t.v, linea: t.linea, archivo: t.archivo };
    if(t.t === "op" && t.v === "("){ const e = exprComa(); espera(")"); return e; }
    if(t.t === "op" && t.v === "["){
      while(!op("]")) tomar(); tomar();
      const params = [];
      if(op("(")){ tomar(); while(!op(")")){ const pt = tipo(); const pn = es("id") ? tomar().v : "_" + params.length; params.push({ t: pt.t, n: pn }); if(!op(")")) espera(","); } tomar(); }
      if(es("op", "->")){ tomar(); tipo(); }
      const cuerpo = bloque();
      return { k: "lambda", f: { n: "lambda", t: "auto", params, cuerpo, linea: t.linea, archivo: t.archivo }, linea: t.linea, archivo: t.archivo };
    }
    if(t.t === "op" && t.v === "{"){ const xs = []; while(!op("}")){ xs.push(asignacion()); if(!op("}")) espera(","); } tomar(); return { k: "lista", xs, linea: t.linea, archivo: t.archivo }; }
    err(t.t === "eof" ? "el código terminó antes de tiempo (¿falta cerrar algo?)" : `no entiendo "${t.v}" acá`, t);
  }

  // ---- Declaraciones de variables: int a = 1, b[3] = {1, 2, 3};  DHT dht(33, DHT22);
  function declaracion(ty, primerNombre, t0){
    const decls = [];
    let n = primerNombre;
    for(;;){
      const d = { k: "decl", t: ty.t, n, const: ty.const, estatico: ty.estatico, linea: t0.linea, archivo: t0.archivo };
      while(op("[")){ tomar(); d.dims = d.dims || []; d.dims.push(op("]") ? null : asignacion()); espera("]"); }
      if(op("(")){ tomar(); d.ctor = []; while(!op(")")){ d.ctor.push(asignacion()); if(!op(")")) espera(","); } tomar(); }
      else if(op("=")){ tomar(); d.init = asignacion(); }
      decls.push(d);
      if(op(",")){ tomar(); while(op("*")) tomar(); n = nombre(); continue; }
      break;
    }
    espera(";", "falta el \";\" al final de la declaración");
    return decls.length === 1 ? decls[0] : { k: "decls", ds: decls, linea: t0.linea, archivo: t0.archivo };
  }

  // ---- Sentencias
  function bloque(){ const t = espera("{"); const ss = []; while(!op("}")){ if(es("eof")) err("falta cerrar una \"}\"", t); ss.push(sentencia()); } tomar(); return { k: "bloque", ss, linea: t.linea, archivo: t.archivo }; }
  function sentencia(){
    const t = ver();
    if(op("{")) return bloque();
    if(op(";")){ tomar(); return { k: "nada", linea: t.linea }; }
    if(t.t === "id"){
      switch(t.v){
        case "if": { tomar(); espera("("); const c = exprComa(); espera(")"); const a = sentencia(); let b = null; if(es("id", "else")){ tomar(); b = sentencia(); } return { k: "if", c, a, b, linea: t.linea, archivo: t.archivo }; }
        case "while": { tomar(); espera("("); const c = exprComa(); espera(")"); return { k: "while", c, a: sentencia(), linea: t.linea, archivo: t.archivo }; }
        case "do": { tomar(); const a = sentencia(); if(!es("id", "while")) err("falta el while del do", ver()); tomar(); espera("("); const c = exprComa(); espera(")"); espera(";"); return { k: "do", c, a, linea: t.linea, archivo: t.archivo }; }
        case "for": {
          tomar(); espera("(");
          let ini = null;
          if(!op(";")){ if(esTipo()){ const t0 = ver(), ty = tipo(); ini = declaracion(ty, nombre(), t0); } else { ini = { k: "expr", e: exprComa(), linea: t.linea, archivo: t.archivo }; espera(";"); } } else tomar();
          const c = op(";") ? null : exprComa(); espera(";");
          const paso = op(")") ? null : exprComa(); espera(")");
          return { k: "for", ini, c, paso, a: sentencia(), linea: t.linea, archivo: t.archivo };
        }
        case "switch": {
          tomar(); espera("("); const c = exprComa(); espera(")"); espera("{");
          const casos = [];
          while(!op("}")){
            if(es("id", "case")){ tomar(); const v = ternario(); espera(":"); casos.push({ v, ss: [] }); continue; }
            if(es("id", "default")){ tomar(); espera(":"); casos.push({ def: true, ss: [] }); continue; }
            if(!casos.length) err("falta un case", ver());
            casos[casos.length - 1].ss.push(sentencia());
          }
          tomar(); return { k: "switch", c, casos, linea: t.linea, archivo: t.archivo };
        }
        case "break": tomar(); espera(";"); return { k: "break", linea: t.linea };
        case "continue": tomar(); espera(";"); return { k: "continue", linea: t.linea };
        case "return": { tomar(); const e = op(";") ? null : exprComa(); espera(";"); return { k: "return", e, linea: t.linea, archivo: t.archivo }; }
      }
      if(esTipo()){ const ty = tipo(); return declaracion(ty, nombre("falta el nombre de la variable"), t); }
    }
    const e = exprComa();
    espera(";", "falta el \";\" al final");
    return { k: "expr", e, linea: t.linea, archivo: t.archivo };
  }

  // ---- El programa: primero se juntan las funciones (como el IDE de Arduino, que arma los prototipos), después se lee todo
  const globales = [], fuentes = [];
  function saltarBloque(){ let prof = 0; do { if(op("{")) prof++; if(op("}")) prof--; if(es("eof")) err("falta cerrar una \"}\"", ver()); tomar(); } while(prof > 0); }
  const k0 = k;
  // pasada 1: nombres y tipos de las funciones
  while(!es("eof")){
    if(op(";")){ tomar(); continue; }
    if(es("id", "typedef") || es("id", "using") || es("id", "enum") || (es("id", "struct") && op("{", 2))){ while(!op(";")){ if(op("{")) saltarBloque(); else tomar(); } tomar(); continue; }
    if(!esTipo()){ tomar(); continue; }
    const ty = tipo();
    if(!es("id")){ tomar(); continue; }
    const n = tomar().v;
    if(op("(")){
      let prof = 0; do { if(op("(")) prof++; if(op(")")) prof--; tomar(); } while(prof > 0 && !es("eof"));
      if(op("{")){ funciones.set(n, ty.t); saltarBloque(); continue; }
    }
    while(!op(";") && !es("eof")){ if(op("{")) saltarBloque(); else tomar(); }
    tomar();
  }
  k = k0;
  const funcs = new Map();
  while(!es("eof")){
    if(op(";")){ tomar(); continue; }
    if(es("id", "typedef") || es("id", "using") || es("id", "enum") || (es("id", "struct") && op("{", 2))){ err(`"${ver().v}" no está en el simulador`, ver()); }
    const t0 = ver();
    if(!esTipo()) err(`no entiendo "${ver().v ?? ver().t}" acá (afuera de las funciones van declaraciones)`, ver());
    const ty = tipo();
    const n = nombre("falta un nombre");
    if(op("(")){
      // ¿función, prototipo u objeto? Si después del ( viene un tipo o ")" seguido de "{" o ";", es función
      let j = 1, prof = 0;
      while(!(op(")", j) && prof === 0) && !es("eof", undefined, j)){ if(op("(", j)) prof++; if(op(")", j)) prof--; j++; }
      const sig = ver(j + 1);
      const esFunc = sig.t === "op" && (sig.v === "{" || (sig.v === ";" && (esTipo(1) || op(")", 1))));
      if(esFunc){
        tomar();
        const params = [];
        while(!op(")")){
          if(es("id", "void") && op(")", 1)){ tomar(); break; }
          const pt = tipo();
          const pn = es("id") ? tomar().v : "_" + params.length;
          let arr = false;
          while(op("[")){ tomar(); while(!op("]")) tomar(); tomar(); arr = true; }
          if(op("=")){ tomar(); asignacion(); }
          params.push({ t: arr ? pt.t + "*" : pt.t, n: pn });
          if(!op(")")) espera(",");
        }
        tomar();
        if(op(";")){ tomar(); continue; }   // prototipo
        const cuerpo = bloque();
        if(funcs.has(n)) err(`la función ${n} está dos veces`, t0);
        funcs.set(n, { n, t: ty.t, params, cuerpo, linea: t0.linea, archivo: t0.archivo });
        continue;
      }
    }
    globales.push(declaracion(ty, n, t0));
  }
  return { globales, funcs };
}

/* ================= Constantes de Arduino ================= */
const CONST = {
  HIGH: 1, LOW: 0, INPUT: 1, OUTPUT: 3, INPUT_PULLUP: 5, INPUT_PULLDOWN: 9, LED_BUILTIN: 2, true: true, false: false, NULL: 0, nullptr: 0,
  RISING: 1, FALLING: 2, CHANGE: 3, ONLOW: 4, ONHIGH: 5, DEC: 10, HEX: 16, OCT: 8, BIN: 2, PI: Math.PI, HALF_PI: Math.PI / 2, TWO_PI: Math.PI * 2,
  DEG_TO_RAD: Math.PI / 180, RAD_TO_DEG: 180 / Math.PI, EULER: Math.E,
  WL_CONNECTED: 3, WL_DISCONNECTED: 6, WL_IDLE_STATUS: 0, WL_NO_SSID_AVAIL: 1, WL_CONNECT_FAILED: 4, WIFI_STA: 1, WIFI_AP: 2, WIFI_AP_STA: 3,
  DHT11: 11, DHT22: 22, DHT21: 21, AM2301: 21,
  SH110X_WHITE: 1, SH110X_BLACK: 0, SH110X_INVERSE: 2, SSD1306_WHITE: 1, SSD1306_BLACK: 0, SSD1306_INVERSE: 2, WHITE: 1, BLACK: 0, SSD1306_SWITCHCAPVCC: 2,
  T0: 4, T1: 0, T2: 2, T3: 15, T4: 13, T5: 12, T6: 14, T7: 27, T8: 33, T9: 32, A0: 36, A3: 39, A4: 32, A5: 33, A6: 34, A7: 35,
  GPIO_NUM_0: 0, LED_ROJO: 23, Wire: "Wire", SPI: "SPI", HTTP_GET: 1, HTTP_POST: 3, U_FLASH: 0, U_SPIFFS: 100,
  __DATE__: "Oct 22 2026", __TIME__: "10:00:00", TELEGRAM_CERTIFICATE_ROOT: "-----BEGIN CERTIFICATE-----", READ: 1, WRITE: 2, READ_WRITE: 3,
  INT8_MAX: 127, INT16_MAX: 32767, INT32_MAX: 2147483647, UINT32_MAX: 4294967295, ULONG_MAX: 4294967295, LONG_MAX: 2147483647
};
for(let i = 0; i <= 39; i++) CONST["GPIO_NUM_" + i] = i;

/* ================= La placa de la cátedra ================= */
const PLACA = {
  2: { nombre: "LED azul", tipo: "led", color: "#3b82f6" },
  23: { nombre: "LED verde", tipo: "led", color: "#22c55e" },
  14: { nombre: "Relé", tipo: "rele" },
  19: { nombre: "Pulsador", tipo: "boton" },
  32: { nombre: "Potenciómetro", tipo: "pote" },
  33: { nombre: "DHT22", tipo: "dht" },
  13: { nombre: "Touch +", tipo: "touch" },
  4: { nombre: "Touch −", tipo: "touch" },
  25: { nombre: "DAC 1", tipo: "dac" }, 26: { nombre: "DAC 2", tipo: "dac" }
};
const SOLO_ENTRADA = new Set([34, 35, 36, 37, 38, 39]);
const ADC2 = new Set([0, 2, 4, 12, 13, 14, 15, 25, 26, 27]);

/* ================= Intérprete ================= */
const COSTO = 0.01;   // ms virtuales por sentencia (la ESP32 es más rápida: alcanza para que millis() avance)
const BREAK = { s: "break" }, CONTINUE = { s: "continue" };
class Retorno { constructor(v){ this.v = v; } }

class Sim {
  constructor(codigo, opts = {}){
    this.t = 0; this.pasos = 0; this.espera = 0; this.error = null; this.terminado = false;
    this.h = { pines: {}, pwm: {}, brillo: {}, serial: [], display: [], thingspeak: [], mqtt: [], avisos: [], servo: {}, tono: [] };
    this.modos = {}; this.salidas = {}; this.pwmv = {};
    this.ent = { boton: false, pote: opts.pote ?? 2048, dht: { t: opts.temp ?? 24.5, h: opts.hum ?? 55 }, touch: {}, digital: {} };
    this.serialIn = ""; this.serialAbierto = false; this.serialTexto = "";
    this.resLectura = 12; this.resEscritura = {}; this.ledc = { canales: {}, pines: {} };
    this.wifi = { estado: 6, desde: null, ssid: "" };
    this.ts = { campos: {}, ultimo: -1e9, canales: JSON.parse(JSON.stringify(opts.canales || {})) };   // opts.canales: lo que ya tiene el canal (para leerlo)
    this.mqtt = { cola: [] };
    this.tickers = []; this.interrupciones = []; this.pendientes = [];
    this.eeprom = new Map(Object.entries(opts.eeprom || {}).map(([k, v]) => [+k, v]));   // opts.eeprom: lo que quedó guardado de antes
    this.azar = 12345;
    this.programadas = [];   // entradas de una prueba: [{ t, ... }]
    this.libs = new Set();
    this.vivo = !!opts.vivo;   // en la página: la historia se recorta para que no crezca sin fin
    this.display = null;
    try {
      const pp = preprocesar(codigo, opts.nombre || "sketch.ino", opts.archivos || [], this.libs);
      const { globales, funcs } = sintaxis(pp.toks);
      this.globales = globales; this.funcs = funcs;
      if(!funcs.has("setup")) err("falta la función void setup()");
      if(!funcs.has("loop")) err("falta la función void loop()");
      this.vars = new Map();   // variables globales: nombre → { v, t }
      this.gen = this.principal();
    } catch(e){
      if(!(e instanceof CppErr)) throw e;
      this.error = { msg: e.message, linea: e.linea, archivo: e.archivo, compilacion: true };
    }
  }
  /* ---- Tiempo */
  *principal(){
    const sc = { vars: this.vars, padre: null };
    for(const d of this.globales) yield* this.sent(d, sc);
    yield* this.llamarGen(this.funcs.get("setup"), [], sc);
    this.enLoop = true;
    for(;;){
      const t0 = this.t;
      yield* this.llamarGen(this.funcs.get("loop"), [], sc);
      this.vueltas = (this.vueltas || 0) + 1;
      if(this.t - t0 < 1){ this.espera = t0 + 1 - this.t; yield { esperar: t0 + 1 - this.t }; }
      if(this.vueltas % 50 === 0) yield null;
    }
  }
  /* Corre hasta el tiempo virtual "hasta" (o hasta gastar "limite" pasos o "ms" de reloj real) */
  avanzar(hasta, limite = 2e6, ms = Infinity){
    if(this.error || !this.gen) return;
    const p0 = this.pasos, r0 = Date.now();
    try {
      while(this.t < hasta){
        if(this.espera > 0){
          const sig = Math.min(hasta, this.t + this.espera, this.proximoEvento());
          this.espera -= sig - this.t; this.t = sig;
          if(this.espera < 1e-9) this.espera = 0;
          this.atender();
          continue;
        }
        const r = this.gen.next();
        if(r.done){ this.terminado = true; return; }
        if(r.value && r.value.esperar) this.espera = r.value.esperar;
        if(this.pasos - p0 > limite || Date.now() - r0 > ms) return "lento";
      }
    } catch(e){
      if(!(e instanceof CppErr) && !(e instanceof RangeError)) throw e;
      this.error = { msg: e instanceof RangeError ? "Guru Meditation Error: se llenó la pila (¿una función que se llama a sí misma sin fin?)" : e.message, linea: e.linea || this.linea, archivo: e.archivo || this.archivo };
      this.gen = null;
    }
  }
  proximoEvento(){
    let t = Infinity;
    for(const p of this.programadas) if(p.t > this.t) { t = Math.min(t, p.t); break; }
    for(const k of this.tickers) if(k.activo) t = Math.min(t, k.prox);
    return t;
  }
  /* Entre sentencias: las entradas programadas, los Ticker y las interrupciones */
  atender(){
    while(this.programadas.length && this.programadas[0].t <= this.t) this.entrada(this.programadas.shift());
    for(const k of this.tickers) if(k.activo && this.t >= k.prox){
      k.prox += k.periodo; if(k.una) k.activo = false;
      this.correrSync(k.fn, k.arg !== undefined ? [k.arg] : []);
    }
    if(this.pendientes.length && !this.enIsr){
      const ps = this.pendientes; this.pendientes = [];
      this.enIsr = true;
      try { for(const f of ps) this.correrSync(f, []); } finally { this.enIsr = false; }
    }
  }
  /* ---- Entradas de la placa (desde la página o desde una prueba) */
  entrada(e){
    const antes = { b: this.leerPin(19), t13: this.touchVal(13), t4: this.touchVal(4) };
    if("boton" in e) this.ent.boton = !!e.boton;
    if("pote" in e) this.ent.pote = Math.max(0, Math.min(4095, Math.round(e.pote)));
    if(e.dht) Object.assign(this.ent.dht, e.dht);
    if(e.touch) Object.assign(this.ent.touch, e.touch);
    if(e.pin) this.ent.digital[e.pin.n] = e.pin.v ? 1 : 0;
    if(e.serial != null) this.serialIn += e.serial;
    if(e.mqtt) this.mqtt.cola.push(e.mqtt);
    if(e.wifiCae){ this.wifi.estado = 6; this.wifi.desde = null; }
    // Interrupciones por flanco y por touch
    const b = this.leerPin(19);
    for(const it of this.interrupciones){
      if(it.touch){ const v = this.touchVal(it.pin), a = it.pin === 13 ? antes.t13 : antes.t4; if(v < it.umbral && a >= it.umbral) this.pendientes.push(it.fn); continue; }
      if(it.pin !== 19 || b === antes.b) continue;
      if(it.modo === 3 || (it.modo === 2 && b === 0) || (it.modo === 1 && b === 1)) this.pendientes.push(it.fn);
    }
  }
  touchVal(pin){ return this.ent.touch[pin] ?? 72; }
  leerPin(pin){
    const modo = this.modos[pin];
    if(modo === 3) return this.salidas[pin] || 0;   // una salida: lee lo que escribió
    if(pin === 19) return this.ent.boton ? 0 : (modo === 9 ? 0 : 1);   // el pulsador va a masa (con pull-up: suelto = HIGH)
    if(pin in this.ent.digital) return this.ent.digital[pin];
    return modo === 5 ? 1 : 0;
  }
  /* ---- Historia */
  anotar(tipo, pin, v){
    const h = this.h[tipo], k = String(pin);
    (h[k] = h[k] || []);
    const l = h[k][h[k].length - 1];
    if(l && l.v === v) return;
    h[k].push({ t: this.t, v });
    if(this.vivo && h[k].length > 4000) h[k].splice(0, 1000);
  }
  escribirSerial(s){
    if(!this.serialAbierto){ this.aviso("Serial.print antes de Serial.begin(): en la placa no sale nada"); return; }
    this.h.serial.push({ t: this.t, s }); this.serialTexto += s;
    if(this.vivo && this.h.serial.length > 4000) this.h.serial.splice(0, 1000);
    if(this.serialTexto.length > 60000) this.serialTexto = this.serialTexto.slice(-40000);
  }
  aviso(s){ if(!this.h.avisos.some(a => a.s === s)) this.h.avisos.push({ t: this.t, s }); }
  estado(){
    return { t: this.t, modos: this.modos, salidas: this.salidas, pwm: this.pwmv, serial: this.serialTexto, display: this.display && this.display.cuadro,
      wifi: this.wifiEstado(), ts: this.h.thingspeak, mqtt: this.h.mqtt, avisos: this.h.avisos, error: this.error, ent: this.ent, servo: this.h.servo };
  }
  wifiEstado(){ if(this.wifi.desde != null && this.t - this.wifi.desde >= 1200) this.wifi.estado = 3; return this.wifi.estado; }

  /* ---- Variables */
  buscar(n, sc){ for(let s = sc; s; s = s.padre) if(s.vars.has(n)) return s.vars.get(n); return null; }
  /* ---- Sentencias (generadores: delay() suspende) */
  *sent(s, sc){
    this.pasos++; this.t += COSTO; this.linea = s.linea; this.archivo = s.archivo;
    if(this.programadas.length || this.tickers.length || this.pendientes.length) this.atender();
    if(this.pasos % 400 === 0) yield null;
    switch(s.k){
      case "nada": return;
      case "expr": {
        const e = s.e;
        // delay() y las funciones propias que se llaman como sentencia pueden suspender
        if(e.k === "call" && e.f.k === "id"){
          if(e.f.n === "delay" || e.f.n === "delayMicroseconds"){
            const ms = +this.ev(e.args[0], sc) / (e.f.n === "delay" ? 1 : 1000);
            if(ms > 0) yield { esperar: ms };
            return;
          }
          const f = this.funcs.get(e.f.n);
          if(f && !this.buscar(e.f.n, sc)){ yield* this.llamarGen(f, e.args.map(a => this.evArg(a, sc)), sc, e); return; }
        }
        if(e.k === "asig" && e.op === "=" && e.b.k === "call" && e.b.f.k === "id" && this.funcs.has(e.b.f.n) && !this.buscar(e.b.f.n, sc)){
          const v = yield* this.llamarGen(this.funcs.get(e.b.f.n), e.b.args.map(a => this.evArg(a, sc)), sc, e.b);
          this.asignar(e.a, v, sc);
          return;
        }
        this.ev(e, sc);
        return;
      }
      case "decl": this.declarar(s, sc); return;
      case "decls": for(const d of s.ds) this.declarar(d, sc); return;
      case "bloque": {
        const sc2 = { vars: new Map(), padre: sc };
        for(const x of s.ss){ const r = yield* this.sent(x, sc2); if(r) return r; }
        return;
      }
      case "if": {
        if(this.verdad(this.ev(s.c, sc))) return yield* this.sent(s.a, sc);
        if(s.b) return yield* this.sent(s.b, sc);
        return;
      }
      case "while": {
        while(this.verdad(this.ev(s.c, sc))){
          const r = yield* this.sent(s.a, sc);
          if(r === BREAK) break; if(r instanceof Retorno) return r;
          this.t += COSTO; this.pasos++;
          if(this.pasos % 400 === 0) yield null;
        }
        return;
      }
      case "do": {
        do {
          const r = yield* this.sent(s.a, sc);
          if(r === BREAK) break; if(r instanceof Retorno) return r;
          this.t += COSTO;
        } while(this.verdad(this.ev(s.c, sc)));
        return;
      }
      case "for": {
        const sc2 = { vars: new Map(), padre: sc };
        if(s.ini) yield* this.sent(s.ini, sc2);
        while(!s.c || this.verdad(this.ev(s.c, sc2))){
          const r = yield* this.sent(s.a, sc2);
          if(r === BREAK) break; if(r instanceof Retorno) return r;
          if(s.paso) this.ev(s.paso, sc2);
          this.t += COSTO; this.pasos++;
          if(this.pasos % 400 === 0) yield null;
        }
        return;
      }
      case "switch": {
        const v = this.ev(s.c, sc);
        let i = s.casos.findIndex(c => !c.def && this.ev(c.v, sc) == v);
        if(i < 0) i = s.casos.findIndex(c => c.def);
        if(i < 0) return;
        const sc2 = { vars: new Map(), padre: sc };
        for(; i < s.casos.length; i++) for(const x of s.casos[i].ss){ const r = yield* this.sent(x, sc2); if(r === BREAK) return; if(r) return r; }
        return;
      }
      case "break": return BREAK;
      case "continue": return CONTINUE;
      case "return": {
        if(s.e && s.e.k === "call" && s.e.f.k === "id" && this.funcs.has(s.e.f.n)) return new Retorno(yield* this.llamarGen(this.funcs.get(s.e.f.n), s.e.args.map(a => this.evArg(a, sc)), sc, s.e));
        return new Retorno(s.e ? this.ev(s.e, sc) : undefined);
      }
    }
    err(`no sé ejecutar "${s.k}"`, s);
  }
  verdad(v){ return typeof v === "string" ? true : !!v && !Number.isNaN(v); }
  declarar(d, sc){
    if(d.estatico && sc.padre){
      // static adentro de una función: se inicializa una sola vez
      d.estatica = d.estatica || null;
      if(d.estatica){ sc.vars.set(d.n, d.estatica); return; }
    }
    let ent;
    if(d.dims){
      const n = d.dims[0] ? Math.trunc(this.ev(d.dims[0], sc)) : null;
      let v;
      if(d.init && d.init.k === "lista") v = d.init.xs.map(x => this.ev(x, sc));
      else if(d.init && d.init.k === "str") v = [...d.init.v].map(c => c.charCodeAt(0)).concat([0]);
      else v = [];
      const largo = n ?? v.length;
      while(v.length < largo) v.push(d.t === "String" ? "" : 0);
      ent = { v: v.map(x => aTipo(x, d.t)), t: d.t + "[]", arr: true };
    } else if(CLASES.has(d.t) && d.t !== "String" && d.t !== "IPAddress" || (!PALABRAS_TIPO.has(d.t) && !esNumT(d.t) && /^[A-Z]/.test(d.t) && !/\*$/.test(d.t))){
      const args = d.ctor ? d.ctor.map(a => this.ev(a, sc)) : d.init && d.init.k === "call" ? d.init.args.map(a => this.ev(a, sc)) : [];
      ent = { v: this.nuevoObjeto(d.t, args, d), t: d.t };
    } else {
      let v = d.init ? (d.init.k === "lista" ? (d.init.xs[0] ? this.ev(d.init.xs[0], sc) : 0) : this.ev(d.init, sc)) : d.ctor && d.ctor.length ? this.ev(d.ctor[0], sc) : (d.t === "String" || d.t === "char*" ? "" : d.t === "float" || d.t === "double" ? 0 : 0);
      ent = { v: aTipo(v, d.t), t: d.t, cnst: d.const };
    }
    sc.vars.set(d.n, ent);
    if(d.estatico && sc.padre) d.estatica = ent;
  }
  /* ---- Funciones propias */
  *llamarGen(f, args, sc, nodo){
    if(args.length !== f.params.length && !(f.params.length > args.length)) err(`${f.n}: se llama con ${args.length} argumentos y recibe ${f.params.length}`, nodo || f);
    if((this.prof = (this.prof || 0) + 1) > 120){ this.prof = 0; throw new RangeError(); }
    const sc2 = { vars: new Map(), padre: { vars: this.vars, padre: null } };
    f.params.forEach((p, i) => sc2.vars.set(p.n, args[i] && args[i].ref ? args[i].ref : { v: aTipo(args[i] && "v" in args[i] ? args[i].v : args[i], p.t), t: p.t }));
    try {
      const r = yield* this.sent(f.cuerpo, sc2);
      return r instanceof Retorno ? (f.t === "void" ? undefined : aTipo(r.v, f.t)) : undefined;
    } finally { this.prof--; }
  }
  /* Una función propia adentro de una expresión (o un Ticker, o una interrupción): se corre de una; delay() solo suma tiempo */
  correrSync(f, args){
    const g = this.llamarGen(f, args, null);
    let n = 0;
    for(;;){
      const r = g.next();
      if(r.done) return r.value;
      if(r.value && r.value.esperar){ this.t += r.value.esperar; if(this.programadas.length) this.atender(); }
      if(++n > 2e6) err(`${f.n} no termina (¿un while que espera algo que no cambia?)`, f);
    }
  }
  /* Los argumentos de una función propia: un valor, o la variable misma si el parámetro es por referencia */
  evArg(a, sc){
    if(a.k === "id"){ const x = this.buscar(a.n, sc); if(x && (x.arr || typeof x.v === "object")) return { ref: x }; }
    return { v: this.ev(a, sc) };
  }

  /* ---- Tipos de las expresiones (para la división entera y los String) */
  tipoDe(e, sc){
    switch(e.k){
      case "num": return e.flot ? "double" : e.sinSigno ? "unsigned long" : "int";
      case "chr": return "char";
      case "str": return "char*";
      case "id": { const x = this.buscar(e.n, sc); if(x) return x.arr ? x.t : x.t; if(e.n === "true" || e.n === "false") return "bool"; if(e.n in CONST) return typeof CONST[e.n] === "number" && !Number.isInteger(CONST[e.n]) ? "double" : "int"; return "int"; }
      case "cast": return e.t;
      case "tern": { const a = this.tipoDe(e.a, sc), b = this.tipoDe(e.b, sc); return a === "String" || b === "String" ? "String" : !esEnteroT(a) || !esEnteroT(b) ? (esNumT(a) && esNumT(b) ? "double" : a) : a; }
      case "un": return e.op === "!" ? "bool" : this.tipoDe(e.a, sc);
      case "post": return this.tipoDe(e.a, sc);
      case "asig": return this.tipoDe(e.a, sc);
      case "coma": return this.tipoDe(e.b, sc);
      case "sizeof": case "sizeofT": return "unsigned int";
      case "idx": { const t = this.tipoDe(e.a, sc); return t === "char*" || t === "String" ? "char" : t === "byte*" ? "byte" : t.replace(/\[\]$|\*$/, ""); }
      case "bin": {
        if(["==", "!=", "<", ">", "<=", ">=", "&&", "||"].includes(e.op)) return "bool";
        const a = this.tipoDe(e.a, sc), b = this.tipoDe(e.b, sc);
        if(e.op === "+" && (a === "String" || b === "String")) return "String";
        if(!esEnteroT(a) || !esEnteroT(b)) return esNumT(a) && esNumT(b) ? "double" : (a === "char*" || b === "char*" ? "char*" : "double");
        if(/long long|64/.test(a + b)) return "long long";
        if(sinSignoT(a) && /long|uint32|unsigned int|size_t/.test(a) || sinSignoT(b) && /long|uint32|unsigned int|size_t/.test(b)) return "unsigned long";
        return "int";
      }
      case "call": return this.tipoLlamada(e, sc);
      case "miembro": return "int";
    }
    return "int";
  }
  tipoLlamada(e, sc){
    if(e.f.k === "id"){
      const n = e.f.n, f = this.funcs.get(n);
      if(f) return f.t;
      if(n === "String") return "String";
      if(["millis", "micros"].includes(n)) return "unsigned long";
      if(["sqrt", "pow", "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "exp", "log", "log10", "fabs", "floor", "ceil", "round", "fmod", "radians", "degrees", "temperatureRead"].includes(n)) return "double";
      if(["abs", "min", "max", "constrain"].includes(n)){ const ts = e.args.map(a => this.tipoDe(a, sc)); return ts.every(esEnteroT) ? ts[0] : "double"; }
      if(["isnan", "isinf", "isDigit", "isAlpha"].includes(n)) return "bool";
      if(n === "F") return "char*";
      return "int";
    }
    if(e.f.k === "miembro"){
      const m = e.f.n, ot = this.tipoDe(e.f.o, sc);
      if(["readTemperature", "readHumidity", "computeHeatIndex", "toFloat", "readFloatField", "convertCtoF", "convertFtoC"].includes(m)) return "float";
      if(["readString", "readStringUntil", "substring", "toString", "localIP", "macAddress", "getString", "readStringField", "c_str", "SSID", "softAPIP", "gatewayIP", "arg", "uri"].includes(m)) return m === "c_str" ? "char*" : "String";
      if(["read"].includes(m) && ot === "int") return "int";
      if(m === "charAt") return "char";
      if(["connected", "connect", "equals", "startsWith", "endsWith", "begin", "publish", "subscribe", "equalsIgnoreCase", "isEmpty"].includes(m)) return "bool";
      if(m === "toInt" || m === "length" || m === "indexOf" || m === "lastIndexOf") return "long";
      return "int";
    }
    return "int";
  }

  /* ---- Expresiones */
  ev(e, sc){
    switch(e.k){
      case "num": return e.v;
      case "chr": return e.v;
      case "str": return e.v;
      case "lista": return e.xs.map(x => this.ev(x, sc));
      case "lambda": return { funcion: e.f };
      case "id": {
        const x = this.buscar(e.n, sc);
        if(x) return x.arr ? x.v : x.v;
        if(e.n in CONST) return CONST[e.n];
        if(this.funcs.has(e.n)) return { funcion: this.funcs.get(e.n) };
        if(OBJETOS_GLOBALES.has(e.n)) return this.global(e.n);
        err(`'${e.n}' no está declarado`, e);
      }
      case "cast": {
        const v = this.ev(e.a, sc);
        if(e.t === "char" && typeof v === "number") return String.fromCharCode(aTipo(v, "char") & 0xFF);
        if(e.t === "String") return aString(v, this.tipoDe(e.a, sc));
        return aTipo(typeof v === "string" && v.length === 1 && esNumT(e.t) ? v.charCodeAt(0) : v, e.t);
      }
      case "tern": return this.verdad(this.ev(e.c, sc)) ? this.ev(e.a, sc) : this.ev(e.b, sc);
      case "coma": this.ev(e.a, sc); return this.ev(e.b, sc);
      case "sizeofT": return /double|long long|64/.test(e.t) ? 8 : /char|byte|bool|int8|uint8/.test(e.t) ? 1 : /short|16/.test(e.t) ? 2 : 4;
      case "sizeof": { if(e.a.k === "id"){ const x = this.buscar(e.a.n, sc); if(x && x.arr) return x.v.length * (/char|byte|bool/.test(x.t) ? 1 : /double/.test(x.t) ? 8 : 4); } const t = this.tipoDe(e.a, sc); return /double/.test(t) ? 8 : /char|byte|bool/.test(t) ? 1 : 4; }
      case "un": {
        if(e.op === "++" || e.op === "--"){ const v = this.ev(e.a, sc); const n = this.asignar(e.a, (typeof v === "boolean" ? +v : v) + (e.op === "++" ? 1 : -1), sc); return n; }
        if(e.op === "&") return this.ev(e.a, sc);
        if(e.op === "*") return this.ev(e.a, sc);
        const v = this.num(this.ev(e.a, sc), e);
        if(e.op === "!") return !this.verdad(v);
        if(e.op === "-") return esEnteroT(this.tipoDe(e.a, sc)) ? aTipo(-v, this.tipoDe(e.a, sc) === "char" ? "int" : this.tipoDe(e.a, sc)) : -v;
        if(e.op === "+") return v;
        if(e.op === "~") return ~v;
        break;
      }
      case "post": { const v = this.ev(e.a, sc); this.asignar(e.a, (typeof v === "boolean" ? +v : v) + (e.op === "++" ? 1 : -1), sc); return v; }
      case "asig": {
        if(e.op === "=") return this.asignar(e.a, this.ev(e.b, sc), sc);
        const bop = e.op.slice(0, -1);
        const tA = this.tipoDe(e.a, sc);
        const v = this.binaria(bop, this.ev(e.a, sc), this.ev(e.b, sc), tA, this.tipoDe(e.b, sc), e, tA === "String" ? "String" : esEnteroT(tA) && esEnteroT(this.tipoDe(e.b, sc)) ? tA : "double");
        return this.asignar(e.a, v, sc);
      }
      case "bin": {
        if(e.op === "&&") return this.verdad(this.ev(e.a, sc)) && this.verdad(this.ev(e.b, sc));
        if(e.op === "||") return this.verdad(this.ev(e.a, sc)) || this.verdad(this.ev(e.b, sc));
        const ta = this.tipoDe(e.a, sc), tb = this.tipoDe(e.b, sc);
        return this.binaria(e.op, this.ev(e.a, sc), this.ev(e.b, sc), ta, tb, e, this.tipoDe(e, sc));
      }
      case "idx": {
        const a = this.ev(e.a, sc), i = Math.trunc(this.num(this.ev(e.i, sc), e));
        if(typeof a === "string"){ if(i < 0 || i > a.length) err(`índice ${i} afuera del texto (largo ${a.length})`, e); return i === a.length ? 0 : a.charCodeAt(i); }
        if(Array.isArray(a)){ if(i < 0 || i >= a.length) err(`índice ${i} afuera del arreglo (tiene ${a.length} lugares): en la placa esto puede colgarla`, e); return a[i]; }
        err("eso no es un arreglo", e);
      }
      case "call": return this.llamar(e, sc);
      case "miembro": {
        const o = this.ev(e.o, sc);
        if(o && typeof o === "object" && e.n in o && typeof o[e.n] !== "function") return o[e.n];
        err(`no sé qué es ".${e.n}" acá`, e);
      }
    }
    err(`no sé evaluar "${e.k}"`, e);
  }
  num(v, e){ if(typeof v === "boolean") return +v; if(typeof v === "string"){ if(v.length === 1) return v.charCodeAt(0); err("acá va un número y hay un texto", e); } return v; }
  binaria(op, a, b, ta, tb, e, tr){
    if(tr === "String" || (op === "+" && (typeof a === "string" && ta === "String" || typeof b === "string" && tb === "String"))){
      if(op !== "+") err(`con String solo se puede sumar (+), no "${op}"`, e);
      return aString(a, ta) + aString(b, tb);
    }
    if(["==", "!="].includes(op) && (typeof a === "string" || typeof b === "string")){
      const sa = typeof a === "string" ? a : ta === "char" ? String.fromCharCode(a) : aString(a, ta), sb = typeof b === "string" ? b : tb === "char" ? String.fromCharCode(b) : aString(b, tb);
      return op === "==" ? sa === sb : sa !== sb;
    }
    if(["<", ">", "<=", ">="].includes(op) && typeof a === "string" && typeof b === "string") return op === "<" ? a < b : op === ">" ? a > b : op === "<=" ? a <= b : a >= b;
    if(op === "+" && (typeof a === "string" && a.length !== 1 || typeof b === "string" && b.length !== 1)) err("para pegar textos con + uno de los dos tiene que ser String: String(\"Temp: \") + t", e);
    a = this.num(a, e); b = this.num(b, e);
    const entero = esEnteroT(ta) && esEnteroT(tb);
    switch(op){
      case "+": return entero ? aTipo(a + b, tr) : a + b;
      case "-": return entero ? aTipo(a - b, tr) : a - b;
      case "*": return entero ? aTipo(Math.imul ? (Math.abs(a * b) < 2 ** 53 ? a * b : a * b) : a * b, tr) : a * b;
      case "/": if(entero){ if(b === 0) err("Guru Meditation Error: Core 1 panic'ed (IntegerDivideByZero): división entera por cero", e); return aTipo(Math.trunc(a / b), tr); } return a / b;
      case "%": if(entero){ if(b === 0) err("Guru Meditation Error: Core 1 panic'ed (IntegerDivideByZero): resto de dividir por cero", e); return aTipo(a % b, tr); } err("el % es para enteros (para float está fmod)", e);
      case "==": return a === b; case "!=": return a !== b;
      case "<": return a < b; case ">": return a > b; case "<=": return a <= b; case ">=": return a >= b;
      case "&": return aTipo(a & b, tr); case "|": return aTipo(a | b, tr); case "^": return aTipo(a ^ b, tr);
      case "<<": return aTipo(a << b, tr); case ">>": return aTipo(sinSignoT(ta) ? a >>> b : a >> b, tr);
    }
    err(`operador "${op}" desconocido`, e);
  }
  /* Guarda en una variable (o en un lugar de un arreglo) con la conversión de su tipo */
  asignar(dest, v, sc){
    if(dest.k === "id"){
      const x = this.buscar(dest.n, sc);
      if(!x) err(`'${dest.n}' no está declarado`, dest);
      if(x.cnst) err(`'${dest.n}' es const: no se puede cambiar`, dest);
      if(x.arr) err(`no se puede asignar un arreglo entero`, dest);
      if(typeof x.v === "object" && x.v !== null && x.v.clase) err(`'${dest.n}' es un objeto`, dest);
      x.v = aTipo(typeof v === "string" && v.length === 1 && esNumT(x.t) && x.t !== "String" ? v.charCodeAt(0) : v, x.t);
      return x.v;
    }
    if(dest.k === "idx"){
      const base = dest.a;
      const i = Math.trunc(this.num(this.ev(dest.i, sc), dest));
      if(base.k === "id"){
        const x = this.buscar(base.n, sc);
        if(x && x.arr){ if(i < 0 || i >= x.v.length) err(`índice ${i} afuera del arreglo (tiene ${x.v.length} lugares)`, dest); x.v[i] = aTipo(v, x.t.replace(/\[\]$/, "")); return x.v[i]; }
        if(x && typeof x.v === "string"){ const c = typeof v === "number" ? String.fromCharCode(v) : String(v)[0]; x.v = x.v.slice(0, i) + c + x.v.slice(i + 1); return v; }
      }
      err("no se puede guardar ahí", dest);
    }
    if(dest.k === "un" && dest.op === "*") return this.asignar(dest.a, v, sc);
    err("a la izquierda del = va una variable", dest);
  }
  /* El valor de un nodo como lugar (para las funciones que escriben: sprintf, EEPROM.get, String.trim…) */
  lugar(e, sc){ return { leer: () => this.ev(e, sc), escribir: v => this.asignar(e, v, sc) }; }

  /* ---- Llamadas: funciones propias, de Arduino y métodos de los objetos */
  llamar(e, sc){
    if(e.f.k === "miembro") return this.metodo(e, sc);
    if(e.f.k !== "id") err("eso no es una función", e);
    const n = e.f.n;
    const x = this.buscar(n, sc);
    if(x && x.v && x.v.funcion) return this.correrSync(x.v.funcion, e.args.map(a => this.evArg(a, sc)));
    const f = this.funcs.get(n);
    if(f) return this.correrSync(f, e.args.map(a => this.evArg(a, sc)));
    if(n in ESCRIBEN) return ESCRIBEN[n].call(this, e.args, sc, e);
    if(CLASES.has(n) || n === "String"){ const args = e.args.map(a => this.ev(a, sc)); if(n === "String") return args.length > 1 && typeof args[0] === "number" ? (esEnteroT(this.tipoDe(e.args[0], sc)) && args[1] !== undefined ? Math.trunc(args[0]).toString(args[1]) : flotante(args[0], args[1])) : aString(args[0] ?? "", this.tipoDe(e.args[0] || { k: "str" }, sc)); return this.nuevoObjeto(n, args, e); }
    const b = ARDUINO[n];
    if(!b) err(`'${n}' no existe${/^[A-Z]/.test(n) ? "" : " (o no está en el simulador)"}`, e);
    return b.call(this, e.args.map(a => this.ev(a, sc)), e, sc);
  }
  metodo(e, sc){
    const m = e.f.n, on = e.f.o;
    const o = this.ev(on, sc);
    const args = e.args.map(a => this.ev(a, sc));
    // String (también char*): los métodos que cambian el texto lo guardan en la variable
    if(typeof o === "string"){
      const r = metodoString(o, m, args, e, this.tipoDe.bind(this), e.args, sc);
      if(r && r.nuevo !== undefined){ this.asignar(on, r.nuevo, sc); return r.devuelve; }
      return r;
    }
    if(!o || typeof o !== "object" || !o.clase) err(`no se puede llamar .${m}() acá`, e);
    const fn = o[m];
    if(typeof fn !== "function") err(`${o.clase} no tiene ${m}() en el simulador`, e);
    return fn.call(o, args, this, e, sc);
  }
  global(n){ this.objs = this.objs || {}; if(!this.objs[n]){ const o = crearGlobal(n, this); this.objs[n] = TOLERANTES.has(o.clase) ? tolerante(o, this) : o; } return this.objs[n]; }
  nuevoObjeto(clase, args, nodo){
    const C = CONSTRUCTORES[clase];
    if(!C) err(`la clase ${clase} no está en el simulador`, nodo);
    const o = C(args, this, nodo);
    return o && TOLERANTES.has(o.clase) ? tolerante(o, this) : o;
  }
  pinSalida(pin, que, e){
    if(SOLO_ENTRADA.has(pin)) err(`el GPIO ${pin} es solo de entrada: no puede ser salida ni dar PWM`, e);
    if(this.modos[pin] !== 3 && que !== "pwm") this.aviso(`Se escribe en el pin ${pin} sin pinMode(${pin}, OUTPUT)`);
  }
}

/* ================= Métodos de String ================= */
function metodoString(s, m, a, e){
  switch(m){
    case "length": return s.length;
    case "charAt": return a[0] < s.length ? s.charCodeAt(a[0]) : 0;
    case "indexOf": { const x = typeof a[0] === "number" ? String.fromCharCode(a[0]) : a[0]; return s.indexOf(x, a[1] || 0); }
    case "lastIndexOf": { const x = typeof a[0] === "number" ? String.fromCharCode(a[0]) : a[0]; return s.lastIndexOf(x); }
    case "substring": return s.substring(a[0], a[1] === undefined ? s.length : a[1]);
    case "toInt": { const r = /^\s*[-+]?\d+/.exec(s); return r ? parseInt(r[0], 10) | 0 : 0; }
    case "toFloat": case "toDouble": { const r = /^\s*[-+]?(\d+\.?\d*|\.\d+)/.exec(s); return r ? parseFloat(r[0]) : 0; }
    case "equals": return s === a[0];
    case "equalsIgnoreCase": return s.toLowerCase() === String(a[0]).toLowerCase();
    case "startsWith": return s.startsWith(a[0]);
    case "endsWith": return s.endsWith(a[0]);
    case "isEmpty": return s.length === 0;
    case "c_str": case "toString": return s;
    case "trim": return { nuevo: s.trim(), devuelve: undefined };
    case "toUpperCase": return { nuevo: s.toUpperCase(), devuelve: undefined };
    case "toLowerCase": return { nuevo: s.toLowerCase(), devuelve: undefined };
    case "replace": return { nuevo: s.split(typeof a[0] === "number" ? String.fromCharCode(a[0]) : a[0]).join(typeof a[1] === "number" ? String.fromCharCode(a[1]) : a[1]), devuelve: undefined };
    case "remove": return { nuevo: s.slice(0, a[0]) + (a[1] === undefined ? "" : s.slice(a[0] + a[1])), devuelve: undefined };
    case "concat": return { nuevo: s + aString(a[0]), devuelve: true };
    case "compareTo": return s < a[0] ? -1 : s > a[0] ? 1 : 0;
  }
  err(`String no tiene ${m}() en el simulador`, e);
}

/* ================= Funciones de Arduino ================= */
const leerValor = (sim, pin) => sim.leerPin(pin);
const ARDUINO = {
  pinMode(a, e){ const [pin, modo] = a; if(SOLO_ENTRADA.has(pin) && modo === 3) err(`el GPIO ${pin} es solo de entrada: no puede ser OUTPUT`, e); this.modos[pin] = modo; if(modo === 3 && !(pin in this.salidas)) { this.salidas[pin] = 0; this.anotar("pines", pin, 0); this.anotar("brillo", pin, 0); } },
  digitalWrite(a, e){ const [pin, v] = a; this.pinSalida(pin, "dig", e); const x = this.verdad(v) ? 1 : 0; this.salidas[pin] = x; delete this.pwmv[pin]; this.anotar("pines", pin, x); this.anotar("brillo", pin, x); },
  digitalRead(a){ if(a[0] === 19 && this.modos[19] !== 5 && this.modos[19] !== 9 && this.modos[19] !== 3) this.aviso("El pulsador (pin 19) se lee sin INPUT_PULLUP: en la placa queda flotante"); return leerValor(this, a[0]); },
  analogRead(a, e){
    const pin = a[0];
    if(this.wifiEstado() === 3 && ADC2.has(pin)) this.aviso(`analogRead(${pin}) con el WiFi prendido: el ADC2 no anda (usá un pin del ADC1, como el 32)`);
    let v = pin === 32 ? this.ent.pote : 0;
    return Math.round(v * (2 ** this.resLectura - 1) / 4095);
  },
  analogReadResolution(a){ this.resLectura = a[0]; },
  analogReadMilliVolts(a){ return Math.round((a[0] === 32 ? this.ent.pote : 0) * 3300 / 4095); },
  analogWrite(a, e){ const [pin, v] = a; this.pinSalida(pin, "pwm", e); const bits = this.resEscritura[pin] || 8, max = 2 ** bits - 1; const d = Math.max(0, Math.min(max, Math.trunc(v))); this.pwmv[pin] = d / max; this.salidas[pin] = d > 0 ? 1 : 0; this.anotar("pwm", pin, d); this.anotar("brillo", pin, d / max); },
  analogWriteResolution(a){ if(a.length === 2) this.resEscritura[a[0]] = a[1]; else for(const p of [2, 23, 14, 25, 26]) this.resEscritura[p] = a[0]; },
  dacWrite(a, e){ const [pin, v] = a; if(pin !== 25 && pin !== 26) err("dacWrite: el DAC está solo en los GPIO 25 y 26", e); const d = Math.max(0, Math.min(255, Math.trunc(v))); this.pwmv[pin] = d / 255; this.anotar("pwm", pin, d); this.anotar("brillo", pin, d / 255); },
  ledcSetup(a){ this.ledc.canales[a[0]] = { freq: a[1], bits: a[2] }; return a[1]; },
  ledcAttachPin(a){ this.ledc.pines[a[1]] = this.ledc.pines[a[1]] || []; this.ledc.pines[a[1]].push(a[0]); this.resEscritura[a[0]] = (this.ledc.canales[a[1]] || {}).bits || 8; },
  ledcAttach(a){ this.resEscritura[a[0]] = a[2] || 8; return true; },
  ledcAttachChannel(a){ this.resEscritura[a[0]] = a[2] || 8; return true; },
  ledcWrite(a, e){
    const [x, v] = a;
    const pins = this.ledc.pines[x];
    if(pins) for(const p of pins) ARDUINO.analogWrite.call(this, [p, v], e);
    else ARDUINO.analogWrite.call(this, [x, v], e);
  },
  tone(a){ this.h.tono.push({ t: this.t, pin: a[0], f: a[1] }); },
  noTone(a){ this.h.tono.push({ t: this.t, pin: a[0], f: 0 }); },
  millis(){ return Math.floor(this.t) >>> 0; },
  micros(){ return Math.floor(this.t * 1000) >>> 0; },
  delay(a){ this.t += Math.max(0, +a[0]); return undefined; },
  delayMicroseconds(a){ this.t += Math.max(0, +a[0]) / 1000; },
  yield(){},
  map(a, e){ const [x, i0, i1, o0, o1] = a.map(Math.trunc); if(i1 === i0) err("map(): el rango de entrada no puede ser vacío", e); return Math.trunc((x - i0) * (o1 - o0) / (i1 - i0)) + o0; },
  constrain(a){ return Math.min(Math.max(a[0], a[1]), a[2]); },
  min(a){ return Math.min(a[0], a[1]); }, max(a){ return Math.max(a[0], a[1]); }, abs(a){ return Math.abs(a[0]); },
  sqrt(a){ return Math.sqrt(a[0]); }, pow(a){ return Math.pow(a[0], a[1]); }, sq(a){ return a[0] * a[0]; },
  sin(a){ return Math.sin(a[0]); }, cos(a){ return Math.cos(a[0]); }, tan(a){ return Math.tan(a[0]); }, asin(a){ return Math.asin(a[0]); }, acos(a){ return Math.acos(a[0]); },
  atan(a){ return Math.atan(a[0]); }, atan2(a){ return Math.atan2(a[0], a[1]); }, exp(a){ return Math.exp(a[0]); }, log(a){ return Math.log(a[0]); }, log10(a){ return Math.log10(a[0]); },
  fabs(a){ return Math.abs(a[0]); }, floor(a){ return Math.floor(a[0]); }, ceil(a){ return Math.ceil(a[0]); }, round(a){ return Math.round(a[0]); }, fmod(a){ return a[0] % a[1]; },
  radians(a){ return a[0] * Math.PI / 180; }, degrees(a){ return a[0] * 180 / Math.PI; },
  isnan(a){ return Number.isNaN(a[0]); }, isinf(a){ return !Number.isFinite(a[0]) && !Number.isNaN(a[0]); },
  random(a){
    this.azar = (this.azar * 1103515245 + 12345) & 0x7fffffff;
    const r = this.azar / 0x80000000;
    if(a.length === 1) return Math.floor(r * a[0]);
    return a[0] + Math.floor(r * (a[1] - a[0]));
  },
  randomSeed(a){ this.azar = Math.trunc(a[0]) & 0x7fffffff; },
  F(a){ return a[0]; },
  digitalPinToInterrupt(a){ return a[0]; },
  attachInterrupt(a, e){
    const [pin, fn, modo] = a;
    if(!fn || !fn.funcion) err("attachInterrupt: el segundo argumento es la función que atiende la interrupción", e);
    this.interrupciones.push({ pin, fn: fn.funcion, modo });
  },
  detachInterrupt(a){ this.interrupciones = this.interrupciones.filter(i => i.pin !== a[0]); },
  touchRead(a){ return this.touchVal(a[0]); },
  touchAttachInterrupt(a, e){
    const [pin, fn, umbral] = a;
    if(!fn || !fn.funcion) err("touchAttachInterrupt: el segundo argumento es la función", e);
    // En el simulador el touch lee 72 suelto y 10 tocado (en la placa, depende del cable): un umbral más alto que lo
    // que lee suelto (como los 950 y 850 del caso 9, medidos en otra placa) se toma como 40
    let u = umbral ?? 40;
    if(u >= 72){ this.aviso(`touchAttachInterrupt con umbral ${u}: en el simulador el touch lee 72 suelto y 10 tocado, así que se usa 40 (en tu placa, medilo con touchRead)`); u = 40; }
    this.interrupciones.push({ pin, fn: fn.funcion, umbral: u, touch: true });
  },
  temperatureRead(){ return 47.8; },
  noInterrupts(){}, interrupts(){},
  isDigit(a){ return a[0] >= 48 && a[0] <= 57; }, isAlpha(a){ return /[A-Za-z]/.test(String.fromCharCode(a[0])); },
  itoa(){ err("itoa no está en el simulador: usá String(numero)"); },
  strlen(a){ return aString(a[0]).length; },
  strcmp(a){ const x = aString(a[0]), y = aString(a[1]); return x < y ? -1 : x > y ? 1 : 0; },
  atoi(a){ return parseInt(aString(a[0]), 10) || 0; }, atof(a){ return parseFloat(aString(a[0])) || 0; }
};
// Las que escriben en una variable (reciben el lugar, no el valor)
const ESCRIBEN = {
  sprintf(args, sc, e){ const s = formatear(this.ev(args[1], sc), args.slice(2).map(a => this.ev(a, sc))); this.escribirEn(args[0], s, sc); return s.length; },
  snprintf(args, sc, e){ const n = this.ev(args[1], sc); const s = formatear(this.ev(args[2], sc), args.slice(3).map(a => this.ev(a, sc))).slice(0, Math.max(0, n - 1)); this.escribirEn(args[0], s, sc); return s.length; },
  strcpy(args, sc){ const s = aString(this.ev(args[1], sc)); this.escribirEn(args[0], s, sc); },
  strcat(args, sc){ const s = aString(this.ev(args[0], sc)) + aString(this.ev(args[1], sc)); this.escribirEn(args[0], s, sc); },
  dtostrf(args, sc){ const s = flotante(this.ev(args[0], sc), this.ev(args[2], sc)).padStart(this.ev(args[1], sc)); this.escribirEn(args[3], s, sc); return s; }
};
Sim.prototype.escribirEn = function(dest, s, sc){
  if(dest.k === "id"){
    const x = this.buscar(dest.n, sc);
    if(x && x.arr){ const cs = [...s].map(c => c.charCodeAt(0)); if(cs.length >= x.v.length) err(`el texto (${cs.length} caracteres) no entra en ${dest.n}[${x.v.length}]: en la placa pisa memoria`, dest); x.v = cs.concat(Array(x.v.length - cs.length).fill(0)); return; }
    if(x){ x.v = s; return; }
  }
  err("acá va un arreglo de char", dest);
};

/* ================= Objetos globales: Serial, WiFi, ThingSpeak, EEPROM… ================= */
const OBJETOS_GLOBALES = new Set(["Serial", "WiFi", "ThingSpeak", "EEPROM", "Wire", "SPI", "ESP", "ArduinoOTA", "ElegantOTA", "MDNS", "ArduinoCloud", "Serial2"]);
function imprimir(sim, args, e, sc, nl){
  let s = "";
  if(args.length){
    const t = e.args[0] ? sim.tipoDe(e.args[0], sc) : "char*";
    const v = args[0];
    if(args.length > 1 && typeof v === "number"){
      if(esEnteroT(t)) s = Math.trunc(v).toString(args[1]).toUpperCase(); else s = flotante(v, args[1]);
    } else s = typeof v === "number" && t === "char" ? String.fromCharCode(v) : aString(v, t);
  }
  return s + (nl ? "\n" : "");
}
function crearGlobal(n, sim){
  switch(n){
    case "Serial": case "Serial2": return { clase: "HardwareSerial",
      begin(a){ sim.serialAbierto = true; sim.baudios = a[0]; },
      end(){ sim.serialAbierto = false; },
      print(a, s, e, sc){ const x = imprimir(sim, a, e, sc, false); sim.escribirSerial(x); return x.length; },
      println(a, s, e, sc){ const x = imprimir(sim, a, e, sc, true); sim.escribirSerial(x); return x.length; },
      printf(a){ const x = formatear(aString(a[0]), a.slice(1)); sim.escribirSerial(x); return x.length; },
      write(a){ const x = typeof a[0] === "number" ? String.fromCharCode(a[0]) : aString(a[0]); sim.escribirSerial(x); return x.length; },
      available(){ return sim.serialIn.length; },
      read(){ if(!sim.serialIn.length) return -1; const c = sim.serialIn.charCodeAt(0); sim.serialIn = sim.serialIn.slice(1); return c; },
      peek(){ return sim.serialIn.length ? sim.serialIn.charCodeAt(0) : -1; },
      readString(){ const s = sim.serialIn; sim.serialIn = ""; return s; },
      readStringUntil(a){ const c = typeof a[0] === "number" ? String.fromCharCode(a[0]) : a[0]; const i = sim.serialIn.indexOf(c); const s = i < 0 ? sim.serialIn : sim.serialIn.slice(0, i); sim.serialIn = i < 0 ? "" : sim.serialIn.slice(i + 1); return s; },
      parseInt(){ const r = /^\D*?(-?\d+)/.exec(sim.serialIn); if(!r) { sim.serialIn = ""; return 0; } sim.serialIn = sim.serialIn.slice(r.index + r[0].length); return parseInt(r[1], 10); },
      parseFloat(){ const r = /^[^\d-]*?(-?\d+\.?\d*)/.exec(sim.serialIn); if(!r) { sim.serialIn = ""; return 0; } sim.serialIn = sim.serialIn.slice(r.index + r[0].length); return parseFloat(r[1]); },
      flush(){}, setTimeout(){}, availableForWrite(){ return 128; }
    };
    case "WiFi": return { clase: "WiFi",
      begin(a){ sim.wifi.ssid = aString(a[0] ?? ""); sim.wifi.desde = sim.t; sim.wifi.estado = 6; if(!sim.wifi.ssid || /^TU_/.test(sim.wifi.ssid)) sim.aviso(`WiFi.begin con "${sim.wifi.ssid}": en la placa de verdad poné tu red (en el simulador conecta igual)`); return 6; },
      status(){ return sim.wifiEstado(); },
      localIP(){ return sim.wifiEstado() === 3 ? "192.168.0.57" : "0.0.0.0"; },
      macAddress(){ return "24:6F:28:AB:12:34"; }, SSID(){ return sim.wifi.ssid; }, RSSI(){ return -58; },
      mode(){}, disconnect(){ sim.wifi.estado = 6; sim.wifi.desde = null; }, setAutoReconnect(){}, reconnect(){ sim.wifi.desde = sim.t; },
      softAP(a){ sim.wifi.ap = aString(a[0]); return true; }, softAPIP(){ return "192.168.4.1"; }, isConnected(){ return sim.wifiEstado() === 3; },
      gatewayIP(){ return "192.168.0.1"; }, setHostname(){ return true; }
    };
    case "ThingSpeak": return { clase: "ThingSpeak",
      begin(a){ sim.ts.iniciado = true; return true; },
      setField(a, s, e){ const [n, v] = a; if(n < 1 || n > 8) err("ThingSpeak.setField: los campos van del 1 al 8", e); sim.ts.campos[n] = v; return 200; },
      setStatus(a){ sim.ts.estado = aString(a[0]); return 200; },
      writeFields(a, s, e){ return escribirTS(sim, a[0], { ...sim.ts.campos }, e, true); },
      writeField(a, s, e){ const [canal, n, v] = a; if(n < 1 || n > 8) err("ThingSpeak.writeField: los campos van del 1 al 8", e); return escribirTS(sim, canal, { [n]: v }, e, false); },
      readFloatField(a){ const [canal, n] = a; const c = sim.ts.canales[canal] || {}; return c[n] !== undefined ? +c[n] : 0; },
      readLongField(a){ const c = sim.ts.canales[a[0]] || {}; return Math.trunc(c[a[1]] || 0); },
      readIntField(a){ const c = sim.ts.canales[a[0]] || {}; return Math.trunc(c[a[1]] || 0); },
      readStringField(a){ const c = sim.ts.canales[a[0]] || {}; return c[a[1]] !== undefined ? aString(c[a[1]]) : ""; },
      getLastReadStatus(){ return 200; }
    };
    case "EEPROM": return { clase: "EEPROM",
      begin(a){ sim.eepromTam = a[0]; return true; },
      read(a){ return sim.eeprom.has(a[0]) ? sim.eeprom.get(a[0]) & 0xFF : 255; },
      write(a){ sim.eeprom.set(a[0], Math.trunc(a[1]) & 0xFF); },
      update(a){ sim.eeprom.set(a[0], Math.trunc(a[1]) & 0xFF); },
      commit(){ sim.aviso("EEPROM.commit(): guardado (en la placa queda aunque la apagues)"); return true; },
      put(a){ sim.eeprom.set("p" + a[0], a[1]); return a[1]; },
      get(a, s, e, sc){ const v = sim.eeprom.get("p" + a[0]); if(v !== undefined && e.args[1]) sim.asignar(e.args[1], v, sc); return v; },
      end(){}
    };
    case "Wire": return { clase: "Wire", begin(){ return true; }, setClock(){}, beginTransmission(){}, endTransmission(){ return 0; }, write(){ return 1; }, requestFrom(){ return 0; }, available(){ return 0; }, read(){ return 0; } };
    case "SPI": return { clase: "SPI", begin(){}, transfer(a){ return 0; } };
    case "ESP": return { clase: "ESP", restart(){ err("ESP.restart(): la placa se reinicia (en el simulador, se detiene)"); }, getFreeHeap(){ return 280000; }, getChipModel(){ return "ESP32-D0WDQ6"; }, getCpuFreqMHz(){ return 240; }, getChipCores(){ return 2; }, getFlashChipSize(){ return 4194304; } };
    case "ArduinoOTA": case "ElegantOTA": case "MDNS": return { clase: n, begin(){ sim.aviso(`${n}: la programación por OTA no se simula (en la placa, se sube el .bin por WiFi)`); return true; }, handle(){}, loop(){}, setHostname(){}, onStart(){}, onEnd(){}, onProgress(){}, onError(){}, setPassword(){}, addService(){} };
    case "ArduinoCloud": return { clase: n, begin(){ sim.aviso("Arduino IoT Cloud no se simula: se conecta con el Device ID y la Device Key"); }, update(){}, addCallback(){}, printDebugInfo(){} };
  }
}
function escribirTS(sim, canal, campos, e, varios){
  if(!sim.ts.iniciado) err("ThingSpeak: falta ThingSpeak.begin(client) en el setup", e);
  if(sim.wifiEstado() !== 3){ sim.h.thingspeak.push({ t: sim.t, canal, campos, codigo: -301 }); sim.aviso("ThingSpeak: el WiFi no está conectado (código -301)"); return -301; }
  if(!Object.keys(campos).length){ sim.h.thingspeak.push({ t: sim.t, canal, campos, codigo: -210 }); return -210; }
  const dt = sim.t - sim.ts.ultimo;
  if(dt < 15000){ sim.h.thingspeak.push({ t: sim.t, canal, campos, codigo: -401 }); sim.aviso("ThingSpeak rechaza los datos que llegan con menos de 15 s de diferencia (código -401)"); if(varios) sim.ts.campos = {}; return -401; }
  sim.ts.ultimo = sim.t;
  sim.ts.canales[canal] = { ...(sim.ts.canales[canal] || {}), ...campos };
  sim.h.thingspeak.push({ t: sim.t, canal, campos, codigo: 200 });
  if(varios) sim.ts.campos = {};
  return 200;
}

/* ================= Clases de las librerías ================= */
const CONSTRUCTORES = {
  DHT(args, sim, nodo){
    const [pin, tipo] = args;
    return { clase: "DHT", pin, tipo, iniciado: false,
      begin(){ this.iniciado = true; },
      readTemperature(a){ if(!this.iniciado) sim.aviso("DHT: falta dht.begin() en el setup"); if(this.pin !== 33) { sim.aviso(`DHT en el pin ${this.pin}: en la placa de la cátedra está en el 33 (da nan)`); return NaN; } const c = sim.ent.dht.t; return a && a[0] ? c * 9 / 5 + 32 : c; },
      readHumidity(){ if(this.pin !== 33) return NaN; return sim.ent.dht.h; },
      computeHeatIndex(a){ const [t, h, f] = a; const tf = f === false ? t * 9 / 5 + 32 : t; let hi = 0.5 * (tf + 61 + (tf - 68) * 1.2 + h * 0.094); if(hi > 79) hi = -42.379 + 2.04901523 * tf + 10.14333127 * h - 0.22475541 * tf * h - 0.00683783 * tf * tf - 0.05481717 * h * h + 0.00122874 * tf * tf * h + 0.00085282 * tf * h * h - 0.00000199 * tf * tf * h * h; return f === false ? (hi - 32) * 5 / 9 : hi; },
      convertCtoF(a){ return a[0] * 9 / 5 + 32; }, convertFtoC(a){ return (a[0] - 32) * 5 / 9; }
    };
  },
  Adafruit_SH1106G(args, sim){ return nuevoDisplay(sim, args[0] || 128, args[1] || 64, "SH1106G"); },
  Adafruit_SSD1306(args, sim){ return nuevoDisplay(sim, args[0] || 128, args[1] || 64, "SSD1306"); },
  WiFiClient(){ return { clase: "WiFiClient", connected(){ return true; }, stop(){}, available(){ return 0; }, setInsecure(){} }; },
  WiFiClientSecure(){ return { clase: "WiFiClientSecure", setInsecure(){}, setCACert(){}, connected(){ return true; }, stop(){} }; },
  PubSubClient(args, sim){
    return { clase: "PubSubClient", servidor: null, puerto: 1883, conectado: false, subs: new Set(), cb: null, id: null,
      setServer(a){ this.servidor = aString(a[0]); this.puerto = a[1]; },
      setCallback(a, s, e){ if(!a[0] || !a[0].funcion) err("setCallback: va el nombre de la función que recibe los mensajes", e); this.cb = a[0].funcion; },
      connect(a, s, e){
        if(!this.servidor) err("PubSubClient: falta client.setServer(broker, 1883) antes de connect", e);
        if(sim.wifiEstado() !== 3){ sim.h.mqtt.push({ t: sim.t, tipo: "error", texto: "connect sin WiFi" }); return false; }
        this.conectado = true; this.id = aString(a[0] ?? "");
        sim.h.mqtt.push({ t: sim.t, tipo: "conn", id: this.id, servidor: this.servidor, puerto: this.puerto });
        return true;
      },
      connected(){ return this.conectado && sim.wifiEstado() === 3; },
      state(){ return this.conectado ? 0 : -1; },
      disconnect(){ this.conectado = false; },
      subscribe(a, s, e){ if(!this.conectado) { sim.aviso("MQTT: subscribe antes de conectar"); return false; } this.subs.add(aString(a[0])); sim.h.mqtt.push({ t: sim.t, tipo: "sub", topic: aString(a[0]) }); sim.mqttSubs = this.subs; return true; },
      unsubscribe(a){ this.subs.delete(aString(a[0])); return true; },
      publish(a, s, e){ if(!this.conectado){ sim.aviso("MQTT: publish sin estar conectado al broker"); return false; } const msg = { t: sim.t, tipo: "pub", topic: aString(a[0]), payload: aString(a[1]) }; sim.h.mqtt.push(msg); if(this.subs.has(msg.topic)) sim.mqtt.cola.push({ topic: msg.topic, payload: msg.payload }); return true; },
      loop(){
        if(!this.conectado) return false;
        while(sim.mqtt.cola.length){
          const m = sim.mqtt.cola.shift();
          if(!this.subs.has(m.topic)) continue;
          sim.h.mqtt.push({ t: sim.t, tipo: "llega", topic: m.topic, payload: m.payload });
          if(this.cb) sim.correrSync(this.cb, [{ v: m.topic }, { v: [...m.payload].map(c => c.charCodeAt(0)) }, { v: m.payload.length }]);
        }
        return true;
      },
      setBufferSize(){ return true; }, setKeepAlive(){}
    };
  },
  Servo(args, sim){ return { clase: "Servo", pin: null, attach(a){ this.pin = a[0]; return 1; }, write(a){ const v = Math.max(0, Math.min(180, a[0])); sim.h.servo[this.pin] = v; sim.anotar("pwm", this.pin, v); }, read(){ return sim.h.servo[this.pin] || 0; }, detach(){}, attached(){ return this.pin !== null; }, setPeriodHertz(){} }; },
  Ticker(args, sim){
    return { clase: "Ticker",
      attach(a, s, e){ this.prog(a[0] * 1000, a[1], false, e, a[2]); }, attach_ms(a, s, e){ this.prog(a[0], a[1], false, e, a[2]); },
      once(a, s, e){ this.prog(a[0] * 1000, a[1], true, e, a[2]); }, once_ms(a, s, e){ this.prog(a[0], a[1], true, e, a[2]); },
      detach(){ if(this.k) this.k.activo = false; }, active(){ return !!(this.k && this.k.activo); },
      prog(ms, fn, una, e, arg){ if(!fn || !fn.funcion) err("Ticker: va el nombre de la función", e); if(this.k) this.k.activo = false; this.k = { prox: sim.t + ms, periodo: ms, fn: fn.funcion, una, activo: true, arg: arg !== undefined ? { v: arg } : undefined }; sim.tickers.push(this.k); }
    };
  },
  WiFiServer(args, sim){ return { clase: "WiFiServer", puerto: args[0] || 80, begin(){ sim.aviso(`Servidor web en el puerto ${this.puerto}: en el simulador no llegan pedidos del navegador`); }, available(){ return { clase: "WiFiClient", connected(){ return false; }, available(){ return 0; }, stop(){}, println(){}, print(){}, readStringUntil(){ return ""; }, read(){ return -1; } }; } }; },
  WebServer(args, sim){ return { clase: "WebServer", on(){}, begin(){ sim.aviso("WebServer: en el simulador no llegan pedidos del navegador"); }, handleClient(){}, send(){}, arg(){ return ""; }, uri(){ return "/"; } }; },
  HTTPClient(args, sim){ return { clase: "HTTPClient", begin(a){ this.url = aString(a[0]); return true; }, GET(){ sim.h.avisos.push({ t: sim.t, s: `HTTP GET ${this.url} (simulado: 200)` }); return 200; }, POST(){ return 200; }, getString(){ return "{}"; }, end(){}, addHeader(){} }; },
  UniversalTelegramBot(args, sim){ return { clase: "UniversalTelegramBot", getUpdates(){ return 0; }, sendMessage(a){ sim.h.avisos.push({ t: sim.t, s: `Telegram: ${aString(a[1])}` }); return true; }, last_message_received: 0 }; },
  IPAddress(args){ return args.join("."); }
};

const TOLERANTES = new Set(["HTTPClient", "WebServer", "WiFiServer", "UniversalTelegramBot", "WiFiClient", "WiFiClientSecure", "ArduinoOTA", "ElegantOTA", "MDNS", "ArduinoCloud", "Wire", "SPI", "WiFiConnectionHandler"]);
function tolerante(o, sim){
  return new Proxy(o, { get(t, p){ if(p in t || typeof p !== "string") return t[p]; return function(){ sim.aviso(`${t.clase}.${p}() no hace nada en el simulador`); return 0; }; } });
}
CONSTRUCTORES.WiFiConnectionHandler = (args, sim) => ({ clase: "WiFiConnectionHandler" });

/* El display OLED (SH1106 o SSD1306): se guardan las cosas que se dibujan y display() las muestra */
function nuevoDisplay(sim, ancho, alto, modelo){
  const d = { clase: "Display", modelo, ancho, alto, ops: [], x: 0, y: 0, tam: 1, color: 1, iniciado: false, wrap: true,
    begin(a){ this.iniciado = true; this.dir = a[0]; if(a[0] !== 0x3C && a[0] !== 0x3D && a[0] !== 2) sim.aviso(`display.begin(0x${(a[0] >>> 0).toString(16)}): el display de la placa está en la dirección 0x3C`); if(modelo === "SSD1306" && a[1] === 0x3C) this.dir = 0x3C; sim.display = this; return true; },
    clearDisplay(){ this.ops = []; },
    setTextSize(a){ this.tam = Math.max(1, a[0] | 0); }, setTextColor(a){ this.color = a[0]; }, setCursor(a){ this.x = a[0]; this.y = a[1]; },
    setTextWrap(a){ this.wrap = !!a[0]; }, setRotation(){}, invertDisplay(a){ this.invertido = !!a[0]; }, dim(){}, cp437(){}, setFont(){},
    getCursorX(){ return this.x; }, getCursorY(){ return this.y; }, width(){ return this.ancho; }, height(){ return this.alto; },
    escribir(s){
      for(const ch of s){
        if(ch === "\n"){ this.x = 0; this.y += 8 * this.tam; continue; }
        if(ch === "\r") continue;
        if(this.wrap && this.x + 6 * this.tam > this.ancho){ this.x = 0; this.y += 8 * this.tam; }
        const ult = this.ops[this.ops.length - 1];
        if(ult && ult.k === "txt" && ult.y === this.y && ult.tam === this.tam && ult.x + ult.s.length * 6 * this.tam === this.x && ult.color === this.color) ult.s += ch;
        else this.ops.push({ k: "txt", x: this.x, y: this.y, s: ch, tam: this.tam, color: this.color });
        this.x += 6 * this.tam;
      }
    },
    print(a, s, e, sc){ this.escribir(imprimir(sim, a, e, sc, false)); }, println(a, s, e, sc){ this.escribir(imprimir(sim, a, e, sc, true)); },
    printf(a){ this.escribir(formatear(aString(a[0]), a.slice(1))); }, write(a){ this.escribir(typeof a[0] === "number" ? String.fromCharCode(a[0]) : aString(a[0])); },
    drawPixel(a){ this.ops.push({ k: "px", x: a[0], y: a[1], color: a[2] }); },
    drawLine(a){ this.ops.push({ k: "linea", x1: a[0], y1: a[1], x2: a[2], y2: a[3], color: a[4] }); },
    drawFastHLine(a){ this.ops.push({ k: "linea", x1: a[0], y1: a[1], x2: a[0] + a[2] - 1, y2: a[1], color: a[3] }); },
    drawFastVLine(a){ this.ops.push({ k: "linea", x1: a[0], y1: a[1], x2: a[0], y2: a[1] + a[2] - 1, color: a[3] }); },
    drawRect(a){ this.ops.push({ k: "rect", x: a[0], y: a[1], w: a[2], h: a[3], color: a[4] }); },
    fillRect(a){ this.ops.push({ k: "rect", x: a[0], y: a[1], w: a[2], h: a[3], color: a[4], lleno: true }); },
    drawRoundRect(a){ this.ops.push({ k: "rect", x: a[0], y: a[1], w: a[2], h: a[3], r: a[4], color: a[5] }); },
    fillRoundRect(a){ this.ops.push({ k: "rect", x: a[0], y: a[1], w: a[2], h: a[3], r: a[4], color: a[5], lleno: true }); },
    drawCircle(a){ this.ops.push({ k: "circ", x: a[0], y: a[1], r: a[2], color: a[3] }); },
    fillCircle(a){ this.ops.push({ k: "circ", x: a[0], y: a[1], r: a[2], color: a[3], lleno: true }); },
    drawTriangle(a){ this.ops.push({ k: "tri", p: a.slice(0, 6), color: a[6] }); },
    fillTriangle(a){ this.ops.push({ k: "tri", p: a.slice(0, 6), color: a[6], lleno: true }); },
    drawBitmap(){}, startscrollright(){}, stopscroll(){},
    display(){ if(!this.iniciado) sim.aviso("display.display() sin display.begin(0x3C, true): en la placa no se ve nada"); this.cuadro = { ops: this.ops.map(o => ({ ...o })), t: sim.t, invertido: this.invertido }; sim.display = this; sim.h.display.push({ t: sim.t, texto: this.ops.filter(o => o.k === "txt").map(o => o.s).join(" ") }); if(sim.h.display.length > 400) sim.h.display.shift(); }
  };
  return d;
}

/* ================= Pruebas sin pantalla =================
   prueba: { hasta: ms, entradas: [{ t, boton | pote | dht | touch | serial | mqtt }], opts }
   devuelve el simulador ya corrido (su historia en s.h) para que la página compare */
function probar(codigo, prueba, opts = {}){
  const s = new Sim(codigo, { ...opts, ...(prueba.opts || {}) });
  if(s.error) return s;
  s.programadas = (prueba.entradas || []).map(x => ({ ...x })).sort((a, b) => a.t - b.t);
  s.atender();
  const r = s.avanzar(prueba.hasta || 3000, prueba.limite || 4e6);
  if(r === "lento" && !s.error) s.error = { msg: "el programa hace demasiadas cuentas sin esperar (¿un bucle sin fin sin delay?)", linea: s.linea };
  return s;
}
/* El valor de un pin en un momento (de la historia) */
function valorEn(lista, t, def = 0){ let v = def; for(const x of lista || []) { if(x.t <= t + 1e-9) v = x.v; else break; } return v; }

/* ---- Lo que se espera de una prueba. Cada control: { k, ..., ok?, error? } (ok y error: los textos que se muestran)
   pin      { pin, t, v }               encendido (1) o apagado (0) en el momento t (digitalWrite o PWM > 0)
   brillo   { pin, t, v, tol }          la fracción de PWM (0 a 1) en t
   pwm      { pin, t, v, tol }          el valor de PWM tal cual (0-255, 0-4095…) en t
   cambios  { pin, desde, hasta, min, max }  cuántas veces se prende o se apaga en ese lapso
   periodo  { pin, ms, tol, desde }     cada cuánto se prende (de un encendido al siguiente)
   serial   { re, flags, desde, hasta, no }  lo que sale por el monitor serie (expresión regular)
   display  { re, flags, t, no }        lo que se ve en el display en t (o en algún momento)
   ts       { min, max, cada: [a, b], campos: { n: [min, max] | valor }, rechazos }   los envíos a ThingSpeak
   mqtt     { tipo, topic, re, min }    conexión, suscripción, publicación o mensaje que llega
   recorre  { pin, de, a, valores, tol } el PWM pasa de "de" a "a" por al menos "valores" valores distintos
   eeprom   { dir, v }                  lo que quedó guardado en la EEPROM (255: nunca se escribió)
   serial con veces: [min, max]         cuántas veces aparece la expresión */
const seg = ms => String(+(ms / 1000).toFixed(2)).replace(".", ",") + " s";
const nombrePin = pin => PLACA[pin] ? `${PLACA[pin].nombre} (GPIO ${pin})` : `GPIO ${pin}`;
function encendidos(lista){
  const out = []; let ant = 0;
  for(const x of lista || []){ const on = x.v > 0 ? 1 : 0; if(on !== ant || !out.length) out.push({ t: x.t, v: on }); ant = on; }
  return out;
}
function controlar(s, c){
  const h = s.h, t = c.t ?? 0;
  const res = (ok, def) => ({ ok, msg: ok ? (c.ok || def[0]) : (c.error || def[1]) });
  switch(c.k){
    case "pin": {
      const l = h.brillo[c.pin], v = l && l.length ? (valorEn(l, t, 0) > 0 ? 1 : 0) : null, que = c.v ? "encendido" : "apagado";
      if(v === null) return res(false, ["", `${nombrePin(c.pin)}: nunca se usó como salida (¿falta pinMode(${c.pin}, OUTPUT)?)`]);
      return res(v === c.v, [`${nombrePin(c.pin)} ${que} en t = ${seg(t)}`, `En t = ${seg(t)}, ${nombrePin(c.pin)} tendría que estar ${que} y está ${v ? "encendido" : "apagado"}`]);
    }
    case "brillo": case "pwm": {
      const l = (c.k === "pwm" ? h.pwm : h.brillo)[c.pin], v = valorEn(l, t, 0), tol = c.tol ?? (c.k === "pwm" ? 1 : 0.02);
      const fmt = x => c.k === "pwm" ? String(Math.round(x)) : Math.round(x * 100) + " %";
      return res(Math.abs(v - c.v) <= tol, [`${nombrePin(c.pin)}: ${c.k === "pwm" ? "PWM" : "brillo"} ${fmt(c.v)} en t = ${seg(t)}`, `En t = ${seg(t)}, ${nombrePin(c.pin)} tendría que tener ${c.k === "pwm" ? "PWM" : "brillo"} ${fmt(c.v)} y tiene ${fmt(v)}`]);
    }
    case "recorre": {
      const l = (h.pwm[c.pin] || []).filter(x => x.t >= (c.desde ?? 0) && x.t <= (c.hasta ?? Infinity)), vs = l.map(x => x.v), tol = c.tol ?? 2;
      const mn = vs.length ? Math.min(...vs) : NaN, mx = vs.length ? Math.max(...vs) : NaN, distintos = new Set(vs).size;
      if(!vs.length) return res(false, ["", `${nombrePin(c.pin)} no recibe PWM (¿falta analogWrite?)`]);
      if(distintos < (c.valores ?? 2)) return res(false, ["", `${nombrePin(c.pin)} pasa por ${distintos} valores de PWM: tendría que cambiar de a poco`]);
      return res(mn <= c.de + tol && mx >= c.a - tol, [`${nombrePin(c.pin)} va de ${c.de} a ${c.a}`, `${nombrePin(c.pin)} va de ${mn} a ${mx} y tendría que ir de ${c.de} a ${c.a}`]);
    }
    case "eeprom": {
      const v = s.eeprom.has(c.dir) ? s.eeprom.get(c.dir) : 255;
      return res(v === c.v, [`La EEPROM guarda ${c.v} en la dirección ${c.dir}`, `En la dirección ${c.dir} de la EEPROM quedó ${v} y tendría que quedar ${c.v}${v === 255 ? " (¿falta EEPROM.write y EEPROM.commit?)" : ""}`]);
    }
    case "cambios": {
      const d = c.desde ?? 0, a = c.hasta ?? Infinity;
      const n = encendidos(h.brillo[c.pin]).filter((x, i) => i > 0 && x.t > d && x.t <= a).length;
      const ok = n >= (c.min ?? 1) && n <= (c.max ?? Infinity);
      return res(ok, [`${nombrePin(c.pin)} cambia ${n} veces`, `${nombrePin(c.pin)} cambió ${n} ${n === 1 ? "vez" : "veces"} entre ${seg(d)} y ${a === Infinity ? "el final" : seg(a)}${c.min != null ? ` (se esperaban${c.max != null && c.max !== c.min ? ` entre ${c.min} y ${c.max}` : c.max === c.min ? ` ${c.min}` : ` al menos ${c.min}`})` : ""}`]);
    }
    case "periodo": {
      const subidas = encendidos(h.brillo[c.pin]).filter((x, i) => i > 0 && x.v === 1 && x.t >= (c.desde ?? 0)).map(x => x.t);
      if(subidas.length < 3) return res(false, ["", `${nombrePin(c.pin)} no titila: se prendió ${subidas.length} ${subidas.length === 1 ? "vez" : "veces"}`]);
      const p = (subidas[subidas.length - 1] - subidas[0]) / (subidas.length - 1), tol = c.tol ?? c.ms * 0.1;
      return res(Math.abs(p - c.ms) <= tol, [`${nombrePin(c.pin)} se prende cada ${seg(c.ms)}`, `${nombrePin(c.pin)} se prende cada ${seg(p)} y tendría que ser cada ${seg(c.ms)}`]);
    }
    case "serial": {
      const txt = h.serial.filter(x => x.t >= (c.desde ?? 0) && x.t <= (c.hasta ?? Infinity)).map(x => x.s).join("");
      if(c.veces){
        const n = (txt.match(new RegExp(c.re, (c.flags ?? "") + "g")) || []).length, [a, b] = c.veces;
        return res(n >= a && n <= b, [`El monitor serie lo muestra ${n} veces`, `El monitor serie muestra /${c.re}/ ${n} ${n === 1 ? "vez" : "veces"} entre ${seg(c.desde ?? 0)} y ${c.hasta == null ? "el final" : seg(c.hasta)} (tendrían que ser ${a === b ? a : `entre ${a} y ${b}`})`]);
      }
      const hay = new RegExp(c.re, c.flags ?? "").test(txt);
      return res(c.no ? !hay : hay, [c.no ? "El monitor serie no muestra lo que no tiene que mostrar" : "El monitor serie muestra lo pedido", c.no ? `El monitor serie muestra algo que no va (/${c.re}/)` : !txt ? "No salió nada por el monitor serie (¿falta Serial.begin(115200)?)" : `El monitor serie no muestra lo pedido (/${c.re}/)`]);
    }
    case "display": {
      const re = new RegExp(c.re, c.flags ?? "");
      let ok;
      if(c.t != null){ let f = null; for(const x of h.display) if(x.t <= c.t) f = x; ok = !!f && re.test(f.texto); }
      else ok = h.display.some(x => re.test(x.texto));
      if(c.no) ok = !ok;
      return res(ok, [`El display muestra lo pedido${c.t != null ? ` en t = ${seg(c.t)}` : ""}`, !h.display.length ? "El display no mostró nada (¿falta display.display() después de escribir?)" : `El display no muestra lo pedido${c.t != null ? ` en t = ${seg(c.t)}` : ""} (/${c.re}/)`]);
    }
    case "ts": {
      const ok = h.thingspeak.filter(x => x.codigo === 200), malos = h.thingspeak.filter(x => x.codigo === -401).length;
      if(c.rechazos != null && malos > c.rechazos) return res(false, ["", `ThingSpeak rechazó ${malos} envíos por mandar con menos de 15 s de diferencia`]);
      if(c.min != null && ok.length < c.min) return res(false, ["", ok.length ? `Llegaron ${ok.length} envíos a ThingSpeak y se esperaban al menos ${c.min}` : "No llegó ningún envío a ThingSpeak (¿WiFi conectado, ThingSpeak.begin(cliente) y writeFields?)"]);
      if(c.max != null && ok.length > c.max) return res(false, ["", `Llegaron ${ok.length} envíos a ThingSpeak y tendrían que ser como mucho ${c.max}`]);
      if(c.cada){
        for(let i = 1; i < ok.length; i++){ const d = ok[i].t - ok[i - 1].t; if(d < c.cada[0] || d > c.cada[1]) return res(false, ["", `Entre dos envíos a ThingSpeak pasaron ${seg(d)} (tendría que ser entre ${seg(c.cada[0])} y ${seg(c.cada[1])})`]); }
      }
      for(const [n, e] of Object.entries(c.campos || {})){
        for(const x of ok){
          const v = x.campos[n];
          if(v === undefined) return res(false, ["", `El envío de los ${seg(x.t)} no tiene el campo ${n}`]);
          const num = typeof v === "number" ? v : parseFloat(v);
          const bien = Array.isArray(e) ? num >= e[0] && num <= e[1] : typeof e === "number" ? Math.abs(num - e) <= (c.tol ?? 0.01) : String(v) === String(e);
          if(!bien) return res(false, ["", `En el envío de los ${seg(x.t)}, el campo ${n} vale ${v} (tendría que ${Array.isArray(e) ? `estar entre ${e[0]} y ${e[1]}` : `ser ${e}`})`]);
        }
      }
      return res(true, [`ThingSpeak recibe ${ok.length} envíos`, ""]);
    }
    case "mqtt": {
      const xs = h.mqtt.filter(x => x.tipo === (c.tipo || "pub") && (c.topic == null || x.topic === c.topic) && (c.re == null || new RegExp(c.re, c.flags ?? "").test(x.payload || "")));
      const qué = { conn: "conexión al broker", sub: "suscripción", pub: "publicación", llega: "mensaje recibido" }[c.tipo || "pub"];
      return res(xs.length >= (c.min ?? 1), [`MQTT: ${qué}${c.topic ? ` en ${c.topic}` : ""}`, `MQTT: no hay ${qué}${c.topic ? ` en «${c.topic}»` : ""}${c.re ? ` con /${c.re}/` : ""}`]);
    }
  }
  return { ok: false, msg: `control desconocido: ${c.k}` };
}
/* Corre las pruebas de un ejercicio: [{ nombre, hasta, entradas, opts, esperar }] → [{ nombre, sim, checks }] */
function pruebas(codigo, lista, opts = {}){
  return lista.map(p => {
    const s = probar(codigo, p, opts);
    const checks = s.error ? [{ ok: false, msg: `${s.error.compilacion ? "No compila" : "Error al correr"}: ${s.error.msg}${s.error.linea ? ` (línea ${s.error.linea}${s.error.archivo && !/\.ino$/.test(s.error.archivo) ? ` de ${s.error.archivo}` : ""})` : ""}` }]
      : (p.esperar || []).map(c => controlar(s, c));
    return { nombre: p.nombre, sim: s, checks };
  });
}

const API = { crear: (codigo, opts) => new Sim(codigo, opts), probar, pruebas, controlar, valorEn, PLACA, formatear, version: 1 };
if(typeof module !== "undefined" && module.exports) module.exports = API; else raiz.ESP32 = API;
})(typeof window !== "undefined" ? window : globalThis);
