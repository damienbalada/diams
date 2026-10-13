-- =============================================================================
-- Donnée déclarée non matérielle : pas d'obligation, donc pas de 0 (v0.7.3)
-- -----------------------------------------------------------------------------
-- La Règle 1 compte 0 une donnée dont la loi impose la publication. Mais la CSRD
-- n'impose pas une donnée que l'entreprise a déclarée non matérielle dans son
-- état de durabilité (audité) : la compter 0 pénaliserait le respect de la loi.
-- Table obligation_exemptions : l'exemption, citée mot pour mot depuis le rapport
-- réglementé, retire l'obligation pour cette entité et cet indicateur ; la fiche
-- l'affiche (« déclarée non matérielle par l'entreprise »). Une donnée simplement
-- « non publiée » ou « non chiffrée » n'est pas exemptée.
-- =============================================================================

create table if not exists obligation_exemptions (
  id           uuid primary key default gen_random_uuid(),
  entity_id    uuid not null references entities(id) on delete cascade,
  indicator_id uuid not null references indicators(id) on delete cascade,
  reason       text not null check (char_length(btrim(reason)) > 0),
  source_url   text not null,
  excerpt      text not null,
  created_at   timestamptz not null default now(),
  unique (entity_id, indicator_id)
);
comment on table obligation_exemptions is
  'Donnée déclarée non matérielle par l''entreprise dans son rapport réglementé : l''obligation de publier (Règle 1) ne s''applique pas (v0.7.3). Citation mot pour mot obligatoire.';
alter table obligation_exemptions enable row level security;
create policy "public read" on obligation_exemptions for select using (true);

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
  -- Donnée déclarée non matérielle par l'entreprise dans son rapport réglementé :
  -- la loi n'en impose pas la publication (v0.7.3).
  where not exists (select 1 from obligation_exemptions x
                    where x.indicator_id = ir.indicator_id and x.entity_id = er.entity_id)
  group by ir.indicator_id
),
exemptions as (
  select x.indicator_id, x.reason
  from obligation_exemptions x
  join indicators gi on gi.id = x.indicator_id
  where x.entity_id = (select id from me)
     or (gi.group_level and x.entity_id = (select id from root) and (select id from root) <> (select id from me))
),
appl as (
  select i.id, i.code, i.name, i.unit, d.code as dimension_code, i.kind, i.direction, i.weight, i.presence_only,
         i.complementary, i.group_level, i.disclosure,
         (o.indicator_id is not null) as mandatory, coalesce(o.regimes, '[]'::jsonb) as mandatory_regimes,
         xm.reason as exemption
  from indicators i join dimensions d on d.id = i.dimension_id
  left join obligations o on o.indicator_id = i.id
  left join exemptions xm on xm.indicator_id = i.id
  where (case
           -- Pertinence par liste de secteurs (indicator_sectors) : l'indicateur ne
           -- s'applique qu'aux secteurs listés ; pour un indicateur de groupe, c'est
           -- le secteur du groupe qui compte (v0.6.0).
           when exists (select 1 from indicator_sectors x where x.indicator_id = i.id)
           then exists (select 1 from indicator_sectors x
                        where x.indicator_id = i.id
                          and x.sector_id = case when i.group_level
                                                 then coalesce((select sector_id from root), (select sector_id from me))
                                                 else (select sector_id from me) end)
           else i.sector_specific = false or i.applies_to_sector_id = (select sector_id from me)
         end)
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
    -- Dispositif national : pour un indicateur de groupe, c'est le pays du groupe
    -- qui compte (le plan de vigilance de Kering couvre Gucci).
    and (i.jurisdiction is null
         or i.jurisdiction = case when i.group_level then (select country from root) else (select country from me) end)
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
      'complementary', complementary, 'group_level', group_level, 'disclosure', disclosure,
      'exemption', exemption)), '[]') from appl),
  'evidence', (select coalesce(jsonb_agg(jsonb_build_object(
      'indicator_code', indicator_code, 'tier', tier, 'nature', nature, 'normalized_value', normalized_value,
      'value_numeric', value_numeric, 'confidence', confidence, 'observed_on', observed_on,
      'specificity', specificity, 'contested', contested, 'source_code', source_code, 'source_url', source_url,
      'excerpt', excerpt, 'source_name', source_name, 'inherited_from', inherited_from)), '[]') from ev),
  'dimensions', (select jsonb_agg(jsonb_build_object('code', code, 'name', name)) from dimensions),
  -- Poids du profil × matérialité sectorielle (ex : climat ×3 dans l'énergie).
  'profileWeights', (select coalesce(jsonb_agg(jsonb_build_object('dimension_code', d.code,
      'weight', pw.weight * coalesce(sdw.multiplier, 1))), '[]')
      from profile_weights pw join dimensions d on d.id = pw.dimension_id
      left join sector_dimension_weights sdw on sdw.dimension_id = d.id and sdw.sector_id = (select sector_id from me)
      where pw.profile_id = (select id from prof limit 1)),
  'materiality', (select coalesce(jsonb_agg(jsonb_build_object('dimension_code', d.code, 'multiplier', sdw.multiplier,
      'note', sdw.note) order by d.code), '[]')
      from sector_dimension_weights sdw join dimensions d on d.id = sdw.dimension_id
      where sdw.sector_id = (select sector_id from me)),
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
  'Entrées du moteur (v0.7.3) : comme v0.6.0, et exemptions d''obligation (donnée déclarée non matérielle par l''entreprise, citée).';

insert into obligation_exemptions (entity_id, indicator_id, reason, source_url, excerpt)
select e.id, i.id,
  'Déclarée non matérielle par LVMH dans son état de durabilité 2025 : la CSRD n''en impose pas la publication.',
  'https://bdif.amf-france.org/back/api/v1/documents/2026/D.26-0195/CA8A1E35A6C70FC2DE6B35F0939523887728C2FE2C11DFAC7F9B5F7675629928.zip',
  'Document d''enregistrement universel 2025 de LVMH, table des points de données ESRS : « S1-16 §97 (a) Écart de rémunération entre hommes et femmes non corrigé SFDR Indicateur n° 12, tableau 1, annexe I NM » ; légende : « NM : non-matériel ».'
from entities e, indicators i where e.slug = 'lvmh' and i.code = 'LAB_GENDER_PAYGAP'
on conflict (entity_id, indicator_id) do nothing;
