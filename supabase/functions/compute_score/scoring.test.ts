// Tests unitaires du moteur de scoring (logique pure).
// Lancer : node --test --experimental-strip-types supabase/functions/compute_score/scoring.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  computeScore,
  toGrade,
  type Evidence,
  type Indicator,
  type ScoreInput,
  type Tier,
  type Nature,
} from "./scoring.ts";

// --- config de référence (miroir des tables de config en base) ---------------
const tierConfig: ScoreInput["tierConfig"] = {
  regulatory:  { evidence_weight: 1.0,  max_confidence: 1.0,  can_penalize_alone: true,  min_score_floor_alone: 0.0 },
  audited_ngo: { evidence_weight: 0.8,  max_confidence: 0.85, can_penalize_alone: true,  min_score_floor_alone: 0.0 },
  press:       { evidence_weight: 0.35, max_confidence: 0.45, can_penalize_alone: false, min_score_floor_alone: 0.3 },
  crowd:       { evidence_weight: 0.2,  max_confidence: 0.3,  can_penalize_alone: false, min_score_floor_alone: 0.4 },
};
const natureConfig: ScoreInput["natureConfig"] = {
  result:      { score_multiplier: 1.0, max_score_without_result: null },
  policy:      { score_multiplier: 0.7, max_score_without_result: 0.6 },
  commitment:  { score_multiplier: 0.4, max_score_without_result: 0.5 },
  controversy: { score_multiplier: 1.0, max_score_without_result: null },
};
const params = { missing_data_score: 0, missing_data_confidence: 0, min_confidence_to_publish: 0.3 };

// --- helpers -----------------------------------------------------------------
function ev(partial: Partial<Evidence> & { indicator_code: string }): Evidence {
  return {
    tier: "regulatory",
    nature: "result",
    normalized_value: null,
    value_numeric: null,
    confidence: 0.9,
    observed_on: "2024-01-01",
    specificity: 2,
    ...partial,
  };
}
function ind(code: string, dim: string, extra: Partial<Indicator> = {}): Indicator {
  return { code, dimension_code: dim, kind: "binary", direction: "higher_better", weight: 1, ...extra };
}
function baseInput(over: Partial<ScoreInput>): ScoreInput {
  return {
    applicableIndicators: [],
    evidence: [],
    dimensions: [{ code: "ENV", name: "Environnement" }, { code: "ANI", name: "Animal" }],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }, { dimension_code: "ANI", weight: 1 }],
    dimensionGroups: [],
    tierConfig,
    natureConfig,
    params,
    ...over,
  };
}

// --- Règle 1 (v0.5) : manquant = 0 SI la publication est obligatoire ---------
test("règle 1 — dimension sans evidence ni obligation : non notée, confiance 0", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV"), ind("ENV_B", "ENV")],
    evidence: [],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const env = res.dimensions.find((d) => d.dimension_code === "ENV")!;
  assert.equal(env.rated, false);
  assert.equal(env.score, 0);
  assert.equal(env.confidence, 0);
  assert.equal(env.covered_indicators, 0);
  assert.equal(res.rated, false);
  assert.equal(res.publishable, false);
});

test("règle 1 — manquant OBLIGATOIRE : tire la note vers le bas (opacité punie)", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV"), ind("ENV_B", "ENV", { mandatory: true, mandatory_regimes: ["CSRD"] })],
    evidence: [ev({ indicator_code: "ENV_A", normalized_value: 1.0 })], // ENV_B manquant
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const env = res.dimensions.find((d) => d.dimension_code === "ENV")!;
  // (1.0*1 + 0*1) / 2 = 0.5
  assert.equal(env.score, 0.5);
  assert.equal(env.covered_indicators, 1);
  const b = env.indicators.find((i) => i.indicator_code === "ENV_B")!;
  assert.equal(b.mandatory, true);
  assert.deepEqual(b.mandatory_regimes, ["CSRD"]);
});

