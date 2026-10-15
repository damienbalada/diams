import { test } from "node:test";
import assert from "node:assert/strict";
import { evaluer } from "./seuils.ts";

const doc = (code: string, valeurNum: number | null, citation = "") => evaluer({ code, etat: "documente", valeurNum, citation });

test("transparence de la mode : Shein à 6,6 % est en alerte, 20 % en vigilance, 40 % sans signal", () => {
  assert.equal(doc("SUP_FTI_SCORE", 6.6)?.niveau, "alerte");
  assert.match(doc("SUP_FTI_SCORE", 6.6)!.motif, /6,6 %/);
  assert.equal(doc("SUP_FTI_SCORE", 20)?.niveau, "vigilance");
  assert.equal(doc("SUP_FTI_SCORE", 40), null);
});

test("Égapro : seuils légaux de 75 et 85", () => {
  assert.equal(doc("LAB_EGAPRO_INDEX", 74)?.niveau, "alerte");
  assert.equal(doc("LAB_EGAPRO_INDEX", 84)?.niveau, "vigilance");
  assert.equal(doc("LAB_EGAPRO_INDEX", 85), null);
});

test("émissions : hausse en alerte, baisse lente en vigilance", () => {
  assert.equal(doc("ENV_GHG_TREND", 23.05)?.niveau, "alerte");
  assert.equal(doc("ENV_GHG_TREND", -2)?.niveau, "vigilance");
  assert.equal(doc("ENV_GHG_TREND", -5), null);
});

test("notes lues dans la citation : CDP, salaire vital, Russie, SBTi", () => {
  assert.equal(doc("ENV_CDP_CLIMATE", null, "« X » — note F")?.niveau, "alerte");
  assert.equal(doc("WAT_CDP", null, "note D-")?.niveau, "vigilance");
  assert.equal(doc("WAT_CDP", null, "note B-"), null);
  assert.equal(doc("SUP_LIVING_WAGE", null, "note E : la marque ne verse")?.niveau, "alerte");
  assert.equal(doc("GEO_RUSSIA_EXIT", null, "— activité poursuivie en Russie ;")?.niveau, "alerte");
  assert.equal(doc("GEO_RUSSIA_EXIT", null, "— activité réduite ;")?.niveau, "vigilance");
  assert.equal(doc("GEO_RUSSIA_EXIT", null, "— sortie effective ;"), null);
  assert.equal(doc("ENV_SBTI_VALIDATED", null, "objectif de court terme : engagement retiré")?.niveau, "vigilance");
});

test("écart de salaire : en valeur absolue, dans les deux sens", () => {
  assert.equal(doc("LAB_GENDER_PAYGAP", -16)?.niveau, "alerte");
  assert.match(doc("LAB_GENDER_PAYGAP", -16)!.motif, /en faveur des femmes/);
  assert.equal(doc("LAB_GENDER_PAYGAP", 7.98)?.niveau, "vigilance");
  assert.equal(doc("LAB_GENDER_PAYGAP", 3), null);
});

test("états non documentés : obligatoire absent en alerte, présumé en vigilance, aucune info sans signal", () => {
  assert.equal(evaluer({ code: "SUP_VIGILANCE_PLAN", etat: "obligatoire_absent", valeurNum: null, citation: null })?.niveau, "alerte");
  assert.equal(evaluer({ code: "ANI_EXPLOITATION", etat: "presume", valeurNum: null, citation: null })?.niveau, "vigilance");
  assert.equal(evaluer({ code: "SUP_FTI_SCORE", etat: "aucune_info", valeurNum: null, citation: null }), null);
});

test("pas de seuil pour les données qui dépendent du secteur ou de contexte", () => {
  assert.equal(doc("ENV_GHG_INTENSITY", 4390), null);
  assert.equal(doc("GEO_LOBBYING_SPEND", 9499999.5), null);
});

test("taux d'impôt bas : pas de vigilance sur un exercice en perte", () => {
  assert.equal(doc("TAX_EFFECTIVE_RATE", 9, "taux effectif 9 %")?.niveau, "vigilance");
  assert.equal(doc("TAX_EFFECTIVE_RATE", -9.2, "note sur l'impôt (charge d'impôt sur une perte avant impôt)"), null);
});
