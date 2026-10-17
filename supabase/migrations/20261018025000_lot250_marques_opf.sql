-- Lot 250 : marques d'Open Products Facts France absentes de l'Index (2026-10-18). Propriétaires prouvés par
-- les mentions légales ou le pied de page du site officiel ; SIREN vérifiés dans l'annuaire des entreprises,
-- LEI dans GLEIF (actifs) ; Alcon Inc. absente de GLEIF sous ce nom.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('electronic-arts-inc', 'ELECTRONIC ARTS INC.', 'Electronic Arts', '549300O7A67PUEYKDL45', null, 'US', 'tech_electronics'),
  ('teva-sante', 'TEVA SANTE', 'Teva Santé', null, '401972476', 'FR', 'personal_care'),
  ('alcon-inc', 'Alcon Inc.', 'Alcon', null, null, 'CH', 'personal_care'),
  ('djeco-sas', 'DJECO', 'Djeco (société)', null, '418255121', 'FR', 'toys_games'),
  ('les-relais-de-florame', 'LES RELAIS DE FLORAME', 'Les Relais de Florame', null, '480280007', 'FR', 'beauty_fragrance'),
  ('compo-france', 'COMPO FRANCE', 'Compo France', null, '345408272', 'FR', 'home_care')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
-- Sigma (SIGMA-ELEKTRO GmbH) retiré du lot : le site ne nomme pas la marque « Sigma Sport » ; l'entité,
-- créée lors d'un premier passage, est supprimée (aucune preuve rattachée).
delete from entities e where e.slug = 'sigma-elektro'
  and not exists (select 1 from evidence v where v.entity_id = e.id)
  and not exists (select 1 from entities b where b.parent_id = e.id);
