/* Java en el navegador, en un Web Worker (para no trabar la página y poder cortarlo si se cuelga).
   Compila con javac + TeaVM (motor.mjs, WebAssembly GC) y corre el programa con WASI (wasi/).
   Los tres archivos grandes se bajan una vez (4,8 MB comprimidos) y quedan en la caché del navegador.

   Mensaje de entrada: { id, archivos: [{ path, content }], entrada: "ar/edu/App.java", datos: { "datos/x.csv": "..." },
                         args: [], controles: [{ k, codigo }] | null, importar: "ar.edu.backend" | null }
   Con { tipo: "preparar" } solo baja y arma el compilador, y responde { tipo: "listo" } o { tipo: "error", mensaje }.
   Respuestas: { tipo: "progreso", texto, pct } mientras prepara, { id, tipo: "corriendo" } al empezar a ejecutar y
               { id, tipo: "fin", etapa: "javac" | "interno" | "ok", ... } con el resultado. */
import { cargarMotor } from "./motor.mjs";
import { WASI, File, OpenFile, ConsoleStdout, PreopenDirectory, Directory } from "./wasi/index.js";

const VERSION = "1";
const PIEZAS = [
  { nombre: "compilador.wasm.gz", bytes: 2323333 },
  { nombre: "compilar.bin.gz", bytes: 218372 },
  { nombre: "armar.bin.gz", bytes: 2259487 }
];
const TOPE_SALIDA = 200000;   // caracteres de salida como máximo (para cortar un print en un ciclo infinito)

let preparando = null;  // la promesa de { comp, diags }: se arma una sola vez aunque lleguen dos pedidos juntos
let prueba = null;      // el texto de Prueba.java (la ayuda de los controles)

const avisar = (texto, pct) => postMessage({ tipo: "progreso", texto, pct });

async function bajar(pieza, hecho, total) {
  const url = new URL(pieza.nombre + "?v=" + VERSION, import.meta.url).href;
  let cache = null, resp = null;
  try { cache = await caches.open("isi-java"); resp = await cache.match(url); } catch (e) { cache = null; }
  let gz;
  if (resp) gz = new Uint8Array(await resp.arrayBuffer());
  else {
    resp = await fetch(url);
    if (!resp.ok) throw new Error(`No se pudo bajar ${pieza.nombre} (${resp.status})`);
    const partes = [];
    let n = 0;
    const lector = resp.body.getReader();
    for (;;) {
      const { done, value } = await lector.read();
      if (done) break;
      partes.push(value); n += value.length;
      avisar("Bajando Java (una sola vez)…", Math.min(99, Math.round((hecho + n) / total * 100)));
    }
    gz = new Uint8Array(n);
    let k = 0;
    for (const p of partes) { gz.set(p, k); k += p.length; }
    if (cache) {
      try {
        await cache.put(url, new Response(gz));
        // Se borran las versiones viejas
        for (const r of await cache.keys()) if (r.url.includes(pieza.nombre) && !r.url.endsWith("v=" + VERSION)) await cache.delete(r);
      } catch (e) { }
    }
  }
  const flujo = new Blob([gz]).stream().pipeThrough(new DecompressionStream("gzip"));
  return new Uint8Array(await new Response(flujo).arrayBuffer());
}

function preparar() {
  return preparando || (preparando = armarCompilador().catch(e => { preparando = null; throw e; }));
}
async function armarCompilador() {
  const total = PIEZAS.reduce((s, p) => s + p.bytes, 0);
  let hecho = 0;
  const bytes = [];
  for (const p of PIEZAS) { bytes.push(await bajar(p, hecho, total)); hecho += p.bytes; }
  avisar("Preparando el compilador…", 100);
  const [wasm, sdk, classlib] = bytes;
  const motor = await cargarMotor(wasm);
  const comp = motor.createCompiler();
  comp.setSdk(new Int8Array(sdk.buffer, sdk.byteOffset, sdk.byteLength));
  comp.setTeaVMClasslib(new Int8Array(classlib.buffer, classlib.byteOffset, classlib.byteLength));
  const diags = [];
  comp.onDiagnostic(d => diags.push({
    tipo: d.type, grave: d.severity === "error", mensaje: String(d.message || ""),
    archivo: d.fileName || null, linea: Math.max(1, d.lineNumber || 1)
  }));
  const r = await fetch(new URL("Prueba.java?v=" + VERSION, import.meta.url));
  if (!r.ok) throw new Error("No se pudo bajar Prueba.java");
  prueba = await r.text();
  return { comp, diags };
}

/* Las anotaciones en métodos y campos (@Override…) rompen este javac: se cambian por espacios.
   No cambian lo que hace el programa y así los números de línea siguen iguales. */
