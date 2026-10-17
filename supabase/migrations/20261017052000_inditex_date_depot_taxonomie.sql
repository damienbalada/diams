-- Inditex, taxonomie (lot 191) : date d'observation alignée sur la date de dépôt ESEF utilisée pour ses autres preuves.
update evidence set observed_on = '2025-05-08'
 where indicator_id = (select id from indicators where code = 'ENV_TAXONOMY_CAPEX')
   and entity_id = (select id from entities where slug = 'inditex')
   and observed_on = '2025-03-12';
