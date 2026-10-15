/**
 * Seuils d'alerte (décision de l'éditeur, 15/10/2026) — logique pure.
 *
 * Le site ne note pas : il signale. Pour chaque indicateur qui s'y prête, un seuil dit quand un
 * fait documenté mérite une alerte (rouge, ⚠️) ou un point de vigilance (orange). Chaque seuil
 * s'appuie sur une référence qu'on peut citer (loi, directive, moyenne publiée du classement) ;
 * quand il n'en existe pas, la règle le dit : « choix de l'Index ». La règle est affichée à côté
 * de chaque signal, pour que le lecteur la juge lui-même.
 *
 * Pas de seuil pour les données qui dépendent trop du secteur (intensité carbone, intensité
 * d'eau), ni pour les données de contexte (dépenses de lobbying).
 */

export type NiveauSignal = "alerte" | "vigilance";
export interface Signal {
  niveau: NiveauSignal;
  /** Ce qui déclenche le signal, en quelques mots (« 6,6 % des points de transparence »). */
  motif: string;
  /** Le seuil et sa référence, en une phrase. */
  regle: string;
}

export interface FaitEvalue {
  code: string;
  etat: string;
  valeurNum: number | null;
  citation: string | null;
}

const nf = (x: number, d = 1) => x.toLocaleString("fr-FR", { maximumFractionDigits: d });
const a = (motif: string, regle: string): Signal => ({ niveau: "alerte", motif, regle });
const v = (motif: string, regle: string): Signal => ({ niveau: "vigilance", motif, regle });
const note = (re: RegExp, s: string) => s.match(re)?.[1] ?? null;

/** Règles affichées dans la méthodologie et la légende, par indicateur. */
export const REGLES: Record<string, { alerte: string; vigilance?: string; reference: string }> = {
  ANI_EXPLOITATION: { alerte: "un produit issu de l'exploitation animale est documenté", vigilance: "exploitation non documentée dans un secteur où elle est la règle", reference: "choix de l'Index" },
  ANI_BBFAW_TIER: { alerte: "niveau 6 sur 6", vigilance: "niveau 5 sur 6", reference: "échelle du classement BBFAW : niveau 6, aucun signe que le bien-être animal soit à l'ordre du jour ; niveau 5, à l'ordre du jour mais peu de preuves de mise en œuvre" },
  ENV_CDP_CLIMATE: { alerte: "note F", vigilance: "note D ou D-", reference: "échelle du CDP : F, l'entreprise n'a pas répondu alors qu'elle y était invitée ; D, plus bas niveau pour une entreprise qui répond" },
  WAT_CDP: { alerte: "note F", vigilance: "note D ou D-", reference: "échelle du CDP : F, l'entreprise n'a pas répondu alors qu'elle y était invitée ; D, plus bas niveau pour une entreprise qui répond" },
  ENV_GHG_TREND: { alerte: "émissions en hausse", vigilance: "baisse de moins de 4,2 % par an", reference: "4,2 % par an : rythme minimal de baisse des objectifs alignés sur 1,5 °C de la SBTi" },
  ENV_SBTI_VALIDATED: { alerte: "—", vigilance: "engagement retiré", reference: "export de la SBTi : l'entreprise s'était engagée à fixer un objectif et ne l'a pas fait dans le délai" },
  ENV_GREENWASHING: { alerte: "décision d'une autorité", reference: "décision publique d'une autorité" },
  PLA_POLLUTER: { alerte: "parmi les dix plus gros pollueurs plastique", reference: "audit mondial des marques de Break Free From Plastic" },
  PLA_REDUCTION: { alerte: "plastique vierge en hausse", reference: "choix de l'Index : toute hausse" },
  SUP_FTI_SCORE: { alerte: "moins de 10 % des points", vigilance: "moins de 26 % des points", reference: "Fashion Transparency Index 2023 : moyenne des 250 marques, 26 % ; 28 % des marques sont entre 0 et 10 %" },
  SUP_LIVING_WAGE: { alerte: "note E", vigilance: "note D", reference: "échelle du Fashion Checker : E, la marque ne verse ni ne prétend verser de salaire vital" },
  SUP_KNOWTHECHAIN: { alerte: "moins de 10 sur 100", vigilance: "moins de 20 sur 100", reference: "KnowTheChain 2023, alimentation et boissons : moyenne 16 sur 100, la moitié des entreprises sous 10 ; seuil de vigilance : choix de l'Index" },
  LAB_EGAPRO_INDEX: { alerte: "moins de 75 sur 100", vigilance: "moins de 85 sur 100", reference: "code du travail : sous 75, l'entreprise doit prendre des mesures de correction ; sous 85, elle doit fixer des objectifs de progression" },
  LAB_GENDER_PAYGAP: { alerte: "écart de 15 % ou plus", vigilance: "écart de 5 % ou plus", reference: "directive européenne 2023/970 : à partir de 5 %, l'employeur doit évaluer l'écart avec les représentants du personnel ; alerte : trois fois ce seuil, choix de l'Index" },
  LAB_CEO_PAY_RATIO: { alerte: "300 fois ou plus", vigilance: "100 fois ou plus", reference: "choix de l'Index : 100 fois, le dirigeant gagne en un an ce que le salarié médian gagne en un siècle" },
  GOV_SANCTIONS: { alerte: "sanction d'une autorité", reference: "décision publique d'une autorité" },
  GOV_BOARD_GENDER: { alerte: "moins de 20 % de femmes", vigilance: "moins de 40 % de femmes", reference: "loi Copé-Zimmermann : 40 % au minimum dans les conseils des sociétés cotées en France ; alerte : la moitié de ce minimum" },
  GOV_BOARD_INDEP: { alerte: "—", vigilance: "moins d'un tiers d'indépendants", reference: "code Afep-Medef : au moins un tiers d'indépendants, même dans une société contrôlée" },
  TAX_EFFECTIVE_RATE: { alerte: "—", vigilance: "taux effectif sous 15 %", reference: "impôt minimum mondial de l'OCDE : 15 % ; un taux bas une année peut aussi venir de pertes ou de crédits d'impôt" },
  GEO_RUSSIA_EXIT: { alerte: "activité poursuivie en Russie", vigilance: "activité réduite ou investissements gelés", reference: "statuts de la base Leave Russia (KSE Institute)" },
  GEO_CONFLICT_TIES: { alerte: "implication documentée", reference: "choix de l'Index : toute implication documentée par une source publique" },
};