test("labels (v0.5.1) — absent : ni note, ni fiabilité, ni ligne ; présent : un résultat compté", () => {
  const indicators = [ind("ENV_A", "ENV"), ind("ENV_LABEL", "ENV", { presence_only: true })];
  const absent = computeScore(baseInput({
    applicableIndicators: indicators,
    evidence: [ev({ indicator_code: "ENV_A", normalized_value: 0.5, confidence: 0.9 })],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const a = absent.dimensions.find((d) => d.dimension_code === "ENV")!;
  assert.equal(a.score, 0.5);
  assert.ok(Math.abs(a.confidence - 0.9) < 1e-9);       // le label absent ne baisse pas la fiabilité
  assert.equal(a.applicable_indicators, 1);
  assert.equal(a.indicators.some((i) => i.indicator_code === "ENV_LABEL"), false);

  const present = computeScore(baseInput({
    applicableIndicators: indicators,
    evidence: [
      ev({ indicator_code: "ENV_A", normalized_value: 0.5, confidence: 0.9 }),
      ev({ indicator_code: "ENV_LABEL", normalized_value: 1.0, confidence: 0.8 }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const p = present.dimensions.find((d) => d.dimension_code === "ENV")!;
  assert.equal(p.score, 0.75);
  assert.equal(p.covered_indicators, 2);
});

test("règle 1 — manquant NON obligatoire : hors note, mais la fiabilité baisse", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV"), ind("ENV_B", "ENV")],
    evidence: [ev({ indicator_code: "ENV_A", normalized_value: 1.0, confidence: 0.9 })],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const env = res.dimensions.find((d) => d.dimension_code === "ENV")!;
  assert.equal(env.rated, true);
  assert.equal(env.score, 1.0);                         // ENV_B n'entre pas dans la note
  assert.ok(Math.abs(env.confidence - 0.45) < 1e-9);    // (0.9 + 0) / 2
});

test("règle 1 — dimension vide mais obligatoire : notée 0", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV", { mandatory: true })],
    evidence: [],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const env = res.dimensions[0];
  assert.equal(env.rated, true);
  assert.equal(env.score, 0);
  assert.equal(res.rated, true);
});

test("règle 1 — un pilier non noté sort de la note globale mais pèse sur la fiabilité", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV"), ind("ANI_A", "ANI")],
    evidence: [ev({ indicator_code: "ENV_A", normalized_value: 0.8, confidence: 0.9 })], // ANI vide, non obligatoire
    profileWeights: [{ dimension_code: "ENV", weight: 1 }, { dimension_code: "ANI", weight: 1 }],
  }));
  assert.ok(Math.abs(res.score - 0.8) < 1e-9);          // ANI hors note
  assert.ok(Math.abs(res.confidence - 0.45) < 1e-9);    // (0.9 + 0) / 2
  assert.equal(res.publishable, true);                  // 0.45 >= 0.30
});

test("règle 5 — une note n'est publiable que si elle repose sur au moins un pilier noté", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV")],
    evidence: [],
    params: { ...params, min_confidence_to_publish: 0 },
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  assert.equal(res.rated, false);
  assert.equal(res.publishable, false);
});

// --- Règle 3 : anti-greenwashing --------------------------------------------
test("règle 3 — une politique seule est plafonnée à 0.6", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV")],
    evidence: [ev({ indicator_code: "ENV_A", nature: "policy", normalized_value: 1.0 })],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const r = res.dimensions[0].indicators[0];
  assert.equal(r.value, 0.6);
  assert.equal(r.capped_by_greenwashing, true);
});

test("règle 3 — un engagement seul est faible (×0.4)", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV")],
    evidence: [ev({ indicator_code: "ENV_A", nature: "commitment", normalized_value: 1.0 })],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  assert.equal(res.dimensions[0].indicators[0].value, 0.4);
});

test("règle 3 — un résultat débloque le plein potentiel", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV")],
    evidence: [
      ev({ indicator_code: "ENV_A", nature: "policy", normalized_value: 1.0 }),
      ev({ indicator_code: "ENV_A", nature: "result", normalized_value: 0.9 }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const r = res.dimensions[0].indicators[0];
  assert.equal(r.value, 0.9);
  assert.equal(r.nature, "result");
  assert.ok(!r.capped_by_greenwashing);
});

// --- Règle 2 : tiers (poids + plafond confiance + plancher anti-presse) -------
test("règle 2 — la confiance d'une source presse est plafonnée à 0.45", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ANI_A", "ANI")],
    evidence: [ev({ indicator_code: "ANI_A", tier: "press", confidence: 0.95, normalized_value: 0.8 })],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  assert.equal(res.dimensions[0].indicators[0].confidence, 0.45);
});

test("règle 2 — deux controverses presse corroborantes : pénalise mais plancher 0.3", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ANI_A", "ANI")],
    // pas de positive -> base 0.5 ; DEUX sources presse distinctes -> corroboré -> compte
    evidence: [
      ev({ indicator_code: "ANI_A", tier: "press", nature: "controversy", normalized_value: 1.0, source_code: "PRESS_A" }),
      ev({ indicator_code: "ANI_A", tier: "press", nature: "controversy", normalized_value: 1.0, source_code: "PRESS_B" }),
    ],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  const r = res.dimensions[0].indicators[0];
  // 0.5 * (1 - 1.0*0.35) = 0.325, plancher 0.3 respecté
  assert.ok(r.value! >= 0.3, `value=${r.value}`);
  assert.ok(Math.abs(r.value! - 0.325) < 1e-9);
});

