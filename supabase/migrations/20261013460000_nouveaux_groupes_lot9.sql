-- Propriétaires de marques de vins, champagnes, glaces et hygiène vendues en
-- hypermarché, identifiés par les mentions légales des sites officiels des marques
-- (société éditrice et numéro RCS) ou par le rapport annuel du groupe (format ESEF).
-- Liens de groupe vérifiés dans le registre GLEIF le 13/10/2026 : la société L.I.D.,
-- éditrice du site de Lanson, a pour société mère ultime LANSON-BCC ; SIREN vérifiés
-- dans l'annuaire officiel des entreprises (entreprise active).
-- Maison Pommery & Associés est l'ancienne Vranken-Pommery Monopole (même SIREN et
-- même LEI ; rapport annuel 2025 « vrankenpommery » au format ESEF).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('lanson-bcc', 'Lanson-BCC', 'Lanson-BCC', '9695002M26EY0PEN7S80', '389391434', 'FR', 'wines_spirits'),
  ('maison-pommery', 'Maison Pommery & Associés', 'Maison Pommery & Associés (ex-Vranken-Pommery)', '969500M5EQJVDASURW53', '348494915', 'FR', 'wines_spirits'),
  ('glaces-thiriet', 'Glaces Thiriet', 'Thiriet (société)', null, '343838306', 'FR', 'food'),
  ('baron-philippe-de-rothschild', 'Baron Philippe de Rothschild SA', 'Baron Philippe de Rothschild', '9695003U51B78VT0C204', '459202644', 'FR', 'wines_spirits'),
  ('terroirs-et-vignerons-de-champagne', 'Terroirs et Vignerons de Champagne', 'Terroirs et Vignerons de Champagne (Nicolas Feuillatte)', '969500VQT0M6HPW6B710', '775611924', 'FR', 'wines_spirits'),
  ('champagne-canard-duchene', 'Champagne Canard-Duchêne', 'Champagne Canard-Duchêne (société)', '969500DWG8SE6IDVIC48', '335680245', 'FR', 'wines_spirits'),
  ('fromagerie-milleret', 'Fromagerie Milleret', 'Fromagerie Milleret', null, '426250023', 'FR', 'food'),
  ('health-and-happiness-france', 'Health & Happiness France', 'Health & Happiness France (Good Goût, Biostime)', null, '612030767', 'FR', 'food'),
  ('natur-vita', 'Natur''Vita', 'Natur''Vita (Pétrole Hahn)', null, '982479131', 'FR', 'personal_care')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
