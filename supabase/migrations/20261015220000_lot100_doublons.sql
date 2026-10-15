-- Collecte complète, lot 100 (15/10/2026) : huit preuves écrites en doublon d'une preuve déjà
-- approuvée sur la même case (même entité, même indicateur), parce que la liste des manques de
-- ces groupes n'avait pas été recalculée avant l'écriture : Henkel, Lactalis, Mars, Nestlé (2),
-- Savencia (3). Les valeurs sont identiques (Henkel : −8,16 contre −8,21 %/an, deux lectures du
-- même tableau). On garde la preuve antérieure, déjà vérifiée ; la nouvelle est écartée, avec son motif.
update evidence n
set review_status = 'rejected', reviewer = 'remplace:doublon-lot100', updated_at = now()
where n.review_status = 'approved'
  and n.created_at::date = date '2026-10-15'
  and n.reviewer in ('auto:verify_curated', 'delegue-editeur:verifie-mot-pour-mot')
  and exists (select 1 from evidence o
              where o.entity_id = n.entity_id and o.indicator_id = n.indicator_id and o.id <> n.id
                and o.review_status = 'approved' and o.created_at::date < date '2026-10-15');
