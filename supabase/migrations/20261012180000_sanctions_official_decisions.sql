-- =============================================================================
-- Sanctions : seulement des décisions officielles, notées par leur gravité
-- -----------------------------------------------------------------------------
-- GOV_SANCTIONS n'avait aucune preuve publiée : les quelques lignes saisies à la
-- main citaient la presse (CNBC, BHRRC) ou une page d'accueil, et un montant
-- était faux (Google : 90 M€ au lieu de 150 M€). Elles sont retirées.
-- L'indicateur devient une controverse : décision officielle d'une autorité
-- (concurrence, marchés numériques, données personnelles, consommateurs) de moins
-- de 5 ans, citée mot pour mot depuis le communiqué de l'autorité.
--   amende d'au moins 1 Md€ ............ sévérité 0,9
--   de 100 M€ à 1 Md€ .................. 0,7
--   moins de 100 M€ .................... 0,5
-- Indicateur de groupe et complémentaire : une entreprise jamais sanctionnée
-- n'est pas pénalisée ; plusieurs décisions : la plus grave compte.
-- =============================================================================

update indicators set kind = 'categorical', direction = 'higher_better', unit = 'controverse',
  name = 'Sanctions d''une autorité (concurrence, données personnelles, consommateurs)',
  methodology = 'Décision officielle d''une autorité de moins de 5 ans (concurrence, marchés numériques, données personnelles, consommateurs) : amende d''au moins 1 Md€ = sévérité 0,9 ; de 100 M€ à 1 Md€ = 0,7 ; moins de 100 M€ = 0,5. Plusieurs décisions : la plus grave compte. Absent : non pénalisé.'
where code = 'GOV_SANCTIONS';

update evidence e set review_status = 'rejected', reviewer = 'remplace:decisions-officielles-2026-10-12'
from indicators i
where i.id = e.indicator_id and i.code = 'GOV_SANCTIONS' and e.review_status = 'pending';
