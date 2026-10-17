-- Secteur « Tabac » (décision de l'éditeur du 17/10/2026 : le tabac entre dans l'Index). Les cigarettes se
-- vendent en bureau de tabac, les feuilles et filtres (OCB, Zig-Zag) aussi en grande surface. Pilier
-- plastique applicable (filtres en acétate de cellulose, premier déchet ramassé sur les plages) ; pas
-- d'enjeu animal ni d'eau propre au secteur ; s'appliquent aussi l'évolution réelle des émissions et la
-- note forêts du CDP (bois de séchage du tabac).
insert into sectors (code, name, description, animal_relevant, plastic_relevant, water_relevant)
values ('tobacco', 'Tabac', 'Cigarettes, tabac à rouler, feuilles et filtres.', false, true, false)
on conflict (code) do nothing;

insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where i.code in ('ENV_GHG_TREND', 'ENV_CDP_FORESTS') and s.code = 'tobacco'
on conflict do nothing;

-- Lot 224 : groupes du tabac, LEI vérifiés dans GLEIF le 17/10/2026 (actifs). Japan Tobacco (Camel et
-- Winston en France) n'est pas ajouté : son site refuse le vérificateur.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, null, v.country, s.id, false
from (values
  ('philip-morris-international', 'Philip Morris International Inc.', 'Philip Morris International', 'HL3H1H2BGXWVG3BSWR90', 'US'),
  ('british-american-tobacco', 'BRITISH AMERICAN TOBACCO P.L.C.', 'British American Tobacco', '213800FKA5MF17RJKT63', 'GB'),
  ('imperial-brands', 'IMPERIAL BRANDS PLC', 'Imperial Brands', '549300DFVPOB67JL3A42', 'GB'),
  ('republic-technologies', 'REPUBLIC TECHNOLOGIES (INTERNATIONAL) SAS', 'Republic Technologies', '9695003RFDAYR0KM3132', 'FR')
) as v(slug, legal_name, display_name, lei, country)
join sectors s on s.code = 'tobacco'
on conflict (slug) do nothing;
