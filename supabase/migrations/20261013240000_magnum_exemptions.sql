-- The Magnum Ice Cream Company déclare non matériels, dans la table des points de
-- données ESRS de son état de durabilité 2025, l'écart de rémunération femmes-hommes et
-- le ratio de rémunération du dirigeant (S1-16) : la CSRD n'en impose pas la publication
-- (v0.7.3, même règle que LVMH). Citations mot pour mot du rapport annuel 2025 (ESEF).
insert into obligation_exemptions (entity_id, indicator_id, reason, source_url, excerpt)
select e.id, i.id, v.reason,
  'https://filings.xbrl.org/25490052LLF3XH6G9847/2025-12-31/ESEF/NL/0/25490052LLF3XH6G9847-2025-12-31-1-en/reports/25490052LLF3XH6G9847-2025-12-31-1-en.xhtml',
  'Rapport annuel 2025 de The Magnum Ice Cream Company (format ESEF, en anglais), état de durabilité, table des points de données ESRS : « ESRS S1-16 97 (a) Unadjusted gender pay gap Not material ESRS S1-16 97 (b) Excessive CEO pay ratio Not material » ; index ESRS : « S1-16 Remuneration metrics (pay gap and total remuneration) Not material ».'
from entities e
join (values
  ('LAB_GENDER_PAYGAP', 'Déclarée non matérielle par The Magnum Ice Cream Company dans son état de durabilité 2025 : la CSRD n''en impose pas la publication.'),
  ('LAB_CEO_PAY_RATIO', 'Déclarée non matérielle par The Magnum Ice Cream Company dans son état de durabilité 2025 : la CSRD n''en impose pas la publication.')
) as v(code, reason) on true
join indicators i on i.code = v.code
where e.slug = 'magnum-ice-cream-company'
on conflict (entity_id, indicator_id) do nothing;
