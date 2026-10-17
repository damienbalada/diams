-- Trois indicateurs d'information, non notés (poids 0), affichés seulement quand une preuve vérifiée
-- existe (décisions de l'éditeur du 17/10/2026).

-- (1) Conventions judiciaires d'intérêt public hors eau (fraude fiscale, corruption, trafic d'influence) :
-- validées par un juge, sans déclaration de culpabilité (article 41-1-2 du code de procédure pénale).
insert into indicators (code, dimension_id, name, kind, direction, sector_specific, weight, unit, methodology, group_level, complementary)
select 'GOV_CJIP', d.id, 'Convention judiciaire d''intérêt public (fraude fiscale, corruption)', 'categorical', 'higher_better', false, 0,
       'controverse',
       'Information, non notée. Convention judiciaire d''intérêt public conclue avec un parquet et validée par un juge (article 41-1-2 du code de procédure pénale) pour des faits de fraude fiscale, de corruption ou de trafic d''influence, publiée par le ministère de la Justice. La validation n''emporte pas déclaration de culpabilité ; la fiche le dit. Les conventions environnementales relèvent du pilier eau (WAT_CONTROVERSY).',
       true, true
from dimensions d where d.code = 'GOV'
on conflict (code) do nothing;

-- (2) Vente d'articles de chasse ou de pêche (pilier animal), documentée par le site de l'enseigne.
insert into indicators (code, dimension_id, name, kind, direction, sector_specific, weight, unit, methodology, group_level, complementary)
select 'ANI_HUNTING_FISHING', d.id, 'Vente d''articles de chasse ou de pêche', 'binary', 'higher_better', false, 0, null,
       'Information, non notée. L''enseigne ou la marque vend des articles de chasse ou de pêche, d''après son propre site (gamme ou marque dédiée). Rien n''est affiché tant que ce n''est pas documenté.',
       false, true
from dimensions d where d.code = 'ANI'
on conflict (code) do nothing;

-- (12) Écart entre le plus haut et le plus bas salaire : mesure distincte du ratio à la médiane
-- (LAB_CEO_PAY_RATIO), publiée par quelques entreprises (La Nef). Information, non notée : trop peu
-- d'entreprises la publient pour un classement entre pairs.
insert into indicators (code, dimension_id, name, kind, direction, sector_specific, weight, unit, methodology, group_level, complementary)
select 'LAB_PAY_RATIO_MAXMIN', d.id, 'Écart entre le plus haut et le plus bas salaire', 'quantitative', 'lower_better', false, 0, 'x',
       'Information, non notée. Rapport entre la rémunération la plus haute et la plus basse, tel que publié par l''entreprise. Ne se compare pas au ratio à la rémunération médiane (LAB_CEO_PAY_RATIO).',
       true, true
from dimensions d where d.code = 'LAB'
on conflict (code) do nothing;

-- La Nef : son ratio (au plus bas salaire) quitte l'indicateur à la médiane.
with deplace as (
  update evidence v set indicator_id = (select id from indicators where code = 'LAB_PAY_RATIO_MAXMIN'), normalized_value = null
  from entities e
  where e.id = v.entity_id and e.slug = 'la-nef'
    and v.indicator_id = (select id from indicators where code = 'LAB_CEO_PAY_RATIO')
  returning v.id, v.indicator_id
)
update indicator_reviews r set indicator_id = d.indicator_id from deplace d where r.evidence_id = d.id;
