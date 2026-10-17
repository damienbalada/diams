// Audit des libellés de fiche : calcule le libellé de chaque preuve active (export JSON passé en
// argument) et liste, par indicateur, les libellés distincts avec un exemple d'extrait, pour repérer
// ceux qui ne disent pas ce que dit la source. Lecture seule. Usage :
//   node --experimental-strip-types apps/web/lib/audit-libelles.mts preuves.json [CODE…]
import { readFileSync } from "node:fs";
import { valeurCourte, type PreuveEntree } from "./carte.ts";

const [fichier, ...codes] = process.argv.slice(2);
const preuves = JSON.parse(readFileSync(fichier, "utf-8")) as Array<Record<string, unknown>>;
const parCode = new Map<string, Map<string, { n: number; ex: string; slug: string }>>();
for (const p of preuves) {
  const code = String(p.code);
  if (codes.length && !codes.includes(code)) continue;
  const entree = { indicator_code: code, tier: "regulatory", specificity: 0, source_url: "", source_name: "", ...p } as unknown as PreuveEntree;
  // Valeur réduite à sa forme : les chiffres sont remplacés pour regrouper les libellés semblables.
  const lib = valeurCourte(code, (p.unit as string) ?? null, entree);
  const forme = lib.replace(/[\d  ,.]+/g, "#");
  const m = parCode.get(code) ?? new Map();
  const e = m.get(forme) ?? { n: 0, ex: "", slug: "" };
  e.n++; if (!e.ex) { e.ex = String(p.excerpt ?? "").slice(0, 160); e.slug = String(p.slug); }
  m.set(forme, e); parCode.set(code, m);
}
for (const [code, m] of [...parCode].sort()) {
  console.log(`### ${code}`);
  for (const [forme, e] of [...m].sort((a, b) => b[1].n - a[1].n)) console.log(`  ${String(e.n).padStart(4)}  ${forme}   ← ${e.slug} : ${e.ex}`);
}
