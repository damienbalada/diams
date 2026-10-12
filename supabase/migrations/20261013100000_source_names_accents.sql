-- =============================================================================
-- Noms des sources : accents rétablis et sigles expliqués en français
-- -----------------------------------------------------------------------------
-- « Commission europeenne », « Autorites de protection des donnees » : saisis
-- sans accents à l'origine, désormais affichés sur les fiches (sanctions).
-- Les sigles seuls (HATVP, URD, DPEF, GLEIF…) sont développés.
-- =============================================================================

update sources set name = 'Commission européenne — Concurrence', publisher = 'Commission européenne'
where code = 'EU_COMPETITION';
update sources set name = 'Autorités de protection des données personnelles (RGPD)',
  publisher = 'CNIL (France), DPC (Irlande), Comité européen de la protection des données'
where code = 'GDPR_DPA';
update sources set name = 'Registre des représentants d''intérêts (HATVP)' where code = 'HATVP';
update sources set name = 'Comptes des partis politiques (CNCCFP)' where code = 'CNCCFP';
update sources set name = 'Document d''enregistrement universel (volet financier)' where code = 'URD_FINANCE';
update sources set name = 'Déclaration de performance extra-financière (volet social)' where code = 'DPEF';
update sources set name = 'Identifiant international d''entité juridique (GLEIF)' where code = 'GLEIF';
update sources set name = 'États de durabilité (CSRD)' where code = 'CSRD_ESRS';
update sources set name = 'Registre de transparence de l''Union européenne' where code = 'EU_TRANSPARENCY';
update sources set name = 'Directive européenne sur la transparence salariale' where code = 'EU_PAY_TRANSP';
update sources set name = 'Rapport de la rapporteuse spéciale de l''ONU sur les territoires palestiniens occupés (A/HRC/59/23)'
where code = 'UN_SR_OPT';
update sources set name = 'Base de données de l''ONU (HCDH) — entreprises et colonies' where code = 'UN_OHCHR';
update sources set name = 'Registre des entreprises (INPI, répertoire SIRENE de l''Insee)' where code = 'INPI_SIRENE';
update sources set name = 'Documents déposés à l''AMF' where code = 'AMF';
