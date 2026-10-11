// Tests du résumé « En bref » (logique pure).
// Lancer : node --test --experimental-strip-types apps/web/lib/flags.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { summarize } from "./flags.ts";
import type { IndicatorResult, ScoreResult } from "./scoring.ts";

function ind(code: string, extra: Partial<IndicatorResult>): IndicatorResult {
  return { indicator_code: code, dimension_code: "X", covered: true, value: 0.5, confidence: 0.8, nature: "result", ...extra };
}
function result(indicators: IndicatorResult[]): ScoreResult {
  return {
    score: 0.5, confidence: 0.5, grade: "C", rated: true, publishable: true, groups: [], last_observed: null,
    dimensions: [{ dimension_code: "X", name: "X", score: 0.5, confidence: 0.5, grade: "C", rated: true,
      applicable_indicators: indicators.length, covered_indicators: indicators.length, indicators }],
  };
}
const names = new Map([["A", "Indicateur A"]]);

test("en bref — points forts ≥ 0,7, vigilance ≤ 0,3, extrait repris", () => {
  const s = summarize(result([
    ind("A", { value: 0.9, excerpt: "Index Égapro 98/100" }),
    ind("B", { value: 0.5 }),
    ind("C", { value: 0.1, excerpt: "9,4 Md$ en 2025" }),
  ]), names);
  assert.deepEqual(s.strengths.map((f) => f.indicator_code), ["A"]);
  assert.equal(s.strengths[0].label, "Indicateur A");
  assert.equal(s.strengths[0].detail, "Index Égapro 98/100");
  assert.deepEqual(s.concerns.map((f) => f.indicator_code), ["C"]);
});

test("en bref — une phrase lisible tirée de la valeur publiée", () => {
  const s = summarize(result([
    ind("GOV_BOARD_GENDER", { value: 0.8, raw_value: 40, excerpt: "… « 40 % d’administratrices » …" }),
    ind("LAB_GENDER_PAYGAP", { value: 0.1, raw_value: -30.1 }),
    ind("SUP_VIGILANCE_PLAN", { value: 1, excerpt: "« 3.6 Plan de Vigilance 3.6.1 Introduction … »" }),
  ]), names, 3);
  const d = Object.fromEntries([...s.strengths, ...s.concerns].map((f) => [f.indicator_code, f.detail]));
  assert.equal(d.GOV_BOARD_GENDER, "40 % de femmes au conseil.");
  assert.match(d.SUP_VIGILANCE_PLAN, /cartographie des risques/);
  assert.equal(d.LAB_GENDER_PAYGAP, "Les femmes gagnent en moyenne 30,1 % de plus que les hommes.");
});

test("en bref — la citation seule, sans le préambule documentaire", () => {
  const s = summarize(result([
    ind("A", { value: 1, excerpt: "Rapport financier annuel 2025 (ESEF), ESRS 2 GOV-1 : « En 2025, le Conseil se composait de 60 % de femmes »" }),
  ]), names);
  assert.equal(s.strengths[0].detail, "« En 2025, le Conseil se composait de 60 % de femmes »");
});

test("en bref — controverse en tête, hors note signalée, obligatoire manquant signalé", () => {
  const s = summarize(result([
    ind("LOW", { value: 0.2 }),
    ind("CTRV", { value: 0.25, nature: "controversy" }),
    ind("UNSC", { display_only: true, value: null, nature: "controversy" }),
    ind("MISS", { covered: false, value: null, mandatory: true, mandatory_regimes: ["CSRD"] }),
  ]), names, 4);
  assert.deepEqual(s.concerns.map((f) => f.reason), ["controversy", "low", "unscored", "mandatory_missing"]);
  assert.match(s.concerns[3].detail, /CSRD/);
});

test("en bref — un manquant non obligatoire n'est jamais un point de vigilance", () => {
  const s = summarize(result([ind("OPT", { covered: false, value: null })]), names);
  assert.equal(s.concerns.length, 0);
});

test("en bref — un rang sur trop peu de pairs n'est ni un point fort ni un point de vigilance", () => {
  const s = summarize(result([
    ind("TAX", { value: 0.25, raw_value: 32.8, peer_count: 2 }),
    ind("PAY", { value: 0.1, raw_value: 1739, peer_count: 8 }),
  ]), names);
  assert.deepEqual(s.concerns.map((f) => f.indicator_code), ["PAY"]);
});

test("en bref — certifications à part, jamais une promesse", () => {
  const s = summarize(result([
    ind("GOV_BCORP", { value: 1 }),
    ind("ENV_SBTI_VALIDATED", { value: 1, nature: "commitment" }), // engagement : pas une certification
  ]), names);
  assert.deepEqual(s.certifications.map((f) => f.label), ["B Corp"]);
  assert.equal(s.strengths.length, 0); // ni la certification ni l'engagement ne sont doublés en point fort
});
