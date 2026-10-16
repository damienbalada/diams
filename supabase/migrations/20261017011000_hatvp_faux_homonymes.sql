-- Répertoire des représentants d'intérêts (HATVP), audit du 17/10/2026 : rapprochements par le nom faux
-- pour des marques sans SIREN. Axe (« AXE 3 E »), Côte d'Or (« MEDEF Côte d'Or »), Île de France (« Collectif
-- vélo Île-de-France »), La Vie (« FNATH, association des accidentés de la vie »), Mont Blanc desserts et eau
-- (« Chambre d'agriculture de Savoie Mont Blanc »), Roquefort Société (« Société L.D.C. »), EcoLogic de Spectrum
-- Brands (« Ecologic », éco-organisme), Coca-Cola (« Coca-Cola Europacific Partners France », embouteilleur
-- indépendant de The Coca-Cola Company), Burger King (« Burger King France », franchisé du groupe Bertrand,
-- pas RBI). Inscriptions et dépenses retirées.
update evidence ev set review_status = 'rejected', reviewer = 'retire:hatvp-homonyme-2026-10-17'
from sources s, entities e
where ev.source_id = s.id and ev.entity_id = e.id and s.code = 'HATVP' and ev.review_status = 'approved'
  and e.slug in ('axe', 'cote-dor', 'ile-de-france', 'la-vie', 'mont-blanc-desserts', 'mont-blanc-eau',
                 'roquefort-societe', 'ecologic', 'coca-cola-classic', 'burger-king');
