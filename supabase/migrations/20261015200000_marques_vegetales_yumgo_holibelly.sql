-- Lot 99 (pilier animal à trois niveaux) : deux marques dont le site officiel (identifié par le
-- SIREN du propriétaire dans ses mentions légales) affirme que TOUTE la marque est végétale :
--   Yumgo     : « Tous les produits Yumgo sont 100% végétaux et sans exploitation animale. »
--   Holibelly : « Oui Holibelly est 100% végétal »
-- Preuves ANI_ANIMAL_FREE vérifiées mot pour mot (delegue-editeur:verifie-mot-pour-mot) ; aucune
-- exploitation animale documentée pour ces marques. Le drapeau fait lire leur pilier comme celui
-- d'une marque végétale (compute_score_input).
update entities set animal_free = true, updated_at = now() where slug in ('yumgo', 'holibelly-marque') and is_brand;
