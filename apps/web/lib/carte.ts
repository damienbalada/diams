/**
 * Carte d'identité d'une marque ou d'un groupe (refonte, PLAN_REFONTE.md) — logique pure.
 *
 * Plus de note : chaque indicateur est un FAIT sourcé, dans l'échelle de sa source, ou un
 * état explicite quand on ne sait rien. Cinq états :
 *   - documenté          : une preuve, avec sa source, sa date et la citation exacte ;
 *   - présumé            : exploitation animale non documentée dans un secteur à enjeu ;
 *   - obligatoire absent : la loi impose la donnée et la lecture du rapport a confirmé son
 *                          absence (journal de relecture) — jamais sans cette lecture ;
 *   - autre forme        : publiée, mais pas sous la forme que la loi exige (sous-périmètre,
 *                          par zone, écart ajusté…) ;
 *   - aucune information : rien de publié, rien d'obligatoire ; on dit où l'on a cherché.
 * La « solidité » d'un pilier ne dépend que des sources utilisées.
 */

import { evaluer, RANG_SIGNAL, type Signal } from "./seuils.ts";

export type Etat = "documente" | "presume" | "obligatoire_absent" | "autre_forme" | "aucune_info";
export type Solidite = "officielle" | "reconnue" | "declarative";

export interface IndicateurEntree {
  code: string;
  name: string;
  dimension_code: string;
  unit: string | null;
  direction?: string;
  mandatory?: boolean;
  mandatory_regimes?: string[];
  exemption?: string | null;
  group_level?: boolean;
}
export interface PreuveEntree {
  indicator_code: string;
  tier: string;
  nature?: string;
  value_numeric: number | string | null;
  normalized_value?: number | string | null;
  observed_on: string;
  event_date?: string | null;
  specificity: number;
  source_code?: string;
  source_url: string | null;
  source_name?: string;
  excerpt: string | null;
  inherited_from?: string | null;
  contested?: boolean;
}
export interface JournalEntree {
  indicator_code: string;
  outcome: string;
  detail: string | null;
  checked_on: string;
  source_url?: string | null;
}

export interface Fait {
  code: string;
  nom: string;
  pilier: string;
  etat: Etat;
  /** Valeur courte, dans l'échelle de la source (« 92/100 », « Note A », « Vend des produits issus de l'exploitation animale : lait »). */
  valeur: string;
  contexte: boolean;
  /** Niveau auquel le fait est établi : le groupe (ou la société propriétaire), la marque, ou
   *  certains produits (décision de l'éditeur, 15/10/2026, pour tout le site). */
  niveau: Niveau;
  preuve?: {
    source: string;
    url: string | null;
    solidite: Solidite;
    /** Date de l'événement si connue, sinon date du relevé. */
    date: string;
    dateEvenement: boolean;
    citation: string | null;
    reprisDe: string | null;
    conteste: boolean;
    valeurNum: number | null;
  };
  /** Obligation légale qui s'applique (régimes). */
  obligation: string[];
  /** Journal de relecture : ce qui a été lu ou cherché pour cet indicateur. */
  note: string | null;
  /** Alerte ou point de vigilance, d'après les seuils (seuils.ts). */
  signal: Signal | null;
  /** Raison d'une dispense de publication (CSRD : thème déclaré non matériel…). */
  exemption: string | null;
}

export interface Pilier {
  code: string;
  nom: string;
  faits: Fait[];
  cle: Fait | null;
  documentes: number;
  total: number;
  solidite: Solidite | null;
}

export interface Carte {
  slug: string;
  nom: string;
  chaine: string[];
  piliers: Pilier[];
  chronologie: Fait[];
  /** Faits signalés (alertes puis points de vigilance). */
  signaux: Fait[];
  documentes: number;
  total: number;
}

export const ORDRE_PILIERS = ["ANI", "ENV", "PLA", "WAT", "LAB", "SUP", "GOV", "TAX", "GEO", "INV"];

const SOLIDITE: Record<string, Solidite> = { regulatory: "officielle", audited_ngo: "reconnue", press: "declarative", crowd: "declarative" };
const RANG: Record<Solidite, number> = { officielle: 1, reconnue: 2, declarative: 3 };

const nf = (x: number, d = 1) => x.toLocaleString("fr-FR", { maximumFractionDigits: d });
const m1 = (re: RegExp, s: string) => (s.match(re)?.[1] ?? "").trim() || null;
const num = (v: number | string | null | undefined) => (v === null || v === undefined || v === "" ? null : Number(v));