// --- Règle 4 : controverse CONTESTÉE à source unique = affichée, hors calcul --
test("règle 4 — une controverse contestée à source unique est affichée mais hors calcul", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("GEO_A", "ENV"), ind("GEO_B", "ENV")],
    evidence: [
      ev({ indicator_code: "GEO_A", nature: "result", normalized_value: 1.0 }),
      // controverse contestée, source unique : ne doit PAS peser
      ev({ indicator_code: "GEO_B", tier: "audited_ngo", nature: "controversy", normalized_value: 1.0, contested: true, source_code: "SR_ONU" }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const env = res.dimensions.find((d) => d.dimension_code === "ENV")!;
  const rb = env.indicators.find((i) => i.indicator_code === "GEO_B")!;
  assert.equal(rb.display_only, true);
  assert.equal(rb.value, null);
  assert.equal(rb.covered, true);          // toujours affiché
  // GEO_B est exclu du calcul -> la dimension ne retient que GEO_A (=1.0)
  assert.equal(env.score, 1.0);
  assert.equal(env.applicable_indicators, 1);
});

test("règle 4 — une controverse NON contestée (ONG auditée) à source unique compte normalement", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("PLA_A", "ENV")],
    // controverse crédible non contestée (ex: audit BFFP), source unique -> compte
    evidence: [
      ev({ indicator_code: "PLA_A", tier: "audited_ngo", nature: "controversy", normalized_value: 1.0, source_code: "BFFP" }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const r = res.dimensions[0].indicators[0];
  assert.ok(!r.display_only);
  // base 0.5 * (1 - 1.0*0.8) = 0.1
  assert.ok(Math.abs(r.value! - 0.1) < 1e-9, `value=${r.value}`);
});

test("règle 4 — une controverse contestée corroborée par une 2e source compte", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("GEO_B", "ENV")],
    evidence: [
      ev({ indicator_code: "GEO_B", tier: "audited_ngo", nature: "controversy", normalized_value: 1.0, contested: true, source_code: "SR_ONU" }),
      ev({ indicator_code: "GEO_B", tier: "audited_ngo", nature: "controversy", normalized_value: 1.0, contested: true, source_code: "OHCHR" }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const rb = res.dimensions[0].indicators[0];
  assert.ok(!rb.display_only);
  assert.ok(rb.value! < 0.5); // pénalisée
});

test("règle 4 — une controverse regulatory seule (adjudiquée) pénalise même si contestée", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("GEO_B", "ENV")],
    evidence: [
      ev({ indicator_code: "GEO_B", tier: "regulatory", nature: "controversy", normalized_value: 1.0, contested: true, source_code: "CIJ" }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const rb = res.dimensions[0].indicators[0];
  // base 0.5 * (1 - 1.0*1.0) = 0
  assert.ok(!rb.display_only);
  assert.equal(rb.value, 0);
});

test("règle 4 — résultat + controverse contestée non corroborée : le résultat compte, controverse signalée", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("GEO_A", "ENV")],
    evidence: [
      ev({ indicator_code: "GEO_A", nature: "result", normalized_value: 0.9 }),
      ev({ indicator_code: "GEO_A", tier: "audited_ngo", nature: "controversy", normalized_value: 1.0, contested: true, source_code: "SR_ONU" }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const r = res.dimensions[0].indicators[0];
  assert.equal(r.value, 0.9);                  // non pénalisé
  assert.equal(r.unscored_controversy, true);  // mais la controverse est signalée
});

test("règle 2 — une controverse régulatoire peut pénaliser fortement (pas de plancher)", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ANI_A", "ANI")],
    evidence: [
      ev({ indicator_code: "ANI_A", nature: "result", normalized_value: 1.0 }),
      ev({ indicator_code: "ANI_A", tier: "regulatory", nature: "controversy", normalized_value: 1.0 }),
    ],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  // 1.0 * (1 - 1.0*1.0) = 0
  assert.equal(res.dimensions[0].indicators[0].value, 0);
});

// --- Spécificité ---------------------------------------------------------------
// Depuis v0.5, compute_score_input ne transmet plus l'evidence du groupe à une
// marque (chaque marque est notée sur ses propres preuves). Le moteur garde
// néanmoins le départage par spécificité, neutre quand toutes valent 0.
test("spécificité — à nature égale, l'evidence la plus spécifique prime", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV")],
    evidence: [
      ev({ indicator_code: "ENV_A", nature: "result", normalized_value: 0.5, specificity: 0 }), // groupe
      ev({ indicator_code: "ENV_A", nature: "result", normalized_value: 0.9, specificity: 2 }), // marque
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  assert.equal(res.dimensions[0].indicators[0].value, 0.9);
});

