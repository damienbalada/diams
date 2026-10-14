-- Sociétés éditrices des sites officiels de marques alimentaires et de boissons (mentions
-- légales), SIREN vérifiés dans l'annuaire officiel des entreprises le 14/10/2026 (toutes
-- actives) ; LEI et liens de consolidation lus dans le registre GLEIF le même jour.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('jean-larnaudie', 'JEAN LARNAUDIE', 'Jean Larnaudie (société)', null, '410252589', 'FR', 'food'),
  ('ets-hilliet', 'ETS GEORGES ET BERNARD HILLIET', 'Conserverie la belle-iloise', '969500DYZ7YXVR4XL548', '873500086', 'FR', 'food'),
  ('kaviari', 'KAVIARI', 'Kaviari (société)', '96950071TEHUIHNWO216', '315734194', 'FR', 'food'),
  ('salines-de-guerande', 'SCA SALINES DE GUERANDE LE GUERANDAIS', 'Les Salines de Guérande – Le Guérandais', '969500A0GSP0G0X80Q69', '349241315', 'FR', 'food'),
  ('huilerie-emile-noel', 'HUILERIE EMILE NOEL SAS', 'Huilerie Émile Noël', '969500DXKDK8CZTOB031', '660201138', 'FR', 'food'),
  ('celnat', 'CELNAT', 'Celnat (société)', '969500IKN9IPQWCGVG21', '585650096', 'FR', 'food'),
  ('markal', 'MARKAL', 'Markal (société)', '969500HXY9M85AU9LE21', '436180582', 'FR', 'food'),
  ('kaoka', 'KAOKA', 'Kaoka (société)', '969500PRVDLM60XOVK23', '392925434', 'FR', 'food'),
  ('tossolia', 'TOSSOLIA', 'Tossolia (société coopérative)', null, '379512163', 'FR', 'food'),
  ('bonnat-chocolatier', 'BONNAT CHOCOLATIER', 'Bonnat Chocolatier', null, '482535416', 'FR', 'food'),
  ('abtey-chocolaterie', 'ABTEY CHOCOLATERIE', 'Abtey Chocolaterie', '969500OEFZ3PBQHMGM55', '946351376', 'FR', 'food'),
  ('chocmod', 'CHOCMOD', 'Chocmod (société)', '969500U865BKPN56I528', '443274477', 'FR', 'food'),
  ('chocolat-mathez', 'CHOCOLAT MATHEZ', 'Chocolat Mathez', '96950030LRDKR1NUDN14', '392886982', 'FR', 'food'),
  ('pages-sas', 'PAGES', 'Pagès (société)', null, '341594034', 'FR', 'food'),
  ('maka', 'MAKA', 'Maka (Les Jardins de Gaïa)', '894500SNRY7CP0O03Y28', '398560375', 'FR', 'food'),
  ('dammann-freres', 'DAMMANN FRERES', 'Dammann Frères (société)', '9695003YQNJ167E4N842', '451570519', 'FR', 'food'),
  ('feerie-gourmande', 'FEERIE GOURMANDE', 'Féerie Gourmande (Maison Francis Miot)', null, '432760197', 'FR', 'food'),
  ('heritiers-h-clement', 'LES HERITIERS H.CLEMENT', 'Les Héritiers H. Clément', null, '303164628', 'FR', 'wines_spirits'),
  ('distillerie-dillon', 'DISTILLERIE DILLON', 'Distillerie Dillon', null, '466203338', 'FR', 'wines_spirits'),
  ('camus-la-grande-marque', 'CAMUS LA GRANDE MARQUE', 'Camus La Grande Marque', '969500T3TBQVYXCEMZ74', '905420014', 'FR', 'wines_spirits'),
  ('alliance-champagne', 'ALLIANCE CHAMPAGNE', 'Alliance Champagne', '969500Y7P0YPKF5GYM19', '419212022', 'FR', 'wines_spirits'),
  ('jacquart-et-associes-distribution', 'JACQUART ET ASSOCIES DISTRIBUTION', 'Jacquart & Associés Distribution', '969500OTNENW56KHRV29', '440233278', 'FR', 'wines_spirits'),
  ('societe-des-caves', 'SOCIETE DES CAVES ET DES PRODUCTEURS REUNIS DE ROQUEFORT', 'Société des Caves (Roquefort)', '969500QESK9FK1LAQB77', '925480030', 'FR', 'food'),
  ('loeuf', 'LOEUF', 'Loeuf (œufs)', '9695003O2677DGTRMJ76', '344652565', 'FR', 'food'),
  ('arcadie', 'ARCADIE', 'Arcadie (société)', null, '393025697', 'FR', 'food'),
  ('les-2-marmottes-sas', 'LES 2 MARMOTTES', 'Les 2 Marmottes (société)', null, '899938161', 'FR', 'food'),
  ('valette-foie-gras', 'VALETTE FOIE GRAS', 'Valette Foie Gras', null, '327843603', 'FR', 'food'),
  ('biobleud', 'BIOBLEUD', 'Biobleud (société)', null, '450266986', 'FR', 'food'),
  ('feyel-et-artzner', 'FEYEL & ARTZNER', 'Feyel & Artzner', '969500IZH9Q24QXYHA04', '830833489', 'FR', 'food'),
  ('conserves-gonidec', 'CONSERVES GONIDEC', 'Conserves Gonidec', null, '375980075', 'FR', 'food'),
  ('uvcdr', 'UNION DES VIGNERONS DES COTES DU RHONE', 'Union des Vignerons des Côtes du Rhône (Cellier des Dauphins)', null, '302558622', 'FR', 'wines_spirits')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;

