-- FTC (Federal Trade Commission, États-Unis) : amendes civiles (« civil penalty ») prononcées dans le
-- cadre d'une transaction homologuée ou d'un jugement, d'après les communiqués officiels (domaine public).
insert into sources (code, name, tier, publisher, url, description)
values ('US_FTC', 'Commission fédérale du commerce des États-Unis (FTC)', 'regulatory',
        'Federal Trade Commission', 'https://www.ftc.gov/news-events/news/press-releases',
        'Amendes civiles obtenues par la FTC (protection des consommateurs, vie privée), communiqué officiel en anglais.')
on conflict (code) do nothing;
