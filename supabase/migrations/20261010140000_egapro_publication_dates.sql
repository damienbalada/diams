-- =============================================================================
-- Égapro : date de publication corrigée (N+1)
-- -----------------------------------------------------------------------------
-- La colonne « Année » des données Égapro est l'année de CALCUL de l'index ; sa
-- publication est obligatoire au plus tard le 1er mars de l'année suivante
-- (C. trav. D1142-4 ; les premières déclarations, au titre de 2018, datent de
-- mars 2019). Le connecteur datait l'index de l'année de calcul : un an trop
-- tôt, donc une décote à 5 ans anticipée d'un an. Corrigé dans import_egapro.py ;
-- ici, les lignes déjà importées par le connecteur sont décalées d'un an.
-- Conditionnel (format exact de l'extrait) : rejouer est sans effet.
-- =============================================================================

update evidence ev
set observed_on = (ev.observed_on + interval '1 year')::date
from sources s
where ev.source_id = s.id and s.code = 'EGAPRO'
  and ev.reviewer = 'auto:pipeline'
  and ev.observed_on = make_date(substring(ev.excerpt from 'Index Égapro (\d{4})')::int, 3, 1);
