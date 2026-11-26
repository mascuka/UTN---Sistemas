/* Abrir el preenunciado de cualquier parcial: lee un ZIP (sin internet: DecompressionStream del navegador, o de Node),
   encuentra el proyecto adentro (la carpeta del pom.xml, o la que tiene src/main/java), su código, su main, el CSV que
   usa por defecto y los demás datos; y compara la salida del main con los números que da un enunciado.
   Uso: Proyecto.leerZip(bytes) → {ruta: bytes} · Proyecto.elegir(archivos, nombreZip) → { nombre, raiz, fuentes, datos, … } */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica();
  else raiz.Proyecto = fabrica();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  async function inflar(bytes) {
    const ds = new DecompressionStream('deflate-raw');
    return new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(ds)).arrayBuffer());
  }
  async function leerZip(buf) {
    if (!(buf instanceof Uint8Array)) buf = new Uint8Array(buf);
    const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
    let fin = buf.length - 22;
    while (fin >= 0 && dv.getUint32(fin, true) !== 0x06054b50) fin--;
    if (fin < 0) throw new Error('No es un archivo ZIP (si es un RAR o un 7z, descomprimilo y volvé a comprimirlo como ZIP).');
    if (typeof DecompressionStream === 'undefined') throw new Error('Este navegador no sabe descomprimir ZIP: probá con Chrome, Edge o Firefox actualizados.');
    const n = dv.getUint16(fin + 10, true);
    let p = dv.getUint32(fin + 16, true);
    const out = {};
    for (let i = 0; i < n; i++) {
      if (dv.getUint32(p, true) !== 0x02014b50) throw new Error('El ZIP está dañado.');
      const metodo = dv.getUint16(p + 10, true), comp = dv.getUint32(p + 20, true), lnom = dv.getUint16(p + 28, true), lext = dv.getUint16(p + 30, true), lcom = dv.getUint16(p + 32, true), off = dv.getUint32(p + 42, true);
      const nombre = decodificar(buf.subarray(p + 46, p + 46 + lnom));
      p += 46 + lnom + lext + lcom;
      if (nombre.endsWith('/') || /(^|\/)__MACOSX\//.test(nombre) || /(^|\/)\.DS_Store$/.test(nombre)) continue;
      const ini = off + 30 + dv.getUint16(off + 26, true) + dv.getUint16(off + 28, true);
      const datos = buf.subarray(ini, ini + comp);
      if (metodo === 0) out[nombre] = datos;
      else if (metodo === 8) out[nombre] = await inflar(datos);
      // otros métodos (raros): se ignoran
    }
    return out;
  }
  // Texto: UTF-8; si no lo es (archivos de Windows con tildes), Windows-1252
  function decodificar(bytes) {
    if (typeof bytes === 'string') return bytes;
    try { return new TextDecoder('utf-8', { fatal: true }).decode(bytes).replace(/^﻿/, ''); }
    catch (e) { return new TextDecoder('windows-1252').decode(bytes); }
  }

  /* De todo lo que trae el ZIP, el proyecto del preenunciado: se prefiere la carpeta de un pom.xml que no sea de un
     enunciado ni de una solución; si no hay pom.xml, la que tiene src/main/java. */
  function elegir(archivos, nombreZip) {
    const rutas = Object.keys(archivos).filter(r => !/(^|\/)(target|\.git|\.idea|\.vscode|out|bin)\//.test(r));
    // la solución va última; el enunciado del parcial, después del preenunciado («Preenunciado» también dice «enunciado»)
    const otraCosa = r => /soluci|resuelt|propuesta|respuesta/i.test(r) ? 2 : /pre-?enunciado|pre-?parcial|modelo-inicial/i.test(r) ? 0 : /enunciado|parcial/i.test(r) ? 1 : 0;
    let raices = rutas.filter(r => /(^|\/)pom\.xml$/.test(r)).map(r => r.slice(0, r.length - 'pom.xml'.length));
    if (!raices.length) raices = [...new Set(rutas.filter(r => /(^|\/)src\/main\/java\//.test(r)).map(r => r.slice(0, r.search(/src\/main\/java\//))))];
    if (!raices.length) {
      const sueltos = rutas.filter(r => r.endsWith('.java'));
      if (!sueltos.length) throw new Error('No encontré código Java en el ZIP (ni pom.xml ni carpeta src/main/java).');
      raices = [''];
    }
    raices = raices.filter(rz => rutas.some(r => r.startsWith(rz) && r.endsWith('.java') && !/\/src\/test\//.test('/' + r.slice(rz.length))));
    if (!raices.length) throw new Error('Encontré un pom.xml, pero ningún archivo .java del programa.');
    raices.sort((a, b) => (otraCosa(a) - otraCosa(b)) || a.split('/').length - b.split('/').length || a.length - b.length);
    const rz = raices[0];
    const fuentes = {}, datos = {}, tests = {}, documentos = {};
    for (const r of rutas) {
      if (!r.startsWith(rz)) continue;
      const rel = r.slice(rz.length);
      if (/\.java$/.test(rel)) { if (/(^|\/)src\/test\//.test(rel)) tests[rel] = decodificar(archivos[r]); else if (!/(^|\/)src\/main\/resources\//.test(rel)) fuentes[rel] = decodificar(archivos[r]); }
      else if (/\.(csv|txt|tsv|dat|json)$/i.test(rel)) datos[rel] = decodificar(archivos[r]);
    }
    for (const r of rutas) if (/\.(md|pdf)$/i.test(r) && !/(^|\/)(README|LICENSE)/i.test(r)) documentos[r] = archivos[r];
    // el main y el CSV que usa por defecto
    const conMain = Object.entries(fuentes).filter(([, t]) => /static\s+void\s+main\s*\(\s*(final\s+)?String/.test(t));
    if (!conMain.length) throw new Error('El proyecto no tiene ninguna clase con «public static void main(String[] args)».');
    conMain.sort((a, b) => (/Menu|Prueba|Test/i.test(a[0]) - /Menu|Prueba|Test/i.test(b[0])) || (/(App|Main)\.java$/.test(b[0]) - /(App|Main)\.java$/.test(a[0])));
    const [archivoMain, textoMain] = conMain[0];
    const paquete = (textoMain.match(/^\s*package\s+([\w.]+)\s*;/m) || [])[1];
    const claseMain = (paquete ? paquete + '.' : '') + archivoMain.split('/').pop().replace(/\.java$/, '');
    let csv = null;
    const lit = textoMain.match(/"([^"\n]*\.(?:csv|txt))"/);
    const partes = textoMain.match(/Path(?:s)?\.(?:of|get)\(\s*"([^"]+)"\s*,\s*"([^"]+\.(?:csv|txt))"\s*\)/);
    if (partes) csv = partes[1] + '/' + partes[2];
    else if (lit) csv = lit[1];
    if (!csv || !(csv.replace(/^\.\//, '') in datos)) csv = Object.keys(datos).find(r => /datos\.csv$/i.test(r)) || Object.keys(datos).find(r => /\.csv$/i.test(r)) || csv;
    const nombre = nombreDe(rz, nombreZip, archivos, rutas);
    const pom = rutas.includes(rz + 'pom.xml') ? decodificar(archivos[rz + 'pom.xml']) : null;
    return { nombre, raiz: rz, fuentes, datos, tests, documentos, pom, main: claseMain, archivoMain, csv: csv && csv.replace(/^\.\//, ''), usaArgs: /args\s*\[\s*0\s*\]/.test(textoMain) };
  }
  function nombreDe(rz, nombreZip, archivos, rutas) {
    const pom = rutas.find(r => r === rz + 'pom.xml');
    const carpetas = rz.split('/').filter(Boolean).filter(x => !/^0?\d+\s*-\s*(pre)?enunciado$|^01-modelo-inicial$|^modelo-inicial$|^preenunciado$|^0?\d+$/i.test(x));
    if (carpetas.length) return carpetas[0].replace(/^\d+\s*-\s*/, '');
    const clases = rutas.filter(r => r.startsWith(rz) && /src\/main\/.*\.java$/.test(r)).map(r => r.split('/').pop().replace(/\.java$/, ''))
      .filter(c => !/^(App|Main|Menu\w*|Parser\w*|Resultado\w*|Error\w*|Lector\w*)$/.test(c));
    if (clases.length) return clases.slice(0, 2).join(' · ');
    if (pom) { const t = decodificar(archivos[pom]); const m = t.match(/<name>([^<]+)<\/name>/) || t.match(/<artifactId>([^<]+)<\/artifactId>/); if (m) return m[1].trim(); }
    return (nombreZip || 'Preenunciado').replace(/\.zip$/i, '');
  }

  /* ¿La salida del main da los números de referencia del enunciado? Busca cada número al lado de su palabra
     («Leídas: 60», «procesadas=54», «Inválidas 15», «NORTE: 11200»), sin importar el formato del proyecto. */
  const sinTildes = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '');
  function chequear(salida, ref) {
    const t = sinTildes(salida || '');
    const buscar = re => { const m = t.match(re); return m ? Number(m[1].replace(/[.,](?=\d{3}\b)/g, '')) : null; };
    const items = [];
    const par = (nombre, esperado, re) => { if (esperado != null) items.push([nombre, esperado, buscar(re)]); };
    par('leídas', ref.leidas, /le[ií]das?\W{0,4}(\d+(?:[.,]\d{3})*)/i);
    par('procesadas', ref.procesadas, /procesad[oa]s?\W{0,4}(\d+(?:[.,]\d{3})*)/i);
    par('descartadas', ref.descartadas, /descartad[oa]s?\W{0,4}(\d+(?:[.,]\d{3})*)/i);
    par('inválidas', ref.invalidas, /invalid[oa]s?\W{0,4}(\d+(?:[.,]\d{3})*)/i);
    if (ref.total != null) par('total', ref.total, /total[^\d\n]{0,40}?(\d+(?:[.,]\d{3})*)/i);
    for (const [z, n] of ref.zonas || []) par(z, n, new RegExp('(?:^|[^\\w-])' + z.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\W{1,4}(\\d+(?:[.,]\\d{3})*)'));
    return items.map(([nombre, esperado, da]) => ({ nombre, esperado, da, ok: da === esperado }));
  }

  return { leerZip, elegir, decodificar, chequear };
});
