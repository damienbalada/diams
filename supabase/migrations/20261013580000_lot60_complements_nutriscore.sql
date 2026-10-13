-- Compléments manuels tirés de la liste officielle du Nutri-Score (Santé publique France,
-- janvier 2026) : sociétés que la sélection en série avait écartées (homonymes dans
-- l'annuaire, effectif non déclaré, société étrangère) et dont l'identité a été vérifiée
-- une à une le 13/10/2026 (annuaire officiel des entreprises, registre GLEIF).
-- Concept' Fruits porte le nom commercial « Roger Descours » dans l'annuaire officiel.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('cocorette-distribution', 'Cocorette Distribution', 'Cocorette Distribution', null, '500384953', 'FR', 'food'),
  ('concept-fruits', 'Concept'' Fruits', 'Concept'' Fruits (Roger Descours)', '969500IEIURSC9ZOZM46', '404055725', 'FR', 'food'),
  ('croc-frais', 'Croc Frais', 'Croc''Frais (société)', null, '419544853', 'FR', 'food'),
  ('alsace-lait', 'Laiterie Coopérative Alsacienne Alsace Lait', 'Alsace Lait (coopérative)', null, '778731174', 'FR', 'food'),
  ('esteban-espuna', 'Esteban Espuña, S.A.', 'Espuña (Esteban Espuña)', '95980020140005953552', null, 'ES', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
