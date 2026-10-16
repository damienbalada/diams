-- ASA (Advertising Standards Authority, Royaume-Uni) : instance de régulation de la publicité, décisions
-- publiées sur les plaintes ; retenues comme les avis du Jury de déontologie publicitaire (même niveau).
insert into sources (code, name, tier, publisher, url, description)
values ('UK_ASA', 'Autorité britannique de régulation de la publicité (ASA)', 'audited_ngo',
        'Advertising Standards Authority', 'https://www.asa.org.uk/codes-and-rulings/rulings.html',
        'Décisions de l''ASA sur les plaintes contre des publicités (allégations environnementales), en anglais.')
on conflict (code) do nothing;
