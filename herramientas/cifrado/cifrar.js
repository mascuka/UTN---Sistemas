/* Cifra los archivos de material/ para que en el repo (que es público) no se puedan abrir sin acceso.

   Cada archivo se cifra con una llave AES-256-GCM al azar, y esa llave se envuelve con la llave pública RSA-OAEP (SHA-256)
   de cifrado/publica.json. Usa WebCrypto, lo mismo que el navegador. Formato (lo abre sw.js con la llave privada que da
   Firebase a quien tiene acceso):
       "ISI1" · largo de la llave envuelta (2 bytes) · llave envuelta · IV (12 bytes) · texto cifrado + etiqueta GCM

   Los originales no se pierden: van al repo privado de originales (por defecto ../UTN---Sistemas-originales, o
   --originales DIR), con manifiesto.json (ruta → SHA-256 del original). Así las herramientas pueden seguir usándolos.

   Uso, desde la raíz del repo:
       node herramientas/cifrado/cifrar.js              cifra lo nuevo o cambiado de material/ (y guarda el original)
       node herramientas/cifrado/cifrar.js --abrir      pone los originales en material/ para trabajar con las herramientas
       node herramientas/cifrado/cifrar.js --revisar    avisa (y sale con error) si hay algo sin cifrar en material/
       node herramientas/cifrado/cifrar.js --instalar   instala el gancho de git que no deja hacer commit de algo sin cifrar

   Flujo de trabajo: --abrir, usar las herramientas o sumar archivos a material/ como siempre, y antes del commit, sin
   argumentos: lo que no cambió vuelve a quedar como está en el repo (sin cifrarlo de nuevo) y lo nuevo se cifra. */
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const { subtle } = require('crypto').webcrypto, { createHash, randomBytes } = require('crypto');

const RAIZ = path.resolve(__dirname, '..', '..');
const MATERIAL = path.join(RAIZ, 'material');
const PUBLICA = path.join(RAIZ, 'cifrado', 'publica.json');
const MAGIA = Buffer.from('ISI1');
const SIN_CIFRAR = /(-version\.txt|\.gitkeep)$/;   // los que la página consulta sola (la versión de los laboratorios)

const arg = n => process.argv.includes(n);
const valor = (n, def) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : def; };
const sha = d => createHash('sha256').update(d).digest('hex');
const esCifrado = d => d.length >= 4 && d.subarray(0, 4).equals(MAGIA);
const rel = (p, base) => path.relative(base, p).split(path.sep).join('/');
function* archivos(base){
  if(!fs.existsSync(base)) return;
  for(const e of fs.readdirSync(base, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))){
    const p = path.join(base, e.name);
    if(e.isDirectory()) yield* archivos(p); else if(e.isFile()) yield p;
  }
}
const primeros = p => { const fd = fs.openSync(p, 'r'), b = Buffer.alloc(4); fs.readSync(fd, b, 0, 4, 0); fs.closeSync(fd); return b; };
const sueltos = () => [...archivos(MATERIAL)].map(p => rel(p, RAIZ)).filter(r => !SIN_CIFRAR.test(r) && !esCifrado(primeros(path.join(RAIZ, r))));
function enHead(r){
  try { return execFileSync('git', ['-C', RAIZ, 'cat-file', '-p', `HEAD:${r}`], { maxBuffer: 1 << 30, stdio: ['ignore', 'pipe', 'ignore'] }); }
  catch(e){ return null; }
}

async function llavePublica(){
  const j = JSON.parse(fs.readFileSync(PUBLICA, 'utf8'));
  return { n: j.n, k: await subtle.importKey('jwk', { kty: 'RSA', n: j.n, e: j.e, alg: 'RSA-OAEP-256' }, { name: 'RSA-OAEP', hash: 'SHA-256' }, false, ['encrypt']) };
}
async function cifrar(plano, publica){
  const clave = randomBytes(32), iv = randomBytes(12);
  const envuelta = Buffer.from(await subtle.encrypt({ name: 'RSA-OAEP' }, publica, clave));
  const aes = await subtle.importKey('raw', clave, 'AES-GCM', false, ['encrypt']);
  const cuerpo = Buffer.from(await subtle.encrypt({ name: 'AES-GCM', iv }, aes, plano));
  const largo = Buffer.alloc(2); largo.writeUInt16BE(envuelta.length);
  return Buffer.concat([MAGIA, largo, envuelta, iv, cuerpo]);
}

