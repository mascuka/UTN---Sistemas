package org.teavm.classlib.java.util;

import java.io.Closeable;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.UncheckedIOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.InputMismatchException;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.stream.Stream;

/**
 * Scanner liviano para el navegador (reemplaza al de TeaVM, que tarda ~12 s en compilarse y no abre File).
 * Lee toda la entrada la primera vez que se usa. Delimitador: espacios por defecto, o el de useDelimiter
 * (literal o una expresión simple: alternativas con |, clases [..], \s \d \w \n \R, y * + ?).
 */
public final class TScanner implements Iterator<String>, Closeable {
    private Reader lector;
    private String texto;
    private int pos;
    private boolean cerrado;
    private Patron delim;
    private String delimTexto = "\\p{javaWhitespace}+";

    public TScanner(Readable fuente) { this.lector = (Reader) fuente; }
    public TScanner(InputStream in) { this(in, StandardCharsets.UTF_8); }
    public TScanner(InputStream in, String charset) { this(in, Charset.forName(charset)); }
    public TScanner(InputStream in, Charset charset) { this.lector = new InputStreamReader(in, charset); }
    public TScanner(File archivo) throws java.io.FileNotFoundException { this(Path.of(archivo.getPath()), StandardCharsets.UTF_8, true); }
    public TScanner(File archivo, String charset) throws java.io.FileNotFoundException { this(Path.of(archivo.getPath()), Charset.forName(charset), true); }
    public TScanner(File archivo, Charset charset) throws IOException { this(Path.of(archivo.getPath()), charset, true); }
    public TScanner(Path ruta) throws IOException { this(ruta, StandardCharsets.UTF_8); }
    public TScanner(Path ruta, String charset) throws IOException { this(ruta, Charset.forName(charset)); }
    public TScanner(Path ruta, Charset charset) throws IOException { this.lector = Files.newBufferedReader(ruta, charset); }
    public TScanner(String fuente) { this.texto = fuente; }

    private TScanner(Path ruta, Charset charset, boolean comoFile) throws java.io.FileNotFoundException {
        try {
            this.lector = Files.newBufferedReader(ruta, charset);
        } catch (IOException e) {
            throw new java.io.FileNotFoundException(ruta + " (No such file or directory)");
        }
    }

