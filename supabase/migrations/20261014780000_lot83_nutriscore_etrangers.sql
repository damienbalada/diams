-- Sociétés étrangères qui déclarent des marques vendues en France dans la liste officielle de
-- Santé publique France « Entreprises et marques utilisant le Nutri-Score en France »
-- (janvier 2026) : nom légal identique à une seule entité active du registre GLEIF
-- (identifiants d'entités juridiques), lu le 14/10/2026. Écartées : Norma (la « marque »
-- relevée est un numéro de TVA) et Del Monte (propriété de la marque partagée selon les pays).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('auga-group', 'AUGA group, AB', 'AUGA group', '48510000P2S3LHJPX414', null, 'LT', 'food'),
  ('costa-meeresspezialitaten', 'COSTA Meeresspezialitäten GmbH & Co. KG', 'COSTA Meeresspezialitäten', '529900ZVZTMQFT1Y2C40', null, 'DE', 'food'),
  ('cui-zsq-food', 'CUI ZSQ FOOD, S.L.', 'CUI ZSQ FOOD', '959800HY194MP3TJSB23', null, 'ES', 'food'),
  ('faropeixe-comercio-geral-de-peixe', 'FAROPEIXE - COMÉRCIO GERAL DE PEIXE LDA', 'FAROPEIXE - COMÉRCIO GERAL DE PEIXE', '9845002C0CDC06EE9997', null, 'PT', 'food'),
  ('grau-nuts', 'GRAU NUTS S.A.U.', 'GRAU NUTS', '959800LR0J9W2Z0D9X06', null, 'ES', 'food'),
  ('hijos-de-teodoro-munoz', 'HIJOS DE TEODORO MUÑOZ, S.L.', 'HIJOS DE TEODORO MUÑOZ', '959800GKB7WG3W51Y853', null, 'ES', 'food'),
  ('jalhuca-explotaciones', 'JALHUCA EXPLOTACIONES SL', 'JALHUCA EXPLOTACIONES', '9598001R3KR8GX0FED80', null, 'ES', 'food'),
  ('kruger', 'Krüger GmbH', 'Krüger', '391200LGIMFNWVZ3RZ54', null, 'DE', 'food'),
  ('lantmannen-unibake-germany', 'Lantmännen Unibake Germany GmbH & Co. KG', 'Lantmännen Unibake Germany', '5299003CS8L30XS1V859', null, 'DE', 'food'),
  ('medicura-naturprodukte', 'MEDICURA Naturprodukte AG', 'MEDICURA Naturprodukte', '529900JRFXN5N797PF34', null, 'DE', 'food'),
  ('musclestadt-sporternahrung', 'Musclestadt Sporternährung GmbH', 'Musclestadt Sporternährung', '3912007LBDFEH3XK7Z37', null, 'DE', 'food'),
  ('pedon', 'PEDON S.P.A.', 'PEDON', '815600F3087FAD0DB715', null, 'IT', 'food'),
  ('pescafacil', 'PESCAFACIL SL', 'PESCAFACIL', '95980020140005883421', null, 'ES', 'food'),
  ('petaca-chico', 'PETACA CHICO SL', 'PETACA CHICO', '95980020140005843166', null, 'ES', 'food'),
  ('united-confectionary', 'UNITED CONFECTIONARY S.L.U.', 'UNITED CONFECTIONARY', '959800G9RRQYKY8Q2Y58', null, 'ES', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
