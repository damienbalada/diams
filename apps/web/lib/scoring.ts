// =============================================================================
// Moteur de scoring — logique PURE (aucune dépendance Supabase/Deno).
// Testable isolément (cf. scoring.test.ts).
//
// ⚠️ FICHIER CANONIQUE. Il est MIROITÉ à l'identique dans apps/web/lib/scoring.ts
// (le web et l'edge function ne peuvent pas partager un import). Ne jamais éditer
// la copie : modifier CE fichier puis lancer `node scripts/sync-scoring.mjs`.
// Le test « miroir » (scoring.test.ts) échoue si les deux fichiers divergent.
//
// Pipeline :
//   evidence active PROPRE à l'entité (v0.5 : une marque n'hérite plus du groupe)
//     -> normalisation [0,1] (intra-secteur pour le quantitatif)
//     -> règle 3 (anti-greenwashing : promesse plafonnée, preuve débloque)
//     -> règle 2 (tiers : poids + plafond de confiance + plancher anti-presse)
//     -> agrégation par dimension (règle 1 v0.5 : manquant = 0 SI publication
//        obligatoire ; sinon hors note, mais la fiabilité baisse ; un label
//        absent est ignoré, v0.5.1)
//     -> pondération par profil de valeurs
//     -> score + indice de confiance (séparés) + méta-scores
// =============================================================================

export type Tier = "regulatory" | "audited_ngo" | "press" | "crowd";
export type Nature = "result" | "commitment" | "policy" | "controversy";
export type Kind = "quantitative" | "categorical" | "binary" | "ordinal";
export type Direction = "higher_better" | "lower_better" | "contextual";

export interface TierConfig {
  evidence_weight: number;
  max_confidence: number;
  can_penalize_alone: boolean;
  min_score_floor_alone: number;
}
export interface NatureConfig {
  score_multiplier: number;
  max_score_without_result: number | null;
}
export interface ScoringParams {
  missing_data_score: number;
  missing_data_confidence: number;
  min_confidence_to_publish: number;
}

export interface Dimension {
  code: string;
  name: string;
}
export interface Indicator {
  code: string;
  /** nom lisible (affichage) */
  name?: string;
  unit?: string;
  dimension_code: string;
  kind: Kind;
  direction: Direction;
  weight: number;
  /** Règle 1 : publication légalement obligatoire pour l'entité notée. Manquant
   *  ⇒ compté missing_data_score. Sinon, manquant ⇒ hors note (fiabilité seule). */
  mandatory?: boolean;
  /** Régimes légaux qui imposent la publication (affichage). */
  mandatory_regimes?: string[];
  /** Label / certification tiers : présent ⇒ compté comme un résultat ; absent
   *  ⇒ ignoré, ni dans la note ni dans la fiabilité (personne ne doit un label). */
  presence_only?: boolean;
}
export interface Evidence {
  indicator_code: string;
  tier: Tier;
  nature: Nature;
  /** valeur normalisée [0,1] précalculée à l'ingestion (prioritaire). */
  normalized_value: number | null;
  /** valeur numérique brute (fallback pour normalisation intra-secteur live). */
  value_numeric: number | null;
  confidence: number;
  observed_on: string; // ISO date
  /** 0 = ancêtre lointain (groupe), plus élevé = plus proche de l'entité notée. */
  specificity: number;
  /** Source explicitement contestée (ex : rapport isolé, mandat-holder controversé). */
  contested?: boolean;
  source_code?: string;
  source_url?: string;
  /** Ce que dit la source (affichage : la fiche montre le fait, pas seulement un %). */
  excerpt?: string;
  source_name?: string;
}
export interface ProfileWeight {
  dimension_code: string;
  weight: number;
}
export interface DimensionGroup {
  code: string;
  name: string;
  members: { dimension_code: string; weight: number }[];
}
/**
 * Plafond de dimension piloté par un indicateur "gate" (ex: exploitation
 * animale plafonne le pilier ANI). Le gate ne pèse PAS dans la moyenne :
 * sa valeur sert de plafond. Si le gate est inconnu, default_ceiling s'applique.
 */
export interface DimensionGate {
  dimension_code: string;
  gate_indicator_code: string;
  default_ceiling: number;
}

