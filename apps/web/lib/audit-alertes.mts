// Audit des alertes : calcule l'alerte ou la vigilance de chaque preuve active (export JSON) et liste,
// par indicateur, les messages distincts avec un exemple, pour repérer un seuil appliqué à tort.
// Lecture seule. Usage : node --experimental-strip-types apps/web/lib/audit-alertes.mts preuves.json
import { readFileSync } from "node:fs";
import { evaluer } from "./seuils.ts";

const preuves = JSON.parse(readFileSync(process.argv[2], "utf-8")) as Array<Record<string, unknown>>;
const parCode = new Map<string, Map<string, { n: number; ex: string }>>();
for (const p of preuves) {
  const code = String(p.code);
  const s = evaluer({ code, etat: "documente", valeurNum: (p.value_numeric as number | null) ?? null, citation: String(p.excerpt ?? "") } as never);
  if (!s) continue;
  const forme = `${s.niveau} · ${s.motif.replace(/[\d  ,.]+/g, "#")}`;
  const m = parCode.get(code) ?? new Map();
  const e = m.get(forme) ?? { n: 0, ex: "" };
  e.n++; if (!e.ex) e.ex = `${p.slug} : ${String(p.excerpt ?? "").slice(0, 140)}`;
  m.set(forme, e); parCode.set(code, m);
}
for (const [code, m] of [...parCode].sort()) {
  console.log(`### ${code}`);
  for (const [forme, e] of [...m].sort((a, b) => b[1].n - a[1].n)) console.log(`  ${String(e.n).padStart(4)}  ${forme}   ← ${e.ex}`);
}
