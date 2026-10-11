// Tests du classement par secteur (logique pure).
// Lancer : node --test --experimental-strip-types apps/web/lib/ranking.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { onePerGroup, rankBySector, sectorAnchor, type RankRow, type SectorInfo } from "./ranking.ts";

const SECTORS: SectorInfo[] = [
  { id: "bank", code: "banking_finance", name: "Banque & Finance" },
  { id: "bev", code: "beverages", name: "Boissons" },
  { id: "food", code: "food", name: "Agroalimentaire" },
];

function row(slug: string, sector_id: string | null, score: number, extra: Partial<RankRow> = {}): RankRow {
  return {
    slug, name: slug, is_brand: false, group: null, grade: "C", score, confidence: 0.4,
    publishable: true, last_observed: null, sector_id, ...extra,
  };
}

test("classement — jamais deux secteurs dans le même tableau", () => {
  const { ranked } = rankBySector([row("lbp", "bank", 0.77), row("coca", "bev", 0.57), row("sg", "bank", 0.55)], SECTORS);
  const bank = ranked.find((s) => s.sector.id === "bank")!;
  assert.deepEqual(bank.groups.map((r) => r.slug), ["lbp", "sg"]);
  assert.deepEqual(ranked.find((s) => s.sector.id === "bev")!.groups.map((r) => r.slug), ["coca"]);
});

test("classement — groupes et marques séparés dans un secteur", () => {
  const { ranked } = rankBySector([row("bnp", "bank", 0.6), row("hello", "bank", 0.9, { is_brand: true })], SECTORS);
  assert.deepEqual(ranked[0].groups.map((r) => r.slug), ["bnp"]);
  assert.deepEqual(ranked[0].brands.map((r) => r.slug), ["hello"]);
});

test("classement — tri par note puis fiabilité ; secteurs les plus fournis d'abord", () => {
  const { ranked } = rankBySector([
    row("a", "bank", 0.5, { confidence: 0.3 }), row("b", "bank", 0.5, { confidence: 0.6 }), row("c", "bank", 0.7),
    row("coca", "bev", 0.57),
  ], SECTORS);
  assert.equal(ranked[0].sector.id, "bank");
  assert.deepEqual(ranked[0].groups.map((r) => r.slug), ["c", "b", "a"]);
});

test("classement — non publiables comptés, secteurs sans publiable à part", () => {
  const { ranked, empty } = rankBySector([
    row("lbp", "bank", 0.77), row("nef", "bank", 0.98, { publishable: false }),
    row("danone", "food", 0.8, { publishable: false }),
  ], SECTORS);
  assert.equal(ranked[0].unranked, 1);
  assert.equal(ranked[0].groups.length, 1); // une note non publiable n'est jamais classée
  assert.deepEqual(empty.map((s) => s.sector.id), ["food"]);
  assert.equal(empty[0].unranked, 1);
});

test("classement — secteur inconnu regroupé, ancre stable", () => {
  const { ranked } = rankBySector([row("x", null, 0.5), row("y", "zzz", 0.4)], SECTORS);
  assert.equal(ranked.length, 1);
  assert.equal(ranked[0].sector.name, "Secteur non renseigné");
  assert.equal(sectorAnchor(SECTORS[0]), "secteur-banking_finance");
});

test("podium — une seule entité par groupe, la mieux notée", () => {
  const rows = [
    row("ariel", "food", 0.83, { is_brand: true, group: "P&G" }),
    row("pampers", "food", 0.82, { is_brand: true, group: "P&G" }),
    row("danone", "food", 0.7, { name: "Danone" }),
    row("evian", "food", 0.68, { is_brand: true, group: "Danone" }),
    row("pg", "food", 0.6, { name: "P&G" }),
  ].sort((a, b) => b.score - a.score);
  assert.deepEqual(onePerGroup(rows).map((r) => r.slug), ["ariel", "danone"]);
});
