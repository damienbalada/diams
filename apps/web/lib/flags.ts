/**
 * « En bref » d'une fiche — lecture pure des résultats du moteur, aucune donnée
 * nouvelle, aucun jugement ajouté. Chaque point renvoie à sa preuve (extrait,
 * source, date). Règles, publiées dans la méthodologie :
 *
 *  - point fort       : RÉSULTAT documenté (jamais une promesse : règle 3),
 *    compté dans la note, valeur ≥ 0,7 ;
 *  - point de vigilance : indicateur compté avec une valeur ≤ 0,3 (dont une
 *    controverse ou un plafond), controverse signalée hors note (Règle 4), ou
 *    publication obligatoire absente (Règle 1) ;
 *  - certification / label : indicateur de certification documenté comme acquis.
 *
 * Une valeur relative (rang dans le secteur) n'est retenue qu'avec au moins
 * MIN_PEERS pairs : sur un très petit groupe, le rang ne dit rien.
 */
import type { IndicatorResult, ScoreResult } from "./scoring";

/** Indicateurs qui attestent une certification ou un label tiers (libellé court). */
export const CERTIFICATIONS: Record<string, string> = {
  GOV_BCORP: "B Corp",
  INV_SOLIDARITY_LABEL: "Label Finansol",
  ANI_FUR_FREE: "Sans fourrure",
  ANI_ANIMAL_FREE: "100 % végétal",
  ENV_SBTI_VALIDATED: "Objectifs climat SBTi validés",
};

export type FlagReason = "high" | "low" | "controversy" | "unscored" | "gate" | "mandatory_missing";

export interface Flag {
  indicator_code: string;
  label: string;
  reason: FlagReason;
  detail: string;
  value: number | null;
  source_name?: string;
  source_url?: string;
  observed_on?: string;
  /** Donnée du groupe reprise par la marque. */
  inherited_from?: string;
}

export interface Summary {
  strengths: Flag[];
  concerns: Flag[];
  certifications: Flag[];
}

const STRONG = 0.7;
const WEAK = 0.3;
/** Un rang intra-secteur n'est un signal qu'à partir de ce nombre de pairs :
 *  avec deux pairs, 0,6 point d'écart suffit à classer « dernier ». */
export const MIN_PEERS = 5;

const clip = (s: string, n = 220) => (s.length > n ? `${s.slice(0, n - 1).trimEnd()}…` : s);

/** Le fait lui-même. Quand l'extrait le résume en français après la citation
 *  (« H&M » — note E : la marque ne verse…), c'est ce résumé ; sinon la citation
 *  « … » (le contexte documentaire reste affiché dans le détail du pilier), sinon
 *  l'extrait entier. */
export const fact = (s: string) => {
  // Résumé en français juste après la citation (« X » — sortie effective ; …),
  // ou en fin d'extrait (… (Sweden), climat — note A.).
  const tail = s.match(/»\s*—\s*([^«»;]+)/) ?? s.match(/—\s*([^«»;—]+?)\s*$/);
  if (tail) {
    const t = tail[1].trim().replace(/\s*:$/, "");
    return t.charAt(0).toUpperCase() + t.slice(1);
  }
  const m = s.match(/«\s*([\s\S]+?)\s*»/);
  return m ? `« ${m[1]} »` : s;
};

const fmt = (n: number, digits = 1) => n.toLocaleString("fr-FR", { maximumFractionDigits: digits });

/**
 * Le fait en une phrase, tirée de la valeur publiée (la citation exacte reste
 * dans le détail du pilier). Seulement quand la phrase ne dit rien de plus que
 * la valeur : sinon, on affiche la citation.
 */
