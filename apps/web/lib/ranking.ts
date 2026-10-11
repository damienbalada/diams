/**
 * Classement par secteur — logique pure (aucun accès base), testable comme le
 * moteur. Règle 6 : on ne compare que des entités du même secteur ET de même
 * nature. Les indicateurs applicables varient d'un secteur à l'autre (une banque
 * n'a pas de pilier « bien-être animal ») : deux notes de secteurs différents ne
 * mesurent pas la même chose. Et un groupe n'est pas une alternative d'achat à
 * une marque.
 */

export interface RankRow {
  slug: string;
  name: string;
  is_brand: boolean;
  group: string | null;
  grade: string;
  score: number;
  confidence: number;
  publishable: boolean;
  last_observed: string | null;
  sector_id: string | null;
}

export interface SectorInfo {
  id: string;
  code: string;
  name: string;
}

export interface SectorRanking<T extends RankRow = RankRow> {
  sector: SectorInfo;
  /** Entités publiables, triées par note (puis fiabilité). */
  groups: T[];
  brands: T[];
  /** Entités du secteur encore sous le seuil de fiabilité. */
  unranked: number;
}

export const UNKNOWN_SECTOR: SectorInfo = { id: "", code: "inconnu", name: "Secteur non renseigné" };

const byScore = (a: RankRow, b: RankRow) => b.score - a.score || b.confidence - a.confidence;

/**
 * Regroupe par secteur. `ranked` : secteurs ayant au moins une entité publiable,
 * les plus fournis d'abord (là où un vrai choix existe) ; `empty` : secteurs dont
 * aucune entité n'est encore publiable.
 */
export function rankBySector<T extends RankRow>(
  rows: T[],
  sectors: SectorInfo[],
): { ranked: SectorRanking<T>[]; empty: SectorRanking<T>[] } {
  const info = new Map(sectors.map((s) => [s.id, s]));
  const buckets = new Map<string, SectorRanking<T>>();
  for (const r of rows) {
    const sector = (r.sector_id && info.get(r.sector_id)) || UNKNOWN_SECTOR;
    const b = buckets.get(sector.id) ?? { sector, groups: [], brands: [], unranked: 0 };
    if (!r.publishable) b.unranked++;
    else (r.is_brand ? b.brands : b.groups).push(r);
    buckets.set(sector.id, b);
  }
  const all = [...buckets.values()];
  for (const b of all) {
    b.groups.sort(byScore);
    b.brands.sort(byScore);
  }
  const size = (b: SectorRanking<T>) => b.groups.length + b.brands.length;
  const byName = (a: SectorRanking<T>, b: SectorRanking<T>) => a.sector.name.localeCompare(b.sector.name, "fr");
  return {
    ranked: all.filter((b) => size(b) > 0).sort((a, b) => size(b) - size(a) || byName(a, b)),
    empty: all.filter((b) => size(b) === 0).sort(byName),
  };
}

/**
 * Meilleure entité de chaque groupe, dans l'ordre donné : une marque reprend les
 * données de son groupe (Règle 8), un podium de quatre marques du même groupe ne
 * montrerait qu'un seul choix.
 */
export function onePerGroup<T extends RankRow>(rows: T[]): T[] {
  const seen = new Set<string>();
  return rows.filter((r) => {
    const key = r.group ?? r.name;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

/** Ancre stable d'un secteur dans la page de classement. */
export const sectorAnchor = (s: SectorInfo) => `secteur-${s.code}`;
