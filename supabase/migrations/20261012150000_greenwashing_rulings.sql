-- =============================================================================
-- Allégations environnementales trompeuses relevées par une autorité (v0.7.1)
-- -----------------------------------------------------------------------------
-- Indicateur d'impact de la mode approuvé par l'éditeur (11/10/2026) : une
-- entreprise sanctionnée, ou contrainte de retirer ses allégations après
-- enquête d'une autorité de protection des consommateurs, a trompé ses clients
-- sur l'environnement. Seules comptent les décisions officielles (communiqué de
-- l'autorité, cité mot pour mot). Controverse : sévérité 0,8 pour une amende,
-- 0,5 pour des engagements obtenus après enquête sans sanction. Indicateur de
-- groupe et complémentaire (une entreprise jamais épinglée n'est pas pénalisée).
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('CONSUMER_AUTHORITY', 'Autorité de protection des consommateurs', 'regulatory', 'Autorités nationales (UE)', null,
   'Décision ou communiqué officiel d''une autorité de protection des consommateurs (ACM aux Pays-Bas, AGCM en Italie, DGCCRF en France…).')
on conflict (code) do nothing;

insert into indicators (code, dimension_id, name, kind, direction, sector_specific, applies_to_sector_id, weight, unit,
                        methodology, presence_only, jurisdiction, complementary, group_level, disclosure)
select 'ENV_GREENWASHING', d.id, 'Allégations environnementales trompeuses (décision d''une autorité)', 'categorical',
       'higher_better', false, null, 1, 'controverse',
       'Décision officielle d''une autorité de protection des consommateurs : amende pour allégations environnementales trompeuses = sévérité 0,8 ; engagements de retrait obtenus après enquête, sans sanction = 0,5. Absent : non pénalisé.',
       false, null, true, true, false
from dimensions d where d.code = 'ENV'
on conflict (code) do nothing;
