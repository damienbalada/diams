-- Géorisques (ministère de la Transition écologique) : arrêtés préfectoraux de mise en demeure des
-- installations classées, publiés sous Licence Ouverte ; texte des scans reconnu par OCR.
insert into sources (code, name, tier, publisher, url, description)
values ('GEORISQUES', 'Géorisques (installations classées)', 'regulatory',
        'Ministère de la Transition écologique', 'https://www.georisques.gouv.fr',
        'Arrêtés préfectoraux de mise en demeure des installations classées pour la protection de l''environnement.')
on conflict (code) do nothing;
