-- =============================================================================
-- Salaire vital chez les fournisseurs : Clean Clothes Campaign (v0.7.0)
-- -----------------------------------------------------------------------------
-- Premier indicateur d'impact de la mode décidé par l'éditeur : le salaire
-- réellement versé dans les usines fournisseurs, tel que le note le collectif
-- Clean Clothes Campaign (Fashion Checker, données ouvertes Wikirate, édition
-- 2026, environ 110 marques). Connecteur : import_fashion_checker.
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('CCC', 'Fashion Checker (salaire vital)', 'audited_ngo', 'Clean Clothes Campaign', 'https://fashionchecker.org',
   'Note A à E du salaire vital versé chez les fournisseurs, d''après ce que publie chaque marque.')
on conflict (code) do nothing;

update indicators set methodology =
  'Clean Clothes Campaign (Fashion Checker) : A = 100 % des usines fournisseurs versent un salaire vital (référence et salaires publiés usine par usine) = 1 ; B plus de 50 % = 0,75 ; C plus de 26 % = 0,5 ; D 1 à 25 % = 0,25 ; E aucun salaire vital versé ni revendiqué = 0. Liste fermée : absent = non évalué.'
where code = 'SUP_LIVING_WAGE';
