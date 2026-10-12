-- =============================================================================
-- Plastique : le résultat plutôt que la promesse (v0.7.3)
-- -----------------------------------------------------------------------------
-- PLA_REDUCTION notait la signature de l'engagement de la Fondation Ellen
-- MacArthur (une promesse ; aucune preuve n'avait été approuvée). Comme pour le
-- climat (v0.7.1), il devient un résultat : l'évolution réelle du tonnage de
-- plastique vierge publiée par l'entreprise, ramenée à un rythme annuel moyen
-- (variation sur au moins deux ans pour une baisse), classée entre pairs du
-- secteur (rang : plus la baisse est rapide, meilleure la note).
-- Le classement « pire pollueur » (PLA_POLLUTER, audits de marques) reste le
-- plafond du pilier.
-- =============================================================================

update indicators set
  name = 'Évolution réelle du plastique vierge',
  kind = 'quantitative', direction = 'lower_better', unit = '%/an', weight = 1.0,
  methodology = 'Rythme annuel moyen d''évolution du tonnage de plastique vierge publié par l''entreprise (rapport légal, ou à défaut rapport volontaire), entre l''année de référence et la dernière année publiée : r = (1 + variation)^(1/années) − 1. Une baisse ne compte que sur deux ans au moins. Classé entre pairs du secteur : la baisse la plus rapide obtient la meilleure note. Tonnage absolu seulement (pas par unité vendue).'
where code = 'PLA_REDUCTION';

-- Anciennes lignes « signataire de l'engagement » et estimations non sourcées :
-- remplacées par le résultat publié.
update evidence e set review_status = 'rejected', reviewer = 'remplace:resultat-plastique-vierge-2026-10-13'
from indicators i
where i.id = e.indicator_id and e.review_status = 'pending' and i.code in ('PLA_REDUCTION', 'PLA_RECYCLED');
