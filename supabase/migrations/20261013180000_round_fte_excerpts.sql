-- =============================================================================
-- Registre de transparence de l'UE : équivalents temps plein arrondis
-- -----------------------------------------------------------------------------
-- Le registre publie des nombres en virgule flottante simple précision ; le
-- connecteur les recopiait tels quels (« 8,899999618530273 équivalents temps
-- plein »). Arrondi au centième (8,9), comme le fait désormais le connecteur.
-- Seule l'écriture change ; la valeur notée (coûts déclarés) est inchangée.
-- =============================================================================

with m as (
  select id, (regexp_match(excerpt, '([0-9]+,[0-9]{6,}) équivalents temps plein'))[1] as raw
  from evidence
  where excerpt ~ '[0-9]+,[0-9]{6,} équivalents temps plein'
), r as (
  select id, raw,
         replace(rtrim(rtrim(to_char(round(replace(raw, ',', '.')::numeric, 2), 'FM999999990.00'), '0'), '.'), '.', ',') as rounded
  from m
)
update evidence e set excerpt = replace(e.excerpt, r.raw || ' équivalents temps plein', r.rounded || ' équivalents temps plein')
from r where r.id = e.id;
