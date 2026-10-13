package org.teavm.classlib.impl.utn;

/**
 * Lo que tira el classlib de TeaVM al convertir textos, con los mismos mensajes que el JDK 21.
 * Los de TeaVM son distintos ("String contains digits out of radix 10: abc", o sin mensaje en Double) y en los
 * parciales se imprime e.getMessage() de cada fila inválida: así la salida queda igual a la de la compu.
 */
public final class Numeros {
    private Numeros() { }

    private static NumberFormatException entrada(String s, int radix) {
        return new NumberFormatException("For input string: \"" + s + "\"" + (radix == 10 ? "" : " under radix " + radix));
    }

    private static void revisarRadix(int radix) {
        if (radix < Character.MIN_RADIX) throw new NumberFormatException("radix " + radix + " less than Character.MIN_RADIX");
        if (radix > Character.MAX_RADIX) throw new NumberFormatException("radix " + radix + " greater than Character.MAX_RADIX");
    }

    /** Integer.parseInt(s, radix), como el del JDK. */
    public static int parseInt(String s, int radix) {
        if (s == null) throw new NumberFormatException("Cannot parse null string");
        revisarRadix(radix);
        int largo = s.length(), i = 0, limite = -Integer.MAX_VALUE;
        if (largo == 0) throw entrada(s, radix);
        boolean negativo = false;
        char primero = s.charAt(0);
        if (primero < '0') {
            if (primero == '-') { negativo = true; limite = Integer.MIN_VALUE; }
            else if (primero != '+') throw entrada(s, radix);
            if (largo == 1) throw entrada(s, radix);
            i++;
        }
        int tope = limite / radix, r = 0;
        while (i < largo) {
            int d = Character.digit(s.charAt(i++), radix);
            if (d < 0 || r < tope) throw entrada(s, radix);
            r *= radix;
            if (r < limite + d) throw entrada(s, radix);
            r -= d;
        }
        return negativo ? r : -r;
    }

    /** Long.parseLong(s, radix), como el del JDK. */
    public static long parseLong(String s, int radix) {
        if (s == null) throw new NumberFormatException("Cannot parse null string");
        revisarRadix(radix);
        int largo = s.length(), i = 0;
        long limite = -Long.MAX_VALUE;
        if (largo == 0) throw entrada(s, radix);
        boolean negativo = false;
        char primero = s.charAt(0);
        if (primero < '0') {
            if (primero == '-') { negativo = true; limite = Long.MIN_VALUE; }
            else if (primero != '+') throw entrada(s, radix);
            if (largo == 1) throw entrada(s, radix);
            i++;
        }
        long tope = limite / radix, r = 0;
        while (i < largo) {
            int d = Character.digit(s.charAt(i++), radix);
            if (d < 0 || r < tope) throw entrada(s, radix);
            r *= radix;
            if (r < limite + d) throw entrada(s, radix);
            r -= d;
        }
        return negativo ? r : -r;
    }

    /**
     * Antes de Double.parseDouble y Float.parseFloat: si el texto no es un número (con la gramática del JDK),
     * tira la excepción con el mensaje del JDK. Si lo es, sigue el de TeaVM.
     */
    public static void revisarDecimal(String s) {
        if (s == null) throw new NullPointerException("Cannot invoke \"String.trim()\" because \"in\" is null");
        String t = s.trim();
        int n = t.length(), i = 0;
        if (n == 0) throw new NumberFormatException("empty String");
        if (t.charAt(0) == '+' || t.charAt(0) == '-') i++;
        if (t.startsWith("NaN", i) && i + 3 == n || t.startsWith("Infinity", i) && i + 8 == n) return;
        if (t.startsWith("0x", i) || t.startsWith("0X", i)) return;   // hexadecimal: que lo resuelva TeaVM
        int digitos = 0;
        while (i < n && Character.isDigit(t.charAt(i))) { i++; digitos++; }
        if (i < n && t.charAt(i) == '.') {
            i++;
            while (i < n && Character.isDigit(t.charAt(i))) { i++; digitos++; }
        }
        if (digitos == 0) throw new NumberFormatException("For input string: \"" + t + "\"");
        if (i < n && (t.charAt(i) == 'e' || t.charAt(i) == 'E')) {
            i++;
            if (i < n && (t.charAt(i) == '+' || t.charAt(i) == '-')) i++;
            int exp = 0;
            while (i < n && Character.isDigit(t.charAt(i))) { i++; exp++; }
            if (exp == 0) throw new NumberFormatException("For input string: \"" + t + "\"");
        }
        if (i < n && "fFdD".indexOf(t.charAt(i)) >= 0) i++;
        if (i != n) throw new NumberFormatException("For input string: \"" + t + "\"");
    }

    /** Para el mensaje de Enum.valueOf ("No enum constant ar.edu.Estado.X"): el nombre de la clase, con puntos. */
    public static String claseEnum(Object o) {
        if (o instanceof Class) return ((Class<?>) o).getName().replace('$', '.');
        return String.valueOf(o);
    }
}
