import { test } from "node:test";
import assert from "node:assert/strict";
import { alternativesParPilier, type EntiteAlt } from "./alternatives-piliers.ts";

const e = (id: string, parent: string | null, sector = "food", is_brand = true): EntiteAlt =>
  ({ id, slug: id, nom: id.toUpperCase(), is_brand, parent_id: parent, sector_id: sector });

test("alternatives : même rayon, autre groupe, critère hérité du groupe", () => {
  const rows = [e("g1", null, "food", false), e("moi", "g1"), e("soeur", "g1"), e("g2", null, "food", false), e("b2", "g2"), e("b3", "g2", "beauty"), e("vege", null)];
  const a = alternativesParPilier(rows, "moi", { ENV: new Set(["g2", "g1"]), ANI: new Set(["vege"]) }, { ANI: new Set(["b2"]) });
  assert.deepEqual(a.ENV.marques.map((m) => m.slug), ["b2"]);          // la sœur du même groupe et l'autre rayon sont exclus
  assert.equal(a.ENV.marques[0].groupe, "G2");
  assert.deepEqual(a.ANI.marques.map((m) => [m.slug, !!m.second]), [["vege", false], ["b2", true]]);
  assert.equal(a.PLA, undefined);
});
