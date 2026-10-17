-- Point 8 du rapport de nuit (17/10/2026) : la Brasserie Lancelot (SIREN 950 471 177) rejoint Agrial.
-- La presse l'affirmait depuis 2021 ; la preuve retenue est officielle : une actualité du site d'Agrial
-- (rubrique Boissons, 11/09/2025) où la coopérative présente la gamme de la brasserie comme ses propres
-- références. Concordant : le directeur général de la brasserie (répertoire officiel des entreprises,
-- annuaire de l'État) est celui de la branche boissons d'Agrial (communiqué du site d'Agrial). La marque
-- Lancelot était déjà rattachée à Agrial (page « Nos marques »).
update entities set parent_id = (select id from entities where slug = 'agrial')
where slug = 'brasserie-lancelot' and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer, checked_on, check_result, check_detail)
select b.id, a.id,
       'https://www.agrial.com/la-brasserie-lancelot-rejoint-le-mouvement-du-reemploi/',
       'Actualité du site officiel d''Agrial « La Brasserie Lancelot rejoint le mouvement du réemploi ! » (rubrique Boissons, 11/09/2025), où la coopérative présente la gamme de la brasserie comme la sienne : « Nous sommes fiers d’annoncer que la Brasserie Lancelot s’engage activement dans le réemploi des emballages » ; « Vous pouvez retrouver nos références Duchesse Anne Triple, Blanche Hermine et Morgane dans des bouteilles réemployables et standardisées RCOEUR 75cl, dans les enseignes partenaires ».',
       '2026-10-17', 'delegue-editeur:verifie-mot-pour-mot', '2026-10-17', 'confirmee', 'citations retrouvées mot pour mot sur la page (17/10/2026)'
from entities b, entities a
where b.slug = 'brasserie-lancelot' and a.slug = 'agrial'
  and not exists (select 1 from entity_ownership_sources s where s.entity_id = b.id and s.owner_id = a.id);
