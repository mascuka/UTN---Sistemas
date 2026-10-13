# Corrector de la práctica: escribe los archivos del alumno, los importa de cero y corre los controles del paso.
import sys, os, json, importlib, traceback, io, contextlib, linecache, re

WORK = os.environ.get("PRACTICA_DIR", "/tmp/practica")
os.makedirs(WORK, exist_ok=True)
if WORK not in sys.path:
    sys.path.insert(0, WORK)


class Falla(Exception):
    pass


def importar(modulo, *nombres):
    """Importa clases o funciones del archivo del alumno, con un mensaje claro si faltan."""
    try:
        m = importlib.import_module(modulo)
    except ModuleNotFoundError as e:
        falta = e.name or modulo
        if falta == modulo:
            raise Falla(f"No encontré el archivo {modulo}.py")
        raise Falla(f"{modulo}.py importa '{falta}', que no existe: revisá el nombre del archivo en el import")
    except ImportError as e:
        raise Falla(_explicar(e))
    if not nombres:
        return m
    res = []
    for n in nombres:
        if not hasattr(m, n):
            raise Falla(f"No encontré «{n}» en {modulo}.py (revisá el nombre: mayúsculas y minúsculas cuentan)")
        res.append(getattr(m, n))
    return res[0] if len(res) == 1 else res


def igual(obtenido, esperado, que):
    if obtenido != esperado:
        raise Falla(f"{que}: tenía que dar {esperado!r} y dio {obtenido!r}")


def cerca(obtenido, esperado, que):
    if isinstance(obtenido, bool) or not isinstance(obtenido, (int, float)):
        raise Falla(f"{que}: tenía que dar el número {esperado!r} y dio {obtenido!r}")
    if abs(obtenido - esperado) > 1e-6 * max(1, abs(esperado)):
        raise Falla(f"{que}: tenía que dar {esperado:g} y dio {obtenido:g}")


def lanza(excepcion, funcion, que):
    try:
        funcion()
    except excepcion:
        return
    except Exception as e:
        raise Falla(f"{que}: tenía que lanzar {excepcion.__name__} y lanzó {type(e).__name__} ({e})")
    raise Falla(f"{que}: tenía que lanzar {excepcion.__name__} y no lanzó nada")


def es_abstracta(clase, *metodos):
    from abc import ABC
    if not issubclass(clase, ABC) and type(clase).__name__ != "ABCMeta":
        raise Falla(f"{clase.__name__} tiene que heredar de ABC (from abc import ABC, abstractmethod)")
    abstractos = getattr(clase, "__abstractmethods__", set())
    for m in metodos:
        if m not in abstractos:
            raise Falla(f"El método {m}() de {clase.__name__} tiene que ser abstracto (@abstractmethod)")


def hereda(sub, base):
    if not (isinstance(sub, type) and issubclass(sub, base)):
        raise Falla(f"{getattr(sub, '__name__', sub)} tiene que heredar de {base.__name__}: class {getattr(sub, '__name__', 'X')}({base.__name__})")


def _nombre(obj):
    n = type(obj).__name__
    return n[6:] if n.startswith("Prueba") else n


def atributo(obj, nombre, esperado=None, que=None, tolerancia=False):
    if not hasattr(obj, nombre):
        padres = [b for b in type(obj).__mro__[1:] if b.__module__ not in ("builtins", "abc")]
        extra = ""
        if padres and not type(obj).__name__.startswith("Prueba"):
            extra = f" Si es un dato de {padres[0].__name__}, ¿llamaste a super().__init__(…) en el constructor?"
        raise Falla(f"El objeto {_nombre(obj)} no tiene el atributo «{nombre}»: guardalo en el constructor con self.{nombre} = …{extra}")
    if esperado is not None:
        v = getattr(obj, nombre)
        (cerca if tolerancia else igual)(v, esperado, que or f"{_nombre(obj)}.{nombre}")


def concreta(base, metodos, *args):
    """Crea una subclase de prueba que implementa los métodos abstractos, para probar la clase base."""
    cuerpo = {m: (lambda self: 0) for m in metodos}
    Prueba = type("Prueba" + base.__name__, (base,), cuerpo)
    return Prueba(*args)


def correr_main(modulo="main", funcion="main"):
    m = importar(modulo)
    if not hasattr(m, funcion):
        raise Falla(f"No encontré la función {funcion}() en {modulo}.py")
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        getattr(m, funcion)()
    return salida.getvalue()


def formatos(v):
    """Las formas más comunes de imprimir un número."""
    xs = {str(v), repr(v)}
    if isinstance(v, float):
        xs |= {f"{v:.2f}", f"{v:,.2f}", f"{v:.1f}", f"{v:,.1f}", f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}
        if v == int(v):
            xs |= {str(int(v)), f"{int(v):,}"}
    if isinstance(v, int):
        xs |= {f"{v:,}", f"{v:.2f}", f"{v:,.2f}", f"{float(v)}"}
    return xs


def aparece(valor, salida, que):
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        if not any(x in salida for x in formatos(valor)):
            raise Falla(f"No veo {que} en lo que imprime el main: tenía que aparecer {valor:,.2f}")
    elif str(valor) not in salida:
        raise Falla(f"No veo {que} en lo que imprime el main: tenía que aparecer «{valor}»")


AYUDAS = {k: v for k, v in dict(globals()).items() if k in (
    "Falla", "importar", "igual", "cerca", "lanza", "es_abstracta", "hereda", "atributo", "concreta",
    "correr_main", "aparece")}


def _donde(tb):
    for fr in reversed(traceback.extract_tb(tb)):
        if fr.filename.startswith(WORK):
            return {"archivo": os.path.basename(fr.filename), "linea": fr.lineno, "codigo": (fr.line or "").strip()}
    return None


