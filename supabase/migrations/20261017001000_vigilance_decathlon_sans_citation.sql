-- Plan de vigilance de Decathlon : ligne de départ sans citation (« Plan de vigilance publié »), en attente
-- depuis le 11/10/2026. Aucun plan trouvé le 17/10/2026 (radar du devoir de vigilance, site, recherche web) :
-- ligne rejetée ; la recherche est consignée au journal.
update evidence ev set review_status = 'rejected', reviewer = 'retire:sans-citation-introuvable-2026-10-17'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and i.code = 'SUP_VIGILANCE_PLAN' and e.slug = 'decathlon'
  and ev.review_status = 'pending' and ev.excerpt = 'Plan de vigilance publié (loi française de 2017).';
