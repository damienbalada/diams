-- Kellanova (Pringles, Kellogg's hors Amérique du Nord…) appartient à Mars depuis le
-- 11/12/2025 : « Mars Completes Acquisition of Kellanova »,
-- https://www.mars.com/news-and-stories/press-releases-statements/mars-completes-acquisition-of-kellanova
-- Kellanova reste une filiale (ses propres preuves — engagement SBTi, inscription au
-- registre de transparence de l'UE — demeurent les siennes) ; les indicateurs de groupe
-- (conseil, fiscalité, exploitation animale…) relèvent désormais de Mars, et la chaîne
-- de propriété affichée devient Kellogg's → Kellanova → Mars.
update entities
   set parent_id = (select id from entities where slug = 'mars'),
       ownership_pct = 100,
       updated_at = now()
 where slug = 'kellanova'
   and parent_id is null;