// --- Normalisation intra-secteur (percentile live) ---------------------------
test("normalisation — quantitatif lower_better via percentile intra-secteur", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("LAB_RATIO", "ENV", { kind: "quantitative", direction: "lower_better" })],
    evidence: [ev({ indicator_code: "LAB_RATIO", nature: "result", value_numeric: 50 })],
    peerValues: { LAB_RATIO: [10, 50, 100, 200] }, // 50 est bas -> bon pour lower_better
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  // percentile(50) = (1 + 0.5)/4 = 0.375 ; lower_better -> 1-0.375 = 0.625
  assert.ok(Math.abs(res.dimensions[0].indicators[0].value! - 0.625) < 1e-9);
});

// --- Pondération par profil --------------------------------------------------
test("profil — un profil qui surpondère ENV change la note globale", () => {
  const common = {
    applicableIndicators: [ind("ENV_A", "ENV"), ind("ANI_A", "ANI")],
    evidence: [
      ev({ indicator_code: "ENV_A", nature: "result", normalized_value: 1.0 }), // ENV excellent
      ev({ indicator_code: "ANI_A", nature: "result", normalized_value: 0.0 }), // ANI nul
    ],
  };
  const equilibre = computeScore(baseInput({
    ...common,
    profileWeights: [{ dimension_code: "ENV", weight: 0.5 }, { dimension_code: "ANI", weight: 0.5 }],
  }));
  const ecolo = computeScore(baseInput({
    ...common,
    profileWeights: [{ dimension_code: "ENV", weight: 0.8 }, { dimension_code: "ANI", weight: 0.2 }],
  }));
  assert.equal(equilibre.score, 0.5);            // (1.0*0.5 + 0*0.5)
  assert.ok(Math.abs(ecolo.score - 0.8) < 1e-9); // (1.0*0.8 + 0*0.2)
  assert.ok(ecolo.score > equilibre.score);
});

// --- Méta-score (groupe de dimensions) ---------------------------------------
test("méta-score — agrège les dimensions membres", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ANI_A", "ANI"), ind("ENV_A", "ENV")],
    evidence: [
      ev({ indicator_code: "ANI_A", nature: "result", normalized_value: 0.4 }),
      ev({ indicator_code: "ENV_A", nature: "result", normalized_value: 0.8 }),
    ],
    dimensionGroups: [{ code: "LIVING", name: "Bien-être du vivant", members: [{ dimension_code: "ANI", weight: 1 }] }],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }, { dimension_code: "ANI", weight: 1 }],
  }));
  const living = res.groups.find((g) => g.code === "LIVING")!;
  assert.equal(living.score, 0.4);
  assert.equal(living.grade, "C");
});

// --- Plafond d'exploitation animale (gate) -----------------------------------
test("gate — l'exploitation animale plafonne le pilier malgré un bon welfare", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [
      ind("ANI_LEATHER_TRACE", "ANI", { weight: 1 }),
      ind("ANI_FUR_FREE", "ANI", { weight: 1 }),
      ind("ANI_EXPLOITATION", "ANI", { weight: 0, kind: "categorical" }), // gate
    ],
    evidence: [
      ev({ indicator_code: "ANI_LEATHER_TRACE", nature: "result", normalized_value: 1.0 }),
      ev({ indicator_code: "ANI_FUR_FREE", nature: "result", normalized_value: 1.0 }),
      ev({ indicator_code: "ANI_EXPLOITATION", nature: "result", normalized_value: 0.40 }), // extensive
    ],
    dimensionGates: [{ dimension_code: "ANI", gate_indicator_code: "ANI_EXPLOITATION", default_ceiling: 0.40 }],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  const ani = res.dimensions.find((d) => d.dimension_code === "ANI")!;
  // welfare moyen = 1.0, mais plafonné à 0.40
  assert.equal(ani.score, 0.40);
  assert.equal(ani.ceiling, 0.40);
  assert.equal(ani.capped_by_gate, true);
  assert.equal(ani.applicable_indicators, 2); // le gate n'est pas compté
});

test("gate — animal_free lève le plafond (note pleine possible)", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [
      ind("ANI_LEATHER_TRACE", "ANI", { weight: 1 }),
      ind("ANI_EXPLOITATION", "ANI", { weight: 0, kind: "categorical" }),
    ],
    evidence: [
      ev({ indicator_code: "ANI_LEATHER_TRACE", nature: "result", normalized_value: 0.9 }),
      ev({ indicator_code: "ANI_EXPLOITATION", nature: "result", normalized_value: 1.0 }), // animal_free
    ],
    dimensionGates: [{ dimension_code: "ANI", gate_indicator_code: "ANI_EXPLOITATION", default_ceiling: 0.40 }],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  const ani = res.dimensions.find((d) => d.dimension_code === "ANI")!;
  assert.equal(ani.score, 0.9);
  assert.ok(!ani.capped_by_gate);
});

