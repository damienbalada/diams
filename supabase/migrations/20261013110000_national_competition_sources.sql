-- =============================================================================
-- Sanctions : autorités nationales de concurrence (France, Italie)
-- -----------------------------------------------------------------------------
-- Décisions publiées par l'autorité elle-même (communiqué officiel, montant par
-- entreprise), retenues comme celles de la Commission européenne (tier
-- « regulatory », décision adjudiquée).
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description)
values
  ('FR_COMPETITION', 'Autorité de la concurrence (France)', 'regulatory', 'Autorité de la concurrence',
   'https://www.autoritedelaconcurrence.fr/fr/communiques-de-presse',
   'Décisions de sanction de l''autorité française de la concurrence (ententes, abus de position dominante), communiqué officiel et tableau des sanctions par entreprise.'),
  ('IT_COMPETITION', 'Autorité italienne de la concurrence et du marché (AGCM)', 'regulatory',
   'Autorità Garante della Concorrenza e del Mercato', 'https://en.agcm.it/en/media/press-releases/',
   'Décisions de sanction de l''autorité italienne (concurrence et protection des consommateurs), communiqué officiel en anglais.')
on conflict (code) do nothing;
