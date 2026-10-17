-- Lot 213 : Pyrex (décision de l'éditeur du 17/10/2026 : afficher les deux sociétés).
-- La marque appartient à Corning Incorporated et est exploitée sous licence en Europe par International
-- Cookware (Châteauroux), qui fabrique et vend les produits : c'est elle qui reçoit l'argent des achats.
-- Pyrex est donc rattachée à International Cookware ; la preuve d'appartenance, affichée sur la fiche,
-- cite la phrase du site officiel qui nomme les deux sociétés.
-- SIREN vérifié dans l'annuaire officiel des entreprises le 17/10/2026 (399311315, active, APE 23.13Z).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'international-cookware', 'INTERNATIONAL COOKWARE', 'International Cookware (licence Pyrex de Corning)',
       null, '399311315', 'FR', s.id, false
from sectors s where s.code = 'household_durables'
on conflict (slug) do nothing;