const sinAnotaciones = t => t.replace(/@(Override|Deprecated|SuppressWarnings|SafeVarargs|FunctionalInterface)\b(\s*\([^)]*\))?/g, m => m.replace(/[^\n]/g, " "));

/* Compila (solo javac). Devuelve los errores (los avisos no). */
function javac(comp, diags, archivos) {
  comp.clearSourceFiles(); comp.clearOutputFiles(); comp.clearInputClassFiles();
  diags.length = 0;
  for (const f of archivos) comp.addSourceFile(f.path, sinAnotaciones(f.content));
  let ok;
  try { ok = comp.compile(); }
  catch (e) { return { interno: "El compilador se trabó con este código (" + (e.message || e) + ")." }; }
  const errores = diags.filter(d => d.tipo === "javac" && d.grave);
  return { ok: ok && !errores.length, errores };
}

/* Arma el programa (TeaVM) y lo corre. */
function armarYCorrer(id, comp, diags, entrada, datos, args) {
  const clase = comp.findEntryClass(entrada);
  if (!clase) return { etapa: "interno", mensaje: "No encontré el main en " + entrada + "." };
  diags.length = 0;
  let wasm;
  try {
    const g = comp.generateWebAssembly({ mainClass: clase, outputName: "app", optimization: "debug" });
    const errores = diags.filter(d => d.tipo !== "javac" && d.grave).map(d => d.mensaje);
    if (!g || errores.length) return { etapa: "interno", mensaje: traducirArmado(errores.join("\n") || "no se pudo armar el programa") };
    wasm = comp.getWebAssemblyOutputFile("app");
  } catch (e) {
    return { etapa: "interno", mensaje: traducirArmado(e.message || String(e)) };
  }
  postMessage({ id, tipo: "corriendo" });
  // Los datos van en un sistema de archivos en memoria, con la raíz abierta (rutas relativas y absolutas)
  const raiz = new Map();
  for (const [ruta, texto] of Object.entries(datos || {})) {
    const partes = ruta.split("/").filter(Boolean);
    let d = raiz;
    for (const p of partes.slice(0, -1)) {
      if (!d.has(p)) d.set(p, new Directory(new Map()));
      d = d.get(p).contents;
    }
    d.set(partes.at(-1), new File(new TextEncoder().encode(texto)));
  }
  let out = "", err = "", cortado = false;
  const escribir = (cual, linea) => {
    if (out.length + err.length > TOPE_SALIDA) { cortado = true; throw new Error("demasiada salida"); }
    if (cual === 1) out += linea + "\n"; else err += linea + "\n";
  };
  const fds = [new OpenFile(new File([])), ConsoleStdout.lineBuffered(l => escribir(1, l)), ConsoleStdout.lineBuffered(l => escribir(2, l)), new PreopenDirectory("/", raiz)];
  const wasi = new WASI(["app", ...(args || [])], [], fds);
  const t = performance.now();
  let codigo = 0, trampa = null;
  try {
    const modulo = new WebAssembly.Module(Uint8Array.from(wasm));
    const inst = new WebAssembly.Instance(modulo, { wasi_snapshot_preview1: wasi.wasiImport, teavmMath: Math });
    codigo = wasi.start(inst);
  } catch (e) {
    trampa = cortado ? "salida" : (/call stack/i.test(e.message || "") ? "pila" : (e.message || String(e)));
  }
  return { etapa: "ok", out, err, codigo, trampa, msCorrer: Math.round(performance.now() - t) };
}

