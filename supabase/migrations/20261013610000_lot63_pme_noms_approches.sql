-- Sociétés françaises qui déclarent des marques dans la liste officielle de Santé publique
-- France « Entreprises et marques utilisant le Nutri-Score en France » (janvier 2026).
-- Sélection en série : nom identique à une seule société active de l'annuaire officiel des
-- entreprises (recherche-entreprises, 13/10/2026), au moins 10 salariés, ni entrepreneur
-- individuel, ni organisme public ou associatif, ni importateur, ni restauration ; relue.
-- Lot 63 : noms proches de l'annuaire (mots inclus), retenus seulement si une seule société
-- active d'activité agroalimentaire et d'au moins 10 salariés correspond ; relus un à un.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('boulangerie-le-roux-concarneau', 'BOULANGERIE LE ROUX CONCARNEAU', 'Boulangerie le Roux Concarneau', null, '492130299', 'FR', 'food'),
  ('brand-masters-france', 'BRAND MASTERS FRANCE SARL', 'Brand Masters France', null, '814090247', 'FR', 'food'),
  ('fromagerie-jacques-delin', 'FROMAGERIE JACQUES DELIN', 'Fromagerie Jacques Delin', null, '379848005', 'FR', 'food'),
  ('laiterie-de-pamplie', 'SOCIETE COOPERATIVE AGRICOLE LAITERIE DE PAMPLIE', 'Laiterie de Pamplie (coopérative)', null, '781462098', 'FR', 'food'),
  ('l-angelys', 'L''ANGELYS', 'L''Angelys', null, '404701989', 'FR', 'food'),
  ('comptoir-des-salaisons', 'COMPTOIR DES SALAISONS', 'Comptoir des Salaisons', null, '488603309', 'FR', 'food'),
  ('la-minoterie-de-colagne', 'LA MINOTERIE DE COLAGNE', 'La Minoterie de Colagne', null, '353523418', 'FR', 'food'),
  ('lescieux-et-cie', 'SARL LESCIEUX ET CIE', 'Lescieux et Cie', null, '332975523', 'FR', 'food'),
  ('les-canards-du-val-de-luce', 'LES CANARDS DU VAL DE LUCE', 'Les Canards du Val de Luce', null, '378320964', 'FR', 'food'),
  ('valfleuri-pates-alimentaires', 'VALFLEURI SA PATES ALIMENTAIRES', 'Valfleuri Pates Alimentaires', null, '915520621', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
