-- =============================================================================
-- Labels et certifications : sources primaires (Finansol, B Corp, base ONU)
-- -----------------------------------------------------------------------------
-- Un label ou une certification n'est pas une note recopiée : c'est un fait
-- public, daté, contrôlé par un tiers (comité du label, évaluation B Lab), que
-- l'on lit à la source. Absence d'un label ≠ fait négatif : l'indicateur n'est
-- jamais obligatoire (Règle 1) — il ne fait que documenter, en particulier les
-- petits acteurs sans obligation de publication.
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('FINANSOL', 'Label Finansol (FAIR)', 'audited_ngo', 'FAIR — finance à impact social',
   'https://www.finance-fair.org/fr/quels-sont-les-placements-labellises-finansol',
   'Liste officielle des produits d''épargne labellisés Finansol ; label attribué et contrôlé chaque année par un comité indépendant.'),
  ('B_LAB', 'Annuaire B Corp (B Lab)', 'audited_ngo', 'B Lab',
   'https://www.bcorporation.net/en-us/find-a-b-corp/',
   'Certification B Corp : évaluation B Impact (seuil 80 points), vérification par B Lab, recertification tous les 3 ans.'),
  ('UN_OHCHR_DB', 'Base de données du HCDH (entreprises et colonies)', 'audited_ngo',
   'Haut-Commissariat des Nations unies aux droits de l''homme',
   'https://www.un.org/unispal/document/business-database-26sep25',
   'Base mandatée par le Conseil des droits de l''homme (rés. 31/36) recensant les entreprises impliquées dans les activités liées aux colonies israéliennes ; mises à jour 2020, 2023, 2025.')
on conflict (code) do nothing;

insert into indicators (code, dimension_id, name, kind, direction, sector_specific, applies_to_sector_id, weight, unit, methodology)
select v.code, d.id, v.name, v.kind::indicator_kind, v.direction::indicator_direction, v.sector_specific,
       (select id from sectors where code = v.sector), v.weight, v.unit, v.methodology
from (values
  ('INV_SOLIDARITY_LABEL', 'INV', 'Épargne solidaire labellisée (Finansol)', 'binary', 'higher_better', true, 'banking_finance', 0.6, 'bool',
   'Au moins un produit d''épargne distribué par l''établissement porte le label Finansol (liste officielle FAIR). Absence non renseignée (jamais comptée 0).'),
  ('GOV_BCORP', 'GOV', 'Certification B Corp', 'binary', 'higher_better', false, null, 0.8, 'bool',
   'Certification B Corp en vigueur (annuaire B Lab ; score B Impact ≥ 80). Absence non renseignée (jamais comptée 0).')
) as v(code, dim, name, kind, direction, sector_specific, sector, weight, unit, methodology)
join dimensions d on d.code = v.dim
on conflict (code) do nothing;
