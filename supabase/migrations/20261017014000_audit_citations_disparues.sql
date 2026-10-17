-- Audit groupé du 17/10/2026 : 677 sources relues, citations recherchées mot pour mot.
-- TotalEnergies (LobbyMap) : la fiche affiche désormais D+ (et non plus C-) ; preuve retirée, non remplacée
-- tant que la collecte sur LobbyMap n'est pas tranchée (robots.txt).
update evidence set review_status = 'rejected', reviewer = 'retire:audit-citation-perimee-2026-10-17'
 where id = '3c007149-23f7-4061-92fe-2f72103b76fd' and review_status = 'approved';
-- Pavé d'Affinois et Ortiz : page réécrite ; remplacées par une citation actuelle de la même page (lot 170).
update evidence set review_status = 'rejected', reviewer = 'remplace:audit-citation-2026-10-17'
 where id in ('a3899965-5df4-468f-8557-9a05ccabb8c2', 'c7260395-4889-4c24-8b4b-23de274bb8d2') and review_status = 'approved';
-- La Belle-Iloise : page disparue (404), site en JavaScript ; preuve retirée (l'exploitation reste présumée).
update evidence set review_status = 'rejected', reviewer = 'retire:source-disparue-2026-10-17'
 where id = '0f0b0db0-e1f3-473b-8923-15c97aaf0755' and review_status = 'approved';
-- Crédit Coopératif : fausse alerte (preuve de registre, contrôlée par le connecteur HATVP) ; doublon en attente supprimé.
delete from evidence e using entities en, indicators i
 where e.entity_id = en.id and e.indicator_id = i.id and en.slug = 'credit-cooperatif'
   and i.code = 'GEO_LOBBYING_TRANSP' and e.observed_on = '2026-10-17' and e.review_status = 'pending';
