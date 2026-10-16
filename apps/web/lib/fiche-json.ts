/**
 * La fiche sous forme de données (API de l'appli mobile) : les mêmes faits, libellés, alertes,
 * repères et raisons que la page web, sans mise en page.
 */
import { raisonVide, type Carte } from "@/lib/carte";
import { EN_SAVOIR_PLUS, REPERES } from "@/lib/seuils";
import { logoDe } from "@/lib/logos";
import type { ProduitScanne } from "@/lib/data";

export const ICONES_PILIERS: Record<string, string> = { ANI: "🐄", ENV: "🌍", PLA: "🧴", WAT: "💧", LAB: "👥", SUP: "🔗", GOV: "🏛️", TAX: "💶", GEO: "🗺️", INV: "🏦" };

export function ficheEnJson(
  slug: string,
  carte: Carte,
  proprietaire: { slug: string; name: string } | null,
  scan: { produit: ProduitScanne; correspondance: string; nomLu: string; phrase: string } | null,
) {
  const logo = logoDe(slug);
  return {
    slug,
    nom: carte.nom,
    logo: logo?.src ?? null,
    proprietaire: proprietaire ? { slug: proprietaire.slug, nom: proprietaire.name, logo: logoDe(proprietaire.slug)?.src ?? null } : null,
    produit: scan ? { ...scan.produit, correspondance: scan.correspondance, nomLu: scan.nomLu, phrase: scan.phrase } : null,
    alertes: carte.signaux.map((f) => ({ pilier: f.pilier, icone: ICONES_PILIERS[f.pilier] ?? "", niveau: f.signal!.niveau, motif: f.signal!.motif, regle: f.signal!.regle })),
    piliers: carte.piliers.map((p) => ({
      code: p.code,
      nom: p.nom,
      icone: ICONES_PILIERS[p.code] ?? "",
      renseignes: p.documentes,
      total: p.total,
      cle: p.cle ? { nom: p.cle.nom, valeur: p.cle.valeur, etat: p.cle.etat, signal: p.cle.signal?.niveau ?? null } : null,
      faits: p.faits.map((f) => ({
        code: f.code,
        nom: f.nom,
        niveau: f.niveau,
        etat: f.etat,
        valeur: f.etat === "aucune_info" ? raisonVide(f)[0] : f.valeur,
        raison: f.etat === "aucune_info" ? raisonVide(f)[1] : null,
        repere: f.etat === "documente" ? REPERES[f.code] ?? null : null,
        enSavoirPlus: f.etat === "documente" ? EN_SAVOIR_PLUS[f.code] ?? null : null,
        signal: f.signal ? { niveau: f.signal.niveau, motif: f.signal.motif, regle: f.signal.regle } : null,
        note: f.note,
        preuve: f.preuve
          ? { source: f.preuve.source, solidite: f.preuve.solidite, date: f.preuve.date, url: f.preuve.url, citation: f.preuve.citation, reprisDe: f.preuve.reprisDe }
          : null,
      })),
    })),
    renseignes: carte.documentes,
    total: carte.total,
  };
}
