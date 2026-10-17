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
  /** Nom de l'indicateur, pour les signaux qui doivent le citer. */
  nom?: string;
  /** Pays du siège (code ISO) de l'entité qui publie la donnée : certains repères sont des lois françaises. */
  pays?: string | null;
}

/** États membres de l'Union européenne (codes ISO). */
const UE = new Set(["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]);
const ADJ: Record<string, string> = {
  US: "américaine", GB: "britannique", CH: "suisse", NL: "néerlandaise", DE: "allemande", ES: "espagnole", IT: "italienne",
  BE: "belge", DK: "danoise", SE: "suédoise", FI: "finlandaise", NO: "norvégienne", IE: "irlandaise", LU: "luxembourgeoise",
  AT: "autrichienne", PT: "portugaise", PL: "polonaise", LT: "lituanienne", CA: "canadienne", JP: "japonaise", KR: "sud-coréenne",
  CN: "chinoise", IN: "indienne", BR: "brésilienne", MX: "mexicaine", AU: "australienne", TH: "thaïlandaise", TR: "turque",
};
/** « une entreprise suisse », ou null si la loi française s'applique (siège en France ou inconnu). */
const etrangere = (p?: string | null) => (p && p !== "FR" ? `une entreprise ${ADJ[p] ?? "étrangère"}` : null);

const nf = (x: number, d = 1) => x.toLocaleString("fr-FR", { maximumFractionDigits: d });
const a = (motif: string, regle: string): Signal => ({ niveau: "alerte", motif, regle });
const v = (motif: string, regle: string): Signal => ({ niveau: "vigilance", motif, regle });
const note = (re: RegExp, s: string) => s.match(re)?.[1] ?? null;

/** Règles affichées dans la méthodologie et la légende, par indicateur. */
export const REGLES: Record<string, { alerte: string; vigilance?: string; reference: string }> = {
  ANI_EXPLOITATION: { alerte: "un produit issu de l'exploitation animale est documenté", vigilance: "exploitation non documentée dans un secteur où elle est la règle", reference: "choix de l'Index" },
  ANI_BBFAW_TIER: { alerte: "niveau 6 sur 6", vigilance: "niveau 5 sur 6", reference: "échelle du classement BBFAW : niveau 6, aucun signe que le bien-être animal soit à l'ordre du jour ; niveau 5, à l'ordre du jour mais peu de preuves de mise en œuvre" },
  ENV_CDP_CLIMATE: { alerte: "note F", vigilance: "note D ou D-", reference: "échelle du CDP : F, l'entreprise n'a pas répondu alors qu'elle y était invitée ; D, plus bas niveau pour une entreprise qui répond" },
  ENV_CDP_FORESTS: { alerte: "note F", vigilance: "note D ou D-", reference: "échelle du CDP : F, l'entreprise n'a pas répondu alors qu'elle y était invitée (le CDP n'interroge que les entreprises exposées au risque de déforestation) ; D, plus bas niveau pour une entreprise qui répond" },
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
  LAB_CEO_PAY_RATIO: { alerte: "300 fois ou plus", vigilance: "100 fois ou plus", reference: "choix de l'Index, pas une limite légale : aucune loi ne plafonne cet écart, ni en France ni dans l'Union européenne (la loi impose seulement de le publier) ; à 100 fois, le dirigeant gagne en un an ce que le salarié médian gagne en un siècle" },
  GOV_SANCTIONS: { alerte: "sanction d'une autorité", reference: "décision publique d'une autorité" },
  GOV_BOARD_GENDER: { alerte: "moins de 20 % de femmes", vigilance: "moins de 40 % de femmes", reference: "loi Copé-Zimmermann : 40 % au minimum dans les conseils des sociétés cotées en France ; alerte : la moitié de ce minimum" },
  GOV_EXEC_GENDER: { alerte: "moins de 15 % de femmes", vigilance: "moins de 30 % de femmes", reference: "loi Rixain : depuis le 1er mars 2026, au moins 30 % de chaque sexe parmi les membres des instances dirigeantes des entreprises d'au moins 1 000 salariés en France (40 % au 1er mars 2029) ; alerte : la moitié de ce minimum" },
  GOV_BOARD_INDEP: { alerte: "—", vigilance: "moins d'un tiers d'indépendants", reference: "code Afep-Medef : au moins un tiers d'indépendants, même dans une société contrôlée" },
  TAX_EFFECTIVE_RATE: { alerte: "—", vigilance: "taux effectif sous 15 %", reference: "impôt minimum mondial de l'OCDE : 15 % ; un taux bas une année peut aussi venir de pertes ou de crédits d'impôt ; un taux négatif ou supérieur à 60 % est affiché comme atypique, sans signal" },
  // Point 9 (17/10/2026) : une convention judiciaire d'intérêt public est une sanction pénale négociée,
  // validée par un juge : alerte, en disant qu'elle n'emporte pas déclaration de culpabilité.
  GOV_CJIP: { alerte: "convention judiciaire d'intérêt public validée par un juge", reference: "article 41-1-2 du code de procédure pénale : amende d'intérêt public, sans déclaration de culpabilité" },
  WAT_CONTROVERSY: { alerte: "convention judiciaire d'intérêt public pour une infraction au droit de l'eau", vigilance: "mise en demeure de la préfecture", reference: "conventions judiciaires validées par un juge (sans déclaration de culpabilité) ; arrêtés préfectoraux de mise en demeure des installations classées" },
  GEO_RUSSIA_EXIT: { alerte: "activité poursuivie en Russie", vigilance: "activité réduite ou investissements gelés", reference: "statuts de la base Leave Russia (KSE Institute)" },
  GEO_CONFLICT_TIES: { alerte: "implication documentée", reference: "choix de l'Index : toute implication documentée par une source publique" },
  GEO_SANCTIONS_BREACH: { alerte: "règlement avec l'OFAC pour violation de sanctions internationales", reference: "avis d'exécution publiés par l'OFAC (Trésor des États-Unis) : l'entreprise règle sa responsabilité civile potentielle, sans reconnaître de faute" },
};

/** Signal d'un fait, ou null s'il ne franchit aucun seuil. */
export function evaluer(f: FaitEvalue): Signal | null {
  const r = REGLES[f.code];
  if (f.etat === "obligatoire_absent") return a(f.nom ? `${f.nom} : donnée exigée par la loi, non publiée` : "donnée exigée par la loi, non publiée", "la loi impose cette donnée et la lecture du rapport officiel confirme qu'elle n'y est pas");
  if (f.code === "ANI_EXPLOITATION" && f.etat === "presume") return v("produits d'origine animale probables (non prouvé)", r.vigilance!);
  if (f.etat !== "documente" || !r) return null;
  const x = f.valeurNum;
  const c = f.citation ?? "";
  const ref = r.reference;
  switch (f.code) {
    case "ANI_EXPLOITATION": return a("vend des produits issus de l'exploitation animale", "un seul produit d'origine animale suffit");
    case "ANI_BBFAW_TIER":
      if (x === null) return null;
      return x >= 6 ? a("mal noté pour le bien-être des animaux d'élevage, au plus bas du classement BBFAW", ref) : x >= 5 ? v("mal noté pour le bien-être des animaux d'élevage (classement BBFAW)", ref) : null;
    case "ENV_CDP_CLIMATE": case "WAT_CDP": case "ENV_CDP_FORESTS": {
      const n = note(/note ([A-F][+-]?)/, c) ?? (/Did not disclose/.test(c) ? "F" : null);
      const q = f.code === "WAT_CDP" ? "eau" : f.code === "ENV_CDP_FORESTS" ? "forêts" : "climat";
      return n === "F" ? a(`aucune réponse au questionnaire ${q} du CDP (note F)`, ref) : n?.startsWith("D") ? v(`note ${n} au questionnaire ${q} du CDP (de A à F)`, ref) : null;
    }
    case "ENV_GHG_TREND":
      if (x === null) return null;
      return x > 0 ? a(`émissions de gaz à effet de serre en hausse de ${nf(x, 2)} % par an`, ref) : x > -4.2 ? v(`émissions de gaz à effet de serre en baisse de ${nf(-x, 2)} % par an seulement (il faudrait 4,2 %)`, ref) : null;
    case "ENV_SBTI_VALIDATED": return /engagement retiré/.test(c) ? v("objectif climat retiré de la validation SBTi", ref) : null;
    case "ENV_GREENWASHING": return a("allégations écologiques jugées trompeuses", ref);
    case "PLA_POLLUTER": return a("parmi les plus gros pollueurs plastique au monde (d'après les déchets ramassés)", ref);
    case "PLA_REDUCTION": return x !== null && x > 0 ? a(`utilise ${nf(x, 2)} % de plastique neuf en plus chaque année`, ref) : null;
    case "SUP_FTI_SCORE":
      if (x === null) return null;
      return x < 10 ? a(`transparence sur ses fournisseurs : ${nf(x)} % des points seulement`, ref) : x < 26 ? v(`transparence sur ses fournisseurs : ${nf(x)} % des points seulement`, ref) : null;
    case "SUP_LIVING_WAGE": {
      const n = note(/note ([A-E])/, c);
      return n === "E" ? a("aucun salaire vital chez ses fournisseurs (note E, la plus basse)", ref) : n === "D" ? v("salaire vital chez ses fournisseurs : note D (de A à E)", ref) : null;
    }
    case "SUP_KNOWTHECHAIN":
      if (x === null) return null;
      return x < 10 ? a(`lutte contre le travail forcé chez ses fournisseurs : ${nf(x, 0)}/100`, ref) : x < 20 ? v(`lutte contre le travail forcé chez ses fournisseurs : ${nf(x, 0)}/100`, ref) : null;
    case "LAB_EGAPRO_INDEX":
      if (x === null) return null;
      {
        // L'index Égapro n'existe qu'en France : pour un groupe étranger, c'est celui de sa filiale française,
        // qui est bien soumise à la loi française.
        const fil = etrangere(f.pays) ? " (filiale française)" : "";
        return x < 75 ? a(`égalité femmes-hommes (index Égapro${fil}) : ${nf(x, 0)}/100, sous le minimum légal de 75`, ref) : x < 85 ? v(`égalité femmes-hommes (index Égapro${fil}) : ${nf(x, 0)}/100`, ref) : null;
      }
    case "LAB_GENDER_PAYGAP": {
      if (x === null) return null;
      const e = Math.abs(x), qui = x < 0 ? "en faveur des femmes" : "en faveur des hommes";
      return e >= 15 ? a(`écart de salaire femmes-hommes de ${nf(e)} % ${qui}`, ref) : e >= 5 ? v(`écart de salaire femmes-hommes de ${nf(e)} % ${qui}`, ref) : null;
    }
    case "LAB_CEO_PAY_RATIO":
      if (x === null) return null;
      return x >= 300 ? a(`patron payé ${nf(x, 0)} fois le salaire médian de ses salariés`, ref) : x >= 100 ? v(`patron payé ${nf(x, 0)} fois le salaire médian de ses salariés`, ref) : null;
    case "GOV_SANCTIONS":
      // Clémence : infraction constatée, amende levée parce que l'entreprise l'a dénoncée (17/10/2026).
      if (/sans amende|pas d.amende|immunité d.amende/i.test(c)) return v("infraction constatée par une autorité, sans amende (clémence)", ref);
      return a("sanctionné par une autorité (amende ou condamnation)", ref);
    case "GOV_EXEC_GENDER":
      if (x === null) return null;
      {
        // Obligation française, déclarée par chaque société employeuse : pour un groupe étranger,
        // c'est sa filiale française qui déclare.
        const fil = etrangere(f.pays) ? " (filiale française)" : "";
        // L'objectif de 30 % ne vaut que depuis le 1er mars 2026 (déclaration au titre de 2025) :
        // une déclaration plus ancienne est signalée sans être jugée contre ce minimum.
        const an = Number(note(/au titre de (\d{4})/, c) ?? 0);
        if (an && an < 2025) return x < 30 ? v(`${nf(x)} % de femmes au comité de direction${fil} en ${an}, avant l'objectif légal de 30 % applicable depuis 2026 (loi Rixain)`, ref) : null;
        const t = `seulement ${nf(x)} % de femmes au comité de direction${fil} (minimum légal : 30 % depuis 2026, loi Rixain)`;
        return x < 15 ? a(t, ref) : x < 30 ? v(t, ref) : null;
      }
    case "GOV_BOARD_GENDER":
      if (x === null) return null;
      {
        // La loi Copé-Zimmermann ne vaut que pour les sociétés françaises : ailleurs, 40 % reste le repère
        // de l'Index, et la phrase dit que l'entreprise n'y est pas tenue.
        const hors = etrangere(f.pays);
        const regle = hors
          ? `choix de l'Index, d'après la loi française Copé-Zimmermann (40 % au minimum dans les conseils des sociétés cotées en France), qui ne s'applique pas à ${hors} ; alerte : la moitié de ce repère` +
            (UE.has(f.pays!) ? " ; dans l'Union européenne, une directive de 2022 fixe aux sociétés cotées un objectif de 40 % des administrateurs non exécutifs, ou 33 % de l'ensemble du conseil, d'ici juin 2026" : "")
          : ref;
        const precision = hors ? ` (repère : 40 %, minimum légal en France, qui ne s'applique pas à ${hors})` : " (repère : 40 %, minimum légal en France)";
        return x < 20 ? a(`seulement ${nf(x)} % de femmes au conseil${precision}`, regle) : x < 40 ? v(`seulement ${nf(x)} % de femmes au conseil${precision}`, regle) : null;
      }
    case "GOV_BOARD_INDEP": {
      if (x === null || x >= 33) return null;
      const hors = etrangere(f.pays);
      return hors
        ? v(`seulement ${nf(x)} % d'administrateurs indépendants au conseil (repère français : un tiers, qui ne s'applique pas à ${hors})`, `choix de l'Index, d'après le code de gouvernance français Afep-Medef (au moins un tiers d'indépendants), qui ne s'applique pas à ${hors}`)
        : v(`seulement ${nf(x)} % d'administrateurs indépendants au conseil`, ref);
    }
    // Pas de vigilance sur un exercice en perte : un taux bas ou négatif n'y dit rien de l'impôt payé.
    case "TAX_EFFECTIVE_RATE": return x !== null && x >= 0 && x <= 60 && x < 15 && !/perte|loss/i.test(c) ? v(`impôt sur les bénéfices : taux réel de ${nf(x)} %, sous le minimum mondial de 15 %`, ref) : null;
    case "GEO_RUSSIA_EXIT":
      if (/activité poursuivie/.test(c)) return a("poursuit ses activités en Russie", ref);
      if (/investissements gelés/.test(c)) return v("toujours présent en Russie, investissements gelés", ref);
      return /activité réduite/.test(c) ? v("toujours présent en Russie, activité réduite", ref) : null;
    case "GEO_CONFLICT_TIES": return a("liens documentés avec un conflit armé ou une occupation", ref);
    case "GEO_SANCTIONS_BREACH": {
      const prog = c.match(/programme de sanctions : ([^;]+);/)?.[1]?.trim();
      return a(`a payé pour régler des violations de sanctions internationales${prog ? ` (${prog})` : ""} auprès du Trésor des États-Unis`, ref);
    }
    case "GOV_CJIP": {
      const motif = c.match(/— motif : ([^;]+);/)?.[1]?.trim();
      return a(`convention judiciaire d'intérêt public${motif ? ` (${motif})` : ""} validée par un juge, sans déclaration de culpabilité`, ref);
    }
    case "WAT_CONTROVERSY":
      return /Convention judiciaire d.intérêt public/i.test(c)
        ? a("convention judiciaire d'intérêt public pour une infraction au droit de l'eau, validée par un juge (sans déclaration de culpabilité)", ref)
        : v("mise en demeure de la préfecture portant sur l'eau", ref);
  }
  return null;
}

/** Ordre d'affichage : alertes d'abord. */
export const RANG_SIGNAL: Record<NiveauSignal, number> = { alerte: 0, vigilance: 1 };

/** Repère pour lire un chiffre : l'échelle de la source, ou une valeur de comparaison citée. */
export const REPERES: Record<string, string> = {
  ENV_CDP_CLIMATE: "Échelle du CDP : de A (meilleure note) à D-, F = l'entreprise n'a pas répondu",
  WAT_CDP: "Échelle du CDP : de A (meilleure note) à D-, F = l'entreprise n'a pas répondu",
  ENV_CDP_FORESTS: "Échelle du CDP : de A (meilleure note) à D-, F = l'entreprise n'a pas répondu ; porte sur le soja, le bœuf et le cuir, le cacao, l'huile de palme, le café, le caoutchouc et le bois",
  ENV_GHG_TREND: "Repère : une baisse d'au moins 4,2 % par an est nécessaire pour rester sous 1,5 °C (SBTi)",
  PLA_REDUCTION: "Repère : évolution moyenne par an sur la période publiée par l'entreprise",
  SUP_LIVING_WAGE: "Échelle du Fashion Checker : de A (salaire vital versé) à E (ni versé ni promis)",
  SUP_FTI_SCORE: "Repère : moyenne des 250 grandes marques de mode en 2023, 26 %",
  SUP_KNOWTHECHAIN: "Repère : moyenne des 60 plus grands groupes alimentaires en 2023, 16/100",
  LAB_EGAPRO_INDEX: "Repère : sous 75/100, la loi impose des mesures de correction ; sous 85, des objectifs",
  LAB_GENDER_PAYGAP: "Repère : à partir de 5 %, l'employeur doit l'analyser avec les représentants du personnel (directive UE)",
  LAB_CEO_PAY_RATIO: "Repère : aucune loi ne plafonne cet écart ; à 100 fois, le dirigeant gagne en un an ce que le salarié médian gagne en un siècle",
  GOV_BOARD_GENDER: "Repère : 40 % au minimum dans les sociétés cotées en France (loi Copé-Zimmermann)",
  GOV_EXEC_GENDER: "Repère : 30 % de chaque sexe au minimum dans les instances dirigeantes depuis le 1er mars 2026, 40 % en 2029 (loi Rixain, entreprises d'au moins 1 000 salariés en France) ; ce sont le comité exécutif ou de direction, pas le conseil d'administration",
  GOV_BOARD_INDEP: "Repère : au moins un tiers recommandé par le code Afep-Medef",
  TAX_EFFECTIVE_RATE: "Repère : impôt minimum mondial de l'OCDE, 15 % ; taux normal en France, 25 %",
  WAT_CONTROVERSY: "Repère : arrêtés préfectoraux de mise en demeure des installations classées (Géorisques) et conventions judiciaires d'intérêt public validées par un juge (ministère de la Justice ; la validation n'emporte pas déclaration de culpabilité), cinq dernières années ; ces documents sont souvent des scans : la citation est le texte reconnu par OCR, parfois sans accents",
  GEO_POL_FINANCING: "Repère : en France, une entreprise ne peut pas financer un parti ni une campagne (loi du 11 mars 1988) ; aux États-Unis, elle le fait par un comité d'action politique déclaré à la Commission électorale fédérale",
  SUP_BHRRC_ALLEG: "Repère : articles de presse et d'ONG relayés par le Business & Human Rights Resource Centre ; ce sont des allégations, pas des faits établis",
  TAX_HAVEN_PRESENCE: "Repère : les dix premiers du classement des paradis fiscaux pour les entreprises du Tax Justice Network (décembre 2025) : îles Vierges britanniques, îles Caïmans, Suisse, Bermudes, Singapour, Hong Kong, Pays-Bas, Jersey, Irlande, Luxembourg ; le pays du siège n'est pas compté",
  ANI_BBFAW_TIER: "Classement BBFAW des politiques de bien-être des animaux d'élevage, du niveau 1 (meilleur) au niveau 6 : bien noté = niveaux 1 et 2, moyennement noté = 3 et 4, mal noté = 5 et 6",
  ENV_TAXONOMY_CAPEX: "Part des investissements de l'année conformes à la taxonomie verte européenne",
  ENV_GHG_INTENSITY: "Dépend beaucoup du secteur : à comparer entre entreprises du même secteur",
  WAT_INTENSITY: "Dépend beaucoup du secteur : à comparer entre entreprises du même secteur",
  WAT_WITHDRAWAL_INTENSITY: "Dépend beaucoup du secteur : à comparer entre entreprises du même secteur",
  ENV_SBTI_VALIDATED: "La SBTi vérifie que l'objectif climat est compatible avec l'accord de Paris ; c'est un engagement, pas un résultat",
};

/**
 * « En savoir plus » : comment lire un chiffre dont le sens n'est pas évident (règles de calcul de la
 * source, pièges de comparaison). Texte général, valable pour toutes les entreprises ; ce qui est
 * propre à une entreprise reste dans la citation vérifiée de sa source.
 */
export const EN_SAVOIR_PLUS: Record<string, string> = {
  TAX_EFFECTIVE_RATE:
    "Le taux effectif rapporte la charge d'impôt sur les bénéfices inscrite dans les comptes au bénéfice avant impôt de la même année. Ce n'est pas l'impôt versé dans l'année : la charge comptable compte aussi les impôts différés (dus ou récupérables plus tard), les crédits d'impôt et les rectifications des années passées. Elle peut donc être négative, quand l'entreprise inscrit un produit d'impôt (pertes passées qu'elle pourra déduire, crédit d'impôt, remboursement), ou dépasser le bénéfice, quand des pertes ou des dépréciations ne sont pas déductibles, ou quand le groupe paie l'impôt dans des pays bénéficiaires alors qu'il perd de l'argent ailleurs. Un taux négatif ou supérieur à 60 % est affiché comme atypique : il ne se compare pas au minimum mondial de 15 %.",
  ENV_TAXONOMY_CAPEX:
    "La taxonomie verte de l'Union européenne est une liste d'activités économiques jugées durables (produire de l'électricité renouvelable, rénover des bâtiments, fabriquer des véhicules à faibles émissions…), avec des critères techniques précis. Les grandes entreprises publient la part de leurs investissements qui finance ces activités. Pour l'énergie et l'automobile, la liste couvre le cœur du métier : la part en dit long. Pour l'alimentation, les boissons, le luxe ou la distribution, peu d'activités y figurent : une part proche de 0 % est normale et ne dit pas que l'entreprise n'investit rien pour le climat. L'Index l'affiche à titre d'information, sans signal.",
  LAB_CEO_PAY_RATIO:
    "Le ratio compare la rémunération totale du dirigeant sur un an (salaire, primes et actions attribuées) à celle du salarié « médian », celui qui se trouve pile au milieu : la moitié des salariés gagne plus, l'autre moitié moins. Le nombre de salariés ou de niveaux hiérarchiques ne fait donc pas monter le chiffre en soi ; ce qui compte, c'est qui se trouve au milieu. Les entreprises cotées aux États-Unis calculent ce salarié médian sur leurs salariés du monde entier, sans corriger le coût de la vie et en comptant les temps partiels tels quels : un groupe qui emploie beaucoup de vendeurs, de serveurs ou d'ouvriers à temps partiel ou dans des pays à bas salaires affiche un ratio très élevé. En France, le « ratio d'équité » de la loi PACTE porte souvent sur les seuls salariés de la société en France : les chiffres de deux pays ne se comparent pas directement.",
};
