-- =============================================================================
-- Filiales françaises des groupes étrangers (décision de l'éditeur du 16/10/2026)
-- -----------------------------------------------------------------------------
-- L'index Égapro et la déclaration Rixain sont dus par chaque société employeuse en France : pour un
-- groupe étranger, c'est sa filiale française qui les publie. Filiales retenues : liens de contrôle
-- déclarés au registre mondial des identifiants d'entités (GLEIF, lien direct ou ultime, statut
-- « publié », mis à jour depuis 2025 ; les liens périmés sont écartés, ex. Panzani, Galderma), SIREN
-- confirmé actif dans le répertoire Sirene, et présence dans l'export Égapro ou Rixain. Une filiale
-- principale par groupe (la plus grande, d'après la tranche d'effectif de Sirene) transmet ses données
-- à la fiche du groupe et de ses marques, signalées comme reprises de la filiale.
-- =============================================================================
alter table entities add column if not exists filiale_fr_principale boolean not null default false;
comment on column entities.filiale_fr_principale is
  'Filiale française principale d''un groupe étranger : transmet au groupe et à ses marques les indicateurs français dus par chaque société employeuse (Égapro, loi Rixain).';

insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand, animal_free, parent_id, filiale_fr_principale)
select v.slug, v.legal, v.nom, v.lei, v.siren, 'FR', p.sector_id, false, false, p.id, v.princ
from (values
  ('reckitt-benckiser-france', 'RECKITT BENCKISER FRANCE (RBF)', 'Reckitt Benckiser France', '549300PE5XG0Z1D2DT55', '562102558', 'reckitt', true),
  ('ab-inbev-france', 'AB INBEV FRANCE', 'AB InBev France', '549300B7JRBPJBVJF653', '321336208', 'ab-inbev', true),
  ('stellantis-auto', 'STELLANTIS AUTO SAS', 'Stellantis Auto SAS', '969500HXH031HJIFGL63', '542065479', 'stellantis', true),
  ('henkel-technologies-france', 'HENKEL TECHNOLOGIES FRANCE (HENKEL SURFACE TECHNOLOGIES FRANCE)', 'Henkel Technologies France', '529900RFA53WAEZSHH37', '592067136', 'henkel', false),
  ('henkel-france', 'HENKEL FRANCE', 'Henkel France', '529900X780BCU838YO16', '552117590', 'henkel', true),
  ('nestle-france', 'NESTLE FRANCE (LABORATOIRES GUIGOZ) (MNF)', 'Nestlé France', '549300Y95C5GHIQ0T024', '542014428', 'nestle', true),
  ('nestle-waters-marketing-distribution', 'NESTLE WATERS MARKETING & DISTRIBUTION (NWMD)', 'Nestlé Waters Marketing & Distribution', '549300YQKN2NG4BM2O03', '479463044', 'nestle', false),
  ('nestle-waters-supply-sud', 'NESTLE WATERS SUPPLY SUD (N W S  SUD)', 'Nestlé Waters Supply Sud', '549300WEO9QVCYTJRI27', '702034398', 'nestle', false),
  ('nestle-waters-supply-est', 'NESTLE WATERS SUPPLY EST (N W S  EST)', 'Nestlé Waters Supply Est', '549300DXW24EJIUPL720', '479464166', 'nestle', false),
  ('nestle-waters-management-technology', 'NESTLE WATERS MANAGEMENT & TECHNOLOGY', 'Nestlé Waters Management & Technology', '549300DO6UY7R5SEO307', '393204516', 'nestle', false),
  ('shell-france', 'SHELL FRANCE', 'Shell France', '213800TZ4772M9VVFE92', '780130175', 'shell', true),
  ('edgewell-personal-care-france', 'EDGEWELL PERSONAL CARE FRANCE', 'Edgewell Personal Care France', '549300L9554X5Y7P7L67', '333565844', 'edgewell', true),
  ('sofibel', 'SOFIBEL (LABORATOIRES SANTE BEAUTE - LABORATOIRES FUMOUZE)', 'Sofibel (Laboratoires Fumouze)', '9695002QBT18RGN6AX08', '397914862', 'church-dwight', true),
  ('hasbro-france', 'HASBRO FRANCE', 'Hasbro France', '549300ZZELWBX2CHTM38', '746220623', 'hasbro', true),
  ('mccormick-france', 'MCCORMICK FRANCE', 'McCormick France', '5493007QJEPNO77MW055', '622980027', 'mccormick', true),
  ('pepsico-france', 'PEPSICO FRANCE', 'PepsiCo France', '549300V4LN12XSLCJB38', '381511039', 'pepsico', true),
  ('essity-pld-france', 'ESSITY PLD FRANCE', 'Essity PLD France', '549300FB6L0MIUTZS283', '509599619', 'essity', false),
  ('essity-operations-france', 'ESSITY OPERATIONS FRANCE', 'Essity Operations France', '5493000DWWM9ODLJWY61', '702055187', 'essity', true),
  ('gelagri-bretagne', 'GELAGRI-BRETAGNE', 'Gelagri Bretagne', '96950088HV0D4EGVJQ52', '307667030', 'greenyard', true),
  ('sofidel-france', 'SOFIDEL FRANCE (SOFIDEL FRANCE ETABLISSEMENT DE FROUARD)', 'Sofidel France', '969500CV0WS9CHMDIZ22', '411198880', 'sofidel', true),
  ('hp-france', 'HP FRANCE SAS', 'HP France', '254900V6WP6ZE2JGF112', '448694133', 'hp-inc', true),
  ('campari-france', 'CAMPARI FRANCE (CAMPARI FRANCE) (CF)', 'Campari France', '213800VYUTS4GKIRQQ53', '511042368', 'campari', true)
) as v(slug, legal, nom, lei, siren, parent, princ)
join entities p on p.slug = v.parent
on conflict (slug) do nothing;