test("gate — exploitation inconnue : plafond par défaut appliqué", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [
      ind("ANI_LEATHER_TRACE", "ANI", { weight: 1 }),
      ind("ANI_EXPLOITATION", "ANI", { weight: 0, kind: "categorical" }),
    ],
    evidence: [ev({ indicator_code: "ANI_LEATHER_TRACE", nature: "result", normalized_value: 1.0 })], // gate non renseigné
    dimensionGates: [{ dimension_code: "ANI", gate_indicator_code: "ANI_EXPLOITATION", default_ceiling: 0.40 }],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  const ani = res.dimensions.find((d) => d.dimension_code === "ANI")!;
  assert.equal(ani.score, 0.40); // plafond par défaut (on suppose l'exploitation)
  assert.equal(ani.capped_by_gate, true);
});

test("gate — documenté seul (aucun autre indicateur) : il fixe la note du pilier", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [
      ind("ANI_FUR_FREE", "ANI", { weight: 1 }),
      ind("ANI_EXPLOITATION", "ANI", { weight: 0, kind: "categorical" }),
    ],
    evidence: [ev({ indicator_code: "ANI_EXPLOITATION", nature: "result", normalized_value: 0.0, tier: "press" })],
    dimensionGates: [{ dimension_code: "ANI", gate_indicator_code: "ANI_EXPLOITATION", default_ceiling: 0.40 }],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  const ani = res.dimensions[0];
  assert.equal(ani.rated, true);
  assert.equal(ani.score, 0);
  assert.equal(ani.capped_by_gate, true);
  assert.equal(ani.confidence, 0); // le gate ne compte pas dans la fiabilité
});

test("gate — non documenté et pilier sans preuve : pilier non noté (pas de plafond appliqué à rien)", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [
      ind("ANI_FUR_FREE", "ANI", { weight: 1 }),
      ind("ANI_EXPLOITATION", "ANI", { weight: 0, kind: "categorical" }),
    ],
    evidence: [],
    dimensionGates: [{ dimension_code: "ANI", gate_indicator_code: "ANI_EXPLOITATION", default_ceiling: 0.40 }],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  assert.equal(res.dimensions[0].rated, false);
  assert.ok(!res.dimensions[0].capped_by_gate);
});

test("socle — pilier sans indicateur connaissable ni plafond documenté : ni note, ni fiabilité", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [
      ind("ANI_BBFAW_TIER", "ANI", { complementary: true }),
      ind("ANI_EXPLOITATION", "ANI", { weight: 0, kind: "categorical" }),
      ind("GOV_X", "GOV"),
    ],
    evidence: [ev({ indicator_code: "GOV_X", normalized_value: 0.8, confidence: 0.9 })],
    dimensionGates: [{ dimension_code: "ANI", gate_indicator_code: "ANI_EXPLOITATION", default_ceiling: 0.40 }],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }, { dimension_code: "GOV", weight: 1 }],
  }));
  assert.deepEqual(res.dimensions.map((d) => d.dimension_code), ["GOV"]);
  assert.ok(Math.abs(res.confidence - 0.9) < 1e-9);
});

test("socle — pilier réduit à son plafond documenté : noté, fiabilité de cette preuve", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [
      ind("ANI_BBFAW_TIER", "ANI", { complementary: true }),
      ind("ANI_EXPLOITATION", "ANI", { weight: 0, kind: "categorical" }),
    ],
    evidence: [ev({ indicator_code: "ANI_EXPLOITATION", normalized_value: 0.2, confidence: 0.8, tier: "audited_ngo" })],
    dimensionGates: [{ dimension_code: "ANI", gate_indicator_code: "ANI_EXPLOITATION", default_ceiling: 0.40 }],
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  const ani = res.dimensions[0];
  assert.equal(ani.rated, true);
  assert.equal(ani.score, 0.2);
  assert.ok(Math.abs(ani.confidence - 0.8) < 1e-9);
});

test("animal_free — pilier ANI noté sur l'absence d'intrant animal, sans plafond (cas Alpro)", () => {
  // Forme produite par compute_score_input pour une marque animal_free :
  // un seul indicateur ANI (ANI_ANIMAL_FREE), AUCUN gate d'exploitation.
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ANI_ANIMAL_FREE", "ANI", { weight: 1 })],
    evidence: [ev({ indicator_code: "ANI_ANIMAL_FREE", nature: "result", normalized_value: 1.0, specificity: 1 })],
    dimensionGates: [], // le gate exploitation est exclu pour les marques végétales
    profileWeights: [{ dimension_code: "ANI", weight: 1 }],
  }));
  const ani = res.dimensions.find((d) => d.dimension_code === "ANI")!;
  assert.equal(ani.score, 1.0);   // meilleur résultat possible
  assert.equal(ani.grade, "A");
  assert.ok(!ani.capped_by_gate); // aucun plafond
});

