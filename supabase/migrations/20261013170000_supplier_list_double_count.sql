-- =============================================================================
-- Liste des fournisseurs de H&M : retirée (double compte de la transparence)
-- -----------------------------------------------------------------------------
-- La publication de la liste des usines est déjà évaluée, pour toutes les
-- grandes marques de mode, par l'indice de transparence de la mode (Fashion
-- Transparency Index, section traçabilité). La compter une seconde fois, et pour
-- H&M seul (aucun concurrent relevé), ferait gagner 5 points à H&M pour de la
-- transparence, quand la v0.7.0 a recentré la mode sur l'impact. La preuve, exacte,
-- est conservée en base, retirée de la note.
-- =============================================================================

update evidence e set review_status = 'rejected', reviewer = 'retire:double-compte-indice-transparence-2026-10-13'
from entities en, indicators i
where en.id = e.entity_id and i.id = e.indicator_id
  and en.slug = 'hm-group' and i.code = 'SUP_SUPPLIER_LIST' and e.review_status = 'approved';

update indicators set methodology = 'Liste des sites de production publiée (oui/non). Hors mode et luxe : dans ces secteurs, la publication des fournisseurs est déjà évaluée par l''indice de transparence de la mode (Fashion Transparency Index) ; elle n''est pas comptée deux fois.'
where code = 'SUP_SUPPLIER_LIST';