const DESCRIBE: Record<string, (v: number | null | undefined) => string | null> = {
  GOV_BOARD_GENDER: (v) => (v == null ? null : `${fmt(v)} % de femmes au conseil.`),
  GOV_BOARD_INDEP: (v) => (v == null ? null : `${fmt(v)} % d'administrateurs indépendants.`),
  LAB_CEO_PAY_RATIO: (v) =>
    v == null ? null : `La rémunération la plus élevée vaut ${fmt(v, 0)} fois la rémunération médiane.`,
  LAB_GENDER_PAYGAP: (v) =>
    v == null ? null
      : v < 0 ? `Les femmes gagnent en moyenne ${fmt(-v)} % de plus que les hommes.`
      : `Les femmes gagnent en moyenne ${fmt(v)} % de moins que les hommes.`,
  LAB_EGAPRO_INDEX: (v) => (v == null ? null : `Index Égapro : ${fmt(v, 0)}/100.`),
  TAX_EFFECTIVE_RATE: (v) => (v == null ? null : `Taux d'impôt effectif : ${fmt(v)} %.`),
  ENV_GHG_INTENSITY: (v) => (v == null ? null : `${fmt(v, 0)} t CO2e émises par million de chiffre d'affaires.`),
  ENV_SCOPE3_DISCLOSED: () => "Publie ses émissions indirectes (scope 3), souvent l'essentiel de son empreinte carbone.",
  SUP_VIGILANCE_PLAN: () => "Plan de vigilance complet : cartographie des risques, alerte et suivi.",
  GEO_LOBBYING_TRANSP: () => "Déclare ses activités de lobbying dans un registre public.",
  TAX_CBCR_PUBLISHED: () => "Publie son activité et ses impôts pays par pays.",
  ENV_GHG_TREND: (v) =>
    v == null ? null
      : v >= 0 ? `Émissions totales en hausse de ${fmt(v)} % par an.`
      : `Émissions totales en baisse de ${fmt(-v)} % par an.`,
};

function toFlag(i: IndicatorResult, label: string, reason: FlagReason, fallback: string): Flag {
  const described = i.covered && !i.display_only ? DESCRIBE[i.indicator_code]?.(i.raw_value) : null;
  return {
    indicator_code: i.indicator_code,
    label,
    reason,
    detail: described ?? (i.excerpt ? clip(fact(i.excerpt)) : fallback),
    value: i.value,
    source_name: i.source_name ?? i.source_code,
    source_url: i.source_url,
    observed_on: i.observed_on,
    inherited_from: i.inherited_from,
  };
}

const CONCERN_ORDER: Record<FlagReason, number> = {
  controversy: 0, gate: 1, low: 2, unscored: 3, mandatory_missing: 4, high: 9,
};

export function summarize(result: ScoreResult, names: Map<string, string>, max = 3): Summary {
  const strengths: Flag[] = [];
  const concerns: Flag[] = [];
  const certifications: Flag[] = [];
  const name = (code: string) => names.get(code) ?? code;

  for (const d of result.dimensions) {
    for (const i of d.indicators) {
      const label = name(i.indicator_code);
      if (!i.covered) {
        if (i.mandatory && !i.is_gate) {
          const regimes = (i.mandatory_regimes ?? []).join(", ");
          concerns.push(toFlag(i, label, "mandatory_missing",
            `La loi l'oblige à publier cette donnée${regimes ? ` (${regimes})` : ""} ; elle n'a pas été trouvée pour l'ensemble du groupe : comptée 0.`));
        }
        continue;
      }
      if (i.display_only) {
        concerns.push(toFlag(i, label, "unscored", "Controverse signalée, non corroborée : affichée mais hors note."));
        continue;
      }
      if (i.compliance_only || i.unrankable || i.informative) continue; // hors note : obligation respectée, rang impossible, contexte
      const v = i.value ?? 0;
      if (i.peer_count !== undefined && i.peer_count < MIN_PEERS) continue; // rang trop fragile
      if (CERTIFICATIONS[i.indicator_code] && i.nature === "result" && v >= 0.99) {
        certifications.push(toFlag(i, CERTIFICATIONS[i.indicator_code], "high", label));
        continue;
      }
      if (v >= STRONG && i.nature === "result") {
        strengths.push(toFlag(i, label, "high", `${Math.round(v * 100)} % sur cet indicateur.`));
      } else if (v <= WEAK) {
        const reason: FlagReason = i.nature === "controversy" ? "controversy" : i.is_gate ? "gate" : "low";
        concerns.push(toFlag(i, label, reason, `${Math.round(v * 100)} % sur cet indicateur.`));
      }
    }
  }
  strengths.sort((a, b) => (b.value ?? 0) - (a.value ?? 0));
  concerns.sort((a, b) => CONCERN_ORDER[a.reason] - CONCERN_ORDER[b.reason] || (a.value ?? 0) - (b.value ?? 0));
  return { strengths: strengths.slice(0, max), concerns: concerns.slice(0, max), certifications };
}
