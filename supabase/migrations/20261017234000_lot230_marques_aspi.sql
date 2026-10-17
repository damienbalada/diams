-- Lot 230 : marques citées par le rapport « Uyghurs for sale » de l'ASPI (lot 227), vendues en France et
-- absentes de l'Index (décision de l'éditeur du 17/10/2026). Propriétaires prouvés par leur rapport annuel
-- (10-K, 20-F) ou le site officiel de la marque ; LEI vérifiés dans GLEIF le 17/10/2026 (actifs) ; BYD Company
-- Limited absente de GLEIF sous ce nom.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, null, v.country, s.id, false
from (values
  ('pvh-corp', 'PVH CORP.', 'PVH', '123WALMHY1GZXG2YDL90', 'US', 'fashion_leather'),
  ('ralph-lauren-corp', 'RALPH LAUREN CORPORATION', 'Ralph Lauren', 'HO1QNWM0IXBZ0QSMMO20', 'US', 'fashion_leather'),
  ('abercrombie-fitch-co', 'ABERCROMBIE & FITCH CO.', 'Abercrombie & Fitch Co.', '5493000J7LL72TOGT983', 'US', 'fashion_leather'),
  ('dell-technologies', 'Dell Technologies Inc.', 'Dell Technologies', '549300TJB5YBRUPOG437', 'US', 'tech_electronics'),
  ('ermenegildo-zegna', 'ERMENEGILDO ZEGNA N.V.', 'Ermenegildo Zegna', '8156003760472AA7E269', 'NL', 'fashion_leather'),
  ('jaguar-land-rover', 'JAGUAR LAND ROVER LIMITED', 'Jaguar Land Rover', '213800WSGIIZCXF1P572', 'GB', 'automotive'),
  ('byd-company', 'BYD Company Limited', 'BYD (groupe)', null, 'CN', 'automotive'),
  ('skechers-usa', 'Skechers U.S.A., Inc.', 'Skechers U.S.A.', '529900D2R54KZPA4XR56', 'US', 'fashion_leather')
) as v(slug, legal_name, display_name, lei, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
