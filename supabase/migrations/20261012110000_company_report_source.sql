-- =============================================================================
-- Rapport volontaire de l'entreprise (tier 3)
-- -----------------------------------------------------------------------------
-- Hors de l'Union, aucun rapport de durabilité n'est imposé : les émissions de
-- Shein, Apple, Microsoft ou Coca-Cola ne figurent que dans leurs rapports
-- volontaires. Ce sont des déclarations de l'entreprise, non soumises à une
-- obligation légale : niveau 3 (confiance plafonnée). L'éditeur a délégué leur
-- validation (« valide pour moi », 11/10/2026) à la seule condition d'une
-- vérification mot pour mot de la citation (étiquette de relecture distincte :
-- delegue-editeur:verifie-mot-pour-mot).
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('COMPANY_REPORT', 'Rapport volontaire de l''entreprise', 'press', 'Entreprise concernée', null,
   'Rapport de durabilité, d''impact ou environnemental publié volontairement par l''entreprise (hors obligation légale) : déclaration de l''entreprise, niveau 3, citée mot pour mot.')
on conflict (code) do nothing;
