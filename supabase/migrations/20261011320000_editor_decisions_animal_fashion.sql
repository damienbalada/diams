-- =============================================================================
-- Décisions de l'éditeur du 11/10/2026 (v0.7.0)
-- -----------------------------------------------------------------------------
-- 1. Exploitation animale : « si une marque utilise et exploite des animaux, sa
--    note est au plus bas dans cette catégorie » — pas d'excuse de marginalité.
--    Le barème à trois niveaux (sans intrant animal 1,0 / marginal 0,55 /
--    au cœur de l'activité 0,40) devient binaire : sans intrant animal 1,0 ;
--    toute exploitation 0. Le niveau inconnu reste présumé (anti-opacité) : 0.
--    La présomption vaut dans tous les secteurs à enjeu animal, plus seulement
--    la mode et le luxe ; seule une gamme sans intrant animal y échappe.
-- 2. Mode : la chaîne d'approvisionnement et l'environnement sont les impacts
--    principaux du secteur (fabrication sous-traitée, salaires, matières,
--    volumes) : les deux piliers comptent double, pour les marques de mode comme
--    pour les groupes de luxe.
-- 3. ENGIE : le ratio de rémunération calculé sur la rémunération moyenne (la
--    médiane n'étant pas calculable, selon le groupe) est accepté tel que publié.
-- =============================================================================

-- 1. Exploitation animale
update dimension_gates set default_ceiling = 0,
  notes = 'Exploitation animale : toute exploitation, même marginale, met le pilier au plus bas (0). Niveau inconnu : exploitation présumée (décision de l''éditeur, 11/10/2026).'
where gate_indicator_id = (select id from indicators where code = 'ANI_EXPLOITATION');

update indicators set methodology =
  'PLAFOND du pilier. Sans intrant animal = 1 ; toute exploitation animale, même marginale = 0 (décision de l''éditeur, 11/10/2026). Inconnu : exploitation présumée.'
where code = 'ANI_EXPLOITATION';

insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where i.code = 'ANI_EXPLOITATION' and s.animal_relevant
on conflict do nothing;

update evidence e set normalized_value = 0
from indicators i
where i.id = e.indicator_id and i.code = 'ANI_EXPLOITATION' and e.normalized_value < 1;

-- 2. Mode et luxe : chaîne d'approvisionnement ×2, environnement ×2
insert into sector_dimension_weights (sector_id, dimension_id, multiplier, note)
select s.id, d.id, 2, n.note
from sectors s cross join dimensions d
join (values
  ('SUP', 'Mode : la fabrication est sous-traitée à des fournisseurs (salaires, conditions de travail) ; le pilier compte double.'),
  ('ENV', 'Mode : matières, volumes produits et émissions de la fabrication sont l''impact principal du secteur ; le pilier compte double.')
) as n(code, note) on n.code = d.code
where s.code in ('fashion_leather', 'luxury_group')
on conflict (sector_id, dimension_id) do update set multiplier = excluded.multiplier, note = excluded.note;

-- 3. ENGIE : ratio de rémunération accepté (lot 18, resté en jugement)
update evidence set review_status = 'approved', reviewer = 'decision-editeur:2026-10-11'
where review_status = 'pending'
  and entity_id = (select id from entities where slug = 'engie')
  and indicator_id = (select id from indicators where code = 'LAB_CEO_PAY_RATIO')
  and observed_on = '2026-03-18' and value_numeric = 74.7;
