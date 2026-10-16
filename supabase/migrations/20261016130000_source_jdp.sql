-- Jury de déontologie publicitaire (ARPP) : avis publiés sur les plaintes, instance d'autorégulation
-- reconnue de la publicité en France (décision de l'éditeur du 16/10/2026).
insert into sources (code, name, tier, publisher, url, description)
values ('JDP', 'Jury de déontologie publicitaire', 'audited_ngo', 'ARPP', 'https://www.jdp-pub.org',
        'Avis rendus sur les plaintes contre des publicités (Recommandation Développement durable de l''ARPP).')
on conflict (code) do nothing;
