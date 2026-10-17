-- Nouvel indicateur géopolitique (décision de l'éditeur du 17/10/2026) : violation de sanctions
-- internationales, établie par un règlement avec l'OFAC (Office of Foreign Assets Control, Trésor des
-- États-Unis). Source officielle, publique : les avis d'exécution (« enforcement information ») nomment
-- l'entreprise, le montant et le programme de sanctions (Iran, Cuba, Russie, Syrie…). L'entreprise
-- règle sa responsabilité civile « potentielle », sans reconnaître de faute : la fiche le dit.
-- Information, non notée ; affichée seulement quand elle est documentée.
insert into sources (code, name, tier, publisher, url, description)
values ('OFAC', 'Trésor des États-Unis, OFAC (avis d''exécution des sanctions)', 'regulatory',
        'U.S. Department of the Treasury — Office of Foreign Assets Control', 'https://ofac.treasury.gov/civil-penalties-and-enforcement-information',
        'Règlements conclus par l''OFAC avec des entreprises pour des violations apparentes des sanctions américaines (Iran, Cuba, Russie, Syrie, trafic de stupéfiants…), en anglais.')
on conflict (code) do nothing;

insert into indicators (code, dimension_id, name, kind, direction, sector_specific, weight, unit, methodology, group_level, complementary)
select 'GEO_SANCTIONS_BREACH', d.id, 'Violation de sanctions internationales (OFAC)', 'categorical', 'higher_better', false, 0, 'controverse',
       'Information, non notée. Règlement conclu avec l''OFAC (Trésor des États-Unis) pour des violations apparentes de sanctions internationales : commerce avec un pays sous embargo (Iran, Cuba, Syrie, Crimée…) ou avec une personne inscrite sur ses listes. L''entreprise paie pour régler sa responsabilité civile potentielle, sans reconnaître de faute. Montant en dollars, année et programme de sanctions cités.',
       true, true
from dimensions d where d.code = 'GEO'
on conflict (code) do nothing;
