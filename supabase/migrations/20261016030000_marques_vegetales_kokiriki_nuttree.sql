-- Lot 112 : deux marques entièrement végétales, preuve approuvée (vérifiée mot pour mot) sur leur
-- site officiel prouvé : Kokiriki (« Large gamme 100% végétale … ») et Nuttree (« OUI ! ET
-- TOUJOURS BIO, VEGAN & SANS GLUTEN. »). Jamais animal_free sans preuve.
update entities set animal_free = true
where slug in ('kokiriki-marque', 'nuttree-marque')
  and exists (select 1 from evidence_active ev join indicators i on i.id = ev.indicator_id
              where ev.entity_id = entities.id and i.code = 'ANI_ANIMAL_FREE');
