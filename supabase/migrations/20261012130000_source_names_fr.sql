-- =============================================================================
-- Noms des sources en français (affichés sur chaque fiche)
-- -----------------------------------------------------------------------------
-- La fiche affiche désormais le nom de la source plutôt que son code. Les noms
-- anglais sont traduits ; le nom propre reste entre parenthèses pour qu'on
-- retrouve l'organisation.
-- =============================================================================

update sources s set name = v.name
from (values
  ('BBFAW', 'Classement du bien-être animal en élevage (BBFAW)'),
  ('BFFP', 'Audits de marques des déchets plastiques (Break Free From Plastic)'),
  ('BHRRC', 'Centre de ressources entreprises et droits humains (BHRRC)'),
  ('BOCC', 'Rapport d''ONG sur le financement des énergies fossiles (Banking on Climate Chaos)'),
  ('B_LAB', 'Annuaire des entreprises certifiées B Corp (B Lab)'),
  ('CDP', 'Questionnaire climat et eau (CDP)'),
  ('EMF_GC', 'Engagement mondial sur le plastique (Fondation Ellen MacArthur)'),
  ('FAIR_WEAR', 'Fondation Fair Wear (conditions de travail dans la mode)'),
  ('FTI', 'Indice de transparence de la mode (Fashion Revolution)'),
  ('FUR_FREE', 'Label sans fourrure (Fur Free Retailer)'),
  ('HIGG', 'Indice Higg (impact des matières)'),
  ('INFLUENCEMAP', 'Lobbying climat (InfluenceMap)'),
  ('KNOWTHECHAIN', 'Classement du travail forcé dans les chaînes d''approvisionnement (KnowTheChain)'),
  ('KSE_LEAVE_RUSSIA', 'Sortie de Russie (KSE Institute, « Leave Russia »)'),
  ('LWG', 'Certification des tanneries (Leather Working Group)'),
  ('NEW_CLIMATE', 'Évaluation des engagements climat des entreprises (NewClimate Institute)'),
  ('OPENSECRETS', 'Lobbying et financement politique aux États-Unis (OpenSecrets)'),
  ('SBTI', 'Objectifs climat fondés sur la science (SBTi)'),
  ('SEC_FILING', 'Documents déposés à la SEC (circulaire de procuration, rapport annuel 10-K)'),
  ('TAX_JUSTICE', 'Réseau pour la justice fiscale (Tax Justice Network)'),
  ('TEXTILE_EXCHANGE', 'Indice des matières textiles (Textile Exchange)'),
  ('TE_STANDARDS', 'Normes de bien-être animal des matières (Textile Exchange)'),
  ('UN_PRI', 'Principes pour l''investissement responsable (ONU)'),
  ('YALE_RUSSIA', 'Liste des entreprises restées en Russie (Université Yale)')
) as v(code, name)
where s.code = v.code;
