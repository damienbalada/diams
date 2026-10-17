// Alternatives par pilier (17/10/2026). L'Index ne note personne : une alternative est une marque du
// même rayon (même secteur), d'un autre groupe, qui remplit un critère vérifiable et sourcé dans ce
// pilier, affiché tel quel (« groupe noté A ou A- au questionnaire climat du CDP »). Une donnée publiée
// par le groupe vaut pour ses marques, comme sur les fiches.

/** Critère de chaque pilier, en toutes lettres (le lecteur sait pourquoi une marque est proposée). */
export const CRITERES: Record<string, string> = {
  ANI: "entièrement végétales (prouvé), sinon qui proposent des produits 100 % végétaux",
  ENV: "dont le groupe a la note A ou A- au questionnaire climat du CDP",
  PLA: "dont le groupe réduit son plastique neuf",
  WAT: "dont le groupe a la note A ou A- au questionnaire eau du CDP",
  LAB: "dont le groupe a une politique de salaire décent",
  SUP: "dont le groupe publie la liste de ses fournisseurs",
  GOV: "certifiées B Corp (elles-mêmes ou leur groupe)",
  TAX: "dont le groupe publie ses impôts pays par pays",
  GEO: "dont le groupe a quitté la Russie",
};

const norm = (s: string) => s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");

export interface EntiteAlt { id: string; slug: string; nom: string; is_brand: boolean; parent_id: string | null; sector_id: string | null }
export interface MarqueAlt { slug: string; nom: string; groupe: string | null; second?: boolean }
export type AlternativesPilier = Record<string, { critere: string; marques: MarqueAlt[]; autres: number }>;

/**
 * Alternatives de chaque pilier pour une entité.
 * @param remplit pilier → identifiants des entités qui remplissent le critère (preuve propre).
 * @param second  pilier → critère de repli (ANI : offre végétale), proposé après le critère principal.
 */
export function alternativesParPilier(
  rows: EntiteAlt[], slug: string, remplit: Record<string, Set<string>>, second: Record<string, Set<string>> = {}, max = 6,
): AlternativesPilier {
  const byId = new Map(rows.map((e) => [e.id, e]));
  const self = rows.find((e) => e.slug === slug);
  if (!self?.sector_id) return {};
  const chaine = (e: EntiteAlt) => {
    const out: EntiteAlt[] = [];
    for (let c: EntiteAlt | undefined = e, i = 0; c && i < 20; c = c.parent_id ? byId.get(c.parent_id) : undefined, i++) out.push(c);
    return out;
  };
  const racine = (e: EntiteAlt) => chaine(e).at(-1)!;
  const maRacine = racine(self).id;
  const candidats = rows
    .filter((e) => e.is_brand && e.sector_id === self.sector_id && e.slug !== slug && racine(e).id !== maRacine)
    .sort((a, b) => a.nom.localeCompare(b.nom, "fr"));
  const out: AlternativesPilier = {};
  for (const [pilier, critere] of Object.entries(CRITERES)) {
    const ok = (ids: Set<string> | undefined, e: EntiteAlt) => !!ids && chaine(e).some((c) => ids.has(c.id));
    const premiers = candidats.filter((e) => ok(remplit[pilier], e));
    const seconds = candidats.filter((e) => !premiers.includes(e) && ok(second[pilier], e));
    const tous = [...premiers.map((e) => ({ e, second: false })), ...seconds.map((e) => ({ e, second: true }))];
    if (!tous.length) continue;
    out[pilier] = {
      critere,
      marques: tous.slice(0, max).map(({ e, second }) => {
        const g = racine(e);
        // Groupe affiché seulement s'il dit autre chose que le nom de la marque (« Holibelly (société) »).
        const meme = norm(g.nom).startsWith(norm(e.nom)) || norm(e.nom).startsWith(norm(g.nom));
        return { slug: e.slug, nom: e.nom, groupe: g.id !== e.id && !meme ? g.nom : null, second };
      }),
      autres: Math.max(0, tous.length - max),
    };
  }
  return out;
}
