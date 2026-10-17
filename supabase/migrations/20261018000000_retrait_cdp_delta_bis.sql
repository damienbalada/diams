-- Retrait (18/10/2026) : le connecteur CDP a de nouveau rattaché « Delta Corp Ltd. » (Inde) à Delta,
-- éditrice de Livoo (Mundolsheim), par égalité du nom court « Delta ». Homonyme : notes retirées, et
-- l'entité est désormais exclue du rapprochement (SKIP dans import_cdp_scores.py).
delete from evidence
where entity_id = (select id from entities where slug = 'delta-mundolsheim')
  and source_url ilike '%cdp.net%'
  and excerpt like '%Delta Corp Ltd.%';
