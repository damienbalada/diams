-- Contrôle de cohérence des notes (17/10/2026).
-- 1) Part d'emballages recyclés : indicateur classé entre pairs du secteur au calcul ; huit lignes saisies
--    cette nuit portaient une note précalculée (part brute), qui les sortait du classement des 26 autres.
update evidence set normalized_value = null
 where review_status = 'approved'
   and indicator_id = (select id from indicators where code = 'PLA_RECYCLED')
   and normalized_value is not null;
-- 2) Mixité du conseil : barème fixe min(1, part / 50) ; sept lignes des 15 et 16/10 n'avaient pas de note
--    et étaient classées entre pairs à la place.
update evidence set normalized_value = round(least(1, value_numeric / 50)::numeric, 4)
 where review_status = 'approved'
   and indicator_id = (select id from indicators where code = 'GOV_BOARD_GENDER')
   and normalized_value is null and value_numeric is not null;
