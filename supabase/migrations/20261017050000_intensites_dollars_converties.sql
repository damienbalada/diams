-- Intensité carbone publiée en dollars (AB InBev, TotalEnergies) : seule devise restée non convertie,
-- alors que les intensités en couronnes et en francs suisses sont converties en euros au taux annuel
-- moyen de la BCE. Comparaison entre pairs faussée d'environ 13 %. Les preuves en dollars sont
-- remplacées par leur conversion (lot 190, citations identiques, contrôle du taux par le vérificateur).
update evidence set review_status = 'rejected', reviewer = 'remplace:conversion-dollars-2026-10-17'
 where review_status = 'approved'
   and indicator_id = (select id from indicators where code = 'ENV_GHG_INTENSITY')
   and entity_id in (select id from entities where slug in ('ab-inbev', 'totalenergies'))
   and observed_on < '2026-10-17'
   and value_numeric in (373, 2078);
