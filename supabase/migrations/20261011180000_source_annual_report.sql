-- =============================================================================
-- Source : rapport annuel légal publié par l'émetteur (version PDF)
-- -----------------------------------------------------------------------------
-- Pour les émetteurs dont le dépôt ESEF de l'exercice n'est indexé ni par
-- filings.xbrl.org ni par l'AMF (Allemagne, Suède, Espagne…) : le rapport
-- annuel (financier et de durabilité) tel que publié par la société cotée,
-- état de durabilité ESRS soumis à l'assurance d'un auditeur. Une plaquette
-- RSE ou un rapport non audité reste en ESG_REPORT (tier 3).
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('ANNUAL_REPORT', 'Rapport annuel légal publié par l''émetteur', 'regulatory', 'Émetteur coté (marché réglementé UE)', null,
   'Rapport annuel légal (financier et de durabilité) d''une société cotée sur un marché réglementé de l''UE, version publiée par l''émetteur ; état de durabilité ESRS soumis à l''assurance d''un auditeur.')
on conflict (code) do nothing;
