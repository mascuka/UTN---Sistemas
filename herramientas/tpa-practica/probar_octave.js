// Compara el Octave del navegador (practica/octave/octave.js) con el Octave de verdad (octave-cli), caso por caso:
// la salida tiene que ser igual (sin espacios al final de las líneas) y los dos tienen que dar error en los mismos casos.
// Cada caso se corre dos veces en el navegador: con sus funciones propias y con los .m del profe cargados como en la
// página (practica/octave/profe/p1 y p2, los que se ejecutan): las dos tienen que dar lo mismo que Octave.
// Uso, desde la raíz:  node herramientas/tpa-practica/probar_octave.js [archivo.json con más casos]
// Los casos van en casos-octave.json (al lado de este archivo): [{ "nombre": "...", "codigo": "..." }].
// Las funciones del profe se toman de los ZIP de material/ (1º y 2º parcial).
const fs = require("fs"), os = require("os"), path = require("path"), { execFileSync } = require("child_process");
const RAIZ = path.resolve(__dirname, "..", "..");
const O = require(path.join(RAIZ, "practica/octave/octave.js"));
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "octave-"));
// Las funciones del profe en una carpeta para el addpath
for(const z of ["material/tecnologias-para-la-automatizacion/p1/funciones-octave-1er-parcial.zip", "material/tecnologias-para-la-automatizacion/p2/funciones-octave-2do-parcial.zip"])
  execFileSync("unzip", ["-qo", path.join(RAIZ, z), "-d", path.join(tmp, "fun")]);
const carpetas = ["funciones-1er-parcial", "funciones-2do-parcial"].map(c => path.join(tmp, "fun", c));
// Los .m del profe tal como los carga la página (los del 2º parcial pisan a los del 1º si se llaman igual)
const PROFE = path.join(RAIZ, "practica/octave/profe");
const deCarpeta = p => JSON.parse(fs.readFileSync(path.join(PROFE, p, "archivos.json"), "utf8")).filter(a => a.ejecuta)
  .map(a => ({ nombre: a.nombre, texto: fs.readFileSync(path.join(PROFE, p, a.nombre), "utf8") }));
const archivos = [...deCarpeta("p1"), ...deCarpeta("p2")].filter((a, i, xs) => xs.findIndex(b => b.nombre === a.nombre) >= i && !xs.slice(i + 1).some(b => b.nombre === a.nombre));
const casos = JSON.parse(fs.readFileSync(process.argv[2] || path.join(__dirname, "casos-octave.json"), "utf8"));
const limpiar = s => s.replace(/\r/g, "").split("\n").map(l => l.replace(/\s+$/, "")).join("\n").replace(/\n+$/, "");
let mal = 0;
for(const c of casos){
  const f = path.join(tmp, "caso.m");
  fs.writeFileSync(f, (/\bfunction\b/.test(c.codigo) ? "1;\n" : "") + c.codigo + "\n");
  let real = "", errReal = false;
  try {
    real = execFileSync("octave-cli", ["-q", "--no-window-system", "--eval", `addpath('${carpetas.join("','")}'); source('${f}');`], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], timeout: 60000 });
  } catch(e){ real = e.stdout || ""; errReal = true; }
  const a = limpiar(real);
  const modos = [["", O.correr(c.codigo)], [" (con los .m del profe)", O.correr(c.codigo, { archivos })]];
  const malos = modos.filter(([, mio]) => limpiar(mio.salida) !== a || errReal !== !!mio.error);
  if(!malos.length){ console.log("ok   " + c.nombre); continue; }
  mal++;
  for(const [modo, mio] of malos){
    const b = limpiar(mio.salida), okErr = errReal === !!mio.error;
    console.log("MAL  " + c.nombre + modo + (okErr ? "" : `  (error: octave ${errReal}, navegador ${mio.error ? mio.error.msg : "no"})`));
    const la = a.split("\n"), lb = b.split("\n");
    for(let i = 0; i < Math.max(la.length, lb.length); i++) if(la[i] !== lb[i]){ console.log(`     línea ${i + 1}\n     octave:    ${JSON.stringify(la[i])}\n     navegador: ${JSON.stringify(lb[i])}`); break; }
  }
}
console.log(mal ? `\n${mal} DISTINTOS de ${casos.length}` : `\nTODO IGUAL (${casos.length} casos)`);
process.exit(mal ? 1 : 0);
