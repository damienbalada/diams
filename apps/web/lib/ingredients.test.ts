import { test } from "node:test";
import assert from "node:assert/strict";
import { analyserIngredients } from "./ingredients.ts";

test("ingrédients animaux repérés, hors traces et « sans »", () => {
  const a = analyserIngredients("Farine de blé 27 %, beurre (LAIT) 4,3 %, œufs entiers, oeuf en poudre, sel. Peut contenir des traces de poisson.");
  assert.deepEqual(a.animaux, ["beurre", "lait", "œufs"]);
  assert.equal(a.statut, "ingredient_animal");
});

test("lait végétal, beurre de cacao et « sans lactose » ne comptent pas", () => {
  const a = analyserIngredients("Lait d'amande (eau, amandes 2,8 %), sucre, beurre de cacao, sel. Sans lactose.");
  assert.deepEqual(a.animaux, []);
  assert.equal(a.statut, "aucun_ingredient_animal_declare");
});

test("ingrédients douteux signalés sans conclure", () => {
  const a = analyserIngredients("Sucre, sirop de glucose, arôme naturel, colorant : E120.");
  assert.deepEqual(a.animaux, ["e120"]);
  assert.ok(a.douteux.includes("arôme naturel"));
});
