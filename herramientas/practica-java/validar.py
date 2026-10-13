"""Prueba cada ejercicio con el JDK (javac y java), con el mismo Prueba.java y la misma forma de armar
Controles.java que la página (practica/java/trabajador.js): la solución de cada paso tiene que pasar todos
los controles y el código de inicio tiene que fallar al menos uno.
Uso (desde la raíz del repo): python3 herramientas/practica-java/validar.py ej1 ej2 …"""
import importlib, os, re, shutil, subprocess, sys, tempfile
sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
PRUEBA = open(os.path.join(REPO, "practica", "java", "Prueba.java"), encoding="utf-8").read()
ENV = {k: v for k, v in os.environ.items() if k != "JAVA_TOOL_OPTIONS"}


def controles_java(controles, importar):
    lineas = ["import java.util.*;", "import java.util.function.*;", "import java.util.stream.*;", "import java.io.*;", "import java.nio.file.*;"]
    for p in importar: lineas.append(f"import {p}.*;")
    lineas += ["public class Controles {", "    public static void main(String[] args) {"]
    rango = {}
    for k, codigo in controles:
        desde = len(lineas) + 1
        lineas.append(f"        Prueba.control({k}, () -> {{")
        for l in codigo.split("\n"): lineas.append("            " + l)
        lineas.append("        });")
        rango[k] = (desde, len(lineas))
    lineas += ["        Prueba.fin();", "    }", "}"]
    return "\n".join(lineas) + "\n", rango


def escribir(dir, archivos):
    for ruta, texto in archivos.items():
        p = os.path.join(dir, ruta); os.makedirs(os.path.dirname(p) or dir, exist_ok=True)
        open(p, "w", encoding="utf-8").write(texto)


def javac(dir, rutas):
    out = os.path.join(dir, "_clases"); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    r = subprocess.run(["javac", "-encoding", "UTF-8", "-nowarn", "-d", out] + rutas, cwd=dir, capture_output=True, text=True, env=ENV)
    errores = []
    for m in re.finditer(r"^(.+?\.java):(\d+): error: (.*)$", r.stderr, re.M):
        errores.append((m.group(1), int(m.group(2)), m.group(3)))
    return r.returncode == 0, errores, r.stderr


def correr(E, archivos, checks, datos):
    """Devuelve (errores_del_alumno, {k: (estado, msg)})."""
    with tempfile.TemporaryDirectory() as d:
        escribir(d, datos); escribir(d, archivos)
        propios = [r for r in archivos if r.endswith(".java")]
        ok, err, txt = javac(d, propios)
        if not ok:
            return err or [("?", 0, txt[:300])], {}
        vivos = list(enumerate(c["c"] for c in checks)); res = {}
        while True:
            texto, rango = controles_java(vivos, E["importar"])
            escribir(d, {"Prueba.java": PRUEBA, "Controles.java": texto})
            ok, err, txt = javac(d, propios + ["Prueba.java", "Controles.java"])
            if ok: break
            malos = {}
            for f, linea, msg in err:
                if not f.endswith("Controles.java"):
                    return [(f, linea, msg)], {}
                for k, _ in vivos:
                    a, b = rango[k]
                    if a <= linea <= b and k not in malos: malos[k] = msg
            if not malos: return [("Controles.java", 0, txt[:300])], {}
            for k, msg in malos.items(): res[k] = ("nocompila", msg)
            vivos = [(k, c) for k, c in vivos if k not in malos]
        if vivos:
            r = subprocess.run(["java", "-cp", os.path.join(d, "_clases"), "Controles"], cwd=d, capture_output=True, text=True, timeout=20, env=ENV)
            for l in r.stdout.splitlines():
                m = re.match(r"@@(ok|mal|error) (\d+) ?(.*)", l)
                if m: res[int(m.group(2))] = (m.group(1), m.group(3))
            if "@@fin" not in r.stdout: print("      ¡no terminó! stderr:", r.stderr[:300])
        return [], res


def ejecutar(E, archivos, datos, entrada, args):
    with tempfile.TemporaryDirectory() as d:
        escribir(d, datos); escribir(d, archivos)
        ok, err, txt = javac(d, [r for r in archivos if r.endswith(".java")])
        if not ok: return "NO COMPILA: " + txt[:300]
        clase = entrada[:-5].replace("/", ".")
        r = subprocess.run(["java", "-cp", os.path.join(d, "_clases"), clase] + list(args), cwd=d, capture_output=True, text=True, timeout=20, env=ENV)
        return r.stdout + r.stderr


def validar(E):
    ok = True; acum = {}
    for k, p in enumerate(E["pasos"], 1):
        antes = dict(acum)
        for f, c in p["inicio"].items(): antes.setdefault(f, c)
        acum.update(p["solucion"])
        for f, c in p["inicio"].items(): acum.setdefault(f, c)
        err, res = correr(E, acum, p["checks"], E["datos"])
        fallan = [(i, res.get(i)) for i in range(len(p["checks"])) if res.get(i, ("?",))[0] != "ok"]
        if err or fallan:
            ok = False
            print(f"  ✗ paso {k} {p['titulo']}: la solución NO pasa:", err or fallan)
        err2, res2 = correr(E, antes, p["checks"], E["datos"])
        n_mal = len(err2) if err2 else sum(1 for i in range(len(p["checks"])) if res2.get(i, ("?",))[0] != "ok")
        if not n_mal:
            ok = False
            print(f"  ✗ paso {k} {p['titulo']}: con el código de inicio ya pasa todo (los controles no sirven)")
        extra = ""
        if p.get("ejecutar"):
            salida = ejecutar(E, acum, E["datos"], p["ejecutar"]["entrada"], p["ejecutar"].get("args", []))
            extra = "\n      salida: " + repr(salida[:240])
        print(f"  {'✓' if not err and not fallan else '✗'} paso {k}: {p['titulo']} · {len(p['checks'])} controles · con el inicio fallan {n_mal}{extra}")
    return ok


if __name__ == "__main__":
    total = True
    for nombre in sys.argv[1:]:
        m = importlib.import_module(nombre)
        print("==", m.E["titulo"])
        total &= validar(m.E)
    sys.exit(0 if total else 1)
