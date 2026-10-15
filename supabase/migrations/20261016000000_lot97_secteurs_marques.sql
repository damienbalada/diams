-- Lot de marques 97 : secteur précis pour les marques importées avec le secteur générique de leur groupe
-- (alimentaire pour Danone, Mars, Magnum ; entretien pour Henkel ; équipement de la maison pour SEB).
update entities set sector_id = (select id from sectors where code = 'food'), updated_at = now() where is_brand and slug in ('real-food-blends', 'functional-formularies', 'kate-farms', 'nutriday', 'ultramel', 'fanmilk', 'jamila', 'salim', 'trefle', 'bebelac', 'nursei', 'sgm', 'dumex', 'international-delight', 'silk');
update entities set sector_id = (select id from sectors where code = 'food'), updated_at = now() where is_brand and slug in ('breyers', 'popsicle');
update entities set sector_id = (select id from sectors where code = 'food'), updated_at = now() where is_brand and slug in ('cheez-it', 'rxbar', 'pop-tarts', 'rice-krispies-treats');
update entities set sector_id = (select id from sectors where code = 'home_care'), updated_at = now() where is_brand and slug in ('weier-riese', 'spee');
update entities set sector_id = (select id from sectors where code = 'household_durables'), updated_at = now() where is_brand and slug in ('supor', 'imusa', 'arno', 'samurai');