// --- Fraîcheur (dernière observation) ----------------------------------------
test("fraîcheur — last_observed = date d'observation la plus récente", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV"), ind("ANI_A", "ANI")],
    evidence: [
      ev({ indicator_code: "ENV_A", nature: "result", normalized_value: 0.8, observed_on: "2022-05-01" }),
      ev({ indicator_code: "ANI_A", nature: "result", normalized_value: 0.6, observed_on: "2024-09-15" }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }, { dimension_code: "ANI", weight: 1 }],
  }));
  assert.equal(res.last_observed, "2024-09-15");
});

test("fraîcheur — aucune preuve : last_observed null", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("ENV_A", "ENV")],
    evidence: [],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  assert.equal(res.last_observed, null);
});

test("socle — un complémentaire absent est ignoré, sauf s'il est obligatoire", () => {
  const indicators = [
    ind("ENV_A", "ENV"),
    ind("ENV_C", "ENV", { complementary: true }),
    ind("ENV_M", "ENV", { complementary: true, mandatory: true, mandatory_regimes: ["CRD"] }),
  ];
  const res = computeScore(baseInput({
    applicableIndicators: indicators,
    evidence: [ev({ indicator_code: "ENV_A", normalized_value: 1.0, confidence: 0.9 })],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const env = res.dimensions[0];
  assert.deepEqual(env.indicators.map((i) => i.indicator_code), ["ENV_A", "ENV_M"]);
  assert.equal(env.score, 0.5);                       // l'obligatoire manquant compte 0
  assert.ok(Math.abs(env.confidence - 0.45) < 1e-9);  // le complémentaire absent ne pèse pas
});

test("données de groupe — la preuve propre passe devant, l'héritée est signalée", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("GOV_X", "ENV", { group_level: true }), ind("GOV_Y", "ENV", { group_level: true })],
    evidence: [
      ev({ indicator_code: "GOV_X", normalized_value: 0.2, specificity: -1, inherited_from: "Groupe" }),
      ev({ indicator_code: "GOV_X", normalized_value: 0.9, specificity: 0 }),
      ev({ indicator_code: "GOV_Y", normalized_value: 0.6, specificity: -1, inherited_from: "Groupe" }),
    ],
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const [x, y] = res.dimensions[0].indicators;
  assert.equal(x.value, 0.9);
  assert.equal(x.inherited_from, undefined);
  assert.equal(y.inherited_from, "Groupe");
});

test("publication obligatoire respectée : fiabilité oui, note non ; volontaire : comptée", () => {
  const run = (mandatory: boolean, value: number) => computeScore(baseInput({
    applicableIndicators: [
      ind("SUP_A", "SUP"),
      ind("SUP_PLAN", "SUP", { disclosure: true, mandatory, mandatory_regimes: mandatory ? ["FR"] : [] }),
    ],
    evidence: [
      ev({ indicator_code: "SUP_A", normalized_value: 0.2, confidence: 0.8 }),
      ev({ indicator_code: "SUP_PLAN", normalized_value: value, confidence: 0.9 }),
    ],
    profileWeights: [{ dimension_code: "SUP", weight: 1 }],
  })).dimensions[0];
  const ok = run(true, 1);
  assert.equal(ok.score, 0.2);                              // la conformité ne relève pas la note
  assert.ok(Math.abs(ok.confidence - 0.85) < 1e-9);         // mais compte dans la fiabilité
  assert.equal(ok.covered_indicators, 2);
  assert.equal(ok.indicators.find((i) => i.indicator_code === "SUP_PLAN")!.compliance_only, true);
  assert.ok(Math.abs(run(false, 1).score - 0.6) < 1e-9);    // volontaire : un plus
  assert.ok(Math.abs(run(true, 0.5).score - 0.35) < 1e-9);  // obligatoire partiel : compté
});

test("publication obligatoire respectée, seule dans le pilier : pilier non noté, fiabilité comptée", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("SUP_PLAN", "SUP", { disclosure: true, mandatory: true, mandatory_regimes: ["FR"] }), ind("GOV_X", "GOV")],
    evidence: [ev({ indicator_code: "SUP_PLAN", normalized_value: 1, confidence: 0.9 }), ev({ indicator_code: "GOV_X", normalized_value: 0.5, confidence: 0.9 })],
    profileWeights: [{ dimension_code: "SUP", weight: 1 }, { dimension_code: "GOV", weight: 1 }],
  }));
  const sup = res.dimensions.find((d) => d.dimension_code === "SUP")!;
  assert.equal(sup.rated, false);
  assert.equal(res.score, 0.5);
  assert.ok(Math.abs(res.confidence - 0.9) < 1e-9);
});

