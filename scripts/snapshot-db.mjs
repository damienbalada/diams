// Instantané versionné des DONNÉES de la base de production.
//
// Pourquoi : la base est la source de vérité opérationnelle (connecteurs,
// curation), mais une donnée qui n'existe qu'en base n'est ni rejouable ni
// auditable. Ce script écrit `supabase/seed/99_snapshot.sql` : l'état complet des
// référentiels, entités et preuves, en upsert sur clés naturelles (slug / code),
// idempotent, déterministe (trié, sans horodatage).
//
//   node scripts/snapshot-db.mjs            # régénère le fichier depuis la base
//   node scripts/snapshot-db.mjs --check    # échoue (exit 1) si base ≠ fichier
//
// Identifiants : SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (env ou pipeline/.env).
// Exclus volontairement : `corrections` (signalements de lecteurs, contiennent
// des coordonnées) et les tables de staging du pipeline marques.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(root, "supabase/seed/99_snapshot.sql");
const CHECK = process.argv.includes("--check");

function loadEnv() {
  const env = { ...process.env };
  const file = join(root, "pipeline/.env");
  if (existsSync(file)) {
    for (const line of readFileSync(file, "utf8").split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z_]+)\s*=\s*(.*)\s*$/);
      if (m && !env[m[1]]) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  }
  if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY) {
    console.error("SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY requis (env ou pipeline/.env).");
    process.exit(2);
  }
  return env;
}

const env = loadEnv();
const headers = {
  apikey: env.SUPABASE_SERVICE_ROLE_KEY,
  Authorization: `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
};

async function fetchAll(table) {
  const rows = [];
  const page = 1000;
  for (let offset = 0; ; offset += page) {
    const res = await fetch(`${env.SUPABASE_URL}/rest/v1/${table}?select=*&limit=${page}&offset=${offset}`, { headers });
    if (!res.ok) throw new Error(`${table} : HTTP ${res.status} ${await res.text()}`);
    const batch = await res.json();
    rows.push(...batch);
    if (batch.length < page) return rows;
  }
}

// --- Littéraux SQL -----------------------------------------------------------
const lit = (v) => {
  if (v === null || v === undefined) return "null";
  if (typeof v === "boolean") return v ? "true" : "false";
  if (typeof v === "number") return String(v);
  return `'${String(v).replace(/'/g, "''")}'`;
};
const ref = (table, key, value) =>
  value === null || value === undefined ? "null" : `(select id from ${table} where ${key} = ${lit(value)})`;
const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

/**
 * Upsert multi-lignes. `cols` : colonnes cibles ; `conflict` : clé naturelle
 * (colonnes de l'index unique) ; les autres colonnes sont mises à jour.
 */
function upsert(table, cols, conflict, tuples) {
  if (tuples.length === 0) return `-- ${table} : aucune ligne.\n`;
  const updates = cols.filter((c) => !conflict.includes(c));
  const set = updates.length
    ? `do update set\n  ${updates.map((c) => `${c} = excluded.${c}`).join(",\n  ")}`
    : "do nothing";
  return (
    `insert into ${table} (${cols.join(", ")}) values\n` +
    tuples.map((t) => `  (${t.join(", ")})`).join(",\n") +
    `\non conflict (${conflict.join(", ")}) ${set};\n`
  );
}