/** Signal d'un fait, ou null s'il ne franchit aucun seuil. */
export function evaluer(f: FaitEvalue): Signal | null {
  const r = REGLES[f.code];
  if (f.etat === "obligatoire_absent") return a("obligatoire, non publié", "la loi impose cette donnée et la lecture du rapport officiel confirme qu'elle n'y est pas");
  if (f.code === "ANI_EXPLOITATION" && f.etat === "presume") return v("exploitation animale présumée", r.vigilance!);
  if (f.etat !== "documente" || !r) return null;
  const x = f.valeurNum;
  const c = f.citation ?? "";
  const ref = r.reference;
  switch (f.code) {
    case "ANI_EXPLOITATION": return a("produits issus de l'exploitation animale", "un seul produit d'origine animale suffit");
    case "ANI_BBFAW_TIER":
      if (x === null) return null;
      return x >= 6 ? a("niveau 6 sur 6 au classement BBFAW", ref) : x >= 5 ? v("niveau 5 sur 6 au classement BBFAW", ref) : null;
    case "ENV_CDP_CLIMATE": case "WAT_CDP": {
      const n = note(/note ([A-F][+-]?)/, c);
      return n === "F" ? a("note F : pas de réponse au CDP", ref) : n?.startsWith("D") ? v(`note ${n} au CDP`, ref) : null;
    }
    case "ENV_GHG_TREND":
      if (x === null) return null;
      return x > 0 ? a(`émissions en hausse de ${nf(x, 2)} % par an`, ref) : x > -4.2 ? v(`baisse de ${nf(-x, 2)} % par an seulement`, ref) : null;
    case "ENV_SBTI_VALIDATED": return /engagement retiré/.test(c) ? v("engagement climat retiré", ref) : null;
    case "ENV_GREENWASHING": return a("allégations environnementales trompeuses", ref);
    case "PLA_POLLUTER": return a("parmi les plus gros pollueurs plastique", ref);
    case "PLA_REDUCTION": return x !== null && x > 0 ? a(`plastique vierge en hausse de ${nf(x, 2)} % par an`, ref) : null;
    case "SUP_FTI_SCORE":
      if (x === null) return null;
      return x < 10 ? a(`${nf(x)} % des points de transparence`, ref) : x < 26 ? v(`${nf(x)} % des points de transparence`, ref) : null;
    case "SUP_LIVING_WAGE": {
      const n = note(/note ([A-E])/, c);
      return n === "E" ? a("aucun salaire vital versé chez les fournisseurs", ref) : n === "D" ? v("note D sur le salaire vital", ref) : null;
    }
    case "SUP_KNOWTHECHAIN":
      if (x === null) return null;
      return x < 10 ? a(`${nf(x, 0)}/100 contre le travail forcé`, ref) : x < 20 ? v(`${nf(x, 0)}/100 contre le travail forcé`, ref) : null;
    case "LAB_EGAPRO_INDEX":
      if (x === null) return null;
      return x < 75 ? a(`index Égapro de ${nf(x, 0)}/100`, ref) : x < 85 ? v(`index Égapro de ${nf(x, 0)}/100`, ref) : null;
    case "LAB_GENDER_PAYGAP": {
      if (x === null) return null;
      const e = Math.abs(x), qui = x < 0 ? "en faveur des femmes" : "en faveur des hommes";
      return e >= 15 ? a(`écart de salaire de ${nf(e)} % ${qui}`, ref) : e >= 5 ? v(`écart de salaire de ${nf(e)} % ${qui}`, ref) : null;
    }
    case "LAB_CEO_PAY_RATIO":
      if (x === null) return null;
      return x >= 300 ? a(`dirigeant payé ${nf(x, 0)} fois le salaire médian`, ref) : x >= 100 ? v(`dirigeant payé ${nf(x, 0)} fois le salaire médian`, ref) : null;
    case "GOV_SANCTIONS": return a("sanctionné par une autorité", ref);
    case "GOV_BOARD_GENDER":
      if (x === null) return null;
      return x < 20 ? a(`${nf(x)} % de femmes au conseil`, ref) : x < 40 ? v(`${nf(x)} % de femmes au conseil`, ref) : null;
    case "GOV_BOARD_INDEP": return x !== null && x < 33 ? v(`${nf(x)} % d'administrateurs indépendants`, ref) : null;
    // Pas de vigilance sur un exercice en perte : un taux bas ou négatif n'y dit rien de l'impôt payé.
    case "TAX_EFFECTIVE_RATE": return x !== null && x < 15 && !/perte|loss/i.test(c) ? v(`taux d'impôt effectif de ${nf(x)} %`, ref) : null;
    case "GEO_RUSSIA_EXIT":
      if (/activité poursuivie/.test(c)) return a("activité poursuivie en Russie", ref);
      if (/investissements gelés/.test(c)) return v("toujours présent en Russie, investissements gelés", ref);
      return /activité réduite/.test(c) ? v("toujours présent en Russie, activité réduite", ref) : null;
    case "GEO_CONFLICT_TIES": return a("implication dans un conflit ou une occupation", ref);
  }
  return null;
}