    private void cargar() {
        if (cerrado) throw new IllegalStateException("Scanner closed");
        if (texto != null) return;
        StringBuilder b = new StringBuilder();
        char[] buf = new char[4096];
        try {
            int n;
            while ((n = lector.read(buf, 0, buf.length)) > 0) b.append(buf, 0, n);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        texto = b.toString();
    }

    public void close() {
        if (cerrado) return;
        cerrado = true;
        try { if (lector != null) lector.close(); } catch (IOException e) { }
    }

    public TScanner useDelimiter(String patron) {
        delimTexto = patron;
        delim = Patron.compilar(patron);
        return this;
    }

    public TScanner useLocale(java.util.Locale locale) { return this; }
    public TScanner reset() { delim = null; delimTexto = "\\p{javaWhitespace}+"; return this; }
    public void remove() { throw new UnsupportedOperationException(); }

    public boolean hasNextLine() {
        cargar();
        return pos < texto.length();
    }

    public String nextLine() {
        cargar();
        if (pos >= texto.length()) throw new NoSuchElementException("No line found");
        int i = pos;
        while (i < texto.length() && texto.charAt(i) != '\n' && texto.charAt(i) != '\r') i++;
        String linea = texto.substring(pos, i);
        if (i < texto.length()) {
            if (texto.charAt(i) == '\r' && i + 1 < texto.length() && texto.charAt(i + 1) == '\n') i += 2;
            else i++;
        }
        pos = i;
        return linea;
    }

    /** Largo del delimitador que empieza en i (0 si no hay). */
    private int delimEn(int i) {
        if (delim == null) {
            int j = i;
            while (j < texto.length() && Character.isWhitespace(texto.charAt(j))) j++;
            return j - i;
        }
        int r = delim.coincide(texto, i);
        return r < 0 ? 0 : r - i;
    }

    /** Busca el próximo token desde pos: devuelve {inicio, fin} o null. Como Java: salta un delimitador
        (la coincidencia más larga) y el token va hasta el próximo, así ";;" deja un token vacío. */
    private int[] buscar() {
        cargar();
        int i = pos, n = texto.length();
        if (i < n) i += delimEn(i);
        if (i >= n) return null;
        int j = i;
        while (j < n && delimEn(j) == 0) j++;
        return new int[] { i, j };
    }

    public boolean hasNext() { return buscar() != null; }

    public String next() {
        int[] t = buscar();
        if (t == null) throw new NoSuchElementException();
        pos = t[1];
        return texto.substring(t[0], t[1]);
    }

    private String mirar() {
        int[] t = buscar();
        return t == null ? null : texto.substring(t[0], t[1]);
    }

    private static String decimal(String s) {
        return s.indexOf(',') >= 0 && s.indexOf('.') < 0 ? s.replace(',', '.') : s;
    }

    public boolean hasNextInt() { String s = mirar(); if (s == null) return false; try { Integer.parseInt(s); return true; } catch (NumberFormatException e) { return false; } }
    public boolean hasNextInt(int radix) { String s = mirar(); if (s == null) return false; try { Integer.parseInt(s, radix); return true; } catch (NumberFormatException e) { return false; } }
    public int nextInt() { return nextInt(10); }
    public int nextInt(int radix) {
        String s = mirar();
        if (s == null) throw new NoSuchElementException();
        try { int v = Integer.parseInt(s, radix); next(); return v; } catch (NumberFormatException e) { throw new InputMismatchException("For input string: \"" + s + "\""); }
    }
    public boolean hasNextLong() { String s = mirar(); if (s == null) return false; try { Long.parseLong(s); return true; } catch (NumberFormatException e) { return false; } }
    public long nextLong() {
        String s = mirar();
        if (s == null) throw new NoSuchElementException();
        try { long v = Long.parseLong(s); next(); return v; } catch (NumberFormatException e) { throw new InputMismatchException("For input string: \"" + s + "\""); }
    }
    public boolean hasNextShort() { String s = mirar(); if (s == null) return false; try { Short.parseShort(s); return true; } catch (NumberFormatException e) { return false; } }
    public short nextShort() { long v = nextLong(); if (v < Short.MIN_VALUE || v > Short.MAX_VALUE) throw new InputMismatchException(); return (short) v; }
    public boolean hasNextByte() { String s = mirar(); if (s == null) return false; try { Byte.parseByte(s); return true; } catch (NumberFormatException e) { return false; } }
    public byte nextByte() { long v = nextLong(); if (v < Byte.MIN_VALUE || v > Byte.MAX_VALUE) throw new InputMismatchException(); return (byte) v; }
    public boolean hasNextDouble() { String s = mirar(); if (s == null) return false; try { Double.parseDouble(decimal(s)); return true; } catch (NumberFormatException e) { return false; } }
    public double nextDouble() {
        String s = mirar();
        if (s == null) throw new NoSuchElementException();
        try { double v = Double.parseDouble(decimal(s)); next(); return v; } catch (NumberFormatException e) { throw new InputMismatchException("For input string: \"" + s + "\""); }
    }
    public boolean hasNextFloat() { return hasNextDouble(); }
    public float nextFloat() { return (float) nextDouble(); }
    public boolean hasNextBoolean() { String s = mirar(); return s != null && (s.equalsIgnoreCase("true") || s.equalsIgnoreCase("false")); }
    public boolean nextBoolean() {
        String s = mirar();
        if (s == null) throw new NoSuchElementException();
        if (!s.equalsIgnoreCase("true") && !s.equalsIgnoreCase("false")) throw new InputMismatchException(s);
        next();
        return s.equalsIgnoreCase("true");
    }

    public Stream<String> tokens() {
        List<String> l = new ArrayList<>();
        while (hasNext()) l.add(next());
        return l.stream();
    }

    public String toString() { return "java.util.Scanner[delimiters=" + delimTexto + "]"; }

    /** Expresión regular mínima para delimitadores. */
    static final class Patron {
        // nodo: tipo 0 = conjunto de caracteres, 1 = alternativas (lista de secuencias)
        final List<List<Elem>> alternativas = new ArrayList<>();

        static final class Elem {
            Conj conj;          // si es un caracter o clase
            Patron grupo;       // si es un grupo (...)
            int min = 1, max = 1;
        }

        static final class Conj {
            final List<char[]> rangos = new ArrayList<>();
            boolean negado, espacio, digito, palabra, linea, cualquiera;
            boolean contiene(char c) {
                boolean r = cualquiera && c != '\n'
                        || espacio && Character.isWhitespace(c)
                        || digito && Character.isDigit(c)
                        || palabra && (Character.isLetterOrDigit(c) || c == '_')
                        || linea && (c == '\n' || c == '\r');
                for (char[] rg : rangos) if (c >= rg[0] && c <= rg[1]) r = true;
                return negado != r;
            }
        }

        private final String s;
        private int i;

        private Patron(String s) { this.s = s; }

        static Patron compilar(String s) {
            Patron p = new Patron(s);
            p.alternativas(p);
            return p;
        }

        private void alternativas(Patron destino) {
            List<Elem> sec = new ArrayList<>();
            destino.alternativas.add(sec);
            while (i < s.length()) {
                char c = s.charAt(i);
                if (c == '|') { i++; sec = new ArrayList<>(); destino.alternativas.add(sec); continue; }
                if (c == ')') return;
                Elem e = new Elem();
                if (c == '(') {
                    i++;
                    if (s.startsWith("?:", i)) i += 2;
                    Patron g = new Patron(s);
                    g.i = i;
                    g.alternativas(g);
                    i = g.i + 1;
                    e.grupo = g;
                } else if (c == '[') {
                    i++;
                    e.conj = clase();
                } else {
                    e.conj = atomo();
                }
                if (i < s.length()) {
                    char q = s.charAt(i);
                    if (q == '*') { e.min = 0; e.max = Integer.MAX_VALUE; i++; }
                    else if (q == '+') { e.min = 1; e.max = Integer.MAX_VALUE; i++; }
                    else if (q == '?') { e.min = 0; e.max = 1; i++; }
                }
                sec.add(e);
            }
        }

        private Conj atomo() {
            Conj k = new Conj();
            char c = s.charAt(i++);
            if (c == '.') { k.cualquiera = true; return k; }
            if (c != '\\') { k.rangos.add(new char[] { c, c }); return k; }
            escape(k);
            return k;
        }

        private void escape(Conj k) {
            char e = s.charAt(i++);
            switch (e) {
                case 's': k.espacio = true; break;
                case 'd': k.digito = true; break;
                case 'w': k.palabra = true; break;
                case 'R': k.linea = true; break;
                case 'n': k.rangos.add(new char[] { '\n', '\n' }); break;
                case 'r': k.rangos.add(new char[] { '\r', '\r' }); break;
                case 't': k.rangos.add(new char[] { '\t', '\t' }); break;
                case 'p':   // \p{javaWhitespace} y parecidos: espacios
                    int fin = s.indexOf('}', i);
                    if (fin > 0) i = fin + 1;
                    k.espacio = true;
                    break;
                default: k.rangos.add(new char[] { e, e });
            }
        }

        private Conj clase() {
            Conj k = new Conj();
            if (i < s.length() && s.charAt(i) == '^') { k.negado = true; i++; }
            boolean primero = true;
            while (i < s.length() && (s.charAt(i) != ']' || primero)) {
                primero = false;
                char c = s.charAt(i++);
                if (c == '\\') { escape(k); continue; }
                if (i + 1 < s.length() && s.charAt(i) == '-' && s.charAt(i + 1) != ']') {
                    char h = s.charAt(i + 1);
                    i += 2;
                    k.rangos.add(new char[] { c, h });
                } else {
                    k.rangos.add(new char[] { c, c });
                }
            }
            i++;   // ']'
            return k;
        }

        /** Fin de la coincidencia más larga que empieza en desde (-1 si no hay o es vacía). */
        int coincide(String t, int desde) {
            int mejor = -1;
            for (List<Elem> sec : alternativas) {
                int r = sec(t, desde, sec, 0);
                if (r > mejor) mejor = r;
            }
            return mejor > desde ? mejor : -1;
        }

        private int sec(String t, int p, List<Elem> sec, int k) {
            if (k == sec.size()) return p;
            Elem e = sec.get(k);
            // posiciones alcanzables repitiendo el elemento (greedy, con vuelta atrás)
            List<Integer> pos = new ArrayList<>();
            pos.add(p);
            int actual = p, veces = 0;
            while (veces < e.max) {
                int sig;
                if (e.conj != null) {
                    if (actual >= t.length() || !e.conj.contiene(t.charAt(actual))) sig = -1;
                    else if (e.conj.linea && t.charAt(actual) == '\r' && actual + 1 < t.length() && t.charAt(actual + 1) == '\n') sig = actual + 2;   // \R: \r\n es un solo salto
                    else sig = actual + 1;
                }
                else sig = e.grupo.coincide(t, actual);
                if (sig < 0 || sig == actual) break;
                actual = sig;
                veces++;
                pos.add(actual);
            }
            for (int v = pos.size() - 1; v >= e.min; v--) {
                int r = sec(t, pos.get(v), sec, k + 1);
                if (r >= 0) return r;
            }
            return -1;
        }
    }
}
