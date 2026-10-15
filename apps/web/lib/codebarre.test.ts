import { test } from "node:test";
import assert from "node:assert/strict";
import { codeValide, normaliser, rapprocher, type EntiteNom } from "./codebarre.ts";

const E: EntiteNom[] = [
  { slug: "president", noms: ["Président"], is_brand: true },
  { slug: "lactalis", noms: ["Lactalis", "Groupe Lactalis"], is_brand: false },
  { slug: "nutella", noms: ["Nutella"], is_brand: true },
  { slug: "ferrero", noms: ["Ferrero"], is_brand: false },
  { slug: "coca-cola-marque", noms: ["Coca-Cola"], is_brand: true },
  { slug: "coca-cola", noms: ["Coca-Cola (groupe)", "The Coca-Cola Company"], is_brand: false },
  { slug: "bio-village", noms: ["Bio Village"], is_brand: true },
];

test("normalisation : accents, casse, symboles", () => {
  assert.equal(normaliser("PRÉSIDENT®"), "president");
  assert.equal(normaliser("L’Oréal"), "loreal");
  assert.equal(normaliser("Ben & Jerry's"), "ben et jerrys");
});

test("codes-barres plausibles", () => {
  assert.ok(codeValide("3228020481471"));
  assert.ok(codeValide("12345678"));
  assert.ok(!codeValide("1234"));
  assert.ok(!codeValide("32280204814a1"));
});

test("rapprochement exact, la première marque citée d'abord, la marque avant le groupe", () => {
  assert.deepEqual(rapprocher(["President"], E), { slug: "president", correspondance: "exacte", nomLu: "President" });
  assert.equal(rapprocher(["Nutella, Ferrero"], E)?.slug, "nutella");
  assert.equal(rapprocher(["Ferrero"], E)?.slug, "ferrero");
});

test("rapprochement approché : le nom lu commence par une marque connue", () => {
  const r = rapprocher(["COCA-COLA SERVICES SA/NV"], E);
  assert.equal(r?.slug, "coca-cola-marque");
  assert.equal(r?.correspondance, "approchee");
});

test("rien de sûr : null, et jamais sur un mot générique", () => {
  assert.equal(rapprocher(["Marque inconnue"], E), null);
  assert.equal(rapprocher(["Bio"], E), null);
  assert.equal(rapprocher([], E), null);
});

test("marque non saisie : le début du nom du produit ; marque absente : le propriétaire déclaré", () => {
  const E2: EntiteNom[] = [...E, { slug: "unilever", noms: ["Unilever"], is_brand: false }];
  assert.deepEqual(rapprocher([], E2, { nomProduit: "coca-cola" }), { slug: "coca-cola-marque", correspondance: "approchee", nomLu: "coca-cola" });
  assert.deepEqual(rapprocher(["Marmite"], E2, { proprietaire: "Unilever UK" }), { slug: "unilever", correspondance: "proprietaire", nomLu: "Unilever UK", marqueNonSuivie: "Marmite" });
  assert.deepEqual(rapprocher(["Marmite, Unilever"], E2), { slug: "unilever", correspondance: "proprietaire", nomLu: "Unilever", marqueNonSuivie: "Marmite" });
  assert.equal(rapprocher(["Marmite"], E2, { proprietaire: "" }), null);
});

test("raison sociale longue : le groupe ; nom exact : la marque", () => {
  const E3: EntiteNom[] = [{ slug: "danone", noms: ["Danone"], is_brand: false }, { slug: "danone-produits-laitiers", noms: ["Danone (produits laitiers)", "Danone"], is_brand: true }];
  assert.equal(rapprocher(["Danone Belux nv"], E3)?.slug, "danone");
  assert.equal(rapprocher(["Danone"], E3)?.slug, "danone-produits-laitiers");
});
