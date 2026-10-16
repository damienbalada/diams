import { unstable_cache } from "next/cache";
import { getSupabase } from "./supabase";
import type { JournalEntree, MarqueDuGroupe } from "./carte";
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
export const getAllScores = unstable_cache(computeAllScores, ["all-scores-v182"], { revalidate: 600 });

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
  // et de son propriétaire direct (index Égapro, v0.7.5) — compute_score_input : même
  // racine, même propriétaire, même secteur, même pays et même indicateur « sans
  // exploitation animale » donnent exactement la même note, calculée une fois.
  const memo = new Map<string, Promise<ScoreCore | null>>();
  const keyOf = (e: any): string | null => {
    if (!own) return null;
    const root = rootOf(e);
    if (root.id === e.id || own.has(e.id)) return null;
    return [root.id, e.is_brand ? e.parent_id ?? "" : "", e.sector_id ?? "", e.country ?? "", e.animal_free ? 1 : 0].join("|");
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
  country: string | null;
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
        .select("id, slug, display_name, legal_name, is_brand, parent_id, sector_id, country")
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

/** Pays du siège (code ISO) de l'entité et de son groupe racine, pour les seuils qui dépendent d'une loi nationale. */
export async function getPays(slug: string): Promise<{ pays: string | null; paysGroupe: string | null }> {
  const idx = await loadEntityIndex();
  if (!idx) return { pays: null, paysGroupe: null };
  const e = idx.bySlug.get(slug) ?? null;
  const root = idx.rootOf(slug);
  return { pays: e?.country ?? null, paysGroupe: root?.country ?? e?.country ?? null };
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

// --- Refonte : carte d'identité (PLAN_REFONTE.md) -----------------------------------------


/** Identifiants de l'entité et de toute sa chaîne de propriétaires (jusqu'à la racine). */
async function chainIds(slug: string): Promise<string[]> {
  const idx = await loadEntityIndex();
  if (!idx) return [];
  const byId = new Map(idx.rows.map((e) => [e.id, e]));
  const out: string[] = [];
  let cur = idx.bySlug.get(slug) ?? null;
  for (let i = 0; cur && i < 20; i++) {
    out.push(cur.id);
    cur = cur.parent_id ? byId.get(cur.parent_id) ?? null : null;
  }
  return out;
}

/**
 * Journal de relecture utile à la fiche : obligations lues (absence confirmée, autre forme)
 * et recherches sans résultat, pour l'entité et ses propriétaires (une marque reprend les
 * indicateurs de son groupe et l'index Égapro de son propriétaire direct).
 */
export async function getJournal(slug: string): Promise<JournalEntree[]> {
  const ids = await chainIds(slug);
  if (!ids.length) return [];
  const supabase = getSupabase();
  const { data, error } = await supabase
    .from("indicator_reviews")
    .select("outcome, detail, checked_on, source_url, indicator:indicator_id(code)")
    .in("entity_id", ids)
    .in("outcome", ["absence_confirmee", "autre_forme", "non_trouvee"])
    .order("checked_on", { ascending: false })
    .limit(500);
  if (error || !data) return [];
  return (data as any[]).map((r) => ({
    indicator_code: r.indicator?.code ?? "", outcome: r.outcome, detail: r.detail, checked_on: r.checked_on, source_url: r.source_url,
  }));
}

/**
 * Autres marques du même rayon (même secteur, autre groupe propriétaire), sans ordre de
 * mérite : rangées par ordre alphabétique. Le lecteur compare les fiches lui-même.
 */
export async function getMemeRayon(slug: string, limit = 8): Promise<{ slug: string; name: string; group: string | null }[]> {
  const idx = await loadEntityIndex();
  if (!idx) return [];
  const self = idx.bySlug.get(slug);
  if (!self) return [];
  const selfRoot = idx.rootOf(slug)?.slug ?? null;
  const others = pickComparable(idx.rows, self)
    .filter((e) => e.slug !== slug && (idx.rootOf(e.slug)?.slug ?? null) !== selfRoot)
    .map((e) => {
      const root = idx.rootOf(e.slug);
      return { slug: e.slug, name: entityName(e), group: root && root.slug !== e.slug ? entityName(root) : null };
    });
  // Choix stable mais varié d'une fiche à l'autre : on part d'un point dépendant du slug.
  others.sort((a, b) => a.name.localeCompare(b.name, "fr"));
  if (others.length <= limit) return others;
  let h = 0;
  for (const ch of slug) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  const start = h % others.length;
  return [...others.slice(start), ...others.slice(0, start)].slice(0, limit).sort((a, b) => a.name.localeCompare(b.name, "fr"));
}

/** Liste des marques et groupes pour l'index (sans note). */
export async function listIndex(): Promise<{ slug: string; name: string; is_brand: boolean; group: string | null }[]> {
  const idx = await loadEntityIndex();
  if (!idx) return [];
  return idx.rows
    .map((e) => {
      const root = idx.rootOf(e.slug);
      return { slug: e.slug, name: entityName(e), is_brand: e.is_brand, group: root && root.slug !== e.slug ? entityName(root) : null };
    })
    .sort((a, b) => a.name.localeCompare(b.name, "fr", { sensitivity: "base" }));
}

/** Marques détenues par l'entité, directement ou via ses filiales (fiche d'un groupe). */
export async function getMarques(slug: string): Promise<{ slug: string; name: string }[]> {
  const idx = await loadEntityIndex();
  if (!idx) return [];
  const self = idx.bySlug.get(slug);
  if (!self) return [];
  const byId = new Map(idx.rows.map((e) => [e.id, e]));
  const sous = (e: EntityRow) => {
    for (let cur: EntityRow | undefined = e, i = 0; cur?.parent_id && i < 20; i++) {
      if (cur.parent_id === self.id) return true;
      cur = byId.get(cur.parent_id);
    }
    return false;
  };
  return idx.rows.filter((e) => e.is_brand && sous(e)).map((e) => ({ slug: e.slug, name: entityName(e) }))
    .sort((a, b) => a.name.localeCompare(b.name, "fr", { sensitivity: "base" }));
}

/** Vrai si l'entité est une marque (et non un groupe ou une société). */
export async function getEstMarque(slug: string): Promise<boolean> {
  const idx = await loadEntityIndex();
  return !!idx?.bySlug.get(slug)?.is_brand;
}

/**
 * Niveau « marques » d'un groupe (décision de l'éditeur, 15/10/2026 : groupe / marque / produit
 * pour tout le site) : les marques suivies du groupe propriétaire (pour une marque) ou du groupe
 * lui-même, chacune avec les indicateurs documentés pour elle-même (preuves approuvées, non
 * contestées), et leur pilier. Sert aux résumés « ses marques » et au résumé animal.
 */
export async function getMarquesGroupe(slug: string): Promise<{ groupe: { slug: string; name: string }; marques: MarqueDuGroupe[] } | null> {
  const idx = await loadEntityIndex();
  if (!idx) return null;
  const racine = idx.rootOf(slug);
  if (!racine) return null;
  const byId = new Map(idx.rows.map((e) => [e.id, e]));
  const sous = (e: EntityRow) => {
    for (let cur: EntityRow | undefined = e, i = 0; cur?.parent_id && i < 20; i++) {
      if (cur.parent_id === racine.id) return true;
      cur = byId.get(cur.parent_id);
    }
    return false;
  };
  const marques = idx.rows.filter((e) => e.is_brand && sous(e));
  if (!marques.length) return null;
  const supabase = getSupabase();
  const codes = new Map<string, Map<string, string>>();
  // Par blocs de 150 marques, et par pages de 1 000 lignes (limite du serveur de la base).
  for (let i = 0; i < marques.length; i += 150) {
    for (let page = 0; ; page++) {
    const { data, error } = await supabase
      .from("evidence")
      .select("id, entity_id, indicator:indicator_id(code, dimension:dimension_id(code))")
      .in("entity_id", marques.slice(i, i + 150).map((m) => m.id))
      .eq("review_status", "approved")
      .eq("contested", false)
      .order("id")
      .range(page * 1000, page * 1000 + 999);
    if (error) throw new Error(error.message);
    for (const r of (data ?? []) as any[]) {
      if (!r.indicator?.code) continue;
      if (!codes.has(r.entity_id)) codes.set(r.entity_id, new Map());
      codes.get(r.entity_id)!.set(r.indicator.code, r.indicator.dimension?.code ?? "");
    }
    if ((data ?? []).length < 1000) break;
    }
  }
  return {
    groupe: { slug: racine.slug, name: entityName(racine) },
    marques: marques
      .map((m) => ({ slug: m.slug, nom: entityName(m), codes: [...(codes.get(m.id) ?? new Map()).entries()].map(([code, pilier]) => ({ code, pilier })) }))
      .sort((a, b) => a.nom.localeCompare(b.nom, "fr", { sensitivity: "base" })),
  };
}

/** Fait marquant d'une vitrine : ce qui est prouvé pour l'entité ou repris de son groupe racine. */
export interface Vitrine {
  slug: string;
  name: string;
  group: string | null;
  faits: number;
  exploitation: boolean;
  vegetale: boolean;
  sanction: boolean;
}

/**
 * Vitrines de l'accueil (« les plus connues », « les plus recherchées ») : pour chaque slug, le
 * nombre de faits sourcés (propres ou repris du groupe racine) et trois signaux tirés des preuves
 * approuvées. Rien n'est calculé ni noté : une simple lecture des preuves.
 */
export async function getVitrines(slugs: string[]): Promise<Vitrine[]> {
  const supabase = getSupabase();
  const entities: any[] = await listEntities();
  const byId = new Map<string, any>(entities.map((e) => [e.id, e]));
  const bySlug = new Map<string, any>(entities.map((e) => [e.slug, e]));
  const root = (e: any) => {
    let cur = e;
    for (let i = 0; i < 20 && cur.parent_id && byId.has(cur.parent_id); i++) cur = byId.get(cur.parent_id);
    return cur;
  };
  const choisies = slugs.map((s) => bySlug.get(s)).filter(Boolean);
  const ids = [...new Set(choisies.flatMap((e) => [e.id, root(e).id]))];
  const [{ data: ind }, { data: ev }] = await Promise.all([
    supabase.from("indicators").select("id, code"),
    supabase.from("evidence_active").select("entity_id, indicator_id").in("entity_id", ids),
  ]);
  const code = new Map<string, string>((ind ?? []).map((i: any) => [i.id, i.code]));
  const parEntite = new Map<string, string[]>();
  for (const r of ev ?? []) parEntite.set(r.entity_id, [...(parEntite.get(r.entity_id) ?? []), code.get(r.indicator_id) ?? ""]);
  return choisies.map((e) => {
    const r = root(e);
    const propres = parEntite.get(e.id) ?? [];
    const groupe = r.id === e.id ? [] : parEntite.get(r.id) ?? [];
    const tous = [...propres, ...groupe];
    return {
      slug: e.slug,
      name: String(e.display_name ?? e.legal_name),
      group: r.id === e.id ? null : String(r.display_name ?? r.legal_name),
      faits: tous.length,
      // Même règle que la fiche : l'exploitation animale se prouve marque par marque, jamais
      // par la seule preuve du groupe (une marque de mode peut ne pas vendre de cuir).
      exploitation: propres.includes("ANI_EXPLOITATION") && !propres.includes("ANI_ANIMAL_FREE"),
      vegetale: propres.includes("ANI_ANIMAL_FREE"),
      sanction: tous.includes("GOV_SANCTIONS"),
    };
  });
}

/**
 * Produits vendus sous une marque alimentaire ou de boisson, d'après Open Food Facts (base
 * collaborative, licence ouverte ODbL). Ils servent à reconnaître la marque en rayon : ce ne
 * sont pas des preuves, et la fiche le dit. Filtre exact sur l'étiquette de marque et la France,
 * produits les plus scannés d'abord.
 */
export interface Produit { code: string; nom: string; image: string | null }
const SECTEURS_PRODUITS = new Set(["food", "beverages", "wines_spirits"]);
const etiquetteOff = (n: string) =>
  n.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/['’]/g, "-").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
export const getProduits = unstable_cache(
  async (slug: string): Promise<{ total: number; produits: Produit[]; lien: string } | null> => {
    const idx = await loadEntityIndex();
    const self = idx?.bySlug.get(slug);
    if (!self || !self.is_brand || !self.sector_id) return null;
    const { data: sec } = await getSupabase().from("sectors").select("code").eq("id", self.sector_id).maybeSingle();
    if (!sec || !SECTEURS_PRODUITS.has((sec as any).code)) return null;
    const tag = etiquetteOff(entityName(self));
    if (!tag) return null;
    const q = encodeURIComponent(`brands_tags:"${tag}" AND countries_tags:"en:france"`);
    try {
      const r = await fetch(
        `https://search.openfoodfacts.org/search?q=${q}&sort_by=-unique_scans_n&page_size=12&fields=code,product_name,product_name_fr,image_small_url`,
        { headers: { "User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)" }, signal: AbortSignal.timeout(6000) },
      );
      if (!r.ok) return null;
      const d = (await r.json()) as { count?: number; hits?: any[] };
      const produits = (d.hits ?? [])
        .map((h) => ({ code: String(h.code), nom: String(h.product_name_fr || h.product_name || "").trim(), image: h.image_small_url ?? null }))
        .filter((p) => p.nom);
      return produits.length ? { total: d.count ?? produits.length, produits, lien: `https://fr.openfoodfacts.org/marque/${tag}` } : null;
    } catch {
      return null;
    }
  },
  ["produits-off-v1"],
  { revalidate: 86400 },
);

/**
 * Produit lu par son code-barres dans Open Food Facts, puis Open Beauty Facts (bases collaboratives,
 * licence ouverte). Sert à savoir de quelle marque il s'agit ; ce n'est pas une preuve.
 */
export interface ProduitScanne { code: string; nom: string; image: string | null; quantite: string | null; marques: string[]; proprietaire: string | null; base: string; lien: string }
/** Les bases n'ont pas répondu (panne, limite d'appels) : jamais mis en cache comme « inconnu ». */
export class BasesIndisponibles extends Error {}
const lireProduit = unstable_cache(
  async (code: string): Promise<ProduitScanne | null> => {
    const bases = [
      { nom: "Open Food Facts", hote: "https://world.openfoodfacts.org", fiche: "https://fr.openfoodfacts.org/produit/" },
      { nom: "Open Beauty Facts", hote: "https://world.openbeautyfacts.org", fiche: "https://fr.openbeautyfacts.org/produit/" },
    ];
    let panne = false;
    for (const b of bases) {
      try {
        // Une seule nouvelle tentative après une limite d'appels (429) ou une erreur passagère (5xx).
        const lire = () => fetch(`${b.hote}/api/v2/product/${code}?fields=code,product_name,product_name_fr,brands,brand_owner,image_front_small_url,quantity`, {
          headers: { "User-Agent": "IndexDesMarques/0.1 (DIAMS verifier; +https://awareness-score.vercel.app)" },
          signal: AbortSignal.timeout(8000),
        });
        let r = await lire();
        if (r.status === 429 || r.status >= 500) {
          await new Promise((ok) => setTimeout(ok, 1500));
          r = await lire();
        }
        if (r.status === 404) continue;
        if (!r.ok) { panne = true; continue; }
        const d = (await r.json()) as { status?: number; product?: any };
        if (d.status !== 1 || !d.product) continue;
        const p = d.product;
        // La fiche produit ne donne parfois qu'une partie des marques (ou aucune) : on complète avec
        // l'index de recherche de la même base (« Lidl, J.D. Gross », « Marmite, Unilever »).
        let enPlus: string[] = [];
        if (b.nom === "Open Food Facts") {
          try {
            const s = await fetch(`https://search.openfoodfacts.org/search?q=${encodeURIComponent(`code:"${code}"`)}&page_size=1&fields=brands,brand_owner`, {
              headers: { "User-Agent": "IndexDesMarques/0.1 (DIAMS verifier; +https://awareness-score.vercel.app)" },
              signal: AbortSignal.timeout(6000),
            });
            if (s.ok) {
              const h = ((await s.json()) as { hits?: any[] }).hits?.[0];
              enPlus = (Array.isArray(h?.brands) ? h.brands : String(h?.brands ?? "").split(",")).map((x: string) => String(x).trim()).filter(Boolean);
              if (!p.brand_owner && h?.brand_owner) p.brand_owner = h.brand_owner;
            }
          } catch {
            /* l'index de recherche est un complément : sans lui, on garde la fiche produit */
          }
        }
        const propres = String(p.brands ?? "").split(",").map((x: string) => x.trim()).filter(Boolean);
        const marques = [...propres, ...enPlus.filter((x) => !propres.some((y) => y.toLowerCase() === x.toLowerCase()))];
        return {
          code, nom: String(p.product_name_fr || p.product_name || "").trim() || "Produit sans nom",
          image: p.image_front_small_url ?? null, quantite: p.quantity ? String(p.quantity) : null,
          marques,
          proprietaire: p.brand_owner ? String(p.brand_owner) : null, base: b.nom, lien: b.fiche + code,
        };
      } catch {
        panne = true;
      }
    }
    // Une panne lève une erreur : unstable_cache ne garde que les réponses réelles.
    if (panne) throw new BasesIndisponibles("Open Food Facts ne répond pas pour l'instant.");
    return null;
  },
  ["produit-par-code-v3"],
  { revalidate: 86400 },
);
export async function getProduitParCode(code: string): Promise<ProduitScanne | null> {
  return lireProduit(code);
}

/** Les noms de chaque entité (affiché et légal), pour reconnaître une marque lue sur un produit. */
export async function listeNomsEntites(): Promise<{ slug: string; noms: string[]; is_brand: boolean }[]> {
  const idx = await loadEntityIndex();
  if (!idx) return [];
  return idx.rows.map((e) => ({ slug: e.slug, noms: [e.display_name ?? "", e.legal_name ?? ""].filter(Boolean), is_brand: e.is_brand }));
}
