-- LEI de la Compagnie Générale des Établissements Michelin (registre GLEIF, enregistré
-- sous le SIREN 855 200 887), lu le 13/10/2026.
update entities set lei = '549300SOSI58J6VIW052', updated_at = now()
 where slug = 'michelin' and lei is null;

-- Pilot Corporation of Europe (SIREN 399 424 753) : société mère directe de Pilot Pen
-- France selon le registre GLEIF (relation « IS_DIRECTLY_CONSOLIDATED_BY », active),
-- lue le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'pilot-corporation-of-europe', 'Pilot Corporation of Europe', 'Pilot Corporation of Europe', '969500TD45HFDX6LI918', '399424753', 'FR', s.id, false
from sectors s where s.code = 'household_durables'
on conflict (slug) do nothing;

update entities
   set parent_id = (select id from entities where slug = 'pilot-corporation-of-europe'),
       ownership_pct = null,
       updated_at = now()
 where slug = 'pilot-pen-france'
   and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = 'pilot-pen-france'), (select id from entities where slug = 'pilot-corporation-of-europe'),
       'https://api.gleif.org/api/v1/lei-records/969500TMZ93AMQNCJF30/direct-parent-relationship',
       'Registre GLEIF, relation de consolidation de Pilot Pen France (LEI 969500TMZ93AMQNCJF30) : « IS_DIRECTLY_CONSOLIDATED_BY » Pilot Corporation of Europe (LEI 969500TD45HFDX6LI918), statut « ACTIVE ».',
       '2026-10-13', 'delegue-editeur:verifie-mot-pour-mot'
on conflict (entity_id, owner_id, source_url) do nothing;
