-- Règle 3 (« un objectif, même validé, est une promesse ») appliquée aux matières animales de la mode
-- (17/10/2026) : les objectifs 2026 de LVMH (duvet, laine, peaux exotiques, cuir) et les objectifs de
-- traçabilité et de certification du cuir d'Hermès passent de « politique » à « engagement » ; la
-- certification RDS déjà acquise des ateliers de duvet de Fast Retailing et d'Uniqlo (depuis fin 2019)
-- passe de « politique » à « résultat ».
update evidence ev set nature = 'commitment'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and ev.review_status = 'approved'
  and i.code in ('ANI_DOWN_RDS', 'ANI_WOOL_MULESING', 'ANI_EXOTIC_SKINS', 'ANI_LEATHER_TRACE')
  and e.slug in ('lvmh', 'hermes') and ev.nature = 'policy' and ev.value_text ilike 'objectif%';
update evidence ev set nature = 'result'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and ev.review_status = 'approved'
  and i.code = 'ANI_DOWN_RDS' and e.slug in ('fast-retailing', 'uniqlo') and ev.nature = 'policy';
