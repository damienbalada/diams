-- Même règle que 20261015220000 : deux preuves de Mondelēz (évolution des émissions, plastique
-- vierge) importées en doublon d'une preuve antérieure approuvée ; la nouvelle est écartée.
update evidence n
set review_status = 'rejected', reviewer = 'remplace:doublon-lot100', updated_at = now()
where n.review_status = 'approved'
  and n.created_at::date = date '2026-10-15'
  and n.reviewer in ('auto:verify_curated', 'delegue-editeur:verifie-mot-pour-mot')
  and exists (select 1 from evidence o
              where o.entity_id = n.entity_id and o.indicator_id = n.indicator_id and o.id <> n.id
                and o.review_status = 'approved' and o.created_at::date < date '2026-10-15');
