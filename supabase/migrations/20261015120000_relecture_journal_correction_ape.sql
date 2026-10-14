-- Journal de relecture, vague 0 : 81 lignes « ecart » consignées à tort pour les preuves
-- d'activité principale (avis de situation Sirene). Le connecteur import_ani_ape ne produit
-- que les preuves encore manquantes : comparer sa sortie aux preuves existantes n'avait pas
-- de sens. Ces lignes sont retirées ; ces preuves sont relues à part, contre l'annuaire
-- officiel des entreprises (code APE à jour).
delete from indicator_reviews
 where reviewer = 'auto:relecture' and wave = 0 and outcome = 'ecart'
   and detail like 'Relecture du connecteur (connecteur import_ani_ape%';
