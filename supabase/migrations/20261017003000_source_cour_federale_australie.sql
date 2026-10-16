-- Cour fédérale d'Australie : jugements de sanction obtenus par l'ACCC (autorité australienne de la
-- concurrence et des consommateurs), publiés par la Cour. Le site de l'ACCC refuse le vérificateur ; le
-- jugement, source primaire, est cité à sa place. Montants en dollars australiens.
insert into sources (code, name, tier, publisher, url, description)
values ('AU_FEDERAL_COURT', 'Cour fédérale d''Australie (jugements obtenus par l''ACCC)', 'regulatory',
        'Federal Court of Australia', 'https://www.judgments.fedcourt.gov.au/',
        'Jugements de la Cour fédérale d''Australie prononçant des amendes civiles à la demande de l''ACCC (droit de la consommation), en anglais.')
on conflict (code) do nothing;
