-- Sociétés françaises éditrices de marques vendues en hypermarché, identifiées par
-- les mentions légales des sites officiels de leurs marques (l'éditeur ou le
-- propriétaire y est nommé, avec son numéro RCS). SIREN vérifiés dans l'annuaire
-- officiel des entreprises (recherche-entreprises.api.gouv.fr, entreprise active)
-- et LEI dans le registre GLEIF (recherche par SIREN) quand il existe, le 13/10/2026.
-- Ces sociétés non cotées publient peu : leur note restera souvent « en attente ».
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('vitagermine', 'Vitagermine', 'Vitagermine', null, '775586811', 'FR', 'food'),
  ('nutrimaine', 'Nutrimaine', 'Nutrimaine', null, '445327083', 'FR', 'food'),
  ('jacquet-brossard', 'Jacquet Brossard Distribution', 'Jacquet Brossard', '969500V17AOISJHSBK79', '318947132', 'FR', 'food'),
  ('grands-chais-de-france', 'Les Grands Chais de France', 'Les Grands Chais de France', '969500165ISQ605GDJ18', '315999201', 'FR', 'wines_spirits'),
  ('merisant', 'Merisant France SAS', 'Merisant', null, '429875149', 'FR', 'food'),
  ('piper-heidsieck', 'Compagnie Champenoise PH-CH Piper-Heidsieck', 'Compagnie Champenoise PH-CH (Piper-Heidsieck, Charles Heidsieck)', '969500LTAAZMU95KMP46', '879810695', 'FR', 'wines_spirits'),
  ('charles-et-alice', 'Charles & Alice', 'Charles & Alice', null, '347681074', 'FR', 'food'),
  ('hra-pharma', 'Laboratoire HRA Pharma', 'HRA Pharma', '969500WQKH7NJ3JG3E77', '420792582', 'FR', 'personal_care'),
  ('comtesse-du-barry', 'Comtesse du Barry', 'Comtesse du Barry (société)', null, '396720310', 'FR', 'food'),
  ('sarbec', 'Laboratoires Sarbec', 'Laboratoires Sarbec', null, '342324761', 'FR', 'personal_care'),
  ('cerelia', 'Cérélia', 'Cérélia', '969500PLB4GTHJTB1333', '419397104', 'FR', 'food'),
  ('cemoi', 'Cémoi Chocolatier', 'Cémoi Chocolatier', '969500VE80HQVNGV8X92', '564202166', 'FR', 'food'),
  ('snacking-services', 'Snacking Services', 'Snacking Services (Daunat)', null, '429449457', 'FR', 'food'),
  ('freixenet-gratien', 'Freixenet Gratien', 'Freixenet Gratien', null, '410381206', 'FR', 'wines_spirits'),
  ('paul-hartmann', 'Paul Hartmann SAS', 'Paul Hartmann', null, '778740001', 'FR', 'personal_care'),
  ('boiron', 'Boiron', 'Boiron', '9695000UMPNY21KKDO98', '967504697', 'FR', 'personal_care'),
  ('amalric', 'Amalric', 'Amalric (Isla Délice)', null, '538449489', 'FR', 'food'),
  ('noo-corp', 'SAS Noo Corp', 'Noo Corp (Joone)', null, '824500797', 'FR', 'personal_care'),
  ('orientis-gourmet', 'Orientis Gourmet', 'Orientis Gourmet (Kusmi Tea)', '969500YNJN6FGX60P864', '350283057', 'FR', 'beverages'),
  ('cofepp', 'Compagnie Financière Européenne de Prises de Participation', 'La Martiniquaise (COFEPP)', '969500Z6VMNEEYTDTS57', '572056331', 'FR', 'wines_spirits'),
  ('geyer-freres', 'Établissements Geyer Frères', 'Geyer Frères (Lorina)', '9695002FE4JLNZ2NSP48', '360800742', 'FR', 'beverages'),
  ('pastacorp', 'Pastacorp', 'Pastacorp', '969500DPZP8R3X8FBZ17', '423068303', 'FR', 'food'),
  ('sill-entreprises', 'SILL Entreprises', 'SILL Entreprises', '969500CXV83ZZR34RC77', '636220220', 'FR', 'food'),
  ('mix-buffet', 'Mix Buffet', 'Mix Buffet (société)', null, '415183896', 'FR', 'food'),
  ('laboratoire-nuxe', 'Laboratoire Nuxe', 'Laboratoire Nuxe', '969500DA9ENESR18X363', '642060123', 'FR', 'personal_care'),
  ('olga', 'Olga', 'Olga (ex-Triballat Noyal)', '969500HWI3EG72HC3407', '709200307', 'FR', 'food'),
  ('biocodex', 'Biocodex', 'Biocodex', '969500JRK0RE7CYZSO20', '562064600', 'FR', 'personal_care'),
  ('segafredo-zanetti', 'Segafredo Zanetti France', 'Segafredo Zanetti France', '969500B1CZ3O8GVRE270', '650501208', 'FR', 'beverages'),
  ('sodebo', 'Société des Établissements Bougro Sodebo', 'Sodebo (société)', '969500FPS98HMOOEIP45', '547350249', 'FR', 'food'),
  ('neptune-distribution', 'SNC Neptune Distribution', 'Neptune Distribution (St-Yorre, Vichy Célestins)', null, '391751351', 'FR', 'beverages'),
  ('urgo', 'Laboratoires Urgo Healthcare', 'Laboratoires Urgo', null, '798251559', 'FR', 'personal_care'),
  ('kbb', 'Kriter Brut de Brut (KBB)', 'KBB (Patriarche)', '98450093D6073F5D4308', '343484879', 'FR', 'wines_spirits'),
  ('pasquier', 'Pasquier', 'Groupe Pasquier', '9695005W53YEH3IM4X54', '329263933', 'FR', 'food'),
  ('cooperl', 'Cooperl Arc Atlantique', 'Cooperl', '9695009LRA45ZLLEWS85', '383986874', 'FR', 'food'),
  ('bigard', 'Groupe Bigard', 'Groupe Bigard', '969500KD789VR9495B53', '776221467', 'FR', 'food'),
  ('lea-nature', 'Léa Nature Services', 'Groupe Léa Nature', null, '409957529', 'FR', 'personal_care')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