// --- Génération --------------------------------------------------------------
async function build() {
  const T = {};
  for (const t of [
    "sectors", "dimensions", "dimension_groups", "dimension_group_members", "indicators",
    "dimension_gates", "sources", "source_tier_config", "evidence_nature_config", "scoring_params",
    "value_profiles", "profile_weights", "entities", "evidence", "political_groups",
    "civic_votes", "civic_positions", "disclosure_regimes", "indicator_regimes", "entity_regimes",
    "indicator_sectors", "sector_dimension_weights", "obligation_exemptions",
  ]) T[t] = await fetchAll(t);

  const code = (rows, field = "code") => new Map(rows.map((r) => [r.id, r[field]]));
  const sector = code(T.sectors);
  const dim = code(T.dimensions);
  const dgroup = code(T.dimension_groups);
  const ind = code(T.indicators);
  const src = code(T.sources);
  const prof = code(T.value_profiles);
  const ent = code(T.entities, "slug");
  const vote = code(T.civic_votes);
  const pgroup = code(T.political_groups);
  const regime = code(T.disclosure_regimes);
  const by = (f) => (a, b) => cmp(f(a), f(b));

  const parts = [];
  const section = (title, sql) => parts.push(`-- ${title}\n${sql}`);

  section("Secteurs", upsert("sectors",
    ["code", "name", "description", "animal_relevant", "wap_relevant", "inv_relevant", "plastic_relevant", "water_relevant"], ["code"],
    [...T.sectors].sort(by((r) => r.code)).map((r) =>
      [r.code, r.name, r.description, r.animal_relevant, r.wap_relevant, r.inv_relevant, r.plastic_relevant, r.water_relevant].map(lit))));

  section("Piliers (dimensions)", upsert("dimensions",
    ["code", "name", "description", "default_weight", "display_order"], ["code"],
    [...T.dimensions].sort(by((r) => r.code)).map((r) =>
      [r.code, r.name, r.description, r.default_weight, r.display_order].map(lit))));

  section("Méta-scores", upsert("dimension_groups",
    ["code", "name", "description", "display_order"], ["code"],
    [...T.dimension_groups].sort(by((r) => r.code)).map((r) =>
      [r.code, r.name, r.description, r.display_order].map(lit))));

  section("Membres des méta-scores", upsert("dimension_group_members",
    ["group_id", "dimension_id", "weight"], ["group_id", "dimension_id"],
    [...T.dimension_group_members].sort(by((r) => `${dgroup.get(r.group_id)}|${dim.get(r.dimension_id)}`)).map((r) =>
      [ref("dimension_groups", "code", dgroup.get(r.group_id)), ref("dimensions", "code", dim.get(r.dimension_id)), lit(r.weight)])));

  section("Indicateurs", upsert("indicators",
    ["code", "dimension_id", "name", "kind", "direction", "sector_specific", "applies_to_sector_id", "weight", "unit", "methodology", "presence_only", "jurisdiction", "complementary", "group_level", "disclosure"], ["code"],
    [...T.indicators].sort(by((r) => r.code)).map((r) => [
      lit(r.code), ref("dimensions", "code", dim.get(r.dimension_id)), lit(r.name), lit(r.kind), lit(r.direction),
      lit(r.sector_specific), ref("sectors", "code", sector.get(r.applies_to_sector_id)), lit(r.weight), lit(r.unit), lit(r.methodology),
      lit(r.presence_only), lit(r.jurisdiction), lit(r.complementary ?? false), lit(r.group_level ?? false), lit(r.disclosure ?? false),
    ])));

  section("Pertinence sectorielle par liste", upsert("indicator_sectors",
    ["indicator_id", "sector_id"], ["indicator_id", "sector_id"],
    [...T.indicator_sectors].sort(by((r) => `${ind.get(r.indicator_id)}|${sector.get(r.sector_id)}`)).map((r) =>
      [ref("indicators", "code", ind.get(r.indicator_id)), ref("sectors", "code", sector.get(r.sector_id))])));

  section("Matérialité sectorielle", upsert("sector_dimension_weights",
    ["sector_id", "dimension_id", "multiplier", "note"], ["sector_id", "dimension_id"],
    [...T.sector_dimension_weights].sort(by((r) => `${sector.get(r.sector_id)}|${dim.get(r.dimension_id)}`)).map((r) =>
      [ref("sectors", "code", sector.get(r.sector_id)), ref("dimensions", "code", dim.get(r.dimension_id)), lit(r.multiplier), lit(r.note)])));

  section("Gates (plafonds de pilier)", upsert("dimension_gates",
    ["dimension_id", "gate_indicator_id", "default_ceiling", "notes"], ["dimension_id"],
    [...T.dimension_gates].sort(by((r) => dim.get(r.dimension_id))).map((r) => [
      ref("dimensions", "code", dim.get(r.dimension_id)), ref("indicators", "code", ind.get(r.gate_indicator_id)), lit(r.default_ceiling), lit(r.notes),
    ])));

  section("Sources", upsert("sources",
    ["code", "name", "tier", "publisher", "url", "description"], ["code"],
    [...T.sources].sort(by((r) => r.code)).map((r) => [r.code, r.name, r.tier, r.publisher, r.url, r.description].map(lit))));

  section("Config méthodo : tiers de source", upsert("source_tier_config",
    ["tier", "evidence_weight", "max_confidence", "can_penalize_alone", "min_score_floor_alone", "notes"], ["tier"],
    [...T.source_tier_config].sort(by((r) => r.tier)).map((r) =>
      [r.tier, r.evidence_weight, r.max_confidence, r.can_penalize_alone, r.min_score_floor_alone, r.notes].map(lit))));

  section("Config méthodo : nature des preuves", upsert("evidence_nature_config",
    ["nature", "score_multiplier", "max_score_without_result", "notes"], ["nature"],
    [...T.evidence_nature_config].sort(by((r) => r.nature)).map((r) =>
      [r.nature, r.score_multiplier, r.max_score_without_result, r.notes].map(lit))));

  section("Config méthodo : paramètres", upsert("scoring_params",
    ["key", "value", "description"], ["key"],
    [...T.scoring_params].sort(by((r) => r.key)).map((r) => [r.key, r.value, r.description].map(lit))));

  section("Profils de valeurs", upsert("value_profiles",
    ["code", "name", "description", "is_default"], ["code"],
    [...T.value_profiles].sort(by((r) => r.code)).map((r) => [r.code, r.name, r.description, r.is_default].map(lit))));

  section("Poids des profils", upsert("profile_weights",
    ["profile_id", "dimension_id", "weight"], ["profile_id", "dimension_id"],
    [...T.profile_weights].sort(by((r) => `${prof.get(r.profile_id)}|${dim.get(r.dimension_id)}`)).map((r) =>
      [ref("value_profiles", "code", prof.get(r.profile_id)), ref("dimensions", "code", dim.get(r.dimension_id)), lit(r.weight)])));

  const entities = [...T.entities].sort(by((r) => r.slug));
  section("Entités (résolution : identifiants officiels)", upsert("entities",
    ["slug", "legal_name", "display_name", "lei", "siren", "country", "sector_id", "is_brand", "animal_free"], ["slug"],
    entities.map((r) => [
      lit(r.slug), lit(r.legal_name), lit(r.display_name), lit(r.lei), lit(r.siren), lit(r.country),
      ref("sectors", "code", sector.get(r.sector_id)), lit(r.is_brand), lit(r.animal_free),
    ])));

  // Chaîne de détention en second temps : un parent inséré dans la même
  // instruction n'est pas encore visible d'une sous-requête.
  const links = entities.filter((r) => r.parent_id);
  section("Entités : chaîne de détention (marque → groupe)",
    links.length === 0 ? "-- aucune.\n" :
    `update entities e set parent_id = p.id, ownership_pct = v.pct\nfrom (values\n` +
    links.map((r) => `  (${lit(r.slug)}, ${lit(ent.get(r.parent_id))}, ${lit(r.ownership_pct)}::numeric)`).join(",\n") +
    `\n) as v(slug, parent_slug, pct)\njoin entities p on p.slug = v.parent_slug\n` +
    `where e.slug = v.slug and (e.parent_id is distinct from p.id or e.ownership_pct is distinct from v.pct);\n`);

  section("Obligations de publication : régimes (Règle 1)", upsert("disclosure_regimes",
    ["code", "name", "jurisdiction", "legal_basis", "scope", "url", "in_force_since"], ["code"],
    [...T.disclosure_regimes].sort(by((r) => r.code)).map((r) =>
      [r.code, r.name, r.jurisdiction, r.legal_basis, r.scope, r.url, r.in_force_since].map(lit))));

  section("Obligations : indicateurs rendus obligatoires", upsert("indicator_regimes",
    ["indicator_id", "regime_id", "note"], ["indicator_id", "regime_id"],
    [...T.indicator_regimes].sort(by((r) => `${regime.get(r.regime_id)}|${ind.get(r.indicator_id)}`)).map((r) =>
      [ref("indicators", "code", ind.get(r.indicator_id)), ref("disclosure_regimes", "code", regime.get(r.regime_id)), lit(r.note)])));

  section("Obligations : entités soumises (faits sourcés)", upsert("entity_regimes",
    ["entity_id", "regime_id", "basis", "source_url", "observed_on", "reviewer"], ["entity_id", "regime_id"],
    [...T.entity_regimes].sort(by((r) => `${ent.get(r.entity_id)}|${regime.get(r.regime_id)}`)).map((r) => [
      ref("entities", "slug", ent.get(r.entity_id)), ref("disclosure_regimes", "code", regime.get(r.regime_id)),
      lit(r.basis), lit(r.source_url), lit(r.observed_on), lit(r.reviewer),
    ])));

  section("Obligations levées : donnée déclarée non matérielle (faits cités, v0.7.3)", upsert("obligation_exemptions",
    ["entity_id", "indicator_id", "reason", "source_url", "excerpt"], ["entity_id", "indicator_id"],
    [...T.obligation_exemptions].sort(by((r) => `${ent.get(r.entity_id)}|${ind.get(r.indicator_id)}`)).map((r) => [
      ref("entities", "slug", ent.get(r.entity_id)), ref("indicators", "code", ind.get(r.indicator_id)),
      lit(r.reason), lit(r.source_url), lit(r.excerpt),
    ])));

  section("Preuves (evidence) — clé : entité + indicateur + source + date", upsert("evidence",
    ["entity_id", "indicator_id", "source_id", "observed_on", "value_type", "value_numeric", "value_boolean", "value_text",
     "normalized_value", "nature", "confidence", "reviewer", "review_status", "contested", "source_url", "excerpt"],
    ["entity_id", "indicator_id", "source_id", "observed_on"],
    [...T.evidence]
      .sort(by((r) => `${ent.get(r.entity_id)}|${ind.get(r.indicator_id)}|${src.get(r.source_id)}|${r.observed_on}`))
      .map((r) => [
        ref("entities", "slug", ent.get(r.entity_id)), ref("indicators", "code", ind.get(r.indicator_id)),
        ref("sources", "code", src.get(r.source_id)), lit(r.observed_on), lit(r.value_type), lit(r.value_numeric),
        lit(r.value_boolean), lit(r.value_text), lit(r.normalized_value), lit(r.nature), lit(r.confidence),
        lit(r.reviewer), lit(r.review_status), lit(r.contested), lit(r.source_url), lit(r.excerpt),
      ])));

  section("Module civique : groupes politiques", upsert("political_groups",
    ["code", "name", "short_name", "chamber", "seats", "ordinal"], ["code"],
    [...T.political_groups].sort(by((r) => r.code)).map((r) => [r.code, r.name, r.short_name, r.chamber, r.seats, r.ordinal].map(lit))));

  section("Module civique : votes", upsert("civic_votes",
    ["code", "title", "vote_date", "pillar_code", "chamber", "source_url", "alignment_note", "total_for", "total_against", "total_abstain"], ["code"],
    [...T.civic_votes].sort(by((r) => r.code)).map((r) =>
      [r.code, r.title, r.vote_date, r.pillar_code, r.chamber, r.source_url, r.alignment_note, r.total_for, r.total_against, r.total_abstain].map(lit))));

  section("Module civique : positions par groupe", upsert("civic_positions",
    ["vote_id", "group_id", "stance", "n_for", "n_against", "n_abstain", "note", "source_url"], ["vote_id", "group_id"],
    [...T.civic_positions].sort(by((r) => `${vote.get(r.vote_id)}|${pgroup.get(r.group_id)}`)).map((r) => [
      ref("civic_votes", "code", vote.get(r.vote_id)), ref("political_groups", "code", pgroup.get(r.group_id)),
      lit(r.stance), lit(r.n_for), lit(r.n_against), lit(r.n_abstain), lit(r.note), lit(r.source_url),
    ])));

  const counts = Object.entries(T).map(([t, rows]) => `--   ${t.padEnd(24)} ${rows.length}`).join("\n");
  const header =
    `-- =============================================================================\n` +
    `-- Seed 99 : INSTANTANÉ des données de production (généré — ne pas éditer).\n` +
    `-- -----------------------------------------------------------------------------\n` +
    `-- Régénérer : node scripts/snapshot-db.mjs   ·   Vérifier : --check\n` +
    `-- Upsert sur clés naturelles (slug / code) : idempotent. Reconstruction d'une\n` +
    `-- base = migrations puis ce fichier, rien d'autre (les seeds de history/ sont\n` +
    `-- périmés). Exclus : corrections (données de lecteurs).\n` +
    `-- Lignes :\n${counts}\n` +
    `-- =============================================================================\n\n` +
    `begin;\n\n`;
  return header + parts.join("\n") + `\ncommit;\n`;
}

const sql = await build();
if (CHECK) {
  const current = existsSync(OUT) ? readFileSync(OUT, "utf8").replace(/\r\n/g, "\n") : "";
  if (current === sql) {
    console.log("Base ↔ 99_snapshot.sql : identiques ✓");
  } else {
    const a = new Set(current.split("\n"));
    const b = new Set(sql.split("\n"));
    const onlyDb = [...b].filter((l) => !a.has(l));
    const onlyFile = [...a].filter((l) => !b.has(l));
    console.error(`DÉRIVE : la base diffère du fichier versionné (${onlyDb.length} ligne(s) en base seulement, ${onlyFile.length} dans le fichier seulement).`);
    for (const l of onlyDb.slice(0, 10)) console.error(`  + ${l.slice(0, 160)}`);
    for (const l of onlyFile.slice(0, 10)) console.error(`  - ${l.slice(0, 160)}`);
    console.error("→ Si le changement est voulu : node scripts/snapshot-db.mjs puis commit.");
    process.exit(1);
  }
} else {
  writeFileSync(OUT, sql);
  console.log(`99_snapshot.sql écrit (${sql.length} octets).`);
}
