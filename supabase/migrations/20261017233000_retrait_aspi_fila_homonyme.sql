-- Retrait d'une preuve rattachée par homonymie (17/10/2026) : le lot 227 (rapport « Uyghurs for sale » de
-- l'ASPI) a rattaché la marque de sport « Fila » (Fila Holdings, Corée du Sud) à l'entité « fila », qui est le
-- groupe italien de papeterie F.I.L.A. (Giotto, Canson, Lyra), sans rapport. Preuve retirée ; la ligne est
-- enlevée du fichier du lot 227.
delete from evidence
where id = '1124231a-e295-4bbd-b523-ef74198fbd74'
  and entity_id = (select id from entities where slug = 'fila');