/** Ordre d'affichage : alertes d'abord. */
export const RANG_SIGNAL: Record<NiveauSignal, number> = { alerte: 0, vigilance: 1 };

/** Repère pour lire un chiffre : l'échelle de la source, ou une valeur de comparaison citée. */
export const REPERES: Record<string, string> = {
  ENV_CDP_CLIMATE: "Échelle du CDP : de A (meilleure note) à D-, F = l'entreprise n'a pas répondu",
  WAT_CDP: "Échelle du CDP : de A (meilleure note) à D-, F = l'entreprise n'a pas répondu",
  ENV_GHG_TREND: "Repère : une baisse d'au moins 4,2 % par an est nécessaire pour rester sous 1,5 °C (SBTi)",
  PLA_REDUCTION: "Repère : évolution moyenne par an sur la période publiée par l'entreprise",
  SUP_LIVING_WAGE: "Échelle du Fashion Checker : de A (salaire vital versé) à E (ni versé ni promis)",
  SUP_FTI_SCORE: "Repère : moyenne des 250 grandes marques de mode en 2023, 26 %",
  SUP_KNOWTHECHAIN: "Repère : moyenne des 60 plus grands groupes alimentaires en 2023, 16/100",
  LAB_EGAPRO_INDEX: "Repère : sous 75/100, la loi impose des mesures de correction ; sous 85, des objectifs",
  LAB_GENDER_PAYGAP: "Repère : à partir de 5 %, l'employeur doit l'analyser avec les représentants du personnel (directive UE)",
  LAB_CEO_PAY_RATIO: "Repère : à 100 fois, le dirigeant gagne en un an ce que le salarié médian gagne en un siècle",
  GOV_BOARD_GENDER: "Repère : 40 % au minimum dans les sociétés cotées en France (loi Copé-Zimmermann)",
  GOV_BOARD_INDEP: "Repère : au moins un tiers recommandé par le code Afep-Medef",
  TAX_EFFECTIVE_RATE: "Repère : impôt minimum mondial de l'OCDE, 15 % ; taux normal en France, 25 %",
  ANI_BBFAW_TIER: "Échelle du BBFAW : niveau 1 (meilleur) à 6 (aucun engagement visible)",
  ENV_TAXONOMY_CAPEX: "Part des investissements de l'année conformes à la taxonomie verte européenne",
  ENV_GHG_INTENSITY: "Dépend beaucoup du secteur : à comparer entre entreprises du même secteur",
  WAT_INTENSITY: "Dépend beaucoup du secteur : à comparer entre entreprises du même secteur",
  ENV_SBTI_VALIDATED: "La SBTi vérifie que l'objectif climat est compatible avec l'accord de Paris ; c'est un engagement, pas un résultat",
};
