-- =============================================================================
-- Preuves héritées sans citation ni source primaire : retirées, motif écrit
-- -----------------------------------------------------------------------------
-- Ces lignes, saisies avant la règle « citation mot pour mot », pointent vers une
-- page d'accueil, un article de presse ou un recensement d'ONG non daté. Elles
-- n'ont jamais compté (en attente). Elles sont retirées avec leur motif ; les
-- faits qui peuvent l'être sont repris depuis une source officielle dans des
-- lots vérifiés.
-- =============================================================================

-- Recensements du BHRRC (Centre de ressources entreprises et droits humains) :
-- nombre d'allégations sans période ni méthode de comptage publiées, lien vers la
-- page d'accueil ; non comparable entre entreprises.
update evidence e set review_status = 'rejected', reviewer = 'retire:recensement-non-borne-2026-10-13'
from indicators i, sources s
where i.id = e.indicator_id and s.id = e.source_id and e.review_status = 'pending'
  and s.code = 'BHRRC' and i.code in ('SUP_BHRRC_ALLEG', 'LAB_LITIGATION_RATE');

-- Articles de presse et pages d'accueil, sans citation : remplacés par une
-- décision officielle quand elle existe (sanctions), sinon non retenus.
update evidence e set review_status = 'rejected', reviewer = 'retire:presse-sans-citation-2026-10-13'
from indicators i, sources s, entities en
where i.id = e.indicator_id and s.id = e.source_id and en.id = e.entity_id and e.review_status = 'pending'
  and ((s.code = 'PRESS' and i.code in ('WAT_CONTROVERSY', 'LAB_LITIGATION_RATE', 'LAB_LIVING_WAGE', 'PLA_REDUCTION'))
    or (s.code = 'TAX_JUSTICE' and i.code = 'TAX_HAVEN_PRESENCE')            -- litige fiscal, pas une présence en paradis fiscal
    or (s.code = 'UN_PRI' and i.code = 'INV_RESPONSIBLE_POLICY')             -- page d'accueil des PRI
    or (en.slug = 'coca-cola' and s.code = 'ESG_REPORT' and i.code = 'SUP_SUPPLIER_LIST'));  -- communiqué d'Oxfam de 2013

-- Exploitation animale de Chanel : le cuir est déjà présumé (règle ANI : niveau
-- inconnu dans le luxe = exploitation supposée, pilier à 0) ; l'article de presse
-- n'ajoute rien de vérifiable.
update evidence e set review_status = 'rejected', reviewer = 'retire:presomption-suffit-2026-10-13'
from indicators i, sources s, entities en
where i.id = e.indicator_id and s.id = e.source_id and en.id = e.entity_id and e.review_status = 'pending'
  and en.slug = 'chanel' and i.code = 'ANI_EXPLOITATION' and s.code = 'PRESS';

-- Stellantis : un objectif de baisse de l'intensité en eau saisi comme une
-- « controverse » ; ce n'en est pas une.
update evidence e set review_status = 'rejected', reviewer = 'retire:objectif-saisi-comme-controverse-2026-10-13'
from indicators i, sources s, entities en
where i.id = e.indicator_id and s.id = e.source_id and en.id = e.entity_id and e.review_status = 'pending'
  and en.slug = 'stellantis' and i.code = 'WAT_CONTROVERSY';
