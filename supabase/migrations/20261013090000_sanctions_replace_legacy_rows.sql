-- =============================================================================
-- Sanctions : deux décisions du lot 31 (Apple 1,8 Md€, Meta 1,2 Md€) ont la même
-- clé (entité, indicateur, source, date) que deux anciennes lignes retirées par
-- 20261012180000. Elles sont réécrites sur place avec le contenu du lot vérifié
-- (curated/groupes_2026-10_lot31_sanctions.csv), remises en attente : seule la
-- vérification mot pour mot (verify_curated --apply) les approuve ensuite.
-- Généré depuis le fichier du lot, sans retouche.
-- =============================================================================

update evidence e set value_type = 'category', value_numeric = null, value_boolean = null,
  value_text = 'amende de plus de 1,8 Md€ (abus de position dominante)', normalized_value = 0.9, nature = 'controversy',
  confidence = 0.95, source_url = 'https://ec.europa.eu/commission/presscorner/detail/en/ip_24_1161',
  excerpt = 'Commission européenne, communiqué IP/24/1161 du 04/03/2024 (en anglais) : « The European Commission has fined Apple over €1.8 billion for abusing its dominant position on the market for the distribution of music streaming apps » — abus de position dominante (règles de l''App Store pour les services de musique en ligne) ; amende de plus de 1,8 Md€ (sévérité 0,9).',
  review_status = 'pending', reviewer = 'ai:lot31-sanctions', contested = false
from entities en, indicators i, sources s
where en.id = e.entity_id and i.id = e.indicator_id and s.id = e.source_id
  and en.slug = 'apple' and i.code = 'GOV_SANCTIONS' and s.code = 'EU_COMPETITION'
  and e.observed_on = date '2024-03-04';

update evidence e set value_type = 'category', value_numeric = null, value_boolean = null,
  value_text = 'amende de 1,2 Md€ (protection des données personnelles)', normalized_value = 0.9, nature = 'controversy',
  confidence = 0.95, source_url = 'https://www.dataprotection.ie/en/news-media/press-releases/Data-Protection-Commission-announces-conclusion-of-inquiry-into-Meta-Ireland',
  excerpt = 'Commission irlandaise de protection des données (DPC), communiqué du 22/05/2023 (en anglais) : « requiring Meta Ireland to suspend any future transfer of personal data to the US » ; « an administrative fine in the amount of €1.2 billion » — transferts de données personnelles vers les États-Unis contraires au règlement général sur la protection des données ; amende de 1,2 Md€ (sévérité 0,9).',
  review_status = 'pending', reviewer = 'ai:lot31-sanctions', contested = false
from entities en, indicators i, sources s
where en.id = e.entity_id and i.id = e.indicator_id and s.id = e.source_id
  and en.slug = 'meta' and i.code = 'GOV_SANCTIONS' and s.code = 'GDPR_DPA'
  and e.observed_on = date '2023-05-22';
