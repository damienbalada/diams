-- Suchard en France relève de Carambar & Co, pas de Mondelez. Le lot 33 l'avait
-- rattachée à Mondelez d'après son rapport « Snacking Made Right » 2025 (« Our global
-- and local brands include … Suchard »), qui vaut pour la marque hors de France. Or le
-- site officiel de Carambar & Co présente Suchard parmi « Nos marques »
-- (https://carambarco.com/marques/suchard/) et précise, page « Nous », que son usine de
-- Strasbourg produit « pour les marques Suchard, dont le fameux Rocher ». Pour un
-- consommateur en France, le propriétaire est celui qui exploite la marque en France.
-- La preuve Mondelez est retirée ; la preuve Carambar & Co est importée par le lot 34.
update entities
   set parent_id = (select id from entities where slug = 'carambar-co'),
       ownership_pct = 100,
       updated_at = now()
 where slug = 'suchard'
   and parent_id = (select id from entities where slug = 'mondelez');

delete from entity_ownership_sources
 where entity_id = (select id from entities where slug = 'suchard')
   and owner_id = (select id from entities where slug = 'mondelez');
