/**
 * Logos des groupes et des marques (base constituée par pipeline/outils_collecte/logos_wikidata.py) :
 * icône officielle enregistrée sur le site, logo de Wikimedia Commons retrouvé par identifiant
 * officiel (LEI, SIREN) ou par le groupe propriétaire, sinon icône du site officiel. Un logo sert
 * à reconnaître l'entreprise ; il ne prouve rien.
 */
import LOGOS from "./logos.json";

export interface Logo { src: string; origine: string }
const TABLE = LOGOS as Record<string, Logo>;
export function logoDe(slug: string): Logo | null {
  return TABLE[slug] ?? null;
}
