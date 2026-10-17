-- Pertinence des piliers par secteur (17/10/2026). Le secteur « Distribution & Retail » a été créé en
-- juillet pour l'e-commerce généraliste, sans enjeu animal, plastique ni eau ; les enseignes alimentaires
-- y ont été rangées depuis (Carrefour, Casino, E.Leclerc, Lidl, Système U, Auchan, Picard…). Résultat :
-- leurs preuves vérifiées (classement BBFAW, qui note explicitement les distributeurs, offre végétale,
-- standards d'abattage, fourrure, emballages, eau) étaient masquées. Les trois piliers sont rendus
-- applicables à la distribution.
update sectors set animal_relevant = true, plastic_relevant = true, water_relevant = true
 where code = 'retail_distribution';
-- Eau : les groupes de la tech, de l'équipement de la maison et du jouet répondent au questionnaire eau
-- du CDP (18, 6 et 2 notes publiées) et SEB publie son intensité en eau ; le pilier leur est rendu applicable.
update sectors set water_relevant = true
 where code in ('tech_electronics', 'household_durables', 'toys_games');
