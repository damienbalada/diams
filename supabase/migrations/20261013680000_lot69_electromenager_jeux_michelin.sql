-- Sociétés qui éditent les sites français de marques d'électroménager, d'électronique et
-- de jeux vendues en hypermarché, et le groupe Michelin (pneumatiques, marque au nom du
-- groupe). SIREN vérifiés dans l'annuaire officiel des entreprises et LEI dans le
-- registre GLEIF le 13/10/2026. Asmodee France a pour société mère directe Asmodee Group
-- (GLEIF). Écartées : Tupperware (site européen édité par une autre société depuis la
-- faillite du groupe, propriété de la marque incertaine) et Luminarc (site de vente en
-- ligne d'une filiale de distribution, sans mention du propriétaire de la marque).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('beko-france', 'Beko France', 'Beko France', null, '347688046', 'FR', 'household_durables'),
  ('asmodee-france', 'Asmodee France', 'Asmodee France', '969500XY1KH18IJTAU20', '821169794', 'FR', 'toys_games'),
  ('hisense-france', 'Hisense France', 'Hisense France', null, '800867426', 'FR', 'tech_electronics'),
  ('tcl-industrial', 'TCL Industrial Holdings Co., Ltd', 'TCL Industrial Holdings', null, null, 'CN', 'tech_electronics'),
  ('karcher-sas', 'Kärcher SAS', 'Kärcher France', null, '775702673', 'FR', 'household_durables'),
  ('michelin', 'Compagnie Générale des Établissements Michelin', 'Michelin', null, '855200887', 'FR', 'automotive')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
