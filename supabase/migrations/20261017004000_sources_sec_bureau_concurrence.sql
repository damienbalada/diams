-- Sanctions de la SEC (autorité américaine des marchés financiers), distinctes des documents déposés
-- (SEC_FILING) ; et Bureau de la concurrence du Canada (publicité trompeuse, y compris environnementale).
insert into sources (code, name, tier, publisher, url, description) values
  ('US_SEC', 'Commission des opérations de bourse des États-Unis (SEC) — sanctions', 'regulatory',
   'U.S. Securities and Exchange Commission', 'https://www.sec.gov/newsroom/press-releases',
   'Ordonnances et amendes civiles de la SEC (déclarations inexactes aux investisseurs), communiqué officiel en anglais.'),
  ('CA_COMPETITION', 'Bureau de la concurrence du Canada', 'regulatory',
   'Competition Bureau Canada', 'https://www.canada.ca/en/competition-bureau/news.html',
   'Accords et sanctions du Bureau de la concurrence (indications fausses ou trompeuses), communiqué officiel.')
on conflict (code) do nothing;
