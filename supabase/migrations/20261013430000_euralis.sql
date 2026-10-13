-- Euralis, coopérative agricole et agroalimentaire du Sud-Ouest (foie gras Maison Montfort
-- et Rougié, traiteur Stalaven…), d'après son site officiel euralis.fr. SIREN vérifié dans
-- l'annuaire officiel des entreprises (Euralis Coop, Lescar) et LEI dans le registre GLEIF
-- le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'euralis', 'Euralis Coop', 'Euralis', '213800RUV6IMHG4CNE89', '775637861', 'FR', s.id, false
from sectors s where s.code = 'food'
on conflict (slug) do nothing;
