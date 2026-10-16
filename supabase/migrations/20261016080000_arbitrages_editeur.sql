-- Arbitrages de l'éditeur du 16/10/2026 sur trois preuves vérifiées mot pour mot mais signalées
-- « à trancher » par l'outil de vérification.
--  - H&M : l'écart de 0,3 % découle de la formulation du rapport (rémunération moyenne des femmes à
--    99,7 % de celle des hommes) : validé.
--  - Michelin et Les Mousquetaires : le lobbying est déclaré à la HATVP par une autre société du
--    groupe ; attribué au groupe, avec la mention de la société déclarante.
update evidence ev
set excerpt = 'MANUF FRANC PNEUMATIQ MICHELIN inscrit au répertoire des représentants d''intérêts depuis le 22/12/2017 ; dépenses déclarées pour 2025 : 600 000 à 700 000 € (société déclarante : Manufacture française des pneumatiques Michelin, SIREN 855200507, et non la Compagnie générale des établissements Michelin ; attribué au groupe).'
from entities en, indicators i
where en.id = ev.entity_id and i.id = ev.indicator_id and en.slug = 'michelin' and i.code = 'GEO_LOBBYING_TRANSP'
  and ev.review_status = 'pending' and ev.excerpt like 'MANUF FRANC PNEUMATIQ MICHELIN inscrit%';

update evidence ev
set excerpt = 'LES MOUSQUETAIRES inscrit au répertoire des représentants d''intérêts depuis le 06/04/2018 ; dépenses déclarées pour 2025 : 100 000 à 200 000 € (société déclarante : la holding LES MOUSQUETAIRES, SIREN 789169323, et non ITM Entreprises ; attribué au groupe).'
from entities en, indicators i
where en.id = ev.entity_id and i.id = ev.indicator_id and en.slug = 'mousquetaires' and i.code = 'GEO_LOBBYING_TRANSP'
  and ev.review_status = 'pending' and ev.excerpt like 'LES MOUSQUETAIRES inscrit%';

update evidence ev
set review_status = 'approved', reviewer = 'editeur:arbitrage-2026-10-16'
from entities en, indicators i
where en.id = ev.entity_id and i.id = ev.indicator_id and ev.review_status = 'pending'
  and ((en.slug in ('michelin', 'mousquetaires') and i.code = 'GEO_LOBBYING_TRANSP')
    or (en.slug = 'hm-group' and i.code = 'LAB_GENDER_PAYGAP'));
