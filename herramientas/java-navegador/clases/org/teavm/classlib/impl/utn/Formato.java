package org.teavm.classlib.impl.utn;

/**
 * Formateador liviano para String.format, String.formatted y PrintStream.printf en el navegador.
 * El de TeaVM trae los datos de todos los idiomas (suma ~4 MB y ~6 s a cada compilación). Este cubre
 * lo que se usa en la materia: %d %s %S %f %e %x %X %c %b %n %% con índice (1$), banderas (- 0 , + espacio),
 * ancho y precisión. Los decimales salen con punto (como Locale.US) y se redondean igual que Java (HALF_UP
 * sobre el decimal más corto del double).
 */
public final class Formato {
    private Formato() { }

    public static String format(String fmt, Object[] args) {
        if (fmt == null) throw new NullPointerException();
        if (args == null) args = new Object[0];
        StringBuilder out = new StringBuilder();
        int n = fmt.length(), siguiente = 0, anterior = -1, i = 0;
        while (i < n) {
            char ch = fmt.charAt(i);
            if (ch != '%') { out.append(ch); i++; continue; }
            int inicio = i++;
            if (i >= n) throw new IllegalArgumentException("Formato incompleto: '%' al final");
            // índice explícito (2$) o relativo (<)
            int indice = -1;
            int j = i;
            while (j < n && Character.isDigit(fmt.charAt(j))) j++;
            if (j < n && j > i && fmt.charAt(j) == '$') { indice = Integer.parseInt(fmt.substring(i, j)) - 1; i = j + 1; }
            else if (fmt.charAt(i) == '<') { indice = -2; i++; }
            // banderas
            boolean izq = false, ceros = false, miles = false, mas = false, espacio = false, parentesis = false, alt = false;
            boolean seguir = true;
            while (i < n && seguir) {
                switch (fmt.charAt(i)) {
                    case '-': izq = true; i++; break;
                    case '0': ceros = true; i++; break;
                    case ',': miles = true; i++; break;
                    case '+': mas = true; i++; break;
                    case ' ': espacio = true; i++; break;
                    case '(': parentesis = true; i++; break;
                    case '#': alt = true; i++; break;
                    default: seguir = false;
                }
            }
            int ancho = -1;
            j = i;
            while (j < n && Character.isDigit(fmt.charAt(j))) j++;
            if (j > i) { ancho = Integer.parseInt(fmt.substring(i, j)); i = j; }
            int prec = -1;
            if (i < n && fmt.charAt(i) == '.') {
                j = ++i;
                while (j < n && Character.isDigit(fmt.charAt(j))) j++;
                if (j == i) throw new IllegalArgumentException("Falta la precisión en " + fmt.substring(inicio, Math.min(n, j + 1)));
                prec = Integer.parseInt(fmt.substring(i, j)); i = j;
            }
            if (i >= n) throw new IllegalArgumentException("Formato incompleto: " + fmt.substring(inicio));
            char conv = fmt.charAt(i++);
            if (conv == 'n') { out.append('\n'); continue; }
            if (conv == '%') { out.append(rellenar("%", ancho, izq, false)); continue; }
            Object arg;
            int k;
            if (indice == -2) k = anterior;
            else if (indice >= 0) k = indice;
            else k = siguiente++;
            if (k < 0 || k >= args.length) throw new IllegalArgumentException("Falta un argumento para '" + fmt.substring(inicio, i) + "'");
            anterior = k;
            arg = args[k];
            String txt;
            switch (conv) {
                case 's': case 'S':
                    txt = String.valueOf(arg);
                    if (prec >= 0 && txt.length() > prec) txt = txt.substring(0, prec);
                    if (conv == 'S') txt = txt.toUpperCase();
                    out.append(rellenar(txt, ancho, izq, false));
                    break;
                case 'b': case 'B':
                    txt = arg == null ? "false" : (arg instanceof Boolean ? arg.toString() : "true");
                    if (conv == 'B') txt = txt.toUpperCase();
                    out.append(rellenar(txt, ancho, izq, false));
                    break;
                case 'c': case 'C':
                    if (arg == null) txt = "null";
                    else if (arg instanceof Character) txt = arg.toString();
                    else if (arg instanceof Integer) txt = String.valueOf((char) ((Integer) arg).intValue());
                    else throw conversion(conv, arg);
                    if (conv == 'C') txt = txt.toUpperCase();
                    out.append(rellenar(txt, ancho, izq, false));
                    break;
                case 'd':
                    if (arg == null) { out.append(rellenar("null", ancho, izq, false)); break; }
                    if (!(arg instanceof Integer || arg instanceof Long || arg instanceof Short || arg instanceof Byte)) throw conversion(conv, arg);
                    long v = ((Number) arg).longValue();
                    boolean neg = v < 0;
                    String digitos = neg ? (v == Long.MIN_VALUE ? "9223372036854775808" : Long.toString(-v)) : Long.toString(v);
                    if (miles) digitos = agrupar(digitos);
                    out.append(numero(digitos, neg, ancho, izq, ceros, mas, espacio, parentesis));
                    break;
                case 'x': case 'X':
                    if (arg == null) { out.append(rellenar("null", ancho, izq, false)); break; }
                    String hex;
                    if (arg instanceof Integer) hex = Integer.toHexString((Integer) arg);
                    else if (arg instanceof Long) hex = Long.toHexString((Long) arg);
                    else if (arg instanceof Short) hex = Integer.toHexString(((Short) arg) & 0xFFFF);
                    else if (arg instanceof Byte) hex = Integer.toHexString(((Byte) arg) & 0xFF);
                    else throw conversion(conv, arg);
                    if (alt) hex = "0x" + hex;
                    if (conv == 'X') hex = hex.toUpperCase();
                    out.append(ceros && !izq ? ceroIzq(hex, ancho) : rellenar(hex, ancho, izq, false));
                    break;
                case 'f': case 'e': case 'E':
                    if (arg == null) { out.append(rellenar("null", ancho, izq, false)); break; }
                    double d;
                    if (arg instanceof Double || arg instanceof Float) d = ((Number) arg).doubleValue();
                    else if (arg instanceof java.math.BigDecimal) d = ((java.math.BigDecimal) arg).doubleValue();
                    else throw conversion(conv, arg);
                    if (Double.isNaN(d) || Double.isInfinite(d)) {
                        String especial = Double.isNaN(d) ? "NaN" : (d > 0 ? (mas ? "+Infinity" : "Infinity") : (parentesis ? "(Infinity)" : "-Infinity"));
                        out.append(rellenar(especial, ancho, izq, false));
                        break;
                    }
                    boolean negd = d < 0 || (d == 0 && 1 / d < 0);
                    String cuerpo = conv == 'f' ? fijo(Math.abs(d), prec < 0 ? 6 : prec) : cientifico(Math.abs(d), prec < 0 ? 6 : prec);
                    if (conv == 'E') cuerpo = cuerpo.toUpperCase();
                    if (miles && conv == 'f') {
                        int p = cuerpo.indexOf('.');
                        cuerpo = p < 0 ? agrupar(cuerpo) : agrupar(cuerpo.substring(0, p)) + cuerpo.substring(p);
                    }
                    out.append(numero(cuerpo, negd, ancho, izq, ceros, mas, espacio, parentesis));
                    break;
                default:
                    throw new IllegalArgumentException("Conversión no soportada acá: '%" + conv + "' (usá %d, %s, %f o %n)");
            }
        }
        return out.toString();
    }

