-- =============================================================================
-- Pertinence géographique des indicateurs liés à un dispositif national
-- -----------------------------------------------------------------------------
-- Méthodologie v0.5.1. L'index Égapro et le plan de vigilance mesurent le
-- respect d'instruments français : une société américaine ne peut pas publier
-- un index Égapro. Comptés comme « donnée manquante », ils abaissaient la
-- fiabilité de toute entité non française pour un manque qui n'en est pas un.
-- Un indicateur portant un code pays (indicators.jurisdiction) ne s'applique
-- désormais qu'aux entités de ce pays. Une filiale française (SIREN) reste
-- concernée : c'est elle, et non son groupe étranger, qui publie l'index.
-- =============================================================================

alter table indicators add column if not exists jurisdiction text;

comment on column indicators.jurisdiction is
  'Code pays (ISO 3166-1 alpha-2) d''un indicateur lié à un dispositif national : il ne s''applique qu''aux entités de ce pays. Méthodologie v0.5.1.';

update indicators set jurisdiction = 'FR' where code in ('LAB_EGAPRO_INDEX', 'SUP_VIGILANCE_PLAN');

-- Preuve attribuée à une autre société : l'index Égapro « périmètre France
-- (Coca-Cola Europacific Partners) » est celui d'un embouteilleur distinct, pas
-- de The Coca-Cola Company (l'extrait le dit). Rejetée (tracé, pas supprimé).
update evidence ev set review_status = 'rejected', reviewer = 'rejet:autre-societe-2026-10-11'
from entities e, indicators i
where ev.entity_id = e.id and ev.indicator_id = i.id and i.code = 'LAB_EGAPRO_INDEX'
  and e.slug = 'coca-cola' and ev.review_status = 'approved'
  and ev.excerpt like '%Coca-Cola Europacific Partners%';

create or replace function compute_score_input(p_slug text, p_profile text default 'equilibre')
returns jsonb
language sql
stable
set search_path = public
as $$
with recursive chain as (
  select id, parent_id, 0 as depth, sector_id, slug, coalesce(display_name, legal_name) as name, country
  from entities where slug = p_slug
  union all
  select e.id, e.parent_id, c.depth+1, e.sector_id, e.slug, coalesce(e.display_name, e.legal_name), e.country
  from entities e join chain c on e.id = c.parent_id
),
me as (select * from chain where depth = 0),
me_animal as (
  select coalesce((select s.animal_relevant from sectors s where s.id = (select sector_id from me)), true) as animal_relevant
),
me_wap as (
  select coalesce((select s.plastic_relevant from sectors s where s.id = (select sector_id from me)), false) as plastic_relevant,
         coalesce((select s.water_relevant   from sectors s where s.id = (select sector_id from me)), false) as water_relevant,
         coalesce((select s.inv_relevant     from sectors s where s.id = (select sector_id from me)), false) as inv_relevant
),
me_flags as (
  select coalesce((select animal_free from entities where slug = p_slug), false) as animal_free
),
spec as (select c.id, c.depth, c.name from chain c),
obligations as (
  select ir.indicator_id, jsonb_agg(dr.name order by dr.name) as regimes
  from indicator_regimes ir
  join entity_regimes er on er.regime_id = ir.regime_id and er.entity_id = (select id from me)
  join disclosure_regimes dr on dr.id = ir.regime_id
  group by ir.indicator_id
),
appl as (
  select i.id, i.code, i.name, i.unit, d.code as dimension_code, i.kind, i.direction, i.weight, i.presence_only,
         (o.indicator_id is not null) as mandatory, coalesce(o.regimes, '[]'::jsonb) as mandatory_regimes
  from indicators i join dimensions d on d.id = i.dimension_id
  left join obligations o on o.indicator_id = i.id
  where (i.sector_specific = false or i.applies_to_sector_id = (select sector_id from me))
    and (
      d.code <> 'ANI'
      or (
        (select animal_relevant from me_animal)
        and case
              when (select animal_free from me_flags) then i.code = 'ANI_ANIMAL_FREE'
              else i.code <> 'ANI_ANIMAL_FREE'
            end
      )
    )
    and (d.code <> 'PLA' or (select plastic_relevant from me_wap))
    and (d.code <> 'WAT' or (select water_relevant from me_wap))
    and (d.code <> 'INV' or (select inv_relevant from me_wap))
    and (i.jurisdiction is null or i.jurisdiction = (select country from me))
),
ev as (
  select a.code as indicator_code, s.tier, e.nature, e.normalized_value, e.value_numeric,
         e.confidence, e.observed_on, 0 as specificity, e.contested, s.code as source_code,
         coalesce(e.source_url, s.url) as source_url, e.excerpt, s.name as source_name
  from evidence_active e
  join appl a  on a.id = e.indicator_id
  join sources s on s.id = e.source_id
  where e.entity_id = (select id from me)
),
peer as (
  select a.code as indicator_code, e.value_numeric
  from evidence_active e
  join appl a on a.id = e.indicator_id and a.kind = 'quantitative'
  join entities en on en.id = e.entity_id and en.sector_id = (select sector_id from me)
  where e.value_numeric is not null
),
prof as (
  select p.id, p.code, p.name from value_profiles p where p.code = p_profile
  union all
  select p.id, p.code, p.name from value_profiles p
  where p.is_default and not exists (select 1 from value_profiles where code = p_profile)
)
select jsonb_build_object(
  'entity', (select jsonb_build_object('slug', slug, 'name', name, 'sector_id', sector_id) from me),
  'ownership_chain', (select jsonb_agg(name order by depth) from spec),
  'profile', (select jsonb_build_object('code', code, 'name', name) from prof limit 1),
  'applicableIndicators', (select coalesce(jsonb_agg(jsonb_build_object(
      'code', code, 'name', name, 'unit', unit,
      'dimension_code', dimension_code, 'kind', kind, 'direction', direction, 'weight', weight,
      'mandatory', mandatory, 'mandatory_regimes', mandatory_regimes, 'presence_only', presence_only)), '[]') from appl),
  'evidence', (select coalesce(jsonb_agg(jsonb_build_object(
      'indicator_code', indicator_code, 'tier', tier, 'nature', nature, 'normalized_value', normalized_value,
      'value_numeric', value_numeric, 'confidence', confidence, 'observed_on', observed_on,
      'specificity', specificity, 'contested', contested, 'source_code', source_code, 'source_url', source_url,
      'excerpt', excerpt, 'source_name', source_name)), '[]') from ev),
  'dimensions', (select jsonb_agg(jsonb_build_object('code', code, 'name', name)) from dimensions),
  'profileWeights', (select coalesce(jsonb_agg(jsonb_build_object('dimension_code', d.code, 'weight', pw.weight)), '[]')
      from profile_weights pw join dimensions d on d.id = pw.dimension_id where pw.profile_id = (select id from prof limit 1)),
  'dimensionGroups', (select coalesce(jsonb_agg(jsonb_build_object('code', dg.code, 'name', dg.name,
      'members', (select coalesce(jsonb_agg(jsonb_build_object('dimension_code', d.code, 'weight', m.weight)), '[]')
                  from dimension_group_members m join dimensions d on d.id = m.dimension_id where m.group_id = dg.id))), '[]')
      from dimension_groups dg),
  'dimensionGates', (select coalesce(jsonb_agg(jsonb_build_object(
      'dimension_code', d.code, 'gate_indicator_code', gi.code, 'default_ceiling', dgt.default_ceiling)), '[]')
      from dimension_gates dgt join dimensions d on d.id = dgt.dimension_id join indicators gi on gi.id = dgt.gate_indicator_id
      where d.code <> 'ANI' or ((select animal_relevant from me_animal) and not (select animal_free from me_flags))),
  'tierConfig', (select jsonb_object_agg(tier, jsonb_build_object('evidence_weight', evidence_weight,
      'max_confidence', max_confidence, 'can_penalize_alone', can_penalize_alone,
      'min_score_floor_alone', min_score_floor_alone)) from source_tier_config),
  'natureConfig', (select jsonb_object_agg(nature, jsonb_build_object('score_multiplier', score_multiplier,
      'max_score_without_result', max_score_without_result)) from evidence_nature_config),
  'params', (select jsonb_object_agg(key, value) from scoring_params),
  'peerValues', (select coalesce(jsonb_object_agg(indicator_code, vals), '{}')
      from (select indicator_code, jsonb_agg(value_numeric) as vals from peer group by indicator_code) pp)
);
$$;

comment on function compute_score_input(text, text) is
  'Entrées du moteur (v0.5.1) : evidence propre à l''entité (avec extrait et source), indicateurs applicables (pertinence sectorielle ANI, PLA, WAT, INV ; géographique via indicators.jurisdiction) avec leur caractère obligatoire (Règle 1) et le drapeau label (presence_only).';
