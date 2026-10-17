-- Offre végétale TREK / Lotus Bakeries (lot 195) : citation complétée par la mention de la marque TREK,
-- vérifiée mot pour mot dans le rapport annuel 2025 (ESEF) avant mise à jour.
update evidence set excerpt = 'Rapport annuel 2025 de Lotus Bakeries, propriétaire de la marque TREK (ESEF, en néerlandais), stratégie des marques : « breidde zijn portfolio uit met de TREK » ; « Protein Flapjack met Biscoff » ; « een vegan proteïnereep » — la marque propose au moins un produit vegan ; elle n''est pas pour autant entièrement végétale.'
 where review_status = 'approved' and observed_on = '2026-04-07'
   and indicator_id = (select id from indicators where code = 'ANI_OFFRE_VEGETALE')
   and entity_id = (select id from entities where slug = 'trek-snacks');
update evidence set excerpt = 'Rapport annuel 2025 de Lotus Bakeries (ESEF, en néerlandais), stratégie des marques : « breidde zijn portfolio uit met de TREK » ; « Protein Flapjack met Biscoff » ; « een vegan proteïnereep » — le groupe propose au moins un produit vegan ; il n''est pas pour autant végétal.'
 where review_status = 'approved' and observed_on = '2026-04-07'
   and indicator_id = (select id from indicators where code = 'ANI_OFFRE_VEGETALE')
   and entity_id = (select id from entities where slug = 'lotus-bakeries');
