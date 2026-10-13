import { unstable_cache } from "next/cache";
import { getSupabase } from "./supabase";
import { computeScore, type ScoreInput } from "./scoring";
import {
  pickComparable,
  selectAlternatives,
  type Alternative,
  type ScoredCandidate,
} from "./alternatives";

export type { Alternative } from "./alternatives";

export interface ScorePayload extends ScoreInput {
  entity: { slug: string; name: string; sector_id: string | null };
  ownership_chain: string[];
  profile: { code: string; name: string };
}

/** Assemble les entrées de scoring d'une entité via la fonction SQL. */
export async function getScorePayload(
  slug: string,
  profile = "equilibre",
): Promise<ScorePayload | null> {
  const supabase = getSupabase();
  const { data, error } = await supabase.rpc("compute_score_input", {
    p_slug: slug,
    p_profile: profile,
  });
  if (error) throw new Error(error.message);
  if (!data || !data.entity) return null;
  return data as ScorePayload;
}

export interface EntityScore {
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

async function mapWithConcurrency<T, R>(items: T[], limit: number, fn: (t: T) => Promise<R>): Promise<R[]> {
  // File de travail : chaque emplacement reprend une entité dès qu'il se libère
  // (un lot n'attend plus la plus lente de ses entités).
  const out = new Array<R>(items.length);
  let next = 0;
  async function worker() {
    while (next < items.length) {
      const i = next++;
      out[i] = await fn(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return out;
}

/** Calcule la note de toutes les entités (pour classement + accueil). */
/**
 * Notes de toutes les entités. Le calcul complet (une requête et un passage du
 * moteur par entité) prend plusieurs secondes : résultat mis en cache 10 minutes,
 * les pages restant rendues à la demande (aucun appel à la base pendant le build).
 */
export const getAllScores = unstable_cache(computeAllScores, ["all-scores-v117"], { revalidate: 600 });

type ScoreCore = Pick<EntityScore, "group" | "grade" | "score" | "confidence" | "publishable" | "last_observed">;

async function scoreCore(slug: string): Promise<ScoreCore | null> {
  // Une nouvelle tentative en cas d'échec passager (délai, saturation) : une
  // entité ne doit pas disparaître du classement pour une erreur réseau.
  const payload = await getScorePayload(slug).catch(() => getScorePayload(slug));
  if (!payload) return null;
  const r = computeScore(payload);
  const chain = payload.ownership_chain ?? [];
  return {
    group: chain.length > 1 ? chain[chain.length - 1] : null,
    grade: r.grade,
    score: r.score,
    confidence: r.confidence,
    publishable: r.publishable,
    last_observed: r.last_observed,
  };
}

/** Entités qui ont des preuves, régimes ou dispenses propres (null si indisponible). */
async function listEntitiesWithOwnData(): Promise<Set<string> | null> {
  const supabase = getSupabase();
  try {
    const ids = await selectAll<string>((from, to) =>
      supabase.rpc("entities_with_own_scoring_data").range(from, to) as any,
    );
    return new Set(ids.map((x: any) => (typeof x === "string" ? x : x?.entities_with_own_scoring_data ?? String(x))));
  } catch {
    return null;
  }
}

async function computeAllScores(): Promise<EntityScore[]> {
  const [entities, own] = await Promise.all([listEntities(), listEntitiesWithOwnData()]);
  const byId = new Map<string, any>(entities.map((e: any) => [e.id, e]));
  const rootOf = (e: any) => {
    let cur = e;
    for (let i = 0; i < 20 && cur.parent_id && byId.has(cur.parent_id); i++) cur = byId.get(cur.parent_id);
    return cur;
  };
  // Une marque sans donnée propre est notée uniquement à partir de son groupe racine
  // (compute_score_input) : même racine, même secteur, même pays et même indicateur
  // « sans exploitation animale » donnent exactement la même note, calculée une fois.
  const memo = new Map<string, Promise<ScoreCore | null>>();
  const keyOf = (e: any): string | null => {
    if (!own) return null;
    const root = rootOf(e);
    if (root.id === e.id || own.has(e.id)) return null;
    return [root.id, e.sector_id ?? "", e.country ?? "", e.animal_free ? 1 : 0].join("|");
  };
  const scored = await mapWithConcurrency(entities, 24, async (e: any) => {
    try {
      const k = keyOf(e);
      let core: ScoreCore | null;
      if (k) {
        if (!memo.has(k)) memo.set(k, scoreCore(e.slug).catch(() => null));
        core = await memo.get(k)!;
      } else {
        core = await scoreCore(e.slug);
      }
      if (!core) return null;
      return {
        slug: e.slug,
        name: e.display_name ?? e.legal_name,
        is_brand: e.is_brand,
        sector_id: e.sector_id ?? null,
        ...core,
      } as EntityScore;
    } catch {
      return null;
    }
  });
  return scored.filter((x): x is EntityScore => x !== null);
}

/** Secteurs (classement par secteur, Règle 6). */
export async function listSectors(): Promise<{ id: string; code: string; name: string }[]> {
  const supabase = getSupabase();
  const { data, error } = await supabase.from("sectors").select("id, code, name");
  if (error) throw new Error(error.message);
  return data ?? [];
}

/** Chiffres de la page d'accueil : preuves publiées et sources distinctes. */
export async function getPublicStats(): Promise<{ evidence: number; sources: number } | null> {
  const supabase = getSupabase();
  const [ev, src] = await Promise.all([
    supabase.from("evidence_active").select("id", { count: "exact", head: true }),
    supabase.from("sources").select("id", { count: "exact", head: true }),
  ]);
  if (ev.error || src.error || ev.count == null || src.count == null) return null;
  return { evidence: ev.count, sources: src.count };
}

/**
 * Toutes les lignes d'une requête, page par page : l'API renvoie au plus 1 000
 * lignes par appel (réglage par défaut de Supabase) et la base en compte davantage.
 * La requête doit être triée sur une clé unique pour que les pages ne se chevauchent pas.
 */
const PAGE = 1000;
async function selectAll<T>(
  page: (from: number, to: number) => PromiseLike<{ data: T[] | null; error: { message: string } | null }>,
): Promise<T[]> {
  const out: T[] = [];
  for (let from = 0; ; from += PAGE) {
    const { data, error } = await page(from, from + PAGE - 1);
    if (error) throw new Error(error.message);
    out.push(...(data ?? []));
    if (!data || data.length < PAGE) return out;
  }
}

/** Liste des entités pour la page d'accueil. */
export async function listEntities() {
  const supabase = getSupabase();
  return selectAll((from, to) =>
    supabase
      .from("entities")
      .select("id, slug, display_name, legal_name, is_brand, parent_id, sector_id, country, animal_free")
      .order("is_brand")
      .order("display_name")
      .order("id")
      .range(from, to),
  );
}

// --- Index de propriété (chargé une fois, réutilisé) -------------------------

interface EntityRow {
  id: string;
  slug: string;
  display_name: string | null;
  legal_name: string;
  is_brand: boolean;
  parent_id: string | null;
  sector_id: string | null;
}

/**
 * Charge la table `entities` une fois et expose la résolution de propriété.
 * Évite de refaire la requête complète pour chaque remontée de chaîne.
 */
async function loadEntityIndex() {
  const supabase = getSupabase();
  let rows: EntityRow[];
  try {
    rows = await selectAll<EntityRow>((from, to) =>
      supabase
        .from("entities")
        .select("id, slug, display_name, legal_name, is_brand, parent_id, sector_id")
        .order("id")
        .range(from, to),
    );
  } catch {
    return null;
  }
  const byId = new Map(rows.map((e) => [e.id, e]));
  const bySlug = new Map(rows.map((e) => [e.slug, e]));
  /** Remonte jusqu'au groupe racine (peut être l'entité elle-même). */
  const rootOf = (slug: string): EntityRow | null => {
    let cur = bySlug.get(slug) ?? null;
    if (!cur) return null;
    while (cur.parent_id && byId.get(cur.parent_id)) cur = byId.get(cur.parent_id)!;
    return cur;
  };
  return { rows, bySlug, rootOf };
}

const entityName = (e: EntityRow) => e.display_name ?? e.legal_name;

// --- Module civique : cartographie des votes des groupes politiques ----------

export interface CivicGroup { code: string; short_name: string; name: string; ordinal: number }
export interface CivicPosition {
  group_code: string;
  stance: "for" | "against" | "split" | "abstain";
  n_for: number | null;
  n_against: number | null;
  n_abstain: number | null;
  note: string | null;
}
export interface CivicVote {
  code: string;
  title: string;
  vote_date: string;
  pillar_code: string;
  chamber: string;
  source_url: string;
  alignment_note: string | null;
  total_for: number | null;
  total_against: number | null;
  total_abstain: number | null;
  positions: CivicPosition[];
}

/** Votes civiques (groupes politiques) + positions, groupés par vote. */
export async function getCivicData(): Promise<{ groups: CivicGroup[]; votes: CivicVote[] }> {
  const supabase = getSupabase();
  const [{ data: groups }, { data: votes }, { data: positions }] = await Promise.all([
    supabase.from("political_groups").select("code, short_name, name, ordinal").order("ordinal"),
    supabase.from("civic_votes").select("id, code, title, vote_date, pillar_code, chamber, source_url, alignment_note, total_for, total_against, total_abstain").order("vote_date", { ascending: false }),
    supabase.from("civic_positions").select("vote_id, group_id, stance, n_for, n_against, n_abstain, note"),
  ]);
  // On relie les positions aux groupes via une requête légère id -> code.
  const { data: groupIds } = await supabase.from("political_groups").select("id, code");
  const codeById = new Map((groupIds ?? []).map((g: any) => [g.id, g.code]));
  const voteById = new Map((votes ?? []).map((v: any) => [v.id, v]));
  const posByVote = new Map<string, CivicPosition[]>();
  for (const p of positions ?? []) {
    const v = voteById.get((p as any).vote_id);
    if (!v) continue;
    const arr = posByVote.get(v.code) ?? [];
    arr.push({
      group_code: codeById.get((p as any).group_id) ?? "",
      stance: (p as any).stance,
      n_for: (p as any).n_for ?? null,
      n_against: (p as any).n_against ?? null,
      n_abstain: (p as any).n_abstain ?? null,
      note: (p as any).note ?? null,
    });
    posByVote.set(v.code, arr);
  }
  const outVotes: CivicVote[] = (votes ?? []).map((v: any) => ({
    code: v.code, title: v.title, vote_date: v.vote_date, pillar_code: v.pillar_code,
    chamber: v.chamber, source_url: v.source_url, alignment_note: v.alignment_note,
    total_for: v.total_for, total_against: v.total_against, total_abstain: v.total_abstain,
    positions: posByVote.get(v.code) ?? [],
  }));
  const outGroups: CivicGroup[] = (groups ?? []).map((g: any) => ({
    code: g.code, short_name: g.short_name, name: g.name, ordinal: g.ordinal,
  }));
  return { groups: outGroups, votes: outVotes };
}

/**
 * Remonte la chaîne de propriété jusqu'au groupe racine (le vrai bénéficiaire
 * économique). Renvoie null si l'entité est elle-même la racine.
 */
export interface OwnershipProof {
  owner: string;
  source_url: string;
  excerpt: string;
  observed_on: string;
  reviewer: string;
}

/** Preuves d'appartenance de l'entité à son groupe (citations du propriétaire). */
export async function getOwnershipProofs(slug: string): Promise<OwnershipProof[]> {
  const supabase = getSupabase();
  const { data: ent } = await supabase.from("entities").select("id").eq("slug", slug).maybeSingle();
  if (!ent) return [];
  const { data, error } = await supabase
    .from("entity_ownership_sources")
    .select("source_url, excerpt, observed_on, reviewer, owner:owner_id(display_name, legal_name)")
    .eq("entity_id", (ent as any).id)
    .order("observed_on", { ascending: false });
  if (error || !data) return [];
  return (data as any[]).map((r) => ({
    owner: r.owner?.display_name ?? r.owner?.legal_name ?? "",
    source_url: r.source_url, excerpt: r.excerpt, observed_on: r.observed_on, reviewer: r.reviewer,
  }));
}

export async function getOwnerGroup(slug: string): Promise<{ slug: string; name: string } | null> {
  const idx = await loadEntityIndex();
  if (!idx) return null;
  const root = idx.rootOf(slug);
  if (!root || root.slug === slug) return null; // l'entité est déjà la racine
  return { slug: root.slug, name: entityName(root) };
}

// --- Alternatives mieux notées ------------------------------------------------

/**
 * Entités du même secteur et de même nature dont la note est strictement
 * meilleure. L'I/O ici, les décisions dans `pickComparable` /
 * `selectAlternatives` (testées).
 *
 * ⚠️ Coût : un appel `compute_score_input` par candidat du secteur (26 au plus
 * aujourd'hui, secteur `food`). Tenable à l'échelle actuelle, intenable à celle
 * du million de marques : il faudra alors matérialiser les scores en base et ne
 * plus les recalculer à chaque affichage de fiche.
 */
export async function getAlternatives(
  slug: string,
  currentScore: number,
  limit = 4,
): Promise<Alternative[]> {
  const idx = await loadEntityIndex();
  if (!idx) return [];
  const self = idx.bySlug.get(slug);
  if (!self) return [];

  const candidates = pickComparable(idx.rows, self);
  if (candidates.length === 0) return [];

  // Notes lues dans le calcul mis en cache (toutes les entités) : une fiche ne
  // recalcule pas chaque concurrent de son secteur (indispensable à des milliers de marques).
  const all = new Map((await getAllScores()).map((s) => [s.slug, s]));
  const scored = candidates.map((e) => {
    const r = all.get(e.slug);
    if (!r) return null;
    return {
      slug: e.slug,
      name: entityName(e),
      grade: r.grade,
      score: r.score,
      confidence: r.confidence,
      publishable: r.publishable,
      root: idx.rootOf(e.slug)?.slug ?? null,
    } as ScoredCandidate;
  });

  const selfRoot = idx.rootOf(slug)?.slug ?? null;
  return selectAlternatives(
    scored.filter((x): x is ScoredCandidate => x !== null),
    currentScore,
    selfRoot,
    limit,
  );
}