export interface ScoreInput {
  applicableIndicators: Indicator[];
  evidence: Evidence[];
  dimensions: Dimension[];
  profileWeights: ProfileWeight[];
  dimensionGroups: DimensionGroup[];
  tierConfig: Record<Tier, TierConfig>;
  natureConfig: Record<Nature, NatureConfig>;
  params: ScoringParams;
  /** indicator_code -> valeurs numériques des pairs du secteur (incl. l'entité). */
  peerValues?: Record<string, number[]>;
  /** plafonds de dimension pilotés par un indicateur gate. */
  dimensionGates?: DimensionGate[];
}

export interface IndicatorResult {
  indicator_code: string;
  dimension_code: string;
  covered: boolean;
  value: number | null;
  confidence: number;
  nature?: Nature;
  tier?: Tier;
  observed_on?: string;
  source_code?: string;
  source_url?: string;
  source_name?: string;
  /** Extrait de la preuve retenue et sa valeur brute (affichage uniquement). */
  excerpt?: string;
  raw_value?: number | null;
  /** Valeur relative : nombre de pairs du secteur ayant servi au rang (percentile). */
  peer_count?: number;
  capped_by_greenwashing?: boolean;
  floored_by_low_tier?: boolean;
  /** Controverse affichée mais EXCLUE du calcul (source unique non corroborée). */
  display_only?: boolean;
  /** Une controverse existe mais n'a pas été comptée faute de corroboration. */
  unscored_controversy?: boolean;
  /** Indicateur-gate (plafond de dimension) : ne se compte pas comme les autres
   *  — s'il est manquant il n'est pas « noté 0 » mais applique default_ceiling. */
  is_gate?: boolean;
  /** Publication obligatoire (Règle 1) : si manquant, compté 0 dans la note. */
  mandatory?: boolean;
  mandatory_regimes?: string[];
}
export interface DimensionResult {
  dimension_code: string;
  name: string;
  score: number;
  confidence: number;
  grade: string;
  /** false : aucune base de note (ni preuve, ni publication obligatoire) — le
   *  pilier n'entre pas dans la note globale, mais pèse sur la fiabilité. */
  rated: boolean;
  applicable_indicators: number;
  covered_indicators: number;
  /** plafond appliqué (gate) si la dimension en a un. */
  ceiling?: number;
  /** true si le plafond a effectivement rabaissé la note (ex: exploitation animale). */
  capped_by_gate?: boolean;
  indicators: IndicatorResult[];
}
export interface GroupResult {
  code: string;
  name: string;
  score: number;
  confidence: number;
  grade: string;
  rated: boolean;
}
export interface ScoreResult {
  score: number;
  confidence: number;
  grade: string;
  /** false : aucun pilier noté — pas de note, seulement une fiabilité. */
  rated: boolean;
  /** Note publiable : notée ET fiabilité >= min_confidence_to_publish (Règle 5). */
  publishable: boolean;
  dimensions: DimensionResult[];
  groups: GroupResult[];
  /** Date d'observation la plus récente parmi les preuves retenues (fraîcheur). */
  last_observed: string | null;
}

// --- helpers ----------------------------------------------------------------

const clamp01 = (x: number): number => Math.max(0, Math.min(1, x));

const NATURE_RANK: Record<Nature, number> = {
  result: 3,
  policy: 2,
  commitment: 1,
  controversy: 0,
};

/** Note lettrée à partir d'un score [0,1]. */
export function toGrade(score: number): string {
  if (score >= 0.8) return "A";
  if (score >= 0.6) return "B";
  if (score >= 0.4) return "C";
  if (score >= 0.2) return "D";
  return "E";
}

/** Percentile [0,1] d'une valeur dans une distribution (rang fractionnaire). */
function percentile(value: number, peers: number[]): number {
  const n = peers.length;
  if (n === 0) return 0.5;
  let below = 0;
  let equal = 0;
  for (const p of peers) {
    if (p < value) below++;
    else if (p === value) equal++;
  }
  return (below + 0.5 * equal) / n;
}

/** Normalise une evidence en [0,1] selon l'indicateur ; `peers` : taille du
 *  groupe de comparaison quand la valeur est un rang intra-secteur. */
