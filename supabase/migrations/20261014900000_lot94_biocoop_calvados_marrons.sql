-- Lot 94 : Biocoop (déclarant de la liste Nutri-Score, LEI lu dans GLEIF), Calvados Christian
-- Drouin et Établissements Clément Faugier (éditeurs de leur site officiel) ; SIREN vérifiés dans
-- l'annuaire officiel des entreprises le 14/10/2026 (tous actifs).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('biocoop', 'BIOCOOP', 'Biocoop (coopérative)', '969500HVYHIQG8E3WF46', '382891752', 'FR', 'retail_distribution'),
  ('calvados-christian-drouin', 'CALVADOS CHRISTIAN DROUIN SAS', 'Calvados Christian Drouin (société)', null, '476950027', 'FR', 'wines_spirits'),
  ('etablissements-clement-faugier', 'ETABLISSEMENTS CLEMENT FAUGIER', 'Établissements Clément Faugier', null, '786511576', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
