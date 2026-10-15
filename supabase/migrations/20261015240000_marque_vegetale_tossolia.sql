-- Lot 102 (sites officiels des marques) : Tossolia, dont le site officiel (identifié par les
-- mentions légales du propriétaire) affirme que toute la gamme est végétale :
--   « Découvrez toutes nos gammes 100% végétales »
-- Preuve ANI_ANIMAL_FREE vérifiée mot pour mot (delegue-editeur:verifie-mot-pour-mot) ; aucune
-- exploitation animale documentée pour cette marque.
update entities set animal_free = true, updated_at = now() where slug = 'tossolia-marque' and is_brand;
