-- Sociétés éditrices des sites officiels de marques alimentaires (mentions légales), SIREN
-- vérifiés dans l'annuaire officiel des entreprises le 14/10/2026 ; LEI de Labeyrie Fine
-- Foods France et lien avec Labeyrie Fine Foods lus dans le registre GLEIF (relation
-- « IS_DIRECTLY_CONSOLIDATED_BY », active).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('pep', 'PEP', 'PEP (Cocotine)', null, '420800492', 'FR', 'food'),
  ('labeyrie-fine-foods-france', 'LABEYRIE FINE FOODS FRANCE', 'Labeyrie Fine Foods France', '96950063PTGNALD6GE17', '882587314', 'FR', 'food'),
  ('borges-tramier', 'BORGES - TRAMIER', 'Borges-Tramier', null, '304012917', 'FR', 'food'),
  ('k-et-s-france', 'K+S FRANCE', 'K+S France', null, '414982942', 'FR', 'food'),
  ('jean-herve', 'JEAN HERVE', 'Jean Hervé (société)', null, '380846618', 'FR', 'food'),
  ('manufacture-cluizel', 'MANUFACTURE CLUIZEL', 'Manufacture Cluizel', null, '603650094', 'FR', 'food'),
  ('chocolat-weiss', 'CHOCOLAT WEISS', 'Chocolat Weiss', null, '353395346', 'FR', 'food'),
  ('monbana', 'MONBANA', 'Monbana', null, '562100032', 'FR', 'food'),
  ('pastacorp', 'PASTACORP', 'Pastacorp', null, '423068303', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;

update entities
   set parent_id = (select id from entities where slug = 'labeyrie'), updated_at = now()
 where slug = 'labeyrie-fine-foods-france' and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = 'labeyrie-fine-foods-france'), (select id from entities where slug = 'labeyrie'),
       'https://api.gleif.org/api/v1/lei-records/96950063PTGNALD6GE17/direct-parent-relationship',
       'Registre GLEIF, relation de consolidation de Labeyrie Fine Foods France (LEI 96950063PTGNALD6GE17) : « IS_DIRECTLY_CONSOLIDATED_BY » Labeyrie Fine Foods (LEI 9695006DAQ2QM2EZ8H43), statut « ACTIVE ».',
       '2026-10-14', 'delegue-editeur:verifie-mot-pour-mot'
on conflict (entity_id, owner_id, source_url) do nothing;