def _explicar(e):
    t, m = type(e).__name__, str(e)
    if isinstance(e, ModuleNotFoundError):
        return f"No encontré el archivo {e.name}.py (revisá el import)"
    if isinstance(e, ImportError):
        g = re.search(r"cannot import name '(\w+)' from '(\w+)'", m)
        return f"No encontré «{g.group(1)}» en {g.group(2)}.py" if g else m
    if isinstance(e, NameError):
        g = re.search(r"name '(\w+)' is not defined", m)
        return f"Usás «{g.group(1)}» pero no está definido (¿falta un import o está mal escrito?)" if g else m
    if isinstance(e, AttributeError):
        g = re.search(r"'(\w+)' object has no attribute '(\w+)'", m)
        if g:
            return f"Un objeto {g.group(1)} no tiene «{g.group(2)}»: si es un dato, guardalo en el constructor con self.{g.group(2)}; si es un método, definilo en la clase"
        return m
    if isinstance(e, TypeError):
        g = re.search(r"Can't instantiate abstract class (\w+) with(?:out an implementation for)? abstract methods? '?([\w', ]+)'?", m)
        if g:
            return f"No se puede crear un {g.group(1)}: le falta definir {g.group(2).strip(chr(39))}()"
        g = re.search(r"(\w+)\(\) takes no arguments", m)
        if g:
            n = g.group(1)[6:] if g.group(1).startswith("Prueba") else g.group(1)
            return f"{n} todavía no tiene constructor: escribí def __init__(self, …) con los datos del contrato"
        g = re.search(r"(\w+)\.__init__\(\) takes (\d+) positional arguments? but (\d+) (?:were|was) given", m)
        if g:
            return f"El constructor de {g.group(1)} recibe {int(g.group(2)) - 1} datos y se le pasaron {int(g.group(3)) - 1}: revisá el contrato"
        g = re.search(r"__init__\(\) missing (\d+) required positional arguments?: (.+)", m)
        if g:
            return f"Al constructor le faltan datos: {g.group(2)}"
        if any(x in m for x in ("unsupported operand", "can only concatenate", "can't multiply sequence", "not supported between instances")):
            return f"Operación entre tipos distintos ({m}): ¿convertiste los datos del CSV con int() o float()?"
        return m
    if isinstance(e, ZeroDivisionError):
        return "División por cero: ¿estás dividiendo por la cantidad de una lista vacía?"
    if isinstance(e, FileNotFoundError):
        return f"No encontré el archivo «{e.filename}»: revisá el nombre del CSV"
    if isinstance(e, ValueError):
        g = re.search(r"could not convert string to float: '(.*)'|invalid literal for int\(\) with base 10: '(.*)'", m)
        if g:
            v = g.group(1) or g.group(2) or ""
            extra = " ¿Te salteaste la línea de títulos?" if re.match(r"^[a-z_]+$", v) else ""
            return f"No se pudo convertir «{v}» a número.{extra}"
        return f"ValueError: {m}"
    if isinstance(e, RecursionError):
        return "Recursión infinita: ¿una propiedad que se llama a sí misma? (usá self._dato adentro de la propiedad)"
    return f"{t}: {m}"


def _sintaxis(e):
    m = e.msg or "error de sintaxis"
    trad = {"expected ':'": "falta ':' al final de la línea", "invalid syntax": "sintaxis inválida",
            "unexpected indent": "sangría de más", "expected an indented block": "falta el bloque con sangría después de ':'",
            "unindent does not match any outer indentation level": "la sangría no coincide con las líneas de arriba",
            "unterminated string literal": "un texto sin cerrar las comillas", "'(' was never closed": "un paréntesis sin cerrar"}
    for k, v in trad.items():
        if m.startswith(k):
            m = v
            break
    return m


def correr(archivos, controles, ejecutar=False):
    import shutil
    for f in os.listdir(WORK):
        p = os.path.join(WORK, f)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for nombre, texto in archivos.items():
        ruta = os.path.join(WORK, nombre)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as a:
            a.write(texto)
    os.chdir(WORK)
    modulos = [n[:-3] for n in archivos if n.endswith(".py")]
    for n in list(sys.modules):
        if n in modulos:
            del sys.modules[n]
    importlib.invalidate_caches()
    linecache.clearcache()
    for nombre, texto in archivos.items():
        if nombre.endswith(".py"):
            try:
                compile(texto, os.path.join(WORK, nombre), "exec")
            except SyntaxError as e:
                return json.dumps({"sintaxis": {"archivo": nombre, "linea": e.lineno, "msg": _sintaxis(e), "codigo": (e.text or "").rstrip("\n")}})
    res = []
    for c in controles:
        ns = dict(AYUDAS)
        basura = io.StringIO()
        try:
            with contextlib.redirect_stdout(basura):
                exec(c["c"], ns)
            res.append({"ok": True, "d": c["d"]})
        except Falla as e:
            res.append({"ok": False, "d": c["d"], "msg": str(e)})
        except AssertionError as e:
            res.append({"ok": False, "d": c["d"], "msg": str(e) or "No se cumple lo pedido", "donde": _donde(e.__traceback__)})
        except Exception as e:
            res.append({"ok": False, "d": c["d"], "msg": _explicar(e), "donde": _donde(e.__traceback__)})
    salida = None
    if ejecutar:
        try:
            salida = correr_main(*ejecutar) if isinstance(ejecutar, list) else correr_main()
        except Falla as e:
            salida = "⚠ " + str(e)
        except Exception as e:
            d = _donde(e.__traceback__)
            salida = "⚠ " + _explicar(e) + (f"\n   en {d['archivo']}, línea {d['linea']}: {d['codigo']}" if d else "")
        salida = salida[:6000]
    return json.dumps({"res": res, "salida": salida})