    private static IllegalArgumentException conversion(char conv, Object arg) {
        return new IllegalArgumentException(conv + " != " + arg.getClass().getName());
    }

    private static String rellenar(String s, int ancho, boolean izq, boolean ceros) {
        if (ancho <= s.length()) return s;
        StringBuilder b = new StringBuilder();
        if (izq) b.append(s);
        for (int k = s.length(); k < ancho; k++) b.append(' ');
        if (!izq) b.append(s);
        return b.toString();
    }

    private static String ceroIzq(String s, int ancho) {
        StringBuilder b = new StringBuilder();
        for (int k = s.length(); k < ancho; k++) b.append('0');
        return b.append(s).toString();
    }

    private static String numero(String digitos, boolean neg, int ancho, boolean izq, boolean ceros, boolean mas, boolean espacio, boolean parentesis) {
        String signo = neg ? (parentesis ? "(" : "-") : (mas ? "+" : (espacio ? " " : ""));
        String fin = neg && parentesis ? ")" : "";
        if (ceros && !izq && ancho > 0) {
            int falta = ancho - signo.length() - digitos.length() - fin.length();
            StringBuilder b = new StringBuilder(signo);
            for (int k = 0; k < falta; k++) b.append('0');
            return b.append(digitos).append(fin).toString();
        }
        return rellenar(signo + digitos + fin, ancho, izq, false);
    }

