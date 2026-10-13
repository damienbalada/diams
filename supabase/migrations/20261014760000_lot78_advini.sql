-- AdVini, groupe viticole coté à Paris (Laroche, Ogier, Gassier, L'Oratoire des Papes) :
-- SIREN vérifié dans l'annuaire officiel des entreprises et LEI dans le registre GLEIF
-- (« ADVINI », enregistré sous le SIREN 896 520 038) le 14/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'advini', 'AdVini', 'AdVini', '9695006S6L6YQECK2015', '896520038', 'FR', s.id, false
from sectors s where s.code = 'wines_spirits'
on conflict (slug) do nothing;
