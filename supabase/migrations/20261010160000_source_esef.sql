-- =============================================================================
-- Source ESEF : rapports financiers annuels au format électronique européen
-- -----------------------------------------------------------------------------
-- Les émetteurs dont les titres sont admis sur un marché réglementé de l'UE
-- déposent leur rapport financier annuel au format ESEF (XHTML + balises XBRL
-- IFRS ; règlement délégué (UE) 2019/815), auprès de l'AMF en France. Les
-- valeurs balisées (résultat avant impôt, impôt…) se lisent sans interprétation :
-- tier regulatory, ingestion par connecteur déterministe (import_esef).
-- Répertoire public utilisé : filings.xbrl.org (XBRL International).
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('ESEF', 'Rapport financier annuel (ESEF)', 'regulatory',
   'Émetteur, dépôt auprès de l''autorité de marché (AMF en France)',
   'https://filings.xbrl.org',
   'Rapport financier annuel au format électronique unique européen (XHTML + XBRL IFRS, règlement délégué (UE) 2019/815).')
on conflict (code) do nothing;
