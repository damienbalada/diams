-- =============================================================================
-- Relecture complète, vague 6 : preuves d'appartenance à reprendre (4 sur 2 147)
-- -----------------------------------------------------------------------------
-- Loctite → Henkel : la page citée a changé ; nouvelle citation sur la page officielle
--   « Adhesive Technologies » de Henkel.
-- Starwax → Brunel : l'ancienne citation reprenait un bloc de page ; remplacée par les
--   lignes d'identification de l'éditeur dans les mentions légales.
-- La Belle-Iloise → Ets Hilliet : citation inchangée, retrouvée ; l'écart venait de
--   guillemets imbriqués dans l'extrait (outil de relecture).
-- Thiriet → Glaces Thiriet : site momentanément hors ligne (« On revient bientôt ! ») ;
--   société active d'après l'annuaire officiel. À relire plus tard.
-- =============================================================================

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = v.child), (select id from entities where slug = v.owner), v.url, v.excerpt,
       '2026-10-15', 'delegue-editeur:verifie-mot-pour-mot'
from (values
  ('loctite', 'henkel', 'https://www.henkel.com/brands-and-businesses/adhesive-technologies',
   'Page « Adhesive Technologies » du site officiel de Henkel (en anglais) : « For consumers and craftsmen, we focus on the four global brand platforms Pritt, Loctite, Ceresit and Pattex. »'),
  ('starwax', 'brunel', 'https://www.starwax.fr/pages/mentions-legales',
   'Mentions légales du site officiel de la marque Starwax (starwax.fr), éditeur du site : « Dénomination sociale : Brunel Forme juridique : S.A.S. » ; « Numéro de RCS : RCS Lille Métropole B 378 517 148 »')
) as v(child, owner, url, excerpt)
on conflict do nothing;

update entity_ownership_sources o set check_result = 'confirmee', checked_on = '2026-10-15',
       check_detail = 'citation retrouvée mot pour mot (guillemets imbriqués dans l''extrait, relue à la main)'
 where o.entity_id = (select id from entities where slug = 'la-belle-iloise') and o.check_result = 'ecart';

update entity_ownership_sources o set check_result = 'source_inaccessible', checked_on = '2026-10-15',
       check_detail = 'site momentanément hors ligne (« On revient bientôt ! ») ; société active d''après l''annuaire officiel'
 where o.entity_id = (select id from entities where slug = 'thiriet') and o.check_result = 'ecart';

-- Starwax : même page que la preuve existante (clé unique) ; on corrige l'extrait en place.
update entity_ownership_sources set excerpt =
  'Mentions légales du site officiel de la marque Starwax (starwax.fr), éditeur du site : « Dénomination sociale : Brunel Forme juridique : S.A.S. » ; « Numéro de RCS : RCS Lille Métropole B 378 517 148 »',
  check_result = null, check_detail = null
 where entity_id = (select id from entities where slug = 'starwax')
   and source_url = 'https://www.starwax.fr/pages/mentions-legales';
