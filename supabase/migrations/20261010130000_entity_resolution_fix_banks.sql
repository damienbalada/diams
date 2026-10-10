-- =============================================================================
-- Résolution d'entités : correction des identifiants + verticale banque
-- -----------------------------------------------------------------------------
-- Audit du 10/10/2026 : chaque SIREN et LEI de la base a été confronté aux
-- registres officiels (API Recherche d'entreprises / INSEE, API GLEIF). Le
-- rapprochement par NOM de enrich_entities s'était trompé sur 19 SIREN et 12 LEI
-- (ex. Crédit Agricole S.A. → Crédit Agricole du Morbihan, L'Oréal → une PME
-- nantaise « OREAL », TotalEnergies → une association créée en 2024).
-- Règle retenue : identifiant confirmé par le registre, ou NULL. Jamais deviné.
-- Les LEI sont désormais obtenus par SIREN (GLEIF « registeredAs »), pas par nom.
--
-- Mises à jour conditionnelles (sur l'ancienne valeur) : rejouer est sans effet.
-- =============================================================================

-- --- SIREN corrigés (registre INSEE) ------------------------------------------
update entities set siren = '784608416', lei = '969500TJ5KRTCJQWXH05' where slug = 'credit-agricole' and siren = '777903816';
update entities set siren = '632012100', lei = '529900JI1GG6F7RKVI53' where slug = 'loreal'          and siren = '823771084';
update entities set siren = '582041943', lei = '52990097YFPX9J0H5D87' where slug = 'pernod-ricard'   and siren = '303656375';
update entities set siren = '441639465', lei = '969500F7JLTX36OUI695' where slug = 'renault'         and siren = '312212301';
update entities set siren = '542051180'                               where slug = 'totalenergies'   and siren = '934082975';
update entities set siren = '542088067', lei = '5493005GNGE7UFJCIL03' where slug = 'groupe-bel'      and siren = '534217195';
update entities set siren = '642050199', lei = '9695008DZ9VGHKZUYG11' where slug = 'citroen'         and siren = '038866927';
update entities set siren = '330160367', lei = '969500DBPH47NB8NMT87' where slug = 'boucheron'       and siren = '807872387';
update entities set siren = '797080850', lei = '213800WEP69ITQTIO365' where slug = 'evian'           and siren = '994187722';
update entities set siren = '395780059'                               where slug = 'volvic'          and siren = '491613212';
update entities set siren = '306688714'                               where slug = 'la-roche-posay'  and siren = '218602076';
update entities set siren = '700200983'                               where slug = 'royal-canin'     and siren = '380824888';

-- SIREN sans entité juridique identifiable (marque) ou homonyme sans lien : NULL.
update entities set siren = null where slug = 'moet-chandon'     and siren = '409760543'; -- personne physique homonyme
update entities set siren = null where slug = 'van-cleef-arpels' and siren = '433901485'; -- l'école de la maison
update entities set siren = null where slug = 'vache-qui-rit'    and siren = '443050752'; -- PME homonyme (marque de Bel)
update entities set siren = null where slug = 'alpine'           and siren = '931914568'; -- PME créée en 2024
update entities set siren = null where slug = 'activia'          and siren = '438284507'; -- PME homonyme (marque Danone)
update entities set siren = null where slug = 'garnier'          and siren = '402651319'; -- PME homonyme (marque L'Oréal)
update entities set siren = null where slug = 'harrys'           and siren = '351715040';
update entities set siren = null where slug = 'ricard'           and siren = '388852055'; -- PME homonyme (Castres)
update entities set siren = null where slug = 'ds-automobiles'   and siren = '788877611'; -- PME homonyme
update entities set siren = null where slug = 'perrier'          and siren = '778147801';

-- --- LEI corrigés ou ajoutés (GLEIF, par SIREN) -------------------------------
update entities set lei = 'R0MUWSFPU8MPRO8K5P83' where slug = 'bnp-paribas' and lei = '969500FZIK0SBNRSC223'; -- était BNP Paribas Public Sector
update entities set lei = 'LAXUQCHT4FH58LRZDY46' where slug = 'engie'            and lei is null;
update entities set lei = '969500KMUQ2B6CBAF162' where slug = 'danone'           and lei is null;
update entities set lei = '549300VGEJKB7SVUZR78' where slug = 'kering'           and lei is null;
update entities set lei = 'IOG4E947OATN0KJYSD45' where slug = 'lvmh'             and lei is null;
update entities set lei = 'O2RNE8IBXP4R0TD8PU41' where slug = 'societe-generale' and lei is null;

-- LEI d'une autre entité (homonyme, filiale, ou société dissoute) : NULL.
update entities set lei = null where slug = 'alfa-romeo'        and lei = '8156006C9A3CF76FDD05'; -- « Villaggio Alfa Romeo »
update entities set lei = null where slug = 'coca-cola-classic' and lei = '254900M1AMHU9C4SZE44'; -- Coca-Cola India Inc.
update entities set lei = null where slug = 'dove'              and lei = '2138004R77GGC1K2C631'; -- L.F. Dove Limited
update entities set lei = null where slug = 'garnier'           and lei = '969500F7WH4RHEWD5572'; -- homonyme
update entities set lei = null where slug = 'lidl'              and lei = '529900KYSC41JNW39541'; -- Lidl U.K. GmbH
update entities set lei = null where slug = 'moet-chandon'      and lei = '969500NROH0B5G0TKY04'; -- comité d'entreprise
update entities set lei = null where slug = 'peugeot'           and lei = '969500TZ5950IT5FPQ42'; -- Peugeot SA, dissoute (Stellantis)
update entities set lei = null where slug = 'president'         and lei = '969500K6CD32R56TJU44'; -- homonyme
update entities set lei = null where slug = 'ricard'            and lei = '969500EBPNF6DFLMJU84'; -- inactif, homonyme
update entities set lei = null where slug = 'fiat'              and lei = '5493004C1SL445NFDR90'; -- Fiat S.p.A., inactif
update entities set lei = null where slug = 'burger-king'       and lei = '54930058TQK6DLGVFI77'; -- inactif
update entities set lei = null where slug = 'twitch'            and lei = '549300NQ0W53YDWJ1G04'; -- inactif

-- --- Preuves rattachées à un mauvais SIREN : rejetées (tracé, pas supprimé) ---
update evidence ev set review_status = 'rejected', reviewer = 'rejet:siren-errone-2026-10-10'
from entities e, indicators i
where ev.entity_id = e.id and ev.indicator_id = i.id and i.code = 'LAB_EGAPRO_INDEX'
  and ev.review_status = 'approved'
  and (   (e.slug = 'credit-agricole' and ev.excerpt like '%CREDIT AGRICOLE DU MORBIHAN%')
       or (e.slug = 'pernod-ricard'   and ev.excerpt like '%PERNOD RICARD FRANCE%')
       or (e.slug = 'renault'         and ev.excerpt like '%RENAULT RETAIL GROUP%'));

-- --- Verticale banque (France) : établissements, identifiants vérifiés --------
-- Têtes de groupe : le bénéficiaire économique. Marques et filiales : notées sur
-- leurs propres preuves (Règle 8), rattachées à leur groupe pour l'affichage.
insert into entities (slug, legal_name, display_name, siren, lei, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.siren, v.lei, 'FR', s.id, v.is_brand
from (values
  ('bpce',                            'BPCE',                                  'Groupe BPCE',                     '493455042', '9695005MSX1OYEMGDF46', false),
  ('credit-mutuel-alliance-federale', 'Caisse Fédérale de Crédit Mutuel',      'Crédit Mutuel Alliance Fédérale', '588505354', '969500LFTDNMONT2EP08', false),
  ('credit-mutuel-arkea',             'Crédit Mutuel Arkéa',                   'Crédit Mutuel Arkéa',             '775577018', '96950041VJ1QP0B69503', false),
  ('la-banque-postale',               'La Banque Postale',                     'La Banque Postale',               '421100645', '96950066U5XAAIRCPA78', false),
  ('la-nef',                          'Société Financière de la Nef',          'La Nef',                          '339799116', '969500RL9JL5GKD1DY57', false),
  ('lcl',                             'Crédit Lyonnais',                       'LCL',                             '954509741', '9695009F5UPB9IITI298', true),
  ('cic',                             'Crédit Industriel et Commercial',       'CIC',                             '542016381', 'N4JDFKKH2FTD8RKFXO39', true),
  ('boursobank',                      'Boursorama',                            'BoursoBank',                      '351058151', '9695003SJ7Z9C9HIGV14', true),
  ('credit-cooperatif',               'Crédit Coopératif',                     'Crédit Coopératif',               '349974931', 'W2RVX391BFSQJQAGEM62', true),
  ('fortuneo',                        'Arkéa Direct Bank',                     'Fortuneo',                        '384288890', '969500EYUH381IUM2589', true),
  ('monabanq',                        'Monabanq',                              'Monabanq',                        '341792448', '969500CHDIA34DPV9611', true),
  ('nickel',                          'Financière des Paiements Électroniques','Nickel',                          '753886092', '969500PSOWV2US4S6V37', true),
  ('hello-bank',                      'BNP Paribas (Hello bank!)',             'Hello bank!',                     null,        null,                   true),
  ('caisse-epargne',                  'Réseau des Caisses d''Épargne',         'Caisse d''Épargne',               null,        null,                   true),
  ('banque-populaire',                'Réseau des Banques Populaires',         'Banque Populaire',                null,        null,                   true)
) as v(slug, legal_name, display_name, siren, lei, is_brand)
join sectors s on s.code = 'banking_finance'
on conflict (slug) do nothing;

update entities e set parent_id = p.id
from (values
  ('lcl', 'credit-agricole'), ('cic', 'credit-mutuel-alliance-federale'), ('boursobank', 'societe-generale'),
  ('credit-cooperatif', 'bpce'), ('fortuneo', 'credit-mutuel-arkea'), ('monabanq', 'credit-mutuel-alliance-federale'),
  ('nickel', 'bnp-paribas'), ('hello-bank', 'bnp-paribas'), ('caisse-epargne', 'bpce'), ('banque-populaire', 'bpce')
) as v(slug, parent_slug)
join entities p on p.slug = v.parent_slug
where e.slug = v.slug and e.parent_id is null;
