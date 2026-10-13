-- Enseignes d'hypermarchés et grands groupes agroalimentaires français non cotés (ou
-- peu documentés). Identifiants vérifiés le 13/10/2026 : SIREN dans l'annuaire officiel
-- des entreprises (recherche-entreprises.api.gouv.fr, données INSEE/INPI) et LEI dans
-- le registre GLEIF (recherche par SIREN, entité active, LEI émis) quand il existe.
--   E.Leclerc            ACDLec (association des centres distributeurs)   SIREN 784413486
--   Système U            Coopérative U          SIREN 304602956  LEI 96950059U7TYET6L7D42
--   Les Mousquetaires    ITM Entreprises SA     SIREN 722064102  LEI 969500LMMR83QL6TLK43
--   Auchan               ELO (société mère)     SIREN 476180625  LEI 969500ASEC557H5A4F22
--   Groupe Casino        Casino, Guichard-Perrachon SIREN 554501171 LEI 969500VHL8F83GBL6L29
--   Picard               Picard Surgelés        SIREN 784939688  LEI 96950060THCJP2U5U446
--   Sodiaal              Sodiaal Union          SIREN 351572888
--   Groupe Avril         Avril                  SIREN 799403050  LEI 9695004R3U32NHY14K02
--   Cristal Union        Cristal Union          SIREN 421343369  LEI 969500D8BWYH453FLN28
--   Agrial               Coopérative Agrial     SIREN 428611719  LEI 969500CIV6V451G2DU77
--   Andros               Andros                 SIREN 428682447  LEI 9695006ARZU1PBC9M649
--   Fleury Michon        Fleury Michon          SIREN 572058329  LEI 96950009EM1D72NGCV27
--   Tereos               Tereos SCA             SIREN 303628499  LEI 9695003FV2AYJQ4ETG94
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, 'FR', s.id, false
from (values
  ('leclerc',        'Association des Centres Distributeurs E. Leclerc', 'E.Leclerc',         null,                   '784413486', 'retail_distribution'),
  ('systeme-u',      'Coopérative U',                  'Système U',          '96950059U7TYET6L7D42', '304602956', 'retail_distribution'),
  ('mousquetaires',  'ITM Entreprises SA',             'Les Mousquetaires',  '969500LMMR83QL6TLK43', '722064102', 'retail_distribution'),
  ('auchan',         'ELO',                            'Auchan',             '969500ASEC557H5A4F22', '476180625', 'retail_distribution'),
  ('casino',         'Casino, Guichard-Perrachon',     'Groupe Casino',      '969500VHL8F83GBL6L29', '554501171', 'retail_distribution'),
  ('picard',         'Picard Surgelés',                'Picard',             '96950060THCJP2U5U446', '784939688', 'retail_distribution'),
  ('sodiaal',        'Sodiaal Union',                  'Sodiaal',            null,                   '351572888', 'food'),
  ('avril',          'Avril',                          'Groupe Avril',       '9695004R3U32NHY14K02', '799403050', 'food'),
  ('cristal-union',  'Cristal Union',                  'Cristal Union',      '969500D8BWYH453FLN28', '421343369', 'food'),
  ('agrial',         'Société coopérative agricole et agro-alimentaire Agrial', 'Agrial', '969500CIV6V451G2DU77', '428611719', 'food'),
  ('andros',         'Andros',                         'Andros',             '9695006ARZU1PBC9M649', '428682447', 'food'),
  ('fleury-michon',  'Fleury Michon',                  'Fleury Michon',      '96950009EM1D72NGCV27', '572058329', 'food'),
  ('tereos',         'Tereos SCA',                     'Tereos',             '9695003FV2AYJQ4ETG94', '303628499', 'food')
) as v(slug, legal_name, display_name, lei, siren, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
