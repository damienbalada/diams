-- Lot 229 : marques exploitées sous licence (décision de l'éditeur du 17/10/2026 : même règle que Pyrex et
-- Whirlpool, la marque est rattachée à la société qui vend en France, la preuve affichée nomme le titulaire).
--  - Osram (éclairage domestique) : « par Ledvance GmbH » sur le site d'OSRAM ; LEDVANCE GmbH (Allemagne),
--    LEI 549300B4TVTT8W8O0H31 vérifié dans GLEIF le 17/10/2026 (actif).
--  - Lonely Planet (éditions françaises) : Edi8 (Paris), éditeur du site lonelyplanet.fr ; SIREN 389160441
--    vérifié dans l'annuaire officiel le 17/10/2026 (actif, APE 58.11Z).
--  - Sharp : pas une licence ; Sharp Electronics (Europe) Limited, filiale du groupe Sharp, LEI
--    213800XBOTLH5CYEGB68 vérifié dans GLEIF le 17/10/2026 (actif).
-- Kodak reste de côté : la marque est concédée à des fabricants différents selon les produits.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('ledvance', 'LEDVANCE GMBH', 'Ledvance (licence OSRAM pour l''éclairage domestique)', '549300B4TVTT8W8O0H31', null, 'DE', 'household_durables'),
  ('edi8', 'EDI8', 'Edi8 (éditions françaises de Lonely Planet)', null, '389160441', 'FR', 'publishing'),
  ('sharp-electronics-europe', 'SHARP ELECTRONICS (EUROPE) LIMITED', 'Sharp Electronics (Europe)', '213800XBOTLH5CYEGB68', null, 'GB', 'tech_electronics')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
