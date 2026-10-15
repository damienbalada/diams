/**
 * Chargement d'une fiche (marque ou groupe), commun à la page web, à la page par code-barres et à
 * l'API de l'appli mobile. Une erreur sur un bloc secondaire n'empêche jamais la carte.
 */
import {
  getScorePayload, getOwnerGroup, getOwnershipProofs, getJournal, getMemeRayon, getMarques, getMarquesGroupe,
  getEstMarque, getProduits, type OwnershipProof,
} from "@/lib/data";
import { construireCarte } from "@/lib/carte";

export async function chargerFiche(slug: string) {
  const payload = await getScorePayload(slug);
  if (!payload) return null;
  const [journal, proprietaire, preuves, memeRayon, marques, marquesGroupe, estMarque] = await Promise.all([
    getJournal(slug).catch(() => []),
    getOwnerGroup(slug).catch(() => null),
    getOwnershipProofs(slug).catch(() => [] as OwnershipProof[]),
    getMemeRayon(slug).catch(() => []),
    getMarques(slug).catch(() => []),
    getMarquesGroupe(slug).catch(() => null),
    getEstMarque(slug).catch(() => false),
  ]);
  const carte = construireCarte(payload as any, journal, { estMarque });
  const estGroupe = (payload.ownership_chain ?? []).length <= 1 || marques.length > 0;
  const produits = estMarque ? await getProduits(slug).catch(() => null) : null;
  return { carte, estGroupe: estGroupe && !proprietaire, proprietaire, preuvesPropriete: preuves, memeRayon, marques, marquesGroupe, estMarque, produits };
}
