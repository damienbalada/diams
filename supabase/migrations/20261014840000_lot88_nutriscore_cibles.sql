-- Sociétés déclarant des marques dans la liste officielle de Santé publique France
-- « Entreprises et marques utilisant le Nutri-Score en France » (janvier 2026), retrouvées
-- une à une dans l'annuaire officiel des entreprises le 14/10/2026 (nom et activité
-- alimentaire concordants) : Heimburger (pâtes Grand'Mère, Marlenheim), Huilerie Cauvin,
-- J.P.S. Lait (Les Prés d'Ariège), Katell (pommes de terre, groupe coopératif Le Gouessant).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('heimburger', 'HEIMBURGER SA', 'Heimburger', null, '410472021', 'FR', 'food'),
  ('huilerie-cauvin', 'HUILERIE CAUVIN', 'Huilerie Cauvin', null, '332587492', 'FR', 'food'),
  ('jps-lait', 'J.P.S. LAIT', 'J.P.S. Lait (Biochamps)', null, '352303457', 'FR', 'food'),
  ('katell', 'KATELL', 'Katell', null, '893552695', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
