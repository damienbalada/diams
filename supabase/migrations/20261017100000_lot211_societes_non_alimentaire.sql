-- Lot 211 : propriétaires de marques non alimentaires (suite du lot 210, 17/10/2026).
--  - Bolton Solitaire (Courbevoie), éditrice du site de Carolin ; SIREN vérifié dans l'annuaire
--    officiel des entreprises le 17/10/2026 (349048819, active, APE 46.44Z). Aucun lien de contrôle
--    déclaré au GLEIF : non rattachée au groupe Bolton.
--  - F.I.L.A. S.p.A. (Pero, Italie), marques Giotto, Lyra, Canson, Daler-Rowney, DAS, Tratto ;
--    LEI vérifié dans GLEIF le 17/10/2026 (81560094A389646CAF21, actif).
--  - Kingfisher plc (Londres), enseignes Castorama et Brico Dépôt ; LEI vérifié dans GLEIF le
--    17/10/2026 (213800KBMEV7I92FY281, actif).
--  - Candy Hoover Group S.r.l. (Brugherio, groupe Haier), marques Candy et Hoover ; LEI vérifié dans
--    GLEIF le 17/10/2026 (8156003BD6546E5CEC55, actif).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('bolton-solitaire', 'BOLTON SOLITAIRE', 'Bolton Solitaire', null, '349048819', 'FR', 'home_care'),
  ('fila', 'F.I.L.A. - Fabbrica Italiana Lapis ed Affini S.p.A.', 'FILA', '81560094A389646CAF21', null, 'IT', 'household_durables'),
  ('kingfisher', 'KINGFISHER PLC', 'Kingfisher', '213800KBMEV7I92FY281', null, 'GB', 'retail_distribution'),
  ('candy-hoover-group', 'CANDY HOOVER GROUP S.R.L.', 'Candy Hoover Group (Haier Europe)', '8156003BD6546E5CEC55', null, 'IT', 'household_durables')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;

-- Gigamarket SAS (Villeneuve-sur-Lot), éditrice du site gifi.fr ; SIREN vérifié dans l'annuaire officiel
-- le 17/10/2026 (521403493, active, APE 47.91A).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'gigamarket', 'GIGAMARKET', 'Gigamarket (GiFi)', null, '521403493', 'FR', s.id, false
from sectors s where s.code = 'retail_distribution'
on conflict (slug) do nothing;
