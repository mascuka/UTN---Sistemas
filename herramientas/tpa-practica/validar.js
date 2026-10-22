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
  : Math.abs(leerNumero(v) - x.valor) <= Math.max((x.tol ?? 0.01) * (x.relativa ? Math.max(1, Math.abs(x.valor)) : 1), (x.tolRel || 0) * Math.abs(x.valor));

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

// ---- El simulacro (practica/tpa-pN/simulacro.json): problemas con números al azar.
// Se arma cada problema con varias semillas, como la página (con sus mismas funciones), y las respuestas se comparan
// con las del Octave de verdad (octave-cli con la carpeta del profe). Si alguna semilla da un caso raro, la página
// prueba con otra: acá se avisa si pasa seguido.
const { execFileSync } = require("child_process"), os = require("os");
const AZ = new Function(["azarRng", "valoresAzar", "numAzar", "plantilla", "mostrarAzar", "instanciarAzar"].map(fuente).join("\n")
  + "\nreturn { instanciarAzar };")();
const SEMILLAS = +(process.env.SEMILLAS || 12);
const mudas = fs.mkdtempSync(path.join(os.tmpdir(), "sin-graficos-"));
for(const n of ["plot", "plot3", "figure", "subplot", "title", "xlabel", "ylabel", "zlabel", "grid", "hold", "axis", "view", "legend", "text", "quiver3", "Dibujar_Temporal", "animar_trayectoria", "DibujarEjes", "dibujarOrigen", "dibujarSistemasDeEjesCoordenadosDeRobot"])
  fs.writeFileSync(path.join(mudas, n + ".m"), `function varargout = ${n}(varargin)\n  varargout = cell(1, nargout);\nend\n`);
const simulacros = process.argv.slice(2).length ? [] : fs.readdirSync(path.join(RAIZ, "practica")).filter(d => d.startsWith("tpa-"))
  .map(d => `practica/${d}/simulacro.json`).filter(f => fs.existsSync(path.join(RAIZ, f)));
for(const f of simulacros){
  const d = JSON.parse(fs.readFileSync(path.join(RAIZ, f), "utf8"));
  profe = carpetaProfe(f);
  const carpeta = path.join(RAIZ, "practica/octave/profe", f.match(/tpa-(p\d)/)[1]);
  console.log(`\n${f} · ${d.grupo} · ${SEMILLAS} semillas por problema, contra octave-cli`);
  for(const p of d.partes) for(const ej of p.ejercicios){
    total++;
    const probs = [], raras = [];
    ej._base = { consigna: ej.consigna, datos: ej.datos, tabla: ej.tabla, archivos: ej.archivos, respuestas: ej.respuestas, pistas: ej.pistas, pasos: ej.pasos };
    let script = "", buenas = [];
    for(let s = 1; s <= SEMILLAS; s++){
      const inst = AZ.instanciarAzar(Octave, ej, s * 7919, profe);
      if(inst.error){ raras.push(`${s}: ${inst.error}`); continue; }
      const malas = inst.respuestas.filter(x => x.opciones ? !x.opciones.includes(x.valor) : !Number.isFinite(x.valor));
      if(malas.length){ raras.push(`${s}: sin valor en ${malas.map(x => x.pregunta).join(", ")}`); continue; }
      const sobra = [inst.consigna, inst.datos, ...(inst.tabla ? inst.tabla.filas.flat() : []), inst.archivos[0].inicial, inst.archivos[0].solucion, ...inst.respuestas.map(x => x.pregunta)].join(" ").match(/\{\w+(\|\w+)?\}/);
      if(sobra) probs.push(`semilla ${s}: quedó ${sobra[0]} sin reemplazar`);
      const ini = Octave.correr(inst.archivos[0].inicial, { archivos: profe });
      if(ini.error) probs.push(`semilla ${s}: el código inicial da error: ${ini.error.msg}`);
      inst.respuestas.forEach(x => { if(!x.opciones && !respuestaOk(x, x.mostrar)) probs.push(`semilla ${s}: lo que se muestra (${x.mostrar}) no pasa: ${x.pregunta}`); });
      buenas.push([s, inst]);
      script += `\nclear;\n${inst.archivos[0].solucion}\n` + ej._base.respuestas.map((x, i) => x.expr ? `printf('@@${s}_${i}=%s\\n', mat2str(double(${plantilla_(x.expr, inst.v)}), 17));\n` : "").join("");
    }
    if(raras.length > SEMILLAS / 5) probs.push(`demasiadas semillas raras (${raras.length}): ${raras.slice(0, 2).join(" · ")}`);
    // El Octave de verdad, con la misma carpeta del profe
    const arch = path.join(mudas, "simulacro.m");
    fs.writeFileSync(arch, "1;\n" + script);
    let real = "";
    try { real = execFileSync("octave-cli", ["-q", "--no-window-system", "--eval", `addpath('${carpeta}'); addpath('${mudas}'); source('${arch}');`], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], timeout: 300000 }); }
    catch(e){ probs.push("octave-cli dio error: " + String(e.stderr || e.message).split("\n").slice(0, 3).join(" ")); }
    const vals = Object.fromEntries([...real.matchAll(/^@@(\d+_\d+)=(.*)$/gm)].map(m => [m[1], m[2]]));
    const comparadas = Object.keys(vals).length;
    for(const [s, inst] of buenas) inst.respuestas.forEach((x, i) => {
      if(!ej._base.respuestas[i].expr) return;
      const r = vals[`${s}_${i}`];
      if(r === undefined){ if(real) probs.push(`semilla ${s}: Octave no dio ${x.pregunta}`); return; }
      const n = parseFloat(r);
      const esperado = x.opciones ? x.opciones.indexOf(x.valor) + 1 : x.valor;
      if(!(Math.abs(n - esperado) <= 1e-6 * Math.max(1, Math.abs(n)))) probs.push(`semilla ${s}: ${x.pregunta} da ${esperado} en el navegador y ${r} en Octave`);
    });
    if(ej.imagen && !fs.existsSync(path.join(RAIZ, ej.imagen.url))) probs.push(`falta la imagen ${ej.imagen.url}`);
    mal += probs.length > 0;
    console.log(`${probs.length ? "✗" : "✓"} ${ej.id} ${ej.titulo} (${buenas.length}/${SEMILLAS} semillas${raras.length ? `, ${raras.length} raras` : ""}, ${comparadas} respuestas iguales a Octave)${probs.slice(0, 6).map(t => `\n    ${t}`).join("")}`);
  }
}
function plantilla_(t, v){ return t.replace(/\{(\w+)(?:\|(\w+))?\}/g, (m, k) => k in v ? String(v[k]) : m); }

console.log(`\n${mal ? `${mal} de ${total} con problemas` : `TODO BIEN (${total} ejercicios)`}`);
process.exit(mal ? 1 : 0);
