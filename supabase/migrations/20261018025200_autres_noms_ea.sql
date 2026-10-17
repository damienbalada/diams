-- Autre nom (18/10/2026) : « EA Sports » est la gamme sportive d'Electronic Arts (site officiel ea.com) ;
-- rapprochement des produits scannés.
update entities set aliases = array['EA Sports'] where slug = 'electronic-arts' and aliases is null;
