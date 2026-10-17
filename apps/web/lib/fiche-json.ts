/**
 * La fiche sous forme de données (API de l'appli mobile) : les mêmes faits, libellés, alertes,
 * repères et raisons que la page web, sans mise en page.
 */
import { raisonVide, type Carte } from "@/lib/carte";
import { EN_SAVOIR_PLUS, REPERES } from "@/lib/seuils";
import { logoDe } from "@/lib/logos";
import type { ProduitLu, ProduitScanne } from "@/lib/data";
import type { AlternativesPilier } from "@/lib/alternatives-piliers";

export const ICONES_PILIERS: Record<string, string> = { ANI: "🐄", ENV: "🌍", PLA: "🧴", WAT: "💧", LAB: "👥", SUP: "🔗", GOV: "🏛️", TAX: "💶", GEO: "🗺️", INV: "🏦" };

export function ficheEnJson(
  slug: string,
  carte: Carte,
  proprietaire: { slug: string; name: string } | null,
  scan: { produit: ProduitScanne; correspondance: string; nomLu: string; phrase: string } | null,
  extras: { estMarque?: boolean; produitsLus?: ProduitLu[]; alternatives?: AlternativesPilier } = {},
) {
  const logo = logoDe(slug);
  return {
    slug,
    nom: carte.nom,
    logo: logo?.src ?? null,
    proprietaire: proprietaire ? { slug: proprietaire.slug, nom: proprietaire.name, logo: logoDe(proprietaire.slug)?.src ?? null } : null,
    produit: scan ? { ...scan.produit, correspondance: scan.correspondance, nomLu: scan.nomLu, phrase: scan.phrase } : null,
    // nom : intitulé de l'indicateur, assez court pour une étiquette d'alerte dans l'en-tête de l'appli.
    alertes: carte.signaux.map((f) => ({ pilier: f.pilier, icone: ICONES_PILIERS[f.pilier] ?? "", niveau: f.signal!.niveau, motif: f.signal!.motif, regle: f.signal!.regle, nom: f.nom, code: f.code })),
    piliers: carte.piliers.map((p) => ({
      code: p.code,
      nom: p.nom,
      icone: ICONES_PILIERS[p.code] ?? "",
      renseignes: p.documentes,
      total: p.total,
      cle: p.cle ? { nom: p.cle.nom, valeur: p.cle.valeur, etat: p.cle.etat, signal: p.cle.signal?.niveau ?? null } : null,
      // Alternatives : marques du même secteur, d'un autre groupe, qui remplissent le critère affiché.
      alternatives: extras.alternatives?.[p.code]
        ? { ...extras.alternatives[p.code], marques: extras.alternatives[p.code].marques.map((m) => ({ ...m, logo: logoDe(m.slug)?.src ?? null })) }
        : null,
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
          ? { source: f.preuve.source, solidite: f.preuve.solidite, date: f.preuve.date, url: f.preuve.url, citation: f.preuve.citation, reprisDe: f.preuve.reprisDe, copie: !!f.preuve.copie }
          : null,
      })),
    })),
    renseignes: carte.documentes,
    total: carte.total,
    estMarque: !!extras.estMarque,
    // Produits lus (fiches du site de la marque ou étiquettes photographiées), ingrédients recopiés.
    produitsLus: (extras.produitsLus ?? []).map((x) => ({
      nom: x.nom, url: x.url, statut: x.statut, animaux: x.animaux, douteux: x.douteux, ingredients: x.ingredients,
      preuveVegetale: x.preuveVegetale, date: x.date, origine: x.origine, achat: x.achat, nature: x.nature,
    })),
  };
}
