-- Brasseur belge familial Duvel Moortgat (Duvel, Vedett, La Chouffe, Liefmans), dont
-- les bières sont vendues en hypermarché. LEI vérifié dans le registre GLEIF le
-- 13/10/2026. Société non cotée : sa note restera probablement « en attente ».
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'duvel-moortgat', 'Duvel Moortgat', 'Duvel Moortgat', '549300WF4F59KPH23D87', null, 'BE', s.id, false
from sectors s where s.code = 'wines_spirits'
on conflict (slug) do nothing;

-- Asahi Group Holdings (Japon, coté à Tokyo), propriétaire des bières Peroni, Grolsch,
-- Pilsner Urquell et Kozel par sa filiale Asahi Europe & International (LEI
-- 213800WGZV998G2AFU02). LEI du groupe vérifié dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'asahi', 'Asahi Group Holdings, Ltd.', 'Asahi Group Holdings', '353800KAJ02XNHLCJW79', null, 'JP', s.id, false
from sectors s where s.code = 'wines_spirits'
on conflict (slug) do nothing;
