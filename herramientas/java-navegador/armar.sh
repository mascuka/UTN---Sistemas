#!/bin/bash
# Arma el Java del navegador de practica/java/ a partir de @wasm-oj/toolchain-java 0.2.0 (npm).
# Necesita: JDK 21, ASM 9 (org.ow2.asm:asm) y Python 3. Uso, desde la raíz del repo:
#   herramientas/java-navegador/armar.sh /ruta/a/asm-9.x.jar
# Deja en practica/java/: compilador.wasm.gz, compilar.bin.gz (lo que lee javac) y armar.bin.gz (lo que usa TeaVM).
set -e
ASM=${1:?"falta la ruta a asm-9.x.jar"}
H=herramientas/java-navegador
T=$(mktemp -d)
echo "Bajando @wasm-oj/toolchain-java 0.2.0…"
curl -sL https://registry.npmjs.org/@wasm-oj/toolchain-java/-/toolchain-java-0.2.0.tgz | tar xz -C "$T"
A="$T/package/assets"
# Clases propias que van dentro del classlib de TeaVM (formato liviano, Scanner liviano, nombres y rutas)
mkdir -p "$T/clases" "$T/stubs" "$T/scanner-stub/java.base/java/util" "$T/scanner-out"
mkdir -p "$T/interop"; javac --release 21 -d "$T/interop" $H/stubs/org/teavm/interop/Import.java   # solo para compilar Salida
javac --release 21 -XDstringConcat=inline -cp "$T/interop" -d "$T/clases" $(find $H/clases -name "*.java")
# Lo que ve javac del Scanner: la misma clase, con el nombre de java.util
sed -e 's/^package org.teavm.classlib.java.util;/package java.util;/' -e 's/TScanner/Scanner/g' \
    $H/clases/org/teavm/classlib/java/util/TScanner.java > "$T/scanner-stub/java.base/java/util/Scanner.java"
javac --patch-module java.base="$T/scanner-stub/java.base" -d "$T/scanner-out" "$T/scanner-stub/java.base/java/util/Scanner.java"
mkdir -p "$T/fd/java.base/java/io"; cp $H/stubs/java/io/FileDescriptor.java "$T/fd/java.base/java/io/"
javac --patch-module java.base="$T/fd/java.base" -d "$T/stubs" "$T/fd/java.base/java/io/FileDescriptor.java"
# Datos de idiomas: solo inglés y español
python3 - "$A/java-teavm-0.13.1.runtime-classlib.bin" "$T/cldr-json.zip" <<'PY'
import struct, sys
b = open(sys.argv[1], "rb").read(); i = 0
while i < len(b):
    ln = struct.unpack(">H", b[i:i+2])[0]; i += 2
    name = b[i:i+ln].decode(); i += ln
    sz = struct.unpack(">I", b[i:i+4])[0]; i += 4
    if name == "org/teavm/classlib/impl/unicode/cldr-json.zip": open(sys.argv[2], "wb").write(b[i:i+sz])
    if name == "org/teavm/runtime/fs/VirtualFileAccessor.class": open(sys.argv[2] + ".vfa", "wb").write(b[i:i+sz])
    i += sz
PY
python3 $H/reducir-cldr.py "$T/cldr-json.zip" "$T/cldr-chico.zip"
X=()
for f in $(cd "$T/clases" && find org -name "*.class"); do X+=("runtime:$f=$T/clases/$f"); done
for f in $(cd "$T/scanner-out" && find java -name "*.class"); do X+=("compile:$f=$T/scanner-out/$f"); done
X+=("compile:java/io/FileDescriptor.class=$T/stubs/java/io/FileDescriptor.class")
X+=("compile:org/teavm/runtime/fs/VirtualFileAccessor.class=$T/cldr-json.zip.vfa")
X+=("runtime:org/teavm/classlib/impl/unicode/cldr-json.zip=$T/cldr-chico.zip")
javac -cp "$ASM" -d "$T/parche" $H/parche/ParcheClasslib.java
java -cp "$ASM:$T/parche" ParcheClasslib "$A/java-teavm-0.13.1.compile-classlib.bin" "$A/java-teavm-0.13.1.runtime-classlib.bin" \
    "$T/compilar.bin" "$T/armar.bin" "${X[@]}"
gzip -9 -c "$A/java-teavm-0.13.1.compiler.wasm" > practica/java/compilador.wasm.gz
gzip -9 -c "$T/compilar.bin" > practica/java/compilar.bin.gz
gzip -9 -c "$T/armar.bin" > practica/java/armar.bin.gz
ls -l practica/java/*.gz
echo "Listo. Si cambió algún archivo, subí VERSION y los tamaños en practica/java/trabajador.js."
