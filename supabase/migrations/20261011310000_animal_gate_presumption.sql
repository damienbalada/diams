-- =============================================================================
-- Règle ANI rétablie : exploitation animale supposée dans la mode et le luxe
-- tant qu'elle n'est pas exclue (v0.6.1)
-- -----------------------------------------------------------------------------
-- La méthodologie (Règle ANI) dit : niveau d'exploitation inconnu dans la mode =
-- plafond 0,40 (« anti-opacité »). Depuis v0.6.0, un pilier sans aucune preuve
-- n'était plus noté : une enseigne sans label échappait au pilier animal, quand
-- celle qui avait le label « sans fourrure » y était plafonnée à 40 — le label
-- faisait baisser la note (H&M Group A, la marque H&M B). Le moteur applique de
-- nouveau le plafond par défaut dès que l'indicateur-gate concerne l'entité ; la
-- fiabilité du pilier reste nulle tant que le niveau n'est pas documenté.
--
-- 1. L'indicateur-gate et le label « sans fourrure » concernent aussi les
--    groupes de luxe (cuirs, peaux exotiques, fourrure) : jusqu'ici réservés au
--    secteur « mode et maroquinerie », ils ignoraient Hermès, Kering, LVMH, dont
--    le niveau est pourtant documenté (lot 15, documents déposés à l'AMF).
-- 2. Ces trois preuves (et la ligne Chanel en attente) portaient un plafond de 0,
--    hors du barème publié : cuir et peaux au cœur de l'activité = « extensive »
--    = 0,40. Alignées sur le barème.
-- =============================================================================

insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id
from indicators i cross join sectors s
where i.code in ('ANI_EXPLOITATION', 'ANI_FUR_FREE')
  and s.code in ('fashion_leather', 'luxury_group')
on conflict do nothing;

update evidence e set normalized_value = 0.4
from indicators i
where i.id = e.indicator_id and i.code = 'ANI_EXPLOITATION'
  and e.normalized_value = 0
  and e.value_text in ('cuirs et cuirs exotiques ; élevage de crocodiliens',
                       'cuirs exotiques et fourrures achetés ; fermes de crocodiliens',
                       'peaux précieuses (fourrure arrêtée)',
                       'Cuir');
