-- Lot 223 : La Française des Jeux (marques FDJ et illiko, jeux de grattage vendus en points de vente) ;
-- LEI vérifié dans GLEIF le 17/10/2026 (969500R4CLSQFTYYI535, actif, SIREN 315065292). Secteur « Jouets &
-- Jeux » faute de secteur propre aux jeux d'argent.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'fdj', 'LA FRANCAISE DES JEUX', 'FDJ United (La Française des Jeux)', '969500R4CLSQFTYYI535', '315065292', 'FR', s.id, false
from sectors s where s.code = 'toys_games'
on conflict (slug) do nothing;

-- Autres graphies relevées dans Open Products Facts (reconnaissance des codes-barres seulement).
update entities set aliases = (select array(select distinct unnest(aliases || array['Etamine'])))
where slug = 'etamine-du-lys';
update entities set aliases = (select array(select distinct unnest(aliases || array['Laboratoire Cooper', 'Laboratoires Cooper'])))
where slug = 'cooper';
update entities set aliases = (select array(select distinct unnest(aliases || array['AfterShokz'])))
where slug = 'shokz';
update entities set aliases = (select array(select distinct unnest(aliases || array['La Française des Jeux', 'La Francaise des Jeux'])))
where slug = 'fdj';
