-- Décision de l'éditeur (15/10/2026) : le pilier bien-être animal se lit à trois niveaux.
--   groupe  : résumé de ses marques suivies (exploitation documentée, entièrement végétales…),
--             calculé sur la fiche, chaque marque renvoyant à sa propre fiche ;
--   marque  : ANI_EXPLOITATION (un seul produit d'origine animale suffit) ou ANI_ANIMAL_FREE
--             (une page officielle dit que TOUTE la marque est végétale) ;
--   produit : ANI_OFFRE_VEGETALE, nouveau : la marque propose des produits 100 % végétaux, sans
--             que cela rende la marque entière végétale. Information affichée, jamais un mérite.
insert into indicators (code, dimension_id, name, kind, direction, sector_specific, weight, unit, methodology, presence_only)
select 'ANI_OFFRE_VEGETALE', d.id, 'Produits 100 % végétaux proposés', 'binary', 'higher_better', false, 0, null,
       'Niveau produit : la marque présente au moins un produit comme 100 % végétal ou vegan sur son site officiel. Ne fait pas de la marque une marque végétale (ANI_ANIMAL_FREE).',
       false
from dimensions d where d.code = 'ANI'
on conflict (code) do nothing;

update indicators set name = 'Marque entièrement végétale',
       methodology = 'Niveau marque : une page officielle affirme que toute la gamme de la marque est sans ingrédient ni matière d''origine animale. Un seul produit végétal ne suffit pas (voir ANI_OFFRE_VEGETALE).'
where code = 'ANI_ANIMAL_FREE';
