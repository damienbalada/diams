/**
 * Code-barres → marque de l'Index (logique pure).
 *
 * Le produit est lu dans Open Food Facts (ou Open Beauty Facts, Open Products Facts) : base collaborative, sous licence
 * ouverte, qui donne le NOM DE MARQUE ÉCRIT SUR LE PRODUIT, tel que saisi par les contributeurs
 * (« President », « Nutella, Ferrero », « COCA-COLA SERVICES SA/NV »). Ce n'est pas une preuve :
 * seulement le moyen de savoir de quelle marque il s'agit. Deux rapprochements :
 *   - exact    : le nom normalisé est celui d'une marque (ou d'un groupe) de l'Index ;
 *   - approché : le nom commence par le nom complet d'une marque de l'Index (« coca cola services
 *                sa nv » → « coca cola »), d'au moins 4 lettres. La fiche le dit en toutes lettres.
 *   - à défaut, le début du NOM DU PRODUIT (« coca-cola » quand la marque n'est pas saisie) : approché ;
 *   - à défaut, le PROPRIÉTAIRE déclaré dans la base (« Unilever » pour Marmite) : la fiche du
 *     propriétaire, avec la mention que ce lien n'est pas vérifié.
 * Une marque passe devant un groupe ; à égalité, le nom le plus long gagne. Rien de sûr : null.
 */

export interface EntiteNom { slug: string; noms: string[]; is_brand: boolean }
export type Correspondance = "exacte" | "approchee" | "proprietaire";
export interface Rapprochement {
  slug: string;
  correspondance: Correspondance;
  nomLu: string;
  /** Marque citée en premier sur le produit mais absente de l'Index (on montre son groupe). */
  marqueNonSuivie?: string;
  /** La fiche montrée est celle d'un groupe, pas d'une marque. */
  groupe?: boolean;
}

/** « Président », « PRESIDENT », « président® » → « president ». */
export function normaliser(s: string): string {
  return s
    .normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[®™©]/g, "")
    .replace(/[’'`]/g, "")
    .replace(/&/g, " et ")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

/** Mots trop génériques pour identifier une marque à eux seuls. */
const GENERIQUES = new Set(["bio", "marque", "groupe", "france", "sas", "sa", "the", "les", "la", "le", "de", "du", "produit", "nature"]);

/** Code-barres plausible : 8 à 14 chiffres (EAN-8, UPC-A, EAN-13, GTIN-14). */
export function codeValide(code: string): boolean {
  return /^\d{8,14}$/.test(code);
}

export function rapprocher(
  marquesLues: string[],
  entites: EntiteNom[],
  autres: { nomProduit?: string | null; proprietaire?: string | null } = {},
): Rapprochement | null {
  const index = new Map<string, EntiteNom[]>();
  for (const e of entites) {
    for (const n of new Set(e.noms.map(normaliser).filter(Boolean))) {
      if (!index.has(n)) index.set(n, []);
      index.get(n)!.push(e);
    }
  }
  const meilleure = (l: EntiteNom[]) => [...l].sort((a, b) => Number(b.is_brand) - Number(a.is_brand))[0];
  const exact = (lu: string) => {
    const n = normaliser(lu);
    if (!n || GENERIQUES.has(n)) return null;
    const l = index.get(n);
    return l?.length ? meilleure(l) : null;
  };
  // Approché : un nom lu plus long qu'une marque (« Danone Belux nv ») désigne une société ; à nom
  // égal, le groupe passe donc devant la marque.
  const approche = (lu: string) => {
    const n = normaliser(lu);
    let gagnant: { e: EntiteNom; long: number } | null = null;
    for (const [nom, l] of index) {
      if (nom.replace(/ /g, "").length < 4 || GENERIQUES.has(nom)) continue;
      if (n === nom || n.startsWith(nom + " ")) {
        const e = n === nom ? meilleure(l) : [...l].sort((a, b) => Number(a.is_brand) - Number(b.is_brand))[0];
        if (!gagnant || nom.length > gagnant.long) gagnant = { e, long: nom.length };
      }
    }
    return gagnant?.e ?? null;
  };
  const lus = marquesLues.flatMap((m) => m.split(",")).map((m) => m.trim()).filter(Boolean);
  // 1. Exact, dans l'ordre où le produit cite ses marques (la première est la plus précise).
  for (const [i, lu] of lus.entries()) {
    const e = exact(lu);
    if (!e) continue;
    // « Marmite, Unilever » : la marque n'est pas suivie, seul son groupe l'est.
    if (i > 0 && !e.is_brand) return { slug: e.slug, correspondance: "proprietaire", nomLu: lu, marqueNonSuivie: lus[0] };
    return { slug: e.slug, correspondance: "exacte", nomLu: lu };
  }
  // 2. Approché : le nom lu commence par le nom entier d'une marque (au moins 4 lettres).
  for (const lu of lus) { const e = approche(lu); if (e) return { slug: e.slug, correspondance: "approchee", nomLu: lu }; }
  // 3. Marque non saisie : le début du nom du produit.
  if (!lus.length && autres.nomProduit) {
    const e = approche(autres.nomProduit);
    if (e) return { slug: e.slug, correspondance: "approchee", nomLu: autres.nomProduit };
  }
  // 4. Le propriétaire déclaré dans la base collaborative (non vérifié).
  for (const p of (autres.proprietaire ?? "").split(",").map((x) => x.trim()).filter(Boolean)) {
    const e = exact(p) ?? approche(p);
    if (e) return { slug: e.slug, correspondance: "proprietaire", nomLu: p, ...(lus[0] ? { marqueNonSuivie: lus[0] } : {}) };
  }
  return null;
}

/** Ajoute à un rapprochement l'indication « c'est un groupe ». */
export function avecGenre(r: Rapprochement | null, entites: EntiteNom[]): Rapprochement | null {
  if (!r) return r;
  const e = entites.find((x) => x.slug === r.slug);
  return e && !e.is_brand ? { ...r, groupe: true } : r;
}