function traducirArmado(m) {
  if (/divide by zero/i.test(m)) return "Hay una división por cero que se puede ver al compilar (por ejemplo, x / 0).";
  const f = m.match(/Method ([\w.$]+)\.(\w+)\(/);
  if (f) return `${f[1]}.${f[2]}(…) no está disponible acá (el Java del navegador no lo trae). Probá otra forma de hacerlo.`;
  return "No se pudo armar el programa: " + m;
}

/* Al ejecutar, el main del alumno se llama desde ArranqueUTN: si sale una excepción que nadie atrapa, la imprime como
   el JDK ("Exception in thread "main" …" y la pila) y termina con código 1. TeaVM solo mostraba la pila, sin la excepción. */
const ARRANQUE = "ArranqueUTN";
const arranque = clase => `public class ${ARRANQUE} {
    public static void main(String[] args) {
        try {
            ${clase}.main(args);
        } catch (Throwable t) {
            System.out.flush();
            System.err.print("Exception in thread \\"main\\" ");
            t.printStackTrace();
            System.exit(1);
        }
    }
}
`;
const claseDe = ruta => ruta.replace(/\.java$/, "").split("/").filter(Boolean).join(".");

/* Arma Controles.java con un bloque por control y anota en qué líneas queda cada uno. */
function controlesJava(controles, importar) {
  const lineas = ["import java.util.*;", "import java.util.function.*;", "import java.util.stream.*;", "import java.io.*;", "import java.nio.file.*;"];
  if (importar) for (const p of [].concat(importar)) lineas.push(`import ${p}.*;`);
  lineas.push("public class Controles {", "    public static void main(String[] args) {");
  const rango = {};
  for (const c of controles) {
    const desde = lineas.length + 1;
    lineas.push(`        Prueba.control(${c.k}, () -> {`);
    for (const l of c.codigo.split("\n")) lineas.push("            " + l);
    lineas.push("        });");
    rango[c.k] = [desde, lineas.length];
  }
  lineas.push("        Prueba.fin();", "    }", "}");
  return { texto: lineas.join("\n") + "\n", rango };
}

onmessage = async ({ data: m }) => {
  // { tipo: "preparar" }: la página lo manda al abrir un ejercicio, para que Java esté listo al corregir
  if (m.tipo === "preparar") {
    try { await preparar(); postMessage({ tipo: "listo" }); }
    catch (e) { postMessage({ tipo: "error", mensaje: String(e.message || e) }); }
    return;
  }
  const t0 = performance.now();
  let res;
  try {
    const { comp, diags } = await preparar();
    const propios = m.archivos;
    if (!m.controles) {
      // Ejecutar el main del alumno, desde ArranqueUTN. Si lo único que no compila es ArranqueUTN (el main no es
      // public static, o el paquete no coincide con la carpeta), se corre directo.
      const r = javac(comp, diags, [...propios, { path: ARRANQUE + ".java", content: arranque(claseDe(m.entrada)) }]);
      const suyos = (r.errores || []).filter(e => e.archivo !== ARRANQUE + ".java");
      if (r.interno) res = { etapa: "interno", mensaje: r.interno };
      else if (r.ok) res = armarYCorrer(m.id, comp, diags, ARRANQUE + ".java", m.datos, m.args);
      else if (suyos.length) res = { etapa: "javac", errores: suyos };
      else {
        const r2 = javac(comp, diags, propios);
        res = r2.interno ? { etapa: "interno", mensaje: r2.interno } : !r2.ok ? { etapa: "javac", errores: r2.errores } : armarYCorrer(m.id, comp, diags, m.entrada, m.datos, m.args);
      }
    } else {
      // Primero se compila solo lo del alumno: si tiene errores, son lo primero que hay que arreglar
      let r = javac(comp, diags, propios);
      if (r.interno) res = { etapa: "interno", mensaje: r.interno };
      else if (!r.ok) res = { etapa: "javac", errores: r.errores };
      else {
        // Después, con los controles. Si un control no compila (falta un método, una clase…) cuenta como mal
        // y se saca, hasta que el resto compile.
        let vivos = m.controles.slice();
        const sinCompilar = [];
        for (let vuelta = 0; vuelta <= m.controles.length; vuelta++) {
          const cj = controlesJava(vivos, m.importar);
          r = javac(comp, diags, [...propios, { path: "Prueba.java", content: prueba }, { path: "Controles.java", content: cj.texto }]);
          if (r.interno) { res = { etapa: "interno", mensaje: r.interno }; break; }
          if (r.ok) {
            if (!vivos.length) { res = { etapa: "controles", resultados: [], sinCompilar }; break; }
            const corrida = armarYCorrer(m.id, comp, diags, "Controles.java", m.datos, []);
            res = { ...corrida, etapa: corrida.etapa === "ok" ? "controles" : corrida.etapa, sinCompilar };
            break;
          }
          const malos = new Map();
          for (const e of r.errores) {
            if (!/Controles\.java$/.test(e.archivo || "")) continue;
            for (const c of vivos) {
              const [a, b] = cj.rango[c.k];
              if (e.linea >= a && e.linea <= b && !malos.has(c.k)) malos.set(c.k, e.mensaje);
            }
          }
          if (!malos.size) { res = { etapa: "javac", errores: r.errores }; break; }
          for (const [k, mensaje] of malos) sinCompilar.push({ k, mensaje });
          vivos = vivos.filter(c => !malos.has(c.k));
        }
      }
    }
  } catch (e) {
    res = { etapa: "interno", mensaje: "No se pudo preparar Java: " + (e.message || e) };
  }
  postMessage({ id: m.id, tipo: "fin", ms: Math.round(performance.now() - t0), ...res });
};