function normalizeEvidence(
  ind: Indicator,
  ev: Evidence,
  peerValues?: Record<string, number[]>,
): { value: number; peers?: number } {
  // 1) valeur normalisée précalculée = prioritaire (faits normalisés à l'ingestion)
  if (ev.normalized_value !== null && ev.normalized_value !== undefined) {
    return { value: clamp01(ev.normalized_value) };
  }
  // 2) quantitatif sans normalisation -> percentile intra-secteur live
  if (ind.kind === "quantitative" && ev.value_numeric !== null && ev.value_numeric !== undefined) {
    const peers = peerValues?.[ind.code] ?? [];
    if (peers.length >= 2) {
      const pct = percentile(ev.value_numeric, peers);
      return { value: clamp01(ind.direction === "lower_better" ? 1 - pct : pct), peers: peers.length };
    }
  }
  // 3) défaut neutre
  return { value: 0.5 };
}

/** Évalue un indicateur à partir de son evidence (positives + controverses). */
function evaluateIndicator(
  ind: Indicator,
  evs: Evidence[],
  cfg: ScoreInput,
): IndicatorResult {
  const positives = evs.filter((e) => e.nature !== "controversy");
  const controversies = evs.filter((e) => e.nature === "controversy");

  if (positives.length === 0 && controversies.length === 0) {
    return {
      indicator_code: ind.code,
      dimension_code: ind.dimension_code,
      covered: false,
      value: null,
      confidence: 0,
    };
  }

  const sortRecent = (a: Evidence, b: Evidence) =>
    b.specificity - a.specificity || b.observed_on.localeCompare(a.observed_on);

  // Corroboration (Règle 4) : une controverse issue d'une source explicitement
  // CONTESTÉE ne PÈSE sur la note que si elle est corroborée — adjudiquée
  // (source regulatory : justice/régulateur) OU recoupée par ≥ 2 sources
  // distinctes. Une controverse NON contestée (ONG auditée, presse recoupée…)
  // compte normalement. On ne laisse jamais une source unique contestée piloter
  // un score, mais on ne neutralise pas les controverses sérieuses.
  const distinctSources = new Set(
    controversies.map((c) => c.source_code ?? `${c.tier}:${c.observed_on}`),
  );
  const corroborated =
    controversies.some((c) => c.tier === "regulatory") || distinctSources.size >= 2;
  const allContested = controversies.length > 0 && controversies.every((c) => c.contested === true);
  const controversyCounts = controversies.length > 0 && (!allContested || corroborated);

  // Cas : uniquement des controverses non corroborées → affiché, hors calcul.
  if (positives.length === 0 && !controversyCounts) {
    const driver = [...controversies].sort(sortRecent)[0];
    return {
      indicator_code: ind.code,
      dimension_code: ind.dimension_code,
      covered: true,
      display_only: true,
      unscored_controversy: true,
      value: null,
      confidence: clamp01(Math.min(driver.confidence, cfg.tierConfig[driver.tier].max_confidence)),
      nature: "controversy",
      tier: driver.tier,
      observed_on: driver.observed_on,
      source_code: driver.source_code,
      source_url: driver.source_url,
      source_name: driver.source_name,
      excerpt: driver.excerpt,
      raw_value: driver.value_numeric ?? null,
    };
  }

  // Meilleure evidence positive : résultat > politique > engagement, puis
  // spécificité (la marque prime sur le groupe), puis récence.
  const sortBest = (a: Evidence, b: Evidence) =>
    NATURE_RANK[b.nature] - NATURE_RANK[a.nature] ||
    b.specificity - a.specificity ||
    b.observed_on.localeCompare(a.observed_on);

  const best = positives.length > 0 ? [...positives].sort(sortBest)[0] : undefined;
  const hasResult = positives.some((e) => e.nature === "result");

  // Valeur de base
  const norm = best ? normalizeEvidence(ind, best, cfg.peerValues) : { value: 0.5 };
  let value = norm.value;

  // Règle 3 — anti-greenwashing
  let cappedByGreenwashing = false;
  if (best) {
    const nc = cfg.natureConfig[best.nature];
    value = value * nc.score_multiplier;
    if (!hasResult && nc.max_score_without_result !== null) {
      if (value > nc.max_score_without_result) {
        value = nc.max_score_without_result;
        cappedByGreenwashing = true;
      }
    }
  }

  // Controverses — pénalité, avec plancher anti-presse (règle 2).
  // N'agit QUE si la controverse est corroborée (cf. controversyCounts).
  let flooredByLowTier = false;
  if (controversies.length > 0 && controversyCounts) {
    const preValue = value;
    let effPenalty = 0;
    for (const c of controversies) {
      const severity = c.normalized_value !== null && c.normalized_value !== undefined
        ? clamp01(c.normalized_value)
        : 0.6;
      effPenalty = Math.max(effPenalty, severity * cfg.tierConfig[c.tier].evidence_weight);
    }
    let after = preValue * (1 - effPenalty);
    const anyCanAlone = controversies.some((c) => cfg.tierConfig[c.tier].can_penalize_alone);
    if (!anyCanAlone) {
      // une source faible seule ne peut pas descendre sous le plancher
      let floor = 0;
      for (const c of controversies) floor = Math.max(floor, cfg.tierConfig[c.tier].min_score_floor_alone);
      after = Math.max(after, Math.min(preValue, floor));
      if (after > preValue * (1 - effPenalty)) flooredByLowTier = true;
    }
    value = after;
  }

  value = clamp01(value);

  // Confiance de l'indicateur : plafonnée par le tier (règle 2)
  const driver = best ?? [...controversies].sort(sortRecent)[0];
  const confidence = clamp01(
    Math.min(driver.confidence, cfg.tierConfig[driver.tier].max_confidence),
  );

  return {
    indicator_code: ind.code,
    dimension_code: ind.dimension_code,
    covered: true,
    value,
    confidence,
    nature: best?.nature ?? "controversy",
    tier: driver.tier,
    observed_on: driver.observed_on,
    source_code: driver.source_code,
    source_url: driver.source_url,
    source_name: driver.source_name,
    excerpt: driver.excerpt,
    raw_value: driver.value_numeric ?? null,
    peer_count: norm.peers,
    capped_by_greenwashing: cappedByGreenwashing || undefined,
    floored_by_low_tier: flooredByLowTier || undefined,
    // controverse présente mais non comptée (source unique non corroborée)
    unscored_controversy: (controversies.length > 0 && !controversyCounts) || undefined,
  };
}

