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
    case "ANI_OFFRE_VEGETALE": return "Propose au moins un produit 100 % végétal";
    case "ANI_FUR_FREE": return "Membre du label « sans fourrure »";
    case "ANI_BBFAW_TIER": return v === null ? "Évalué" : `Niveau ${nf(v, 0)} sur 6 au classement du bien-être animal`;
    case "GEO_RUSSIA_EXIT": { const s = m1(/» — ([^;.]+)/, x) ?? m1(/— ([^;.]+)/, x); return s ? `Russie : ${s.replace(/ en Russie$/, "")}` : "Documenté"; }
    case "GOV_SANCTIONS": case "ENV_GREENWASHING": {
      // « Autorité de la concurrence, décision n° 23-D-15 du 29/12/2023 : … ; amende de 0,566 M€ »
      const autorite = (x.split(/[,:(]/)[0] ?? "").trim();
      const an = m1(/du \d{2}\/\d{2}\/(\d{4})/, x);
      const amende = m1(/amende (?:de|d’un montant de) ([\d  ,.]+ ?(?:M€|Md€|€|millions? d[’']euros|milliards? d[’']euros|euros))/, x)
        ?? m1(/fine of ([\d.,]+ (?:million|billion)? ?euros)/i, x);
      const quoi = code === "GOV_SANCTIONS" ? "Sanctionné" : "Allégations écologiques trompeuses relevées";
      // Article devant le nom de l'autorité : « l'Autorité… », « la Commission… », « la CNIL ».
      const art = !autorite ? "" : /^(Commission|Cour|DGCCRF|CNIL|FTC)\b/.test(autorite) ? "la " : /^[AEÉIOU][a-zé]/.test(autorite) ? "l'" : "";
      return `${quoi} par ${autorite ? art + autorite : "une autorité"}${an ? ` (${an})` : ""}${amende ? ` : amende de ${amende}` : ""}`;
    }
    case "GEO_CONFLICT_TIES": return "Implication dans un conflit ou une occupation, documentée";
    case "GEO_LOBBYING_ALIGN": { const n = m1(/Climate Policy Engagement ([A-F][+-]?)/, x); return n ? `Note ${n} d'InfluenceMap sur le lobbying climat` : "Évalué par InfluenceMap"; }
    case "LAB_LIVING_WAGE": { const s = m1(/\((salaire (?:décent|adéquat)[^)]*)\)/, x); return s ? s[0].toUpperCase() + s.slice(1) : "Salaire décent : engagement publié"; }
    case "INV_RESPONSIBLE_POLICY": { const s = m1(/— ([^:«]+) :/, x); return s ? s[0].toUpperCase() + s.slice(1) : "Politique publiée"; }
    case "GEO_LOBBYING_TRANSP": return /HATVP|répertoire/i.test(x + (p.source_name ?? "")) ? "Inscrit au répertoire des lobbyistes (HATVP)" : "Inscrit au registre européen des lobbyistes";
    case "GEO_LOBBYING_SPEND": { const s = m1(/déclarés[^:]*: ([^,]+(?:€[^,]*€)?)/, x) ?? (v === null ? null : `${nf(v, 0)} €`); return s ? `${s} de lobbying déclarés par an` : "Déclaré"; }
    case "ENV_CDP_CLIMATE": return `Note ${m1(/note ([A-F][+-]?)/, x) ?? "?"} au questionnaire climat du CDP`;
    case "WAT_CDP": return `Note ${m1(/note ([A-F][+-]?)/, x) ?? "?"} au questionnaire eau du CDP`;
    case "ENV_SBTI_VALIDATED": return m1(/— (objectif[^(]+\([^)]*\))/, x) ?? m1(/— ([^(]+)\(/, x) ?? "Documenté";
    case "SUP_LIVING_WAGE": return `Note ${m1(/note ([A-E])/, x) ?? "?"} sur le salaire vital des ouvriers`;
    case "SUP_VIGILANCE_PLAN": return "Plan de vigilance publié";
    case "ENV_SCOPE3_DISCLOSED": return "Émissions indirectes (scope 3) publiées";
    case "TAX_CBCR_PUBLISHED": return "Impôts publiés pays par pays";
    case "PLA_POLLUTER": return "Parmi les plus gros pollueurs plastique";
    case "SUP_FTI_SCORE": return v === null ? "Évalué" : `${nf(v)} % des points de transparence`;
    case "LAB_CEO_PAY_RATIO": return v === null ? "Publié" : `Le dirigeant gagne ${nf(v, 0)} fois le salaire médian`;
    case "LAB_GENDER_PAYGAP": return v === null ? "Publié" : v < 0 ? `${nf(-v)} % en faveur des femmes` : `${nf(v)} % en faveur des hommes`;
    case "LAB_EGAPRO_INDEX": return v === null ? "Publié" : `Index Égapro : ${nf(v, 0)}/100`;
    case "GOV_BCORP": return "Certifiée B Corp";
    case "GOV_BOARD_GENDER": return v === null ? "Publié" : `${nf(v)} % de femmes au conseil d'administration`;
    case "GOV_BOARD_INDEP": return v === null ? "Publié" : `${nf(v)} % d'administrateurs indépendants`;
    case "TAX_EFFECTIVE_RATE": return v === null ? "Publié" : `Impôt payé : ${nf(v)} % des bénéfices`;
    case "ENV_GHG_TREND": return v === null ? "Publié" : v > 0 ? `Émissions en hausse de ${nf(v, 2)} % par an` : `Émissions en baisse de ${nf(-v, 2)} % par an`;
    case "PLA_REDUCTION": return v === null ? "Publié" : v > 0 ? `Plastique neuf en hausse de ${nf(v, 2)} % par an` : `Plastique neuf en baisse de ${nf(-v, 2)} % par an`;
    case "PLA_RECYCLED": return v === null ? "Publié" : `${nf(v)} % d'emballages recyclés ou réutilisables`;
    case "ENV_TAXONOMY_CAPEX": return v === null ? "Publié" : `${nf(v)} % des investissements jugés verts par l'UE`;
    case "ENV_GHG_INTENSITY": return v === null ? "Publié" : `${nf(v, 0)} tonnes de CO₂ par million d'euros de ventes`;
    case "WAT_INTENSITY": return v === null ? "Publié" : `${nf(v, 0)} m³ d'eau prélevés par million d'euros de ventes`;
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

/** Preuve retenue : la plus spécifique (propre à l'entité), puis la plus récente. */
function meilleure(ps: PreuveEntree[]): PreuveEntree | null {
  return [...ps].sort((a, b) => b.specificity - a.specificity || (b.event_date ?? b.observed_on).localeCompare(a.event_date ?? a.observed_on))[0] ?? null;
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
const NIVEAU_PROPRIETAIRE = new Set(["LAB_EGAPRO_INDEX"]);
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
  [/Autorité de la concurrence/, "décisions de l'Autorité de la concurrence"],
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
    const p = meilleure(parCode.get(i.code) ?? []);
    const js = (jparCode.get(i.code) ?? []).sort((a, b) => b.checked_on.localeCompare(a.checked_on));
    const obligation = i.mandatory ? (i.mandatory_regimes ?? []) : [];
    const contexte = i.direction === "contextual";
    if (p) {
      return {
        code: i.code, nom: i.name, pilier: i.dimension_code, etat: "documente", valeur: valeurCourte(i.code, i.unit, p), contexte, obligation, note: null,
        niveau: niveauDe(i, p, estMarque),
        preuve: {
          source: p.source_name ?? p.source_code ?? "Source", url: p.source_url, solidite: SOLIDITE[p.tier] ?? "declarative",
          date: p.event_date ?? p.observed_on, dateEvenement: !!p.event_date, citation: p.excerpt, reprisDe: p.inherited_from ?? null,
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