async function main(){
  if(arg('--revisar')){
    const s = sueltos();
    s.forEach(r => console.log('sin cifrar:', r));
    process.exit(s.length ? 1 : 0);
  }
  if(arg('--instalar')){
    const gancho = path.join(RAIZ, '.git', 'hooks', 'pre-commit');
    fs.writeFileSync(gancho, `#!/bin/sh
# No deja hacer commit de archivos de material/ sin cifrar (herramientas/cifrado/cifrar.js)
[ -f cifrado/publica.json ] || exit 0
git diff --cached --name-only --diff-filter=AM -z -- material/ | while IFS= read -r -d '' f; do
  case "$f" in *-version.txt|*.gitkeep) continue;; esac
  if [ "$(git show ":$f" | head -c 4)" != "ISI1" ]; then echo "Sin cifrar: $f (corré node herramientas/cifrado/cifrar.js)"; exit 1; fi
done
`, { mode: 0o755 });
    console.log('Gancho instalado:', gancho);
    return;
  }
  const orig = path.resolve(valor('--originales', path.join(path.dirname(RAIZ), 'UTN---Sistemas-originales')));
  if(!fs.existsSync(orig)) throw new Error(`No encuentro el repo de originales en ${orig} (clonalo o pasá --originales).`);
  const manRuta = path.join(orig, 'manifiesto.json');
  const man = fs.existsSync(manRuta) ? JSON.parse(fs.readFileSync(manRuta, 'utf8')) : {};

  if(arg('--abrir')){
    let n = 0;
    for(const r of Object.keys(man).sort()){
      const o = path.join(orig, r), p = path.join(RAIZ, r);
      if(!fs.existsSync(o)) continue;
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.copyFileSync(o, p); n++;
    }
    console.log(`${n} originales puestos en material/. Antes del commit: node herramientas/cifrado/cifrar.js`);
    return;
  }

  const pub = await llavePublica();
  // La página tiene que conocer la misma llave (CIFRADO.n en index.html); si no, no abriría nada
  const m = fs.readFileSync(path.join(RAIZ, 'index.html'), 'utf8').match(/const CIFRADO = \{ n: "([^"]*)" \}/);
  if(!m || m[1] !== pub.n) throw new Error('CIFRADO.n en index.html no es el módulo de cifrado/publica.json: no cifro nada.');

  let cifrados = 0, iguales = 0, borrados = 0;
  // 1) Lo que está sin cifrar en material/: si es igual al original guardado y en el repo ya está cifrado, vuelve a como
  //    estaba (así no cambia en cada commit); si es nuevo o cambió, se guarda el original y se cifra
  for(const p of [...archivos(MATERIAL)]){
    const r = rel(p, RAIZ);
    if(SIN_CIFRAR.test(r)) continue;
    const datos = fs.readFileSync(p);
    if(esCifrado(datos)) continue;
    const h = sha(datos);
    if(man[r] === h){
      const ant = enHead(r);
      if(ant && esCifrado(ant)){ fs.writeFileSync(p, ant); iguales++; continue; }
    }
    const o = path.join(orig, r);
    fs.mkdirSync(path.dirname(o), { recursive: true });
    fs.copyFileSync(p, o);
    fs.writeFileSync(p, await cifrar(datos, pub.k));
    man[r] = h; cifrados++;
  }
  // 2) Lo que se cambió o se sumó directamente en los originales
  for(const o of [...archivos(path.join(orig, 'material'))]){
    const r = 'material/' + rel(o, path.join(orig, 'material'));
    if(SIN_CIFRAR.test(r)) continue;
    const datos = fs.readFileSync(o), p = path.join(RAIZ, r);
    if(man[r] === sha(datos) && fs.existsSync(p)) continue;
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, await cifrar(datos, pub.k));
    man[r] = sha(datos); cifrados++;
  }
  // 3) Lo que se borró de material/ se borra también de los originales
  for(const r of Object.keys(man).sort()) if(!fs.existsSync(path.join(RAIZ, r))){
    const o = path.join(orig, r);
    if(fs.existsSync(o)) fs.unlinkSync(o);
    delete man[r]; borrados++;
  }
  fs.writeFileSync(manRuta, JSON.stringify(Object.fromEntries(Object.entries(man).sort(([a], [b]) => a.localeCompare(b))), null, 1) + '\n');
  console.log(`Cifrados: ${cifrados} · sin cambios: ${iguales} · borrados: ${borrados} · en el manifiesto: ${Object.keys(man).length}`);
  const s = sueltos();
  if(s.length) throw new Error('Quedaron sin cifrar: ' + s.join(', '));
}
main().catch(e => { console.error(e.message || e); process.exit(1); });