-- Liens de groupe lus dans le registre GLEIF (relations de consolidation au statut « ACTIVE »).
update entities set parent_id = (select id from entities where slug = 'alliance-champagne'), updated_at = now()
 where slug = 'jacquart-et-associes-distribution' and parent_id is null;
update entities set parent_id = (select id from entities where slug = 'lactalis'), updated_at = now()
 where slug = 'societe-des-caves' and parent_id is null;
update entities set parent_id = (select id from entities where slug = 'ldc'), updated_at = now()
 where slug = 'loeuf' and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = v.child), (select id from entities where slug = v.owner), v.url, v.excerpt,
       '2026-10-14', 'delegue-editeur:verifie-mot-pour-mot'
from (values
  ('jacquart-et-associes-distribution', 'alliance-champagne',
   'https://api.gleif.org/api/v1/lei-records/969500OTNENW56KHRV29/direct-parent-relationship',
   'Registre GLEIF, relation de consolidation de Jacquart et Associés Distribution (LEI 969500OTNENW56KHRV29) : « IS_DIRECTLY_CONSOLIDATED_BY » Alliance Champagne (LEI 969500Y7P0YPKF5GYM19), statut « ACTIVE ».'),
  ('societe-des-caves', 'lactalis',
   'https://api.gleif.org/api/v1/lei-records/969500QESK9FK1LAQB77/direct-parent-relationship',
   'Registre GLEIF, relation de consolidation de la Société des Caves et des Producteurs Réunis de Roquefort (LEI 969500QESK9FK1LAQB77) : « IS_DIRECTLY_CONSOLIDATED_BY » Groupe Lactalis (LEI 9695001K2B8Q8CDK6H67), statut « ACTIVE », niveau « FULLY_CORROBORATED » ; exercice déclaré 2016, fiche LEI non renouvelée depuis décembre 2020.'),
  ('loeuf', 'ldc',
   'https://api.gleif.org/api/v1/lei-records/9695003O2677DGTRMJ76/ultimate-parent-relationship',
   'Registre GLEIF, relation de consolidation de Loeuf (LEI 9695003O2677DGTRMJ76) : « IS_ULTIMATELY_CONSOLIDATED_BY » Société L.D.C. (LEI 969500W6740M4US9ES57), statut « ACTIVE » (mère directe déclarée : Amont LDC) ; exercice déclaré 2022, fiche LEI non renouvelée.')
) as v(child, owner, url, excerpt)
on conflict (entity_id, owner_id, source_url) do nothing;
