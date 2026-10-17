-- Retrait de deux notes CDP rattachées par erreur (17/10/2026) : le connecteur des notes CDP a rapproché
-- « Delta Corp Ltd. » (Inde) de Delta (Mundolsheim, SIREN 324432186), société française qui édite la
-- marque Livoo. Homonymie sans rapport : notes retirées. À éviter : ne pas lancer import_cdp_scores sur
-- une société au nom court et courant sans contrôler le pays.
delete from evidence
where id in ('92756bf8-8abc-4492-9dd5-c6b5d7945fa7', '7e50b457-741e-44bf-9ce8-4f2d116431ba')
  and entity_id = (select id from entities where slug = 'delta-mundolsheim');
