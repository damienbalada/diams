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
  { name: "GLEIF / SIRENE / SEC", pillar: "—", produces: "Identité des entreprises (LEI, SIREN, CIK), confirmée par le registre officiel", source: "GLEIF, INSEE, SEC", level: "—" },
  { name: "OpenFoodFacts / Wikidata", pillar: "—", produces: "Univers de marques + chaînes de détention", source: "OFF, Wikidata", level: "—" },
  { name: "Rapports annuels ESEF", pillar: "TAX, GOV, LAB, ENV, SUP", produces: "Taux effectif d'impôt (faits IFRS balisés) ; données obligatoires CSRD lues et citées mot pour mot : mixité et indépendance du conseil, écart et ratio de rémunération, Scope 3, intensité carbone, plan de vigilance", source: "filings.xbrl.org, AMF (BDIF), rapports annuels légaux", level: "groupe" },
  { name: "SEC (États-Unis)", pillar: "TAX, LAB, GOV", produces: "Taux effectif d'impôt (XBRL du 10-K) ; ratio PDG / salarié médian et composition du conseil (circulaire DEF 14A)", source: "SEC EDGAR", level: "groupe" },
  { name: "Égapro", pillar: "LAB", produces: "Index égalité professionnelle femmes-hommes (/100), rapprochement par SIREN exact", source: "Ministère du Travail (Égapro)", level: "groupe ou marque" },
  { name: "HATVP", pillar: "GEO", produces: "Inscription et dépenses de lobbying (France)", source: "HATVP", level: "groupe" },
  { name: "Yale", pillar: "GEO", produces: "Position Russie", source: "Yale CELI", level: "groupe" },
  { name: "SBTi", pillar: "ENV", produces: "Objectifs climat validés (anti-greenwashing)", source: "Science Based Targets initiative", level: "groupe" },
  { name: "CDP", pillar: "ENV, WAT", produces: "Notes climat & eau A..D- (barème A = 1,00 … D- = 0,13, F = 0)", source: "CDP", level: "groupe" },
  { name: "BFFP", pillar: "PLA", produces: "Pollueurs plastique : sévérité (plafond) qui borne la note plastique", source: "Break Free From Plastic", level: "groupe ou marque" },
  { name: "Benchmarks", pillar: "ANI, SUP", produces: "BBFAW (Tier 1 → 1,0 … 6 → 0,10), KnowTheChain (/100), FTI (%)", source: "BBFAW, BHRRC, Fashion Revolution", level: "groupe ou marque" },
  { name: "Finance éthique", pillar: "INV", produces: "Financement de l'expansion fossile (Banking on Climate Chaos), politiques d'exclusion", source: "BOCC, Reclaim Finance, UN PRI", level: "groupe" },
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
    body: "Une donnée lue dans un rapport n'entre que si sa citation figure mot pour mot dans le document déposé et contient la valeur (vérificateur automatique). Les cas douteux (définition voisine, périmètre partiel) sont écartés et justifiés dans un journal public.",
  },
  {
    title: "Publication graduée, revue humaine pour le reste",
    body: "Une source réglementaire ou une ONG auditée, vérifiée, est publiée automatiquement. Un rapport rédigé par l'entreprise elle-même, la presse ou une contribution passent par une revue humaine avant de compter.",
  },
];
