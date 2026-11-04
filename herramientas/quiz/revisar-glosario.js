// Revisa la lamparita de los quiz: que cada quiz tenga "glosario", que cada pregunta encuentre al menos un término
// (con la misma búsqueda que la página: enunciado, código, opciones y líneas de armar) y que no sobren términos.
// Uso, desde la raíz:  node herramientas/quiz/revisar-glosario.js [quiz/archivo.json ...]   (sin archivos: todos los de quiz/)
const fs = require('fs'), path = require('path');
const RAIZ = path.join(__dirname, '..', '..');
const archivos = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(path.join(RAIZ, 'quiz')).filter(f => f.endsWith('.json')).map(f => path.join('quiz', f));
const sinEtiquetas = h => String(h || '').replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ');
let problemas = 0;
for (const a of archivos) {
  const d = JSON.parse(fs.readFileSync(path.isAbsolute(a) ? a : path.join(RAIZ, a), 'utf8'));
  const G = d.glosario || [];
  if (!G.length) { console.log(`✗ ${a}: no tiene glosario (no va a mostrar la lamparita)`); problemas++; continue; }
  const rx = G.map(g => { try { return new RegExp(g.re, g.i ? 'i' : ''); } catch (e) { console.log(`✗ ${a}: la expresión de «${g.t}» no anda: ${e.message}`); problemas++; return null; } });
  const usados = new Set(), sin = [];
  let total = 0, max = 0;
  for (const s of d.secciones) for (const q of s.preguntas) {
    total++;
    const txt = [q.en, q.code, ...(q.op || []).map(o => o[0]), ...(q.objetivo || []), ...(q.huecos || []), ...(q.fichas || [])].map(sinEtiquetas).join('\n');
    const t = G.filter((g, k) => rx[k] && txt.search(rx[k]) >= 0);
    t.forEach(g => usados.add(g.t));
    max = Math.max(max, t.length);
    if (!t.length) sin.push(sinEtiquetas(q.en).replace(/\s+/g, ' ').trim().slice(0, 90));
  }
  const nunca = G.filter(g => !usados.has(g.t)).map(g => g.t);
  console.log(`${sin.length || nunca.length ? '✗' : '✓'} ${a}: ${total} preguntas, ${G.length} términos, hasta ${max} por pregunta (se muestran 8)`);
  sin.forEach(x => console.log(`    sin términos: ${x}`));
  if (nunca.length) console.log(`    términos que no usa ninguna: ${nunca.join(' · ')}`);
  problemas += sin.length + nunca.length;
}
process.exit(problemas ? 1 : 0);
