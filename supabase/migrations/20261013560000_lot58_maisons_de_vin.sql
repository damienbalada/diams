-- Maisons de vin dont les marques sont vendues en hypermarché, identifiées par les
-- mentions légales de leurs sites ; SIREN vérifiés dans l'annuaire officiel des
-- entreprises et LEI dans le registre GLEIF le 13/10/2026. Perrin et Fils déclare
-- « La Vieille Ferme » parmi ses noms commerciaux dans l'annuaire officiel.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('grands-vins-jean-claude-boisset', 'Grands Vins Jean-Claude Boisset', 'Boisset (Grands Vins Jean-Claude Boisset)', '969500OK9ZDCGW897439', '300221017', 'FR', 'wines_spirits'),
  ('perrin-et-fils', 'Perrin et Fils', 'Famille Perrin (Perrin et Fils)', '969500W93EL6KGVSQA24', '705620417', 'FR', 'wines_spirits')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
