-- Retrait de deux sociétés créées par la migration précédente sans marque rattachable :
-- « Aurige » éditait le site d'un homonyme (l'entreprise de construction Jacquet, et non
-- la marque de pain de mie) ; « Green Family » : la marque Love & Green n'est pas citée
-- assez près de la société sur ses mentions légales pour être prouvée. Aucune marque ni
-- preuve ne leur était rattachée.
delete from entities e
where e.slug in ('aurige', 'green-family')
  and not exists (select 1 from entities b where b.parent_id = e.id)
  and not exists (select 1 from evidence v where v.entity_id = e.id);