/** Calcule le score complet d'une entité pour un profil donné. */
export function computeScore(input: ScoreInput): ScoreResult {
  // Index evidence par indicateur
  const byIndicator = new Map<string, Evidence[]>();
  for (const ev of input.evidence) {
    const arr = byIndicator.get(ev.indicator_code) ?? [];
    arr.push(ev);
    byIndicator.set(ev.indicator_code, arr);
  }

  // Évalue chaque indicateur applicable
  const indicatorResults: IndicatorResult[] = input.applicableIndicators.map((ind) =>
    evaluateIndicator(ind, byIndicator.get(ind.code) ?? [], input)
  );
  const resByCode = new Map(indicatorResults.map((r) => [r.indicator_code, r]));
  const indByCode = new Map(input.applicableIndicators.map((i) => [i.code, i]));
  const dimName = new Map(input.dimensions.map((d) => [d.code, d.name]));

  // Agrégation par dimension (règle 1 : manquant obligatoire = missing_data_score)
  const dimResults: DimensionResult[] = [];
  const dimScore = new Map<string, number>();
  const dimConf = new Map<string, number>();

  const gateByDim = new Map((input.dimensionGates ?? []).map((g) => [g.dimension_code, g]));
  const dimsWithIndicators = [...new Set(input.applicableIndicators.map((i) => i.dimension_code))];

  for (const dimCode of dimsWithIndicators) {
    // Un label absent n'existe pas pour l'entité : ni note, ni fiabilité, ni ligne.
    const inds = input.applicableIndicators.filter(
      (i) => i.dimension_code === dimCode && !(i.presence_only && !resByCode.get(i.code)?.covered),
    );
    const gate = gateByDim.get(dimCode);
    const gateCode = gate?.gate_indicator_code;

    // Le gate ne pèse PAS dans la moyenne (il sert de plafond), et une
    // controverse non corroborée « display_only » est affichée mais hors calcul.
    const scored = inds.filter(
      (i) => i.code !== gateCode && !resByCode.get(i.code)?.display_only,
    );

    let scoreNum = 0;
    let scoreWeight = 0; // poids des indicateurs qui entrent dans la note
    let confNum = 0;
    let confWeight = 0;  // poids de TOUS les indicateurs applicables (fiabilité)
    let covered = 0;
    const indicators: IndicatorResult[] = [];

    for (const ind of inds) {
      const r = resByCode.get(ind.code)!;
      if (ind.code === gateCode) r.is_gate = true;
      if (ind.mandatory) {
        r.mandatory = true;
        r.mandatory_regimes = ind.mandatory_regimes;
      }
      indicators.push(r);
      if (ind.code === gateCode) continue; // exclu de la moyenne et des compteurs
      if (r.display_only) continue;        // affiché mais hors calcul (controverse non corroborée)
      confWeight += ind.weight;
      if (r.covered) {
        scoreNum += (r.value ?? 0) * ind.weight;
        scoreWeight += ind.weight;
        confNum += r.confidence * ind.weight;
        covered++;
      } else {
        // Donnée manquante : la fiabilité baisse toujours. La note n'est
        // pénalisée que si la publication était obligatoire (Règle 1).
        confNum += input.params.missing_data_confidence * ind.weight;
        if (ind.mandatory) {
          scoreNum += input.params.missing_data_score * ind.weight;
          scoreWeight += ind.weight;
        }
      }
    }

    if (scored.length === 0 && !gate) continue;

    // Plafond (gate) : valeur du gate si connue, sinon default_ceiling (conservateur).
    const gr = gate ? resByCode.get(gateCode!) : undefined;
    const gateKnown = !!(gr && gr.covered && gr.value !== null);
    // Noté s'il y a une base : une preuve, un manquant obligatoire, ou un gate
    // documenté (seul, il fixe la note du pilier : son plafond).
    const rated = scoreWeight > 0 || gateKnown;
    const avg = scoreWeight > 0 ? scoreNum / scoreWeight : 1;
    const ceiling = gate ? (gateKnown ? gr!.value! : gate.default_ceiling) : 1;
    const score = rated ? clamp01(Math.min(avg, ceiling)) : 0;
    const cappedByGate = gate && rated ? score < avg - 1e-9 : false;
    const confidence = clamp01(confWeight > 0 ? confNum / confWeight : 0);

    if (rated) dimScore.set(dimCode, score);
    dimConf.set(dimCode, confidence);

    dimResults.push({
      dimension_code: dimCode,
      name: dimName.get(dimCode) ?? dimCode,
      score,
      confidence,
      grade: toGrade(score),
      rated,
      applicable_indicators: scored.length,
      covered_indicators: covered,
      ceiling: gate ? clamp01(ceiling) : undefined,
      capped_by_gate: cappedByGate || undefined,
      indicators,
    });
  }

  // Score global pondéré par le profil : la note sur les piliers NOTÉS, la
  // fiabilité sur TOUS les piliers applicables (un pilier sans base la tire vers 0).
  let gScoreNum = 0;
  let gScoreW = 0;
  let gConfNum = 0;
  let gConfW = 0;
  for (const pw of input.profileWeights) {
    if (!dimConf.has(pw.dimension_code)) continue;
    gConfNum += dimConf.get(pw.dimension_code)! * pw.weight;
    gConfW += pw.weight;
    if (!dimScore.has(pw.dimension_code)) continue;
    gScoreNum += dimScore.get(pw.dimension_code)! * pw.weight;
    gScoreW += pw.weight;
  }
  const rated = gScoreW > 0;
  const score = rated ? clamp01(gScoreNum / gScoreW) : 0;
  const confidence = gConfW > 0 ? clamp01(gConfNum / gConfW) : 0;

  // Fraîcheur : date d'observation la plus récente parmi les preuves retenues.
  let last_observed: string | null = null;
  for (const ev of input.evidence) {
    if (ev.observed_on && (last_observed === null || ev.observed_on > last_observed)) {
      last_observed = ev.observed_on;
    }
  }

  // Méta-scores (groupes de dimensions)
  const groups: GroupResult[] = [];
  for (const g of input.dimensionGroups) {
    let sNum = 0;
    let sW = 0;
    let cNum = 0;
    let cW = 0;
    for (const m of g.members) {
      if (!dimConf.has(m.dimension_code)) continue;
      cNum += dimConf.get(m.dimension_code)! * m.weight;
      cW += m.weight;
      if (!dimScore.has(m.dimension_code)) continue;
      sNum += dimScore.get(m.dimension_code)! * m.weight;
      sW += m.weight;
    }
    if (cW === 0) continue;
    const gs = sW > 0 ? clamp01(sNum / sW) : 0;
    groups.push({
      code: g.code,
      name: g.name,
      score: gs,
      confidence: clamp01(cNum / cW),
      grade: toGrade(gs),
      rated: sW > 0,
    });
  }

  return {
    score,
    confidence,
    grade: toGrade(score),
    rated,
    publishable: rated && confidence >= input.params.min_confidence_to_publish,
    dimensions: dimResults.sort((a, b) => a.dimension_code.localeCompare(b.dimension_code)),
    groups,
    last_observed,
  };
}