test("rang — moins de pairs que le minimum : valeur affichée, fiabilité seulement", () => {
  const run = (peers: number[], min?: number) => computeScore(baseInput({
    applicableIndicators: [ind("TAX_R", "TAX", { kind: "quantitative", direction: "higher_better" }), ind("TAX_B", "TAX")],
    evidence: [
      ev({ indicator_code: "TAX_R", normalized_value: null, value_numeric: 30, confidence: 0.9 }),
      ev({ indicator_code: "TAX_B", normalized_value: 0.4, confidence: 0.9 }),
    ],
    peerValues: { TAX_R: peers },
    params: { missing_data_score: 0, missing_data_confidence: 0, min_confidence_to_publish: 0.3, ...(min ? { min_peers_for_rank: min } : {}) },
    profileWeights: [{ dimension_code: "TAX", weight: 1 }],
  })).dimensions[0];
  const few = run([10, 20, 30], 5);
  assert.equal(few.score, 0.4);                                    // le rang sur 3 pairs n'entre pas dans la note
  assert.ok(Math.abs(few.confidence - 0.9) < 1e-9);                // mais la donnée compte dans la fiabilité
  assert.equal(few.indicators[0].unrankable, true);
  assert.equal(few.indicators[0].peer_count, 3);
  const enough = run([10, 15, 20, 25, 30], 5);
  assert.ok(enough.score > 0.4 + 1e-9);                            // 5 pairs : rangé et noté
  assert.equal(enough.indicators[0].unrankable, undefined);
  assert.equal(run([30]).indicators[0].peer_count, 1);             // sans paramètre : comportement inchangé
});

test("base de la note — A plafonné et publication refusée quand le socle est trop peu documenté", () => {
  const params = { missing_data_score: 0, missing_data_confidence: 0, min_confidence_to_publish: 0.3,
    min_basis_to_publish: 0.3, min_basis_for_top_grade: 0.5 };
  const indicators = [ind("ENV_A", "ENV"), ind("ENV_B", "ENV"), ind("ENV_C", "ENV"), ind("ENV_D", "ENV")];
  const run = (n: number) => computeScore(baseInput({
    applicableIndicators: indicators,
    evidence: indicators.slice(0, n).map((i) => ev({ indicator_code: i.code, normalized_value: 1, confidence: 1 })),
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
    params,
  }));
  const thin = run(1);                       // 1 indicateur sur 4 : base 25 %
  assert.equal(thin.basis, 0.25);
  assert.equal(thin.publishable, false);     // sous la base minimale
  const mid = run(3);                        // 75 % : A possible
  assert.equal(mid.grade, "A");
  assert.equal(mid.capped_by_basis, undefined);
  const two = run(2);                        // 50 % : A possible (seuil atteint)
  assert.equal(two.grade, "A");
  const capped = computeScore(baseInput({     // 40 % documenté, tout à 100 % : plafonné sous A
    applicableIndicators: [...indicators, ind("ENV_E", "ENV")],
    evidence: indicators.slice(0, 2).map((i) => ev({ indicator_code: i.code, normalized_value: 1, confidence: 1 })),
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
    params,
  }));
  assert.equal(capped.capped_by_basis, true);
  assert.equal(capped.grade, "B");
  assert.equal(capped.score, 0.79);
  assert.equal(capped.publishable, true);
});

test("base de la note — un obligatoire manquant compte dans la base (il est noté 0)", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("LAB_A", "LAB"), ind("LAB_M", "LAB", { mandatory: true, mandatory_regimes: ["X"] })],
    evidence: [ev({ indicator_code: "LAB_A", normalized_value: 1, confidence: 1 })],
    profileWeights: [{ dimension_code: "LAB", weight: 1 }],
  }));
  assert.equal(res.basis, 1);
  assert.equal(res.score, 0.5);
});

test("normalisation — écart au plus près de zéro : -30 % n'est pas meilleur que 2 %", () => {
  const peers = { GAP: [-30.1, 2.0, 12.4, 20] };
  const score = (v: number) => computeScore(baseInput({
    applicableIndicators: [ind("GAP", "ENV", { kind: "quantitative", direction: "closer_to_zero" })],
    evidence: [ev({ indicator_code: "GAP", value_numeric: v })],
    peerValues: peers,
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  })).dimensions[0].indicators[0].value!;
  assert.ok(score(2.0) > score(12.4));
  assert.ok(score(12.4) > score(20));
  assert.ok(score(20) > score(-30.1)); // 30 % d'écart, même en faveur des femmes : le plus loin de l'égalité
});

