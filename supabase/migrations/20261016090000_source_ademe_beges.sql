-- Source réglementaire : bilans d'émissions de gaz à effet de serre (BEGES) déposés sur la plateforme
-- de l'Ademe (obligation du code de l'environnement, art. L229-25), jeu ouvert « Bilan GES » sous
-- Licence Ouverte 2.0. Utilisée pour la publication des émissions indirectes (scope 3).
insert into sources (code, name, tier, publisher, url, description)
values ('ADEME_BEGES', 'Bilans d''émissions de gaz à effet de serre (plateforme de l''Ademe)', 'regulatory', 'Ademe',
        'https://bilans-ges.ademe.fr', 'Bilans GES réglementaires déposés par les entreprises (France), jeu ouvert de l''Ademe.')
on conflict (code) do nothing;
