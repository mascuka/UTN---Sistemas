// Valida la Práctica de TPA con el mismo Octave y las mismas comparaciones que usa la página:
// la solución de cada ejercicio tiene que pasar (sin error, variables, controles y respuestas) y el código inicial no.
// Desde la raíz:  node herramientas/tpa-practica/validar.js [practica/tpa-p1/ejercicios.json ...]
const fs = require("fs"), path = require("path");
const RAIZ = path.join(__dirname, "..", "..");
const Octave = require(path.join(RAIZ, "practica/octave/octave.js"));

// Las funciones de comparación, tal cual están en index.html
const html = fs.readFileSync(path.join(RAIZ, "index.html"), "utf8");
const fuente = nombre => {
  const i = html.indexOf(`\nfunction ${nombre}(`);
  if(i < 0) throw new Error(`no está ${nombre} en index.html`);
  return html.slice(i + 1, html.indexOf("\n}\n", i) + 2);
};
const { sinComentarios, sinComentariosOct, verificarEjp, compararVar } = new Function(
  ["sinComentarios", "sinComentariosOct", "verificarEjp", "compararVar"].map(fuente).join("\n") + "\nreturn { sinComentarios, sinComentariosOct, verificarEjp, compararVar };")();
const leerNumero = new Function(`return ${html.match(/const leerNumero = (s => .*);\n/)[1]}`)();
const respuestaOk = (x, v) => x.opciones ? v === x.valor
  : Math.abs(leerNumero(v) - x.valor) <= (x.tol ?? 0.01) * (x.relativa ? Math.max(1, Math.abs(x.valor)) : 1);

// Como en la página: los .m de la carpeta del profe de ese parcial (practica/octave/profe/pN) se cargan al correr
let profe = [];
const carpetaProfe = f => {
  const c = path.join(RAIZ, "practica/octave/profe", (f.match(/tpa-(p\d)/) || [])[1] || "-");
  if(!fs.existsSync(path.join(c, "archivos.json"))) return [];
  return JSON.parse(fs.readFileSync(path.join(c, "archivos.json"), "utf8")).filter(a => a.ejecuta)
    .map(a => ({ nombre: a.nombre, texto: fs.readFileSync(path.join(c, a.nombre), "utf8") }));
};
function correr(ej, cual){
  const codigo = ej.archivos.map(a => a[cual] ?? a.inicial).join("\n");
  const archivos = profe.filter(a => !(ej.ocultar || []).includes(a.nombre.replace(/\.m$/, "")));
  const r = Octave.correr(codigo, { ocultar: ej.ocultar, archivos, limiteMs: 20000 });
  const checks = [];
  if(r.error) checks.push({ ok: false, msg: `error: ${r.error.msg} (línea ${r.error.linea})` });
  (ej.vars || []).forEach(v => checks.push(compararVar(v, r.vars)));
  const texto = ej.archivos.map(a => sinComentariosOct(a[cual] ?? a.inicial)).join("\n");
  checks.push(...verificarEjp(texto, ej.checks || []));
  return { r, checks };
}

let mal = 0, total = 0;
const archivos = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(path.join(RAIZ, "practica"))
  .filter(d => d.startsWith("tpa-")).map(d => `practica/${d}/ejercicios.json`).filter(f => fs.existsSync(path.join(RAIZ, f)));
for(const f of archivos){
  const d = JSON.parse(fs.readFileSync(path.join(RAIZ, f), "utf8"));
  profe = carpetaProfe(f);
  console.log(`\n${f} · ${d.grupo}${profe.length ? ` · con ${profe.length} .m del profe` : ""}`);
  for(const p of d.partes) for(const ej of p.ejercicios){
    total++;
    const probs = [];
    if(ej.tipo === "codigo"){
      // No se corre (C++ de la ESP32): la solución tiene que pasar los checks y el código inicial no
      const pasa = cual => verificarEjp(ej.archivos.map(a => sinComentarios(a[cual])).join("\n"), ej.checks || []);
      pasa("solucion").filter(c => !c.ok).forEach(c => probs.push(`la solución no pasa: ${c.msg}`));
      if(!(ej.checks || []).length) probs.push("no tiene checks");
      else if(pasa("inicial").every(c => c.ok)) probs.push("el código inicial ya pasa");
    }
    if(ej.tipo === "octave"){
      const s = correr(ej, "solucion");
      s.checks.filter(c => !c.ok).forEach(c => probs.push(`la solución no pasa: ${c.msg}`));
      const i = correr(ej, "inicial");
      if(i.checks.every(c => c.ok) && (ej.vars || []).length + (ej.checks || []).length) probs.push("el código inicial ya pasa");
      if(i.r.error && !/no está definida|undefined/.test(i.r.error.msg)) probs.push(`el código inicial da error: ${i.r.error.msg}`);
    }
    for(const x of ej.respuestas || []){
      if(x.valor === undefined) probs.push(`respuesta sin valor: ${x.pregunta}`);
      else if(x.opciones && !x.opciones.includes(x.valor)) probs.push(`la respuesta no está entre las opciones: ${x.pregunta}`);
      else if(!respuestaOk(x, x.mostrar)) probs.push(`lo que se muestra (${x.mostrar}) no pasa como respuesta: ${x.pregunta}`);
    }
    for(const it of ej.items || []) if(!ej.opciones.includes(it.respuesta)) probs.push(`opción inexistente: ${it.respuesta}`);
    if(ej.imagen && !fs.existsSync(path.join(RAIZ, ej.imagen.url))) probs.push(`falta la imagen ${ej.imagen.url}`);
    mal += probs.length > 0;
    console.log(`${probs.length ? "✗" : "✓"} ${ej.id} ${ej.titulo}${probs.map(t => `\n    ${t}`).join("")}`);
  }
}
console.log(`\n${mal ? `${mal} de ${total} con problemas` : `TODO BIEN (${total} ejercicios)`}`);
process.exit(mal ? 1 : 0);
