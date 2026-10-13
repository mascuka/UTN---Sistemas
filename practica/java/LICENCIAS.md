# Licencias del Java del navegador

Lo de esta carpeta corre Java en el navegador para la Práctica por partes. Casi todo es de otros proyectos, con
estas licencias (los textos están en `licencias/`):

| Archivo | Qué es | De dónde sale | Licencia |
|---|---|---|---|
| `compilador.wasm.gz` | javac + el compilador de TeaVM 0.13.1, en WebAssembly GC | `@wasm-oj/toolchain-java` 0.2.0 (npm), `java-teavm-0.13.1.compiler.wasm`, sin cambios | TeaVM: Apache-2.0 · OpenJDK 21: GPL-2.0 con Classpath exception |
| `compilar.bin.gz` | Las clases que lee javac | `java-teavm-0.13.1.compile-classlib.bin`, con los cambios de `herramientas/java-navegador/parche/ParcheClasslib.java` | OpenJDK y Android libcore: GPL-2.0 con Classpath exception · TeaVM: Apache-2.0 |
| `armar.bin.gz` | La biblioteca de clases de TeaVM, que se suma a cada programa | `java-teavm-0.13.1.runtime-classlib.bin`, con los cambios de `ParcheClasslib.java` y las clases de `herramientas/java-navegador/clases/` | TeaVM: Apache-2.0 · Android libcore (Scanner, Spliterators): GPL-2.0 con Classpath exception |
| `motor.mjs` | El arranque del compilador | `@wasm-oj/server` 0.2.4 (`java-compiler-runtime.mjs`, `java-compiler-bindings.mjs`) | WASM-OJ: MIT · TeaVM: Apache-2.0 |
| `wasi/` | WASI para el navegador | `@bjorn3/browser_wasi_shim` 0.4.2 (npm), sin cambios | MIT o Apache-2.0 |
| `trabajador.js`, `Prueba.java` | El worker y la ayuda de los controles | Propios de esta página | — |

Fuentes:
- TeaVM: <https://github.com/konsoletyper/teavm> y <https://github.com/konsoletyper/teavm-javac>
- WASM-OJ: <https://github.com/wasm-oj/forge> (el detalle de versiones está en `THIRD_PARTY_NOTICES.md` del paquete de npm)
- OpenJDK: <https://github.com/openjdk/jdk21u> · Android libcore: <https://android.googlesource.com/platform/libcore>
- browser_wasi_shim: <https://github.com/bjorn3/browser_wasi_shim>

Los cambios a las bibliotecas (qué se corrige y por qué) están explicados al principio de `ParcheClasslib.java`, y
`herramientas/java-navegador/armar.sh` rehace los tres archivos `.gz` desde el paquete de npm.
