-- Source officielle : conventions judiciaires d'intérêt public publiées par le ministère de la Justice (17/10/2026).
insert into sources (code, name, tier, publisher, url, description)
values ('FR_CJIP', 'Conventions judiciaires d''intérêt public (ministère de la Justice)', 'regulatory', 'Ministère de la Justice',
 'https://www.justice.gouv.fr/documentation/ressources/conventions-judiciaires-dinteret-public',
 'Conventions conclues avec le procureur de la République et validées par le président du tribunal judiciaire (articles 41-1-2 et 41-1-3 du code de procédure pénale), publiées par le ministère de la Justice : amende d''intérêt public, réparation du préjudice écologique. La validation n''emporte pas déclaration de culpabilité.')
on conflict (code) do nothing;
