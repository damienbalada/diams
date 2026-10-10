-- =============================================================================
-- Verticale banque : source BOCC + mesure explicite du financement fossile
-- -----------------------------------------------------------------------------
-- Banking on Climate Chaos (BOCC) : rapport annuel d'une coalition d'ONG (RAN,
-- BankTrack, Reclaim Finance, Sierra Club, Urgewald…) sur les 65 plus grandes
-- banques, établi sur données de marché ; chaque banque peut revoir les
-- financements qui lui sont attribués avant publication. Tier audited_ngo, comme
-- Reclaim Finance (membre de la coalition).
--
-- INV_FOSSIL_FINANCING : la mesure retenue pour comparer les banques est le
-- financement annuel des entreprises qui DÉVELOPPENT de nouveaux projets
-- pétroliers et gaziers (tableaux « Oil & Gas Expansion » : amont + transport/GNL
-- + centrales à gaz), en Md$. Valeur brute, percentile inversé intra-secteur.
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('BOCC', 'Banking on Climate Chaos', 'audited_ngo',
   'Coalition BOCC (Rainforest Action Network, BankTrack, Reclaim Finance, Sierra Club, Urgewald, Oil Change International…)',
   'https://www.bankingonclimatechaos.org',
   'Rapport annuel sur les financements fossiles des 65 plus grandes banques ; chaque banque peut revoir les montants qui lui sont attribués avant publication.')
on conflict (code) do nothing;

update indicators
set unit = 'Md$',
    methodology = 'Financement annuel des entreprises qui développent de nouveaux projets pétroliers et gaziers (BOCC : amont + transport/GNL + centrales à gaz), en Md$. Valeur brute, percentile inversé intra-secteur.'
where code = 'INV_FOSSIL_FINANCING';
