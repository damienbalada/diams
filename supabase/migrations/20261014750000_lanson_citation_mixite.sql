-- Lanson-BCC, mixité du conseil (preuve en attente) : la citation contenait des guillemets
-- imbriqués (« femmes ») qui coupaient la lecture des citations ; on cite la seule phrase
-- de composition du conseil.
update evidence e
   set excerpt = 'Document d''enregistrement universel 2025 de Lanson-BCC déposé à l''AMF le 02/04/2026 (D.26-0213), gouvernement d''entreprise : « Le Conseil d’administration est composé de 6 femmes et 6 hommes » ; calcul : 6 / (6 + 6) = 50,0 %.',
       updated_at = now()
 where e.entity_id = (select id from entities where slug = 'lanson-bcc')
   and e.indicator_id = (select id from indicators where code = 'GOV_BOARD_GENDER')
   and e.observed_on = '2026-04-02'
   and e.review_status = 'pending';
