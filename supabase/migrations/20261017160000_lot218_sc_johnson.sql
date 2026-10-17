-- Lot 218 : SC Johnson (relevé des scans non reconnus : Canard WC) et marques U. Les sites refusent le
-- vérificateur (scjohnson.com : 429 deux fois ; magasins-u.com : 403 deux fois) : pages enregistrées par
-- l'éditeur de l'Index le 17/10/2026 (pipeline/curated/copies/), contrôlées mot pour mot.
-- S.C. Johnson & Son, Inc. (Racine, Wisconsin), société familiale non cotée, nommée en pied de la page
-- « Nos marques » de son site (« © 2026 S.C. Johnson & Son, Inc. ») ; aucun LEI dans le registre GLEIF
-- pour la société mère (vérifié le 17/10/2026) ; filiale française SC Johnson SAS, SIREN 548274042
-- (annuaire officiel, active), non rattachée faute de lien de contrôle publié.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'sc-johnson', 'S.C. Johnson & Son, Inc.', 'SC Johnson', null, null, 'US', s.id, false
from sectors s where s.code = 'home_care'
on conflict (slug) do nothing;
