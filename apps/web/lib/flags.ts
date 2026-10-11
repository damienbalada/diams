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
}

export interface Summary {
  strengths: Flag[];
  concerns: Flag[];
  certifications: Flag[];
}

const STRONG = 0.7;
const WEAK = 0.3;

const clip = (s: string, n = 220) => (s.length > n ? `${s.slice(0, n - 1).trimEnd()}…` : s);

/** Le fait lui-même : la citation « … » si l'extrait en contient une (le contexte
 *  documentaire reste affiché dans le détail du pilier), sinon l'extrait entier. */
export const fact = (s: string) => {
  const m = s.match(/«\s*([\s\S]+?)\s*»/);
  return m ? `« ${m[1]} »` : s;
};

function toFlag(i: IndicatorResult, label: string, reason: FlagReason, fallback: string): Flag {
  return {
    indicator_code: i.indicator_code,
    label,
    reason,
    detail: i.excerpt ? clip(fact(i.excerpt)) : fallback,
    value: i.value,
    source_name: i.source_name ?? i.source_code,
    source_url: i.source_url,
    observed_on: i.observed_on,
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
            `Publication obligatoire${regimes ? ` (${regimes})` : ""} : aucune preuve versée à ce jour, comptée 0.`));
        }
        continue;
      }
      if (i.display_only) {
        concerns.push(toFlag(i, label, "unscored", "Controverse signalée, non corroborée : affichée mais hors note."));
        continue;
      }
      const v = i.value ?? 0;
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
