-- SEB, intensité en eau : l'extrait ne disait pas qu'il s'agit de l'eau consommée (ESRS E3-4 § 29) ;
-- complété par la ligne de consommation du même tableau, vérifiée mot pour mot (lot 180, 17/10/2026).
update evidence set excerpt = 'Rapport financier annuel 2025 du Groupe SEB (ESEF), état de durabilité, ESRS E3-4 (consommation d''eau rapportée au chiffre d''affaires ; colonnes 2025, 2024, 2023 puis variation 2025/2024) : « Quantité totale d’eau consommée (C = A-B) 724 953 1 049 » ; « Water Intensity Ratio ( m 3 /M€) 89 115 131 - 23 % » — 89 m³ d''eau consommés par million d''euros de chiffre d''affaires en 2025.'
 where review_status = 'approved'
   and indicator_id = (select id from indicators where code = 'WAT_INTENSITY')
   and entity_id = (select id from entities where slug = 'seb')
   and excerpt like '%Water Intensity Ratio ( m 3 /M€) 89 115 131%';
