/**
 * Appels au site de l'Index (mêmes faits que les fiches web) : /api/code, /api/fiche, /api/recherche.
 * Tant que le site est privé, l'appli envoie le mot de passe saisi dans les Réglages (identifiant
 * HTTP Basic), gardé dans le coffre sécurisé du téléphone ; une fois le site public, il ne sert plus.
 */
import { ecrire, lire } from './stockage';

export const SITE_PAR_DEFAUT = 'https://awareness-score.vercel.app';
const CLE_SITE = 'index.site';
const CLE_UTILISATEUR = 'index.utilisateur';
const CLE_MOT_DE_PASSE = 'index.motdepasse';
const CLE_HISTORIQUE = 'index.historique';

export interface Reglages { site: string; utilisateur: string; motDePasse: string }

export async function lireReglages(): Promise<Reglages> {
  const [site, utilisateur, motDePasse] = await Promise.all([lire(CLE_SITE), lire(CLE_UTILISATEUR), lire(CLE_MOT_DE_PASSE)]);
  return { site: site || SITE_PAR_DEFAUT, utilisateur: utilisateur || 'diams', motDePasse: motDePasse || '' };
}

export async function enregistrerReglages(r: Reglages): Promise<void> {
  await Promise.all([
    ecrire(CLE_SITE, r.site.trim().replace(/\/+$/, '') || SITE_PAR_DEFAUT),
    ecrire(CLE_UTILISATEUR, r.utilisateur.trim() || null),
    ecrire(CLE_MOT_DE_PASSE, r.motDePasse || null),
  ]);
}

/** Base64 sans dépendance (en-tête d'authentification), pour les moteurs sans btoa. */
function base64(s: string): string {
  const octets = Array.from(new TextEncoder().encode(s));
  const a = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let out = '';
  for (let i = 0; i < octets.length; i += 3) {
    const [x, y, z] = [octets[i], octets[i + 1], octets[i + 2]];
    out += a[x >> 2] + a[((x & 3) << 4) | ((y ?? 0) >> 4)];
    out += y === undefined ? '=' : a[((y & 15) << 2) | ((z ?? 0) >> 6)];
    out += z === undefined ? '=' : a[z & 63];
  }
  return out;
}

export async function entetes(): Promise<Record<string, string>> {
  const r = await lireReglages();
  const h: Record<string, string> = { Accept: 'application/json' };
  if (r.motDePasse) h.Authorization = `Basic ${base64(`${r.utilisateur}:${r.motDePasse}`)}`;
  return h;
}

/** Adresse complète d'une image du site (« /logos/x.png ») ; les adresses externes restent telles quelles. */
export async function adresseImage(src: string | null | undefined): Promise<string | null> {
  if (!src) return null;
  if (/^https?:\/\//.test(src)) return src;
  return (await lireReglages()).site + src;
}

export class ErreurSite extends Error {
  constructor(message: string, public statut?: number) {
    super(message);
  }
}

async function appeler<T>(chemin: string): Promise<T> {
  const r = await lireReglages();
  let rep: Response;
  // Jamais d'attente sans fin : abandon au bout de 20 secondes.
  const arret = new AbortController();
  const minuterie = setTimeout(() => arret.abort(), 20000);
  try {
    rep = await fetch(r.site + chemin, { headers: await entetes(), signal: arret.signal });
  } catch {
    throw new ErreurSite(
      arret.signal.aborted
        ? 'Le site ne répond pas. Vérifiez votre réseau, puis réessayez.'
        : 'Pas de connexion au site. Vérifiez votre réseau, puis réessayez.',
    );
  } finally {
    clearTimeout(minuterie);
  }
  if (rep.status === 401) throw new ErreurSite("Le site est encore privé : saisissez son mot de passe dans les Réglages.", 401);
  const corps = await rep.json().catch(() => null);
  if (!corps) throw new ErreurSite(`Réponse illisible du site (code ${rep.status}).`, rep.status);
  return corps as T;
}

// Types de l'API (miroir de apps/web/lib/fiche-json.ts)
export type NiveauSignal = 'alerte' | 'vigilance';
export interface Signal { niveau: NiveauSignal; motif: string; regle: string }
export interface Fait {
  code: string;
  nom: string;
  niveau: 'groupe' | 'marque' | 'produit';
  etat: 'documente' | 'presume' | 'obligatoire_absent' | 'autre_forme' | 'aucune_info';
  valeur: string;
  raison: string | null;
  repere: string | null;
  signal: Signal | null;
  note: string | null;
  preuve: { source: string; solidite: 'officielle' | 'reconnue' | 'declarative'; date: string; url: string | null; citation: string | null; reprisDe: string | null } | null;
}
export interface Pilier {
  code: string;
  nom: string;
  icone: string;
  renseignes: number;
  total: number;
  cle: { nom: string; valeur: string; etat: string; signal: NiveauSignal | null } | null;
  faits: Fait[];
}
export interface Produit {
  code: string; nom: string; image: string | null; quantite: string | null; marques: string[]; base: string; lien: string;
  correspondance: 'exacte' | 'approchee' | 'proprietaire'; nomLu: string; phrase: string;
}
export interface Fiche {
  slug: string;
  nom: string;
  logo: string | null;
  proprietaire: { slug: string; nom: string; logo: string | null } | null;
  produit: Produit | null;
  alertes: { pilier: string; icone: string; niveau: NiveauSignal; motif: string; regle: string }[];
  piliers: Pilier[];
  renseignes: number;
  total: number;
}
export type ReponseFiche = { trouve: true; fiche: Fiche } | { trouve: false; raison: string; indisponible?: boolean; produit?: Omit<Produit, 'correspondance' | 'nomLu' | 'phrase'> };
export interface Resultat { slug: string; nom: string; marque: boolean; groupe: string | null; logo: string | null }

export const ficheParCode = (code: string) => appeler<ReponseFiche>(`/api/code/${encodeURIComponent(code)}`);
export const ficheParSlug = (slug: string) => appeler<ReponseFiche>(`/api/fiche/${encodeURIComponent(slug)}`);
export const rechercher = (q: string) => appeler<{ q: string; resultats: Resultat[] }>(`/api/recherche?q=${encodeURIComponent(q)}`);

// Historique des scans (sur le téléphone seulement : rien n'est envoyé)
export interface Scan { code: string; produit: string; marque: string; alertes: number; date: string }
export async function historique(): Promise<Scan[]> {
  try {
    return JSON.parse((await lire(CLE_HISTORIQUE)) || '[]');
  } catch {
    return [];
  }
}
export async function noterScan(s: Scan): Promise<void> {
  const h = (await historique()).filter((x) => x.code !== s.code);
  await ecrire(CLE_HISTORIQUE, JSON.stringify([s, ...h].slice(0, 12)));
}
export async function effacerHistorique(): Promise<void> {
  await ecrire(CLE_HISTORIQUE, null);
}
