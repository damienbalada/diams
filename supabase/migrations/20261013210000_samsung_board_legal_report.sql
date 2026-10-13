-- Samsung, indépendance du conseil : la preuve citait le rapport de durabilité 2026,
-- document volontaire (aucune obligation en Corée), classé à tort comme rapport légal.
-- Remplacée par le rapport d'activité annuel 2025 (rapport légal, situation au
-- 31/12/2025 : 6 indépendants sur 9). Remise en attente, puis revérifiée mot pour mot.
update evidence ev set
  source_url = 'https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_4Q_Interim_Report.pdf',
  observed_on = '2026-04-21',
  value_numeric = 66.7,
  normalized_value = 0.667,
  excerpt = 'Rapport d''activité annuel 2025 de Samsung Electronics (rapport légal déposé en Corée, traduction anglaise publiée par le groupe), gouvernement d''entreprise : « As of the end of 2025, the Board of Directors consisted of 9 members: 3 Executive Directors (Young-Hyun Jun, Tae-moon Roh, and Jai-Hyuk Song) and 6 Independent Directors (Je-yoon Shin, Jun-sung Kim, Eun-nyeong Heo, Myung-hee Yoo, Hye-kyung Cho and Hyuk-Jae Lee) » ; calcul : 6 / 9 = 66,7 % (administrateurs indépendants).',
  review_status = 'pending',
  reviewer = null,
  updated_at = now()
where ev.entity_id = (select id from entities where slug = 'samsung')
  and ev.indicator_id = (select id from indicators where code = 'GOV_BOARD_INDEP')
  and ev.source_url like '%Sustainability_Report_2026%';
