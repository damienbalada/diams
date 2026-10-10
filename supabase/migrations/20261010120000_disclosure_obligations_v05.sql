-- =============================================================================
-- Méthodologie v0.5 — deux décisions tranchées le 10/10/2026
-- -----------------------------------------------------------------------------
-- (1) Règle 1 révisée : une donnée manquante n'est pénalisante (comptée
--     missing_data_score = 0) QUE si sa publication est légalement obligatoire
--     pour l'entité notée. Sinon, elle baisse la fiabilité mais n'entre pas dans
--     la note. Rationale : ne pas publier ce que la loi impose est un choix ; ne
--     pas publier ce que rien n'impose (PME, coopérative, marque) n'en est pas un
--     — sans cette nuance, les petits acteurs vertueux sont condamnés d'avance.
--
--     Modèle : un RÉGIME (texte légal) rend obligatoires certains INDICATEURS ;
--     une ENTITÉ est soumise à un régime — fait sourcé et daté, comme une preuve.
--
-- (2) Une marque est notée sur SES PROPRES preuves : plus d'héritage de
--     l'evidence du groupe. La chaîne de détention reste affichée (encart « à qui
--     va l'argent ») et la fiche du groupe a sa propre note.
-- =============================================================================

create table disclosure_regimes (
  id              uuid primary key default gen_random_uuid(),
  code            text not null unique,
  name            text not null,
  jurisdiction    text not null,
  legal_basis     text not null,
  scope           text not null,
  url             text not null check (url ~ '^https?://'),
  in_force_since  date,
  created_at      timestamptz not null default now()
);

comment on table disclosure_regimes is
  'Obligations légales de publication (Règle 1 v0.5). Un indicateur rendu obligatoire par un régime auquel l''entité est soumise compte 0 s''il manque.';

create table indicator_regimes (
  indicator_id  uuid not null references indicators(id) on delete cascade,
  regime_id     uuid not null references disclosure_regimes(id) on delete cascade,
  note          text,
  primary key (indicator_id, regime_id)
);

comment on table indicator_regimes is
  'Quels indicateurs un régime rend obligatoires (ex : Égapro -> LAB_EGAPRO_INDEX).';

create table entity_regimes (
  entity_id    uuid not null references entities(id) on delete cascade,
  regime_id    uuid not null references disclosure_regimes(id) on delete cascade,
  -- Pourquoi l'entité est soumise (ex : « établissement de crédit agréé »).
  basis        text not null check (char_length(btrim(basis)) > 0),
  source_url   text not null check (source_url ~ '^https?://'),
  observed_on  date not null,
  reviewer     text,
  created_at   timestamptz not null default now(),
  primary key (entity_id, regime_id)
);

comment on table entity_regimes is
  'Assujettissement d''une entité à un régime — un fait sourcé et daté, comme une evidence.';

alter table disclosure_regimes enable row level security;
alter table indicator_regimes  enable row level security;
alter table entity_regimes     enable row level security;
create policy "public read" on disclosure_regimes for select using (true);
create policy "public read" on indicator_regimes  for select using (true);
create policy "public read" on entity_regimes     for select using (true);

-- --- Régimes (périmètre de départ : FR + UE, priorité verticale banque) ------
insert into disclosure_regimes (code, name, jurisdiction, legal_basis, scope, url, in_force_since) values
  ('FR_EGAPRO', 'Index de l''égalité professionnelle femmes-hommes', 'FR',
   'Code du travail, art. L1142-8 et D1142-4 (loi n° 2018-771 du 5 septembre 2018)',
   'Entreprises d''au moins 50 salariés : publication annuelle de l''index et de ses indicateurs, au plus tard le 1er mars, et sur le site du ministère du Travail.',
   'https://egapro.travail.gouv.fr/', '2020-03-01'),
  ('EU_CRD_CBCR', 'Déclaration pays par pays des établissements de crédit', 'UE',
   'Directive 2013/36/UE (CRD IV), art. 89 ; Code monétaire et financier, art. L511-45 ; décret n° 2014-1657',
   'Établissements de crédit, compagnies financières holding et entreprises d''investissement : publication annuelle, par pays d''implantation, de l''activité, du produit net bancaire, des effectifs, du résultat avant impôt, de l''impôt et des subventions publiques reçues.',
   'https://eur-lex.europa.eu/eli/dir/2013/36/oj', '2015-01-01'),
  ('EU_CSRD_W1', 'Rapport de durabilité CSRD — première vague', 'UE',
   'Directive (UE) 2022/2464 (CSRD) et normes ESRS (règlement délégué (UE) 2023/2772) ; ordonnance n° 2023-1142 du 6 décembre 2023',
   'Grandes entités d''intérêt public de plus de 500 salariés (ex-périmètre NFRD), exercices ouverts dès le 1er janvier 2024. Les filiales couvertes par le rapport consolidé de leur société mère en sont exemptées. Hors ESRS 2, les points de données dépendent de l''analyse de double matérialité.',
   'https://eur-lex.europa.eu/eli/dir/2022/2464/oj', '2025-01-01'),
  ('FR_VIGILANCE', 'Plan de vigilance', 'FR',
   'Loi n° 2017-399 du 27 mars 2017 ; Code de commerce, art. L225-102-4',
   'Sociétés employant, à la clôture de deux exercices consécutifs, au moins 5 000 salariés (avec leurs filiales françaises) ou 10 000 (avec leurs filiales dans le monde) : plan et compte rendu de mise en œuvre publiés dans le rapport de gestion.',
   'https://www.legifrance.gouv.fr/eli/loi/2017/3/27/2017-399/jo/texte', '2018-01-01'),
  ('FR_COPE_ZIMMERMANN', 'Mixité des conseils d''administration', 'FR',
   'Loi n° 2011-103 du 27 janvier 2011 ; Code de commerce, art. L225-18-1',
   'Sociétés cotées, et sociétés de plus de 250 salariés et 50 M€ de chiffre d''affaires : au moins 40 % de chaque sexe au conseil ; composition publiée.',
   'https://www.legifrance.gouv.fr/eli/loi/2011/1/27/2011-103/jo/texte', '2017-01-01');

