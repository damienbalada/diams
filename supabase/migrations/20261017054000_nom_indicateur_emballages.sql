-- Emballages : l'indicateur réunit deux mesures publiées par les entreprises (recyclabilité dès la
-- conception, ou part de matière recyclée) ; le nom et la méthode le disent (17/10/2026).
update indicators set name = 'Emballages recyclables ou réutilisables, ou part de matière recyclée',
  methodology = 'Part d''emballages recyclables ou réutilisables dès la conception, ou, à défaut, part de matière recyclée dans les emballages, telle que publiée par l''entreprise ; la fiche indique laquelle des deux mesures est publiée (les deux ne sont pas équivalentes).'
 where code = 'PLA_RECYCLED';
