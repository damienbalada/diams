-- Confiseurs et torréfacteur européens dont les marques sont vendues en hypermarché ;
-- LEI vérifiés dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('storck', 'August Storck KG', 'Storck', '529900YNBT62HCUPRG10', null, 'DE', 'food'),
  ('alfred-ritter', 'Alfred Ritter GmbH & Co. KG', 'Alfred Ritter (Ritter Sport)', '529900349RA56TFGAP64', null, 'DE', 'food'),
  ('lavazza', 'Luigi Lavazza S.p.A.', 'Groupe Lavazza', '815600A32CD898614484', null, 'IT', 'beverages')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;

-- Carte Noire SAS (marque Carte Noire, et éditrice du site français de Lavazza :
-- « © CARTE NOIRE SAS 2025 » sur www.lavazza.fr) appartient au groupe Lavazza depuis
-- 2016. Page « Our brands » du site du groupe
-- (https://www.lavazzagroup.com/en/our-brands.html), lue mot pour mot le 13/10/2026.
update entities
   set parent_id = (select id from entities where slug = 'lavazza'),
       ownership_pct = 100,
       updated_at = now()
 where slug = 'carte-noire-sas'
   and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = 'carte-noire-sas'), (select id from entities where slug = 'lavazza'),
       'https://www.lavazzagroup.com/en/our-brands.html',
       'Page « Our brands » du site officiel du groupe Lavazza (en anglais) : « Our Group encompasses the global brand of Lavazza , as well as the Carte Noire , Kicking Horse and Merrild brands, all market leaders in their respective countries » ; « Today, Carte Noire is the top brand in terms of penetration in the French coffee market. A perfect brand for our Group, which it joined in 2016. »',
       '2026-10-13', 'delegue-editeur:verifie-mot-pour-mot'
on conflict (entity_id, owner_id, source_url) do nothing;
