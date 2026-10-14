-- Lot 92 : déclarants de la liste Nutri-Score (Santé publique France, janvier 2026) retrouvés
-- par recherche approchée dans l'annuaire officiel des entreprises (nom du déclarant sans la
-- forme juridique, activité alimentaire, candidat unique, forme juridique concordante), relus à
-- la main le 14/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('a-tex', 'A TEX', 'A-Tex', null, '682020672', 'FR', 'food'),
  ('banette', 'BANETTE', 'Banette (société)', null, '315736694', 'FR', 'food'),
  ('biodune-riviera', 'BIODUNE RIVIERA', 'Biodune Riviera', null, '852960558', 'FR', 'food'),
  ('charcuterie-pierre-geronimi-et-fils', 'CHARCUTERIE PIERRE GERONIMI ET FILS', 'Charcuterie Pierre Geronimi et Fils', null, '891746042', 'FR', 'food'),
  ('clarelia', 'CLARELIA', 'Clarelia', null, '878868439', 'FR', 'food'),
  ('covi', 'COVI', 'Covi (traiteur)', null, '391892171', 'FR', 'food'),
  ('delices-comtadins', 'DELICES COMTADINS', 'Délices Comtadins', null, '902842640', 'FR', 'food'),
  ('eivie-nature', 'EIVIE NATURE', 'Eivie Nature (société)', null, '920428802', 'FR', 'food'),
  ('foodyssey', 'FOODYSSEY', 'Foodyssey', null, '881598940', 'FR', 'food'),
  ('journey', 'JOURNEY', 'Journey (Aussitôt Bon)', null, '893577577', 'FR', 'food'),
  ('la-consigne', 'LA CONSIGNE', 'La Consigne (société)', null, '812649184', 'FR', 'food'),
  ('les-jardins-de-l-ocean', 'LES JARDINS DE L''OCEAN', 'Les Jardins de l''Océan (société)', null, '838937126', 'FR', 'food'),
  ('marcel-et-fils', 'MARCEL & FILS', 'Marcel & Fils', null, '508801305', 'FR', 'food'),
  ('mc-and-co', 'MC AND CO', 'MC and Co', null, '523449809', 'FR', 'food'),
  ('oriental-viandes', 'ORIENTAL VIANDES', 'Oriental Viandes (société)', null, '343454666', 'FR', 'food'),
  ('perenn', 'PERENN', 'Perenn (société)', null, '882215163', 'FR', 'food'),
  ('procom-international', 'PROCOM INTERNATIONAL', 'Procom International', null, '384942058', 'FR', 'food'),
  ('qualibio', 'QUALIBIO', 'Qualibio', null, '891921801', 'FR', 'food'),
  ('sagame', 'SAGAME', 'Sagame (société)', null, '812267912', 'FR', 'food'),
  ('besson-et-associes', 'BESSON ET ASSOCIES', 'Besson et Associés', null, '805173200', 'FR', 'food'),
  ('fraich-melba', 'FRAICH''MELBA', 'Fraich''Melba', null, '814873683', 'FR', 'food'),
  ('galzin', 'GALZIN', 'Galzin (société)', null, '799431408', 'FR', 'food'),
  ('holibelly', 'HOLIBELLY', 'Holibelly (société)', null, '929937886', 'FR', 'food'),
  ('kerdeo', 'KERDEO', 'Kerdeo (société)', null, '847873379', 'FR', 'food'),
  ('la-vie-saine', 'LA VIE SAINE', 'La Vie Saine (société)', null, '339277030', 'FR', 'food'),
  ('thaas-chips', 'THAAS CHIPS', 'Thaas Chips (société)', null, '832866966', 'FR', 'food'),
  ('agrodoubs', 'AGRODOUBS', 'Agrodoubs', null, '347826570', 'FR', 'food'),
  ('sarl-angsthelm-et-fils', 'SARL ANGSTHELM ET FILS', 'Angsthelm et Fils', null, '677080244', 'FR', 'food'),
  ('la-chips-du-perche', 'LA CHIPS DU PERCHE', 'La Chips du Perche (société)', null, '897975827', 'FR', 'food'),
  ('landreau', 'LANDREAU', 'Landreau (société)', null, '482053824', 'FR', 'food'),
  ('les-freres-popote', 'LES FRERES POPOTE', 'Les Frères Popote (société)', null, '884680935', 'FR', 'food'),
  ('l-oeuf-gascon', 'L''OEUF GASCON', 'L''Œuf Gascon (société)', null, '394031256', 'FR', 'food'),
  ('p3a', 'P3A', 'P3A', null, '900524224', 'FR', 'food'),
  ('plithos', 'PLITHOS', 'Plithos', null, '918018094', 'FR', 'food'),
  ('sofal', 'SOFAL', 'Sofal', null, '348324351', 'FR', 'food'),
  ('sustn-food', 'SUSTN FOOD', 'Sustn Food', null, '839194438', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
