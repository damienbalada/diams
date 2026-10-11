-- =============================================================================
-- Obligation de publication américaine : ratio de rémunération PDG / médian
-- -----------------------------------------------------------------------------
-- Règle 1 (v0.5) : une donnée manquante compte 0 si sa publication est
-- légalement obligatoire. Aux États-Unis, la circulaire de procuration des
-- sociétés cotées (formulaire DEF 14A) doit publier le ratio entre la
-- rémunération du PDG et celle du salarié médian. Les émetteurs étrangers
-- (formulaire 20-F) et les petites sociétés en sont exemptés.
-- Rattachement par entité dans curated/regimes_groupes_2026-10.csv.
-- =============================================================================

insert into disclosure_regimes (code, name, jurisdiction, legal_basis, scope, url, in_force_since) values
  ('US_SEC_PAY_RATIO', 'Ratio de rémunération PDG / salarié médian (SEC)', 'US',
   'Dodd-Frank Act, art. 953(b) ; Regulation S-K, Item 402(u) (17 CFR 229.402(u))',
   'Sociétés déposant une circulaire de procuration auprès de la SEC (hors émetteurs étrangers, petites sociétés et sociétés en croissance émergentes) : rémunération annuelle totale du PDG, du salarié médian et leur ratio, chaque année.',
   'https://www.ecfr.gov/current/title-17/chapter-II/part-229/subpart-229.400/section-229.402', '2017-01-01')
on conflict (code) do nothing;

insert into indicator_regimes (indicator_id, regime_id, note)
select i.id, r.id, 'Ratio PDG / salarié médian publié dans la circulaire DEF 14A.'
from indicators i, disclosure_regimes r
where i.code = 'LAB_CEO_PAY_RATIO' and r.code = 'US_SEC_PAY_RATIO'
on conflict do nothing;
