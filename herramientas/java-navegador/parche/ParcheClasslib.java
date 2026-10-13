import org.objectweb.asm.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Corrige los classlib del compilador Java de TeaVM (formato: u16 largo + nombre, u32 largo + bytes).
 * 1. En el classlib de compilación (lo que lee javac) los métodos que TeaVM marca con @Rename aparecen
 *    con el nombre interno (getMessage0, getClass0...): se renombran al nombre real (getMessage, getClass...).
 * 2. A java.lang.Long le faltan sum, max y min (los usa Collectors.counting): se agregan en los dos classlib.
 * 4. String.format, String.formatted y PrintStream.printf/format usan un formateador liviano
 *    (org.teavm.classlib.impl.utn.Formato) en lugar del de TeaVM, que trae los datos de todos los idiomas.
 * 5. Class.getSimpleName sale de getName (el de TeaVM se cae con las clases del classlib) y las rutas
 *    relativas de archivos se toman desde la raíz (TeaVM solo encontraba las absolutas).
 * 6. Los mensajes de Integer.parseInt, Long.parseLong, Double.parseDouble, Float.parseFloat y Enum.valueOf son
 *    los del JDK (org.teavm.classlib.impl.utn.Numeros), y Files.createDirectories no falla si la carpeta ya existe.
 * 7. System.exit (no estaba) y Runtime.exit (no hacía nada) terminan el programa (org.teavm.classlib.impl.utn.Salida).
 * 3. Algunos stubs quedaron heredándose a sí mismos (java.lang.annotation.Annotation extends Annotation, porque
 *    TAnnotation extiende la Annotation real): se saca esa herencia. Sin esto, cualquier anotación (@Override)
 *    rompe el compilador.
 * Uso: java ParcheClasslib compile.bin runtime.bin compile-salida.bin runtime-salida.bin
 */
public class ParcheClasslib {
    record Entrada(String nombre, byte[] datos) {}

    static List<Entrada> leer(Path p) throws IOException {
        DataInputStream in = new DataInputStream(new BufferedInputStream(Files.newInputStream(p)));
        List<Entrada> out = new ArrayList<>();
        while (in.available() > 0) {
            byte[] n = new byte[in.readUnsignedShort()]; in.readFully(n);
            byte[] d = new byte[in.readInt()]; in.readFully(d);
            out.add(new Entrada(new String(n, "UTF-8"), d));
        }
        return out;
    }

    static void escribir(Path p, List<Entrada> entradas) throws IOException {
        try (DataOutputStream out = new DataOutputStream(new BufferedOutputStream(Files.newOutputStream(p)))) {
            for (Entrada e : entradas) {
                byte[] n = e.nombre().getBytes("UTF-8");
                out.writeShort(n.length); out.write(n); out.writeInt(e.datos().length); out.write(e.datos());
            }
        }
    }

