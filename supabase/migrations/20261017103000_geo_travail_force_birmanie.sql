-- Deux indicateurs géopolitiques d'information (décision de l'éditeur du 17/10/2026), non notés,
-- affichés seulement quand ils sont documentés.
--
-- Au 17/10/2026, aucune preuve n'a pu être saisie :
--   * travail forcé des Ouïghours : le rapport « Uyghurs for Sale » de l'ASPI (Australian Strategic
--     Policy Institute, 2020) refuse le vérificateur (deux tentatives, code 403) ; la liste officielle
--     UFLPA du département de la Sécurité intérieure des États-Unis ne nomme aucune entreprise suivie
--     (homonymes seulement) ;
--   * armée birmane : le rapport de l'ONU (A/HRC/42/CRP.3, 2019) ne nomme aucune entreprise suivie
--     (Kirin n'est pas dans l'Index ; « Oberthur Technologies », société de cartes à puce, n'est pas la
--     marque de papeterie Oberthur).
-- Les indicateurs sont prêts pour des preuves vérifiées mot pour mot (au besoin sur une copie de page
-- enregistrée par l'éditeur).

insert into sources (code, name, tier, publisher, url, description)
values ('ASPI', 'Australian Strategic Policy Institute (rapport « Uyghurs for Sale »)', 'audited_ngo',
        'Australian Strategic Policy Institute', 'https://www.aspi.org.au/report/uyghurs-sale',
        'Rapport de 2020 de l''institut australien de recherche stratégique sur le transfert de travailleurs ouïghours vers des usines de Chine, avec les marques dont les chaînes d''approvisionnement y seraient liées. Allégations, en anglais.'),
       ('UN_FFM_MYANMAR', 'ONU, Mission internationale indépendante d''établissement des faits sur le Myanmar', 'regulatory',
        'Conseil des droits de l''homme des Nations unies', 'https://www.ohchr.org/sites/default/files/Documents/HRBodies/HRCouncil/FFM-Myanmar/EconomicInterestsMyanmarMilitary/A_HRC_42_CRP_3.pdf',
        'Rapport A/HRC/42/CRP.3 (2019) sur les intérêts économiques de l''armée birmane : entreprises étrangères en coentreprise ou en relation commerciale avec ses conglomérats (MEHL, MEC), en anglais.')
on conflict (code) do nothing;

insert into indicators (code, dimension_id, name, kind, direction, sector_specific, weight, unit, methodology, group_level, complementary)
select 'GEO_FORCED_LABOR', d.id, 'Liens allégués avec le travail forcé des Ouïghours', 'categorical', 'higher_better', false, 0, 'controverse',
       'Information, non notée. Marque ou groupe nommé par une source reconnue (rapport de l''ASPI, liste UFLPA du gouvernement des États-Unis) comme lié, par sa chaîne d''approvisionnement, à des usines employant des Ouïghours transférés de force. Ce sont des allégations : la réponse publiée de l''entreprise est citée quand elle existe.',
       true, true
from dimensions d where d.code = 'GEO'
on conflict (code) do nothing;

insert into indicators (code, dimension_id, name, kind, direction, sector_specific, weight, unit, methodology, group_level, complementary)
select 'GEO_MYANMAR_MILITARY', d.id, 'Liens économiques avec l''armée birmane', 'categorical', 'higher_better', false, 0, 'controverse',
       'Information, non notée. Entreprise nommée par la Mission d''établissement des faits de l''ONU (2019) pour une coentreprise, une relation commerciale ou un don au profit de l''armée birmane (Tatmadaw) et de ses conglomérats. Un retrait annoncé depuis est indiqué avec sa source.',
       true, true
from dimensions d where d.code = 'GEO'
on conflict (code) do nothing;
