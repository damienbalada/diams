-- Compléments manuels tirés de la liste officielle du Nutri-Score (Santé publique France,
-- janvier 2026) : sociétés vérifiées une à une le 13/10/2026 dans l'annuaire officiel des
-- entreprises (et le registre GLEIF pour Maître Prunille).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('elivia', 'Elivia', 'Elivia (viandes)', null, '344477468', 'FR', 'food'),
  ('odnv', 'O.D.N.V', 'ODNV (L''Œuf de nos Villages)', null, '798902730', 'FR', 'food'),
  ('fleuron-d-anjou', 'Fleuron d''Anjou', 'Fleuron d''Anjou (coopérative)', null, '786187898', 'FR', 'food'),
  ('val-d-eurre', 'Société Val d''Eurre', 'Val d''Eurre', null, '339390734', 'FR', 'food'),
  ('maitre-prunille', 'Maître Prunille', 'Maître Prunille (société)', '9695008IEMEGP7942V36', '380678250', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
