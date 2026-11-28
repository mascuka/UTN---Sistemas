# Notas para trabajar en este repo

Todo está explicado en `LEEME.md`. Lo más importante para no romper nada:

- **Los archivos de `material/` van cifrados** (ver «Archivos cifrados» en `LEEME.md`). Nunca hacer commit de un PDF, ZIP o cualquier archivo de `material/` sin cifrar.
  - Los originales están en el repo privado `mascuka/UTN---Sistemas-originales`: clonarlo al lado, en `../UTN---Sistemas-originales`.
  - Para usar las herramientas: `node herramientas/cifrado/cifrar.js --abrir`.
  - Antes de cada commit: `node herramientas/cifrado/cifrar.js` (y `--revisar` para confirmar que no quedó nada sin cifrar). Después, hacer commit y push también en el repo de originales.
  - `node herramientas/cifrado/cifrar.js --instalar` pone un gancho que frena un commit con algo sin cifrar.
- No hay que cambiar ni crear las llaves: la privada está solo en Firebase (`llaves/archivos`); para cifrar alcanza con la pública (`cifrado/publica.json`).
- Las reglas de Firestore están en `firestore.rules`, con el mail del dueño como `MAIL_DEL_DUEÑO`. Si cambian, el dueño las pega en Firebase con su mail real. El mail no se escribe en el repo, que es público.
