-- Propriétaires de marques vendues en hypermarché, identifiés par la mention de marque
-- déposée ou de droits d'auteur du site officiel de chaque marque (« Ebly est une marque
-- déposée de Mars », « © Groupe Melitta », « trademarks of Bacardi & Company Limited »),
-- par les mentions légales (société éditrice et numéro RCS), ou par le rapport annuel
-- du groupe. SIREN vérifiés dans l'annuaire officiel des entreprises
-- (recherche-entreprises.api.gouv.fr, entreprise active) et LEI dans le registre GLEIF,
-- le 13/10/2026. Ces sociétés, souvent non cotées, publient peu : leur note restera
-- souvent « en attente ».
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('essential-home', 'Essential Home', 'Essential Home (Advent International, ex-Reckitt)', null, null, null, 'home_care'),
  ('melitta', 'Melitta Group Management GmbH & Co. KG', 'Groupe Melitta', '5299006ELY38N3VPXQ92', null, 'DE', 'home_care'),
  ('brita-se', 'BRITA SE', 'BRITA SE', '529900371VDJJIG22X52', null, 'DE', 'household_durables'),
  ('hipp-vertrieb', 'HiPP GmbH & Co. Vertrieb KG', 'HiPP (groupe)', '529900ZF7H3V56V8IM45', null, 'DE', 'food'),
  ('werner-mertz', 'Werner & Mertz GmbH', 'Werner & Mertz', '529900PHKIKL9OSBCG77', null, 'DE', 'home_care'),
  ('scholls-wellness-company', 'Scholl''s Wellness Company', 'Scholl''s Wellness Company', null, '902497353', 'FR', 'personal_care'),
  ('expanscience', 'Laboratoires Expanscience', 'Laboratoires Expanscience', '969500MK7EJJJMOZIS88', '331930081', 'FR', 'personal_care'),
  ('pastificio-rana', 'Pastificio Rana S.p.A.', 'Pastificio Rana', '815600530D7A6B12BC38', null, 'IT', 'food'),
  ('capri-sun-group', 'Capri Sun Group Holding AG', 'Capri Sun Group', '254900UBDGLNV2VBR454', null, 'CH', 'beverages'),
  ('weleda', 'Weleda', 'Weleda (société)', '96950055G2C90P7QL965', '945850246', 'FR', 'personal_care'),
  ('babyliss', 'BaByliss SARL', 'BaByliss (société)', null, '612021923', 'FR', 'household_durables'),
  ('cafes-meo', 'Cafés Méo', 'Cafés Méo', '969500GMR9XYH09HIQ20', '459501219', 'FR', 'beverages'),
  ('cite-marine', 'Cité Marine', 'Cité Marine (société)', '969500LISG99J9U5G532', '353786841', 'FR', 'food'),
  ('michel-et-augustin', 'Michel et Augustin', 'Michel et Augustin (société)', null, '479205460', 'FR', 'food'),
  ('lucien-georgelin', 'Lucien Georgelin', 'Lucien Georgelin (société)', '969500CELM5WWIPHGM35', '382510816', 'FR', 'food'),
  ('eaux-de-quezac', 'Eaux Minérales Naturelles de Quézac', 'Eaux Minérales Naturelles de Quézac', null, '479463481', 'FR', 'beverages'),
  ('fromagerie-guilloteau', 'Fromagerie Guilloteau', 'Fromagerie Guilloteau', '9695005GADXJCBKZWU96', '322927146', 'FR', 'food'),
  ('juva-sante', 'Laboratoires Juva Santé', 'Laboratoires Juva Santé', null, '618500193', 'FR', 'personal_care'),
  ('sodalis-france', 'Sodalis France', 'Sodalis France', '894500343FEOP6P0UI88', '337796064', 'FR', 'home_care'),
  ('mousline', 'Mousline', 'Mousline (société)', '8945000RJSFNHA1G1G76', '572049500', 'FR', 'food'),
  ('lipton-teas-and-infusions', 'Lipton Teas and Infusions France', 'LIPTON Teas and Infusions', null, '898477096', 'FR', 'beverages'),
  ('bacardi', 'Bacardi Limited', 'Bacardi', '549300R32WTQNHNN5055', null, 'BM', 'wines_spirits'),
  ('bolton', 'Bolton Group S.r.l.', 'Bolton', '5493007FML7DO1CCDU16', null, 'IT', 'fmcg_group')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;

-- Air Wick ne relève plus de Reckitt. Le rapport annuel 2025 de Reckitt (format ESEF)
-- l'indique : « Essential Home brings together long-established brands including Air
-- Wick, Calgon, Cillit Bang, Mortein, Easy-Off and Woolite », la cession à Advent
-- International « completed on 31 December 2025 », et Reckitt ne garde qu'une
-- participation de 30 % (« Reckitt's retained 30% equity stake in Advent's acquisition
-- vehicle »). Règle de propriété : une opération achevée change le groupe.
-- La preuve d'appartenance à Reckitt écrite le 13/10/2026 citait justement la section
-- « Essential Home » de ce rapport : c'était une erreur de lecture, on la retire. La
-- nouvelle preuve (même rapport) est importée par le lot de marques 33.
update entities
   set parent_id = (select id from entities where slug = 'essential-home'),
       ownership_pct = 100,
       updated_at = now()
 where slug = 'air-wick'
   and parent_id = (select id from entities where slug = 'reckitt');

delete from entity_ownership_sources
 where entity_id = (select id from entities where slug = 'air-wick')
   and owner_id = (select id from entities where slug = 'reckitt');
