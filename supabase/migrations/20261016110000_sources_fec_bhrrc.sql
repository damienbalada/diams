-- Sources du 16/10/2026 : Commission électorale fédérale des États-Unis (fichiers publics, domaine
-- public, connecteur déterministe) et Business & Human Rights Resource Centre (articles relayés :
-- niveau presse, preuves vérifiées mot pour mot avant approbation).
insert into sources (code, name, tier, publisher, url, description) values
 ('FEC', 'Commission électorale fédérale des États-Unis (FEC)', 'regulatory', 'Federal Election Commission',
  'https://www.fec.gov', 'Comités d''action politique d''entreprise et leurs contributions (fichiers publics).'),
 ('BHRRC', 'Business & Human Rights Resource Centre', 'press', 'Business & Human Rights Resource Centre',
  'https://www.business-humanrights.org', 'Articles relayant des allégations d''atteintes aux droits humains (exactitude non garantie par le site).')
on conflict (code) do nothing;
