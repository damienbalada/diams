-- Sociétés qui éditent les sites de marques non alimentaires vendues en hypermarché
-- (jouets, papeterie, électroménager, animalerie). SIREN vérifiés dans l'annuaire officiel
-- des entreprises et LEI dans le registre GLEIF le 13/10/2026. Pilot Pen France a pour
-- société mère directe Pilot Corporation of Europe (GLEIF). Whirlpool n'est pas retenue :
-- en Europe, la marque est exploitée par European Appliances France SAS (Beko Europe).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('vtech-electronics-europe', 'VTech Electronics Europe BV', 'VTech Electronics Europe', null, null, 'NL', 'toys_games'),
  ('smoby-toys', 'Smoby Toys SAS', 'Smoby Toys', '9695005CZ9EHLNG9XP55', '503233421', 'FR', 'toys_games'),
  ('pilot-pen-france', 'Pilot Pen France', 'Pilot Pen France', '969500TMZ93AMQNCJF30', '798362778', 'FR', 'household_durables'),
  ('clairefontaine-rhodia', 'Clairefontaine-Rhodia', 'Clairefontaine-Rhodia', '969500OH2DS5RUKIAF28', '339956781', 'FR', 'household_durables'),
  ('bsh-electromenager', 'BSH Electroménager', 'BSH Électroménager (Bosch)', null, '341911790', 'FR', 'household_durables'),
  ('zolux', 'Zolux', 'Zolux (société)', '9695006Z277T5CXXSO54', '431967447', 'FR', 'household_durables')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
