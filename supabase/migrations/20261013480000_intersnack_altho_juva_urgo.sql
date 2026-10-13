-- Deux fabricants de chips et biscuits apéritifs vendus en hypermarché, identifiés par
-- les mentions légales des sites de leurs marques ; SIREN et LEI vérifiés dans
-- l'annuaire officiel des entreprises et le registre GLEIF le 13/10/2026.
-- Intersnack France (Vico, Curly, Monster Munch, Tyrrell's) a pour présidente la
-- société Intersnack International B.V. ; Altho (Bret's) a pour présidente Alain Glon
-- Holding (annuaire officiel des entreprises).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('intersnack-france', 'Intersnack France', 'Intersnack France (Vico)', '969500F3XO79N25PM642', '412581878', 'FR', 'food'),
  ('altho', 'Altho', 'Altho (Bret''s)', '969500HIPBJZTZAEHK75', '397729591', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;

-- Laboratoires Juva Santé (Mercurochrome), créés comme société indépendante au lot 33,
-- appartiennent au Groupe Urgo. Mentions légales du site officiel de Ricqlès
-- (https://www.ricqles.fr/mentions-legales/), lues mot pour mot le 13/10/2026 :
-- « ricqles.fr est un site co-édité et sous la co-responsabilité des Laboratoires JUVA
-- SANTÉ et des LABORATOIRES SUPERDIET toutes deux des entreprises du GROUPE URGO ».
update entities
   set parent_id = (select id from entities where slug = 'urgo'),
       ownership_pct = 100,
       updated_at = now()
 where slug = 'juva-sante'
   and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = 'juva-sante'), (select id from entities where slug = 'urgo'),
       'https://www.ricqles.fr/mentions-legales/',
       'Mentions légales du site officiel de la marque Ricqlès : « ricqles.fr est un site co-édité et sous la co-responsabilité des Laboratoires JUVA SANTÉ et des LABORATOIRES SUPERDIET toutes deux des entreprises du GROUPE URGO et commercialisant la marque Ricqlès »',
       '2026-10-13', 'delegue-editeur:verifie-mot-pour-mot'
on conflict (entity_id, owner_id, source_url) do nothing;
