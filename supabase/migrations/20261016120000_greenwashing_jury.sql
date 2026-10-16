-- Décision de l'éditeur du 16/10/2026 : l'indicateur couvre aussi les avis des jurys de déontologie
-- publicitaire (Jury de déontologie publicitaire en France), instances d'autorégulation reconnues.
update indicators
set name = 'Allégations environnementales trompeuses (décision d''une autorité ou d''un jury publicitaire)',
    methodology = 'Décision officielle d''une autorité de protection des consommateurs : amende pour allégations environnementales trompeuses = sévérité 0,8 ; engagements de retrait obtenus après enquête, sans sanction = 0,5. Avis du Jury de déontologie publicitaire (plainte fondée ou partiellement fondée au regard des règles « Développement durable ») publié dans les cinq dernières années = 0,5. Absent : non pénalisé.'
where code = 'ENV_GREENWASHING';
