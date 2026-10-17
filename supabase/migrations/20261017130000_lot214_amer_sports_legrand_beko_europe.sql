-- Lot 214 : propriétaires de marques non alimentaires absentes (Open Products Facts, 17/10/2026).
--  - Amer Sports, Inc. (George Town, îles Caïmans ; Salomon, Atomic, Wilson, Arc'teryx, Peak
--    Performance) ; LEI vérifié dans GLEIF le 17/10/2026 (391200YCSWTRD1J21867, actif).
--  - Legrand (Limoges) ; LEI vérifié dans GLEIF (969500XXRPGD7HCAFA90, actif) et SIREN dans l'annuaire
--    officiel des entreprises (421259615, actif) le 17/10/2026.
--  - Beko Europe B.V. (Amsterdam), licenciée de la marque Whirlpool pour l'Europe (rapport 10-K 2025 de
--    Whirlpool Corporation) : même règle que Pyrex (décision de l'éditeur du 17/10/2026), la marque est
--    rattachée à la société qui vend en Europe et la preuve nomme le propriétaire. LEI vérifié dans GLEIF
--    le 17/10/2026 (984500BA7EDAE5BC8B05, actif).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('amer-sports', 'Amer Sports, Inc.', 'Amer Sports', '391200YCSWTRD1J21867', null, 'KY', 'fashion_leather'),
  ('legrand', 'LEGRAND', 'Legrand', '969500XXRPGD7HCAFA90', '421259615', 'FR', 'household_durables'),
  ('beko-europe', 'Beko Europe B.V.', 'Beko Europe (licence Whirlpool pour l''Europe)', '984500BA7EDAE5BC8B05', null, 'NL', 'household_durables')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
