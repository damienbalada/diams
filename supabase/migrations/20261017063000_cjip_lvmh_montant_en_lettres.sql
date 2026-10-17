-- Convention LVMH (trafic d'influence, 17/12/2021) : les trois citations sont retrouvées mot pour mot dans
-- le communiqué du parquet ; le montant y est écrit en lettres (« dix millions d'euros »), que le contrôle
-- automatique des chiffres ne lit pas. Approuvée sur cette lecture (10 000 000 €).
update evidence set review_status = 'approved', reviewer = 'delegue-editeur:montant-en-lettres'
 where review_status = 'pending'
   and entity_id = (select id from entities where slug = 'lvmh')
   and indicator_id = (select id from indicators where code = 'GOV_CJIP')
   and excerpt like '%dix millions d’euros%';