    /** clase del stub (java/lang/Throwable) -> (nombre interno -> nombre real), leído de los @Rename del runtime. */
    static Map<String, Map<String, String>> renombres(List<Entrada> runtime) {
        Map<String, Map<String, String>> mapa = new HashMap<>();
        String pre = "org/teavm/classlib/";
        for (Entrada e : runtime) {
            if (!e.nombre().startsWith(pre) || !e.nombre().endsWith(".class")) continue;
            String rel = e.nombre().substring(pre.length(), e.nombre().length() - 6);
            int b = rel.lastIndexOf('/');
            String simple = rel.substring(b + 1);
            if (!simple.startsWith("T")) continue;
            String stub = rel.substring(0, b + 1) + simple.substring(1).replace("$T", "$");
            new ClassReader(e.datos()).accept(new ClassVisitor(Opcodes.ASM9) {
                @Override public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] exc) {
                    return new MethodVisitor(Opcodes.ASM9) {
                        @Override public AnnotationVisitor visitAnnotation(String d, boolean vis) {
                            if (!d.endsWith("/Rename;")) return null;
                            return new AnnotationVisitor(Opcodes.ASM9) {
                                @Override public void visit(String n, Object v) {
                                    String real = String.valueOf(v);
                                    if (!real.startsWith("<") && !real.equals("fakeInit") && !real.equals(name))
                                        mapa.computeIfAbsent(stub, k -> new HashMap<>()).put(name, real);
                                }
                            };
                        }
                    };
                }
            }, ClassReader.SKIP_CODE);
        }
        return mapa;
    }

    /** Renombra métodos de un stub; si el nombre real ya existe con el mismo descriptor, se queda el que estaba. */
    static byte[] renombrar(byte[] clase, Map<String, String> ren, List<String> log, String nombreClase) {
        Set<String> existentes = new HashSet<>();
        new ClassReader(clase).accept(new ClassVisitor(Opcodes.ASM9) {
            @Override public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] exc) {
                existentes.add(name + desc); return null;
            }
        }, ClassReader.SKIP_CODE);
        ClassWriter cw = new ClassWriter(0);
        new ClassReader(clase).accept(new ClassVisitor(Opcodes.ASM9, cw) {
            @Override public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] exc) {
                String real = ren.get(name);
                if (real == null) return super.visitMethod(acc, name, desc, sig, exc);
                if (existentes.contains(real + desc)) { log.add(nombreClase + "." + name + desc + " -> se quita (ya está " + real + ")"); return null; }
                existentes.add(real + desc);
                log.add(nombreClase + "." + name + desc + " -> " + real);
                return super.visitMethod(acc, real, desc, sig, exc);
            }
        }, 0);
        return cw.toByteArray();
    }

    /** Saca la herencia de sí misma (superclase o interfaz igual a la propia clase). */
    static byte[] sinCiclo(byte[] clase, List<String> log) {
        ClassReader cr = new ClassReader(clase);
        String yo = cr.getClassName();
        boolean superYo = yo.equals(cr.getSuperName());
        boolean ifaceYo = Arrays.asList(cr.getInterfaces()).contains(yo);
        if (!superYo && !ifaceYo) return clase;
        ClassWriter cw = new ClassWriter(0);
        cr.accept(new ClassVisitor(Opcodes.ASM9, cw) {
            @Override public void visit(int v, int acc, String name, String sig, String sup, String[] ifaces) {
                String[] limpio = Arrays.stream(ifaces).filter(i -> !i.equals(name)).toArray(String[]::new);
                log.add(name + ": se saca la herencia de sí misma");
                super.visit(v, acc, name, sig == null || !sig.contains(name) ? sig : null, sup.equals(name) ? "java/lang/Object" : sup, limpio);
            }
        }, 0);
        return cw.toByteArray();
    }

    /** Agrega a una clase métodos estáticos (J J)J: sum, max y min, si no los tiene. */
    static byte[] agregarLong(byte[] clase, List<String> log, String nombreClase) {
        Set<String> existentes = new HashSet<>();
        new ClassReader(clase).accept(new ClassVisitor(Opcodes.ASM9) {
            @Override public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] exc) {
                existentes.add(name + desc); return null;
            }
        }, ClassReader.SKIP_CODE);
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        new ClassReader(clase).accept(new ClassVisitor(Opcodes.ASM9, cw) {
            @Override public void visitEnd() {
                for (String m : List.of("sum", "max", "min")) {
                    if (existentes.contains(m + "(JJ)J")) continue;
                    MethodVisitor mv = cv.visitMethod(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC, m, "(JJ)J", null, null);
                    mv.visitCode();
                    mv.visitVarInsn(Opcodes.LLOAD, 0);
                    mv.visitVarInsn(Opcodes.LLOAD, 2);
                    if (m.equals("sum")) mv.visitInsn(Opcodes.LADD);
                    else mv.visitMethodInsn(Opcodes.INVOKESTATIC, "java/lang/Math", m, "(JJ)J", false);
                    mv.visitInsn(Opcodes.LRETURN);
                    mv.visitMaxs(0, 0);
                    mv.visitEnd();
                    log.add(nombreClase + ": se agrega " + m + "(JJ)J");
                }
                super.visitEnd();
            }
        }, 0);
        return cw.toByteArray();
    }

    /** Reemplaza el cuerpo de los métodos de formato por una llamada a Formato.format. */
    static byte[] formatoLiviano(byte[] clase, List<String> log, String nombreClase) {
        final String F = "org/teavm/classlib/impl/utn/Formato", FD = "(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;";
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        new ClassReader(clase).accept(new ClassVisitor(Opcodes.ASM9, cw) {
            @Override public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] exc) {
                boolean string = nombreClase.equals("TString") && (name.equals("format") || name.equals("formatted"));
                boolean ps = nombreClase.equals("TPrintStream") && (name.equals("printf") || name.equals("format"));
                if (!string && !ps) return super.visitMethod(acc, name, desc, sig, exc);
                boolean conLocale = desc.startsWith("(Ljava/util/Locale;");
                MethodVisitor mv = super.visitMethod(acc & ~Opcodes.ACC_NATIVE, name, desc, sig, exc);
                mv.visitCode();
                if (string && name.equals("formatted")) { mv.visitVarInsn(Opcodes.ALOAD, 0); mv.visitVarInsn(Opcodes.ALOAD, 1); }
                else if (string) { mv.visitVarInsn(Opcodes.ALOAD, conLocale ? 1 : 0); mv.visitVarInsn(Opcodes.ALOAD, conLocale ? 2 : 1); }
                else { mv.visitVarInsn(Opcodes.ALOAD, 0); mv.visitVarInsn(Opcodes.ALOAD, conLocale ? 2 : 1); mv.visitVarInsn(Opcodes.ALOAD, conLocale ? 3 : 2); }
                mv.visitMethodInsn(Opcodes.INVOKESTATIC, F, "format", FD, false);
                if (string) mv.visitInsn(Opcodes.ARETURN);
                else {
                    mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "org/teavm/classlib/java/io/TPrintStream", "print", "(Ljava/lang/String;)V", false);
                    mv.visitVarInsn(Opcodes.ALOAD, 0);
                    mv.visitInsn(Opcodes.ARETURN);
                }
                mv.visitMaxs(0, 0);
                mv.visitEnd();
                log.add(nombreClase + "." + name + desc + " -> Formato.format");
                return null;
            }
        }, 0);
        return cw.toByteArray();
    }

    static final String N = "org/teavm/classlib/impl/utn/Nombres";

    static byte[] simpleYRutas(byte[] clase, List<String> log, String nombreClase) {
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        new ClassReader(clase).accept(new ClassVisitor(Opcodes.ASM9, cw) {
            @Override public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] exc) {
                if (nombreClase.equals("TClass") && name.equals("getSimpleName") && desc.equals("()Ljava/lang/String;")) {
                    MethodVisitor mv = super.visitMethod(acc, name, desc, sig, exc);
                    mv.visitCode();
                    mv.visitVarInsn(Opcodes.ALOAD, 0);
                    mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "org/teavm/classlib/java/lang/TClass", "getName", "()Ljava/lang/String;", false);
                    mv.visitMethodInsn(Opcodes.INVOKESTATIC, N, "simple", "(Ljava/lang/String;)Ljava/lang/String;", false);
                    mv.visitInsn(Opcodes.ARETURN);
                    mv.visitMaxs(0, 0);
                    mv.visitEnd();
                    log.add("TClass.getSimpleName -> Nombres.simple(getName())");
                    return null;
                }
                MethodVisitor mv = super.visitMethod(acc, name, desc, sig, exc);
                if (nombreClase.equals("WasiFileSystem") && name.equals("findBestPreopened")) {
                    log.add("WasiFileSystem.findBestPreopened: rutas relativas desde la raíz");
                    return new MethodVisitor(Opcodes.ASM9, mv) {
                        @Override public void visitCode() {
                            super.visitCode();
                            super.visitVarInsn(Opcodes.ALOAD, 1);
                            super.visitMethodInsn(Opcodes.INVOKESTATIC, N, "absoluta", "(Ljava/lang/String;)Ljava/lang/String;", false);
                            super.visitVarInsn(Opcodes.ASTORE, 1);
                        }
                    };
                }
                return mv;
            }
        }, 0);
        return cw.toByteArray();
    }

    static final String NUM = "org/teavm/classlib/impl/utn/Numeros";

    /** Escribe un método nuevo que solo llama a un estático de las ayudas con los mismos parámetros y devuelve lo que da. */
    static void llamar(MethodVisitor mv, String clase, String metodo, String desc, int[] cargas, int retorno) {
        mv.visitCode();
        for (int k = 0; k < cargas.length; k += 2) mv.visitVarInsn(cargas[k], cargas[k + 1]);
        mv.visitMethodInsn(Opcodes.INVOKESTATIC, clase, metodo, desc, false);
        mv.visitInsn(retorno);
        mv.visitMaxs(0, 0);
        mv.visitEnd();
    }

    static byte[] mensajesJdk(byte[] clase, List<String> log, String nombreClase) {
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        new ClassReader(clase).accept(new ClassVisitor(Opcodes.ASM9, cw) {
            @Override public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] exc) {
                String m = nombreClase + "." + name + desc;
                if (m.equals("TInteger.parseInt(Ljava/lang/String;I)I")) {
                    llamar(super.visitMethod(acc, name, desc, sig, exc), NUM, "parseInt", desc, new int[] { Opcodes.ALOAD, 0, Opcodes.ILOAD, 1 }, Opcodes.IRETURN);
                    log.add(m + " -> Numeros.parseInt"); return null;
                }
                if (m.equals("TLong.parseLong(Ljava/lang/String;I)J")) {
                    llamar(super.visitMethod(acc, name, desc, sig, exc), NUM, "parseLong", desc, new int[] { Opcodes.ALOAD, 0, Opcodes.ILOAD, 1 }, Opcodes.LRETURN);
                    log.add(m + " -> Numeros.parseLong"); return null;
                }
                if (m.equals("TFiles.createDirectories(Lorg/teavm/classlib/java/nio/file/TPath;[Lorg/teavm/classlib/java/nio/file/attribute/TFileAttribute;)Lorg/teavm/classlib/java/nio/file/TPath;")) {
                    llamar(super.visitMethod(acc, name, desc, sig, exc), N, "crearCarpetas", "(Ljava/nio/file/Path;[Ljava/nio/file/attribute/FileAttribute;)Ljava/nio/file/Path;",
                        new int[] { Opcodes.ALOAD, 0, Opcodes.ALOAD, 1 }, Opcodes.ARETURN);
                    log.add(m + " -> Nombres.crearCarpetas"); return null;
                }
                MethodVisitor mv = super.visitMethod(acc, name, desc, sig, exc);
                if (m.equals("TDouble.parseDouble(Ljava/lang/String;)D") || m.equals("TFloat.parseFloat(Ljava/lang/String;)F")) {
                    log.add(m + ": antes, Numeros.revisarDecimal");
                    return new MethodVisitor(Opcodes.ASM9, mv) {
                        @Override public void visitCode() {
                            super.visitCode();
                            super.visitVarInsn(Opcodes.ALOAD, 0);
                            super.visitMethodInsn(Opcodes.INVOKESTATIC, NUM, "revisarDecimal", "(Ljava/lang/String;)V", false);
                        }
                    };
                }
                if (nombreClase.equals("TEnum") && name.equals("valueOf") && desc.startsWith("(Lorg/teavm/classlib/java/lang/TClass;")) {
                    log.add(m + ": mensaje \"No enum constant X.Y\"");
                    return new MethodVisitor(Opcodes.ASM9, mv) {
                        boolean primero = true;
                        @Override public void visitMethodInsn(int op, String owner, String n, String d, boolean itf) {
                            // el primer String.valueOf(Object) es el de la clase: se cambia por su nombre con puntos
                            if (primero && op == Opcodes.INVOKESTATIC && owner.equals("java/lang/String") && n.equals("valueOf") && d.equals("(Ljava/lang/Object;)Ljava/lang/String;")) {
                                primero = false;
                                super.visitMethodInsn(op, NUM, "claseEnum", d, false);
                                return;
                            }
                            super.visitMethodInsn(op, owner, n, d, itf);
                        }
                        @Override public void visitInvokeDynamicInsn(String n, String d, Handle bsm, Object... args) {
                            if (args.length == 1 && "Enum \u0001 does not have the \u0001 constant".equals(args[0])) args = new Object[] { "No enum constant \u0001.\u0001" };
                            super.visitInvokeDynamicInsn(n, d, bsm, args);
                        }
                    };
                }
                return mv;
            }
        }, 0);
        return cw.toByteArray();
    }

    static final String SAL = "org/teavm/classlib/impl/utn/Salida";

    /** System.exit(int): se agrega al stub de javac (vacío) y al runtime (llama a Salida.salir); Runtime.exit llama a Salida.salir. */
    static byte[] salir(byte[] clase, List<String> log, String nombreClase, boolean runtime) {
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        new ClassReader(clase).accept(new ClassVisitor(Opcodes.ASM9, cw) {
            boolean hay = false;
            @Override public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] exc) {
                if (!name.equals("exit") || !desc.equals("(I)V")) return super.visitMethod(acc, name, desc, sig, exc);
                hay = true;
                if (!runtime) return super.visitMethod(acc, name, desc, sig, exc);
                boolean estatico = (acc & Opcodes.ACC_STATIC) != 0;
                llamar(super.visitMethod(acc & ~Opcodes.ACC_NATIVE, name, desc, sig, exc), SAL, "salir", "(I)V", new int[] { Opcodes.ILOAD, estatico ? 0 : 1 }, Opcodes.RETURN);
                log.add(nombreClase + ".exit -> Salida.salir");
                return null;
            }
            @Override public void visitEnd() {
                if (!hay && nombreClase.endsWith("System")) {
                    MethodVisitor mv = cv.visitMethod(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC, "exit", "(I)V", null, null);
                    if (runtime) llamar(mv, SAL, "salir", "(I)V", new int[] { Opcodes.ILOAD, 0 }, Opcodes.RETURN);
                    else { mv.visitCode(); mv.visitInsn(Opcodes.RETURN); mv.visitMaxs(0, 0); mv.visitEnd(); }
                    log.add(nombreClase + ": se agrega exit(int)");
                }
                super.visitEnd();
            }
        }, 0);
        return cw.toByteArray();
    }

    public static void main(String[] args) throws Exception {
        List<Entrada> compile = leer(Path.of(args[0])), runtime = leer(Path.of(args[1]));
        Map<String, Map<String, String>> mapa = renombres(runtime);
        List<String> log = new ArrayList<>();
        List<Entrada> c2 = new ArrayList<>();
        for (Entrada e : compile) {
            byte[] d = e.datos();
            String cls = e.nombre().endsWith(".class") ? e.nombre().substring(0, e.nombre().length() - 6) : null;
            if (cls != null && mapa.containsKey(cls)) d = renombrar(d, mapa.get(cls), log, cls);
            if ("java/lang/Long".equals(cls)) d = agregarLong(d, log, cls);
            if ("java/lang/System".equals(cls)) d = salir(d, log, cls, false);
            if (cls != null) d = sinCiclo(d, log);
            c2.add(new Entrada(e.nombre(), d));
        }
        List<Entrada> r2 = new ArrayList<>();
        for (Entrada e : runtime) {
            byte[] d = e.datos();
            if (e.nombre().equals("org/teavm/classlib/java/lang/TLong.class")) d = agregarLong(d, log, "TLong");
            if (e.nombre().equals("org/teavm/classlib/java/lang/TString.class")) d = formatoLiviano(d, log, "TString");
            if (e.nombre().equals("org/teavm/classlib/java/io/TPrintStream.class")) d = formatoLiviano(d, log, "TPrintStream");
            if (e.nombre().equals("org/teavm/classlib/java/lang/TClass.class")) d = simpleYRutas(d, log, "TClass");
            if (e.nombre().equals("org/teavm/backend/wasm/runtime/fs/WasiFileSystem.class")) d = simpleYRutas(d, log, "WasiFileSystem");
            if (e.nombre().equals("org/teavm/classlib/java/lang/TSystem.class")) d = salir(d, log, "TSystem", true);
            if (e.nombre().equals("org/teavm/classlib/java/lang/TRuntime.class")) d = salir(d, log, "TRuntime", true);
            for (String c : List.of("java/lang/TInteger", "java/lang/TLong", "java/lang/TDouble", "java/lang/TFloat", "java/lang/TEnum", "java/nio/file/TFiles"))
                if (e.nombre().equals("org/teavm/classlib/" + c + ".class")) d = mensajesJdk(d, log, c.substring(c.lastIndexOf('/') + 1));
            r2.add(new Entrada(e.nombre(), d));
        }
        // clases extra (compiladas aparte): runtime:ruta/en/classlib=archivo.class o compile:ruta=archivo.class
        for (int k = 4; k < args.length; k++) {
            String[] par = args[k].split("=");
            boolean aCompile = par[0].startsWith("compile:");
            String ruta = par[0].substring(par[0].indexOf(':') + 1);
            List<Entrada> destino = aCompile ? c2 : r2;
            Entrada nueva = new Entrada(ruta, Files.readAllBytes(Path.of(par[1])));
            int ya = -1;
            for (int q = 0; q < destino.size(); q++) if (destino.get(q).nombre().equals(ruta)) ya = q;
            if (ya >= 0) destino.set(ya, nueva); else destino.add(nueva);
            log.add((aCompile ? "compile" : "runtime") + (ya >= 0 ? ": se reemplaza " : ": se agrega ") + ruta);
        }
        escribir(Path.of(args[2]), c2);
        escribir(Path.of(args[3]), r2);
        log.forEach(System.out::println);
    }
}
