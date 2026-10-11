-- =============================================================================
-- Source : documents d'enregistrement universel déposés à l'AMF (BDIF)
-- -----------------------------------------------------------------------------
-- Base des décisions et informations financières de l'Autorité des marchés
-- financiers : le document tel que déposé par l'émetteur (rapport financier
-- annuel, rapport de gestion et état de durabilité CSRD compris). Utilisée
-- quand le dépôt ESEF de l'exercice n'est pas encore indexé par filings.xbrl.org.
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('AMF_BDIF', 'Document d''enregistrement universel déposé à l''AMF', 'regulatory', 'Autorité des marchés financiers',
   'https://bdif.amf-france.org/',
   'Document d''enregistrement universel tel que déposé auprès de l''AMF (numéro D.AA-NNNN) : rapport financier annuel, rapport de gestion et état de durabilité (CSRD).')
on conflict (code) do nothing;