test("normalisation — le rang intra-secteur expose la taille du groupe de pairs", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("TAX_X", "ENV", { kind: "quantitative", direction: "higher_better" })],
    evidence: [ev({ indicator_code: "TAX_X", value_numeric: 32.8 })],
    peerValues: { TAX_X: [32.8, 33.4] },
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  const r = res.dimensions[0].indicators[0];
  assert.equal(r.peer_count, 2);
  assert.equal(r.raw_value, 32.8);
});

// --- Quantitatif higher_better (percentile, ex. taux effectif d'imposition) --
test("normalisation — quantitatif higher_better via percentile intra-secteur", () => {
  const res = computeScore(baseInput({
    applicableIndicators: [ind("TAX_ETR", "ENV", { kind: "quantitative", direction: "higher_better" })],
    evidence: [ev({ indicator_code: "TAX_ETR", nature: "result", value_numeric: 100 })],
    peerValues: { TAX_ETR: [10, 50, 100, 200] }, // 100 est plutôt haut -> bon pour higher_better
    profileWeights: [{ dimension_code: "ENV", weight: 1 }],
  }));
  // percentile(100) = (2 + 0.5)/4 = 0.625 ; higher_better -> 0.625
  assert.ok(Math.abs(res.dimensions[0].indicators[0].value! - 0.625) < 1e-9);
});

// --- Gate PLA : sévérité de la controverse -> plafond (verrou anti-régression) -
// Le gate PLA_POLLUTER est écrit comme une CONTROVERSE : normalized = sévérité.
// Le moteur en dérive le plafond (0.5*(1 - sévérité*poids_tier)). Plus la sévérité
// est haute (pire pollueur), plus la note plastique est bridée. Ce test verrouille
// cette sémantique subtile (ne PAS traiter normalized comme un plafond direct).
test("gate PLA — une sévérité BFFP plus haute bride davantage la note plastique", () => {
  const mk = (severity: number) => {
    const res = computeScore(baseInput({
      applicableIndicators: [
        ind("PLA_REDUCTION", "ENV", { weight: 1 }),
        ind("PLA_POLLUTER", "ENV", { weight: 0, kind: "categorical" }), // gate
      ],
      evidence: [
        ev({ indicator_code: "PLA_REDUCTION", nature: "result", normalized_value: 1.0 }),
        ev({ indicator_code: "PLA_POLLUTER", nature: "controversy", tier: "audited_ngo",
             normalized_value: severity, source_code: "BFFP" }),
      ],
      dimensionGates: [{ dimension_code: "ENV", gate_indicator_code: "PLA_POLLUTER", default_ceiling: 1.0 }],
      dimensions: [{ code: "ENV", name: "Env" }],
      profileWeights: [{ dimension_code: "ENV", weight: 1 }],
    }));
    return res.dimensions.find((d) => d.dimension_code === "ENV")!;
  };
  const worst = mk(0.90); // #1 pollueur mondial
  const minor = mk(0.60); // top 10
  assert.ok(Math.abs(worst.score - 0.14) < 1e-9); // 0.5*(1 - 0.90*0.8)
  assert.ok(Math.abs(minor.score - 0.26) < 1e-9); // 0.5*(1 - 0.60*0.8)
  assert.ok(worst.score < minor.score);           // le pire pollueur est plus bridé
  assert.equal(worst.capped_by_gate, true);
});

// --- Garde-fou miroir --------------------------------------------------------
// Le moteur existe en deux exemplaires (edge Deno + web Next.js) faute d'import
// partageable. Ce test échoue si les copies divergent — une divergence
// silencieuse produirait des notes différentes entre l'API et le site.
test("miroir — scoring.ts (edge) et apps/web/lib/scoring.ts sont identiques", async () => {
  const { readFileSync } = await import("node:fs");
  const { fileURLToPath } = await import("node:url");
  const { dirname, join } = await import("node:path");
  const here = dirname(fileURLToPath(import.meta.url));
  const root = join(here, "..", "..", "..");
  const canonical = readFileSync(join(here, "scoring.ts"), "utf8");
  const mirror = readFileSync(join(root, "apps/web/lib/scoring.ts"), "utf8");
  assert.equal(
    mirror,
    canonical,
    "Divergence détectée : lancer `node scripts/sync-scoring.mjs` après avoir édité le fichier canonique.",
  );
});

// --- Notes lettrées ----------------------------------------------------------
test("toGrade — seuils", () => {
  assert.equal(toGrade(0.85), "A");
  assert.equal(toGrade(0.6), "B");
  assert.equal(toGrade(0.4), "C");
  assert.equal(toGrade(0.2), "D");
  assert.equal(toGrade(0.1), "E");
});