/** Valeur courte d'une preuve, dans l'échelle de sa source (aucune conversion en note). */
export function valeurCourte(code: string, unit: string | null, p: PreuveEntree): string {
  const x = p.excerpt ?? "";
  const v = num(p.value_numeric);
  switch (code) {
    case "ANI_EXPLOITATION": {
      // Ce que la marque vend d'origine animale (« fromage », « cuir »), ou l'activité déclarée au registre.
      const ape = m1(/APE\) [\d.]+[A-Z] - ([^»]+)»/, x);
      if (ape) return `Activité déclarée au registre : ${ape.trim().toLowerCase()}`;
      // Jusqu'à la dernière parenthèse : le produit peut en contenir une (« laine (vêtements) »).
      const produit = m1(/exploitation animale \((.+)\)/, x);
      return produit ? `Vend des produits issus de l'exploitation animale : ${produit}` : "Exploitation animale documentée";
    }
    case "ANI_ANIMAL_FREE": return "Marque entièrement végétale (prouvé)";
    case "INV_SUSTAINABLE_FINANCE":
      return /Green Bond Framework|bonds framework|cadre d.émission|cadre établi/i.test(x)
        ? "Cadre structuré d'émission d'obligations vertes ou sociales" : "Émet des obligations vertes ou sociales (cadre non cité)";
    case "ANI_OFFRE_VEGETALE": return "Propose au moins un produit 100 % végétal";
    case "ANI_FUR_FREE": return "Membre du label « sans fourrure »";
    case "ANI_TESTING": return /Leaping Bunny de Cruelty Free/.test(x) ? "Certifiée sans tests sur les animaux (Leaping Bunny)" : "Arrêt des tests sur les animaux déclaré (sans certification du groupe)";
    // Matières animales de la mode : objectif ou politique publiés (aucune interdiction ni certification constatée).
    case "ANI_DOWN_RDS":
      if (/sans certification/i.test(x)) return "Plumage à vif exclu (politique, sans certification)";
      if (/virgin down|duvet neuf exclu/i.test(x)) return "Duvet et plumes neufs exclus (seulement recyclés)";
      return /objectif|horizon/i.test(x) ? "Objectif de duvet recyclé ou certifié (norme RDS, sans plumage à vif)" : "Duvet certifié (norme RDS) exigé";
    case "ANI_WOOL_MULESING":
      if (/sans certification/i.test(x)) return "Laine issue du mulesing refusée (politique, sans certification)";
      if (/must be certified|exigée/i.test(x)) return "Laine neuve certifiée sans mulesing (norme RWS) exigée";
      return /objectif|horizon/i.test(x) ? "Objectif de laine recyclée ou certifiée (norme RWS, sans mulesing)" : "Politique sur la laine publiée";
    case "ANI_ANGORA_MOHAIR":
      if (/angora et mohair exclus/i.test(x)) return "Angora et mohair exclus";
      return /angora rabbit hair|angora exclu/i.test(x) ? "Angora exclu ; mohair certifié (norme RMS) exigé" : "Politique sur l'angora et le mohair publiée";
    case "ANI_EXOTIC_SKINS": return /does not accept the use of exotic|exclues/i.test(x) ? "Peaux exotiques exclues" : "Peaux exotiques : approvisionnement certifié ou audité (pas d'interdiction)";
    case "ANI_LEATHER_TRACE": {
      const part = m1(/(\d+ ?%) étaient certifiées LWG/, x);
      if (part) return `${part} des tanneries du groupe certifiées par le Leather Working Group`;
      if (/tanneries certified by the Leather Working Group/.test(x)) return "Cuir de tanneries certifiées (Leather Working Group) exigé";
      return "Objectifs de traçabilité et de certification des tanneries (Leather Working Group)";
    }
    case "ANI_BBFAW_TIER": return v === null ? "Évalué" : `Niveau ${nf(v, 0)} sur 6 au classement du bien-être animal`;
    case "GEO_RUSSIA_EXIT": { const s = m1(/» — ([^;.]+)/, x) ?? m1(/— ([^;.]+)/, x); return s ? `Russie : ${s.replace(/ en Russie$/, "")}` : "Documenté"; }
    case "GOV_SANCTIONS": case "ENV_GREENWASHING": {
      // « Autorité de la concurrence, décision n° 23-D-15 du 29/12/2023 : … ; amende de 0,566 M€ »
      const autorite = (x.split(/[,:(]/)[0] ?? "").trim();
      const an = m1(/du \d{2}\/\d{2}\/(\d{4})/, x);
      const amende = m1(/amendes? (?:civiles? )?(?:de(?: plus de)?|d’un montant de) ([\d  ,.]+ ?(?:M€|Md€|M£|MA\$|M\$|Md\$|€|millions? d[’']euros|milliards? d[’']euros|euros))/, x)
        ?? m1(/fine of ([\d.,]+ (?:million|billion)? ?euros)/i, x);
      const quoi = code === "GOV_SANCTIONS" ? "Sanctionné" : "Allégations écologiques trompeuses relevées";
      // Article devant le nom de l'autorité : « l'Autorité… », « la Commission… », « la CNIL ».
      const art = !autorite ? "" : /^(Commission|Cour|DGCCRF|CNIL|FTC|CMA|SEC)\b/.test(autorite) ? "la " : /^(Jury|Bureau)\b/.test(autorite) ? "le " : /^ASA\b/.test(autorite) ? "l'" : /^[AEÉIOU][a-zé]/.test(autorite) ? "l'" : "";
      return `${quoi} par ${autorite ? art + autorite : "une autorité"}${an ? ` (${an})` : ""}${amende ? ` : amende de ${amende.replace(/MA\$$/, "M$ australiens")}${/pour chacune des deux filiales/.test(x) ? " pour chacune de deux filiales" : ""}` : ""}`;
    }
    case "GEO_CONFLICT_TIES": return "Implication dans un conflit ou une occupation, documentée";
    case "GEO_LOBBYING_ALIGN": { const n = m1(/Climate Policy Engagement ([A-F][+-]?)/, x); return n ? `Note ${n} d'InfluenceMap sur le lobbying climat` : "Évalué par InfluenceMap"; }
    case "LAB_LIVING_WAGE": { const s = m1(/\((salaire (?:décent|adéquat)[^)]*)\)/, x); return s ? s[0].toUpperCase() + s.slice(1) : "Salaire décent : engagement publié"; }
    case "INV_RESPONSIBLE_POLICY": if (/Principes pour l.[Ii]nvestissement [Rr]esponsable|\bUN PRI\b|signataires? des PRI/.test(x)) return "Signataire des Principes pour l'investissement responsable de l'ONU (par ses filiales de gestion ou d'assurance)"; {
      const s = m1(/— ([^:«]+) :/, x); return s ? s[0].toUpperCase() + s.slice(1) : "Politique publiée"; }
    case "GEO_LOBBYING_TRANSP": return /HATVP|répertoire/i.test(x + (p.source_name ?? "")) ? "Inscrit au répertoire des lobbyistes (HATVP)" : "Inscrit au registre européen des lobbyistes";
    case "GEO_LOBBYING_SPEND": { const s = m1(/déclarés[^:]*: ([^,]+(?:€[^,]*€)?)/, x) ?? (v === null ? null : `${nf(v, 0)} €`); return s ? `${s} de lobbying déclarés par an` : "Déclaré"; }
    case "ENV_CDP_CLIMATE": return `Note ${m1(/note ([A-F][+-]?)/, x) ?? "?"} au questionnaire climat du CDP`;
    case "WAT_CDP": return `Note ${m1(/note ([A-F][+-]?)/, x) ?? "?"} au questionnaire eau du CDP`;
    case "ENV_SBTI_VALIDATED": return m1(/— (objectif[^(]+\([^)]*\))/, x) ?? m1(/— ([^(]+)\(/, x) ?? "Documenté";
    case "SUP_LIVING_WAGE": return `Note ${m1(/note ([A-E])/, x) ?? "?"} sur le salaire vital des ouvriers`;
    case "SUP_VIGILANCE_PLAN": return "Plan de vigilance publié";
    case "SUP_SUPPLIER_LIST": return /huileries de palme/.test(x) ? "Liste nominative des huileries de palme fournisseurs publiée (filière palme seulement)" : /régions de fabrication/.test(x) ? "Liste des fournisseurs et de leurs régions de fabrication publiée" : "Liste des sites de production fournisseurs publiée";
    case "ENV_SCOPE3_DISCLOSED": return "Émissions indirectes (scope 3) publiées";
    case "TAX_CBCR_PUBLISHED": return "Impôts publiés pays par pays";
    case "PLA_POLLUTER": return "Parmi les plus gros pollueurs plastique";
    case "SUP_FTI_SCORE": return v === null ? "Évalué" : `${nf(v)} % des points de transparence`;
    case "LAB_CEO_PAY_RATIO":
      if (v === null) return "Publié";
      // La Nef publie l'écart au salaire le plus bas, pas à la médiane (17/10/2026).
      if (/plus bas|lowest[- ]paid/i.test(x)) return `Le plus haut salaire vaut ${nf(v, v < 10 ? 2 : 0)} fois le plus bas`;
      return `Le dirigeant gagne ${nf(v, v < 20 ? 1 : 0)} fois le salaire médian`;
    case "LAB_GENDER_PAYGAP": return v === null ? "Publié" : v < 0 ? `${nf(-v)} % en faveur des femmes` : `${nf(v)} % en faveur des hommes`;
    case "LAB_EGAPRO_INDEX": return v === null ? "Publié" : `Index Égapro : ${nf(v, 0)}/100`;
    case "GOV_BCORP": return "Certifiée B Corp";
    case "GOV_BOARD_GENDER": return v === null ? "Publié" : `${nf(v)} % de femmes au conseil ${/conseil de surveillance|supervisory board/i.test(x) ? "de surveillance" : "d'administration"}`;
    case "GOV_EXEC_GENDER": return v === null ? "Publié" : `${nf(v)} % de femmes dans les instances dirigeantes (comité de direction)`;
    case "GOV_BOARD_INDEP": return v === null ? "Publié" : `${nf(v)} % d'administrateurs indépendants`;
    case "TAX_EFFECTIVE_RATE": return v === null ? "Publié" : `Taux effectif d'impôt : ${nf(v)} % du bénéfice avant impôt (charge comptable)`;
    case "WAT_CONTROVERSY": {
      // « Convention judiciaire d'intérêt public validée le 13/09/2022 … : amende d'intérêt public de 40 000 € … »
      if (/^Convention judiciaire d.intérêt public/.test(x)) {
        const anC = m1(/validée le \d{2}\/\d{2}\/(\d{4})/, x);
        const montant = m1(/amende d.intérêt public de ([\d  ]+ ?(?:€|M€))/, x);
        return `Convention judiciaire d'intérêt public pour infraction au droit de l'eau${anC ? ` (${anC})` : ""}${montant ? ` : amende de ${montant}` : ""}`;
      }
      // « … arrêté préfectoral de mise en demeure du 19/08/2026, site de Formerie … »
      const an = m1(/mise en demeure du \d{2}\/\d{2}\/(\d{4})/, x);
      const site = m1(/site de ([^,(]+)/, x);
      return `Mise en demeure de la préfecture portant sur l'eau${site ? ` (site de ${site.trim()}` : ""}${an ? `${site ? ", " : " ("}${an})` : site ? ")" : ""}`;
    }
    case "GEO_POL_FINANCING": return v === null ? "Publié" : v === 0 ? "Comité politique déclaré aux États-Unis, sans contribution ce cycle" : `${nf(v, 0)} $ versés à des candidats et comités politiques aux États-Unis (2025-2026)`;
    case "SUP_BHRRC_ALLEG": return v === null ? "Relayé" : `${nf(v, 0)} article${v > 1 ? "s" : ""} relayant des allégations en 12 mois (BHRRC)`;
    case "TAX_HAVEN_PRESENCE": return v === null ? "Publié" : v === 0 ? "Aucune filiale listée dans les dix premiers paradis fiscaux" : `Au moins ${nf(v, 0)} filiale${v > 1 ? "s" : ""} dans les dix premiers paradis fiscaux`;
    case "ENV_GHG_TREND": return v === null ? "Publié" : v > 0 ? `Émissions en hausse de ${nf(v, 2)} % par an` : `Émissions en baisse de ${nf(-v, 2)} % par an`;
    case "PLA_REDUCTION": return v === null ? "Publié" : v > 0 ? `Plastique neuf en hausse de ${nf(v, 2)} % par an` : `Plastique neuf en baisse de ${nf(-v, 2)} % par an`;
    case "PLA_RECYCLED": {
      // Trois mesures différentes selon le rapport : recyclabilité dès la conception, part de matière
      // recyclée, ou emballages consignés ; le libellé reprend celle que la preuve publie (17/10/2026).
      if (v === null) return "Publié";
      if (/biosourc/i.test(x)) return `${nf(v)} % de plastiques recyclés ou biosourcés dans les emballages`;
      if (/consign/i.test(x)) return `${nf(v)} % des produits en emballage consigné ou majoritairement recyclé`;
      if (/recyclables?|conçus pour le recyclage|prêts pour le recyclage|recycle-ready|recycleerbaar|designed (?:to be recyclable|for recycling)/i.test(x))
        return `${nf(v)} % d'emballages recyclables ou réutilisables`;
      const matiere = /réutilisés ou recyclés|reused or recycled/i.test(x) ? "matière recyclée ou réutilisée" : "matière recyclée";
      return `${nf(v)} % de ${matiere} dans les emballages${/plasti/i.test(x) && !/verre|glass/i.test(x) ? " plastiques" : ""}`;
    }
    case "ENV_TAXONOMY_CAPEX": return v === null ? "Publié" : `${nf(v)} % des investissements conformes à la taxonomie verte de l'UE (évaluation de l'entreprise)`;
    case "ENV_GHG_INTENSITY": return v === null ? "Publié" : `${nf(v, 0)} tonnes de CO₂ par million ${/M\$|U ?S ?D|dollar/i.test(x) && !/taux de change annuel moyen/i.test(x) ? "de dollars" : "d'euros"} de ventes`;
    case "WAT_INTENSITY": {
      if (v === null) return "Publié";
      // Le rapport publie soit les prélèvements, soit la consommation (ESRS E3-4 § 29) : le premier terme cité l'emporte.
      const c = x.search(/consomm|consumption/i), pr = x.search(/pr[ée]l[èe]v|withdraw/i);
      return `${nf(v, 0)} m³ d'eau ${c >= 0 && (pr < 0 || c < pr) ? "consommés" : "prélevés"} par million d'euros de ventes`;
    }
    case "SUP_KNOWTHECHAIN": return v === null ? "Évalué" : `${nf(v, 0)}/100 contre le travail forcé (KnowTheChain)`;
    case "INV_FOSSIL_FINANCING": return v === null ? "Documenté" : `${nf(v)} milliards de dollars liés aux énergies fossiles`;
    case "INV_SOLIDARITY_LABEL": return "Produits labellisés Finansol";
  }
  if (v === null) return "Documenté";
  switch (unit) {
    case "%": return `${nf(v)} %`;
    case "score/100": return `${nf(v, 0)}/100`;
    case "%/an": return `${v > 0 ? "+" : "−"}${nf(Math.abs(v), 2)} % par an`;
    case "tCO2e/M€": return `${nf(v, 0)} t CO₂e par M€ de chiffre d'affaires`;
  }
  return `${nf(v)}${unit ? ` ${unit}` : ""}`;
}

/** Indicateurs de décision dont la valeur normalisée est la gravité : la plus grave est affichée. */
const PAR_GRAVITE = new Set(["GOV_SANCTIONS"]);

/** Preuve retenue : la plus spécifique (propre à l'entité), puis la plus récente. Pour une sanction,
 *  la plus grave d'abord (méthode : « plusieurs décisions : la plus grave compte, et c'est elle que la
 *  fiche affiche »), puis la plus récente. */
function meilleure(ps: PreuveEntree[], code?: string): PreuveEntree | null {
  const g = (p: PreuveEntree) => (code && PAR_GRAVITE.has(code) ? Number(p.normalized_value ?? 0) : 0);
  return [...ps].sort((a, b) => b.specificity - a.specificity || g(b) - g(a)
    || (b.event_date ?? b.observed_on).localeCompare(a.event_date ?? a.observed_on))[0] ?? null;
}

/**
 * Trois niveaux, pour tout le site (décision de l'éditeur, 15/10/2026) :
 *   - groupe  : ce que publie le groupe (ou, pour Égapro, la société propriétaire directe) ;
 *   - marque  : ce qui est prouvé pour la marque elle-même ;
 *   - produit : ce qui ne vaut que pour certains produits (produits 100 % végétaux, épargne
 *               labellisée) et ne s'étend pas à la marque entière.
 * Un fait documenté est de niveau « marque » si sa preuve porte sur la marque elle-même, « groupe »
 * s'il est repris du groupe. Sur la fiche d'un groupe, tout ce qui n'est pas « produit » est
 * de niveau groupe.
 */
export type Niveau = "groupe" | "marque" | "produit";
export const NIVEAU_PRODUIT = new Set(["ANI_OFFRE_VEGETALE", "INV_SOLIDARITY_LABEL"]);
const NIVEAU_PROPRIETAIRE = new Set(["LAB_EGAPRO_INDEX", "GOV_EXEC_GENDER"]);
export function niveauDe(i: IndicateurEntree, p: PreuveEntree | null, estMarque: boolean): Niveau {
  if (NIVEAU_PRODUIT.has(i.code)) return "produit";
  if (!estMarque) return "groupe";
  if (p) return p.inherited_from ? "groupe" : "marque";
  return i.group_level || NIVEAU_PROPRIETAIRE.has(i.code) ? "groupe" : "marque";
}

/** Une marque du groupe et les indicateurs documentés pour elle-même (preuves approuvées). */
export interface MarqueDuGroupe { slug: string; nom: string; codes: { code: string; pilier: string }[] }

/** Résumé animal d'un groupe à partir de l'état de chacune de ses marques suivies. */
export type EtatAnimalMarque = "exploitation" | "vegetale" | "non_documentee";
export interface MarqueAnimale { slug: string; nom: string; etat: EtatAnimalMarque; offreVegetale: boolean }
export function marqueAnimale(m: MarqueDuGroupe): MarqueAnimale {
  const c = new Set(m.codes.map((x) => x.code));
  return {
    slug: m.slug, nom: m.nom, offreVegetale: c.has("ANI_OFFRE_VEGETALE"),
    etat: c.has("ANI_ANIMAL_FREE") ? "vegetale" : c.has("ANI_EXPLOITATION") ? "exploitation" : "non_documentee",
  };
}
/** Marques du groupe qui ont au moins une information propre documentée dans un pilier. */
export function marquesDocumentees(marques: MarqueDuGroupe[], pilier: string): MarqueDuGroupe[] {
  return marques.filter((m) => m.codes.some((c) => c.pilier === pilier));
}
export function resumeGroupe(marques: MarqueAnimale[]) {
  const n = (e: EtatAnimalMarque) => marques.filter((m) => m.etat === e).length;
  return {
    total: marques.length, exploitation: n("exploitation"), vegetale: n("vegetale"), nonDocumentee: n("non_documentee"),
    offreVegetale: marques.filter((m) => m.etat !== "vegetale" && m.offreVegetale).length,
  };
}

const SOURCES_CHERCHEES: [RegExp, string][] = [
  [/CDP/, "liste publique CDP"], [/SBTi/, "export SBTi"], [/Leave Russia/, "base Leave Russia (KSE)"],
  [/registre de transparence/, "registre européen"], [/HATVP/, "répertoire de la HATVP"],
  [/transparence de la mode/, "indice de transparence de la mode"], [/KnowTheChain/, "KnowTheChain"],
  [/BBFAW/, "classement BBFAW"], [/Fur Free/, "liste Fur Free Retailer"], [/Fashion Checker/, "Fashion Checker"],
  [/Finansol/, "liste Finansol"],
  [/Break Free From Plastic/, "audit Break Free From Plastic"],
  [/plateforme de l'Ademe/, "bilans GES déposés à l'Ademe"],
  [/Jury de déontologie publicitaire/, "avis du Jury de déontologie publicitaire"],
  [/Advertising Standards Authority/, "décisions de l'autorité britannique de la publicité (ASA)"],
  [/Business & Human Rights Resource Centre/, "Business & Human Rights Resource Centre"],
  [/Autorité de la concurrence/, "décisions de l'Autorité de la concurrence"],
  [/Géorisques/, "arrêtés de mise en demeure publiés sur Géorisques"],
  [/Commission électorale fédérale/, "fichiers de la Commission électorale fédérale (FEC)"],
  [/loi Rixain/, "déclarations de la loi Rixain"],
  [/aucun index Égapro/, "index Égapro"],
  [/base de données de l'ONU des entreprises impliquées dans les colonies/, "base de données de l'ONU sur les colonies israéliennes"],
  [/annuaire B Lab/, "annuaire B Corp de B Lab"],
  [/radar du devoir de vigilance/, "radar du devoir de vigilance (CCFD-Terre Solidaire, Sherpa) et site de l'entreprise"],
  [/annuaire Leaping Bunny/, "annuaire Leaping Bunny des marques sans tests sur les animaux"],
];

/** Construit la carte à partir de l'entrée de calcul (compute_score_input) et du journal. */
export function construireCarte(
  payload: { entity: { slug: string; name: string }; ownership_chain?: string[]; applicableIndicators: IndicateurEntree[]; evidence: PreuveEntree[]; dimensions: { code: string; name: string }[] },
  journal: JournalEntree[] = [],
  options: { estMarque?: boolean; pays?: string | null; paysGroupe?: string | null } = {},
): Carte {
  const estMarque = options.estMarque ?? (payload.ownership_chain ?? []).length > 1;
  const nomPilier = new Map(payload.dimensions.map((d) => [d.code, d.name]));
  const parCode = new Map<string, PreuveEntree[]>();
  for (const e of payload.evidence) {
    if (!parCode.has(e.indicator_code)) parCode.set(e.indicator_code, []);
    parCode.get(e.indicator_code)!.push(e);
  }
  const jparCode = new Map<string, JournalEntree[]>();
  for (const j of journal) {
    if (!jparCode.has(j.indicator_code)) jparCode.set(j.indicator_code, []);
    jparCode.get(j.indicator_code)!.push(j);
  }

  const bruts: Omit<Fait, "signal" | "exemption">[] = payload.applicableIndicators.map((i): Omit<Fait, "signal" | "exemption"> => {
    const p = meilleure(parCode.get(i.code) ?? [], i.code);
    const js = (jparCode.get(i.code) ?? []).sort((a, b) => b.checked_on.localeCompare(a.checked_on));
    const obligation = i.mandatory ? (i.mandatory_regimes ?? []) : [];
    const contexte = i.direction === "contextual";
    if (p) {
      return {
        code: i.code, nom: i.name, pilier: i.dimension_code, etat: "documente", valeur: valeurCourte(i.code, i.unit, p), contexte, obligation, note: null,
        niveau: niveauDe(i, p, estMarque),
        preuve: {
          source: p.source_name ?? p.source_code ?? "Source", url: p.source_url, solidite: SOLIDITE[p.tier] ?? "declarative",
          date: p.event_date ?? p.observed_on, dateEvenement: !!p.event_date, citation: p.excerpt, reprisDe: p.inherited_from ? (p.specificity === -2 ? `la filiale française ${p.inherited_from}` : p.inherited_from) : null,
          conteste: !!p.contested, valeurNum: num(p.value_numeric),
        },
      };
    }
    const lu = js.find((j) => j.outcome === "absence_confirmee" || j.outcome === "autre_forme");
    if (lu?.outcome === "autre_forme") {
      // Égapro « NC » : déclaration faite, index non calculable (cas prévu par la loi).
      const nc = /index non calculable/.test(lu.detail ?? "");
      return { code: i.code, nom: i.name, pilier: i.dimension_code, etat: "autre_forme", valeur: nc ? "Déclaré : index non calculable" : "Publié sous une autre forme", contexte, obligation, note: lu.detail, niveau: niveauDe(i, null, estMarque) };
    }
    if (lu && obligation.length) {
      return { code: i.code, nom: i.name, pilier: i.dimension_code, etat: "obligatoire_absent", valeur: "Obligatoire, non publié", contexte, obligation, note: lu.detail, niveau: niveauDe(i, null, estMarque) };
    }
    if (i.code === "ANI_EXPLOITATION") {
      return { code: i.code, nom: i.name, pilier: i.dimension_code, etat: "presume", valeur: "Non documentée, présumée dans ce secteur", contexte, obligation, note: null, niveau: niveauDe(i, null, estMarque) };
    }
    const cherche = [...new Set(js.filter((j) => j.outcome === "non_trouvee").map((j) => SOURCES_CHERCHEES.find(([re]) => re.test(j.detail ?? ""))?.[1]).filter(Boolean))];
    const date = js.find((j) => j.outcome === "non_trouvee")?.checked_on;
    // Lecture d'un rapport (« Rapport … lu : … ») : la phrase du journal est affichée telle quelle.
    const lecture = js.find((j) => j.outcome === "non_trouvee" && /^Rapport/.test(j.detail ?? ""))?.detail ?? null;
    // Taille officielle (répertoire Sirene) : dit pourquoi une PME ne publie pas ces données.
    const taille = js.find((j) => /^Catégorie d'entreprise/.test(j.detail ?? ""))?.detail ?? null;
    const notes = [lecture, taille, cherche.length ? `Cherché sans résultat (${cherche.join(", ")}), le ${date?.split("-").reverse().join("/")}.` : null].filter(Boolean);
    return {
      code: i.code, nom: i.name, pilier: i.dimension_code, etat: "aucune_info", valeur: "Aucune information", contexte, niveau: niveauDe(i, null, estMarque),
      obligation, note: notes.length ? notes.join(" ") : null,
    };
  });

  const exo = new Map(payload.applicableIndicators.map((i) => [i.code, i.exemption ?? null]));
  const faits: Fait[] = bruts.map((f) => ({
    ...f,
    exemption: exo.get(f.code) ?? null,
    signal: evaluer({ code: f.code, etat: f.etat, valeurNum: f.preuve?.valeurNum ?? null, citation: f.preuve?.citation ?? null, nom: f.nom,
      // Donnée reprise du groupe : c'est le pays du groupe qui compte (son conseil, sa loi).
      pays: (f.preuve?.reprisDe ? options.paysGroupe : options.pays) ?? options.pays ?? null }),
  }));

  const piliers: Pilier[] = [];
  for (const d of ORDRE_PILIERS) {
    const fs = faits.filter((f) => f.pilier === d);
    if (!fs.length) continue;
    const doc = fs.filter((f) => f.etat === "documente");
    const rangs = doc.map((f) => RANG[f.preuve!.solidite]);
    const moy = rangs.length ? rangs.reduce((a, b) => a + b, 0) / rangs.length : null;
    piliers.push({
      code: d, nom: nomPilier.get(d) ?? d, faits: fs, cle: faitCle(d, fs), documentes: doc.length, total: fs.length,
      solidite: moy === null ? null : moy <= 1.4 ? "officielle" : moy <= 2.2 ? "reconnue" : "declarative",
    });
  }
  const chronologie = faits.filter((f) => f.etat === "documente").sort((a, b) => b.preuve!.date.localeCompare(a.preuve!.date));
  return {
    slug: payload.entity.slug, nom: payload.entity.name, chaine: payload.ownership_chain ?? [payload.entity.name], piliers,
    chronologie, documentes: chronologie.length, total: faits.length,
    signaux: faits.filter((f) => f.signal).sort((a, b) => RANG_SIGNAL[a.signal!.niveau] - RANG_SIGNAL[b.signal!.niveau] || ORDRE_PILIERS.indexOf(a.pilier) - ORDRE_PILIERS.indexOf(b.pilier)),
  };
}

const PRIORITE: Record<string, string[]> = {
  ANI: ["ANI_EXPLOITATION", "ANI_ANIMAL_FREE", "ANI_BBFAW_TIER"],
  ENV: ["ENV_GHG_TREND", "ENV_CDP_CLIMATE", "ENV_SBTI_VALIDATED"],
  LAB: ["LAB_EGAPRO_INDEX", "LAB_GENDER_PAYGAP"],
  SUP: ["SUP_VIGILANCE_PLAN", "SUP_LIVING_WAGE", "SUP_KNOWTHECHAIN"],
  GOV: ["GOV_SANCTIONS", "GOV_BOARD_GENDER"],
  TAX: ["TAX_EFFECTIVE_RATE"],
  GEO: ["GEO_RUSSIA_EXIT", "GEO_CONFLICT_TIES", "GEO_LOBBYING_TRANSP"],
};

/** Fait clé d'un pilier : exploitation animale d'abord ; puis une alerte, un manque obligatoire lu,
 *  un point de vigilance ; puis le fait prioritaire documenté ; puis le mieux sourcé (hors donnée
 *  de contexte). */
export function faitCle(pilier: string, fs: Fait[]): Fait | null {
  if (pilier === "ANI") {
    const a = fs.find((f) => f.code === "ANI_ANIMAL_FREE" && f.etat === "documente") ?? fs.find((f) => f.code === "ANI_EXPLOITATION");
    if (a) return a;
  }
  const rouge = fs.find((f) => f.signal?.niveau === "alerte") ?? fs.find((f) => f.etat === "obligatoire_absent") ?? fs.find((f) => f.signal?.niveau === "vigilance");
  if (rouge) return rouge;
  for (const c of PRIORITE[pilier] ?? []) {
    const f = fs.find((x) => x.code === c && x.etat === "documente");
    if (f) return f;
  }
  const doc = fs.filter((f) => f.etat === "documente" && !f.contexte).sort((a, b) => RANG[a.preuve!.solidite] - RANG[b.preuve!.solidite]);
  return doc[0] ?? fs.find((f) => f.etat === "autre_forme") ?? null;
}


/** Indicateurs qui viennent d'un classement, d'un questionnaire ou d'un registre externe. */
const EXTERNE = new Set([
  "ENV_CDP_CLIMATE", "WAT_CDP", "ENV_SBTI_VALIDATED", "SUP_FTI_SCORE", "SUP_KNOWTHECHAIN", "SUP_LIVING_WAGE", "ANI_BBFAW_TIER",
  "ANI_FUR_FREE", "GOV_BCORP", "GEO_RUSSIA_EXIT", "GEO_LOBBYING_ALIGN", "GEO_LOBBYING_TRANSP", "GEO_LOBBYING_SPEND",
  "INV_SOLIDARITY_LABEL", "ENV_MATERIAL_CHANGE",
]);
/** Indicateurs de signalement : leur absence veut dire « rien trouvé », pas « non publié ». */
const SIGNALEMENT = new Set(["GOV_SANCTIONS", "ENV_GREENWASHING", "PLA_POLLUTER", "GEO_CONFLICT_TIES", "SUP_BHRRC_ALLEG", "WAT_CONTROVERSY"]);

/** Pourquoi un indicateur est vide : un statut court (« Non renseigné ») et sa raison. */
export function raisonVide(f: Pick<Fait, "code" | "obligation" | "exemption">): [string, string] {
  if (SIGNALEMENT.has(f.code)) return ["Rien trouvé", "dans les sources suivies (ce n'est pas la preuve qu'il n'y a rien)"];
  if (f.exemption) return ["Non renseigné", `pas d'obligation : ${f.exemption}`];
  if (f.obligation.length) return ["Non renseigné", `publication obligatoire (${f.obligation.join(", ")}) ; le rapport n'a pas encore été relu pour cet indicateur`];
  if (EXTERNE.has(f.code)) return ["Non évalué", "donnée d'un classement ou d'un registre externe, où l'entreprise n'a pas été trouvée"];
  return ["Non renseigné", "aucune obligation légale de le publier"];
}
