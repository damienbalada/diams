-- Doublons de marques sous un même propriétaire, repérés le 14/10/2026 (aucune preuve de
-- notation ni entité rattachée) : on garde la fiche la plus ancienne. Les preuves
-- d'appartenance des copies disparaissent avec elles (suppression en cascade).
--   Paysan Breton (Laïta), Malo (SILL Entreprises), St Michel : recréées par le lot 85 ;
--   Valfleuri, Sains et Saufs : recréées par le lot 82 ;
--   Pastilles Vichy (Carambar & Co) : saisie deux fois le 13/10/2026 (lots 24 et 34).
delete from entities
 where is_brand
   and slug in ('paysan-breton-marque', 'malo-marque', 'st-michel-marque', 'valfleuri-marque',
                'sains-et-saufs-marque', 'pastilles-vichy');