-- Filiales françaises déjà présentes (Carte Noire SAS pour Lavazza, Orangina Schweppes France pour Suntory).
update entities set filiale_fr_principale = true where slug in ('carte-noire-sas', 'orangina-schweppes-france');

create or replace function compute_score_input(p_slug text, p_profile text default 'equilibre')
returns jsonb
language sql
stable
set search_path = public
as $$
with recursive chain as (
  select id, parent_id, 0 as depth, sector_id, slug, coalesce(display_name, legal_name) as name, country, is_brand
  from entities where slug = p_slug
  union all
  select e.id, e.parent_id, c.depth+1, e.sector_id, e.slug, coalesce(e.display_name, e.legal_name), e.country, e.is_brand
  from entities e join chain c on e.id = c.parent_id
),
me as (select * from chain where depth = 0),
-- Groupe racine (l'entité elle-même si elle n'a pas de parent).
root as (select * from chain order by depth desc limit 1),
-- Propriétaire direct d'une marque (v0.7.5) : c'est lui qui transmet les indicateurs
-- « du propriétaire » (owner_level), dus par chaque société employeuse (Égapro).
owner as (select * from chain where depth = 1 and (select is_brand from me)),
-- Filiale française principale (16/10/2026) : pour un groupe étranger (ou une marque dont le
-- propriétaire direct est étranger), les indicateurs dus par chaque société employeuse française
-- (Égapro, loi Rixain) sont repris de sa filiale française principale, déclarée dans entities.
holder as (select * from owner
           union all select * from me where not (select is_brand from me) and not exists (select 1 from owner)),
fr_sub as (select e.id, coalesce(e.display_name, e.legal_name) as name
           from entities e
           where e.parent_id = (select id from holder) and e.filiale_fr_principale
             and (select country from holder) is distinct from 'FR'
           limit 1),
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
        or (gi.group_level and er.entity_id = (select id from root) and (select id from root) <> (select id from me))
        or (gi.owner_level and er.entity_id = (select id from owner)))
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
     or (gi.owner_level and x.entity_id = (select id from owner))
),
appl as (
  select i.id, i.code, i.name, i.unit, d.code as dimension_code, i.kind, i.direction, i.weight, i.presence_only,
         i.complementary, i.group_level, i.owner_level, i.disclosure,
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
                                                 when i.owner_level and exists (select 1 from owner)
                                                 then coalesce((select sector_id from owner), (select sector_id from me))
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
         or (i.jurisdiction = 'FR' and i.owner_level and not i.group_level and exists (select 1 from fr_sub))
         or i.jurisdiction = case when i.group_level then (select country from root)
                                    when i.owner_level and exists (select 1 from owner)
                                    then coalesce((select country from owner), (select country from me))
                                    else (select country from me) end)
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
  union all
  -- Marque : preuves de son propriétaire direct sur les indicateurs « du propriétaire »
  -- (index Égapro, v0.7.5), signalées comme reprises ; une preuve propre passe devant.
  select a.code, s.tier, e.nature, e.normalized_value, e.value_numeric,
         e.confidence, e.observed_on, -1, e.contested, s.code,
         coalesce(e.source_url, s.url), e.excerpt, s.name,
         (select name from owner)
  from evidence_active e
  join appl a  on a.id = e.indicator_id and a.owner_level and not a.group_level
  join sources s on s.id = e.source_id
  where e.entity_id = (select id from owner)
  union all
  -- Groupe étranger, ou marque d'un propriétaire étranger : preuves de la filiale française
  -- principale sur les indicateurs français « du propriétaire », signalées comme reprises.
  select a.code, s.tier, e.nature, e.normalized_value, e.value_numeric,
         e.confidence, e.observed_on, -2, e.contested, s.code,
         coalesce(e.source_url, s.url), e.excerpt, s.name,
         (select name from fr_sub)
  from evidence_active e
  join appl a  on a.id = e.indicator_id and a.owner_level and not a.group_level
  join sources s on s.id = e.source_id
  where e.entity_id = (select id from fr_sub)
),
peer as (
  select a.code as indicator_code, e.value_numeric
  from evidence_active e
  join appl a on a.id = e.indicator_id and a.kind = 'quantitative'
  -- Indicateur de groupe : rang parmi les pairs du secteur du groupe, pour qu'une
  -- marque reprenne exactement le rang de son groupe (ni doublon, ni autre échelle).
  join entities en on en.id = e.entity_id
   and en.sector_id = case when a.group_level then coalesce((select sector_id from root), (select sector_id from me))
                           when a.owner_level and exists (select 1 from owner)
                           then coalesce((select sector_id from owner), (select sector_id from me))
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
