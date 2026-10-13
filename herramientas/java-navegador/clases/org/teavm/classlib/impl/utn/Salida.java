package org.teavm.classlib.impl.utn;

import org.teavm.interop.Import;

/** System.exit y Runtime.exit: en TeaVM no hacían nada. Terminan el programa con proc_exit de WASI. */
public final class Salida {
    private Salida() { }

    @Import(name = "proc_exit", module = "wasi_snapshot_preview1")
    private static native void procExit(int codigo);

    public static void salir(int codigo) {
        System.out.flush();
        System.err.flush();
        procExit(codigo);
    }
}
