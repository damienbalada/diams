-- Audit des preuves invisibles (16/10/2026) : preuves rattachées à une entité dont le secteur n'est pas
-- dans le champ de l'indicateur.
-- 1. Indice de transparence de la mode (FTI) : Fashion Revolution évalue aussi des groupes de luxe
--    (Hermès, Chanel) et des distributeurs (Amazon, Carrefour, Lidl, Monoprix) ; la liste des secteurs
--    remplace l'ancien secteur unique (mode).
insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where i.code = 'SUP_FTI_SCORE' and s.code in ('fashion_leather', 'luxury_group', 'retail_distribution')
on conflict do nothing;
-- 2. Label « sans fourrure » (Fur Free Retailer) : programme destiné aussi aux distributeurs (Lidl, Monoprix).
insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where i.code = 'ANI_FUR_FREE' and s.code = 'retail_distribution'
on conflict do nothing;
-- 3. Rattachement faux : la note FTI 2023 de « Jockey International Inc » (sous-vêtements, États-Unis)
--    était portée par la marque de fromage blanc Jockey (Danone).
delete from evidence ev using indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id
  and i.code = 'SUP_FTI_SCORE' and e.slug = 'jockey' and ev.excerpt like '%Jockey International Inc%';
