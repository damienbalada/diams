-- =============================================================================
-- Statuts en français dans les extraits (SBTi, KSE « Leave Russia »)
-- -----------------------------------------------------------------------------
-- Les extraits reprenaient les statuts anglais des sources (« Validated
-- Targets », « Suspension »…). Le résumé de la fiche les affichait tels quels.
-- Ils sont traduits ; la valeur brute (value_text) garde le statut d'origine.
-- Correctif : la migration précédente avait aussi réécrit l'extrait des deux
-- engagements retirés comme s'ils étaient des objectifs validés.
-- =============================================================================

-- SBTi : engagements retirés (fait, pas promesse)
update evidence e set excerpt = replace(e.excerpt,
    '(objectif validé par la SBTi : un engagement sur l''avenir, pas un résultat).', '(un fait : l''engagement a été retiré).')
from indicators i
where i.id = e.indicator_id and i.code = 'ENV_SBTI_VALIDATED' and e.excerpt like '%Commitment Removed%';

-- SBTi : statuts et classifications
update evidence e set excerpt =
  replace(replace(replace(replace(replace(replace(e.excerpt,
    'objectif de court terme : Validated Targets', 'objectif de court terme validé'),
    'objectif de court terme : Commitment to Set Targets', 'objectif de court terme : engagement à en fixer un'),
    'objectif de court terme : Commitment Removed', 'objectif de court terme : engagement retiré'),
    'Well-below 2°C', 'bien en dessous de 2 °C'),
    '1.5°C', '1,5 °C'),
    '(2°C', '(2 °C')
from indicators i
where i.id = e.indicator_id and i.code = 'ENV_SBTI_VALIDATED';

-- KSE « Leave Russia » : le statut en français seulement
update evidence e set excerpt =
  replace(replace(replace(replace(replace(replace(e.excerpt,
    '— Exit Completed (sortie effective)', '— sortie effective'),
    '— Withdrawal (sortie annoncée, en cours)', '— sortie annoncée, en cours'),
    '— Suspension (activité suspendue)', '— activité suspendue'),
    '— Scaling Back (activité réduite)', '— activité réduite'),
    '— Pausing Investments (investissements gelés, activité maintenue)', '— investissements gelés, activité maintenue'),
    '— Continue Operations (activité poursuivie en Russie)', '— activité poursuivie en Russie')
from indicators i
where i.id = e.indicator_id and i.code = 'GEO_RUSSIA_EXIT' and e.reviewer = 'auto:import_kse';
