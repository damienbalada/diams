-- Scission des glaces d'Unilever, achevée le 06/12/2025 ; The Magnum Ice Cream Company
-- (TMICC) est cotée à Amsterdam, Londres et New York depuis le 08/12/2025. Magnum et
-- Ben & Jerry's en font partie : ils ne relèvent plus d'Unilever (qui conserve 19,95 %
-- du capital). Rapport annuel 2025 de TMICC (format ESEF) :
-- https://filings.xbrl.org/25490052LLF3XH6G9847/2025-12-31/ESEF/NL/0/25490052LLF3XH6G9847-2025-12-31-1-en/reports/25490052LLF3XH6G9847-2025-12-31-1-en.xhtml
insert into entities (slug, legal_name, display_name, lei, country, sector_id, is_brand)
select 'magnum-ice-cream-company', 'The Magnum Ice Cream Company N.V.', 'The Magnum Ice Cream Company',
       '25490052LLF3XH6G9847', 'NL', s.id, false
from sectors s where s.code = 'fmcg_group'
on conflict (slug) do nothing;

update entities
   set parent_id = (select id from entities where slug = 'magnum-ice-cream-company'),
       ownership_pct = 100,
       updated_at = now()
 where slug in ('magnum-ice', 'ben-jerrys')
   and parent_id = (select id from entities where slug = 'unilever');
