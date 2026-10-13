package org.teavm.classlib.impl.utn;

/** Ayudas para el classlib de TeaVM en el navegador: nombre simple de una clase y rutas relativas. */
public final class Nombres {
    private Nombres() { }

    /** getSimpleName a partir de getName ("java.util.ArrayList" -> "ArrayList", "Main$1Q" -> "Q"). */
    public static String simple(String nombre) {
        if (nombre == null) return null;
        if (nombre.startsWith("[")) {
            int dim = 0;
            while (dim < nombre.length() && nombre.charAt(dim) == '[') dim++;
            String base;
            char t = dim < nombre.length() ? nombre.charAt(dim) : 'L';
            switch (t) {
                case 'I': base = "int"; break;
                case 'J': base = "long"; break;
                case 'D': base = "double"; break;
                case 'F': base = "float"; break;
                case 'Z': base = "boolean"; break;
                case 'C': base = "char"; break;
                case 'B': base = "byte"; break;
                case 'S': base = "short"; break;
                default: base = simple(nombre.substring(dim + 1, nombre.endsWith(";") ? nombre.length() - 1 : nombre.length()));
            }
            StringBuilder b = new StringBuilder(base);
            for (int k = 0; k < dim; k++) b.append("[]");
            return b.toString();
        }
        int i = Math.max(nombre.lastIndexOf('.'), nombre.lastIndexOf('$'));
        String s = nombre.substring(i + 1);
        int k = 0;
        while (k < s.length() && Character.isDigit(s.charAt(k))) k++;
        return s.substring(k);
    }

    /** Las rutas relativas se toman desde la raíz ("datos/x.csv" -> "/datos/x.csv"), sin "." ni "..". */
    public static String absoluta(String ruta) {
        if (ruta == null) return null;
        String[] partes = ruta.split("/");
        java.util.ArrayList<String> pila = new java.util.ArrayList<>();
        for (String p : partes) {
            if (p.isEmpty() || p.equals(".")) continue;
            if (p.equals("..")) { if (!pila.isEmpty()) pila.remove(pila.size() - 1); continue; }
            pila.add(p);
        }
        StringBuilder b = new StringBuilder();
        for (String p : pila) b.append('/').append(p);
        return b.length() == 0 ? "/" : b.toString();
    }

    /**
     * Files.createDirectories como el del JDK: si la carpeta ya existe no hace nada (el de TeaVM tiraba
     * FileAlreadyExistsException con las rutas de un solo nombre, como "datos").
     */
    public static java.nio.file.Path crearCarpetas(java.nio.file.Path p, java.nio.file.attribute.FileAttribute<?>[] atributos) throws java.io.IOException {
        if (java.nio.file.Files.isDirectory(p)) return p;
        if (java.nio.file.Files.exists(p)) throw new java.nio.file.FileAlreadyExistsException(p.toString());
        java.nio.file.Path padre = p.getParent();
        if (padre != null) crearCarpetas(padre, atributos);
        java.nio.file.Files.createDirectory(p, atributos);
        return p;
    }
}
