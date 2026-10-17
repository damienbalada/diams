-- Lot 222 : propriétaires de marques non alimentaires (suivi Open Products Facts, 17/10/2026), nommés dans
-- les mentions légales ou le pied de page du site officiel de chaque marque. SIREN vérifiés dans l'annuaire
-- officiel et LEI dans GLEIF le 17/10/2026 (actifs) ; sans LEI : Shokz Euro, Moleskine Srl, Ugreen Group.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('tp-link-enterprises-france', 'TP-LINK ENTERPRISES FRANCE', 'TP-Link Enterprises France', null, '850105123', 'FR', 'tech_electronics'),
  ('shokz-euro', 'Shokz Euro B.V.', 'Shokz Euro', null, null, 'NL', 'tech_electronics'),
  ('arena-spa', 'ARENA S.P.A.', 'Arena (société)', '8156005C51F30B1FEC30', null, 'IT', 'fashion_leather'),
  ('beaba-sas', 'BEABA', 'Béaba (société)', null, '352684377', 'FR', 'household_durables'),
  ('bioviva-editions', 'BIOVIVA EDITIONS', 'Bioviva Éditions', null, '409686888', 'FR', 'toys_games'),
  ('interlude-games', 'INTERLUDE GAMES', 'Interlude (Cocktail Games)', null, '493414221', 'FR', 'toys_games'),
  ('dr-beckmann-group-france', 'DR. BECKMANN GROUP FRANCE', 'Dr. Beckmann Group France', null, '818880023', 'FR', 'home_care'),
  ('dreame-international', 'Dreame International (HongKong) Limited', 'Dreame International', '98450060B3E38740D979', null, 'HK', 'household_durables'),
  ('fellowes-inc', 'FELLOWES, INC.', 'Fellowes (société)', '549300KXGFBOIZDNIW71', null, 'US', 'household_durables'),
  ('evergreen-garden-care-france', 'EVERGREEN GARDEN CARE FRANCE SAS', 'Evergreen Garden Care France', null, '830854006', 'FR', 'home_care'),
  ('werner-mertz', 'Werner & Mertz GmbH', 'Werner & Mertz', '529900PHKIKL9OSBCG77', null, 'DE', 'home_care'),
  ('madrigall', 'MADRIGALL', 'Madrigall (groupe Gallimard)', null, '389332677', 'FR', 'publishing'),
  ('iello-sas', 'IELLO', 'Iello (société)', null, '478339617', 'FR', 'toys_games'),
  ('franckh-kosmos', 'Franckh-Kosmos Verlags-GmbH & Co. KG', 'Franckh-Kosmos', '391200013E3CSFJWWN55', null, 'DE', 'toys_games'),
  ('moleskine-srl', 'Moleskine Srl', 'Moleskine (société)', null, null, 'IT', 'household_durables'),
  ('laboratoires-nhco-nutrition', 'LABORATOIRES NHCO NUTRITION', 'Laboratoires NHCO Nutrition', null, '503363111', 'FR', 'personal_care'),
  ('northwave-srl', 'NORTHWAVE S.R.L.', 'Northwave (société)', '8156000ED9A13AD3CC81', null, 'IT', 'fashion_leather'),
  ('editions-oberthur', 'EDITIONS OBERTHUR', 'Éditions Oberthur', null, '329286066', 'FR', 'household_durables'),
  ('pop-mart-france', 'POP MART FRANCE', 'Pop Mart France', null, '919005439', 'FR', 'toys_games'),
  ('puma-europe', 'PUMA Europe GmbH', 'PUMA Europe', '529900BMH4WOV2MWXU51', null, 'DE', 'fashion_leather'),
  ('puressentiel-france', 'PURESSENTIEL FRANCE', 'Puressentiel France', null, '418425716', 'FR', 'personal_care'),
  ('ugreen-group', 'Ugreen Group Limited', 'Ugreen Group', null, null, 'CN', 'tech_electronics'),
  ('wirquin-plastiques', 'WIRQUIN PLASTIQUES', 'Wirquin Plastiques', null, '309494953', 'FR', 'household_durables'),
  ('flam-up-sas', 'FLAM''UP', 'Flam''Up (société)', null, '334111457', 'FR', 'home_care'),
  ('laboratoires-nutrimea', 'LABORATOIRES NUTRIMEA', 'Laboratoires Nutrimea (Plastimea)', null, '539390633', 'FR', 'household_durables')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
