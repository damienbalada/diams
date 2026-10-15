-- Source officielle : sanctions publiées par la DGCCRF (amendes administratives, notamment pour
-- retards de paiement aux fournisseurs, art. L. 441-16 et L. 470-2 du code de commerce). La loi
-- impose leur publication sur le site de la DGCCRF ; chaque page nomme la société et son SIRET,
-- rapproché du SIREN des entités DIAMS. Publications temporaires : la date retenue est celle de la
-- page (plan du site officiel).
insert into sources (code, name, tier, publisher, url, description)
values ('FR_DGCCRF', 'DGCCRF — sanctions publiées', 'regulatory', 'Direction générale de la concurrence, de la consommation et de la répression des fraudes',
        'https://www.economie.gouv.fr/dgccrf/laction-de-la-dgccrf/injonctions-et-sanctions',
        'Injonctions et amendes administratives publiées par la DGCCRF (délais de paiement, pratiques commerciales) ; société identifiée par son SIRET.')
on conflict (code) do nothing;
