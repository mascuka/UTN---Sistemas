/* Service worker de la página: abre los archivos cifrados de material/.
   En el repo, los PDF, ZIP y demás de material/ están cifrados (formato ISI1, lo arma herramientas/cifrado/cifrar.py):
     "ISI1" · largo de la llave envuelta (2 bytes) · llave AES envuelta con RSA-OAEP (SHA-256) · IV (12 bytes) · AES-GCM
   La llave privada la da Firebase solo a quien tiene acceso; la página la guarda en IndexedDB (isi-cifrado) y avisa acá.
   Cada pedido a material/ (el visor, una pestaña nueva, una descarga, el ZIP de la materia) pasa por acá: si el archivo
   está cifrado se descifra y se devuelve como si fuera el original; si no, va tal cual. Sin llave, «Necesitás acceso». */
const MAGIA = [73, 83, 73, 49];   // "ISI1"
const TIPOS = {
  pdf: "application/pdf", zip: "application/zip", rar: "application/vnd.rar", html: "text/html; charset=utf-8",
  txt: "text/plain; charset=utf-8", csv: "text/csv; charset=utf-8", json: "application/json", ino: "text/plain; charset=utf-8",
  py: "text/plain; charset=utf-8", java: "text/plain; charset=utf-8", m: "text/plain; charset=utf-8", md: "text/plain; charset=utf-8",
  pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", svg: "image/svg+xml"
};
let llave;   // undefined: no se miró todavía; null: no hay

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("message", e => { if(e.data && e.data.tipo === "llave") llave = e.data.llave || null; });

function leerLlave(){
  return new Promise(ok => {
    try {
      const r = indexedDB.open("isi-cifrado", 1);
      r.onupgradeneeded = () => r.result.createObjectStore("llaves");
      r.onerror = () => ok(null);
      r.onsuccess = () => {
        try {
          const q = r.result.transaction("llaves", "readonly").objectStore("llaves").get("archivos");
          q.onsuccess = () => ok(q.result || null);
          q.onerror = () => ok(null);
        } catch(e){ ok(null); }
      };
    } catch(e){ ok(null); }
  });
}

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if(e.request.method !== "GET" || url.origin !== self.location.origin || !url.pathname.includes("/material/")) return;
  e.respondWith(servir(e.request, url));
});

const tipoDe = p => TIPOS[(p.split(".").pop() || "").toLowerCase()] || "application/octet-stream";

async function servir(pedido, url){
  // Siempre el archivo entero (sin Range): lo cifrado no se puede abrir de a pedazos
  const r = await fetch(url.href, { credentials: "same-origin" });
  if(!r.ok) return r;
  const datos = new Uint8Array(await r.arrayBuffer());
  const cifrado = datos.length > 18 && MAGIA.every((b, i) => datos[i] === b);
  if(!cifrado) return new Response(datos, { status: 200, headers: { "Content-Type": r.headers.get("Content-Type") || tipoDe(url.pathname) } });
  if(llave === undefined || llave === null) llave = await leerLlave();
  if(!llave) return sinAcceso(pedido, "Para abrir este archivo, entrá a la página con una cuenta que tenga acceso.");
  try {
    const lk = (datos[4] << 8) | datos[5];
    const envuelta = datos.subarray(6, 6 + lk), iv = datos.subarray(6 + lk, 18 + lk), cuerpo = datos.subarray(18 + lk);
    const crudo = await crypto.subtle.decrypt({ name: "RSA-OAEP" }, llave, envuelta);
    const aes = await crypto.subtle.importKey("raw", crudo, "AES-GCM", false, ["decrypt"]);
    const plano = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, aes, cuerpo);
    return new Response(plano, { status: 200, headers: { "Content-Type": tipoDe(url.pathname), "Cache-Control": "no-store" } });
  } catch(e){
    return sinAcceso(pedido, "No se pudo abrir el archivo: la llave de este navegador no es la de los archivos. Volvé a entrar a la página.");
  }
}

function sinAcceso(pedido, texto){
  if(pedido.mode !== "navigate") return new Response(texto, { status: 403, headers: { "Content-Type": "text/plain; charset=utf-8" } });
  const raiz = new URL("./", self.registration.scope).href;
  const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Necesitás acceso</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;font:16px system-ui,sans-serif;background:#faf9f5;color:#1f1e1d;padding:16px}
.c{max-width:400px;text-align:center;background:#fff;border:1px solid #e8e6dc;border-radius:16px;padding:28px}h1{font:500 1.5rem Georgia,serif;margin:0 0 10px}p{color:#6b6a64;line-height:1.5}
a{display:inline-block;margin-top:8px;background:#2d8992;color:#fff;text-decoration:none;padding:10px 18px;border-radius:10px}
@media (prefers-color-scheme:dark){body{background:#262624;color:#f5f4ef}.c{background:#30302e;border-color:#3d3d3a}p{color:#a8a69e}}</style></head>
<body><div class="c"><h1>Necesitás acceso</h1><p>${texto}</p><a href="${raiz}">Ir a la página</a></div></body></html>`;
  return new Response(html, { status: 403, headers: { "Content-Type": "text/html; charset=utf-8" } });
}
