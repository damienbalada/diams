-- Source propre aux déclarations de représentation équilibrée (loi Rixain), distincte de l'index
-- Égapro (même site du ministère du Travail, autre obligation) ; les preuves déjà importées sous
-- la source Égapro y sont rattachées.
insert into sources (code, name, tier, publisher, url, description)
values ('RIXAIN', 'Représentation équilibrée femmes-hommes (loi Rixain)', 'regulatory', 'Ministère du Travail',
        'https://egapro.travail.gouv.fr/representation-equilibree',
        'Déclarations annuelles de la part de femmes parmi les cadres dirigeants et les membres des instances dirigeantes (entreprises d''au moins 1 000 salariés), export public du site Égapro.')
on conflict (code) do nothing;

update evidence ev set source_id = (select id from sources where code = 'RIXAIN')
from indicators i
where ev.indicator_id = i.id and i.code = 'GOV_EXEC_GENDER'
  and ev.source_id = (select id from sources where code = 'EGAPRO');
