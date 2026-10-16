-- Jugements de la Cour fédérale d'Australie (Google, 2022 FCA 942 ; Samsung, 2022 FCA 875) : le site de la
-- Cour refuse le vérificateur automatique, mais une seconde requête, sous la même identité déclarée, a
-- obtenu les deux jugements le 17/10/2026. Les citations y figurent mot pour mot (« being penalties
-- cumulatively totalling $60 million for the said » ; « pecuniary penalties of $14 million, pursuant to
-- section 224 of the ACL ») et la gravité (0,5, moins de 100 M€ au taux BCE 2022) est conforme : approbation
-- par délégation de l'éditeur, trace écrite dans le relecteur.
update evidence ev set review_status = 'approved', reviewer = 'delegue-editeur:verifie-mot-pour-mot-copie-2026-10-17'
from indicators i, entities e, sources s
where ev.indicator_id = i.id and ev.entity_id = e.id and ev.source_id = s.id
  and s.code = 'AU_FEDERAL_COURT' and i.code = 'GOV_SANCTIONS' and ev.review_status = 'pending'
  and e.slug in ('google', 'samsung');
