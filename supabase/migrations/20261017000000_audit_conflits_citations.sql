-- Audit des preuves sans citation (17/10/2026), indicateur « implication dans un conflit ou une occupation ».
-- 1. McDonald's : le résumé rédigé est remplacé par la citation exacte du BHRRC (allégation signalée le
--    03/11/2023, relevée par le centre ; le rachat du franchisé par McDonald's Corp en 2024 reste mentionné).
update evidence ev set
  excerpt = 'Business & Human Rights Resource Centre, suivi des territoires palestiniens occupés (en anglais), allégation signalée le 03/11/2023 : « McDonald''s'' Israel-based franchise allegedly stated it had given away thousands of free meals to members of the Israeli military amid Israel''s assault on Gaza » — allégation relayée par le centre ; McDonald''s Corp a racheté ce franchisé en 2024.',
  observed_on = '2023-11-03', reviewer = 'revue-manuelle:citation-verifiee-2026-10-17'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and i.code = 'GEO_CONFLICT_TIES' and e.slug = 'mcdonalds'
  and ev.excerpt like 'Le franchisé israélien de McDonald''s%';
-- 2. Starbucks : un procès contre son syndicat après un message de soutien à la Palestine relève d'un
--    conflit social, pas d'une implication dans un conflit armé ou une occupation : retiré du champ.
update evidence ev set review_status = 'rejected', reviewer = 'retire:hors-champ-conflit-social-2026-10-17'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and i.code = 'GEO_CONFLICT_TIES' and e.slug = 'starbucks'
  and ev.excerpt like 'Starbucks a poursuivi en justice son syndicat%';
