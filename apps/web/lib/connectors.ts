// Source unique des connecteurs d'ingestion, partagée par la page /pipeline
// (et disponible pour toute autre vue). Éviter la double maintenance : cette
// liste fait foi côté web. La prose versionnée reste dans METHODOLOGY.md.

export type ConnectorLevel = "groupe" | "marque" | "groupe ou marque" | "—";

export type Connector = {
  name: string;
  pillar: string;
  produces: string;
  source: string;
  level: ConnectorLevel;
};

export const CONNECTORS: Connector[] = [
  { name: "Registres d'identité", pillar: "—", produces: "Identité des entreprises (LEI, SIREN, CIK), confirmée par le registre officiel", source: "GLEIF, INSEE (SIRENE), SEC", level: "—" },
  { name: "Marques et propriétaires", pillar: "—", produces: "Univers de marques et chaînes de détention (qui possède qui)", source: "Open Food Facts, Wikidata", level: "—" },
  { name: "Rapports annuels réglementés", pillar: "TAX, GOV, LAB, ENV, SUP", produces: "Taux effectif d'impôt (données comptables balisées) ; données obligatoires de l'état de durabilité (CSRD), citées mot pour mot : mixité et indépendance du conseil, écart et ratio de rémunération, émissions indirectes, intensité carbone, évolution des émissions, plan de vigilance", source: "filings.xbrl.org, AMF (BDIF), rapports annuels légaux", level: "groupe" },
  { name: "Documents déposés à la SEC (États-Unis)", pillar: "TAX, LAB, GOV, ANI", produces: "Taux effectif d'impôt (rapport annuel 10-K) ; ratio PDG / salarié médian et composition du conseil (circulaire de procuration) ; matières premières animales citées dans le 10-K", source: "SEC EDGAR", level: "groupe" },
  { name: "Rapports volontaires des entreprises", pillar: "ENV, ANI", produces: "Hors de l'Union : émissions totales sur plusieurs années (évolution réelle), recours à des matières ou ingrédients animaux. Niveau 3 : validé seulement après vérification mot pour mot", source: "Rapports de durabilité publiés par les entreprises", level: "groupe" },
  { name: "Égapro", pillar: "LAB", produces: "Index égalité professionnelle femmes-hommes (/100), rapprochement par SIREN exact", source: "Ministère du Travail (Égapro)", level: "groupe ou marque" },
  { name: "Lobbying", pillar: "GEO", produces: "Inscription et dépenses de lobbying en France et auprès de l'Union ; alignement du lobbying climat", source: "HATVP, registre de transparence de l'UE, InfluenceMap", level: "groupe" },
  { name: "Sortie de Russie", pillar: "GEO", produces: "Statut depuis l'invasion de l'Ukraine : sortie effective (1) … activité poursuivie (0)", source: "KSE Institute, base « Leave Russia »", level: "groupe" },
  { name: "Climat et eau", pillar: "ENV, WAT", produces: "Notes climat et eau A à D- (A = 1,00 … D- = 0,13, sollicitée sans réponse = 0) ; objectifs climat validés, comptés comme des engagements", source: "CDP, Science Based Targets initiative (SBTi)", level: "groupe" },
  { name: "Écoblanchiment sanctionné", pillar: "ENV", produces: "Allégations environnementales trompeuses relevées par une autorité : amende (sévérité 0,8), engagements après enquête (0,5)", source: "Autorités de protection des consommateurs (ACM, AGCM…)", level: "groupe" },
  { name: "Plastique", pillar: "PLA", produces: "Pollueurs plastique : sévérité (plafond) qui borne la note plastique", source: "Break Free From Plastic", level: "groupe ou marque" },
  { name: "Salaire vital chez les fournisseurs", pillar: "SUP", produces: "Note A à E du salaire vital réellement versé dans les usines (E = aucun salaire vital versé ni revendiqué)", source: "Clean Clothes Campaign (Fashion Checker)", level: "groupe" },
  { name: "Classements d'ONG", pillar: "ANI, SUP", produces: "Bien-être animal en élevage (BBFAW), travail forcé dans les chaînes d'approvisionnement (KnowTheChain), transparence de la mode (Fashion Revolution), label sans fourrure", source: "BBFAW, KnowTheChain, Fashion Revolution, Fur Free Retailer", level: "groupe ou marque" },
  { name: "Finance éthique", pillar: "INV", produces: "Financement de l'expansion fossile, politiques d'exclusion", source: "Banking on Climate Chaos, Reclaim Finance, Principes pour l'investissement responsable (ONU)", level: "groupe" },
  { name: "Labels", pillar: "INV, GOV", produces: "Label Finansol (liste officielle), certification B Corp (annuaire B Lab, site vérifié)", source: "FAIR, B Lab", level: "groupe ou marque" },
  { name: "ONU (HCDH)", pillar: "GEO", produces: "Base des entreprises liées aux colonies (présence = controverse)", source: "Conseil des droits de l'homme", level: "groupe" },
];

export type Guard = { title: string; body: string };

export const GUARDS: Guard[] = [
  {
    title: "Des sources officielles, lues par du code",
    body: "Les connecteurs lisent des données balisées ou des listes officielles, sans modèle de langage : même entrée, même résultat. Les identités (LEI, SIREN, CIK) sont confirmées par le registre, jamais devinées à partir d'un nom.",
  },
  {
    title: "Chaque chiffre retrouvé mot pour mot",
    body: "Une donnée lue dans un rapport n'entre que si sa citation figure mot pour mot dans le document et contient la valeur ; les calculs (conversion de devise au cours de la BCE, rythme d'évolution des émissions) sont refaits par le vérificateur automatique. Les cas douteux (définition voisine, périmètre partiel) sont écartés et justifiés dans un journal public.",
  },
  {
    title: "Publication graduée selon la source",
    body: "Une source réglementaire ou une ONG auditée, vérifiée, est publiée automatiquement. Un rapport volontaire de l'entreprise (niveau 3) n'est publié qu'après vérification mot pour mot, par délégation de l'éditeur, avec une étiquette de relecture distincte ; la presse et les contributions passent par une revue humaine.",
  },
];
