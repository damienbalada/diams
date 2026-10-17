-- Lot 251 : marques d'Open Products Facts France absentes de l'Index (2026-10-18). Propriétaires prouvés par
-- les mentions légales ou le pied de page du site officiel ; SIREN vérifiés dans l'annuaire des entreprises,
-- sociétés françaises sans LEI.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('tricotage-des-vosges', 'TRICOTAGE DES VOSGES', 'Tricotage des Vosges', null, '398356246', 'FR', 'fashion_leather'),
  ('gault-millau-france', 'GAULTMILLAU', 'Gault&Millau France', null, '418576955', 'FR', 'publishing'),
  ('elp-sas', 'ELP', 'ELP', null, '581980018', 'FR', 'personal_care')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