    private static String agrupar(String ent) {
        StringBuilder b = new StringBuilder();
        int n = ent.length();
        for (int k = 0; k < n; k++) {
            if (k > 0 && (n - k) % 3 == 0) b.append(',');
            b.append(ent.charAt(k));
        }
        return b.toString();
    }

    /** Dígitos decimales del double (sin signo) y la posición de la coma: "12.5" -> (125, 2). */
    private static String digitosDe(double v, int[] punto) {
        String s = Double.toString(v);
        int exp = 0, e = s.indexOf('E');
        if (e >= 0) { exp = Integer.parseInt(s.substring(e + 1)); s = s.substring(0, e); }
        int p = s.indexOf('.');
        String ent = p < 0 ? s : s.substring(0, p), dec = p < 0 ? "" : s.substring(p + 1);
        String dig = ent + dec;
        int pos = ent.length() + exp;
        int k = 0;
        while (k < dig.length() - 1 && dig.charAt(k) == '0') { k++; pos--; }
        punto[0] = pos;
        return dig.substring(k);
    }

    /** Redondea HALF_UP la cadena de dígitos dejando "cuantos" dígitos; devuelve los dígitos y corre la coma si hace falta. */
    private static String redondear(String dig, int cuantos, int[] punto) {
        if (cuantos < 0) { punto[0] = punto[0] - cuantos; return "0"; }
        if (cuantos >= dig.length()) {
            StringBuilder b = new StringBuilder(dig);
            while (b.length() < cuantos) b.append('0');
            return b.toString();
        }
        boolean sube = dig.charAt(cuantos) >= '5';
        char[] c = dig.substring(0, cuantos).toCharArray();
        if (sube) {
            int k = c.length - 1;
            while (k >= 0) {
                if (c[k] == '9') { c[k] = '0'; k--; }
                else { c[k]++; break; }
            }
            if (k < 0) { punto[0]++; return "1" + new String(c); }
        }
        return new String(c);
    }

    private static String fijo(double v, int prec) {
        int[] punto = new int[1];
        String dig = digitosDe(v, punto);
        if (v == 0) { dig = "0"; punto[0] = 1; }
        String r = redondear(dig, punto[0] + prec, punto);
        // r tiene punto[0] dígitos enteros (puede ser <= 0) y el resto decimales
        StringBuilder b = new StringBuilder();
        int pos = punto[0];
        if (pos <= 0) {
            b.append('0');
            if (prec > 0) {
                b.append('.');
                int ceros = Math.min(-pos, prec);
                for (int k = 0; k < ceros; k++) b.append('0');
                for (int k = 0; k < r.length() && b.length() < 2 + prec; k++) b.append(r.charAt(k));
                while (b.length() < 2 + prec) b.append('0');
            }
            return b.toString();
        }
        for (int k = 0; k < pos; k++) b.append(k < r.length() ? r.charAt(k) : '0');
        if (prec > 0) {
            b.append('.');
            for (int k = pos; k < pos + prec; k++) b.append(k < r.length() ? r.charAt(k) : '0');
        }
        return b.toString();
    }

    private static String cientifico(double v, int prec) {
        if (v == 0) {
            StringBuilder b = new StringBuilder("0");
            if (prec > 0) { b.append('.'); for (int k = 0; k < prec; k++) b.append('0'); }
            return b.append("e+00").toString();
        }
        int[] punto = new int[1];
        String dig = digitosDe(v, punto);
        String r = redondear(dig, 1 + prec, punto);
        int exp = punto[0] - 1;
        StringBuilder b = new StringBuilder();
        b.append(r.charAt(0));
        if (prec > 0) { b.append('.'); for (int k = 1; k <= prec; k++) b.append(k < r.length() ? r.charAt(k) : '0'); }
        b.append(exp < 0 ? "e-" : "e+");
        int a = Math.abs(exp);
        if (a < 10) b.append('0');
        return b.append(a).toString();
    }
}
