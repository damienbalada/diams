-- Coty, mixité du conseil (preuve en attente) : citation allongée pour inclure le
-- contexte « our Board’s overall composition » exigé par le contrôle mot pour mot.
update evidence e
   set excerpt = 'Circulaire de procuration de Coty déposée à la SEC le 2026-09-24 (en anglais), composition des candidats au conseil : « important to our Board’s overall composition and functioning. Average Age Gender Average Tenure Refreshment 57 44% ~ 1 77% years years 4/9 are women » ; calcul : 4 / 9 = 44,4 %.',
       updated_at = now()
 where e.entity_id = (select id from entities where slug = 'coty')
   and e.indicator_id = (select id from indicators where code = 'GOV_BOARD_GENDER')
   and e.observed_on = '2026-09-24'
   and e.review_status = 'pending';
