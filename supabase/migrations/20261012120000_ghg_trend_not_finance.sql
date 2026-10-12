-- =============================================================================
-- Évolution des émissions : pas pour la banque et l'assurance
-- -----------------------------------------------------------------------------
-- Les émissions totales d'une banque ou d'un assureur sont surtout des émissions
-- financées (scope 3, catégorie 15), dont le périmètre change d'une année à
-- l'autre (Société Générale : « hors scope 3 des contreparties financées » ;
-- AXA : base 2019 retraitée, investissements passés de 56 à 25 Mt). Leur
-- évolution ne mesure pas une baisse réelle : l'indicateur ne s'applique pas
-- au secteur banque et finance (pertinence par liste de secteurs).
-- =============================================================================

insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where i.code = 'ENV_GHG_TREND' and s.code <> 'banking_finance'
on conflict do nothing;
