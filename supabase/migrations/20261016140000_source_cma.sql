-- CMA (Competition and Markets Authority, Royaume-Uni) : décisions de sanction publiées sur gov.uk
-- (Open Government Licence), communiqués officiels en anglais.
insert into sources (code, name, tier, publisher, url, description)
values ('UK_COMPETITION', 'Autorité britannique de la concurrence et des marchés (CMA)', 'regulatory',
        'Competition and Markets Authority', 'https://www.gov.uk/cma-cases',
        'Décisions de sanction de la CMA (droit de la concurrence et protection des consommateurs), communiqué officiel en anglais.')
on conflict (code) do nothing;
