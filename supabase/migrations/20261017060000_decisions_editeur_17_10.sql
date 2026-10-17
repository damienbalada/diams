-- Décisions de l'éditeur du 17/10/2026 (réponses au rapport de nuit).

-- (15) Carrefour Veggie est l'ancien nom de Carrefour Sensation (document d'enregistrement universel
-- de Carrefour : « Carrefour Sensation, anciennement Carrefour Veggie »). La fiche Carrefour Veggie, sans
-- preuve, est fusionnée : son nom devient un alias de Carrefour Sensation, ses constats de journal la suivent.
insert into entity_aliases (entity_id, alias, norm, source)
select s.id, 'Carrefour Veggie', 'carrefour veggie', 'fusion:ancien-nom'
from entities s where s.slug = 'carrefour-sensation'
on conflict do nothing;
update indicator_reviews set entity_id = (select id from entities where slug = 'carrefour-sensation')
 where entity_id = (select id from entities where slug = 'carrefour-veggie');
delete from entity_ownership_sources where entity_id = (select id from entities where slug = 'carrefour-veggie');
delete from entity_aliases where entity_id = (select id from entities where slug = 'carrefour-veggie');
delete from entities where slug = 'carrefour-veggie';

-- (16) Haleon : le rapport détaille « 1 Chair 2 Executive Directors 8 Independent Non-Executive
-- Directors » sans écrire le total ; l'éditeur admet le total obtenu par addition. Citation vérifiée mot
-- pour mot pendant la nuit ; le calcul est rendu explicite.
update evidence
   set excerpt = replace(excerpt, 'calcul : 8 / 11 = 72,7 %', 'calcul : 8 / (1 + 2 + 8) = 8 / 11 = 72,7 %'),
       normalized_value = 0.727,
       review_status = 'approved',
       reviewer = 'delegue-editeur:total-par-addition'
 where id = '241501d1-857f-4c74-ba65-e375c53dbc50';

-- (19) Filiale française sans identifiant LEI : admise quand l'annexe consolidée du groupe la liste.
-- Zara France, S.A.R.L. (SIREN 348 991 555) figure dans la liste des sociétés consolidées du rapport
-- annuel 2024 d'Inditex (ESEF, exercice clos le 31/01/2025) : « Zara France, S.A.R.L. 100.00% Paris -
-- France Full Consol. 31-jan Zara Retail sales ». Elle transmet Égapro et la loi Rixain à Inditex et Zara.
insert into entities (slug, legal_name, display_name, siren, country, sector_id, is_brand, animal_free, parent_id, ownership_pct, filiale_fr_principale)
select 'zara-france', 'ZARA FRANCE', 'Zara France', '348991555', 'FR', p.sector_id, false, false, p.id, 100, true
from entities p where p.slug = 'inditex'
on conflict (slug) do nothing;
-- SIREN confirmé actif dans l'annuaire officiel des entreprises le 17/10/2026 (ZARA FRANCE, 22 rue Bergère, Paris).
insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select f.id, p.id,
  'https://filings.xbrl.org/549300TTCXZOGZM2EY83/2025-01-31/ESEF/ES/0/549300TTCXZOGZM2EY83-20250131-0-en/reports/549300TTCXZOGZM2EY83-20250131-0-en.xhtml',
  'Rapport annuel 2024 d''Inditex (ESEF, en anglais), annexe des sociétés consolidées : « Zara France, S.A.R.L. 100.00% Paris - France Full Consol. 31-jan Zara Retail sales »',
  '2026-10-17', 'delegue-editeur:annexe-consolidee'
from entities f, entities p where f.slug = 'zara-france' and p.slug = 'inditex'
  and not exists (select 1 from entity_ownership_sources o where o.entity_id = f.id);
