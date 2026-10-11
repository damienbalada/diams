-- =============================================================================
-- Socle d'indicateurs et données de groupe reprises par les marques (v0.6.0)
-- -----------------------------------------------------------------------------
-- Décisions de l'utilisateur du 11/10/2026 (fiabilité visée : 85 %) :
--
-- 1. Socle. Un indicateur sans source publique systématique aujourd'hui
--    (salaire décent, contentieux, présence en paradis fiscaux…) ou qui recense
--    des controverses (sanctions, allégations, conflits) est COMPLÉMENTAIRE :
--    présent, il compte ; absent, il ne baisse ni la note ni la fiabilité. Une
--    publication obligatoire manquante compte toujours 0 (Règle 1).
--
-- 2. Règle 8 révisée. Pour les indicateurs qui relèvent par nature du groupe
--    (gouvernance, fiscalité, lobbying, climat, rémunération, vigilance,
--    financement), une marque reprend les preuves de son groupe, signalées
--    « donnée du groupe », et ses obligations. Les politiques propres au produit
--    (animaux, plastique, transparence textile) et les labels restent propres à
--    la marque. Une preuve propre à la marque passe toujours devant.
--
-- 3. Lobbying climat (InfluenceMap) compté (poids 0,8), complémentaire.
-- =============================================================================

alter table indicators add column if not exists complementary boolean not null default false;
alter table indicators add column if not exists group_level boolean not null default false;

comment on column indicators.complementary is
  'Indicateur hors socle (pas de source publique systématique, ou recensement de controverses) : présent = compté ; absent = ignoré, sauf publication obligatoire. Méthodologie v0.6.0.';
comment on column indicators.group_level is
  'Indicateur qui relève par nature du groupe : une marque reprend les preuves et obligations de son groupe (Règle 8 révisée, v0.6.0).';

update indicators set complementary = true where code in (
  'LAB_LIVING_WAGE', 'LAB_LITIGATION_RATE', 'SUP_SUPPLIER_LIST', 'SUP_LIVING_WAGE', 'TAX_HAVEN_PRESENCE',
  'TAX_CBCR_PUBLISHED', 'WAT_INTENSITY', 'WAT_CONTROVERSY', 'PLA_RECYCLED', 'INV_CONTROVERSIAL_HOLDINGS',
  'INV_SUSTAINABLE_FINANCE', 'GOV_SANCTIONS', 'SUP_BHRRC_ALLEG', 'GEO_CONFLICT_TIES', 'GEO_POL_FINANCING',
  'GEO_LOBBYING_ALIGN', 'ENV_MATERIAL_CHANGE', 'ANI_ANGORA_MOHAIR', 'ANI_DOWN_RDS', 'ANI_EXOTIC_SKINS',
  'ANI_LEATHER_TRACE', 'ANI_SLAUGHTER', 'ANI_TESTING', 'ANI_WOOL_MULESING');

update indicators set group_level = true where code in (
  'GOV_BOARD_GENDER', 'GOV_BOARD_INDEP', 'GOV_SANCTIONS',
  'TAX_EFFECTIVE_RATE', 'TAX_CBCR_PUBLISHED', 'TAX_HAVEN_PRESENCE',
  'GEO_LOBBYING_TRANSP', 'GEO_LOBBYING_SPEND', 'GEO_LOBBYING_ALIGN', 'GEO_POL_FINANCING', 'GEO_RUSSIA_EXIT', 'GEO_CONFLICT_TIES',
  'ENV_SBTI_VALIDATED', 'ENV_CDP_CLIMATE', 'ENV_SCOPE3_DISCLOSED', 'ENV_GHG_INTENSITY', 'WAT_CDP',
  'LAB_CEO_PAY_RATIO', 'LAB_GENDER_PAYGAP', 'SUP_VIGILANCE_PLAN', 'SUP_KNOWTHECHAIN',
  'INV_FOSSIL_FINANCING', 'INV_RESPONSIBLE_POLICY', 'INV_CONTROVERSIAL_HOLDINGS', 'INV_SUSTAINABLE_FINANCE');

update indicators set weight = 0.8 where code = 'GEO_LOBBYING_ALIGN';

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
-- Groupe racine (l'entité elle-même si elle n'a pas de parent).
root as (select * from chain order by depth desc limit 1),
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
  -- Obligations de l'entité, et pour une marque celles de son groupe sur les
  -- indicateurs qui relèvent du groupe (Règle 8 révisée, v0.6.0).
  select ir.indicator_id, jsonb_agg(distinct dr.name order by dr.name) as regimes
  from indicator_regimes ir
  join indicators gi on gi.id = ir.indicator_id
  join entity_regimes er on er.regime_id = ir.regime_id
   and (er.entity_id = (select id from me)
        or (gi.group_level and er.entity_id = (select id from root) and (select id from root) <> (select id from me)))
  join disclosure_regimes dr on dr.id = ir.regime_id
  group by ir.indicator_id
),
appl as (
  select i.id, i.code, i.name, i.unit, d.code as dimension_code, i.kind, i.direction, i.weight, i.presence_only,
         i.complementary, i.group_level,
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
         coalesce(e.source_url, s.url) as source_url, e.excerpt, s.name as source_name,
         null::text as inherited_from
  from evidence_active e
  join appl a  on a.id = e.indicator_id
  join sources s on s.id = e.source_id
  where e.entity_id = (select id from me)
  union all
  -- Marque : preuves du groupe sur les indicateurs de groupe, moins spécifiques
  -- que les siennes (une preuve propre à la marque passe toujours devant).
  select a.code, s.tier, e.nature, e.normalized_value, e.value_numeric,
         e.confidence, e.observed_on, -1, e.contested, s.code,
         coalesce(e.source_url, s.url), e.excerpt, s.name,
         (select name from root)
  from evidence_active e
  join appl a  on a.id = e.indicator_id and a.group_level
  join sources s on s.id = e.source_id
  where e.entity_id = (select id from root) and (select id from root) <> (select id from me)
),
peer as (
  select a.code as indicator_code, e.value_numeric
  from evidence_active e
  join appl a on a.id = e.indicator_id and a.kind = 'quantitative'
  -- Indicateur de groupe : rang parmi les pairs du secteur du groupe, pour qu'une
  -- marque reprenne exactement le rang de son groupe (ni doublon, ni autre échelle).
  join entities en on en.id = e.entity_id
   and en.sector_id = case when a.group_level then coalesce((select sector_id from root), (select sector_id from me))
                           else (select sector_id from me) end
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
      'mandatory', mandatory, 'mandatory_regimes', mandatory_regimes, 'presence_only', presence_only,
      'complementary', complementary, 'group_level', group_level)), '[]') from appl),
  'evidence', (select coalesce(jsonb_agg(jsonb_build_object(
      'indicator_code', indicator_code, 'tier', tier, 'nature', nature, 'normalized_value', normalized_value,
      'value_numeric', value_numeric, 'confidence', confidence, 'observed_on', observed_on,
      'specificity', specificity, 'contested', contested, 'source_code', source_code, 'source_url', source_url,
      'excerpt', excerpt, 'source_name', source_name, 'inherited_from', inherited_from)), '[]') from ev),
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
  'Entrées du moteur (v0.6.0) : preuves propres à l''entité et, pour une marque, preuves du groupe sur les indicateurs de groupe (inherited_from) ; indicateurs applicables (pertinence sectorielle et géographique, socle / complémentaire, niveau groupe) avec leur caractère obligatoire (Règle 1).';
