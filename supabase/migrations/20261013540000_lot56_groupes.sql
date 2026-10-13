-- Groupes des marques du lot 56 : Suntory Holdings et sa filiale de spiritueux Suntory
-- Global Spirits (Jim Beam, Laphroaig, Roku…), et les sociétés qui éditent les sites de
-- marques vendues en hypermarché (Saint Jean, Brasserie Castelain, Ethiquable, Les
-- Crudettes, Galletas Gullón, Conservas Ortiz). SIREN vérifiés dans l'annuaire officiel
-- des entreprises et LEI dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('suntory-holdings', 'Suntory Holdings Limited', 'Suntory Holdings', '54930074QUY8RD0UZM08', null, 'JP', 'beverages'),
  ('suntory-global-spirits', 'Suntory Global Spirits Inc.', 'Suntory Global Spirits', 'EWRDABCN7XBHM37LIA98', null, 'US', 'wines_spirits'),
  ('saint-jean-sas', 'Saint Jean', 'Saint Jean (société)', null, '311821268', 'FR', 'food'),
  ('brasserie-castelain', 'Brasserie Castelain', 'Brasserie Castelain', null, '315255752', 'FR', 'wines_spirits'),
  ('ethiquable-scop', 'Ethiquable', 'Ethiquable (coopérative)', '96950081UXNUBZ1HDM29', '449164482', 'FR', 'food'),
  ('les-crudettes-sas', 'Les Crudettes', 'Les Crudettes (société)', null, '343127585', 'FR', 'food'),
  ('galletas-gullon', 'Galletas Gullón, S.A.', 'Galletas Gullón', '95980020140005778758', null, 'ES', 'food'),
  ('conservas-ortiz', 'Conservas Ortiz, S.A.', 'Conservas Ortiz', '95980020140005690876', null, 'ES', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;

-- Suntory Global Spirits (ex-Beam Suntory) appartient à Suntory Holdings depuis le
-- rachat de Beam Inc. en 2014. Page « About us » du site officiel
-- (https://www.suntoryglobalspirits.com/about-us), lue mot pour mot le 13/10/2026.
update entities
   set parent_id = (select id from entities where slug = 'suntory-holdings'),
       ownership_pct = 100,
       updated_at = now()
 where slug = 'suntory-global-spirits'
   and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = 'suntory-global-spirits'), (select id from entities where slug = 'suntory-holdings'),
       'https://www.suntoryglobalspirits.com/about-us',
       'Page « About us » du site officiel de Suntory Global Spirits (en anglais), frise historique : « 2014 Suntory Holdings acquires Beam Inc. to create Suntory Global Spirits, a world leader in premium spirits. »',
       '2026-10-13', 'delegue-editeur:verifie-mot-pour-mot'
on conflict (entity_id, owner_id, source_url) do nothing;

-- Charal SAS (SIREN 546 950 379, éditrice du site charal.fr) fait partie du Groupe Bigard :
-- le site du groupe présente Charal parmi ses marques, et l'annuaire officiel des
-- entreprises désigne la Société Financière Bigard comme présidente de Charal SAS.
-- Page « Fiers de la vitalité de nos marques »
-- (https://www.groupe-bigard.fr/notre-groupe/fiers-de-la-vitalite-de-nos-marques.html),
-- lue mot pour mot le 13/10/2026.
update entities
   set parent_id = (select id from entities where slug = 'bigard'),
       updated_at = now()
 where slug = 'charal-sas'
   and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = 'charal-sas'), (select id from entities where slug = 'bigard'),
       'https://www.groupe-bigard.fr/notre-groupe/fiers-de-la-vitalite-de-nos-marques.html',
       'Page « Fiers de la vitalité de nos marques » du site officiel du Groupe Bigard : « Forts de nos nombreuses années d’existence, nous avons su développer nos métiers et savoir-faire au travers de différentes marques, chacunes reconnues pour leurs expertises. » ; « CHARAL : La viande devrait toujours être aussi bonne que ça ! Marque de viande préférée des Français, CHARAL propose depuis plus de 30 ans des viandes reconnues pour leurs qualités gustatives et nutritionnelles. »',
       '2026-10-13', 'delegue-editeur:verifie-mot-pour-mot'
on conflict (entity_id, owner_id, source_url) do nothing;
