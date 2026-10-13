"""Deja en cldr-json.zip (datos de idiomas de TeaVM) solo inglés y español: pasa de 15,8 MB a 0,24 MB.
Uso: python3 reducir-cldr.py cldr-json.zip cldr-chico.zip"""
import sys, zipfile
GUARDAR = {"en", "en-001", "es", "es-AR", "es-419", "root"}
entrada, salida = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(entrada)
with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as out:
    for info in z.infolist():
        top = info.filename.split("/")[0]
        if "/" not in info.filename or top in GUARDAR or top == "supplemental":
            out.writestr(info, z.read(info.filename))
