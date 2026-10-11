-- =============================================================================
-- Règle 8 (v0.6.0) : ce que mesure la SOURCE décide du niveau de l'indicateur
-- -----------------------------------------------------------------------------
-- Ces indicateurs restaient propres à la marque alors que leur source ne mesure
-- que le groupe : Break Free From Plastic attribue les déchets audités au groupe
-- propriétaire, le Global Commitment (Ellen MacArthur) et le BBFAW évaluent les
-- engagements et politiques d'un groupe, les données eau (ESRS E3), les
-- allégations (BHRRC), la liste fournisseurs et les pratiques sociales internes
-- sont publiées pour le groupe. Résultat avant ce correctif : Ariel échappait au
-- plafond « gros pollueur plastique » de Procter & Gamble, faute de preuve propre.
--
-- Restent propres à la marque : politiques matières animales (fourrure, cuir,
-- peaux exotiques, laine, duvet, angora) et plafond d'exploitation animale,
-- transparence textile (Fashion Transparency Index, qui note chaque marque),
-- matières (Textile Exchange), labels (B Corp, Finansol) et l'index Égapro (dû
-- par chaque société employeuse). Une marque 100 % végétale reste hors du pilier
-- animal de son groupe (filtre animal_free inchangé), et une preuve propre à la
-- marque passe toujours devant celle du groupe.
-- =============================================================================

update indicators set group_level = true where code in (
  'PLA_POLLUTER', 'PLA_REDUCTION', 'PLA_RECYCLED',
  'ANI_BBFAW_TIER',
  'WAT_INTENSITY', 'WAT_CONTROVERSY',
  'SUP_BHRRC_ALLEG', 'SUP_SUPPLIER_LIST', 'SUP_LIVING_WAGE',
  'LAB_LIVING_WAGE', 'LAB_LITIGATION_RATE');
