-- =============================================================================
-- Relecture complète : Kellanova appartient à Mars depuis le 11/12/2025
-- -----------------------------------------------------------------------------
-- Kellanova n'apparaissait plus ni au registre de transparence de l'UE ni dans KnowTheChain.
-- Vérification : l'acquisition par Mars est CONCLUE (règle de propriété : une acquisition
-- conclue change le groupe). Deux sources officielles, citations relues mot pour mot le
-- 15/10/2026 : le formulaire 8-K de Kellanova déposé à la SEC (11/12/2025) et le communiqué
-- de Mars sur son site. Kellanova (et ses marques) se rattache donc à Mars.
-- Également : retrait d'une ligne du journal consignée à tort (preuve d'Engie issue d'une
-- décision de l'éditeur, relue mot pour mot et confirmée).
-- =============================================================================

update entities set parent_id = (select id from entities where slug = 'mars'), updated_at = now()
 where slug = 'kellanova' and parent_id is null;

insert into entity_ownership_sources (entity_id, owner_id, source_url, excerpt, observed_on, reviewer)
select (select id from entities where slug = 'kellanova'), (select id from entities where slug = 'mars'), v.url, v.excerpt,
       '2026-10-15', 'delegue-editeur:verifie-mot-pour-mot'
from (values
  ('https://www.sec.gov/Archives/edgar/data/55067/000119312525315130/d90636d8k.htm',
   'Formulaire 8-K de Kellanova déposé à la SEC (11/12/2025), note d''introduction : « Mars, Incorporated, a Delaware corporation (“Parent”) » ; « On December 11, 2025 (the “Closing Date”), pursuant to the Merger Agreement, Merger Sub was merged with and into the Company (the “Merger”), with the Company surviving the Merger as a wholly owned subsidiary of Acquiror »'),
  ('https://www.mars.com/news-and-stories/press-releases-statements/mars-completes-acquisition-of-kellanova',
   'Communiqué de Mars du 11/12/2025 sur son site officiel : « Mars, Incorporated, a family-owned, global leader in pet care, snacking and food, is pleased to announce the successful completion of its acquisition of Kellanova »')
) as v(url, excerpt)
on conflict do nothing;

delete from indicator_reviews
 where reviewer = 'auto:relecture' and wave = 0 and outcome = 'ecart'
   and entity_id = (select id from entities where slug = 'engie')
   and indicator_id = (select id from indicators where code = 'LAB_CEO_PAY_RATIO');
