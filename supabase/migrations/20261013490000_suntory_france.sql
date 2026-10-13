-- Suntory en France : Orangina, Schweppes, Pulco, Oasis, MayTea, Champomy.
-- Mentions légales du site de Suntory Beverage & Food France
-- (https://suntorybeverageandfood-europe.com/fr-fr/france/legal/), lues mot pour mot
-- le 13/10/2026 : « Suntory Beverage & Food Europe est la division régionale européenne
-- de Suntory Beverage & Food Limited et fait partie du groupe Suntory. Le Site […] est
-- édité par Orangina Schweppes France […] immatriculée au Registre du Commerce et des
-- Sociétés de Nanterre sous le numéro 404 907 941 ». SIREN vérifié dans l'annuaire
-- officiel des entreprises (entreprise active, nom d'usage Suntory Beverage & Food
-- France) ; LEI de Suntory Beverage & Food Limited (cotée à Tokyo) vérifié dans le
-- registre GLEIF.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('suntory-beverage-food', 'Suntory Beverage & Food Limited', 'Suntory Beverage & Food', '549300FONLMVK7YYYH41', null, 'JP', 'beverages'),
  ('orangina-schweppes-france', 'Orangina Schweppes France', 'Suntory Beverage & Food France (Orangina Schweppes France)', null, '404907941', 'FR', 'beverages')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;

update entities
   set parent_id = (select id from entities where slug = 'suntory-beverage-food'),
       ownership_pct = 100,
       updated_at = now()
 where slug = 'orangina-schweppes-france'
   and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = 'orangina-schweppes-france'), (select id from entities where slug = 'suntory-beverage-food'),
       'https://suntorybeverageandfood-europe.com/fr-fr/france/legal/',
       'Mentions légales du site de Suntory Beverage & Food France : « Suntory Beverage & Food Europe est la division régionale européenne de Suntory Beverage & Food Limited et fait partie du groupe Suntory. Le Site www.suntorybeverageandfood-europe.com/fr-FR/france/ est édité par Orangina Schweppes France, une société de droit français au capital de 446 036 924,00€, dont le siège social est situé au 52 boulevard du Parc, 92200 Neuilly-sur-Seine, immatriculée au Registre du Commerce et des Sociétés de Nanterre sous le numéro 404 907 941. »',
       '2026-10-13', 'delegue-editeur:verifie-mot-pour-mot'
on conflict (entity_id, owner_id, source_url) do nothing;
