-- Évolution des émissions : la règle exclut la banque et l'assurance (émissions surtout financées,
-- périmètre changeant). La preuve d'AXA, déjà hors champ par son secteur, est retirée par cohérence.
update evidence ev set review_status = 'rejected', reviewer = 'retire:hors-champ-assurance-2026-10-17'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and ev.review_status = 'approved'
  and i.code = 'ENV_GHG_TREND' and e.slug = 'axa';
