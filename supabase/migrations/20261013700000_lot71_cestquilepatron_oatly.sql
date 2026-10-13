-- La Société des Consommateurs (SCIC, SIREN 828 852 871), éditrice du site de la marque
-- « C'est qui le Patron ?! » ; Oatly Group AB (marque au nom du groupe). SIREN vérifié dans
-- l'annuaire officiel des entreprises et LEI dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('societe-des-consommateurs', 'La Société des Consommateurs', 'La Société des Consommateurs (coopérative)', null, '828852871', 'FR', 'food'),
  ('oatly', 'Oatly Group AB', 'Oatly', '894500CEIOQNBAH10Z10', null, 'SE', 'beverages')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
