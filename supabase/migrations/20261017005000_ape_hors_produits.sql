-- Exploitation animale lue dans le code APE du propriétaire (17/10/2026) : la règle étend l'activité
-- principale d'une société à toutes ses marques. Elle se trompe quand la marque vend autre chose que
-- l'activité principale : Sojasun et Sojade (soja, Olga, « lait liquide »), Tablée Végétale (plats
-- végétaux, Madrange, « produits à base de viande »), Materne, Pom'Potes, Confipote et Récré O'lé
-- (compotes et confitures, Groupe Bel, « fromage ») ; et pour la spiruline, une algue classée en
-- aquaculture (Miraculine, Spirales de Lux, sociétés et marques). Deux marques dont les produits n'ont
-- pas pu être confirmés (Légumes & vous, Le Petit Vert) sont retirées par prudence. Les fiches reviennent
-- à l'état présumé, signalé comme tel.
update evidence ev set review_status = 'rejected', reviewer = 'retire:ape-hors-produits-2026-10-17'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and i.code = 'ANI_EXPLOITATION'
  and ev.review_status = 'approved' and ev.reviewer = 'auto:ani_ape'
  and e.slug in ('sojasun', 'sojade', 'tablee-vegetale', 'materne', 'pompotes', 'confipote', 'recre-o-le',
                 'miraculine-spiruline-de-l-est', 'earl-miraculine', 'spirales-de-lux', 'spirales-de-lux-marque',
                 'legumes-et-vous', 'le-petit-vert');
