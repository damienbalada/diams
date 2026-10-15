-- Lot 108 : l'outil de vérification avait approuvé, pour Louis Vuitton et Bottega Veneta, la ligne
-- en attente dont la citation disait seulement « maroquinerie », alors que la citation vérifiée mot
-- pour mot (ci-dessous) écrit « cuir ». On remplace la citation par celle qui a été vérifiée.
-- L'outil compare désormais la citation avant d'approuver (verify_curated.approve).
update evidence ev
set excerpt = 'Document d''enregistrement universel 2025 déposé à l''AMF (D.26-0195) : « En Espagne, les ateliers Louis Vuitton, en plus de la fabrication de maroquinerie, concentrent également l’ensemble de l’activité Accessoires Cuir (ceintures, bracelets) » — recours à l''exploitation animale (cuir (ceintures, bracelets)).',
    value_text = 'cuir (ceintures, bracelets)'
from entities en, indicators i
where en.id = ev.entity_id and i.id = ev.indicator_id and en.slug = 'louis-vuitton' and i.code = 'ANI_EXPLOITATION'
  and ev.excerpt like '%vingt-neuf ateliers%';

update evidence ev
set excerpt = 'Document d''enregistrement universel 2025 déposé à l''AMF (D.26-0266) : « Bottega Veneta a mis en place plusieurs projets de recyclage et réutilisation de ses chutes de cuir » — recours à l''exploitation animale (cuir).',
    value_text = 'cuir'
from entities en, indicators i
where en.id = ev.entity_id and i.id = ev.indicator_id and en.slug = 'bottega-veneta' and i.code = 'ANI_EXPLOITATION'
  and ev.excerpt like '%cœur de métier de Bottega Veneta%';
