-- Lot 216 : Monin (scan d'un lecteur, relevé des scans non reconnus). Le site refuse le vérificateur
-- (erreur 530 deux fois) : mentions légales copiées par l'éditeur de l'Index le 17/10/2026
-- (pipeline/curated/copies/monin_mentions-legales_2026-10-17.txt), contrôlées mot pour mot.
-- Georges Monin SAS (Bourges) ; SIREN vérifié dans l'annuaire officiel des entreprises le 17/10/2026
-- (573721370, active, APE 11.07B).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'georges-monin', 'GEORGES MONIN SAS', 'Georges Monin', null, '573721370', 'FR', s.id, false
from sectors s where s.code = 'beverages'
on conflict (slug) do nothing;
