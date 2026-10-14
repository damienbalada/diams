-- Lot 93 : sociétés éditrices ou propriétaires de marques de fromages et de confiserie, SIREN
-- vérifiés dans l'annuaire officiel des entreprises le 14/10/2026 (toutes actives) ; LEI lus
-- dans le registre GLEIF.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('laiteries-h-triballat', 'LAITERIES H. TRIBALLAT', 'Laiteries H. Triballat (Rians)', '969500AP1QSMRSKR2R50', '583720644', 'FR', 'food'),
  ('union-laitiere-vittelloise', 'UNION LAITIERE VITTELLOISE', 'Fromagerie de l''Ermitage (Union laitière vittelloise)', '969500D9LX2K2S6O1L45', '783423270', 'FR', 'food'),
  ('fromageries-arnaud', 'FROMAGERIES ARNAUD', 'Fromageries Arnaud', null, '625880109', 'FR', 'food'),
  ('sucralliance', 'SUCRALLIANCE', 'Sucralliance (confiserie)', null, '487446395', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
