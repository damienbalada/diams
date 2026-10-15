-- Collecte complète (15/10/2026), lecture des rapports réglementés : la consignation générique
-- « donnée non trouvée par recherche dans le texte du rapport » a été écrite aussi pour 18 cases
-- qui avaient déjà une explication précise (une seule année de comparaison, publié autrement…).
-- On retire ces lignes génériques en doublon ; l'explication précise reste.
delete from indicator_reviews g
where g.reviewer = 'lecture-rapport'
  and g.detail like '%non trouvée par recherche dans le texte du rapport%'
  and exists (select 1 from indicator_reviews s
              where s.reviewer = 'lecture-rapport' and s.entity_id = g.entity_id
                and s.indicator_id = g.indicator_id and s.id <> g.id
                and s.detail not like '%non trouvée par recherche dans le texte du rapport%');
