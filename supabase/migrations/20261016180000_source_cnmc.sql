-- CNMC (Comisión Nacional de los Mercados y la Competencia, Espagne) : décisions de sanction,
-- communiqués officiels (en anglais ou en espagnol).
insert into sources (code, name, tier, publisher, url, description)
values ('ES_COMPETITION', 'Autorité espagnole de la concurrence et des marchés (CNMC)', 'regulatory',
        'Comisión Nacional de los Mercados y la Competencia', 'https://www.cnmc.es/prensa',
        'Décisions de sanction de la CNMC (concurrence), communiqué officiel.')
on conflict (code) do nothing;