insert into indicator_regimes (indicator_id, regime_id, note)
select i.id, r.id, v.note
from (values
  ('LAB_EGAPRO_INDEX',     'FR_EGAPRO',          'Note globale de l''index.'),
  ('TAX_CBCR_PUBLISHED',   'EU_CRD_CBCR',        'Déclaration pays par pays publique.'),
  ('TAX_EFFECTIVE_RATE',   'EU_CRD_CBCR',        'Impôt et résultat avant impôt publiés par pays.'),
  ('GOV_BOARD_GENDER',     'EU_CSRD_W1',         'ESRS 2 GOV-1 (hors matérialité).'),
  ('GOV_BOARD_INDEP',      'EU_CSRD_W1',         'ESRS 2 GOV-1 (hors matérialité).'),
  ('ENV_SCOPE3_DISCLOSED', 'EU_CSRD_W1',         'ESRS E1-6 (sous réserve de matérialité du climat).'),
  ('ENV_GHG_INTENSITY',    'EU_CSRD_W1',         'ESRS E1-6, intensité par chiffre d''affaires net.'),
  ('LAB_GENDER_PAYGAP',    'EU_CSRD_W1',         'ESRS S1-16 (sous réserve de matérialité).'),
  ('LAB_CEO_PAY_RATIO',    'EU_CSRD_W1',         'ESRS S1-16, ratio de rémunération totale annuelle.'),
  ('SUP_VIGILANCE_PLAN',   'FR_VIGILANCE',       'Plan publié dans le rapport de gestion.'),
  ('GOV_BOARD_GENDER',     'FR_COPE_ZIMMERMANN', 'Composition du conseil.')
) as v(ind, reg, note)
join indicators i on i.code = v.ind
join disclosure_regimes r on r.code = v.reg;

-- --- Fonction d'entrée du moteur ---------------------------------------------
-- Changements v0.5 : evidence PROPRE à l'entité uniquement (plus d'héritage du
-- groupe) ; chaque indicateur applicable porte `mandatory` + les régimes qui
-- l'imposent à cette entité.
create or replace function compute_score_input(p_slug text, p_profile text default 'equilibre')
returns jsonb
language sql
stable
set search_path = public
as $$
with recursive chain as (
  select id, parent_id, 0 as depth, sector_id, slug, coalesce(display_name, legal_name) as name
  from entities where slug = p_slug
  union all
  select e.id, e.parent_id, c.depth+1, e.sector_id, e.slug, coalesce(e.display_name, e.legal_name)
  from entities e join chain c on e.id = c.parent_id
),
me as (select * from chain where depth = 0),
me_animal as (
  select coalesce((select s.animal_relevant from sectors s where s.id = (select sector_id from me)), true) as animal_relevant
),
me_wap as (
  select coalesce((select s.plastic_relevant from sectors s where s.id = (select sector_id from me)), false) as plastic_relevant,
         coalesce((select s.water_relevant   from sectors s where s.id = (select sector_id from me)), false) as water_relevant
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
  select i.id, i.code, i.name, i.unit, d.code as dimension_code, i.kind, i.direction, i.weight,
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
),
ev as (
  select a.code as indicator_code, s.tier, e.nature, e.normalized_value, e.value_numeric,
         e.confidence, e.observed_on, 0 as specificity, e.contested, s.code as source_code,
         coalesce(e.source_url, s.url) as source_url
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
      'mandatory', mandatory, 'mandatory_regimes', mandatory_regimes)), '[]') from appl),
  'evidence', (select coalesce(jsonb_agg(jsonb_build_object(
      'indicator_code', indicator_code, 'tier', tier, 'nature', nature, 'normalized_value', normalized_value,
      'value_numeric', value_numeric, 'confidence', confidence, 'observed_on', observed_on,
      'specificity', specificity, 'contested', contested, 'source_code', source_code, 'source_url', source_url)), '[]') from ev),
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
  'Entrées du moteur (v0.5) : evidence propre à l''entité (sans héritage du groupe), indicateurs applicables avec leur caractère obligatoire (Règle 1).';
