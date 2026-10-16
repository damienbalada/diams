-- Lot 113 : l'ancienne preuve en attente de Fendi (rapport de LVMH, « maroquinerie » sans nommer la
-- matière) est remplacée par la page Fendi du site officiel de LVMH, qui parle de fourrure (approuvée,
-- vérifiée mot pour mot). L'ancienne ligne est écartée.
update evidence ev set review_status = 'rejected'
from entities en, indicators i
where en.id = ev.entity_id and i.id = ev.indicator_id and en.slug = 'fendi' and i.code = 'ANI_EXPLOITATION'
  and ev.review_status = 'pending' and ev.excerpt like '%Fendi est propriétaire en Italie de ses sites de production%';
